# -*- coding: utf-8 -*-
"""
Protokoll der Modell-Gültigkeitswarnungen.

Während der Auswertung werden Überschreitungen von Gültigkeitsbereichen
(z. B. Kapillarzahl außerhalb des Bretherton-Bereichs) und auffällige
Fit-Ergebnisse gesammelt und in eine Textdatei geschrieben. Gleiche
Meldungen im gleichen Kontext werden nur einmal protokolliert.

Die Datei wird zu Beginn jedes Laufs neu angelegt (``starte``).
"""

from __future__ import annotations

from pathlib import Path

_datei: Path | None = None
_gemeldet: set[str] = set()


def starte(datei: Path) -> None:
    """Legt die Protokolldatei neu an und leert die Duplikat-Liste."""
    global _datei
    _datei = Path(datei)
    _datei.parent.mkdir(parents=True, exist_ok=True)
    _gemeldet.clear()
    with open(_datei, "w", encoding="utf-8") as f:
        f.write("=== MODELL-GÜLTIGKEITSWARNUNGEN ===\n")
        f.write("Überschreitungen von Gültigkeitsbereichen und auffällige Fit-Ergebnisse "
                "dieses Auswertungslaufs.\n\n")


def warnung(kontext: str, meldung: str) -> None:
    """Protokolliert eine Warnung (ohne Duplikate je Kontext und Meldung)."""
    schluessel = f"{kontext}|{meldung}"
    if schluessel in _gemeldet:
        return
    _gemeldet.add(schluessel)
    if _datei is None:
        return
    with open(_datei, "a", encoding="utf-8") as f:
        f.write(f"[{kontext}]\n  -> {meldung}\n\n")
