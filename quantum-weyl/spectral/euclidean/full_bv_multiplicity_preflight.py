"""Exact multiplicity bridge preflight for the covariant pure-Weyl BV complex."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json"
SCHEMA = HERE / "schema/repository-full-bv-multiplicity-preflight-v1.schema.json"
EXPORT_SCHEMA = HERE / "schema/repository-full-bv-multiplicity-export-v1.schema.json"

DEPENDENCIES = {
    "covariant_minimal_import": ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
    "covariant_minimal_export": ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
    "general_nonminimal_G2": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "standard_factorization": HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "standard_auxiliary_match": HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json",
    "Berger_gauge_fixed_carrier": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
}

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/full_bv_multiplicity_preflight.py",
    "quantum-weyl/spectral/euclidean/verify_full_bv_multiplicity_preflight.py",
    "quantum-weyl/spectral/euclidean/schema/repository-full-bv-multiplicity-preflight-v1.schema.json",
    "quantum-weyl/spectral/euclidean/schema/repository-full-bv-multiplicity-export-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_full_bv_multiplicity_preflight.py",
    "quantum-weyl/reports/repository-full-bv-multiplicity-preflight.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transverse_traceless_rank_4d(spin: int) -> int:
    """Rank of a transverse traceless symmetric spin-s tensor in four dimensions."""

    if spin < 0:
        raise ValueError("spin must be nonnegative")
    unconstrained_traceless = (spin + 1) ** 2
    divergence_image = spin**2 if spin else 0
    return unconstrained_traceless - divergence_image


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def analysis() -> dict[str, Any]:
    values = _load()
    imported = values["covariant_minimal_import"]
    exported = values["covariant_minimal_export"]
    nonminimal = values["general_nonminimal_G2"]
    standard = values["standard_factorization"]
    auxiliary = values["standard_auxiliary_match"]
    berger = values["Berger_gauge_fixed_carrier"]

    classical_commit = exported.get("classical_commit")
    if (
        imported.get("classical_commit") != classical_commit
        or nonminimal.get("classical_commit") != classical_commit
        or imported.get("claim_flags", {}).get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED")
        is not True
        or nonminimal.get("claim_flags", {}).get("FULL_BV_G2_COMPLETE") is not True
    ):
        raise ValueError("covariant BV snapshot drifted")
    generators = exported.get("generators", [])
    by_role = {row.get("role"): row for row in generators}
    required_roles = {
        "metric",
        "diffeomorphism_ghost",
        "weyl_ghost",
        "metric_antifield",
        "diffeomorphism_ghost_antifield",
        "weyl_ghost_antifield",
    }
    if len(generators) != 6 or set(by_role) != required_roles:
        raise ValueError("covariant minimal generator dictionary drifted")
    metric_rank = 4 * 5 // 2
    diffeomorphism_ghost_rank = 4
    weyl_ghost_rank = 1
    if (
        by_role["metric"].get("tensor_type", {}).get("symmetry")
        != "symmetric_covariant_2"
        or by_role["diffeomorphism_ghost"].get("tensor_type", {}).get(
            "contravariant_rank"
        )
        != 1
        or by_role["weyl_ghost"].get("tensor_type", {}).get("symmetry")
        != "scalar"
    ):
        raise ValueError("covariant tensor ranks drifted")

    factor_rows = standard.get("coefficient_calculation", {}).get(
        "constant_curvature_factor_ledger", []
    )
    expected_factor_ids = (
        "physical_depth_0",
        "ghost_depth_0",
        "physical_depth_1",
        "ghost_depth_1",
    )
    if tuple(row.get("factor_id") for row in factor_rows) != expected_factor_ids:
        raise ValueError("standard factor ordering drifted")
    factor_multiplicities = []
    signed_rank = 0
    for row in factor_rows:
        spin = row["spin"]
        rank = transverse_traceless_rank_4d(spin)
        sign = row["determinant_sign"]
        signed_rank += sign * rank
        factor_multiplicities.append(
            {
                "factor_id": row["factor_id"],
                "spin": spin,
                "bundle_rank": rank,
                "determinant_sign": sign,
                "statistics": "BOSONIC" if row["factor_id"].startswith("physical") else "FERMIONIC_GHOST",
                "M_squared": row["M_squared"],
            }
        )
    if [row["bundle_rank"] for row in factor_multiplicities] != [5, 1, 5, 3]:
        raise AssertionError("standard factor multiplicities drifted")
    if signed_rank != 6 or standard["coefficient_calculation"]["effective_degrees_of_freedom_nu"] != 6:
        raise AssertionError("signed standard multiplicity does not reproduce nu=6")
    if (
        auxiliary.get("claim_flags", {}).get(
            "STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY"
        )
        is not True
    ):
        raise ValueError("standard physical TT auxiliary identity is unavailable")

    dictionary = nonminimal.get("field_dictionary", {})
    if (
        len(dictionary.get("gauge_directions", [])) != 5
        or dictionary.get("atom_count") != 20
    ):
        raise ValueError("general nonminimal direction inventory drifted")
    if (
        berger.get("row_layout", {}).get("total_rows") != 54
        or berger.get("row_layout", {}).get("minimal_rows") != 34
        or berger.get("row_layout", {}).get("nonminimal_rows") != 20
        or berger.get("operator_semantics", {}).get("not_quantum_loop_operator")
        is not True
    ):
        raise ValueError("Berger negative-authority carrier drifted")

    transverse_vector_rank = transverse_traceless_rank_4d(1)
    scalar_rank = transverse_traceless_rank_4d(0)
    if metric_rank != 5 + 4 + 1 or diffeomorphism_ghost_rank != transverse_vector_rank + scalar_rank:
        raise AssertionError("covariant York/Hodge rank balance drifted")
    scalar_ghost_candidates = scalar_rank + weyl_ghost_rank
    standard_scalar_ghost_rank = next(
        row["bundle_rank"]
        for row in factor_multiplicities
        if row["factor_id"] == "ghost_depth_0"
    )
    unresolved_scalar_rank = scalar_ghost_candidates - standard_scalar_ghost_rank
    if unresolved_scalar_rank != 1:
        raise AssertionError("minimal scalar ghost cancellation rank drifted")

    return {
        "classical_commit": classical_commit,
        "dependency_hashes": {name: _sha256(path) for name, path in DEPENDENCIES.items()},
        "factor_multiplicities": factor_multiplicities,
        "signed_effective_rank": signed_rank,
        "metric_rank": metric_rank,
        "diffeomorphism_ghost_rank": diffeomorphism_ghost_rank,
        "weyl_ghost_rank": weyl_ghost_rank,
        "transverse_vector_rank": transverse_vector_rank,
        "scalar_rank": scalar_rank,
        "scalar_ghost_candidates": scalar_ghost_candidates,
        "standard_scalar_ghost_rank": standard_scalar_ghost_rank,
        "unresolved_scalar_rank": unresolved_scalar_rank,
    }


def build() -> dict[str, Any]:
    result = analysis()
    proof_payload = {
        "dependencies": result["dependency_hashes"],
        "factors": result["factor_multiplicities"],
        "scalar_gap": result["unresolved_scalar_rank"],
    }
    certificate = {
        "schema": "quantum-weyl-repository-full-bv-multiplicity-preflight-v1",
        "result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT",
        "result_state": "STANDARD_FACTOR_AND_COVARIANT_FIELD_RANKS_MATCHED_SCALAR_GHOST_AND_ANALYTIC_ROW_MAP_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": result["classical_commit"],
        "dependency_hashes": result["dependency_hashes"],
        "accepted_export": {
            "result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
            "schema": "quantum-weyl-repository-full-bv-multiplicity-export-v1",
            "schema_path": "quantum-weyl/spectral/euclidean/schema/repository-full-bv-multiplicity-export-v1.schema.json",
            "status": "RECEIVER_SCHEMA_READY_INPUT_NOT_RECEIVED",
        },
        "standard_factor_multiplicities": {
            "dimension": 4,
            "rank_formula": "rank(TT_s)=((s+1)^2-s^2)=2s+1",
            "rows": result["factor_multiplicities"],
            "signed_effective_rank": result["signed_effective_rank"],
            "expected_nu": 6,
            "nu_match": True,
        },
        "covariant_BV_component_inventory": {
            "integration_candidates": [
                {"generator": "g", "role": "metric", "statistics": "BOSONIC", "component_rank": result["metric_rank"]},
                {"generator": "xi", "role": "diffeomorphism_ghost", "statistics": "FERMIONIC", "component_rank": result["diffeomorphism_ghost_rank"]},
                {"generator": "omega", "role": "weyl_ghost", "statistics": "FERMIONIC", "component_rank": result["weyl_ghost_rank"]},
            ],
            "antifield_roles": [
                "metric_antifield",
                "diffeomorphism_ghost_antifield",
                "weyl_ghost_antifield",
            ],
            "antifield_integration_status": "MUST_BE_DERIVED_FROM_GAUGE_FIXED_LAGRANGIAN_SLICE_NOT_INTEGRATED_INDEPENDENTLY",
            "gauge_direction_count": 5,
            "general_nonminimal_atom_count": 20,
            "nonminimal_analytic_kinetic_rows": "NOT_EXPORTED",
        },
        "exact_rank_decomposition": {
            "metric": "10=5_TT+4_Diff_orbit+1_Weyl_trace",
            "diffeomorphism_ghost": "4=3_transverse+1_longitudinal_scalar",
            "weyl_ghost": "1=1_scalar",
            "scalar_ghost_candidate_rank": result["scalar_ghost_candidates"],
            "standard_scalar_ghost_factor_rank": result["standard_scalar_ghost_rank"],
            "unresolved_scalar_cancellation_rank": result["unresolved_scalar_rank"],
        },
        "factor_origin_bridge": [
            {
                "factor_id": "physical_depth_0",
                "candidate_origin": "g_TT",
                "rank_status": "MATCHED_5",
                "operator_status": "STANDARD_ONLY_REPOSITORY_HESSIAN_MAP_OPEN",
            },
            {
                "factor_id": "physical_depth_1",
                "candidate_origin": "g_TT",
                "rank_status": "MATCHED_5",
                "operator_status": "STANDARD_AUXILIARY_SCHUR_IDENTITY_VERIFIED_REPOSITORY_HESSIAN_MAP_OPEN",
            },
            {
                "factor_id": "ghost_depth_1",
                "candidate_origin": "xi_transverse",
                "rank_status": "MATCHED_3",
                "operator_status": "REPOSITORY_GHOST_OPERATOR_MAP_OPEN",
            },
            {
                "factor_id": "ghost_depth_0",
                "candidate_origin": "quotient_of_xi_longitudinal_and_omega_scalar_sector",
                "rank_status": "TARGET_1_FROM_CANDIDATE_2_UNRESOLVED_RANK_ONE_CANCELLATION",
                "operator_status": "SCALAR_GHOST_JACOBIAN_AND_NONMINIMAL_CANCELLATION_OPEN",
            },
        ],
        "forbidden_shortcut_audit": {
            "Berger_total_component_rows": 54,
            "Berger_minimal_component_rows": 34,
            "Berger_nonminimal_component_rows": 20,
            "producer_semantics": "classical_unary_q1_not_quantum_loop_operator",
            "component_rows_equal_determinant_multiplicities": False,
            "reason": "the carrier includes antifields and contractible BV rows and supplies no Euclidean integration slice, Hessian, Berezinian, or determinant exponent map",
        },
        "minimal_missing_carrier_theorem": {
            "status": "EXACT_RANK_ONE_SCALAR_GHOST_AND_FULL_ANALYTIC_ROW_MAP_GAP",
            "missing_scalar_rank": 1,
            "required_rows": [
                "Euclidean gauge-fixed Lagrangian integration slice",
                "metric York/Hodge decomposition Jacobian",
                "xi-longitudinal/Weyl scalar ghost operator matrix",
                "antighost/multiplier and nonminimal Berezinian cancellation",
                "factor-by-factor map to the four standard determinant rows",
            ],
            "no_component_row_counting_shortcut": True,
        },
        "claim_flags": {
            "STANDARD_FACTOR_MULTIPLICITIES_COMPLETE": True,
            "COVARIANT_MINIMAL_COMPONENT_RANKS_COMPLETE": True,
            "SCALAR_GHOST_GAP_LOCALIZED_TO_RANK_ONE": True,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_WITH_SCALAR_GHOST_AND_NONMINIMAL_CANCELLATION",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL preflight computes the four standard determinant bundle ranks 5,1,5,3, their signed effective rank six, the covariant metric/diffeomorphism-ghost/Weyl-ghost component ranks 10,4,1, and the generic rank decompositions 10=5+4+1 and 4=3+1. It localizes the unmatched multiplicity problem to one scalar ghost rank plus the full analytic row/operator/Berezinian map. The 54-row Berger classical carrier is explicitly rejected as loop multiplicity authority because it contains antifields and contractible rows and is marked not a quantum loop operator. No Euclidean Lagrangian integration slice, full Hessian, scalar ghost cancellation, nonminimal determinant, zero-mode policy, measure, contour, repository coefficient, regulated Slavnov breaking, QME disposition, Cartan class, residual transfer, or Lorentzian theorem is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(certificate)
    return certificate


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("STANDARD_FACTOR_MULTIPLICITIES_COMPLETE") is not True
        or flags.get("COVARIANT_MINIMAL_COMPONENT_RANKS_COMPLETE") is not True
        or flags.get("SCALAR_GHOST_GAP_LOCALIZED_TO_RANK_ONE") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
                "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED",
                "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
                "QME_DISPOSITION",
            )
        )
    ):
        raise ValueError("full-BV multiplicity preflight crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale full-BV multiplicity preflight: {OUTPUT}")
    print("FULL BV MULTIPLICITY PREFLIGHT: STANDARD RANKS PASS; SCALAR RANK-ONE/ANALYTIC ROW MAP OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
