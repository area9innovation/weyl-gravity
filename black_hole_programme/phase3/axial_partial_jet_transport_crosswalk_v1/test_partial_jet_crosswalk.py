#!/usr/bin/env python3
"""Mutation tests for the partial-jet crosswalk verifier."""
from __future__ import annotations

import copy
import json
import unittest

from .produce import HERE
from .verify import verify_document


class PartialJetCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        self.assertEqual(verify_document(copy.deepcopy(self.document)), [])

    def test_mutated_C_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["exact_blocks"]["C_Lx_to_metric_RW"][0][0] = "0"
        self.assertTrue(verify_document(changed))

    def test_mutated_full_transform_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["full_transform_crosswalk"][
            "transformed_full_6x6"
        ][0][0] = "1"
        self.assertTrue(verify_document(changed))

    def test_joint_rank_promotion_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["exact_blocks"]["joint_E_C_rank"] = 2
        self.assertTrue(verify_document(changed))

    def test_outer_factorization_mutation_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["common_scalar_forcing"]["outer_column_ell"][0][0] = "1"
        self.assertTrue(verify_document(changed))

    def test_endpoint_hypothesis_promotion_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["conditional_endpoint_derivative"][
            "hypothesis_verified_here"
        ] = True
        self.assertTrue(verify_document(changed))

    def test_T_plus_promotion_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["T_plus_recovered"] = True
        self.assertTrue(verify_document(changed))

    def test_H4_promotion_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["transport_method_boundary"][
            "tau_dual_alone_cures_H4"
        ] = True
        self.assertTrue(verify_document(changed))

    def test_import_hash_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["imports"]["complete_reconstruction"]["sha256"] = "0" * 64
        self.assertTrue(verify_document(changed))


if __name__ == "__main__":
    unittest.main()
