"""Fast-rail (Tier 1) tests for BH2_POLAR_CROSS_COVECTOR.

Exact linear algebra on the recorded (a, K) matrices -- no mode rebuild -- so
sub-second.  Includes the null-covector invariant, signature, the non-null
mutation, and the BH-3 vocabulary lock.
"""
import json
from pathlib import Path

import sympy as sp
import pytest

HERE = Path(__file__).resolve().parent.parent
CERT = HERE / "certificates" / "BH2_POLAR_CROSS_COVECTOR.json"
w = sp.Symbol("omega")

pytestmark = pytest.mark.skipif(not CERT.exists(),
                                reason="certificate not built yet")


def _cert():
    return json.loads(CERT.read_text())


def _ak(wtag):
    c = _cert()
    a = sp.Matrix([sp.sympify(x) for x in c["a_records"][wtag]])
    K = sp.Matrix([[sp.sympify(x) for x in row] for row in c["K_records"][wtag]])
    return a, K


def test_cross_covector_is_K_null_everywhere():
    c = _cert()
    assert c["over_determination_points"] >= 3
    for wtag in c["K_records"]:
        a, K = _ak(wtag)
        # nonzero covector
        assert any(sp.cancel(x) != 0 for x in a)
        # null in the extra-block metric
        S = sp.cancel((a.T * K.inv() * a.conjugate())[0, 0])
        assert S == 0, f"S != 0 at {wtag}"


def test_extra_block_hermitian_signature_2_1_nondegenerate():
    for wtag, _ in _cert()["K_records"].items():
        a, K = _ak(wtag)
        Kp = sp.I * K
        assert sp.simplify(Kp - Kp.conjugate().T) == sp.zeros(3, 3)
        assert sp.cancel(K.det()) != 0
        signs = []
        for ev, m in Kp.eigenvals().items():
            signs += [1 if complex(sp.N(ev, 30)).real > 0 else -1] * int(m)
        assert (signs.count(1), signs.count(-1)) == (2, 1)


def test_recovers_polar_fixtures():
    c = _cert()
    fix = json.loads((HERE / "certificates"
                      / "BH2B_COMPOSED_REPAIR.json").read_text())
    for tag in ("3/5", "2/7"):
        if tag not in c["a_records"]:
            continue
        a, _ = _ak(tag)
        for j in range(3):
            assert sp.cancel(a[j] - sp.sympify(fix["fixtures"][tag][f"E|X{j}"])) == 0


def test_EX1_native_form_recovers_fixtures():
    c = _cert()
    ex1 = sp.sympify(c["EX1_native_frame_rational"])
    fix = json.loads((HERE / "certificates"
                      / "BH2B_COMPOSED_REPAIR.json").read_text())
    for tag in ("3/5", "2/7"):
        p, q = tag.split("/")
        assert sp.cancel(ex1.subs(w, sp.Rational(int(p), int(q)))
                         - sp.sympify(fix["fixtures"][tag]["E|X1"])) == 0


def test_mutation_nonnull_rejected():
    # perturbing a off the K-null cone must make S != 0
    c = _cert()
    wtag = next(iter(c["K_records"]))
    a, K = _ak(wtag)
    a_mut = a + sp.Matrix([1, 0, 0])
    S_mut = sp.cancel((a_mut.T * K.inv() * a_mut.conjugate())[0, 0])
    assert S_mut != 0
    assert c["mutation_nonnull_rejected"] is True


def test_no_real_exceptional_frequency():
    assert _cert()["real_exceptional_frequencies"] == []


def test_bh3_vocabulary_lock():
    banned = ("quasinormal", "ringdown", "scattering", "stability", "ghost",
              "unitarity", "particle", "graviton")
    c = _cert()
    c.pop("not_claimed", None)
    blob = json.dumps(c).lower()
    for term in banned:
        assert term not in blob, f"forbidden BH-3 term promoted: {term}"
