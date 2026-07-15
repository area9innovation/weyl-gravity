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


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = _load("total_d_disposition_test_module", TRANSFER_ROOT / "total_d_disposition.py")
CERTIFICATE = _load(
    "total_d_disposition_certificate_test_module",
    TRANSFER_ROOT / "total_d_disposition_certificate.py",
)


def _terminal_payload(verdict: str) -> dict[str, object]:
    payload = deepcopy(CERTIFICATE.build_certificate())
    payload["result_id"] = f"FIXTURE_{verdict}"
    payload["claim_status"] = "CERTIFIED"
    payload["assessment_status"] = "COMPUTED"
    payload["verdict"] = verdict
    payload["charge_audit"].update(
        {
            "combined_gravitational_matter_presymplectic_contraction": "COMPUTED",
            "normalization": "FIXED",
            "allowed_fixed_coupling_delta_Q_tangent": "EXISTS",
        }
    )
    signatures = {
        "D_GAUGE": ("INTEGRABLE", "D_IN_KERNEL", "ZERO"),
        "D_CHARGED": ("INTEGRABLE", "D_NOT_IN_KERNEL", "NONZERO"),
        "SECTOR_DEPENDENT": (
            "SECTOR_DEPENDENT",
            "SECTOR_DEPENDENT",
            "SECTOR_DEPENDENT",
        ),
        "NOT_HAMILTONIAN": ("NONINTEGRABLE", "NOT_DEFINED", "NOT_DEFINED"),
    }
    (
        payload["charge_audit"]["integrability"],
        payload["charge_audit"]["presymplectic_kernel"],
        payload["charge_audit"]["total_D_charge_variation"],
    ) = signatures[verdict]
    payload["exact_checks"] = {key: True for key in payload["exact_checks"]}
    payload["fail_closed"] = {
        "D_quotient_authorized": verdict == "D_GAUGE",
        "unresolved_fields": [],
        "claim_boundary": "Exact fixture classification only.",
    }
    payload["sector_ledger"] = []
    if verdict == "SECTOR_DEPENDENT":
        payload["charge_audit"]["allowed_fixed_coupling_delta_Q_tangent"] = "SECTOR_DEPENDENT"
        payload["sector_ledger"] = [
            {
                "sector_id": "zero-charge-sector",
                "phase_space_id": payload["phase_space_id"],
                "verdict": "D_GAUGE",
                "total_D_charge_variation": "ZERO",
                "presymplectic_kernel": "D_IN_KERNEL",
            },
            {
                "sector_id": "charged-sector",
                "phase_space_id": payload["phase_space_id"],
                "verdict": "D_CHARGED",
                "total_D_charge_variation": "NONZERO",
                "presymplectic_kernel": "D_NOT_IN_KERNEL",
            },
        ]
    return payload


class TotalDDispositionTests(unittest.TestCase):
    def test_checked_in_scoped_D_gauge_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        rebuilt = CERTIFICATE.build_certificate()
        self.assertEqual(checked, rebuilt)
        disposition = CONTRACT.validate_total_d_disposition(rebuilt)
        self.assertEqual(disposition.status, "D_GAUGE")
        self.assertTrue(disposition.D_quotient_authorized)
        self.assertEqual(
            disposition.dependency_tags,
            ("LOCAL-ALGEBRAIC", "REDUCED-MODE"),
        )
        self.assertEqual(
            rebuilt["charge_audit"]["allowed_fixed_coupling_delta_Q_tangent"],
            "ABSENT",
        )
        self.assertEqual(
            rebuilt["charge_audit"]["total_D_charge_variation"],
            "ZERO",
        )

    def test_all_four_canonical_terminal_verdicts_validate(self) -> None:
        for verdict in CONTRACT.TERMINAL_DISPOSITIONS:
            with self.subTest(verdict=verdict):
                disposition = CONTRACT.validate_total_d_disposition(
                    _terminal_payload(verdict)
                )
                self.assertEqual(disposition.status, verdict)
                self.assertEqual(
                    disposition.D_quotient_authorized,
                    verdict == "D_GAUGE",
                )

    def test_noncanonical_D_charged_alias_is_rejected(self) -> None:
        payload = _terminal_payload("D_CHARGED")
        payload["verdict"] = "D_CHARGED_NO_QUOTIENT"
        with self.assertRaisesRegex(ValueError, "verdict is invalid"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_terminal_verdict_requires_combined_current_and_tangent_audit(self) -> None:
        payload = _terminal_payload("D_GAUGE")
        payload["charge_audit"][
            "combined_gravitational_matter_presymplectic_contraction"
        ] = "OPEN"
        with self.assertRaisesRegex(ValueError, "combined presymplectic contraction"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = _terminal_payload("D_GAUGE")
        payload["charge_audit"]["allowed_fixed_coupling_delta_Q_tangent"] = "OPEN"
        with self.assertRaisesRegex(ValueError, "tangent audit"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_verdict_signature_and_authorization_cannot_be_forged(self) -> None:
        payload = _terminal_payload("D_GAUGE")
        payload["charge_audit"]["total_D_charge_variation"] = "NONZERO"
        with self.assertRaisesRegex(ValueError, "audit signature"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = _terminal_payload("D_CHARGED")
        payload["fail_closed"]["D_quotient_authorized"] = True
        with self.assertRaisesRegex(ValueError, "authorization"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_sector_dependent_verdict_requires_consistent_sector_ledger(self) -> None:
        payload = _terminal_payload("SECTOR_DEPENDENT")
        payload["sector_ledger"] = []
        with self.assertRaisesRegex(ValueError, "lacks a sector ledger"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = _terminal_payload("SECTOR_DEPENDENT")
        payload["sector_ledger"][0]["total_D_charge_variation"] = "NONZERO"
        with self.assertRaisesRegex(ValueError, "disagrees"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_scope_hash_commit_and_dependency_mutations_fail_closed(self) -> None:
        payload = CERTIFICATE.build_certificate()
        payload["boundary_conditions_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "boundary-condition hash"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = CERTIFICATE.build_certificate()
        payload["provenance"]["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "disagrees with classical"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = CERTIFICATE.build_certificate()
        payload["dependency_tags"] = ["LOCAL-ALGEBRAIC"]
        with self.assertRaisesRegex(ValueError, "lost REDUCED-MODE"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_source_manifest_canonical_hash_is_checked(self) -> None:
        payload = CERTIFICATE.build_certificate()
        payload["provenance"]["source_manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "canonical hash mismatch"):
            CONTRACT.validate_total_d_disposition(payload)

    def test_source_artifacts_require_immutable_git_commits(self) -> None:
        payload = CERTIFICATE.build_certificate()
        payload["provenance"]["source_artifacts"][0].pop("git_commit")
        with self.assertRaisesRegex(ValueError, "wrong field set"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = CERTIFICATE.build_certificate()
        payload["provenance"]["source_artifacts"][0]["git_commit"] = "bad"
        with self.assertRaisesRegex(ValueError, "commit is invalid"):
            CONTRACT.validate_total_d_disposition(payload)
        payload = CERTIFICATE.build_certificate()
        payload["provenance"]["source_artifacts"][0]["path"] = "../../escape.json"
        with self.assertRaisesRegex(ValueError, "escapes the repository"):
            CONTRACT.validate_total_d_disposition(payload)


if __name__ == "__main__":
    unittest.main()
