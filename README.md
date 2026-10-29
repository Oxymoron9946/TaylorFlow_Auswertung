# TaylorFlow-Auswertung

**Deutsch** · [English](#english)

[![Handbuch-PDF](https://github.com/Oxymoron9946/TaylorFlow_Auswertung/actions/workflows/handbuch-pdf.yml/badge.svg)](https://github.com/Oxymoron9946/TaylorFlow_Auswertung/actions/workflows/handbuch-pdf.yml)

Auswertung von Taylor-Flow-Messungen zur CO2-Absorption in Wasser in
Einzelkanälen (rund oder quadratisch, ca. 1 mm) und in einem Monolithen.

Aus den Ergebnissen der Videoauswertung (Blasen- und Sluglänge,
Blasengeschwindigkeit an mehreren Kamerapositionen) berechnet das Programm
je Betriebspunkt (u_G, u_L):

- das Druckprofil im Kanal
- die absorbierte CO2-Stoffmenge und die Sättigung der Flüssigkeit
- den volumetrischen Stoffübergangskoeffizienten kLa (logarithmisches
  Mittel über die aktive Zone)
- den volumenspezifischen Molenstrom und Vorhersagen aus zehn
  Literaturmodellen

und stellt die Ergebnisse in anpassbaren Plots dar.

> **Handbuch:** [PDF deutsch](docs/Handbuch_TaylorFlow.pdf) ·
> [PDF English](docs/Handbuch_TaylorFlow_en.pdf) ·
> [alle Kapitel](docs/README.md) ·
> **[Handbuch bearbeiten](docs/HANDBUCH_BEARBEITEN.md)**
>
> **Eingangsdaten:** Die Dateien `Auswertung_Masse_….csv` stammen aus der
> [Videoauswertung Taylor-Flow](https://github.com/Oxymoron9946/Bildauswertung-und-Analyse)
> (MATLAB, Blasenlängen und -geschwindigkeiten aus Hochgeschwindigkeitsvideos).

## Schnellstart

1. **Installieren** (einmalig, Python 3.10 oder neuer):

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Auswerten:**

   ```bat
   python auswertung.py
   ```

   Im Auswahlfenster eine oder mehrere Dateien `Auswertung_Masse_….csv`
   wählen, z. B. aus `data/raw/` oder direkt aus dem Ausgabeordner der
   Videoauswertung.

3. **Ergebnisse** liegen in `ergebnisse/<Kanal>/`: Tabellen
   `<Kanal>_betriebspunkte.csv` und `<Kanal>_profile.csv`, alle Plots im
   Unterordner `plots/`, Warnungen in `ergebnisse/Modell_Gueltigkeitswarnungen.txt`.

4. **Plots anpassen** in `config.py`, Abschnitt `PLOTS` (je Plot ein Block
   mit allen Optionen), oder eine einzelne Abbildung mit `abbildung.py`.

Ausführliche Anleitung: **Handbuch** [docs/Handbuch_TaylorFlow.pdf](docs/Handbuch_TaylorFlow.pdf)
(englisch: [docs/Handbuch_TaylorFlow_en.pdf](docs/Handbuch_TaylorFlow_en.pdf)).

| Befehl | Zweck | Kapitel |
|---|---|---|
| `python auswertung.py` | Messdateien auswerten, Tabellen und Plots | [3](docs/03_erste_auswertung.md), [4](docs/04_plots.md) |
| `python abbildung.py` | eine einzelne angepasste Abbildung | [4.11](docs/04_plots.md) |
| `python literaturvergleich.py` | Messwerte gegen Literaturmodelle, eigenes Modell anpassen | [9](docs/09_literaturvergleich.md) |
| `python kalibrierung.py` | Bretherton-Faktor c aus Druckmessungen | [10](docs/10_druckkalibrierung.md) |
| `python monolith.py` | Monolith auswerten und mit einem Kanal vergleichen | [11](docs/11_monolith.md) |
| `python -m pytest` | Tests, u. a. Vergleich mit den Referenzergebnissen | [12](docs/12_erweitern.md) |

## Handbuch

1. [Installation](docs/01_installation.md)
2. [Messdaten](docs/02_messdaten.md)
3. [Erste Auswertung](docs/03_erste_auswertung.md)
4. [Plots auswählen und anpassen](docs/04_plots.md)
5. [Konfiguration](docs/05_konfiguration.md)
6. [Ergebnisse](docs/06_ergebnisse.md)
7. [Methodik](docs/07_methodik.md)
8. [Grenzen](docs/08_grenzen.md)
9. [Literaturvergleich und eigene Modelle](docs/09_literaturvergleich.md)
10. [Druckkalibrierung](docs/10_druckkalibrierung.md)
11. [Monolith](docs/11_monolith.md)
12. [Programmaufbau und Erweiterung](docs/12_erweitern.md)

Englische Kapitel in [docs/en/](docs/en/). Beide PDFs werden bei jeder
Änderung in `docs/` automatisch neu gebaut; lokal mit `python docs/build_pdf.py`
bzw. `python docs/build_pdf.py en`.

**Handbuch ändern:** [docs/HANDBUCH_BEARBEITEN.md](docs/HANDBUCH_BEARBEITEN.md) –
im Browser, ohne Installation.

## Ordner

```
config.py                  Einstellungen (einzige Datei, die man ändern muss)
auswertung.py              Auswertung und Plots
abbildung.py               einzelne Abbildung
literaturvergleich.py      Modellvergleich und eigene Modelle
kalibrierung.py            Druckkalibrierung
monolith.py                Monolith-Auswertung
config/ausschluesse.yaml   ausgeschlossene Messpunkte und Betriebspunkte
config/eigene_modelle.yaml angepasste eigene Modelle (entsteht bei Bedarf)
data/raw/                  mitgelieferte Messdateien
data/calibrated_c_database.json   Bretherton-Faktoren der runden Kanäle
taylorflow/                Programmcode
tests/                     Tests und Referenzergebnisse
docs/                      Handbuch
ergebnisse/                Ausgaben (wird erzeugt)
```

---

## English

Evaluation of Taylor flow measurements of CO2 absorption in water in single
channels (round or square, about 1 mm) and in a monolith.

From the results of the video evaluation (bubble and slug length, bubble
velocity at several camera positions) the program computes for every
operating point (u_G, u_L):

- the pressure profile in the channel
- the absorbed amount of CO2 and the saturation of the liquid
- the volumetric mass transfer coefficient kLa (logarithmic mean over the
  active zone)
- the volume-specific molar flux and predictions from ten literature models

and presents the results in adjustable plots.

> **Manual:** [PDF English](docs/Handbuch_TaylorFlow_en.pdf) ·
> [PDF Deutsch](docs/Handbuch_TaylorFlow.pdf) ·
> [all chapters](docs/README.md) ·
> **[Editing the manual](docs/en/EDITING_THE_MANUAL.md)**
>
> **Input data:** the files `Auswertung_Masse_….csv` come from the
> [video evaluation](https://github.com/Oxymoron9946/Bildauswertung-und-Analyse)
> (MATLAB, bubble lengths and velocities from high-speed videos).

### Quick start

1. **Install** (once, Python 3.10 or newer):

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Evaluate:**

   ```bat
   python auswertung.py
   ```

   In the file dialog select one or more files `Auswertung_Masse_….csv`,
   e.g. from `data/raw/` or directly from the output folder of the video
   evaluation.

3. The **results** are in `ergebnisse/<channel>/`: tables
   `<channel>_betriebspunkte.csv` and `<channel>_profile.csv`, all plots in
   the subfolder `plots/`, warnings in `ergebnisse/Modell_Gueltigkeitswarnungen.txt`.

4. **Adjust plots** in `config.py`, section `PLOTS` (one block per plot with
   all options), or create a single figure with `abbildung.py`.

Full instructions: **manual** [docs/Handbuch_TaylorFlow_en.pdf](docs/Handbuch_TaylorFlow_en.pdf).

| Command | Purpose | Chapter |
|---|---|---|
| `python auswertung.py` | evaluate measurement files, tables and plots | [3](docs/en/03_erste_auswertung.md), [4](docs/en/04_plots.md) |
| `python abbildung.py` | a single adjusted figure | [4.11](docs/en/04_plots.md) |
| `python literaturvergleich.py` | measurements vs. literature models, fit an own model | [9](docs/en/09_literaturvergleich.md) |
| `python kalibrierung.py` | Bretherton factor c from pressure measurements | [10](docs/en/10_druckkalibrierung.md) |
| `python monolith.py` | evaluate the monolith and compare it with a channel | [11](docs/en/11_monolith.md) |
| `python -m pytest` | tests, incl. comparison with the reference results | [12](docs/en/12_erweitern.md) |

### Manual

1. [Installation](docs/en/01_installation.md)
2. [Measurement data](docs/en/02_messdaten.md)
3. [First evaluation](docs/en/03_erste_auswertung.md)
4. [Selecting and adjusting plots](docs/en/04_plots.md)
5. [Configuration](docs/en/05_konfiguration.md)
6. [Results](docs/en/06_ergebnisse.md)
7. [Methodology](docs/en/07_methodik.md)
8. [Limitations](docs/en/08_grenzen.md)
9. [Literature comparison and own models](docs/en/09_literaturvergleich.md)
10. [Pressure calibration](docs/en/10_druckkalibrierung.md)
11. [Monolith](docs/en/11_monolith.md)
12. [Program structure and extension](docs/en/12_erweitern.md)

Both PDFs are rebuilt automatically whenever anything in `docs/` changes;
locally with `python docs/build_pdf.py en`.

**Editing the manual:** [docs/en/EDITING_THE_MANUAL.md](docs/en/EDITING_THE_MANUAL.md) –
in the browser, nothing to install.

### Folders

```
config.py                  settings (the only file you need to change)
auswertung.py              evaluation and plots
abbildung.py               single figure
literaturvergleich.py      model comparison and own models
kalibrierung.py            pressure calibration
monolith.py                monolith evaluation
config/ausschluesse.yaml   excluded measurement points and operating points
config/eigene_modelle.yaml fitted own models (created when needed)
data/raw/                  supplied measurement files
data/calibrated_c_database.json   Bretherton factors of the round channels
taylorflow/                program code
tests/                     tests and reference results
docs/                      manual
ergebnisse/                output (generated)
```
