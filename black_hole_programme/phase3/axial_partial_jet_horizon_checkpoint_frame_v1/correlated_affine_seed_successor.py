#!/usr/bin/env python3
"""First executable correlated omega-Taylor/dual-tau horizon successor.

The model is a degree-four Taylor polynomial in one shared complex frequency
coordinate, viewed affinely through its common linear generator, plus one
coupled complex l-infinity residual.  No componentwise interval state is used
as a checkpoint.  The mixed Levelt seed is normalized symbolically over the
dual tau jet, then one radial Taylor step is enclosed uniformly.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    CI,
    RI,
    eval_rational_rect,
)
from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt
from . import checkpoint_transport as transport

sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "correlated-affine-seed-successor-run.json"

OMEGA_CENTER = sp.Rational(transport.OMEGA.numerator, transport.OMEGA.denominator)
OMEGA_RADIUS = sp.Rational(1, 2**22)
OMEGA_CAUCHY_RADIUS = sp.Rational(1, 2**20)
OMEGA_ORDER = 4
RADIAL_ORDER = 6
RADIAL_STEP = sp.Rational(transport.RHO0.numerator, transport.RHO0.denominator) / 64
RADIAL_CAUCHY_RADIUS = 4 * RADIAL_STEP
PIVOT = 2
STATE_ORDER = [
    "tangent_0",
    "tangent_1",
    "tangent_2",
    "tangent_3",
    "base_0",
    "base_1",
    "base_2",
    "base_3",
]


def clean(value: sp.Expr) -> sp.Expr:
    # Full polynomial factorization of the post-step rational functions is
    # unnecessary and can dominate the entire certificate.  Cancellation is
    # the canonical algebraic operation needed here; the interval evaluator
    # factors only the small denominator when it needs a separated reciprocal.
    return sp.cancel(sp.together(value))


def frac(value: sp.Expr | Fraction | int) -> Fraction:
    value = sp.Rational(value)
    return Fraction(int(value.p), int(value.q))


def enc(value: sp.Expr | Fraction | int) -> str:
    return str(frac(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def model_content_valid(model: dict) -> bool:
    payload = dict(model)
    expected = payload.pop("content_sha256", None)
    return expected is not None and canonical_hash(payload) == expected


def model_chain_valid(initial: dict, successor: dict) -> bool:
    return (
        model_content_valid(initial)
        and model_content_valid(successor)
        and successor.get("parent_sha256") == initial.get("content_sha256")
    )


def omega_box(radius: sp.Rational) -> CI:
    center = frac(OMEGA_CENTER)
    rad = frac(radius)
    return CI(RI(center - rad, center + rad), RI(-rad, rad))


def rho_box(center: sp.Rational, radius: sp.Rational) -> CI:
    c = frac(center)
    rad = frac(radius)
    return CI(RI(c - rad, c + rad), RI(-rad, rad))


def point_ci(value: sp.Expr) -> CI:
    return eval_rational_rect(clean(value), {})


def norm_upper(value: sp.Expr, environment: dict[sp.Symbol, CI]) -> Fraction:
    return eval_rational_rect(clean(value), environment).norm_one_hi()


def interval_min_abs(interval: RI) -> Fraction:
    if interval.lo <= 0 <= interval.hi:
        return Fraction(0)
    return min(abs(interval.lo), abs(interval.hi))


def modulus_lower_linf(value: CI) -> Fraction:
    return max(interval_min_abs(value.re), interval_min_abs(value.im))


def row_norm_bound(
    matrix: sp.Matrix, environment: dict[sp.Symbol, CI]
) -> tuple[list[Fraction], Fraction]:
    rows = [
        sum(
            (
                norm_upper(matrix[row, column], environment)
                for column in range(matrix.cols)
            ),
            Fraction(0),
        )
        for row in range(matrix.rows)
    ]
    return rows, max(rows)


def uniform_levelt_tail(data: dict) -> dict:
    """Reissue the Levelt majorant uniformly on the complex omega disk."""
    w = omega_box(OMEGA_CAUCHY_RADIUS)
    rho = CI(
        RI(-frac(levelt.CAUCHY_RADIUS), frac(levelt.CAUCHY_RADIUS)),
        RI(-frac(levelt.CAUCHY_RADIUS), frac(levelt.CAUCHY_RADIUS)),
    )
    base_rows, majorant_base = row_norm_bound(
        data["regular_base"], {levelt.W: w, levelt.RHO: rho}
    )
    tangent_rows, majorant_tangent = row_norm_bound(
        data["tangent"], {levelt.W: w, levelt.RHO: rho}
    )
    pivot_constant = Fraction(levelt.PIVOT_CONSTANT)
    finite = []
    for n in range(2, 13):
        inverse = (n * sp.eye(4) - data["residue"]).inv().applyfunc(clean)
        rows, bound = row_norm_bound(inverse, {levelt.W: w})
        scaled = n * bound
        if scaled >= pivot_constant:
            raise RuntimeError(f"uniform Levelt pivot failed at n={n}")
        finite.append(
            {
                "n": n,
                "row_bounds": [str(value) for value in rows],
                "n_norm_upper": str(scaled),
            }
        )
    residue_rows, residue_bound = row_norm_bound(
        data["residue"], {levelt.W: w}
    )
    if residue_bound >= 13 or Fraction(13, 1) / (13 - residue_bound) >= 3:
        raise RuntimeError("uniform large-n Levelt pivot failed")
    f1_bound = max(
        norm_upper(value, {levelt.W: w}) for value in data["f"][1]
    )
    if f1_bound > pivot_constant * majorant_base:
        raise RuntimeError("uniform resonant f1 domination failed")

    p = pivot_constant * majorant_base * frac(levelt.CAUCHY_RADIUS)
    q = pivot_constant * majorant_tangent * frac(levelt.CAUCHY_RADIUS)
    x = frac(levelt.RHO0 / levelt.CAUCHY_RADIUS)
    coefficient_value = Fraction(1)
    harmonic = Fraction(0)
    for n in range(1, levelt.ORDER + 2):
        harmonic += Fraction(1, 1) / (p + n - 1)
        coefficient_value *= (p + n - 1) / n
    first_base = coefficient_value * x ** (levelt.ORDER + 1)
    first_tangent = (
        q
        * coefficient_value
        * harmonic
        * x ** (levelt.ORDER + 1)
    )
    ratio_base = x * (p + levelt.ORDER + 1) / (levelt.ORDER + 2)
    ratio_tangent = (
        x * (levelt.ORDER + 1 + 2 * p) / (levelt.ORDER + 2)
    )
    if not (0 <= ratio_base < 1 and 0 <= ratio_tangent < 1):
        raise RuntimeError("uniform Levelt tail ratio failed")
    return {
        "omega_box_radius": enc(OMEGA_CAUCHY_RADIUS),
        "base_rows": [str(value) for value in base_rows],
        "tangent_rows": [str(value) for value in tangent_rows],
        "majorant_base": str(majorant_base),
        "majorant_tangent": str(majorant_tangent),
        "finite_inverse_bounds": finite,
        "residue_rows": [str(value) for value in residue_rows],
        "residue_bound": str(residue_bound),
        "f1_bound": str(f1_bound),
        "p": str(p),
        "q": str(q),
        "x": str(x),
        "ratio_base": str(ratio_base),
        "ratio_tangent": str(ratio_tangent),
        # CI uses the complex 1-norm.  The majorant itself is already a
        # complex-component bound, so it is retained as the coupled l-infinity
        # radius rather than issued as independent real/imaginary boxes.
        "tail_base": str(first_base / (1 - ratio_base)),
        "tail_tangent": str(first_tangent / (1 - ratio_tangent)),
    }


def normalize_dual_nominal(
    tangent: list[sp.Expr],
    base: list[sp.Expr],
    error: Fraction,
    error_radius: sp.Rational,
    analytic_radius: sp.Rational,
) -> tuple[list[sp.Expr], list[sp.Expr], Fraction, dict]:
    """Normalize a dual line and bound the coupled perturbation."""
    error_env = {levelt.W: omega_box(error_radius)}
    analytic_env = {levelt.W: omega_box(analytic_radius)}
    s0 = clean(base[PIVOT])
    s_error_ci = eval_rational_rect(s0, error_env)
    s_analytic_ci = eval_rational_rect(s0, analytic_env)
    lower0 = modulus_lower_linf(s_error_ci)
    analytic_lower = modulus_lower_linf(s_analytic_ci)
    lower = lower0 - error
    if lower <= 0 or analytic_lower <= 0:
        raise RuntimeError("correlated pivot denominator is not separated")

    normalized_base = [clean(value / s0) for value in base]
    normalized_tangent = [
        clean((tangent[index] - normalized_base[index] * tangent[PIVOT]) / s0)
        for index in range(4)
    ]
    normalized_base[PIVOT] = sp.Integer(1)
    normalized_tangent[PIVOT] = sp.Integer(0)

    base_differences: list[Fraction] = []
    tangent_differences: list[Fraction] = []
    s_upper = s_error_ci.norm_one_hi()
    tangent_pivot_upper = norm_upper(tangent[PIVOT], error_env)
    for index in range(4):
        if index == PIVOT:
            base_differences.append(Fraction(0))
            tangent_differences.append(Fraction(0))
            continue
        base_upper = norm_upper(base[index], error_env)
        base_diff = error * (s_upper + base_upper) / (lower0 * lower)
        base_differences.append(base_diff)
        normalized_base_upper = norm_upper(normalized_base[index], error_env)
        numerator0 = clean(
            tangent[index] - normalized_base[index] * tangent[PIVOT]
        )
        numerator0_upper = norm_upper(numerator0, error_env)
        numerator_diff = (
            error
            + base_diff * (tangent_pivot_upper + error)
            + normalized_base_upper * error
        )
        tangent_diff = (
            numerator_diff / lower
            + numerator0_upper * error / (lower0 * lower)
        )
        tangent_differences.append(tangent_diff)
    normalized_error = max([*base_differences, *tangent_differences])
    return (
        normalized_tangent,
        normalized_base,
        normalized_error,
        {
            "pivot": PIVOT,
            "nominal_modulus_lower_error_domain": str(lower0),
            "full_denominator_modulus_lower": str(lower),
            "nominal_modulus_lower_analytic_domain": str(analytic_lower),
            "input_coupled_residual": str(error),
            "base_perturbation_bounds": [str(value) for value in base_differences],
            "tangent_perturbation_bounds": [
                str(value) for value in tangent_differences
            ],
            "normalized_coupled_residual": str(normalized_error),
            "exact_base_pivot": "1",
            "exact_tangent_pivot": "0",
        },
    )


def omega_coefficients(functions: list[sp.Expr]) -> list[list[sp.Expr]]:
    return [
        [
            clean(
                sp.diff(function, levelt.W, degree).subs(
                    levelt.W, OMEGA_CENTER
                )
                / sp.factorial(degree)
            )
            for function in functions
        ]
        for degree in range(OMEGA_ORDER + 1)
    ]


def coefficient_norm(value: sp.Expr) -> Fraction:
    return norm_upper(value, {})


def omega_model(
    functions: list[sp.Expr],
    physical_residual: Fraction,
    parent_sha256: str | None,
    stage: str,
    rho: sp.Rational,
    pivot_constraints: bool,
) -> tuple[dict, list[sp.Expr], Fraction]:
    coefficients = omega_coefficients(functions)
    q = frac(OMEGA_RADIUS / OMEGA_CAUCHY_RADIUS)
    outer_env = {levelt.W: omega_box(OMEGA_CAUCHY_RADIUS)}
    function_bounds = [norm_upper(function, outer_env) for function in functions]
    remainders = [
        bound * q ** (OMEGA_ORDER + 1) / (1 - q)
        for bound in function_bounds
    ]
    omega_remainder = max(remainders)
    coupled_residual = physical_residual + omega_remainder
    zeta = levelt.W - OMEGA_CENTER
    polynomial_functions = [
        clean(
            sum(
                (
                    coefficients[degree][index] * zeta**degree
                    for degree in range(OMEGA_ORDER + 1)
                ),
                sp.Integer(0),
            )
        )
        for index in range(len(functions))
    ]
    affine_generator = [
        clean(OMEGA_RADIUS * coefficients[1][index])
        for index in range(len(functions))
    ]
    payload = {
        "schema": "phase3-correlated-omega-dual-tau-model-v1",
        "stage": stage,
        "rho": enc(rho),
        "r": enc(rho + 2),
        "parent_sha256": parent_sha256,
        "state_order": STATE_ORDER,
        "omega_model": {
            "coordinate": "zeta=omega-omega_center",
            "omega_center": enc(OMEGA_CENTER),
            "omega_radius": enc(OMEGA_RADIUS),
            "cauchy_radius": enc(OMEGA_CAUCHY_RADIUS),
            "degree": OMEGA_ORDER,
            "shared_parameter": "xi_omega=zeta/omega_radius, |xi_omega|<=1",
        },
        "dual_tau_state": {
            "ordering": "tangent_then_base",
            "same_omega_parameter_for_both_rails": True,
        },
        "polynomial_coefficients": [
            {
                "degree": degree,
                "values": [sp.sstr(value) for value in coefficients[degree]],
            }
            for degree in range(OMEGA_ORDER + 1)
        ],
        "affine_generators": [
            {
                "noise": "xi_omega",
                "semantics": (
                    "derived shared linear part; not additional to the "
                    "polynomial coefficients"
                ),
                "values": [sp.sstr(value) for value in affine_generator],
            }
        ],
        "shared_noise_domain": {
            "xi_omega": "complex unit disk",
            "independent_component_noise_symbols": 0,
        },
        "nonlinear_polynomial_terms": "degrees 2 through omega_order",
        "residual_norm_ball": {
            "norm": "complex vector l_infinity using |Re|+|Im| per component",
            "radius": str(coupled_residual),
            "physical_transport_or_seed_part": str(physical_residual),
            "omega_cauchy_remainder_part": str(omega_remainder),
            "componentwise_independent_boxes": False,
        },
        "radial_taylor_coefficients": (
            "not_applicable_at_seed"
            if stage == "normalized_symbolic_seed"
            else "bound_in_successor_step_metadata"
        ),
        "pivot_constraints": {
            "enabled": pivot_constraints,
            "base_pivot_state_index": 4 + PIVOT,
            "tangent_pivot_state_index": PIVOT,
            "exact_base_pivot": "1" if pivot_constraints else None,
            "exact_tangent_pivot": "0" if pivot_constraints else None,
            "residual_zero_on_pivot_coordinates": pivot_constraints,
        },
        "analytic_bounds": {
            "outer_function_norm_one_bounds": [
                str(value) for value in function_bounds
            ],
            "omega_remainders": [str(value) for value in remainders],
        },
    }
    payload["content_sha256"] = canonical_hash(payload)
    return payload, polynomial_functions, coupled_residual


def matrix_rho_coefficients(
    generator: sp.Matrix, order: int
) -> list[sp.Matrix]:
    rho0 = sp.Rational(
        transport.RHO0.numerator, transport.RHO0.denominator
    )
    return [
        generator.applyfunc(
            lambda value: clean(
                sp.diff(value, levelt.RHO, degree).subs(levelt.RHO, rho0)
                / sp.factorial(degree)
            )
        )
        for degree in range(order)
    ]


def radial_nominal_step(
    generator: sp.Matrix, initial: list[sp.Expr]
) -> tuple[list[sp.Expr], list[list[sp.Expr]]]:
    matrix_coefficients = matrix_rho_coefficients(generator, RADIAL_ORDER)
    coefficients = [sp.Matrix(initial)]
    for degree in range(RADIAL_ORDER - 1):
        next_value = sum(
            (
                matrix_coefficients[power] * coefficients[degree - power]
                for power in range(degree + 1)
            ),
            sp.zeros(len(initial), 1),
        ) / (degree + 1)
        coefficients.append(next_value.applyfunc(clean))
    endpoint = sum(
        (
            coefficients[degree] * RADIAL_STEP**degree
            for degree in range(RADIAL_ORDER)
        ),
        sp.zeros(len(initial), 1),
    ).applyfunc(clean)
    return list(endpoint), [list(column) for column in coefficients]


def polynomial_bound(functions: list[sp.Expr], radius: sp.Rational) -> Fraction:
    environment = {levelt.W: omega_box(radius)}
    return max(norm_upper(value, environment) for value in functions)


def generator_hash(generator: sp.Matrix) -> str:
    return canonical_hash(
        [
            [sp.sstr(clean(generator[i, j])) for j in range(generator.cols)]
            for i in range(generator.rows)
        ]
    )


def compute() -> dict:
    crosswalk = json.loads(transport.CROSSWALK.read_text())
    data = levelt.exact_data(crosswalk)
    tail = uniform_levelt_tail(data)
    raw_seed_error = max(
        Fraction(tail["tail_base"]), Fraction(tail["tail_tangent"])
    )
    initial_tangent, initial_base, initial_physical_error, initial_pivot = (
        normalize_dual_nominal(
            list(data["tangent_seed"]),
            list(data["base_seed"]),
            raw_seed_error,
            OMEGA_CAUCHY_RADIUS,
            OMEGA_CAUCHY_RADIUS,
        )
    )
    initial_functions = [*initial_tangent, *initial_base]
    initial_model, initial_polynomial, initial_model_error = omega_model(
        initial_functions,
        initial_physical_error,
        None,
        "normalized_symbolic_seed",
        sp.Rational(transport.RHO0.numerator, transport.RHO0.denominator),
        True,
    )
    if initial_model["pivot_constraints"]["exact_base_pivot"] != "1":
        raise RuntimeError("initial exact pivot drift")

    generator = transport.block_generator(data["base"], data["tangent"])
    nominal_endpoint, radial_coefficients = radial_nominal_step(
        generator, initial_polynomial
    )
    rho0 = sp.Rational(transport.RHO0.numerator, transport.RHO0.denominator)
    generator_rows, generator_bound = row_norm_bound(
        generator,
        {
            levelt.W: omega_box(OMEGA_RADIUS),
            levelt.RHO: rho_box(rho0, RADIAL_CAUCHY_RADIUS),
        },
    )
    scaled = frac(RADIAL_CAUCHY_RADIUS) * generator_bound
    if scaled >= 1:
        raise RuntimeError("radial Cauchy self-map failed")
    initial_norm = polynomial_bound(initial_polynomial, OMEGA_RADIUS)
    ratio = frac(RADIAL_STEP / RADIAL_CAUCHY_RADIUS)
    radial_tail = (
        initial_norm
        / (1 - scaled)
        * ratio**RADIAL_ORDER
        / (1 - ratio)
    )
    real_step_scaled = frac(RADIAL_STEP) * generator_bound
    if real_step_scaled >= 1:
        raise RuntimeError("radial residual propagation failed")
    propagated_initial_error = initial_model_error / (1 - real_step_scaled)
    raw_endpoint_error = propagated_initial_error + radial_tail

    endpoint_tangent = nominal_endpoint[:4]
    endpoint_base = nominal_endpoint[4:]
    successor_tangent, successor_base, successor_physical_error, successor_pivot = (
        normalize_dual_nominal(
            endpoint_tangent,
            endpoint_base,
            raw_endpoint_error,
            OMEGA_RADIUS,
            OMEGA_CAUCHY_RADIUS,
        )
    )
    successor_functions = [*successor_tangent, *successor_base]
    successor_model, _, successor_model_error = omega_model(
        successor_functions,
        successor_physical_error,
        initial_model["content_sha256"],
        "normalized_one_radial_step_successor",
        rho0 + RADIAL_STEP,
        True,
    )
    if successor_model_error >= 1:
        raise RuntimeError("successor coupled residual is too large for pivot")

    radial_metadata = {
        "rho_start": enc(rho0),
        "rho_endpoint": enc(rho0 + RADIAL_STEP),
        "step": enc(RADIAL_STEP),
        "order": RADIAL_ORDER,
        "cauchy_radius": enc(RADIAL_CAUCHY_RADIUS),
        "generator_sha256": generator_hash(generator),
        "generator_row_bounds": [str(value) for value in generator_rows],
        "generator_norm_upper": str(generator_bound),
        "cauchy_scaled_norm": str(scaled),
        "initial_polynomial_norm_upper": str(initial_norm),
        "tail_ratio": str(ratio),
        "radial_tail": str(radial_tail),
        "initial_model_residual": str(initial_model_error),
        "residual_propagation_denominator": str(1 - real_step_scaled),
        "propagated_initial_residual": str(propagated_initial_error),
        "raw_endpoint_coupled_residual": str(raw_endpoint_error),
        "coefficient_hash": canonical_hash(
            [
                [sp.sstr(value) for value in coefficient]
                for coefficient in radial_coefficients
            ]
        ),
        "coefficient_degrees": list(range(RADIAL_ORDER)),
    }
    successor_model["radial_taylor_coefficients"] = radial_metadata
    # Re-hash after binding the complete radial step metadata.
    successor_model.pop("content_sha256")
    successor_model["content_sha256"] = canonical_hash(successor_model)

    return {
        "schema": "phase3-axial-horizon-correlated-affine-seed-successor-run-v1",
        "frequency_domain": {
            "center": enc(OMEGA_CENTER),
            "radius": enc(OMEGA_RADIUS),
            "complex_disk": True,
        },
        "source": {
            "restart_contract": {
                "path": str(
                    (
                        HERE / "correlated-affine-export-audit-certificate.json"
                    ).relative_to(ROOT)
                ),
                "sha256": sha256(
                    HERE / "correlated-affine-export-audit-certificate.json"
                ),
            },
            "crosswalk": {
                "path": str(transport.CROSSWALK.relative_to(ROOT)),
                "sha256": sha256(transport.CROSSWALK),
            },
            "symbolic_levelt": {
                "path": str(Path(levelt.__file__).relative_to(ROOT)),
                "sha256": sha256(Path(levelt.__file__)),
            },
        },
        "uniform_levelt_tail": tail,
        "initial_normalization": initial_pivot,
        "initial_model": initial_model,
        "radial_step": radial_metadata,
        "successor_normalization": successor_pivot,
        "successor_model": successor_model,
        "content_chain": {
            "initial_sha256": initial_model["content_sha256"],
            "successor_parent_sha256": successor_model["parent_sha256"],
            "successor_sha256": successor_model["content_sha256"],
            "parent_bound": (
                successor_model["parent_sha256"]
                == initial_model["content_sha256"]
            ),
        },
        "terminal": {
            "gate": None,
            "rho": enc(rho0 + RADIAL_STEP),
            "one_radial_successor_certified": True,
        },
        "claim_flags": {
            "symbolic_pre_omega_substitution_seed_used": True,
            "uniform_complex_omega_levelt_tail_certified": True,
            "shared_omega_parameter_serialized": True,
            "dual_tau_rails_share_parameter": True,
            "independent_component_remainders_used": False,
            "coupled_residual_serialized": True,
            "initial_projective_pivot_certified": True,
            "initial_projective_normalization_certified": True,
            "one_radial_taylor_step_certified": True,
            "successor_projective_pivot_certified": True,
            "successor_projective_normalization_certified": True,
            "content_addressed_model_chain": True,
            "next_base_panel_completed": False,
            "r4_reached": False,
            "H4_certified": False,
            "T_plus_certified": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
