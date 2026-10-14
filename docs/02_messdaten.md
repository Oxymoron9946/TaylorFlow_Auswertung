# 2 Messdaten und neue Messreihen

## 2.1 Dateinamen

Jede Messreihe ist eine CSV-Datei in `data/raw/`. Alle Angaben zum Versuchsaufbau
werden **ausschließlich aus dem Dateinamen** gelesen; gleichnamige Spalten in der
Datei (Material, Kanal_um, …) werden ignoriert.

```
Auswertung_<Messart>_<Material>_<Form>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um.csv
```

| Feld | Bedeutung | Beispiel |
|---|---|---|
| Messart | `Masse` = Stoffübergangsmessung, `Druck` = Messung ohne CO2 für die Druckkalibrierung | `Masse` |
| Material | Kanalmaterial, frei wählbar (Buchstaben/Ziffern) | `PVC`, `Glas`, `PTFE` |
| Form | `R` oder `Rund` = runder Kanal; `Q` oder `Eckig` = quadratischer Kanal | `R` |
| D | Kanaldurchmesser bzw. Seitenlänge [µm] | `1000` |
| L | Reaktorlänge [cm], legt das Integrationsgitter fest | `72` |
| X | CO2-Anteil im Eingangsgas [mol-%] | `20` |
| Gas | Gasname; Henry-Konstanten sind für CO2, O2, N2 und Luft hinterlegt | `CO2` |
| Nadel | Innendurchmesser der Gaseinlassnadel [µm] (nur zur Unterscheidung) | `600` |

Aus dem Dateinamen entsteht der **Kanalname**, unter dem alle Ergebnisse,
Ausschlussregeln und Plots laufen:

```
Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv  →  PVC_Rund_1000um_72cm_20molCO2_600um
```

Zwei Messreihen dürfen nicht denselben Kanalnamen haben; sonst überschreibt die
zweite die Ergebnisse der ersten. Eine Wiederholungsmessung am selben Aufbau
bekommt deshalb z. B. ein anderes Material-Kürzel (`PVC2`).

Für die Druckkalibrierung gilt ein kürzerer **Kalibrierschlüssel** ohne Länge und
CO2-Anteil, z. B. `PVC_circular_1000um_600um`. Eine Druckmessung gilt damit für
alle Stoffübergangsmessungen am selben Kanal mit derselben Nadel.

## 2.2 Dateiinhalt

Format: Semikolon als Trennzeichen, Dezimalpunkt oder Dezimalkomma, Kodierung
UTF-8. Eine Zeile je Betriebspunkt, Kamera und Positions-Bin. Das ist das
Ausgabeformat der MATLAB-Bildauswertung.

**Pflichtspalten:**

| Spalte | Einheit | Bedeutung |
|---|---|---|
| `GasVelocity` | m/s | Leerrohrgeschwindigkeit Gas (Sollwert MFC) |
| `LiquidVelocity` | m/s | Leerrohrgeschwindigkeit Flüssigkeit |
| `CameraPosition` | – | Nummer der Kameraposition (1 = Einlass) |
| `BinCenter_mm` | mm | Position des Bins im Kanal, gemessen ab Einlass |
| `mean_BubbleLength_mm` | mm | mittlere Blasenlänge im Bin |
| `mean_UnitCellLength_mm` | mm | mittlere Länge der Einheitszelle (Blase + Slug) |
| `mean_Speed_m_s` | m/s | mittlere Blasengeschwindigkeit |
| `Temperatur_C` | °C | Temperatur (Mittel je Betriebspunkt wird verwendet) |
| `Druck_Pa_Auslass` | Pa | Absolutdruck am Auslass |

**Zusätzlich ausgewertet, falls vorhanden:**

| Spalte | Verwendung |
|---|---|
| `std_BubbleLength_mm` | Messunsicherheit für den Blasenfit und den Kamerafilter |
| `numel_BubbleLength_mm` | Anzahl Blasen im Bin, für den Standardfehler und den Kamerafilter |

Fehlt `numel_BubbleLength_mm`, entfällt der automatische Kamerafilter, und als
Messunsicherheit wird die Standardabweichung statt des Standardfehlers verwendet.

## 2.3 Eine neue Messreihe auswerten

1. Datei nach dem Schema benennen und in `data/raw/` legen.
2. `python auswertung.py` starten. Ohne weitere Angabe werden alle Messreihen
   ausgewertet; nur die neue mit
   `KANAELE = ["<Kanalname>"]` in `config.py`.
3. Ergebnisse prüfen:
   - `ergebnisse/Modell_Gueltigkeitswarnungen.txt` lesen, siehe
     [Kapitel 4](04_auswertung.md#warnungsprotokoll).
   - Für jeden Betriebspunkt den Blasenlängen-Fit ansehen
     (`plots/blasenlaenge_*.png`): Folgt die Fitkurve den Messpunkten aller
     Kameras? Liegen die Kamera-Offsets im Bereich weniger µm?
   - Die Kennzahlen-Übersicht (`plots/heatmaps.png`) auf Ausreißer prüfen.
4. Unbrauchbare Betriebspunkte in `config/ausschluesse.yaml` eintragen
   (Abschnitt 2.4) und erneut auswerten.
5. **Runder Kanal:**
   - Ohne Eintrag in der Kalibrier-Datenbank rechnet das Druckmodell mit dem
     Theoriewert c = 0,465. Im Protokoll steht dann „nicht kalibriert“.
   - Mit einer Druckmessung (`Auswertung_Druck_…`) kann der Kanal kalibriert
     werden, siehe [Kapitel 9](09_druckkalibrierung.md).
6. **Quadratischer Kanal:** Es wird keine Kalibrierung benötigt.

**Nur andere Abmessungen** (z. B. 500 µm statt 1000 µm, andere Länge, anderer
CO2-Anteil): Es ist nichts weiter anzupassen.

**Andere Flüssigkeit als Wasser:**
- `fluessigkeit` in `config.PARAMETER` setzen.
- Henry-Konstante und Diffusionskoeffizient sind derzeit nur für Wasser
  hinterlegt (`taylorflow/stoffdaten.py`), siehe
  [Kapitel 11](11_erweitern.md).

**Rechteckiger, nicht quadratischer Kanal:** wird nicht unterstützt. Die
Geometrie geht von Seitenlänge = Durchmesser aus.

## 2.4 Ausschlussregeln

Alle Ausschlüsse stehen in `config/ausschluesse.yaml`, gegliedert nach
Kanalname. Es gibt drei Arten:

```yaml
PVC_Rund_1000um_72cm_20molCO2_800um:
  messpunkte_entfernen:          # Zeilen der Rohdatei vor der Auswertung entfernen
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
  kla_ungueltig:                 # wird ausgewertet, aber kLa_log_mean = leer
    Gas_0_07_Liq_0_111: "nur 3 valide Punkte"
```

- **`messpunkte_entfernen`:** Möglich sind `GasVelocity`, `LiquidVelocity`,
  `CameraPosition` und `BinCenter_mm` (Toleranz 0,1 mm). Alle angegebenen
  Felder müssen zutreffen.
- **`betriebspunkte_ueberspringen`:** `GasVelocity` und/oder `LiquidVelocity`.
  Ein weggelassenes Feld bedeutet „alle Werte“.
- **`kla_ungueltig`:**
  - Der Name des Betriebspunkts steht in der Spalte `Config` der
    Betriebspunkt-Tabelle.
  - In der Tabelle wird `manual_exclude = True` gesetzt und der Grund
    übernommen.
  - Diese Punkte fallen aus 3D-Flächen und Modellvergleichen heraus. Profile
    und Blasenlängen-Fits bleiben verfügbar.

Die mitgelieferte Datei enthält alle Ausschlüsse des Forschungspraktikums mit
Begründung.

## 2.5 Automatischer Kamerafilter

Vor der Auswertung werden unzuverlässige Kamerapositionen entfernt (nur
Messart `Masse`). Ein Bin gilt als gültig, wenn alle drei Bedingungen erfüllt
sind:

- relativer Standardfehler der Blasenlänge ≤ 5 %
- mindestens 50 Blasen im Bin
- Variationskoeffizient ≤ 50 %

Eine Kamera eines Betriebspunkts bleibt, wenn mindestens 75 % ihrer Bins und
mindestens 3 Bins gültig sind. Betriebspunkte mit nur noch einer Kamera
entfallen. Die Grenzwerte stehen in `config.PARAMETER` (`kamerafilter_*`). Die
Konsole meldet, welche Kameras verworfen wurden.
