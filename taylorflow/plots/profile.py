# -*- coding: utf-8 -*-
"""
Profile entlang der Reaktorposition für einen Betriebspunkt.

    blasenlaengen_fit   Messwerte je Kamera, Fit mit und ohne Kamera-Offsets,
                        druckkorrigierte Blasenlänge (Plot B aus PLOT_KONZEPT)
    stoffmenge          absorbierte CO2-Stoffmenge je Blase Δn(z)
    druckprofil         berechneter Druck p(z)

Eingabe ist jeweils der Teil der Profiltabelle für einen Betriebspunkt
(``ergebnisse.profil_eines_betriebspunkts``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from .stil import (BLAU_HELL, BLAU_MITTEL, GRUEN, KAMERA_FARBEN, PlotStil, formatiere_achsen,
                   neue_figur, rc, t, zahl)


def _kamerafenster(profil: pd.DataFrame):
    """Kamerafenster [m] und Offsets [mm] aus den konstanten Spalten der Profiltabelle."""
    erste = profil.iloc[0]
    fenster, offsets = [], []
    for j in (1, 2, 3):
        zmin, zmax = erste.get(f"cam{j}_z_min_m", np.nan), erste.get(f"cam{j}_z_max_m", np.nan)
        if np.isfinite(zmin) and np.isfinite(zmax):
            o = erste.get(f"fit_offset_o{j}_m", np.nan)
            fenster.append((float(zmin), float(zmax)))
            offsets.append(float(o) * 1000.0 if np.isfinite(o) else 0.0)
    return fenster, offsets


def _fit_mit_offsets(z, L_m, offsets_mm, fenster):
    """Fitkurve plus Offset der jeweiligen Kamera; zwischen den Fenstern linear überblendet."""
    y = L_m * 1000.0
    if not fenster:
        return y.copy(), np.zeros_like(y, dtype=bool)
    off = np.full_like(z, np.nan, dtype=float)
    for j, (a, b) in enumerate(fenster):
        off[(z >= a) & (z <= b)] = offsets_mm[j]
    for j in range(len(fenster) - 1):
        a, b = fenster[j][1], fenster[j + 1][0]
        m = (z > a) & (z < b)
        if m.any() and b > a:
            off[m] = offsets_mm[j] + (z[m] - a) / (b - a) * (offsets_mm[j + 1] - offsets_mm[j])
    off[z < fenster[0][0]] = offsets_mm[0]
    off[z > fenster[-1][1]] = offsets_mm[-1]
    im_fenster = np.zeros_like(z, dtype=bool)
    for a, b in fenster:
        im_fenster |= (z >= a) & (z <= b)
    return y + off, im_fenster


def _abschnitte(maske):
    """Zusammenhängende True-Abschnitte als (start, ende)-Indexpaare."""
    idx = np.where(maske)[0]
    if idx.size == 0:
        return []
    grenzen = np.where(np.diff(idx) > 1)[0]
    teile, start = [], idx[0]
    for s in grenzen:
        teile.append((start, idx[s] + 1))
        start = idx[s + 1]
    teile.append((start, idx[-1] + 1))
    return teile


def _glaetten(y):
    """Savitzky-Golay-Glättung (Ordnung 3) der druckkorrigierten Blasenlänge."""
    ok = np.isfinite(y)
    if ok.sum() < 15:
        return y
    w = max(5, min(31, ok.sum() // 2 * 2 - 1))
    w += (w % 2 == 0)
    aus = np.full_like(y, np.nan)
    aus[ok] = savgol_filter(y[ok], window_length=w, polyorder=3, mode="interp")
    return aus


def blasenlaengen_fit(profil: pd.DataFrame, kennwerte: pd.Series, stil: PlotStil, titel: str = ""):
    """
    Blasenlängen-Fit eines Betriebspunkts.

    Parameter
    ---------
    profil : Profiltabelle des Betriebspunkts
    kennwerte : Zeile der Betriebspunkt-Tabelle (für R² und chi²_red)
    """
    z = profil["Position_z_m"].values
    z_mess = profil["z_meas_m"].dropna().values
    L_mess = profil["L_b_meas_m"].dropna().values
    fenster, offsets = _kamerafenster(profil)
    L_off, im_fenster = _fit_mit_offsets(z, profil["L_bubble_fit_m"].values, offsets, fenster)
    L_korr = _glaetten(profil["L_bubble_corrected_m"].values * 1000.0)

    with rc(stil):
        fig, ax = neue_figur(stil, stil.groesse_profil_cm)
        for j, (a, b) in enumerate(fenster):
            ax.axvspan(a * 100, b * 100, facecolor="lightgray", alpha=0.25, zorder=0)
            ax.text((a + b) * 50, 0.03, f"{t('kamera', stil)} {j + 1}", transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=stil.schriftgroesse * 0.8, color="0.35", style="italic")
        kamera = np.full(len(z_mess), -1)
        for i, zm in enumerate(z_mess):
            for j, (a, b) in enumerate(fenster):
                if a <= zm <= b:
                    kamera[i] = j
                    break
        for j in range(len(fenster)):
            sel = kamera == j
            if sel.any():
                ax.scatter(z_mess[sel] * 100, L_mess[sel] * 1000, s=22, edgecolors="k", linewidths=0.4,
                           color=KAMERA_FARBEN[j % len(KAMERA_FARBEN)], alpha=0.85, zorder=5,
                           label=t("messwerte_kamera", stil, j=j + 1))
        ax.plot(z * 100, profil["L_bubble_fit_m"].values * 1000, color=BLAU_HELL, ls="--", lw=1.4,
                zorder=2, label=t("fit_ohne", stil))
        for k, (s, e) in enumerate(_abschnitte(im_fenster)):
            ax.plot(z[s:e] * 100, L_off[s:e], color=BLAU_MITTEL, lw=2.0, zorder=4,
                    label=t("fit_mit", stil) if k == 0 else None)
        for k, (s, e) in enumerate(_abschnitte(~im_fenster & np.isfinite(L_off))):
            ax.plot(z[s:e] * 100, L_off[s:e], color=BLAU_MITTEL, ls=":", lw=1.3, alpha=0.7, zorder=3,
                    label=t("fit_mit_zwischen", stil) if k == 0 else None)
        ok = np.isfinite(L_korr)
        if ok.any():
            ax.plot(z[ok] * 100, L_korr[ok], color=GRUEN, lw=2.0, zorder=4, label=t("L_korr", stil))

        r2, chi2 = float(kennwerte.get("fit_r2", np.nan)), float(kennwerte.get("fit_chi2_red", np.nan))
        zeilen = [f"$o_{j + 1}$ = {o:+.4f} mm" for j, o in enumerate(offsets)]
        if stil.sprache == "de":
            zeilen = [z.replace(".", ",") for z in zeilen]
        zeilen += [f"$R^2$ = {zahl(r2, stil, 4)}", f"$\\chi^2_{{red}}$ = {zahl(chi2, stil, 3)}"]
        ax.text(0.985, 0.985, "\n".join(zeilen), transform=ax.transAxes, ha="right", va="top",
                fontsize=stil.schriftgroesse * 0.85,
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="0.6", alpha=0.95))
        ax.set_xlabel(t("z_cm", stil))
        ax.set_ylabel(t("L_b_mm", stil))
        if stil.titel_anzeigen and titel:
            ax.set_title(titel)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3,
                  fontsize=stil.schriftgroesse * 0.8, framealpha=0.9)
        formatiere_achsen(ax, stil)
    return fig


def stoffmenge(profil: pd.DataFrame, stil: PlotStil, titel: str = ""):
    """Absorbierte CO2-Stoffmenge je Blase über der Reaktorposition."""
    z = profil["Position_z_m"].values * 100
    n = profil["Diffused_Gas_mol"].values * 1e6
    ok = np.isfinite(z) & np.isfinite(n)
    with rc(stil):
        fig, ax = neue_figur(stil, stil.groesse_profil_cm)
        ax.plot(z[ok], n[ok], color=GRUEN, lw=2)
        ax.fill_between(z[ok], 0, n[ok], color=GRUEN, alpha=0.2)
        ax.set_xlabel(t("z_cm", stil))
        ax.set_ylabel(t("dn_umol", stil))
        if stil.titel_anzeigen and titel:
            ax.set_title(titel)
        formatiere_achsen(ax, stil)
    return fig


def druckprofil(profil: pd.DataFrame, stil: PlotStil, titel: str = ""):
    """Berechneter Absolutdruck über der Reaktorposition."""
    z = profil["Position_z_m"].values * 100
    p = profil["Pressure_Pa"].values
    ok = np.isfinite(z) & np.isfinite(p)
    with rc(stil):
        fig, ax = neue_figur(stil, stil.groesse_profil_cm)
        ax.plot(z[ok], p[ok], color=BLAU_MITTEL, lw=2)
        ax.set_xlabel(t("z_cm", stil))
        ax.set_ylabel(t("p_pa", stil))
        if stil.titel_anzeigen and titel:
            ax.set_title(titel)
        formatiere_achsen(ax, stil)
    return fig
