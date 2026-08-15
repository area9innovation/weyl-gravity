from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_operator_portability_audit.py", "operator_portability_builder_test")
checker = module(HERE / "check_strict_386_operator_portability_audit.py", "operator_portability_checker_test")


class Strict386OperatorPortabilityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json").read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])

    def test_generated_current(self) -> None:
        result, report = builder.generated()
        self.assertEqual(result, (HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json").read_bytes())
        self.assertEqual(report, (HERE / "REPORT_STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.md").read_bytes())

    def test_contract_conflation_fails(self) -> None:
        value = deepcopy(self.value)
        value["portability_contracts"][2]["id"] = "FINITE_COMPONENT_JET_TABLE"
        self.assertTrue(checker.check(value))

    def test_full_q1_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] = True
        self.assertTrue(checker.check(value))

    def test_green_action_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_FULL_GREEN_PORTABLE_ACTION_SERIALIZED"] = True
        self.assertTrue(checker.check(value))

    def test_causal_theorem_revocation_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_CAUSAL_GREEN_HOMOTOPY_THEOREM_PRESERVED"] = False
        self.assertTrue(checker.check(value))

    def test_foundational_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["foundational_strength"]["weakest_base_for_analytic_green_action"] = "PRA"
        self.assertTrue(checker.check(value))

    def test_gate_and_quantum_promotions_fail(self) -> None:
        for key in ("CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            value = deepcopy(self.value)
            value["claim_flags"][key] = True
            self.assertTrue(checker.check(value), key)


if __name__ == "__main__":
    unittest.main()
