# 7 Gültigkeit und bekannte Einschränkungen

## 7.1 Gültigkeitsbereiche der Modelle

| Modell | Bereich | Verhalten außerhalb |
|---|---|---|
| Bretherton-Druckverlust (rund) | Ca ≤ 0,005 | Warnung im Protokoll, Rechnung läuft weiter |
| Kurimoto-Druckverlust (quadratisch) | 0,00159 ≤ Ca ≤ 0,0989; 0,0817 ≤ We ≤ 25,4; 8,33 ≤ Re ≤ 791; L_B/d ≳ 2,3 | Warnung; im Glaskanal unterschreiten 10 Betriebspunkte L_B/d = 2 leicht |
| Filmdicke rund | Ca ≤ 1,5 | Näherung δ = 0,05 d mit Warnung (im Datensatz nie erreicht) |
| Schlupf Liu (2005) | 0,008–0,7 m/s (Gas), 0,008–0,5 m/s (Flüssigkeit), d 0,9–3 mm | Warnung (nur Hinweis, keine Rechengröße) |
| Henry-Konstante | CO2, O2, N2, Luft in Wasser | Abbruch mit Meldung |
| CO2-Diffusion | Wasser | – |
| Literaturmodelle | siehe [Kapitel 8](08_literaturvergleich.md); fast alle werden hier extrapoliert | – |

## 7.2 Bekannte Einschränkungen

1. **Isotherm, Stoffdaten am Auslass:**
   - T und p am Auslass gelten für den ganzen Kanal.
   - Bei Temperaturänderungen über ca. 5 K entlang des Kanals wäre eine
     lokale Auswertung nötig.
2. **Konstantes Flüssigkeitsvolumen:**
   - V_L wird am Einlass bestimmt.
   - Änderungen der Sluglänge entlang z gehen nicht in C_L ein.
3. **Kappen und Zwickel im quadratischen Kanal:**
   - Das Zwickelvolumen in den Ecken wird nur im runden Kanal (als halbes
     Kappenvolumen) zum Flüssigkeitsvolumen gezählt.
   - Die Kappen werden in beiden Geometrien als Halbellipsoide genähert.
   - Im Praktikum hatte der Wechsel von Würfel- auf Ellipsoidnäherung im
     Glaskanal bis zu 26 % Einfluss auf einzelne kLa-Werte (Median 1,8 %).
4. **Druckkalibrierung der runden Kanäle:**
   - Kein veröffentlichtes Druckmodell (Bretherton, Kreutzer 2005,
     Warnier 2010) gibt alle drei runden Kanäle des Praktikums ohne
     kanalspezifische Anpassung mit weniger als 70 % MAPE wieder.
   - Für PVC sind deshalb kalibrierte c-Werte hinterlegt.
   - Der Kanal PVC 1500/1150 ist als nicht verwendbar markiert
     (c zwischen −7,6 und +16); dort gilt c = 0,465.
   - Mehr dazu in [Kapitel 9](09_druckkalibrierung.md).
5. **Eckig und rund im Vergleich:**
   - Im Glaskanal (eckig) folgen die Messwerte dem Trend der
     Literaturmodelle, besonders Yue 2007. Die Absolutwerte weichen aber
     teils um ein Mehrfaches ab.
   - Die runden Kanäle zeigen kaum einen Trend.
   - Ursachen sind vermutlich Druckmodell und Materialeffekte; Details im
     Archiv (`docs/FEHLERANALYSE_ECKIG_VS_RUND.md`).
6. **Unsicherheit `u_rel_kLa`:**
   - Bei der Rekonstruktion von C_L für die Fehlerfortpflanzung wird
     C*(Einlass) statt C*(z) verwendet.
   - Das betrifft nur die Spalte `u_rel_kLa`, nicht kLa selbst und nicht
     die aktive Zone.
7. **Aktive Zone als ein Bereich:**
   - kLa_log_mean nutzt den ersten und den letzten aktiven Punkt.
   - Ist die aktive Zone unterbrochen, zählen die inaktiven Abschnitte
     dazwischen zur Verweilzeit mit.
   - Im Datensatz tritt das nicht auf.
8. **Literaturmodelle bei 25 °C:**
   - Ca, Re und Sc der Literaturmodelle werden mit festen Stoffwerten für
     etwa 25 °C berechnet.
   - Die Hauptauswertung nutzt dagegen die gemessene Temperatur.
   - Bei 20–25 °C beträgt der Unterschied wenige Prozent.
9. **Zwischenspeicher der Stoffdaten:**
   - Stoffdaten werden mit auf 0,1 K gerundeter Temperatur
     zwischengespeichert.
   - Betriebspunkte mit fast gleicher Temperatur erhalten identische Werte.
     Die Abweichung ist vernachlässigbar, macht das Ergebnis aber von der
     Reihenfolge der Auswertung abhängig.
   - Die Referenzergebnisse gelten für die Auswertung aller Kanäle in
     alphabetischer Reihenfolge.
10. **3D-Flächen:**
    - Die kubische Interpolation kann bei wenigen, unregelmäßig verteilten
      Punkten über- oder unterschwingen.
    - Für quantitative Aussagen gelten die Messpunkte.

## 7.3 Was die Sensitivitätsanalysen gezeigt haben

Im Praktikum wurden alle festen Schwellwerte variiert (Datensatz: 5 Kanäle,
55 Betriebspunkte). Wirkung auf kLa_log_mean:

| Größe | Variation | Effekt |
|---|---|---|
| Startwert λ_0 des Fits | 0,01–0,2 m | keiner (bit-identisch) |
| Ortsschritt dz | 0,25–2 mm | im Prozentbereich, unter der Messunsicherheit |
| Sättigungsgrenze | 0,99–0,999 | keiner |
| Grenze aktive Zone u_rel(ΔC) | 0,3–0,7 | keiner |
| Einbruchfilter auf dn/dz | Fenster und Schwelle variiert | keiner |
| Deckel für U_fit | – | nie aktiv |
| Offset-Grenze | – | nie erreicht |
| Ersatzmodell der Kalibrierung | Linear statt Polynomial | ≤ 3,6 % in einem Betriebspunkt |
| Filmdickenmodell | δ/d 0,03–0,10, Aussillous statt Bretherton | keiner (Ersatzwert nie aktiv) |

Die Ergebnisse hängen damit praktisch nicht von den numerischen
Einstellungen ab. Maßgeblich sind die Messdaten, das Druckmodell und die
Ausschlussentscheidungen.

## 7.4 Offene Punkte

- **Druckmodell runde Kanäle:** Eine physikalisch begründete Alternative zur
  Kalibrierung fehlt, siehe 7.2 Nr. 4.
- **Kalibrierung:** Die Ersatzmodelle werden mit nur 5–8 Punkten angepasst.
  `auto` wählt das größte R²; AIC/BIC empfehlen für PVC 1000/800 das lineare
  Modell. Im Datensatz wirkt sich das nicht aus, weil alle Betriebspunkte
  innerhalb der kalibrierten Punktwolke liegen.
- **Rechteckige, nicht quadratische Kanäle:** Geometrie, Druck- und
  Filmmodell müssten erweitert werden.
- **Andere Flüssigkeiten:** Henry-Konstante und Diffusionskoeffizient müssten
  ergänzt werden.
