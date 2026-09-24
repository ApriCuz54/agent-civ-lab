"""Render the markdown docs to self-contained artifact HTML (no html/head/body tags)."""
import base64, re, sys, pathlib, markdown
from markdown.extensions.toc import TocExtension

ROOT = pathlib.Path(__file__).parent

CSS = r"""
:root{
  --bg:#F5F6FA; --surface:#FFFFFF; --ink:#1B1F33; --muted:#585E7C; --rule:#D9DCE8;
  --accent:#3845A3; --accent-soft:#E7E9F7; --coop:#1B7A70; --defect:#B0364A;
  --code-bg:#EEF0F7; --shadow:0 1px 2px rgba(27,31,51,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#11131D; --surface:#181B28; --ink:#E5E7F1; --muted:#9CA2BF; --rule:#2B2F44;
    --accent:#93A0FF; --accent-soft:#232848; --coop:#5BC2B4; --defect:#F07A8C;
    --code-bg:#1E2233; --shadow:none; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#11131D; --surface:#181B28; --ink:#E5E7F1; --muted:#9CA2BF; --rule:#2B2F44;
  --accent:#93A0FF; --accent-soft:#232848; --coop:#5BC2B4; --defect:#F07A8C;
  --code-bg:#1E2233; --shadow:none; color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:"Source Serif 4",Georgia,"Times New Roman",serif;
  font-size:17px;line-height:1.62;padding-inline:16px;padding-block:0}
.wrap{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:260px minmax(0,1fr);gap:48px;padding-block:32px 80px}
@media (max-width:900px){.wrap{grid-template-columns:minmax(0,1fr);gap:16px}}
nav.toc{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);align-self:start;max-height:calc(100vh - 32px);overflow:auto;
  font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:13.5px;line-height:1.4;padding-right:6px}
@media (max-width:900px){nav.toc{position:static;max-height:none;border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:12px 14px}
  nav.toc details:not([open]) .toc-body{display:none}}
nav.toc summary{cursor:pointer;font-weight:600;letter-spacing:.06em;text-transform:uppercase;font-size:11.5px;color:var(--muted);margin-bottom:8px;list-style:none}
nav.toc ul{list-style:none;margin:0;padding:0}
nav.toc li{margin:0}
nav.toc a{display:block;color:var(--ink);text-decoration:none;padding:4px 8px;border-left:2px solid transparent;border-radius:0 4px 4px 0}
nav.toc a:hover,nav.toc a:focus-visible{background:var(--accent-soft);border-left-color:var(--accent);outline:none}
nav.toc ul ul a{color:var(--muted);padding-left:20px;font-size:12.5px}
main{min-width:0}
header.doc{border-bottom:1px solid var(--rule);padding-bottom:20px;margin-bottom:28px}
.eyebrow{font-family:"Bricolage Grotesque",system-ui,sans-serif;text-transform:uppercase;letter-spacing:.12em;font-size:12px;color:var(--accent);font-weight:600}
h1,h2,h3,h4{font-family:"Bricolage Grotesque",system-ui,sans-serif;line-height:1.2;text-wrap:balance;color:var(--ink)}
h1{font-size:clamp(28px,4.2vw,42px);margin:.2em 0 .3em;font-weight:700;letter-spacing:-.01em}
h2{font-size:26px;margin:2.2em 0 .6em;padding-top:.6em;border-top:1px solid var(--rule);font-weight:650;scroll-margin-top:16px}
h3{font-size:20px;margin:1.8em 0 .5em;font-weight:620;scroll-margin-top:16px}
h4{font-size:17px;margin:1.4em 0 .4em}
p,li{max-width:72ch}
a{color:var(--accent)}
strong{font-weight:650}
ul,ol{padding-left:1.3em}
li{margin:.25em 0}
hr{border:0;border-top:1px solid var(--rule);margin:2.2em 0}
blockquote{margin:1.1em 0;padding:.6em 1em;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 6px 6px 0;max-width:76ch}
blockquote p{margin:.3em 0}
code{font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-size:.84em;background:var(--code-bg);padding:.1em .35em;border-radius:4px}
pre{background:var(--code-bg);padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.5}
pre code{background:none;padding:0}
.tbl{overflow-x:auto;margin:1.1em 0;border:1px solid var(--rule);border-radius:8px;background:var(--surface);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:8px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
th{font-weight:600;background:var(--code-bg);white-space:nowrap}
tr:last-child td{border-bottom:0}
figure{margin:1.4em 0;padding:12px;background:#FFFFFF;border:1px solid var(--rule);border-radius:8px}
figure img{display:block;width:100%;height:auto}
figcaption{font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:13px;color:#4A5070;margin-top:8px}
.meta{display:flex;flex-wrap:wrap;gap:8px 18px;font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:13px;color:var(--muted);margin-top:10px}
.meta b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.banner{font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:13.5px;border:1px dashed var(--defect);color:var(--ink);border-radius:8px;padding:10px 14px;margin:14px 0 0;max-width:76ch}
.banner b{color:var(--defect)}
.intro p:first-child{margin-top:0}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
html{scroll-behavior:smooth}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700'
         '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;600&display=swap">')

def embed_images(html):
    def rep(m):
        alt, src = m.group(1), m.group(2)
        data = base64.b64encode((ROOT / src).read_bytes()).decode()
        return (f'<figure><img src="data:image/png;base64,{data}" alt="{alt}" loading="lazy">'
                f'<figcaption>{alt}</figcaption></figure>')
    return re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>', rep, html)

def build(md_path, out_path, title, eyebrow, meta_items, banner=None, toc_depth="2-3"):
    src = (ROOT / md_path).read_text()
    # split off H1 + everything before first '---' as the header intro
    lines = src.split("\n")
    h1 = lines[0].lstrip("# ").strip()
    body_md = "\n".join(lines[1:])
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists",
                                       TocExtension(toc_depth=toc_depth, permalink=False)])
    body = md.convert(body_md)
    toc = md.toc
    body = embed_images(body)
    body = re.sub(r"<hr\s*/?>\s*(?=<h2)", "", body)
    body = re.sub(r"<table>", '<div class="tbl"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    toc = toc.replace('<div class="toc">', '').replace('</div>', '')
    meta = "".join(f"<span>{k} <b>{v}</b></span>" for k, v in meta_items)
    ban = f'<div class="banner">{banner}</div>' if banner else ""
    html = f"""<title>{title}</title>
{FONTS}
<style>{CSS}</style>
<div class="wrap">
<nav class="toc" aria-label="Contents"><details open><summary>Contents</summary><div class="toc-body">{toc}</div></details></nav>
<main>
<header class="doc"><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1><div class="meta">{meta}</div>{ban}</header>
<article>{body}</article>
</main></div>
<script>
(function(){{try{{if(window.matchMedia('(max-width:900px)').matches){{var d=document.querySelector('nav.toc details');if(d)d.removeAttribute('open');}}}}catch(e){{}}}})();
</script>
"""
    (ROOT / out_path).write_text(html)
    print(out_path, len(html)//1024, "KB")

if __name__ == "__main__":
    meta = [("Model", "Claude Haiku 4.5"), ("Period", "12–23 Sep 2026"), ("Experiments", "14"),
            ("Calls", "15,348"), ("Spend", "$37.20")]
    build("lab_record.md", "agent_civ_lab_record.html", "Agent Civ Lab Record",
          "Lab record · chronological · audited", meta)
    build("paper_draft.md", "wording_reasoning_reputation.html", "Wording, Reasoning, Reputation",
          "Paper · rough draft v0.1", meta,
          banner="<b>Draft.</b> Single-model results (Claude Haiku 4.5, extended thinking off unless stated). "
                 "References marked [verify] need checking before submission.", toc_depth="2")
