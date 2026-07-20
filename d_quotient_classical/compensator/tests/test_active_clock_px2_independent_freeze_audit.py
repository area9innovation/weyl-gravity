from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import sympy as sp

from d_quotient_classical.compensator.active_clock_px2_independent_freeze_audit import (
    audit_terminal_payload,
)
from d_quotient_classical.compensator.verify_active_clock_px2_independent_freeze_audit import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json"
)
TERMINAL = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json"
)


class ActiveClockPX2IndependentFreezeAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())
        cls.terminal = json.loads(TERMINAL.read_text())

    def test_exact_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_coefficient_mutation_rejected(self) -> None:
        mutated = deepcopy(self.terminal)
        entry = next(
            row
            for row in mutated["stationary_background_equations"][
                "frozen_Berger_clock"
            ]["matrix"]["entries"]
            if row["row"] == 0 and row["column"] == 5
        )
        entry["coefficient"] = "-242/256"
        with self.assertRaisesRegex(AssertionError, "BERGER_ROW_MISMATCH"):
            audit_terminal_payload(mutated)

    def test_background_invariant_mutation_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "BERGER_ROW_MISMATCH"):
            audit_terminal_payload(self.terminal, q=sp.Rational(1, 4))

    def test_stress_sign_mutation_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "CYLINDER_ROW_MISMATCH"):
            audit_terminal_payload(self.terminal, stress_sign=-1)

    def test_omitted_longitudinal_gate_rejected(self) -> None:
        gates = {
            "stationarity",
            "principal",
            "velocity",
            "Lee_Wald",
            "raw_D",
            "K_Berger",
            "monotonicity",
        }
        with self.assertRaisesRegex(AssertionError, "OMITTED_LONGITUDINAL_GATE"):
            audit_terminal_payload(self.terminal, required_gates=gates)

    def test_zero_stratum_cannot_be_dropped(self) -> None:
        mutated = deepcopy(self.value)
        del mutated["singular_and_denominator_audit"]["t=0"]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_cofactor_kernel_cannot_be_replaced_by_sample(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_real_locus_audit"]["primitive_integer_kernel"] = [
            81,
            27,
            -324,
            486,
            18,
            1,
        ]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_candidate_and_universal_promotions_rejected(self) -> None:
        for path in (
            ("freeze_verdict", "candidate_C_active_selected"),
            ("claim_flags", "UNIVERSAL_SCALAR_TENSOR_OR_K_ESSENCE_NO_GO"),
            ("claim_flags", "HADAMARD_ANOMALY_QME_OR_QUANTUM"),
        ):
            with self.subTest(path=path):
                mutated = deepcopy(self.value)
                mutated[path[0]][path[1]] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
