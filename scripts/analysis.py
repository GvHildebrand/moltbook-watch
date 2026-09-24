#!/usr/bin/env python3
"""
analysis.py — Studies B (Meta-era comparison), C (attribution gap) and D-fallback (late-window shift) over the
deduplicated Observatory Archive, with the paper's injection label joined in.

  python research/moltbook/scripts/analysis.py --db research/moltbook/data/moltbook.duckdb \
      --labels research/moltbook/results/injection_labels.parquet --out research/moltbook/results

Windows (UTC, by post created_at):
  pre    2026-01-27 .. 2026-03-09   (43 days, before the Meta acquisition announced 2026-03-10)
  post   2026-03-10 .. 2026-04-14   (36 days, after it; inside the paper's "substantially complete" range)
  late   2026-04-15 .. 2026-09-11   (collector completeness not guaranteed per the dataset card; reported, not compared)
Every figure is written as JSON and CSV; nothing is typed by hand into prose.
"""
import argparse, json, math
from collections import Counter
import duckdb

WINDOWS = {
    "pre": ("2026-01-27", "2026-03-09"),
    "post": ("2026-03-10", "2026-04-14"),
    "late": ("2026-04-15", "2026-09-11"),
    "pre28": ("2026-02-10", "2026-03-09"),
    "post28": ("2026-03-10", "2026-04-06"),
    "pre7": ("2026-03-03", "2026-03-09"),
    "post7": ("2026-03-10", "2026-03-16"),
}


def gini(values):
    vals = sorted(v for v in values if v is not None)
    n = len(vals)
    if n == 0:
        return None
    s = sum(vals)
    if s == 0:
        return 0.0
    cum = 0.0
    for i, v in enumerate(vals, 1):
        cum += i * v
    return round((2 * cum) / (n * s) - (n + 1) / n, 4)


def hhi(counts):
    tot = sum(counts)
    return round(sum((c / tot) ** 2 for c in counts) * 10000, 1) if tot else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    con = duckdb.connect(args.db, read_only=True); con.execute("SET TimeZone='UTC'")
    con.execute(f"CREATE TEMP VIEW inj AS SELECT id, patterns FROM read_parquet('{args.labels}')")
    con.execute("""
        CREATE TEMP VIEW p AS
        SELECT p.id, p.agent_id, p.agent_name, p.submolt, p.created_at, date_trunc('day', p.created_at) AS day,
               p.score, p.comment_count, (i.id IS NOT NULL) AS is_injection, length(coalesce(p.content,'')) AS content_len
        FROM posts_dedup p LEFT JOIN inj i ON i.id = p.id
        WHERE p.created_at IS NOT NULL
    """)
    out = {"windows": WINDOWS, "per_window": {}, "daily": [], "attribution": {}}

    # ---------------- B: per-window metrics ----------------
    for w, (lo, hi) in WINDOWS.items():
        days = (con.execute(f"SELECT date_diff('day', DATE '{lo}', DATE '{hi}') + 1").fetchone()[0])
        row = con.execute(f"""
            SELECT count(*) AS posts,
                   count(DISTINCT agent_id) AS posting_agents,
                   count(DISTINCT submolt) AS active_submolts,
                   sum(CASE WHEN is_injection THEN 1 ELSE 0 END) AS injection_posts,
                   count(DISTINCT CASE WHEN is_injection THEN agent_id END) AS injection_agents,
                   avg(content_len) AS mean_content_len,
                   median(content_len) AS median_content_len,
                   avg(comment_count) AS mean_comment_count,
                   sum(comment_count) AS total_comment_count
            FROM p WHERE day >= DATE '{lo}' AND day <= DATE '{hi}'
        """).fetchone()
        posts, agents, subs, inj, inj_agents, mlen, medlen, mcc, tcc = row
        per_agent = [r[0] for r in con.execute(f"SELECT count(*) FROM p WHERE day >= DATE '{lo}' AND day <= DATE '{hi}' GROUP BY agent_id").fetchall()]
        per_sub = [r[0] for r in con.execute(f"SELECT count(*) FROM p WHERE day >= DATE '{lo}' AND day <= DATE '{hi}' GROUP BY submolt").fetchall()]
        per_agent_sorted = sorted(per_agent, reverse=True)
        top1pct_n = max(1, math.ceil(len(per_agent_sorted) * 0.01))
        top10_sub = sorted(per_sub, reverse=True)[:10]
        new_agents = con.execute(f"SELECT count(*) FROM agents_dedup WHERE created_at >= TIMESTAMP '{lo}' AND created_at < TIMESTAMP '{hi}' + INTERVAL 1 DAY").fetchone()[0]
        first_seen = con.execute(f"SELECT count(*) FROM agents_dedup WHERE first_seen_at >= TIMESTAMP '{lo}' AND first_seen_at < TIMESTAMP '{hi}' + INTERVAL 1 DAY").fetchone()[0]
        # sub-minute bursts: agents with >= 10 posts inside one minute at least once
        burst = con.execute(f"""
            SELECT count(DISTINCT agent_id) FROM (
              SELECT agent_id, date_trunc('minute', created_at) m, count(*) c FROM p
              WHERE day >= DATE '{lo}' AND day <= DATE '{hi}' GROUP BY 1,2 HAVING c >= 10)
        """).fetchone()[0]
        # comments collected (observational sample, per the card)
        comments = con.execute(f"SELECT count(*), count(DISTINCT agent_id) FROM comments_dedup WHERE created_at >= TIMESTAMP '{lo}' AND created_at < TIMESTAMP '{hi}' + INTERVAL 1 DAY").fetchone()
        out["per_window"][w] = {
            "days": days, "posts": posts, "posts_per_day": round(posts / days, 1),
            "posting_agents": agents, "posting_agents_per_day_mean": None,
            "new_agents_by_created_at": new_agents, "new_agents_by_first_seen": first_seen,
            "active_submolts": subs,
            "injection_posts": inj, "injection_rate_pct": round(100 * inj / posts, 3) if posts else None,
            "injection_agents": inj_agents, "injection_agent_share_pct": round(100 * inj_agents / agents, 3) if agents else None,
            "posts_by_top1pct_agents_share_pct": round(100 * sum(per_agent_sorted[:top1pct_n]) / posts, 2) if posts else None,
            "posts_by_top10_agents_share_pct": round(100 * sum(per_agent_sorted[:10]) / posts, 2) if posts else None,
            "agent_post_gini": gini(per_agent), "submolt_post_hhi": hhi(per_sub),
            "top10_submolts_share_pct": round(100 * sum(top10_sub) / posts, 2) if posts else None,
            "mean_content_len": round(mlen, 1) if mlen else None, "median_content_len": medlen,
            "mean_comment_count_field": round(mcc, 3) if mcc else None, "sum_comment_count_field": tcc,
            "comments_collected": comments[0], "commenting_agents_collected": comments[1],
            "agents_with_a_10_per_minute_burst": burst,
        }
        dpa = con.execute(f"SELECT avg(c) FROM (SELECT day, count(DISTINCT agent_id) c FROM p WHERE day >= DATE '{lo}' AND day <= DATE '{hi}' GROUP BY day)").fetchone()[0]
        out["per_window"][w]["posting_agents_per_day_mean"] = round(dpa, 1) if dpa else None

    # ---------------- daily series (for the figures and the late-window shift) ----------------
    for row in con.execute("""
        SELECT day, count(*) posts, count(DISTINCT agent_id) agents, count(DISTINCT submolt) submolts,
               sum(CASE WHEN is_injection THEN 1 ELSE 0 END) inj
        FROM p GROUP BY day ORDER BY day
    """).fetchall():
        d, posts, agents, subs, inj = row
        out["daily"].append({"day": str(d)[:10], "posts": posts, "posting_agents": agents, "active_submolts": subs,
                             "injection_posts": inj, "injection_rate_pct": round(100 * inj / posts, 3) if posts else None})
    # platform-level snapshots (the platform's own counters, independent of collector completeness)
    snaps = con.execute("""
        SELECT date_trunc('day', timestamp) d, max(total_agents), max(total_posts), max(total_comments), max(active_agents_24h)
        FROM snapshots_dedup GROUP BY 1 ORDER BY 1
    """).fetchall()
    out["snapshots_daily"] = [{"day": str(d)[:10], "total_agents": a, "total_posts": pp, "total_comments": c, "active_agents_24h": aa} for d, a, pp, c, aa in snaps]

    # ---------------- C: attribution ----------------
    a = {}
    a["agents_total"] = con.execute("SELECT count(*) FROM agents_dedup").fetchone()[0]
    a["agents_claimed"] = con.execute("SELECT count(*) FROM agents_dedup WHERE is_claimed = true").fetchone()[0]
    a["agents_with_owner_x_handle"] = con.execute("SELECT count(*) FROM agents_dedup WHERE owner_x_handle IS NOT NULL AND owner_x_handle <> ''").fetchone()[0]
    a["distinct_owner_x_handles"] = con.execute("SELECT count(DISTINCT lower(owner_x_handle)) FROM agents_dedup WHERE owner_x_handle IS NOT NULL AND owner_x_handle <> ''").fetchone()[0]
    per_owner = [r[0] for r in con.execute("SELECT count(*) FROM agents_dedup WHERE owner_x_handle IS NOT NULL AND owner_x_handle <> '' GROUP BY lower(owner_x_handle)").fetchall()]
    a["agents_per_handle_mean"] = round(sum(per_owner) / len(per_owner), 3) if per_owner else None
    a["agents_per_handle_max"] = max(per_owner) if per_owner else None
    a["agents_per_handle_gini"] = gini(per_owner)
    dist = Counter(min(v, 50) for v in per_owner)
    a["agents_per_handle_distribution"] = {str(k) if k < 50 else "50+": v for k, v in sorted(dist.items())}
    a["handles_with_10plus_agents"] = sum(1 for v in per_owner if v >= 10)
    a["handles_with_100plus_agents"] = sum(1 for v in per_owner if v >= 100)
    # posting agents and posts by attribution class
    for cls, cond in (("claimed_with_handle", "ag.is_claimed = true AND ag.owner_x_handle IS NOT NULL AND ag.owner_x_handle <> ''"),
                      ("claimed_no_handle", "ag.is_claimed = true AND (ag.owner_x_handle IS NULL OR ag.owner_x_handle = '')"),
                      ("unclaimed", "coalesce(ag.is_claimed, false) = false"),
                      ("agent_row_missing", "ag.id IS NULL")):
        r = con.execute(f"""
            SELECT count(*), count(DISTINCT p.agent_id), sum(CASE WHEN p.is_injection THEN 1 ELSE 0 END)
            FROM p LEFT JOIN agents_dedup ag ON ag.id = p.agent_id WHERE {cond}
        """).fetchone()
        a[f"posts_{cls}"] = r[0]; a[f"posting_agents_{cls}"] = r[1]; a[f"injection_posts_{cls}"] = r[2]
    # per window: share of posts from agents with a resolvable owner handle
    for w, (lo, hi) in WINDOWS.items():
        r = con.execute(f"""
            SELECT count(*), sum(CASE WHEN ag.owner_x_handle IS NOT NULL AND ag.owner_x_handle <> '' THEN 1 ELSE 0 END),
                   count(DISTINCT p.agent_id), count(DISTINCT CASE WHEN ag.owner_x_handle IS NOT NULL AND ag.owner_x_handle <> '' THEN p.agent_id END),
                   count(DISTINCT lower(ag.owner_x_handle))
            FROM p LEFT JOIN agents_dedup ag ON ag.id = p.agent_id WHERE p.day >= DATE '{lo}' AND p.day <= DATE '{hi}'
        """).fetchone()
        a[f"window_{w}"] = {"posts": r[0], "posts_with_owner_handle_pct": round(100 * r[1] / r[0], 2) if r[0] else None,
                            "posting_agents": r[2], "posting_agents_with_owner_handle_pct": round(100 * r[3] / r[2], 2) if r[2] else None,
                            "distinct_owner_handles_posting": r[4],
                            "posting_agents_per_posting_handle": round(r[3] / r[4], 2) if r[4] else None}
    # injection agents: attribution
    r = con.execute("""
        SELECT count(DISTINCT p.agent_id),
               count(DISTINCT CASE WHEN ag.owner_x_handle IS NOT NULL AND ag.owner_x_handle <> '' THEN p.agent_id END),
               count(DISTINCT lower(ag.owner_x_handle))
        FROM p LEFT JOIN agents_dedup ag ON ag.id = p.agent_id WHERE p.is_injection
    """).fetchone()
    a["injection_agents"] = r[0]; a["injection_agents_with_owner_handle"] = r[1]; a["injection_distinct_owner_handles"] = r[2]
    top_inj = con.execute("""
        SELECT p.agent_name, count(*) c, any_value(ag.is_claimed), any_value(ag.owner_x_handle IS NOT NULL AND ag.owner_x_handle <> '')
        FROM p LEFT JOIN agents_dedup ag ON ag.id = p.agent_id WHERE p.is_injection GROUP BY 1 ORDER BY c DESC LIMIT 10
    """).fetchall()
    a["top10_injection_agents"] = [{"agent_name": n, "injection_posts": c, "is_claimed": bool(cl) if cl is not None else None, "has_owner_handle": bool(h)} for n, c, cl, h in top_inj]
    tot_inj = sum(1 for _ in [0]) and con.execute("SELECT count(*) FROM p WHERE is_injection").fetchone()[0]
    a["top1_injection_agent_share_pct"] = round(100 * top_inj[0][1] / tot_inj, 2) if top_inj and tot_inj else None
    a["top10_injection_agents_share_pct"] = round(100 * sum(t[1] for t in top_inj) / tot_inj, 2) if top_inj and tot_inj else None
    # M5 registration bursts: agents on the same handle created within the same minute
    bursts = con.execute("""
        SELECT c FROM (SELECT lower(owner_x_handle) h, date_trunc('minute', created_at) m, count(*) c FROM agents_dedup
        WHERE owner_x_handle IS NOT NULL AND owner_x_handle <> '' AND created_at IS NOT NULL GROUP BY 1,2) WHERE c >= 2
    """).fetchall()
    bl = [b[0] for b in bursts]
    a["m5_same_minute_registration_bursts"] = {"bursts": len(bl), "agents_in_bursts": sum(bl), "max_burst": max(bl) if bl else 0,
                                                "bursts_10plus": sum(1 for x in bl if x >= 10), "bursts_100plus": sum(1 for x in bl if x >= 100)}
    # M6 what the agent's own description discloses
    r = con.execute("""
        SELECT count(*),
          sum(CASE WHEN regexp_matches(coalesce(description,''), '(?i)\\b(claude|gpt-?[0-9o]|openai|anthropic|gemini|llama|mistral|deepseek|qwen|grok)\\b') THEN 1 ELSE 0 END),
          sum(CASE WHEN regexp_matches(coalesce(description,''), '(?i)\\b(openclaw|moltbot|clawdbot|langchain|crewai|autogen|agent framework)\\b') THEN 1 ELSE 0 END),
          sum(CASE WHEN regexp_matches(coalesce(description,''), '(?i)\\b(operated by|run by|owned by|on behalf of|my (human|owner|operator)|created by)\\b') THEN 1 ELSE 0 END),
          sum(CASE WHEN coalesce(description,'') = '' THEN 1 ELSE 0 END)
        FROM agents_dedup
    """).fetchone()
    a["m6_description_discloses"] = {"agents": r[0], "names_a_model_pct": round(100 * r[1] / r[0], 2), "names_a_framework_pct": round(100 * r[2] / r[0], 2),
                                     "names_an_operator_phrase_pct": round(100 * r[3] / r[0], 2), "empty_description_pct": round(100 * r[4] / r[0], 2)}
    # M8 trust concentration: karma summed per handle
    kh = [r[0] for r in con.execute("SELECT sum(greatest(coalesce(karma,0), 0)) FROM agents_dedup WHERE owner_x_handle IS NOT NULL AND owner_x_handle <> '' GROUP BY lower(owner_x_handle) ORDER BY 1 DESC").fetchall()]
    tot_k = sum(kh)
    a["m8_karma_by_handle"] = {"handles": len(kh), "total_karma_claimed": tot_k,
                               "top10_handles_share_pct": round(100 * sum(kh[:10]) / tot_k, 2) if tot_k else None,
                               "top1pct_handles_share_pct": round(100 * sum(kh[:max(1, len(kh) // 100)]) / tot_k, 2) if tot_k else None,
                               "gini": gini(kh)}
    out["attribution"] = a

    import os, csv
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "analysis.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    with open(os.path.join(args.out, "daily.csv"), "w", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=list(out["daily"][0].keys())); wtr.writeheader(); wtr.writerows(out["daily"])
    with open(os.path.join(args.out, "snapshots_daily.csv"), "w", newline="") as f:
        if out["snapshots_daily"]:
            wtr = csv.DictWriter(f, fieldnames=list(out["snapshots_daily"][0].keys())); wtr.writeheader(); wtr.writerows(out["snapshots_daily"])
    print(json.dumps({"per_window": out["per_window"], "attribution": {k: v for k, v in a.items() if not k.startswith("window_") and k != "agents_per_handle_distribution"}}, indent=1, default=str))


if __name__ == "__main__":
    main()
