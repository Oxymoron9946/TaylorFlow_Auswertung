# -*- coding: utf-8 -*-
"""
Druckkalibrierung (Bretherton-Faktor c) aus Messungen ohne CO2.

    python kalibrierung.py

Einstellungen: config.KALIBRIERUNG. Die Dateien Auswertung_Druck_*.csv werden
per Auswahlfenster oder als feste Liste angegeben. Ohne ``datenbank_schreiben=True`` wird nur gerechnet und
angezeigt; die Datenbank bleibt unverändert.

Ergebnisse in <ERGEBNIS_ORDNER>/kalibrierung/:
    <Schlüssel>_c_werte.csv      c je Betriebspunkt
    <Schlüssel>_c_flaeche.png    c über u_G und u_L
Hintergrund und Einschränkungen: Handbuch, Kapitel „Druckkalibrierung“
"""

from __future__ import annotations

import sys
import warnings

import matplotlib

matplotlib.use("Agg")

import config  # noqa: E402
from taylorflow import plots as pl  # noqa: E402
from taylorflow.einlesen import lade_ausschluesse, waehle_messreihen  # noqa: E402
from taylorflow.kalibrierung import kalibriere, schreibe_in_datenbank, waehle_ersatzmodell  # noqa: E402
from taylorflow.parameter import AuswerteParameter  # noqa: E402
from matplotlib import cm  # noqa: E402


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    k = config.KALIBRIERUNG
    p = AuswerteParameter.aus_dict(config.PARAMETER)
    stil = pl.PlotStil(**config.STIL)
    ausschluesse = lade_ausschluesse(config.AUSSCHLUSS_DATEI)
    ordner = config.ERGEBNIS_ORDNER / "kalibrierung"
    ordner.mkdir(parents=True, exist_ok=True)

    reihen = waehle_messreihen(k.get("messdateien", "dialog"), "Druck", config.ROHDATEN_ORDNER,
                               k.get("dialog_ordner"))
    if not reihen:
        print("Keine Messdatei ausgewählt, Kalibrierung beendet.")
        return 1
    for reihe in reihen:
        print(f"\n=== {reihe.kalibrier_key} ===")
        erg = kalibriere(reihe, p, ausschluesse)
        if erg is None or erg.punkte.empty:
            continue
        erg.punkte.to_csv(ordner / f"{erg.kalibrier_key}_c_werte.csv", index=False,
                          sep=";", decimal=",", encoding="utf-8-sig")
        for name, m in erg.ersatzmodelle.items():
            print(f"  Ersatzmodell {name:<11} R² = {m['r2']:.3f}  AIC = {m['aic']:.1f}")
        modell = waehle_ersatzmodell(erg, k.get("ersatzmodell", "auto"))
        print(f"  gewählt: {modell}")
        if len(erg.punkte) >= 3:
            try:
                pl.speichere(pl.flaeche_3d(erg.punkte["u_gas"], erg.punkte["u_liq"], erg.punkte["c_calib"],
                                           stil, "c [-]", cm.viridis, erg.kalibrier_key),
                             ordner, f"{erg.kalibrier_key}_c_flaeche", stil)
            except Exception as e:
                print(f"  Plot nicht erzeugt ({e})")
        if k.get("datenbank_schreiben"):
            schreibe_in_datenbank(erg, modell, config.KALIBRIER_DATENBANK)
            print(f"  in {config.KALIBRIER_DATENBANK.name} geschrieben (USE/NOTE bleiben erhalten).")
    if not k.get("datenbank_schreiben"):
        print("\nDatenbank nicht verändert (config.KALIBRIERUNG['datenbank_schreiben'] = False).")
    print(f"Ergebnisse in {ordner}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
