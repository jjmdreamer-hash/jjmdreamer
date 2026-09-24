#!/usr/bin/env python3
"""content.py → 인쇄용 HTML(mystery/out/) → PDF(mystery/pdf/).

사용법: python3 mystery/build.py
PDF 변환에는 Node + playwright가 필요합니다(mystery/pdf.mjs).
"""
import html
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import content as C  # noqa: E402

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "out"
PDF = ROOT / "pdf"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=Noto+Sans+KR:wght@400;500;700&display=swap');
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans KR',sans-serif;color:#1d2230;font-size:10.5pt;line-height:1.7;word-break:keep-all;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:20mm 20mm 18mm;position:relative;overflow:hidden;page-break-after:always;background:#fbfaf7}
.page:last-child{page-break-after:auto}
.serif{font-family:'Noto Serif KR',serif}
h1{font-family:'Noto Serif KR',serif;font-weight:900;font-size:30pt;line-height:1.2;letter-spacing:-.01em}
h2{font-family:'Noto Serif KR',serif;font-weight:900;font-size:17pt;margin:0 0 4mm;color:#14203a}
h3{font-size:11pt;font-weight:700;color:#9b2c2c;margin:6mm 0 2mm;letter-spacing:.04em}
p{margin:0 0 2.5mm}
.kicker{font-size:9pt;letter-spacing:.3em;color:#9b2c2c;font-weight:700}
.muted{color:#5b6275}
.foot{position:absolute;bottom:9mm;left:20mm;right:20mm;font-size:8pt;color:#8a90a0;display:flex;justify-content:space-between}
.cover{background:radial-gradient(ellipse at 30% 20%,#2c3b63 0%,#0f1629 70%);color:#eef1f8;display:flex;flex-direction:column;justify-content:flex-end}
.cover h1{color:#fff;font-size:44pt}
.cover .sub{font-family:'Noto Serif KR',serif;font-size:16pt;color:#c9d2ea;margin-top:3mm}
.cover .meta{margin-top:12mm;font-size:10pt;color:#aeb8d4;letter-spacing:.1em}
.snow{position:absolute;inset:0;background-image:radial-gradient(#ffffff55 1px,transparent 1.6px),radial-gradient(#ffffff33 1px,transparent 1.4px);
  background-size:18mm 18mm,11mm 11mm;background-position:0 0,5mm 7mm}
.box{border:1px solid #d9d4c7;border-radius:3mm;padding:5mm 6mm;background:#fff;margin:3mm 0}
.box.red{border-color:#e3b7b7;background:#fff7f6}
.box.dark{background:#14203a;color:#eef1f8;border:none}
table{border-collapse:collapse;width:100%;font-size:9.5pt}
td,th{border-bottom:1px solid #e3dfd4;padding:1.8mm 2mm;text-align:left;vertical-align:top}
th{font-weight:700;color:#14203a;background:#f1eee6}
td.t{white-space:nowrap;font-weight:700;color:#9b2c2c;width:22mm}
ol,ul{padding-left:5mm}
li{margin-bottom:1.5mm}
.tag{display:inline-block;font-size:8pt;font-weight:700;padding:.6mm 2.4mm;border-radius:10mm;background:#14203a;color:#fff;margin-right:1.5mm}
.two{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
/* 단서 카드 */
.cards{padding:12mm 13mm;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:0}
.card{border:0.3mm dashed #b8b2a3;padding:6mm 7mm;display:flex;flex-direction:column;background:#fff}
.card .top{display:flex;justify-content:space-between;align-items:center;font-size:8pt;font-weight:700;letter-spacing:.1em}
.card .rd{color:#fff;background:#9b2c2c;padding:.5mm 2.5mm;border-radius:10mm}
.card.r1 .rd{background:#14203a}.card.r0 .rd{background:#5a6b3a}.card.r3 .rd{background:#6b2c7a}
.card .pl{color:#5b6275}
.card h4{font-family:'Noto Serif KR',serif;font-size:15pt;font-weight:900;margin:4mm 0 3mm;color:#14203a}
.card .tx{font-size:10pt;line-height:1.75}
.card .id{margin-top:auto;font-size:8pt;color:#a3a8b5;text-align:right}
/* 초대장 */
.inv{height:148.5mm;padding:14mm 18mm;border-bottom:0.3mm dashed #b8b2a3;position:relative;overflow:hidden;
  background:radial-gradient(ellipse at 80% 0%,#2c3b63 0%,#0f1629 75%);color:#eef1f8}
.inv h2{color:#fff;font-size:22pt;margin-top:4mm}
.inv .role{font-family:'Noto Serif KR',serif;font-size:14pt;color:#f3c9c9;margin-top:6mm}
.inv .blank{display:inline-block;min-width:45mm;border-bottom:0.3mm solid #aeb8d4}
"""


def e(s):
    return html.escape(str(s))


def paras(text):
    return "".join(f"<p>{e(t)}</p>" for t in str(text).split("\n\n"))


def doc(title, pages):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(title)}</title>'
            f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")


def foot(label):
    return f'<div class="foot"><span>{e(C.TITLE)} · {e(C.SUBTITLE)}</span><span>{e(label)}</span></div>'


def cover(kind, note=""):
    return (f'<section class="page cover"><div class="snow"></div><div style="position:relative">'
            f'<div class="kicker" style="color:#f3c9c9">{e(kind)}</div>'
            f"<h1>{e(C.TITLE)}</h1><div class=\"sub\">{e(C.SUBTITLE)}</div>"
            f'<div class="meta">{C.PLAYERS}인 · {e(C.PLAYTIME)} · 추리 파티 게임</div>'
            f'{f"<p style=margin-top:8mm;color:#c9d2ea>{e(note)}</p>" if note else ""}'
            f"</div></section>")


def by_round(r):
    return [c for c in C.CLUES if c["round"] == r]


# ---------- 1. 진행자 가이드 ----------
def host_guide():
    p = [cover("진행자 가이드", "이 책자에는 해답이 없습니다. 진행자도 플레이어로 참여할 수 있습니다.")]

    places = {}
    for c in by_round(2):
        places.setdefault(c["place"], []).append(c["id"])
    place_rows = "".join(f"<tr><td>{e(k)}</td><td>{', '.join(v)}</td></tr>" for k, v in places.items())

    p.append(f"""<section class="page"><div class="kicker">PREPARE</div><h2>준비하기</h2>
<div class="box"><ol>
<li><b>인쇄:</b> 캐릭터북 6부, 단서 카드, 초대장을 인쇄합니다. 단서 카드는 점선을 따라 자릅니다.</li>
<li><b>봉투 준비:</b> 봉투 4개에 「1라운드」 「2라운드」 「3라운드」 「해답」이라고 쓰고, 카드 오른쪽 아래의 번호대로 넣습니다.
(A=1라운드, B=2라운드, C=3라운드. E1 「한결의 카메라」는 한결 역에게 캐릭터북과 함께 줍니다.)</li>
<li><b>배역:</b> 모임 며칠 전에 초대장을 보내 배역을 정해 주세요. 복장 팁이 있으면 훨씬 재밌습니다.
배역은 성별과 관계없이 누구나 맡을 수 있습니다.</li>
<li><b>분위기:</b> 조명을 조금 어둡게, 캐럴 대신 잔잔한 피아노 음악, 따뜻한 음료. 윷놀이 판을 소품으로 두면 좋습니다.</li>
<li><b>해답:</b> 해답 PDF는 진행자가 투표 전까지 절대 열지 않습니다.</li>
</ol></div>
<h3>준비물</h3><p>필기구 6개 · 메모지 · 봉투 4개 · (선택) 윷놀이 세트, 카메라·만년필 같은 소품</p>
<h3>산장 구조</h3>
<table>{''.join(f"<tr><th style='width:22mm'>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in C.MAP.items())}</table>
<h3>진행 순서 한눈에</h3>
<table><tr><th>단계</th><th>시간</th><th>내용</th></tr>
<tr><td>0. 입장</td><td>15분</td><td>캐릭터북 배부, 각자 읽기. 음료 준비.</td></tr>
<tr><td>1. 프롤로그</td><td>5분</td><td>진행자가 프롤로그를 낭독합니다.</td></tr>
<tr><td>2. 자기소개</td><td>10분</td><td>각자 캐릭터북의 ‘공개 소개’를 캐릭터 말투로 읽습니다.</td></tr>
<tr><td>3. 1라운드 · 현장</td><td>25분</td><td>A 카드 7장을 모두 공개. 자유 토론.</td></tr>
<tr><td>4. 2라운드 · 수색</td><td>30분</td><td>장소를 골라 B 카드 획득. 공개 여부는 자유. 1:1 밀담 허용.</td></tr>
<tr><td>5. 3라운드 · 재조사</td><td>15분</td><td>C 카드 3장을 모두 공개. 최종 토론.</td></tr>
<tr><td>6. 투표 · 해답</td><td>15분</td><td>투표 → 해답 낭독 → 점수 계산.</td></tr></table>
{foot("진행자 가이드 · 1")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">PROLOGUE</div><h2>프롤로그 <span class="muted" style="font-size:10pt">— 진행자가 천천히 낭독</span></h2>
<div class="box dark serif" style="font-size:11pt;line-height:1.95">{''.join(f"<p>{e(t)}</p>" for t in C.PROLOGUE)}</div>
<h3>모두가 아는 사실</h3><ul>{''.join(f"<li>{e(t)}</li>" for t in C.COMMON_FACTS)}</ul>
{foot("진행자 가이드 · 2")}</section>""")

    p.append(f"""<section class="page"><div class="kicker">RULES</div><h2>규칙</h2>
{''.join(f'<div class="box"><b>{i}. {e(a)}</b><p class="muted" style="margin-top:1.5mm">{e(b)}</p></div>' for i, (a, b) in enumerate(C.RULES, 1))}
{foot("진행자 가이드 · 3")}</section>
<section class="page"><div class="kicker">ROUNDS</div><h2>라운드 진행</h2>
<div class="box"><p><span class="tag">1라운드</span><b>현장.</b> A 카드 7장을 테이블 가운데에 모두 펼칩니다. 누구나 볼 수 있습니다.</p>
<p><span class="tag">2라운드</span><b>수색.</b> 자기소개 순서대로 한 명씩 아래 장소 중 하나를 고르면, 진행자가 그 장소의 카드를 건넵니다.
자기 방(관리인실은 도현의 방)은 고를 수 없습니다. 모든 장소가 수색될 때까지 계속 돕니다.
카드는 받은 사람만 보고, 공개 여부는 자유입니다. 이 라운드에는 다른 방으로 가서 1:1 밀담을 해도 됩니다.</p>
<table style="margin:2mm 0 3mm"><tr><th>장소</th><th>카드</th></tr>{place_rows}</table>
<p><span class="tag">3라운드</span><b>재조사.</b> “눈이 그치고 날이 밝아, 서재를 다시 살펴봅니다.” C 카드 3장을 모두 공개합니다.</p>
<p><span class="tag">투표</span>각자 종이에 <b>범인 · 동기 · 사망 시각을 속인 방법</b>을 적어 동시에 공개합니다. 그다음 진행자가 해답을 엽니다.</p></div>
<h3>점수 (선택)</h3>
<table><tr><th>항목</th><th style="width:20mm">점수</th></tr>{''.join(f"<tr><td>{e(a)}</td><td>+{b}</td></tr>" for a, b in C.SCORING)}</table>
{foot("진행자 가이드 · 4")}</section>""")

    names = "".join(f"<th>{e(c['name'])}</th>" for c in C.CHARACTERS)
    rows = "".join(f"<tr><td>{e(a)}</td>{'<td></td>' * len(C.CHARACTERS)}</tr>" for a, _ in C.SCORING)
    p.append(f"""<section class="page"><div class="kicker">VOTE</div><h2>투표지 · 점수표</h2>
<div class="two">{''.join('<div class="box" style="height:58mm"><b>투표지</b><p class="muted" style="margin-top:3mm">범인:</p><p class="muted" style="margin-top:6mm">동기:</p><p class="muted" style="margin-top:6mm">사망 시각을 속인 방법:</p></div>' for _ in range(4))}</div>
<h3>점수표</h3><table><tr><th></th>{names}</tr>{rows}<tr><th>합계</th>{'<td></td>' * len(C.CHARACTERS)}</tr></table>
{foot("진행자 가이드 · 5")}</section>""")
    return doc("진행자 가이드", p)


# ---------- 2. 캐릭터북 ----------
def character_book(ch):
    killer = ch.get("is_killer")
    secret_label = "당신만 아는 진실" if killer else "당신의 비밀"
    tl = "".join(f'<tr><td class="t">{e(t)}</td><td>{e(d)}</td></tr>' for t, d in ch["timeline"])
    cover_story = (f'<h3>둘러댈 이야기</h3><div class="box red serif">{e(ch["cover"])}</div>' if killer else "")
    rule = ("당신은 <b>거짓말을 해도 되는 유일한 사람</b>입니다."
            if killer else "당신은 범인이 아닙니다. 비밀을 숨기거나 대답을 거부할 수는 있지만 <b>거짓말은 할 수 없습니다.</b>")
    return f"""<section class="page"><div class="kicker">CHARACTER · 남에게 보여주지 마세요</div>
<h1 style="font-size:32pt;margin-top:3mm">{e(ch['name'])} <span class="muted" style="font-size:14pt;font-weight:400">{ch['age']}세</span></h1>
<p class="serif" style="font-size:13pt;color:#9b2c2c;margin-top:1mm">{e(ch['role'])}</p>
<p class="muted" style="font-size:9pt">복장 팁 · {e(ch['costume'])}</p>
<h3>공개 소개 <span class="muted" style="font-weight:400">— 자기소개 때 소리 내어 읽으세요</span></h3>
<div class="box serif">{e(ch['public'])}</div>
<h3>{secret_label}</h3><div class="box red">{paras(ch['secret'])}</div>
<p style="font-size:9.5pt">{rule}</p>
{foot(ch['name'] + " · 1/2")}</section>
<section class="page"><div class="kicker">{e(ch['name'])}</div>
<h3 style="margin-top:0">그날 밤 당신의 진짜 행적</h3><table>{tl}</table>
{cover_story}
<h3>당신이 알고 있는 것</h3><ul>{''.join(f"<li>{e(k)}</li>" for k in ch['knows'])}</ul>
<h3>개인 목표 <span class="muted" style="font-weight:400">(각 +1점)</span></h3><ol>{''.join(f"<li>{e(g)}</li>" for g in ch['goals'])}</ol>
{foot(ch['name'] + " · 2/2")}</section>"""


def characters():
    return doc("캐릭터북", [cover("캐릭터북", "한 사람에게 두 장씩, 자기 배역만 나눠 주세요.")]
               + [character_book(ch) for ch in C.CHARACTERS])


# ---------- 3. 단서 카드 ----------
def card(c):
    label = {0: "소지품", 1: "1라운드 · 현장", 2: "2라운드 · 수색", 3: "3라운드 · 재조사"}[c["round"]]
    return (f'<div class="card r{c["round"]}"><div class="top"><span class="rd">{label}</span>'
            f'<span class="pl">{e(c["place"])}</span></div><h4>{e(c["title"])}</h4>'
            f'<div class="tx">{e(c["text"])}</div><div class="id">{c["id"]}</div></div>')


def clue_cards():
    order = by_round(1) + by_round(0) + by_round(2) + by_round(3)
    pages = [f'<section class="page cards">{"".join(card(c) for c in order[i:i + 6])}</section>'
             for i in range(0, len(order), 6)]
    return doc("단서 카드", pages)


# ---------- 4. 해답 ----------
def solution():
    S = C.SOLUTION
    chain = "".join(f'<div class="box"><b>{i}. {e(a)}</b><p class="muted" style="margin-top:1.5mm">{e(b)}</p></div>'
                    for i, (a, b) in enumerate(S["chain"], 1))
    side = "".join(f"<tr><th style='width:40mm'>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in S["side"])
    return doc("해답", [
        cover("해답 · 투표 후에 여세요", "진행자는 투표가 끝날 때까지 이 뒷장을 보지 마세요."),
        f"""<section class="page"><div class="kicker">SOLUTION</div>
<h1 style="font-size:28pt">범인은 <span style="color:#9b2c2c">{e(S['killer'])}</span></h1>
<p class="serif" style="font-size:12pt;margin-top:2mm">{e(S['motive'])}</p>
<h3>추리의 사슬</h3>{chain}
{foot("해답 · 1")}</section>""",
        f"""<section class="page"><div class="kicker">EPILOGUE</div><h2>남은 수수께끼들</h2><table>{side}</table>
<div class="box dark serif" style="margin-top:8mm;line-height:1.95">{''.join(f"<p>{e(t)}</p>" for t in S["epilogue"])}</div>
{foot("해답 · 2")}</section>"""])


# ---------- 5. 초대장 ----------
def invitations():
    cards = [f"""<div class="inv"><div class="snow"></div><div style="position:relative">
<div class="kicker" style="color:#f3c9c9">INVITATION</div><h2>{e(C.TITLE)}</h2>
<p style="color:#c9d2ea">윤태오 작가가 올해도 백설장 송년회에 당신을 초대합니다.</p>
<div class="role">당신의 배역 — {e(ch['name'])}, {e(ch['role'])}</div>
<p style="margin-top:3mm;color:#c9d2ea">복장 · {e(ch['costume'])}</p>
<p style="margin-top:8mm">일시 <span class="blank"></span>　장소 <span class="blank"></span></p>
<p style="margin-top:3mm;font-size:9pt;color:#aeb8d4">비밀 하나쯤은 챙겨 오세요. 오늘 밤, 누군가는 거짓말을 할 테니까요.</p>
</div></div>""" for ch in C.CHARACTERS]
    return doc("초대장", [f'<section class="page" style="padding:0">{"".join(cards[i:i + 2])}</section>'
                          for i in range(0, len(cards), 2)])


# ---------- 무료 체험판 ----------
def sample():
    ch = next(c for c in C.CHARACTERS if c["id"] == "hajin")
    return doc("무료 체험판", [
        cover("무료 체험판", "프롤로그와 캐릭터 1명(서하진)을 미리 보세요."),
        f"""<section class="page"><div class="kicker">PROLOGUE</div><h2>프롤로그</h2>
<div class="box dark serif" style="font-size:11pt;line-height:1.95">{''.join(f"<p>{e(t)}</p>" for t in C.PROLOGUE)}</div>
<h3>정식판 구성</h3><ul><li>진행자 가이드(준비·규칙·라운드 진행·투표지·점수표)</li>
<li>캐릭터북 6인(각 2쪽: 공개 소개·비밀·진짜 행적·개인 목표)</li><li>단서 카드 {len(C.CLUES)}장(자르는 선 포함)</li>
<li>배역 초대장 6장</li><li>해답과 에필로그</li></ul>{foot("무료 체험판")}</section>""",
        character_book(ch)])


FILES = {
    "01_진행자가이드": host_guide,
    "02_캐릭터북": characters,
    "03_단서카드": clue_cards,
    "04_해답_투표후개봉": solution,
    "05_초대장": invitations,
    "00_무료체험판": sample,
}


def main():
    OUT.mkdir(exist_ok=True)
    PDF.mkdir(exist_ok=True)
    for name, fn in FILES.items():
        (OUT / f"{name}.html").write_text(fn(), encoding="utf-8")
        print(f"✔ out/{name}.html")
    subprocess.run(["node", str(ROOT / "pdf.mjs"), str(OUT), str(PDF)], check=True)


if __name__ == "__main__":
    main()
