# -*- coding: utf-8 -*-
"""
Einstellungen der Taylor-Flow-Auswertung.

Diese Datei ist die einzige Stelle, an der Einstellungen geändert werden.
Die Skripte im Hauptordner lesen sie beim Start:

    python auswertung.py          Auswertung der Messreihen + Plots
    python literaturvergleich.py  Vergleich mit Literatur- und eigenen Modellen
    python monolith.py            Monolith-Auswertung und Vergleich mit einem Kanal
    python kalibrierung.py        Druckkalibrierung (Bretherton-Faktor c)

Bedeutung jedes Eintrags: docs/03_konfiguration.md
"""

from pathlib import Path

HIER = Path(__file__).resolve().parent

# =============================================================================
# 1. Ordner und Dateien
# =============================================================================
ROHDATEN_ORDNER = HIER / "data" / "raw"            # Auswertung_Masse_*.csv, Auswertung_Druck_*.csv
ERGEBNIS_ORDNER = HIER / "ergebnisse"              # wird angelegt; ein Unterordner je Kanal
AUSSCHLUSS_DATEI = HIER / "config" / "ausschluesse.yaml"
KALIBRIER_DATENBANK = HIER / "data" / "calibrated_c_database.json"
MODELL_DATEI = HIER / "config" / "eigene_modelle.yaml"

# =============================================================================
# 2. Was wird ausgewertet?
# =============================================================================
# True:  Messdateien neu auswerten, danach Plots erzeugen.
# False: nur Plots aus vorhandenen Ergebnissen erzeugen (schnell).
NEU_RECHNEN = True

# None = alle Dateien Auswertung_Masse_*.csv im Rohdatenordner.
# Sonst Liste von Kanalnamen, z. B. ["PVC_Rund_1000um_72cm_20molCO2_600um"].
# Kanalname = <Material>_<Rund|Eckig>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um
KANAELE = None

# =============================================================================
# 3. Auswerte-Parameter
# =============================================================================
# Standardwerte = Stand des Forschungspraktikums. Erläuterung, Herkunft und
# Sensitivität jedes Werts: docs/03_konfiguration.md, Abschnitt 3.
PARAMETER = dict(
    # Automatischer Kamerafilter
    kamerafilter_rel_se_max_prozent=5.0,
    kamerafilter_n_min=50,
    kamerafilter_cv_max_prozent=50.0,
    kamerafilter_anteil_min=0.75,
    kamerafilter_bins_min=3,
    # Blasenlängen-Fit
    fit_serien_offsets=True,
    fit_loss="soft_l1",
    sigma_sys_m=2e-6,
    sigma_sem_floor_m=1e-6,
    fit_lambda0_m=0.05,
    offset_bound_anteil=0.2,
    # Integration
    dz_m=1e-3,
    u_fit_cap_faktor=1.5,
    saettigung_clip=0.999,
    # Messunsicherheiten (gehen in die Grenze der aktiven Zone ein)
    u_rel_h_cp=0.03,
    u_rel_p_co2=0.02,
    # Messunsicherheiten, nur für taylorflow/unsicherheit.py
    k_opt_mm_pro_px=0.0548,
    u_rel_dn_dt=0.0729,
    pixel_unsicherheit_px=1.41,
    # kLa-Auswertung
    max_urel_delta_c=0.5,
    logmean_min_aktive_punkte=10,
    # Druckverlust (runde Kanäle ohne Kalibrierung)
    c_bretherton_theorie=0.465,
    # Flüssigkeit (Name für die Bibliothek thermo)
    fluessigkeit="Water",
)

# =============================================================================
# 4. Plots von auswertung.py
# =============================================================================
PLOTS = dict(
    # Je Betriebspunkt
    blasenlaengen_fit=True,      # Messwerte, Fit mit/ohne Kamera-Offsets, Druckkorrektur
    stoffmenge=True,             # absorbierte Stoffmenge je Blase Δn(z)
    druckprofil=True,            # berechneter Druck p(z)
    # Je Kanal
    kla_flaeche=True,            # 3D: kLa_log_mean über u_G, u_L
    nspez_flaeche=True,          # 3D: volumenspezifischer Molenstrom
    heatmaps=True,               # 2 × 3 Kennzahlen-Übersicht
    modell_flaechen=["yue_2007"],  # 3D: Modellvorhersagen (Namen siehe docs/05_plots.md)
)

# Betriebspunkte für die Plots je Betriebspunkt.
# None = alle; sonst Namen wie in der Spalte "Config", z. B. ["Gas_0_134_Liq_0_056"].
BETRIEBSPUNKTE = None

# =============================================================================
# 5. Darstellung (gilt für alle Skripte)
# =============================================================================
STIL = dict(
    sprache="de",                 # "de" oder "en"
    formate=("png",),             # z. B. ("png", "pdf")
    dpi=300,
    schriftgroesse=10.0,
    groesse_profil_cm=(16.0, 9.0),
    groesse_3d_cm=(14.0, 11.0),
    groesse_heatmaps_cm=(30.0, 17.0),
    groesse_paritaet_cm=(12.0, 11.0),
    titel_anzeigen=True,
    blickwinkel_3d=(25, 135),     # (Höhe, Azimut) in Grad
)

# =============================================================================
# 6. Literaturvergleich und eigene Modelle (literaturvergleich.py)
# =============================================================================
VERGLEICH = dict(
    kanaele=None,                      # None = alle ausgewerteten Kanäle
    zielgroesse="kLa_log_mean_1_s",    # beliebige Zahlenspalte der Betriebspunkt-Tabelle
    groesse_beschriftung=r"$k_La_{\mathrm{log}}$ [1/s]",
    modelle=["van_baten_voll", "vandu", "shao", "liu_wang", "heiszwolf", "yao", "yue_2007", "yue_2009"],
    band_prozent=15.0,
    logarithmisch=True,
    # Eigenes Modell anpassen und speichern (None = kein Fit)
    eigener_fit=dict(
        name="potenz_kla_ug_ul",
        titel="Potenzansatz u_G, u_L",
        kanaele=None,                  # Daten für den Fit; None = wie oben
        variablen=["GasVelocity_m_s", "LiquidVelocity_m_s"],
        speichern=False,               # True: in MODELL_DATEI ablegen
    ),
)

# =============================================================================
# 7. Monolith (monolith.py)
# =============================================================================
MONOLITH = dict(
    datei=HIER / "data" / "raw" / "Monolith_Messungen.csv",
    n_kanaele=100,
    d_kanal_m=1e-3,               # quadratische Kanäle, Seitenlänge
    laenge_m=1.0,
    henry_ref_mol_m3_pa=3.3e-4,   # H_cp bei 298,15 K
    henry_dlnh_dt_k=2400.0,       # d(ln H)/d(1/T)
    vergleich_kanal="Glas_Eckig_1000um_72cm_20molCO2_600um",   # None = kein Vergleich
    vergleich_modell="yue_2007",  # zusätzliche Modellfläche im Vergleich; None = keine
)

# =============================================================================
# 8. Druckkalibrierung (kalibrierung.py)
# =============================================================================
KALIBRIERUNG = dict(
    # None = alle Auswertung_Druck_*.csv; sonst Liste von Kalibrier-Schlüsseln
    # <Material>_<circular|rectangular>_<D>um_<Nadel>um
    kanaele=None,
    # Modell für Werte außerhalb der kalibrierten Betriebspunkte:
    # "Linear", "Power-Law", "Polynomial" oder "auto" (größtes R²)
    ersatzmodell="auto",
    # True: Datenbank wirklich schreiben. False: nur berechnen und anzeigen.
    datenbank_schreiben=False,
)
