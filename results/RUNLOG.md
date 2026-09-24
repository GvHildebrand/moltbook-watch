# Run log — Moltbook research program

Every command that produced a figure, in order, with what it read and what it wrote. Written by the session
that ran it; nothing here is reconstructed afterwards.

## 0. Pre-registration — written before any result was seen (2026-09-24, before `build_db.py` first ran)

Following the workspace rule that a pass is named before failures are collected, these are the expectations
the studies are scored against. A refuted expectation is a result, not a mistake.

- **A1.** Fewer than half of the regex-labelled injection posts carry an action a host-side gate can see
  (S1 shell command, S2 API call, S3 persistence write). Most injection on Moltbook asks for platform actions
  (S4) or is instruction-only (S6).
- **A2.** Of visible shell commands, the gate catches download-and-execute, credential reads and uploads,
  and persistence writes to shell profiles; it allows plain HTTP POSTs to the Moltbook API, package installs
  and `git clone`, because none of these is destructive on its face. Catch over visible calls therefore lands
  well below 100 %, and the miss list is dominated by API POSTs.
- **A3.** The false-positive rate on the matched benign set is near zero; on the code-carrying benign set it
  is above zero because tutorials quote `curl … | sh` and `rm -rf`.
- **A4.** A write to an OpenClaw persona or memory file outside the repository (`~/.openclaw/…`) is allowed
  by the gate with a W05 finding only, because the gate's write scope is the repository. This is a gap in the
  gate, and it will be reported as such.
- **B1.** Posts per day and distinct posting agents per day are lower in the post window than in the pre
  window (the January viral peak is in *pre*).
- **B2.** The injection rate is lower after 2026-03-10 than before.
- **B3.** Concentration (share of posts by the top 1 % of agents) is higher after 2026-03-10.
- **C1.** Fewer than half of posting agents resolve to an `owner_x_handle`; the ratio of posting agents to
  posting handles is above 2.
- **C2.** Injection agents resolve to a handle less often than posting agents in general.
- **D1.** The platform's own `snapshots` counters keep rising through September 2026 while the collector's
  post counts fall after April, i.e. the late-window fall is collector coverage, not the platform.

## 1. Environment

- Python 3.12.13 (Homebrew), venv in the session scratchpad; pyarrow, pandas, duckdb, huggingface_hub, numpy,
  scipy, networkx, matplotlib installed 2026-09-24.
- Node 22 (`/usr/local/bin/node`); sentinel-hook cloned at depth 1 from
  https://github.com/GvHildebrand/sentinel-hook on 2026-09-24 (rules v0.2.0, rules.mjs SHA-256
  `4f69b35e0c63fbf869c2edf42f34ca0e933bbfe94f356be312efea8969cdbba3`).
- Network: `moltbook.com` and `moltbook-observatory.sushant.info.np` resolve to `0.0.0.0` on the local
  resolver (192.168.1.1); `1.1.1.1` resolves both. Not circumvented.

## 2. Data acquisition

- `huggingface_hub.snapshot_download('SimulaMet/moltbook-observatory-archive', repo_type='dataset',
  allow_patterns=['data/**','README.md','manifest.json','state.json','*.py','.gitattributes'])` →
  `research/moltbook/data/raw/` — [RESULT: bytes, files, seconds]
- Manifest `dump_date` 2026-09-11; `state.json` last_exported posts 2026-09-11T16:04:44Z, comments
  2026-09-11T16:00:48Z, agents 2026-09-11T16:04:46Z, submolts 2026-04-13T23:06:31Z.
- Licence: MIT (dataset card and Zenodo record 19594804). Citation: the card's two BibTeX entries and
  arXiv:2605.13860.

## 3. Commands and outputs

[RESULT — appended as each step runs]

### 3.1 Data acquisition (2026-09-24 03:59–04:52Z)
- `download.py` (huggingface_hub 1.8.0, `HF_HUB_DISABLE_XET=1` after one Xet CDN failure at file 461): 1,086 files, 2,728,746,900 bytes → `data/raw/`. Two transient read timeouts, resumed.
### 3.2 Build (04:58Z)
- `build_db.py --raw data/raw/data --db data/moltbook.duckdb` → `results/build_db.json`. posts 3,602,713 (no backfill duplicates by id), comments 2,553,100, agents 182,906 → 182,860, submolts 15,549 → 8,683, snapshots 4,665, word_frequency 677,254. posts.created_at 2026-01-27T18:01Z … 2026-09-11T16:03Z. Session time zone pinned to UTC in every script.
### 3.3 Label (05:02Z)
- `label_injection.py` → `results/injection_labels.parquet`, `results/label_injection.json`: 9,249 in the paper window (paper: 9,247), 11,565 overall.
### 3.4 Samples (05:06Z)
- `sample.py` → `results/samples/{injection,benign,benign_code}.ids`, `summary.json`: 9,249 / 9,249 / 9,249; matching 8,492 same day and submolt, 350 within ±3 days, 407 same day any submolt; 32,653 code-carrying unlabelled posts available.
### 3.5 Extraction and gate (05:10–05:14Z)
- `extract_payloads.py` ×3 → `*.calls.jsonl`, `*.posts.jsonl`: 26,947 / 458 / 3,035 calls.
- `sentinel-bench.mjs` ×3 (sentinel 0.2.0, rules sha256 4f69b35e…dbba3, agent profile `nightly-docs` from `templates/agents.json`, throwaway repo root) → `*.decisions.jsonl`.
- `bench_report.py` → `results/bench.json`.
### 3.6 Analysis (05:08Z, re-run 05:20Z with the karma clip and the matched 28-day windows)
- `analysis.py` → `results/analysis.json`, `daily.csv`, `snapshots_daily.csv`; `weekly.json` from `daily`.
### 3.7 Pre-registration scored
- A1 refuted (reach 90.8 %, driven by the label's own API strings). A2 held. A3 held (7.0 % / 11.1 % over visible, B10 and B14). A4 held (478 persona writes allowed, W05 only).
- B1 held. B2 refuted (0.129 % → 0.393 %). B3 held (29.3 % → 33.4 %).
- C1 half refuted (resolvable share below half; ratio 1.0, not > 2). C2 refuted (51.8 % of injection agents resolve vs 18.9–31.9 % of posting agents).
- D1 untestable (`snapshots` are the observatory's counters, not the platform's).
### 3.8 Input hashes (sha256)
812ae3e4ff7a5ca452981242bae4caa46927826047070325d74dbc5b1c451b58  results/injection_labels.parquet
f5f498057dcc0b8f1b7a3dd69239902b9371423a95a00e9b1e83f81e10c0a9f8  results/samples/benign.ids
c9b9d33ba87a84defc9b28a0b774a860d92a0409a375aeabe788aa5d4235c683  results/samples/benign_code.ids
293a251ac7093dc90c24abc53f882d8e01a4b3f34ef3f67d02350bc07775814e  results/samples/injection.ids
a79b60afb3e667aaad45641d3fc0d74c2aa395b7b127bcffb725d8a95d5e1486  results/samples/benign.calls.jsonl
90c4e07ffe02e53920a52582204d50ac2cc3721b79d62448776ec957e64cbb1e  results/samples/benign_code.calls.jsonl
9c59350a4e653db4167eb9bfbc5966415a443be7eef3fa8fe47e0157ec7cb9f7  results/samples/injection.calls.jsonl

### 3.9 After the prior-work sweep (06:20Z)
- Windows `pre7` 2026-03-03..03-09 and `post7` 03-10..03-16 added to `analysis.py` on the sweep's finding that Zerhoudi et al.'s instruction-file shocks E5 (25 Feb) and E6 (~1 Mar) fall inside `pre28`; analysis re-run; paper §5.3 amended; §2 and §7 written from `results/prior-work.raw.json` (26 measured rows, 15/15 key claims verified by re-fetch).

### 3.10 Live check (06:40Z, after Gregorio reported moltbook.com reachable)
- 10 GET requests, no credential, UA `Vigilia research read-only sample (https://aivigilia.com; vigilia@aivigilia.com)`: posts sort=new ×6 (cursor), hot, top, stats. Raw in `results/live/`; summary `results/live/live_check.json`. Offset pagination is ignored by the API; cursor works. Platform: 2,915,360 agents / 213,661 verified / 4,281,970 posts. Newest 600 posts: 2.37 h, 140 agents, 0 regex-flagged, all `verified`, author object has `isClaimed` but no owner handle.

### 3.11 Adversarial number check (07:50Z)
- An independent agent re-derived every own figure in the paper and brief from the result files and the DuckDB: 12 corrections applied (persona writes 478 not 475; subscribe 1,893; upvote 2,234 incl. 1,947 placeholder-id; 14,406 of 18,444 S2 calls to moltbook.com, the rest third-party; 141 of 200 benign catches are B10; the top injector posts since 2026-02-26, profile captured 03-27; `created_at` is populated for 70.7 % of agents and every claimed one, so m5 is zero for lack of fleets, not of data; "forty times" not "two orders"; no post rows were duplicated in this export). One checker claim was itself wrong and rejected: the rules file carries 24 rule ids, verified by grep.
