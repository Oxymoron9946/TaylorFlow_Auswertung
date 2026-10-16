# -*- coding: utf-8 -*-
"""
Auswertung der Taylor-Flow-Messreihen.

    python auswertung.py

Liest die Einstellungen aus config.py, fragt die Messdateien ab (Auswahlfenster
oder feste Liste, Abschnitt 2 in config.py), wertet sie aus und erzeugt die
gewählten Plots (Abschnitt 4).

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
from taylorflow.plots import optionen  # noqa: E402
from taylorflow.einlesen import lade_ausschluesse, waehle_messreihen  # noqa: E402
from taylorflow.parameter import AuswerteParameter  # noqa: E402
from taylorflow.pipeline import werte_kanal_aus  # noqa: E402


def rechne(reihen) -> list[str]:
    """Wertet die Messreihen aus und speichert die Ergebnisse. Gibt die Kanalnamen zurück."""
    p = AuswerteParameter.aus_dict(config.PARAMETER)
    ausschluesse = lade_ausschluesse(config.AUSSCHLUSS_DATEI)
    protokoll.starte(config.ERGEBNIS_ORDNER / "Modell_Gueltigkeitswarnungen.txt")
    for r in reihen:
        e = werte_kanal_aus(r, p, ausschluesse, config.KALIBRIER_DATENBANK)
        ergebnisse.speichere(e, config.ERGEBNIS_ORDNER, ausschluesse)
    return [r.kanal for r in reihen]


def zeichne(kanaele: list[str]) -> None:
    """Erzeugt die in config.PLOTS eingeschalteten Plots für die angegebenen Kanäle."""
    stil = pl.PlotStil(**config.STIL)
    # Alle Blöcke vorab prüfen: ein Tippfehler bricht sofort mit einer Meldung ab
    wahl = {name: optionen.mische(name, block) for name, block in config.PLOTS.items()}
    wahl = {name: opt for name, opt in wahl.items() if opt["an"]}
    for kanal in kanaele:
        ordner = ergebnisse.kanal_ordner(config.ERGEBNIS_ORDNER, kanal) / "plots"
        bp = ergebnisse.lade_betriebspunkte(config.ERGEBNIS_ORDNER, kanal)
        profile = ergebnisse.lade_profile(config.ERGEBNIS_ORDNER, kanal)
        print(f"\nPlots für {kanal}")

        def zeichne_plot(name, opt, betriebspunkt=None):
            try:
                for datei, figur in optionen.erzeuge(name, opt, stil, bp, profile, betriebspunkt,
                                                     kanal, config.MODELL_DATEI):
                    try:
                        pl.speichere(figur(), ordner, datei, stil)
                    except Exception as e:  # ein fehlender Plot soll den Lauf nicht abbrechen
                        print(f"  {datei}: nicht erzeugt ({e})")
            except KeyError as e:
                print(f"  {name}: {e}")

        for name, opt in wahl.items():
            if name not in optionen.JE_BETRIEBSPUNKT:
                zeichne_plot(name, opt)
        for betriebspunkt in config.BETRIEBSPUNKTE or list(bp["Config"]):
            for name, opt in wahl.items():
                if name in optionen.JE_BETRIEBSPUNKT:
                    zeichne_plot(name, opt, betriebspunkt)
        print(f"  gespeichert in {ordner}")


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    start = time.time()
    reihen = waehle_messreihen(config.MESSDATEIEN, "Masse", config.ROHDATEN_ORDNER, config.DIALOG_ORDNER)
    if not reihen:
        print("Keine Messdatei ausgewählt, Auswertung beendet.")
        return 1
    print("Messdateien:")
    for r in reihen:
        print(f"  {r.datei}")
    if config.NEU_RECHNEN:
        kanaele = rechne(reihen)
    else:
        kanaele = [r.kanal for r in reihen]
        fehlend = sorted(set(kanaele) - set(ergebnisse.vorhandene_kanaele(config.ERGEBNIS_ORDNER)))
        if fehlend:
            print(f"Noch keine Ergebnisse für {fehlend} in {config.ERGEBNIS_ORDNER}. NEU_RECHNEN = True setzen.")
            return 1
    zeichne(kanaele)
    print(f"\nFertig nach {time.time() - start:.0f} s. Ergebnisse: {config.ERGEBNIS_ORDNER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
