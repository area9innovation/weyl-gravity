from __future__ import annotations

import copy
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


IMPORT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = IMPORT_ROOT / "verify_support_local_q2_export.py"
SPEC = importlib.util.spec_from_file_location("verify_support_local_q2_export", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


ROLE_DATA = (
    ("h", "metric", 0, 0, 0),
    ("xi", "diffeomorphism_ghost", 1, 0, 1),
    ("omega", "weyl_ghost", 1, 0, 1),
    ("h_star", "metric_antifield", -1, 1, 1),
    ("xi_star", "diffeomorphism_ghost_antifield", -2, 2, 0),
    ("omega_star", "weyl_ghost_antifield", -2, 2, 0),
)


def _generators() -> list[dict[str, object]]:
    return [
        {
            "symbol": symbol,
            "role": role,
            "sector": "minimal",
            "tensor_type": {"bundle": role},
            "ghost_number": ghost,
            "antifield_number": antifield,
            "form_degree": 0 if antifield == 0 else 4,
            "Grassmann_parity": parity,
            "mass_dimension": 0,
            "Weyl_weight": 0,
            "canonical_index_symmetry": {"kind": "fixture"},
        }
        for symbol, role, ghost, antifield, parity in ROLE_DATA
    ]


def _operator(
    arity: int,
    degree: int,
    components: list[dict[str, object]],
    symbols: list[str],
) -> dict[str, object]:
    return {
        "arity": arity,
        "degree": degree,
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "components": components,
        "row_completeness": [
            {
                "output": symbol,
                "status": "COMPLETE",
                "component_ids": [
                    component["component_id"]
                    for component in components
                    if component["output"] == symbol
                ],
            }
            for symbol in symbols
        ],
    }


def _rehash(payload: dict[str, object]) -> dict[str, object]:
    payload["canonical_hashes"] = {
        "support_metadata_hash": VERIFY._digest(
            {
                "convention": payload["convention"],
                "expression_schema_version": payload["expression_schema_version"],
                "support_category": payload["support_category"],
            }
        ),
        "generator_dictionary_hash": VERIFY._digest(payload["generators"]),
        "q1_hash": VERIFY._digest(payload["q1"]),
        "q2_hash": VERIFY._digest(payload["q2"]),
        "D_action_hash": VERIFY._digest(payload["D_action"]),
        "proof_checks_hash": VERIFY._digest(payload["proof_checks"]),
    }
    return payload


def valid_payload() -> dict[str, object]:
    generators = _generators()
    symbols = [generator["symbol"] for generator in generators]
    q2_component = {
        "component_id": "q2_h_h_xi",
        "output": "h",
        "inputs": ["h", "xi"],
        "max_jet_orders": [0, 1],
        "expression": {"terms": [{"coefficient": 1, "operator": "Lie"}]},
    }
    D_component = {
        "component_id": "D_h_h",
        "output": "h",
        "inputs": ["h"],
        "max_jet_orders": [1],
        "expression": {"terms": [{"coefficient": 1, "operator": "Lie_D"}]},
    }
    checks = [
        {
            "check_id": check_id,
            "status": "VERIFIED",
            "proof_artifact": {
                "path": f"proof/{check_id}.json",
                "sha256": "0" * 64,
            },
        }
        for check_id in sorted(VERIFY.REQUIRED_PROOF_CHECKS)
    ]
    payload: dict[str, object] = {
        "schema": "quantum-weyl-support-local-q2-export-v1",
        "classical_commit": "0" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "expression_schema_version": "test-local-expression-v1",
        "support_category": {
            "spacetime_dimension": 4,
            "background_id": "fixture",
            "boundary_conditions": "compact support",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "test_function_space": "C_c_infinity",
            "integration_by_parts_quotient": False,
            "maximum_jet_order": 4,
        },
        "generators": generators,
        "q1": _operator(1, 1, [], symbols),
        "q2": _operator(2, 1, [q2_component], symbols),
        "D_action": _operator(1, 0, [D_component], symbols),
        "proof_checks": checks,
    }
    return _rehash(payload)


class SupportLocalQ2ExportPreflightTests(unittest.TestCase):
    def test_complete_exact_fixture_passes(self) -> None:
        result = VERIFY.validate_export(valid_payload())
        self.assertEqual(result["status"], "PREFLIGHT_VERIFIED")
        self.assertEqual(result["generator_count"], 6)
        self.assertEqual(result["component_counts"]["q2"], 1)

    def test_finite_mode_substitution_fails_closed(self) -> None:
        payload = valid_payload()
        payload["support_category"]["locality"] = "FINITE_MODE"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "not support-local"):
            VERIFY.validate_export(payload)

    def test_missing_antifield_role_fails_closed(self) -> None:
        payload = valid_payload()
        payload["generators"][-1]["role"] = "other_antifield"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "missing minimal roles"):
            VERIFY.validate_export(payload)

    def test_incomplete_q2_row_fails_closed(self) -> None:
        payload = valid_payload()
        payload["q2"]["row_completeness"][0]["status"] = "INCOMPLETE"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "not COMPLETE"):
            VERIFY.validate_export(payload)

    def test_unknown_q2_input_fails_closed(self) -> None:
        payload = valid_payload()
        payload["q2"]["components"][0]["inputs"][1] = "missing"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "unknown input"):
            VERIFY.validate_export(payload)

    def test_float_expression_fails_closed(self) -> None:
        payload = valid_payload()
        payload["q2"]["components"][0]["expression"]["terms"][0]["coefficient"] = 1.0
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "floating-point"):
            VERIFY.validate_export(payload)

    def test_operator_parity_violation_fails_closed(self) -> None:
        payload = valid_payload()
        payload["q2"]["components"][0]["output"] = "h_star"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "parity degree"):
            VERIFY.validate_export(payload)

    def test_unverified_derivation_proof_fails_closed(self) -> None:
        payload = valid_payload()
        check = next(
            row for row in payload["proof_checks"] if row["check_id"] == "D_q2_derivation"
        )
        check["status"] = "NOT_COMPUTED"
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "not VERIFIED"):
            VERIFY.validate_export(payload)

    def test_hash_drift_fails_closed(self) -> None:
        payload = copy.deepcopy(valid_payload())
        payload["q2"]["components"][0]["max_jet_orders"][0] = 2
        with self.assertRaisesRegex(VERIFY.SupportLocalQ2ExportError, "hashes do not reproduce"):
            VERIFY.validate_export(payload)

    def test_proof_artifacts_are_pinned_to_worktree_and_commit(self) -> None:
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
            payload = valid_payload()
            for check in payload["proof_checks"]:
                path = root / check["proof_artifact"]["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                data = (check["check_id"] + "\n").encode("ascii")
                path.write_bytes(data)
                check["proof_artifact"]["sha256"] = hashlib.sha256(data).hexdigest()
            subprocess.run(["git", "add", "proof"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            payload["classical_commit"] = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            _rehash(payload)
            result = VERIFY.validate_export(payload, repository_root=root)
            self.assertEqual(result["proof_artifact_integrity_status"], "VERIFIED")

            first = root / payload["proof_checks"][0]["proof_artifact"]["path"]
            first.write_text("drift\n", encoding="ascii")
            with self.assertRaisesRegex(
                VERIFY.SupportLocalQ2ExportError, "working-tree proof hash"
            ):
                VERIFY.validate_export(payload, repository_root=root)


if __name__ == "__main__":
    unittest.main()
