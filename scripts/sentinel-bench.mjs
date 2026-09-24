#!/usr/bin/env node
/**
 * sentinel-bench.mjs — run the sentinel-hook rules (deterministic, no model in the path) over a JSONL of
 * candidate tool calls extracted from Moltbook posts, and write one decision per call.
 *
 *   node research/moltbook/scripts/sentinel-bench.mjs <calls.jsonl> <out.jsonl> <path/to/sentinel-hook>
 *
 * Input line: { "id": "...", "post_id": "...", "set": "injection|benign", "surface": "S1..S6",
 *               "tool": "Bash|Write|Read", "input": { "command": "..." } | { "file_path": "...", "content": "..." } }
 * Output line: input + { "agent": {decision, rule, reason, severity}, "person": {decision, rule, reason, severity} }
 *
 * The rules judge the TEXT of a command; nothing is executed. The repo root handed to the rules is a
 * throwaway directory so that "outside the repository" means what it would for a real agent.
 */
import { createReadStream, mkdtempSync, writeFileSync, readFileSync } from 'node:fs'
import { createInterface } from 'node:readline'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const [, , inFile, outFile, hookDir = process.env.SENTINEL_HOOK_DIR, inventoryFile] = process.argv
if (!inFile || !outFile || !hookDir) {
  console.error('usage: sentinel-bench.mjs <calls.jsonl> <out.jsonl> <sentinel-hook dir>')
  process.exit(2)
}
const rulesPath = path.join(hookDir, 'scripts', 'sentinel', 'rules.mjs')
const rules = await import(pathToFileURL(rulesPath).href)
const { evaluate, SENTINEL_VERSION } = rules
const inventory = JSON.parse(readFileSync(inventoryFile || path.join(hookDir, 'templates', 'agents.json'), 'utf8'))

// A synthetic repository root: the agent's declared scope is what templates/agents.json says.
const repoRoot = mkdtempSync(path.join(tmpdir(), 'sentinel-bench-'))
const agentId = (Array.isArray(inventory.agents) && inventory.agents[0] && inventory.agents[0].id) || 'agent'
const agent = { kind: 'agent', agent: agentId, email: `${agentId}@example.invalid` }
const person = { kind: 'person', agent: null, email: 'person@example.invalid' }

const run = (tool, input, identity) => {
  try {
    const v = evaluate({ tool, input, identity, cwd: repoRoot, repoRoot, inventory })
    return {
      decision: v.decision,
      rule: v.rule || null,
      reason: v.reason || null,
      severity: v.severity || null,
      findings: (v.findings || []).map((f) => (typeof f === 'string' ? f : f.rule || JSON.stringify(f))),
    }
  } catch (e) {
    return { decision: 'error', rule: null, reason: String(e.message || e), severity: null, findings: [] }
  }
}

const out = []
let n = 0
const rl = createInterface({ input: createReadStream(inFile) })
for await (const line of rl) {
  if (!line.trim()) continue
  const rec = JSON.parse(line)
  const tool = rec.tool || 'Bash'
  const input = rec.input || { command: rec.command }
  out.push({ ...rec, agent: run(tool, input, agent), person: run(tool, input, person) })
  n++
}
writeFileSync(outFile, out.map((o) => JSON.stringify(o)).join('\n') + '\n')
const digest = typeof rules.rulesDigest === 'function' ? rules.rulesDigest() : null
console.error(JSON.stringify({ evaluated: n, sentinel_version: SENTINEL_VERSION, rules_sha256: digest, repoRoot, agentId, inventory: inventoryFile || 'templates/agents.json' }))
