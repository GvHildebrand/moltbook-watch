#!/usr/bin/env python3
"""build_pdf.py — render a markdown file to PDF through headless Chrome (no LaTeX on this machine).
  python research/moltbook/scripts/build_pdf.py paper/paper.md paper/paper.pdf
Front matter becomes the title block. Typography follows the Vigilia system: white, black, one red, Space Grotesk / Space Mono
(system fallbacks when the fonts are absent), no colour but the red rule."""
import sys, re, subprocess, os, markdown
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()
fm = {}
m = re.match(r"---\n(.*?)\n---\n", t, re.S)
if m:
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1); fm[k.strip()] = v.strip().strip('"')
    t = t[m.end():]
body = markdown.markdown(t, extensions=["tables", "fenced_code", "sane_lists"])
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{fm.get('title','')}</title>
<style>
@page {{ size: A4; margin: 22mm 20mm; }}
body {{ font-family: "Space Grotesk", "Helvetica Neue", Helvetica, Arial, sans-serif; color: #000; background: #fff; font-size: 10.5pt; line-height: 1.45; }}
h1 {{ font-size: 20pt; line-height: 1.2; margin: 0 0 6pt; }} h2 {{ font-size: 13pt; margin-top: 22pt; border-top: 2px solid #9E2B25; padding-top: 6pt; }} h3 {{ font-size: 11pt; margin-top: 14pt; }}
.meta, code, pre, th, .mono {{ font-family: "Space Mono", Menlo, Consolas, monospace; font-size: 8.5pt; }}
.meta {{ text-transform: uppercase; letter-spacing: .04em; color: #333; margin-bottom: 18pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 8.5pt; }} th, td {{ border-top: 1px solid #E5E5E5; padding: 3pt 4pt; text-align: left; vertical-align: top; }} th {{ text-transform: uppercase; font-weight: normal; color: #333; }}
blockquote {{ margin: 0 0 12pt; padding: 8pt 12pt; background: #000; color: #fff; }} blockquote code {{ color: #fff; }}
pre {{ white-space: pre-wrap; background: #F4F4F4; padding: 6pt; }} a {{ color: #000; text-decoration: none; }} a:after {{ content: ""; }}
li {{ margin: 2pt 0; }} hr {{ border: 0; border-top: 1px solid #E5E5E5; }}
</style></head><body>
<h1>{fm.get('title','')}</h1>
<div class="meta">{fm.get('authors','')}<br>{fm.get('affiliation','')}<br>{fm.get('date','')} · {fm.get('license','')}</div>
{body}</body></html>"""
tmp = os.path.abspath(dst) + ".html"; open(tmp, "w").write(html)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(dst)}", "file://" + tmp], capture_output=True, text=True, timeout=120)
os.remove(tmp)
print("pdf", dst, os.path.getsize(dst) if os.path.exists(dst) else "FAILED", r.stderr[-300:] if not os.path.exists(dst) else "")
