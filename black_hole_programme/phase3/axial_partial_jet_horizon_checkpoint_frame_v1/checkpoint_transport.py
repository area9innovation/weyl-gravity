#!/usr/bin/env python3
"""Validated exact-frequency transport of the canonical horizon jet frame.

The calculation deliberately separates the local endpoint-normalizer theorem
from radial transport.  At one exact real frequency it transports the
phase-factored spin-two carrier jet and the Levelt-factored spin-one lift.
Every panel is recentered by a complex dual scalar.  The common scalar is
recorded, rather than discarded, so the three physical jet columns can be
reconstructed at r=4.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import acb, acb_series, arb, ctx

from ..axial_partial_jet_horizon_moving_phase_v1 import produce as moving
from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "checkpoint-run.json"
CROSSWALK = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_transport_crosswalk_v1/certificate.json"
)

OMEGA = Fraction(4097, 8192)
RHO0 = Fraction(1, 2**22)
SHELLS = 23
PANELS = 64
ORDER = 16
CAUCHY_FACTOR = 4


def af(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(value.numerator) / arb(value.denominator)


def cf(value: sp.Expr) -> acb:
    value = sp.cancel(value)
    real, imag = sp.re(value), sp.im(value)
    if not (real.is_Rational and imag.is_Rational):
        raise TypeError(f"non-Gaussian-rational coefficient: {value}")
    return acb(
        arb(int(real.p)) / arb(int(real.q)),
        arb(int(imag.p)) / arb(int(imag.q)),
    )


def inflate(value: acb, radius: arb) -> acb:
    return value + acb(arb(0, radius), arb(0, radius))


def width(value: acb) -> arb:
    return max(value.real.rad(), value.imag.rad())


class RationalFunction:
    """A rational function in rho with exact Gaussian-rational coefficients."""

    def __init__(self, expression: sp.Expr):
        expression = sp.cancel(expression.subs(moving.W, sp.Rational(OMEGA)))
        numerator, denominator = sp.fraction(expression)
        self.numerator = [
            cf(x) for x in reversed(sp.Poly(numerator, moving.RHO).all_coeffs())
        ]
        self.denominator = [
            cf(x) for x in reversed(sp.Poly(denominator, moving.RHO).all_coeffs())
        ]

    @staticmethod
    def polynomial(coefficients: list[acb], x):
        out = coefficients[-1]
        for coefficient in reversed(coefficients[:-1]):
            out = out * x + coefficient
        return out

    def series(self, center: Fraction, order: int) -> list[acb]:
        x = acb_series([acb(af(center)), acb(1)], order)
        numerator = self.polynomial(self.numerator, x)
        denominator = self.polynomial(self.denominator, x)
        quotient = numerator / denominator
        if isinstance(quotient, acb):
            return [quotient, *[acb(0) for _ in range(order - 1)]]
        return [quotient[index] for index in range(order)]

    def ball(self, center: Fraction, radius: Fraction) -> acb:
        x = acb(arb(af(center), af(radius)))
        return self.polynomial(self.numerator, x) / self.polynomial(
            self.denominator, x
        )


def compile_matrix(matrix: sp.Matrix) -> list[list[RationalFunction]]:
    return [
        [RationalFunction(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def block_generator(base: sp.Matrix, tangent: sp.Matrix):
    size = base.rows
    out = sp.zeros(2 * size)
    out[:size, :size] = tangent
    out[:size, size:] = base
    out[size:, size:] = base
    return out


def matrix_series(
    matrix: list[list[RationalFunction]], center: Fraction, order: int
) -> list[list[list[acb]]]:
    return [
        [entry.series(center, order) for entry in row] for row in matrix
    ]


def matrix_bound(
    matrix: list[list[RationalFunction]], center: Fraction, radius: Fraction
) -> arb:
    best = arb(0)
    for row in matrix:
        total = sum((entry.ball(center, radius).abs_upper() for entry in row), arb(0))
        best = max(best, total)
    return best


def vector_norm(vector: list[acb]) -> arb:
    return max((entry.abs_upper() for entry in vector), default=arb(0))


def taylor_step(
    matrix: list[list[RationalFunction]],
    state: list[acb],
    start: Fraction,
    step: Fraction,
) -> tuple[list[acb] | None, dict]:
    center = start
    radius = abs(step) * CAUCHY_FACTOR
    bound = matrix_bound(matrix, center, radius)
    scaled = af(radius) * bound
    if scaled >= 1:
        return None, {
            "gate": "CAUCHY_SELF_MAP",
            "scaled_norm": str(scaled),
            "center": str(center),
            "radius": str(radius),
        }
    majorant = vector_norm(state) / (1 - scaled)
    coefficients = [list(state)]
    series = matrix_series(matrix, center, ORDER)
    size = len(state)
    for degree in range(ORDER - 1):
        next_coefficient = []
        for row in range(size):
            value = acb(0)
            for power in range(degree + 1):
                for column in range(size):
                    value += (
                        series[row][column][power]
                        * coefficients[degree - power][column]
                    )
            next_coefficient.append(value / (degree + 1))
        coefficients.append(next_coefficient)
    result = [acb(0) for _ in state]
    power = arb(1)
    h = af(step)
    for coefficient in coefficients:
        for row in range(size):
            result[row] += coefficient[row] * power
        power *= h
    ratio = af(abs(step)) / af(radius)
    tail = majorant * ratio**ORDER / (1 - ratio)
    result = [inflate(value, tail) for value in result]
    return result, {
        "gate": None,
        "scaled_norm": str(scaled),
        "tail": str(tail),
    }


@dataclass
class DualLine:
    tangent: list[acb]
    base: list[acb]
    amplitude: acb
    amplitude_tangent: acb
    pivot: int = -1

    def packed(self) -> list[acb]:
        return [*self.tangent, *self.base]

    @classmethod
    def unpacked(
        cls, packed: list[acb], amplitude: acb, amplitude_tangent: acb
    ) -> "DualLine":
        half = len(packed) // 2
        return cls(packed[:half], packed[half:], amplitude, amplitude_tangent)

    def normalize(self, allowed: tuple[int, ...] | None = None) -> dict:
        candidates = allowed or tuple(range(len(self.base)))
        pivot = max(candidates, key=lambda index: self.base[index].abs_lower())
        scalar = self.base[pivot]
        if scalar.abs_lower() <= 0:
            return {"passed": False, "gate": "PIVOT_CONTAINS_ZERO", "pivot": pivot}
        tangent_scalar = self.tangent[pivot]
        old_base = self.base
        old_tangent = self.tangent
        self.base = [value / scalar for value in old_base]
        self.tangent = [
            (old_tangent[index] * scalar - old_base[index] * tangent_scalar)
            / (scalar * scalar)
            for index in range(len(old_base))
        ]
        self.amplitude_tangent = (
            self.amplitude_tangent * scalar
            + self.amplitude * tangent_scalar
        )
        self.amplitude *= scalar
        self.pivot = pivot
        return {
            "passed": True,
            "pivot": pivot,
            "pivot_modulus_lower": str(scalar.abs_lower()),
        }

    def reconstruct(self) -> tuple[list[acb], list[acb]]:
        base = [self.amplitude * value for value in self.base]
        tangent = [
            self.amplitude_tangent * self.base[index]
            + self.amplitude * self.tangent[index]
            for index in range(len(self.base))
        ]
        return tangent, base


def seed_vector(values: sp.Matrix, tail: sp.Expr) -> list[acb]:
    radius = af(Fraction(int(sp.numer(tail)), int(sp.denom(tail))))
    return [inflate(cf(value.subs(moving.W, sp.Rational(OMEGA))), radius) for value in values]


def serialize_vector(values: list[acb]) -> list[dict]:
    return [
        {
            "ball": str(value),
            "radius_upper": str(width(value).upper()),
            "modulus_upper": str(value.abs_upper()),
        }
        for value in values
    ]


def frame_rank_gate(frame: list[list[acb]]) -> dict:
    """Certify the three columns independent using one explicit 3x3 minor."""
    # Rows X0, Y0, Z0 are triangular in the jet frame:
    # E has X only, R has Y, and S has Z.
    rows = (0, 2, 4)
    matrix = [[frame[column][row] for column in range(3)] for row in rows]
    determinant = (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    return {
        "rows": list(rows),
        "determinant": str(determinant),
        "modulus_lower": str(determinant.abs_lower()),
        "certified": determinant.abs_lower() > 0,
    }


def compute() -> dict:
    ctx.prec = 192
    crosswalk = json.loads(CROSSWALK.read_text())
    pure = moving.exact_data(crosswalk)
    mixed = levelt.exact_data(crosswalk)
    pure_tail = moving.coupled_tail_majorant(pure)
    mixed_tail = levelt.tail_majorant(mixed)

    pure_generator = compile_matrix(block_generator(pure["A"], pure["E"]))
    mixed_generator = compile_matrix(block_generator(mixed["base"], mixed["tangent"]))

    pure_line = DualLine(
        tangent=seed_vector(pure["tangent_seed"], pure_tail["tail_tangent"]),
        base=seed_vector(pure["base_seed"], pure_tail["tail_base"]),
        amplitude=acb(1),
        amplitude_tangent=acb(0),
    )
    mixed_line = DualLine(
        tangent=seed_vector(mixed["tangent_seed"], mixed_tail["tail_tangent"]),
        base=seed_vector(mixed["base_seed"], mixed_tail["tail_base"]),
        amplitude=acb(1),
        amplitude_tangent=acb(0),
    )
    initial_pure = pure_line.normalize()
    initial_mixed = mixed_line.normalize((2, 3))
    if not initial_pure["passed"] or not initial_mixed["passed"]:
        raise RuntimeError("canonical seed pivot failed")

    rho = RHO0
    checkpoints = []
    accepted = 0
    terminal = None
    for shell in range(SHELLS):
        shell_start = rho
        step = shell_start / PANELS
        for panel in range(PANELS):
            pure_next, pure_meta = taylor_step(
                pure_generator, pure_line.packed(), rho, step
            )
            mixed_next, mixed_meta = taylor_step(
                mixed_generator, mixed_line.packed(), rho, step
            )
            if pure_next is None or mixed_next is None:
                terminal = {
                    "shell": shell,
                    "panel": panel,
                    "rho": str(rho),
                    "pure": pure_meta,
                    "mixed": mixed_meta,
                }
                break
            pure_line = DualLine.unpacked(
                pure_next, pure_line.amplitude, pure_line.amplitude_tangent
            )
            mixed_line = DualLine.unpacked(
                mixed_next, mixed_line.amplitude, mixed_line.amplitude_tangent
            )
            pure_pivot = pure_line.normalize()
            mixed_pivot = mixed_line.normalize((2, 3))
            if not pure_pivot["passed"] or not mixed_pivot["passed"]:
                terminal = {
                    "shell": shell,
                    "panel": panel,
                    "rho": str(rho),
                    "gate": "PROJECTIVE_PIVOT",
                    "pure": pure_pivot,
                    "mixed": mixed_pivot,
                }
                break
            rho += step
            accepted += 1
        checkpoints.append(
            {
                "shell": shell,
                "rho": str(rho),
                "r": str(rho + 2),
                "accepted_panels": accepted,
                "pure_pivot": pure_line.pivot,
                "mixed_pivot": mixed_line.pivot,
                "pure_projective_width": str(
                    max(width(value) for value in pure_line.packed()).upper()
                ),
                "mixed_projective_width": str(
                    max(width(value) for value in mixed_line.packed()).upper()
                ),
                "pure_amplitude_width": str(
                    max(width(pure_line.amplitude), width(pure_line.amplitude_tangent)).upper()
                ),
                "mixed_amplitude_width": str(
                    max(width(mixed_line.amplitude), width(mixed_line.amplitude_tangent)).upper()
                ),
            }
        )
        if terminal is not None:
            break

    reached = terminal is None and rho == Fraction(2)
    frame = None
    rank = None
    if reached:
        pure_tangent, pure_base = pure_line.reconstruct()
        mixed_tangent, mixed_base = mixed_line.reconstruct()
        # Undo the mixed Levelt scaling at rho=2.
        mixed_tangent = [
            mixed_tangent[0] / 2,
            mixed_tangent[1] / 2,
            mixed_tangent[2] / 2,
            mixed_tangent[3] / 4,
        ]
        mixed_base = [
            mixed_base[0] / 2,
            mixed_base[1] / 2,
            mixed_base[2] / 2,
            mixed_base[3] / 4,
        ]
        zero = acb(0)
        metric = [*pure_base, zero, zero, zero, zero]
        carrier = [*pure_tangent, *pure_base, zero, zero]
        spin_one = [*mixed_tangent[:2], *mixed_base[:2], *mixed_base[2:]]
        columns = [metric, carrier, spin_one]
        frame = {
            "state_order": ["X0", "X1", "Y0", "Y1", "Z0", "Z1"],
            "column_order": ["Einstein_metric", "carrier_spin2", "spin_one_lift"],
            "columns": [serialize_vector(column) for column in columns],
        }
        rank = frame_rank_gate(columns)

    return {
        "schema": "phase3-axial-partial-jet-horizon-checkpoint-run-v1",
        "frequency": f"{OMEGA.numerator}/{OMEGA.denominator}",
        "scope": {
            "rho_start": str(RHO0),
            "rho_target": "2",
            "r_target": "4",
            "shells": SHELLS,
            "panels_per_shell": PANELS,
            "taylor_order": ORDER,
            "cauchy_radius_over_step": CAUCHY_FACTOR,
            "precision_bits": ctx.prec,
        },
        "canonical_endpoint_normalization": {
            "spin_two_leading_pairing": "ell_H^T f_0=1, tau-independent",
            "spin_one_quotient_leading_vector": "[1,-1], tau-independent",
            "levelt_order_one_free_parameter": "0, tau-independent",
            "K_H": [["0", "0"], ["0", "0"]],
        },
        "initial_pivots": {"pure": initial_pure, "mixed": initial_mixed},
        "accepted_panels": accepted,
        "reached_r4": reached,
        "terminal": terminal,
        "checkpoints": checkpoints,
        "frame_r4": frame,
        "rank_gate": rank,
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
