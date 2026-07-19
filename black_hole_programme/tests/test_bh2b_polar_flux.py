"""Tier-1 fast rail for the BH-2B polar flux certificate.

Exhaustive rail: `verify_bh2b_polar_flux.py` (~20 min, independent VbGeo
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

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_FLUX.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-flux-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2B_POLAR_FLUX_STAGE1_EINSTEIN_BRANCH_SYMPLECTICALLY_NULL",
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["einstein_block_null_certified"])
        self.assertTrue(flags["conformal_degeneracy_certified"])
        self.assertTrue(flags["offshell_identity_certified"])
        self.assertFalse(flags["extra_block_certified"])
        self.assertFalse(flags["cross_block_certified"])
        self.assertFalse(flags["flux_signs_certified"])
        self.assertEqual(CERT["conformal_control"]["result"], "EXACT_ZERO_OFF_SHELL")

    def test_dependency_tags_and_vocabulary(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)

    def test_null_theorem_exact_spot_check(self):
        """The recorded coefficients must all vanish at omega2 = -omega1 and
        the diagonals at omega2 = omega1 (cheap exact check on the stored
        closed forms)."""
        import sympy as sp

        r = sp.Symbol("r", positive=True)
        m = sp.Symbol("m", positive=True)
        alpha = sp.Symbol("alpha")
        w1, w2 = sp.symbols("omega1 omega2")
        loc = {"r": r, "m": m, "alpha": alpha, "I": sp.I, "pi": sp.pi,
               "omega1": w1, "omega2": w2}
        C = {k: sp.sympify(v, locals=loc)
             for k, v in CERT["einstein_block"]["coefficients"].items()}
        for k, c in C.items():
            self.assertEqual(sp.cancel(sp.together(c.subs(w2, -w1))), 0, k)
        for k in ("KK", "HH"):
            self.assertEqual(sp.cancel(sp.together(C[k].subs(w2, w1))), 0, k)
        # swap antisymmetry of the cross coefficients
        swap = C["HK"].subs([(w1, w2), (w2, w1)], simultaneous=True)
        self.assertEqual(sp.cancel(sp.together(C["KH"] + swap)), 0)


if __name__ == "__main__":
    unittest.main()
