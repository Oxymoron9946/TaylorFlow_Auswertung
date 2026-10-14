# -*- coding: utf-8 -*-
"""
Kurvenanpassung der gemessenen Blasenlänge, Sluglänge und Blasengeschwindigkeit.

Blasenlänge (Modell v2, METHODIK §3):

    L(z) = L0 − A · (1 − exp(−z/λ)) + B · z    (+ Offset o_j je Kamera j >= 2)

    L0  Blasenlänge am Einlass [m]
    A   absorptionsbedingte Längenabnahme [m]          (>= 0)
    λ   charakteristische Absorptionslänge [m]          (> 0)
    B   Expansion durch Druckverlust [m/m]              (>= 0)
    o_j additiver Versatz der Kamera j gegenüber Kamera 1 [m]

Der Fit ist ein gewichteter, robuster Zwei-Pass-Fit (scipy ``curve_fit``,
Verlustfunktion ``soft_l1``). Schlägt er fehl, greift die Kaskade
v2 → v1 (exponentiell + linear) → linear.

Sluglänge und Geschwindigkeit werden ungewichtet linear angepasst.
"""

from __future__ import annotations

import warnings
from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


# =============================================================================
# Modellfunktionen
# =============================================================================

def linear(x, a, b):
    """y = a·x + b"""
    return a * x + b


def blase_v1(x, a, b, c, d):
    """Ersatzmodell v1: L = a·exp(−b·x) + c + d·x"""
    return a * np.exp(-b * x) + c + d * x


def blase_v2(x, L0, A, lam, B):
    """Blasenlängenmodell v2: L = L0 − A·(1 − exp(−x/λ)) + B·x"""
    return L0 - A * (1.0 - np.exp(-x / lam)) + B * x


def _modell_mit_offsets(kamera_idx: np.ndarray, n_serien: int):
    """Modell v2 mit additiven Offsets je Kamera (Kamera-Index 0 = Referenz)."""
    def modell(x, *p):
        L0, A, lam, B = p[:4]
        basis = L0 - A * (1.0 - np.exp(-x / lam)) + B * x
        for j in range(1, n_serien):
            basis = np.where(kamera_idx == j, basis + p[4 + (j - 1)], basis)
        return basis
    return modell


# =============================================================================
# Gütemaße
# =============================================================================

def r2(y, f) -> float:
    """Bestimmtheitsmaß R²."""
    y = np.asarray(y)
    f = np.asarray(f)
    if len(y) < 2:
        return 0.0
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot == 0:
        return 0.0
    return 1 - (np.sum((y - f) ** 2) / ss_tot)


def chi2_red(y, f, sigma, n_param) -> float | None:
    """Reduziertes Chi-Quadrat Σ((y−f)/σ)² / (n − p); Zielwert ≈ 1."""
    if sigma is None:
        return None
    sigma = np.asarray(sigma, dtype=float)
    ok = np.isfinite(sigma) & (sigma > 0)
    if not np.any(ok):
        return None
    dof = max(int(np.count_nonzero(ok)) - n_param, 1)
    return float(np.sum(((y[ok] - f[ok]) / sigma[ok]) ** 2) / dof)


def _parameter_am_bound(popt, lb, ub, rel_tol=1e-3) -> list[str]:
    """Meldet Parameter am Bound (A -> 0 und B -> 0 sind physikalisch erlaubt)."""
    treffer = []
    namen = ["L0", "A", "lam", "B"] + [f"o{j}" for j in range(2, 2 + max(0, len(popt) - 4))]
    for name, p, lo, hi in zip(namen, popt, lb, ub):
        if np.isfinite(hi) and abs(p - hi) <= rel_tol * max(abs(hi), 1e-12):
            treffer.append(f"{name} am oberen Bound ({p:.4g} ~ {hi:.4g})")
        if lo > 0 and abs(p - lo) <= rel_tol * max(abs(lo), 1e-12):
            treffer.append(f"{name} am unteren Bound ({p:.4g} ~ {lo:.4g})")
    return treffer


def _max_korrelation(pcov) -> float | None:
    """Größte Korrelation zweier Fitparameter (Betrag)."""
    try:
        d = np.sqrt(np.diag(pcov))
        if np.any(d <= 0) or not np.all(np.isfinite(d)):
            return None
        corr = pcov / np.outer(d, d)
        return float(np.max(np.abs(corr - np.eye(corr.shape[0]))))
    except Exception:
        return None


# =============================================================================
# Blasenlängen-Fit
# =============================================================================

def _bounds_v2(x, y, L_reaktor):
    """Datengeleitete Grenzen für L0, A, λ, B (METHODIK §3.2)."""
    y_max = float(np.max(y))
    y_min = float(np.min(y))
    y_span = max(y_max - y_min, 1e-9)
    z_u = np.unique(np.sort(x))
    dz_min = float(np.min(np.diff(z_u))) if len(z_u) > 1 else 1e-3
    lb = [0.1 * y_max, 0.0, dz_min, 0.0]
    ub = [5.0 * y_max, 2.0 * y_span, 10.0 * L_reaktor, 2.0 * y_max / max(L_reaktor, 1e-9)]
    return lb, ub


def _zwei_pass_fit(modell, x, y, sigma, p0, lb, ub, loss, maxfev):
    """Pass 1: gewichteter Fit; Pass 2: robuster Fit mit f_scale aus der Residuen-MAD."""
    popt1, _ = curve_fit(modell, x, y, sigma=sigma, absolute_sigma=True,
                         p0=p0, bounds=(lb, ub), maxfev=maxfev)
    r1 = (y - modell(x, *popt1)) / sigma
    mad = float(np.median(np.abs(r1 - np.median(r1))))
    f_scale = max(mad / 0.6745, 1e-9)
    popt, pcov = curve_fit(modell, x, y, sigma=sigma, absolute_sigma=True, p0=popt1,
                           bounds=(lb, ub), loss=loss, f_scale=f_scale, maxfev=maxfev)
    return popt, pcov, f_scale


def _fit_v2(x, y, sigma, L_reaktor, loss, lambda0):
    lb, ub = _bounds_v2(x, y, L_reaktor)
    y_min = float(np.min(y))
    p0 = [float(np.clip(y[0], lb[0], ub[0])),
          float(np.clip(max(1e-6, y[0] - y_min), 1e-9, ub[1])),
          float(np.clip(lambda0, lb[2] * 1.01, ub[2] * 0.99)),
          1e-6]
    popt, pcov, f_scale = _zwei_pass_fit(blase_v2, x, y, sigma, p0, lb, ub, loss, 20000)
    return popt, pcov, (lb, ub), f_scale


def _fit_v2_offsets(x, y, sigma, kamera_idx, n_serien, L_reaktor, loss, lambda0, offset_anteil):
    lb, ub = _bounds_v2(x, y, L_reaktor)
    o_max = float(max(offset_anteil * np.mean(np.asarray(y, dtype=float)), 1e-6))
    lb = list(lb) + [-o_max] * (n_serien - 1)
    ub = list(ub) + [o_max] * (n_serien - 1)
    y_min = float(np.min(y))
    p0 = [float(np.clip(y[0], lb[0], ub[0])),
          float(np.clip(max(1e-6, y[0] - y_min), 1e-9, ub[1])),
          float(np.clip(lambda0, lb[2] * 1.01, ub[2] * 0.99)),
          1e-6] + [0.0] * (n_serien - 1)
    modell = _modell_mit_offsets(kamera_idx, n_serien)
    popt, pcov, f_scale = _zwei_pass_fit(modell, x, y, sigma, p0, lb, ub, loss, 30000)
    return popt, pcov, (lb, ub), f_scale


def fit_blasenlaenge(x, y, sigma, L_reaktor: float, loss: str = "soft_l1",
                     serien_offsets: bool = True, kamera_idx: np.ndarray | None = None,
                     lambda0: float = 0.05, offset_anteil: float = 0.2):
    """
    Fit der Blasenlänge über die Kanalposition (Kaskade v2+Offsets → v2 → v1 → linear).

    Parameter
    ---------
    x, y : Position [m] und gemessene Blasenlänge [m]
    sigma : Messunsicherheit je Punkt [m]
    L_reaktor : Reaktorlänge [m] (für die Parametergrenzen)
    kamera_idx : 0-basierter Kamera-Index je Punkt (für Offsets), sonst None

    Rückgabe
    --------
    (funktion, r2, modellname, popt, info)
        funktion(z) liefert die Blasenlänge OHNE Kamera-Offsets.
        info: chi2_red, bound_warnings, corr_max, f_scale, loss,
              model_version (3 = v2+Offsets, 2 = v2, 1 = v1, 0 = linear),
              offsets (Array o_2.. [m] oder None), n_series.
    """
    if len(x) < 2 or len(y) < 2:
        raise ValueError("Blasenlängen-Fit: mindestens 2 Messpunkte nötig.")
    info = {"chi2_red": None, "bound_warnings": [], "corr_max": None, "f_scale": None,
            "loss": None, "model_version": 0, "offsets": None, "n_series": 0}
    n_serien = int(len(np.unique(kamera_idx))) if kamera_idx is not None else 0

    if serien_offsets and n_serien >= 2:
        try:
            popt, pcov, (lb, ub), f_scale = _fit_v2_offsets(
                x, y, sigma, kamera_idx, n_serien, L_reaktor, loss, lambda0, offset_anteil)
            f_voll = _modell_mit_offsets(kamera_idx, n_serien)(x, *popt)
            info.update({"chi2_red": chi2_red(y, f_voll, sigma, len(popt)),
                         "bound_warnings": _parameter_am_bound(popt, lb, ub),
                         "corr_max": _max_korrelation(pcov), "f_scale": f_scale, "loss": loss,
                         "model_version": 3, "offsets": np.asarray(popt[4:]), "n_series": n_serien})
            return (lambda z, p=popt: blase_v2(z, *p[:4]), r2(y, f_voll),
                    f"Exp+Expansion v2+Offsets (robust, {loss}, {n_serien} Serien)", popt, info)
        except Exception as e:
            warnings.warn(f"Serien-Offset-Fit fehlgeschlagen ({e}). Fallback auf v2 ohne Offsets.")

    try:
        popt, pcov, (lb, ub), f_scale = _fit_v2(x, y, sigma, L_reaktor, loss, lambda0)
        f = blase_v2(x, *popt)
        info.update({"chi2_red": chi2_red(y, f, sigma, 4),
                     "bound_warnings": _parameter_am_bound(popt, lb, ub),
                     "corr_max": _max_korrelation(pcov), "f_scale": f_scale, "loss": loss,
                     "model_version": 2})
        return (lambda z, p=popt: blase_v2(z, *p), r2(y, f),
                f"Exp+Expansion v2 (robust, {loss})", popt, info)
    except Exception as e:
        warnings.warn(f"v2-Fit fehlgeschlagen ({e}). Fallback auf v1-Modell.")

    try:
        popt, _ = curve_fit(blase_v1, x, y, sigma=sigma, absolute_sigma=True,
                            p0=[max(1e-5, y[0] - np.min(y)), 5.0, float(np.min(y)), 0.001],
                            bounds=([0.0, 1e-4, 0.0, 0.0], [np.inf, 500.0, np.inf, 1.0]),
                            maxfev=15000)
        f = blase_v1(x, *popt)
        info.update({"chi2_red": chi2_red(y, f, sigma, 4), "model_version": 1})
        return (lambda z, p=popt: blase_v1(z, *p), r2(y, f),
                "Exp + Expansion v1 (Fallback)", popt, info)
    except Exception as e:
        warnings.warn(f"v1-Fit fehlgeschlagen ({e}). Fallback auf linearen Fit.")

    popt, _ = curve_fit(linear, x, y, sigma=sigma, absolute_sigma=True)
    f = linear(x, *popt)
    info["chi2_red"] = chi2_red(y, f, sigma, 2)
    return lambda z, p=popt: linear(z, *p), r2(y, f), "Linear (Fallback)", popt, info


def fit_linear(x, y) -> Callable:
    """Ungewichteter linearer Fit; gibt die Fitfunktion zurück."""
    if len(x) < 2 or len(y) < 2:
        raise ValueError("Linearer Fit: mindestens 2 Messpunkte nötig.")
    popt, _ = curve_fit(linear, x, y)
    return lambda z, p=popt: linear(z, *p)


# =============================================================================
# Glättung
# =============================================================================

def entferne_einbrueche(werte: np.ndarray, fenster: int = 3, schwelle: float = 0.8) -> np.ndarray:
    """
    Ersetzt Einbrüche durch lineare Interpolation.

    Ein Punkt gilt als Einbruch, wenn er unter (1 − schwelle) · gleitender Median
    (Fensterbreite ``fenster``) liegt.
    """
    s = pd.Series(werte)
    median = s.rolling(fenster, center=True, min_periods=1).median()
    s[s < (1.0 - schwelle) * median] = np.nan
    return s.interpolate(method="linear").bfill().ffill().values
