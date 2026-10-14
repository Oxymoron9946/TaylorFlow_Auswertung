"""Liest die Programmversion aus taylorflow/__init__.py (ohne das Paket zu importieren)."""
import re
from pathlib import Path


def version() -> str:
    text = (Path(__file__).resolve().parents[1] / "taylorflow" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)
