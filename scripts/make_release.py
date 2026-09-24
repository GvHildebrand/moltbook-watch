#!/usr/bin/env python3
"""
make_release.py — assemble the public release folder from the working tree, applying the ethics note:
  - code, README, paper, brief, one-pager, prior work, legal frame, run log: copied as is
  - derived tables (analysis, bench, labels summary, weekly, daily, samples summary): copied as is
  - post-id lists: copied (ids are public identifiers of public posts)
  - extracted calls and gate decisions: copied with every host that is not Moltbook's replaced by example.invalid,
    and bare IPs replaced by 192.0.2.1 (RFC 5737); 'localhost' kept
  - live raw responses: NOT copied (full post bodies); only live_check.json
  - injection_labels.parquet: NOT copied (per-post rows); regenerate with label_injection.py
  - never: raw Parquet, the DuckDB, any per-handle table

  python research/moltbook/scripts/make_release.py --src research/moltbook --dst research/moltbook/release
"""
import argparse, json, os, re, shutil

HOST = re.compile(r"(https?://)([^/\s\"'<>)\]]+)")
IP = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")


def redact(s: str) -> str:
    def h(m):
        host = m.group(2)
        if host.endswith("moltbook.com") or host.startswith("localhost") or host.startswith("127.0.0.1"):
            return m.group(0)
        return m.group(1) + "example.invalid"
    s = HOST.sub(h, s)
    return IP.sub(lambda m: "192.0.2.1" if not m.group(0).startswith("127.") else m.group(0), s)


def redact_jsonl(src, dst):
    n = 0
    with open(src) as f, open(dst, "w") as g:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if "input" in r and "command" in r["input"]:
                r["input"]["command"] = redact(r["input"]["command"])
            for k in ("commands", "api_calls"):
                if k in r:
                    r[k] = [redact(x) for x in r[k]]
            g.write(json.dumps(r) + "\n"); n += 1
    return n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
    a = ap.parse_args()
    if os.path.exists(a.dst):
        shutil.rmtree(a.dst)
    os.makedirs(a.dst)
    copy = ["prior-work.md", "legal-frame.md", "DATA-LICENSE.md",
            "paper/paper.md", "paper/policy-brief-attribution-gap.md", "paper/one-pager-funding.md",
            "paper/newsletter-items.md", "paper/instagram-videos.md", "paper/explainer-video.md", "paper/zenodo.json",
            "paper/paper.pdf", "paper/policy-brief-attribution-gap.pdf", "paper/one-pager-funding.pdf",
            "results/RUNLOG.md", "results/analysis.json", "results/bench.json", "results/build_db.json",
            "results/label_injection.json", "results/weekly.json", "results/daily.csv", "results/snapshots_daily.csv",
            "results/prior-work.raw.json", "results/legal-frame.raw.json", "results/live/live_check.json",
            "results/samples/summary.json", "results/samples/injection.ids", "results/samples/benign.ids", "results/samples/benign_code.ids",
            "results/samples-heldout/summary.json", "results/samples-heldout/injection.ids", "results/samples-heldout/benign.ids", "results/samples-heldout/benign_code.ids",
            "results/inventory-allowlist.json", "results/inventory-allowlist-dev.json"] + [f"results/bench-{sp}-{cfg}.json" for sp in ("samples", "samples-heldout") for cfg in ("0.2", "0.3", "0.3-allow", "0.3-allowdev")]
    for rel in copy:
        s = os.path.join(a.src, rel)
        if not os.path.exists(s):
            print("skip (absent):", rel); continue
        d = os.path.join(a.dst, rel); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d)
    shutil.copy2(os.path.join(a.src, "release-README.md"), os.path.join(a.dst, "README.md"))
    for f in os.listdir(os.path.join(a.src, "scripts")):
        if f.endswith((".py", ".mjs")):
            shutil.copy2(os.path.join(a.src, "scripts", f), os.path.join(a.dst, "scripts", f) if os.path.isdir(os.path.join(a.dst, "scripts")) else (os.makedirs(os.path.join(a.dst, "scripts"), exist_ok=True) or os.path.join(a.dst, "scripts", f)))
    counts = {}
    for split in ("samples", "samples-heldout"):
        os.makedirs(os.path.join(a.dst, "results", split), exist_ok=True)
        for st in ("injection", "benign", "benign_code"):
            for kind in ("calls", "decisions", "decisions-0.2", "decisions-0.3", "decisions-0.3-allow", "decisions-0.3-allowdev", "posts"):
                s = os.path.join(a.src, "results", split, f"{st}.{kind}.jsonl")
                if os.path.exists(s):
                    counts[f"{split}/{st}.{kind}"] = redact_jsonl(s, os.path.join(a.dst, "results", split, f"{st}.{kind}.jsonl"))
    os.makedirs(os.path.join(a.dst, "data"), exist_ok=True)
    open(os.path.join(a.dst, "data", "README.md"), "w").write("Raw data is not part of this release. Download the Moltbook Observatory Archive (MIT) from https://huggingface.co/datasets/SimulaMet/moltbook-observatory-archive as the top-level README says; the snapshot used is dump_date 2026-09-11 (Zenodo 10.5281/zenodo.19594804 holds the 2026-04-15 freeze).\n")
    print(json.dumps({"copied": len(copy), "redacted_jsonl": counts}, indent=1))


if __name__ == "__main__":
    main()
