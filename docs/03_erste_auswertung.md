# 3 Erste Auswertung

Dieses Kapitel führt einmal durch eine komplette Auswertung, vom Start bis
zur Prüfung der Ergebnisse.

## 3.1 Programmteile im Überblick

Alle Einstellungen stehen in **einer** Datei, `config.py`. Gestartet wird
über eines von fünf Skripten im Projektordner:

| Skript | Zweck | Kapitel |
|---|---|---|
| `auswertung.py` | Messdateien auswerten, Tabellen und Plots erzeugen | 3, 4 |
| `abbildung.py` | eine einzelne Abbildung erzeugen und anpassen, z. B. für eine Arbeit | 4.11 |
| `literaturvergleich.py` | Messwerte mit Literaturmodellen vergleichen, eigenes Modell anpassen | 9 |
| `kalibrierung.py` | Bretherton-Faktor c aus Druckmessungen bestimmen | 10 |
| `monolith.py` | Monolith auswerten und mit einem Kanal vergleichen | 11 |

## 3.2 Starten

In der Eingabeaufforderung (Umgebung aktiviert, Kapitel 1.4):

```bat
cd C:\Messungen\TaylorFlow_Auswertung
.venv\Scripts\activate
python auswertung.py
```

oder in VS Code `auswertung.py` öffnen und **▷ Run Python File** klicken.

## 3.3 Messdateien auswählen

Es öffnet sich das Fenster **„Messdateien auswählen“**. Es startet in dem
Ordner, der in `config.py` als `DIALOG_ORDNER` eingetragen ist, und zeigt nur
Dateien `Auswertung_Masse_*.csv`. Über die Auswahlliste unten rechts lassen
sich auch alle CSV-Dateien anzeigen.

- Eine Datei: anklicken und **Öffnen**.
- Mehrere Dateien: mit gedrückter **Strg**-Taste anklicken, oder mit
  **Strg+A** alle markieren.
- **Abbrechen** beendet das Programm ohne Auswertung.

Die Konsole zeigt danach die gewählten Dateien und für jeden Betriebspunkt
die wichtigsten Zwischenergebnisse:

```
Messdateien:
  C:\…\data\raw\Auswertung_Masse_Glas_Q_1000um_72cm_20molCO2_600um.csv

=== Glas_Eckig_1000um_72cm_20molCO2_600um ===
  200 Messpunkte laut ausschluesse.yaml entfernt.
  Kamerafilter: 0 von 2892 Bins entfernt (0.0 %), 0 von 54 Kamerapositionen.

  Betriebspunkt Gas_0_07_Liq_0_02 (u_G = 0.07 m/s, u_L = 0.02 m/s)
    übersprungen (ausschluesse.yaml): Starke Abweichung des gemessenen Drucks.

  Betriebspunkt Gas_0_07_Liq_0_111 (u_G = 0.07 m/s, u_L = 0.111 m/s)
    Blasenfit: Exp+Expansion v2+Offsets (…), R² = 0.8338, chi²_red = 5.06
    Offset Kamera 2: -0.024 mm
    Offset Kamera 3: -0.019 mm
    Druck: Auslass 100373.3 Pa, Einlass 108958.7 Pa
    kLa_log_mean = 0.285 1/s (721 Punkte in der aktiven Zone)
  …
Plots für Glas_Eckig_1000um_72cm_20molCO2_600um
  gespeichert in C:\…\ergebnisse\Glas_Eckig_1000um_72cm_20molCO2_600um\plots

Fertig nach 18 s.
```

## 3.4 Ergebnisse finden und prüfen

```
ergebnisse\
  Modell_Gueltigkeitswarnungen.txt          Warnungen dieses Laufs (Kapitel 6.4)
  Glas_Eckig_1000um_72cm_20molCO2_600um\
    …_betriebspunkte.csv                    eine Zeile je Betriebspunkt, u. a. kLa_log_mean
    …_profile.csv                           Verläufe entlang des Kanals
    …_meta.json                             Quelldatei und Zeitpunkt
    plots\                                  alle Plots (Kapitel 4)
```

Die CSV-Dateien lassen sich direkt in Excel öffnen (Semikolon,
Dezimalkomma). Alle Spalten erklärt Kapitel 6.

**Bei einer neuen Messreihe in dieser Reihenfolge prüfen:**

1. **Warnungsprotokoll** `Modell_Gueltigkeitswarnungen.txt` lesen
   (Bedeutung der Meldungen: Kapitel 6.4).
2. **Blasenlängen-Fit** jedes Betriebspunkts ansehen
   (Dateien `blasenlaenge_*.png` in `plots`, Kapitel 4.2): Folgt die
   dunkelblaue Kurve den Messpunkten aller Kameras? Fällt die grüne Kurve
   monoton ab?
3. **Kennzahlen-Übersicht** `plots\heatmaps.png` auf Ausreißer prüfen.
4. Unbrauchbare Punkte in `config/ausschluesse.yaml` eintragen (Kapitel 2.4)
   und erneut auswerten.

## 3.5 Häufige Varianten

**Nur Plots neu zeichnen**, z. B. nach einer Änderung in `PLOTS` oder `STIL`:
in `config.py`

```python
NEU_RECHNEN = False
```

setzen und `auswertung.py` erneut starten. Im Auswahlfenster dieselben
Dateien wählen; es wird nichts neu gerechnet, das Zeichnen dauert nur
Sekunden.

**Ohne Auswahlfenster**, z. B. für wiederholte Läufe mit denselben Dateien:

```python
MESSDATEIEN = [
    Path(r"C:\Messungen\Videoauswertung\output\Output_MassTransfer\Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv"),
    Path(r"C:\Messungen\Videoauswertung\output\Output_MassTransfer\Auswertung_Masse_Glas_Q_1000um_72cm_20molCO2_600um.csv"),
]
```

oder `MESSDATEIEN = "alle"` für alle Dateien `Auswertung_Masse_*.csv` in
`ROHDATEN_ORDNER` (Standard `data/raw/`).

**Plots nur für einzelne Betriebspunkte:**

```python
BETRIEBSPUNKTE = ["Gas_0_134_Liq_0_056", "Gas_0_198_Liq_0_111"]
```

Die Namen stehen in der Spalte `Config` der Betriebspunkt-Tabelle und in
der Konsolenausgabe.
