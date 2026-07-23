"""Unvalidated high-precision preview of the axial Schwarzschild connection.

This module is intentionally not a certificate producer.  It evaluates the
frozen exact six-state flow and the certified endpoint normal forms at five
point frequencies.  The radial integration is arbitrary precision, but it
has neither interval enclosures nor a validated truncation remainder.

The output is diagnostic evidence only:

    UNVALIDATED-NUMERIC / does_not_establish

In particular, it does not establish a global connection, a scattering
channel, a physical ghost, stability, or a pole exclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

import mpmath as mp
import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair import (
    produce as repair,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    cauchy_majorant,
    exact_horizon_data,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    exact_blocks,
)


HERE = Path(__file__).resolve().parent
PHASE3 = HERE.parent
OUTPUT = HERE / "numeric-preview.json"

FLOW_CERT = PHASE3 / "axial_complete_reconstruction_repair/certificate.json"
HORIZON_CERT = PHASE3 / "axial_endpoint_remainder_enclosures/certificate.json"
INFINITY_CERT = PHASE3 / "axial_infinity_practical_transfer/certificate.json"
CURRENT_CERT = PHASE3 / "axial_null_infinity_trace_preflight/certificate.json"
GRAM_CERT = PHASE3 / "axial_null_flux_gram/certificate.json"

FREQUENCIES = (
    sp.Rational(1, 2),
    sp.Rational(9, 16),
    sp.Rational(5, 8),
    sp.Rational(11, 16),
    sp.Rational(3, 4),
)
HORIZON_ORDER = ("XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus")
FUTURE_REGULAR = ("XH0a", "XH0b", "EH0")
INFINITY_ORDER = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")
IMINUS_ROWS = (0, 1, 4)
IPLUS_ROWS = (2, 3, 5)


class PreviewError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreviewError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mp_matrix(rows: int, cols: int, values: Iterable[mp.mpc] | None = None) -> mp.matrix:
    matrix = mp.matrix(rows, cols)
    if values is not None:
        for index, value in enumerate(values):
            matrix[index // cols, index % cols] = value
    return matrix


def mp_conjugate_transpose(matrix: mp.matrix) -> mp.matrix:
    return matrix.transpose_conj()


def max_abs(matrix: mp.matrix) -> mp.mpf:
    return max((abs(matrix[i, j])
                for i in range(matrix.rows)
                for j in range(matrix.cols)), default=mp.mpf("0"))


def matrix_submatrix(matrix: mp.matrix, rows: tuple[int, ...],
                     cols: tuple[int, ...] | None = None) -> mp.matrix:
    if cols is None:
        cols = tuple(range(matrix.cols))
    return mp.matrix([[matrix[i, j] for j in cols] for i in rows])


def parse_expression(text: str, omega_symbol: sp.Symbol) -> sp.Expr:
    return sp.sympify(text, locals={"omega": omega_symbol, "I": sp.I})


def eval_sympy(expr: sp.Expr, substitutions: dict[sp.Symbol, sp.Expr],
               digits: int) -> mp.mpc:
    value = sp.N(expr.subs(substitutions), digits + 15)
    real, imag = value.as_real_imag()
    return mp.mpc(mp.mpf(str(real)), mp.mpf(str(imag)))


def eval_sympy_matrix(matrix: sp.Matrix,
                      substitutions: dict[sp.Symbol, sp.Expr],
                      digits: int) -> mp.matrix:
    return mp.matrix([
        [eval_sympy(matrix[i, j], substitutions, digits)
         for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ])


def rk4_step(rhs: Callable[[mp.mpf, mp.matrix], mp.matrix],
             x: mp.mpf, y: mp.matrix, h: mp.mpf) -> mp.matrix:
    half = h / 2
    k1 = rhs(x, y)
    k2 = rhs(x + half, y + half * k1)
    k3 = rhs(x + half, y + half * k2)
    k4 = rhs(x + h, y + h * k3)
    return y + h * (k1 + 2*k2 + 2*k3 + k4) / 6


def repeated_rk4(rhs: Callable[[mp.mpf, mp.matrix], mp.matrix],
                 x: mp.mpf, y: mp.matrix, h: mp.mpf,
                 divisions: int) -> mp.matrix:
    step = h / divisions
    out = y
    at = x
    for _ in range(divisions):
        out = rk4_step(rhs, at, out, step)
        at += step
    return out


def extrapolated_step(rhs: Callable[[mp.mpf, mp.matrix], mp.matrix],
                      x: mp.mpf, y: mp.matrix,
                      h: mp.mpf) -> tuple[mp.matrix, mp.mpf]:
    """One exact-coefficient RK4 Richardson step of nominal order six."""
    u1 = repeated_rk4(rhs, x, y, h, 1)
    u2 = repeated_rk4(rhs, x, y, h, 2)
    v5 = u2 + (u2 - u1) / 15
    u4 = repeated_rk4(rhs, x, y, h, 4)
    v5_fine = u4 + (u4 - u2) / 15
    v6 = v5_fine + (v5_fine - v5) / 31
    return v6, max_abs(v6 - v5_fine)


def integrate_fixed(
    rhs: Callable[[mp.mpf, mp.matrix], mp.matrix],
    x0: mp.mpf,
    x1: mp.mpf,
    initial: mp.matrix,
    macro_step: mp.mpf,
    checkpoints: tuple[mp.mpf, ...] = (),
) -> tuple[mp.matrix, dict[str, mp.matrix], mp.mpf]:
    direction = mp.sign(x1 - x0)
    require(direction != 0, "zero integration interval")
    step_size = abs(macro_step) * direction
    at = mp.mpf(x0)
    out = initial.copy()
    pending = sorted((mp.mpf(x) for x in checkpoints),
                     reverse=direction < 0)
    saved: dict[str, mp.matrix] = {}
    error = mp.mpf("0")
    targets = pending + [mp.mpf(x1)]
    for target in targets:
        require(direction * (target - at) >= 0,
                "checkpoint is behind the integration direction")
        while direction * (target - at) > mp.mpf("1e-60"):
            h = step_size
            if direction * (at + h - target) > 0:
                h = target - at
            out, local_error = extrapolated_step(rhs, at, out, h)
            error = max(error, local_error)
            at += h
        if target != x1:
            saved[mp.nstr(target, 30)] = out.copy()
    return out, saved, error


@lru_cache(maxsize=1)
def make_flow() -> tuple[sp.Symbol, sp.Symbol, sp.Matrix,
                         Callable[[mp.mpf, mp.mpf], mp.matrix]]:
    system = repair.build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    flow = system["flow6"]
    compiled = sp.lambdify((r, omega), flow, modules="mpmath")

    def evaluate(radius: mp.mpf, frequency: mp.mpf) -> mp.matrix:
        return mp.matrix(compiled(radius, frequency))

    return r, omega, flow, evaluate


@lru_cache(maxsize=1)
def cached_horizon_data() -> tuple[dict, dict]:
    data = exact_horizon_data(repair)
    return data, cauchy_majorant(data)


@lru_cache(maxsize=1)
def cached_infinity_blocks() -> dict:
    return exact_blocks()


@lru_cache(maxsize=1)
def make_normalized_infinity_generator():
    """Compile the exact phase-normalized correction generator.

    If ``F=B D`` is the truncated formal frame and
    ``R=F'-A F``, an exact frame has the form ``Y=F Z`` with

        Z' = -D^{-1} B^{-1} R_B D Z,

    where ``R_B`` is the columnwise residual before multiplying by the
    diagonal phase.  Propagating ``Z`` avoids the catastrophic numerical
    collapse of six full solutions integrated inward over a long interval.
    """
    blocks = cached_infinity_blocks()
    r = blocks["r"]
    omega = blocks["omega"]
    z = blocks["z"]
    flow = blocks["system"]["flow6"].subs(r, 1/z)
    basis = sp.Matrix.hstack(*(column for _, column in blocks["columns"]))
    residual_columns = []
    for (_, column), rate, power in zip(
            blocks["columns"], blocks["rates"], blocks["powers"]):
        derivative = (
            column.applyfunc(lambda value: -z**2 * sp.diff(value, z))
            + (rate + power*z) * column
        )
        residual_columns.append(derivative - flow*column)
    residual = sp.Matrix.hstack(*residual_columns)
    basis_fn = sp.lambdify((z, omega), basis, modules="mpmath")
    residual_fn = sp.lambdify((z, omega), residual, modules="mpmath")
    rate_fn = [sp.lambdify(omega, value, modules="mpmath")
               for value in blocks["rates"]]
    power_fn = [sp.lambdify(omega, value, modules="mpmath")
                for value in blocks["powers"]]

    def basis_at(radius: mp.mpf, frequency: mp.mpf) -> mp.matrix:
        return mp.matrix(basis_fn(1/radius, frequency))

    def generator(radius: mp.mpf, frequency: mp.mpf) -> mp.matrix:
        zz = 1/radius
        b = mp.matrix(basis_fn(zz, frequency))
        residual_value = mp.matrix(residual_fn(zz, frequency))
        # mpmath's lu_solve accepts only a vector right-hand side.  Solving
        # the six columns together through the inverse is acceptable on this
        # nonvalidated point-frequency rail; the exact interval producer uses
        # independent certified solves.
        transformed = b**-1 * residual_value
        phases = [
            mp.exp(rate_fn[j](frequency) * (radius - 32))
            * (radius/32) ** power_fn[j](frequency)
            for j in range(6)
        ]
        return mp.matrix(6, 6, lambda i, j:
                         -transformed[i, j] * phases[j] / phases[i])

    return basis_at, generator


def horizon_initializer(frequency: sp.Rational, digits: int) -> tuple[mp.matrix, mp.mpf]:
    data, majorant = cached_horizon_data()
    rho = mp.mpf(majorant["epsilon"].numerator) / majorant["epsilon"].denominator
    substitutions = {
        data["omega"]: frequency,
        data["rho"]: sp.Rational(majorant["epsilon"].numerator,
                                 majorant["epsilon"].denominator),
    }
    chart = mp.matrix(6, 3)
    for n, head in enumerate(data["physical_heads"]):
        evaluated = eval_sympy_matrix(head[:, :3], substitutions, digits)
        chart += rho**n * evaluated
    # The certified regular columns all have residue exponent zero.
    standard = chart.copy()
    for column in range(3):
        standard[5, column] /= rho
    return standard, rho


def infinity_initializer(frequency: sp.Rational, radius: int,
                         digits: int) -> mp.matrix:
    blocks = cached_infinity_blocks()
    omega = blocks["omega"]
    z = blocks["z"]
    substitutions = {omega: frequency, z: sp.Rational(1, radius)}
    columns = []
    for (_, column), rate, power in zip(
            blocks["columns"], blocks["rates"], blocks["powers"]):
        vector = eval_sympy_matrix(column, substitutions, digits)
        phase = (
            mp.exp(eval_sympy(rate, {omega: frequency}, digits)
                   * mp.mpf(radius - 32))
            * (mp.mpf(radius) / 32)
            ** eval_sympy(power, {omega: frequency}, digits)
        )
        columns.append(phase * vector)
    return mp.matrix(6, 6, lambda i, j: columns[j][i])


def normalized_infinity_frame(
    frequency: sp.Rational,
    radius: int,
    macro_step: mp.mpf,
) -> tuple[mp.matrix, mp.matrix, mp.matrix, mp.mpf]:
    """Transport the asymptotic correction rather than six collapsing modes."""
    basis_at, generator = make_normalized_infinity_generator()
    wmp = mp.mpf(frequency.p) / frequency.q

    def rhs(radial: mp.mpf, correction: mp.matrix) -> mp.matrix:
        return generator(radial, wmp) * correction

    correction, _, error = integrate_fixed(
        rhs, mp.mpf(radius), mp.mpf("32"), mp.eye(6), macro_step,
    )
    bare = basis_at(mp.mpf("32"), wmp)
    return bare * correction, bare, correction, error


def parse_gram(endpoint: str, omega_value: sp.Rational,
               digits: int) -> mp.matrix:
    payload = json.loads(GRAM_CERT.read_text())
    rows = payload["endpoint_grams"][endpoint]["stokes_gram_over_pi_alpha_W"]
    omega = sp.Symbol("omega", positive=True, real=True)
    symbolic = sp.Matrix([[parse_expression(value, omega) for value in row]
                          for row in rows])
    canonical = eval_sympy_matrix(symbolic, {omega: omega_value}, digits)
    # The practical infinity transport uses
    # exp(rate*(r-32))*(r/32)^power, whereas the endpoint Grams use the
    # canonical exp(rate*r)*r^power amplitudes.  If Y_norm=Y_can*S, then the
    # Gram in normalized connection coordinates is S^dagger G_can S.
    blocks = cached_infinity_blocks()
    indices = IMINUS_ROWS if endpoint == "Iminus" else IPLUS_ROWS
    scales = []
    for index in indices:
        rate = eval_sympy(
            blocks["rates"][index], {blocks["omega"]: omega_value}, digits)
        power = eval_sympy(
            blocks["powers"][index], {blocks["omega"]: omega_value}, digits)
        scales.append(mp.exp(-32*rate) * mp.mpf(32)**(-power))
    scaling = mp.diag(scales)
    return mp_conjugate_transpose(scaling) * canonical * scaling


def parse_current(omega_value: sp.Rational, digits: int) -> mp.matrix:
    payload = json.loads(CURRENT_CERT.read_text())
    rows = payload["exact_radial_current"]["matrix_without_pi_alpha"]
    omega = sp.Symbol("omega", real=True)
    symbolic = sp.Matrix([[parse_expression(value, omega) for value in row]
                          for row in rows])
    return eval_sympy_matrix(symbolic, {omega: omega_value}, digits)


def future_horizon_outward_gram(
    horizon_state: mp.matrix,
    radial_current_matrix: mp.matrix,
) -> mp.matrix:
    """Return the Stokes-oriented i*F^r Gram at the future horizon.

    The imported current satisfies
    F^r/(pi*alpha_W)=z^dagger*Jhat*y.  The Schwarzschild exterior has the
    future horizon as its inner radial boundary, so the outward normal is
    minus the increasing-r coordinate normal.
    """
    coordinate_gram = (
        mp_conjugate_transpose(horizon_state)
        * (mp.j * radial_current_matrix)
        * horizon_state
    )
    return -coordinate_gram


def singular_values(matrix: mp.matrix) -> list[mp.mpf]:
    _, values, _ = mp.svd(matrix)
    return sorted((abs(values[i]) for i in range(values.rows)), reverse=True)


def numeric_rank(matrix: mp.matrix, tolerance: mp.mpf) -> int:
    values = singular_values(matrix)
    if not values:
        return 0
    threshold = max(values[0] * tolerance, tolerance)
    return sum(value > threshold for value in values)


def hermitian_inertia(matrix: mp.matrix, tolerance: mp.mpf) -> tuple[int, int, int, list[mp.mpf]]:
    hermitian = (matrix + mp_conjugate_transpose(matrix)) / 2
    eigenvalues = sorted((mp.re(value) for value in mp.eighe(
        hermitian, eigvals_only=True)))
    scale = max((abs(value) for value in eigenvalues), default=mp.mpf("1"))
    threshold = max(scale * tolerance, tolerance)
    positive = sum(value > threshold for value in eigenvalues)
    negative = sum(value < -threshold for value in eigenvalues)
    zero = len(eigenvalues) - positive - negative
    return positive, negative, zero, eigenvalues


def complex_json(value: mp.mpc, digits: int = 22) -> dict[str, str]:
    return {
        "re": mp.nstr(mp.re(value), digits),
        "im": mp.nstr(mp.im(value), digits),
    }


def matrix_json(matrix: mp.matrix, digits: int = 22) -> list[list[dict[str, str]]]:
    return [[complex_json(matrix[i, j], digits)
             for j in range(matrix.cols)] for i in range(matrix.rows)]


def real_list(values: Iterable[mp.mpf], digits: int = 22) -> list[str]:
    return [mp.nstr(value, digits) for value in values]


def one_frequency(frequency: sp.Rational, digits: int,
                  horizon_step: mp.mpf, infinity_step: mp.mpf,
                  infinity_radius: int) -> dict:
    _, _, _, flow = make_flow()
    wmp = mp.mpf(frequency.p) / frequency.q

    horizon0, epsilon = horizon_initializer(frequency, digits)

    def horizon_log_rhs(u: mp.mpf, y: mp.matrix) -> mp.matrix:
        rho = mp.exp(u)
        return rho * flow(2 + rho, wmp) * y

    u0 = mp.log(epsilon)
    at_r3, _, horizon_log_error = integrate_fixed(
        horizon_log_rhs, u0, mp.mpf("0"), horizon0,
        mp.mpf("0.25"),
    )

    def radial_rhs(radius: mp.mpf, y: mp.matrix) -> mp.matrix:
        return flow(radius, wmp) * y

    horizon32, checkpoints, horizon_radial_error = integrate_fixed(
        radial_rhs, mp.mpf("3"), mp.mpf("32"), at_r3,
        horizon_step, checkpoints=(mp.mpf("4"),),
    )
    horizon4 = checkpoints[mp.nstr(mp.mpf("4"), 30)]

    infinity32, bare_infinity32, infinity_correction, infinity_error = normalized_infinity_frame(
        frequency, infinity_radius, infinity_step,
    )
    coefficients = infinity32**-1 * horizon32
    cminus = matrix_submatrix(coefficients, IMINUS_ROWS)
    cplus = matrix_submatrix(coefficients, IPLUS_ROWS)

    gminus_endpoint = parse_gram("Iminus", frequency, digits)
    gplus_endpoint = parse_gram("Iplus", frequency, digits)
    gminus = mp_conjugate_transpose(cminus) * gminus_endpoint * cminus
    gplus = mp_conjugate_transpose(cplus) * gplus_endpoint * cplus

    j4 = parse_current(frequency, digits)
    horizon_plus = future_horizon_outward_gram(horizon4, j4)
    conservation = horizon_plus + gplus - gminus
    denominator = max(
        max_abs(horizon_plus) + max_abs(gplus) + max_abs(gminus),
        mp.mpf("1"),
    )

    tolerance = mp.mpf(10) ** (-(min(digits // 2, 24)))
    full_singular = singular_values(coefficients)
    minus_singular = singular_values(cminus)
    plus_singular = singular_values(cplus)
    full_inertia = hermitian_inertia(horizon_plus + gplus, tolerance)
    minus_inertia = hermitian_inertia(gminus, tolerance)
    plus_inertia = hermitian_inertia(gplus, tolerance)
    horizon_inertia = hermitian_inertia(horizon_plus, tolerance)
    bare_singular = singular_values(bare_infinity32)
    correction_singular = singular_values(infinity_correction)
    frame_singular = singular_values(infinity32)

    def condition(values: list[mp.mpf]) -> str:
        if not values or values[-1] == 0:
            return "inf"
        return mp.nstr(values[0] / values[-1], 22)

    return {
        "frequency": str(frequency),
        "omega_decimal": mp.nstr(wmp, 20),
        "integration": {
            "digits": digits,
            "horizon_epsilon": mp.nstr(epsilon, 25),
            "horizon_log_macro_step": "1/4",
            "horizon_radial_macro_step": mp.nstr(horizon_step, 20),
            "infinity_radius": infinity_radius,
            "infinity_radial_macro_step": mp.nstr(infinity_step, 20),
            "max_embedded_step_defect": {
                "horizon_log": mp.nstr(horizon_log_error, 12),
                "horizon_radial": mp.nstr(horizon_radial_error, 12),
                "infinity_radial": mp.nstr(infinity_error, 12),
            },
        },
        "connection": {
            "basis_order": {
                "horizon_regular": list(FUTURE_REGULAR),
                "infinity_full": list(INFINITY_ORDER),
                "Iminus": [INFINITY_ORDER[i] for i in IMINUS_ROWS],
                "Iplus": [INFINITY_ORDER[i] for i in IPLUS_ROWS],
            },
            "full_6_by_3": matrix_json(coefficients),
            "Cminus_3_by_3": matrix_json(cminus),
            "Cplus_3_by_3": matrix_json(cplus),
            "rank": {
                "full": numeric_rank(coefficients, tolerance),
                "Cminus": numeric_rank(cminus, tolerance),
                "Cplus": numeric_rank(cplus, tolerance),
            },
            "singular_values": {
                "full": real_list(full_singular),
                "Cminus": real_list(minus_singular),
                "Cplus": real_list(plus_singular),
            },
            "infinity_frame_diagnostics": {
                "bare_B_at_R32": {
                    "rank": numeric_rank(bare_infinity32, tolerance),
                    "singular_values": real_list(bare_singular),
                    "condition_2": condition(bare_singular),
                },
                "transported_correction_Z": {
                    "rank": numeric_rank(infinity_correction, tolerance),
                    "singular_values": real_list(correction_singular),
                    "condition_2": condition(correction_singular),
                },
                "corrected_frame_BZ": {
                    "rank": numeric_rank(infinity32, tolerance),
                    "singular_values": real_list(frame_singular),
                    "condition_2": condition(frame_singular),
                },
            },
        },
        "flux": {
            "Gminus_pullback": matrix_json(gminus),
            "Gplus_pullback": matrix_json(gplus),
            "Hplus_outward": matrix_json(horizon_plus),
            "populated_outgoing_total_Hplus_plus_Iplus": matrix_json(horizon_plus + gplus),
            "inertia": {
                "Iminus_pullback": list(minus_inertia[:3]),
                "Iplus_pullback": list(plus_inertia[:3]),
                "Hplus": list(horizon_inertia[:3]),
                "outgoing_total": list(full_inertia[:3]),
            },
            "eigenvalues": {
                "Iminus_pullback": real_list(minus_inertia[3]),
                "Iplus_pullback": real_list(plus_inertia[3]),
                "Hplus": real_list(horizon_inertia[3]),
                "outgoing_total": real_list(full_inertia[3]),
            },
            "conservation": {
                "identity_tested": "Hplus + Iplus - Iminus = 0",
                "absolute_max_residual": mp.nstr(max_abs(conservation), 20),
                "relative_max_residual": mp.nstr(max_abs(conservation) / denominator, 20),
                "residual_matrix": matrix_json(conservation),
            },
        },
        "missing_Hminus": {
            "available": False,
            "reason": (
                "Only the three future-horizon-regular columns "
                "XH0a,XH0b,EH0 are propagated.  No past-horizon incoming "
                "basis or two-ended scattering matrix is constructed."
            ),
        },
    }


def convergence_delta(coarse: dict, fine: dict) -> dict:
    def decode(rows):
        return mp.matrix([
            [mp.mpc(entry["re"], entry["im"]) for entry in row]
            for row in rows
        ])

    answer = {}
    for name in ("full_6_by_3", "Cminus_3_by_3", "Cplus_3_by_3"):
        left = decode(coarse["connection"][name])
        right = decode(fine["connection"][name])
        scale = max(max_abs(right), mp.mpf("1"))
        answer[name] = {
            "absolute_max": mp.nstr(max_abs(left - right), 16),
            "relative_max": mp.nstr(max_abs(left - right) / scale, 16),
        }
    return answer


def build_preview(digits: int = 70, quick: bool = False) -> dict:
    mp.mp.dps = digits
    # The quick setting is useful for smoke tests only and is never emitted.
    horizon_step = mp.mpf("0.5") if quick else mp.mpf("0.25")
    infinity_step = mp.mpf("-0.5") if quick else mp.mpf("-0.25")
    radius = 128 if quick else 256

    results = []
    for frequency in FREQUENCIES:
        fine = one_frequency(
            frequency, digits, horizon_step, infinity_step, radius,
        )
        if not quick:
            coarse = one_frequency(
                frequency, digits,
                mp.mpf("0.5"), mp.mpf("-0.5"), 128,
            )
            fine["convergence_against_R128_step_half"] = convergence_delta(coarse, fine)
            fine["coarse_conservation_relative"] = (
                coarse["flux"]["conservation"]["relative_max_residual"]
            )
        results.append(fine)

    return {
        "schema": "axial-global-connection-numeric-preview-v1",
        "lifecycle": "UNVALIDATED-NUMERIC",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "UNVALIDATED-NUMERIC"],
        "claim_flags": {
            "diagnostic_preview_computed": True,
            "validated_global_connection": False,
            "physical_scattering_channels_classified": False,
            "physical_ghost_established": False,
            "stability_or_pole_exclusion_established": False,
        },
        "scope": {
            "theory": "strict pure Weyl gravity",
            "background": "Schwarzschild, M=1",
            "parity": "axial",
            "ell": 2,
            "frequencies": [str(value) for value in FREQUENCIES],
            "arithmetic": f"mpmath {digits}-decimal-digit working precision",
            "method": (
                "exact-coefficient RK4 Richardson extrapolation, formal "
                "endpoint series, and nonvalidated truncation convergence"
            ),
        },
        "imports": {
            str(path.relative_to(PHASE3.parents[2])): sha256(path)
            for path in (
                FLOW_CERT, HORIZON_CERT, INFINITY_CERT, CURRENT_CERT, GRAM_CERT
            )
        },
        "basis_contract": {
            "horizon_full": list(HORIZON_ORDER),
            "horizon_future_regular": list(FUTURE_REGULAR),
            "infinity_full": list(INFINITY_ORDER),
            "Iminus": [INFINITY_ORDER[i] for i in IMINUS_ROWS],
            "Iplus": [INFINITY_ORDER[i] for i in IPLUS_ROWS],
        },
        "results": results,
        "does_not_establish": [
            "an interval-certified or exact horizon-to-infinity connection",
            "a two-ended scattering map because Hminus data are absent",
            "uniform-in-frequency ranks or inertia",
            "physical scattering channels or a physical ghost",
            "complex-frequency poles, stability, CPT positivity or unitarity",
            "a PDE scattering theorem",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--digits", type=int, default=70)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build_preview(args.digits, args.quick)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.quick:
        print(json.dumps({
            "lifecycle": document["lifecycle"],
            "frequencies": [row["frequency"] for row in document["results"]],
            "relative_conservation": [
                row["flux"]["conservation"]["relative_max_residual"]
                for row in document["results"]
            ],
        }, indent=2))
        return
    if args.check:
        require(OUTPUT.exists(), "numeric preview is absent")
        require(OUTPUT.read_text() == encoded, "numeric preview drift")
        print("PASS numeric preview reproduces")
    else:
        OUTPUT.write_text(encoded)
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
