from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_pbw_backend_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_pbw_backend_certificate_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)
BACKEND = sys.modules[CERTIFICATE.build_operator_backend_registry.__module__]


class BergerPBWBackendTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_backend_is_content_addressed_and_validates_import(self) -> None:
        registry = BACKEND.build_operator_backend_registry(repository_root=CERTIFICATE.ROOT)
        descriptor = registry.descriptor(BACKEND.BACKEND_ID)
        self.assertEqual(descriptor.supported_arities, (1,))
        self.assertEqual(descriptor.assembly_mode, "OPERATOR_VALIDATION_ONLY")
        self.assertFalse(descriptor.nd2_physical_assembly_authorized)
        payload = json.loads(CERTIFICATE.INPUT_PATH.read_text(encoding="utf-8"))
        verified = registry.validate(
            BACKEND.BACKEND_ID,
            BACKEND.EXPRESSION_SCHEMA_VERSION,
            payload,
            required_arity=1,
        )
        self.assertEqual(verified.retained_rows, 26)
        self.assertEqual(verified.pbw_term_count, 891)
        self.assertEqual(verified.maximum_differential_order, 4)

    def test_schema_arity_and_payload_drift_fail_closed(self) -> None:
        registry = BACKEND.build_operator_backend_registry(repository_root=CERTIFICATE.ROOT)
        payload = json.loads(CERTIFICATE.INPUT_PATH.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "does not accept"):
            registry.validate(
                BACKEND.BACKEND_ID,
                "forged-schema",
                payload,
                required_arity=1,
            )
        with self.assertRaisesRegex(ValueError, "does not support arity 2"):
            registry.validate(
                BACKEND.BACKEND_ID,
                BACKEND.EXPRESSION_SCHEMA_VERSION,
                payload,
                required_arity=2,
            )
        forged = deepcopy(payload)
        forged["nd2_gate"]["physical_execution_authorized"] = True
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            registry.validate(
                BACKEND.BACKEND_ID,
                BACKEND.EXPRESSION_SCHEMA_VERSION,
                forged,
                required_arity=1,
            )

    def test_duplicate_backend_and_false_validation_authorization_are_rejected(self) -> None:
        registry = BACKEND.build_operator_backend_registry(repository_root=CERTIFICATE.ROOT)
        descriptor = registry.descriptor(BACKEND.BACKEND_ID)
        with self.assertRaisesRegex(ValueError, "duplicate operator backend"):
            registry.register(descriptor, BACKEND.validate_retained_q1_receipt)
        fields = dict(descriptor.__dict__)
        fields["nd2_physical_assembly_authorized"] = True
        with self.assertRaisesRegex(ValueError, "validation-only"):
            BACKEND.OperatorBackendDescriptor(**fields)
        fields["nd2_physical_assembly_authorized"] = False
        fields["implementation_manifest"] = ()
        with self.assertRaisesRegex(ValueError, "manifest is required"):
            BACKEND.OperatorBackendDescriptor(**fields)


if __name__ == "__main__":
    unittest.main()
