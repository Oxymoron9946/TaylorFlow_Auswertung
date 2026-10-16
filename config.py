# -*- coding: utf-8 -*-
"""
Einstellungen der Taylor-Flow-Auswertung.

Diese Datei ist die einzige Stelle, an der Einstellungen geändert werden.
Die Skripte im Hauptordner lesen sie beim Start:

    python auswertung.py          Auswertung der Messreihen + Plots
    python literaturvergleich.py  Vergleich mit Literatur- und eigenen Modellen
    python monolith.py            Monolith-Auswertung und Vergleich mit einem Kanal
    python kalibrierung.py        Druckkalibrierung (Bretherton-Faktor c)

Bedeutung jedes Eintrags: Handbuch, Kapitel 4 (Plots) und 5 (übrige Einträge)
"""

from pathlib import Path

HIER = Path(__file__).resolve().parent

# =============================================================================
# 1. Ordner und Dateien
# =============================================================================
ROHDATEN_ORDNER = HIER / "data" / "raw"            # mitgelieferte Messdateien
# Ordner, in dem das Auswahlfenster startet, z. B. der Ausgabeordner der Videoauswertung:
# DIALOG_ORDNER = Path(r"C:\Messungen\Videoauswertung\output\Output_MassTransfer")
DIALOG_ORDNER = ROHDATEN_ORDNER
ERGEBNIS_ORDNER = HIER / "ergebnisse"              # wird angelegt; ein Unterordner je Kanal
AUSSCHLUSS_DATEI = HIER / "config" / "ausschluesse.yaml"
KALIBRIER_DATENBANK = HIER / "data" / "calibrated_c_database.json"
MODELL_DATEI = HIER / "config" / "eigene_modelle.yaml"

# =============================================================================
# 2. Was wird ausgewertet?
# =============================================================================
# Welche Messdateien (Auswertung_Masse_*.csv)?
#   "dialog"  beim Start öffnet sich ein Auswahlfenster (mehrere Dateien mit Strg)
#   "alle"    alle Dateien Auswertung_Masse_*.csv im ROHDATEN_ORDNER
#   Liste     feste Dateien, z. B.
#             [ROHDATEN_ORDNER / "Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv"]
MESSDATEIEN = "dialog"

# True:  Messdateien auswerten, danach Plots erzeugen.
# False: nur Plots aus vorhandenen Ergebnissen dieser Messdateien neu zeichnen (schnell).
NEU_RECHNEN = True

# =============================================================================
# 3. Auswerte-Parameter
# =============================================================================
# Standardwerte = Stand des Forschungspraktikums. Erläuterung, Herkunft und
# Wirkung jedes Werts: Handbuch, Kapitel 5.3.
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
# Je Plot ein Block. an=False schaltet den Plot ab. Alle anderen Einträge sind
# Anpassungen; gelöschte Einträge gelten mit dem hier gezeigten Standardwert.
# Bilder und Beispiele zu jeder Option: Handbuch, Kapitel 4.
#
# Für alle Plots:
#   titel       "auto" (Kanal bzw. Kanal | Betriebspunkt), eigener Text oder "" (ohne)
#   groesse_cm  (Breite, Höhe) in cm; None = Wert aus STIL
# Achsbereiche: (min, max) oder None = automatisch
# Farben: matplotlib-Namen ("tab:red") oder Hex-Codes ("#3B8B3B")
# Farbskalen: matplotlib-Namen, z. B. "plasma", "viridis", "coolwarm", "cividis"
PLOTS = dict(
    # --- Je Betriebspunkt (Dateien <name>_<Betriebspunkt>.png) ---------------------
    blasenlaengen_fit=dict(             # Messwerte, Fit mit/ohne Kamera-Offsets, Druckkorrektur
        an=True, titel="auto", groesse_cm=None,
        x_bereich_cm=None,              # Reaktorposition z [cm]
        y_bereich_mm=None,              # Blasenlänge [mm]
        messwerte=True,                 # Messpunkte je Kamera
        fit_ohne_offsets=True,          # hellblau gestrichelt
        fit_mit_offsets=True,           # dunkelblau
        druckkorrigiert=True,           # grün: Blasenlänge auf Einlassdruck umgerechnet
        kamerafenster=True,             # graue Bänder mit Kameranummer
        kennwertkasten=True,            # Kasten mit Offsets, R², χ²_red
        legende="unten",                # "unten", "innen", "aus" oder z. B. "upper left", "lower right"
    ),
    stoffmenge=dict(                    # absorbierte Stoffmenge je Blase Δn(z)
        an=True, titel="auto", groesse_cm=None,
        x_bereich_cm=None, y_bereich_umol=None,
        flaeche=True,                   # Fläche unter der Kurve einfärben
        farbe="#3B8B3B",
    ),
    druckprofil=dict(                   # berechneter Druck p(z)
        an=True, titel="auto", groesse_cm=None,
        x_bereich_cm=None, y_bereich=None,
        einheit="Pa",                   # "Pa", "hPa", "mbar", "kPa" oder "bar"
        farbe="#0F5FA3",
    ),
    # --- Je Kanal -------------------------------------------------------------------
    kla_flaeche=dict(                   # 3D: kLa_log_mean über u_G, u_L
        an=True, titel="auto", groesse_cm=None,
        farbskala="plasma",
        achsen=None,                    # feste Achsen, z. B. dict(x=(0, 0.3), y=(0, 0.3), z=(0, 1.5))
        blickwinkel=None,               # (Höhe, Azimut) in Grad; None = Wert aus STIL
        messpunkte=True, hoehenlinien=True,
        transparenz=0.85,               # Deckkraft der Fläche, 0 … 1
    ),
    nspez_flaeche=dict(                 # 3D: volumenspezifischer Molenstrom ṅ_spez
        an=True, titel="auto", groesse_cm=None,
        farbskala="coolwarm", achsen=None, blickwinkel=None,
        messpunkte=True, hoehenlinien=True, transparenz=0.85,
    ),
    modell_flaechen=dict(               # 3D: Vorhersage von Literatur- oder eigenen Modellen
        an=True, titel="auto", groesse_cm=None,
        modelle=["yue_2007"],           # je Modell ein Bild; Namen: Handbuch, Kapitel 4.7
        farbskala="plasma", achsen=None, blickwinkel=None,
        messpunkte=True, hoehenlinien=True, transparenz=0.85,
    ),
    spalten_flaechen=dict(              # 3D: beliebige Spalten der Betriebspunkt-Tabelle
        an=False, titel="auto", groesse_cm=None,
        spalten=[                       # je Eintrag ein Bild flaeche_<spalte>.png
            dict(spalte="SlugLength_mean_m", beschriftung="Sluglänge $L_S$ [mm]", faktor=1000),
        ],
        farbskala="viridis", achsen=None, blickwinkel=None,
        messpunkte=True, hoehenlinien=True, transparenz=0.85,
    ),
    heatmaps=dict(                      # Kennzahlen-Übersicht als Farbkarten
        an=True, titel="auto", groesse_cm=None,
        # Felder in Leserichtung, bis drei je Zeile. Möglich: "kla", "saettigung_aus",
        # "z95", "beta_ein", "schlupf", "L_b_ein" oder eine Spalte der Betriebspunkt-Tabelle
        felder=["kla", "saettigung_aus", "z95", "beta_ein", "schlupf", "L_b_ein"],
        farbskalen=None,                # z. B. dict(kla="viridis")
        beschriftungen=None,            # Überschriften, z. B. dict(n_spez_mol_s_m3="ṅ_spez [mol/(s m³)]")
    ),
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
    # Messdateien Auswertung_Druck_*.csv: "dialog", "alle" (im ROHDATEN_ORDNER) oder Liste
    messdateien="dialog",
    # Startordner des Auswahlfensters, z. B. Output_PressureCalibration der Videoauswertung
    dialog_ordner=ROHDATEN_ORDNER,
    # Modell für Werte außerhalb der kalibrierten Betriebspunkte:
    # "Linear", "Power-Law", "Polynomial" oder "auto" (größtes R²)
    ersatzmodell="auto",
    # True: Datenbank wirklich schreiben. False: nur berechnen und anzeigen.
    datenbank_schreiben=False,
)
