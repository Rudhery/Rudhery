"""Atualiza as partes vivas do README: número de releases e downloads do Cay.

Roda na GitHub Action (.github/workflows/readme.yml). Só usa a biblioteca padrão.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "Rudhery"
README = Path(__file__).resolve().parent.parent / "README.md"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(path):
    """GET paginado na API do GitHub; devolve a lista completa."""
    items, url = [], f"https://api.github.com{path}{'&' if '?' in path else '?'}per_page=100"
    while url:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req) as res:
            items += json.load(res)
            nxt = re.search(r'<([^>]+)>;\s*rel="next"', res.headers.get("Link", ""))
            url = nxt.group(1) if nxt else None
    return items


def replace(text, marker, body, inline=False):
    sep = "" if inline else "\n"
    pattern = re.compile(rf"(<!-- {marker}:start -->).*?(<!-- {marker}:end -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}{sep}{body}{sep}{m.group(2)}", text)


def main():
    cay = [r for r in api(f"/repos/{USER}/cay/releases") if not r["draft"] and r["published_at"]]
    downloads = sum(a["download_count"] for r in cay for a in r.get("assets", []))

    text = README.read_text(encoding="utf-8")
    new = replace(text, "cay-releases", str(len(cay)), inline=True)
    new = replace(new, "cay-downloads", f"{downloads:,}", inline=True)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README atualizado")
    else:
        print("nada mudou")


if __name__ == "__main__":
    main()
