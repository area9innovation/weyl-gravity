from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.matter_content_anomaly_cancellation_lattice import build, validate
from anomalies.matter_content_anomaly_cancellation_lattice_certificate import (
    OUTPUT,
    build as build_certificate,
)
from anomalies.verify_matter_content_anomaly_cancellation_lattice import (
    verify,
    verify_payload,
)


class MatterContentAnomalyCancellationLatticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_two_methods_and_exact_checks(self) -> None:
        value = build()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            value["signed_determinant_lattice"]["smith_invariant_factors"],
            [1, 30],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build_certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE",
        )

    def test_single_scalar_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["matter_vectors_absolute_determinant"][
            "real_conformal_scalar"
        ]["vector"][0]["numerator"] = 2
        with self.assertRaisesRegex(ValueError, "single-field"):
            verify_payload(mutant)

    def test_vector_ghost_sign_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["coefficient_methods"]["repository_heat_kernel"]["rows"][
            "gauge_complex_scalar_FP_ghost_minus_logdet"
        ][0]["numerator"] = 1
        with self.assertRaisesRegex(ValueError, "ghost ledger"):
            verify_payload(mutant)

    def test_compensator_scalar_alias_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["matter_vectors_absolute_determinant"][
            "ordinary_homogeneous_conformal_compensator_scalar"
        ]["vector"][0]["numerator"] = 2
        with self.assertRaisesRegex(ValueError, "single-field"):
            verify_payload(mutant)

    def test_BoxR_scheme_pin_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["input_pins"]["BoxR_scheme_conversion"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dependency hash"):
            verify_payload(mutant)

    def test_chiral_Ward_policy_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["chiral_phase_ledger"][
            "declared_common_Ward_regulator"
        ] = "p=1/48"
        with self.assertRaisesRegex(ValueError, "chiral Ward-policy"):
            verify_payload(mutant)

    def test_kernel_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["signed_determinant_lattice"]["kernel_basis"][1][0] = 47
        with self.assertRaises(ValueError):
            verify_payload(mutant)

    def test_healthy_solution_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_compensator_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["COMPENSATOR_IS_STRICT_CANCELLATION"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
