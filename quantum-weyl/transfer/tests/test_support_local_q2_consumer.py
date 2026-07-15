from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
CONSUMER_PATH = TRANSFER_ROOT / "support_local_q2_consumer.py"
CONSUMER_SPEC = importlib.util.spec_from_file_location("support_local_q2_consumer", CONSUMER_PATH)
assert CONSUMER_SPEC is not None and CONSUMER_SPEC.loader is not None
CONSUMER = importlib.util.module_from_spec(CONSUMER_SPEC)
sys.modules[CONSUMER_SPEC.name] = CONSUMER
CONSUMER_SPEC.loader.exec_module(CONSUMER)

IMPORT_TEST = TRANSFER_ROOT.parent / "classical_import" / "tests" / "test_verify_support_local_q2_export.py"
FIXTURE_SPEC = importlib.util.spec_from_file_location("support_local_q2_fixture", IMPORT_TEST)
assert FIXTURE_SPEC is not None and FIXTURE_SPEC.loader is not None
FIXTURE = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(FIXTURE)


def _identity_monomial(arity: int) -> dict[str, object]:
    return {
        "operator_id": "scalar_identity",
        "input_jets": [[0, 0, 0, 0] for _ in range(arity)],
        "free_indices": [],
        "contractions": [],
    }


def canonical_payload() -> dict[str, object]:
    payload = FIXTURE.valid_payload()
    payload["expression_schema_version"] = "quantum-weyl-canonical-local-expression-v1"
    payload["q2"]["components"][0]["expression"] = {
        "terms": [
            {
                "coefficient": {"numerator": 1, "denominator": 2},
                "monomial": _identity_monomial(2),
            },
            {
                "coefficient": {"numerator": 1, "denominator": 2},
                "monomial": _identity_monomial(2),
            },
        ]
    }
    payload["D_action"]["components"][0]["expression"] = {
        "terms": [{"coefficient": 0, "monomial": _identity_monomial(1)}]
    }
    return FIXTURE._rehash(payload)


class SupportLocalQ2ConsumerTests(unittest.TestCase):
    def test_payload_parses_canonically_and_evaluates_exact_fixture(self) -> None:
        parsed = CONSUMER.parse_support_local_export(canonical_payload())
        self.assertEqual(parsed.expression_schema_version, "quantum-weyl-canonical-local-expression-v1")
        self.assertEqual(len(parsed.q2_components[0].expression.terms), 1)
        evaluated = CONSUMER.evaluate_identity_fixture(parsed)
        symbol_index = {symbol: index for index, symbol in enumerate(parsed.symbols)}
        self.assertEqual(
            evaluated.q2.entries[symbol_index["xi"]][symbol_index["h"]][symbol_index["h"]],
            1,
        )
        self.assertTrue(evaluated.complex.linear_bracket(
            evaluated.complex.q1, evaluated.q2, name="[q1,q2]"
        ).is_zero())

    def test_unknown_expression_language_fails_closed(self) -> None:
        payload = canonical_payload()
        payload["expression_schema_version"] = "unknown-language-v9"
        FIXTURE._rehash(payload)
        with self.assertRaisesRegex(ValueError, "no registered"):
            CONSUMER.parse_support_local_export(payload)

    def test_expression_exceeding_declared_jet_bound_fails_closed(self) -> None:
        payload = canonical_payload()
        monomial = payload["q2"]["components"][0]["expression"]["terms"][0]["monomial"]
        monomial["input_jets"][0] = [1, 0, 0, 0]
        FIXTURE._rehash(payload)
        with self.assertRaisesRegex(ValueError, "input jet bound"):
            CONSUMER.parse_support_local_export(payload)

    def test_fixture_evaluator_rejects_nonidentity_local_operator(self) -> None:
        payload = canonical_payload()
        payload["q2"]["components"][0]["expression"]["terms"][0]["monomial"]["operator_id"] = "Bach"
        payload["q2"]["components"][0]["expression"]["terms"][1]["monomial"]["operator_id"] = "Bach"
        FIXTURE._rehash(payload)
        parsed = CONSUMER.parse_support_local_export(payload)
        with self.assertRaisesRegex(ValueError, "only accepts scalar_identity"):
            CONSUMER.evaluate_identity_fixture(parsed)


if __name__ == "__main__":
    unittest.main()
