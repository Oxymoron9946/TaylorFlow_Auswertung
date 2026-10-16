# TaylorFlow-Auswertung

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

Ausführliche Anleitung: **Handbuch** `docs/Handbuch_TaylorFlow.pdf`
(englisch: `docs/Handbuch_TaylorFlow_en.pdf`).

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
