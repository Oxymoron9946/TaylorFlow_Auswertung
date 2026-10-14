# -*- coding: utf-8 -*-
"""
Baut docs/Handbuch.pdf aus README.md, den Kapiteln docs/01–11 und dem CHANGELOG.

    python docs/build_pdf.py

Benötigt Pandoc (z. B. pip install pypandoc_binary) und XeLaTeX (TeX Live, MiKTeX).
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DOCS = Path(__file__).resolve().parent
WURZEL = DOCS.parent
KAPITEL = sorted(DOCS.glob("[0-9][0-9]_*.md"))


def pandoc_pfad() -> str:
    try:
        import pypandoc
        return pypandoc.get_pandoc_path()
    except Exception:
        return "pandoc"


def _ohne_codeblock(text: str, funktion) -> str:
    """Wendet ``funktion`` nur außerhalb von ```-Codeblöcken an."""
    teile = re.split(r"(```.*?```)", text, flags=re.S)
    return "".join(t if t.startswith("```") else funktion(t) for t in teile)


def bereinige(text: str, art: str = "kapitel") -> str:
    """art: "kapitel" (Handnummern entfernen, LaTeX nummeriert), "readme" oder "unnummeriert"."""
    # Querverweise auf andere Markdown-Dateien und Code-Dateien in reinen Text umwandeln
    text = re.sub(r"\[([^\]]+)\]\((?!http)[^)]*\.md(#[^)]*)?\)", r"\1", text)
    text = re.sub(r"\[(`?[^\]]+`?)\]\((?!http)[^)]+\.py\)", r"\1", text)
    if art == "readme":
        # Inhaltsverzeichnis der README entfällt (PDF hat ein eigenes)
        text = re.sub(r"## Dokumentation.*?(?=## Ordner)", "", text, flags=re.S)
        text = text.replace("# TaylorFlow-Auswertung", "# Überblick", 1)
    if art == "kapitel":
        text = _ohne_codeblock(text, lambda t: re.sub(r"(?m)^(#{1,4})[ \t]+\d+(?:\.\d+)*[ \t]+", r"\1 ", t))
    else:
        text = _ohne_codeblock(text, lambda t: re.sub(r"(?m)^(#{1,4}[ \t]+[^\n]+?)[ \t]*$", r"\1 {-}", t))
    # Pandoc braucht eine Leerzeile vor Listen, GitHub nicht
    text = _ohne_codeblock(text, lambda t: re.sub(
        r"(?m)^((?![ \t]*(?:[-*]|\d+\.)[ \t])[^\n|#][^\n]*)\n(?=[ \t]*(?:-|\d+\.)[ \t])", r"\1\n\n", t))
    return text


def main() -> int:
    teile = [bereinige((WURZEL / "README.md").read_text(encoding="utf-8"), "readme")]
    teile += [bereinige(k.read_text(encoding="utf-8")) for k in KAPITEL]
    teile.append(bereinige((DOCS / "CHANGELOG.md").read_text(encoding="utf-8"), "unnummeriert"))
    gesamt = "\n\n\\newpage\n\n".join(teile)

    build = DOCS / "_build"
    build.mkdir(exist_ok=True)
    quelle = build / "handbuch.md"
    quelle.write_text(gesamt, encoding="utf-8")

    from taylorflow_version import version
    befehl = [
        pandoc_pfad(), str(quelle), "-o", str(DOCS / "Handbuch.pdf"),
        "--pdf-engine=xelatex", "--toc", "--toc-depth=2", "--number-sections",
        f"--resource-path={DOCS}",
        "-V", "documentclass=scrreprt", "-V", "lang=de-DE",
        "-V", "geometry:margin=2.3cm", "-V", "fontsize=10pt",
        "-V", "mainfont=Cambria", "-V", "sansfont=Calibri", "-V", "monofont=Consolas",
        "-V", "mathfont=Cambria Math", "-V", "colorlinks=true", "-V", "linkcolor=black",
        "-V", "urlcolor=blue", "-V", "toccolor=black",
        "-M", "title=TaylorFlow-Auswertung",
        "-M", "subtitle=Handbuch zur Auswertungssoftware",
        "-M", f"date=Version {version()}, {date.today().strftime('%d.%m.%Y')}",
        "--top-level-division=chapter", "--shift-heading-level-by=0",
        "-H", str(DOCS / "handbuch_kopf.tex"),
    ]
    print("Baue Handbuch …")
    erg = subprocess.run(befehl, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if erg.returncode != 0:
        print(erg.stderr)
        return 1
    warnungen = [z for z in erg.stderr.splitlines() if "Missing character" in z]
    if warnungen:
        print(f"{len(warnungen)} fehlende Zeichen, z. B.: {warnungen[:3]}")
    print(f"Fertig: {DOCS / 'Handbuch.pdf'}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(DOCS))
    sys.exit(main())
