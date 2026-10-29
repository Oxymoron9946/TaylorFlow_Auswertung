# Editing the manual

German version: [HANDBUCH_BEARBEITEN.md](../HANDBUCH_BEARBEITEN.md)

The manual consists of text files (`docs/*.md` in German, `docs/en/*.md` in
English, format *Markdown*). The PDFs `docs/Handbuch_TaylorFlow.pdf` and
`docs/Handbuch_TaylorFlow_en.pdf` are **generated automatically** from them. Only edit
the `.md` files, never the PDFs.

## Editing in the browser, nothing to install

1. On GitHub, open the folder **docs** (German) or **docs/en** (English) and
   click a chapter (list below). GitHub shows it fully formatted.
2. Click the **pencil** (*Edit this file*) at the top right.
3. Edit the text. Check the result with the **Preview** tab.
4. Green **Commit changes…** → briefly describe the change →
   **Commit changes**.
5. After about **3 minutes** the new PDFs (German and English) are in the
   folder `docs`. The **Actions** tab shows the progress: yellow dot =
   running, green tick = done, red ✗ = error (see below).

Editing several chapters one after another is fine; the PDFs are simply
rebuilt again afterwards.

**Adding an image:** open `docs/bilder` → **Add file → Upload files** →
upload the image. Insert it in the text with
`![Caption](bilder/name.png)` (the English chapters use their own folder `docs/en/bilder`).

## Chapters

| File in `docs/en/` | Chapter |
|---|---|
| `01_installation.md` | 1 Installation |
| `02_messdaten.md` | 2 Measurement data |
| `03_erste_auswertung.md` | 3 First evaluation |
| `04_plots.md` | 4 Selecting and adjusting plots |
| `05_konfiguration.md` | 5 Configuration |
| `06_ergebnisse.md` | 6 Results |
| `07_methodik.md` | 7 Methodology |
| `08_grenzen.md` | 8 Limitations |
| `09_literaturvergleich.md` | 9 Literature comparison and own models |
| `10_druckkalibrierung.md` | 10 Pressure calibration |
| `11_monolith.md` | 11 Monolith |
| `12_erweitern.md` | 12 Program structure and extension |

The German chapters in `docs/` have the same file names. Neither version is
translated automatically: if you change one, update the other one as well
where needed.

## Markdown in brief

| You write | Result |
|---|---|
| `## 2.3 Heading` | section heading (`#` chapter, `##` section, `###` subsection) |
| `**bold**`, `*italic*` | **bold**, *italic* |
| `- item` or `1. item` | bullet list or numbered list |
| `` `config.m` `` | program text `config.m` |
| `[text](https://…)` | link |
| `![caption](bilder/x.png)` | image with caption |
| `\| a \| b \|` | table row (easiest: copy an existing table) |
| `$p_{tr} = p - p_v$` | inline formula (LaTeX syntax); `$$…$$` on its own line |
| `![](bilder/x.png){width=49%}` | image at half width; `{width=…}` only works in the PDF and shows as plain text in the preview |

An **empty line** separates paragraphs; a single line break is ignored.

## If something goes wrong

- **Red ✗ under Actions:** click the run → expand the step *PDFs bauen*;
  the last lines usually point to the place in the text. Fix the file you
  changed last and commit again. The previous PDF stays in place until then.
- **Rebuild the PDFs by hand:** Actions → *Handbuch-PDF bauen* → **Run workflow**.
- **New chapter:** create `docs/NN_name.md` *and* `docs/en/NN_name.md`, and add
  the name to the list `KAPITEL = [...]` in `docs/build_pdf.py`; otherwise it
  is missing from the PDF.

## Optional: on your own computer

- **View and edit:** [VS Code](https://code.visualstudio.com) → open the
  folder `docs` → open a chapter → `Ctrl+K`, then `V`: text on the left,
  formatted preview on the right.
- If you work with Git: **pull** before editing, because the automatic PDF
  build adds its own commit after every change.
- Build the PDFs locally (needs MiKTeX or TeX Live and the DejaVu fonts):
  `pip install -r docs/requirements.txt`, then `python docs/build_pdf.py`
  or `python docs/build_pdf.py en`.
