from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from d_quotient_classical.compensator.complex_compensator_vacuum_cylinder_causal_parent import (
    build,
    validate,
)
from d_quotient_classical.compensator.verify_complex_compensator_vacuum_cylinder_causal_parent import (
    verify,
)


def _rehash(record: dict[str, object]) -> None:
    core = dict(record)
    core.pop("sha256", None)
    record["sha256"] = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class ComplexCompensatorVacuumCylinderCausalParentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_producer_and_independent_verifier_agree(self) -> None:
        validate(self.value)
        verify(self.value)

    def test_wrong_R_squared_tuning_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["background_and_action"]["couplings"]["alpha_R"] = {
            "numerator": -1,
            "denominator": 145,
        }
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_nonzero_background_F_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["background_and_action"]["couplings"]["V0"] = {
            "numerator": 1,
            "denominator": 5,
        }
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_trace_Hessian_normalization_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["background_and_action"]["quadratic_variation"][
            "trace_Hessian_coefficient"
        ] = {"numerator": -1, "denominator": 4}
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_noniterated_trace_Green_operator_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["scalar_phase_endpoint"]["operator_dictionary"][
            "G_u_plus"
        ] = "-8 G_2_plus"
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_trace_homotopy_sign_mutation_is_rejected_after_rehash(self) -> None:
        mutant = deepcopy(self.value)
        matrix = mutant["scalar_phase_endpoint"]["Lambda_plus"]
        matrix["entries"][1]["coefficient"] = "-1"
        _rehash(matrix)
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_old_compact_trace_class_cannot_remain_closed(self) -> None:
        mutant = deepcopy(self.value)
        mutant["old_obstruction_disposition"]["status"] = (
            "REMAINS_NONTRIVIAL"
        )
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_Wess_Zumino_cannot_supply_classical_kinetic_term(self) -> None:
        mutant = deepcopy(self.value)
        mutant["action_identity"]["Wess_Zumino_in_classical_action"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_Hadamard_positivity_and_QME_promotions_are_rejected(self) -> None:
        for flag in ("HADAMARD_STATE", "POSITIVITY", "QME"):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.subTest(flag=flag), self.assertRaises(AssertionError):
                verify(mutant)

    def test_carrier_rank_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["complete_carrier"]["full_rank"] = 391
        with self.assertRaises(AssertionError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
