from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from cartan.ward_insertion_contract import (
    CONSISTENCY_CHECKS,
    OPERATOR_DEGREES,
    validate_ward_insertion_export,
)
from cartan.ward_insertion_contract_certificate import OUTPUT, ROOT, build_certificate
from local_bv.schema_validation import validate_instance


class WardInsertionContractTests(unittest.TestCase):
    def _artifact(self, root: Path, name: str, format_: str) -> dict[str, str]:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name + "\n", encoding="utf-8")
        return {
            "format": format_,
            "path": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _payload(self, root: Path, *, restored: bool) -> dict[str, object]:
        operators = {
            name: {
                "degree": degree,
                "evaluator_id": "finite-exact-fixture-v1",
                "expression_schema_version": "finite-exact-matrix-v1",
                "artifact": self._artifact(
                    root, f"operators/{name}.json", "JSON_LOCAL_OPERATOR"
                ),
            }
            for name, degree in OPERATOR_DEGREES.items()
        }
        checks = {}
        for name in CONSISTENCY_CHECKS:
            status = "VERIFIED"
            if name in {"Q0_squared_zero", "first_order_Ward_compatibility"}:
                status = "VERIFIED_ZERO"
            if name == "first_order_QME_linearization":
                status = "VERIFIED_ZERO" if restored else "COMPUTED_NONZERO"
            if name == "defect_consistency_Q_closed":
                status = "VERIFIED_ZERO" if restored else "SOURCED_NONZERO"
            checks[name] = {
                "status": status,
                "proof_artifact": self._artifact(
                    root, f"proofs/{name}.json", "JSON_PROOF_CERTIFICATE"
                ),
            }
        return {
            "schema": "quantum-weyl-renormalized-D-ward-insertion-export-v1",
            "result_id": "RENORMALIZED_D_WARD_INSERTION",
            "result_state": (
                "QME_RESTORED_CARTAN_CLASSIFIED"
                if restored
                else "REGULATED_BREAKING_COMPUTED_QME_OPEN"
            ),
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "setting_id": "vacuum_cylinder",
            "generator_id": "D_compact",
            "phase_space_id": "compact_quantum",
            "renormalization": {
                "signature": "Euclidean",
                "gauge": "fixture",
                "regularization": "fixture",
                "scheme": "fixture",
                "boundary_conditions": "closed_spatial_cylinder",
                "zero_mode_policy": "explicit_projection",
            },
            "observable_complex": {
                "algebra_id": "finite_fixture",
                "grading_convention": "cohomological",
                "representation_artifact": self._artifact(
                    root, "observable/complex.json", "JSON_OBSERVABLE_COMPLEX"
                ),
                "admissibility_policy_artifact": self._artifact(
                    root, "observable/policy.json", "JSON_ADMISSIBILITY_POLICY"
                ),
            },
            "operators": operators,
            "slavnov": {
                "qme_status": "RESTORED" if restored else "NOT_RESTORED_SOURCE_RETAINED",
                "regulated_breaking": self._artifact(
                    root, "slavnov/breaking.json", "JSON_PROOF_CERTIFICATE"
                ),
                "qme_source": (
                    None
                    if restored
                    else self._artifact(root, "slavnov/source.json", "JSON_LOCAL_OPERATOR")
                ),
            },
            "consistency_checks": checks,
            "cartan_defect": {
                "status": "ZERO" if restored else "UNDEFINED_ANALYTICALLY",
                "artifact": self._artifact(root, "cartan/defect.json", "JSON_LOCAL_OPERATOR"),
                "primitive": None,
                "dual_witness": None,
            },
            "local_to_cartan_map": {
                "status": "CONSTRUCTED" if restored else "NOT_CONSTRUCTED",
                "artifact": (
                    self._artifact(root, "cartan/map.json", "JSON_LOCAL_OPERATOR")
                    if restored
                    else None
                ),
            },
            "claim_boundary": "Finite fixture only.",
        }

    def test_checked_certificate_and_schema_reproduce(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "renormalized-D-ward-insertion-contract-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))

    def test_restored_zero_branch_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_ward_insertion_export(
                self._payload(root, restored=True), repository_root=root
            )
        self.assertEqual(result["cartan_status"], "ZERO")
        self.assertEqual(result["map_status"], "CONSTRUCTED")

    def test_sourced_open_branch_remains_unclassified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_ward_insertion_export(
                self._payload(root, restored=False), repository_root=root
            )
        self.assertEqual(result["qme_status"], "NOT_RESTORED_SOURCE_RETAINED")
        self.assertEqual(result["cartan_status"], "UNDEFINED_ANALYTICALLY")

    def test_operator_degree_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, restored=True)
            payload["operators"]["iota_D1"]["degree"] = 0
            with self.assertRaisesRegex(ValueError, "wrong degree"):
                validate_ward_insertion_export(payload, repository_root=root)

    def test_qme_promotion_with_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, restored=True)
            payload["slavnov"]["qme_source"] = self._artifact(
                root, "slavnov/forged_source.json", "JSON_LOCAL_OPERATOR"
            )
            with self.assertRaisesRegex(ValueError, "closure gate"):
                validate_ward_insertion_export(payload, repository_root=root)

    def test_local_map_cannot_precede_qme_restoration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, restored=False)
            payload["local_to_cartan_map"] = {
                "status": "CONSTRUCTED",
                "artifact": self._artifact(root, "cartan/early_map.json", "JSON_LOCAL_OPERATOR"),
            }
            with self.assertRaisesRegex(ValueError, "QME gate"):
                validate_ward_insertion_export(payload, repository_root=root)

    def test_nontrivial_status_requires_dual_witness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, restored=True)
            payload["cartan_defect"]["status"] = "NONTRIVIAL_ANOMALY"
            with self.assertRaisesRegex(ValueError, "unique witness"):
                validate_ward_insertion_export(payload, repository_root=root)

    def test_unknown_consistency_status_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, restored=False)
            payload["consistency_checks"]["Q0_squared_zero"]["status"] = "ASSUMED"
            with self.assertRaisesRegex(ValueError, "invalid status"):
                validate_ward_insertion_export(payload, repository_root=root)


if __name__ == "__main__":
    unittest.main()
