# -*- coding: utf-8 -*-
"""
Geometrie einer Taylor-Blase im runden oder quadratischen Kanal.

Die Blase wird als Zylinder (rund) bzw. Quader (quadratisch) mit zwei
halbkugel- bzw. halbellipsoidförmigen Kappen beschrieben. Das Kappenvolumen
beider Kappen zusammen ist in beiden Fällen V_caps = π/6 · d_b³.
"""

from __future__ import annotations

import numpy as np


def blasengeometrie(d_blase, L_blase, geometrie: str) -> dict:
    """
    Querschnitt, Zylinderlänge und Volumen einer Taylor-Blase.

    Parameter
    ---------
    d_blase : Blasendurchmesser bzw. -seitenlänge nach Abzug des Films [m]
    L_blase : Blasenlänge [m] (Skalar oder Array)
    geometrie : "circular" oder "rectangular"

    Rückgabe
    --------
    dict mit A_bubble [m²], L_cyl [m], V_bubble [m³], V_caps [m³]
    """
    L_cyl = np.maximum(0.0, L_blase - d_blase)
    if geometrie == "circular":
        A_bubble = np.pi * (d_blase / 2.0) ** 2
    elif geometrie == "rectangular":
        A_bubble = d_blase ** 2
    else:
        raise ValueError(f"Unbekannte Geometrie '{geometrie}' (erwartet: circular, rectangular).")
    V_caps = (np.pi / 6.0) * d_blase ** 3
    return {"A_bubble": A_bubble, "L_cyl": L_cyl,
            "V_bubble": V_caps + A_bubble * L_cyl, "V_caps": V_caps}
