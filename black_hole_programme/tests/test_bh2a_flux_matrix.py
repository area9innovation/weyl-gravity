"""Tier-1 fast rail for the BH-2A flux-matrix certificate.

Exhaustive rail: `verify_bh2a_flux_matrix.py` (~95 s), run separately.
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

CERT = json.loads((PKG / "certificates" / "BH2A_FLUX_MATRIX.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-flux-matrix-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"], "BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL"
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["rw_branch_null_certified"])
        self.assertFalse(flags["cross_block_certified"])
        self.assertFalse(flags["extra_block_certified"])
        self.assertFalse(flags["causal_disposition_decided"])
        self.assertFalse(flags["stability_or_ringdown_certified"])

    def test_closed_formula_null_for_conjugate_pairs(self):
        alpha = sp.Symbol("alpha")
        w1, w2 = sp.symbols("omega1 omega2")
        r = sp.Symbol("r", positive=True)
        ps1, ps2 = sp.symbols("ps1 ps2")
        closed = sp.sympify(
            CERT["rw_block"]["on_shell_flux"].split("= ", 1)[1],
            locals={"pi": sp.pi, "alpha": alpha, "omega1": w1, "omega2": w2,
                    "psi1": ps1, "psi2": ps2, "r": r},
        )
        self.assertEqual(sp.simplify(closed.subs(w2, w1)), 0)
        self.assertEqual(sp.simplify(closed.subs(w2, -w1)), 0)
        self.assertNotEqual(sp.simplify(closed), 0)

    def test_bilinear_antisymmetry_spot(self):
        # swapping (a <-> b) must flip the sign of the stored F^r
        t = sp.Symbol("t")
        r = sp.Symbol("r", positive=True)
        m = sp.Symbol("m", positive=True)
        alpha = sp.Symbol("alpha")
        loc = {"h0a": sp.Function("h0a"), "h1a": sp.Function("h1a"),
               "h0b": sp.Function("h0b"), "h1b": sp.Function("h1b"),
               "t": t, "r": r, "m": m, "alpha": alpha, "pi": sp.pi}
        Fr = sp.sympify(CERT["bilinear"]["F_r"], locals=loc)
        swap = {loc["h0a"](t, r): loc["h0b"](t, r), loc["h0b"](t, r): loc["h0a"](t, r),
                loc["h1a"](t, r): loc["h1b"](t, r), loc["h1b"](t, r): loc["h1a"](t, r)}
        self.assertEqual(sp.expand(Fr.subs(swap, simultaneous=True) + Fr), 0)


if __name__ == "__main__":
    unittest.main()
