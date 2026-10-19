# 1 Installation

## 1.1 Python installieren

Benötigt wird **Python 3.10 oder neuer** (getestet mit Python 3.12) mit diesen
Paketen. Sie werden in Abschnitt 1.4 mit einem einzigen Befehl installiert:

| Paket | Wofür |
|---|---|
| numpy, pandas, scipy | Rechnung, Tabellen, Kurvenanpassung |
| matplotlib | alle Plots |
| thermo | Stoffdaten von Wasser (Dichte, Viskosität, Oberflächenspannung, Dampfdruck) |
| pyyaml | Ausschlussregeln und eigene Modelle (`.yaml`-Dateien) |
| pytest | Prüfung der Installation |

Das Auswahlfenster für die Messdateien nutzt `tkinter`. Es ist Teil der
Python-Installation von python.org und muss nicht eigens installiert werden.

**Python neu installieren (Windows)**

1. Auf <https://www.python.org/downloads/> den Installer der aktuellen
   Version 3.12 oder 3.13 herunterladen (*Windows installer (64-bit)*).
2. Den Installer starten. Im ersten Fenster **unten den Haken bei „Add
   python.exe to PATH“ setzen**, dann **Install Now** wählen.
3. Die Voreinstellungen enthalten bereits *tcl/tk and IDLE*; das wird für das
   Auswahlfenster gebraucht. Bei **Customize installation** diesen Haken nicht
   entfernen.
4. Installation abschließen.

**Prüfen**

Die Eingabeaufforderung öffnen (Startmenü → „cmd“) und eingeben:

```bat
python --version
```

Erwartet wird z. B. `Python 3.12.7`. Erscheint stattdessen der Microsoft
Store oder „Python wurde nicht gefunden“, fehlt der Haken bei „Add to PATH“:
den Installer erneut starten, **Modify** → **Next** → *Add Python to
environment variables* anhaken.

## 1.2 Programm herunterladen

Das Programm liegt auf GitHub:
<https://github.com/Oxymoron9946/TaylorFlow_Auswertung> (Branch `main`).
Das Repository ist öffentlich; zum Herunterladen ist kein GitHub-Konto
nötig.

**Variante A: als ZIP, ohne weitere Software**

1. Die Seite im Browser öffnen.
2. Oben rechts auf **Code** → **Download ZIP** klicken.
3. Das ZIP entpacken, z. B. nach `C:\Messungen\TaylorFlow_Auswertung`.
   Dieser Ordner ist im Folgenden der **Projektordner**; er enthält u. a.
   `config.py`, `auswertung.py` und `abbildung.py`.

Für eine neuere Version das ZIP erneut herunterladen und den Ordner
ersetzen. Eigene Änderungen an `config.py`, `config/ausschluesse.yaml` und
`config/eigene_modelle.yaml` vorher sichern.

**Variante B: mit Git (bequem für spätere Aktualisierungen)**

1. *Git for Windows* von <https://git-scm.com/download/win> installieren
   (Standardeinstellungen genügen).
2. Die Eingabeaufforderung öffnen, in den gewünschten Elternordner wechseln
   und das Repository holen:

   ```bat
   cd C:\Messungen
   git clone https://github.com/Oxymoron9946/TaylorFlow_Auswertung.git
   ```

3. Später eine neue Version holen (im Projektordner):

   ```bat
   cd C:\Messungen\TaylorFlow_Auswertung
   git pull
   ```

   Hat man `config.py` lokal geändert, meldet `git pull` einen Konflikt nur
   dann, wenn dieselbe Datei auch auf GitHub geändert wurde.

## 1.3 Messdaten bereitstellen

Die Auswertung liest die Ergebnisdateien der **Videoauswertung**
(Handbuch der Videoauswertung, Kapitel 4.2):

| Datei der Videoauswertung | Wofür hier |
|---|---|
| `output/Output_MassTransfer/Auswertung_Masse_<…>.csv` | Stoffübergang, `auswertung.py` |
| `output/Output_PressureCalibration/Auswertung_Druck_<…>.csv` | Druckkalibrierung, `kalibrierung.py` |

Die Dateien müssen nicht kopiert werden: Beim Start öffnet sich ein
Auswahlfenster, in dem sie direkt im Ausgabeordner der Videoauswertung
gewählt werden. Damit das Fenster gleich dort startet, in `config.py` den
Ordner eintragen:

```python
DIALOG_ORDNER = Path(r"C:\Messungen\Videoauswertung\output\Output_MassTransfer")
```

Die Messdaten des Forschungspraktikums liegen bereits im Projektordner unter
`data/raw/`. Mit ihnen lässt sich alles ausprobieren. Aufbau der Dateien:
Kapitel 2.

## 1.4 Einrichtung

Im Projektordner wird eine eigene Python-Umgebung (*virtual environment*,
Ordner `.venv`) angelegt. Sie enthält genau die benötigten Pakete und stört
keine andere Python-Installation.

1. Eingabeaufforderung öffnen und in den Projektordner wechseln:

   ```bat
   cd C:\Messungen\TaylorFlow_Auswertung
   ```

2. Umgebung anlegen (einmalig) und aktivieren:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Vor der Eingabezeile steht danach `(.venv)`. Die Aktivierung gilt nur für
   dieses Fenster; in jedem neuen Fenster ist `.venv\Scripts\activate`
   erneut nötig.

3. Pakete installieren (einmalig, dauert ein bis zwei Minuten):

   ```bat
   pip install -r requirements.txt
   ```

4. Installation prüfen:

   ```bat
   python -m pytest
   ```

   Erwartet: eine Zeile wie `40 passed`, kein `failed`. Der Test wertet die
   mitgelieferten Messdaten vollständig aus und vergleicht jede Zahl mit den
   Referenzergebnissen in `tests/referenz/`. Läuft er durch, rechnet die
   Installation richtig.

Unter Linux und macOS lautet die Aktivierung `source .venv/bin/activate`.

## 1.5 Erster Start

Mit aktivierter Umgebung im Projektordner:

```bat
python auswertung.py
```

Das Auswahlfenster öffnet sich in `data/raw/`. Eine oder mehrere Dateien
`Auswertung_Masse_….csv` wählen (mehrere mit gedrückter Strg-Taste) und
**Öffnen** klicken. Nach etwa 20 Sekunden je Datei stehen Tabellen und Plots
in `ergebnisse/` (Kapitel 3).

## 1.6 Arbeiten in VS Code oder Spyder

Die Skripte lassen sich auch in einer Entwicklungsumgebung starten. Wichtig
ist in beiden Fällen: **Der Projektordner muss das Arbeitsverzeichnis sein**,
sonst wird `config.py` nicht gefunden.

**VS Code**

1. VS Code von <https://code.visualstudio.com> installieren und die
   Erweiterung *Python* (von Microsoft) hinzufügen.
2. **Datei** → **Ordner öffnen** → Projektordner.
3. Unten rechts bzw. mit Strg+Umschalt+P → *Python: Select Interpreter* die
   Umgebung `.venv` wählen.
4. `auswertung.py` öffnen und oben rechts auf **▷ Run Python File**
   klicken. Die Ausgabe erscheint im Terminal unten.

**Spyder**

1. Unter **Extras** → **Einstellungen** → **Python-Interpreter** den
   Interpreter `…\TaylorFlow_Auswertung\.venv\Scripts\python.exe` eintragen.
   In der Umgebung zusätzlich `pip install spyder-kernels` ausführen.
2. **Ausführen** → **Konfiguration pro Datei** → *Arbeitsverzeichnis:
   Verzeichnis der Datei*.

## 1.7 Typische Fehler

| Meldung | Ursache | Abhilfe |
|---|---|---|
| `'python' wird nicht erkannt …` oder der Microsoft Store öffnet sich | Python fehlt im PATH | Installer → Modify → *Add Python to environment variables* (1.1) |
| `ModuleNotFoundError: No module named 'thermo'` (oder `numpy`, `yaml`) | Umgebung nicht aktiviert oder Pakete nicht installiert | `.venv\Scripts\activate`, dann `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'config'` | Skript nicht aus dem Projektordner gestartet | in den Projektordner wechseln (1.4) bzw. Arbeitsverzeichnis einstellen (1.6) |
| `ModuleNotFoundError: No module named 'tkinter'` | Python ohne *tcl/tk* installiert | Installer → Modify → *tcl/tk and IDLE* anhaken, oder feste Dateiliste statt Auswahlfenster (Kapitel 3.5) |
| `Keine Messdatei ausgewählt, Auswertung beendet.` | Auswahlfenster abgebrochen | erneut starten und Datei wählen |
| `Dateiname '…' passt nicht zum Schema` | Messdatei falsch benannt | Kapitel 2.2 |
| `In '…' fehlen die Spalten […]` | Datei stammt nicht aus der Videoauswertung oder ist unvollständig | Kapitel 2.3 |
| Tests schlagen mit sehr kleinen Abweichungen fehl | andere Paketversionen liefern Stoffdaten, die in der letzten Stelle abweichen | Versionen aus `requirements.txt` verwenden; getestet mit numpy 2.5, pandas 3.0, scipy 1.18, thermo 0.6 |
