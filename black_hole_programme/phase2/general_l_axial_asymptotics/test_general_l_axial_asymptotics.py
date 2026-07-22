"""Fast structural rail for the generic-ell axial asymptotic certificate."""
from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
PAYLOAD = json.loads((HERE / "certificate.json").read_text())
SCHEMA = json.loads((HERE / "schema.json").read_text())
RECEIPT = json.loads((HERE / "receipt.json").read_text())
GIT_ROOT = next(parent for parent in HERE.parents if (parent / ".git").exists())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_id(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


class GeneralLAxialAsymptoticsTest(unittest.TestCase):
    def test_schema(self):
        jsonschema.Draft202012Validator(SCHEMA).validate(PAYLOAD)

    def test_generic_lambda_master(self):
        self.assertEqual(
            PAYLOAD["metric"]["master"]["coefficients"],
            ["-2*M*r + r**2", "2*M + 2*I*omega*r**2 + 2*r",
             "-Lambda + 6*I*omega*r"],
        )

    def test_pivots_have_no_lambda_denominator(self):
        pivots = [
            PAYLOAD["metric"]["formal_sectors"]["rate_0"]["recurrence_pivot"],
            PAYLOAD["metric"]["formal_sectors"]["rate_minus_2_i_omega"]
            ["recurrence_pivot"],
        ]
        for sector in PAYLOAD["carrier"]["sectors"].values():
            pivots += [sector["top_recurrence_pivot"], sector["lower_recurrence_pivot"]]
        self.assertTrue(all("Lambda" not in pivot and "M" not in pivot for pivot in pivots))

    def test_integer_resonances_are_compatible(self):
        for sector in PAYLOAD["carrier"]["sectors"].values():
            self.assertTrue(sector["top_n1_resonance"]["compatible"])
            self.assertFalse(sector["logarithm_forced"])

    def test_exact_exceptional_set(self):
        self.assertEqual(PAYLOAD["exceptional_set"]["frequency"], ["omega=0"])
        self.assertEqual(PAYLOAD["exceptional_set"]["angular_representations"],
                         ["ell=0", "ell=1"])

    def test_decisive_pivot_mutations_rejected(self):
        n, omega = sp.symbols("n omega")
        recorded = sp.sympify(
            PAYLOAD["carrier"]["sectors"]["0"]["top_recurrence_pivot"],
            locals={"n": n, "omega": omega},
        )
        wrong_integer_shift = -4 * n * (n + 1) * omega**2
        wrong_angular_pole = recorded / (sp.Symbol("Lambda") - 6)
        self.assertNotEqual(sp.simplify(recorded - wrong_integer_shift), 0)
        self.assertNotEqual(sp.simplify(recorded - wrong_angular_pole), 0)

    def test_successor_claims_remain_false(self):
        flags = PAYLOAD["claim_flags"]
        for name in ("literal_lee_wald_current_computed",
                     "finite_pairing_selection_certified", "polar_certified",
                     "asymptotic_phase_space_constructed"):
            self.assertFalse(flags[name])

    def test_receipt_uses_distinct_content_and_git_blob_manifests(self):
        for relative, digest in RECEIPT["content_sha256_manifest"].items():
            self.assertEqual(_sha256(GIT_ROOT / "physics" / "symplectic-reconstruction" / relative),
                             digest)
        for relative, digest in RECEIPT["source_manifest"].items():
            self.assertEqual(_git_blob_id(GIT_ROOT / relative), digest)


if __name__ == "__main__":
    unittest.main()
