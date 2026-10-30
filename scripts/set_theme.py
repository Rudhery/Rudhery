"""Troca o tema visual do README.

Uso: python scripts/set_theme.py <tema>
Sem argumento, lista os temas disponíveis e mostra o atual.
Cada tema é uma pasta em assets/themes/ com os mesmos 19 SVGs.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
THEMES = ROOT / "assets" / "themes"
PATTERN = re.compile(r"assets/themes/([\w-]+)/")


def main():
    themes = sorted(p.name for p in THEMES.iterdir() if p.is_dir())
    text = README.read_text(encoding="utf-8")
    current = set(PATTERN.findall(text))

    if len(sys.argv) < 2:
        print("atual:", ", ".join(sorted(current)) or "nenhum")
        print("disponíveis:", ", ".join(themes))
        return

    theme = sys.argv[1]
    if theme not in themes:
        sys.exit(f"tema '{theme}' não existe. Disponíveis: {', '.join(themes)}")

    README.write_text(PATTERN.sub(f"assets/themes/{theme}/", text), encoding="utf-8")
    print(f"README agora usa o tema {theme}")


if __name__ == "__main__":
    main()
