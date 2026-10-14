# -*- coding: utf-8 -*-
"""
Auswerte-Parameter der Taylor-Flow-Auswertung.

Alle Zahlenwerte, die das Ergebnis der Auswertung beeinflussen, sind hier
gesammelt. Die Standardwerte entsprechen exakt dem Stand, mit dem die
Ergebnisse des Forschungspraktikums berechnet wurden (ETL 2.2.12).

Geändert werden die Werte nicht hier, sondern in ``config.py`` im
Hauptordner (Abschnitt ``PARAMETER``). Begründung und Herkunft jedes Wertes
stehen in ``docs/03_konfiguration.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class AuswerteParameter:
    """Numerische Einstellungen der Auswertung (Einheiten im Namen bzw. Kommentar)."""

    # --- Automatischer Kamerafilter (Rohdaten) -----------------------------
    kamerafilter_rel_se_max_prozent: float = 5.0   # max. rel. Standardfehler je Bin [%]
    kamerafilter_n_min: int = 50                   # min. Anzahl Blasen je Bin [-]
    kamerafilter_cv_max_prozent: float = 50.0      # max. Variationskoeffizient je Bin [%]
    kamerafilter_anteil_min: float = 0.75          # min. Anteil gültiger Bins je Kamera [-]
    kamerafilter_bins_min: int = 3                 # min. gültige Bins je Kamera [-]

    # --- Blasenlängen-Fit ---------------------------------------------------
    fit_serien_offsets: bool = True                # Kamera-Offsets im Fit (o_1 = 0)
    fit_loss: str = "soft_l1"                      # robuste Verlustfunktion (scipy)
    sigma_sys_m: float = 2e-6                      # systematischer Messfehler [m]
    sigma_sem_floor_m: float = 1e-6                # Untergrenze Standardfehler [m]
    fit_lambda0_m: float = 0.05                    # Startwert Absorptionslänge [m]
    offset_bound_anteil: float = 0.2               # |o_j| <= Anteil * mittlere Blasenlänge [-]

    # --- Integration und Glättung ---------------------------------------------
    dz_m: float = 1e-3                             # Ortsschritt der Integration [m]
    u_fit_cap_faktor: float = 1.5                  # U_fit > Faktor * U_ref wird verworfen [-]
    saettigung_clip: float = 0.999                 # C_L wird auf Faktor * C* begrenzt [-]
    drop_fenster: int = 3                          # Fenster für Einbruch-Filter auf dn/dz [-]
    drop_schwelle: float = 0.8                     # relativer Einbruch gegen lokalen Median [-]

    # --- Messunsicherheiten -------------------------------------------------
    k_opt_mm_pro_px: float = 0.0548                # optischer Kalibrierfaktor Kamera [mm/px]
    u_rel_h_cp: float = 0.03                       # rel. Unsicherheit Henry-Konstante [-]
    u_rel_p_co2: float = 0.02                      # rel. Unsicherheit CO2-Partialdruck [-]
    u_rel_dn_dt: float = 0.0729                    # rel. Unsicherheit Stoffstrom [-]
    pixel_unsicherheit_px: float = 1.41            # Kantenunsicherheit Blasenlänge [px]

    # --- kLa-Auswertung -------------------------------------------------------
    max_urel_delta_c: float = 0.5                  # aktive Zone: u_rel(ΔC) <= Wert [-]
    logmean_min_aktive_punkte: int = 10            # min. Punkte aktive Zone für Log-Mean [-]
    kla_min_valide_punkte: int = 10                # min. valide lokale kLa-Punkte [-]
    ausreisser_mad_k: float = 3.5                  # Modified Z-Score Schwelle [-]
    ausreisser_hard_cap_1_s: float = 20.0          # Untergrenze der Ausreißer-Schwelle [1/s]

    # --- Druckverlust -------------------------------------------------------
    c_bretherton_theorie: float = 0.465            # Bretherton-Faktor ohne Kalibrierung [-]

    # --- Stoffdaten -----------------------------------------------------------
    fluessigkeit: str = "Water"                    # Name für die thermo-Bibliothek

    # --- Feste Stoffwerte nur für Literaturmodelle (Wasser/CO2, ca. 25 °C) ----
    lit_mu_l_pa_s: float = 8.9e-4
    lit_sigma_l_n_m: float = 0.072
    lit_rho_l_kg_m3: float = 997.0
    lit_mu_g_pa_s: float = 1.49e-5
    lit_rho_g_kg_m3: float = 1.80

    @classmethod
    def aus_dict(cls, werte: dict | None) -> "AuswerteParameter":
        """Erzeugt Parameter aus einem Dict; unbekannte Schlüssel sind ein Fehler."""
        werte = dict(werte or {})
        bekannt = {f.name for f in fields(cls)}
        unbekannt = sorted(set(werte) - bekannt)
        if unbekannt:
            raise KeyError(
                f"Unbekannte Parameter in config.PARAMETER: {unbekannt}. "
                f"Erlaubt sind: {sorted(bekannt)}"
            )
        return cls(**werte)
