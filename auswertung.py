# -*- coding: utf-8 -*-
"""
Auswertung der Taylor-Flow-Messreihen.

    python auswertung.py

Liest die Einstellungen aus config.py, wertet die Messdateien aus
(Abschnitt 2 in config.py) und erzeugt die gewählten Plots (Abschnitt 4).

Ergebnisse:  <ERGEBNIS_ORDNER>/<Kanal>/<Kanal>_profile.csv
                                       <Kanal>_betriebspunkte.csv
                                       plots/...
Protokoll:   <ERGEBNIS_ORDNER>/Modell_Gueltigkeitswarnungen.txt
"""

from __future__ import annotations

import sys
import time
import warnings

import matplotlib

matplotlib.use("Agg")

import config  # noqa: E402
from taylorflow import ergebnisse, protokoll  # noqa: E402
from taylorflow import plots as pl  # noqa: E402
from taylorflow.einlesen import finde_messreihen, lade_ausschluesse  # noqa: E402
from taylorflow.parameter import AuswerteParameter  # noqa: E402
from taylorflow.pipeline import werte_kanal_aus  # noqa: E402


def rechne(kanaele=None) -> list[str]:
    """Wertet die Messreihen aus und speichert die Ergebnisse. Gibt die Kanalnamen zurück."""
    p = AuswerteParameter.aus_dict(config.PARAMETER)
    ausschluesse = lade_ausschluesse(config.AUSSCHLUSS_DATEI)
    reihen = finde_messreihen(config.ROHDATEN_ORDNER, "Masse")
    if kanaele:
        unbekannt = set(kanaele) - {r.kanal for r in reihen}
        if unbekannt:
            raise ValueError(f"Keine Messdatei für {sorted(unbekannt)} in {config.ROHDATEN_ORDNER}. "
                             f"Vorhanden: {[r.kanal for r in reihen]}")
        reihen = [r for r in reihen if r.kanal in kanaele]
    if not reihen:
        raise FileNotFoundError(f"Keine Dateien Auswertung_Masse_*.csv in {config.ROHDATEN_ORDNER}.")

    protokoll.starte(config.ERGEBNIS_ORDNER / "Modell_Gueltigkeitswarnungen.txt")
    for r in reihen:
        e = werte_kanal_aus(r, p, ausschluesse, config.KALIBRIER_DATENBANK)
        ergebnisse.speichere(e, config.ERGEBNIS_ORDNER, ausschluesse)
    return [r.kanal for r in reihen]


def zeichne(kanaele: list[str]) -> None:
    """Erzeugt die in config.PLOTS gewählten Plots für die angegebenen Kanäle."""
    stil = pl.PlotStil(**config.STIL)
    wahl = config.PLOTS
    for kanal in kanaele:
        ordner = ergebnisse.kanal_ordner(config.ERGEBNIS_ORDNER, kanal) / "plots"
        bp = ergebnisse.lade_betriebspunkte(config.ERGEBNIS_ORDNER, kanal)
        profile = ergebnisse.lade_profile(config.ERGEBNIS_ORDNER, kanal)
        print(f"\nPlots für {kanal}")

        def versuche(name, erzeuge):
            try:
                pl.speichere(erzeuge(), ordner, name, stil)
            except Exception as e:  # ein fehlender Plot soll den Lauf nicht abbrechen
                print(f"  {name}: nicht erzeugt ({e})")

        if wahl.get("kla_flaeche"):
            versuche("kla_flaeche", lambda: pl.kla_flaeche(bp, stil, titel=kanal))
        if wahl.get("nspez_flaeche"):
            versuche("nspez_flaeche", lambda: pl.nspez_flaeche(bp, stil, titel=kanal))
        if wahl.get("heatmaps"):
            versuche("heatmaps", lambda: pl.kennzahlen_heatmaps(profile, bp, stil, titel=kanal))
        for modell in wahl.get("modell_flaechen") or []:
            versuche(f"modell_{modell}", lambda m=modell: pl.modell_flaeche(
                bp, m, stil, titel=kanal, modelldatei=config.MODELL_DATEI))

        punkte = config.BETRIEBSPUNKTE or list(bp["Config"])
        for name in punkte:
            zeile = bp[bp["Config"] == name]
            if zeile.empty:
                print(f"  Betriebspunkt {name} nicht in {kanal}.")
                continue
            profil = ergebnisse.profil_eines_betriebspunkts(profile, name)
            titel = f"{kanal} | {name}"
            if wahl.get("blasenlaengen_fit"):
                versuche(f"blasenlaenge_{name}", lambda: pl.blasenlaengen_fit(profil, zeile.iloc[0], stil, titel))
            if wahl.get("stoffmenge"):
                versuche(f"stoffmenge_{name}", lambda: pl.stoffmenge(profil, stil, titel))
            if wahl.get("druckprofil"):
                versuche(f"druck_{name}", lambda: pl.druckprofil(profil, stil, titel))
        print(f"  gespeichert in {ordner}")


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    start = time.time()
    if config.NEU_RECHNEN:
        kanaele = rechne(config.KANAELE)
    else:
        kanaele = config.KANAELE or ergebnisse.vorhandene_kanaele(config.ERGEBNIS_ORDNER)
        if not kanaele:
            print(f"Keine Ergebnisse in {config.ERGEBNIS_ORDNER}. NEU_RECHNEN = True setzen.")
            return 1
    zeichne(kanaele)
    print(f"\nFertig nach {time.time() - start:.0f} s. Ergebnisse: {config.ERGEBNIS_ORDNER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
