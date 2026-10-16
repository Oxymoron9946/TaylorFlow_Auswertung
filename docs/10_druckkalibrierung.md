# 10 Druckkalibrierung

> **Status:** Das Verfahren ist vollständig enthalten, aber noch nicht
> abschließend validiert und wird derzeit nicht routinemäßig genutzt. Die
> Auswertung liest nur die vorhandene Datenbank
> `data/calibrated_c_database.json`. `kalibrierung.py` verändert diese Datei
> nur, wenn es ausdrücklich eingestellt ist.

## 10.1 Wozu

Im runden Kanal wird der Druckverlust mit dem Bretherton-Modell berechnet
(Kapitel 7.4). Es enthält einen Faktor c mit dem Theoriewert 0,465. Mit
diesem Wert passt das berechnete Druckprofil nicht zu allen Kanälen, und
kein anderes veröffentlichtes Modell passt besser (Kapitel 8.2). c wird
deshalb je Kanal aus Messungen ohne CO2 bestimmt; dort ändert sich die
Blasenlänge nur durch den Druck.

Für quadratische Kanäle (Kurimoto-Modell) wird nicht kalibriert.

## 10.2 Verfahren

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

Ausgegeben werden je Modell R² und AIC (kleiner = besser; bestraft
zusätzliche Parameter).

## 10.3 Nutzung in der Auswertung

Für einen runden Kanal wird der Eintrag mit dem Kalibrierschlüssel gesucht,
z. B. `PVC_circular_1000um_600um` (Kapitel 2.2). Dann gilt:

| Lage | verwendetes c |
|---|---|
| innerhalb der kalibrierten Betriebspunkte | lineare Interpolation |
| außerhalb | gespeichertes Ersatzmodell (`fallback_model`) |
| kein Eintrag, `"USE": false` oder weniger als 4 Punkte | Theoriewert 0,465 (Meldung in der Konsole) |

Das Ergebnis ist mindestens 0,001.

**Inhalt der Datenbank:**

| Schlüssel | Punkte | c | Ersatzmodell | verwendet |
|---|---|---|---|---|
| `PVC_circular_1000um_600um` | 5 | 0,31–1,33 | Power-Law (R² 0,91) | ja |
| `PVC_circular_1000um_800um` | 8 | 0,05–0,70 | Polynomial (R² 0,58) | ja |
| `PVC_circular_1500um_1150um` | 8 | −7,6 bis +16 | Polynomial | nein (`USE: false`) |
| `Glas_rectangular_1000um_600um` | 8 | – | – | nein; eckig, Kurimoto |
| PTFE | – | – | – | kein Eintrag, c = 0,465 |

Ein Eintrag lässt sich von Hand abschalten:

```json
"PVC_circular_1500um_1150um": {
    "USE": false,
    "NOTE": "c_calib zwischen -7.6 und +16, vermutlich Messfehler",
    ...
}
```

## 10.4 Neu kalibrieren

1. Mit der Videoauswertung die Druckmessung auswerten; die Datei
   `Auswertung_Druck_….csv` entsteht in `output/Output_PressureCalibration/`.
   Material, Form, D und Nadel müssen zur Stoffübergangsmessung passen.
2. In `config.py`, Abschnitt `KALIBRIERUNG`:

   | Eintrag | Standard | Bedeutung |
   |---|---|---|
   | `messdateien` | `"dialog"` | `"dialog"` = Auswahlfenster, `"alle"` = alle `Auswertung_Druck_*.csv` in `ROHDATEN_ORDNER`, oder Liste von Pfaden |
   | `dialog_ordner` | `ROHDATEN_ORDNER` | Startordner des Auswahlfensters, z. B. `Output_PressureCalibration` der Videoauswertung |
   | `ersatzmodell` | `"auto"` | `"auto"` (größtes R²) oder `"Linear"`, `"Polynomial"`, `"Power-Law"` |
   | `datenbank_schreiben` | `False` | zuerst `False` lassen |

3. `python kalibrierung.py` ausführen und die Datei(en) auswählen.
4. Ergebnisse in `ergebnisse/kalibrierung/` prüfen:
   - `<Schlüssel>_c_werte.csv`: c je Betriebspunkt
   - `<Schlüssel>_c_flaeche.png`: c über u_G und u_L

   Plausibel sind Werte in der Größenordnung des Theoriewerts (0,1–2).
   Negative oder stark streuende Werte deuten auf ein Problem in der
   Druckmessung oder den Fits hin.
5. Erst dann `datenbank_schreiben = True` setzen und erneut ausführen.
   Vorhandene Felder `USE` und `NOTE` bleiben erhalten. Danach
   `auswertung.py` für den Kanal erneut laufen lassen.

Eine Neukalibrierung der mitgelieferten Druckdaten reproduziert die
gespeicherten c-Werte auf etwa 10⁻⁴ genau und wählt dieselben
Ersatzmodelle.

## 10.5 Offene Fragen

- **Annahme Volumen proportional zur Länge:** Kappen werden vernachlässigt,
  die Filmdicke gilt als konstant. Bei kurzen Blasen ist die Annahme grob.
- **Anpassung mit wenigen Punkten:** Fünf bis acht Punkte je Kanal sind
  wenig, um drei bis vier Parameter anzupassen. `auto` wählt nach R² und
  bevorzugt damit das Polynom; nach AIC wäre für PVC 1000/800 das lineare
  Modell zu wählen. Für Betriebspunkte innerhalb der kalibrierten Punkte
  spielt das keine Rolle (Interpolation).
- **PVC 1500/1150:** Die stark streuenden c-Werte sind nicht erklärt.
- **Messabweichung der Blasenlänge:** Sie geht in der Kalibrierung nur über
  die Standardabweichung ein, nicht über Standardfehler und systematischen
  Anteil wie im Blasenlängen-Fit der Stoffübergangsmessung.
