#!/usr/bin/env python3
"""Certify the minimal six-master pole-four span of the physical triangle."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import itertools
import json
import multiprocessing
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_i29_integrated_function import _pole4_system
from .generic_background_ghost_n3_pole3_relative_ibp import (
    A,
    B,
    C,
    X1,
    X2,
    X3,
    _domain_matrix,
    _monomials,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-master-completeness-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json"
POLE4 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"

E3 = sp.expand(A * B * C)
NEW_MASTERS = (
    E3,
    sp.expand(E3 * (A - B)),
    sp.expand(E3 * (B - C)),
)
NEW_MASTER_IDS = ("M14_singlet", "M15_standard_u", "M16_standard_v")
PIVOT_FIXTURE = {X1: sp.Rational(2), X2: sp.Rational(3), X3: sp.Rational(5)}
RANK_FIXTURES = ((1, 1, 1), (2, 3, 5), (3, 5, 7), (5, 7, 11))
ORBIT_REPRESENTATIVES = (0, 1, 4, 7, 10)

_RANK_MATRIX: Any | None = None
_TARGET_MATRICES: list[Any] | None = None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _target(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            * X1 ** term["box_exponents"][0]
            * X2 ** term["box_exponents"][1]
            * X3 ** term["box_exponents"][2]
            for term in row["terms"]
        )
    )


def _master_coordinate(expression: sp.Expr) -> list[int]:
    u, v = NEW_MASTERS[1:]
    coefficients = sp.symbols("master_u master_v")
    defect = sp.Poly(sp.expand(expression - coefficients[0] * u - coefficients[1] * v), A, B)
    solution = sp.solve(list(defect.coeffs()), coefficients, dict=True)
    if len(solution) != 1:
        raise ValueError("standard-master coordinate solve failed")
    return [int(solution[0][coefficient]) for coefficient in coefficients]


def _s3_action() -> list[dict[str, Any]]:
    rows = []
    for permutation in itertools.permutations((A, B, C), 3):
        substitution = {A: permutation[0], B: permutation[1]}
        singlet = E3.subs(substitution, simultaneous=True)
        transformed = [
            master.subs(substitution, simultaneous=True)
            for master in NEW_MASTERS[1:]
        ]
        if sp.expand(singlet - E3) != 0:
            raise ValueError("M14 lost S3 invariance")
        matrix = [_master_coordinate(value) for value in transformed]
        rows.append(
            {
                "alpha_permutation": [
                    ("alpha1" if value == A else "alpha2" if value == B else "alpha0")
                    for value in permutation
                ],
                "standard_pair_action_columns": matrix,
                "determinant": int(sp.Matrix(matrix).det()),
                "trace": int(sp.Matrix(matrix).trace()),
            }
        )
    return rows


def _polynomial_key(expression: sp.Expr) -> tuple[Any, ...]:
    return tuple(sp.Poly(sp.expand(expression), A, B, X1, X2, X3, domain=sp.QQ).terms())


def _orbit_crosswalk(
    projection: dict[str, Any], targets: list[sp.Expr]
) -> list[dict[str, Any]]:
    lookup = {_polynomial_key(target): row["channel_id"] for row, target in zip(projection["projection_rows"], targets)}
    if len(lookup) != len(targets):
        raise ValueError("physical target polynomial identities collided")
    generators = (
        ("swap_alpha0_alpha2", {A: A, B: C, X1: X2, X2: X1, X3: X3}),
        ("swap_alpha1_alpha2", {A: B, B: A, X1: X3, X2: X2, X3: X1}),
    )
    output = []
    for generator_id, substitution in generators:
        mapping = []
        for row, target in zip(projection["projection_rows"], targets):
            transformed = target.subs(substitution, simultaneous=True)
            target_id = lookup.get(_polynomial_key(transformed))
            if target_id is None:
                raise ValueError(f"physical S3 orbit does not close: {generator_id} {row['channel_id']}")
            mapping.append({"source_channel_id": row["channel_id"], "target_channel_id": target_id})
        output.append({"generator_id": generator_id, "channel_map": mapping})
    return output


def _system(projection: dict[str, Any]) -> dict[str, Any]:
    tangent, _, old_masters = _pole4_system()
    all_columns = [*tangent, *old_masters, *NEW_MASTERS]
    basis = _monomials(9)
    fixture_matrix = _domain_matrix(
        [value.subs(PIVOT_FIXTURE) for value in all_columns], basis
    )
    pivot_columns = tuple(fixture_matrix.rref()[1])
    if len(pivot_columns) != 52:
        raise ValueError("six-master pivot rank drifted")
    selected = [all_columns[index] for index in pivot_columns]
    selected_matrix = _domain_matrix(selected, basis)
    targets = [_target(row) for row in projection["projection_rows"]]
    return {
        "tangent": tangent,
        "old_masters": old_masters,
        "all_columns": all_columns,
        "basis": basis,
        "pivot_columns": pivot_columns,
        "selected": selected,
        "selected_matrix": selected_matrix,
        "targets": targets,
    }


def _generic_rank_worker(index: int) -> int:
    if _RANK_MATRIX is None or _TARGET_MATRICES is None:
        raise RuntimeError("generic-rank worker was not initialized")
    return int(_RANK_MATRIX.hstack(_TARGET_MATRICES[index]).rank())


def _generic_target_ranks(system: dict[str, Any], jobs: int) -> list[int]:
    global _RANK_MATRIX, _TARGET_MATRICES
    _RANK_MATRIX = system["selected_matrix"]
    _TARGET_MATRICES = [
        _domain_matrix([target], system["basis"], _RANK_MATRIX.domain)
        for target in system["targets"]
    ]
    representative_indices = list(ORBIT_REPRESENTATIVES)
    if jobs <= 1:
        representative_ranks = []
        for index in representative_indices:
            rank = _generic_rank_worker(index)
            print(f"generic physical orbit representative rank: index={index} rank={rank}", flush=True)
            representative_ranks.append(rank)
    else:
        context = multiprocessing.get_context("fork")
        with ProcessPoolExecutor(max_workers=jobs, mp_context=context) as executor:
            representative_ranks = list(executor.map(_generic_rank_worker, representative_indices))
    family_ranks = {
        family: rank
        for family, rank in zip(("I10", "I24", "I25", "I28", "I29"), representative_ranks)
    }
    return [
        family_ranks[row["channel_id"].split("_")[0]]
        for row in json.loads(PROJECTION.read_text())["projection_rows"]
    ]


def _fixture_ranks(system: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for fixture in RANK_FIXTURES:
        substitution = dict(zip((X1, X2, X3), map(sp.Rational, fixture)))
        base = _domain_matrix(
            [value.subs(substitution) for value in system["selected"]],
            system["basis"],
        )
        targets = _domain_matrix(
            [value.subs(substitution) for value in system["targets"]],
            system["basis"],
            base.domain,
        )
        rows.append(
            {
                "boxes": list(fixture),
                "six_master_rank": int(base.rank()),
                "six_master_plus_all_physical_rows_rank": int(base.hstack(targets).rank()),
            }
        )
    return rows


def build(*, exhaustive: bool, jobs: int = 1) -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    pole4 = json.loads(POLE4.read_text())
    if (
        projection.get("claim_flags", {}).get("PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED")
        is not True
        or len(projection.get("projection_rows", [])) != 11
        or pole4.get("rank_ledger", {}).get("tangent_plus_masters_rank") != 49
    ):
        raise ValueError("triangle-master dependency drifted")
    system = _system(projection)
    tangent_pivots = [index for index in system["pivot_columns"] if index < 84]
    if len(tangent_pivots) != 46:
        raise ValueError("canonical tangent pivot count drifted")
    stages = []
    stage_columns = [system["all_columns"][index] for index in tangent_pivots]
    for master_id, master in zip(
        ("J_triangle", "M_x1", "M_x2", *NEW_MASTER_IDS),
        (*system["old_masters"], *NEW_MASTERS),
    ):
        stage_columns.append(master)
        stages.append(
            {
                "added_master_id": master_id,
                "generic_rank": int(_domain_matrix(stage_columns, system["basis"]).rank()),
            }
        )
    expected_stages = [47, 48, 49, 50, 51, 52]
    if [row["generic_rank"] for row in stages] != expected_stages:
        raise ValueError("six-master generic rank ladder drifted")

    if exhaustive:
        generic_ranks = _generic_target_ranks(system, jobs)
    else:
        if not OUTPUT.exists():
            raise ValueError("fast build requires the emitted exhaustive certificate")
        stored = json.loads(OUTPUT.read_text())
        generic_ranks = [row["generic_augmented_rank"] for row in stored["physical_channel_rows"]]
    if generic_ranks != [52] * 11:
        raise ValueError("a physical channel escapes the six-master generic span")

    channel_rows = [
        {
            "channel_id": row["channel_id"],
            "numerator_box_degree": row["numerator_box_degree"],
            "generic_augmented_rank": rank,
            "membership_status": "IN_SIX_MASTER_RELATIVE_IBP_SPAN",
        }
        for row, rank in zip(projection["projection_rows"], generic_ranks)
    ]
    formula_payload = {
        "ambient_alpha_monomial_count": len(system["basis"]),
        "raw_tangent_column_count": len(system["tangent"]),
        "canonical_tangent_pivot_count": len(tangent_pivots),
        "canonical_pivot_columns": list(system["pivot_columns"]),
        "rank_ladder": stages,
        "new_master_numerators": {
            "M14_singlet": "alpha0*alpha1*alpha2",
            "M15_standard_u": "alpha0*alpha1*alpha2*(alpha1-alpha2)",
            "M16_standard_v": "alpha0*alpha1*alpha2*(alpha2-alpha0)",
        },
        "S3_action": _s3_action(),
        "physical_channel_orbit_crosswalk": _orbit_crosswalk(
            projection, system["targets"]
        ),
        "physical_channel_rows": channel_rows,
        "exact_rank_fixtures": _fixture_ranks(system),
    }
    return {
        "schema": "quantum-weyl-generic-background-physical-hessian-triangle-master-completeness-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS",
        "result_state": "ALL_ELEVEN_PHYSICAL_TRIANGLE_ROWS_REDUCED_TO_SIX_MASTER_RELATIVE_IBP_SPAN",
        "lifecycle_state": "TRIANGLE_MASTER_CARRIERS_COMPLETE_RENORMALIZED_MASTER_VALUES_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "dependencies": {
            "physical_five_carrier_projection": _reference(PROJECTION),
            "pole4_relative_IBP_architecture": _reference(POLE4),
        },
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "generic nonexceptional x1,x2,x3",
            "input": "eleven exact physical three-H1 numerator rows over Delta^4",
            "output": "minimal singlet plus standard-S3 master carrier completion of the pole-four relative-IBP span",
        },
        **formula_payload,
        "formula_digest": _canonical_digest(formula_payload),
        "claim_flags": {
            "M14_SINGLET_REQUIRED": True,
            "STANDARD_S3_MASTER_PAIR_REQUIRED": True,
            "ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN": True,
            "GENERIC_MASTER_SPAN_RANK_52": True,
            "RENORMALIZED_SIX_MASTER_VALUES_COMPUTED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "verification_policy": {
            "exhaustive_rail": "recompute five S3-orbit-representative generic fraction-field augmented ranks and the exact orbit crosswalk covering all eleven rows",
            "fast_rail": "recompute generic six-master rank ladder, S3 action, dependency hashes and four exact rank fixtures",
        },
        "next_gate": "EVALUATE_RENORMALIZED_SINGLET_AND_STANDARD_S3_MASTER_VALUES_AND_ASSEMBLE_PHYSICAL_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate proves that the eleven generic physical three-H1 numerator rows lie in the pole-four relative-IBP span after adjoining exactly three carriers: the previously identified symmetric M14 carrier and a two-dimensional standard S3 pair. The rank ladder is 49 to 50 to 51 to 52, and every physical row leaves the generic rank at 52. This completes the carrier inventory needed by the physical triangle. It does not evaluate the three renormalized master values, integrate the physical triangle, assemble the repository cubic form factors, supply Gamma1 or Q1, restore a QME, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, positivity, scattering or unitarity theorem."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda row: list(row.path)
    )
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    value = build(exhaustive=not args.fast, jobs=max(1, args.jobs))
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale triangle-master completeness certificate: {OUTPUT}")
    print("GENERIC PHYSICAL TRIANGLE MASTER COMPLETENESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
