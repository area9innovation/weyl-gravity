from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.matter_gauge_representation_projection_obstruction import (
    build,
    validate,
)
from anomalies.matter_gauge_representation_projection_obstruction_certificate import (
    OUTPUT,
    build as build_certificate,
)
from anomalies.verify_matter_gauge_representation_projection_obstruction import (
    verify,
    verify_payload,
)


class MatterGaugeRepresentationProjectionObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_exact_projection_checks(self) -> None:
        self.assertTrue(all(build()["exact_checks"].values()))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build_certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["projection_theorem"]["joint_solution_set"],
            "EMPTY",
        )

    def test_separator_sign_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["projection_theorem"]["species_separator_values"][
            "left_Weyl_fermion"
        ]["numerator"] = -1
        with self.assertRaisesRegex(ValueError, "coefficient import"):
            verify_payload(mutant)

    def test_input_hash_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["input_pin"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "input hash"):
            verify_payload(mutant)

    def test_representation_enumeration_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"][
            "BOUNDED_REPRESENTATION_CLASSIFICATION_PERFORMED"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_GUT_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"][
            "GUT_STANDARD_MODEL_OR_PARTICLE_SELECTION_CLAIM"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_signed_lattice_health_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["SIGNED_LATTICE_IS_HEALTHY_MATTER"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
