# -*- coding: utf-8 -*-
"""
Übersicht eines Kanals: sechs Kennzahlen als Farbkarten über u_G × u_L.

    kLa_log_mean | Sättigung am Austritt | Absorptionslänge z95
    β am Einlass | Schlupf u_B/u_TP      | Blasenlänge am Einlass

Die Farbkarten werden zwischen den Messpunkten trianguliert; die Messpunkte
sind als weiße Kreise eingezeichnet.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .stil import PlotStil, formatiere_achsen, rc, t


def kennzahlen(profile: pd.DataFrame, betriebspunkte: pd.DataFrame) -> pd.DataFrame:
    """
    Kennzahlen je Betriebspunkt für die Übersicht.

    saettigung_aus   Sättigung C_L/C* am letzten z [%]
    z95_prozent      Kanalposition, bis zu der 95 % der insgesamt absorbierten
                     Stoffmenge aufgenommen sind, bezogen auf die Kanallänge [%]
    beta_ein         L_B / (L_B + L_S) am Einlass [-]
    L_b_ein_mm       gefittete Blasenlänge am Einlass [mm]
    """
    zeilen = []
    for _, bp in betriebspunkte.iterrows():
        g = profile[profile["Config_Name"] == bp["Config"]].sort_values("Position_z_m")
        if g.empty:
            continue
        erste, letzte = g.iloc[0], g.loc[g["Position_z_m"].idxmax()]
        L_b, L_s = erste["L_bubble_fit_m"], erste["L_slug_fit_m"]
        zeilen.append({
            "u_G": bp["GasVelocity_m_s"], "u_L": bp["LiquidVelocity_m_s"],
            "kla": bp["kLa_log_mean_1_s"] if bp["kLa_log_mean_1_s"] > 0 else np.nan,
            "saettigung_aus": float(letzte["Saturation_percent"]),
            "z95_prozent": _z95_prozent(g["Position_z_m"].values, g["Diffused_Gas_mol"].values),
            "beta_ein": L_b / (L_b + L_s) if (L_b + L_s) > 0 else np.nan,
            "schlupf": bp["slip_meas_over_theo"] if bp["slip_meas_over_theo"] > 0 else np.nan,
            "L_b_ein_mm": L_b * 1000.0,
        })
    return pd.DataFrame(zeilen)


def _z95_prozent(z, n_absorbiert) -> float:
    """Position, an der 95 % der am Kanalende absorbierten Stoffmenge erreicht sind [% der Länge]."""
    ok = np.isfinite(z) & np.isfinite(n_absorbiert)
    z, n = z[ok], n_absorbiert[ok]
    if len(z) < 2 or n[-1] <= 0:
        return np.nan
    return float(z[np.argmax(n >= 0.95 * n[-1])] / z[-1] * 100.0)


def _karte(ax, x, y, z, titel, farbskala, stil, vmin=None, vmax=None):
    x, y, z = (np.asarray(v, dtype=float) for v in (x, y, z))
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[ok], y[ok], z[ok]
    ax.set_title(titel, fontsize=stil.schriftgroesse)
    ax.set_xlabel(t("u_G", stil))
    ax.set_ylabel(t("u_L", stil))
    if len(z) < 3:
        ax.text(0.5, 0.5, t("keine_daten", stil), transform=ax.transAxes, ha="center", va="center")
        return
    flaeche = ax.tricontourf(x, y, z, levels=14, cmap=farbskala, vmin=vmin, vmax=vmax)
    ax.scatter(x, y, color="white", edgecolor="black", s=18, zorder=5, linewidths=0.5)
    cbar = ax.figure.colorbar(flaeche, ax=ax, shrink=0.85)
    formatiere_achsen(ax, stil)
    if stil.sprache == "de":
        cbar.ax.yaxis.set_major_formatter(ax.xaxis.get_major_formatter())


def kennzahlen_heatmaps(profile: pd.DataFrame, betriebspunkte: pd.DataFrame, stil: PlotStil,
                        titel: str = ""):
    """Sechs Farbkarten in einer Abbildung (2 × 3)."""
    k = kennzahlen(profile, betriebspunkte)
    with rc(stil):
        b, h = stil.groesse_heatmaps_cm
        fig, ax = plt.subplots(2, 3, figsize=(b / 2.54, h / 2.54), layout="constrained")
        if k.empty:
            return fig
        s_ok = k["saettigung_aus"].dropna()
        rand = max(1.0, 0.05 * (s_ok.max() - s_ok.min())) if len(s_ok) else 1.0
        felder = [
            ("kla", t("kla", stil), "plasma", None, None),
            ("saettigung_aus", t("saettigung_aus", stil), "plasma",
             max(0.0, s_ok.min() - rand) if len(s_ok) else None, s_ok.max() + rand if len(s_ok) else None),
            ("z95_prozent", t("z95", stil), "RdYlGn", 0, 100),
            ("beta_ein", t("beta_ein", stil), "cividis", 0, 1),
            ("schlupf", t("schlupf", stil), "magma", None, None),
            ("L_b_ein_mm", t("L_b_ein_mm", stil), "viridis", None, None),
        ]
        for a, (spalte, ueberschrift, farbskala, vmin, vmax) in zip(ax.flat, felder):
            _karte(a, k["u_G"], k["u_L"], k[spalte], ueberschrift, farbskala, stil, vmin, vmax)
        if stil.titel_anzeigen and titel:
            fig.suptitle(titel)
    return fig
