# -*- coding: utf-8 -*-
"""
Stoffdaten für Flüssigkeit und Gas.

Flüssigkeitsdaten (Dichte, Viskosität, Oberflächenspannung) und Dampfdruck
kommen aus der Bibliothek ``thermo``. Henry-Konstante und CO2-Diffusions-
koeffizient werden mit Literaturkorrelationen berechnet.

Abgerufene Werte werden zwischengespeichert. Der Schlüssel rundet die
Temperatur auf 0,1 K und den Druck auf 1 Pa; zwei Betriebspunkte mit fast
gleicher Temperatur erhalten daher identische Stoffwerte.

Quellen:
    [Sander2015]   Sander, R. (2015). Compilation of Henry's law constants for
                   water as solvent. Atmos. Chem. Phys. 15, 4399-4981.
    [Versteeg1988] Versteeg, G. F., van Swaaij, W. P. M. (1988). Solubility and
                   diffusivity of acid gases (CO2, N2O) in aqueous alkanolamine
                   solutions. J. Chem. Eng. Data 33(1), 29-34.
"""

from __future__ import annotations

import math
import warnings

from scipy.constants import R

try:
    from thermo.chemical import Chemical
except ImportError as e:
    raise ImportError(
        "Die Bibliothek 'thermo' fehlt. Installation: pip install thermo"
    ) from e

# Henry-Konstanten bei 298,15 K [mol/(m³·Pa)] und Temperaturkoeffizient
# d(ln H)/d(1/T) [K] nach [Sander2015].
HENRY_DATEN = {
    "co2": {"H_ref": 3.36e-4, "dsolH_over_R": 2400.0},
    "o2": {"H_ref": 1.27e-4, "dsolH_over_R": 1500.0},
    "n2": {"H_ref": 6.46e-5, "dsolH_over_R": 1300.0},
    "air": {"H_ref": 5.87e-5, "dsolH_over_R": 1300.0},  # Näherung über N2
}
_WASSER_NAMEN = ("water", "water (liquid)", "h2o")

_cache: dict[str, object] = {}


def fluessigkeit(name: str, T: float, P: float) -> dict[str, float]:
    """Dichte [kg/m³], Viskosität [Pa·s], Oberflächenspannung [N/m] der Flüssigkeit."""
    key = f"liq_{name}_{T:.1f}_{P:.0f}"
    if key in _cache:
        return _cache[key]
    try:
        chem = Chemical(name, T=T, P=P)
    except Exception as e:
        raise ValueError(f"Fluid '{name}' nicht in thermo gefunden: {e}") from e
    if chem.phase and chem.phase != "l":
        warnings.warn(f"'{name}' liegt bei T={T} K, P={P} Pa evtl. nicht flüssig vor "
                      f"(Phase '{chem.phase}').")
    fehlend = [n for n, v in (("rho", chem.rho), ("mu", chem.mu), ("sigma", chem.sigma)) if v is None]
    if fehlend:
        raise ValueError(f"Stoffdaten für '{name}' unvollständig, es fehlen: {fehlend}")
    if chem.rho <= 0:
        raise ValueError(f"Ungültige Dichte für '{name}' bei T={T} K.")
    werte = {"rho": chem.rho, "mu": chem.mu, "sigma": chem.sigma, "nu": chem.mu / chem.rho}
    _cache[key] = werte
    return werte


def pruefe_gas(name: str) -> None:
    """Bricht ab, wenn ``thermo`` das Gas nicht kennt (Plausibilitätsprüfung beim Einlesen)."""
    try:
        chem = Chemical(name, T=298.15, P=101325.0)
    except Exception as e:
        raise ValueError(f"Gas '{name}' nicht in thermo gefunden: {e}") from e
    if chem.MW is None or chem.mug is None:
        raise ValueError(f"Stoffdaten für Gas '{name}' unvollständig.")


def henry(gas: str, fluessigkeit_name: str, T: float) -> float:
    """Henry-Konstante H_cp [mol/(m³·Pa)] nach van't Hoff [Sander2015]."""
    if T <= 0:
        raise ValueError(f"Ungültige Temperatur T={T} K.")
    if fluessigkeit_name.lower() not in _WASSER_NAMEN:
        raise ValueError(f"Henry-Konstanten sind nur für Wasser hinterlegt, nicht für '{fluessigkeit_name}'.")
    daten = HENRY_DATEN.get(gas.lower())
    if daten is None:
        raise ValueError(f"Keine Henry-Konstante für Gas '{gas}' hinterlegt "
                         f"(vorhanden: {sorted(HENRY_DATEN)}).")
    return daten["H_ref"] * math.exp(daten["dsolH_over_R"] * (1.0 / T - 1.0 / 298.15))


def dampfdruck(name: str, T: float) -> float:
    """Sättigungsdampfdruck der Flüssigkeit [Pa]."""
    key = f"Pv_{name}_{T:.1f}"
    if key in _cache:
        return _cache[key]
    try:
        Pv = Chemical(name, T=T).Psat
    except Exception as e:
        raise ValueError(f"Dampfdruck für '{name}' bei T={T} K nicht verfügbar: {e}") from e
    if Pv is None:
        raise ValueError(f"Kein Dampfdruck für '{name}' bei T={T} K.")
    _cache[key] = Pv
    return Pv


def diffusion_co2_wasser(T: float) -> float:
    """Diffusionskoeffizient CO2 in Wasser [m²/s] nach [Versteeg1988]."""
    if T <= 0:
        raise ValueError(f"Ungültige Temperatur T={T} K.")
    return 2.35e-6 * math.exp(-2119.0 / T)


GASKONSTANTE = R
