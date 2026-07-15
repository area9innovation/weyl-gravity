from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TRANSFER_ROOT / "support_local_q2_consumer.py"
SPEC = importlib.util.spec_from_file_location("support_local_q2_consumer_registry_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CONSUMER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CONSUMER
SPEC.loader.exec_module(CONSUMER)

CONSUMER_TEST_PATH = TRANSFER_ROOT / "tests" / "test_support_local_q2_consumer.py"
FIXTURE_SPEC = importlib.util.spec_from_file_location("support_local_consumer_fixture", CONSUMER_TEST_PATH)
assert FIXTURE_SPEC is not None and FIXTURE_SPEC.loader is not None
FIXTURE = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(FIXTURE)


class EvaluatorRegistryTests(unittest.TestCase):
    def test_registered_fixture_dispatch_is_content_addressed(self) -> None:
        parsed = CONSUMER.parse_support_local_export(FIXTURE.canonical_payload())
        registry = CONSUMER.build_evaluator_registry()
        descriptor = registry.descriptor("scalar-identity-fixture-v1")
        self.assertEqual(len(descriptor.implementation_manifest_sha256), 64)
        self.assertEqual(descriptor.allowed_operator_ids, ("scalar_identity",))
        evaluated = CONSUMER.evaluate_registered(
            parsed,
            evaluator_id="scalar-identity-fixture-v1",
            registry=registry,
        )
        self.assertFalse(evaluated.q2.is_zero())

    def test_unknown_or_schema_mismatched_evaluator_fails_closed(self) -> None:
        parsed = CONSUMER.parse_support_local_export(FIXTURE.canonical_payload())
        registry = CONSUMER.build_evaluator_registry()
        with self.assertRaisesRegex(ValueError, "unregistered evaluator"):
            CONSUMER.evaluate_registered(parsed, evaluator_id="physical-guessed-v1", registry=registry)
        with self.assertRaisesRegex(ValueError, "does not accept"):
            registry.dispatch(
                "scalar-identity-fixture-v1",
                "different-expression-language-v1",
                parsed,
            )

    def test_duplicate_registration_is_rejected(self) -> None:
        registry = CONSUMER.build_evaluator_registry()
        descriptor = registry.descriptor("scalar-identity-fixture-v1")
        with self.assertRaisesRegex(ValueError, "duplicate evaluator"):
            registry.register(descriptor, CONSUMER.evaluate_identity_fixture)

    def test_declared_operator_inventory_is_enforced_before_dispatch(self) -> None:
        payload = FIXTURE.canonical_payload()
        payload["q2"]["components"][0]["expression"]["terms"][0]["monomial"]["operator_id"] = "undeclared_Bach"
        payload["q2"]["components"][0]["expression"]["terms"][1]["monomial"]["operator_id"] = "undeclared_Bach"
        FIXTURE.FIXTURE._rehash(payload)
        parsed = CONSUMER.parse_support_local_export(payload)
        with self.assertRaisesRegex(ValueError, "outside its declared inventory"):
            CONSUMER.evaluate_registered(
                parsed,
                evaluator_id="scalar-identity-fixture-v1",
            )


if __name__ == "__main__":
    unittest.main()
