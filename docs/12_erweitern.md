# 12 Programmaufbau und Erweiterung

## 12.1 Aufbau

```
config.py              alle Einstellungen
auswertung.py          Auswertung und Plots
abbildung.py           einzelne Abbildung
literaturvergleich.py  Modellvergleich
kalibrierung.py        Druckkalibrierung
monolith.py            Monolith
taylorflow/
  parameter.py         Zahlenwerte der Auswertung (Dataclass AuswerteParameter)
  einlesen.py          Dateiauswahl, Dateinamen, Messdaten, Ausschlüsse, Kamerafilter
  pipeline.py          Auswertung je Kanal und Betriebspunkt (Schritte 1–8, Kapitel 6.1)
  fits.py              Blasenmodell mit Kamera-Offsets, lineare Fits
  druckverlust.py      Bretherton, Kurimoto, Kalibrier-Datenbank
  hydrodynamik.py      Kapillarzahl, Filmdicke
  geometrie.py         Blasenvolumen und -querschnitt
  stoffdaten.py        thermo-Anbindung, Henry, Dampfdruck, Diffusion
  kla.py               aktive Zone, kLa_log_mean
  unsicherheit.py      Fehlerfortpflanzung (wird von der Auswertung nicht aufgerufen)
  literatur.py         Literaturmodelle und Registry
  modellvergleich.py   Vorhersagen, Potenzansatz-Fit, Statistik, eigene Modelle
  ergebnisse.py        Speichern und Laden der Ergebnisdateien
  protokoll.py         Warnungsprotokoll
  monolith.py          Gasbilanz des Monolithen
  kalibrierung.py      Druckkalibrierung
  plots/
    stil.py            PlotStil, Texte deutsch/englisch, Speichern
    optionen.py        Optionen je Plot: Standardwerte, Prüfung, Aufruf
    profile.py         Plots je Betriebspunkt
    flaechen.py        3D-Flächen
    heatmaps.py        Kennzahlen-Übersicht
    paritaet.py        Paritätsdiagramme
tests/                 Tests und Referenzergebnisse
docs/                  Handbuch (Markdown), Bilder, PDF-Erzeugung
```

**Abhängigkeiten:** Die Skripte im Projektordner lesen `config.py` und rufen
das Paket `taylorflow` auf. Das Paket selbst kennt `config.py` nicht; alle
Einstellungen werden als Argumente übergeben. Die Funktionen lassen sich
also auch einzeln nutzen.

## 12.2 Tests

```bat
python -m pytest
```

| Datei | Prüft |
|---|---|
| `tests/test_regression.py` | wertet alle mitgelieferten Messdateien aus und vergleicht jede Zahl der Betriebspunkt-Tabellen und einen Auszug der Profile exakt mit `tests/referenz/` |
| `tests/test_bausteine.py` | Einzelteile mit synthetischen Daten: Dateinamen, Fit, aktive Zone, kLa_log_mean, Unsicherheit, Modellregistry, Potenzansatz |
| `tests/test_dateiauswahl.py` | Auswahl der Messdateien (Liste, „alle“, Auswahlfenster), Dateien der Videoauswertung |
| `tests/test_plots.py` | Plot-Optionen in `config.py` und `abbildung.py` für jeden Plot |

Nach jeder Code-Änderung zeigt der Regressionstest, ob sich Ergebnisse
verändert haben.

**Wenn eine Änderung die Ergebnisse absichtlich verändert** (neues Modell,
Korrektur):

1. Die Wirkung beziffern:

   ```bat
   python tests/referenz_erneuern.py
   ```

   listet jede abweichende Spalte mit der größten relativen Abweichung.
2. Die Referenz neu schreiben:

   ```bat
   python tests/referenz_erneuern.py --schreiben
   ```

3. `__version__` in `taylorflow/__init__.py` erhöhen; die Version steht in
   jeder `<Kanal>_meta.json`.

## 12.3 Typische Erweiterungen

### Neues Literaturmodell

In `taylorflow/literatur.py`:

```python
def mein_modell(u_B, L_B, L_S, d_h, D):
    """Autor (Jahr), Zeitschrift. Gültig für …"""
    return 2.0 * np.sqrt(D * u_B / (L_B + L_S)) / d_h

LITERATURMODELLE["mein_modell"] = Literaturmodell(
    "mein_modell", "Autor 2027", "kLa_lit_mein_modell_1_s",
    lambda x: mein_modell(*_e(x, "u_B", "L_B", "L_S", "d_h", "D")))
```

Die verfügbaren Eingangsgrößen stehen in `modelleingaben()`. Neue Größen
werden dort und beim Aufruf in `pipeline.py` und `modellvergleich.vorhersage`
ergänzt. Die neue Spalte ändert die Betriebspunkt-Tabelle; danach die
Referenz neu schreiben (12.2).

### Neuer Plot

1. Funktion in einem Modul unter `taylorflow/plots/` anlegen. Sie bekommt
   die Daten, einen `PlotStil`, einen Titel und ihre Optionen als
   Schlüsselwort-Argumente und gibt eine Figure zurück. Für den Aufbau:
   - `neue_figur(stil, groesse_cm)`
   - `t(schluessel, stil)` für Beschriftungen; neue Texte in `TEXTE`
     eintragen, jeweils deutsch und englisch
   - `formatiere_achsen(ax, stil)`
2. In `taylorflow/plots/optionen.py`:
   - in `STANDARD` einen Eintrag mit allen Optionen und Standardwerten
   - in `erzeuge` einen Zweig, der die Funktion aufruft und den Dateinamen
     festlegt
3. In `config.PLOTS` einen Block mit denselben Einträgen wie in `STANDARD`
   anlegen. Der Test `test_config_zeigt_alle_optionen_mit_standardwerten`
   prüft, dass beide übereinstimmen.

Danach steht der Plot in `auswertung.py` und `abbildung.py` zur Verfügung.

### Neue Option für einen vorhandenen Plot

Parameter mit Standardwert in der Plotfunktion ergänzen, denselben Namen
mit demselben Standardwert in `STANDARD` (`optionen.py`) und im Block in
`config.PLOTS` eintragen.

### Andere Flüssigkeit oder anderes Gas

- **Flüssigkeit:** `fluessigkeit` in `config.PARAMETER` setzen (Name für
  thermo, z. B. `"ethanol"`).
- **Henry-Konstante:** Für andere Flüssigkeiten als Wasser
  `stoffdaten.henry` erweitern; derzeit gibt es eine Fehlermeldung.
- **Diffusionskoeffizient:** `stoffdaten.diffusion_co2_wasser` gilt nur für
  CO2/Wasser. Er wird nur für die Literaturmodelle und die Spalte
  `D_CO2_m2_s` verwendet.
- **Gas:** Neue Gase in `HENRY_DATEN` eintragen.

### Neuer Auswerte-Parameter

1. Feld mit Standardwert in `AuswerteParameter` (`parameter.py`) anlegen.
2. In der Rechnung über `p.<name>` verwenden.
3. In `config.PARAMETER` aufführen und in Kapitel 5 dokumentieren.

## 12.4 Handbuch erzeugen

Das Handbuch besteht aus den Markdown-Dateien in `docs/` (englisch in
`docs/en/`). Bilder und PDF werden mit zwei Skripten erzeugt:

```bat
python docs/bilder_erzeugen.py          Bilder aus den mitgelieferten Messdaten (deutsch)
python docs/bilder_erzeugen.py en       dasselbe mit englischer Beschriftung
python docs/build_pdf.py                docs/Handbuch_TaylorFlow.pdf
python docs/build_pdf.py en             docs/Handbuch_TaylorFlow_en.pdf
```

Für das PDF werden zusätzlich `pip install pypandoc_binary` und eine
LaTeX-Installation mit XeLaTeX (TeX Live oder MiKTeX) benötigt.
