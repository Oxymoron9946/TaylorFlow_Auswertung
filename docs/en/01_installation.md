# 1 Installation

The program, its settings and its console messages use German names (for
example `config.py`, `auswertung.py`, `MESSDATEIEN`). This manual explains
every name in English; the names themselves are written exactly as they
must be typed.

## 1.1 Installing Python

**Python 3.10 or newer** is required (tested with Python 3.12) together with
these packages. They are installed with a single command in section 1.4:

| Package | Used for |
|---|---|
| numpy, pandas, scipy | calculation, tables, curve fitting |
| matplotlib | all plots |
| thermo | property data of water (density, viscosity, surface tension, vapour pressure) |
| pyyaml | exclusion rules and own models (`.yaml` files) |
| pytest | checking the installation |

The file selection window uses `tkinter`. It is part of the Python
installation from python.org and does not need to be installed separately.

**New Python installation (Windows)**

1. Download the installer of the current version 3.12 or 3.13 from
   <https://www.python.org/downloads/> (*Windows installer (64-bit)*).
2. Start the installer. In the first window **tick “Add python.exe to PATH”
   at the bottom**, then choose **Install Now**.
3. The default settings already include *tcl/tk and IDLE*, which the file
   selection window needs. Do not untick it under **Customize installation**.
4. Finish the installation.

**Check**

Open the command prompt (Start menu → “cmd”) and enter:

```bat
python --version
```

The expected answer is e.g. `Python 3.12.7`. If the Microsoft Store opens or
Python is “not found”, the PATH option is missing: start the installer
again, choose **Modify** → **Next** and tick *Add Python to environment
variables*.

## 1.2 Downloading the program

The program is on GitHub:
<https://github.com/Oxymoron9946/TaylorFlow_Auswertung> (branch `main`).
The repository is public; no GitHub account is needed to download it.

**Option A: as a ZIP file, no further software**

1. Open the page in a browser.
2. Click **Code** → **Download ZIP** at the top right.
3. Unpack the ZIP file, e.g. to `C:\Measurements\TaylorFlow_Auswertung`.
   This folder is called the **project folder** below; it contains among
   others `config.py`, `auswertung.py` and `abbildung.py`.

For a newer version, download the ZIP file again and replace the folder.
Back up your own changes to `config.py`, `config/ausschluesse.yaml` and
`config/eigene_modelle.yaml` first.

**Option B: with Git (convenient for later updates)**

1. Install *Git for Windows* from <https://git-scm.com/download/win>
   (default settings are sufficient).
2. Open the command prompt, change to the desired parent folder and fetch
   the repository:

   ```bat
   cd C:\Measurements
   git clone https://github.com/Oxymoron9946/TaylorFlow_Auswertung.git
   ```

3. Fetch a newer version later (in the project folder):

   ```bat
   cd C:\Measurements\TaylorFlow_Auswertung
   git pull
   ```

   If `config.py` was changed locally, `git pull` only reports a conflict if
   the same file was also changed on GitHub.

## 1.3 Providing the measurement data

The evaluation reads the result files of the **video analysis** (manual of
the video analysis, chapter 4.2):

| File of the video analysis | Used here for |
|---|---|
| `output/Output_MassTransfer/Auswertung_Masse_<…>.csv` | mass transfer, `auswertung.py` |
| `output/Output_PressureCalibration/Auswertung_Druck_<…>.csv` | pressure calibration, `kalibrierung.py` |

The files do not have to be copied: at start-up a file selection window
opens in which they are chosen directly in the output folder of the video
analysis. To make the window open there, enter the folder in `config.py`:

```python
DIALOG_ORDNER = Path(r"C:\Measurements\Videoauswertung\output\Output_MassTransfer")
```

The measurement data of the existing test series are already in the
project folder under `data/raw/` and can be used to try everything out.
File structure: chapter 2.

## 1.4 Setting up

A separate Python environment (*virtual environment*, folder `.venv`) is
created in the project folder. It contains exactly the required packages
and does not interfere with any other Python installation.

1. Open the command prompt and change to the project folder:

   ```bat
   cd C:\Measurements\TaylorFlow_Auswertung
   ```

2. Create the environment (once) and activate it:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

   The prompt then starts with `(.venv)`. The activation only applies to
   this window; every new window needs `.venv\Scripts\activate` again.

3. Install the packages (once, takes one to two minutes):

   ```bat
   pip install -r requirements.txt
   ```

4. Check the installation:

   ```bat
   python -m pytest
   ```

   Expected: a line such as `40 passed`, no `failed`. The test evaluates
   the supplied measurement data completely and compares every number with
   the reference results in `tests/referenz/`. If it passes, the
   installation calculates correctly.

On Linux and macOS the activation is `source .venv/bin/activate`.

## 1.5 First start

With the environment activated, in the project folder:

```bat
python auswertung.py
```

The file selection window opens in `data/raw/`. Select one or more files
`Auswertung_Masse_….csv` (several with the Ctrl key held down) and click
**Open**. After about 20 seconds per file, tables and plots are in
`ergebnisse/` (chapter 3).

## 1.6 Working in VS Code or Spyder

The scripts can also be started from a development environment. In both
cases **the project folder must be the working directory**, otherwise
`config.py` is not found.

**VS Code**

1. Install VS Code from <https://code.visualstudio.com> and add the
   extension *Python* (by Microsoft).
2. **File** → **Open Folder** → project folder.
3. At the bottom right or with Ctrl+Shift+P → *Python: Select Interpreter*,
   choose the environment `.venv`.
4. Open `auswertung.py` and click **▷ Run Python File** at the top right.
   The output appears in the terminal below.

**Spyder**

1. Under **Tools** → **Preferences** → **Python interpreter**, enter the
   interpreter `…\TaylorFlow_Auswertung\.venv\Scripts\python.exe`. In the
   environment, also run `pip install spyder-kernels`.
2. **Run** → **Configuration per file** → *Working directory: the directory
   of the file being executed*.

## 1.7 Common errors

| Message | Cause | Remedy |
|---|---|---|
| `'python' is not recognized …` or the Microsoft Store opens | Python is not on the PATH | installer → Modify → *Add Python to environment variables* (1.1) |
| `ModuleNotFoundError: No module named 'thermo'` (or `numpy`, `yaml`) | environment not activated or packages not installed | `.venv\Scripts\activate`, then `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'config'` | script not started from the project folder | change to the project folder (1.4) or set the working directory (1.6) |
| `ModuleNotFoundError: No module named 'tkinter'` | Python installed without *tcl/tk* | installer → Modify → tick *tcl/tk and IDLE*, or use a fixed file list instead of the selection window (chapter 3.5) |
| `Keine Messdatei ausgewählt, Auswertung beendet.` | selection window cancelled | start again and select a file |
| `Dateiname '…' passt nicht zum Schema` | file name does not follow the naming scheme | chapter 2.2 |
| `In '…' fehlen die Spalten […]` | file does not come from the video analysis or is incomplete | chapter 2.3 |
| tests fail with very small deviations | other package versions return property data that differ in the last digit | use the versions from `requirements.txt`; tested with numpy 2.5, pandas 3.0, scipy 1.18, thermo 0.6 |
