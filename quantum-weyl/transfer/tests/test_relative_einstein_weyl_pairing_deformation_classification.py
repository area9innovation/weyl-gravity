from __future__ import annotations

from copy import deepcopy
import json
import unittest

from transfer.relative_einstein_weyl_pairing_deformation_classification import (
    build,
    validate,
)
from transfer.relative_einstein_weyl_pairing_deformation_classification_certificate import (
    OUTPUT,
    build as build_certificate,
)
from transfer.verify_relative_einstein_weyl_pairing_deformation_classification import (
    verify,
    verify_payload,
)


class RelativePairingDeformationClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_exact_producer_classification(self) -> None:
        value = build()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            [
                row["minimal_target_pairing_repair"]["rank"]
                for row in value["sector_classification"]
            ],
            [1, 1],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build_certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION",
        )

    def test_axial_signature_wall_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sector_classification"][0]["wall_mutations"]["determinants"][0] = "lambda"
        with self.assertRaisesRegex(ValueError, "axial signature wall"):
            verify_payload(mutant)

    def test_polar_signature_wall_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sector_classification"][1]["wall_mutations"]["determinants"][2] = "-4"
        with self.assertRaisesRegex(ValueError, "polar signature wall"):
            verify_payload(mutant)

    def test_axial_repair_matrix_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sector_classification"][0][
            "minimal_target_pairing_repair"
        ]["Delta"][1][1] = "9*lambda - 1"
        with self.assertRaisesRegex(ValueError, "axial exact matrix"):
            verify_payload(mutant)

    def test_polar_repair_matrix_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sector_classification"][1][
            "minimal_target_pairing_repair"
        ]["cyclic_map_S"][0][1] = "(3*lambda + 2)/4"
        with self.assertRaisesRegex(ValueError, "polar exact matrix"):
            verify_payload(mutant)

    def test_typed_auxiliary_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sector_classification"][1][
            "minimal_physical_auxiliary_repair"
        ]["auxiliary_pairing"] = "2*(lambda + 2)"
        with self.assertRaisesRegex(ValueError, "polar typed auxiliary"):
            verify_payload(mutant)

    def test_standard_action_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["STANDARD_ACTION_PRESERVING_REPAIR_EXISTS"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_qme_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["RELATIVE_QME_RESTORED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
