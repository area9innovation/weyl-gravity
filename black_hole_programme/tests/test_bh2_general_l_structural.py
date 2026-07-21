"""Fast-rail (Tier 1) tests for BH2_GENERAL_L_STRUCTURAL.

Sub-second: certificate-field checks plus the exact exceptional-harmonic algebra
(no mode rebuild).  Guards the disposition (pairing NOT_ACTIVATED, no
extrapolation) and the proven symbolic-l structure.
"""
import json
from pathlib import Path

import sympy as sp
import pytest

HERE = Path(__file__).resolve().parent.parent
CERT = HERE / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json"
x = sp.Symbol("x")

pytestmark = pytest.mark.skipif(not CERT.exists(),
                                reason="certificate not built yet")


def _cert():
    return json.loads(CERT.read_text())


def test_disposition_and_pairing_not_activated():
    c = _cert()
    assert c["disposition"] == "AXIAL_SYMBOLIC_L_PROVEN + PAIRING_NOT_ACTIVATED"
    assert c["pairing_not_activated"]["no_extrapolation_from_samples"] is True
    assert c["claim_flags"]["generic_l_cross_pairing_certified"] is False


def test_rw_branch_symbolic_l():
    rw = _cert()["proven_axial_generic_l"]["einstein_rw_branch"]
    assert rw["rw_master_potential"] == "B*(Lambda/r**2 - 6*m/r**3)"
    assert rw["master_proportionality_factor"] == "-r**6"
    assert rw["horizon_exponents_lambda_independent"] is True
    assert rw["rw_ingoing_dimension"] == 1
    # exponents are +-2imw
    w, m = sp.symbols("omega m")
    exps = {sp.simplify(sp.sympify(e)) for e in rw["horizon_exponents"]}
    assert exps == {sp.simplify(2 * sp.I * m * w), sp.simplify(-2 * sp.I * m * w)}


def test_extra_branch_residue_lambda_independent():
    ex = _cert()["proven_axial_generic_l"]["extra_branch"]
    assert ex["residue_lambda_independent"] is True
    assert set(ex["extra_branch_residue_spectrum"]) == {
        "0 (x2)", "-4*I*m*omega", "-2 - 4*I*m*omega"}


def test_exceptional_harmonics_vanish_exactly():
    # independent of the certificate: the exact harmonic degeneration
    legP = {0: sp.Integer(1), 1: x, 2: (3 * x**2 - 1) / 2,
            3: (5 * x**3 - 3 * x) / 2}
    for l, P in legP.items():
        S = sp.expand(-(1 - x**2) * sp.diff(P, x))
        H2 = sp.expand(l * (l + 1) * P - 2 * x * sp.diff(P, x))
        if l == 0:
            assert S == 0 and H2 == 0
        elif l == 1:
            assert S != 0 and H2 == 0
        else:
            assert S != 0 and H2 != 0
    assert _cert()["proven_axial_generic_l"]["exceptional_set"]["exceptional_l"] \
        == [0, 1]


def test_stop_condition_gate_fixture_only():
    # the cert must depend on the fixture-only polar repair
    c = _cert()
    assert "fixture-only" in c["stop_condition_branch"]
    assert c["provenance"]["polar_repair_sha256"]
    assert len(c["provenance"]["polar_repair_sha256"]) == 64


def test_polar_detailed_reduction_not_overclaimed():
    c = _cert()
    assert c["claim_flags"]["polar_detailed_reduction_certified"] is False
    assert "polar_detailed_symbolic_lambda_reduction" in c["not_claimed"]


def test_bh3_vocabulary_lock():
    banned = ("quasinormal", "ringdown", "scattering", "stability", "ghost",
              "unitarity", "particle", "graviton")
    c = _cert()
    c.pop("not_claimed", None)
    blob = json.dumps(c).lower()
    for term in banned:
        assert term not in blob, f"forbidden BH-3 term promoted: {term}"
