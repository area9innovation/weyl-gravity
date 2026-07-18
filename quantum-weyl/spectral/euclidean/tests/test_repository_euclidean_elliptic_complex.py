from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.elliptic_complex_receiver import validate_euclidean_elliptic_complex
from spectral.euclidean.repository_euclidean_elliptic_complex import OUTPUT, ROOT, build
from spectral.euclidean.verify_repository_euclidean_elliptic_complex import verify


class RepositoryEuclideanEllipticComplexTests(unittest.TestCase):
    def test_physical_artifact_is_accepted(self) -> None:
        value = build()[2]
        receipt = validate_euclidean_elliptic_complex(value, repository_root=ROOT)
        self.assertEqual(receipt["symbol_sector_count"], 4)
        self.assertEqual(receipt["kinetic_block_count"], 4)

    def test_composition_and_coverage_mutations_are_rejected(self) -> None:
        value = build()[2]
        mutant = deepcopy(value)
        mutant["principal_symbol_exactness"][0]["outgoing_symbol"]["entries"][0]["coefficient"]["numerator"] = 2
        with self.assertRaisesRegex(ValueError, "composition"):
            validate_euclidean_elliptic_complex(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["principal_symbol_exactness"].pop()
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_euclidean_elliptic_complex(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["gauge_fixed_kinetic_blocks"].pop()
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_euclidean_elliptic_complex(mutant, repository_root=ROOT)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build()[2])
        self.assertEqual(verify()["status"], "SEMANTIC_RECEIVER_ACCEPTED")


if __name__ == "__main__":
    unittest.main()
