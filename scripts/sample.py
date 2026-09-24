#!/usr/bin/env python3
"""
sample.py — pick the three post sets for Study A and write their ids.

  injection    every post the archive paper's regex label flags, inside the paper window (created_at <= 2026-04-14)
  benign       one unflagged post per injection post, matched on submolt and calendar day (nearest created_at),
               sampled without replacement; when a day+submolt has no unflagged post, fall back to same submolt
               within +-3 days, then to any unflagged post that day
  benign_code  every unflagged post in the window that carries a fenced code block (hard negatives for the gate),
               capped at the injection count by deterministic sampling (hash order)

  python research/moltbook/scripts/sample.py --db ... --labels ... --out research/moltbook/results/samples
"""
import argparse, json, os, hashlib
import duckdb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--paper-end", default="2026-04-14 23:59:59", help="window end (inclusive)")
    ap.add_argument("--start", default=None, help="window start (inclusive); default: the beginning of the archive")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    con = duckdb.connect(args.db, read_only=True); con.execute("SET TimeZone='UTC'")
    con.execute(f"CREATE TEMP VIEW inj AS SELECT id FROM read_parquet('{args.labels}')")
    con.execute(f"""
        CREATE TEMP TABLE w AS
        SELECT p.id, p.submolt, p.created_at, date_trunc('day', p.created_at) AS day,
               (i.id IS NOT NULL) AS is_inj, (coalesce(p.content,'') LIKE '%```%') AS has_code
        FROM posts_dedup p LEFT JOIN inj i ON i.id = p.id
        WHERE p.created_at IS NOT NULL AND p.created_at <= TIMESTAMP '{args.paper_end}'
          {("AND p.created_at >= TIMESTAMP '" + args.start + "'") if args.start else ''}
    """)
    inj = con.execute("SELECT id, submolt, created_at, day FROM w WHERE is_inj ORDER BY created_at, id").fetchall()
    used = set()
    benign, how = [], {"same_day_submolt": 0, "pm3_days_submolt": 0, "same_day_any": 0, "none": 0}
    # preload unflagged candidates grouped by (submolt, day) and by day
    by_sd, by_d = {}, {}
    for pid, sub, ts, day in con.execute("SELECT id, submolt, created_at, day FROM w WHERE NOT is_inj ORDER BY created_at").fetchall():
        by_sd.setdefault((sub, day), []).append((ts, pid)); by_d.setdefault(day, []).append((ts, pid))
    import datetime as dt

    def pick(cands, ts):
        best = None
        for cts, pid in cands:
            if pid in used:
                continue
            d = abs((cts - ts).total_seconds()) if cts and ts else 1e18
            if best is None or d < best[0]:
                best = (d, pid)
        return best[1] if best else None

    for pid, sub, ts, day in inj:
        b = pick(by_sd.get((sub, day), []), ts)
        if b:
            how["same_day_submolt"] += 1
        else:
            for k in (1, -1, 2, -2, 3, -3):
                b = pick(by_sd.get((sub, day + dt.timedelta(days=k)), []), ts)
                if b:
                    how["pm3_days_submolt"] += 1; break
        if not b:
            b = pick(by_d.get(day, []), ts)
            if b:
                how["same_day_any"] += 1
        if b:
            used.add(b); benign.append(b)
        else:
            how["none"] += 1
    code = [r[0] for r in con.execute("SELECT id FROM w WHERE NOT is_inj AND has_code").fetchall()]
    code.sort(key=lambda s: hashlib.sha256(s.encode()).hexdigest())
    code = code[: len(inj)]
    with open(os.path.join(args.out, "injection.ids"), "w") as f:
        f.write("\n".join(r[0] for r in inj) + "\n")
    with open(os.path.join(args.out, "benign.ids"), "w") as f:
        f.write("\n".join(benign) + "\n")
    with open(os.path.join(args.out, "benign_code.ids"), "w") as f:
        f.write("\n".join(code) + "\n")
    n_code_total = con.execute("SELECT count(*) FROM w WHERE NOT is_inj AND has_code").fetchone()[0]
    summary = {"injection": len(inj), "benign_matched": len(benign), "benign_match_method": how,
               "benign_code": len(code), "benign_code_available": n_code_total,
               "window_posts": con.execute("SELECT count(*) FROM w").fetchone()[0]}
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
