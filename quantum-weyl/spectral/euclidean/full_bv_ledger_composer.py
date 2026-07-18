"""Compose the round-S4 repository full-BV determinant multiplicity ledger.

The only free scientific input is the content-addressed repository TT Hessian
dictionary.  All ghost, York/Hodge, nonminimal, zero-mode, and standard-factor
rows are imported from exact certificates already present in this repository.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

try:
    from .multiplicity_export_receiver import (
        validate_repository_multiplicity_export,
    )
    from .tt_hessian_dictionary_receiver import validate_tt_hessian_dictionary
except ImportError:
    from multiplicity_export_receiver import validate_repository_multiplicity_export
    from tt_hessian_dictionary_receiver import validate_tt_hessian_dictionary


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

DEPENDENCIES = {
    "scalar_ghost": HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json",
    "york_hodge_nonminimal": HERE
    / "certificates/YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCH.json",
    "zero_modes": HERE
    / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json",
    "standard_slice": HERE
    / "certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
}

EXPECTED_ROWS = {
    "h_TT": {
        "role": "field",
        "statistics": "BOSONIC",
        "component_rank": 5,
        "operator_id": "repository_H_TT=(1/2)Delta_2_perp(2)Delta_2_perp(4)",
        "determinant_exponent": {"numerator": -1, "denominator": 2},
        "zero_mode_policy_id": "round_s4_unprimed_kernel_dimension_0",
    },
    "xi_T": {
        "role": "ghost",
        "statistics": "FERMIONIC",
        "component_rank": 3,
        "operator_id": "Delta_1_perp(-3)",
        "determinant_exponent": {"numerator": 1, "denominator": 2},
        "zero_mode_policy_id": "round_s4_prime_delete_10_killing_vectors",
    },
    "xi_L": {
        "role": "ghost",
        "statistics": "FERMIONIC",
        "component_rank": 1,
        "operator_id": "coupled_Diff_Weyl_scalar_FP_input",
        "determinant_exponent": {"numerator": 0, "denominator": 1},
        "zero_mode_policy_id": "round_s4_coupled_scalar_prime_delete_5_conformal_modes",
    },
    "omega": {
        "role": "ghost",
        "statistics": "FERMIONIC",
        "component_rank": 1,
        "operator_id": "coupled_Diff_Weyl_scalar_FP_input",
        "determinant_exponent": {"numerator": 0, "denominator": 1},
        "zero_mode_policy_id": "round_s4_coupled_scalar_prime_delete_5_conformal_modes",
    },
}

EXPECTED_FACTORS = {
    "repository_physical_upper": {
        "bundle": "TT2",
        "statistics": "BOSONIC",
        "component_rank": 5,
        "operator": "Delta_2_perp(4)",
        "determinant_exponent": {"numerator": -1, "denominator": 2},
        "source_generator_ids": ["h_TT"],
    },
    "repository_scalar_ghost": {
        "bundle": "scalar",
        "statistics": "FERMIONIC",
        "component_rank": 1,
        "operator": "Delta_0(-4)",
        "determinant_exponent": {"numerator": 1, "denominator": 2},
        "source_generator_ids": ["xi_L", "omega"],
    },
    "repository_physical_lower": {
        "bundle": "TT2",
        "statistics": "BOSONIC",
        "component_rank": 5,
        "operator": "Delta_2_perp(2)",
        "determinant_exponent": {"numerator": -1, "denominator": 2},
        "source_generator_ids": ["h_TT"],
    },
    "repository_vector_ghost": {
        "bundle": "T1",
        "statistics": "FERMIONIC",
        "component_rank": 3,
        "operator": "Delta_1_perp(-3)",
        "determinant_exponent": {"numerator": 1, "denominator": 2},
        "source_generator_ids": ["xi_T"],
    },
}

STANDARD_MAP = (
    ("physical_depth_0", 5, 1, "repository_physical_upper"),
    ("ghost_depth_0", 1, -1, "repository_scalar_ghost"),
    ("physical_depth_1", 5, 1, "repository_physical_lower"),
    ("ghost_depth_1", 3, -1, "repository_vector_ghost"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, *, format_: str = "JSON_PROOF") -> dict[str, str]:
    return {
        "format": format_,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _load_dependencies() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    scalar = values["scalar_ghost"]
    york = values["york_hodge_nonminimal"]
    zero = values["zero_modes"]
    standard = values["standard_slice"]
    if not (
        scalar.get("claim_flags", {}).get("SCALAR_GHOST_DIFFERENTIAL_RANK_TWO_TO_ONE")
        is True
        and scalar.get("claim_flags", {}).get("STANDARD_SCALAR_GHOST_OPERATOR_MATCHED")
        is True
        and scalar.get("target_match", {}).get("repository_scalar_operator")
        == "Delta_0-R/3"
    ):
        raise ValueError("scalar Diff-Weyl reduction dependency drifted")
    if not all(
        york.get("claim_flags", {}).get(name) is True
        for name in (
            "YORK_GRAM_OPERATORS_DERIVED",
            "HODGE_SUPERJACOBIAN_DELTA0_CANCELLATION",
            "NONZERO_MODE_BRST_QUARTET_SUPERDETERMINANT_ONE",
            "STANDARD_GHOST_OPERATOR_RANK_AND_EXPONENTS_MATCHED",
        )
    ):
        raise ValueError("York/Hodge/nonminimal dependency drifted")
    if not (
        zero.get("claim_flags", {}).get("STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE")
        is True
        and zero.get("claim_flags", {}).get("FIFTEEN_CONFORMAL_REDUCIBILITY_MODES_MATCHED")
        is True
        and zero.get("claim_flags", {}).get("REPOSITORY_SCALAR_FP_KERNEL_MATCHED")
        is True
    ):
        raise ValueError("round-S4 zero-mode dependency drifted")
    rows = standard.get("factor_exponent_ledger", [])
    observed = [
        (
            row.get("factor_id"),
            row.get("operator"),
            row.get("bundle_rank"),
            row.get("Z_determinant_exponent"),
            row.get("zero_mode_dimension"),
        )
        for row in rows
    ]
    expected = [
        ("physical_depth_0", "Delta_2_perp(4)", 5, {"numerator": -1, "denominator": 2}, 0),
        ("ghost_depth_0", "Delta_0(-4)", 1, {"numerator": 1, "denominator": 2}, 5),
        ("physical_depth_1", "Delta_2_perp(2)", 5, {"numerator": -1, "denominator": 2}, 0),
        ("ghost_depth_1", "Delta_1_perp(-3)", 3, {"numerator": 1, "denominator": 2}, 10),
    ]
    if observed != expected:
        raise ValueError("standard local-b4 factor ledger drifted")


def _validate_tt_artifact(
    payload: dict[str, Any], artifact: object, *, repository_root: Path
) -> dict[str, str]:
    if not isinstance(artifact, dict) or set(artifact) != {"format", "path", "sha256"}:
        raise ValueError("TT dictionary source artifact fields drifted")
    if artifact["format"] != "JSON_DATA":
        raise ValueError("TT dictionary source artifact must be JSON_DATA")
    path = (repository_root / artifact["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError("TT dictionary source artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != artifact["sha256"]:
        raise ValueError("TT dictionary source artifact hash mismatch")
    if json.loads(path.read_text()) != payload:
        raise ValueError("TT dictionary source artifact content mismatch")
    return artifact


def compose_repository_multiplicity_export(
    tt_payload: dict[str, Any],
    *,
    tt_dictionary_artifact: dict[str, str],
    repository_root: Path = ROOT,
    expected_classical_commit: str,
) -> dict[str, Any]:
    """Compose and independently replay the exact round-S4 multiplicity map."""

    validate_tt_hessian_dictionary(
        tt_payload,
        repository_root=repository_root,
        expected_classical_commit=expected_classical_commit,
    )
    _validate_tt_artifact(
        tt_payload, tt_dictionary_artifact, repository_root=repository_root
    )
    values = _load_dependencies()
    _validate_dependencies(values)
    proofs = {name: _artifact(path) for name, path in DEPENDENCIES.items()}

    rows = [
        {"generator_id": generator_id, **deepcopy(specification)}
        for generator_id, specification in EXPECTED_ROWS.items()
    ]
    factor_proofs = {
        "repository_physical_upper": tt_dictionary_artifact,
        "repository_scalar_ghost": proofs["scalar_ghost"],
        "repository_physical_lower": tt_dictionary_artifact,
        "repository_vector_ghost": proofs["york_hodge_nonminimal"],
    }
    factors = [
        {
            "factor_id": factor_id,
            **deepcopy(specification),
            "derivation_artifact": factor_proofs[factor_id],
        }
        for factor_id, specification in EXPECTED_FACTORS.items()
    ]
    factor_by_id = {row["factor_id"]: row for row in factors}
    maps = [
        {
            "target_factor_id": target,
            "target_bundle_rank": rank,
            "target_determinant_sign": sign,
            "repository_factor_ids": [factor_id],
            "status": "VERIFIED",
            "proof_artifact": factor_by_id[factor_id]["derivation_artifact"],
        }
        for target, rank, sign, factor_id in STANDARD_MAP
    ]
    payload = {
        "schema": "quantum-weyl-repository-full-bv-multiplicity-export-v1",
        "result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
        "result_state": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": expected_classical_commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "integration_slice": {
            "status": "VERIFIED",
            "gauge": "round_S4_fourth_order_TT_after_exact_York_Hodge_and_BRST_quartet_reduction",
            "rows": rows,
            "antifields_integrated_independently": False,
            "all_rows_accounted": True,
            "proof_artifact": proofs["york_hodge_nonminimal"],
        },
        "repository_factors": factors,
        "standard_factor_map": maps,
        "cancellations": {
            "contractible_pairs_status": "VERIFIED",
            "scalar_ghost_reduction_status": "VERIFIED",
            "scalar_ghost_input_rank": 2,
            "scalar_ghost_output_rank": 1,
            "scalar_ghost_input_generator_ids": ["xi_L", "omega"],
            "scalar_ghost_output_repository_factor_id": "repository_scalar_ghost",
            "nonminimal_Berezinian_status": "VERIFIED",
            "cancelled_repository_factor_ids": [],
            "cancelled_integration_row_ids": [],
            "factor_coverage_status": "VERIFIED",
            "integration_row_coverage_status": "VERIFIED",
            "determinant_exponent_balance_status": "VERIFIED",
            "proof_artifact": proofs["york_hodge_nonminimal"],
        },
        "proof_artifacts": [tt_dictionary_artifact, *proofs.values()],
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL ledger accounts for the complete reduced "
            "round-S4 gauge-fixed BV determinant multiplicities after the exact "
            "York/Hodge, scalar Diff-Weyl, and nonminimal quartet cancellations. "
            "It fixes local heat-kernel factor ranks, exponents, and priming only. "
            "It does not normalize the finite conformal-group volume, choose the "
            "global determinant phase, compute a regulated Slavnov breaking, "
            "decide the QME, or establish Lorentzian quantum theory."
        ),
    }
    validate_composed_repository_multiplicity_export(
        payload,
        tt_payload=tt_payload,
        tt_dictionary_artifact=tt_dictionary_artifact,
        repository_root=repository_root,
        expected_classical_commit=expected_classical_commit,
    )
    return payload


def validate_composed_repository_multiplicity_export(
    payload: dict[str, Any],
    *,
    tt_payload: dict[str, Any],
    tt_dictionary_artifact: dict[str, str],
    repository_root: Path = ROOT,
    expected_classical_commit: str,
) -> dict[str, Any]:
    """Replay generic coverage plus the exact composer-specific dictionary."""

    receipt = validate_repository_multiplicity_export(
        payload,
        repository_root=repository_root,
        expected_classical_commit=expected_classical_commit,
        expected_analytic_route="EUCLIDEAN_ELLIPTIC",
    )
    validate_tt_hessian_dictionary(
        tt_payload,
        repository_root=repository_root,
        expected_classical_commit=expected_classical_commit,
    )
    _validate_tt_artifact(
        tt_payload, tt_dictionary_artifact, repository_root=repository_root
    )
    rows = {row["generator_id"]: row for row in payload["integration_slice"]["rows"]}
    if rows != {
        generator_id: {"generator_id": generator_id, **specification}
        for generator_id, specification in EXPECTED_ROWS.items()
    }:
        raise ValueError("composed integration row dictionary drifted")
    factors = {row["factor_id"]: row for row in payload["repository_factors"]}
    for factor_id, specification in EXPECTED_FACTORS.items():
        if factor_id not in factors or any(
            factors[factor_id].get(key) != expected
            for key, expected in specification.items()
        ):
            raise ValueError("composed factor dictionary drifted")
    observed_map = [
        (
            row["target_factor_id"],
            row["target_bundle_rank"],
            row["target_determinant_sign"],
            row["repository_factor_ids"],
        )
        for row in payload["standard_factor_map"]
    ]
    expected_map = [
        (target, rank, sign, [factor_id])
        for target, rank, sign, factor_id in STANDARD_MAP
    ]
    if observed_map != expected_map:
        raise ValueError("composed standard factor map drifted")
    signed_rank = sum(
        row["target_bundle_rank"] * row["target_determinant_sign"]
        for row in payload["standard_factor_map"]
    )
    z_exponent_rank = sum(
        _fraction(factor["determinant_exponent"]) * factor["component_rank"]
        for factor in payload["repository_factors"]
    )
    if signed_rank != 6 or z_exponent_rank != Fraction(-3):
        raise ValueError("composed signed-rank or Z-exponent balance drifted")
    return {
        **receipt,
        "standard_factor_operators": [
            factors[factor_id]["operator"]
            for _, _, _, factor_id in STANDARD_MAP
        ],
        "Z_exponent_weighted_rank": {
            "numerator": z_exponent_rank.numerator,
            "denominator": z_exponent_rank.denominator,
        },
        "physical_TT_dictionary_bound": True,
        "standard_non_TT_dependencies_bound": True,
        "status": "COMPOSED_LEDGER_SEMANTICALLY_ACCEPTED",
    }


def mutation_receipts(
    payload: dict[str, Any],
    *,
    tt_payload: dict[str, Any],
    tt_dictionary_artifact: dict[str, str],
    expected_classical_commit: str,
) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
        (
            "wrong_physical_upper_operator",
            lambda row: row["repository_factors"][0].update(operator="Delta_2_perp(5)"),
        ),
        (
            "scalar_source_missing_omega",
            lambda row: row["repository_factors"][1].update(
                source_generator_ids=["xi_L"]
            ),
        ),
        (
            "wrong_vector_zero_mode_policy",
            lambda row: row["integration_slice"]["rows"][1].update(
                zero_mode_policy_id="unprimed"
            ),
        ),
        (
            "duplicate_physical_factor_map",
            lambda row: row["standard_factor_map"][2].update(
                repository_factor_ids=["repository_physical_upper"]
            ),
        ),
    )
    receipts = []
    for name, mutate in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        try:
            validate_composed_repository_multiplicity_export(
                mutant,
                tt_payload=tt_payload,
                tt_dictionary_artifact=tt_dictionary_artifact,
                expected_classical_commit=expected_classical_commit,
            )
        except Exception:
            rejected = True
        else:
            rejected = False
        receipts.append({"mutation": name, "rejected": rejected})
    return receipts


def compose_from_path(tt_input: Path) -> dict[str, Any]:
    """Load and content-address one committed TT dictionary, then compose."""

    path = tt_input.resolve()
    try:
        relative = path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("TT dictionary input must be inside the repository") from exc
    if not path.is_file():
        raise ValueError("TT dictionary input is not a file")
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("TT dictionary input is not a JSON object")
    artifact = {
        "format": "JSON_DATA",
        "path": str(relative),
        "sha256": _sha256(path),
    }
    classical_commit = payload.get("classical_commit")
    if not isinstance(classical_commit, str):
        raise ValueError("TT dictionary input has no classical commit")
    return compose_repository_multiplicity_export(
        payload,
        tt_dictionary_artifact=artifact,
        expected_classical_commit=classical_commit,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tt-input", type=Path, required=True)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--emit", type=Path)
    output.add_argument("--check", type=Path)
    args = parser.parse_args()
    value = compose_from_path(args.tt_input)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit is not None:
        args.emit.parent.mkdir(parents=True, exist_ok=True)
        args.emit.write_text(rendered)
    if args.check is not None and (
        not args.check.exists() or args.check.read_text() != rendered
    ):
        raise SystemExit(f"stale composed full-BV multiplicity ledger: {args.check}")
    print("repository full-BV multiplicity ledger composition: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
