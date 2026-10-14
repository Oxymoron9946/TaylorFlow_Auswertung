# -*- coding: utf-8 -*-
"""
Druckverlust einer Taylor-Flow-Einheitszelle (Slug + Blase).

Runde Kanäle:   Bretherton-Modell (aufbereitet nach Fries 2008) mit einem
                Faktor c, der aus der Druckkalibrierung stammt
                (``data/calibrated_c_database.json``) oder dem Theoriewert
                c = 0,465 entspricht.
Eckige Kanäle:  Kurimoto et al. (2020), Gl. 27/28, ohne Kalibrierung.

Quellen:
    [Bretherton1961] Bretherton, F. P. (1961). J. Fluid Mech. 10(2), 166-188.
    [Fries2008]      Fries, D. M. et al. (2008). Int. J. Multiphase Flow 34.
    [Kurimoto2020]   Kurimoto, R. et al. (2020). Chem. Eng. Sci.
    [Liu2005]        Liu, H. et al. (2005). Ind. Eng. Chem. Res. 44(14), 4884-4897.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import griddata


def schlupf_warnung(u_tp: float, mu_l: float, sigma: float) -> str:
    """Warnung, falls das Schlupfmodell nach [Liu2005] seinen Bereich verlässt (Ca > 1)."""
    if u_tp <= 0 or sigma <= 0:
        return "Fehler: U_tp oder Oberflächenspannung (sigma) ungültig."
    ca = mu_l * u_tp / sigma
    if ca > 1.0:
        return f"Warnung: Ca = {ca:.3f} > 1. Das Slip-Modell verlässt seinen Gültigkeitsbereich."
    return ""


def bretherton(u_tp, l_slug, d, mu_l, rho_l, sigma, c_bretherton) -> tuple[float, str]:
    """
    Druckverlust der Einheitszelle im runden Kanal [Pa].

        f_app = 16/Re · [1 + c · (d/L_S) · Ca^(-1/3)]
        Δp    = 2 · f_app · ρ_L · u_TP² · L_S / d
    """
    if any(v <= 0 for v in (u_tp, l_slug, d, mu_l, rho_l, sigma)):
        return 0.0, "Fehler: Ungültige/Null-Eingaben für Bretherton-Modell."
    re = rho_l * u_tp * d / mu_l
    ca = mu_l * u_tp / sigma
    f_app = (16.0 / re) * (1.0 + c_bretherton * (d / l_slug) * (1.0 / ca) ** (1.0 / 3.0))
    dp = 2.0 * f_app * rho_l * (u_tp ** 2) * (l_slug / d)
    warnung = ""
    if ca > 0.005:
        warnung = f"Warnung (Bretherton): Ca = {ca:.4f} > 0.005. Modell gilt nur für sehr kleine Ca."
    return dp, warnung


def kurimoto(u_tp, l_slug, l_bubble, d, mu_l, rho_l, sigma) -> tuple[float, float, str]:
    """
    Druckverlust im quadratischen Kanal nach [Kurimoto2020] (Slug- und Blasenanteil [Pa]).

    Gültigkeit (Kurimoto 2024): 0,00159 <= Ca <= 0,0989; 0,0817 <= We <= 25,4;
    8,33 <= Re <= 791; L_B/d >= ca. 2,3.
    """
    if any(v <= 0 for v in (u_tp, l_slug, d, mu_l, rho_l, sigma)):
        return 0.0, 0.0, "Fehler: Ungültige Eingaben für Kurimoto-Modell."
    l_uc = l_slug + l_bubble
    re = rho_l * u_tp * d / mu_l
    ca = mu_l * u_tp / sigma
    we = rho_l * (u_tp ** 2) * d / sigma
    warnung = ""
    if ca < 0.00159 or ca > 0.0989:
        warnung = "Kurimoto: Ca_T ausserhalb [0.00159, 0.0989] (Kurimoto 2024 Ranges)."
    elif we < 0.0817 or we > 25.4:
        warnung = "Kurimoto: We_T ausserhalb [0.0817, 25.4] (Kurimoto 2024 Ranges)."
    elif re < 8.33 or re > 791.0:
        warnung = "Kurimoto: Re_T ausserhalb [8.33, 791] (Kurimoto 2024 Ranges)."
    elif (l_bubble / d) < 2.0:
        warnung = "Kurimoto: L_B/D_h < 2 (Kurimoto Table A1 min ca. 2.3)."
    nenner = 1.0 + 0.744 * (ca ** (2.0 / 3.0)) - 0.623 * (we ** 0.120)
    dp_bubble = (sigma / d) * ((7.106 * (ca ** (2.0 / 3.0))) / nenner)
    basis = (l_slug / l_uc) * (rho_l * (u_tp ** 2) / (2.0 * d)) * (56.9 / re)
    korrektur = 1.0 + (d / l_slug) * (0.250 * (ca ** (-1.0 / 3.0))) / nenner
    dp_total = basis * korrektur * l_uc
    return dp_total - dp_bubble, dp_bubble, warnung


def druckgradient_einheitszelle(u_tp, mu_l, rho_l, sigma, d, l_slug, l_bubble,
                                geometrie: str, c_bretherton: float) -> tuple[float, list[str]]:
    """
    Druckgradient dp/dz [Pa/m] einer Einheitszelle und Liste von Warnungen.

    ``c_bretherton`` wird nur im runden Kanal verwendet.
    """
    warnungen = []
    w = schlupf_warnung(u_tp, mu_l, sigma)
    if w:
        warnungen.append(w)
    if geometrie == "circular":
        dp_slug, w = bretherton(u_tp, l_slug, d, mu_l, rho_l, sigma, c_bretherton)
        dp_bubble = 0.0
    elif geometrie == "rectangular":
        dp_slug, dp_bubble, w = kurimoto(u_tp, l_slug, l_bubble, d, mu_l, rho_l, sigma)
    else:
        raise ValueError(f"Unbekannte Geometrie '{geometrie}'.")
    if w:
        warnungen.append(w)
    l_uc = l_slug + l_bubble
    dp_dz = (dp_slug + dp_bubble) / l_uc if l_uc > 0 else 0.0
    return dp_dz, warnungen


def kalibrierter_c(db_datei: Path, kalibrier_key: str, u_gas: float, u_liq: float,
                   c_theorie: float) -> tuple[float, str]:
    """
    Bretherton-Faktor c für einen runden Kanal aus der Kalibrier-Datenbank.

    Ablauf: lineare Interpolation zwischen den kalibrierten Betriebspunkten;
    außerhalb davon das gespeicherte Ersatzmodell (Linear, Polynomial oder
    Power-Law), zuletzt der nächstgelegene Punkt. Ergebnis mindestens 0,001.
    Ohne Eintrag, mit ``USE: false`` oder mit weniger als 4 Punkten wird
    ``c_theorie`` verwendet.

    Rückgabe: (c, Herkunftsbeschreibung)
    """
    db_datei = Path(db_datei)
    if not db_datei.exists():
        return c_theorie, f"WARNUNG: '{db_datei}' nicht gefunden! Nutze c_Theorie = {c_theorie}"
    try:
        with open(db_datei, "r", encoding="utf-8") as f:
            db = json.load(f)
        key = kalibrier_key
        if key not in db:
            alt = key.replace("rectangular", "Eckig").replace("circular", "Rund")
            if alt in db:
                key = alt
            else:
                for k in db:
                    if k.lower() in (key.lower(), alt.lower()):
                        key = k
                        break
        if key not in db:
            return c_theorie, f"WARNUNG: Kanal '{key}' nicht kalibriert! Nutze c_Theorie = {c_theorie}"
        daten = db[key]
        if daten.get("USE", True) is False:
            notiz = daten.get("NOTE", "markiert als USE=false")
            return c_theorie, (f"WARNUNG: Kalibrierung fuer '{key}' ist als NICHT verwendbar "
                               f"markiert (USE=false). Grund: {notiz} - nutze c_Theorie = {c_theorie}.")
        if len(daten.get("u_gas", [])) < 4:
            return c_theorie, f"WARNUNG: Zu wenige Daten für Interpolation. Nutze c_Theorie = {c_theorie}"

        pts = np.array([daten["u_gas"], daten["u_liq"]]).T
        vals = np.array(daten.get("c_calib", daten.get("cB")))
        c_int = griddata(pts, vals, (u_gas, u_liq), method="linear")
        if np.isnan(c_int):
            modell = daten.get("fallback_model")
            p = daten.get("fallback_params", [])
            if modell == "Linear" and len(p) == 3:
                c = p[0] * u_gas + p[1] * u_liq + p[2]
            elif modell == "Polynomial" and len(p) == 4:
                c = p[0] * u_gas + p[1] * u_liq + p[2] * (u_gas * u_liq) + p[3]
            elif modell == "Power-Law" and len(p) == 3:
                c = p[0] * (max(u_gas, 1e-6) ** p[1]) * (max(u_liq, 1e-6) ** p[2])
            else:
                c = float(griddata(pts, vals, (u_gas, u_liq), method="nearest"))
            c = max(0.001, float(c))
            return c, f"Extrapoliert (Fit): c_lokal = {c:.4f}"
        c = max(0.001, float(c_int))
        return c, f"Interpoliert: c_lokal = {c:.4f}"
    except Exception as e:
        return c_theorie, f"Fehler beim Laden der Kalibrierung: {e}. Nutze c_Theorie = {c_theorie}"
