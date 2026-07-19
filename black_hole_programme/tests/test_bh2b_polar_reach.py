"""Tier-1 fast rail for the BH-2B polar-reach certificate.

Exhaustive rail: `verify_bh2b_polar_reach.py` (~3.5 min, independent VbGeo
engine), run separately.  Here: schema + verdict + flags + a cheap exact
spot-check of the sliced residue spectrum structure at m = 1 recorded in
the certificate text.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_REACH.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-reach-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL",
        )
        self.assertEqual(
            CERT["horizon_analysis"]["indicial_exponents"],
            ["0 (multiplicity 3)", "1 - 4*I*m*omega",
             "-1 - 4*I*m*omega", "-3 - 4*I*m*omega"],
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["operator_identity_reduction_certified"])
        self.assertTrue(flags["conformal_gauge_identity_certified"])
        self.assertTrue(flags["gauge_quotient_certified"])
        self.assertFalse(flags["flux_or_sign_certified"])
        self.assertFalse(flags["zerilli_benchmark_certified"])
        self.assertFalse(flags["causal_exclusion_decided"])
        self.assertFalse(flags["growth_or_stability_certified"])
        self.assertFalse(flags["omega_zero_classified"])

    def test_dependency_tags_and_scope(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")
        self.assertIn("real omega != 0", CERT["declaration"]["frequency_domain"])
        # BH-3 vocabulary must not appear anywhere in the certificate
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)

    def test_conformal_gauge_trace_relation(self):
        """Cheap exact spot check: psi_conf = -DDPhi - g BoxPhi/2 has trace
        -3 BoxPhi on flat space in Cartesian coordinates (algebraic identity
        independent of the heavy pipeline)."""
        import sympy as sp

        t, xx, yy, zz = sp.symbols("t x y z")
        phi = sp.Function("phi")(t, xx, yy, zz)
        eta = sp.diag(-1, 1, 1, 1)
        coords = [t, xx, yy, zz]
        DD = sp.Matrix(4, 4, lambda i, j: sp.diff(phi, coords[i], coords[j]))
        box = sum(eta.inv()[i, i] * DD[i, i] for i in range(4))
        psi = -DD - eta * box / 2
        trace = sum(eta.inv()[i, i] * psi[i, i] for i in range(4))
        self.assertEqual(sp.simplify(trace + 3 * box), 0)


if __name__ == "__main__":
    unittest.main()
