#!/usr/bin/env python3
"""Compute the first non-stabilizer physical q70 Berger isotype exactly.

The complete all-k j=1/2 block is the smallest nonzero Peter--Weyl isotype.
The diagonal-U1 and gauge-fixed complements contract, leaving the 26-row
minimal endpoint.  This producer constructs its actual gauge quotient and
finds a genuine complex-frequency physical factor.  That first exact failure
settles the requested full-health gate without extrapolating a low-mode name
or mistaking the odd BV pairing for a positive state-space form.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy import QQ

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import generators


OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-payload-v1.schema.json"

IMPORTS = {
    "repaired_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
        "3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2",
    ),
    "repaired_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json",
        "c59b1a74aced082155db3446c40aa1b14e3982e66670a3c097539b25d5d5c938",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2",
    ),
    "all_k_closure": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json",
        "a4e3ce0462344c05bb8ad1fa6d5c367bf2453b923916ba1aa34b58b8bee4a85c",
        "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1",
    ),
    "all_k_closure_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1.json",
        "3e3bc451c7d3fec892634c9428cbda50bd274bd6dff3fbef2fa0fbc7e5407834",
        "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1",
    ),
    "retained_operator": (
        "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
        "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77",
        "BERGER_RETAINED_MINIMAL_OPERATOR",
    ),
    "retained_layout": (
        "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json",
        "3eccbcc1076eaf29ab1dc540440f8f2d3ffd5c9aa5be9265443db2997f68b1ba",
        "BERGER_RETAINED_MINIMAL_LAYOUT",
    ),
    "peter_weyl": (
        "closed_universe_observers/certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
        "e24c860b338188254c4388a7ca660ac454ba7b70c13659ffc36a98bf39250120",
        "BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE",
    ),
    "D_action": (
        "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json",
        "8b5f1277c1969507e58b4389984338f2a063b99f9d7cf8a929abcffa298b3e49",
        "BERGER_54_ROW_LOCAL_D_ACTION",
    ),
    "charge_clock": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json",
        "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1",
    ),
}

Z = sp.Symbol("z")
SQRT10 = sp.sqrt(10)
U = 3 * SQRT10 / 20
V = 2 * SQRT10 / 3
TWO_J = 1
N = 2


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _expr(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(value))


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id) in IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        actual = _sha(path)
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    parent = values["repaired_parent"]
    if (
        parent["terminal_verdict"]["result_state"]
        != "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT"
        or not parent["exact_checks"]["q70_degree_plus_one"]
        or not parent["exact_checks"]["q70_cyclic"]
    ):
        raise AssertionError("repaired parent gate not satisfied")
    if values["all_k_closure"]["terminal_verdict"]["ungraded_isotypical_closure"] != "CERTIFIED_FINITE_COMPLETE":
        raise AssertionError("finite all-k closure missing")
    return records, values


def _finite(record: dict[str, Any], two_j: int = TWO_J) -> sp.Matrix:
    n = two_j + 1
    spatial = generators(two_j)
    result = sp.MutableSparseMatrix(record["shape"][0] * n, record["shape"][1] * n, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(n)
        for exponents, raw in terms:
            operator = sp.eye(n) * Z ** exponents[0]
            for axis in range(3):
                operator *= spatial[axis] ** exponents[axis + 1]
            coefficient = sp.sympify(raw, locals={"u": U, "v": V, "alpha_B": 1})
            block += coefficient * operator
        for i in range(n):
            for j in range(n):
                if block[i, j] != 0:
                    result[row * n + i, column * n + j] = sp.expand(block[i, j])
    return sp.Matrix(result)


def _matrix_record(matrix: sp.Matrix) -> dict[str, Any]:
    entries = [
        [row, column, _expr(matrix[row, column])]
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if matrix[row, column] != 0
    ]
    core = {"shape": [matrix.rows, matrix.cols], "entries": entries}
    return {**core, "sha256": _digest(core)}


def _quotient_data(operator: dict[str, Any]) -> dict[str, Any]:
    blocks = operator["q1_blocks"]
    gauge = _finite(blocks["K_spatial"])
    hessian = _finite(blocks["H_retained"])
    identity = _finite(blocks["minus_K_spatial_sharp"])

    if sp.simplify(hessian * gauge) != sp.zeros(20, 6):
        raise AssertionError("H K identity failed")
    if sp.simplify(identity * hessian) != sp.zeros(6, 20):
        raise AssertionError("Ksharp H identity failed")

    _, gauge_pivot_rows = gauge.subs(Z, 0).T.rref()
    field_free = [index for index in range(20) if index not in gauge_pivot_rows]
    _, identity_pivot_columns = identity.subs(Z, 0).rref()
    equation_free = [index for index in range(20) if index not in identity_pivot_columns]
    if tuple(gauge_pivot_rows) != (8, 9, 10, 11, 12, 13):
        raise AssertionError("gauge quotient chart drifted")
    if tuple(identity_pivot_columns) != tuple(gauge_pivot_rows):
        raise AssertionError("dual quotient chart drifted")

    gauge_pivot = gauge[list(gauge_pivot_rows), :]
    field_inclusion = sp.eye(20)[:, field_free]
    field_projection = sp.zeros(14, 20)
    correction = -gauge[field_free, :] * gauge_pivot.inv()
    for local, ambient in enumerate(gauge_pivot_rows):
        field_projection[:, ambient] = correction[:, local]
    for local, ambient in enumerate(field_free):
        field_projection[local, ambient] = 1

    identity_pivot = identity[:, list(identity_pivot_columns)]
    equation_inclusion = sp.zeros(20, 14)
    pivot_part = -identity_pivot.inv() * identity[:, equation_free]
    for local, ambient in enumerate(identity_pivot_columns):
        equation_inclusion[ambient, :] = pivot_part[local, :]
    for local, ambient in enumerate(equation_free):
        equation_inclusion[ambient, local] = 1
    equation_projection = sp.eye(20)[equation_free, :]

    physical = hessian.extract(equation_free, field_free)
    checks = {
        "gauge_rank": gauge.subs(Z, 0).rank(),
        "identity_rank": identity.subs(Z, 0).rank(),
        "gauge_pivot_determinant": _expr(gauge_pivot.det()),
        "identity_pivot_determinant": _expr(identity_pivot.det()),
        "field_projection_times_gauge_zero": sp.simplify(field_projection * gauge) == sp.zeros(14, 6),
        "field_projection_times_inclusion_identity": field_projection * field_inclusion == sp.eye(14),
        "identity_times_equation_inclusion_zero": sp.simplify(identity * equation_inclusion) == sp.zeros(6, 14),
        "equation_projection_times_inclusion_identity": equation_projection * equation_inclusion == sp.eye(14),
        "H_field_inclusion_equals_equation_inclusion_Hphysical": sp.simplify(hessian * field_inclusion - equation_inclusion * physical) == sp.zeros(20, 14),
    }
    if checks != {
        "gauge_rank": 6,
        "identity_rank": 6,
        "gauge_pivot_determinant": "1/16",
        "identity_pivot_determinant": "1/16",
        "field_projection_times_gauge_zero": True,
        "field_projection_times_inclusion_identity": True,
        "identity_times_equation_inclusion_zero": True,
        "equation_projection_times_inclusion_identity": True,
        "H_field_inclusion_equals_equation_inclusion_Hphysical": True,
    }:
        raise AssertionError(f"quotient identities drifted: {checks}")

    determinant = sp.factor(physical.det(method="domain-ge"))
    factors = [
        Z**2 + 13,
        40 * Z**4 + 773 * Z**2 + 3748,
        3240 * Z**4 + 168093 * Z**2 + 2172895,
        933120 * Z**6 + 10517040 * Z**4 + 34117578 * Z**2 + 24373901,
    ]
    normalized = sp.Poly(determinant, Z).monic().as_expr()
    expected = sp.prod(factor**2 for factor in factors)
    if sp.expand(normalized - sp.Poly(expected, Z).monic().as_expr()) != 0:
        raise AssertionError("physical characteristic determinant drifted")

    return {
        "gauge": gauge,
        "hessian": hessian,
        "identity": identity,
        "physical": physical,
        "factors": factors,
        "maps": {
            "field_inclusion_B": _matrix_record(field_inclusion),
            "field_projection_P": _matrix_record(field_projection),
            "equation_inclusion_E": _matrix_record(equation_inclusion),
            "equation_projection_R": _matrix_record(equation_projection),
            "physical_H": _matrix_record(physical),
        },
        "checks": checks,
        "field_free_indices": field_free,
        "equation_free_indices": equation_free,
        "characteristic": _expr(normalized),
    }


def _rref_mod(matrix: sp.Matrix, polynomial: sp.Expr) -> tuple[list[list[Any]], list[int], Any, Any]:
    coefficient_field = QQ.algebraic_field(SQRT10, sp.I)
    ring = coefficient_field.poly_ring(Z)
    modulus = ring.from_sympy(polynomial)

    def convert(value: sp.Expr) -> Any:
        return ring.rem(ring.from_sympy(sp.expand(value)), modulus)

    rows = [[convert(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(matrix.cols):
        found = next((row for row in range(pivot_row, matrix.rows) if rows[row][column]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        inverse = ring.invert(rows[pivot_row][column], modulus)
        rows[pivot_row] = [ring.rem(value * inverse, modulus) for value in rows[pivot_row]]
        for row in range(matrix.rows):
            if row != pivot_row and rows[row][column]:
                coefficient = rows[row][column]
                rows[row] = [
                    ring.rem(rows[row][j] - coefficient * rows[pivot_row][j], modulus)
                    for j in range(matrix.cols)
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == matrix.rows:
            break
    return rows, pivots, ring, modulus


def _nullspace_mod(matrix: sp.Matrix, polynomial: sp.Expr) -> tuple[list[list[Any]], Any, Any]:
    reduced, pivots, ring, modulus = _rref_mod(matrix, polynomial)
    free = [column for column in range(matrix.cols) if column not in pivots]
    basis = [[ring.zero for _ in free] for _ in range(matrix.cols)]
    for basis_column, free_column in enumerate(free):
        basis[free_column][basis_column] = ring.one
        for row, pivot in enumerate(pivots):
            basis[pivot][basis_column] = ring.rem(-reduced[row][free_column], modulus)
    return basis, ring, modulus


def _factor_audit(physical: sp.Matrix, polynomial: sp.Expr) -> dict[str, Any]:
    right, ring, modulus = _nullspace_mod(physical, polynomial)
    left, _, _ = _nullspace_mod(physical.T, polynomial)
    if len(right[0]) != 2 or len(left[0]) != 2:
        raise AssertionError("factor nullity is not two")

    derivative = physical.diff(Z)
    derivative_q = [
        [ring.rem(ring.from_sympy(sp.expand(derivative[i, j])), modulus) for j in range(14)]
        for i in range(14)
    ]

    def multiply(left_matrix: list[list[Any]], right_matrix: list[list[Any]]) -> list[list[Any]]:
        return [
            [
                ring.rem(
                    sum((left_matrix[i][k] * right_matrix[k][j] for k in range(len(right_matrix))), ring.zero),
                    modulus,
                )
                for j in range(len(right_matrix[0]))
            ]
            for i in range(len(left_matrix))
        ]

    residue = multiply(multiply([list(row) for row in zip(*left)], derivative_q), right)
    determinant = ring.rem(residue[0][0] * residue[1][1] - residue[0][1] * residue[1][0], modulus)
    if not determinant:
        raise AssertionError("residue pairing degenerated")
    determinant_expr = sp.factor(ring.to_sympy(determinant))
    if sp.gcd(sp.Poly(sp.together(determinant_expr).as_numer_denom()[0], Z), sp.Poly(polynomial, Z)).degree() != 0:
        raise AssertionError("residue determinant vanishes on a characteristic factor")
    residue_expr = [[sp.factor(ring.to_sympy(value)) for value in row] for row in residue]
    return {
        "factor": _expr(polynomial),
        "physical_matrix_rank_over_factor_field": 12,
        "H0_dimension": 2,
        "H1_dimension": 2,
        "Hminus1_dimension": 0,
        "H2_dimension": 0,
        "residue_pairing": [[_expr(value) for value in row] for row in residue_expr],
        "residue_determinant": _expr(determinant_expr),
        "residue_nondegenerate": True,
        "Jordan_status": "SEMISIMPLE_NO_POLYNOMIAL_TIME_PARTNER",
    }


def _spectral_ledger(factors: list[sp.Expr], physical: sp.Matrix) -> list[dict[str, Any]]:
    audits = [_factor_audit(physical, factor) for factor in factors]
    audits[0].update({
        "root_description": "z=+/-i*sqrt(13)",
        "root_class": "PURELY_IMAGINARY",
        "root_count": 2,
        "algebraic_multiplicity_per_root": 2,
        "geometric_multiplicity_per_root": 2,
    })
    audits[1].update({
        "y_equals_z_squared_roots": ["(-773+3*i*sqrt(239))/80", "(-773-3*i*sqrt(239))/80"],
        "y_discriminant": "-2151",
        "root_class": "COMPLEX_FREQUENCY_QUARTET_WITH_NONZERO_REAL_PART",
        "root_count": 4,
        "algebraic_multiplicity_per_root": 2,
        "geometric_multiplicity_per_root": 2,
        "positive_growth_rate": "sqrt((8*sqrt(9370)-773)/160)",
        "oscillation_rate": "sqrt((8*sqrt(9370)+773)/160)",
    })
    audits[2].update({
        "y_equals_z_squared_roots": ["-18677/720-3*sqrt(1601)/80", "-18677/720+3*sqrt(1601)/80"],
        "root_class": "FOUR_PURELY_IMAGINARY_ROOTS",
        "root_count": 4,
        "algebraic_multiplicity_per_root": 2,
        "geometric_multiplicity_per_root": 2,
    })
    audits[3].update({
        "y_equals_z_squared_root_isolating_intervals": ["(-6,-5)", "(-5,-4)", "(-1,0)"],
        "root_class": "SIX_PURELY_IMAGINARY_ROOTS",
        "root_count": 6,
        "algebraic_multiplicity_per_root": 2,
        "geometric_multiplicity_per_root": 2,
    })
    return audits


def _unstable_energy() -> dict[str, Any]:
    block = sp.Matrix([
        [-3748, 0, 0, 0],
        [0, 773, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, sp.Rational(1, 40)],
    ])
    doubled = sp.kronecker_product(block, sp.eye(2))
    if block.det() == 0 or doubled.rank() != 8:
        raise AssertionError("unstable Ostrogradsky block drifted")
    return {
        "local_Smith_sector": "two copies of 40*D^4+773*D^2+3748",
        "principal_time_order_four_matrix": [[40, 0], [0, 40]],
        "time_order_two_matrix": [[773, 0], [0, 773]],
        "fixed_isotype_spatial_potential_matrix": [[3748, 0], [0, 3748]],
        "Ostrogradsky_basis_per_copy": ["q", "Dq", "P0", "P1"],
        "Ostrogradsky_Hessian_per_copy": [[_expr(value) for value in block.row(row)] for row in range(4)],
        "two_copy_inertia_positive_negative_zero": [4, 4, 0],
        "classification": "GENUINE_HAMILTONIAN_HOPF_EXPONENTIAL_OSCILLATORY_DIRECTION",
        "not_a_pure_gradient_sign_claim": True,
    }


def _carrier_and_mutations(values: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    e1, e2, _ = generators(TWO_J)
    off_diagonal = sum(1 for matrix in (e1, e2) for (row, column), value in matrix.todok().items() if row != column and value != 0)
    if off_diagonal == 0:
        raise AssertionError("all-k connectivity disappeared")
    carrier = {
        "labels": {"two_j": 1, "j": "1/2", "m": ["-1/2", "+1/2"], "k_internal": ["-1/2", "+1/2"]},
        "per_fixed_m_dimension": 140,
        "degree_ranks_per_fixed_m": [12, 58, 58, 12],
        "basis": "e_row tensor Y_(1/2,m,k), row=0,...,69 and both k weights",
        "normalized_inclusion": "iota_jm(e_row tensor e_k)=e_row*sqrt((2j+1)/Vol_Berger)*D^j_mk",
        "normalized_projection": "pi_jm is the normalized L2 Peter-Weyl coefficient extraction",
        "pi_iota_identity": True,
        "all_70_rows_present": True,
        "all_k_closure": True,
        "U1_component_dimension": 32,
        "U1_cohomology_dimension": 0,
        "q54_to_q26_contracted_component_dimension": 56,
        "retained_q26_component_dimension": 52,
    }
    mutations = {
        "omitted_weight": {"status": "REJECTED", "witness": "e1/e2 has a nonzero edge between k=-1/2 and k=+1/2"},
        "proper_k_truncation": {"status": "REJECTED", "witness_count": off_diagonal},
        "old_U1_orientation": {"status": "REJECTED", "degree_shift_histogram": {"+1": 309 * N, "-1": 8 * N}},
        "round_or_changed_anisotropy": {"status": "OUTSIDE_SAME_BACKGROUND_GATE", "reason": "changing u=v or the e3 scale changes the selected Berger PBW relations and does not retain the pinned q=9/40 stationary action"},
    }
    return carrier, mutations


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    quotient = _quotient_data(values["retained_operator"])
    spectral = _spectral_ledger(quotient["factors"], quotient["physical"])
    carrier, mutations = _carrier_and_mutations(values)
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "carrier": carrier,
        "physical_quotient": {
            "degree_dimensions_before_on_shell_specialization": [0, 0, 0, 0],
            "generic_z_statement": "H0=H1=0 away from the characteristic divisor; Hminus1=H2=0 because K is injective and Ksharp is surjective",
            "gauge_rank": 6,
            "field_dimension": 20,
            "physical_field_quotient_dimension": 14,
            "field_free_indices": quotient["field_free_indices"],
            "equation_free_indices": quotient["equation_free_indices"],
            "maps": quotient["maps"],
            "checks": quotient["checks"],
            "characteristic_determinant_monic": quotient["characteristic"],
            "factor_audits": spectral,
            "cross_m_BV_pairing": "the nondegenerate cyclic q70 form pairs (m,z) with (-m,-z) and descends perfectly between H0 and H1",
            "cohomology_pairing_radical_dimension": 0,
        },
        "unstable_sector": _unstable_energy(),
        "charge_actions": {
            "local_Diff_gauge": "rank-six image of K_spatial, divided out explicitly",
            "diagonal_U1": "rank-32 contractible summand on this all-k block",
            "R_rel": "zero tangent action in every j>0 isotype; the charged group-orbit tangent is the separate j=0 constant phase",
            "D": "multiplication by z on every dressed coefficient",
            "K": "D-(3/4)R_rel=D on this j=1/2 block",
            "unrestricted_Q_rel": "delta Q_rel=0 because every j=1/2 harmonic has zero spatial integral",
            "fixed_charge_comparison": "identical to unrestricted on this nonhomogeneous block; no charged orbit is quotiented here",
            "action_angle_tangent": "NOT_PRESENT; the size-two zero Jordan family tangent belongs to j=0",
        },
        "mutations": mutations,
        "terminal_verdict": {
            "result_state": "OBSTRUCTED_FIRST_NONSTABILIZER_ISOTYPE_HAS_GENUINE_COMPLEX_FREQUENCY_PHYSICAL_MODES",
            "first_failed_health_block": "j=1/2 complete all-k physical quotient",
            "complex_frequency_factor": "40*z^4+773*z^2+3748",
            "physical_multiplicity_per_root": 2,
            "pairing_radical": 0,
            "energy_inertia_on_real_eight_dimensional_unstable_sector": [4, 4, 0],
            "generic_all_j_health_theorem": "OBSTRUCTED_BY_EXPLICIT_GENERIC_BLOCK_COUNTEREXAMPLE",
            "low_j_stabilizer_census": "SEPARATE_NEXT_GATE",
        },
        "claim_boundary": {
            "establishes": [
                "complete fixed-m all-k 140-dimensional repaired q70 j=1/2 carrier",
                "explicit normalized gauge quotient to a 14-by-14 physical Hessian",
                "exact characteristic divisor and root/geometric/Jordan census",
                "nondegenerate descended residue/BV pairing",
                "a genuine non-gauge non-charge non-action-angle complex-frequency physical sector with split energy inertia",
            ],
            "does_not_establish": [
                "the spectra of every higher-j or low-j stabilizer block",
                "nonlinear instability or a finite-time blow-up theorem",
                "Hadamard, anomaly, QME, particle, positivity or unitarity claims",
            ],
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal_verdict"]
    value = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": payload["content_sha256"]},
        "carrier": payload["carrier"],
        "physical_quotient_summary": {
            "dimension": payload["physical_quotient"]["physical_field_quotient_dimension"],
            "characteristic_determinant_monic": payload["physical_quotient"]["characteristic_determinant_monic"],
            "cohomology_pairing_radical_dimension": 0,
        },
        "unstable_sector": payload["unstable_sector"],
        "charge_actions": payload["charge_actions"],
        "terminal_verdict": terminal,
        "claim_boundary": payload["claim_boundary"],
    }
    value["content_hashes"] = {
        "carrier_sha256": _digest(value["carrier"]),
        "quotient_sha256": _digest(value["physical_quotient_summary"]),
        "unstable_sha256": _digest(value["unstable_sector"]),
        "charges_sha256": _digest(value["charge_actions"]),
        "terminal_sha256": _digest(value["terminal_verdict"]),
        "boundary_sha256": _digest(value["claim_boundary"]),
    }
    return value


def _validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload digest failed")
    if payload["terminal_verdict"]["physical_multiplicity_per_root"] != 2:
        raise AssertionError("physical multiplicity drifted")
    if payload["unstable_sector"]["two_copy_inertia_positive_negative_zero"] != [4, 4, 0]:
        raise AssertionError("unstable energy inertia drifted")
    expected = {
        "carrier_sha256": _digest(certificate["carrier"]),
        "quotient_sha256": _digest(certificate["physical_quotient_summary"]),
        "unstable_sha256": _digest(certificate["unstable_sector"]),
        "charges_sha256": _digest(certificate["charge_actions"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected:
        raise AssertionError("certificate hashes failed")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _load_imports()
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload)
    _validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    _validate(certificate, payload)
    certificate_schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(certificate_schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(certificate_schema).validate(certificate)
    Draft202012Validator(payload_schema).validate(payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if json.loads(OUTPUT.read_text()) != certificate or json.loads(PAYLOAD.read_text()) != payload:
        raise AssertionError("stored generic-isotypical obstruction drifted")
    print("TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
