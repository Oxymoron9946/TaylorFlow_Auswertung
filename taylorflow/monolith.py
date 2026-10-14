# -*- coding: utf-8 -*-
"""
Auswertung der Monolith-Messungen (Gasbilanz über Ein- und Austritt).

Eingangsdatei (eine Zeile je Betriebspunkt, Semikolon-getrennt):

    V_L_L_h      Flüssigkeitsvolumenstrom [L/h]
    V_G_in_L_h   Gasvolumenstrom Eintritt [L/h]
    V_G_out_L_h  Gasvolumenstrom Austritt [L/h]
    y_CO2_in     CO2-Anteil Eintritt [%]
    y_CO2_out    CO2-Anteil Austritt [%]
    T_in_C       Temperatur Eintritt [°C]
    T_out_C      Temperatur Austritt [°C]
    p_in_Pa      Druck Eintritt [Pa]
    p_out_Pa     Druck Austritt [Pa]

Rechnung (alle Kanäle zusammen, Querschnitt A = N · d²):

    u_G = V̇_G,ein / A,  u_L = V̇_L / A                    Leerrohrgeschwindigkeiten
    ṅ   = V̇_G,ein · c_G,ein − V̇_G,aus · c_G,aus           c_G = p · y / (R T)
    ṅ_spez = ṅ / (A · L)
    C*  = H(T) · p · y,   H(T) = H_ref · exp(dlnH/dT · (1/T − 1/298,15))
    t   = L / u_L,  V_L = V̇_L · t,  C_L,aus = ṅ t / V_L
    kLa = ṅ / (V_L · ΔC_log),  ΔC_log = (ΔC_ein − ΔC_aus) / ln(ΔC_ein / ΔC_aus)

Betriebspunkte mit ΔC_aus <= 0 (Flüssigkeit am Austritt gesättigt) erhalten
kein kLa (NaN).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import griddata

R_GAS = 8.314


def berechne(datei: Path, n_kanaele: int = 100, d_kanal_m: float = 1e-3, laenge_m: float = 1.0,
             henry_ref_mol_m3_pa: float = 3.3e-4, henry_dlnh_dt_k: float = 2400.0) -> pd.DataFrame:
    """Kennwerte je Betriebspunkt: u_G, u_L [m/s], kLa [1/s], n_spez [mol/(s m³)], gesaettigt."""
    df = pd.read_csv(datei, sep=";")
    A = n_kanaele * d_kanal_m ** 2
    V = A * laenge_m
    v_L = df["V_L_L_h"].values * 1e-3 / 3600.0
    v_Gi = df["V_G_in_L_h"].values * 1e-3 / 3600.0
    v_Go = df["V_G_out_L_h"].values * 1e-3 / 3600.0
    y_in, y_out = df["y_CO2_in"].values / 100.0, df["y_CO2_out"].values / 100.0
    T_in, T_out = df["T_in_C"].values + 273.15, df["T_out_C"].values + 273.15
    p_in, p_out = df["p_in_Pa"].values.astype(float), df["p_out_Pa"].values.astype(float)

    def henry(T):
        return henry_ref_mol_m3_pa * np.exp(henry_dlnh_dt_k * (1.0 / T - 1.0 / 298.15))

    u_G, u_L = v_Gi / A, v_L / A
    n_dot = v_Gi * (p_in * y_in) / (R_GAS * T_in) - v_Go * (p_out * y_out) / (R_GAS * T_out)
    t_res = laenge_m / u_L
    V_L = v_L * t_res
    dC_ein = henry(T_in) * p_in * y_in
    dC_aus = henry(T_out) * p_out * y_out - n_dot * t_res / V_L
    gesaettigt = dC_aus <= 0
    kla = np.full(len(df), np.nan)
    ok = ~gesaettigt
    dC_log = (dC_ein[ok] - dC_aus[ok]) / np.log(dC_ein[ok] / dC_aus[ok])
    kla[ok] = n_dot[ok] / (V_L[ok] * dC_log)
    return pd.DataFrame({"u_G": u_G, "u_L": u_L, "kla": kla, "n_spez": n_dot / V, "gesaettigt": gesaettigt})


def interpoliere(x, y, z, x_ziel, y_ziel) -> np.ndarray:
    """Interpoliert z(x, y) auf Zielpunkte (kubisch ab 8 Punkten, sonst linear; außen nächster Punkt)."""
    x, y, z = (np.asarray(v, dtype=float) for v in (x, y, z))
    ok = np.isfinite(z)
    pts = np.column_stack([x[ok], y[ok]])
    ziel = np.column_stack([np.asarray(x_ziel, float), np.asarray(y_ziel, float)])
    aus = griddata(pts, z[ok], ziel, method="cubic" if ok.sum() >= 8 else "linear")
    leer = ~np.isfinite(aus)
    if leer.any():
        aus[leer] = griddata(pts, z[ok], ziel[leer], method="nearest")
    return aus
