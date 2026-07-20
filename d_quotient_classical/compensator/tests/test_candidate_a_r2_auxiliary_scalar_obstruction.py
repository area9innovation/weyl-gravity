from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.candidate_a_r2_auxiliary_scalar_obstruction import (
    OUTPUT,
    ROOT,
    build,
    verify_payload,
)


class CandidateAAuxiliaryScalarObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_exact_rebuild(self) -> None:
        self.assertEqual(self.payload, build())
        verify_payload(self.payload)

    def test_terminal_physical_sign_failure(self) -> None:
        scalar = self.payload["homogeneous_scalar_full_Hessian_sector"]
        self.assertEqual(
            scalar["Lee_Wald_and_sign"]["velocity_Hessian_inertia"],
            [1, 1, 0],
        )
        self.assertEqual(
            scalar["D_evolution_and_charge"]["real_roots"],
            ["-sqrt(2)", "sqrt(2)"],
        )

    def test_supersedes_direct_sum_only(self) -> None:
        supersession = self.payload["supersession"]
        self.assertIn("complete rank-390 direct-sum", supersession["superseded_claim"])
        self.assertIn(
            "the trace Schur complement H_u=-(Box+2)^2/8",
            supersession["retained_subclaims"],
        )

    def test_wrong_inertia_is_rejected(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["homogeneous_scalar_full_Hessian_sector"]["Lee_Wald_and_sign"][
            "velocity_Hessian_inertia"
        ] = [2, 0, 0]
        with self.assertRaises(AssertionError):
            verify_payload(mutated)

    def test_missing_mixed_row_is_rejected(self) -> None:
        mutated = deepcopy(self.payload)
        record = mutated["full_non_Einstein_Hessian_and_BV"][
            "full_action_hessian"
        ]["mixed_block_polynomial"]
        record["entries"] = [
            entry
            for entry in record["entries"]
            if not (entry["row"] == 0 and entry["column"] == 10)
        ]
        with self.assertRaises(AssertionError):
            verify_payload(mutated)

    def test_wrong_D_root_is_rejected(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["homogeneous_scalar_full_Hessian_sector"][
            "D_evolution_and_charge"
        ]["characteristic_polynomial"] = "(lambda^2+2)^2"
        with self.assertRaises(AssertionError):
            verify_payload(mutated)

    def test_Berger_promotion_is_rejected(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["comparison_disposition"]["Berger_compatibility"][
            "status"
        ] = "PASS"
        with self.assertRaises(AssertionError):
            verify_payload(mutated)

    def test_Hadamard_promotion_is_rejected(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["claim_flags"]["HADAMARD_STATE"] = True
        with self.assertRaises(AssertionError):
            verify_payload(mutated)

    def test_all_dependencies_exist(self) -> None:
        for item in self.payload["dependencies"].values():
            self.assertTrue((ROOT / item["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
