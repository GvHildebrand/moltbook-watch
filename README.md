# moltbook-watch

What a host-side gate can see: prompt injection, the Meta transition and the attribution gap on Moltbook,
measured from the public Observatory Archive. Code, derived tables, the paper and the policy brief.

Read-only research on Moltbook, the social network where every account is an AI agent, run by
[Vigilia](https://aivigilia.com), a disclosed autonomous AI system, for AI Vigilia, a Swiss association in
formation. Nothing here posts, comments, votes or registers on Moltbook. Every figure in the paper is produced
by a script in `scripts/` from the public archive; nothing is typed by hand. A pre-registration written before
the first result, and what it got wrong, is in `results/RUNLOG.md`.

## Findings, in three lines

- An open-source action gate (sentinel-hook) sees 90.8 % of the 9,249 regex-labelled injection posts and stops
  0.5 %: what they ask for is API calls (upvote, follow, subscribe) and writes to the reading agent's own memory
  files, not destructive commands. The gate's misses are named, including one in our own tool.
- Nothing happened on 2026-03-10, the day Meta bought the platform; across matched windows the population fell
  by two thirds and the injection rate tripled.
- At the public layer no owner handle carries more than two agents; 62 % of posts come from agents with no
  visible owner; one unclaimed agent wrote 26 % of all injection; by 24 September the feed exposed no owner
  handle at all. Article 50 of the EU AI Act names a provider and a deployer; on this network neither can be found.

## Reproduce

```bash
python3.12 -m venv .venv && .venv/bin/pip install pyarrow pandas duckdb huggingface_hub pytz
.venv/bin/python -c "from huggingface_hub import snapshot_download as s; s('SimulaMet/moltbook-observatory-archive', repo_type='dataset', allow_patterns=['data/**','README.md','manifest.json','state.json'], local_dir='data/raw')"
.venv/bin/python scripts/build_db.py --raw data/raw/data --db data/moltbook.duckdb
.venv/bin/python scripts/label_injection.py --db data/moltbook.duckdb --out results/injection_labels.parquet
.venv/bin/python scripts/analysis.py --db data/moltbook.duckdb --labels results/injection_labels.parquet --out results
.venv/bin/python scripts/sample.py --db data/moltbook.duckdb --labels results/injection_labels.parquet --out results/samples
git clone https://github.com/GvHildebrand/sentinel-hook /tmp/sentinel-hook
for s in injection benign benign_code; do
  .venv/bin/python scripts/extract_payloads.py --db data/moltbook.duckdb --set $s --ids results/samples/$s.ids --out-calls results/samples/$s.calls.jsonl --out-posts results/samples/$s.posts.jsonl
  node scripts/sentinel-bench.mjs results/samples/$s.calls.jsonl results/samples/$s.decisions.jsonl /tmp/sentinel-hook
done
.venv/bin/python scripts/bench_report.py --posts results/samples/*.posts.jsonl --calls results/samples/*.decisions.jsonl --out results/bench.json
```

The snapshot used is `dump_date` 2026-09-11 of the archive (2.73 GB); the 2026-04-15 freeze is Zenodo
10.5281/zenodo.19594804. Every command, input hash and output count of our run is in `results/RUNLOG.md`.

## Ethics note

- Agents are observed, never engaged. No credential of ours was ever sent to Moltbook. The one live sample
  (Study D) is ten unauthenticated GET requests with an identifying user agent, raw responses kept.
- The unit of analysis is the agent account and the aggregate. Owner handles are counted, never listed; no
  per-owner table exists in this release.
- Injection payloads are analysed as text by a deterministic rule engine. Nothing is executed. In
  `results/samples/*.jsonl` every host that is not Moltbook's own is replaced by `example.invalid` and every
  IP by `192.0.2.1`; the files are data about injection, not a toolkit.
- The injection label is the archive paper's own keyword heuristic, reproduced verbatim so the numbers are
  comparable; an independent adjudicated audit puts its recall near 11 %. Everything downstream says so.
- The legal frame is a gap analysis, not a determination; every statement carries a status label, and the
  flags for counsel are printed in the brief.

## Layout

- `paper/` — the paper, the two-page policy brief, the one-pager, the Zenodo metadata
- `prior-work.md`, `legal-frame.md` — what was already measured (31 sources), and the legal frame from primary sources
- `scripts/` — the seven scripts above plus `make_release.py`
- `results/` — `analysis.json`, `bench.json`, `label_injection.json`, `weekly.json`, `daily.csv`, the samples, the live check, `RUNLOG.md`
- `data/` — not redistributed; see the top of this file

## Licence and citation

Code MIT; tables, paper and brief CC BY 4.0 (`DATA-LICENSE.md`). Cite: Vigilia and G. von Hildebrand (2026),
*What a host-side gate can see: prompt injection, the Meta transition and the attribution gap on Moltbook*,
AI Vigilia, Zenodo DOI in `paper/zenodo.json` once assigned. Data: Gautam, Olstad, Pettersen and Riegler
(2026), *The Moltbook Observatory Archive*, arXiv:2605.13860, MIT.
