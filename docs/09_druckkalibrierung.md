# 9 Druckkalibrierung

> **Status:** Übernommen aus dem Forschungspraktikum, aber noch nicht
> abschließend validiert. Die Auswertung nutzt nur die vorhandene Datenbank
> `data/calibrated_c_database.json`. `kalibrierung.py` verändert diese Datei
> nur, wenn es ausdrücklich eingestellt ist.

## 9.1 Wozu

Im runden Kanal wird der Druckverlust mit dem Bretherton-Modell berechnet
([6.4](06_methodik.md)). Es enthält einen Faktor c, Theoriewert 0,465. Im
Praktikum hat sich gezeigt:
- Mit dem Theoriewert passt das berechnete Druckprofil nicht zu allen
  Kanälen.
- Kein anderes veröffentlichtes Modell passt besser ([7.2](07_grenzen.md)).

c wird deshalb je Kanal aus Messungen ohne CO2 bestimmt; dann ändert sich
die Blasenlänge nur durch den Druck.

Für quadratische Kanäle (Kurimoto) wird nicht kalibriert.

## 9.2 Verfahren

Für jeden Betriebspunkt einer Datei `Auswertung_Druck_…_0molCO2_….csv`:

1. **Fits:** Blasenlänge (gewichtet), Sluglänge und Geschwindigkeit linear
   über z.
2. **Realer Druckverlust** aus der Blasenexpansion (ideales Gas, Volumen
   proportional zur Länge):

   $$p_{tr,ein} = p_{tr,aus}\,\frac{L_B(z_{Ende})}{L_B(0)}, \qquad \Delta p_{real} = p_{tr,ein} + p_v - p_{aus}$$

3. **Zerlegung des Modells:** Das Bretherton-Modell ist linear in c:
   - $\mathrm{d}p/\mathrm{d}z = \text{Basis} + c \cdot \text{Zusatz}$
   - Basis = Modell mit c = 0
   - Zusatz = Modell(c = 1) − Modell(c = 0)
   - Beide Anteile werden über den Kanal integriert.
4. **Ergebnis:**
   $c = (\Delta p_{real} - \Delta p_{Basis}) / \Delta p_{Zusatz}$

Über alle Betriebspunkte werden drei **Ersatzmodelle** für c(u_G, u_L)
angepasst:

| Modell | Form |
|---|---|
| Linear | $a\,u_G + b\,u_L + c_0$ |
| Polynomial | $a\,u_G + b\,u_L + c_1\,u_G u_L + c_0$ |
| Power-Law | $a\,u_G^{b}\,u_L^{c_1}$ |

Ausgegeben werden je Modell R² und AIC (kleiner = besser, bestraft
zusätzliche Parameter).

## 9.3 Nutzung in der Auswertung

Für einen runden Kanal wird der Eintrag mit dem Kalibrierschlüssel gesucht,
z. B. `PVC_circular_1000um_600um` ([2.1](02_messdaten.md)). Dann gilt:

| Lage | verwendetes c |
|---|---|
| innerhalb der kalibrierten Betriebspunkte | lineare Interpolation |
| außerhalb | gespeichertes Ersatzmodell (`fallback_model`) |
| kein Eintrag, `"USE": false` oder < 4 Punkte | Theoriewert 0,465 (Meldung in der Konsole) |

Das Ergebnis ist mindestens 0,001.

**Stand der Datenbank:**

| Schlüssel | Punkte | c | Ersatzmodell | Verwendet |
|---|---|---|---|---|
| `PVC_circular_1000um_600um` | 5 | 0,31–1,33 | Power-Law (R² 0,91) | ja |
| `PVC_circular_1000um_800um` | 8 | 0,05–0,70 | Polynomial (R² 0,58) | ja |
| `PVC_circular_1500um_1150um` | 8 | −7,6 bis +16 | Polynomial | nein (`USE: false`) |
| `Glas_rectangular_1000um_600um` | 8 | – | – | nein; eckig, Kurimoto |
| PTFE | – | – | – | kein Eintrag → 0,465 |

Ein Eintrag lässt sich von Hand abschalten:

```json
"PVC_circular_1500um_1150um": {
    "USE": false,
    "NOTE": "c_calib zwischen -7.6 und +16, vermutlich Messfehler",
    ...
}
```

## 9.4 Neu kalibrieren

1. `Auswertung_Druck_….csv` in `data/raw/` legen. Material, Form, D und
   Nadel müssen zur Stoffübergangsmessung passen.
2. In `config.py`, Abschnitt `KALIBRIERUNG`:
   - `kanaele`: `None` = alle Druckdateien, sonst Liste von Schlüsseln
   - `ersatzmodell`: `"auto"` (größtes R², Verhalten des Praktikums) oder
     ein fester Name
   - `datenbank_schreiben`: zuerst `False`
3. `python kalibrierung.py` ausführen.
4. Ergebnisse in `ergebnisse/kalibrierung/` prüfen:
   - `<Schlüssel>_c_werte.csv`: c je Betriebspunkt
   - `<Schlüssel>_c_flaeche.png`: c über u_G und u_L

   Plausibel sind Werte in der Größenordnung des Theoriewerts (0,1–2).
   Negative oder stark streuende Werte deuten auf ein Problem in der
   Druckmessung oder den Fits hin.
5. Erst dann `datenbank_schreiben = True` setzen und erneut ausführen.
   - Vorhandene Felder `USE` und `NOTE` bleiben erhalten.
   - Danach `auswertung.py` erneut laufen lassen.

Eine Neukalibrierung der mitgelieferten Druckdaten reproduziert die
gespeicherten c-Werte auf etwa 10⁻⁴ genau (abweichende Stoffdatenversion)
und wählt dieselben Ersatzmodelle.

## 9.5 Offene Fragen

- **Annahme Volumen proportional zur Länge:**
  - Die Kappen werden vernachlässigt, die Filmdicke als konstant angesehen.
  - Bei kurzen Blasen ist die Annahme grob.
- **Anpassung mit wenigen Punkten:**
  - Fünf bis acht Punkte je Kanal sind wenig, um drei bis vier Parameter
    anzupassen.
  - `auto` wählt nach R² und bevorzugt damit das Polynom.
  - Nach AIC wäre für PVC 1000/800 das lineare Modell zu wählen. Für die
    vorhandenen Betriebspunkte spielt das keine Rolle (Interpolation).
- **Unklare Ursache bei PVC 1500/1150:** Die stark streuenden c-Werte sind
  nicht erklärt.
- **Messabweichung der Blasenlänge:** Sie geht in der Kalibrierung nur über
  die Standardabweichung ein, nicht über Standardfehler und systematischen
  Anteil wie im Stoffübergangs-Fit.
