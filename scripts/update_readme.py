"""Atualiza as partes vivas do README: número de releases e downloads do Cay.

Os números ficam dentro de assets/themes/*/p-cay.svg (todos os temas, para que
trocar de tema não traga números velhos).

Roda na GitHub Action (.github/workflows/readme.yml). Só usa a biblioteca padrão.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "Rudhery"
THEMES = Path(__file__).resolve().parent.parent / "assets" / "themes"
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


def stat(text, label, value):
    """Troca o número do <text> logo antes do rótulo (RELEASES / DOWNLOADS)."""
    pattern = re.compile(rf"(>)[^<]*(</text><text[^>]*>{label}</text>)")
    return pattern.sub(lambda m: f"{m.group(1)}{value}{m.group(2)}", text)


def main():
    cay = [r for r in api(f"/repos/{USER}/cay/releases") if not r["draft"] and r["published_at"]]
    downloads = sum(a["download_count"] for r in cay for a in r.get("assets", []))

    for svg in sorted(THEMES.glob("*/p-cay.svg")):
        text = svg.read_text(encoding="utf-8")
        new = stat(text, "RELEASES", str(len(cay)))
        new = stat(new, "DOWNLOADS", f"{downloads:,}")
        if new != text:
            svg.write_text(new, encoding="utf-8", newline="\n")
            print(f"{svg.parent.name}: atualizado")
        else:
            print(f"{svg.parent.name}: nada mudou")


if __name__ == "__main__":
    main()
