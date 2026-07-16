"""Pinned import of the repaired Berger 26/54-row and D-Cartan v2 chain."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "743183594a7a33dbb869154dafd7eb2c3482bac0"
ENDPOINT = "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
FULL = "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
CARTAN = "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json"
ENDPOINT_PROOF = "d_quotient_classical/generated/berger_26_row_causal_green_homotopy_v2/causal_proof.json"
VOLTERRA = "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
REDUCTION = "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
D_ACTION = "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
TRANSFER = "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json"
Q2 = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
GAUGE_FIXED = "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
V2_QUANTUM_IMPORT = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"


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
        raise ValueError(f"missing pinned causal-chain v2 artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned causal-chain v2 JSON is not an object: {relative}")
    return value


def _sha256(relative: str) -> str:
    return hashlib.sha256(_git_blob(relative)).hexdigest()


def _expected_dependency(relative: str) -> dict[str, str]:
    payload = _git_json(relative)
    return {"result_id": payload["result_id"], "sha256": _sha256(relative)}


def _validate_endpoint(endpoint: dict[str, Any]) -> dict[str, bool]:
    if (
        endpoint.get("schema") != "quantum-weyl-berger-26-row-green-endpoint-export-v2"
        or endpoint.get("result_id") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"
        or endpoint.get("result_state") != "GREEN_CERTIFIED_HADAMARD_OPEN"
        or endpoint.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or endpoint.get("classical_commit")
        != "eb56d5aff7d622de423d4994051b0e048c4fb4bf"
        or endpoint.get("dependency_refs")
        != {"retained_metric_volterra_v2": _expected_dependency(VOLTERRA)}
    ):
        raise ValueError("26-row v2 endpoint identity or provenance drifted")
    layout = endpoint.get("row_layout", {})
    if (
        layout.get("total_rows") != 26
        or layout.get("degree_ranks") != [3, 10, 10, 3]
        or len(layout.get("row_ids", [])) != 26
        or len(set(layout.get("row_ids", []))) != 26
    ):
        raise ValueError("26-row v2 layout drifted")
    proof_hash = _sha256(ENDPOINT_PROOF)
    expected_checks = {
        "D_equivariance", "advanced_chain_homotopy_identity", "advanced_support",
        "cyclic_advanced_retarded_adjointness", "retarded_chain_homotopy_identity",
        "retarded_support", "row_completeness", "zero_mode_policy_applied",
    }
    checks = endpoint.get("green_proof_checks", {})
    if set(checks) != expected_checks or any(
        row.get("status") != "VERIFIED"
        or row.get("proof_artifact", {}).get("path") != ENDPOINT_PROOF
        or row.get("proof_artifact", {}).get("sha256") != proof_hash
        for row in checks.values()
    ):
        raise ValueError("26-row v2 proof ledger drifted")
    proof = _git_json(ENDPOINT_PROOF)
    if not all(proof.get("exact_checks", {}).values()):
        raise ValueError("26-row v2 proof exact check dropped")
    if endpoint.get("hadamard") != {"status": "NOT_CONSTRUCTED", "proof_checks": {}}:
        raise ValueError("26-row v2 Hadamard stage was promoted")
    support = endpoint.get("support_category", {})
    if (
        support.get("globally_hyperbolic") is not True
        or "no elliptic projector" not in support.get("zero_mode_policy", "")
    ):
        raise ValueError("26-row v2 support category drifted")
    return {
        "row_completeness": True,
        "advanced_retarded_chain_homotopies": True,
        "cyclic_adjointness": True,
        "D_equivariance": True,
        "causal_support": True,
        "zero_modes_retained": True,
        "Hadamard_open": True,
    }


def _validate_full(full: dict[str, Any], endpoint: dict[str, Any]) -> dict[str, bool]:
    if (
        full.get("result_id") != "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"
        or full.get("claim_status")
        != "CERTIFIED_COMPLETE_GAUGE_FIXED_CAUSAL_GREEN_HOMOTOPY_HADAMARD_OPEN"
        or full.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or full.get("dependency_refs") != {
            "support_local_cyclic_reduction": _expected_dependency(REDUCTION),
            "retained_endpoint_green_homotopy": {
                "result_id": endpoint["result_id"], "sha256": _sha256(ENDPOINT)
            },
            "local_D_action": _expected_dependency(D_ACTION),
        }
        or full.get("next_gate") != "BERGER_CAUSAL_D_CARTAN_V2"
    ):
        raise ValueError("54-row v2 identity or dependency chain drifted")
    dimensions = full.get("dimension_ledger", {})
    if (
        dimensions.get("complete_rows") != 54
        or dimensions.get("algebraically_contracted_rows") != 28
        or dimensions.get("causally_propagating_rows") != 26
        or dimensions.get("degree_ranks") != [5, 22, 22, 5]
    ):
        raise ValueError("54-row v2 dimension ledger drifted")
    if not all(full.get("exact_checks", {}).values()):
        raise ValueError("54-row v2 exact check dropped")
    if full.get("flags") != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2": True,
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2": True,
        "BERGER_54_ROW_CAUSAL_REDUCTION": True,
        "BERGER_CAUSAL_D_CARTAN_V2": False,
        "BERGER_CAUSAL_GREEN_HOMOTOPY_V2": True,
        "BERGER_HADAMARD_DATA": False,
    }:
        raise ValueError("54-row v2 lifecycle boundary drifted")
    construction = full.get("construction", {})
    if any(construction.get(key) is not False for key in (
        "inverse_curl", "inverse_spatial_laplacian", "mode_projector"
    )):
        raise ValueError("nonlocal projector entered 54-row v2 chain")
    return {
        "all_54_rows": True,
        "support_local_SDR_lift": True,
        "advanced_retarded_chain_identity": True,
        "cyclic_adjointness": True,
        "D_equivariance": True,
        "zero_modes_retained": True,
    }


def _validate_cartan(cartan: dict[str, Any], full: dict[str, Any]) -> dict[str, bool]:
    if (
        cartan.get("result_id") != "BERGER_CAUSAL_D_CARTAN_V2"
        or cartan.get("claim_status")
        != "CERTIFIED_CAUSAL_UNARY_AND_CYCLIC_ARITY_TWO_D_CARTAN"
        or cartan.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or cartan.get("dependency_refs") != {
            "complete_causal_contraction": {
                "result_id": full["result_id"], "sha256": _sha256(FULL)
            },
            "conditional_transfer": _expected_dependency(TRANSFER),
            "support_local_q2": _expected_dependency(Q2),
            "local_D_action": _expected_dependency(D_ACTION),
            "odd_Darboux_pairing": _expected_dependency(GAUGE_FIXED),
        }
        or cartan.get("next_gate") != "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD"
    ):
        raise ValueError("causal D-Cartan v2 identity or dependencies drifted")
    if not all(cartan.get("exact_checks", {}).values()):
        raise ValueError("causal D-Cartan v2 exact check dropped")
    audit = cartan.get("arity_two_contraction", {}).get("concrete_Koszul_audit", {})
    if (
        audit.get("total_rows") != 54
        or audit.get("odd_Darboux_dual_slots") != 27
        or audit.get("admissible_degree_zero_row_triples") != 25543
        or audit.get("C3_group_law_defects") != 0
    ):
        raise ValueError("causal D-Cartan v2 Koszul audit drifted")
    scope = cartan.get("support_scope", {})
    if (
        scope.get("advanced_retarded_chain_homotopies_remain_one_sided") is not True
        or scope.get("cyclic_Cartan_primitives_are_two_sided_causal") is not True
        or scope.get("inverse_spatial_laplacian") is not False
        or scope.get("mode_projector") is not False
    ):
        raise ValueError("causal D-Cartan v2 support scope drifted")
    if cartan.get("flags") != {
        "BERGER_ARITY_THREE_D_CARTAN": False,
        "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION": True,
        "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED": True,
        "BERGER_CAUSAL_D_CARTAN_V2": True,
        "BERGER_CAUSAL_GREEN_HOMOTOPY_V2": True,
        "BERGER_CAUSAL_UNARY_D_CARTAN": True,
        "BERGER_HADAMARD_DATA": False,
        "QUANTUM_CLAIM": False,
    }:
        raise ValueError("causal D-Cartan v2 lifecycle boundary drifted")
    return {
        "unary_Cartan": True,
        "arity_two_source_closed": True,
        "arity_two_cyclic_primitive": True,
        "actual_54_row_C3_group_law": True,
        "two_sided_causal_hull_support": True,
        "arity_three_open": True,
        "Hadamard_open": True,
    }


@lru_cache(maxsize=1)
def evaluate_import() -> dict[str, Any]:
    metric_import = json.loads(V2_QUANTUM_IMPORT.read_text())
    if (
        metric_import.get("result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT"
        or metric_import.get("claim_flags", {}).get(
            "BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED"
        ) is not True
        or metric_import.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"
    ):
        raise ValueError("quantum retained-metric v2 import boundary drifted")
    endpoint = _git_json(ENDPOINT)
    full = _git_json(FULL)
    cartan = _git_json(CARTAN)
    checks = {
        "endpoint_26": _validate_endpoint(endpoint),
        "full_54": _validate_full(full, endpoint),
        "causal_D_Cartan": _validate_cartan(cartan, full),
    }
    result = {
        "schema": "quantum-weyl-berger-causal-chain-v2-import-v1",
        "result_id": "BERGER_CAUSAL_CHAIN_V2_IMPORT",
        "result_state": "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": endpoint["setting_id"],
        "coverage": {
            "retained_rows": 26,
            "complete_rows": 54,
            "D_Cartan_arities": [1, 2],
            "checks": checks,
        },
        "claim_flags": {
            "BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED": True,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED": True,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED": True,
            "BERGER_CAUSAL_D_CARTAN_V2_IMPORTED": True,
            "BERGER_ARITY_THREE_D_CARTAN": False,
            "BERGER_HADAMARD_DATA": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_artifacts": {
                "endpoint_26": {"path": ENDPOINT, "sha256": _sha256(ENDPOINT)},
                "full_54": {"path": FULL, "sha256": _sha256(FULL)},
                "causal_D_Cartan": {"path": CARTAN, "sha256": _sha256(CARTAN)},
                "endpoint_proof": {"path": ENDPOINT_PROOF, "sha256": _sha256(ENDPOINT_PROOF)},
            },
            "quantum_metric_import": {
                "path": str(V2_QUANTUM_IMPORT.relative_to(ROOT)),
                "sha256": hashlib.sha256(V2_QUANTUM_IMPORT.read_bytes()).hexdigest(),
            },
        },
        "claim_boundary": "Independently imports the repaired classical causal v2 chain: advanced and retarded homotopies on all 26 retained and all 54 gauge-fixed rows, plus the cyclic two-sided-causal D-Cartan contraction through arity two with the concrete 54-row Koszul audit. It does not construct arity-three D-Cartan, Hadamard data, renormalized Lorentzian products, restore a Lorentzian QME or make a quantum claim.",
    }
    validate_import(result)
    return result


def validate_import(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_CAUSAL_CHAIN_V2_IMPORT"
        or result.get("result_state")
        != "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate") != "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD"
    ):
        raise ValueError("causal chain v2 import identity drifted")
    checks = result.get("coverage", {}).get("checks", {})
    if set(checks) != {"endpoint_26", "full_54", "causal_D_Cartan"} or any(
        not all(group.values()) for group in checks.values()
    ):
        raise ValueError("causal chain v2 import check dropped")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED",
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED",
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED",
        "BERGER_CAUSAL_D_CARTAN_V2_IMPORTED",
    }:
        raise ValueError("causal chain v2 lifecycle boundary drifted")
