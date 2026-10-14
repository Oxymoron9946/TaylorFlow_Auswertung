# -*- coding: utf-8 -*-
"""
Vergleich gemessener Kennwerte mit Literaturmodellen und eigenen Modellen.

    python literaturvergleich.py

Einstellungen: config.VERGLEICH. Voraussetzung: auswertung.py ist gelaufen.

Ergebnisse in <ERGEBNIS_ORDNER>/vergleich/:
    vergleich_<Zielgröße>.csv        Statistik je Modell (MAPE, Bias, RMSE, Anteil im Band)
    paritaet_<Modell>.png            Paritätsdiagramm je Modell, Kanäle farblich getrennt
    eigenes_modell_<Name>.png        Paritätsdiagramm des angepassten Potenzansatzes
"""

from __future__ import annotations

import sys
import warnings

import matplotlib

matplotlib.use("Agg")

import config  # noqa: E402
from taylorflow import plots as pl  # noqa: E402
from taylorflow.modellvergleich import (fit_potenzansatz, lade_betriebspunkte_mehrerer_kanaele,  # noqa: E402
                                        modell_titel, speichere_modell, vergleichstabelle, vorhersage)


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    v = config.VERGLEICH
    stil = pl.PlotStil(**config.STIL)
    ziel = v["zielgroesse"]
    ordner = config.ERGEBNIS_ORDNER / "vergleich"
    daten = lade_betriebspunkte_mehrerer_kanaele(config.ERGEBNIS_ORDNER, v.get("kanaele"))
    gueltig = daten[~daten["manual_exclude"].astype(bool)]
    print(f"{len(gueltig)} Betriebspunkte aus {gueltig['Kanal'].nunique()} Kanälen "
          f"(ohne {len(daten) - len(gueltig)} als ungültig markierte).")

    modelle = list(v["modelle"])
    fit = v.get("eigener_fit")
    if fit:
        basis = daten if not fit.get("kanaele") else lade_betriebspunkte_mehrerer_kanaele(
            config.ERGEBNIS_ORDNER, fit["kanaele"])
        modell = fit_potenzansatz(basis, ziel, fit["variablen"], name=fit["name"], titel=fit.get("titel", ""))
        print(f"\nEigenes Modell '{modell.name}': {modell.formel()}")
        print(f"  n = {modell.n_punkte}, MAPE = {modell.mape_prozent:.1f} %, R² (log) = {modell.r2_log:.3f}")
        if fit.get("speichern"):
            print(f"  gespeichert in {speichere_modell(modell, config.MODELL_DATEI)}")
            modelle.append(modell.name)
        b = basis[~basis["manual_exclude"].astype(bool)]
        fig = pl.paritaet(b[ziel], {modell.titel: modell.berechne(b)}, stil, v["groesse_beschriftung"],
                          v["band_prozent"], v["logarithmisch"], gruppen=b["Kanal"].values)
        pl.speichere(fig, ordner, f"eigenes_modell_{modell.name}", stil)

    tabelle = vergleichstabelle(daten, ziel, modelle, config.MODELL_DATEI, v["band_prozent"])
    ordner.mkdir(parents=True, exist_ok=True)
    tabelle.to_csv(ordner / f"vergleich_{ziel}.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("\n" + tabelle.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    for m in modelle:
        b = vorhersage(gueltig, m, config.MODELL_DATEI)
        try:
            fig = pl.paritaet(gueltig[ziel], {modell_titel(m, config.MODELL_DATEI): b}, stil,
                              v["groesse_beschriftung"], v["band_prozent"], v["logarithmisch"],
                              gruppen=gueltig["Kanal"].values)
            pl.speichere(fig, ordner, f"paritaet_{m}", stil)
        except Exception as e:
            print(f"  Paritätsplot {m}: nicht erzeugt ({e})")
    print(f"\nErgebnisse in {ordner}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
