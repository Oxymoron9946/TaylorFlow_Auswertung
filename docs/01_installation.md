# 1 Installation

## Voraussetzungen

- **Python:** 3.10 oder neuer (getestet mit 3.12).
- **Python-Pakete:** numpy, pandas, scipy, matplotlib, pyyaml und `thermo`.
  `thermo` liefert die Stoffdaten von Wasser, also Dichte, Viskosität,
  Oberflächenspannung und Dampfdruck.
- **Für das PDF-Handbuch zusätzlich:** Pandoc und eine LaTeX-Installation mit
  XeLaTeX (z. B. TeX Live). Pandoc lässt sich als Python-Paket installieren:
  `pip install pypandoc_binary`.

## Einrichtung

Im Hauptordner des Projekts:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Unter Linux und macOS lautet die zweite Zeile `source .venv/bin/activate`.

Prüfen, ob alles funktioniert:

```
python -m pytest
```

Erwartet: `20 passed`. Der Test wertet die mitgelieferten Messdaten aus und
vergleicht jede Zahl mit den eingefrorenen Referenzergebnissen in
`tests/referenz/`. Läuft er durch, rechnet die Installation identisch zum
Stand der Übergabe.

## Arbeiten mit Spyder oder VS Code

Die Skripte sind normale Python-Dateien und lassen sich auch in einer
Entwicklungsumgebung starten. Arbeitsverzeichnis muss dabei der Hauptordner
des Projekts sein, sonst wird `config.py` nicht gefunden.

In Spyder: *Ausführen → Konfiguration pro Datei → Arbeitsverzeichnis: Ordner
der Datei*.

## Typische Fehler

| Meldung | Ursache und Abhilfe |
|---|---|
| `ModuleNotFoundError: No module named 'thermo'` | Virtuelle Umgebung nicht aktiviert oder Pakete nicht installiert, siehe oben. |
| `ModuleNotFoundError: No module named 'config'` | Skript nicht aus dem Hauptordner gestartet. |
| `Dateiname '…' passt nicht zum Schema` | Messdatei falsch benannt, siehe [Messdaten](02_messdaten.md). |
| Tests schlagen mit kleinen Abweichungen fehl | Andere Paketversionen können in der letzten Stelle abweichende Stoffdaten liefern. Getestete Versionen: numpy 2.5, pandas 3.0, scipy 1.18, thermo 0.6. |
