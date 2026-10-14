# -*- coding: utf-8 -*-
"""
Volumetrischer Stoffübergangskoeffizient kLa (METHODIK §6 und §7).

Lokal:     kLa(z) = (dn/dz · U) / (V_L · ΔC(z))         [Yue2007]
Log-Mean:  kLa_log = ln(ΔC_ein / ΔC_aus) / t_res         [Kashid2011]

ΔC = C* − C_L ist die treibende Konzentrationsdifferenz. Ausgewertet wird
nur die aktive Zone: ΔC > 0 und relative Unsicherheit u_rel(ΔC) <= Grenzwert.

Quellen:
    [Yue2007]    Yue, J. et al. (2007). Chem. Eng. Sci. 62(7), 2096-2108.
    [Kashid2011] Kashid, M. N. et al. (2011). Chem. Eng. Sci. 66(14), 3876-3897.
"""

from __future__ import annotations

import numpy as np

from .parameter import AuswerteParameter


def kla_profile(z, U_fit, L_b_fit, dn_dz, treibende_kraft, C_star_start,
                V_L, C_star_lokal, p: AuswerteParameter) -> dict:
    """
    Lokaler kLa, kLa_log_mean und relative Unsicherheit des lokalen kLa.

    Parameter
    ---------
    z : Ortsgitter [m]
    U_fit, L_b_fit : Blasengeschwindigkeit [m/s] und Blasenlänge [m]
    dn_dz : Ableitung der absorbierten Stoffmenge je Blase [mol/m]
    treibende_kraft : ΔC = C* − C_L [mol/m³]
    C_star_start : C* am Einlass [mol/m³]
    V_L : Flüssigkeitsvolumen je Einheitszelle [m³]
    C_star_lokal : C*(z) [mol/m³]

    Rückgabe
    --------
    dict mit kLa_lokal [1/s], kLa_log_mean [1/s], u_rel_kLa_lokal [-]
    """
    dn_dt = dn_dz * U_fit

    # --- Aktive Zone: u_rel(ΔC) aus dem C*-Anteil der Unsicherheit ---------------
    u_rel_C_star = np.sqrt(p.u_rel_h_cp ** 2 + p.u_rel_p_co2 ** 2)
    u_abs_C_star = u_rel_C_star * np.asarray(C_star_lokal, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        u_rel_dC = np.where(treibende_kraft > 0,
                            u_abs_C_star / np.maximum(treibende_kraft, 1e-12), np.inf)
    aktiv = (treibende_kraft > 0) & (u_rel_dC <= p.max_urel_delta_c)

    kLa_lokal = np.zeros_like(z)
    kLa_lokal[aktiv] = dn_dt[aktiv] / (V_L * treibende_kraft[aktiv])

    # --- Log-Mean über die aktive Zone ---------------------------------------
    idx = np.where(aktiv)[0]
    kLa_log_mean = 0.0
    if len(idx) >= p.logmean_min_aktive_punkte:
        i_ein, i_aus = idx[0], idx[-1]
        dC_ein = treibende_kraft[i_ein]
        dC_aus = treibende_kraft[i_aus]
        # Verweilzeit vom ersten bis einschließlich zum letzten aktiven Punkt
        # (bis Version 2.x endete die Integration einen Gitterpunkt zu früh).
        t_res = np.trapezoid(1.0 / U_fit[i_ein:i_aus + 1], x=z[i_ein:i_aus + 1])
        if dC_aus > 0 and dC_ein > dC_aus and t_res > 0:
            kLa_log_mean = (1.0 / t_res) * np.log(dC_ein / dC_aus)

    # --- Relative Unsicherheit des lokalen kLa (METHODIK §6.2) ----------------
    L_b_px = (L_b_fit * 1000.0) / p.k_opt_mm_pro_px
    u_rel_V_L = p.pixel_unsicherheit_px / np.maximum(L_b_px, 1.0)
    # Bekannte Einschränkung: C_L wird hier mit C*_start statt C*(z) rekonstruiert
    # (siehe docs/07_grenzen.md). Wirkt nur auf u_rel_kLa, nicht auf kLa.
    C_L = np.maximum(0.0, C_star_start - treibende_kraft)
    dC_L = np.zeros_like(C_L)
    dC_L[0] = C_L[0]
    if len(C_L) > 1:
        dC_L[1:] = np.diff(C_L)
    u_rel_schritt = np.sqrt(p.u_rel_dn_dt ** 2 + u_rel_V_L ** 2)
    u_abs_C_L = np.sqrt(np.cumsum((dC_L * u_rel_schritt) ** 2))
    u_abs_dC = np.sqrt(u_abs_C_star ** 2 + u_abs_C_L ** 2)
    u_rel_dC_voll = u_abs_dC / np.maximum(treibende_kraft, 1e-6)
    u_rel_kLa = np.sqrt(p.u_rel_dn_dt ** 2 + u_rel_V_L ** 2 + u_rel_dC_voll ** 2)

    return {"kLa_lokal": kLa_lokal, "kLa_log_mean": kLa_log_mean, "u_rel_kLa_lokal": u_rel_kLa}
