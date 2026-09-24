#!/usr/bin/env python3
"""clients/*.json → docs/<slug>/index.html 로 가게 홈페이지를 생성합니다.

사용법:
    python3 build.py            # 모든 가게 빌드
    python3 build.py cafe-onda  # 특정 가게만 빌드
"""
import datetime
import html
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).parent
TEMPLATE = (ROOT / "template.html").read_text(encoding="utf-8")

REQUIRED = ["slug", "name", "category", "tagline", "intro", "phone", "address", "hours", "services"]


def e(value):
    return html.escape(str(value), quote=True)


def render_highlights(items):
    return "".join(
        f'<div class="card"><div class="num">{e(h.get("num", ""))}</div>'
        f'<h3>{e(h["title"])}</h3><p>{e(h.get("desc", ""))}</p></div>'
        for h in items
    )


def render_services(items):
    out = []
    for s in items:
        desc = f'<small>{e(s["desc"])}</small>' if s.get("desc") else ""
        out.append(
            f'<div class="item"><div><b>{e(s["name"])}</b>{desc}</div>'
            f'<div class="price">{e(s.get("price", ""))}</div></div>'
        )
    return "".join(out)


def render_reviews(items):
    return "".join(
        f'<div class="card review"><div class="stars">★★★★★</div><p>{e(r["text"])}</p>'
        f'<div class="who">— {e(r.get("author", "방문 고객"))}</div></div>'
        for r in items
    )


def build(data):
    missing = [k for k in REQUIRED if not data.get(k)]
    if missing:
        raise ValueError(f"{data.get('slug', '?')}: 필수 항목 누락 {missing}")

    map_url = data.get("map_url") or (
        "https://map.naver.com/p/search/" + urllib.parse.quote(f'{data["name"]} {data["address"]}')
    )
    # 예약 링크(네이버 예약/카톡 채널)가 있으면 그걸 메인 버튼으로, 없으면 전화
    phone_raw = re.sub(r"[^0-9+]", "", data["phone"])
    primary_href = data.get("booking_url") or data.get("kakao_url") or f"tel:{phone_raw}"
    primary_label = data.get("primary_label") or ("예약하기" if data.get("booking_url") else "문의하기")

    extra = ""
    if data.get("kakao_url"):
        extra += f'\n<a href="{e(data["kakao_url"])}">카카오톡 채널</a>'
    if data.get("instagram"):
        extra += f'\n<a href="https://instagram.com/{e(data["instagram"])}">인스타그램 @{e(data["instagram"])}</a>'

    if data.get("hero_image"):
        hero_bg = f'url("{e(data["hero_image"])}")'
    else:
        c1, c2 = data.get("gradient", [data.get("color", "#333"), "#111"])
        hero_bg = f"linear-gradient(135deg,{e(c1)},{e(c2)})"

    values = {
        "name": e(data["name"]),
        "category": e(data["category"]),
        "tagline": e(data["tagline"]),
        "intro": e(data["intro"]),
        "about_title": e(data.get("about_title", f'{data["name"]}을 소개합니다')),
        "color": e(data.get("color", "#2f6f5e")),
        "hero_bg": hero_bg,
        "phone": e(data["phone"]),
        "phone_raw": e(phone_raw),
        "address": e(data["address"]),
        "hours": e("\n".join(data["hours"])),
        "map_url": e(map_url),
        "primary_href": e(primary_href),
        "primary_label": e(primary_label),
        "extra_contacts": extra,
        "menu_eyebrow": e(data.get("menu_eyebrow", "Menu")),
        "menu_title": e(data.get("menu_title", "메뉴 & 가격")),
        "highlights": render_highlights(data.get("highlights", [])),
        "services": render_services(data["services"]),
        "reviews": render_reviews(data.get("reviews", [])),
        "year": str(datetime.date.today().year),
        # 데모용 가상 가게는 후기·연락처가 실제가 아님을 명시
        "sample_note": "샘플 페이지입니다. 가상의 가게이며 후기와 연락처는 예시입니다.<br>" if data.get("sample") else "",
    }
    page = TEMPLATE
    for key, val in values.items():
        page = page.replace("{{" + key + "}}", val)
    leftover = re.findall(r"\{\{\w+\}\}", page)
    if leftover:
        raise ValueError(f"치환되지 않은 항목: {leftover}")

    out = ROOT / "docs" / data["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


def main():
    only = set(sys.argv[1:])
    built = []
    for path in sorted((ROOT / "clients").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if only and data["slug"] not in only:
            continue
        built.append((data, build(data)))
        print(f"✔ {data['name']} → {built[-1][1].relative_to(ROOT)}")

    # 포트폴리오 목록 페이지 (영업할 때 보여주는 용도)
    if not only:
        cards = "".join(
            f'<a class="card" href="{e(d["slug"])}/"><b>{e(d["name"])}</b><span>{e(d["category"])}</span></a>'
            for d, _ in built
        )
        (ROOT / "docs" / "index.html").write_text(
            f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>홈페이지 제작 포트폴리오</title>
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:60px auto;padding:0 20px;background:#fff;color:#1b1b1f}}
h1{{font-size:28px}}p{{color:#666}}.card{{display:flex;justify-content:space-between;padding:18px 20px;border:1px solid #e5e5e5;border-radius:14px;margin-top:12px;text-decoration:none;color:inherit}}
.card span{{color:#888}}@media (prefers-color-scheme:dark){{body{{background:#141416;color:#eee}}.card{{border-color:#333}}}}</style></head>
<body><h1>가게 홈페이지 제작 샘플</h1><p>모바일 최적화 · 전화/길찾기/예약 버튼 · 네이버 검색 노출용 기본 설정 포함</p>{cards}</body></html>""",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
