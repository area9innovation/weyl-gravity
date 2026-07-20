from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_active_clock_px2_locus import verify


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json"
)


class ActiveClockPX2LocusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_minimal_import_hash_drift_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["dependencies"]["minimal_action_classification"]["sha256"] = "0" * 64
        with self.assertRaises(Exception):
            verify(mutated)

    def test_berger_p2_coefficient_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        matrix = mutated["stationary_background_equations"][
            "frozen_Berger_clock"
        ]["matrix"]
        next(
            row
            for row in matrix["entries"]
            if row["row"] == 0 and row["column"] == 5
        )["coefficient"] = "-242/256"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_rank_or_kernel_promotion_is_detected(self) -> None:
        for key, bad in (("rank", 6), ("kernel_dimension", 0)):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["stationary_background_equations"]["common_system"][key] = bad
                with self.assertRaises(Exception):
                    verify(mutated)

    def test_velocity_sign_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        matrix = mutated["coupled_homogeneous_analysis"]["velocity_Hessian"]
        next(
            row
            for row in matrix["entries"]
            if row["row"] == 2 and row["column"] == 2
        )["coefficient"] = "36*t/25"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_longitudinal_condition_cannot_be_replaced_by_PX_alone(self) -> None:
        mutated = deepcopy(self.value)
        mutated["Berger_sound_cone_and_clock"][
            "P_X_plus_2X_P_XX"
        ] = "-81 t/200"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_empty_locus_cannot_export_candidate(self) -> None:
        mutated = deepcopy(self.value)
        mutated["selection"]["candidate_C_active_selected"] = True
        mutated["selection"]["candidate_C_active_action_hash"] = "1" * 64
        with self.assertRaises(Exception):
            verify(mutated)

    def test_gate5_cannot_be_promoted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["seven_gate_classification"]["gates"][4]["status"] = "PASS"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_scope_cannot_be_broadened_or_quantized(self) -> None:
        for flag in (
            "UNIVERSAL_K_ESSENCE_OR_COMPENSATOR_NO_GO",
            "HADAMARD_OR_QUANTUM_RESULT",
        ):
            with self.subTest(flag=flag):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
