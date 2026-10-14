# -*- coding: utf-8 -*-
"""Schnelle Tests einzelner Bausteine mit synthetischen Daten."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from taylorflow.einlesen import messreihe_aus_dateiname
from taylorflow.fits import blase_v2, entferne_einbrueche, fit_blasenlaenge
from taylorflow.kla import kla_profile
from taylorflow.literatur import LITERATURMODELLE, modelleingaben, vandu
from taylorflow.modellvergleich import fit_potenzansatz, statistik
from taylorflow.parameter import AuswerteParameter


# --- Dateinamen ------------------------------------------------------------------

def test_dateiname_wird_zerlegt():
    r = messreihe_aus_dateiname(Path("Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_800um.csv"))
    assert (r.material, r.geometrie, r.d_kanal_um, r.laenge_cm, r.co2_mol_prozent, r.nadel_um) == \
        ("PVC", "circular", 1000, 72, 20, 800)
    assert r.kanal == "PVC_Rund_1000um_72cm_20molCO2_800um"
    assert r.kalibrier_key == "PVC_circular_1000um_800um"


def test_kanalname_unterscheidet_laenge_und_co2():
    a = messreihe_aus_dateiname(Path("Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_800um.csv"))
    b = messreihe_aus_dateiname(Path("Auswertung_Masse_PVC_R_1000um_50cm_10molCO2_800um.csv"))
    assert a.kanal != b.kanal


@pytest.mark.parametrize("name", ["Auswertung_Masse_PVC_X_1000um_72cm_20molCO2_800um.csv",
                                  "Messung_PVC.csv"])
def test_falscher_dateiname_bricht_ab(name):
    with pytest.raises(ValueError):
        messreihe_aus_dateiname(Path(name))


# --- Fits ------------------------------------------------------------------------

def test_blasenfit_findet_parameter_wieder():
    z = np.linspace(0.005, 0.55, 120)
    wahr = (2.0e-3, 0.3e-3, 0.08, 1.0e-4)
    y = blase_v2(z, *wahr) + np.random.default_rng(1).normal(0, 2e-6, z.size)
    f, r2, _, popt, info = fit_blasenlaenge(z, y, np.full(z.size, 3e-6), 0.72, serien_offsets=False)
    assert info["model_version"] == 2
    assert r2 > 0.99
    np.testing.assert_allclose(popt, wahr, rtol=0.1)


def test_einbruch_wird_interpoliert():
    x = np.array([1.0, 1.0, 0.05, 1.0, 1.0])
    np.testing.assert_allclose(entferne_einbrueche(x), [1, 1, 1, 1, 1])


# --- kLa -------------------------------------------------------------------------

def test_kla_log_mean_fuer_exponentiellen_abfall():
    """ΔC(z) = ΔC0 · exp(−k t(z)) mit konstanter Geschwindigkeit ergibt kLa_log = k."""
    p = AuswerteParameter()
    z = np.arange(0, 0.5, 1e-3)
    U = np.full(z.size, 0.2)
    k = 2.0
    C_star = np.full(z.size, 10.0)
    dC = C_star * np.exp(-k * z / U)
    erg = kla_profile(z, U, np.full(z.size, 2e-3), np.gradient(10.0 - dC, z) * 1e-9,
                      dC, 10.0, 1e-9, C_star, p)
    assert erg["kLa_log_mean"] == pytest.approx(k, rel=1e-3)


# --- Literatur und Modellvergleich -------------------------------------------------

def test_registry_deckt_alle_spalten_ab():
    eingaben = modelleingaben(0.3, 2e-3, 1e-3, 1e-3, 2e-9, "eckig", 0.1, 0.1, AuswerteParameter())
    for m in LITERATURMODELLE.values():
        assert np.isfinite(m.funktion(eingaben)) or m.geometrie == "rund"
    assert LITERATURMODELLE["vandu"].funktion(eingaben) == vandu(0.3, 2e-3, 1e-3, 1e-3, 2e-9)


def test_potenzansatz_trifft_exakte_daten():
    rng = np.random.default_rng(0)
    d = pd.DataFrame({"x1": rng.uniform(0.05, 0.3, 30), "x2": rng.uniform(0.02, 0.25, 30)})
    d["y"] = 3.0 * d.x1 ** 0.5 * d.x2 ** 0.9
    m = fit_potenzansatz(d, "y", ["x1", "x2"], name="test")
    assert m.koeffizient == pytest.approx(3.0)
    np.testing.assert_allclose(m.exponenten, [0.5, 0.9])
    assert m.mape_prozent == pytest.approx(0.0, abs=1e-9)


def test_statistik():
    s = statistik([1.0, 2.0, 4.0], [1.1, 1.8, 4.0], band_prozent=15)
    assert s["n"] == 3
    assert s["MAPE_%"] == pytest.approx((10 + 10 + 0) / 3)
    assert s["im_Band_%"] == pytest.approx(100.0)
