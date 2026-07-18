import copy
import unittest

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


if __name__ == "__main__":
    unittest.main()
