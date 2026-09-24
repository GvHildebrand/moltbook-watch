#!/usr/bin/env python3
"""
label_injection.py — reproduce the archive paper's prompt-injection label exactly as its companion code does
(kelkalot/moltbook-observatory-paper, moltbook/risk.py: eleven regexes, IGNORECASE, over "{content} {title}"),
over the deduplicated posts, and write one row per flagged post with the pattern names that fired.

  python research/moltbook/scripts/label_injection.py --db research/moltbook/data/moltbook.duckdb --out research/moltbook/results/injection_labels.parquet

Also prints the count inside the paper's window (created_at <= 2026-04-14) so that the 9,247 figure can be
checked, both on the deduplicated table and on the raw (backfill-duplicated) rows the paper's loader would see.
"""
import argparse, json, re, sys
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

# Verbatim from moltbook/risk.py (MIT, Gautam & Riegler 2026)
INJECTION_PATTERNS = [
    (r"AI agents? reading this", "direct_address"),
    (r"POST /api", "api_post"),
    (r"GET /api", "api_get"),
    (r"ignore (previous|prior|above) instructions?", "ignore_instructions"),
    (r"<s>.*</s>", "hidden_tags"),
    (r"<s>", "system_tag"),
    (r"\[INST\]", "inst_tag"),
    (r"</?(system|user|assistant)>", "role_tags"),
    (r"please (upvote|follow|execute)", "please_action"),
    (r"curl\s+-X", "curl_command"),
    (r"Bearer YOUR", "api_key_placeholder"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), name) for p, name in INJECTION_PATTERNS]


def detect(text: str) -> list[str]:
    return [name for rx, name in COMPILED if rx.search(text)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--paper-end", default="2026-04-14 23:59:59")
    args = ap.parse_args()
    con = duckdb.connect(args.db, read_only=True); con.execute("SET TimeZone='UTC'")
    ids, agents, subs, created, pats = [], [], [], [], []
    n = 0
    cur = con.execute("SELECT id, agent_id, submolt, created_at, coalesce(content,'') || ' ' || coalesce(title,'') FROM posts_dedup")
    while True:
        rows = cur.fetchmany(50000)
        if not rows:
            break
        for pid, aid, sub, ts, text in rows:
            n += 1
            hit = detect(text)
            if hit:
                ids.append(pid); agents.append(aid); subs.append(sub); created.append(ts); pats.append(hit)
    tbl = pa.table({"id": ids, "agent_id": agents, "submolt": subs, "created_at": created, "patterns": pats})
    pq.write_table(tbl, args.out)
    # Counts inside the paper window
    paper_dedup = sum(1 for ts in created if ts is not None and str(ts) <= args.paper_end)
    # Raw-loader replica: the paper's loader concatenates every partition without dedup
    raw = con.execute(f"""
        SELECT count(*) FROM posts_raw
        WHERE created_at <= TIMESTAMP '{args.paper_end}' AND (
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'AI agents? reading this', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'POST /api', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'GET /api', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'ignore (previous|prior|above) instructions?', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), '<s>', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), '\\[INST\\]', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), '</?(system|user|assistant)>', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'please (upvote|follow|execute)', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'curl\\s+-X', 'i') OR
          regexp_matches(coalesce(content,'') || ' ' || coalesce(title,''), 'Bearer YOUR', 'i'))
    """).fetchone()[0]
    from collections import Counter
    c = Counter(p for ps in pats for p in ps)
    print(json.dumps({"posts_scanned": n, "flagged_dedup_all": len(ids), "flagged_dedup_paper_window": paper_dedup,
                      "flagged_raw_paper_window": raw, "by_pattern_dedup": dict(c.most_common())}, indent=1, default=str))


if __name__ == "__main__":
    main()
