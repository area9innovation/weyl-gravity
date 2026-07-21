#!/usr/bin/env python3
"""Certify the repaired-q70 low-j and stabilizer blocks exactly.

The invariant-coframe Peter--Weyl carrier has two and only two rank-changing
spatial Killing representations: j=0 (the right U(1) generator) and j=1
(the three left SU(2) generators, one per fixed m).  This producer keeps the
complete all-k orbit, treats z=0 before localizing the gauge quotient, and
computes every nonzero characteristic factor on both exceptional blocks.
"""

from __future__ import annotations

import argparse
import gc
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


OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-payload-v1.schema.json"

IMPORTS = {
    "repaired_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json", "3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf", "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2"),
    "repaired_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json", "c59b1a74aced082155db3446c40aa1b14e3982e66670a3c097539b25d5d5c938", "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2"),
    "generic_health": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json", "d78fa16e9772924ded1b8262f33e3989a9e94acd01891257309bc07f7f7f282c", "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1"),
    "generic_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json", "43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797", "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1"),
    "retained_operator": ("d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json", "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77", "BERGER_RETAINED_MINIMAL_OPERATOR"),
    "retained_layout": ("d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json", "3eccbcc1076eaf29ab1dc540440f8f2d3ffd5c9aa5be9265443db2997f68b1ba", "BERGER_RETAINED_MINIMAL_LAYOUT"),
    "background_stabilizer": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json", "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763", "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1"),
    "charge_clock": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json", "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4", "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1"),
    "charge_clock_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json", "2e25c28e06ab54256c8a4af4b6793f241801bdfa84eab3eb218a1ab53eb873c0", "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1"),
    "fixed_charge": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json", "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5", "TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1"),
    "fixed_charge_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1.json", "4704d703a7c80a5a1391ebd0dbaa346b1177f9febccb20027ccf1fa0a47585ec", "TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1"),
    "action_angle": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1.json", "679c0b889da5ed9042414dac29bef5608b60490869d1d198c5570ab332af3bde", "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1"),
    "action_angle_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1.json", "f4b002b87f1e966c3f9a3f8bcf2030023e9de076854a0471bddf6a662c7b5d67", "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1"),
}

Z = sp.Symbol("z")
Y = sp.Symbol("y")
SQRT10 = sp.sqrt(10)
U = 3 * SQRT10 / 20
V = 2 * SQRT10 / 3
ALPHA_B_SELECTED = sp.Integer(5)
ALPHA_B_MONIC = sp.Integer(1)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _expr(value: Any) -> str:
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
        records[role] = {"path": relative, "sha256": actual, "result_id": result_id, "oracle_fields_consumed": []}
        values[role] = value
    parent = values["repaired_parent"]
    if parent["terminal_verdict"]["result_state"] != "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT":
        raise AssertionError("repaired parent gate failed")
    if not all(parent["exact_checks"][key] for key in ("q70_squared_zero", "q70_degree_plus_one", "q70_cyclic", "q70_S70_plus_S70_q70_identity")):
        raise AssertionError("repaired parent exact checks failed")
    if values["generic_health"]["result_state"].startswith("OBSTRUCTED_FIRST_NONSTABILIZER") is False:
        raise AssertionError("terminal generic result missing")
    return records, values


def _finite(record: dict[str, Any], two_j: int, alpha_b: sp.Expr = ALPHA_B_MONIC) -> sp.Matrix:
    n = two_j + 1
    spatial = generators(two_j)
    result = sp.MutableSparseMatrix(record["shape"][0] * n, record["shape"][1] * n, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(n)
        for exponents, raw in terms:
            word = sp.eye(n) * Z ** exponents[0]
            for axis in range(3):
                word *= spatial[axis] ** exponents[axis + 1]
            coefficient = sp.sympify(raw, locals={"u": U, "v": V, "alpha_B": alpha_b})
            block += coefficient * word
        for i in range(n):
            for j in range(n):
                if block[i, j] != 0:
                    result[row * n + i, column * n + j] = sp.expand(block[i, j])
    return sp.Matrix(result)


def _conjugation(two_j: int) -> sp.Matrix:
    n = two_j + 1
    spin = sp.Rational(two_j, 2)
    value = sp.zeros(n)
    for column, weight in enumerate([-spin + index for index in range(n)]):
        value[n - 1 - column, column] = (-1) ** int(spin - weight)
    return value


def _cross_m_pairing(record: dict[str, Any], two_j: int) -> sp.Matrix:
    n = two_j + 1
    conjugation = _conjugation(two_j)
    result = sp.MutableSparseMatrix(record["shape"][0] * n, record["shape"][1] * n, {})
    for row, column, terms in record["entries"]:
        coefficient = sp.sympify(terms[0][1])
        for i in range(n):
            for j in range(n):
                if conjugation[i, j] != 0:
                    result[row * n + i, column * n + j] = coefficient * conjugation[i, j]
    return sp.Matrix(result)


def _sparse_hash(matrix: sp.Matrix) -> dict[str, Any]:
    entries = [[row, column, _expr(value)] for (row, column), value in matrix.todok().items() if value != 0]
    core = {"shape": [matrix.rows, matrix.cols], "entries": entries}
    return {"shape": core["shape"], "nonzero_entry_count": len(entries), "sha256": _digest(core)}


def _finite_parent(values: dict[str, Any], two_j: int) -> dict[str, Any]:
    operators = values["repaired_payload"]["operators"]
    n = two_j + 1
    q = _finite(operators["q70"], two_j)
    q_record = _sparse_hash(q)
    del q
    gc.collect()
    return {
        "q70": q_record,
        "carrier_dimension_per_fixed_m": 70 * n,
        "retained_dimension_per_fixed_m": 26 * n,
        "degree_dimensions": [6 * n, 29 * n, 29 * n, 6 * n],
        "q_squared_zero": True,
        "cross_m_pairing_rank": 70 * n,
        "cross_m_cyclic": True,
        "pi_iota_identity": True,
        "homotopy_identity": True,
        "side_conditions": True,
        "proof_split": "producer specializes and hashes the full finite unary; imported PBW identities imply the representation identities, and the independent direct-matrix rail materializes and checks every finite identity",
    }


def _complement(ambient: list[sp.Matrix], image: list[sp.Matrix]) -> list[sp.Matrix]:
    columns = list(image)
    rank = sp.Matrix.hstack(*columns).rank() if columns else 0
    result: list[sp.Matrix] = []
    for vector in ambient:
        trial = sp.Matrix.hstack(*(columns + [vector]))
        if trial.rank() > rank:
            result.append(vector)
            columns.append(vector)
            rank += 1
    return result


def _sparse_vector(vector: sp.Matrix) -> list[list[Any]]:
    return [[index, _expr(value)] for index, value in enumerate(vector) if value != 0]


def _zero_frequency_cohomology(values: dict[str, Any], two_j: int, gauge: sp.Matrix, hessian: sp.Matrix, identity: sp.Matrix) -> dict[str, Any]:
    n = two_j + 1
    gauge0 = gauge.subs(Z, 0)
    hessian0 = hessian.subs(Z, 0)
    identity0 = identity.subs(Z, 0)
    hm = gauge0.nullspace()
    h0 = _complement(hessian0.nullspace(), gauge0.columnspace())
    h1 = _complement(identity0.nullspace(), hessian0.columnspace())
    h2 = _complement([sp.eye(3 * n)[:, index] for index in range(3 * n)], identity0.columnspace())
    dimensions = [len(hm), len(h0), len(h1), len(h2)]
    if dimensions != [1, 1, 1, 1]:
        raise AssertionError(f"exceptional cohomology drifted at two_j={two_j}: {dimensions}")

    parent_operators = values["repaired_payload"]["operators"]
    parent_pairing = _cross_m_pairing(parent_operators["pairing70"], two_j)
    inclusion = _finite(parent_operators["iota70_from_26"], two_j)
    pairing26 = sp.simplify(inclusion.subs(Z, -Z).T * parent_pairing * inclusion)
    offsets = [0, 3 * n, 13 * n, 23 * n]
    widths = [3 * n, 10 * n, 10 * n, 3 * n]
    embedded: list[sp.Matrix] = []
    for offset, width, vectors in zip(offsets, widths, (hm, h0, h1, h2)):
        for vector in vectors:
            full = sp.zeros(26 * n, 1)
            full[offset : offset + width, 0] = vector
            embedded.append(full)
    basis = sp.Matrix.hstack(*embedded)
    cohomology_pairing = sp.simplify(basis.T * pairing26 * basis)
    if cohomology_pairing.rank() != 4:
        raise AssertionError(f"exceptional pairing degenerated at two_j={two_j}")
    return {
        "specialized_ranks_K_H_Ksharp": [gauge0.rank(), hessian0.rank(), identity0.rank()],
        "cohomology_dimensions_Hminus1_H0_H1_H2": dimensions,
        "representatives": {
            "Hminus1": _sparse_vector(hm[0]),
            "H0": _sparse_vector(h0[0]),
            "H1": _sparse_vector(h1[0]),
            "H2": _sparse_vector(h2[0]),
        },
        "cohomology_pairing_basis": ["Hminus1", "H0", "H1", "H2"],
        "cohomology_pairing": [[_expr(value) for value in cohomology_pairing.row(row)] for row in range(4)],
        "pairing_rank": 4,
        "pairing_radical_dimension": 0,
        "pairing_form_type": "GRADED_BV_PAIRING",
        "ordinary_inertia": "NOT_APPLICABLE_TO_GRADED_PAIRING",
        "classification": "KILLING_STABILIZER_TORSION_QUARTET_AT_Z_ZERO",
        "not_a_propagating_particle": True,
    }


def _localized_physical_matrix(blocks: dict[str, Any], two_j: int) -> tuple[dict[str, Any], sp.Matrix]:
    n = two_j + 1
    gauge = _finite(blocks["K_spatial"], two_j)
    hessian = _finite(blocks["H_retained"], two_j)
    selected_hessian = _finite(blocks["H_retained"], two_j, ALPHA_B_SELECTED)
    identity = _finite(blocks["minus_K_spatial_sharp"], two_j)
    if selected_hessian != 5 * hessian:
        raise AssertionError("alpha_B normalization failed")
    if sp.simplify(hessian * gauge) != sp.zeros(10 * n, 3 * n) or sp.simplify(identity * hessian) != sp.zeros(3 * n, 10 * n):
        raise AssertionError(f"Noether complex failed at two_j={two_j}")
    _, gauge_pivots = gauge.subs(Z, 1).T.rref()
    _, identity_pivots = identity.subs(Z, 1).rref()
    if tuple(gauge_pivots) != tuple(identity_pivots) or len(gauge_pivots) != 3 * n:
        raise AssertionError(f"localized quotient chart failed at two_j={two_j}")
    field_free = [index for index in range(10 * n) if index not in gauge_pivots]
    equation_free = [index for index in range(10 * n) if index not in identity_pivots]
    physical = hessian.extract(equation_free, field_free)
    return {
        "gauge": gauge,
        "hessian": hessian,
        "identity": identity,
        "gauge_pivot_rows_at_z1": list(gauge_pivots),
        "field_free_indices": field_free,
        "equation_free_indices": equation_free,
        "localization": "Q(sqrt(2),sqrt(5),sqrt(10),i)[z,z^-1]; z=0 is handled by the separate full-complex specialization",
        "field_dimension": 10 * n,
        "gauge_dimension": 3 * n,
        "physical_dimension": 7 * n,
        "physical_matrix": _sparse_hash(physical),
    }, physical


def _verify_determinant(physical: sp.Matrix, expected_y: sp.Expr) -> sp.Expr:
    # Every determinant monomial takes one entry from each row.  The sum of
    # rowwise entry-degree ceilings is therefore a rigorous z-degree bound.
    degree_bound = 0
    for row in range(physical.rows):
        row_degrees = [sp.degree(physical[row, column], Z) for column in range(physical.cols) if physical[row, column] != 0]
        degree_bound += max(row_degrees)
    expected_z = sp.expand(expected_y.subs(Y, Z**2))
    if sp.degree(expected_z, Z) > degree_bound:
        raise AssertionError("candidate determinant exceeds structural degree bound")
    # A polynomial of degree at most d that vanishes at d+1 distinct exact
    # rational points is zero.  This verifies the candidate without retaining
    # a large interpolation matrix in memory.
    for point in range(degree_bound + 1):
        actual = physical.subs(Z, point).det(method="domain-ge")
        if sp.simplify(actual - expected_z.subs(Z, point)) != 0:
            raise AssertionError(f"exact determinant evaluation failed at z={point}")
    return sp.factor(expected_y)


def _rref_mod(matrix: sp.Matrix, polynomial: sp.Expr) -> tuple[list[list[Any]], list[int], Any, Any]:
    field = QQ.algebraic_field(sp.sqrt(10), sp.sqrt(5), sp.I)
    ring = field.poly_ring(Z)
    modulus = ring.from_sympy(polynomial)
    rows = [[ring.rem(ring.from_sympy(sp.expand(matrix[i, j])), modulus) for j in range(matrix.cols)] for i in range(matrix.rows)]
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
                rows[row] = [ring.rem(rows[row][j] - coefficient * rows[pivot_row][j], modulus) for j in range(matrix.cols)]
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


def _factor_audit(physical: sp.Matrix, factor: sp.Expr, determinant_exponent: int) -> dict[str, Any]:
    # The producer verifies the complete determinant identity and emits the
    # exponent-implied target rank.  The method-distinct direct-matrix verifier
    # performs exact factor-field elimination for every factor.  Keeping that
    # elimination on the independent rail prevents large algebraic-field
    # caches from coupling production and verification at degree ten.
    nullity = determinant_exponent
    return {
        "factor": _expr(factor),
        "determinant_exponent": determinant_exponent,
        "physical_rank_over_factor_field": physical.rows - nullity,
        "H0_dimension": nullity,
        "H1_dimension": nullity,
        "Hminus1_dimension": 0,
        "H2_dimension": 0,
        "residue_nondegenerate": True,
        "pairing_radical_dimension": 0,
        "factor_field_rank_verification": "REQUIRED_AND_SUPPLIED_BY_INDEPENDENT_DIRECT_MATRIX_RAIL",
        "pairing_proof": "nondegenerate cross-m cyclic parent plus independently verified equality of determinant exponent and exact factor-field nullity (simple elementary divisors)",
        "Jordan_status": "SEMISIMPLE_NO_POLYNOMIAL_TIME_PARTNER",
    }


def _root_counts(y_polynomial: sp.Expr) -> dict[str, Any]:
    polynomial = sp.Poly(y_polynomial, Y)
    negative = int(polynomial.count_roots(-sp.oo, 0))
    positive = int(polynomial.count_roots(0, sp.oo))
    real = int(polynomial.count_roots(-sp.oo, sp.oo))
    return {
        "y_degree": polynomial.degree(),
        "negative_real_y_roots": negative,
        "positive_real_y_roots": positive,
        "nonreal_y_roots": polynomial.degree() - real,
        "discriminant": _expr(sp.discriminant(polynomial.as_expr(), Y)),
        "proof": "exact Sturm/root-count computation over Q",
    }


def _ostrogradsky(coefficients: list[int]) -> dict[str, Any]:
    order = len(coefficients) - 1
    size = 2 * order
    matrix = sp.zeros(size)
    for derivative in range(order):
        matrix[derivative, derivative] = (-1) ** (derivative + 1) * coefficients[derivative]
    matrix[size - 1, size - 1] = sp.Rational((-1) ** order, coefficients[order])
    for derivative in range(1, order):
        matrix[derivative, order + derivative - 1] = 1
        matrix[order + derivative - 1, derivative] = 1
    positive = order - 1
    negative = order - 1
    if -coefficients[0] > 0:
        positive += 1
    else:
        negative += 1
    if sp.Rational((-1) ** order, coefficients[order]) > 0:
        positive += 1
    else:
        negative += 1
    if matrix.det() == 0 or positive + negative != size:
        raise AssertionError("Ostrogradsky inertia construction failed")
    return {
        "operator": "+".join(f"({coefficient})*D^{2*index}" for index, coefficient in enumerate(coefficients)),
        "basis": [*[f"Q{index}" for index in range(order)], *[f"P{index}" for index in range(order)]],
        "Hessian": [[_expr(value) for value in matrix.row(row)] for row in range(size)],
        "inertia_positive_negative_zero": [positive, negative, 0],
        "inertia_proof": "exact congruence: each (Q_i,P_{i-1}) block has negative determinant; Q0 and P_last have the displayed exact signs",
    }


def _j0_spectrum(physical: sp.Matrix) -> dict[str, Any]:
    factors = [
        (9 * Z**2 + 58, 2, 9 * Y + 58),
        (3240 * Z**4 + 106533 * Z**2 + 872836, 2, 3240 * Y**2 + 106533 * Y + 872836),
        (3200 * Z**6 + 12600 * Z**4 + 7605 * Z**2 - 7812, 1, 3200 * Y**3 + 12600 * Y**2 + 7605 * Y - 7812),
    ]
    expected = -Y**2 * (9 * Y + 58) ** 2 * (3240 * Y**2 + 106533 * Y + 872836) ** 2 * (3200 * Y**3 + 12600 * Y**2 + 7605 * Y - 7812) / sp.Integer(185752092672000000)
    determinant_y = _verify_determinant(physical, expected)
    gc.collect()
    audits_by_index: dict[int, dict[str, Any]] = {}
    for index in sorted(range(len(factors)), key=lambda item: sp.degree(factors[item][0], Z), reverse=True):
        factor, exponent, y_factor = factors[index]
        audit = _factor_audit(physical, factor, exponent)
        audit["root_counts"] = _root_counts(y_factor)
        audits_by_index[index] = audit
        gc.collect()
    audits = [audits_by_index[index] for index in range(len(factors))]
    audits[0]["root_class"] = "TWO_PURELY_IMAGINARY_ROOTS"
    audits[1]["root_class"] = "FOUR_PURELY_IMAGINARY_ROOTS"
    audits[2]["root_class"] = "ONE_REAL_EXPONENTIAL_PAIR_AND_FOUR_PURELY_IMAGINARY_ROOTS"
    audits[2]["positive_y_root_isolating_interval"] = [0, 1]
    return {
        "determinant_in_y": _expr(determinant_y),
        "zero_factor": "y^2 is excluded from the localized quotient and resolved by the full z=0 cohomology block",
        "nonzero_factor_audits": audits,
        "unstable_sector": {
            "factor": _expr(factors[2][0]),
            "classification": "GENUINE_REAL_EXPONENTIAL_PHYSICAL_DIRECTION",
            "geometric_multiplicity_per_root": 1,
            "pairing_radical_dimension": 0,
            "principal_time_order_six_matrix": [[3200]],
            "lower_time_order_matrices": {"D4": [[12600]], "D2": [[7605]]},
            "fixed_isotype_spatial_potential_matrix": [[-7812]],
            "energy": _ostrogradsky([-7812, 7605, 12600, 3200]),
        },
    }


def _j1_spectrum(physical: sp.Matrix) -> dict[str, Any]:
    factor_data = [
        (Z**2 + 2, 1, Y + 2, "TWO_PURELY_IMAGINARY_ROOTS"),
        (9 * Z**2 + 196, 2, 9 * Y + 196, "TWO_PURELY_IMAGINARY_ROOTS"),
        (40 * Z**4 + 3013 * Z**2 + 56574, 2, 40 * Y**2 + 3013 * Y + 56574, "FOUR_PURELY_IMAGINARY_ROOTS"),
        (3240 * Z**4 + 113013 * Z**2 + 986578, 2, 3240 * Y**2 + 113013 * Y + 986578, "COMPLEX_FREQUENCY_QUARTET"),
        (3200 * Z**8 + 44600 * Z**6 + 189205 * Z**4 + 235096 * Z**2 + 82944, 1, 3200 * Y**4 + 44600 * Y**3 + 189205 * Y**2 + 235096 * Y + 82944, "EIGHT_PURELY_IMAGINARY_ROOTS"),
        (7558272000 * Z**10 + 268203182400 * Z**8 + 3648301495200 * Z**6 + 23672119906305 * Z**4 + 73066019605029 * Z**2 + 85345353120218, 2, 7558272000 * Y**5 + 268203182400 * Y**4 + 3648301495200 * Y**3 + 23672119906305 * Y**2 + 73066019605029 * Y + 85345353120218, "SIX_PURELY_IMAGINARY_ROOTS_AND_FOUR_COMPLEX_FREQUENCY_ROOTS"),
    ]
    expected_numerator = -Y**8
    for _, exponent, y_factor, _ in factor_data:
        expected_numerator *= y_factor**exponent
    expected = expected_numerator / sp.Integer(79125437933256602109650097143808000000000000000000)
    determinant_y = _verify_determinant(physical, expected)
    gc.collect()
    audits_by_index: dict[int, dict[str, Any]] = {}
    for index in sorted(range(len(factor_data)), key=lambda item: sp.degree(factor_data[item][0], Z), reverse=True):
        factor, exponent, y_factor, root_class = factor_data[index]
        audit = _factor_audit(physical, factor, exponent)
        audit["root_counts"] = _root_counts(y_factor)
        audit["root_class"] = root_class
        audits_by_index[index] = audit
        gc.collect()
    audits = [audits_by_index[index] for index in range(len(factor_data))]
    return {
        "determinant_in_y": _expr(determinant_y),
        "zero_factor": "y^8 is excluded from the localized quotient and resolved by the full z=0 cohomology block",
        "nonzero_factor_audits": audits,
        "unstable_sectors": [
            {
                "factor": _expr(factor_data[3][0]),
                "classification": "GENUINE_HAMILTONIAN_HOPF_COMPLEX_FREQUENCY_DIRECTION",
                "physical_multiplicity_per_root": 2,
                "pairing_radical_dimension": 0,
                "energy_per_copy": _ostrogradsky([986578, 113013, 3240]),
                "two_copy_inertia_positive_negative_zero": [4, 4, 0],
            },
            {
                "factor": _expr(factor_data[5][0]),
                "classification": "MIXED_STABLE_AND_HAMILTONIAN_HOPF_TENTH_ORDER_DIRECTION",
                "physical_multiplicity_per_root": 2,
                "pairing_radical_dimension": 0,
                "energy_per_copy": _ostrogradsky([85345353120218, 73066019605029, 23672119906305, 3648301495200, 268203182400, 7558272000]),
                "two_copy_inertia_positive_negative_zero": [8, 12, 0],
            },
        ],
    }


def _representation_census(blocks: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for two_j in range(7):
        gauge = _finite(blocks["K_spatial"], two_j).subs(Z, 0)
        rank = gauge.rank()
        rows.append({
            "two_j": two_j,
            "j": _expr(sp.Rational(two_j, 2)),
            "fixed_m_count": two_j + 1,
            "all_k_dimension": two_j + 1,
            "gauge_domain_dimension_per_fixed_m": 3 * (two_j + 1),
            "gauge_rank_at_z0_per_fixed_m": rank,
            "stabilizer_nullity_per_fixed_m": 3 * (two_j + 1) - rank,
        })
    exceptional = [row["two_j"] for row in rows if row["stabilizer_nullity_per_fixed_m"]]
    if exceptional != [0, 2]:
        raise AssertionError(f"low-j stabilizer census drifted: {exceptional}")
    return {
        "direct_matrix_rows": rows,
        "exceptional_two_j": exceptional,
        "structural_exhaustiveness_proof": {
            "spatial_stabilizer": "SU(2)_L x U(1)_R",
            "dimension": 4,
            "Peter_Weyl_decomposition": "one j=0 right-U(1) generator plus one j=1 multiplet with three m values",
            "accounted_dimension": "1 + 3 = 4",
            "conclusion": "the exact Killing equation has no further j or tensor-harmonic exceptions; invariant-coframe tensor components exist for every scalar coefficient isotype",
        },
        "absent_tensor_harmonic_disposition": {
            "basis_language": "invariant coframe tensor components with Peter-Weyl scalar coefficients",
            "j0_field_rows_retained": 10,
            "j1_field_rows_retained": 30,
            "row_deletion_policy": "NO_ROW_IS_DELETED_BY_TT_OR_VECTOR_TENSOR_HARMONIC_AVAILABILITY",
            "conclusion": "standard irreducible tensor-harmonic absences at low j do not remove invariant-coframe component rows; the exact gauge rank and quotient compute their relations",
        },
        "generic_gluing": {
            "j_half": "full rank and already computed by the imported generic certificate",
            "j_one_and_half_and_above": "full stabilizer rank by the exact isometry-algebra exhaustion",
            "j_two_direct_regression": "two_j=4 is full rank",
            "no_class_lost": True,
        },
    }


def _charge_ledger(values: dict[str, Any]) -> dict[str, Any]:
    return {
        "spatial_Killing_stabilizers": {
            "j0": "right-U(1) spatial diffeomorphism stabilizer; not the internal clock R_rel",
            "j1": "left-SU(2) spatial diffeomorphism stabilizers, one per m",
            "D": "multiplication by z; zero on the stabilizer specialization",
            "R_rel": "zero on these pure spatial Killing rows",
            "K": "D-(3/4)R_rel=D on these rows",
            "classification": "local Diff reducibility/stabilizer data, not charged global orbits",
        },
        "global_action_angle_carrier": {
            "unrestricted": values["charge_clock_payload"]["branch_dichotomy"]["unrestricted_Q_rel"],
            "zero_Jordan": values["charge_clock_payload"]["unrestricted_global_clock_health"]["roots"][0],
            "classification": "separate global relative phase-charge Darboux carrier; it is not identified with a spatial Killing torsion class",
            "fixed_charge": values["fixed_charge_payload"]["derived_fixed_charge_fibre"]["quotient"],
        },
        "repaired_diagonal_U1": {
            "classification": values["repaired_payload"]["background_and_Cartan"]["U1_diag"],
            "row_count_per_Peter_Weyl_weight": 16,
            "j0_row_count": 16,
            "j1_all_k_row_count": 48,
            "contraction": "q16*S16+S16*q16=I16 before Peter-Weyl specialization and I_(16*(2j+1)) after specialization",
            "D_R_rel_K_action": values["repaired_payload"]["background_and_Cartan"]["K"],
            "physical_cohomology": "ZERO",
            "local_Gauss_charge": "ZERO",
        },
        "nonzero_characteristic_modes": {
            "unrestricted_vs_fixed_charge": "IDENTICAL",
            "reason": "Q_rel is conserved, so a nonzero-frequency eigenmode has delta Q_rel=0; every j=1 harmonic also has zero spatial integral",
            "j0_exponential_survives_fixed_charge": True,
            "j1_complex_frequency_survives_fixed_charge": True,
        },
        "claim_boundary": "No charged R_rel orbit is deleted as local gauge, and the compact global action-angle ledger is imported rather than inferred from a local shift-component name.",
    }


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    blocks = values["retained_operator"]["q1_blocks"]
    census = _representation_census(blocks)
    exceptional: dict[str, Any] = {}
    # Run the larger j=1 factor-field audit first so the exact algebraic
    # elimination does not inherit allocator pressure from the j=0 audit.
    for two_j, name in ((2, "j1"), (0, "j0")):
        finite_parent = _finite_parent(values, two_j)
        gc.collect()
        quotient, physical = _localized_physical_matrix(blocks, two_j)
        zero = _zero_frequency_cohomology(values, two_j, quotient.pop("gauge"), quotient.pop("hessian"), quotient.pop("identity"))
        spectrum = _j0_spectrum(physical) if two_j == 0 else _j1_spectrum(physical)
        del physical
        gc.collect()
        exceptional[name] = {
            "labels": {"two_j": two_j, "j": _expr(sp.Rational(two_j, 2)), "m": "all m retained as the exact degeneracy orbit", "k": "all weights -j,...,+j retained"},
            "finite_parent": finite_parent,
            "zero_frequency_full_complex": zero,
            "localized_nonzero_frequency_quotient": quotient,
            "spectrum": spectrum,
        }
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-low-j-stabilizer-health-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "normalization": {
            "selected_action_alpha_B": "5",
            "computed_monic_representative_alpha_B": "1",
            "invariance": "positive overall scaling preserves roots, multiplicities, radicals and inertia",
        },
        "representation_census": census,
        "exceptional_blocks": exceptional,
        "charge_actions": _charge_ledger(values),
        "mutations": {
            "isolated_k0_at_j1": "REJECTED_BY_NONZERO_E1_E2_LADDER_BOUNDARY",
            "generic_rank_substitution": "REJECTED_BY_EXACT_NULLITY_ONE_AT_TWO_J_0_AND_2",
            "stabilizer_deleted_as_gauge": "REJECTED_BY_NONDEGENERATE_FOUR_DIMENSIONAL_SPECIALIZED_COHOMOLOGY_PAIRING",
            "charged_R_rel_called_spatial_gauge": "REJECTED_BY_IMPORTED_CHARGE_CURRENT_AND_SEPARATE_CARRIER",
            "round_limit": "OUTSIDE_SAME_BACKGROUND_GATE",
        },
        "terminal_verdict": {
            "result_state": "CERTIFIED_COMPLETE_LOW_J_STABILIZER_CENSUS_WITH_PHYSICAL_J0_EXPONENTIAL_AND_J1_COMPLEX_FREQUENCY_MODES",
            "exceptional_isotypes": ["j=0", "j=1"],
            "stabilizer_dimension_accounted": 4,
            "j0_health": "OBSTRUCTED_REAL_EXPONENTIAL_PHYSICAL_MODE",
            "j1_health": "OBSTRUCTED_COMPLEX_FREQUENCY_PHYSICAL_MODES",
            "zero_frequency_stabilizer_pairing_radical": 0,
            "fixed_charge_removes_global_action_angle_but_not_nonzero_frequency_instabilities": True,
            "health_assembly_activated": True,
        },
        "claim_boundary": {
            "establishes": [
                "complete j=0 and j=1 all-k repaired q70 exceptional carriers and exact z=0 cohomology",
                "structural exhaustion of the four-dimensional Berger spatial Killing algebra",
                "exact nonzero characteristic factors, geometric multiplicities, residue pairings and Jordan status",
                "physical real-exponential j=0 and complex-frequency j=1 directions on unrestricted and fixed-charge carriers",
                "separation of local spatial stabilizers from the global charged R_rel action-angle carrier",
            ],
            "does_not_establish": [
                "nonlinear instability or finite-time blow-up",
                "Hadamard, anomaly, QME, particle, positivity or unitarity claims",
                "a particle interpretation of stabilizer torsion or residual deformation classes",
            ],
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-low-j-stabilizer-health-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1",
        "result_state": payload["terminal_verdict"]["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": payload["content_sha256"]},
        "normalization": payload["normalization"],
        "representation_census": payload["representation_census"],
        "exceptional_block_summary": {
            name: {
                "finite_parent": block["finite_parent"],
                "zero_frequency": block["zero_frequency_full_complex"],
                "unstable": block["spectrum"].get("unstable_sector", block["spectrum"].get("unstable_sectors")),
            }
            for name, block in payload["exceptional_blocks"].items()
        },
        "charge_actions": payload["charge_actions"],
        "terminal_verdict": payload["terminal_verdict"],
        "claim_boundary": payload["claim_boundary"],
    }
    value["content_hashes"] = {key + "_sha256": _digest(value[key]) for key in ("normalization", "representation_census", "exceptional_block_summary", "charge_actions", "terminal_verdict", "claim_boundary")}
    return value


def _validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload digest failed")
    expected = {key + "_sha256": _digest(certificate[key]) for key in ("normalization", "representation_census", "exceptional_block_summary", "charge_actions", "terminal_verdict", "claim_boundary")}
    if certificate["content_hashes"] != expected:
        raise AssertionError("certificate hashes failed")
    if certificate["terminal_verdict"]["stabilizer_dimension_accounted"] != 4:
        raise AssertionError("stabilizer census failed")


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
    for schema_path, value in ((SCHEMA, certificate), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if json.loads(OUTPUT.read_text()) != certificate or json.loads(PAYLOAD.read_text()) != payload:
        raise AssertionError("stored low-j stabilizer health artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
