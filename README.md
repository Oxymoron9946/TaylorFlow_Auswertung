# TaylorFlow-Auswertung

Auswertung von Taylor-Flow-Messungen zur CO2-Absorption in Wasser in
Einzelkanälen (rund oder quadratisch, ca. 1 mm) und in einem Monolithen.

Aus den Ergebnissen der Bildauswertung (Blasen- und Sluglänge,
Blasengeschwindigkeit an mehreren Kamerapositionen) berechnet das Programm
je Betriebspunkt (u_G, u_L):

- das Druckprofil im Kanal
- die absorbierte CO2-Stoffmenge und die Sättigung der Flüssigkeit
- den lokalen und den mittleren volumetrischen Stoffübergangskoeffizienten
  kLa (logarithmisches Mittel über die aktive Zone)
- den volumenspezifischen Molenstrom und Vorhersagen aus zehn Literaturmodellen

Entstanden im Forschungspraktikum (2026); Stand der Rechnung: Version 3.0
(siehe [CHANGELOG](docs/CHANGELOG.md)).

## Schnellstart

1. **Installieren** (einmalig, Python 3.10 oder neuer):

   ```
   python -m venv .venv
   .venv\Scripts\activate          (Linux/macOS: source .venv/bin/activate)
   pip install -r requirements.txt
   ```

2. **Messdateien ablegen** in `data/raw/`, Dateinamen nach dem Schema
   `Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv`
   (Details: [Messdaten](docs/02_messdaten.md)).

3. **Einstellungen prüfen** in [`config.py`](config.py). Für die mitgelieferten
   Daten muss nichts geändert werden.

4. **Auswerten:**

   ```
   python auswertung.py
   ```

   Dauer: etwa eine Minute für fünf Kanäle inklusive aller Plots.

5. **Ergebnisse** liegen in `ergebnisse/<Kanal>/`:
   - Tabellen `<Kanal>_betriebspunkte.csv` und `<Kanal>_profile.csv`
   - alle Plots im Unterordner `plots/`
   - das Warnungsprotokoll in `ergebnisse/Modell_Gueltigkeitswarnungen.txt`

Weitere Auswertungen:

| Befehl | Zweck | Kapitel |
|---|---|---|
| `python literaturvergleich.py` | Messwerte gegen Literaturmodelle, eigenes Modell anpassen | [08](docs/08_literaturvergleich.md) |
| `python monolith.py` | Monolith auswerten und mit einem Kanal vergleichen | [10](docs/10_monolith.md) |
| `python kalibrierung.py` | Bretherton-Faktor c aus Messungen ohne CO2 | [09](docs/09_druckkalibrierung.md) |
| `python -m pytest` | Tests, u. a. Vergleich mit den Referenzergebnissen | [11](docs/11_erweitern.md) |

## Dokumentation

Das Handbuch liegt als Markdown in `docs/` und lässt sich mit
`python docs/build_pdf.py` zu `docs/Handbuch.pdf` zusammensetzen.

1. [Installation](docs/01_installation.md)
2. [Messdaten und neue Messreihen](docs/02_messdaten.md)
3. [Konfiguration: alle Einstellungen](docs/03_konfiguration.md)
4. [Ablauf der Auswertung und Ergebnisdateien](docs/04_auswertung.md)
5. [Plots](docs/05_plots.md)
6. [Methodik: Modelle und Gleichungen](docs/06_methodik.md)
7. [Gültigkeit und bekannte Einschränkungen](docs/07_grenzen.md)
8. [Literaturvergleich und eigene Modelle](docs/08_literaturvergleich.md)
9. [Druckkalibrierung](docs/09_druckkalibrierung.md)
10. [Monolith](docs/10_monolith.md)
11. [Programmaufbau und Erweiterung](docs/11_erweitern.md)

## Ordner

```
config.py                  Einstellungen (einzige Datei, die man ändern muss)
auswertung.py              Hauptprogramm
literaturvergleich.py      Modellvergleich und eigene Modelle
monolith.py                Monolith-Auswertung
kalibrierung.py            Druckkalibrierung
config/ausschluesse.yaml   ausgeschlossene Messpunkte und Betriebspunkte
config/eigene_modelle.yaml angepasste eigene Modelle (entsteht bei Bedarf)
data/raw/                  Messdateien
data/calibrated_c_database.json   Bretherton-Faktoren der runden Kanäle
taylorflow/                Programmcode
tests/                     Tests und Referenzergebnisse
docs/                      Handbuch
ergebnisse/                Ausgaben (wird erzeugt)
```
