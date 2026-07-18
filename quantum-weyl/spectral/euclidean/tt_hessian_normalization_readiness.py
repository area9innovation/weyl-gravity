"""Fail-closed audit of the repository physical TT Hessian normalization.

The repository already contains three nearby statements: an action-normalized
``C1^sharp C1`` Hessian on conformally flat backgrounds, a cylinder TT Bach
factorization, and the standard Euclidean spin-two determinant factors.  This
module checks those statements but deliberately refuses to identify them
without the missing round-S4/constant-curvature TT operator dictionary.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json"
SCHEMA = HERE / "schema/repository-tt-hessian-normalization-readiness-v1.schema.json"
STANDARD = HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json"
CYLINDER = ROOT / "covariant_completion/certificates/tt_local_factorization.json"
NARIAI = ROOT / "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/tt_hessian_normalization_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_tt_hessian_normalization_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-tt-hessian-normalization-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_tt_hessian_normalization_readiness.py",
    "quantum-weyl/reports/repository-tt-hessian-normalization-readiness.md",
    "symbolic/verify_conformal_detour_action.py",
    "notes/conformal-local-detour.md",
    "covariant_completion/certificates/tt_local_factorization.json",
    "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def curvature_identity(*, scalar_coefficient: tuple[int, int] = (1, 3)) -> dict[str, Any]:
    """Check ``Ric^2-R^2/3=(C^2-E4)/2`` coefficientwise."""

    numerator, denominator = scalar_coefficient
    # Coordinates are (Riemann^2, Ricci^2, R^2).
    reduced = (Fraction(0), Fraction(1), -Fraction(numerator, denominator))
    weyl = (Fraction(1), Fraction(-2), Fraction(1, 3))
    euler = (Fraction(1), Fraction(-4), Fraction(1))
    target = tuple((left - right) / 2 for left, right in zip(weyl, euler))
    residual = tuple(left - right for left, right in zip(reduced, target))
    return {
        "declared_scalar_coefficient": f"{numerator}/{denominator}",
        "reduced_coordinates": [str(value) for value in reduced],
        "half_C2_minus_E4_coordinates": [str(value) for value in target],
        "residual_coordinates": [str(value) for value in residual],
        "verified": all(value == 0 for value in residual),
    }


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    standard = json.loads(STANDARD.read_text())
    cylinder = json.loads(CYLINDER.read_text())
    nariai = json.loads(NARIAI.read_text())
    if standard.get("result_id") != "STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH":
        raise ValueError("standard TT factor dependency drifted")
    if cylinder.get("schema") != "pure-weyl-tt-local-factorization-v1":
        raise ValueError("cylinder TT factor dependency drifted")
    if nariai.get("result_id") != "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1":
        raise ValueError("Nariai action-derived endpoint dependency drifted")
    return standard, cylinder, nariai


def build() -> dict[str, Any]:
    standard, cylinder, nariai = _load_inputs()
    identity = curvature_identity()
    mutant = curvature_identity(scalar_coefficient=(1, 4))
    if not identity["verified"] or mutant["verified"]:
        raise AssertionError("action normalization mutation control failed")

    evidence = [
        {
            "artifact": "repository reduced Weyl action",
            "setting": "four-dimensional conformally flat background",
            "establishes": "S_red=(C2-E4)/2 and Hessian B_lin=C1^sharp C1 with unit coefficient",
            "eligibility": "ACCEPTED_ACTION_NORMALIZATION_INPUT",
        },
        {
            "artifact": "pure-weyl-tt-local-factorization-v1",
            "setting": "unit Lorentzian cylinder and its periodic Euclidean continuation",
            "establishes": "action-derived reduced TT Bach factorization and r+2,r+4 frequencies",
            "eligibility": "ACCEPTED_CYLINDER_OPERATOR_INPUT",
        },
        {
            "artifact": "STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH",
            "setting": "standard constant-curvature Euclidean determinant convention",
            "establishes": "target A(A+2)=Delta_2_perp(2)Delta_2_perp(4) and auxiliary Schur identity",
            "eligibility": "ACCEPTED_TARGET_NOT_REPOSITORY_IDENTIFICATION",
        },
        {
            "artifact": "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1",
            "setting": "unit Nariai with nonzero parallel Weyl curvature",
            "establishes": "complete action-derived Nariai Bach endpoint and normalization",
            "eligibility": "REJECTED_AS_ROUND_S4_OPERATOR_DICTIONARY_BACKGROUND_MISMATCH",
        },
    ]
    missing = {
        "result": "MINIMAL_MISSING_CARRIER_THEOREM",
        "missing_artifact": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "required_domain": "smooth real TT symmetric rank-two tensors on the round unit S4, with zero modes declared separately",
        "required_identity": "H_TT^repository=kappa Delta_2_perp(2)Delta_2_perp(4)",
        "required_exact_fields": [
            "repository action and Euclidean-continuation convention",
            "TT L2 pairing and formal-adjoint convention",
            "definition of Delta_2_perp(M_squared)",
            "exact scalar kappa including sign",
            "integration-by-parts and Euler-term policy",
            "zero-mode domain/exclusion policy",
        ],
        "why_existing_inputs_do_not_close_it": "the cylinder factorization and Nariai endpoint live on different backgrounds, while the standard S4 pair is presently only a target determinant convention",
    }
    proof_payload = {
        "identity": identity,
        "mutant": mutant,
        "standard": _sha256(STANDARD),
        "cylinder": _sha256(CYLINDER),
        "nariai": _sha256(NARIAI),
        "missing": missing,
    }
    value = {
        "schema": "quantum-weyl-repository-tt-hessian-normalization-readiness-v1",
        "result_id": "REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS",
        "result_state": "ACTION_NORMALIZATION_AND_NEARBY_FACTORIZATIONS_VERIFIED_ROUND_S4_TT_DICTIONARY_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": _git_head(),
        "dependency_hashes": {
            "standard_TT_auxiliary_match": _sha256(STANDARD),
            "cylinder_TT_factorization": _sha256(CYLINDER),
            "nariai_action_derived_Bach_endpoint": _sha256(NARIAI),
        },
        "repository_action_normalization": {
            "action": "S_red=int sqrt(g)(Ricci^2-R^2/3)=1/2 int sqrt(g)(C2-E4)",
            "conformally_flat_mixed_hessian": "delta_h delta_k S_red=<C1 h,C1 k>",
            "operator": "B_lin=C1^sharp C1",
            "unit_coefficient_verified": True,
            "curvature_identity": identity,
        },
        "evidence_eligibility_ledger": evidence,
        "target_operator": {
            "bundle": "real transverse traceless symmetric rank-two tensors",
            "standard_identity": "Delta_2_perp(2)Delta_2_perp(4)=A(A+2)",
            "repository_identity_status": "NOT_COMPUTED_ON_ROUND_S4",
        },
        "negative_control": {
            "mutation": "replace the repository R^2 coefficient 1/3 by 1/4",
            "mutated_identity": mutant,
            "rejected": True,
        },
        "minimal_missing_carrier_theorem": missing,
        "claim_flags": {
            "REPOSITORY_ACTION_NORMALIZATION_VERIFIED": True,
            "CONFORMALLY_FLAT_C1_ADJOINT_C1_HESSIAN_VERIFIED": True,
            "CYLINDER_TT_BACH_FACTORIZATION_IMPORTED": True,
            "NARIAI_ENDPOINT_ELIGIBILITY_AUDITED": True,
            "ROUND_S4_REPOSITORY_TT_HESSIAN_DICTIONARY_SUPPLIED": False,
            "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL readiness audit verifies the repository curvature identity, the unit C1-adjoint-C1 Hessian coefficient on conformally flat backgrounds, the existing cylinder TT Bach factorization, the standard Euclidean A(A+2) target, and the action-derived Nariai endpoint. It proves that these are nearby but nonidentical statements. The Nariai endpoint is not eligible as a round-S4 operator dictionary because its background has nonzero parallel Weyl curvature, and the cylinder factorization does not by itself fix the repository round-S4 transverse Laplacian convention. Therefore the exact scalar and sign in H_TT^repository=kappa Delta_2_perp(2)Delta_2_perp(4) remain uncomputed. No repository determinant, anomaly coefficient, Slavnov breaking, QME disposition, D-Cartan class, residual transfer, or Lorentzian quantum theorem is claimed."
        ),
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(
        flags.get(name) is True
        for name in (
            "REPOSITORY_ACTION_NORMALIZATION_VERIFIED",
            "CONFORMALLY_FLAT_C1_ADJOINT_C1_HESSIAN_VERIFIED",
            "CYLINDER_TT_BACH_FACTORIZATION_IMPORTED",
            "NARIAI_ENDPOINT_ELIGIBILITY_AUDITED",
        )
    ) or any(
        flags.get(name) is not False
        for name in (
            "ROUND_S4_REPOSITORY_TT_HESSIAN_DICTIONARY_SUPPLIED",
            "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED",
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
            "QME_DISPOSITION",
        )
    ):
        raise ValueError("TT Hessian readiness claim boundary crossed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale TT Hessian readiness certificate: {OUTPUT}")
    print("repository TT Hessian normalization readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
