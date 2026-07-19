"""Tier-1 fast rail for the BH-2B polar cross-flux certificate.

Exhaustive rail: `verify_bh2b_polar_cross_flux.py` (~30 min, independent
VbGeo engine), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_CROSS_FLUX.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-cross-flux-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2B_POLAR_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES",
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["composition_certified"])
        self.assertTrue(flags["all_rows_verified_on_composed_modes"])
        self.assertTrue(flags["cross_block_nonzero_certified"])
        self.assertTrue(flags["extra_block_canonical_positivity_certified"])
        self.assertFalse(flags["invariant_extra_sign_certified"])
        self.assertFalse(flags["symbolic_frequency_certified"])
        self.assertFalse(flags["causal_exclusion_decided"])

    def test_dependency_tags_and_vocabulary(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)

    def test_recorded_matrix_structure(self):
        """Cheap exact checks on the stored rho = 1/4 flux matrix: exact
        Hermiticity of the X-block, real positive diagonals, controls tiny."""
        import sympy as sp

        alpha = sp.Symbol("alpha", positive=True)
        loc = {"alpha": alpha, "I": sp.I, "pi": sp.pi}
        M = {k: sp.sympify(v, locals=loc)
             for k, v in CERT["fixtures"]["flux_matrix_rho_1_4"].items()}

        def mag(e):
            return abs(complex(sp.N(sp.I * e / (sp.pi * alpha), 8)))

        phys = min(mag(M[f"{i}|{j}"]) for i in ("X0", "X1", "X2")
                   for j in ("X0", "X1", "X2"))
        tol = 1e-4 * phys
        Kn = {k2: complex(sp.N(sp.I * M[k2] / (sp.pi * alpha), 10)) for k2 in M}
        for i in ("X0", "X1", "X2"):
            for j in ("X0", "X1", "X2"):
                dev = abs(Kn[f"{i}|{j}"] - Kn[f"{j}|{i}"].conjugate())
                self.assertLess(dev, tol)
        for i in ("X0", "X1", "X2"):
            val = Kn[f"{i}|{i}"]
            self.assertLess(abs(val.imag), tol)
            self.assertGreater(val.real, 0)
        ctrl = max(mag(M["E|E"]), mag(M["G|G"]),
                   *[mag(M[f"G|{n}"]) for n in ("E", "X0", "X1", "X2")])
        self.assertLess(ctrl, 1e-4 * phys)
        for j in ("X0", "X1", "X2"):
            self.assertGreater(mag(M[f"E|{j}"]), 1e3 * ctrl)


if __name__ == "__main__":
    unittest.main()
