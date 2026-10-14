# -*- coding: utf-8 -*-
"""
Monolith-Auswertung und Vergleich mit einem Einzelkanal.

    python monolith.py

Einstellungen: config.MONOLITH. Für den Vergleich muss auswertung.py für den
Vergleichskanal gelaufen sein.

Ergebnisse in <ERGEBNIS_ORDNER>/monolith/:
    monolith_kennwerte.csv          u_G, u_L, kLa, ṅ_spez je Betriebspunkt
    kla_monolith.png                3D-Fläche kLa des Monolithen
    nspez_monolith.png              3D-Fläche ṅ_spez des Monolithen
    kla_kanal.png, nspez_kanal.png  dieselben Größen des Vergleichskanals,
                                    auf gleichen Achsen wie der Monolith
    kla_modell.png                  Modellfläche (z. B. Yue 2007) auf gleichen Achsen
    paritaet_monolith_kanal.png     kLa Kanal gegen kLa Monolith an den Monolith-Punkten
"""

from __future__ import annotations

import sys
import warnings

import matplotlib
import numpy as np

matplotlib.use("Agg")

import config  # noqa: E402
from taylorflow import ergebnisse, monolith  # noqa: E402
from taylorflow import plots as pl  # noqa: E402
from taylorflow.modellvergleich import modell_titel, vorhersage  # noqa: E402
from taylorflow.plots.stil import achsgrenzen, t  # noqa: E402
from matplotlib import cm  # noqa: E402


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    m = config.MONOLITH
    stil = pl.PlotStil(**config.STIL)
    ordner = config.ERGEBNIS_ORDNER / "monolith"
    ordner.mkdir(parents=True, exist_ok=True)

    mono = monolith.berechne(m["datei"], m["n_kanaele"], m["d_kanal_m"], m["laenge_m"],
                             m["henry_ref_mol_m3_pa"], m["henry_dlnh_dt_k"])
    mono.to_csv(ordner / "monolith_kennwerte.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"Monolith: {len(mono)} Betriebspunkte, davon {int(mono['gesaettigt'].sum())} am Austritt gesättigt (ohne kLa).")

    kanal = m.get("vergleich_kanal")
    bp = None
    if kanal:
        bp = ergebnisse.lade_betriebspunkte(config.ERGEBNIS_ORDNER, kanal)
        bp = bp[bp["kLa_log_mean_1_s"] > 0]

    # Gemeinsame Achsen, damit Monolith und Kanal direkt vergleichbar sind
    ug = [mono["u_G"]] + ([bp["GasVelocity_m_s"]] if bp is not None else [])
    ul = [mono["u_L"]] + ([bp["LiquidVelocity_m_s"]] if bp is not None else [])
    kla_werte = [mono["kla"]] + ([bp["kLa_log_mean_1_s"]] if bp is not None else [])
    modell = m.get("vergleich_modell")
    if bp is not None and modell:
        kla_modell = vorhersage(bp, modell, config.MODELL_DATEI)
        kla_werte.append(kla_modell)
    n_werte = [mono["n_spez"]] + ([bp["n_spez_mol_s_m3"]] if bp is not None else [])
    xy = {"x": achsgrenzen(np.concatenate(ug)), "y": achsgrenzen(np.concatenate(ul))}
    achsen_kla = dict(xy, z=achsgrenzen(np.concatenate(kla_werte)))
    achsen_n = dict(xy, z=achsgrenzen(np.concatenate(n_werte)))

    def speichere(name, erzeuge):
        try:
            pl.speichere(erzeuge(), ordner, name, stil)
        except Exception as e:
            print(f"  {name}: nicht erzeugt ({e})")

    speichere("kla_monolith", lambda: pl.flaeche_3d(mono["u_G"], mono["u_L"], mono["kla"], stil, t("kla", stil),
                                                   cm.plasma, "Monolith", achsen_kla))
    speichere("nspez_monolith", lambda: pl.flaeche_3d(mono["u_G"], mono["u_L"], mono["n_spez"], stil,
                                                     t("nspez", stil), cm.coolwarm, "Monolith", achsen_n))
    if bp is not None:
        speichere("kla_kanal", lambda: pl.kla_flaeche(bp, stil, kanal, achsen_kla))
        speichere("nspez_kanal", lambda: pl.nspez_flaeche(bp, stil, kanal, achsen_n))
        if modell:
            speichere("kla_modell", lambda: pl.modell_flaeche(bp, modell, stil, f"{kanal} | "
                                                             f"{modell_titel(modell, config.MODELL_DATEI)}",
                                                             achsen_kla, config.MODELL_DATEI))
        # Parität an den Monolith-Punkten: gesättigte Monolith-Punkte aus der eigenen Fläche interpoliert
        x = mono["kla"].to_numpy(float).copy()
        satt = mono["gesaettigt"].to_numpy(bool)
        if satt.any():
            x[satt] = monolith.interpoliere(mono["u_G"], mono["u_L"], mono["kla"],
                                            mono["u_G"][satt], mono["u_L"][satt])
        y = monolith.interpoliere(bp["GasVelocity_m_s"], bp["LiquidVelocity_m_s"], bp["kLa_log_mean_1_s"],
                                  mono["u_G"], mono["u_L"])
        de = stil.sprache == "de"
        gruppen = np.where(satt, "Monolith gesättigt (interpoliert)" if de else "Monolith saturated (interpolated)",
                           "Monolith gemessen" if de else "Monolith measured")
        speichere("paritaet_monolith_kanal", lambda: pl.paritaet(
            x, {kanal: y}, stil, gruppen=gruppen, titel=kanal,
            x_beschriftung=r"$k_La$ Monolith [1/s]",
            y_beschriftung=(r"$k_La$ Kanal [1/s]" if de else r"$k_La$ channel [1/s]")))
    print(f"Ergebnisse in {ordner}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
