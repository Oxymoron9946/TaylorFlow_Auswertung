# 3 First evaluation

This chapter walks through a complete evaluation once, from the start to
checking the results.

## 3.1 Program parts at a glance

All settings are in **one** file, `config.py`. One of five scripts in the
project folder is started:

| Script | Purpose | Chapter |
|---|---|---|
| `auswertung.py` | evaluate measurement files, create tables and plots | 3, 4 |
| `abbildung.py` | create and adjust a single figure, e.g. for a thesis | 4.11 |
| `literaturvergleich.py` | compare measurements with literature models, fit an own model | 9 |
| `kalibrierung.py` | determine the Bretherton factor c from pressure measurements | 10 |
| `monolith.py` | evaluate the monolith and compare it with a channel | 11 |

## 3.2 Starting

In the command prompt (environment activated, chapter 1.4):

```bat
cd C:\Measurements\TaylorFlow_Auswertung
.venv\Scripts\activate
python auswertung.py
```

or open `auswertung.py` in VS Code and click **▷ Run Python File**.

## 3.3 Selecting the measurement files

The window **“Messdateien auswählen”** (select measurement files) opens. It
starts in the folder entered as `DIALOG_ORDNER` in `config.py` and shows
only files `Auswertung_Masse_*.csv`. The list at the bottom right can also
show all CSV files.

- One file: click it and **Open**.
- Several files: click them with the **Ctrl** key held down, or select all
  with **Ctrl+A**.
- **Cancel** ends the program without evaluation.

The console then shows the selected files and the main intermediate
results for each operating point (program messages are in German):

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

Per operating point: bubble fit with R² and χ²_red, camera offsets, outlet
and inlet pressure (`Druck: Auslass …, Einlass …`) and kLa_log_mean with the
number of grid points in the active zone.

## 3.4 Finding and checking the results

```
ergebnisse\
  Modell_Gueltigkeitswarnungen.txt          warnings of this run (chapter 6.4)
  Glas_Eckig_1000um_72cm_20molCO2_600um\
    …_betriebspunkte.csv                    one row per operating point, incl. kLa_log_mean
    …_profile.csv                           profiles along the channel
    …_meta.json                             source file and time
    plots\                                  all plots (chapter 4)
```

The CSV files can be opened directly in Excel (semicolon, decimal comma).
Chapter 6 explains all columns.

**For a new series, check in this order:**

1. Read the **warning log** `Modell_Gueltigkeitswarnungen.txt` (meaning of
   the messages: chapter 6.4).
2. Look at the **bubble length fit** of each operating point (files
   `blasenlaenge_*.png` in `plots`, chapter 4.2): does the dark blue curve
   follow the data points of all cameras? Does the green curve decrease
   monotonically?
3. Check the **overview of key figures** `plots\heatmaps.png` for outliers.
4. Enter unusable points in `config/ausschluesse.yaml` (chapter 2.4) and
   evaluate again.

## 3.5 Common variants

**Only redraw the plots**, e.g. after a change in `PLOTS` or `STIL`: set in
`config.py`

```python
NEU_RECHNEN = False
```

and start `auswertung.py` again. Select the same files in the selection
window; nothing is recalculated and drawing only takes seconds.

**Without the selection window**, e.g. for repeated runs with the same files:

```python
MESSDATEIEN = [
    Path(r"C:\Measurements\Videoauswertung\output\Output_MassTransfer\Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv"),
    Path(r"C:\Measurements\Videoauswertung\output\Output_MassTransfer\Auswertung_Masse_Glas_Q_1000um_72cm_20molCO2_600um.csv"),
]
```

or `MESSDATEIEN = "alle"` for all files `Auswertung_Masse_*.csv` in
`ROHDATEN_ORDNER` (default `data/raw/`).

**Plots only for selected operating points:**

```python
BETRIEBSPUNKTE = ["Gas_0_134_Liq_0_056", "Gas_0_198_Liq_0_111"]
```

The names are in the column `Config` of the operating point table and in
the console output.
