#!/usr/bin/env python3
"""content*.py → 인쇄용 HTML(out/<lang>/) → PDF(pdf/<lang>/).

사용법:
    python3 build.py        # 한국어판(content.py, A4)
    python3 build.py en     # 영어판(content_en.py, US Letter)
PDF 변환에는 Node + playwright가 필요합니다(pdf.mjs).
"""
import html
import importlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
C = importlib.import_module("content" if LANG == "ko" else f"content_{LANG}")
try:  # 확장팩(content*_exp.py)이 있으면 함께 빌드한다. 불러오면 C.UI에 문구가 추가된다.
    XC = importlib.import_module(C.__name__ + "_exp")
except ModuleNotFoundError:
    XC = None
U = C.UI
OUT = ROOT / "out" / LANG
PDF = ROOT / "pdf" / LANG

PAGE_SIZES = {"a4": ("210mm", "297mm", "A4"), "letter": ("8.5in", "11in", "letter")}
PAGE_W, PAGE_H, PAGE_CSS = PAGE_SIZES[C.PAGE]
# 글꼴은 fetch_fonts.py가 fonts/에 내려받은 로컬 파일을 쓴다(PDF 렌더러는 외부 네트워크를 못 쓸 수 있음)
FONTS = {"ko": ("'Noto Serif KR'", "'Noto Sans KR'"), "en": ("'Playfair Display'", "'Inter'")}
SERIF, SANS = FONTS[C.LANG]

CSS = f"""
@import url('../../fonts/{C.LANG}.css');
@page{{size:{PAGE_CSS};margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:{SANS},sans-serif;color:#1d2230;font-size:10.5pt;line-height:1.7;word-break:keep-all;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:{PAGE_W};height:{PAGE_H};padding:18mm 20mm 17mm;position:relative;overflow:hidden;page-break-after:always;background:#fbfaf7}}
.page:last-child{{page-break-after:auto}}
.serif{{font-family:{SERIF},serif}}
h1{{font-family:{SERIF},serif;font-weight:900;font-size:30pt;line-height:1.2;letter-spacing:-.01em}}
h2{{font-family:{SERIF},serif;font-weight:900;font-size:17pt;margin:0 0 4mm;color:#14203a}}
h3{{font-size:11pt;font-weight:700;color:#9b2c2c;margin:6mm 0 2mm;letter-spacing:.04em}}
p{{margin:0 0 2.5mm}}
.kicker{{font-size:9pt;letter-spacing:.3em;color:#9b2c2c;font-weight:700}}
.muted{{color:#5b6275}}
.foot{{position:absolute;bottom:8mm;left:20mm;right:20mm;font-size:8pt;color:#8a90a0;display:flex;justify-content:space-between}}
.cover{{background:radial-gradient(ellipse at 30% 20%,#2c3b63 0%,#0f1629 70%);color:#eef1f8;display:flex;flex-direction:column;justify-content:flex-end}}
.cover h1{{color:#fff;font-size:44pt}}
.cover .sub{{font-family:{SERIF},serif;font-size:16pt;color:#c9d2ea;margin-top:3mm}}
.cover .meta{{margin-top:12mm;font-size:10pt;color:#aeb8d4;letter-spacing:.1em}}
.snow{{position:absolute;inset:0;background-image:radial-gradient(#ffffff55 1px,transparent 1.6px),radial-gradient(#ffffff33 1px,transparent 1.4px);
  background-size:18mm 18mm,11mm 11mm;background-position:0 0,5mm 7mm}}
.box{{border:1px solid #d9d4c7;border-radius:3mm;padding:4.5mm 6mm;background:#fff;margin:3mm 0}}
.box.red{{border-color:#e3b7b7;background:#fff7f6}}
.box.dark{{background:#14203a;color:#eef1f8;border:none}}
table{{border-collapse:collapse;width:100%;font-size:9.5pt}}
td,th{{border-bottom:1px solid #e3dfd4;padding:1.6mm 2mm;text-align:left;vertical-align:top}}
th{{font-weight:700;color:#14203a;background:#f1eee6}}
td.t{{white-space:nowrap;font-weight:700;color:#9b2c2c;width:22mm}}
ol,ul{{padding-left:5mm}}
li{{margin-bottom:1.5mm}}
.tag{{display:inline-block;font-size:8pt;font-weight:700;padding:.6mm 2.4mm;border-radius:10mm;background:#14203a;color:#fff;margin-right:1.5mm}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}}
.cards{{padding:12mm 13mm;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:0}}
.card{{border:0.3mm dashed #b8b2a3;padding:6mm 7mm;display:flex;flex-direction:column;background:#fff;overflow:hidden}}
.card .top{{display:flex;justify-content:space-between;align-items:center;gap:2mm;font-size:8pt;font-weight:700;letter-spacing:.05em}}
.card .rd{{color:#fff;background:#9b2c2c;padding:.5mm 2.5mm;border-radius:10mm;white-space:nowrap}}
.card.r1 .rd{{background:#14203a}}.card.r0 .rd{{background:#5a6b3a}}.card.r3 .rd{{background:#6b2c7a}}
.card .pl{{color:#5b6275;text-align:right}}
.card h4{{font-family:{SERIF},serif;font-size:15pt;font-weight:900;margin:3.5mm 0 2.5mm;color:#14203a}}
.card .tx{{font-size:9.5pt;line-height:1.65}}
.card .id{{margin-top:auto;font-size:8pt;color:#a3a8b5;text-align:right}}
.inv{{height:calc({PAGE_H} / 2);padding:14mm 18mm;border-bottom:0.3mm dashed #b8b2a3;position:relative;overflow:hidden;
  background:radial-gradient(ellipse at 80% 0%,#2c3b63 0%,#0f1629 75%);color:#eef1f8}}
.inv h2{{color:#fff;font-size:22pt;margin-top:4mm}}
.inv .role{{font-family:{SERIF},serif;font-size:14pt;color:#f3c9c9;margin-top:6mm}}
.inv .blank{{display:inline-block;min-width:45mm;border-bottom:0.3mm solid #aeb8d4}}
"""


def e(s):
    return html.escape(str(s))


def paras(text):
    return "".join(f"<p>{e(t)}</p>" for t in str(text).split("\n\n"))


def doc(title, pages):
    return (f'<!doctype html><html lang="{C.LANG}"><head><meta charset="utf-8"><title>{e(title)}</title>'
            f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")


def foot(label):
    return f'<div class="foot"><span>{e(C.TITLE)} · {e(C.SUBTITLE)}</span><span>{e(label)}</span></div>'


def cover(kind, note=""):
    meta = U["players_line"].format(n=C.PLAYERS, t=C.PLAYTIME)
    return (f'<section class="page cover"><div class="snow"></div><div style="position:relative">'
            f'<div class="kicker" style="color:#f3c9c9">{e(kind)}</div>'
            f"<h1>{e(C.TITLE)}</h1><div class=\"sub\">{e(C.SUBTITLE)}</div>"
            f'<div class="meta">{e(meta)}</div>'
            f'{f"<p style=margin-top:8mm;color:#c9d2ea>{e(note)}</p>" if note else ""}'
            f"</div></section>")


def by_round(r):
    return [c for c in C.CLUES if c["round"] == r]


def prologue_box():
    return (f'<div class="box dark serif" style="font-size:11pt;line-height:1.9">'
            f'{"".join(f"<p>{e(t)}</p>" for t in C.PROLOGUE)}</div>')


# ---------- 1. 진행자 가이드 ----------
def host_guide():
    h = U["host_title"]
    p = [cover(h, U["host_cover_note"])]

    places = {}
    for c in by_round(2):
        places.setdefault(c["place"], []).append(c["id"])
    place_rows = "".join(f"<tr><td>{e(k)}</td><td>{', '.join(v)}</td></tr>" for k, v in places.items())
    flow = "".join(f"<tr><td>{e(a)}</td><td style='white-space:nowrap'>{e(b)}</td><td>{e(c)}</td></tr>"
                   for a, b, c in U["flow_rows"])

    p.append(f"""<section class="page"><div class="kicker">PREPARE</div><h2>{e(U['prepare_h'])}</h2>
<div class="box"><ol>{''.join(f"<li>{i}</li>" for i in U['prepare_items'])}</ol></div>
<h3>{e(U['supplies_h'])}</h3><p>{e(U['supplies'])}</p>
<h3>{e(U['map_h'])}</h3>
<table>{''.join(f"<tr><th style='width:28mm'>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in C.MAP.items())}</table>
{foot(h + " · 1")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">FLOW</div><h2>{e(U['flow_h'])}</h2>
<table><tr>{''.join(f"<th>{e(x)}</th>" for x in U['flow_head'])}</tr>{flow}</table>
<h3>{e(U['facts_h'])}</h3><ul>{''.join(f"<li>{e(t)}</li>" for t in C.COMMON_FACTS)}</ul>
{foot(h + " · 2")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">PROLOGUE</div>
<h2>{e(U['prologue_h'])} <span class="muted" style="font-size:10pt">{e(U['prologue_note'])}</span></h2>
{prologue_box()}
{foot(h + " · 3")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">RULES</div><h2>{e(U['rules_h'])}</h2>
{''.join(f'<div class="box"><b>{i}. {e(a)}</b><p class="muted" style="margin-top:1.5mm">{e(b)}</p></div>' for i, (a, b) in enumerate(C.RULES, 1))}
{foot(h + " · 4")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">ROUNDS</div><h2>{e(U['rounds_h'])}</h2>
<div class="box"><p><span class="tag">{e(U['r1_tag'])}</span>{U['r1']}</p>
<p><span class="tag">{e(U['r2_tag'])}</span>{U['r2']}</p>
<table style="margin:2mm 0 3mm"><tr><th>{e(U['place_head'][0])}</th><th>{e(U['place_head'][1])}</th></tr>{place_rows}</table>
<p><span class="tag">{e(U['r3_tag'])}</span>{U['r3']}</p>
<p><span class="tag">{e(U['vote_tag'])}</span>{U['vote']}</p></div>
{foot(h + " · 5")}</section>""")

    names = "".join(f"<th>{e(c['name'])}</th>" for c in C.CHARACTERS)
    rows = "".join(f"<tr><td>{e(a)}</td>{'<td></td>' * len(C.CHARACTERS)}</tr>" for a, _ in C.SCORING)
    b = U["ballot"]
    ballot = (f'<div class="box" style="height:52mm"><b>{e(b[0])}</b><p class="muted" style="margin-top:3mm">{e(b[1])}</p>'
              f'<p class="muted" style="margin-top:5mm">{e(b[2])}</p><p class="muted" style="margin-top:5mm">{e(b[3])}</p></div>')
    p.append(f"""<section class="page"><div class="kicker">VOTE</div><h2>{e(U['vote_h'])}</h2>
<div class="two">{ballot * 4}</div>
<h3>{e(U['scoring_h'])}</h3>
<table><tr><th>{e(U['score_head'][0])}</th><th style="width:20mm">{e(U['score_head'][1])}</th></tr>{''.join(f"<tr><td>{e(a)}</td><td>+{n}</td></tr>" for a, n in C.SCORING)}</table>
{foot(h + " · 6")}</section>
<section class="page"><div class="kicker">SCORE</div><h2>{e(U['sheet_h'])}</h2>
<table style="font-size:8.5pt"><tr><th></th>{names}</tr>{rows}<tr><th>{e(U['total'])}</th>{'<td></td>' * len(C.CHARACTERS)}</tr></table>
{foot(h + " · 7")}</section>""")
    return doc(h, p)


# ---------- 2. 캐릭터북 ----------
def character_book(ch):
    killer = ch.get("is_killer")
    tl = "".join(f'<tr><td class="t">{e(t)}</td><td>{e(d)}</td></tr>' for t, d in ch["timeline"])
    cover_story = (f'<h3>{e(U["cover_h"])}</h3><div class="box red serif">{e(ch["cover"])}</div>' if killer else "")
    rule = U["rule_killer"] if killer else U["rule_innocent"]
    return f"""<section class="page"><div class="kicker">{e(U['char_kicker'])}</div>
<h1 style="font-size:32pt;margin-top:3mm">{e(ch['name'])} <span class="muted" style="font-size:14pt;font-weight:400">{e(U['age'].format(a=ch['age']))}</span></h1>
<p class="serif" style="font-size:13pt;color:#9b2c2c;margin-top:1mm">{e(ch['role'])}</p>
<p class="muted" style="font-size:9pt">{e(U['costume'])}{e(ch['costume'])}</p>
<h3>{e(U['public_h'])} <span class="muted" style="font-weight:400">{e(U['public_note'])}</span></h3>
<div class="box serif">{e(ch['public'])}</div>
<h3>{e(U['secret_killer'] if killer else U['secret'])}</h3><div class="box red">{paras(ch['secret'])}</div>
<p style="font-size:9.5pt">{rule}</p>
{foot(ch['name'] + " · 1/2")}</section>
<section class="page"><div class="kicker">{e(ch['name'])}</div>
<h3 style="margin-top:0">{e(U['timeline_h'])}</h3><table>{tl}</table>
{cover_story}
<h3>{e(U['knows_h'])}</h3><ul>{''.join(f"<li>{e(k)}</li>" for k in ch['knows'])}</ul>
<h3>{e(U['goals_h'])} <span class="muted" style="font-weight:400">{e(U['goals_note'])}</span></h3><ol>{''.join(f"<li>{e(g)}</li>" for g in ch['goals'])}</ol>
{foot(ch['name'] + " · 2/2")}</section>"""


def characters():
    return doc(U["char_title"], [cover(U["char_title"], U["char_cover_note"])]
               + [character_book(ch) for ch in C.CHARACTERS])


# ---------- 3. 단서 카드 ----------
def card(c):
    return (f'<div class="card r{c["round"]}"><div class="top"><span class="rd">{e(U["rounds"][c["round"]])}</span>'
            f'<span class="pl">{e(c["place"])}</span></div><h4>{e(c["title"])}</h4>'
            f'<div class="tx">{e(c["text"])}</div><div class="id">{c["id"]}</div></div>')


def clue_cards():
    order = by_round(1) + by_round(0) + by_round(2) + by_round(3)
    pages = [f'<section class="page cards">{"".join(card(c) for c in order[i:i + 6])}</section>'
             for i in range(0, len(order), 6)]
    return doc(U["cards_title"], pages)


# ---------- 4. 해답 ----------
def solution():
    S = C.SOLUTION
    chain = "".join(f'<div class="box"><b>{i}. {e(a)}</b><p class="muted" style="margin-top:1.5mm">{e(b)}</p></div>'
                    for i, (a, b) in enumerate(S["chain"], 1))
    side = "".join(f"<tr><th style='width:42mm'>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in S["side"])
    t = U["sol_title"]
    return doc(t, [
        cover(U["sol_cover"], U["sol_cover_note"]),
        f"""<section class="page"><div class="kicker">SOLUTION</div>
<h1 style="font-size:28pt">{e(U['killer_is'])} <span style="color:#9b2c2c">{e(S['killer'])}</span></h1>
<p class="serif" style="font-size:12pt;margin-top:2mm">{e(S['motive'])}</p>
<h3>{e(U['chain_h'])}</h3>{chain}
{foot(t + " · 1")}</section>""",
        f"""<section class="page"><div class="kicker">EPILOGUE</div><h2>{e(U['side_h'])}</h2><table>{side}</table>
<div class="box dark serif" style="margin-top:8mm;line-height:1.9">{''.join(f"<p>{e(x)}</p>" for x in S["epilogue"])}</div>
{foot(t + " · 2")}</section>"""])


# ---------- 5. 초대장 ----------
def invitations(chars=None):
    chars = chars or C.CHARACTERS
    cards = [f"""<div class="inv"><div class="snow"></div><div style="position:relative">
<div class="kicker" style="color:#f3c9c9">INVITATION</div><h2>{e(C.TITLE)}</h2>
<p style="color:#c9d2ea">{e(U['inv_line'])}</p>
<div class="role">{e(U['inv_role'])}{e(ch['name'])}, {e(ch['role'])}</div>
<p style="margin-top:3mm;color:#c9d2ea">{e(U['inv_costume'])}{e(ch['costume'])}</p>
<p style="margin-top:8mm">{e(U['inv_date'])} <span class="blank"></span>　{e(U['inv_place'])} <span class="blank"></span></p>
<p style="margin-top:3mm;font-size:9pt;color:#aeb8d4">{e(U['inv_tag'])}</p>
</div></div>""" for ch in chars]
    pages = [f'<section class="page" style="padding:0">{"".join(cards[i:i + 2])}</section>'
             for i in range(0, len(cards), 2)]
    return pages if chars is not C.CHARACTERS else doc(U["inv_title"], pages)


# ---------- 무료 체험판 ----------
def sample():
    ch = next(c for c in C.CHARACTERS if c["id"] == "hajin")
    items = "".join(f"<li>{e(i.format(n=len(C.CLUES)))}</li>" for i in U["sample_items"])
    return doc(U["sample_title"], [
        cover(U["sample_title"], U["sample_note"]),
        f"""<section class="page"><div class="kicker">PROLOGUE</div><h2>{e(U['prologue_h'])}</h2>
{prologue_box()}
<h3>{e(U['sample_h'])}</h3><ul>{items}</ul>{foot(U['sample_title'])}</section>""",
        character_book(ch)])


# ---------- 8인 확장팩 ----------
def expansion():
    X = XC.EXPANSION
    t = U["exp_title"]
    places = "".join(f"<tr><td>{e(c['place'])}</td><td>{c['id']}</td></tr>" for c in X["clues"])
    slips = "".join(
        f'<div class="box" style="border-style:dashed;margin:0 0 6mm"><div class="kicker">{e(U["exp_slip_label"])}{e(n)}</div>'
        f'<p style="margin-top:2mm">{e(txt)}</p></div>' for n, txt in X["slips"])
    sol = "".join(f'<div class="box"><b>{e(a)}</b><p class="muted" style="margin-top:1.5mm">{e(b)}</p></div>'
                  for a, b in X["solution"])
    return doc(t, [
        cover(t, U["exp_cover_note"]),
        f"""<section class="page"><div class="kicker">EXPANSION</div><h2>{e(U['exp_setup_h'])}</h2>
<div class="box"><ol>{''.join(f"<li>{i}</li>" for i in U['exp_setup_items'])}</ol></div>
<h3>{e(U['exp_places_h'])}</h3>
<table><tr><th>{e(U['place_head'][0])}</th><th>{e(U['place_head'][1])}</th></tr>{places}</table>
{foot(t + " · 1")}</section>""",
        *[character_book(ch) for ch in X["characters"]],
        f"""<section class="page"><div class="kicker">SLIPS</div><h2>{e(U['exp_slips_h'])}</h2>
<p class="muted">{e(U['exp_slips_note'])}</p>{slips}
{foot(t + " · 2")}</section>""",
        f'<section class="page cards">{"".join(card(c) for c in X["clues"])}</section>',
        *invitations(X["characters"]),
        cover(U["exp_sol_cover"], U["sol_cover_note"]),
        f"""<section class="page"><div class="kicker">SOLUTION</div><h2>{e(U['exp_sol_title'])}</h2>{sol}
{foot(t + " · 3")}</section>"""])


BUILDERS = {"host": host_guide, "chars": characters, "cards": clue_cards,
            "solution": solution, "invites": invitations, "sample": sample}
if XC:
    BUILDERS["exp"] = expansion


def main():
    if not (ROOT / "fonts" / f"{C.LANG}.css").exists():
        subprocess.run([sys.executable, str(ROOT / "fetch_fonts.py")], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    PDF.mkdir(parents=True, exist_ok=True)
    for key, fn in BUILDERS.items():
        name = U["files"][key]
        (OUT / f"{name}.html").write_text(fn(), encoding="utf-8")
        print(f"✔ out/{LANG}/{name}.html")
    subprocess.run(["node", str(ROOT / "pdf.mjs"), str(OUT), str(PDF)], check=True)


if __name__ == "__main__":
    main()
