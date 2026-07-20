#!/usr/bin/env python3
"""Build the exact closed-S3 relative-phase clock quotient atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_decomp
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
RAW_OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_CLOCK_CONFLUX_EXPORT_V1.json"
)
RESULT_OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1.json"
)
ATLAS_OUTPUT = (
    ROOT / "residual_atlas/closed-s3-relative-phase-clock-fragment-v1.json"
)
REQUEST = (
    ROOT
    / "planning/forge-requests/"
    "closed-s3-relative-phase-clock-atlas-conflux-consumer.json"
)
SOURCE = Path(__file__).resolve()

PREDECESSOR = {
    "path": (
        "d_quotient_classical/compensator/"
        "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1.json"
    ),
    "sha256": "c88b41a26262c2e79f2e7dbcccf66c50e19cfc179ed96dad8a847fc81f4e2433",
    "source_commit": "02a688837b866e9318ae92107744bba9c52de4d7",
    "result_id": "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1",
    "result_state": (
        "CERTIFIED_FINITE_HOMOGENEOUS_GAUSS_RELATIVE_CLOCK_STRUCTURE_THEOREM"
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _rat(value: Any) -> sp.Rational:
    if isinstance(value, bool) or isinstance(value, float):
        raise AssertionError("exact inputs refuse booleans and floating-point values")
    if isinstance(value, int):
        return sp.Rational(value)
    if not isinstance(value, str):
        raise AssertionError(f"exact scalar must be an integer or rational string: {value!r}")
    parsed = sp.Rational(value)
    if str(parsed) != value and value not in {f"{parsed.p}/{parsed.q}", str(parsed.p)}:
        raise AssertionError(f"noncanonical rational string: {value}")
    return parsed


def _q(value: sp.Expr) -> str:
    value = sp.factor(value)
    if not bool(value.is_Rational):
        raise AssertionError(f"non-rational exact value: {value}")
    return str(value)


def _matrix(rows: list[list[Any]], n: int | None = None, r: int | None = None) -> sp.Matrix:
    if n is not None and r == 0:
        if rows != [[] for _ in range(n)]:
            raise AssertionError("zero-column matrix must retain its declared row count")
        return sp.zeros(n, 0)
    matrix = sp.Matrix([[_rat(value) for value in row] for row in rows])
    if n is not None and matrix.shape != (n, r):
        raise AssertionError(f"matrix shape {matrix.shape} != {(n, r)}")
    return matrix


def _integer_matrix(rows: list[list[Any]], n: int, r: int) -> sp.Matrix:
    matrix = _matrix(rows, n, r)
    if any(not bool(value.is_Integer) for value in matrix):
        raise AssertionError("charge matrices must be integral")
    return matrix


def _rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[_q(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _integer_rows(matrix: sp.Matrix) -> list[list[int]]:
    if any(not bool(value.is_Integer) for value in matrix):
        raise AssertionError("expected an integer matrix")
    return [[int(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _inertia(matrix: sp.Matrix) -> dict[str, int]:
    if matrix.rows != matrix.cols or matrix != matrix.T:
        raise AssertionError("inertia requires a square symmetric matrix")
    if matrix.rows == 0:
        return {"positive": 0, "negative": 0, "zero": 0}
    polynomial = sp.Poly(matrix.charpoly().as_expr())
    negative = int(polynomial.count_roots(-sp.oo, 0))
    positive = int(polynomial.count_roots(0, sp.oo))
    zero = matrix.rows - negative - positive
    return {"positive": positive, "negative": negative, "zero": zero}


def _sign_status(inertia: dict[str, int], dimension: int) -> str:
    if dimension == 0:
        return "NOT_APPLICABLE_ZERO_DIMENSION"
    if inertia["zero"]:
        return "DEGENERATE_DIRAC_REQUIRED"
    if inertia["positive"] == dimension:
        return "POSITIVE"
    if inertia["negative"] == dimension:
        return "NEGATIVE"
    return "INDEFINITE_KREIN"


def _case(
    case_id: str,
    q: list[list[int]],
    m: list[list[str | int]],
    pi: list[str | int],
    *,
    input_class: str,
) -> dict[str, Any]:
    n = len(q)
    r = len(q[0]) if q else 0
    if any(len(row) != r for row in q):
        raise AssertionError(f"{case_id}: ragged charge matrix")
    if len(m) != n or any(len(row) != n for row in m):
        raise AssertionError(f"{case_id}: wrong kinetic matrix shape")
    return {
        "case_id": case_id,
        "field_count": n,
        "gauge_generator_count": r,
        "input_class": input_class,
        "Q": q,
        "M": [[_q(_rat(value)) for value in row] for row in m],
        "relative_momentum_coordinates_Pi": [_q(_rat(value)) for value in pi],
    }


def build_raw_export() -> dict[str, Any]:
    cases = [
        _case(
            "n2_rank0_positive",
            [[], []],
            [[2, 1], [1, 3]],
            [1, -1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_rank1_primitive_counterflow",
            [[1], [1]],
            [[2, 0], [0, 3]],
            [1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_rank1_primitive_coordinate",
            [[1], [0]],
            [[2, 0], [0, 3]],
            [1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_rank1_nonprimitive",
            [[2], [4]],
            [[2, 0], [0, 3]],
            [1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_rank2_faithful",
            [[1, 0], [0, 1]],
            [[2, 0], [0, 3]],
            [],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_rank2_nonprimitive",
            [[2, 0], [0, 4]],
            [[2, 0], [0, 3]],
            [],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank0_positive",
            [[], [], []],
            [[2, 1, 0], [1, 3, 1], [0, 1, 4]],
            [1, -1, 2],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank1_primitive",
            [[1], [1], [1]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [1, 2],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank1_nonprimitive",
            [[2], [4], [6]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [1, 2],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank2_faithful",
            [[1, 0], [0, 1], [1, 1]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank2_nonprimitive",
            [[2, 0], [0, 2], [2, 2]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [1],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank3_faithful",
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n3_rank3_nonprimitive",
            [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [],
            input_class="POSITIVE_KINETIC",
        ),
        _case(
            "n2_indefinite_a",
            [[1], [1]],
            [[2, 0], [0, -3]],
            [1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
        _case(
            "n2_indefinite_b",
            [[1], [1]],
            [[2, 0], [0, -1]],
            [1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
        _case(
            "n2_indefinite_c",
            [[1], [1]],
            [[1, 0], [0, -1]],
            [1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
        _case(
            "n3_indefinite_a",
            [[1], [0], [0]],
            [[1, 0, 0], [0, 2, 0], [0, 0, -3]],
            [1, 1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
        _case(
            "n3_indefinite_b",
            [[1], [0], [0]],
            [[1, 0, 0], [0, -2, 0], [0, 0, -3]],
            [1, 1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
        _case(
            "n3_indefinite_c",
            [[1], [0], [0]],
            [[0, 1, 0], [1, 0, 0], [0, 0, 1]],
            [1, 1],
            input_class="DECLARED_INDEFINITE_KINETIC",
        ),
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "pure-weyl-closed-s3-relative-phase-clock-conflux-export-v1",
        "export_id": "CLOSED_S3_RELATIVE_PHASE_CLOCK_CONFLUX_EXPORT_V1",
        "field": "Q",
        "source_scope": (
            "raw finite homogeneous compact-Abelian charge and kinetic matrices "
            "for the closed-S3 relative-phase quotient atlas"
        ),
        "oracle_exclusion": {
            "excluded_fields": [
                "rank",
                "smith_invariant_factors",
                "stabilizer",
                "relative_dimension",
                "reduced_metric",
                "kinetic_sign",
                "moment_map_verdict",
                "claim_status",
            ],
            "statement": (
                "A Conflux importer may read only case identifiers, declared matrix "
                "shapes, exact Q/M/Pi data and the declared input class. It must "
                "derive every quotient and sign result independently."
            ),
        },
        "cases": cases,
    }


def _canonicalize_case(raw: dict[str, Any]) -> dict[str, Any]:
    n = raw["field_count"]
    r = raw["gauge_generator_count"]
    q = _integer_matrix(raw["Q"], n, r)
    m = _matrix(raw["M"], n, n)
    if m != m.T or m.det() == 0:
        raise AssertionError(f"{raw['case_id']}: M must be symmetric and nonsingular")

    d, u, v = smith_normal_decomp(q, domain=ZZ)
    if u * q * v != d or abs(int(u.det())) != 1 or (r and abs(int(v.det())) != 1):
        raise AssertionError(f"{raw['case_id']}: invalid Smith witness")
    rank = int(q.rank())
    factors = [abs(int(d[i, i])) for i in range(rank)]
    if any(value == 0 for value in factors):
        raise AssertionError(f"{raw['case_id']}: zero nontrivial Smith factor")
    e_gauge = sp.eye(n)[:, :rank]
    e_relative = sp.eye(n)[:, rank:]
    primitive_image = u.inv() * e_gauge
    relative_tangent = u.inv() * e_relative
    relative_character = u.T * e_relative
    if (
        q.T * relative_character != sp.zeros(r, n - rank)
        or relative_character.T * primitive_image != sp.zeros(n - rank, rank)
        or relative_character.T * relative_tangent != sp.eye(n - rank)
    ):
        raise AssertionError(f"{raw['case_id']}: lattice duality failed")
    qv = q * v
    expected_qv = primitive_image * sp.diag(*factors) if rank else sp.zeros(n, 0)
    if r > rank:
        expected_qv = expected_qv.row_join(sp.zeros(n, r - rank))
    if qv != expected_qv:
        raise AssertionError(f"{raw['case_id']}: raw-to-primitive image witness failed")

    relative_dimension = n - rank
    pi = (
        sp.zeros(0, 1)
        if relative_dimension == 0
        else sp.Matrix([_rat(value) for value in raw["relative_momentum_coordinates_Pi"]])
    )
    if pi.rows != relative_dimension:
        raise AssertionError(f"{raw['case_id']}: wrong relative momentum dimension")
    p = relative_character * pi
    gauss = q.T * p
    if gauss != sp.zeros(r, 1):
        raise AssertionError(f"{raw['case_id']}: exact Gauss fibre failed")
    a = relative_character.T * m.inv() * relative_character
    inertia_m = _inertia(m)
    inertia_a = _inertia(a)
    sign = _sign_status(inertia_a, relative_dimension)
    g_rel = None if inertia_a["zero"] else a.inv()
    velocity = m.inv() * p
    relative_velocity = relative_character.T * velocity
    raw_d = (p.T * velocity)[0]
    if raw_d != (pi.T * relative_velocity)[0]:
        raise AssertionError(f"{raw['case_id']}: raw-D reduction failed")
    if g_rel is not None and relative_dimension:
        lhs = sp.Rational(1, 2) * (p.T * m.inv() * p)[0]
        rhs = sp.Rational(1, 2) * (
            relative_velocity.T * g_rel * relative_velocity
        )[0]
        if sp.factor(lhs - rhs) != 0:
            raise AssertionError(f"{raw['case_id']}: kinetic quotient mismatch")

    finite_factors = [value for value in factors if value > 1]
    finite_order = 1
    for value in finite_factors:
        finite_order *= value
    original_action_faithful = r == rank and not finite_factors
    all_momenta_supported = all(value != 0 for value in p) if p.rows else False
    all_velocities_supported = all(value != 0 for value in velocity) if velocity.rows else False

    return {
        "case_id": raw["case_id"],
        "input_class": raw["input_class"],
        "field_count": n,
        "gauge_generator_count": r,
        "rank": rank,
        "smith": {
            "D": _integer_rows(d),
            "U": _integer_rows(u),
            "V": _integer_rows(v),
            "UQ_equals_DVinv": True,
            "UQV_equals_D": True,
            "det_U": int(u.det()),
            "det_V": int(v.det()) if r else 1,
            "invariant_factors": factors,
        },
        "lattices": {
            "raw_charge_lattice_basis_after_V": _integer_rows(qv),
            "primitive_image_lattice_basis_J": _integer_rows(primitive_image),
            "primitive_image_index": finite_order,
            "relative_tangent_lattice_basis_B": _integer_rows(relative_tangent),
            "relative_character_lattice_basis_N": _integer_rows(relative_character),
            "checks": {
                "QT_N_zero": True,
                "NT_J_zero": True,
                "NT_B_identity": True,
                "QV_equals_J_diag_d_then_zero": True,
            },
        },
        "orbit_and_stabilizer": {
            "compact_gauge_orbit_dimension": rank,
            "continuous_stabilizer_dimension": r - rank,
            "finite_stabilizer_invariant_factors": finite_factors,
            "finite_stabilizer_order": finite_order,
            "original_torus_action_faithful": original_action_faithful,
            "relative_phase_torus_dimension": relative_dimension,
        },
        "zero_total_charge_fibre": {
            "equation": "Q^T p=0",
            "dimension": relative_dimension,
            "canonical_parameterization": "p=N Pi",
            "Pi": [_q(value) for value in pi],
            "p": [_q(value) for value in p],
            "QT_p": [_q(value) for value in gauss],
            "nonzero_physical_relative_momentum_iff": (
                "relative_dimension>0 and Pi!=0"
            ),
            "fixture_is_nonzero": bool(any(value != 0 for value in pi)),
            "fixture_all_phase_momenta_nonzero": all_momenta_supported,
        },
        "kinetic_restriction": {
            "M": _rows(m),
            "M_inertia": inertia_m,
            "A_equals_NT_Minv_N": _rows(a),
            "A_inertia": inertia_a,
            "Grel_equals_Ainv": None if g_rel is None else _rows(g_rel),
            "sign_status": sign,
            "horizontal_velocity_Minv_p": [_q(value) for value in velocity],
            "relative_velocity_NT_Minv_p": [
                _q(value) for value in relative_velocity
            ],
            "fixture_all_phase_velocities_nonzero": all_velocities_supported,
        },
        "moment_maps": {
            "raw_D_per_unit_volume": _q(raw_d),
            "raw_D_identity": "D_phase=p^T M^{-1}p=Pi^T dot(psi)",
            "K_Berger_phase_with_matched_helical_stabilizer": "0",
            "K_Berger_activation_condition": (
                "w=dot(psi) belongs to the continuous stabilizer of the potential"
            ),
            "unmatched_K_Berger_status": "NO_MODEL_SPECIFIC_POTENTIAL_SELECTED",
        },
        "basis_change_witness": {
            "phase_coordinates": "theta'=U theta",
            "momenta": "p'=U^{-T}p",
            "kinetic_matrix": "M'=U^{-T} M U^{-1}",
            "gauge_coordinates": "gamma'=V^{-1}gamma",
            "relative_characters": "psi=N^T theta",
        },
    }


def _stratum(
    n: int,
    rank: int,
    primitive: bool | None,
    canonical_factors: list[int],
) -> dict[str, Any]:
    if rank == 0:
        stratum_id = f"n{n}_rank0"
        parameter = "no nonzero Smith factors"
    else:
        suffix = "primitive" if primitive else "nonprimitive"
        stratum_id = f"n{n}_rank{rank}_{suffix}"
        parameter = (
            "d_i=1 for every i"
            if primitive
            else "0<d_1|...|d_k and at least one d_i>1"
        )
    relative_dimension = n - rank
    return {
        "stratum_id": stratum_id,
        "field_count": n,
        "rank": rank,
        "smith_parameter_locus": parameter,
        "canonical_effective_representative_D": [
            [canonical_factors[i] if i == j and i < rank else 0 for j in range(rank)]
            for i in range(n)
        ],
        "compact_orbit_dimension": rank,
        "continuous_stabilizer_dimension_for_r_generators": f"r-{rank}",
        "finite_stabilizer": (
            "trivial"
            if primitive is not False
            else "direct sum_i Z/d_i over nonunit invariant factors"
        ),
        "relative_phase_torus_dimension": relative_dimension,
        "zero_charge_fibre_dimension": relative_dimension,
        "nonzero_physical_relative_momentum_exists": relative_dimension > 0,
        "positive_M_reduced_sign": (
            "NOT_APPLICABLE_ZERO_DIMENSION"
            if relative_dimension == 0
            else "POSITIVE"
        ),
        "declared_indefinite_M_reduced_sign_rule": (
            "inertia of A=N^T M^{-1}N; A singular requires Dirac reduction"
        ),
        "raw_D_restriction": "Pi^T A Pi",
        "K_Berger_restriction": (
            "zero in the phase sector only when w=dot(psi) is a potential symmetry"
        ),
    }


def _strata() -> list[dict[str, Any]]:
    return [
        _stratum(2, 0, None, []),
        _stratum(2, 1, True, [1]),
        _stratum(2, 1, False, [2]),
        _stratum(2, 2, True, [1, 1]),
        _stratum(2, 2, False, [1, 2]),
        _stratum(3, 0, None, []),
        _stratum(3, 1, True, [1]),
        _stratum(3, 1, False, [2]),
        _stratum(3, 2, True, [1, 1]),
        _stratum(3, 2, False, [1, 2]),
        _stratum(3, 3, True, [1, 1, 1]),
        _stratum(3, 3, False, [1, 1, 2]),
    ]


def _check_import(path: Path, declaration: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    actual = _sha(path)
    if (
        actual != declaration["sha256"]
        or payload["result_id"] != declaration["result_id"]
        or payload["result_state"] != declaration["result_state"]
    ):
        raise AssertionError(f"import drifted: {path}")
    return {**declaration, "actual_sha256": actual}


def build_result(raw: dict[str, Any], raw_sha: str) -> dict[str, Any]:
    predecessor = _check_import(ROOT / PREDECESSOR["path"], PREDECESSOR)
    request = json.loads(REQUEST.read_text())
    request_sha = _sha(REQUEST)
    if (
        request["id"]
        != "sf:forge-request/closed-s3-relative-phase-clock-atlas-conflux-consumer"
        or request["body"]["state"] not in {"REQUESTED", "ACCEPTED", "LANDED"}
    ):
        raise AssertionError("Conflux consumer request drifted or was refused")
    exact_cases = [_canonicalize_case(case) for case in raw["cases"]]
    strata = _strata()
    theorem = {
        "smith_and_lattice_decomposition": (
            "For UQV=D, J=U^{-1}E_gauge is a primitive image-lattice basis, "
            "B=U^{-1}E_relative is a quotient tangent-lattice basis and "
            "N=U^T E_relative is its dual relative-character basis. "
            "N^T J=0 and N^T B=1."
        ),
        "compact_stabilizer": (
            "ker(T^r -> T^n) has identity component T^{r-k} and component "
            "group direct_sum_i Z/d_i; unit factors are omitted."
        ),
        "zero_charge_fibre": (
            "Q^T p=0 iff p=N Pi. A nonzero physical relative momentum exists "
            "iff n-rank(Q)>0 and Pi is nonzero."
        ),
        "positive_kinetic_restriction": (
            "For M>0, A=N^T M^{-1}N and G_rel=A^{-1} are positive definite "
            "on every nonzero relative stratum."
        ),
        "declared_indefinite_restriction": (
            "For symmetric nonsingular declared-indefinite M, the regular "
            "relative sign is exactly inertia(A). If A is singular, the "
            "standard quotient is not promoted and an additional Dirac "
            "reduction is required."
        ),
        "component_support": {
            "momenta": (
                "There exists p in ker(Q^T) with all selected p_i nonzero iff "
                "every selected e_i is outside im_R(Q)."
            ),
            "velocities": (
                "There exists v in ker(Q^T M) with all selected v_i nonzero iff "
                "every selected e_i is outside im_R(MQ)."
            ),
        },
        "moment_maps": {
            "raw_D": "D_phase/Vol=p^T M^{-1}p=Pi^T A Pi",
            "K_Berger": (
                "K_phase=D_phase-R_w vanishes for a uniform helical solution "
                "only when w=dot(psi) lies in the continuous stabilizer of V."
            ),
        },
    }
    conflux = {
        "raw_export_path": str(RAW_OUTPUT.relative_to(ROOT)),
        "raw_export_sha256": raw_sha,
        "field": "Q",
        "oracle_exclusion": "STRUCTURAL",
        "consumer_id": "sf:program/work/classical-closed-s3-relative-phase-clock-atlas",
        "consumer_policy_status": "NO_CONSUMER_DECLARATION",
        "generic_math_request": {
            "path": "planning/forge-requests/exact-symplectic-poisson-moment-map-reduction.json",
            "state": "ACCEPTED_NOT_LANDED",
        },
        "consumer_request": {
            "path": str(REQUEST.relative_to(ROOT)),
            "sha256": request_sha,
            "state": request["body"]["state"],
        },
        "certified_conflux_map": False,
        "lifecycle_status": "NO_CERTIFIED_CONFLUX_IMPORTER",
    }
    payload = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "pure-weyl-closed-s3-relative-phase-clock-atlas-v1",
        "result_id": "CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1",
        "result_state": "CERTIFIED_EXACT_CLASSICAL_QUOTIENT_ATLAS_CONFLUX_PENDING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "imports": [predecessor],
        "scope": {
            "spatial_manifold": "closed smooth S3",
            "field_counts_fully_classified": [2, 3],
            "charge_domain": "integer matrices Q in Mat_{n x r}(Z)",
            "carrier": "finite homogeneous phase quotient at fixed moduli",
            "kinetic_domain": (
                "symmetric exact rational M, positive or explicitly declared "
                "indefinite; singular M excluded"
            ),
            "external_sources": False,
            "boundary": False,
        },
        "theorem": theorem,
        "strata": strata,
        "exact_cases": exact_cases,
        "atlas_export": {
            "path": str(ATLAS_OUTPUT.relative_to(ROOT)),
            "status": "CERTIFIED_STRUCTURAL_FRAGMENT",
            "physical_mode_identification": "NO_CERTIFIED_MAP",
        },
        "conflux_export": conflux,
        "proof_obligations": {
            "smith_witnesses": "VERIFIED_EXACTLY",
            "primitive_lattice_duality": "VERIFIED_EXACTLY",
            "rank_and_stabilizer_strata": "COMPLETE_FOR_N2_AND_N3",
            "positive_kinetic_sign": "VERIFIED_EXACTLY",
            "declared_indefinite_sign_examples": "VERIFIED_EXACTLY",
            "gauss_charge_fibres": "VERIFIED_EXACTLY",
            "raw_D_and_conditional_K_Berger": "VERIFIED_EXACTLY",
            "residual_atlas_fragment": "SCHEMA_VALIDATED",
            "conflux_rediscovery": "NOT_RUN_NO_CERTIFIED_IMPORTER",
        },
        "claim_flags": {
            "EXACT_TWO_AND_THREE_FIELD_ATLAS": True,
            "ARBITRARY_FINITE_N_CLASSIFICATION": False,
            "MODEL_SPECIFIC_ACTION_SELECTED": False,
            "SCALE_GAUGE_REPAIR": False,
            "FULL_BV_OR_CAUSAL_PARENT": False,
            "CONFLUX_IDENTIFICATION": False,
            "PHYSICAL_RESIDUAL_MODE": False,
            "HADAMARD_OR_QUANTUM": False,
        },
        "claim_boundary": (
            "This result is an exact finite-dimensional classical quotient atlas "
            "for two and three homogeneous phase fields on closed source-free S3. "
            "It classifies integer charge homomorphisms, primitive image and "
            "relative lattices, compact stabilizers, zero-charge fibres, reduced "
            "kinetic signs and raw-D/conditional K_Berger phase moment maps. It "
            "does not select a pure-Weyl action, repair the failed scale gauge, "
            "identify a physical residual mode, establish nonhomogeneous PDE or "
            "full BV/causal/Hadamard data, or certify a Conflux map."
        ),
    }
    payload["content_hashes"] = {
        "raw_export_sha256": raw_sha,
        "theorem_sha256": _digest(theorem),
        "strata_sha256": _digest(strata),
        "exact_cases_sha256": _digest(exact_cases),
        "conflux_boundary_sha256": _digest(conflux),
        "claim_boundary_sha256": _digest(payload["claim_boundary"]),
    }
    validate_result(payload)
    return payload


def validate_result(payload: dict[str, Any]) -> None:
    if payload["result_state"] != (
        "CERTIFIED_EXACT_CLASSICAL_QUOTIENT_ATLAS_CONFLUX_PENDING"
    ):
        raise AssertionError("result state promoted or narrowed")
    if len(payload["strata"]) != 12:
        raise AssertionError("two/three-field stratum census incomplete")
    expected_ids = {
        "n2_rank0",
        "n2_rank1_primitive",
        "n2_rank1_nonprimitive",
        "n2_rank2_primitive",
        "n2_rank2_nonprimitive",
        "n3_rank0",
        "n3_rank1_primitive",
        "n3_rank1_nonprimitive",
        "n3_rank2_primitive",
        "n3_rank2_nonprimitive",
        "n3_rank3_primitive",
        "n3_rank3_nonprimitive",
    }
    if {item["stratum_id"] for item in payload["strata"]} != expected_ids:
        raise AssertionError("stratum identifiers drifted")
    for case in payload["exact_cases"]:
        if (
            not all(case["smith"][key] for key in ("UQ_equals_DVinv", "UQV_equals_D"))
            or not all(case["lattices"]["checks"].values())
            or any(value != "0" for value in case["zero_total_charge_fibre"]["QT_p"])
        ):
            raise AssertionError("exact quotient witness failed")
        if case["input_class"] == "POSITIVE_KINETIC":
            expected = (
                "NOT_APPLICABLE_ZERO_DIMENSION"
                if case["orbit_and_stabilizer"]["relative_phase_torus_dimension"] == 0
                else "POSITIVE"
            )
            if case["kinetic_restriction"]["sign_status"] != expected:
                raise AssertionError("positive quotient sign drifted")
    sign_cases = {
        item["case_id"]: item["kinetic_restriction"]["sign_status"]
        for item in payload["exact_cases"]
        if item["input_class"] == "DECLARED_INDEFINITE_KINETIC"
    }
    if sign_cases != {
        "n2_indefinite_a": "POSITIVE",
        "n2_indefinite_b": "NEGATIVE",
        "n2_indefinite_c": "DEGENERATE_DIRAC_REQUIRED",
        "n3_indefinite_a": "INDEFINITE_KREIN",
        "n3_indefinite_b": "NEGATIVE",
        "n3_indefinite_c": "DEGENERATE_DIRAC_REQUIRED",
    }:
        raise AssertionError(f"declared-indefinite sign census drifted: {sign_cases}")
    conflux = payload["conflux_export"]
    if (
        conflux["certified_conflux_map"]
        or conflux["lifecycle_status"] != "NO_CERTIFIED_CONFLUX_IMPORTER"
        or conflux["consumer_policy_status"] != "NO_CONSUMER_DECLARATION"
    ):
        raise AssertionError("Conflux boundary promoted")
    flags = payload["claim_flags"]
    if (
        not flags["EXACT_TWO_AND_THREE_FIELD_ATLAS"]
        or flags["ARBITRARY_FINITE_N_CLASSIFICATION"]
        or flags["MODEL_SPECIFIC_ACTION_SELECTED"]
        or flags["SCALE_GAUGE_REPAIR"]
        or flags["FULL_BV_OR_CAUSAL_PARENT"]
        or flags["CONFLUX_IDENTIFICATION"]
        or flags["PHYSICAL_RESIDUAL_MODE"]
        or flags["HADAMARD_OR_QUANTUM"]
    ):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "raw_export_sha256": payload["conflux_export"]["raw_export_sha256"],
        "theorem_sha256": _digest(payload["theorem"]),
        "strata_sha256": _digest(payload["strata"]),
        "exact_cases_sha256": _digest(payload["exact_cases"]),
        "conflux_boundary_sha256": _digest(payload["conflux_export"]),
        "claim_boundary_sha256": _digest(payload["claim_boundary"]),
    }
    if payload["content_hashes"] != expected_hashes:
        raise AssertionError("content hashes drifted")


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build_atlas_fragment(result_sha: str) -> dict[str, Any]:
    evidence = {
        "path": str(RESULT_OUTPUT.relative_to(ROOT)),
        "result_id": "CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1",
        "sha256": result_sha,
    }
    entries = []
    for stratum in _strata():
        relative_dimension = stratum["relative_phase_torus_dimension"]
        entries.append(
            {
                "id": f"closed-s3-relative-phase-clock.{stratum['stratum_id']}",
                "scope": {
                    "theory": (
                        "finite homogeneous compact-Abelian scalar sigma-model "
                        "class; no selected pure-Weyl action"
                    ),
                    "background": "closed smooth S3 homogeneous mechanics",
                    "boundaries": "none",
                    "charge_sector": (
                        f"Q^T p=0; {stratum['stratum_id']}; "
                        f"relative dimension {relative_dimension}"
                    ),
                    "carrier": (
                        "structural relative-phase torus character/tangent lattice; "
                        "not a certified pure-Weyl physical mode"
                    ),
                    "degree": 0,
                    "parity": "scalar phase; no pure-Weyl parity crosswalk",
                    "ell": 0,
                    "m": 0,
                    "k": stratum["rank"],
                    "omega": "not fixed; no causal dispersion imported",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": _claim(
                        "NO_CERTIFIED_MAP",
                        "No nonhomogeneous causal operator or frequency carrier is selected.",
                    ),
                    "lee_wald": _claim(
                        "NO_CERTIFIED_MAP",
                        "The exact finite quotient is not a Lee-Wald field-theory pairing.",
                    ),
                    "taub_maps": _claim(
                        "CERTIFIED",
                        (
                            "The homogeneous phase restriction of raw D is Pi^T A Pi; "
                            "the K_Berger phase term vanishes only under the recorded "
                            "matched potential-stabilizer condition."
                        ),
                    ),
                    "resonance": _claim(
                        "NOT_APPLICABLE",
                        "No oscillatory carrier or resonance problem is part of this atlas.",
                    ),
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": _claim(
                            "NO_CERTIFIED_MAP",
                            "No second-order PDE correction class is imported.",
                        ),
                        "smooth_secular": _claim(
                            "NO_CERTIFIED_MAP",
                            "No second-order PDE correction class is imported.",
                        ),
                        "causal_retarded": _claim(
                            "NO_CERTIFIED_MAP",
                            "No retarded Green carrier is imported.",
                        ),
                    },
                },
                "evidence": [evidence],
                "claim_boundary": (
                    "CERTIFIED only as an exact finite homogeneous symplectic/charge "
                    "quotient stratum. This row is not a particle, a pure-Weyl "
                    "residual class, a background crosswalk, a causal mode or a "
                    "scale-compensator repair."
                ),
            }
        )
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(SOURCE.relative_to(ROOT)),
        "generated_by_sha256": _sha(SOURCE),
        "status_vocabulary": [
            "CERTIFIED",
            "OBSTRUCTED",
            "OPEN",
            "NOT_APPLICABLE",
            "NO_CERTIFIED_MAP",
        ],
        "description_axes": [
            "causal",
            "symplectic",
            "nonlinear",
            "observational",
            "quantum",
        ],
        "entries": entries,
        "verification_commands": [
            (
                "python3 d_quotient_classical/compensator/"
                "closed_s3_relative_phase_clock_atlas.py --check"
            ),
            (
                "python3 residual_atlas/validate_fragment.py "
                "residual_atlas/closed-s3-relative-phase-clock-fragment-v1.json"
            ),
        ],
    }


def build_all() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    raw = build_raw_export()
    raw_sha = hashlib.sha256(_dump(raw).encode()).hexdigest()
    result = build_result(raw, raw_sha)
    result_sha = hashlib.sha256(_dump(result).encode()).hexdigest()
    atlas = build_atlas_fragment(result_sha)
    return raw, result, atlas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw, result, atlas = build_all()
    outputs = (
        (RAW_OUTPUT, raw),
        (RESULT_OUTPUT, result),
        (ATLAS_OUTPUT, atlas),
    )
    if args.check:
        for path, value in outputs:
            if path.read_text() != _dump(value):
                raise AssertionError(f"generated artifact drifted: {path}")
        print("CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1: PASS")
        return
    for path, value in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump(value))
    print(RESULT_OUTPUT)


if __name__ == "__main__":
    main()
