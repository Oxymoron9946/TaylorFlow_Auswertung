# 8 Grenzen

## 8.1 Gültigkeitsbereiche der Modelle

| Modell | Bereich | Verhalten außerhalb |
|---|---|---|
| Bretherton-Druckverlust (rund) | Ca ≤ 0,005 | Warnung im Protokoll, Rechnung läuft weiter |
| Kurimoto-Druckverlust (quadratisch) | 0,00159 ≤ Ca ≤ 0,0989; 0,0817 ≤ We ≤ 25,4; 8,33 ≤ Re ≤ 791; L_B/d ≥ ca. 2,3 | Warnung, Rechnung läuft weiter |
| Filmdicke rund | Ca ≤ 1,5 | Näherung δ = 0,05 d mit Warnung |
| Schlupf Liu (2005) | 0,008–0,7 m/s (Gas), 0,008–0,5 m/s (Flüssigkeit), d 0,9–3 mm | Warnung (nur Hinweis, keine Rechengröße) |
| Henry-Konstante | CO2, O2, N2, Luft in Wasser | Abbruch mit Meldung |
| CO2-Diffusion | Wasser | – |
| Literaturmodelle | siehe Kapitel 9.2; die mitgelieferten Kanäle liegen bei fast allen Modellen außerhalb des Originalbereichs | – |

Im mitgelieferten Glaskanal unterschreiten einige Betriebspunkte bei
kleinem u_G das Kurimoto-Kriterium L_B/d leicht.

## 8.2 Bekannte Einschränkungen

1. **Isotherm, Stoffdaten am Auslass:**
   - T und p am Auslass gelten für den ganzen Kanal.
   - Bei Temperaturänderungen über ca. 5 K entlang des Kanals wäre eine
     abschnittsweise Auswertung nötig.
2. **Konstantes Flüssigkeitsvolumen:**
   - V_L wird am Einlass bestimmt.
   - Änderungen der Sluglänge entlang z gehen nicht in C_L ein.
3. **Kappen und Zwickel im quadratischen Kanal:**
   - Das Zwickelvolumen in den Ecken wird nur im runden Kanal (als halbes
     Kappenvolumen) zum Flüssigkeitsvolumen gezählt.
   - Die Kappen werden in beiden Geometrien als Halbellipsoide genähert.
   - Eine Würfel- statt Ellipsoidnäherung der Kappen ändert im Glaskanal
     einzelne kLa-Werte um bis zu 26 % (Median 1,8 %).
4. **Druckmodell der runden Kanäle:**
   - Kein veröffentlichtes Druckmodell (Bretherton, Kreutzer 2005,
     Warnier 2010) gibt alle drei mitgelieferten runden Kanäle ohne
     kanalspezifische Anpassung mit weniger als 70 % mittlerer Abweichung
     wieder.
   - Für PVC sind deshalb kalibrierte c-Werte hinterlegt (Kapitel 10).
   - Der Kanal PVC 1500/1150 ist als nicht verwendbar markiert (c zwischen
     −7,6 und +16); dort gilt c = 0,465.
5. **Eckige und runde Kanäle im Vergleich:**
   - Im Glaskanal (eckig) folgen die Messwerte dem Trend der
     Literaturmodelle, besonders Yue 2007; die Absolutwerte weichen teils
     um ein Mehrfaches ab.
   - Die runden Kanäle zeigen kaum einen Trend. Wahrscheinliche Ursachen
     sind das Druckmodell und Materialeffekte.
6. **Aktive Zone als ein Bereich:**
   - kLa_log_mean nutzt den ersten und den letzten aktiven Punkt.
   - Wäre die aktive Zone unterbrochen, zählten die Abschnitte dazwischen
     zur Verweilzeit mit. In den mitgelieferten Messreihen kommt das nicht
     vor.
7. **Literaturmodelle bei 25 °C:**
   - Ca, Re und Sc der Literaturmodelle werden mit festen Stoffwerten für
     etwa 25 °C berechnet.
   - Die übrige Auswertung nutzt die gemessene Temperatur.
   - Bei 20–25 °C beträgt der Unterschied wenige Prozent.
8. **Zwischenspeicher der Stoffdaten:**
   - Stoffdaten werden mit auf 0,1 K gerundeter Temperatur
     zwischengespeichert.
   - Betriebspunkte mit fast gleicher Temperatur erhalten identische Werte.
     Das Ergebnis eines Betriebspunkts hängt damit geringfügig davon ab,
     welche Punkte im selben Lauf vorher gerechnet wurden: Wird ein
     Betriebspunkt zusätzlich ausgewertet oder ausgeschlossen, ändern sich
     andere kLa_log_mean-Werte um höchstens etwa 0,002 %.
   - Die Referenzergebnisse gelten für die Auswertung aller mitgelieferten
     Kanäle in alphabetischer Reihenfolge.
9. **3D-Flächen:**
   - Die kubische Interpolation kann bei wenigen, unregelmäßig verteilten
     Punkten über- oder unterschwingen.
   - Für quantitative Aussagen gelten die Messpunkte.
10. **Mehrere Aufnahmen je Bin:** Enthält eine Messdatei mehrere Zeilen für
    dieselbe Kamera und dasselbe Bin, wird die kleinste Blasenlänge
    verwendet (Kapitel 2.3).

## 8.3 Empfindlichkeit gegenüber den Einstellungen

Alle festen Schwellwerte wurden mit den mitgelieferten Messreihen variiert
(5 Kanäle, 55 Betriebspunkte). Wirkung auf kLa_log_mean:

| Größe | Variation | Effekt |
|---|---|---|
| Startwert λ_0 des Fits | 0,01–0,2 m | keiner (identische Ergebnisse) |
| Ortsschritt dz | 0,25–2 mm | im Prozentbereich, unter der Messunsicherheit |
| Sättigungsgrenze | 0,99–0,999 | keiner |
| Grenze aktive Zone u_rel(ΔC) | 0,3–0,7 | keiner |
| Deckel für U_fit | – | nie aktiv |
| Offset-Grenze | – | nie erreicht |
| Ersatzmodell der Kalibrierung | Linear statt Polynomial | ≤ 3,6 % in einem Betriebspunkt |
| Filmdickenmodell | δ/d 0,03–0,10, Aussillous statt Bretherton | keiner (Ersatzwert nie aktiv) |

Die Ergebnisse hängen damit praktisch nicht von den numerischen
Einstellungen ab. Maßgeblich sind die Messdaten, das Druckmodell und die
Ausschlussregeln.

## 8.4 Offene Punkte

- **Druckmodell runde Kanäle:** Eine physikalisch begründete Alternative
  zur Kalibrierung fehlt (8.2 Nr. 4).
- **Kalibrierung:** Die Ersatzmodelle werden mit nur 5–8 Punkten angepasst
  (Kapitel 10.5).
- **Rechteckige, nicht quadratische Kanäle:** Geometrie, Druck- und
  Filmmodell müssten erweitert werden.
- **Andere Flüssigkeiten:** Henry-Konstante und Diffusionskoeffizient
  müssten ergänzt werden (Kapitel 12.3).
