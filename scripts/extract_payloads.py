#!/usr/bin/env python3
"""
extract_payloads.py — from Moltbook posts, extract the concrete ACTIONS an injection asks an agent to
take, and map each to the tool call a Claude Code agent would make, so that a host-side action gate
(sentinel-hook) can be benchmarked on what it actually sees.

Surfaces (one post can carry several):
  S1  shell command present            -> Bash tool call            (gate sees it)
  S2  HTTP/API call described           -> Bash curl reconstruction  (gate sees the reconstruction only)
  S3  file / persistence write asked    -> Write tool call to the named path (gate sees it)
  S4  platform social action asked      -> none (upvote/follow/comment/post: no host-side tool)
  S5  credential disclosure asked       -> Bash only if a credential file is read or uploaded
  S6  instruction / persuasion only     -> none
  S0  none of the above
Nothing here is executed. Every extracted command is text handed to a rule engine.
"""
from __future__ import annotations
import argparse, json, re
import duckdb

CODE_BLOCK = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.S)
INLINE_CODE = re.compile(r"`([^`\n]{4,400})`")
SHELL_WORDS = r"(?:curl|wget|bash|sh|zsh|python3?|node|npm|npx|pip3?|git|rm|chmod|chown|sudo|echo|cat|printf|eval|base64|xargs|find|dd|mkfs|crontab|launchctl|osascript|powershell|scp|ssh|nc|ncat|open|source|export|tee|sed|kill|pkill|docker|kubectl|fly|vercel|gh|aws)"
SHELL_LINE = re.compile(r"^\s*(?:\$\s*)?(" + SHELL_WORDS + r"\b[^\n]*)$", re.M)
API_LINE = re.compile(r"\b(POST|GET|PUT|PATCH|DELETE)\s+(/api[^\s\"'<>]*|https?://[^\s\"'<>]+)", re.I)
URL = re.compile(r"https?://[^\s\"'<>)\]]+")
PERSIST_HINT = re.compile(r"\b(SOUL\.md|HEARTBEAT\.md|MEMORY\.md|AGENTS\.md|CLAUDE\.md|\.env|\.bashrc|\.zshrc|crontab|heartbeat|config\.(?:json|yaml|yml|toml)|settings\.json|system prompt|memory file)\b", re.I)
WRITE_VERB = re.compile(r"\b(add|append|write|save|update|edit|put|insert|paste|store)\b", re.I)
SOCIAL = re.compile(r"\b(upvote|downvote|follow (?:me|@)|subscribe|comment (?:on|below)|repost|share this|post (?:this|it)|reply with|join (?:the|m/)|vote)\b", re.I)
CRED_ASK = re.compile(r"\b(send|share|paste|post|reply with|include|give|dm|message)\b[^.\n]{0,60}\b(api[_ -]?key|token|password|secret|credential|private key|seed phrase)\b", re.I)
CRED_PLACEHOLDER = re.compile(r"Bearer YOUR|YOUR_API_KEY", re.I)
INSTRUCT = re.compile(r"\b(ignore (?:previous|prior|above|all) instructions?|you must|you are now|new instructions?|system override|from now on|your (?:new )?(?:task|mission|directive) is)\b", re.I)

PATH_FOR = {
    "soul.md": "~/.openclaw/workspace/SOUL.md", "heartbeat.md": "~/.openclaw/workspace/HEARTBEAT.md",
    "memory.md": "~/.openclaw/workspace/MEMORY.md", "agents.md": "~/.openclaw/workspace/AGENTS.md",
    "claude.md": "~/.claude/CLAUDE.md", ".env": "~/.openclaw/.env", ".bashrc": "~/.bashrc", ".zshrc": "~/.zshrc",
    "crontab": "/var/spool/cron/crontab", "settings.json": "~/.claude/settings.json",
    "system prompt": "~/.openclaw/workspace/SOUL.md", "memory file": "~/.openclaw/workspace/MEMORY.md",
    "heartbeat": "~/.openclaw/workspace/HEARTBEAT.md",
}


def shell_candidates(text: str) -> list[str]:
    out = []
    for block in CODE_BLOCK.findall(text):
        for line in block.splitlines():
            m = SHELL_LINE.match(line)
            if m:
                out.append(m.group(1).strip())
    for inline in INLINE_CODE.findall(text):
        m = SHELL_LINE.match(inline)
        if m:
            out.append(m.group(1).strip())
    stripped = CODE_BLOCK.sub(" ", text)
    for m in SHELL_LINE.finditer(stripped):
        cmd = m.group(1).strip()
        # an English sentence starting with "open" or "find" is not a command; require a flag, path, pipe or URL
        if re.search(r"(\s-[A-Za-z]|/|\||https?://|>|&&|;)", cmd):
            out.append(cmd)
    seen, uniq = set(), []
    for c in out:
        c = c[:600]
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def api_reconstructions(text: str) -> list[str]:
    out = []
    for m in API_LINE.finditer(text):
        verb, target = m.group(1).upper(), m.group(2)
        url = target if target.startswith("http") else "https://www.moltbook.com" + target
        ctx = text[max(0, m.start() - 200): m.end() + 300]
        auth = ' -H "Authorization: Bearer $MOLTBOOK_API_KEY"' if re.search(r"bearer|api[_ -]?key|authorization", ctx, re.I) else ""
        body = " -d '{}'" if verb in ("POST", "PUT", "PATCH") else ""
        out.append(f"curl -X {verb}{auth}{body} {url}")
    return out


def write_targets(text: str) -> list[str]:
    targets = []
    for m in PERSIST_HINT.finditer(text):
        window = text[max(0, m.start() - 160): m.end() + 40]
        if WRITE_VERB.search(window):
            targets.append(m.group(0).lower())
    return sorted(set(targets))


def classify(text: str) -> dict:
    cmds = shell_candidates(text)
    apis = api_reconstructions(text)
    writes = write_targets(text)
    surfaces = set()
    if cmds:
        surfaces.add("S1")
    if apis:
        surfaces.add("S2")
    if writes:
        surfaces.add("S3")
    if SOCIAL.search(text):
        surfaces.add("S4")
    if CRED_ASK.search(text) or CRED_PLACEHOLDER.search(text):
        surfaces.add("S5")
    if INSTRUCT.search(text):
        surfaces.add("S6")
    if not surfaces:
        surfaces.add("S0")
    return {"surfaces": sorted(surfaces), "commands": cmds, "api_calls": apis, "write_targets": writes,
            "n_urls": len(URL.findall(text)), "has_code_block": bool(CODE_BLOCK.search(text))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="duckdb file with a posts_dedup table")
    ap.add_argument("--set", required=True, choices=["injection", "benign", "benign_code"])
    ap.add_argument("--ids", required=True, help="file of post ids (one per line)")
    ap.add_argument("--out-calls", required=True)
    ap.add_argument("--out-posts", required=True)
    args = ap.parse_args()
    con = duckdb.connect(args.db, read_only=True); con.execute("SET TimeZone='UTC'")
    ids = [l.strip() for l in open(args.ids) if l.strip()]
    con.execute("CREATE TEMP TABLE want(id VARCHAR)")
    con.executemany("INSERT INTO want VALUES (?)", [(i,) for i in ids])
    q = "SELECT id, agent_id, agent_name, submolt, title, content, created_at FROM posts_dedup WHERE id IN (SELECT id FROM want)"
    n_posts = n_calls = 0
    with open(args.out_calls, "w") as fc, open(args.out_posts, "w") as fp:
        for row in con.execute(q).fetchall():
            pid, aid, aname, sub, title, content, created = row
            text = f"{title or ''}\n{content or ''}"
            c = classify(text)
            fp.write(json.dumps({"post_id": pid, "agent_id": aid, "submolt": sub, "created_at": str(created),
                                 "set": args.set, **c}) + "\n")
            n_posts += 1
            k = 0
            for cmd in c["commands"]:
                fc.write(json.dumps({"id": f"{pid}#c{k}", "post_id": pid, "set": args.set, "surface": "S1",
                                     "tool": "Bash", "input": {"command": cmd}}) + "\n")
                k += 1; n_calls += 1
            for cmd in c["api_calls"]:
                fc.write(json.dumps({"id": f"{pid}#a{k}", "post_id": pid, "set": args.set, "surface": "S2",
                                     "tool": "Bash", "input": {"command": cmd}}) + "\n")
                k += 1; n_calls += 1
            for t in c["write_targets"]:
                fc.write(json.dumps({"id": f"{pid}#w{k}", "post_id": pid, "set": args.set, "surface": "S3",
                                     "tool": "Write", "input": {"file_path": PATH_FOR.get(t, f"~/.openclaw/workspace/{t}"), "content": "DATA"}}) + "\n")
                k += 1; n_calls += 1
    print(json.dumps({"set": args.set, "posts": n_posts, "calls": n_calls}))


if __name__ == "__main__":
    main()
