#!/usr/bin/env python3
"""Multipanel joint omega/radial Taylor continuation without Cartesian wrapping."""
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
    eval_rect,
)
from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt
from . import checkpoint_transport as transport
from . import correlated_affine_seed_successor as seed

sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_RUN = HERE / "correlated-affine-seed-successor-run.json"
ADAPTIVE_RUN = HERE / "adaptive-chart-separation-run.json"
RUN = HERE / "correlated-affine-multipanel-successor-run.json"

STEPS = 33
RADIAL_ORDER = 6
STEP = sp.Rational(transport.RHO0.numerator, transport.RHO0.denominator) / 64
CAUCHY_RADIUS = 4 * STEP


def clean(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def frac(value: sp.Expr | str | int) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    value = sp.Rational(value)
    return Fraction(int(value.p), int(value.q))


def enc(value: sp.Expr | Fraction | int) -> str:
    return str(frac(value))


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


Gaussian = tuple[Fraction, Fraction]
ZERO: Gaussian = (Fraction(0), Fraction(0))


def gaussian(value: sp.Expr) -> Gaussian:
    real, imag = sp.expand_complex(value).as_real_imag()
    real = sp.Rational(real)
    imag = sp.Rational(imag)
    return (
        Fraction(int(real.p), int(real.q)),
        Fraction(int(imag.p), int(imag.q)),
    )


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gscale(value: Gaussian, scalar: Fraction) -> Gaussian:
    return value[0] * scalar, value[1] * scalar


def gnorm(value: Gaussian) -> Fraction:
    return abs(value[0]) + abs(value[1])


def gstring(value: Gaussian) -> str:
    real, imag = value
    if imag == 0:
        return str(real)
    if real == 0:
        return f"({imag})*I"
    sign = "+" if imag >= 0 else "-"
    return f"({real}){sign}({abs(imag)})*I"


def parse_coefficients(model: dict) -> list[list[Gaussian]]:
    return [
        [
            gaussian(sp.sympify(value, locals={"I": sp.I}))
            for value in row["values"]
        ]
        for row in model["polynomial_coefficients"]
    ]


def polynomial_bound(
    coefficients: list[list[Gaussian]], radius: sp.Rational
) -> Fraction:
    r = frac(radius)
    bounds = []
    for state_index in range(len(seed.STATE_ORDER)):
        bounds.append(
            sum(
                (
                    gnorm(coefficients[degree][state_index])
                    * r**degree
                    for degree in range(seed.OMEGA_ORDER + 1)
                ),
                Fraction(0),
            )
        )
    return max(bounds)


def pivot_gate(
    coefficients: list[list[Gaussian]], residual: Fraction
) -> dict:
    state_index = 4 + seed.PIVOT
    center = coefficients[0][state_index]
    center_lower = max(abs(center[0]), abs(center[1]))
    variation = sum(
        (
            gnorm(coefficients[degree][state_index])
            * frac(seed.OMEGA_RADIUS) ** degree
            for degree in range(1, seed.OMEGA_ORDER + 1)
        ),
        Fraction(0),
    )
    lower = center_lower - variation - residual
    return {
        "row": "e2",
        "state_index": state_index,
        "center_modulus_lower": str(center_lower),
        "polynomial_variation_upper": str(variation),
        "coupled_residual": str(residual),
        "full_modulus_lower": str(lower),
        "excludes_zero": lower > 0,
    }


def generator_joint_coefficients(generator: sp.Matrix) -> list[list[sp.Matrix]]:
    rho0 = levelt.RHO
    omega0 = levelt.W
    expressions = []
    for radial_degree in range(RADIAL_ORDER):
        radial = generator.applyfunc(
            lambda value: sp.diff(value, levelt.RHO, radial_degree)
            / sp.factorial(radial_degree)
        )
        row = []
        for omega_degree in range(seed.OMEGA_ORDER + 1):
            row.append(
                radial.applyfunc(
                    lambda value: clean(
                        sp.diff(value, levelt.W, omega_degree)
                        / sp.factorial(omega_degree)
                    )
                )
            )
        expressions.append(row)
    return expressions


class CachedRational:
    """Rational rectangle evaluator with one-time denominator factorization."""

    def __init__(self, value: sp.Expr):
        numerator, denominator = sp.fraction(sp.cancel(value))
        coefficient, factors = sp.factor_list(denominator)
        self.numerator = numerator
        self.coefficient = coefficient
        self.factors = factors

    def norm_upper(self, environment: dict[sp.Symbol, CI]) -> Fraction:
        value = eval_rect(self.numerator, environment) / eval_rect(
            self.coefficient, environment
        )
        for factor, multiplicity in self.factors:
            value = value / eval_rect(factor, environment).power(multiplicity)
        return value.norm_one_hi()


def cached_generator(generator: sp.Matrix) -> list[list[CachedRational]]:
    return [
        [CachedRational(generator[row, column]) for column in range(generator.cols)]
        for row in range(generator.rows)
    ]


def cached_row_norm_bound(
    generator: list[list[CachedRational]],
    environment: dict[sp.Symbol, CI],
) -> Fraction:
    return max(
        sum(
            (entry.norm_upper(environment) for entry in row),
            Fraction(0),
        )
        for row in generator
    )


def specialize_generator_coefficients(
    expressions: list[list[sp.Matrix]], rho: sp.Rational
) -> list[list[list[list[Gaussian]]]]:
    substitutions = {levelt.RHO: rho, levelt.W: seed.OMEGA_CENTER}
    return [
        [
            [
                [
                    gaussian(clean(matrix[row, column].subs(substitutions)))
                    for column in range(matrix.cols)
                ]
                for row in range(matrix.rows)
            ]
            for matrix in row
        ]
        for row in expressions
    ]


def joint_step(
    generator_coefficients: list[list[list[list[Gaussian]]]],
    initial: list[list[Gaussian]],
) -> tuple[list[list[Gaussian]], list[list[list[str]]]]:
    # c[n][q] is the coefficient of h^n zeta^q.
    size = len(seed.STATE_ORDER)
    c: list[list[list[Gaussian]]] = [
        [[value for value in initial[q]] for q in range(seed.OMEGA_ORDER + 1)]
    ]
    for n in range(RADIAL_ORDER - 1):
        next_row = []
        for q in range(seed.OMEGA_ORDER + 1):
            value = [ZERO for _ in range(size)]
            for radial_power in range(n + 1):
                for omega_power in range(q + 1):
                    matrix = generator_coefficients[radial_power][omega_power]
                    vector = c[n - radial_power][q - omega_power]
                    for row in range(size):
                        product = ZERO
                        for column in range(size):
                            product = gadd(
                                product,
                                gmul(matrix[row][column], vector[column]),
                            )
                        value[row] = gadd(value[row], product)
            next_row.append(
                [gscale(entry, Fraction(1, n + 1)) for entry in value]
            )
        c.append(next_row)
    endpoint = []
    for q in range(seed.OMEGA_ORDER + 1):
        value = [ZERO for _ in range(size)]
        for n in range(RADIAL_ORDER):
            scalar = frac(STEP) ** n
            for row in range(size):
                value[row] = gadd(value[row], gscale(c[n][q][row], scalar))
        endpoint.append(value)
    serialized_radial = [
        [
            [gstring(value) for value in c[n][q]]
            for q in range(seed.OMEGA_ORDER + 1)
        ]
        for n in range(RADIAL_ORDER)
    ]
    return endpoint, serialized_radial


def transport_bounds(
    generator: list[list[CachedRational]],
    coefficients: list[list[sp.Expr]],
    residual: Fraction,
    rho: sp.Rational,
) -> tuple[Fraction, dict]:
    outer_complex_env = {
        levelt.W: seed.omega_box(seed.OMEGA_CAUCHY_RADIUS),
        levelt.RHO: seed.rho_box(rho, CAUCHY_RADIUS),
    }
    complex_bound = cached_row_norm_bound(generator, outer_complex_env)
    scaled = frac(CAUCHY_RADIUS) * complex_bound
    if scaled >= 1:
        raise RuntimeError("multipanel radial Cauchy self-map failed")
    outer_poly = polynomial_bound(
        coefficients, seed.OMEGA_CAUCHY_RADIUS
    )
    radial_ratio = frac(STEP / CAUCHY_RADIUS)
    radial_tail = (
        outer_poly
        / (1 - scaled)
        * radial_ratio**RADIAL_ORDER
        / (1 - radial_ratio)
    )

    inner_real_env = {
        levelt.W: seed.omega_box(seed.OMEGA_RADIUS),
        levelt.RHO: CI(RI(frac(rho), frac(rho + STEP)), RI(0)),
    }
    inner_real_bound = cached_row_norm_bound(generator, inner_real_env)
    inner_step_scaled = frac(STEP) * inner_real_bound
    if inner_step_scaled >= 1:
        raise RuntimeError("inner residual propagation failed")
    propagated = residual / (1 - inner_step_scaled)

    outer_real_env = {
        levelt.W: seed.omega_box(seed.OMEGA_CAUCHY_RADIUS),
        levelt.RHO: CI(RI(frac(rho), frac(rho + STEP)), RI(0)),
    }
    outer_real_bound = cached_row_norm_bound(generator, outer_real_env)
    outer_step_scaled = frac(STEP) * outer_real_bound
    if outer_step_scaled >= 1:
        raise RuntimeError("outer nominal propagation failed")
    solution_outer = outer_poly / (1 - outer_step_scaled)
    omega_ratio = frac(seed.OMEGA_RADIUS / seed.OMEGA_CAUCHY_RADIUS)
    omega_tail = (
        (solution_outer + radial_tail)
        * omega_ratio ** (seed.OMEGA_ORDER + 1)
        / (1 - omega_ratio)
    )
    new_residual = propagated + radial_tail + omega_tail
    return new_residual, {
        "complex_generator_norm_upper": str(complex_bound),
        "cauchy_scaled_norm": str(scaled),
        "outer_polynomial_norm_upper": str(outer_poly),
        "radial_ratio": str(radial_ratio),
        "radial_tail": str(radial_tail),
        "inner_real_generator_norm_upper": str(inner_real_bound),
        "inner_step_scaled_norm": str(inner_step_scaled),
        "propagated_input_residual": str(propagated),
        "outer_real_generator_norm_upper": str(outer_real_bound),
        "outer_step_scaled_norm": str(outer_step_scaled),
        "nominal_solution_outer_bound": str(solution_outer),
        "omega_ratio": str(omega_ratio),
        "omega_tail": str(omega_tail),
        "output_coupled_residual": str(new_residual),
    }


def checkpoint(
    index: int,
    rho: sp.Rational,
    coefficients: list[list[Gaussian]],
    residual: Fraction,
    parent: str,
    step_metadata: dict,
    radial_coefficients: list[list[list[sp.Expr]]],
) -> dict:
    gate = pivot_gate(coefficients, residual)
    payload = {
        "schema": "phase3-correlated-multipanel-checkpoint-v1",
        "index": index,
        "rho": enc(rho),
        "r": enc(rho + 2),
        "parent_sha256": parent,
        "state_order": seed.STATE_ORDER,
        "omega_model": {
            "center": enc(seed.OMEGA_CENTER),
            "radius": enc(seed.OMEGA_RADIUS),
            "degree": seed.OMEGA_ORDER,
            "shared_parameter": "xi_omega",
        },
        "dual_tau_shared_parameter": True,
        "polynomial_coefficients": [
            {
                "degree": degree,
                "values": [gstring(value) for value in coefficients[degree]],
            }
            for degree in range(seed.OMEGA_ORDER + 1)
        ],
        "affine_generator": {
            "noise": "xi_omega",
            "values": [
                gstring(gscale(value, frac(seed.OMEGA_RADIUS)))
                for value in coefficients[1]
            ],
        },
        "coupled_residual": {
            "norm": "complex vector l_infinity using |Re|+|Im|",
            "radius": str(residual),
            "componentwise_independent_boxes": False,
        },
        "pivot_gate": gate,
        "step_metadata": step_metadata,
        "radial_coefficient_sha256": canonical_hash(radial_coefficients),
    }
    payload["content_sha256"] = canonical_hash(payload)
    return payload


def checkpoint_valid(value: dict) -> bool:
    payload = dict(value)
    expected = payload.pop("content_sha256", None)
    return expected is not None and canonical_hash(payload) == expected


def compute() -> dict:
    source = json.loads(SOURCE_RUN.read_text())
    adaptive = json.loads(ADAPTIVE_RUN.read_text())
    initial_model = source["initial_model"]
    if not seed.model_content_valid(initial_model):
        raise RuntimeError("source correlated seed model hash drift")
    coefficients = parse_coefficients(initial_model)
    residual = Fraction(initial_model["residual_norm_ball"]["radius"])
    rho = sp.Rational(transport.RHO0.numerator, transport.RHO0.denominator)

    crosswalk = json.loads(transport.CROSSWALK.read_text())
    data = levelt.exact_data(crosswalk)
    generator = transport.block_generator(data["base"], data["tangent"])
    bounded_generator = cached_generator(generator)
    symbolic_joint = generator_joint_coefficients(generator)
    joint_generator_sha256 = canonical_hash(
        [
            [
                [
                    [sp.sstr(value) for value in matrix.row(row)]
                    for row in range(matrix.rows)
                ]
                for matrix in radial
            ]
            for radial in symbolic_joint
        ]
    )

    parent = initial_model["content_sha256"]
    checkpoints = []
    for index in range(STEPS):
        specialized = specialize_generator_coefficients(symbolic_joint, rho)
        endpoint, radial_coefficients = joint_step(specialized, coefficients)
        new_residual, metadata = transport_bounds(
            bounded_generator, coefficients, residual, rho
        )
        rho += STEP
        row = checkpoint(
            index,
            rho,
            endpoint,
            new_residual,
            parent,
            metadata,
            radial_coefficients,
        )
        if not row["pivot_gate"]["excludes_zero"]:
            raise RuntimeError(
                f"correlated pivot failed at multipanel index {index}"
            )
        if not checkpoint_valid(row):
            raise RuntimeError("checkpoint self-hash drift")
        checkpoints.append(row)
        parent = row["content_sha256"]
        coefficients = endpoint
        residual = new_residual

    former_endpoint = sp.Rational(
        adaptive["terminal_raw_enclosure"]["rho"]
    )
    crossed = rho >= former_endpoint
    if not crossed:
        raise RuntimeError("multipanel rail did not cross former obstruction")
    final = checkpoints[-1]
    return {
        "schema": "phase3-axial-horizon-correlated-affine-multipanel-run-v1",
        "frequency_domain": source["frequency_domain"],
        "source": {
            "seed_successor_run": {
                "path": str(SOURCE_RUN.relative_to(ROOT)),
                "sha256": sha256(SOURCE_RUN),
                "initial_model_sha256": initial_model["content_sha256"],
            },
            "former_cartesian_obstruction": {
                "path": str(ADAPTIVE_RUN.relative_to(ROOT)),
                "sha256": sha256(ADAPTIVE_RUN),
                "rho": enc(former_endpoint),
            },
        },
        "controls": {
            "steps": STEPS,
            "step": enc(STEP),
            "radial_order": RADIAL_ORDER,
            "omega_order": seed.OMEGA_ORDER,
            "joint_generator_sha256": joint_generator_sha256,
            "normalization_during_multipanel_run": "none",
            "reason": (
                "retain one homogeneous correlated line and test a fixed "
                "projective denominator without repeated quotient wrapping"
            ),
        },
        "checkpoint_chain": checkpoints,
        "reached_rho": enc(rho),
        "former_obstruction_rho": enc(former_endpoint),
        "crossed_former_obstruction": crossed,
        "final_pivot_gate": final["pivot_gate"],
        "final_coupled_residual": final["coupled_residual"],
        "content_chain": {
            "source_sha256": initial_model["content_sha256"],
            "terminal_sha256": final["content_sha256"],
            "all_checkpoints_valid": all(checkpoint_valid(row) for row in checkpoints),
            "all_parent_links_valid": all(
                row["parent_sha256"]
                == (
                    initial_model["content_sha256"]
                    if index == 0
                    else checkpoints[index - 1]["content_sha256"]
                )
                for index, row in enumerate(checkpoints)
            ),
        },
        "terminal": {
            "gate": None,
            "rho": enc(rho),
            "crossed_former_cartesian_obstruction": crossed,
            "fixed_e2_denominator_excludes_zero": final["pivot_gate"][
                "excludes_zero"
            ],
        },
        "claim_flags": {
            "correlated_multipanel_transport_certified": True,
            "former_cartesian_obstruction_radius_crossed": crossed,
            "fixed_chart_denominator_excludes_zero_after_crossing": final[
                "pivot_gate"
            ]["excludes_zero"],
            "cartesian_zero_vector_wrapping_obstruction_removed_on_this_domain": (
                crossed and final["pivot_gate"]["excludes_zero"]
            ),
            "independent_component_remainders_used": False,
            "content_addressed_checkpoint_chain": True,
            "original_next_base_panel_completed": False,
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
