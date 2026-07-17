#!/usr/bin/env python3
"""Independent verification of the Berger 84-row rod--gravity unary gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers.generate_berger_84_row_rod_gravity_unary import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
)


X = rods.X
T = rods.T
LOCALS = {str(symbol): symbol for symbol in (*X, T)}


def _frame(value: sp.Expr, axis: int) -> sp.Expr:
    """Reconstruct the Berger invariant frame without the producer helper."""

    x0, x1, x2, x3 = X
    c = 3 * sp.sqrt(10) / 20
    coefficients = (
        (-x1 / 2, x0 / 2, x3 / 2, -x2 / 2),
        (-x2 / 2, -x3 / 2, x0 / 2, x1 / 2),
        (-x3 / (2 * c), x2 / (2 * c), -x1 / (2 * c), x0 / (2 * c)),
    )[axis]
    return sp.expand(sum(coefficient * sp.diff(value, coordinate) for coefficient, coordinate in zip(coefficients, X)))


def _independent_gamma(value: dict) -> None:
    global_rods_path = DEPENDENCIES["global_rods"]
    global_rods = json.loads(global_rods_path.read_text())
    expected_entries: list[dict] = []
    temporal_nonzero = 0
    event_blocks: list[sp.Matrix] = []
    row_offset = 0
    for detector_index, detector in enumerate(global_rods["global_rods"]):
        phase = sp.sympify(detector["hopf_phase"], locals=LOCALS)
        event_time = sp.sympify(detector["physical_event_time"], locals=LOCALS)
        event = {X[0]: sp.cos(phase), X[1]: 0, X[2]: 0, X[3]: sp.sin(phase), T: event_time}
        block = sp.zeros(3)
        for rod_index, text in enumerate(detector["rod_fields"], start=1):
            field = sp.sympify(text, locals=LOCALS)
            temporal_nonzero += int(sp.trigsimp(sp.diff(field, T)) != 0)
            for ghost_index in range(3):
                coefficient = sp.trigsimp(_frame(field, ghost_index))
                block[rod_index - 1, ghost_index] = sp.trigsimp(coefficient.subs(event))
                if coefficient != 0:
                    expected_entries.append({
                        "output_index": 64 + row_offset,
                        "output_row": f"R{detector_index}_{rod_index}",
                        "input_index": ghost_index,
                        "input_row": f"c_spatial_{ghost_index + 1}",
                        "coefficient": sp.sstr(coefficient),
                    })
            row_offset += 1
        event_blocks.append(block)

    gauge = value["rod_gauge_blocks"]
    if temporal_nonzero != gauge["raw_temporal_nonzero_count"] or temporal_nonzero != 6:
        raise ValueError("independent temporal rod-column count failed")
    if expected_entries != gauge["gamma_entries"]:
        raise ValueError("independent Gamma_R reconstruction failed")
    expected_block = sp.Matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    if any(block != expected_block or block.det() != 1 or block.rank() != 3 for block in event_blocks):
        raise ValueError("independent detector-event Gamma_R rank failed")

    expected_adjoint = []
    for entry in expected_entries:
        expected_adjoint.append({
            "output_index": entry["input_index"] + 49,
            "output_row": f"c_spatial_star_{entry['input_index'] + 1}",
            "input_index": entry["output_index"] + 10,
            "input_row": f"{entry['output_row']}_plus",
            "coefficient": sp.sstr(-sp.sympify(entry["coefficient"], locals=LOCALS)),
        })
    if expected_adjoint != gauge["gamma_sharp_q1_entries"]:
        raise ValueError("Gamma_R cotangent adjoint is not the exact negative transpose")


def _independent_hessian(value: dict) -> None:
    eta = sp.diag(-1, 1, 1, 1)
    fixtures = [
        (sp.Matrix([1, 2, 0, 1]), sp.Matrix([2, -1, 1, 0]), sp.diag(1, 2, -1, 1), sp.diag(0, 1, 2, -1)),
        (sp.Matrix([0, 1, 3, -1]), sp.Matrix([1, 0, -2, 2]), sp.Matrix([[1, 1, 0, 0], [1, 0, 1, 0], [0, 1, 2, 0], [0, 0, 0, -1]]), sp.diag(2, -1, 1, 0)),
    ]
    alpha, beta, rho = sp.symbols("alpha beta rho")
    fixture_values = []
    for background_gradient, rod_variation, h, k in fixtures:
        metric = eta + alpha * h + beta * k
        gradient = background_gradient + rho * rod_variation
        lagrangian = -sp.sqrt(-metric.det()) * (gradient.T * metric.inv() * gradient)[0] / 2
        mixed_forward = sp.diff(lagrangian, alpha, rho).subs({alpha: 0, beta: 0, rho: 0})
        mixed_reverse = sp.diff(lagrangian, rho, alpha).subs({alpha: 0, beta: 0, rho: 0})
        metric_forward = sp.diff(lagrangian, alpha, beta).subs({alpha: 0, beta: 0, rho: 0})
        metric_reverse = sp.diff(lagrangian, beta, alpha).subs({alpha: 0, beta: 0, rho: 0})
        if sp.simplify(mixed_forward - mixed_reverse) != 0:
            raise ValueError("independent mixed Hessian symmetry failed")
        if sp.simplify(metric_forward - metric_reverse) != 0:
            raise ValueError("independent metric Hessian symmetry failed")
        fixture_values.append({"mixed_h_rod": sp.sstr(mixed_forward), "metric_h_k": sp.sstr(metric_forward)})
    audit = value["raw_covariant_rod_hessian"]["exact_specialization_audit"]
    if fixture_values != audit["fixture_values"]:
        raise ValueError("persisted action-Hessian values drifted")
    if sum(sp.sympify(row["mixed_h_rod"]) != 0 for row in fixture_values) != audit["nonzero_mixed_fixture_count"]:
        raise ValueError("mixed-Hessian mutation witness drifted")


def _independent_laurent_inverse(*, delete_feedback: bool = False) -> tuple[int, int]:
    """Replay the Schur-Laurent formula on a second noncommuting fixture."""

    rho = sp.symbols("rho", nonzero=True)
    a0 = sp.Matrix([[3, 1], [2, 1]])
    a1 = sp.Matrix([[0, 1], [-1, 2]])
    b = sp.Matrix([[2, 1], [0, 1]])
    c = sp.Matrix([[1, -1], [1, 0]])
    d = sp.Matrix([[2, 0], [1, 1]])
    a0_inv, d_inv = a0.inv(), d.inv()
    effective = a1 if delete_feedback else a1 - b * d_inv * c
    s_inverse = a0_inv - rho * a0_inv * effective * a0_inv
    candidate = sp.Matrix.vstack(
        sp.Matrix.hstack(s_inverse, -s_inverse * b * d_inv),
        sp.Matrix.hstack(
            -d_inv * c * s_inverse,
            d_inv / rho + d_inv * c * s_inverse * b * d_inv,
        ),
    )
    operator = sp.Matrix.vstack(
        sp.Matrix.hstack(a0 + rho * a1, rho * b),
        sp.Matrix.hstack(rho * c, rho * d),
    )

    def defects(residual: sp.Matrix) -> int:
        return sum(
            sp.simplify(sp.expand(residual[row, column]).coeff(rho, power)) != 0
            for row in range(residual.rows)
            for column in range(residual.cols)
            for power in (-1, 0, 1)
        )

    return defects(operator * candidate - sp.eye(4)), defects(candidate * operator - sp.eye(4))


def _semantic_boundary(value: dict) -> None:
    flags = value["flags"]
    required_true = (
        "CLOCK_DRESSED_ROD_COORDINATES_CANONICAL",
        "GAMMA_R_EXPLICIT",
        "GAMMA_R_SHARP_EXPLICIT",
        "ROD_GRAVITY_ACTION_HESSIAN_EXPORTED",
        "ROD_GRAVITY_BV_NOETHER_FIRST_JET_CERTIFIED",
        "COUPLED_84_ROW_PRINCIPAL_CAUSAL_WITNESS_EXPORTED",
        "84_ROW_Q1_AXIAL_FIRST_JET_CERTIFIED",
        "84_ROW_ADVANCED_RETARDED_GREEN_AXIAL_FIRST_JET_CERTIFIED",
    )
    required_false = (
        "84_ROW_Q1_CERTIFIED",
        "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "84_ROW_Q2_Q3_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "QUANTUM_CLAIM",
    )
    if not all(flags[key] is True for key in required_true):
        raise ValueError("qualified axial first-jet result was demoted")
    if not all(flags[key] is False for key in required_false):
        raise ValueError("unqualified or mixed result was over-promoted")
    scope = value["coefficient_scope"]
    if scope["q1_certified_bidegrees_r_kappa"] != [[0, 0], [1, 0], [0, 1]]:
        raise ValueError("axial coefficient scope drifted")
    if "r*kappa" not in scope["excluded"] or not scope["singular_probe_limit_explicit"]:
        raise ValueError("mixed-jet or Laurent boundary was hidden")
    orders = value["coupled_causal_witness"]["operator_order_audit"]
    if orders["principal_part_defect_count"] != 0:
        raise ValueError("cross block changes the declared diagonal principal part")
    if any(row["order"] >= row["comparison_order"] for row in orders["cross_block_orders"]):
        raise ValueError("independent differential-order audit failed")
    inverse_audit = value["coupled_causal_witness"]["laurent_inverse_audit"]
    if _independent_laurent_inverse() != (0, 0):
        raise ValueError("independent coupled Laurent inverse failed")
    mutated_left, mutated_right = _independent_laurent_inverse(delete_feedback=True)
    if mutated_left + mutated_right == 0:
        raise ValueError("independent Schur-feedback mutation was not detected")
    if inverse_audit["checked_laurent_powers"] != [-1, 0, 1] or inverse_audit["first_omitted_order"] != "r^2":
        raise ValueError("Laurent truncation boundary drifted")
    mutations = value["mutation_results"]
    if len(mutations) != 5 or not all(row["detected"] and row["defect_count"] > 0 for row in mutations):
        raise ValueError("a required mutation was not detected computationally")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("84-row rod--gravity unary certificate is stale")
    for name, path in DEPENDENCIES.items():
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        if value["dependency_refs"][name]["sha256"] != expected:
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {entry["path"]: entry["sha256"] for entry in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        expected_path = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(expected_path) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {expected_path}")
    _independent_gamma(value)
    _independent_hessian(value)
    _semantic_boundary(value)
    for key in (
        "84_ROW_Q1_CERTIFIED",
        "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "84_ROW_Q2_Q3_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][key] = True
        try:
            _semantic_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    schema_mutant = deepcopy(value)
    schema_mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(schema_mutant)
    except ValidationError:
        pass
    else:
        raise ValueError("strict-schema mutation accepted")
    return value


def main() -> int:
    verify()
    print("BERGER_84_ROW_ROD_GRAVITY_UNARY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
