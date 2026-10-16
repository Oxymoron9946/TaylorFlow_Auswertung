# -*- coding: utf-8 -*-
"""
Auswertung einer Messreihe (ein Kanal) Betriebspunkt für Betriebspunkt.

Ablauf je Betriebspunkt (u_G, u_L), Details im Handbuch, Kapitel 7:

1. Messpunkte vorbereiten   Duplikate je Kamera und Bin entfernen, Kamera-Index
2. Stoffdaten               T, p am Auslass; Flüssigkeitsdaten, Henry, Dampfdruck
3. Phasenlängen fitten      Blasenlänge (Modell v2 + Offsets), Slug und U linear
4. Druckprofil              Rückwärtsintegration vom Auslass (Bretherton/Kurimoto)
5. Stoffbilanz              absorbierte Stoffmenge, C_L, C*, Sättigung
6. kLa                      aktive Zone, logarithmisches Mittel
7. Druckkorrektur           Blasenlänge auf Einlassdruck umgerechnet
8. Literaturmodelle         Vorhersagen aller registrierten Korrelationen
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import protokoll, stoffdaten
from .druckverlust import druckgradient_einheitszelle, kalibrierter_c
from .einlesen import Messreihe, betriebspunkt_ueberspringen, lade_messdaten
from .fits import fit_blasenlaenge, fit_linear
from .geometrie import blasengeometrie
from .hydrodynamik import filmdicke, kapillarzahl
from .kla import aktive_zone, kla_log_mean
from .literatur import alle_literaturwerte, modelleingaben
from .parameter import AuswerteParameter

R_GAS = stoffdaten.GASKONSTANTE


@dataclass
class KanalErgebnis:
    """Ergebnis einer Messreihe."""
    reihe: Messreihe
    profile: dict[str, pd.DataFrame] = field(default_factory=dict)   # Betriebspunkt -> Profile
    betriebspunkte: list[dict] = field(default_factory=list)         # eine Zeile je Betriebspunkt


def betriebspunkt_name(gas: float, liq: float) -> str:
    """Name eines Betriebspunkts, z. B. ``Gas_0_134_Liq_0_056``."""
    return f"Gas_{str(gas).replace('.', '_')}_Liq_{str(liq).replace('.', '_')}"


def werte_kanal_aus(reihe: Messreihe, p: AuswerteParameter, ausschluesse: dict,
                    kalibrier_db: Path, ausgabe=print) -> KanalErgebnis:
    """Wertet alle Betriebspunkte einer Messdatei (Messart „Masse“) aus."""
    ausgabe(f"\n=== {reihe.kanal} ===")
    df = lade_messdaten(reihe, ausschluesse, p, ausgabe)
    regeln = ausschluesse.get(reihe.kanal) or {}
    ergebnis = KanalErgebnis(reihe)

    for _, zeile in df[["GasVelocity", "LiquidVelocity"]].drop_duplicates().iterrows():
        gas, liq = zeile["GasVelocity"], zeile["LiquidVelocity"]
        name = betriebspunkt_name(gas, liq)
        maske = np.isclose(df["GasVelocity"], gas) & np.isclose(df["LiquidVelocity"], liq)
        bp = _werte_betriebspunkt_aus(df[maske].copy(), reihe, gas, liq, name, p,
                                      regeln, kalibrier_db, ausgabe)
        if bp is not None:
            ergebnis.profile[name], zeile_global = bp
            ergebnis.betriebspunkte.append(zeile_global)
    return ergebnis


# =============================================================================
# Einzelschritte
# =============================================================================

def _bereite_messpunkte_vor(df: pd.DataFrame):
    """Behält je Kamera und Bin den Punkt mit der kleinsten Blasenlänge; Kamera-Index 0, 1, ..."""
    if not df.empty:
        df = df.loc[df.groupby(["CameraPosition", "BinCenter_mm"])["mean_BubbleLength_mm"].idxmin()]
    df = df.sort_values(by="BinCenter_mm")
    kamera_idx, n_serien = None, 0
    kam = pd.to_numeric(df["CameraPosition"], errors="coerce").values
    eindeutig = np.sort(pd.unique(kam[~np.isnan(kam)]))
    if len(eindeutig) >= 2:
        zuordnung = {v: k for k, v in enumerate(eindeutig)}
        kamera_idx = np.array([zuordnung[v] for v in kam])
        n_serien = len(eindeutig)
    return df, kamera_idx, n_serien


def _pruefe_gueltigkeit(kontext, geometrie, gas, liq, d, ca_l):
    """Protokolliert Überschreitungen der Gültigkeitsbereiche (Liu 2005, Bretherton 1961)."""
    if geometrie != "circular":
        return  # Kurimoto prüft seine Grenzen selbst (druckverlust.kurimoto)
    if not (0.008 <= gas <= 0.7):
        protokoll.warnung(kontext, f"Liu (2005): U_G ({gas:.3f} m/s) außerhalb [0.008, 0.7]")
    if not (0.008 <= liq <= 0.5):
        protokoll.warnung(kontext, f"Liu (2005): U_L ({liq:.3f} m/s) außerhalb [0.008, 0.5]")
    if not (0.0009 <= d <= 0.003):
        protokoll.warnung(kontext, f"Liu (2005): d_h ({d:.4f} m) außerhalb [0.0009, 0.003]")
    if not (0.0002 <= ca_l <= 0.39):
        protokoll.warnung(kontext, f"Liu (2005): Ca ({ca_l:.5f}) außerhalb der empirischen Validierung [0.0002, 0.39]")
    if ca_l > 0.005:
        protokoll.warnung(kontext, f"Bretherton (1961): Ca_L ({ca_l:.5f}) > 0.005 (außerhalb schleichender Strömung)")


def _fit_phasenlaengen(df, kamera_idx, reihe, p, kontext, ausgabe):
    """Fit von Blasenlänge (gewichtet, robust), Sluglänge und Geschwindigkeit."""
    z = df["BinCenter_mm"].values * 1e-3
    L_b = df["mean_BubbleLength_mm"].values * 1e-3
    L_uc = df["mean_UnitCellLength_mm"].values * 1e-3
    U = df["mean_Speed_m_s"].values
    L_s = L_uc - L_b

    if "numel_BubbleLength_mm" in df.columns:
        n = pd.to_numeric(df["numel_BubbleLength_mm"], errors="coerce").values
        n = np.where(np.isfinite(n) & (n >= 1), n, 1.0)
    else:
        n = np.ones_like(z)
        warnings.warn("numel_BubbleLength_mm fehlt - nutze Standardabweichung als Sigma.")
    sigma_sem = df["std_BubbleLength_mm"].values * 1e-3 / np.sqrt(n) + p.sigma_sem_floor_m
    sigma = np.sqrt(sigma_sem ** 2 + p.sigma_sys_m ** 2)

    f_b, r2_b, name_b, popt_b, info = fit_blasenlaenge(
        z, L_b, sigma, reihe.laenge_m, loss=p.fit_loss, serien_offsets=p.fit_serien_offsets,
        kamera_idx=kamera_idx, lambda0=p.fit_lambda0_m, offset_anteil=p.offset_bound_anteil)
    chi2 = info.get("chi2_red")
    ausgabe(f"    Blasenfit: {name_b}, R² = {r2_b:.4f}" + (f", chi²_red = {chi2:.2f}" if chi2 is not None else ""))

    bound = info.get("bound_warnings", []) or []
    offsets = info.get("offsets")
    guete = {
        "fit_model": str(name_b),
        "fit_r2": float(r2_b) if r2_b is not None else float("nan"),
        "fit_chi2_red": float(chi2) if chi2 is not None else float("nan"),
        "fit_corr_max": float(info["corr_max"]) if info.get("corr_max") is not None else float("nan"),
        "fit_n_bound_hits": int(len(bound)),
        "fit_bound_hits": "; ".join(bound) if bound else "",
        "fit_n_offsets": int(len(offsets)) if offsets is not None else 0,
    }

    for w in bound:
        protokoll.warnung(kontext, f"Blasen-Fit: {w}")
    if info.get("corr_max") is not None and info["corr_max"] > 0.95:
        protokoll.warnung(kontext, f"Blasen-Fit: Parameter hoch korreliert (max |corr| = "
                                   f"{info['corr_max']:.3f} > 0.95) - Identifizierbarkeit pruefen")
    if chi2 is not None:
        stufe = ("KRITISCH (systematischer Modellfehler/physikalisch nicht plausibel)" if chi2 > 10.0 else
                 "ERHEBLICH (Modellabweichung >3 sigma)" if chi2 > 3.0 else
                 "MODERAT (Sigma zu optimistisch oder kleine Systematik)" if chi2 > 1.5 else None)
        if stufe:
            protokoll.warnung(kontext, f"Blasen-Fit: chi2_red = {chi2:.2f} -> {stufe}")
    if offsets is not None and len(offsets) > 0:
        o_max = float(max(p.offset_bound_anteil * np.mean(L_b), 1e-6))
        A_hat = float(popt_b[1]) if (popt_b is not None and len(popt_b) >= 4) else np.nan
        for j, o in enumerate(offsets, start=2):
            ausgabe(f"    Offset Kamera {j}: {o * 1e3:+.3f} mm")
            if abs(o) > 0.8 * o_max:
                protokoll.warnung(kontext, f"Serien-Offset o{j} = {o*1e3:+.3f} mm nahe/am Bound "
                                           f"({o_max*1e3:.3f} mm) - Kameraposition systematisch "
                                           f"versetzt oder Kalibrierung pruefen")
            if np.isfinite(A_hat) and A_hat > 0 and abs(o) > 0.5 * A_hat:
                protokoll.warnung(kontext, f"Serien-Offset o{j} = {o*1e3:+.3f} mm > 50% des "
                                           f"Absorptionssignals A = {A_hat*1e3:.3f} mm - Gefahr, dass "
                                           f"der Offset Physik absorbiert")

    f_s = fit_linear(z, L_s)
    f_u = fit_linear(z, U)
    return {"z_meas": z, "L_b_meas": L_b, "U_meas": U, "f_b": f_b, "f_s": f_s, "f_u": f_u,
            "popt_b": popt_b, "info": info, "name_b": name_b, "guete": guete}


def _begrenze_geschwindigkeit(U_fit, U_meas, gas, liq, p, kontext):
    """Schlupf U_meas/U_TP und Deckel für U_fit (Fit-Überschwinger)."""
    U_tp = gas + liq
    U_ok = U_meas[np.isfinite(U_meas)]
    if len(U_ok) > 0:
        U_med = float(np.nanmedian(U_ok))
        schlupf = U_med / U_tp if U_tp > 0 else np.nan
        if np.isfinite(schlupf) and schlupf > 1.5:
            protokoll.warnung(kontext, f"Slip U_meas/U_TP = {schlupf:.2f} > 1.5 - "
                                       f"MFC-Aufloesungsgrenze bei U_g={gas:.4f}, U_l={liq:.4f} pruefen")
        U_ref = max(U_med, U_tp)
    else:
        schlupf, U_ref = np.nan, U_tp
    zu_gross = U_fit > p.u_fit_cap_faktor * U_ref
    if np.any(zu_gross):
        U_fit[zu_gross] = np.nan
        U_fit = pd.Series(U_fit).interpolate(method="linear").bfill().ffill().values
    return U_fit, schlupf


def _druckprofil(z, U_fit, L_s_fit, L_b_fit, P_aus, stoff, reihe, gas, liq, kalibrier_db, p,
                 kontext, ausgabe):
    """Rückwärtsintegration dp/dz vom Auslassdruck; None bei Fehler."""
    c_b = p.c_bretherton_theorie
    if reihe.geometrie == "circular":
        try:
            c_b, meldung = kalibrierter_c(kalibrier_db, reihe.kalibrier_key, gas, liq,
                                          p.c_bretherton_theorie)
            ausgabe(f"    Bretherton-Faktor: {meldung}")
        except Exception as e:
            warnings.warn(f"Kalibrierung für {reihe.kalibrier_key} fehlgeschlagen: {e}. Nutze Theorie-Standard.")
    P = np.zeros(len(z))
    P[-1] = P_aus
    dz = p.dz_m
    for i in range(len(z) - 2, -1, -1):
        try:
            dp_dz, meldungen = druckgradient_einheitszelle(
                float(U_fit[i]), float(stoff["mu"]), float(stoff["rho"]), float(stoff["sigma"]),
                float(reihe.d_kanal_m), float(L_s_fit[i]), float(L_b_fit[i]), reihe.geometrie, c_b)
            P[i] = P[i + 1] + dp_dz * dz
            for m in meldungen:
                protokoll.warnung(kontext, m)
        except Exception as e:
            warnings.warn(f"Druckverlust bei z = {z[i]:.3f} m fehlgeschlagen: {e}")
            return None
    return P


def _blasen_entlang_z(U_fit, L_b_fit, stoff, reihe, kontext):
    """Filmdicke, Blasendurchmesser, Blasenquerschnitt und -volumen an jedem z."""
    n = len(U_fit)
    delta, d_b, A_b, V_b, V_caps = (np.zeros(n) for _ in range(5))
    d = reihe.d_kanal_m
    for i in range(n):
        ca = kapillarzahl(stoff["mu"], U_fit[i], stoff["sigma"])
        delta[i], hinweis = filmdicke(d, ca, reihe.geometrie)
        if hinweis and ("extrapoliert" in hinweis or "ungültig" in hinweis):
            protokoll.warnung(kontext, f"Filmdicke Modell: {hinweis}")
        d_b[i] = d - 2.0 * delta[i]
        g = blasengeometrie(d_b[i], L_b_fit[i], reihe.geometrie)
        A_b[i], V_b[i] = g["A_bubble"], g["V_bubble"]
        V_caps[i] = blasengeometrie(d_b[i], 0.0, reihe.geometrie)["V_caps"]
    return {"delta": delta, "d_b": d_b, "A_b": A_b, "V_b": V_b, "V_caps": V_caps}


def _stoffbilanz(P, L_s_fit, L_b_fit, blasen, stoff, reihe, p):
    """
    Absorbierte CO2-Menge je Blase aus der Volumenabnahme (ideales Gas, trockenes Gas
    nach Abzug des Dampfdrucks), Konzentration C_L im Slug und Gleichgewicht C*.
    """
    d = reihe.d_kanal_m
    T, P_v, H = stoff["T"], stoff["P_v"], stoff["H_cp"]
    A_kanal = np.pi * (d / 2.0) ** 2 if reihe.geometrie == "circular" else d ** 2

    V_zwickel = (blasengeometrie(blasen["d_b"][0], L_b_fit[0], reihe.geometrie)["V_caps"] / 2.0
                 if reihe.geometrie == "circular" else 0.0)
    V_L = max(1e-12, L_s_fit[0] * A_kanal + L_b_fit[0] * (A_kanal - blasen["A_b"][0]) + V_zwickel)

    P_trocken_0 = max(1.0, P[0] - P_v)
    n_start = (P_trocken_0 * blasen["V_b"][0]) / (R_GAS * T)
    n_co2_0 = n_start * reihe.y_co2
    n_inert = n_start * (1.0 - reihe.y_co2)

    n_verlust = np.zeros(len(P))
    C_L = np.zeros(len(P))
    C_star = np.zeros(len(P))
    for i in range(len(P)):
        P_tr = max(1.0, P[i] - P_v)
        n_lokal = (P_tr * blasen["V_b"][i]) / (R_GAS * T)
        n_weg = min(max(0.0, n_start - n_lokal), n_co2_0)
        n_verlust[i] = n_weg
        C_L[i] = n_weg / V_L
        n_co2 = n_co2_0 - n_weg
        n_ges = n_inert + n_co2
        y = (n_co2 / n_ges) if n_ges > 0 else 0.0
        C_star[i] = P_tr * y * H

    with np.errstate(divide="ignore", invalid="ignore"):
        sat_roh = (C_L / C_star) * 100.0
    # Korrigiert: absorbierte Menge kann nicht abnehmen (Monotonie)
    n_korr = np.maximum.accumulate(n_verlust)
    C_L_korr = n_korr / V_L
    P_trocken = np.maximum(1.0, P - P_v)
    n_co2_korr = n_co2_0 - n_korr
    n_ges_korr = n_inert + n_co2_korr
    y_korr = np.where(n_ges_korr > 0, n_co2_korr / n_ges_korr, 0.0)
    C_star_korr = P_trocken * y_korr * H
    C_L_korr = np.where(C_L_korr >= C_star_korr, p.saettigung_clip * C_star_korr, C_L_korr)
    with np.errstate(divide="ignore", invalid="ignore"):
        sat_korr = (C_L_korr / C_star_korr) * 100.0

    return {"V_L": V_L, "A_kanal": A_kanal, "P_trocken": P_trocken, "P_trocken_0": P_trocken_0,
            "n_roh": n_verlust, "C_L_roh": C_L, "C_star_roh": C_star, "sat_roh": sat_roh,
            "n_korr": n_korr, "C_L_korr": C_L_korr, "C_star_korr": C_star_korr,
            "sat_korr": sat_korr}


def _kla(z, U_fit, bilanz, z_meas, p, ausgabe):
    """Aktive Zone und kLa_log_mean."""
    treibende_kraft = bilanz["C_star_korr"] - bilanz["C_L_korr"]
    aktiv = aktive_zone(treibende_kraft, bilanz["C_star_korr"], p)
    kla_log = kla_log_mean(z, U_fit, treibende_kraft, aktiv, p)

    # Einlauf vor dem ersten Messpunkt: keine Messinformation, nicht aktiv
    aktiv_anzeige = aktiv.copy()
    if len(z_meas) > 0:
        aktiv_anzeige[:np.searchsorted(z, z_meas[0])] = False
    n_aktiv = int(aktiv.sum())
    ausgabe(f"    kLa_log_mean = {kla_log:.3f} 1/s ({n_aktiv} Punkte in der aktiven Zone)")
    return {"aktiv": aktiv_anzeige, "kla_log_mean": kla_log}


def _druckkorrigierte_blasenlaenge(blasen, bilanz):
    """Blasenvolumen auf den Einlassdruck umgerechnet und zurück in eine Länge."""
    V_korr = blasen["V_b"] * (bilanz["P_trocken"] / bilanz["P_trocken_0"])
    L = np.zeros(len(V_korr))
    for i in range(len(V_korr)):
        V_zyl = max(0.0, V_korr[i] - blasen["V_caps"][i])
        L[i] = V_zyl / blasen["A_b"][i] + blasen["d_b"][i]
    return L


# =============================================================================
# Betriebspunkt
# =============================================================================

def _werte_betriebspunkt_aus(df, reihe, gas, liq, name, p, regeln, kalibrier_db, ausgabe):
    kontext = f"{reihe.bezeichnung} | {name}"
    ausgabe(f"\n  Betriebspunkt {name} (u_G = {gas} m/s, u_L = {liq} m/s)")
    df, kamera_idx, n_serien = _bereite_messpunkte_vor(df)

    grund = betriebspunkt_ueberspringen(regeln.get("betriebspunkte_ueberspringen"), gas, liq)
    if grund:
        ausgabe(f"    übersprungen (ausschluesse.yaml): {grund}")
        return None
    if df.empty:
        ausgabe("    übersprungen: keine Messpunkte.")
        return None

    # --- Stoffdaten -----------------------------------------------------------------
    T = df["Temperatur_C"].mean() + 273.15
    P_aus = df["Druck_Pa_Auslass"].mean()
    try:
        stoff = dict(stoffdaten.fluessigkeit(p.fluessigkeit, T=T, P=P_aus))
        stoff["H_cp"] = stoffdaten.henry(reihe.gas, p.fluessigkeit, T=T)
        stoff["P_v"] = stoffdaten.dampfdruck(p.fluessigkeit, T=T)
        stoff["T"] = T
    except ValueError as e:
        warnings.warn(f"Betriebspunkt {name} übersprungen, Stoffdaten fehlerhaft: {e}")
        return None
    _pruefe_gueltigkeit(kontext, reihe.geometrie, gas, liq, reihe.d_kanal_m,
                        (stoff["mu"] * liq) / stoff["sigma"])

    # --- Fits und Ortsgitter --------------------------------------------------------
    fit = _fit_phasenlaengen(df, kamera_idx, reihe, p, kontext, ausgabe)
    z = np.arange(0, reihe.laenge_m + p.dz_m, p.dz_m)
    L_b_fit = fit["f_b"](z)
    L_s_fit = fit["f_s"](z)
    U_fit, schlupf = _begrenze_geschwindigkeit(fit["f_u"](z), fit["U_meas"], gas, liq, p, kontext)
    if np.any(U_fit <= 0) or np.any(L_s_fit <= 0):
        warnings.warn(f"Betriebspunkt {name} übersprungen: Fit ergibt negative Geschwindigkeit oder Sluglänge.")
        return None
    L_b_fit = np.maximum(L_b_fit, 1e-6)

    # --- Druck, Stoffbilanz, kLa ----------------------------------------------------
    P = _druckprofil(z, U_fit, L_s_fit, L_b_fit, P_aus, stoff, reihe, gas, liq,
                     kalibrier_db, p, kontext, ausgabe)
    if P is None:
        return None
    ausgabe(f"    Druck: Auslass {P_aus:.1f} Pa, Einlass {P[0]:.1f} Pa")
    blasen = _blasen_entlang_z(U_fit, L_b_fit, stoff, reihe, kontext)
    bilanz = _stoffbilanz(P, L_s_fit, L_b_fit, blasen, stoff, reihe, p)
    kla = _kla(z, U_fit, bilanz, fit["z_meas"], p, ausgabe)
    L_b_korr = _druckkorrigierte_blasenlaenge(blasen, bilanz)
    D_co2 = stoffdaten.diffusion_co2_wasser(T)

    profile = _profiltabelle(z, L_b_fit, L_b_korr, L_s_fit, U_fit, P, bilanz, kla, fit,
                             kamera_idx, n_serien)

    # --- Kennwerte je Betriebspunkt -------------------------------------------------
    u_B, L_B, L_S = float(np.nanmean(U_fit)), float(np.nanmean(L_b_fit)), float(np.nanmean(L_s_fit))
    geom_lit = "rund" if reihe.geometrie == "circular" else "eckig"
    try:
        lit = alle_literaturwerte(modelleingaben(u_B, L_B, L_S, float(reihe.d_kanal_m), float(D_co2),
                                                 geom_lit, float(gas), float(liq), p))
    except Exception as e:
        protokoll.warnung(kontext, f"Literatur-kLa fehlgeschlagen: {e}")
        lit = {}
    info, offsets = fit["info"], fit["info"].get("offsets")
    n_spez = (bilanz["n_korr"][-1] * (U_fit[0] / (L_b_fit[0] + L_s_fit[0]))
              / (bilanz["A_kanal"] * z[-1]))
    zeile = {
        "Config": name,
        "GasVelocity_m_s": gas,
        "LiquidVelocity_m_s": liq,
        "kLa_log_mean_1_s": kla["kla_log_mean"],
        "BubbleLength_mean_m": np.nanmean(L_b_fit),
        "BubbleLength_start_m": float(L_b_fit[0]) if len(L_b_fit) else np.nan,
        "BubbleLength_meas_mean_m": np.nanmean(fit["L_b_meas"]),
        "Velocity_mean_m_s": np.nanmean(U_fit),
        "Velocity_meas_mean_m_s": np.nanmean(fit["U_meas"]),
        "slip_meas_over_theo": schlupf,
        "fit_n_series": int(info.get("n_series", 0)),
        "fit_offset_o2_mm": float(offsets[0] * 1e3) if offsets is not None and len(offsets) >= 1 else np.nan,
        "fit_offset_o3_mm": float(offsets[1] * 1e3) if offsets is not None and len(offsets) >= 2 else np.nan,
        **fit["guete"],
        **lit,
        "SlugLength_mean_m": L_S,
        "n_spez_mol_s_m3": n_spez,
        "d_h_m": float(reihe.d_kanal_m),
        "Geometrie": geom_lit,
        "D_CO2_m2_s": float(D_co2),
        "T_sys_K": float(T),
        "P_aus_Pa": float(P_aus),
    }
    return profile, zeile


def _profiltabelle(z, L_b_fit, L_b_korr, L_s_fit, U_fit, P, bilanz, kla, fit, kamera_idx, n_serien):
    """Profile entlang z plus Kamerafenster, Fit-Offsets und Messpunkte."""
    df = pd.DataFrame({
        "Position_z_m": z,
        "L_bubble_fit_m": L_b_fit,
        "L_bubble_corrected_m": L_b_korr,
        "L_slug_fit_m": L_s_fit,
        "U_fit_m_s": U_fit,
        "Pressure_Pa": P,
        "Diffused_Gas_mol": bilanz["n_korr"],
        "C_L_bulk_mol_m3": bilanz["C_L_korr"],
        "C_star_lokal_mol_m3": bilanz["C_star_korr"],
        "C_star_lokal_raw_mol_m3": bilanz["C_star_roh"],
        "Saturation_percent": bilanz["sat_korr"],
        "Saturation_percent_raw": bilanz["sat_roh"],
        "aktive_zone": kla["aktiv"].astype(int),
    })
    n = len(z)
    off = fit["info"].get("offsets")
    off = off if off is not None else np.array([])
    df["fit_offset_o1_m"] = np.zeros(n) if kamera_idx is not None else np.full(n, np.nan)
    df["fit_offset_o2_m"] = np.full(n, float(off[0])) if len(off) >= 1 else np.full(n, np.nan)
    df["fit_offset_o3_m"] = np.full(n, float(off[1])) if len(off) >= 2 else np.full(n, np.nan)
    z_meas = fit["z_meas"]
    for j in range(3):
        zmin, zmax = np.nan, np.nan
        if kamera_idx is not None and j < n_serien and (kamera_idx == j).any():
            zmin, zmax = float(np.nanmin(z_meas[kamera_idx == j])), float(np.nanmax(z_meas[kamera_idx == j]))
        df[f"cam{j+1}_z_min_m"] = zmin
        df[f"cam{j+1}_z_max_m"] = zmax
    mess = pd.DataFrame({"z_meas_m": z_meas, "L_b_meas_m": fit["L_b_meas"]})
    return pd.concat([df, mess], axis=1)
