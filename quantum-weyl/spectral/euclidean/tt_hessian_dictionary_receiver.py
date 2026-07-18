"""Semantic receiver for the round-S4 repository TT Hessian dictionary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA = HERE / "schema/repository-round-s4-tt-hessian-dictionary-input-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_artifact(value: object, *, repository_root: Path, index: int) -> None:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"TT dictionary proof artifact {index} fields drifted")
    path = (repository_root / value["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError("TT dictionary proof artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != value["sha256"]:
        raise ValueError(f"TT dictionary proof artifact {index} hash mismatch")


def validate_tt_hessian_dictionary(
    payload: object,
    *,
    repository_root: Path,
    expected_classical_commit: str,
) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("TT Hessian dictionary is not an object")
    if payload["classical_commit"] != expected_classical_commit:
        raise ValueError("TT Hessian dictionary classical commit drifted")

    kappa = payload["action_normalization"]["kappa"]
    leading = payload["flat_tt_leading_symbol"]["Hessian_leading_coefficient"]
    if kappa != {"numerator": 1, "denominator": 2} or leading != kappa:
        raise ValueError("TT Hessian action/leading-symbol normalization drifted")
    operator = payload["operator_dictionary"]
    if (
        operator["lower_factor"] != "Delta_2_perp(2)"
        or operator["upper_factor"] != "Delta_2_perp(4)"
        or operator["repository_Hessian"]
        != "(1/2) Delta_2_perp(2) Delta_2_perp(4)"
        or operator["identity_verified"] is not True
    ):
        raise ValueError("TT Hessian factor dictionary drifted")
    if payload["constant_curvature_derivation"]["residual_operator"] != "ZERO":
        raise ValueError("TT Hessian constant-curvature residual is nonzero")
    if payload["zero_modes"]["Hessian_kernel_dimension"] != 0:
        raise ValueError("TT Hessian zero-mode statement drifted")
    for index, artifact in enumerate(payload["proof_artifacts"]):
        _validate_artifact(artifact, repository_root=repository_root, index=index)
    return {
        "result_id": payload["result_id"],
        "classical_commit": payload["classical_commit"],
        "bundle_rank": operator["bundle_rank"],
        "kappa": kappa,
        "lower_factor": operator["lower_factor"],
        "upper_factor": operator["upper_factor"],
        "Hessian_kernel_dimension": payload["zero_modes"]["Hessian_kernel_dimension"],
        "proof_artifact_count": len(payload["proof_artifacts"]),
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_payload(*, repository_root: Path = ROOT, classical_commit: str = "0" * 40) -> dict[str, Any]:
    """Non-scientific fixture exercising the complete receiver surface."""

    paths = (
        ("PYTHON_PRODUCER", "symbolic/verify_conformal_detour_action.py"),
        ("JSON_CERTIFICATE", "quantum-weyl/spectral/euclidean/certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json"),
    )
    artifacts = [
        {"format": format_, "path": path, "sha256": _sha256(repository_root / path)}
        for format_, path in paths
    ]
    proof_payload = {"fixture": True, "classical_commit": classical_commit, "artifacts": artifacts}
    return {
        "schema": "quantum-weyl-repository-round-s4-tt-hessian-dictionary-input-v1",
        "result_id": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "result_state": "REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": classical_commit,
        "background": {"geometry": "round unit S4", "dimension": 4, "scalar_curvature": 12, "Ricci": "3 g", "Weyl": "0"},
        "action_normalization": {"repository_action": "S_red=int sqrt(g)(Ricci^2-R^2/3)=1/2 int sqrt(g)(C2-E4)", "mixed_hessian": "delta_h delta_k S_red=<C1 h,C1 k>", "kappa": {"numerator": 1, "denominator": 2}},
        "flat_tt_leading_symbol": {"linearized_Ricci": "Ricci1_TT=(1/2) p^2 h_TT", "linearized_scalar": "R1_TT=0", "quadratic_action": "S_red^(2)=(1/4)<h,p^4 h>", "Hessian_leading_coefficient": {"numerator": 1, "denominator": 2}, "standard_product_leading_coefficient": 1, "kappa_match": True},
        "operator_dictionary": {"bundle": "real transverse traceless symmetric rank-two tensors", "bundle_rank": 5, "Delta2_definition": "Delta_2_perp(M_squared)=-nabla^2+M_squared", "lower_factor": "Delta_2_perp(2)", "upper_factor": "Delta_2_perp(4)", "repository_Hessian": "(1/2) Delta_2_perp(2) Delta_2_perp(4)", "factor_commutator_zero": True, "identity_verified": True},
        "constant_curvature_derivation": {"method": "synthetic receiver fixture, not a scientific derivation", "all_connection_variations_included": True, "integration_by_parts_policy": "closed S4 no boundary term", "Euler_term_policy": "E4 variation integrated to zero at fixed topology", "residual_operator": "ZERO", "verified": True},
        "formal_properties": {"formally_self_adjoint": True, "elliptic_on_TT": True, "real_operator": True, "parity_even": True},
        "zero_modes": {"lower_factor_kernel_dimension": 0, "upper_factor_kernel_dimension": 0, "Hessian_kernel_dimension": 0, "verified": True},
        "proof_artifacts": artifacts,
        "claim_flags": {"REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_SUPPLIED": True, "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED": True, "REPOSITORY_ELLIPTIC_TT_BLOCK_CERTIFIED": True, "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False, "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False, "REGULATED_SLAVNOV_BREAKING_COMPUTED": False, "QME_DISPOSITION": False},
        "proof_sha256": hashlib.sha256(json.dumps(proof_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }


def synthetic_receipt() -> dict[str, Any]:
    payload = synthetic_payload()
    return validate_tt_hessian_dictionary(payload, repository_root=ROOT, expected_classical_commit="0" * 40)
