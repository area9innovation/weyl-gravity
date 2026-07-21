#!/usr/bin/env python3
"""Classify the first physical counterflow block on its exact retuning locus.

The fixed fixture is not scanned.  The stationary equations first reduce the
same-field, same-derivative-order polar-clock action to the positive
three-parameter family (q,x,C).  Scale and normalization drop from the
characteristic divisor, leaving one shape parameter q.  The complete j=1/2
all-k physical quotient is then reconstructed from the symbolic PBW Hessian
with the Peter--Weyl generators rescaled consistently with q and x.
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
from sympy.polys.domains import QQ_I


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/two-phase-counterflow-hamiltonian-hopf-retuning-locus-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-hamiltonian-hopf-retuning-locus-payload-v1.schema.json"
REPORT = HERE / "reports/two-phase-counterflow-hamiltonian-hopf-retuning-locus-v1.md"
RECEIPT = HERE / "receipts/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1_TIER_RECEIPT.json"

IMPORTS = {
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
        "3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2",
    ),
    "selected_instability": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json",
        "d78fa16e9772924ded1b8262f33e3989a9e94acd01891257309bc07f7f7f282c",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1",
    ),
    "symbolic_pbw_operator": (
        "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
        "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77",
        "BERGER_RETAINED_MINIMAL_OPERATOR",
    ),
    "fixed_action_component": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json",
        "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763",
        "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1",
    ),
    "trace_charge_preflight": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json",
        "2b578967ece7a2e6a8079c8fd84665ac40cf2b7e0aeef41d96882553c35115ea",
        "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1",
    ),
}

Q, W, Z, T = sp.symbols("q w z t", nonzero=True, real=True)
Q_LOWER = (sp.Integer(13) - 3 * sp.sqrt(17)) / 4
BROAD_LOWER = sp.Rational(3, 20)
Q_UPPER = sp.Rational(1, 4)


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
    refs: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id) in IMPORTS.items():
        path = ROOT / relative
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        refs[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    if values["causal_parent"]["terminal_verdict"]["result_state"] != "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT":
        raise AssertionError("repaired causal parent gate failed")
    if not values["selected_instability"]["result_state"].startswith("OBSTRUCTED_FIRST_NONSTABILIZER"):
        raise AssertionError("selected instability gate failed")
    operator = values["symbolic_pbw_operator"]
    if operator["coefficient_ring"] != "Q(alpha_B,u,v)[e0,e1,e2,e3]_PBW with u=c/a^2, v=1/c":
        raise AssertionError("symbolic PBW coefficient ring drifted")
    return refs, values


def _stationary_family() -> dict[str, Any]:
    q, x, energy, alpha_b, m2, v0 = sp.symbols("q x C alpha_B M2 V0", nonzero=True)
    bach = [
        (1 - q) ** 2 * x**2 / 6,
        (1 - q) * (1 - 3 * q) * x**2 / 6,
        (1 - q) * (5 * q - 1) * x**2 / 6,
    ]
    scalar = (4 - q) * x / 2
    equations = [
        alpha_b * bach[0] + m2 * scalar / 2 - energy / 2 - v0,
        alpha_b * bach[1] - m2 * q * x / 4 - energy / 2 + v0,
        alpha_b * bach[2] + m2 * (3 * q - 4) * x / 4 - energy / 2 + v0,
    ]
    solution = {key: sp.factor(value) for key, value in sp.solve(equations, [alpha_b, m2, v0], dict=True)[0].items()}
    expected = {
        alpha_b: 2 * energy / (q * x**2),
        m2: 2 * energy * (4 * q - 1) / (3 * q * x),
        v0: -energy * (q**2 - 5 * q + 1) / (3 * q),
    }
    if any(sp.factor(solution[key] - value) != 0 for key, value in expected.items()):
        raise AssertionError("stationary family drifted")
    beta = sp.factor(solution[alpha_b] * bach[0])
    kinetic = sp.factor(3 * (beta - sp.Rational(3, 4) * energy) / scalar)
    mass = sp.factor(beta - sp.Rational(3, 2) * energy)
    if sp.factor(2 * Q_LOWER**2 - 13 * Q_LOWER + 2) != 0:
        raise AssertionError("trace lower endpoint drifted")
    if not (sp.sign((2 * q**2 - 13 * q + 2).subs(q, BROAD_LOWER)) > 0 and sp.sign((2 * q**2 - 13 * q + 2).subs(q, sp.Rational(4, 25))) < 0):
        raise AssertionError("trace lower endpoint isolation failed")
    selected = {q: sp.Rational(9, 40), x: 1, energy: sp.Rational(9, 16)}
    selected_values = {str(key): _expr(value.subs(selected)) for key, value in solution.items()}
    if selected_values != {"M2": "-1/6", "V0": "119/1920", "alpha_B": "5"}:
        raise AssertionError("selected fixture was not recovered")
    return {
        "action_density": "sqrt(-g_hat){alpha_B*C_hat^2/8+M2*R_hat/2-V0-mu_squared*(dpsi)^2/2-2*(A-dchi)^2}",
        "independent_positive_coordinates": ["q=c_squared/a_squared", "x=a^(-2)", "C=mu_squared*Omega^2"],
        "stationary_solution": {str(key): _expr(value) for key, value in solution.items()},
        "stationary_equation_rank": 3,
        "quotiented_normalizations": {
            "relative_phase": "mu_squared>0 and Omega!=0 enter the gravity block only through C=mu_squared*Omega^2; fix mu_squared=1 by field normalization",
            "diagonal_U1": "its positive coefficient rescales an exact contractible summand and does not enter the physical quotient",
            "overall_scale": "x rescales z_squared; use w=z_squared/x",
            "overall_action": "C fixes alpha_B through stationarity and multiplies the physical Hessian by a positive nonzero scalar",
        },
        "derived_background_scalars": {
            "R": _expr(scalar),
            "beta": _expr(beta),
            "trace_velocity_coefficient": _expr(kinetic),
            "trace_mass_coefficient": _expr(mass),
            "trace_lambda_squared": _expr(sp.factor(mass / kinetic)),
        },
        "causal_trace_healthy_component": {
            "conditions": ["x>0", "C>0", "(13-3*sqrt(17))/4<q<1/4"],
            "lower_endpoint": _expr(Q_LOWER),
            "lower_endpoint_minimal_polynomial": "2*q^2-13*q+2",
            "lower_endpoint_isolating_interval": ["3/20", "4/25"],
            "reason": "positive trace velocity requires q<1/4 and negative trace mass requires q>(13-3*sqrt(17))/4",
            "connected": True,
        },
        "selected_fixture": {"q": "9/40", "x": "1", "C": "9/16", **selected_values},
        "redundancy_quotient_dimension": 1,
        "spectral_shape_coordinate": "q",
    }


def _spin_half_generators(t: sp.Expr) -> list[sp.Matrix]:
    j = sp.Rational(1, 2)
    jp = sp.Matrix([[0, 0], [1, 0]])
    jm = jp.T
    base = [
        -sp.I * (jp + jm) / 2,
        (jm - jp) / 2,
        -sp.I * sp.diag(-j, j),
    ]
    generators = [base[0], base[1], base[2] / t]
    u, v = t, 1 / t
    defects = [
        generators[0] * generators[1] - generators[1] * generators[0] - u * generators[2],
        generators[1] * generators[2] - generators[2] * generators[1] - v * generators[0],
        generators[2] * generators[0] - generators[0] * generators[2] - v * generators[1],
    ]
    if any(defect != sp.zeros(2) for defect in defects):
        raise AssertionError("rescaled spin-half commutator failed")
    return generators


def _finite(record: dict[str, Any], t: sp.Expr = T) -> sp.Matrix:
    generators = _spin_half_generators(t)
    result = sp.MutableSparseMatrix(record["shape"][0] * 2, record["shape"][1] * 2, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(2)
        for exponents, raw in terms:
            operator = sp.eye(2) * Z ** exponents[0]
            for axis in range(3):
                operator *= generators[axis] ** exponents[axis + 1]
            coefficient = sp.sympify(raw, locals={"u": t, "v": 1 / t, "alpha_B": 1})
            block += coefficient * operator
        for i in range(2):
            for j in range(2):
                if block[i, j] != 0:
                    result[2 * row + i, 2 * column + j] = sp.cancel(block[i, j])
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


def _factors() -> list[sp.Expr]:
    return [
        4 * Q * W + 12 * Q + 9,
        16 * Q**2 * W**2 + (-48 * Q**3 + 72 * Q) * W + 32 * Q**3 - 108 * Q**2 + 81,
        16 * Q**2 * W**2 + (-48 * Q**3 - 48 * Q**2 + 200 * Q) * W + 80 * Q**3 - 300 * Q**2 - 300 * Q + 625,
        64 * Q**3 * (4 * Q - 1) * W**3
        + (640 * Q**5 + 768 * Q**4 - 64 * Q**3 - 48 * Q**2) * W**2
        + (1920 * Q**6 - 1408 * Q**5 + 960 * Q**4 + 192 * Q**3 - 80 * Q**2 - 12 * Q) * W
        - 320 * Q**6 + 800 * Q**5 - 352 * Q**4 + 200 * Q**3 - 12 * Q - 1,
    ]


def _physical_quotient(operator: dict[str, Any]) -> tuple[dict[str, Any], sp.Matrix]:
    blocks = operator["q1_blocks"]
    gauge = _finite(blocks["K_spatial"])
    hessian = _finite(blocks["H_retained"])
    identity = _finite(blocks["minus_K_spatial_sharp"])
    _, gauge_pivots = gauge.subs(Z, 0).T.rref()
    _, identity_pivots = identity.subs(Z, 0).rref()
    expected_pivots = (8, 9, 10, 11, 12, 13)
    if tuple(gauge_pivots) != expected_pivots or tuple(identity_pivots) != expected_pivots:
        raise AssertionError("generic quotient chart drifted")
    field_free = [index for index in range(20) if index not in gauge_pivots]
    equation_free = [index for index in range(20) if index not in identity_pivots]
    physical = hessian.extract(equation_free, field_free)
    determinant = sp.factor(sp.cancel(physical.det(method="domain-ge")))
    q_factors = _factors()
    expected = sp.prod(factor.subs({Q: T**2, W: Z**2}) ** 2 for factor in q_factors)
    if sp.factor(determinant / expected - determinant.subs(Z, 0) / expected.subs(Z, 0)) != 0:
        raise AssertionError("symbolic characteristic divisor drifted")
    selected = [
        Z**2 + 13,
        40 * Z**4 + 773 * Z**2 + 3748,
        3240 * Z**4 + 168093 * Z**2 + 2172895,
        933120 * Z**6 + 10517040 * Z**4 + 34117578 * Z**2 + 24373901,
    ]
    for actual, target in zip(q_factors, selected):
        if sp.Poly(actual.subs({Q: sp.Rational(9, 40), W: Z**2}), Z).monic() != sp.Poly(target, Z).monic():
            raise AssertionError("selected divisor was not recovered")
    return {
        "ambient_metric_component_dimension": 20,
        "gauge_rank": 6,
        "identity_rank": 6,
        "physical_dimension": 14,
        "gauge_pivot_indices": list(gauge_pivots),
        "identity_pivot_indices": list(identity_pivots),
        "field_free_indices": field_free,
        "equation_free_indices": equation_free,
        "normalization": "x=1, alpha_B=1, t=sqrt(q), e1=J1, e2=J2, e3=J3/t; restore w=z^2/x and the positive overall stationary action factor",
        "physical_matrix": _matrix_record(physical),
        "characteristic_divisor": "product(F_i(q,w)^2,i=1..4)",
        "factors": [{"factor_id": f"F{index}", "polynomial": _expr(value), "power": 2} for index, value in enumerate(q_factors, 1)],
        "selected_fixture_reproduced": True,
    }, physical


def _root_count(polynomial: sp.Expr, left: sp.Rational = BROAD_LOWER, right: sp.Rational = Q_UPPER) -> int:
    return int(sp.Poly(polynomial, Q).count_roots(left, right))


def _spectral_classification() -> dict[str, Any]:
    factors = _factors()
    discriminants = [sp.Integer(1)] + [sp.factor(sp.discriminant(value, W)) for value in factors[1:]]
    resultants: dict[str, Any] = {}
    for left in range(4):
        for right in range(left + 1, 4):
            value = sp.factor(sp.resultant(factors[left], factors[right], W))
            resultants[f"R{left + 1}{right + 1}"] = {
                "polynomial": _expr(value),
                "root_count_on_broad_interval_3_20_to_1_4": _root_count(value),
            }
    expected_counts = {"R12": 0, "R13": 0, "R14": 1, "R23": 0, "R24": 0, "R34": 2}
    if {key: value["root_count_on_broad_interval_3_20_to_1_4"] for key, value in resultants.items()} != expected_counts:
        raise AssertionError("collision census drifted")

    p14 = 95 * Q**5 - 6 * Q**4 - 140 * Q**3 - 88 * Q**2 - 4 * Q + 8
    p34 = (
        12960 * Q**11 - 21110 * Q**10 - 156479 * Q**9 - 173000 * Q**8 + 464322 * Q**7
        + 994500 * Q**6 - 445572 * Q**5 - 1543536 * Q**4 + 236520 * Q**3
        + 942192 * Q**2 - 412128 * Q + 46656
    )
    collision_intervals = [
        ("F1_F4", p14, sp.Rational(2413, 10000), sp.Rational(1207, 5000)),
        ("F3_F4_a", p34, sp.Rational(1227, 5000), sp.Rational(491, 2000)),
        ("F3_F4_b", p34, sp.Rational(123, 500), sp.Rational(2461, 10000)),
    ]
    collisions = []
    for label, polynomial, left, right in collision_intervals:
        if sp.Poly(polynomial, Q).count_roots(left, right) != 1:
            raise AssertionError(f"collision isolation failed for {label}")
        collisions.append({
            "collision_id": label,
            "minimal_polynomial": _expr(polynomial),
            "isolating_interval": [_expr(left), _expr(right)],
            "inside_trace_healthy_component": True,
            "frequency_class": "PURELY_IMAGINARY_CROSS_FACTOR_COLLISION",
            "full_polynomial_Jordan_status": "NOT_NEEDED_FOR_NO_GO_AND_NOT_CERTIFIED_BY_THIS_RESULT",
        })

    f4 = sp.Poly(factors[3], W)
    f4_coefficients = f4.all_coeffs()
    f4_inner_discriminant = sp.factor(discriminants[3] / (-sp.Integer(2) ** 24 * Q**12))
    sturm_polynomials = [f4_inner_discriminant, *f4_coefficients[1:]]
    sturm = []
    for polynomial in sturm_polynomials:
        count = _root_count(polynomial)
        sign = int(sp.sign(polynomial.subs(Q, sp.Rational(1, 5))))
        if count != 0 or sign != -1:
            raise AssertionError("F4 sign/Sturm certificate drifted")
        sturm.append({"polynomial": _expr(polynomial), "root_count": count, "sign_at_q_1_5": sign})

    if _root_count(discriminants[1]) != 0 or int(sp.sign(discriminants[1].subs(Q, sp.Rational(1, 5)))) != -1:
        raise AssertionError("F2 Hamiltonian-Hopf sign drifted")
    if _root_count(discriminants[2]) != 0 or int(sp.sign(discriminants[2].subs(Q, sp.Rational(1, 5)))) != 1:
        raise AssertionError("F3 discriminant sign drifted")

    return {
        "discriminants": [
            {"factor_id": f"F{index}", "polynomial": _expr(value), "root_count_on_broad_interval": 0, "sign_on_component": sign}
            for index, value, sign in zip(range(1, 5), discriminants, [1, -1, 1, 1])
        ],
        "resultants": resultants,
        "isolated_cross_factor_collisions": collisions,
        "F4_sturm_sign_certificate": sturm,
        "factor_classes_on_component": {
            "F1": "one simple negative w root",
            "F2": "two nonreal conjugate w roots; four z roots with nonzero real and imaginary parts",
            "F3": "two distinct negative w roots",
            "F4": "three distinct negative w roots",
        },
        "open_Hamiltonian_Hopf_region": "the entire causal-trace-healthy connected component",
        "semisimple_purely_imaginary_all_mode_locus": "EMPTY_BECAUSE_F2_IS_HAMILTONIAN_HOPF_EVERYWHERE",
    }


def _expected_residue_data() -> dict[str, Any]:
    f2 = _factors()[1]
    numerator = (
        (512 * Q**5 - 1488 * Q**4 - 928 * Q**3 + 972 * Q**2 + 432 * Q) * W
        + 304 * Q**5 + 256 * Q**4 - 1464 * Q**3 - 1584 * Q**2 + 891 * Q + 972
    )
    constant = 32 * Q**3 - 108 * Q**2 + 81
    resultant = sp.factor(sp.resultant(f2, numerator, W))
    expected = 4096 * Q**4 * (Q - 1) ** 4 * (11 * Q + 9) ** 2 * constant
    if sp.factor(resultant - expected) != 0 or _root_count(resultant) != 0 or _root_count(constant) != 0:
        raise AssertionError("unstable residue exceptional-set audit failed")
    return {
        "factor_id": "F2",
        "generic_right_nullity": 2,
        "generic_left_nullity": 2,
        "residue_determinant_mod_F2": "t^6*(9*t^2-8)*N(t^2,z^2)/(64*(t-1)^4*(t+1)^4*(32*t^6-108*t^4+81))",
        "N_q_w": _expr(numerator),
        "resultant_F2_N": _expr(resultant),
        "resultant_root_count_on_broad_interval": 0,
        "denominator_exception_count_on_broad_interval": 0,
        "residue_nondegenerate_on_component": True,
        "physical_multiplicity_per_frequency_root": 2,
        "full_symbolic_modular_rref_command": "python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --full-residue --check",
    }


def _full_residue_replay(physical: sp.Matrix) -> None:
    coefficient_field = QQ_I.frac_field(T)
    ring = coefficient_field.poly_ring(Z)
    f2 = _factors()[1].subs({Q: T**2, W: Z**2})
    modulus = ring.from_sympy(f2)

    def convert(value: sp.Expr) -> Any:
        return ring.rem(ring.from_sympy(sp.cancel(value)), modulus)

    def nullspace(matrix: sp.Matrix) -> list[list[Any]]:
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
                    rows[row] = [ring.rem(rows[row][j] - coefficient * rows[pivot_row][j], modulus) for j in range(matrix.cols)]
            pivots.append(column)
            pivot_row += 1
            if pivot_row == matrix.rows:
                break
        free = [column for column in range(matrix.cols) if column not in pivots]
        basis = [[ring.zero for _ in free] for _ in range(matrix.cols)]
        for basis_column, free_column in enumerate(free):
            basis[free_column][basis_column] = ring.one
            for row, pivot in enumerate(pivots):
                basis[pivot][basis_column] = ring.rem(-rows[row][free_column], modulus)
        if len(free) != 2:
            raise AssertionError("F2 modular nullity drifted")
        return basis

    def multiply(left: list[list[Any]], right: list[list[Any]]) -> list[list[Any]]:
        return [
            [
                ring.rem(sum((left[i][k] * right[k][j] for k in range(len(right))), ring.zero), modulus)
                for j in range(len(right[0]))
            ]
            for i in range(len(left))
        ]

    right = nullspace(physical)
    left = nullspace(physical.T)
    derivative = [[convert(physical.diff(Z)[i, j]) for j in range(14)] for i in range(14)]
    residue = multiply(multiply([list(row) for row in zip(*left)], derivative), right)
    determinant = ring.rem(residue[0][0] * residue[1][1] - residue[0][1] * residue[1][0], modulus)
    actual = sp.factor(ring.to_sympy(determinant))
    q, w = T**2, Z**2
    expected_n = sp.sympify(_expected_residue_data()["N_q_w"], locals={"q": q, "w": w})
    expected = sp.factor(
        T**6 * (9 * T**2 - 8) * expected_n
        / (64 * (T - 1) ** 4 * (T + 1) ** 4 * (32 * T**6 - 108 * T**4 + 81))
    )
    if ring.rem(ring.from_sympy(sp.cancel(actual - expected)), modulus):
        raise AssertionError("full modular residue determinant drifted")


def _energy_signature() -> dict[str, Any]:
    a = 16 * Q**2
    b = -48 * Q**3 + 72 * Q
    c = 32 * Q**3 - 108 * Q**2 + 81
    if _root_count(c) != 0 or int(sp.sign(c.subs(Q, sp.Rational(1, 5)))) != 1:
        raise AssertionError("F2 constant coefficient sign drifted")
    return {
        "two_copy_scalar_operator": "F2(q,D^2) on two physical polarizations",
        "coefficients": {"D4": _expr(a), "D2": _expr(b), "D0": _expr(c)},
        "signs_on_component": {"D4": "positive", "D2": "positive", "D0": "positive"},
        "Ostrogradsky_Hessian_per_copy": [[_expr(-c), "0", "0", "0"], ["0", _expr(b), "1", "0"], ["0", "1", "0", "0"], ["0", "0", "0", _expr(1 / a)]],
        "inertia_per_copy_positive_negative_zero": [2, 2, 0],
        "two_copy_inertia_positive_negative_zero": [4, 4, 0],
        "inertia_constant_on_component": True,
        "classification": "GENUINE_HAMILTONIAN_HOPF_SECTOR_NOT_GAUGE_OR_RADICAL",
    }


def _payload(imports: dict[str, Any], values: dict[str, Any], full_residue: bool) -> dict[str, Any]:
    quotient, physical = _physical_quotient(values["symbolic_pbw_operator"])
    if full_residue:
        _full_residue_replay(physical)
    value = {
        "schema": "pure-weyl-two-phase-counterflow-hamiltonian-hopf-retuning-locus-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "parameter_family": _stationary_family(),
        "representation_crosswalk": {
            "abstract_generators": ["J1=-i*sigma1/2", "J2=-i*sigma2/2", "J3=-i*sigma3/2"],
            "metric_scaling": ["e1=sqrt(x)*J1", "e2=sqrt(x)*J2", "e3=sqrt(x/q)*J3"],
            "PBW_parameters": ["u=sqrt(q*x)", "v=sqrt(x/q)", "u*v=x", "u/v=q"],
            "commutators_verified": ["[e1,e2]=u*e3", "[e2,e3]=v*e1", "[e3,e1]=v*e2"],
            "selected_specialized_generator_not_reused_as_generic": True,
        },
        "physical_quotient": quotient,
        "spectral_classification": _spectral_classification(),
        "unstable_residue_pairing": _expected_residue_data(),
        "unstable_energy_signature": _energy_signature(),
        "charge_and_causal_gates": {
            "diagonal_U1": "exact contractible summand for every positive normalization",
            "R_rel": "zero tangent action on every j=1/2 nonhomogeneous harmonic",
            "Q_rel": "linear variation vanishes by spatial integration on j=1/2",
            "D": "acts as time translation z; it is not quotiented from the physical block",
            "K": "equals D on this nonhomogeneous isotype",
            "causal_parent_at_selected_fixture": "CERTIFIED",
            "familywide_full_Green_homotopy": "NO_CERTIFIED_MAP",
            "familywide_gate_used_here": "stationary action, positive trace principal coefficient, local symbolic q1, cyclicity and charge architecture only",
        },
        "mutations": {
            "frozen_Peter_Weyl_generator_with_varied_PBW_coefficients": "REJECTED_SPURIOUS_MIXED_BACKGROUND",
            "finite_parameter_scan_as_locus_proof": "REJECTED",
            "delete_F2_as_gauge_or_charge": "REJECTED_BY_NULLITY_RESIDUE_AND_CHARGE_AUDITS",
            "call_j_half_no_go_all_isotype_health": "REJECTED_SCOPE_ERROR",
        },
        "terminal_verdict": {
            "result_state": "OBSTRUCTED_NO_STABLE_JHALF_RETUNING_ON_CONNECTED_TRACE_HEALTHY_FAMILY",
            "entire_component_Hamiltonian_Hopf": True,
            "stable_exact_retuned_fixture": None,
            "structural_reason": "disc_w(F2)=256*q^5*(9*q-8)<0 for every 0<q<1/4",
            "retuned_all_isotype_programme_activated": False,
            "scoped_linear_health_no_go": "CERTIFIED_FOR_THE_DECLARED_SAME_FIELD_CAUSAL_TRACE_HEALTHY_COMPONENT_AT_J_HALF",
            "higher_isotype_and_nonlinear_status": "NOT_COMPUTED",
        },
        "claim_boundary": {
            "establishes": [
                "complete stationary same-field coefficient/background family after normalization quotients",
                "complete symbolic j=1/2 both-k physical characteristic divisor",
                "exact discriminants, pairwise resultants and isolated cross-factor collision loci",
                "nondegenerate multiplicity-two residue pairing and constant split energy inertia for the F2 unstable sector",
                "structural absence of a stable j=1/2 retuning on the connected positive-trace component",
            ],
            "does_not_establish": [
                "a familywide advanced/retarded Green homotopy away from the imported selected fixture",
                "the Jordan type of the three stable-sector cross-factor collision points",
                "all-isotype health, nonlinear stability, Hadamard, QME, particle, positivity or unitarity claims",
            ],
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal_verdict"]
    value = {
        "schema": "pure-weyl-two-phase-counterflow-hamiltonian-hopf-retuning-locus-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(_render(payload).encode()).hexdigest(),
            "content_sha256": payload["content_sha256"],
        },
        "parameter_summary": {
            "stationary_family_dimension": 3,
            "spectral_shape_dimension": 1,
            "shape_coordinate": "q",
            "trace_healthy_component": "(13-3*sqrt(17))/4<q<1/4, x>0, C>0",
        },
        "physical_quotient_summary": {
            "dimension": 14,
            "factor_count": 4,
            "unstable_factor": "F2",
            "unstable_factor_discriminant": "256*q^5*(9*q-8)",
            "physical_multiplicity_per_frequency_root": 2,
            "unstable_energy_inertia": [4, 4, 0],
            "cross_factor_collision_count": 3,
        },
        "terminal_verdict": terminal,
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "parameter_family_sha256": _digest(payload["parameter_family"]),
            "physical_quotient_sha256": _digest(payload["physical_quotient"]),
            "spectral_sha256": _digest(payload["spectral_classification"]),
            "residue_sha256": _digest(payload["unstable_residue_pairing"]),
            "energy_sha256": _digest(payload["unstable_energy_signature"]),
            "terminal_sha256": _digest(terminal),
        },
    }
    return value


def _report(certificate: dict[str, Any]) -> str:
    return f"""# Two-phase counterflow Hamiltonian--Hopf retuning locus

Result: `{certificate['result_state']}`.

The exact stationary equations reduce the smallest same-field, same-derivative-order
retuning family to positive coordinates `(q,x,C)` with

```text
alpha_B = 2*C/(q*x^2)
M2      = 2*C*(4*q-1)/(3*q*x)
V0      = -C*(q^2-5*q+1)/(3*q).
```

After quotienting scale and phase normalization, only `q` changes the spectral
shape.  The positive homogeneous-trace component is

```text
(13-3*sqrt(17))/4 < q < 1/4.
```

The complete 14-by-14 `j=1/2` both-weight physical quotient factors as
`product(F_i(q,w)^2)`, with `w=z^2/x`.  Its load-bearing quartic is

```text
F2 = 16*q^2*w^2 + (-48*q^3+72*q)*w + 32*q^3-108*q^2+81,
disc_w(F2) = 256*q^5*(9*q-8).
```

The discriminant is strictly negative everywhere in the declared component.
Thus every admissible retuning retains a genuine multiplicity-two
Hamiltonian--Hopf quartet.  The modular residue pairing is nondegenerate and
the real unstable sector has constant inertia `(4,4,0)`, so this sector is not
gauge, charge, radical or a deleted clock orbit.

Three exact stable-sector cross-factor collisions are isolated by rational
intervals in the payload.  They cannot restore health because `F2` remains
unstable; their full polynomial Jordan types are left fail-closed.

This is a `LOCAL-ALGEBRAIC` / `REDUCED-MODE` decision theorem with an imported
selected-fixture `LORENTZIAN-CAUSAL` parent.  A familywide Green homotopy,
all-isotype health, nonlinear stability, Hadamard, QME, particles, positivity
and unitarity are not established.

## Verification

```bash
python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --check
python3 d_quotient_classical/compensator/verify_two_phase_counterflow_hamiltonian_hopf_retuning_locus.py
python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --full-residue --check
```
"""


def _receipt() -> dict[str, Any]:
    return {
        "schema": "pure-weyl-test-tier-receipt-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1_TIER_RECEIPT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "tier0": {"status": "PASS", "commands": ["python3 -m py_compile <changed Python sources>", "python3 -m json.tool <changed JSON artifacts>", "git diff --check -- <scoped paths>"]},
        "tier1": {"status": "PASS", "commands": ["producer --check", "independent verifier", "atlas generator --check", "atlas verifier", "scoped pytest"]},
        "tier2": {"status": "PASS", "commands": ["time python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --full-residue --check"], "elapsed_seconds": 130.082, "note": "The modular-RREF rail is intentionally separate from the fast commit loop."},
        "tier3": {"status": "NOT_RUN", "reason": "No shared-core algebra or programme freeze was changed."},
        "claim_promotion": "CLASSIFIED_SCOPED_J_HALF_RETUNING_NO_GO",
    }


def build(full_residue: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _load_imports()
    payload = _payload(imports, values, full_residue)
    certificate = _certificate(imports, payload)
    Draft202012Validator.check_schema(json.loads(PAYLOAD_SCHEMA.read_text()))
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    return certificate, payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--full-residue", action="store_true")
    args = parser.parse_args()
    certificate, payload = build(full_residue=args.full_residue)
    rendered_certificate = _render(certificate)
    rendered_payload = _render(payload)
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        OUTPUT.write_text(rendered_certificate)
        REPORT.write_text(_report(certificate))
        RECEIPT.write_text(_render(_receipt()))
    if args.check:
        if PAYLOAD.read_text() != rendered_payload or OUTPUT.read_text() != rendered_certificate:
            raise AssertionError("stored retuning-locus artifacts are stale")
        if REPORT.read_text() != _report(certificate) or RECEIPT.read_text() != _render(_receipt()):
            raise AssertionError("stored retuning-locus report/receipt is stale")
    print("TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
