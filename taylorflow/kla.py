# -*- coding: utf-8 -*-
"""
Volumetrischer Stoffübergangskoeffizient kLa (Handbuch, Kapitel 7.6).

    kLa_log = ln(ΔC_ein / ΔC_aus) / t_res         [Kashid2011]

ΔC = C* − C_L ist die treibende Konzentrationsdifferenz. Ausgewertet wird
nur die aktive Zone: ΔC > 0 und relative Unsicherheit u_rel(ΔC) <= Grenzwert.

Quelle:
    [Kashid2011] Kashid, M. N. et al. (2011). Chem. Eng. Sci. 66(14), 3876-3897.
"""

from __future__ import annotations

import numpy as np

from .parameter import AuswerteParameter


def aktive_zone(treibende_kraft, C_star, p: AuswerteParameter) -> np.ndarray:
    """
    Maske der aktiven Zone.

    Ein Gitterpunkt ist aktiv, wenn ΔC > 0 ist und die Unsicherheit von C*
    (Henry-Konstante und CO2-Partialdruck) höchstens ``p.max_urel_delta_c``
    von ΔC ausmacht. In gesättigten Abschnitten ist ΔC so klein, dass die
    Unsicherheit überwiegt; dort ist kein kLa bestimmbar.

    Parameter
    ---------
    treibende_kraft : ΔC = C* − C_L [mol/m³]
    C_star : C*(z) [mol/m³]
    """
    u_rel_C_star = np.sqrt(p.u_rel_h_cp ** 2 + p.u_rel_p_co2 ** 2)
    u_abs_C_star = u_rel_C_star * np.asarray(C_star, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        u_rel_dC = np.where(treibende_kraft > 0,
                            u_abs_C_star / np.maximum(treibende_kraft, 1e-12), np.inf)
    return (treibende_kraft > 0) & (u_rel_dC <= p.max_urel_delta_c)


def kla_log_mean(z, U_fit, treibende_kraft, aktiv, p: AuswerteParameter) -> float:
    """
    Logarithmisch gemitteltes kLa über die aktive Zone [1/s].

    Verweilzeit vom ersten bis einschließlich zum letzten aktiven Punkt.
    Ergibt 0, wenn weniger als ``p.logmean_min_aktive_punkte`` Punkte aktiv
    sind oder ΔC in der aktiven Zone nicht abnimmt.

    Parameter
    ---------
    z : Ortsgitter [m]
    U_fit : Blasengeschwindigkeit [m/s]
    treibende_kraft : ΔC = C* − C_L [mol/m³]
    aktiv : Maske der aktiven Zone (``aktive_zone``)
    """
    idx = np.where(aktiv)[0]
    if len(idx) < p.logmean_min_aktive_punkte:
        return 0.0
    i_ein, i_aus = idx[0], idx[-1]
    dC_ein = treibende_kraft[i_ein]
    dC_aus = treibende_kraft[i_aus]
    t_res = np.trapezoid(1.0 / U_fit[i_ein:i_aus + 1], x=z[i_ein:i_aus + 1])
    if dC_aus > 0 and dC_ein > dC_aus and t_res > 0:
        return (1.0 / t_res) * np.log(dC_ein / dC_aus)
    return 0.0
