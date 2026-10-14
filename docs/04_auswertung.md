# 4 Ablauf der Auswertung und Ergebnisdateien

## 4.1 Ablauf

`python auswertung.py` führt für jede Messdatei folgende Schritte aus
(Code: `taylorflow/pipeline.py`, Gleichungen: [Kapitel 6](06_methodik.md)):

```
Messdatei ──► Einlesen, Ausschlüsse, Kamerafilter                 (einlesen.py)
   │
   └─► je Betriebspunkt (u_G, u_L):
         1  Messpunkte: Duplikate je Kamera und Bin entfernen
         2  Stoffdaten bei T und p am Auslass (thermo, Henry, Dampfdruck)
         3  Fits über z: Blasenlänge (v2 + Kamera-Offsets), Sluglänge, Geschwindigkeit
         4  Druckprofil: Rückwärtsintegration vom Auslass (Bretherton bzw. Kurimoto)
         5  Stoffbilanz: Blasenvolumen → absorbierte Stoffmenge → C_L, C*, Sättigung
         6  dn/dz analytisch aus dem Blasenfit
         7  kLa lokal, aktive Zone, kLa_log_mean, Ausreißer, Mindestpunktzahl
         8  Blasenlänge auf Einlassdruck korrigiert
         9  Literaturmodelle
   │
   └─► Speichern: Profile, Betriebspunkt-Tabelle, Metadaten       (ergebnisse.py)
Danach: Plots nach config.PLOTS                                    (taylorflow/plots/)
```

Die Konsole meldet je Betriebspunkt:
- das Fitmodell mit R² und χ²_red
- die Kamera-Offsets
- den verwendeten Bretherton-Faktor
- Ein- und Auslassdruck
- kLa_log_mean

## 4.2 Ergebnisdateien

Je Kanal entsteht `ergebnisse/<Kanal>/` mit:

| Datei | Inhalt |
|---|---|
| `<Kanal>_betriebspunkte.csv` | eine Zeile je Betriebspunkt: Kennwerte, Fitgüte, Literaturmodelle |
| `<Kanal>_profile.csv` | eine Zeile je z-Gitterpunkt (1 mm) und Betriebspunkt |
| `<Kanal>_meta.json` | Programmversion, Zeitpunkt, Quelldatei |
| `plots/` | Plots nach `config.PLOTS` |

Format: Semikolon, Dezimalkomma, UTF-8 mit BOM; die Dateien lassen sich direkt
in Excel öffnen. In Python liest man sie am einfachsten mit
`taylorflow.ergebnisse.lade_betriebspunkte(...)` bzw. `lade_profile(...)`; diese
Funktionen lesen Gleitkommazahlen ohne Rundungsfehler.

Die Spaltennamen sind aus dem Praktikum übernommen (englisch mit Einheit am
Ende), damit Ergebnisse vergleichbar bleiben.

### Betriebspunkt-Tabelle

| Spalte | Einheit | Bedeutung |
|---|---|---|
| `Config` | – | Name des Betriebspunkts, z. B. `Gas_0_134_Liq_0_056` |
| `GasVelocity_m_s`, `LiquidVelocity_m_s` | m/s | Leerrohrgeschwindigkeiten u_G, u_L |
| **`kLa_log_mean_1_s`** | 1/s | **Hauptergebnis:** logarithmisches Mittel über die aktive Zone; leer bei zu wenigen validen Punkten oder `kla_ungueltig` |
| `kLa_start_1_s`, `kLa_end_1_s` | 1/s | lokales kLa am ersten und letzten Gitterpunkt (am Einlauf per Definition 0) |
| `kLa_n_valid` | – | Anzahl valider lokaler kLa-Werte (nach Ausreißerfilter) |
| `BubbleLength_mean_m`, `BubbleLength_start_m` | m | gefittete Blasenlänge, Mittel über den Kanal bzw. am Einlass |
| `BubbleLength_meas_mean_m` | m | Mittel der gemessenen Blasenlängen |
| `SlugLength_mean_m` | m | gefittete Sluglänge, Mittel über den Kanal |
| `Velocity_mean_m_s` | m/s | gefittete Blasengeschwindigkeit, Mittel (= u_B der Literaturmodelle) |
| `Velocity_meas_mean_m_s` | m/s | Mittel der gemessenen Geschwindigkeiten |
| `slip_meas_over_theo` | – | Median gemessene Geschwindigkeit / (u_G + u_L); erwartet 1,05–1,30 |
| `n_spez_mol_s_m3` | mol/(s·m³) | volumenspezifischer CO2-Molenstrom über den ganzen Kanal ([6.8](06_methodik.md)) |
| `fit_model` | – | verwendetes Blasenmodell (Normalfall: `Exp+Expansion v2+Offsets …`) |
| `fit_r2`, `fit_chi2_red` | – | Güte des Blasenfits; χ²_red ≈ 1 ideal, > 3 auffällig, > 10 kritisch |
| `fit_corr_max` | – | größte Korrelation zweier Fitparameter; > 0,95 = schlecht bestimmbar |
| `fit_n_bound_hits`, `fit_bound_hits` | – | Parameter an einer Fitgrenze (Anzahl, Beschreibung) |
| `fit_n_series`, `fit_n_offsets` | – | Anzahl Kameras bzw. gefitteter Offsets |
| `fit_offset_o2_mm`, `fit_offset_o3_mm` | mm | Kamera-Offsets gegenüber Kamera 1 |
| `kLa_lit_*_1_s` | 1/s | Vorhersagen der Literaturmodelle ([Kapitel 8](08_literaturvergleich.md)) |
| `d_h_m`, `Geometrie` | m, – | Kanaldurchmesser; `rund` oder `eckig` |
| `D_CO2_m2_s` | m²/s | Diffusionskoeffizient CO2 in Wasser bei T |
| `T_sys_K`, `P_aus_Pa` | K, Pa | Temperatur und Auslassdruck (Mittel des Betriebspunkts) |
| `manual_exclude`, `manual_exclude_reason` | – | `True` und Grund bei Eintrag unter `kla_ungueltig` |

### Profiltabelle

| Spalte | Einheit | Bedeutung |
|---|---|---|
| `Config_Name` | – | Betriebspunkt |
| `Position_z_m` | m | Position im Kanal (Gitter mit `dz_m`) |
| `L_bubble_fit_m` | m | gefittete Blasenlänge (ohne Kamera-Offsets) |
| `L_bubble_corrected_m` | m | Blasenlänge, umgerechnet auf den Einlassdruck; zeigt die reine Absorption |
| `L_slug_fit_m`, `U_fit_m_s` | m, m/s | gefittete Sluglänge und Blasengeschwindigkeit |
| `Pressure_Pa` | Pa | berechneter Absolutdruck |
| `Diffused_Gas_mol` | mol | bis z absorbierte CO2-Menge je Blase (monoton) |
| `C_L_bulk_mol_m3` | mol/m³ | CO2-Konzentration in der Flüssigkeit |
| `C_star_lokal_mol_m3` | mol/m³ | Gleichgewichtskonzentration C* = H · p_CO2 |
| `Saturation_percent` | % | C_L / C* |
| `kLa_lokal_1_s` | 1/s | lokales kLa; 0 außerhalb der aktiven Zone, leer bei Ausreißern |
| `u_rel_kLa` | – | relative Unsicherheit des lokalen kLa |
| `*_raw_*` | | dieselben Größen vor Monotonie- und Sättigungskorrektur |
| `fit_offset_o1_m` … `o3_m` | m | Kamera-Offsets (konstant je Betriebspunkt) |
| `cam1_z_min_m` … `cam3_z_max_m` | m | Bereich der Messpunkte je Kamera |
| `z_meas_m`, `L_b_meas_m` | m | Messpunkte (nur in den ersten Zeilen belegt, sonst leer) |

## 4.3 Warnungsprotokoll

`ergebnisse/Modell_Gueltigkeitswarnungen.txt` wird bei jedem Lauf neu
geschrieben. Es sammelt, getrennt nach Kanal und Betriebspunkt:

| Meldung | Bedeutung | Handlungsbedarf |
|---|---|---|
| `Liu (2005): … außerhalb` | Betriebspunkt außerhalb des Bereichs der Schlupfkorrelation | meist keiner, nur Hinweis |
| `Bretherton (1961): Ca_L … > 0.005` | Kapillarzahl über dem Gültigkeitsbereich des Bretherton-Druckmodells | Druckprofil mit Vorsicht |
| `Kurimoto: …` | Ca, We, Re oder L_B/d außerhalb des Kurimoto-Bereichs | Druckprofil mit Vorsicht |
| `Blasen-Fit: chi2_red = … -> ERHEBLICH/KRITISCH` | Fit beschreibt die Messung schlecht | Blasenlängen-Plot ansehen |
| `Blasen-Fit: Parameter hoch korreliert` | A und λ (oder B) nicht unabhängig bestimmbar | kLa des Punkts kritisch prüfen |
| `Serien-Offset … nahe/am Bound` | Kameras stark gegeneinander versetzt | Kamerakalibrierung prüfen |
| `Serien-Offset … > 50% des Absorptionssignals` | Offset könnte die Absorption „schlucken“ | Plot prüfen, ggf. Kamera ausschließen |
| `Slip U_meas/U_TP > 1.5` | gemessene Geschwindigkeit unplausibel hoch | MFC-Sollwert prüfen |
| `kLa nicht berichtbar: nur n valide Punkte` | aktive Zone zu kurz | Wert bleibt leer |
| `kla_ungueltig aktiv: …` | Eintrag aus `ausschluesse.yaml` angewendet | – |
