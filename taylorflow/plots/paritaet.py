# -*- coding: utf-8 -*-
"""
Paritätsdiagramm: berechnete gegen gemessene Werte.

Mehrere Modelle können in einem Diagramm stehen. Die 1:1-Linie und ein
Toleranzband (Standard ±15 %) sind eingezeichnet; die Legende nennt je
Modell die mittlere absolute relative Abweichung (MAPE).
"""

from __future__ import annotations

import numpy as np

from ..modellvergleich import statistik
from .stil import KAMERA_FARBEN, PlotStil, formatiere_achsen, neue_figur, rc, t, zahl

_MARKER = ["o", "s", "^", "D", "v", "P", "X", "<", ">"]


def paritaet(gemessen, vorhersagen: dict, stil: PlotStil, groesse: str = "",
             band_prozent: float = 15.0, logarithmisch: bool = False, titel: str = "",
             gruppen=None, x_beschriftung: str | None = None, y_beschriftung: str | None = None):
    """
    Parameter
    ---------
    gemessen : Messwerte (Array)
    vorhersagen : {Anzeigename: Array der berechneten Werte}
    groesse : Name der Größe für die Achsbeschriftung, z. B. r"$k_La$ [1/s]"
    gruppen : optional Array mit Gruppennamen je Punkt (z. B. Kanal); dann
              werden bei nur einem Modell die Gruppen farblich getrennt
    x_beschriftung, y_beschriftung : ersetzen die Standard-Achsentitel
    """
    g = np.asarray(gemessen, dtype=float)
    with rc(stil):
        fig, ax = neue_figur(stil, stil.groesse_paritaet_cm)
        alle = [g]
        if gruppen is not None and len(vorhersagen) == 1:
            (name, b), = vorhersagen.items()
            b = np.asarray(b, dtype=float)
            gruppen = np.asarray(gruppen)
            for k, gr in enumerate(dict.fromkeys(gruppen)):
                sel = gruppen == gr
                if not (np.isfinite(g[sel]) & np.isfinite(b[sel])).any():
                    continue  # Modell gilt für diese Gruppe nicht (z. B. nur eckige Kanäle)
                ax.scatter(g[sel], b[sel], s=28, marker=_MARKER[k % len(_MARKER)],
                           color=KAMERA_FARBEN[k % len(KAMERA_FARBEN)], edgecolor="k", linewidth=0.4,
                           label=str(gr), zorder=5)
            s = statistik(g, b, band_prozent)
            ax.set_title(f"{name}: MAPE {zahl(s['MAPE_%'], stil, 3)} %", fontsize=stil.schriftgroesse)
            alle.append(b)
        else:
            for k, (name, b) in enumerate(vorhersagen.items()):
                b = np.asarray(b, dtype=float)
                s = statistik(g, b, band_prozent)
                ax.scatter(g, b, s=28, marker=_MARKER[k % len(_MARKER)],
                           color=KAMERA_FARBEN[k % len(KAMERA_FARBEN)], edgecolor="k", linewidth=0.4,
                           label=f"{name} (MAPE {zahl(s['MAPE_%'], stil, 3)} %)", zorder=5)
                alle.append(b)
        werte = np.concatenate(alle)
        werte = werte[np.isfinite(werte) & (werte > 0)]
        hi = float(werte.max()) * 1.1 if werte.size else 1.0
        lo = float(werte.min()) / 1.1 if (logarithmisch and werte.size) else 0.0
        linie = np.array([lo if lo > 0 else hi * 1e-3, hi]) if logarithmisch else np.array([lo, hi])
        f = band_prozent / 100
        ax.plot(linie, linie, color="k", lw=0.9, ls="--", label="1:1", zorder=2)
        ax.plot(linie, linie * (1 + f), color="gray", lw=0.8, ls=":", zorder=1,
                label=t("band", stil, p=band_prozent))
        ax.plot(linie, linie * (1 - f), color="gray", lw=0.8, ls=":", zorder=1)
        if logarithmisch:
            ax.set_xscale("log")
            ax.set_yscale("log")
        ax.set_xlim(linie[0], hi)
        ax.set_ylim(linie[0], hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(x_beschriftung or f"{groesse} {t('gemessen', stil)}".strip())
        ax.set_ylabel(y_beschriftung or f"{groesse} {t('berechnet', stil)}".strip())
        if stil.titel_anzeigen and titel:
            ax.set_title(titel)
        ax.legend(fontsize=stil.schriftgroesse * 0.8, loc="upper left")
        if logarithmisch:
            ax.grid(stil.gitter, which="both", ls=":", alpha=0.4)
        else:
            formatiere_achsen(ax, stil)
    return fig
