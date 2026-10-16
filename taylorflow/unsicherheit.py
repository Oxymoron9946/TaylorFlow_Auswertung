# -*- coding: utf-8 -*-
"""
Relative Messunsicherheit des volumetrischen Stoffübergangs entlang z.

Die Auswertung (``pipeline``) ruft diese Funktion nicht auf; sie steht für
eigene Unsicherheitsbetrachtungen zur Verfügung. Die Eingangsgrößen liefert
die Profiltabelle eines Betriebspunkts, die Unsicherheiten der Einzelgrößen
stehen in ``config.PARAMETER`` (Abschnitt „Messunsicherheiten“).

Fortpflanzung (Gauß, unkorreliert):

    u_rel(kLa)² = u_rel(dn/dt)² + u_rel(V_L)² + u_rel(ΔC)²

    u_rel(V_L)  = Pixelunsicherheit / Blasenlänge in Pixeln
    u(ΔC)²      = u(C*)² + u(C_L)²,  u(C*) aus Henry-Konstante und p_CO2,
                  u(C_L) kumuliert aus den Zuwächsen von C_L entlang z
"""

from __future__ import annotations

import numpy as np

from .parameter import AuswerteParameter


def relative_unsicherheit(L_b_fit, treibende_kraft, C_star, p: AuswerteParameter) -> np.ndarray:
    """
    Relative Unsicherheit des Stoffübergangs je Gitterpunkt [-].

    Parameter
    ---------
    L_b_fit : gefittete Blasenlänge [m]
    treibende_kraft : ΔC = C* − C_L [mol/m³]
    C_star : C*(z) [mol/m³]; C_L wird mit C* am Einlass rekonstruiert
    """
    C_star = np.asarray(C_star, dtype=float)
    u_rel_C_star = np.sqrt(p.u_rel_h_cp ** 2 + p.u_rel_p_co2 ** 2)
    u_abs_C_star = u_rel_C_star * C_star
    L_b_px = (np.asarray(L_b_fit, dtype=float) * 1000.0) / p.k_opt_mm_pro_px
    u_rel_V_L = p.pixel_unsicherheit_px / np.maximum(L_b_px, 1.0)
    C_L = np.maximum(0.0, C_star[0] - treibende_kraft)
    dC_L = np.zeros_like(C_L)
    dC_L[0] = C_L[0]
    if len(C_L) > 1:
        dC_L[1:] = np.diff(C_L)
    u_rel_schritt = np.sqrt(p.u_rel_dn_dt ** 2 + u_rel_V_L ** 2)
    u_abs_C_L = np.sqrt(np.cumsum((dC_L * u_rel_schritt) ** 2))
    u_abs_dC = np.sqrt(u_abs_C_star ** 2 + u_abs_C_L ** 2)
    u_rel_dC_voll = u_abs_dC / np.maximum(treibende_kraft, 1e-6)
    return np.sqrt(p.u_rel_dn_dt ** 2 + u_rel_V_L ** 2 + u_rel_dC_voll ** 2)
