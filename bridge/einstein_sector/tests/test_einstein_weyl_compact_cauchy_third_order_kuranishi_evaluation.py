import json
import copy
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-v1.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_cauchy_balanced_q2_q3_resonant_slice_v1.json"


class ThirdOrderKuranishiEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(CERT.read_text())

    def test_schema(self):
        jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.value)

    def test_slice_is_complete(self):
        value = json.loads(SLICE.read_text())
        self.assertEqual(value["term_counts"], {"q2": 832, "q3": 579})
        self.assertEqual(value["coefficient_derivative_order"], 5)

    def test_global_and_shell_verdicts_are_distinct(self):
        self.assertEqual(self.value["global_constraint_projection"]["intrinsic_global_K3_class"], "0")
        self.assertFalse(self.value["classification"]["bounded_third_order_extension"])
        self.assertTrue(self.value["classification"]["smooth_secular_third_order_extension"])

    def test_all_original_shells_have_a_witness(self):
        rows = {tuple(row["target"]): row for row in self.value["resonant_shells"]}
        self.assertEqual(set(rows), {(-1, 0), (1, 0), (0, -1), (0, 1)})
        for row in rows.values():
            self.assertTrue(any(not witness["exact_zero"] for witness in row["pairing_witnesses"]))

    def test_status_mutations_are_rejected(self):
        schema = json.loads(SCHEMA.read_text())
        mutations = []
        bounded = copy.deepcopy(self.value)
        bounded["classification"]["bounded_third_order_extension"] = True
        mutations.append(bounded)
        global_class = copy.deepcopy(self.value)
        global_class["global_constraint_projection"]["K3_representative"][0] = "1"
        mutations.append(global_class)
        omitted_shell = copy.deepcopy(self.value)
        omitted_shell["resonant_shells"].pop()
        mutations.append(omitted_shell)
        causal = copy.deepcopy(self.value)
        causal["classification"]["causal_retarded_third_order_extension"] = True
        mutations.append(causal)
        for mutation in mutations:
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.Draft202012Validator(schema).validate(mutation)


if __name__ == "__main__":
    unittest.main()
