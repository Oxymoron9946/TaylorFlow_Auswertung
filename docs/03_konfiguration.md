# 3 Konfiguration

Alle Einstellungen stehen in `config.py` im Hauptordner. Die Datei ist in
Abschnitte gegliedert. Werte, die das Rechenergebnis betreffen, stehen in
Abschnitt 3 (`PARAMETER`). Ihre Standardwerte entsprechen dem Stand des
Forschungspraktikums; damit sind auch die Referenzergebnisse in
`tests/referenz/` berechnet.

## 3.1 Ordner und Dateien

| Name | Standard | Bedeutung |
|---|---|---|
| `ROHDATEN_ORDNER` | `data/raw` | Messdateien `Auswertung_Masse_*.csv` und `Auswertung_Druck_*.csv` |
| `ERGEBNIS_ORDNER` | `ergebnisse` | Ausgaben; ein Unterordner je Kanal |
| `AUSSCHLUSS_DATEI` | `config/ausschluesse.yaml` | Ausschlussregeln, siehe [Kapitel 2.4](02_messdaten.md) |
| `KALIBRIER_DATENBANK` | `data/calibrated_c_database.json` | Bretherton-Faktoren der runden Kanäle |
| `MODELL_DATEI` | `config/eigene_modelle.yaml` | gespeicherte eigene Modelle |

## 3.2 Umfang der Auswertung

| Name | Standard | Bedeutung |
|---|---|---|
| `NEU_RECHNEN` | `True` | `False`: nur Plots aus vorhandenen Ergebnissen (z. B. nach Stiländerung) |
| `KANAELE` | `None` | `None` = alle Messdateien; sonst Liste von Kanalnamen |
| `BETRIEBSPUNKTE` | `None` | Betriebspunkte für die Plots je Betriebspunkt; `None` = alle |

## 3.3 Auswerte-Parameter (`PARAMETER`)

Die Sensitivitätsangaben stammen aus den Analysen des Forschungspraktikums
(Datensatz: 5 Kanäle, 55 Betriebspunkte).

### Kamerafilter

| Name | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `kamerafilter_rel_se_max_prozent` | 5,0 | % | max. relativer Standardfehler der Blasenlänge je Bin |
| `kamerafilter_n_min` | 50 | – | min. Blasenanzahl je Bin |
| `kamerafilter_cv_max_prozent` | 50,0 | % | max. Variationskoeffizient je Bin |
| `kamerafilter_anteil_min` | 0,75 | – | min. Anteil gültiger Bins, damit eine Kamera bleibt |
| `kamerafilter_bins_min` | 3 | – | min. Anzahl gültiger Bins je Kamera |

### Blasenlängen-Fit

| Name | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `fit_serien_offsets` | `True` | – | Kamera-Offsets o_j mitfitten (Kamera 1 ist Referenz) |
| `fit_loss` | `"soft_l1"` | – | robuste Verlustfunktion von scipy; `"linear"` = klassische kleinste Quadrate |
| `sigma_sys_m` | 2e-6 | m | systematischer Messfehler (Positionierung, Optik), wird quadratisch zum Standardfehler addiert |
| `sigma_sem_floor_m` | 1e-6 | m | Untergrenze des Standardfehlers je Bin |
| `fit_lambda0_m` | 0,05 | m | Startwert der Absorptionslänge λ; Ergebnis unempfindlich zwischen 0,01 und 0,2 m |
| `offset_bound_anteil` | 0,2 | – | Grenze \|o_j\| ≤ Anteil · mittlere Blasenlänge; im Datensatz nie erreicht |

Hintergrund zu den beiden Fehlergrenzen:
- Die Kamera löst 54,8 µm/px auf.
- Beide Werte (1 µm, 2 µm) liegen weit darunter. Sie verhindern nur, dass Bins
  mit sehr vielen Blasen den Fit dominieren und χ²_red künstlich ansteigt.

### Integration und Glättung

| Name | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `dz_m` | 1e-3 | m | Ortsschritt für Druckprofil und Stoffbilanz; Änderungen im Prozentbereich bei 0,25–2 mm |
| `u_fit_cap_faktor` | 1,5 | – | Werte der gefitteten Geschwindigkeit über Faktor · U_ref werden verworfen und interpoliert (U_ref = max(Median der Messung, u_G + u_L)); im Datensatz nie aktiv |
| `saettigung_clip` | 0,999 | – | C_L wird höchstens auf diesen Anteil von C* gesetzt (numerischer Schutz); 0,99–0,999 ohne Einfluss auf kLa_log_mean |
| `drop_fenster` | 3 | – | Fensterbreite des Einbruchfilters auf dn/dz |
| `drop_schwelle` | 0,8 | – | Punkt gilt als Einbruch, wenn er unter (1 − Schwelle) · gleitender Median liegt; ohne Einfluss im Datensatz |

### Messunsicherheiten

Diese Werte gehen in die aktive Zone und in die Spalte `u_rel_kLa` ein.

| Name | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `k_opt_mm_pro_px` | 0,0548 | mm/px | optischer Kalibrierfaktor der Hochgeschwindigkeitskamera |
| `u_rel_h_cp` | 0,03 | – | relative Unsicherheit der Henry-Konstante (Sander 2015) |
| `u_rel_p_co2` | 0,02 | – | relative Unsicherheit des CO2-Partialdrucks (Drucksensor) |
| `u_rel_dn_dt` | 0,0729 | – | relative Unsicherheit des Stoffstroms je Blase (Volumen 4,73 % und Geschwindigkeit 5,55 %, quadratisch addiert) |
| `pixel_unsicherheit_px` | 1,41 | px | Unsicherheit einer Länge aus zwei Kanten mit je ±1 px (√2) |

**Bei einer neuen Kamera oder Optik:** `k_opt_mm_pro_px` anpassen.

### kLa-Auswertung

| Name | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `max_urel_delta_c` | 0,5 | – | Punkt gehört zur aktiven Zone, wenn ΔC > 0 und u_rel(ΔC) ≤ Wert. 0,3 ist strenger, 0,7 großzügiger; 0,3–0,7 ohne Einfluss auf kLa_log_mean im Datensatz |
| `logmean_min_aktive_punkte` | 10 | – | weniger aktive Gitterpunkte: kLa_log_mean = 0 |
| `kla_min_valide_punkte` | 10 | – | weniger valide lokale kLa-Werte (nach Ausreißerfilter): kLa_log_mean = leer |
| `ausreisser_mad_k` | 3,5 | – | Modified Z-Score nach Iglewicz/Hoaglin (1993): lokales kLa über Median + k · 1,4826 · MAD gilt als Ausreißer |
| `ausreisser_hard_cap_1_s` | 20,0 | 1/s | Die Ausreißerschwelle liegt mindestens hier (Größenordnung aus Yue 2007) |

Der Ausreißerfilter wirkt nur auf das lokale kLa (`kLa_lokal_1_s`) und damit
auf die Zahl valider Punkte. kLa_log_mean selbst wird aus den
Konzentrationen an den Rändern der aktiven Zone berechnet
(siehe [Kapitel 6](06_methodik.md)).

### Druckverlust und Stoffdaten

| Name | Standard | Bedeutung |
|---|---|---|
| `c_bretherton_theorie` | 0,465 | Bretherton-Faktor für runde Kanäle ohne (verwendbare) Kalibrierung |
| `fluessigkeit` | `"Water"` | Flüssigkeitsname für die Bibliothek `thermo` |

Die festen Stoffwerte der Literaturmodelle (`lit_*`, Wasser/CO2 bei etwa 25 °C)
stehen in `taylorflow/parameter.py`. Sie sind nicht in `config.py` aufgeführt,
können dort aber ebenfalls gesetzt werden.

## 3.4 Plots (`PLOTS`)

| Name | Standard | Plot |
|---|---|---|
| `blasenlaengen_fit` | `True` | je Betriebspunkt: Messwerte, Fit, druckkorrigierte Blasenlänge |
| `stoffmenge` | `True` | je Betriebspunkt: absorbierte Stoffmenge Δn(z) |
| `druckprofil` | `True` | je Betriebspunkt: p(z) |
| `kla_flaeche` | `True` | je Kanal: 3D-Fläche kLa_log_mean |
| `nspez_flaeche` | `True` | je Kanal: 3D-Fläche ṅ_spez |
| `heatmaps` | `True` | je Kanal: sechs Kennzahlen als Farbkarten |
| `modell_flaechen` | `["yue_2007"]` | je Kanal: 3D-Fläche je genanntem Modell; `[]` = keine |

Beispiele und Erläuterung: [Kapitel 5](05_plots.md).

## 3.5 Darstellung (`STIL`)

| Name | Standard | Bedeutung |
|---|---|---|
| `sprache` | `"de"` | `"de"` (Dezimalkomma) oder `"en"` |
| `formate` | `("png",)` | ein oder mehrere Formate, z. B. `("png", "pdf")` |
| `dpi` | 300 | Auflösung der Rastergrafiken |
| `schriftgroesse` | 10 | Grundschriftgröße [pt] |
| `groesse_profil_cm` | (16, 9) | Breite, Höhe der Profilplots [cm] |
| `groesse_3d_cm` | (14, 11) | 3D-Flächen |
| `groesse_heatmaps_cm` | (30, 17) | Kennzahlen-Übersicht |
| `groesse_paritaet_cm` | (12, 11) | Paritätsdiagramme |
| `titel_anzeigen` | `True` | Titel über den Plots (für Abbildungen in Arbeiten meist `False`) |
| `blickwinkel_3d` | (25, 135) | Höhe und Azimut der 3D-Ansicht [°] |

## 3.6 Weitere Abschnitte

- `VERGLEICH`: Literaturvergleich, siehe [Kapitel 8](08_literaturvergleich.md)
- `MONOLITH`: siehe [Kapitel 10](10_monolith.md)
- `KALIBRIERUNG`: siehe [Kapitel 9](09_druckkalibrierung.md)
