"""Tier-1 fast rail for the BH-2B polar Einstein-branch certificate.

Exhaustive rail: `verify_bh2b_polar_einstein.py` (~30 s, independent VbGeo
engine), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_EINSTEIN.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-einstein-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2B_POLAR_EINSTEIN_BRANCH_REDUCED_TWO_DIMENSIONAL",
        )
        self.assertEqual(CERT["horizon_analysis"]["ingoing_spectrum"],
                         ["0", "-4*I*m*omega"])
        flags = CERT["claim_flags"]
        self.assertTrue(flags["two_dimensionality_certified"])
        self.assertTrue(flags["horizon_benchmark_certified"])
        self.assertFalse(flags["master_scalar_certified"])
        self.assertFalse(flags["flux_or_sign_certified"])
        self.assertEqual(CERT["master_scalar"]["status"], "OPEN")

    def test_dependency_tags_and_vocabulary(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)

    def test_recorded_system_exact_spot_check(self):
        """The recorded M satisfies a cheap exact invariant: at m=1 the
        ingoing-adapted residue matrix must have trace -4*I*omega."""
        import sympy as sp

        r = sp.Symbol("r", positive=True)
        w = sp.Symbol("omega")
        m = sp.Symbol("m", positive=True)
        rho = sp.Symbol("rho")
        loc = {"r": r, "omega": w, "m": m, "I": sp.I,
               "K": sp.Function("K"), "H1": sp.Function("H1")}
        M = sp.Matrix(2, 2, lambda i, j: sp.sympify(
            CERT["reduction"]["M"][i][j], locals=loc))
        B0 = 1 - 2 * m / r
        D = sp.diag(1, B0)
        Mad = D * M * D.inv() + sp.diff(D, r) * D.inv()
        Min = Mad - sp.I * w / B0 * sp.eye(2)
        tr = sp.cancel(sp.together(Min.trace())).subs(r, 2 * m + rho)
        res_tr = sp.simplify(sp.limit(rho * sp.cancel(sp.together(tr)), rho, 0))
        self.assertEqual(sp.simplify(res_tr + 4 * sp.I * m * w), 0)


if __name__ == "__main__":
    unittest.main()
