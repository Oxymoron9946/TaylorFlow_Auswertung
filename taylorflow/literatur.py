# -*- coding: utf-8 -*-
"""
Literaturkorrelationen für kLa im Taylor-Flow und ihre Registry.

Jedes Modell ist in ``LITERATURMODELLE`` mit Namen, Quelle, Ergebnisspalte und
Gültigkeitsbereich eingetragen. Die Auswertung schreibt die Vorhersagen aller
Modelle in die Betriebspunkt-Tabelle (Spalten ``kLa_lit_*``). Für Vergleiche
und eigene Modelle siehe ``taylorflow.modellvergleich``.

Konvention: Als Geschwindigkeit wird die gemessene Blasengeschwindigkeit u_B
eingesetzt (Mittel der gefitteten Geschwindigkeit über den Kanal), auch wo das
Original u_GS oder u_TP nennt. Der Unterschied liegt bei den vorliegenden
Daten unter 3 % (Haase 2016). Yue 2007 nutzt die Leerrohrgeschwindigkeiten.

Die Stoffwerte für Ca, Re und Sc sind feste Werte für Wasser/CO2 bei etwa
25 °C (``AuswerteParameter.lit_*``), nicht die temperaturabhängigen Werte der
Hauptauswertung.

Quellen (Gültigkeitsbereiche des Originals in den Funktionen):
    [vanBaten2004]  van Baten, Krishna (2004). Chem. Eng. Sci. 59, 2535-2545.
    [Vandu2005]     Vandu, Liu, Krishna (2005). Chem. Eng. Sci. 60, 6430-6437.
    [Shao2010]      Shao, Gavriilidis, Angeli (2010). Chem. Eng. J. 160, 873-881.
    [Heiszwolf2001] Heiszwolf, Kreutzer et al. (2001). Catal. Today 69, 51-55.
    [LiuWang2011]   Liu, Wang (2011). Chem. Eng. Sci. 66, 3876.
    [Yao2023]       Yao et al. (2023). Chin. J. Chem. Eng.
    [Yue2007]       Yue et al. (2007). Chem. Eng. Sci. 62, 2096-2108.
    [Yue2009]       Yue et al. (2009). Chem. Eng. Sci. 64, 3697-3708.
    [Aussillous2000] Aussillous, Quéré (2000). Phys. Fluids 12, 2367-2371.
    [Haase2016]     Haase, Murzin, Salmi (2016). ChERD 113, 304-329.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


# =============================================================================
# Modelle
# =============================================================================

def van_baten_voll(u_B, L_B, L_S, d_h, D):
    """
    [vanBaten2004], Kappe + Film (Kurzzeitkontakt, Fo < 0,1).

        kL_cap  = 2√2/π · √(D u_B / d_h),   a_cap  = 4 / L_UC
        kL_film = 2 √(D u_B / (π L_B)),      a_film = 4 L_B / (d_h L_UC)

    Original: d_h 1,5–3 mm rund, u_B 0,15–0,55 m/s, L_UC 15–50 mm.
    Rückgabe: (kLa gesamt, Kappenanteil, Filmanteil) [1/s]
    """
    L_UC = L_B + L_S
    kla_cap = 2.0 * np.sqrt(2.0) / np.pi * np.sqrt(D * u_B / d_h) * (4.0 / L_UC)
    kla_film = 2.0 * np.sqrt(D * u_B / (np.pi * L_B)) * (4.0 * L_B / (d_h * L_UC))
    return kla_cap + kla_film, kla_cap, kla_film


def vandu(u_B, L_B, L_S, d_h, D):
    """[Vandu2005]: kLa = 4,5 √(D u_B / L_UC) / d_h. Original: d_h 1–3 mm, u_B 0,09–0,65 m/s."""
    return 4.5 * np.sqrt(D * u_B / (L_B + L_S)) * (1.0 / d_h)


def shao(u_B, L_B, L_S, d_h, D):
    """[Shao2010]: kLa = 3,0 √(D u_B / L_UC) / d_h (CFD, CO2/NaOH)."""
    return 3.0 * np.sqrt(D * u_B / (L_B + L_S)) * (1.0 / d_h)


def liu_wang(u_B, L_B, L_S, d_h, D, mu_L, sigma_L, geom):
    """
    [LiuWang2011], nur runde Kanäle (sonst NaN).

        kLa = 0,12 Li^0,44 Pe^0,54 D / d_h²,  Li = L_F d_h / (L_S δ_F),
        Pe = u_B d_h / D,  L_F = L_B − d_h,  δ_F nach [Aussillous2000].

    Original: d_h 1–3 mm, u_B 0,1–1,2 m/s, L_S 8–28 mm.
    """
    if geom != "rund":
        return float("nan")
    ca23 = (mu_L * u_B / sigma_L) ** (2.0 / 3.0)
    delta_F = 0.66 * ca23 / (1.0 + 3.33 * ca23) * d_h
    L_F = np.maximum(L_B - d_h, 1e-9)
    Li = L_F * d_h / (L_S * delta_F)
    Pe = u_B * d_h / D
    return 0.12 * Li ** 0.44 * Pe ** 0.54 * D / d_h ** 2


def heiszwolf(u_B, L_S, D, n=0.5, D_ref=2.0e-9):
    """
    [Heiszwolf2001]: kLa = 0,133 u^1,2 / √L_S · (D/D_ref)^n, n = 0,5 (Penetrationstheorie).

    Original: d_h 0,8 und 1,5 mm quadratisch (Monolith), u_TP 0,1–0,5 m/s.
    """
    return 0.133 * u_B ** 1.2 / np.sqrt(L_S) * (D / D_ref) ** n


def yao_eq10(u_B, L_B, L_S, d_h, D, mu_L, sigma_L):
    """[Yao2023] Gl. 10: kLa = kLa_cap · Ca^0,023 + kLa_film · Ca^0,103 (Basis van Baten)."""
    ca = mu_L * u_B / sigma_L
    _, cap, film = van_baten_voll(u_B, L_B, L_S, d_h, D)
    return cap * ca ** 0.023 + film * ca ** 0.103


def yue_2007(u_GS, u_LS, d_h, D, mu_L, rho_L, mu_G, rho_G, geom):
    """
    [Yue2007], nur eckige Kanäle (sonst NaN).

        kLa = 0,084 Re_G^0,213 Re_L^0,937 Sc_L^0,5 · D / d_h²  (Leerrohrgeschwindigkeiten)

    Original: 0,5 × 1,0 mm (d_h 0,67 mm), CO2/Wasser, L_B 1,1–1,3 mm.
    """
    if geom != "eckig" or not (u_GS > 0 and u_LS > 0 and d_h > 0 and D > 0):
        return np.nan
    Re_G = rho_G * u_GS * d_h / mu_G
    Re_L = rho_L * u_LS * d_h / mu_L
    Sc_L = mu_L / (rho_L * D)
    return 0.084 * (Re_G ** 0.213) * (Re_L ** 0.937) * (Sc_L ** 0.5) * D / (d_h ** 2)


def yue_2009(u_B, L_B, L_S, d_h, D, geom):
    """
    [Yue2009], nur eckige Kanäle (sonst NaN).

        kLa = (2 / d_h) · √(D u_B / d_h) · (L_B / L_UC)^0,3

    Original: d_h 0,2–0,4 mm quadratisch, u_B 0,4–2,0 m/s, O2/Wasser.
    """
    if geom != "eckig" or not (u_B > 0 and L_B > 0 and L_S > 0 and d_h > 0 and D > 0):
        return np.nan
    return (2.0 / d_h) * math.sqrt(D * u_B / d_h) * (L_B / (L_B + L_S)) ** 0.3


# =============================================================================
# Registry
# =============================================================================

@dataclass(frozen=True)
class Literaturmodell:
    """Eintrag der Modell-Registry."""
    name: str            # Kurzname für config.py und Plots
    titel: str           # Anzeigename
    spalte: str          # Ergebnisspalte in der Betriebspunkt-Tabelle
    funktion: Callable[[dict], float]
    geometrie: str = "beide"   # "rund", "eckig" oder "beide"
    zielgroesse: str = "kLa_log_mean_1_s"
    einheit: str = "1/s"
    hinweis: str = ""


def _e(x: dict, *namen):
    return [x[n] for n in namen]


LITERATURMODELLE: dict[str, Literaturmodell] = {m.name: m for m in [
    Literaturmodell("van_baten_voll", "van Baten 2004 (Kappe + Film)", "kLa_lit_van_baten_full_1_s",
                    lambda x: van_baten_voll(*_e(x, "u_B", "L_B", "L_S", "d_h", "D"))[0]),
    Literaturmodell("van_baten_kappe", "van Baten 2004 (Kappe)", "kLa_lit_van_baten_cap_1_s",
                    lambda x: van_baten_voll(*_e(x, "u_B", "L_B", "L_S", "d_h", "D"))[1]),
    Literaturmodell("van_baten_film", "van Baten 2004 (Film)", "kLa_lit_van_baten_film_1_s",
                    lambda x: van_baten_voll(*_e(x, "u_B", "L_B", "L_S", "d_h", "D"))[2]),
    Literaturmodell("vandu", "Vandu 2005", "kLa_lit_vandu_1_s",
                    lambda x: vandu(*_e(x, "u_B", "L_B", "L_S", "d_h", "D"))),
    Literaturmodell("shao", "Shao 2010", "kLa_lit_shao_1_s",
                    lambda x: shao(*_e(x, "u_B", "L_B", "L_S", "d_h", "D"))),
    Literaturmodell("liu_wang", "Liu und Wang 2011", "kLa_lit_liu_wang_1_s",
                    lambda x: liu_wang(*_e(x, "u_B", "L_B", "L_S", "d_h", "D", "mu_L", "sigma_L", "geom")),
                    geometrie="rund"),
    Literaturmodell("heiszwolf", "Heiszwolf 2001 (n = 0,5)", "kLa_lit_heiszwolf_n05_1_s",
                    lambda x: heiszwolf(*_e(x, "u_B", "L_S", "D"))),
    Literaturmodell("yao", "Yao 2023 (Gl. 10)", "kLa_lit_yao_eq10_1_s",
                    lambda x: yao_eq10(*_e(x, "u_B", "L_B", "L_S", "d_h", "D", "mu_L", "sigma_L"))),
    Literaturmodell("yue_2007", "Yue 2007", "kLa_lit_yue_2007_1_s",
                    lambda x: yue_2007(*_e(x, "u_GS", "u_LS", "d_h", "D", "mu_L", "rho_L", "mu_G", "rho_G", "geom")),
                    geometrie="eckig"),
    Literaturmodell("yue_2009", "Yue 2009", "kLa_lit_yue_2009_1_s",
                    lambda x: yue_2009(*_e(x, "u_B", "L_B", "L_S", "d_h", "D", "geom")),
                    geometrie="eckig"),
]}


def modelleingaben(u_B, L_B, L_S, d_h, D, geom, u_GS, u_LS, p) -> dict:
    """Bündelt die Eingangsgrößen aller Literaturmodelle (``p``: AuswerteParameter)."""
    return {"u_B": u_B, "L_B": L_B, "L_S": L_S, "d_h": d_h, "D": D, "geom": geom,
            "u_GS": u_GS, "u_LS": u_LS, "mu_L": p.lit_mu_l_pa_s, "sigma_L": p.lit_sigma_l_n_m,
            "rho_L": p.lit_rho_l_kg_m3, "mu_G": p.lit_mu_g_pa_s, "rho_G": p.lit_rho_g_kg_m3}


def alle_literaturwerte(eingaben: dict) -> dict[str, float]:
    """Vorhersagen aller registrierten Modelle als {Spaltenname: Wert}."""
    return {m.spalte: m.funktion(eingaben) for m in LITERATURMODELLE.values()}
