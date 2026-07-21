from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from cartan.berger_k_one_loop_insertion_nondefinition import (
    ATLAS_OUTPUT,
    OUTPUT,
    build,
    validate,
)
from cartan.verify_berger_k_one_loop_insertion_nondefinition import (
    verify,
    verify_payload,
)


class BergerKOneLoopInsertionNondefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build())

    def test_method_distinct_audit(self) -> None:
        self.assertEqual(
            verify()["result_state"],
            "NONDEFINED_UPSTREAM_Q1_AND_RENORMALIZED_K_INSERTIONS_ABSENT",
        )

    def test_k_and_raw_d_are_separate(self) -> None:
        self.assertEqual(self.value["setting"]["generator"], "K_Berger=D-omega R")
        self.assertFalse(self.value["classical_import"]["raw_D_fixes_background"])
        self.assertEqual(
            self.value["defect_target"]["raw_D_disposition"],
            "SEPARATE_AFFINE_GENERATOR_NO_QUANTUM_D_IDENTITY_INFERRED",
        )

    def test_q1_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["operator_ledger"]["Q1"] = "CERTIFIED"
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_defect_classification_promotion_is_rejected(self) -> None:
        for classification in ("ZERO", "Q0_EXACT", "NONTRIVIAL"):
            mutant = deepcopy(self.value)
            mutant["defect_target"]["classification"] = classification
            with self.assertRaises((ValidationError, ValueError)):
                verify_payload(mutant)

    def test_zero_quotient_shortcut_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["one_loop_import"]["zero_quotient_implication"] = "DEFECT_ZERO"
        with self.assertRaises((ValidationError, ValueError)):
            verify_payload(mutant)

    def test_phase_current_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["phase_boundary_zero_mode_ledger"][
            "phase_shift_current_regulated_insertion"
        ] = "CERTIFIED"
        with self.assertRaises((ValidationError, ValueError)):
            verify_payload(mutant)

    def test_quantum_claim_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["QUANTUM_K_CARTAN_DEFECT_CLASSIFIED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_atlas_row_remains_open_and_nonparticle(self) -> None:
        atlas = json.loads(ATLAS_OUTPUT.read_text(encoding="utf-8"))
        row = atlas["entries"][0]
        self.assertEqual(row["quantum_data"]["entry_kind"], "NON_MODE_PARTICLE_GUARD")
        self.assertEqual(row["quantum_data"]["BRST_exactness"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(row["quantum_data"]["particle_interpretation"]["status"], "NOT_APPLICABLE")


if __name__ == "__main__":
    unittest.main()
