# -*- coding: utf-8 -*-
"""
Eine einzelne Abbildung erzeugen und anpassen, z. B. für eine Arbeit oder einen Vortrag.

    python abbildung.py

Ausgangspunkt sind die Einstellungen aus config.PLOTS und config.STIL. Geändert
wird nur, was unten in ANPASSUNGEN und STIL_ANPASSUNGEN steht; config.py bleibt
unverändert. Es wird nichts neu gerechnet: auswertung.py muss für den Kanal
schon gelaufen sein.
"""

from __future__ import annotations

import sys
from pathlib import Path

import config

# =============================================================================
# Einstellungen
# =============================================================================
# Kanal = Ordnername in ERGEBNIS_ORDNER, z. B. "Glas_Eckig_1000um_72cm_20molCO2_600um"
KANAL = "Glas_Eckig_1000um_72cm_20molCO2_600um"

# Plot = Name eines Blocks in config.PLOTS:
#   je Betriebspunkt: "blasenlaengen_fit", "stoffmenge", "druckprofil"
#   je Kanal:         "kla_flaeche", "nspez_flaeche", "modell_flaechen",
#                     "spalten_flaechen", "heatmaps"
PLOT = "blasenlaengen_fit"

# Nur für die Plots je Betriebspunkt: Name wie in der Spalte "Config"
BETRIEBSPUNKT = "Gas_0_134_Liq_0_056"

# Änderungen gegenüber config.PLOTS[PLOT] (mögliche Einträge: siehe dort)
ANPASSUNGEN = dict(
    x_bereich_cm=(0, 40),
    kennwertkasten=False,
    legende="upper right",
)

# Änderungen gegenüber config.STIL, z. B. englisch, als PDF, ohne Titel
STIL_ANPASSUNGEN = dict(
    sprache="en",
    formate=("png", "pdf"),
    titel_anzeigen=False,
)

ZIEL_ORDNER = config.ERGEBNIS_ORDNER / "abbildungen"
DATEINAME = None        # None = Name wie in auswertung.py, z. B. blasenlaenge_Gas_0_134_Liq_0_056
VORSCHAU = True         # True: Abbildung zusätzlich in einem Fenster anzeigen


# =============================================================================

def erzeuge_abbildung(kanal: str, plot: str, betriebspunkt: str | None = None,
                      anpassungen: dict | None = None, stil_anpassungen: dict | None = None,
                      ziel_ordner: Path | None = None, dateiname: str | None = None,
                      vorschau: bool = False, ergebnis_ordner: Path | None = None) -> list[Path]:
    """Erzeugt die Abbildung(en) eines Plots und gibt die gespeicherten Dateien zurück."""
    import matplotlib
    if not vorschau:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from taylorflow import ergebnisse
    from taylorflow import plots as pl
    from taylorflow.plots import optionen

    ergebnis_ordner = Path(ergebnis_ordner or config.ERGEBNIS_ORDNER)
    vorhanden = ergebnisse.vorhandene_kanaele(ergebnis_ordner)
    if kanal not in vorhanden:
        raise KeyError(f"Keine Ergebnisse für '{kanal}' in {ergebnis_ordner}. "
                       f"Vorhanden: {vorhanden}. Zuerst auswertung.py laufen lassen.")
    block = config.PLOTS.get(plot, {})
    block = {"an": block} if isinstance(block, bool) else dict(block)
    opt = optionen.mische(plot, {**block, **(anpassungen or {}), "an": True})
    stil = pl.PlotStil(**config.STIL).mit(**(stil_anpassungen or {}))
    bp = ergebnisse.lade_betriebspunkte(ergebnis_ordner, kanal)
    profile = ergebnisse.lade_profile(ergebnis_ordner, kanal)

    pfade = []
    teile = list(optionen.erzeuge(plot, opt, stil, bp, profile, betriebspunkt, kanal, config.MODELL_DATEI))
    for i, (name, figur) in enumerate(teile):
        if dateiname:
            name = dateiname if len(teile) == 1 else f"{dateiname}_{i + 1}"
        neu = pl.speichere(figur(), Path(ziel_ordner or ergebnis_ordner / "abbildungen"), name, stil,
                           schliessen=not vorschau)
        pfade += neu
        print("gespeichert: " + ", ".join(str(p) for p in neu))
    if vorschau and teile:
        plt.show()
    return pfade


if __name__ == "__main__":
    erzeuge_abbildung(KANAL, PLOT, BETRIEBSPUNKT, ANPASSUNGEN, STIL_ANPASSUNGEN,
                      ZIEL_ORDNER, DATEINAME, VORSCHAU)
    sys.exit(0)
