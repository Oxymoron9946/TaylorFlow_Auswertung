# 5 Konfiguration

Alle Einstellungen stehen in `config.py` im Projektordner. Die Datei ist in
nummerierte Abschnitte gegliedert. Plots und Darstellung (Abschnitte 4 und 5
der Datei) beschreibt Kapitel 4; dieses Kapitel beschreibt die übrigen
Einträge.

Werte, die das Rechenergebnis beeinflussen, stehen in `PARAMETER`. Mit ihren
Standardwerten entstehen die Referenzergebnisse in `tests/referenz/`. Die
Spalte **Wirkung** gibt an, wie stark sich eine Änderung auf kLa_log_mean
auswirkt. Grundlage sind Variationsrechnungen mit den mitgelieferten
Messreihen (5 Kanäle, 55 Betriebspunkte); „–“ heißt nicht gesondert untersucht.

## 5.1 Ordner und Dateien

| Eintrag | Standard | Bedeutung |
|---|---|---|
| `ROHDATEN_ORDNER` | `data/raw` | mitgelieferte Messdateien; Quelle für `MESSDATEIEN = "alle"` |
| `DIALOG_ORDNER` | wie `ROHDATEN_ORDNER` | Ordner, in dem das Auswahlfenster startet, z. B. der Ausgabeordner der Videoauswertung |
| `ERGEBNIS_ORDNER` | `ergebnisse` | Ausgaben; ein Unterordner je Kanal |
| `AUSSCHLUSS_DATEI` | `config/ausschluesse.yaml` | Ausschlussregeln (Kapitel 2.4) |
| `KALIBRIER_DATENBANK` | `data/calibrated_c_database.json` | Bretherton-Faktoren der runden Kanäle (Kapitel 10) |
| `MODELL_DATEI` | `config/eigene_modelle.yaml` | gespeicherte eigene Modelle (Kapitel 9) |

Pfade außerhalb des Projektordners werden mit `Path(r"…")` angegeben, z. B.
`DIALOG_ORDNER = Path(r"D:\Videoauswertung\output\Output_MassTransfer")`.

## 5.2 Umfang der Auswertung

| Eintrag | Standard | Bedeutung |
|---|---|---|
| `MESSDATEIEN` | `"dialog"` | `"dialog"` = Auswahlfenster; `"alle"` = alle `Auswertung_Masse_*.csv` in `ROHDATEN_ORDNER`; oder eine Liste von Dateipfaden |
| `NEU_RECHNEN` | `True` | `False`: nur die Plots aus vorhandenen Ergebnissen neu zeichnen |
| `BETRIEBSPUNKTE` | `None` | Betriebspunkte für die Plots je Betriebspunkt; `None` = alle |

## 5.3 Auswerte-Parameter (`PARAMETER`)

### Kamerafilter

| Eintrag | Standard | Einheit | Bedeutung |
|---|---|---|---|
| `kamerafilter_rel_se_max_prozent` | 5,0 | % | max. relativer Standardfehler der Blasenlänge je Bin |
| `kamerafilter_n_min` | 50 | – | min. Anzahl Messpunkte je Bin |
| `kamerafilter_cv_max_prozent` | 50,0 | % | max. Variationskoeffizient je Bin |
| `kamerafilter_anteil_min` | 0,75 | – | min. Anteil gültiger Bins, damit eine Kamera bleibt |
| `kamerafilter_bins_min` | 3 | – | min. Anzahl gültiger Bins je Kamera |

### Blasenlängen-Fit

| Eintrag | Standard | Einheit | Bedeutung | Wirkung |
|---|---|---|---|---|
| `fit_serien_offsets` | `True` | – | Kamera-Offsets o_j mitfitten (Kamera 1 ist Bezug) | – |
| `fit_loss` | `"soft_l1"` | – | robuste Verlustfunktion; `"linear"` = klassische kleinste Quadrate | – |
| `sigma_sys_m` | 2e-6 | m | systematischer Messfehler, quadratisch zum Standardfehler addiert | – |
| `sigma_sem_floor_m` | 1e-6 | m | Untergrenze des Standardfehlers je Bin | – |
| `fit_lambda0_m` | 0,05 | m | Startwert der Absorptionslänge λ | keine (0,01–0,2 m) |
| `offset_bound_anteil` | 0,2 | – | Grenze \|o_j\| ≤ Anteil · mittlere Blasenlänge | keine (Grenze nie erreicht) |

Die Kamera löst etwa 55 µm/px auf. Die beiden Fehlergrenzen von 1 und 2 µm
liegen weit darunter; sie verhindern nur, dass Bins mit sehr vielen Blasen
den Fit dominieren.

### Integration

| Eintrag | Standard | Einheit | Bedeutung | Wirkung |
|---|---|---|---|---|
| `dz_m` | 1e-3 | m | Ortsschritt für Druckprofil und Stoffbilanz | gering (0,25–2 mm: Prozentbereich) |
| `u_fit_cap_faktor` | 1,5 | – | gefittete Geschwindigkeiten über Faktor · U_ref werden verworfen und interpoliert; U_ref = max(Median der Messung, u_G + u_L) | keine (nie aktiv) |
| `saettigung_clip` | 0,999 | – | C_L wird höchstens auf diesen Anteil von C* gesetzt | keine (0,99–0,999) |

### Messunsicherheiten

| Eintrag | Standard | Bedeutung |
|---|---|---|
| `u_rel_h_cp` | 0,03 | relative Unsicherheit der Henry-Konstante |
| `u_rel_p_co2` | 0,02 | relative Unsicherheit des CO2-Partialdrucks |

Beide Werte legen fest, wo die aktive Zone endet (Kapitel 7.6). Die übrigen
drei Einträge dieses Abschnitts (`k_opt_mm_pro_px`, `u_rel_dn_dt`,
`pixel_unsicherheit_px`) gehören zur Fehlerfortpflanzung in
`taylorflow/unsicherheit.py`. Diese Funktion ist für eigene
Unsicherheitsbetrachtungen vorhanden und wird von der Auswertung nicht
aufgerufen.

### kLa-Auswertung

| Eintrag | Standard | Bedeutung | Wirkung |
|---|---|---|---|
| `max_urel_delta_c` | 0,5 | ein Gitterpunkt gehört zur aktiven Zone, wenn ΔC > 0 und die Unsicherheit von C* höchstens dieser Anteil von ΔC ist | keine (0,3–0,7) |
| `logmean_min_aktive_punkte` | 10 | weniger aktive Gitterpunkte: kLa_log_mean = 0 | – |

### Druckverlust und Stoffdaten

| Eintrag | Standard | Bedeutung |
|---|---|---|
| `c_bretherton_theorie` | 0,465 | Bretherton-Faktor für runde Kanäle ohne verwendbare Kalibrierung |
| `fluessigkeit` | `"Water"` | Flüssigkeitsname für die Bibliothek `thermo` |

Die Literaturmodelle rechnen mit festen Stoffwerten für Wasser/CO2 bei etwa
25 °C (Kapitel 9.2). Diese stehen in `taylorflow/parameter.py` (`lit_*`) und
lassen sich bei Bedarf ebenfalls in `PARAMETER` setzen.

Ein unbekannter Name in `PARAMETER` führt zu einer Meldung mit allen
erlaubten Namen.

## 5.4 Weitere Abschnitte

| Abschnitt | Skript | Kapitel |
|---|---|---|
| `VERGLEICH` | `literaturvergleich.py` | 9 |
| `KALIBRIERUNG` | `kalibrierung.py` | 10 |
| `MONOLITH` | `monolith.py` | 11 |
