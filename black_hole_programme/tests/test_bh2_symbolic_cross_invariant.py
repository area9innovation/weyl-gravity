"""Fast-rail (Tier 1) tests for BH2_SYMBOLIC_CROSS_INVARIANT.

All checks are exact algebra on the recorded closed form -- no mode rebuild --
so the suite is a sub-second regression net.  Includes decisive mutations
(wrong pole, wrong conjugation sign, wrong normalization) and the BH-3
vocabulary lock.
"""
import json
from pathlib import Path

import sympy as sp
import pytest

HERE = Path(__file__).resolve().parent.parent
CERT = HERE / "certificates" / "BH2_SYMBOLIC_CROSS_INVARIANT.json"
w = sp.Symbol("omega")

pytestmark = pytest.mark.skipif(not CERT.exists(),
                                reason="certificate not built yet")


def _cert():
    return json.loads(CERT.read_text())


def _cross():
    return sp.sympify(_cert()["cross_of_omega"])


def test_a_equals_i_cross():
    c = _cert()
    assert sp.cancel(sp.sympify(c["a_of_omega"]) - sp.I * _cross()) == 0


def test_closed_form_matches_recorded_samples():
    c = _cert()
    cross = _cross()
    for wstr, vstr in c["samples"].items():
        wv = sp.sympify(wstr)
        assert sp.cancel(cross.subs(w, wv) - sp.sympify(vstr)) == 0


def test_recovers_both_certified_fixtures():
    c = _cert()
    cross = _cross()
    fix = json.loads((HERE / "certificates"
                      / "BH2A_COMPOSED_REPAIR.json").read_text())
    for tag in ("3/5", "2/7"):
        p, q = tag.split("/")
        wv = sp.Rational(int(p), int(q))
        assert sp.cancel(cross.subs(w, wv)
                         - sp.sympify(fix["fixtures"][tag]["cross"])) == 0


def test_no_real_zeros_or_poles_except_origin():
    cross = _cross()
    zeros = sp.roots(sp.Poly(sp.numer(sp.cancel(cross)), w))
    poles = sp.roots(sp.Poly(sp.denom(sp.cancel(cross)), w))
    assert not [z for z in zeros if sp.im(z) == 0 and sp.re(z) != 0]
    assert not [p for p in poles if sp.im(p) == 0]
    assert zeros.get(sp.Integer(0)) == 1


def test_conjugate_frequency_law():
    cross = _cross()
    a = sp.I * cross
    for wv in (sp.Rational(1, 2), sp.Rational(3, 5), sp.Rational(2, 7),
               sp.Rational(5, 3), sp.Rational(7, 4)):
        assert sp.cancel(cross.subs(w, -wv)
                         - sp.conjugate(cross.subs(w, wv))) == 0
        assert sp.cancel(a.subs(w, -wv) + sp.conjugate(a.subs(w, wv))) == 0


# -------------------- decisive mutations (must be REJECTED) ----------------

def test_mutation_shifted_pole_rejected():
    cross = _cross()
    num = sp.numer(sp.cancel(cross))
    den = sp.denom(sp.cancel(cross))
    mutated = sp.cancel(num / den.subs(sp.I, 2 * sp.I))
    # the shifted-pole form must disagree with the true value at some fixture
    assert sp.cancel(mutated.subs(w, sp.Rational(3, 5))
                     - cross.subs(w, sp.Rational(3, 5))) != 0


def test_mutation_wrong_conjugation_sign_rejected():
    cross = _cross()
    # cross(-w) = +conj(cross(w)) is the WRONG law; must fail generically
    wv = sp.Rational(3, 5)
    assert sp.cancel(cross.subs(w, -wv) + sp.conjugate(cross.subs(w, wv))) != 0


def test_mutation_scaled_normalization_rejected():
    c = _cert()
    cross = _cross()
    fix = json.loads((HERE / "certificates"
                      / "BH2A_COMPOSED_REPAIR.json").read_text())
    tgt = sp.sympify(fix["fixtures"]["3/5"]["cross"])
    assert sp.cancel(2 * cross.subs(w, sp.Rational(3, 5)) - tgt) != 0


def test_degree_is_minimal_recorded():
    c = _cert()
    cross = _cross()
    assert sp.degree(sp.numer(sp.cancel(cross)), w) == c["degree"]["numerator"]
    assert sp.degree(sp.denom(sp.cancel(cross)), w) == c["degree"]["denominator"]
    assert c["held_out_prediction_points"] >= 1


def test_bh3_vocabulary_lock():
    # forbidden promotions must not appear as CLAIMS.  The not_claimed subtree
    # is a disclaimer that legitimately names excluded concepts, so it is
    # stripped before the scan (naming what is NOT established is the opposite
    # of promoting it).
    banned = ("quasinormal", "ringdown", "scattering", "stability", "ghost",
              "unitarity", "particle", "graviton")
    c = _cert()
    c.pop("not_claimed", None)
    blob = json.dumps(c).lower()
    for term in banned:
        assert term not in blob, f"forbidden BH-3 term promoted: {term}"
