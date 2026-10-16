# -*- coding: utf-8 -*-
"""
Plot-Auswahl und Anpassungen aus ``config.PLOTS``.

Jeder Plot hat einen Block mit Optionen. ``STANDARD`` enthält alle möglichen
Optionen mit ihren Standardwerten; was in ``config.PLOTS`` fehlt, wird von
hier ergänzt. Ein Tippfehler im Namen einer Option führt zu einer Meldung mit
allen möglichen Namen.

``auswertung.py`` und ``abbildung.py`` zeichnen beide über ``erzeuge``.
"""

from __future__ import annotations

from typing import Callable, Iterator

import pandas as pd

from .flaechen import kla_flaeche, modell_flaeche, nspez_flaeche, spalten_flaeche
from .heatmaps import STANDARD_FELDER, kennzahlen_heatmaps
from .profile import blasenlaengen_fit, druckprofil, stoffmenge
from .stil import BLAU_MITTEL, GRUEN, PlotStil

_ALLGEMEIN = dict(an=True, titel="auto", groesse_cm=None)
_FLAECHE = dict(blickwinkel=None, achsen=None, messpunkte=True, hoehenlinien=True, transparenz=0.85)

STANDARD: dict[str, dict] = {
    # --- je Betriebspunkt -----------------------------------------------------------
    "blasenlaengen_fit": dict(**_ALLGEMEIN, x_bereich_cm=None, y_bereich_mm=None, messwerte=True,
                              fit_ohne_offsets=True, fit_mit_offsets=True, druckkorrigiert=True,
                              kamerafenster=True, kennwertkasten=True, legende="unten"),
    "stoffmenge": dict(**_ALLGEMEIN, x_bereich_cm=None, y_bereich_umol=None, flaeche=True, farbe=GRUEN),
    "druckprofil": dict(**_ALLGEMEIN, x_bereich_cm=None, y_bereich=None, einheit="Pa", farbe=BLAU_MITTEL),
    # --- je Kanal -------------------------------------------------------------------
    "kla_flaeche": dict(**_ALLGEMEIN, **_FLAECHE, farbskala="plasma"),
    "nspez_flaeche": dict(**_ALLGEMEIN, **_FLAECHE, farbskala="coolwarm"),
    "modell_flaechen": dict(**_ALLGEMEIN, **_FLAECHE, farbskala="plasma", modelle=["yue_2007"]),
    "spalten_flaechen": {**_ALLGEMEIN, **_FLAECHE, "an": False, "farbskala": "viridis", "spalten": [
        dict(spalte="SlugLength_mean_m", beschriftung="Sluglänge $L_S$ [mm]", faktor=1000)]},
    "heatmaps": dict(**_ALLGEMEIN, felder=list(STANDARD_FELDER), farbskalen=None, beschriftungen=None),
}

JE_BETRIEBSPUNKT = ("blasenlaengen_fit", "stoffmenge", "druckprofil")
_GROESSE = {"blasenlaengen_fit": "groesse_profil_cm", "stoffmenge": "groesse_profil_cm",
            "druckprofil": "groesse_profil_cm", "heatmaps": "groesse_heatmaps_cm"}


def mische(name: str, block: dict | bool | None) -> dict:
    """
    Optionen eines Plots: Standardwerte, überschrieben durch den Block aus ``config.PLOTS``.

    ``block`` darf auch ``True``/``False`` sein (nur ein- oder ausschalten).
    """
    if name not in STANDARD:
        raise KeyError(f"Unbekannter Plot '{name}' in config.PLOTS. Möglich: {list(STANDARD)}")
    if isinstance(block, bool) or block is None:
        block = {"an": bool(block)}
    unbekannt = sorted(set(block) - set(STANDARD[name]))
    if unbekannt:
        raise KeyError(f"Unbekannte Option {unbekannt} für den Plot '{name}'. "
                       f"Möglich: {sorted(STANDARD[name])}")
    return {**STANDARD[name], **block}


def _stil_fuer(name: str, opt: dict, stil: PlotStil) -> PlotStil:
    aenderung = {}
    if opt.get("groesse_cm"):
        aenderung[_GROESSE.get(name, "groesse_3d_cm")] = tuple(opt["groesse_cm"])
    if opt.get("blickwinkel"):
        aenderung["blickwinkel_3d"] = tuple(opt["blickwinkel"])
    return stil.mit(**aenderung) if aenderung else stil


def _titel(opt: dict, automatisch: str) -> str:
    return automatisch if opt["titel"] == "auto" else str(opt["titel"] or "")


def _ohne(opt: dict, *schluessel) -> dict:
    weg = {"an", "titel", "groesse_cm", "blickwinkel", *schluessel}
    return {k: v for k, v in opt.items() if k not in weg}


def erzeuge(name: str, opt: dict, stil: PlotStil, betriebspunkte: pd.DataFrame,
            profile: pd.DataFrame | None = None, betriebspunkt: str | None = None,
            kanal: str = "", modelldatei=None, meldung=print) -> Iterator[tuple[str, Callable]]:
    """
    Liefert (Dateiname, Funktion, die die Figure erzeugt) für einen Plot.

    Plots je Betriebspunkt brauchen ``profile`` und ``betriebspunkt``;
    ``modell_flaechen`` und ``spalten_flaechen`` liefern eine Figure je Eintrag.
    """
    st = _stil_fuer(name, opt, stil)
    bp = betriebspunkte

    if name in JE_BETRIEBSPUNKT:
        from ..ergebnisse import profil_eines_betriebspunkts
        zeile = bp[bp["Config"] == betriebspunkt]
        if zeile.empty:
            raise KeyError(f"Betriebspunkt '{betriebspunkt}' nicht in {kanal}. "
                           f"Vorhanden: {list(bp['Config'])}")
        profil = profil_eines_betriebspunkts(profile, betriebspunkt)
        titel = _titel(opt, f"{kanal} | {betriebspunkt}")
        if name == "blasenlaengen_fit":
            yield f"blasenlaenge_{betriebspunkt}", lambda: blasenlaengen_fit(
                profil, zeile.iloc[0], st, titel, **_ohne(opt))
        elif name == "stoffmenge":
            yield f"stoffmenge_{betriebspunkt}", lambda: stoffmenge(profil, st, titel, **_ohne(opt))
        else:
            yield f"druck_{betriebspunkt}", lambda: druckprofil(profil, st, titel, **_ohne(opt))
        return

    titel = _titel(opt, kanal)
    if name == "kla_flaeche":
        yield "kla_flaeche", lambda: kla_flaeche(bp, st, titel, **_ohne(opt))
    elif name == "nspez_flaeche":
        yield "nspez_flaeche", lambda: nspez_flaeche(bp, st, titel, **_ohne(opt))
    elif name == "heatmaps":
        yield "heatmaps", lambda: kennzahlen_heatmaps(profile, bp, st, titel, **_ohne(opt))
    elif name == "modell_flaechen":
        from ..literatur import LITERATURMODELLE
        for modell in opt["modelle"] or []:
            geltung = LITERATURMODELLE[modell].geometrie if modell in LITERATURMODELLE else "beide"
            if geltung != "beide" and not (bp["Geometrie"] == geltung).all():
                meldung(f"  modell_{modell}: übersprungen (Modell nur für {geltung}e Kanäle)")
                continue
            yield f"modell_{modell}", lambda m=modell: modell_flaeche(
                bp, m, st, titel, modelldatei=modelldatei, **_ohne(opt, "modelle"))
    elif name == "spalten_flaechen":
        for eintrag in opt["spalten"] or []:
            eintrag = dict(eintrag)
            spalte = eintrag.pop("spalte")
            yield f"flaeche_{spalte}", lambda s=spalte, e=eintrag: spalten_flaeche(
                bp, s, st, titel, **e, **_ohne(opt, "spalten"))
