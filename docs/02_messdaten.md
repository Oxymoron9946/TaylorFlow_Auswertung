# 2 Messdaten

## 2.1 Herkunft

Eingangsdaten sind die Ergebnisdateien der Videoauswertung (siehe deren
Handbuch, Kapitel 4). Je Kanal und Messart gibt es eine Datei, in der jede
Zeile ein Positions-Bin einer Kameraposition bei einem Betriebspunkt ist:

```
Videoauswertung\output\
  Output_MassTransfer\
    Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv     →  auswertung.py
  Output_PressureCalibration\
    Auswertung_Druck_PVC_R_1000um_72cm_0molCO2_600um.csv      →  kalibrierung.py
```

Die Videoauswertung erzeugt Dateinamen und Spalten bereits im passenden
Format. Die Dateien werden unverändert verwendet und beim Start im
Auswahlfenster gewählt (Kapitel 3).

## 2.2 Dateinamen

Alle Angaben zum Versuchsaufbau werden **ausschließlich aus dem Dateinamen**
gelesen; gleichnamige Spalten in der Datei (Material, Kanal_um, …) werden
nicht verwendet.

```
Auswertung_<Messart>_<Material>_<Form>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um.csv
```

| Feld | Bedeutung | Beispiel |
|---|---|---|
| Messart | `Masse` = Stoffübergangsmessung, `Druck` = Messung ohne CO2 für die Druckkalibrierung | `Masse` |
| Material | Kanalmaterial, frei wählbar (Buchstaben und Ziffern) | `PVC`, `Glas`, `PTFE` |
| Form | `R` oder `Rund` = runder Kanal; `Q` oder `Eckig` = quadratischer Kanal | `R` |
| D | Kanaldurchmesser bzw. Seitenlänge [µm] | `1000` |
| L | Reaktorlänge [cm]; legt die Länge des Rechengitters fest | `72` |
| X | CO2-Anteil im Eingangsgas [mol-%] | `20` |
| Gas | Gasname; Henry-Konstanten sind für CO2, O2, N2 und Luft hinterlegt | `CO2` |
| Nadel | Innendurchmesser der Gaseinlassnadel [µm] | `600` |

Aus dem Dateinamen entsteht der **Kanalname**. Unter ihm stehen Ergebnisse,
Plots und Ausschlussregeln:

```
Datei:      Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv
Kanalname:  PVC_Rund_1000um_72cm_20molCO2_600um
```

Zwei Messreihen mit demselben Kanalnamen überschreiben sich gegenseitig.
Eine Wiederholungsmessung am selben Aufbau bekommt deshalb ein eigenes
Material-Kürzel, z. B. `PVC2`.

Für die Druckkalibrierung gilt ein kürzerer **Kalibrierschlüssel** ohne
Länge und CO2-Anteil, z. B. `PVC_circular_1000um_600um`. Eine Druckmessung
gilt damit für alle Stoffübergangsmessungen am selben Kanal mit derselben
Nadel.

## 2.3 Dateiinhalt

Format: Semikolon als Trennzeichen, Dezimalpunkt oder Dezimalkomma,
Kodierung UTF-8.

**Pflichtspalten**

| Spalte | Einheit | Bedeutung |
|---|---|---|
| `GasVelocity` | m/s | Leerrohrgeschwindigkeit Gas u_G (Sollwert) |
| `LiquidVelocity` | m/s | Leerrohrgeschwindigkeit Flüssigkeit u_L |
| `CameraPosition` | – | Nummer der Kameraposition (1 = am Einlass) |
| `BinCenter_mm` | mm | Position des Bins im Kanal, gemessen ab Einlass |
| `mean_BubbleLength_mm` | mm | mittlere Blasenlänge im Bin |
| `mean_UnitCellLength_mm` | mm | mittlere Länge der Einheitszelle (Blase + Slug) |
| `mean_Speed_m_s` | m/s | mittlere Blasengeschwindigkeit |
| `Temperatur_C` | °C | Temperatur (je Betriebspunkt gemittelt) |
| `Druck_Pa_Auslass` | Pa | Absolutdruck am Auslass |

**Zusätzlich verwendet, falls vorhanden**

| Spalte | Verwendung |
|---|---|
| `std_BubbleLength_mm` | Messunsicherheit im Blasenlängen-Fit und im Kamerafilter |
| `GroupCount` bzw. `numel_BubbleLength_mm` | Anzahl Messpunkte im Bin; für den Standardfehler und den Kamerafilter |

Fehlt die Anzahl je Bin, entfällt der Kamerafilter (2.5), und der Fit
gewichtet mit der Standardabweichung statt mit dem Standardfehler.

**Mehrere Aufnahmen oder Sensitivitäten.** Enthält eine Datei für dieselbe
Kamera und dasselbe Bin mehrere Zeilen, z. B. aus mehreren Aufnahmen oder
einem Sensitivitäts-Sweep der Videoauswertung, wird je Kamera und Bin die
Zeile mit der **kleinsten Blasenlänge** verwendet. Für eine nachvollziehbare
Auswertung sollte die Datei je Betriebspunkt nur eine Sensitivität
enthalten.

## 2.4 Ausschlussregeln

Messpunkte oder ganze Betriebspunkte, die nicht ausgewertet werden sollen,
stehen in `config/ausschluesse.yaml`, gegliedert nach Kanalname. Jede Regel
nennt ihren Grund. Es gibt drei Arten:

```yaml
PVC_Rund_1000um_72cm_20molCO2_800um:
  messpunkte_entfernen:          # Zeilen der Messdatei vor der Auswertung entfernen
    - GasVelocity: 0.134
      LiquidVelocity: 0.25
      grund: Absorption vor dem ersten Messpunkt abgeschlossen
    - GasVelocity: 0.07
      LiquidVelocity: 0.111
      CameraPosition: 3          # nur Kamera 3 dieses Betriebspunkts
      grund: Kamera 3 unscharf
  betriebspunkte_ueberspringen:  # Betriebspunkt erscheint in keiner Ergebnisdatei
    - LiquidVelocity: 0.056      # alle Betriebspunkte mit u_L = 0,056 m/s
      grund: Pumpe instabil
  kla_ungueltig:                 # wird ausgewertet, aber kLa_log_mean bleibt leer
    Gas_0_07_Liq_0_111: "Absorption kaum auswertbar"
```

| Art | Felder | Wirkung |
|---|---|---|
| `messpunkte_entfernen` | `GasVelocity`, `LiquidVelocity`, `CameraPosition`, `BinCenter_mm` (Toleranz 0,1 mm); alle angegebenen müssen zutreffen | Zeilen fallen vor der Auswertung weg |
| `betriebspunkte_ueberspringen` | `GasVelocity` und/oder `LiquidVelocity`; ein fehlendes Feld bedeutet „alle Werte“ | Betriebspunkt wird nicht ausgewertet |
| `kla_ungueltig` | Name des Betriebspunkts wie in Spalte `Config` | kLa_log_mean leer, `manual_exclude = True` mit Grund; Profile und Blasenlängen-Fit bleiben verfügbar, 3D-Flächen und Modellvergleiche lassen den Punkt weg |

Die mitgelieferte Datei enthält die Ausschlüsse der mitgelieferten
Messreihen mit Begründung. Nach einer Änderung `auswertung.py` erneut
ausführen.

## 2.5 Automatischer Kamerafilter

Vor der Auswertung werden unzuverlässige Kamerapositionen entfernt (nur
Messart `Masse`). Ein Bin ist gültig, wenn alle drei Bedingungen erfüllt
sind:

- relativer Standardfehler der Blasenlänge ≤ 5 %
- mindestens 50 Messpunkte im Bin
- Variationskoeffizient ≤ 50 %

Eine Kamera eines Betriebspunkts bleibt, wenn mindestens 75 % ihrer Bins und
mindestens 3 Bins gültig sind. Betriebspunkte mit nur noch einer Kamera
entfallen. Die Konsole meldet, wie viele Bins und Kameras verworfen wurden.
Die Grenzwerte stehen in `config.PARAMETER` (`kamerafilter_*`, Kapitel 5).

## 2.6 Neue Messreihe auswerten

1. In der Videoauswertung den Batch für den Messordner laufen lassen. Die
   Datei `Auswertung_Masse_….csv` entsteht in `output/Output_MassTransfer/`.
2. `python auswertung.py` starten und die Datei im Auswahlfenster wählen.
3. Ergebnisse prüfen (Kapitel 3.4): Warnungsprotokoll, Blasenlängen-Fits,
   Kennzahlen-Übersicht.
4. Unbrauchbare Messpunkte oder Betriebspunkte in
   `config/ausschluesse.yaml` eintragen (2.4) und erneut auswerten.
5. **Runder Kanal:** Ohne Eintrag in der Kalibrier-Datenbank rechnet das
   Druckmodell mit dem Theoriewert c = 0,465; die Konsole meldet dann „nicht
   kalibriert“. Mit einer Druckmessung kann der Kanal kalibriert werden
   (Kapitel 10). **Quadratischer Kanal:** keine Kalibrierung nötig.

**Andere Abmessungen** (Durchmesser, Länge, CO2-Anteil): Es ist nichts
weiter anzupassen; alles kommt aus dem Dateinamen.

**Andere Flüssigkeit als Wasser** oder **rechteckige, nicht quadratische
Kanäle** werden nicht unterstützt (Kapitel 8 und 12).
