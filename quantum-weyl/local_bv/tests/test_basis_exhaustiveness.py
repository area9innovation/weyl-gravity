import unittest
from dataclasses import replace

from local_bv.algebra import canonical_sha256
from local_bv.basis_exhaustiveness import (
    BasisExhaustivenessProof,
    grading_signature_manifest,
)


class BasisExhaustivenessTests(unittest.TestCase):
    def test_integer_signatures_are_exhaustive_for_declared_scalar_grading(self) -> None:
        h04 = grading_signature_manifest(0, "even")
        h14 = grading_signature_manifest(1, "odd")
        self.assertEqual(h04["integer_solution_count"], 3)
        self.assertEqual(h14["integer_solution_count"], 21)
        self.assertEqual(h04["currently_generated_signature_count"], 2)
        self.assertEqual(h14["currently_generated_signature_count"], 2)
        self.assertEqual(h04["exhaustiveness_status"], "IN_PROGRESS")
        self.assertRegex(h14["grading_manifest_hash"], r"^[0-9a-f]{64}$")

    def test_unsupported_ghost_number_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "ghost number"):
            grading_signature_manifest(2, "even")
        with self.assertRaisesRegex(ValueError, "parity"):
            grading_signature_manifest(1, "mixed")

    def test_exhaustiveness_proof_is_hash_bound(self) -> None:
        hashes = [canonical_sha256({"row": row}) for row in range(7)]
        proof = BasisExhaustivenessProof.create(
            basis_manifest_hash=hashes[0],
            declared_bounds_hash=hashes[1],
            generator_algebra_hash=hashes[2],
            grading_solution_hash=hashes[3],
            orbit_enumeration_hash=hashes[4],
            identity_quotient_hash=hashes[5],
            proof_artifact_hash=hashes[6],
        )
        proof.verify(expected_basis_manifest_hash=hashes[0])
        with self.assertRaisesRegex(ValueError, "supplied basis"):
            proof.verify(expected_basis_manifest_hash="0" * 64)
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            replace(proof, proof_hash="0" * 64).verify(
                expected_basis_manifest_hash=hashes[0]
            )


if __name__ == "__main__":
    unittest.main()
