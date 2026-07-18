import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from d_quotient_classical.relative import relative_linfinity_through_arity_three_preflight as result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_executable_taylor_fixture(directory: Path, result_id: str, theory_id: str) -> dict:
    carrier_id = f"synthetic_{theory_id.lower().replace('-', '_')}_carrier"

    def payload(kind: str, content: dict) -> dict:
        return {
            "schema": "pure-weyl-relative-linfinity-product-pbw-payload-v1",
            "result_id": f"{result_id}_{kind.upper()}",
            "kind": kind,
            "theory_id": theory_id,
            "background_id": result.BACKGROUND_ID,
            "carrier_id": carrier_id,
            "coefficient_field": "Q",
            "content": content,
        }

    values = {
        "row_layout": payload("row_layout", {"row_count": 1, "rows": [{"index": 0, "row_id": "x", "degree": 0, "parity": "even", "bundle_id": "scalar", "dual_row": 0}]}),
        "action": payload("action", {"density": "x^2/2+x^3/6+x^4/24", "couplings": {}, "background_substitution": {"x": "0"}, "master_terms": ["S_cl"], "derivation_convention": "q_n is the n-th polarized Taylor coefficient of the BV Hamiltonian vector field at the declared background, with no factorial absorbed"}),
        "q1": payload("operation", {"arity": 1, "row_count": 1, "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1", "maximum_total_order": 0, "term_count": 1, "terms": [{"output_row": 0, "inputs": [{"row": 0, "word": []}], "coefficient": "1", "coefficient_jets": [{"word": [], "coefficient": "1"}]}]}),
        "q2": payload("operation", {"arity": 2, "row_count": 1, "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1", "maximum_total_order": 0, "term_count": 1, "terms": [{"output_row": 0, "inputs": [{"row": 0, "word": []}, {"row": 0, "word": []}], "coefficient": "1", "coefficient_jets": [{"word": [], "coefficient": "1"}]}]}),
        "q3": payload("operation", {"arity": 3, "row_count": 1, "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1", "maximum_total_order": 0, "term_count": 1, "terms": [{"output_row": 0, "inputs": [{"row": 0, "word": []}, {"row": 0, "word": []}, {"row": 0, "word": []}], "coefficient": "1", "coefficient_jets": [{"word": [], "coefficient": "1"}]}]}),
        "pairing": payload("pairing", {"row_count": 1, "term_count": 1, "terms": [{"left_row": 0, "right_row": 0, "coefficient": "1"}]}),
    }
    artifacts = {}
    for name, value in values.items():
        path = directory / f"{theory_id.lower().replace('-', '_')}_{name}.json"
        path.write_text(json.dumps(value, sort_keys=True))
        artifacts[name] = {"result_id": value["result_id"], "kind": value["kind"], "path": str(path.relative_to(result.ROOT)), "sha256": _sha256(path)}
    for name, kind, body in (("independent_verifier", "independent_verifier", "# fixture\n"), ("verification_receipt", "verification_receipt", "{}\n")):
        path = directory / f"{theory_id.lower().replace('-', '_')}_{name}.txt"
        path.write_text(body)
        artifacts[name] = {"result_id": f"{result_id}_{name.upper()}", "kind": kind, "path": str(path.relative_to(result.ROOT)), "sha256": _sha256(path)}
    value = result.synthetic_taylor(result_id, theory_id)
    value["carrier_id"] = carrier_id
    value["coefficient_field"] = "Q"
    value["taylor_artifacts"] = artifacts
    value["executable_contract"]["row_layout_sha256"] = artifacts["row_layout"]["sha256"]
    value["executable_contract"]["action_sha256"] = artifacts["action"]["sha256"]
    return value


class RelativeLinfinityPreflightTests(unittest.TestCase):
    def test_current_gate_imports_einstein_and_waits_for_weyl(self):
        value = result.build()
        self.assertEqual(value["input_status"]["relative_linear_triangle"], "IMPORTED")
        self.assertEqual(value["input_status"]["einstein_product_q2_q3"], "IMPORTED")
        self.assertEqual(value["input_status"]["weyl_product_q2_q3"], "MISSING")
        self.assertFalse(value["claim_flags"]["ALL_SCIENTIFIC_INPUTS_IMPORTED"])
        self.assertNotIn("relative_branch_dictionary", value["dependency_refs"])
        self.assertFalse(value["scope_guard"]["berger_tensors_eligible"])
        self.assertFalse(value["claim_flags"]["Q4_AUTHORIZED"])

    def test_synthetic_product_payload_validates(self):
        value = result.synthetic_taylor("WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
        result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)

    def test_executable_product_payload_validates_content(self):
        with tempfile.TemporaryDirectory(dir=result.ROOT) as temporary:
            value = _write_executable_taylor_fixture(Path(temporary), "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
            result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Weyl-Maxwell")

    def test_berger_payload_is_rejected(self):
        value = result.synthetic_taylor("WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
        value["background_id"] = "fixed_rational_positive_Berger_clock"
        with self.assertRaises(Exception):
            result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)

    def test_missing_arity_three_identity_is_rejected(self):
        value = copy.deepcopy(result.synthetic_taylor("EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Einstein-Maxwell"))
        value["acceptance_flags"]["ARITY_THREE_IDENTITY_VERIFIED"] = False
        with self.assertRaises(Exception):
            result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Einstein-Maxwell", verify_artifacts=False)

    def test_triangle_background_is_explicit(self):
        value = result.synthetic_triangle()
        result.validate_triangle(value)
        value["background_id"] = "fixed_rational_positive_Berger_clock"
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_triangle_artifact_hash_is_verified(self):
        value = result.synthetic_triangle()
        value["triangle_artifacts"]["inclusion"]["sha256"] = "0" * 64
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_generic_cyclic_map_inertia_obstruction_must_be_respected(self):
        value = result.synthetic_triangle()
        value["acceptance_flags"]["GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED"] = False
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_generic_cyclic_map_inertia_obstruction_requires_hashed_artifact(self):
        value = result.synthetic_triangle()
        del value["triangle_artifacts"]["generic_cyclic_map_inertia_obstruction"]
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_standard_pairing_cyclic_map_cannot_be_restored(self):
        value = result.synthetic_triangle()
        value["pairing_disposition"]["standard_pairing_cyclic_map_exists"] = True
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_three_forms_must_remain_distinct(self):
        value = result.synthetic_triangle()
        value["pairing_disposition"]["three_forms_kept_distinct"] = False
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_missing_inputs_cannot_claim_ready(self):
        value = result.build()
        value["result_state"] = "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY"
        with self.assertRaises(Exception):
            result.verify(value)

    def test_all_valid_inputs_activate_relative_morphism_solve(self):
        with tempfile.TemporaryDirectory(dir=result.ROOT) as temporary:
            directory = Path(temporary)
            triangle_path = directory / "triangle.json"
            einstein_path = directory / "einstein.json"
            weyl_path = directory / "weyl.json"
            triangle_path.write_text(json.dumps(result.synthetic_triangle()))
            einstein_path.write_text(json.dumps(_write_executable_taylor_fixture(directory,
                "EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
                "Einstein-Maxwell",
            )))
            weyl_path.write_text(json.dumps(_write_executable_taylor_fixture(directory,
                "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
                "Weyl-Maxwell",
            )))
            absent = directory / "absent.json"
            with (
                patch.object(result, "TRIANGLE_CANDIDATES", (triangle_path, absent)),
                patch.object(result, "EINSTEIN_CANDIDATES", (einstein_path, absent)),
                patch.object(result, "WEYL_CANDIDATES", (weyl_path, absent)),
            ):
                value = result.build()
        self.assertTrue(all(status == "IMPORTED" for status in value["input_status"].values()))
        self.assertTrue(value["claim_flags"]["ALL_SCIENTIFIC_INPUTS_IMPORTED"])
        self.assertEqual(value["result_state"], "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY")
        self.assertEqual(value["next_gate"], "COMPUTE_RELATIVE_ARITY_TWO_AND_THREE_DEFECTS")


if __name__ == "__main__":
    unittest.main()
