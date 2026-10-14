# -*- coding: utf-8 -*-
"""
Kapillarzahl und Filmdicke im Taylor-Flow.

Quellen:
    [Bretherton1961] Bretherton, F. P. (1961). J. Fluid Mech. 10(2), 166-188.
    [Aussillous2000] Aussillous, P., Quéré, D. (2000). Phys. Fluids 12, 2367-2371.
    [Kreutzer2001]   Kreutzer, M. T. (2003). Hydrodynamics of Taylor flow in
                     capillaries and monolith reactors. Diss. TU Delft;
                     Thulasidas et al. (1995), Chem. Eng. Sci. 50, 183-199.
"""

from __future__ import annotations

import math


def kapillarzahl(mu: float, u: float, sigma: float) -> float:
    """Kapillarzahl Ca = mu * u / sigma [-]."""
    return mu * u / sigma


def filmdicke(d_kanal: float, ca: float, geometrie: str) -> tuple[float, str]:
    """
    Dicke des Flüssigkeitsfilms zwischen Blase und Wand.

    Modellwahl:
        rund, Ca <= 0,005:        Bretherton   δ = r · 1,34 Ca^(2/3)
        rund, 0,005 < Ca <= 1,5:  Aussillous   δ = r · 1,34 Ca^(2/3) / (1 + 3,35 Ca^(2/3))
        rund, Ca > 1,5:           Näherung     δ = 0,05 d (mit Hinweis)
        eckig:                    Kreutzer     δ/d = 0,357 − 0,25 exp(−2,25 Ca^0,445)

    Parameter
    ---------
    d_kanal : Kanaldurchmesser bzw. Seitenlänge [m]
    ca : Kapillarzahl [-]
    geometrie : "circular" oder "rectangular"

    Rückgabe
    --------
    (δ [m], Hinweis) – der Hinweis ist leer, wenn das Modell gültig ist.
    """
    r = d_kanal / 2.0
    if geometrie in ("rectangular", "square"):
        return d_kanal * (0.357 - 0.25 * math.exp(-2.25 * (ca ** 0.445))), \
            "Kreutzer/Thulasidas Modell für quadratische Kanäle."
    if ca <= 0.005:
        return r * 1.34 * (ca ** (2.0 / 3.0)), ""
    if ca <= 1.5:
        ca23 = ca ** (2.0 / 3.0)
        return r * (1.34 * ca23 / (1.0 + 1.34 * 2.5 * ca23)), ""
    return 0.05 * d_kanal, f"Ca = {ca:.3f} > 1.5: Modell ungültig. Nutze Näherung."
