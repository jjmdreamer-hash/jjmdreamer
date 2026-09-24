#!/usr/bin/env python3
"""Google Fonts를 fonts/에 내려받아 로컬 CSS(fonts/<lang>.css)를 만든다.
PDF 렌더러가 네트워크 없이도 같은 글꼴을 쓰도록 하기 위함."""
import pathlib
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent / "fonts"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
FAMILIES = {
    "ko": "Noto+Serif+KR:wght@400;700;900&family=Noto+Sans+KR:wght@400;500;700",
    "en": "Playfair+Display:wght@400;700;900&family=Inter:wght@400;500;700",
}


def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()
        except OSError:
            if i == tries - 1:
                raise


def fetch(url, dest):
    if not dest.exists():
        dest.write_bytes(get(url))


for lang, fam in FAMILIES.items():
    css = get(f"https://fonts.googleapis.com/css2?family={fam}&display=swap").decode()
    (ROOT / lang).mkdir(parents=True, exist_ok=True)

    jobs = {}

    def local(m):
        url = m.group(1)
        name = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/s/", 1)[1])
        jobs[url] = ROOT / lang / name
        return f"url({lang}/{name})"

    css = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", local, css)
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda kv: fetch(*kv), jobs.items()))
    (ROOT / f"{lang}.css").write_text(css)
    print(lang, len(list((ROOT / lang).iterdir())), "files")
