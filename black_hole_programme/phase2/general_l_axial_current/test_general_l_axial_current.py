"""Fast structural and mutation rail for the all-ell axial current theorem."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GIT_ROOT = next(parent for parent in HERE.parents if (parent / ".git").exists())
PAYLOAD = json.loads((HERE / "certificate.json").read_text())
SCHEMA = json.loads((HERE / "schema.json").read_text())
RECEIPT_PATH = HERE / "receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


class GeneralLAxialCurrentTest(unittest.TestCase):
    def test_schema(self):
        jsonschema.Draft202012Validator(SCHEMA).validate(PAYLOAD)

    def test_closed_generic_coefficients_not_sampled_modes(self):
        e0 = PAYLOAD["coefficients"]["E0"]
        e2 = PAYLOAD["coefficients"]["E2_unit_F"]
        self.assertIn("Lambda", e0)
        self.assertIn("ell", e0)
        self.assertIn("Lambda", e2)
        self.assertFalse(PAYLOAD["angular_reduction"]["unevaluated_integral_remaining"])
        self.assertEqual(set(PAYLOAD["literal_controls"]), {"2", "3"})

    def test_exact_wall_resultant_and_discrete_nonvanishing(self):
        lam, u = sp.symbols("Lambda u")
        wall = PAYLOAD["legacy_wall"]
        real = sp.sympify(wall["real_G_in_u"], locals={"Lambda": lam, "u": u})
        imag = sp.sympify(wall["imag_G_over_12omega_in_u"],
                          locals={"Lambda": lam, "u": u})
        recorded = sp.sympify(wall["resultant_u"], locals={"Lambda": lam})
        self.assertEqual(sp.simplify(sp.resultant(real, imag, u) - recorded), 0)
        self.assertNotEqual(int(wall["H_at_ell2"]), 0)
        self.assertNotEqual(int(wall["H_at_ell3"]), 0)
        k = sp.Symbol("k")
        shifted = sp.Poly(sp.sympify(wall["H_shifted_ell_ge_4"], locals={"k": k}), k)
        self.assertTrue(all(c > 0 for c in shifted.all_coeffs()))

    def test_normalization_and_frequency_symmetry(self):
        self.assertEqual(PAYLOAD["normalization"]["rescaling_law"],
                         "E -> c E sends A_EE -> |c|^2 A_EE")
        self.assertIn("basis-normalization wall", PAYLOAD["normalization"]["legacy_reading"])
        self.assertTrue(PAYLOAD["frequency_extension"]["nonvanishing_preserved"])

    def test_exponent_only_and_selection_promotions_rejected(self):
        flags = PAYLOAD["claim_flags"]
        self.assertTrue(flags["literal_all_ell_axial_einstein_current_certified"])
        self.assertTrue(flags["all_ell_einstein_finite_radial_form_certified"])
        self.assertFalse(flags["extra_branch_selection_certified"])
        self.assertFalse(flags["asymptotic_phase_space_constructed"])
        self.assertFalse(flags["hilbert_norm_constructed"])

    def test_dual_provenance(self):
        for record in PAYLOAD["provenance"].values():
            path = ROOT / record["path"]
            self.assertEqual(record["content_sha256"], sha256(path))
            self.assertEqual(record["git_blob"], git_blob(path))

    def test_receipt_distinguishes_sha256_from_git_blobs(self):
        receipt = json.loads(RECEIPT_PATH.read_text())
        for relative, digest in receipt["content_sha256_manifest"].items():
            self.assertEqual(len(digest), 64)
            self.assertEqual(sha256(ROOT / relative), digest)
        for relative, digest in receipt["source_manifest"].items():
            self.assertEqual(len(digest), 40)
            self.assertEqual(git_blob(GIT_ROOT / relative), digest)


if __name__ == "__main__":
    unittest.main()
