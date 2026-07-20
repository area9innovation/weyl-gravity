"""Tier-1 fast rail for BH2C_METRIC_ALL_ORDERS.

Re-derives the exponents, the recurrence-theorem coefficient and the omega=0
indicial DIRECTLY from the recorded master-ODE coefficient strings (no
geometry rebuild), then checks schema, claim-flag discipline and the BH-3
vocabulary lock.  The heavy independent geometry rail lives in
verify_bh2c_metric_all_orders.py.
"""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2C_METRIC_ALL_ORDERS.json").read_text())

r = sp.Symbol("r")
w = sp.Symbol("omega")


def _master():
    c2, c1, c0 = (sp.sympify(s, locals={"omega": w, "I": sp.I})
                  for s in CERT["master_ode"]["coefficients"])
    return c2, c1, c0


class TestFastRail(unittest.TestCase):
    def test_schema_and_token(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh2c-metric-all-orders-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2C_METRIC_ALL_ORDERS_ONE_POWER_POLYNOMIAL_LOG_FREE")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])

    def test_lam0_exponent_from_recorded_ode(self):
        c2, c1, c0 = _master()
        s = sp.Symbol("s")
        F = r**s
        lhs = sp.expand((c2 * sp.diff(F, r, 2) + c1 * sp.diff(F, r) + c0 * F)
                        / r**s)
        # leading r^{+1} coefficient must vanish at the recorded exponent
        sig = sp.sympify(CERT["exponents"]["lam0_branch"])
        self.assertEqual(sp_simplify(lhs.coeff(r, 1).subs(s, sig)), 0)

    def test_recurrence_theorem_coefficient(self):
        c2, c1, c0 = _master()
        k = sp.Symbol("k")
        term = r**(-k)
        lt = sp.expand((c2 * sp.diff(term, r, 2) + c1 * sp.diff(term, r)
                        + c0 * term) / r**(-k))
        diag = sp.factor(lt.coeff(r, 1))
        self.assertEqual(
            diag, sp.sympify(CERT["recurrence"]["diagonal_coeff"],
                             locals={"omega": w, "I": sp.I, "k": k}))
        # nonzero for every integer k >= 4 when omega != 0
        for kk in range(4, 12):
            self.assertNotEqual(diag.subs(k, kk), 0)

    def test_lam0_series_head_solves_recursion(self):
        c2, c1, c0 = _master()
        head = CERT["recurrence"]["lam0_series_head"]
        F = sum(sp.sympify(head[str(j)], locals={"omega": w, "I": sp.I})
                * r**(-j) for j in range(3, 7))
        res = sp.expand(c2 * sp.diff(F, r, 2) + c1 * sp.diff(F, r) + c0 * F)
        # the recorded head must annihilate the ODE through its own order band
        # (residual pushed to r^{-4} and below beyond the truncation)
        for p in (2, 1, 0, -1):
            self.assertEqual(sp_simplify(res.coeff(r, p)), 0,
                             f"series head fails at r^{p}")

    def test_omega_zero_indicial(self):
        c2, c1, c0 = (c.subs(w, 0) for c in _master())
        s = sp.Symbol("s")
        F = r**s
        lhs = sp.expand((c2 * sp.diff(F, r, 2) + c1 * sp.diff(F, r) + c0 * F)
                        / r**s)
        ind = sp.factor(lhs.coeff(r, 0))
        self.assertEqual(ind, sp.sympify(CERT["omega_zero"]["indicial"]))

    def test_positive_control_and_flags(self):
        pc = CERT["positive_control"]
        self.assertTrue(pc["match"])
        self.assertEqual(pc["oscillatory_exponent"], "-4*I*omega + 1")
        self.assertEqual(CERT["exponents"]["oscillatory_branch"],
                         "-4*I*omega + 1")
        cf = CERT["claim_flags"]
        for f in ("all_orders_reconstruction_certified",
                  "one_power_polynomial_certified", "log_free_certified",
                  "ramification_excluded_certified",
                  "recurrence_theorem_certified", "omega_zero_excluded"):
            self.assertTrue(cf[f], f)
        for f in ("general_l_certified",
                  "finite_flux_boundary_class_certified"):
            self.assertFalse(cf[f], f)

    def test_polynomial_mode_is_log_free_unramified(self):
        pm = CERT["polynomial_mode"]
        self.assertEqual(pm["degree"], 1)
        self.assertFalse(pm["logarithm"])
        self.assertFalse(pm["ramified"])
        self.assertFalse(CERT["recurrence"]["log_forced_omega_nonzero"])

    def test_mutation_wrong_lam0_exponent_is_rejected(self):
        # the true lam=0 exponent is -3; a wrong exponent -2 must NOT satisfy
        # the leading balance of the recorded master ODE
        c2, c1, c0 = _master()
        s = sp.Symbol("s")
        F = r**s
        lead = sp.expand((c2 * sp.diff(F, r, 2) + c1 * sp.diff(F, r) + c0 * F)
                         / r**s).coeff(r, 1)
        self.assertEqual(sp_simplify(lead.subs(s, -3)), 0)      # true
        self.assertNotEqual(sp_simplify(lead.subs(s, -2)), 0)   # mutant
        self.assertNotEqual(sp_simplify(lead.subs(s, -4)), 0)   # mutant

    def test_mutation_recurrence_resonance_only_at_k3(self):
        # the recurrence coefficient must vanish at exactly k=3 (indicial
        # root) and nowhere else; a mutant claiming resonance at k=2 fails
        k = sp.Symbol("k")
        diag = sp.sympify(CERT["recurrence"]["diagonal_coeff"],
                          locals={"omega": w, "I": sp.I, "k": k})
        self.assertEqual(diag.subs(k, 3), 0)
        self.assertNotEqual(diag.subs(k, 2), 0)
        self.assertNotEqual(diag.subs(k, 4), 0)

    def test_mutation_omitted_log_at_omega_zero(self):
        # omitting the omega=0 exception (claiming log-free there) is wrong:
        # the omega=0 exponents are integer-separated, so a log is admissible
        self.assertTrue(CERT["omega_zero"]["integer_separated"])
        exps = sorted(int(e) for e in CERT["omega_zero"]["exponents"])
        self.assertEqual(exps[1] - exps[0], 5)  # 2 - (-3) = 5, integer gap

    def test_bh3_vocabulary_lock(self):
        blob = json.dumps(CERT).lower()
        for banned in ("quasinormal", "ringdown", "stability", "scattering",
                       "ghost", "unitarity", "particle", "positivity"):
            self.assertNotIn(banned, blob, banned)


def sp_simplify(e):
    return sp.simplify(sp.expand(e))


if __name__ == "__main__":
    unittest.main()
