# -*- coding: utf-8 -*-
"""
3D-Flächen einer Kenngröße über der Gas- und Flüssigkeitsgeschwindigkeit.

    flaeche_3d       allgemeine Fläche aus Punkten (x, y, z)
    kla_flaeche      gemessenes kLa_log_mean eines Kanals
    nspez_flaeche    volumenspezifischer Molenstrom ṅ_spez eines Kanals
    modell_flaeche   Vorhersage eines Literatur- oder eigenen Modells

Die Fläche wird kubisch zwischen den Messpunkten interpoliert (linear, wenn
kubisch nicht möglich ist). Außerhalb der konvexen Hülle der Messpunkte
bleibt sie leer.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib import cm
from scipy.interpolate import griddata

from .stil import BLAU, PlotStil, achsgrenzen, formatiere_achsen, neue_figur, rc, t


def _interpoliere(x, y, z, gitter=100):
    xi = np.linspace(np.min(x), np.max(x), gitter)
    yi = np.linspace(np.min(y), np.max(y), gitter)
    X, Y = np.meshgrid(xi, yi)
    Z = None
    if len(z) >= 4:
        try:
            Z = griddata((x, y), z, (X, Y), method="cubic")
        except Exception:
            Z = None
    if Z is None or np.all(np.isnan(Z)):
        Z = griddata((x, y), z, (X, Y), method="linear")
    return X, Y, Z


def flaeche_3d(x, y, z, stil: PlotStil, z_beschriftung: str, farbskala=cm.plasma,
               titel: str = "", achsen: dict | None = None,
               x_beschriftung: str | None = None, y_beschriftung: str | None = None):
    """
    3D-Fläche mit Messpunkten und Höhenlinien am Boden.

    Parameter
    ---------
    x, y, z : Punkte (NaN-Werte werden ignoriert, mindestens 3 Punkte)
    z_beschriftung : Beschriftung der Farbskala
    achsen : optional {"x": (min, max), "y": (...), "z": (...)} für feste Achsbereiche
             (z. B. zum direkten Vergleich mehrerer Flächen)
    """
    x, y, z = (np.asarray(v, dtype=float) for v in (x, y, z))
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[ok], y[ok], z[ok]
    if len(z) < 3:
        raise ValueError(f"Zu wenige gültige Punkte für eine Fläche ({len(z)} < 3).")
    X, Y, Z = _interpoliere(x, y, z)
    achsen = dict(achsen or {})
    xlim = achsen.get("x") or achsgrenzen(x)
    ylim = achsen.get("y") or achsgrenzen(y)
    zlim = achsen.get("z") or achsgrenzen(np.concatenate([z, Z[np.isfinite(Z)]]))

    with rc(stil):
        fig, ax = neue_figur(stil, stil.groesse_3d_cm, projektion="3d")
        flaeche = ax.plot_surface(X, Y, Z, cmap=farbskala, edgecolor="none", alpha=0.85,
                                  antialiased=True, vmin=zlim[0], vmax=zlim[1])
        ax.scatter(x, y, z, color=BLAU, s=18, edgecolors="k", depthshade=True, label=t("messpunkte", stil))
        ax.contour(X, Y, Z, zdir="z", offset=zlim[0], cmap=farbskala, linewidths=1.2,
                   vmin=zlim[0], vmax=zlim[1])
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_zlim(*zlim)
        ax.set_xlabel(x_beschriftung or t("u_G", stil), labelpad=8)
        ax.set_ylabel(y_beschriftung or t("u_L", stil), labelpad=8)
        ax.view_init(elev=stil.blickwinkel_3d[0], azim=stil.blickwinkel_3d[1])
        cbar = fig.colorbar(flaeche, ax=ax, shrink=0.6, pad=0.1)
        cbar.set_label(z_beschriftung)
        if stil.titel_anzeigen and titel:
            ax.set_title(titel)
        formatiere_achsen(ax, stil, "xyz")
        if stil.sprache == "de":
            cbar.ax.yaxis.set_major_formatter(ax.zaxis.get_major_formatter())
    return fig


def kla_flaeche(betriebspunkte: pd.DataFrame, stil: PlotStil, titel: str = "", achsen=None):
    """Gemessenes kLa_log_mean; Betriebspunkte ohne gültigen Wert entfallen."""
    d = betriebspunkte.dropna(subset=["kLa_log_mean_1_s"])
    return flaeche_3d(d["GasVelocity_m_s"], d["LiquidVelocity_m_s"], d["kLa_log_mean_1_s"],
                      stil, t("kla", stil), cm.plasma, titel, achsen)


def nspez_flaeche(betriebspunkte: pd.DataFrame, stil: PlotStil, titel: str = "", achsen=None):
    """
    Volumenspezifischer Molenstrom über den ganzen Kanal:

        ṅ_spez = Δn(z_Ende) · f_Blase / (A_Kanal · z_Ende),   f_Blase = U(0) / (L_B(0) + L_S(0))
    """
    d = betriebspunkte.dropna(subset=["n_spez_mol_s_m3"])
    return flaeche_3d(d["GasVelocity_m_s"], d["LiquidVelocity_m_s"], d["n_spez_mol_s_m3"],
                      stil, t("nspez", stil), cm.coolwarm, titel, achsen)


def modell_flaeche(betriebspunkte: pd.DataFrame, modell: str, stil: PlotStil, titel: str = "",
                   achsen=None, modelldatei=None):
    """Vorhersage eines Literatur- oder eigenen Modells (Name aus ``modellvergleich.verfuegbare_modelle``)."""
    from ..modellvergleich import modell_titel, vorhersage
    z = vorhersage(betriebspunkte, modell, modelldatei)
    if np.isfinite(z).sum() < 3:
        raise ValueError(f"Modell '{modell}' liefert für diesen Kanal zu wenige Werte "
                         "(Gültigkeit z. B. nur für eckige Kanäle).")
    beschriftung = f"{t('kla', stil)} ({modell_titel(modell, modelldatei)})"
    return flaeche_3d(betriebspunkte["GasVelocity_m_s"], betriebspunkte["LiquidVelocity_m_s"], z,
                      stil, beschriftung, cm.plasma, titel, achsen)
