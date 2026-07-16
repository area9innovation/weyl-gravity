"""Direct exact nonzero-momentum Lee--Wald fixtures in both parities.

The calculation varies the full Einstein--Maxwell presymplectic potential,
not the already reduced quadratic action.  It keeps ``k`` symbolic and uses
the ell=2 axisymmetric harmonic, whose norm is 4*pi/5.  This is a slow
independent rail for the covariant-current normalization.
"""

from __future__ import annotations

import argparse

import sympy as sp


class LeeWaldFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LeeWaldFixtureError(message)


def _exterior_derivative(
    potential: sp.Matrix, coordinates: tuple[sp.Symbol, ...]
) -> sp.Matrix:
    return sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.diff(potential[nu], coordinates[mu])
        - sp.diff(potential[mu], coordinates[nu]),
    )


def _theta_time_component(
    metric: sp.Matrix,
    field: sp.Matrix,
    metric_variation: sp.Matrix,
    potential_variation: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Expr:
    inverse = metric.inv()
    sine = sp.sin(coordinates[2])
    volume = sp.sqrt(-metric.det()).subs(sp.Abs(sine), sine)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = sum(
                    inverse[target, index]
                    * (
                        sp.diff(metric[index, right], coordinates[left])
                        + sp.diff(metric[index, left], coordinates[right])
                        - sp.diff(metric[left, right], coordinates[index])
                    )
                    for index in range(4)
                ) / 2
    raised = inverse * metric_variation * inverse
    trace = sum(
        inverse[mu, nu] * metric_variation[mu, nu]
        for mu in range(4)
        for nu in range(4)
    )
    mu = 0
    divergence = sp.S.Zero
    for nu in range(4):
        divergence += sp.diff(raised[mu, nu], coordinates[nu])
        for rho in range(4):
            divergence += connection[mu][nu][rho] * raised[rho, nu]
            divergence += connection[nu][nu][rho] * raised[mu, rho]
    gradient = sum(
        inverse[mu, nu] * sp.diff(trace, coordinates[nu]) for nu in range(4)
    )
    theta_gravity = volume * (divergence - gradient) / 2
    field_up = inverse * field * inverse
    theta_maxwell = -volume * sum(
        field_up[mu, nu] * potential_variation[nu] for nu in range(4)
    )
    return theta_gravity + theta_maxwell


def _symplectic_current_time(
    metric_background: sp.Matrix,
    field_background: sp.Matrix,
    first: tuple[sp.Matrix, sp.Matrix],
    second: tuple[sp.Matrix, sp.Matrix],
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Expr:
    epsilon = sp.symbols("epsilon")
    first_metric, first_potential = first
    second_metric, second_potential = second
    first_theta = _theta_time_component(
        metric_background + epsilon * first_metric,
        field_background
        + epsilon * _exterior_derivative(first_potential, coordinates),
        second_metric,
        second_potential,
        coordinates,
    )
    second_theta = _theta_time_component(
        metric_background + epsilon * second_metric,
        field_background
        + epsilon * _exterior_derivative(second_potential, coordinates),
        first_metric,
        first_potential,
        coordinates,
    )
    return sp.factor(sp.diff(first_theta - second_theta, epsilon).subs(epsilon, 0))


def _sphere_integral(
    density: sp.Expr, theta: sp.Symbol, azimuth: sp.Symbol
) -> sp.Expr:
    sine = sp.sin(theta)
    z = sp.symbols("z", real=True)
    oriented = sp.refine(density, sp.Q.positive(sine))
    polynomial = sp.trigsimp(oriented / sine)
    polynomial = (
        sp.expand_trig(polynomial)
        .subs(sine**2, 1 - sp.cos(theta) ** 2)
        .subs(sp.cos(theta), z)
    )
    return sp.factor(
        2 * sp.pi * sp.integrate(sp.simplify(polynomial), (z, -1, 1))
    )


def _axial_variation(
    metric_master: sp.Expr,
    maxwell_master: sp.Expr,
    wave: sp.Expr,
    harmonic: sp.Expr,
    axial_one_form: sp.Expr,
    momentum: sp.Symbol,
    frequency: sp.Symbol,
) -> tuple[sp.Matrix, sp.Matrix]:
    metric = sp.zeros(4)
    metric[0, 3] = metric[3, 0] = (
        momentum * metric_master * wave * axial_one_form
    )
    metric[1, 3] = metric[3, 1] = (
        -frequency * metric_master * wave * axial_one_form
    )
    potential = sp.zeros(4, 1)
    potential[0] = momentum * maxwell_master * wave * harmonic
    potential[1] = -frequency * maxwell_master * wave * harmonic
    return metric, potential


def _polar_variation(
    metric_master: sp.Expr,
    maxwell_master: sp.Expr,
    wave: sp.Expr,
    harmonic: sp.Expr,
    axial_one_form: sp.Expr,
    sine: sp.Expr,
    momentum: sp.Symbol,
    frequency: sp.Symbol,
) -> tuple[sp.Matrix, sp.Matrix]:
    mass = frequency**2 - momentum**2
    radial = metric_master - 2 * maxwell_master
    diagonal = -(frequency**2 + momentum**2) * radial / mass
    mixed = 2 * momentum * frequency * radial / mass
    metric = sp.zeros(4)
    metric[0, 0] = diagonal * wave * harmonic
    metric[0, 1] = metric[1, 0] = mixed * wave * harmonic
    metric[1, 1] = diagonal * wave * harmonic
    metric[2, 2] = metric_master * wave * harmonic
    metric[3, 3] = metric_master * wave * harmonic * sine**2
    potential = sp.zeros(4, 1)
    potential[3] = maxwell_master * wave * axial_one_form
    return metric, potential


def exact_integrated_currents() -> dict[str, sp.Expr]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    momentum, frequency = sp.symbols("k omega", real=True)
    metric_master, maxwell_master = sp.symbols("H Q", real=True)
    polar_metric, polar_maxwell = sp.symbols("K U", real=True)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    metric_background = sp.diag(-1, 1, 1, sine**2)
    field_background = sp.zeros(4)
    field_background[2, 3] = sine
    field_background[3, 2] = -sine
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    conjugate_wave = 1 / wave

    axial_first = _axial_variation(
        metric_master,
        maxwell_master,
        wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    axial_second = _axial_variation(
        metric_master,
        maxwell_master,
        conjugate_wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    polar_first = _polar_variation(
        polar_metric,
        polar_maxwell,
        wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )
    polar_second = _polar_variation(
        polar_metric,
        polar_maxwell,
        conjugate_wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )
    return {
        "axial": _sphere_integral(
            _symplectic_current_time(
                metric_background,
                field_background,
                axial_first,
                axial_second,
                coordinates,
            ),
            theta,
            azimuth,
        ),
        "polar": _sphere_integral(
            _symplectic_current_time(
                metric_background,
                field_background,
                polar_first,
                polar_second,
                coordinates,
            ),
            theta,
            azimuth,
        ),
    }


def verify() -> None:
    momentum, frequency = sp.symbols("k omega", real=True)
    metric_master, maxwell_master = sp.symbols("H Q", real=True)
    polar_metric, polar_maxwell = sp.symbols("K U", real=True)
    mass = frequency**2 - momentum**2
    norm = 4 * sp.pi / 5
    axial_coefficient_form = sp.diag(6, 2)
    polar_form = sp.Matrix([[1, -2], [-2, 12]])
    axial_vector = sp.Matrix([metric_master, maxwell_master])
    polar_vector = sp.Matrix([polar_metric, polar_maxwell])
    expected = {
        "axial": -2
        * sp.I
        * frequency
        * norm
        / 2
        * mass
        * (axial_vector.T * axial_coefficient_form * axial_vector)[0],
        "polar": -2
        * sp.I
        * frequency
        * norm
        / 2
        * (polar_vector.T * polar_form * polar_vector)[0],
    }
    actual = exact_integrated_currents()
    for parity in ("axial", "polar"):
        _require(
            sp.simplify(actual[parity] - expected[parity]) == 0,
            f"{parity} direct Lee-Wald current changed",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required")
    verify()


if __name__ == "__main__":
    main()
