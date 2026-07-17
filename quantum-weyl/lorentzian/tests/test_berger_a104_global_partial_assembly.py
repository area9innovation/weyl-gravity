from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_a104_global_partial_assembly import validate
from lorentzian.berger_a104_global_partial_assembly_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_a104_global_partial_assembly import verify


class BergerA104GlobalPartialAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.artifacts = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-a104-global-partial-assembly-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_global_partial_operator_and_mask_are_emitted(self) -> None:
        self.assertEqual(
            set(self.artifacts),
            {"global_A104_partial", "global_A104_known_entry_mask"},
        )
        self.assertEqual(self.artifacts["global_A104_partial"]["shape"], [104, 104])
        mask = self.artifacts["global_A104_known_entry_mask"]
        self.assertEqual(mask["shape"], [104, 104])
        self.assertEqual(mask["known_coordinate_count"], 10528)
        self.assertEqual(mask["unknown_coordinate_count"], 288)

    def test_sector_embeddings_use_exact_frozen_global_indices(self) -> None:
        embeddings = self.certificate["sector_embeddings"]
        self.assertEqual(embeddings["metric"]["local_to_global_indices"], list(range(6, 26)) + list(range(58, 78)))
        self.assertEqual(embeddings["metric_antifield"]["local_to_global_indices"], list(range(26, 46)) + list(range(78, 98)))
        self.assertFalse(
            set(embeddings["metric"]["local_to_global_indices"])
            & set(embeddings["metric_antifield"]["local_to_global_indices"])
        )

    def test_two_A12_slots_cover_exactly_the_unknown_coordinates(self) -> None:
        slots = self.certificate["endpoint_A24_import_contract"]["derived_block_slots"]
        self.assertEqual([slot["block_id"] for slot in slots], ["ghost_A12", "identity_A12"])
        self.assertEqual(slots[0]["global_row_indices"], list(range(0, 6)) + list(range(52, 58)))
        self.assertEqual(slots[1]["global_row_indices"], list(range(46, 52)) + list(range(98, 104)))
        self.assertEqual(sum(len(slot["global_row_indices"]) ** 2 for slot in slots), 288)

    def test_factor_and_q_cauchy_contracts_are_frozen(self) -> None:
        endpoint = self.certificate["endpoint_A24_import_contract"]
        self.assertEqual(endpoint["status"], "FROZEN_NOT_POPULATED")
        self.assertEqual(
            endpoint["accepted_export_schema"]["schema_id"],
            "quantum-weyl-berger-endpoint-a24-cauchy-export-v1",
        )
        self.assertEqual(len(endpoint["factor_records"]), 4)
        q_contract = self.certificate["q_Cauchy_import_contract"]
        self.assertEqual(q_contract["status"], "FROZEN_NOT_POPULATED")
        self.assertEqual(q_contract["required_artifacts"]["q52_companion"]["shape"], [52, 52])
        self.assertEqual(q_contract["required_artifacts"]["q_Cauchy_104"]["shape"], [104, 104])

    def test_future_endpoint_export_schema_is_operational_and_fail_closed(self) -> None:
        schema = json.loads(
            (HERE / "schema/berger-endpoint-a24-cauchy-export-v1.schema.json").read_text()
        )
        endpoint = self.certificate["endpoint_A24_import_contract"]
        factor_records = {}
        for contract in endpoint["factor_records"]:
            factor_id = contract["factor_record_id"]
            factor_records[factor_id] = {
                "factor_record_id": factor_id,
                "shape": [3, 3],
                "row_ids": ["r0", "r1", "r2"],
                "column_ids": ["c0", "c1", "c2"],
                "entries": [],
                "sha256": "0" * 64,
                "source_commit": "0" * 40,
            }
        payload = {
            "schema": "quantum-weyl-berger-endpoint-a24-cauchy-export-v1",
            "result_id": "BERGER_ENDPOINT_A24_CAUCHY_EXPORT",
            "result_state": "ENDPOINT_FACTORS_AND_DERIVED_A24_EXACT",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "classical_commit": "0" * 40,
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "coefficient_ring": "QQ",
            "differential_axis_order": ["t", "berger_frame_1", "berger_frame_2", "berger_frame_3"],
            "factor_records": factor_records,
            "derived_A12_blocks": {
                slot["block_id"]: {
                    "block_id": slot["block_id"],
                    "shape": [12, 12],
                    "local_ordering": slot["local_ordering"],
                    "entries": [],
                    "sha256": "0" * 64,
                }
                for slot in endpoint["derived_block_slots"]
            },
            "exact_checks": {check: True for check in endpoint["required_exact_checks"]},
            "claim_boundary": "Syntactic test fixture only; no scientific endpoint export is asserted by this unit-test payload.",
        }
        self.assertFalse(validate_instance(payload, schema))
        mutant = deepcopy(payload)
        del mutant["factor_records"]["F_spatial_K_spatial"]
        self.assertTrue(validate_instance(mutant, schema))
        mutant = deepcopy(payload)
        mutant["derived_A12_blocks"]["ghost_A12"]["local_ordering"].reverse()
        self.assertTrue(validate_instance(mutant, schema))

    def test_full_operator_and_quantum_claims_fail_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_FULL_A104_CAUCHY_OPERATOR"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["endpoint_A24_import_contract"]["status"] = "POPULATED"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
