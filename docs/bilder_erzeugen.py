# -*- coding: utf-8 -*-
"""Erzeugt alle Bilder des Handbuchs aus den mitgelieferten Messdaten.

Aufruf (aus dem Projektordner):
    python docs/bilder_erzeugen.py        deutsche Beschriftung -> docs/bilder/
    python docs/bilder_erzeugen.py en     englische Beschriftung -> docs/en/bilder/

Die Auswertung läuft in einem temporären Ordner; config.py und der
Ergebnisordner bleiben unverändert. Dauer: etwa eine Minute.
"""

import sys
import tempfile
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

DOCS = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS.parent))

import config  # noqa: E402
import abbildung  # noqa: E402
import literaturvergleich  # noqa: E402
import monolith  # noqa: E402
from taylorflow import ergebnisse, protokoll  # noqa: E402
from taylorflow.einlesen import finde_messreihen, lade_ausschluesse  # noqa: E402
from taylorflow.parameter import AuswerteParameter  # noqa: E402
from taylorflow.pipeline import werte_kanal_aus  # noqa: E402

KANAL = "Glas_Eckig_1000um_72cm_20molCO2_600um"
BP = "Gas_0_07_Liq_0_111"
DPI = 150

#: Name -> (Plot, Anpassungen). Ohne Anpassungen = Standarddarstellung aus config.PLOTS.
BILDER = {
    # Standarddarstellung (Galerie und je Plot das große Bild)
    "blasenlaengen_fit": ("blasenlaengen_fit", {}),
    "stoffmenge": ("stoffmenge", {}),
    "druckprofil": ("druckprofil", {}),
    "kla_flaeche": ("kla_flaeche", {}),
    "nspez_flaeche": ("nspez_flaeche", {}),
    "modell_flaeche": ("modell_flaechen", {}),
    "heatmaps": ("heatmaps", {}),
    "spalten_flaeche": ("spalten_flaechen", {}),
    # Beispiele für Anpassungen
    "blasenlaengen_fit_angepasst": ("blasenlaengen_fit", dict(
        x_bereich_cm=(0, 40), fit_ohne_offsets=False, kennwertkasten=False, legende="upper right")),
    "stoffmenge_angepasst": ("stoffmenge", dict(flaeche=False, farbe="tab:red", x_bereich_cm=(0, 30))),
    "druckprofil_angepasst": ("druckprofil", dict(einheit="mbar", titel="")),
    "kla_flaeche_angepasst": ("kla_flaeche", dict(
        farbskala="viridis", blickwinkel=(35, 220), achsen=dict(z=(0, 1.5)), hoehenlinien=False)),
    "nspez_flaeche_angepasst": ("nspez_flaeche", dict(
        farbskala="cividis", messpunkte=False, transparenz=1.0)),
    "heatmaps_angepasst": ("heatmaps", dict(
        felder=["kla", "z95", "n_spez_mol_s_m3"],
        beschriftungen={"n_spez_mol_s_m3": r"$\dot n_{\mathrm{spez}}$ [mol/(s m³)]"},
        farbskalen=dict(kla="viridis"))),
}


#: Markierungen im Blasenlängen-Fit: Nummer -> (Ziel x [cm], y [mm], Nummer x, y); None = ohne Pfeil
MARKEN = {
    1: ((4.5, 1.552), (9.5, 1.575)),        # Messwerte
    2: ((40.0, 1.556), (36.0, 1.588)),      # Fit ohne Offsets
    3: ((47.0, 1.556), (46.0, 1.528)),      # Fit mit Offsets
    4: ((62.0, 1.522), (64.0, 1.497)),      # druckkorrigiert
    5: (None, (7.0, 1.622)),                # Kamerafenster
    6: ((58.8, 1.620), (53.5, 1.622)),      # Kennwertkasten
}


def markiertes_bild(tmp, ziel, sprache):
    """Blasenlängen-Fit mit nummerierten Markierungen der Bildelemente."""
    import matplotlib.pyplot as plt
    from taylorflow import plots as pl

    stil = pl.PlotStil(**config.STIL).mit(sprache=sprache, dpi=DPI, formate=("png",))
    bp = ergebnisse.lade_betriebspunkte(tmp, KANAL)
    profil = ergebnisse.profil_eines_betriebspunkts(ergebnisse.lade_profile(tmp, KANAL), BP)
    fig = pl.blasenlaengen_fit(profil, bp[bp["Config"] == BP].iloc[0], stil, f"{KANAL} | {BP}")
    ax = fig.axes[0]
    kreis = dict(boxstyle="circle,pad=0.25", fc="#C8102E", ec="white", lw=0.8)
    for nr, (ziel_xy, text_xy) in MARKEN.items():
        ax.annotate(str(nr), xy=ziel_xy or text_xy, xytext=text_xy, color="white", fontweight="bold",
                    fontsize=9, ha="center", va="center", bbox=kreis, zorder=20,
                    arrowprops=dict(arrowstyle="-|>", color="#C8102E", lw=1.2) if ziel_xy else None)
    fig.text(0.012, 0.07, "7", color="white", fontweight="bold", fontsize=9, ha="center", va="center",
             bbox=kreis, zorder=20)
    fig.savefig(ziel / "blasenlaengen_fit_markiert.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main(sprache="de"):
    warnings.filterwarnings("ignore")
    ziel = DOCS / "bilder" if sprache == "de" else DOCS / "en" / "bilder"
    ziel.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    print(f"Auswertung der mitgelieferten Messdaten in {tmp} …")
    aus = lade_ausschluesse(config.AUSSCHLUSS_DATEI)
    protokoll.starte(tmp / "protokoll.txt")
    for r in finde_messreihen(config.ROHDATEN_ORDNER, "Masse"):
        e = werte_kanal_aus(r, AuswerteParameter.aus_dict(config.PARAMETER), aus,
                            config.KALIBRIER_DATENBANK, ausgabe=lambda *a: None)
        ergebnisse.speichere(e, tmp, aus, ausgabe=lambda *a: None)

    stil = dict(sprache=sprache, dpi=DPI, formate=("png",))
    for name, (plot, anpassungen) in BILDER.items():
        abbildung.erzeuge_abbildung(KANAL, plot, BP, anpassungen, stil, ziel, name, ergebnis_ordner=tmp)
    abbildung.erzeuge_abbildung(KANAL, "blasenlaengen_fit", BP, {}, dict(stil, sprache="en", titel_anzeigen=False),
                                ziel, "blasenlaengen_fit_englisch", ergebnis_ordner=tmp)

    markiertes_bild(tmp, ziel, sprache)

    # Bilder der Zusatzskripte: Skripte mit temporärem Ergebnisordner ausführen
    config.ERGEBNIS_ORDNER = tmp
    config.STIL = {**config.STIL, **stil}
    literaturvergleich.main()
    monolith.main()
    for quelle, name in [("vergleich/paritaet_yue_2007.png", "paritaet.png"),
                         (f"vergleich/eigenes_modell_{config.VERGLEICH['eigener_fit']['name']}.png",
                          "eigenes_modell.png"),
                         ("monolith/kla_monolith.png", "monolith_kla.png"),
                         ("monolith/paritaet_monolith_kanal.png", "monolith_paritaet.png")]:
        (ziel / name).write_bytes((tmp / quelle).read_bytes())
    print(f"Bilder in {ziel}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "de")
