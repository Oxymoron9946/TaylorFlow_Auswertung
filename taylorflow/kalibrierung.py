# -*- coding: utf-8 -*-
"""
Druckkalibrierung: Bretherton-Faktor c für runde Kanäle.

Status: übernommen aus dem Forschungspraktikum, noch nicht abschließend
validiert (siehe Handbuch, Kapitel 10). Für eckige Kanäle wird nicht
kalibriert, dort gilt Kurimoto (2020) ohne freien Faktor.

Idee (je Betriebspunkt einer Messung ohne Stoffübergang, 0 mol-% CO2):

1. Blasenlänge, Sluglänge und Geschwindigkeit linear über z fitten.
2. Realer Druckverlust aus der Blasenexpansion (ideales Gas, Volumen ~ Länge):
       p_trocken,ein = p_trocken,aus · L_B(Ende) / L_B(0),   Δp_real = p_ein − p_aus
3. Bretherton-Modell zerlegen: dp/dz = Basis + c · Zusatzterm
   (Basis mit c = 0, Zusatzterm = Modell(c = 1) − Modell(c = 0)), über z integriert.
4. c = (Δp_real − Δp_Basis) / Δp_Zusatz

Über alle Betriebspunkte wird zusätzlich ein Ersatzmodell c(u_G, u_L) angepasst
(Linear, Polynomial oder Power-Law), das die Auswertung außerhalb der
kalibrierten Punkte nutzt.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import OptimizeWarning, curve_fit

from . import stoffdaten
from .druckverlust import druckgradient_einheitszelle
from .einlesen import Messreihe, lade_messdaten
from .fits import linear
from .parameter import AuswerteParameter

ERSATZMODELLE = {
    "Linear": (lambda x, a, b, c: a * x[0] + b * x[1] + c, 3),
    "Polynomial": (lambda x, a, b, c, d: a * x[0] + b * x[1] + c * (x[0] * x[1]) + d, 4),
    "Power-Law": (lambda x, a, b, c: a * np.maximum(x[0], 1e-6) ** b * np.maximum(x[1], 1e-6) ** c, 3),
}


@dataclass
class Kalibrierung:
    """Ergebnis der Kalibrierung eines Kanals."""
    kalibrier_key: str
    punkte: pd.DataFrame                                  # u_gas, u_liq, c_calib je Betriebspunkt
    ersatzmodelle: dict = field(default_factory=dict)     # Name -> {"params", "r2", "aic"}


def _fit_linear_gewichtet(z, y, sigma=None):
    popt, _ = curve_fit(linear, z, y, sigma=sigma, absolute_sigma=sigma is not None)
    return lambda x, p=popt: linear(np.asarray(x, dtype=float), *p)


def kalibriere(reihe: Messreihe, p: AuswerteParameter, ausschluesse: dict, ausgabe=print) -> Kalibrierung | None:
    """Berechnet c je Betriebspunkt und passt die Ersatzmodelle an (nur runde Kanäle)."""
    if reihe.geometrie != "circular":
        ausgabe(f"{reihe.kalibrier_key}: eckiger Kanal, keine Kalibrierung (Kurimoto ohne freien Faktor).")
        return None
    df = lade_messdaten(reihe, ausschluesse, p, ausgabe)
    zeilen = []
    for _, bp in df[["GasVelocity", "LiquidVelocity"]].drop_duplicates().iterrows():
        gas, liq = bp["GasVelocity"], bp["LiquidVelocity"]
        d = df[(df["GasVelocity"] == gas) & (df["LiquidVelocity"] == liq)].sort_values("BinCenter_mm")
        T = d["Temperatur_C"].mean() + 273.15
        P_aus = d["Druck_Pa_Auslass"].mean()
        if not np.isfinite(P_aus) or P_aus <= 0:
            continue
        try:
            stoff = stoffdaten.fluessigkeit(p.fluessigkeit, T=T, P=P_aus)
            P_v = stoffdaten.dampfdruck(p.fluessigkeit, T=T)
        except ValueError as e:
            warnings.warn(f"Stoffdaten fehlen bei {gas}/{liq}: {e}")
            continue
        z_m = d["BinCenter_mm"].values * 1e-3
        L_b = d["mean_BubbleLength_mm"].values * 1e-3
        L_s = d["mean_UnitCellLength_mm"].values * 1e-3 - L_b
        try:
            f_b = _fit_linear_gewichtet(z_m, L_b, d["std_BubbleLength_mm"].values * 1e-3 + 1e-6)
            f_s = _fit_linear_gewichtet(z_m, L_s)
            f_u = _fit_linear_gewichtet(z_m, d["mean_Speed_m_s"].values)
        except Exception as e:
            warnings.warn(f"Fit fehlgeschlagen bei {gas}/{liq}: {e}")
            continue
        z = np.arange(0, reihe.laenge_m + p.dz_m, p.dz_m)
        L_b_fit = np.maximum(f_b(z), 1e-6)
        L_s_fit = np.maximum(f_s(z), 1e-5)
        U_fit = np.maximum(f_u(z), 1e-3)

        P_tr_aus = max(1.0, P_aus - P_v)
        dp_real = P_tr_aus * (L_b_fit[-1] / L_b_fit[0]) + P_v - P_aus

        basis = np.zeros_like(z)
        zusatz = np.zeros_like(z)
        for i in range(len(z)):
            argumente = (float(U_fit[i]), float(stoff["mu"]), float(stoff["rho"]), float(stoff["sigma"]),
                         float(reihe.d_kanal_m), float(L_s_fit[i]), float(L_b_fit[i]), reihe.geometrie)
            b0, _ = druckgradient_einheitszelle(*argumente, c_bretherton=0.0)
            b1, _ = druckgradient_einheitszelle(*argumente, c_bretherton=1.0)
            basis[i], zusatz[i] = b0, b1 - b0
        dp_basis, dp_zusatz = np.sum(basis) * p.dz_m, np.sum(zusatz) * p.dz_m
        if dp_zusatz < 1e-10:
            continue
        c = (dp_real - dp_basis) / dp_zusatz
        if np.isfinite(c):
            zeilen.append({"u_gas": float(gas), "u_liq": float(liq), "c_calib": float(c),
                           "dp_real_Pa": float(dp_real)})
            ausgabe(f"  u_G = {gas}, u_L = {liq}: Δp_real = {dp_real:.1f} Pa, c = {c:.4f}")

    punkte = pd.DataFrame(zeilen)
    erg = Kalibrierung(reihe.kalibrier_key, punkte)
    if len(punkte) >= 4:
        x = (punkte["u_gas"].values, punkte["u_liq"].values)
        y = punkte["c_calib"].values
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            for name, (f, k) in ERSATZMODELLE.items():
                if len(y) < k:
                    continue
                try:
                    popt, _ = curve_fit(f, x, y, p0=[1.0] * k, maxfev=10000)
                except Exception:
                    continue
                res = y - f(x, *popt)
                ss_tot = np.sum((y - y.mean()) ** 2)
                r2 = max(0.0, 1 - np.sum(res ** 2) / ss_tot) if ss_tot > 0 else 0.0
                aic = len(y) * np.log(np.sum(res ** 2) / len(y)) + 2 * k
                erg.ersatzmodelle[name] = {"params": [float(v) for v in popt], "r2": float(r2), "aic": float(aic)}
    return erg


def waehle_ersatzmodell(erg: Kalibrierung, wahl: str = "auto") -> str | None:
    """'auto' = größtes R²; sonst der angegebene Name."""
    if not erg.ersatzmodelle:
        return None
    if wahl == "auto":
        return max(erg.ersatzmodelle, key=lambda n: erg.ersatzmodelle[n]["r2"])
    if wahl not in erg.ersatzmodelle:
        raise ValueError(f"Ersatzmodell '{wahl}' nicht verfügbar: {sorted(erg.ersatzmodelle)}")
    return wahl


def schreibe_in_datenbank(erg: Kalibrierung, modell: str | None, datei: Path) -> None:
    """
    Schreibt den Eintrag des Kanals. Manuell gesetzte Felder (USE, NOTE und alle
    weiteren unbekannten Felder) eines bestehenden Eintrags bleiben erhalten.
    """
    datei = Path(datei)
    db = {}
    if datei.exists():
        with open(datei, "r", encoding="utf-8") as f:
            db = json.load(f)
    eintrag = dict(db.get(erg.kalibrier_key, {}))
    m = erg.ersatzmodelle.get(modell, {}) if modell else {}
    eintrag.update({
        "u_gas": erg.punkte["u_gas"].tolist(),
        "u_liq": erg.punkte["u_liq"].tolist(),
        "c_calib": erg.punkte["c_calib"].tolist(),
        "fallback_model": modell,
        "fallback_r2": m.get("r2", 0.0),
        "fallback_params": m.get("params", []),
    })
    db[erg.kalibrier_key] = eintrag
    with open(datei, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)
