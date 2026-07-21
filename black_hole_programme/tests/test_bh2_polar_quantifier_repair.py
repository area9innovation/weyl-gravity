"""Fast-rail (Tier 1) tests for BH2_POLAR_QUANTIFIER_REPAIR.

Sub-second: exact algebra on the certificate fields plus the a!=0 proof.  No
mode rebuild.  Guards the fail-closed quantifier: the universal
no-real-exceptional-frequency flag must stay FALSE, a!=0 must be a genuine
all-real-omega theorem, and the null-cone fixture theorem must be preserved.
"""
import json
from pathlib import Path

import sympy as sp
import pytest

HERE = Path(__file__).resolve().parent.parent
CERT = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"
POLAR = HERE / "certificates" / "BH2_POLAR_CROSS_COVECTOR.json"
w = sp.Symbol("omega")

pytestmark = pytest.mark.skipif(not CERT.exists(),
                                reason="certificate not built yet")


def _cert():
    return json.loads(CERT.read_text())


def test_universal_flags_are_fail_closed():
    f = _cert()["claim_flags"]
    assert f["generic_real_frequency_certified"] is False
    assert f["no_real_exceptional_frequency_certified"] is False


def test_disposition_is_fixture_theorem_plus_shortfall():
    assert _cert()["disposition"] == "NINE_FIXTURE_THEOREM + UNIVERSAL_SHORTFALL"


def test_covector_nonzero_is_all_real_omega_theorem():
    c = _cert()["universal_results"]["covector_nonzero_all_real_omega"]
    assert c["proven"] is True
    assert c["denominator_real_zeros"] == []
    # P, Q share no real root: resultant nonzero, and re-derive it here
    P, Q = 64 * w**3 - 240 * w, -200 * w**2 + 49
    assert sp.resultant(P, Q, w) != 0
    assert sp.sympify(c["resultant_P_Q"]) == sp.resultant(P, Q, w)


def test_fixture_theorem_preserved_nine_frequencies():
    ft = _cert()["preserved_fixture_theorem"]
    assert ft["over_determination_points"] >= 9
    for wtag, rec in ft["per_frequency"].items():
        assert rec["inertia"] == [2, 1]
        assert rec["S"] == "0"
        assert rec["a_nonzero"] is True
        assert rec["detK_nonzero"] is True


def test_S_is_null_recomputed_from_polar_records():
    # independent re-derivation of S=0 from the imported exact (a,K)
    src = json.loads(POLAR.read_text())
    for wtag in src["K_records"]:
        a = sp.Matrix([sp.sympify(x) for x in src["a_records"][wtag]])
        K = sp.Matrix([[sp.sympify(x) for x in row]
                       for row in src["K_records"][wtag]])
        S = sp.cancel((a.T * K.solve(a.conjugate()))[0, 0])
        assert S == 0, f"S != 0 at {wtag}"


def test_obstruction_frame_not_rational():
    o = _cert()["obstruction_to_universal_signature"]
    assert o["sampler_frame_is_rational"] is False
    for name in ("t1", "t2", "t3"):
        assert "NO rational fit" in o["held_out_reconstruction"][name]


def test_provenance_hashes_present():
    p = _cert()["provenance"]
    for k in ("polar_covector_sha256", "polar_fixture_sha256"):
        assert len(p[k]) == 64
    assert _cert()["repairs"]["target_sha256"] == p["polar_covector_sha256"]


def test_missing_object_named():
    m = _cert()["missing_object"]
    assert "canonical" in m["route_A_canonical_frame"].lower()
    assert "gauge" in m["route_B_structural_identity"].lower() \
        or "radical" in m["route_B_structural_identity"].lower()


def test_bh3_vocabulary_lock():
    banned = ("quasinormal", "ringdown", "scattering", "stability", "ghost",
              "unitarity", "particle", "graviton")
    c = _cert()
    c.pop("not_claimed", None)          # disclaimers may name excluded concepts
    blob = json.dumps(c).lower()
    for term in banned:
        assert term not in blob, f"forbidden BH-3 term promoted: {term}"
