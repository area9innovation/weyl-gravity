from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from jsonschema import Draft202012Validator

from classical_import.verify_antifield_export_v2 import (
    AntifieldExportV2Error,
    _digest,
    synthetic_fixture,
    validate_export_v2,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema/antifield_export_v2.schema.json"


def _rehash(payload: dict) -> dict:
    payload["canonical_hashes"] = {
        "scope_hash": _digest(payload["scope"]),
        "generator_hash": _digest(payload["generators"]),
        "atom_hash": _digest(payload["atoms"]),
        "differential_hash": _digest(payload["differential"]),
        "dependency_hash": _digest(payload["dependency_refs"]),
    }
    return payload


def _row(payload: dict, component: str, atom: str) -> dict:
    return next(
        row
        for row in payload["differential"][component]["rows"]
        if row["source_atom"] == atom
    )


class AntifieldExportV2Tests(unittest.TestCase):
    def test_fixture_is_strict_and_independently_replayed(self) -> None:
        payload = synthetic_fixture()
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        result = validate_export_v2(payload)
        self.assertEqual(
            result["status"], "EXECUTABLE_V2_EXPORT_INDEPENDENTLY_REPLAYED"
        )
        self.assertFalse(result["producer_proofs_used_as_authority"])
        self.assertEqual(result["component_shifts"], [-1, 0])
        self.assertEqual(
            result["filtered_complex_adapter"]["status"],
            "FILTERED_LOCAL_COMPLEX_DRY_RUN_VERIFIED",
        )
        self.assertGreater(result["filtered_complex_adapter"]["afn0_space_count"], 0)

    def test_missing_base_generator_role_fails_closed(self) -> None:
        payload = synthetic_fixture()
        payload["generators"][0]["role"] = "other_minimal"
        with self.assertRaisesRegex(AntifieldExportV2Error, "roles are incomplete"):
            validate_export_v2(_rehash(payload))

    def test_float_and_opaque_expression_fail_closed(self) -> None:
        payload = synthetic_fixture()
        payload["scope"]["engineering_dimension_bound"] = 4.0
        with self.assertRaisesRegex(AntifieldExportV2Error, "floating-point"):
            validate_export_v2(payload)
        payload = synthetic_fixture()
        _row(payload, "gamma", "g")["image"] = {"opaque": "omega*g"}
        with self.assertRaisesRegex(AntifieldExportV2Error, "canonical polynomial AST"):
            validate_export_v2(_rehash(payload))

    def test_noncanonical_super_order_and_odd_square_fail_closed(self) -> None:
        payload = synthetic_fixture()
        _row(payload, "gamma", "g")["image"]["terms"][0]["factors"] = ["omega", "g"]
        with self.assertRaisesRegex(AntifieldExportV2Error, "canonical super-order"):
            validate_export_v2(_rehash(payload))
        payload = synthetic_fixture()
        _row(payload, "gamma", "g")["image"]["terms"][0]["factors"] = ["omega", "omega"]
        with self.assertRaisesRegex(AntifieldExportV2Error, "nilpotent odd square"):
            validate_export_v2(_rehash(payload))

    def test_Q_reconstruction_mutation_fails_closed(self) -> None:
        payload = synthetic_fixture()
        _row(payload, "Q", "g")["image"]["terms"][0]["coefficient"] = 2
        with self.assertRaisesRegex(AntifieldExportV2Error, "does not reconstruct"):
            validate_export_v2(_rehash(payload))

    def test_delta_gamma_identity_mutation_fails_closed(self) -> None:
        payload = synthetic_fixture()
        _row(payload, "gamma", "E_g")["image"]["terms"][0]["coefficient"] = -1
        _row(payload, "Q", "E_g")["image"]["terms"][0]["coefficient"] = -1
        with self.assertRaisesRegex(AntifieldExportV2Error, "anticommutator"):
            validate_export_v2(_rehash(payload))

    def test_grading_and_atom_order_mutations_fail_closed(self) -> None:
        payload = synthetic_fixture()
        payload["atoms"][0]["ghost_number"] = 2
        with self.assertRaisesRegex(AntifieldExportV2Error, "generator atom grading"):
            validate_export_v2(_rehash(payload))
        payload = synthetic_fixture()
        payload["atoms"][0]["canonical_order"] = 1
        with self.assertRaisesRegex(AntifieldExportV2Error, "canonical order"):
            validate_export_v2(_rehash(payload))

    def test_unsafe_dependency_and_hash_drift_fail_closed(self) -> None:
        payload = synthetic_fixture()
        payload["dependency_refs"]["field_dictionary"]["path"] = "../escape.json"
        with self.assertRaisesRegex(AntifieldExportV2Error, "safe content-addressed"):
            validate_export_v2(_rehash(payload))
        payload = synthetic_fixture()
        payload["dependency_refs"]["field_dictionary"]["sha256"] = "1" * 64
        with self.assertRaisesRegex(AntifieldExportV2Error, "hashes do not reproduce"):
            validate_export_v2(payload)

    def test_pinned_dependencies_and_proofs_are_checked_at_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "fixture@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Fixture"], cwd=root, check=True
            )
            payload = synthetic_fixture()
            references = [
                *payload["dependency_refs"].values(),
                *(check["proof_artifact"] for check in payload["producer_checks"]),
            ]
            for reference in references:
                path = root / reference["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                data = (reference["path"] + "\n").encode()
                path.write_bytes(data)
                reference["sha256"] = hashlib.sha256(data).hexdigest()
            subprocess.run(["git", "add", "proof"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            payload["classical_commit"] = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            result = validate_export_v2(_rehash(payload), repository_root=root)
            self.assertEqual(result["proof_artifact_integrity"], "VERIFIED")
            first = root / payload["dependency_refs"]["field_dictionary"]["path"]
            first.write_text("drift\n")
            with self.assertRaisesRegex(AntifieldExportV2Error, "working-tree"):
                validate_export_v2(payload, repository_root=root)


if __name__ == "__main__":
    unittest.main()
