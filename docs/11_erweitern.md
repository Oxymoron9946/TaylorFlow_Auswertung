# 11 Programmaufbau und Erweiterung

## 11.1 Module

```
taylorflow/
  parameter.py        alle Zahlenwerte der Auswertung (Dataclass AuswerteParameter)
  einlesen.py         Dateinamen, Messdaten, Ausschlüsse, Kamerafilter
  pipeline.py         Auswertung je Kanal und Betriebspunkt (Schritte 1–9)
  fits.py             Blasenmodell v2 mit Offsets, lineare Fits, Einbruchfilter
  druckverlust.py     Bretherton, Kurimoto, Kalibrier-Datenbank
  hydrodynamik.py     Kapillarzahl, Filmdicke
  geometrie.py        Blasenvolumen und -querschnitt
  stoffdaten.py       thermo-Anbindung, Henry, Dampfdruck, Diffusion
  kla.py              aktive Zone, lokales kLa, Log-Mean, Unsicherheit
  literatur.py        Literaturmodelle und Registry
  modellvergleich.py  Vorhersagen, Potenzansatz-Fit, Statistik, eigene Modelle
  ergebnisse.py       Speichern und Laden der Ergebnisdateien
  protokoll.py        Warnungsprotokoll
  monolith.py         Gasbilanz des Monolithen
  kalibrierung.py     Druckkalibrierung
  plots/              stil.py (Stil, Texte de/en, Speichern), profile.py,
                      flaechen.py, heatmaps.py, paritaet.py
```

**Abhängigkeiten:**
- Die Skripte im Hauptordner lesen `config.py` und rufen das Paket auf.
- Das Paket selbst kennt `config.py` nicht. Alle Einstellungen werden als
  Argumente übergeben; die Funktionen lassen sich also unabhängig nutzen.

## 11.2 Tests

```
python -m pytest
```

- **`tests/test_regression.py`:**
  - Wertet alle mitgelieferten Messdateien aus.
  - Vergleicht jede Zahl der Betriebspunkt-Tabellen und einen Auszug der
    Profile mit `tests/referenz/`, und zwar exakt, nicht mit Toleranz.
  - Nach jeder Code-Änderung zeigt der Test, ob sich Ergebnisse verändert
    haben.
- **`tests/test_bausteine.py`:**
  - Prüft Einzelteile mit synthetischen Daten: Dateinamen, Fit, Log-Mean,
    Modellregistry, Potenzansatz.

**Wenn eine Änderung die Ergebnisse absichtlich verändert** (neues Modell,
Fehlerkorrektur):

1. Die Wirkung beziffern: Vorher und nachher vergleichen, z. B. mit
   `taylorflow.ergebnisse.lade_betriebspunkte`.
2. Die Referenz neu erzeugen:

   ```python
   import shutil
   from pathlib import Path
   import config, auswertung
   auswertung.rechne()            # alle Kanäle, Standardparameter in config.py!
   ref = Path("tests/referenz")
   for k in auswertung.ergebnisse.vorhandene_kanaele(config.ERGEBNIS_ORDNER):
       shutil.copy(config.ERGEBNIS_ORDNER / k / f"{k}_betriebspunkte.csv", ref)
       p = auswertung.ergebnisse.lade_profile(config.ERGEBNIS_ORDNER, k)
       p = p[p["Position_z_m"].round(6).isin([0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.72])]
       p.to_csv(ref / f"{k}_profile_auszug.csv", index=False, sep=";", decimal=",",
                encoding="utf-8-sig")
   ```

3. Die Änderung in `docs/CHANGELOG.md` mit der Wirkung eintragen und
   `__version__` in `taylorflow/__init__.py` erhöhen.

## 11.3 Typische Erweiterungen

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

Verfügbare Eingangsgrößen stehen in `modelleingaben()`. Neue Größen werden
dort und beim Aufruf in `pipeline.py` und `modellvergleich.vorhersage`
ergänzt.

Die neue Spalte ändert die Betriebspunkt-Tabelle; danach die Referenz neu
erzeugen (11.2).

### Neuer Plot

1. Funktion in einem Modul unter `taylorflow/plots/` anlegen. Sie bekommt
   die Daten und einen `PlotStil` und gibt eine Figure zurück. Für den
   Aufbau:
   - `neue_figur(stil, groesse_cm)`
   - `t(schluessel, stil)` für Beschriftungen; neue Texte in `TEXTE`
     eintragen, jeweils deutsch und englisch
   - `formatiere_achsen(ax, stil)`
2. In `taylorflow/plots/__init__.py` exportieren.
3. In `auswertung.zeichne()` mit einem neuen Schalter in `config.PLOTS`
   aufrufen.

### Andere Flüssigkeit oder anderes Gas

- **Flüssigkeit:** `fluessigkeit` in `config.PARAMETER` setzen (Name für
  thermo, z. B. `"ethanol"`).
- **Henry-Konstante:** Für Nicht-Wasser `stoffdaten.henry` erweitern.
  Derzeit gibt es eine Fehlermeldung.
- **Diffusionskoeffizient:** `stoffdaten.diffusion_co2_wasser` ist
  CO2/Wasser-spezifisch. Er wird nur für die Literaturmodelle und
  `D_CO2_m2_s` verwendet.
- **Gas:** Neue Gase in `HENRY_DATEN` eintragen.

### Neuer Parameter

1. Feld mit Standardwert in `AuswerteParameter` (`parameter.py`) anlegen.
2. In der Rechnung über `p.<name>` verwenden.
3. In `config.PARAMETER` aufführen.
4. In [Kapitel 3](03_konfiguration.md) dokumentieren.

## 11.4 Herkunft

Dieses Repository ist aus dem Arbeitsstand des Forschungspraktikums
entstanden (Repository `Datenauswertung-Taylor-Flow`, Commit 4edd541).

- **Im Archiv verblieben:**
  - GUI
  - rund 45 Diagnose- und Sensitivitätsskripte
  - die ausführliche Methodik (`docs/METHODIK.md`, 1700 Zeilen)
  - die Fehleranalyse eckig/rund
  - ältere Plotvarianten
- **Verifikation:** Die Übernahme wurde Spalte für Spalte gegen die
  Ergebnisse des Archivstands geprüft. Bis auf die dokumentierte
  Log-Mean-Korrektur sind alle Werte bit-gleich (siehe CHANGELOG).
