# Änderungshistorie

Versionen ab 3.0 gelten für dieses Repository. Die Versionen 1.x und 2.x
stammen aus dem Repository des Forschungspraktikums (dort als `ETL_VERSION`
geführt); ausführlich beschrieben sind sie in METHODIK.md §11 des alten
Repositorys.

## 3.0.0 (Oktober 2026), Übergabeversion

### Rechnung

- **Log-Mean-kLa:** Die Verweilzeit wird jetzt bis einschließlich zum letzten
  Punkt der aktiven Zone integriert; bis 2.2.12 endete die Integration einen
  Gitterpunkt (1 mm) zu früh.
  - Auswirkung auf `kLa_log_mean_1_s` der mitgelieferten Daten: Median
    −0,14 %, größte Änderung −2,2 % (PVC 1500/1150).
  - Alle Werte je Betriebspunkt: `docs/belege/logmean_fix_vergleich.csv`.
- **Alle anderen Ergebniswerte sind bit-gleich zu 2.2.12.** Geprüft mit einem
  Vergleich aller Spalten aller fünf Kanäle gegen den Stand des Praktikums
  (alter Commit 4edd541).

### Entfernt

- **GUI:** Plots und Auswertung werden über `config.py` und die Skripte
  gesteuert.
- **Gewichteter kLa-Mittelwert:** alle Varianten (`kLa_weighted_mean_*`,
  `kLa_chi2_red*`, `kLa_weight_mode`).
- **Vergleichsspalten:** `kLa_mean_1_s` (Mittel inklusive Einlauf-Nullen),
  `kLa_mean_valid_1_s`, `kLa_legacy_mean_1_s`, `Velocity_theo_mean_m_s`.
- **Diagnose-Schalter über Umgebungsvariablen:** alternative Druckmodelle
  Kreutzer/Warnier, Würfelnäherung der Blasenkappen, Fit-Vergleichslauf.
- **Toter Code:** u. a. ein Re-Fit ungefilterter Daten, der nie ausgeführt
  wurde.
- **Diagnose-Skripte, Plot-Altlasten, LaTeX-Warnungstabelle,
  Status-Scanner:** Sie bleiben im Archiv-Repository.

### Neu

- **`config.py`:** alle Einstellungen an einer Stelle.
- **`config/ausschluesse.yaml`:** Ausschlussregeln, die bisher an drei Stellen
  im Code verteilt waren (Datei-Ausschlüsse, Sonderregeln Glas/PTFE,
  `manual_exclude.yaml`).
- **Kanalname:** enthält jetzt Reaktorlänge und CO2-Anteil, z. B.
  `PVC_Rund_1000um_72cm_20molCO2_600um`. Unbekannte Formbuchstaben im
  Dateinamen führen zu einer Fehlermeldung statt still zu „eckig“.
- **Neue Spalten in der Betriebspunkt-Tabelle:** `SlugLength_mean_m`,
  `n_spez_mol_s_m3`, `d_h_m`, `Geometrie`, `D_CO2_m2_s`, `T_sys_K`,
  `P_aus_Pa`.
- **Literaturmodelle:** stehen in einer Registry; eigene Modelle
  (Potenzansatz) lassen sich anpassen, speichern und vergleichen
  (`literaturvergleich.py`).
- **Monolith-Auswertung:** jetzt als ein Modul; vorher gab es drei
  abweichende Kopien.
- **Druckkalibrierung:**
  - Die Datenbank wird nur auf ausdrücklichen Wunsch geschrieben.
  - Manuelle `USE`/`NOTE`-Felder bleiben beim Neukalibrieren erhalten.
  - Je Ersatzmodell werden R² und AIC ausgegeben.
- **Plots:**
  - einheitlicher Stil
  - Größen in cm
  - Deutsch oder Englisch
  - Dezimalkomma
  - PNG und/oder PDF
- **Tests:** Regressionstest gegen eingefrorene Referenzwerte und Tests
  einzelner Bausteine.

## Frühere Versionen (Forschungspraktikum, Kurzfassung)

| Version | Änderung |
|---|---|
| 2.2.12 | Kappenvolumen im eckigen Kanal als Halbellipsoid π/6·d³ statt Würfel d³ (nur Glas Eckig betroffen) |
| 2.2.11 | Kappen-Größen (kL_caps, kLa_caps) zurückgezogen, Fourier-Trennung nicht belastbar |
| 2.2.9 | Kalibrierung Glas eckig und PVC 1500/1150 als USE=false markiert; Warnier-Reste entfernt |
| 2.2.6 | Ausreißerfilter auf Modified Z-Score (k = 3,5) + Hard-Cap 20 1/s; Log-Mean ab 10 aktiven Punkten |
| 2.2.5 | Sättigung in Heatmaps mit Systemtemperatur; Warnungen statt stiller Ausfälle |
| 2.2 | Literaturkorrelationen für kLa im Export |
| 2.1 | Datenqualitätsfilter: Mindestzahl valider Punkte, manuelle Ausschlussliste |
| 2.0 | Analytische Ableitung dn/dz aus dem Blasenfit tatsächlich aktiviert (Bugfix) |
| 1.9 | Duplikatregel je Kamera und Bin |
| 1.8 | Kurimoto (2020) für eckige Kanäle |
| 1.6 | Lokales C*, Fehlerkriterium für die aktive Zone, Snap-to-First entfernt |
| 1.5 | Schlupffilter physikalisch begründet |
| 1.3 | Kamera-Offsets im Blasenfit |
