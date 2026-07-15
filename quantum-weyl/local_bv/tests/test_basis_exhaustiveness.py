import unittest
from dataclasses import replace

from local_bv.basis_exhaustiveness import (
    BasisExhaustivenessProof,
    grading_signature_manifest,
)


class BasisExhaustivenessTests(unittest.TestCase):
    def test_integer_signatures_are_exhaustive_for_declared_scalar_grading(self) -> None:
        h04 = grading_signature_manifest(0, "even")
        h14 = grading_signature_manifest(1, "odd")
        self.assertEqual(h04["coarse_grading_signature_count"], 3)
        self.assertEqual(h04["refined_grading_signature_count"], 2)
        self.assertEqual(h14["coarse_grading_signature_count"], 9)
        self.assertEqual(h14["refined_grading_signature_count"], 5)
        self.assertEqual(h14["diff_top_form_coarse_signature_count"], 12)
        self.assertEqual(h14["diff_top_form_refined_signature_count"], 7)
        self.assertEqual(h14["combined_coarse_signature_count"], 21)
        self.assertEqual(h04["template_covered_signature_count"], 2)
        self.assertEqual(h14["template_covered_signature_count"], 2)
        self.assertEqual(h04["exhaustiveness_status"], "IN_PROGRESS")
        self.assertRegex(h14["grading_manifest_hash"], r"^[0-9a-f]{64}$")

    def test_unsupported_ghost_number_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "ghost number"):
            grading_signature_manifest(2, "even")
        with self.assertRaisesRegex(ValueError, "parity"):
            grading_signature_manifest(1, "mixed")

    def test_exhaustiveness_proof_is_hash_bound(self) -> None:
        artifacts = [{"row": row} for row in range(7)]
        proof = BasisExhaustivenessProof.create(
            basis_manifest=artifacts[0],
            declared_bounds=artifacts[1],
            generator_algebra=artifacts[2],
            grading_solution=artifacts[3],
            orbit_enumeration=artifacts[4],
            identity_quotient=artifacts[5],
            proof_artifact=artifacts[6],
        )
        proof.verify(expected_basis_manifest_hash=proof.basis_manifest_hash)
        with self.assertRaisesRegex(ValueError, "supplied basis"):
            proof.verify(expected_basis_manifest_hash="0" * 64)
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            replace(proof, proof_hash="0" * 64).verify(
                expected_basis_manifest_hash=proof.basis_manifest_hash
            )

    def test_exhaustiveness_proof_rejects_mutated_embedded_artifact(self) -> None:
        artifacts = [{"row": row} for row in range(7)]
        proof = BasisExhaustivenessProof.create(
            basis_manifest=artifacts[0],
            declared_bounds=artifacts[1],
            generator_algebra=artifacts[2],
            grading_solution=artifacts[3],
            orbit_enumeration=artifacts[4],
            identity_quotient=artifacts[5],
            proof_artifact=artifacts[6],
        )
        mutated = replace(
            proof.bound_artifacts[0], payload_json='{"row":99}'
        )
        with self.assertRaisesRegex(ValueError, "hash does not reproduce"):
            replace(
                proof,
                bound_artifacts=(mutated, *proof.bound_artifacts[1:]),
            ).verify(expected_basis_manifest_hash=proof.basis_manifest_hash)


if __name__ == "__main__":
    unittest.main()
