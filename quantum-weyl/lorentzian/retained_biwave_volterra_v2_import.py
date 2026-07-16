"""Pinned quantum import of the repaired retained Berger Volterra theorem v2."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "eb56d5aff7d622de423d4994051b0e048c4fb4bf"
CLASSICAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
CLASSICAL_SCHEMA = "d_quotient_classical/schema/berger-retained-biwave-volterra-resolvent-v2.schema.json"
CLASSICAL_PRODUCER = "d_quotient_classical/backreacted_clock/berger_retained_biwave_volterra_resolvent.py"
CLASSICAL_VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_retained_biwave_volterra_resolvent.py"
CLASSICAL_TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_retained_biwave_volterra_resolvent.py"
CLASSICAL_REPORT = "d_quotient_classical/reports/berger-retained-biwave-volterra-resolvent-v2.md"
CLASSICAL_MANIFEST = "d_quotient_classical/manifests/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_SOURCE_MANIFEST.json"
CLASSICAL_RECEIPT = "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_VERIFICATION_RECEIPT.json"
HISTORICAL_AUDIT = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS.json"


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned v2 artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned v2 JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": _sha256_bytes(_git_blob(relative)),
    }


def _validate_source() -> tuple[dict[str, Any], dict[str, Any]]:
    source = _git_json(CLASSICAL_CERTIFICATE)
    schema = _git_json(CLASSICAL_SCHEMA)
    errors = validate_instance(source, schema)
    if errors:
        raise ValueError("pinned v2 source failed strict schema: " + "; ".join(errors))
    if (
        source.get("result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2"
        or source.get("schema") != "pure-weyl-berger-retained-biwave-volterra-resolvent-v2"
        or source.get("schema_version") != "2.0.0"
        or source.get("claim_status")
        != "CERTIFIED_TYPED_RETAINED_METRIC_CAUSAL_GREEN_OPERATORS"
        or source.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or source.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"
    ):
        raise ValueError("pinned v2 source identity drifted")
    if source.get("supersedes", {}).get("result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT":
        raise ValueError("v2 supersession ledger drifted")
    if not all(source.get("exact_checks", {}).values()):
        raise ValueError("v2 source exact check dropped")
    expected_true = {
        "BERGER_RETAINED_BIWAVE_COMPANION_EXACT",
        "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT",
        "BERGER_RETAINED_METRIC_GREEN_OPERATORS",
    }
    if {
        name for name, value in source.get("flags", {}).items() if value is True
    } != expected_true:
        raise ValueError("v2 source lifecycle boundary drifted")
    return source, schema


def _validate_proofs(source: dict[str, Any]) -> dict[str, bool]:
    artifacts = source["analytic_proof_artifacts"]
    expected_names = {
        "finite_slab_estimate",
        "causal_support_passage",
        "globalization_uniqueness",
        "inverse_identities",
        "adjoint_reversal",
    }
    if set(artifacts) != expected_names:
        raise ValueError("v2 analytic proof inventory drifted")
    proofs = {}
    for name, record in artifacts.items():
        if set(record) != {"format", "path", "sha256"} or record["format"] != "JSON_PROOF_CERTIFICATE":
            raise ValueError(f"v2 proof record drifted: {name}")
        blob = _git_blob(record["path"])
        if _sha256_bytes(blob) != record["sha256"]:
            raise ValueError(f"v2 proof hash mismatch: {name}")
        proofs[name] = json.loads(blob)

    finite = proofs["finite_slab_estimate"]
    if finite.get("spaces") != {
        "X_s(I)": "(C0(I;H^(s+1)) intersect C1(I;H^s)) direct_sum (C0(I;H^s) intersect C1(I;H^(s-1)))",
        "Y_s(I)": "L1(I;H^s) direct_sum L1(I;H^(s-1))",
        "spatial_bundle": "H^r means H^r(S3;Sym2)",
    }:
        raise ValueError("v2 time-regularity spaces drifted")
    if (
        "X_s(I)->X_s(I)" not in finite.get("solution_series_bound", "")
        or "Y_s(I)->Y_s(I)" not in finite.get("source_series_bound", "")
    ):
        raise ValueError("v2 two-sided factorial bounds drifted")

    support = proofs["causal_support_passage"].get("support_bound", {})
    if support != {
        "advanced": "supp(term f) subset J^-(supp f)",
        "retarded": "supp(term f) subset J^+(supp f)",
    }:
        raise ValueError("v2 advanced/retarded support convention drifted")

    inverse = proofs["inverse_identities"].get("typed_resolvents", {})
    if (
        "X_s(I)->X_s(I)" not in inverse.get("R_sol_advanced_retarded", "")
        or "Y_s(I)->Y_s(I)" not in inverse.get("R_src_advanced_retarded", "")
        or inverse.get("R_sol_advanced_retarded")
        == inverse.get("R_src_advanced_retarded")
    ):
        raise ValueError("v2 source and solution resolvents were conflated")

    adjoint = proofs["adjoint_reversal"]
    if (
        adjoint.get("typed_identity")
        != "(G_A,advanced)^sharp=G_(A^sharp),retarded and (G_A,retarded)^sharp=G_(A^sharp),advanced"
        or adjoint.get("self_adjoint_simplification_used") is not False
        or not adjoint.get("pairing")
    ):
        raise ValueError("v2 typed adjoint reversal drifted")
    return {
        "strict_proof_inventory": True,
        "proof_artifact_hashes": True,
        "time_regular_slab_spaces": True,
        "two_sided_factorial_bounds": True,
        "distinct_source_solution_resolvents": True,
        "named_advanced_retarded_support": True,
        "typed_metric_antifield_adjoint_reversal": True,
    }


def _validate_manifest_and_receipt(source: dict[str, Any]) -> dict[str, bool]:
    manifest = _git_json(CLASSICAL_MANIFEST)
    if manifest.get("target_result_id") != source["result_id"]:
        raise ValueError("v2 source manifest target drifted")
    records = manifest.get("files", [])
    required_roles = {
        "certificate", "schema", "producer", "verifier", "tests", "report",
        "analytic_proof:finite_slab_estimate",
        "analytic_proof:causal_support_passage",
        "analytic_proof:globalization_uniqueness",
        "analytic_proof:inverse_identities",
        "analytic_proof:adjoint_reversal",
    }
    if {record.get("role") for record in records} != required_roles:
        raise ValueError("v2 source manifest role coverage drifted")
    for record in records:
        if _sha256_bytes(_git_blob(record["path"])) != record["sha256"]:
            raise ValueError(f"v2 source manifest hash mismatch: {record['role']}")

    receipt = _git_json(CLASSICAL_RECEIPT)
    if (
        receipt.get("target_result_id") != source["result_id"]
        or receipt.get("overall_status") != "PASS"
        or receipt.get("covered_roles") != sorted(required_roles)
        or receipt.get("source_manifest", {}).get("sha256")
        != _sha256_bytes(_git_blob(CLASSICAL_MANIFEST))
        or receipt.get("certificate_sha256")
        != _sha256_bytes(_git_blob(CLASSICAL_CERTIFICATE))
        or any(
            row.get("status") != "PASS"
            or row.get("return_code") != 0
            or not isinstance(row.get("elapsed_seconds"), (int, float))
            for row in receipt.get("commands", [])
        )
    ):
        raise ValueError("v2 verification receipt drifted")
    return {
        "source_manifest_complete": True,
        "source_manifest_hashes": True,
        "timed_verification_receipt": True,
    }


@lru_cache(maxsize=1)
def evaluate_import() -> dict[str, Any]:
    source, _ = _validate_source()
    proof_checks = _validate_proofs(source)
    receipt_checks = _validate_manifest_and_receipt(source)
    historical = json.loads(HISTORICAL_AUDIT.read_text())
    if (
        historical.get("result_id")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS"
        or historical.get("source_audit", {}).get("status")
        != "REJECTED_FAIL_CLOSED"
        or historical.get("claim_flags", {}).get("BERGER_RETAINED_BIWAVE_D_EQUIVARIANT")
        is not True
        or historical.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY"
        )
        is not True
    ):
        raise ValueError("historical Volterra audit boundary drifted")

    closed_defects = {
        "UNDECLARED_DEPENDENCY_TAG": "normalized to LOCAL-ALGEBRAIC and LORENTZIAN-CAUSAL",
        "MISSING_STRICT_SOURCE_SCHEMA": "strict Draft 2020-12 v2 schema validates",
        "CONFLATED_SOURCE_AND_SOLUTION_RESOLVENTS": "R_sol on X_s(I) and R_src on Y_s(I) are separate",
        "MALFORMED_FORMAL_ADJOINT_IDENTITY": "advanced/retarded reversal is typed against A^sharp and the BV pairing",
        "UNREFERENCED_ANALYTIC_BOOLEAN_ASSERTIONS": "five content-addressed analytic proof artifacts are bound",
        "MISSING_SOURCE_PROVENANCE_AND_VERIFICATION_RECEIPT": "source manifest and timed receipt validate",
        "SOURCE_SIDE_FACTORIAL_BOUND_NOT_STATED": "both X_s(I) and Y_s(I) factorial bounds are present",
        "GRADED_ENERGY_PROOF_NOT_BOUND_TO_CERTIFICATE": "time-regular slab spaces and estimates are certificate-bound",
    }
    historical_ids = {
        item["defect_id"] for item in historical["source_audit"]["defects"]
    }
    if set(closed_defects) != historical_ids:
        raise ValueError("v2 repair does not close the historical defect ledger exactly")

    result = {
        "schema": "quantum-weyl-berger-retained-biwave-volterra-v2-import-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT",
        "result_state": "REPAIRED_V2_IMPORTED_D_ADJOINT_COMPATIBLE_26_ROW_V2_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": source["setting_id"],
        "source_import": {
            "status": "IMPORTED",
            "commit": CLASSICAL_COMMIT,
            "result_id": source["result_id"],
            "schema": source["schema"],
            "claim_status": source["claim_status"],
            "proof_checks": proof_checks,
            "provenance_checks": receipt_checks,
        },
        "repair_closure": closed_defects,
        "compatibility_import": {
            "historical_certificate": str(HISTORICAL_AUDIT.relative_to(ROOT)),
            "historical_sha256": _sha256_bytes(HISTORICAL_AUDIT.read_bytes()),
            "D_equivariance": "IMPORTED_FROM_EXACT_HISTORICAL_PBW_REPLAY",
            "formal_adjoint_bundle": "IMPORTED_FROM_EXACT_HISTORICAL_PBW_REPLAY",
            "companion_graph_SDR": "IMPORTED_AND_RECHECKED_BY_V2_SOURCE",
        },
        "claim_flags": {
            "BERGER_RETAINED_BIWAVE_D_EQUIVARIANT": True,
            "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY": True,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED": True,
            "BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED": True,
            "BERGER_RETAINED_BIWAVE_COMPANION_CYCLIC_PAIRING": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2": False,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2": False,
            "BERGER_CAUSAL_D_CARTAN_V2": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
        "provenance": {
            "classical_artifacts": {
                "certificate": _artifact(CLASSICAL_CERTIFICATE),
                "schema": _artifact(CLASSICAL_SCHEMA),
                "producer": _artifact(CLASSICAL_PRODUCER),
                "verifier": _artifact(CLASSICAL_VERIFIER),
                "tests": _artifact(CLASSICAL_TEST),
                "report": _artifact(CLASSICAL_REPORT),
                "manifest": _artifact(CLASSICAL_MANIFEST),
                "receipt": _artifact(CLASSICAL_RECEIPT),
            }
        },
        "claim_boundary": "Independently imports the repaired classical retained-metric Volterra v2 theorem, including strict schema, typed time-regular slab spaces, separate source/solution resolvents, both factorial bounds, named advanced/retarded support, both inverse identities, typed metric-antifield adjoint reversal, proof hashes, source manifest and timed receipt. Exact D and adjoint compatibility are retained from the prior PBW replay. This does not construct the 26- or 54-row v2 BV homotopy, a companion cyclic pairing, causal D-Cartan v2, Hadamard data, a QME or a quantum result.",
    }
    validate_import(result)
    return result


def validate_import(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT"
        or result.get("result_state")
        != "REPAIRED_V2_IMPORTED_D_ADJOINT_COMPATIBLE_26_ROW_V2_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"
    ):
        raise ValueError("v2 import identity drifted")
    source = result.get("source_import", {})
    if (
        source.get("status") != "IMPORTED"
        or source.get("commit") != CLASSICAL_COMMIT
        or not all(source.get("proof_checks", {}).values())
        or not all(source.get("provenance_checks", {}).values())
    ):
        raise ValueError("v2 source import receipt drifted")
    if len(result.get("repair_closure", {})) != 8:
        raise ValueError("historical repair closure is incomplete")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_RETAINED_BIWAVE_D_EQUIVARIANT",
        "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY",
        "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED",
        "BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED",
    }:
        raise ValueError("v2 import lifecycle boundary drifted")
