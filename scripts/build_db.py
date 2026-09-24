#!/usr/bin/env python3
"""
build_db.py — build a DuckDB over the Observatory Archive Parquet files with one deduplicated table per
entity (the export appends a rolling 7-day backfill, so a row can appear under several dump_dates).

  python research/moltbook/scripts/build_db.py --raw research/moltbook/data/raw/data --db research/moltbook/data/moltbook.duckdb

Dedup rule: one row per primary key, the row from the LATEST dump_date, ties broken by the table's
incremental column (fetched_at / last_seen_at). Snapshots and word_frequency are time series and are kept whole
(deduplicated on their own keys only).
"""
import argparse, json, sys, time
import duckdb

TABLES = [
    # table, primary key, incremental column
    ("posts", "id", "fetched_at"),
    ("comments", "id", "fetched_at"),
    ("agents", "id", "last_seen_at"),
    ("submolts", "name", "first_seen_at"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()
    con = duckdb.connect(args.db)
    con.execute("SET threads TO 6")
    report = {}
    for tbl, key, inc in TABLES:
        t0 = time.time()
        con.execute(f"CREATE OR REPLACE VIEW {tbl}_raw AS SELECT * FROM read_parquet('{args.raw}/{tbl}/*.parquet', union_by_name=true, filename=true)")
        cols = [r[0] for r in con.execute(f"DESCRIBE {tbl}_raw").fetchall()]
        order = "dump_date DESC" if "dump_date" in cols else "filename DESC"
        if inc in cols:
            order += f", {inc} DESC NULLS LAST"
        con.execute(f"""
            CREATE OR REPLACE TABLE {tbl}_dedup AS
            SELECT * EXCLUDE (rn) FROM (
              SELECT *, row_number() OVER (PARTITION BY {key} ORDER BY {order}) AS rn FROM {tbl}_raw
            ) WHERE rn = 1
        """)
        raw_n = con.execute(f"SELECT count(*) FROM {tbl}_raw").fetchone()[0]
        n = con.execute(f"SELECT count(*) FROM {tbl}_dedup").fetchone()[0]
        report[tbl] = {"raw_rows": raw_n, "dedup_rows": n, "columns": cols, "seconds": round(time.time() - t0, 1)}
        print(tbl, report[tbl], file=sys.stderr)
    for tbl in ("snapshots", "word_frequency"):
        con.execute(f"CREATE OR REPLACE VIEW {tbl}_raw AS SELECT * FROM read_parquet('{args.raw}/{tbl}/*.parquet', union_by_name=true, filename=true)")
        cols = [r[0] for r in con.execute(f"DESCRIBE {tbl}_raw").fetchall()]
        key = "id" if "id" in cols else ("word, hour" if "word" in cols else "*")
        if key != "*":
            con.execute(f"CREATE OR REPLACE TABLE {tbl}_dedup AS SELECT * EXCLUDE (rn) FROM (SELECT *, row_number() OVER (PARTITION BY {key} ORDER BY filename DESC) rn FROM {tbl}_raw) WHERE rn = 1")
        else:
            con.execute(f"CREATE OR REPLACE TABLE {tbl}_dedup AS SELECT DISTINCT * FROM {tbl}_raw")
        report[tbl] = {"raw_rows": con.execute(f"SELECT count(*) FROM {tbl}_raw").fetchone()[0],
                       "dedup_rows": con.execute(f"SELECT count(*) FROM {tbl}_dedup").fetchone()[0], "columns": cols}
        print(tbl, report[tbl], file=sys.stderr)
    # date ranges
    for tbl, col in (("posts", "created_at"), ("comments", "created_at"), ("agents", "created_at"), ("agents", "first_seen_at")):
        lo, hi = con.execute(f"SELECT min({col}), max({col}) FROM {tbl}_dedup").fetchone()
        report.setdefault("ranges", {})[f"{tbl}.{col}"] = [str(lo), str(hi)]
    print(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
