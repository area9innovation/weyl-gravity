import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from d_quotient_classical.backreacted_clock import berger_mixed_ell3_branch_projection_importer as result


class BranchProjectionImporterTests(unittest.TestCase):
    def test_current_import_is_fail_closed(self):
        value = result.build()
        self.assertEqual(value["input_contract"]["status"], "MISSING")
        self.assertFalse(value["claim_flags"]["BRIDGE_2_ACTIVATED"])
        self.assertEqual(value["downstream_disposition"]["projected_operation"], "NO_CERTIFIED_MAP")
        self.assertFalse(value["claim_flags"]["Q4_AUTHORIZED"])

    def test_synthetic_contract_validates(self):
        result.validate_candidate(result.synthetic_candidate(), verify_artifacts=False)

    def test_background_name_matching_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["background_id"] = "compact_product_with_similarly_named_modes"
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_missing_pairing_transport_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["acceptance_flags"]["PAIRING_TRANSPORT_VERIFIED"] = False
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_interaction_alias_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["interaction_dependency"]["path"] = "bridge/certificates/similarly_named_interaction.json"
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_incomplete_mode_scope_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        del value["mode_scope"]["omega"]
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_missing_crosswalk_evidence_role_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["map_artifacts"] = [
            artifact for artifact in value["map_artifacts"]
            if artifact["role"] != "carrier_crosswalk"
        ]
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_reduced_mode_nonlocal_map_requires_dependency_tag(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["map_category"] = "REDUCED_MODE_NONLOCAL"
        value["dependency_tags"] = ["LOCAL-ALGEBRAIC"]
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_untyped_evidence_artifact_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        del value["map_artifacts"][0]["schema_path"]
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_duplicate_evidence_role_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["map_artifacts"][1]["role"] = value["map_artifacts"][0]["role"]
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=False)

    def test_repository_escape_is_rejected(self):
        value = copy.deepcopy(result.synthetic_candidate())
        value["map_artifacts"][0]["path"] = "../outside.json"
        with self.assertRaises(Exception):
            result.validate_candidate(value, verify_artifacts=True)

    def test_typed_candidate_activates_receiver_end_to_end(self):
        with tempfile.TemporaryDirectory(dir=result.ROOT) as directory:
            root = Path(directory)
            artifact_schema = root / "artifact.schema.json"
            artifact_schema.write_text(json.dumps({
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "additionalProperties": False,
                "required": ["result_id"],
                "properties": {"result_id": {"type": "string", "minLength": 1}},
            }))
            candidate = result.synthetic_candidate()
            for artifact in candidate["map_artifacts"]:
                payload = root / f"{artifact['role']}.json"
                payload.write_text(json.dumps({"result_id": artifact["result_id"]}))
                artifact.update({
                    "path": str(payload.relative_to(result.ROOT)),
                    "sha256": result._sha256(payload),
                    "schema_path": str(artifact_schema.relative_to(result.ROOT)),
                    "schema_sha256": result._sha256(artifact_schema),
                })
            candidate_path = root / "candidate.json"
            candidate_path.write_text(json.dumps(candidate))
            with mock.patch.object(result, "CANDIDATES", (candidate_path, root / "absent.json")):
                value = result.build()
        self.assertEqual(value["input_contract"]["status"], "IMPORTED")
        self.assertTrue(value["claim_flags"]["BRIDGE_2_ACTIVATED"])
        self.assertEqual(value["downstream_disposition"]["projected_operation"], "OPEN")
        self.assertEqual(value["imported_branch_map"]["mode_scope"], candidate["mode_scope"])


if __name__ == "__main__":
    unittest.main()
