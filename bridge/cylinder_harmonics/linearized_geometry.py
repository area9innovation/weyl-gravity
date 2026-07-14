"""Exact phase-reduced linearized geometry on ``R x S3``.

The module works in the rational Euler chart

    r = tan(beta/2),

and suppresses one common Fourier/radial factor

    exp[-i(E tau + m_L alpha + m_R gamma)] (1+r^2)^(-a).

All returned tensor entries are the exact rational coefficients multiplying
that factor.  Keeping the factor outside the expressions is what makes it
possible to differentiate the all-energy E/A/L highest weights symbolically.

The curvature convention is

    R^rho{}_{sigma mu nu}
      = d_mu Gamma^rho_{nu sigma} - d_nu Gamma^rho_{mu sigma}
        + Gamma^rho_{mu lambda} Gamma^lambda_{nu sigma}
        - Gamma^rho_{nu lambda} Gamma^lambda_{mu sigma}.

The Weyl tensor has every index lowered.  ``bach_from_weyl`` implements

    (C^sharp U)_{mu nu}
      = nabla^rho nabla^sigma U_{mu rho nu sigma}
        + (1/2) R^{rho sigma} U_{mu rho nu sigma}

on the conformal-cylinder background.  This is the linear Bach operator
when ``U=C_1 h``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import product
from typing import Mapping

import sympy as sp


I = sp.I
R = sp.Rational
DIMENSION = 4
INDICES = range(DIMENSION)
r = sp.symbols("r", positive=True, real=True)
z = 1 + r**2
n_symbol = sp.symbols("n", integer=True, positive=True)

Tensor = dict[tuple[int, ...], sp.Expr]


def _zero(expression: sp.Expr) -> bool:
    return expression == 0 or bool(expression.is_zero)


def canonical(expression: sp.Expr) -> sp.Expr:
    """Canonicalize a coefficient in ``Q(i,n,radicals)(r)``.

    The all-energy modes contain square roots depending only on ``n``.
    With the common radial power suppressed, every coordinate coefficient
    is rational in ``r``.  ``cancel`` is consequently both exact and much
    cheaper than a general trigonometric simplification.
    """

    expression = sp.sympify(expression)
    if _zero(expression):
        return sp.Integer(0)
    return sp.factor(sp.cancel(sp.together(expression)))


def tensor_get(tensor: Mapping[tuple[int, ...], sp.Expr], *indices: int) -> sp.Expr:
    return tensor.get(tuple(indices), sp.Integer(0))


def dense_tensor(rank: int, function) -> Tensor:
    output: Tensor = {}
    for indices in product(INDICES, repeat=rank):
        value = canonical(function(*indices))
        if value != 0:
            output[indices] = value
    return output


@dataclass(frozen=True)
class CylinderMode:
    """One common-phase trace-free metric perturbation."""

    family: str
    energy: sp.Expr
    spin_left: sp.Expr
    spin_right: sp.Expr
    magnetic_left: sp.Expr
    magnetic_right: sp.Expr
    radial_exponent: sp.Expr
    amplitude: sp.Expr
    metric: Tensor

    def phase_derivative(self, coordinate: int, expression: sp.Expr) -> sp.Expr:
        """Differentiate a phase-reduced coefficient covariantly as a scalar."""

        if expression == 0:
            return sp.Integer(0)
        if coordinate == 0:
            return canonical(-I * self.energy * expression)
        if coordinate == 1:
            return canonical(-I * self.magnetic_left * expression)
        if coordinate == 2:
            return canonical(
                sp.diff(expression, r)
                - 2 * self.radial_exponent * r * expression / z
            )
        if coordinate == 3:
            return canonical(-I * self.magnetic_right * expression)
        raise IndexError(coordinate)


def _q_covector() -> tuple[sp.Expr, ...]:
    # q=d beta+i sin(beta)d gamma, rewritten in r=tan(beta/2).
    return (sp.Integer(0), sp.Integer(0), 2 / z, 2 * I * r / z)


def highest_weight_mode(
    family: str, energy: sp.Expr = n_symbol, chirality: int = 1
) -> CylinderMode:
    """Return the normalized positive-chirality E/A/L metric representative.

    These are Hamada--Horata's unit-``S3`` highest-weight harmonics with the
    oscillator coefficients of their Eqs. (3.26)--(3.27).  The expressions
    are valid at ``n>=2`` for E, ``n>=3`` for A, and ``n>=4`` for L.
    ``metric`` stores the coefficient after removing the common radial and
    Fourier factor documented at module level.
    """

    if chirality not in (-1, 1):
        raise ValueError("chirality must be +1 or -1")
    energy = sp.sympify(energy)
    q = _q_covector()
    metric: Tensor = {}

    if family == "E":
        j = energy / 2
        spin_left, spin_right = j + 1, j - 1
        radial_exponent = (energy - 2) / 2
        harmonic_amplitude = sp.sqrt(2 * (energy - 1)) / (16 * sp.pi)
        oscillator = 1 / (4 * sp.sqrt(j * (2 * j + 1)))
        amplitude = sp.simplify(harmonic_amplitude * oscillator)
        for first, second in product(range(1, 4), repeat=2):
            value = q[first] * q[second]
            if value != 0:
                metric[first, second] = canonical(value)
    elif family == "A":
        j = (energy - 1) / 2
        spin_left, spin_right = j + R(1, 2), j - R(1, 2)
        radial_exponent = (energy - 2) / 2
        harmonic_amplitude = -sp.sqrt(energy - 1) / (4 * sp.pi)
        oscillator = 1 / (
            2 * sp.sqrt((energy - 2) * energy * (energy + 2))
        )
        amplitude = sp.simplify(harmonic_amplitude * oscillator)
        for spatial in range(1, 4):
            value = q[spatial]
            if value != 0:
                metric[0, spatial] = canonical(value)
                metric[spatial, 0] = canonical(value)
    elif family == "L":
        j = (energy - 2) / 2
        spin_left, spin_right = j + 1, j - 1
        radial_exponent = (energy - 4) / 2
        harmonic_amplitude = sp.sqrt(2 * (energy - 3)) / (16 * sp.pi)
        oscillator = 1 / (4 * sp.sqrt((j + 1) * (2 * j + 1)))
        amplitude = sp.simplify(harmonic_amplitude * oscillator)
        for first, second in product(range(1, 4), repeat=2):
            value = q[first] * q[second]
            if value != 0:
                metric[first, second] = canonical(value)
    else:
        raise ValueError(f"unknown family {family!r}")

    normalized_metric = {
        key: canonical(amplitude * value) for key, value in metric.items()
    }
    if chirality == -1:
        # Orientation-reversing S3 isometry alpha <-> gamma.  Pullback swaps
        # the two SU(2) factors and therefore turns a self-dual highest weight
        # into its opposite-chirality parity partner.
        parity_index = {0: 0, 1: 3, 2: 2, 3: 1}
        normalized_metric = {
            (parity_index[first], parity_index[second]): value
            for (first, second), value in normalized_metric.items()
        }
        spin_left, spin_right = spin_right, spin_left

    return CylinderMode(
        family=family,
        energy=energy,
        spin_left=sp.simplify(spin_left),
        spin_right=sp.simplify(spin_right),
        magnetic_left=sp.simplify(spin_left),
        magnetic_right=sp.simplify(spin_right),
        radial_exponent=sp.simplify(radial_exponent),
        amplitude=amplitude,
        metric=normalized_metric,
    )


class LinearizedCylinderGeometry:
    """Background and exact linearized curvature operators."""

    def __init__(self) -> None:
        metric = sp.zeros(DIMENSION)
        metric[0, 0] = -1
        metric[1, 1] = R(1, 4)
        metric[2, 2] = 1 / z**2
        metric[3, 3] = R(1, 4)
        metric[1, 3] = metric[3, 1] = (1 - r**2) / (4 * z)
        self.metric = metric.applyfunc(canonical)
        self.inverse = self.metric.inv().applyfunc(canonical)

    @staticmethod
    def background_partial(coordinate: int, expression: sp.Expr) -> sp.Expr:
        return canonical(sp.diff(expression, r)) if coordinate == 2 else sp.Integer(0)

    @cached_property
    def christoffel(self) -> Tensor:
        g = self.metric
        inverse = self.inverse

        def entry(upper: int, first: int, second: int) -> sp.Expr:
            return sum(
                inverse[upper, contracted]
                * (
                    self.background_partial(first, g[contracted, second])
                    + self.background_partial(second, g[contracted, first])
                    - self.background_partial(contracted, g[first, second])
                )
                / 2
                for contracted in INDICES
            )

        return dense_tensor(3, entry)

    @cached_property
    def riemann_mixed(self) -> Tensor:
        gamma = self.christoffel

        def entry(upper: int, lower: int, first: int, second: int) -> sp.Expr:
            value = self.background_partial(
                first, tensor_get(gamma, upper, second, lower)
            ) - self.background_partial(
                second, tensor_get(gamma, upper, first, lower)
            )
            value += sum(
                tensor_get(gamma, upper, first, contracted)
                * tensor_get(gamma, contracted, second, lower)
                - tensor_get(gamma, upper, second, contracted)
                * tensor_get(gamma, contracted, first, lower)
                for contracted in INDICES
            )
            return value

        return dense_tensor(4, entry)

    @cached_property
    def ricci(self) -> sp.Matrix:
        result = sp.zeros(DIMENSION)
        for first, second in product(INDICES, repeat=2):
            result[first, second] = canonical(
                sum(
                    tensor_get(self.riemann_mixed, upper, first, upper, second)
                    for upper in INDICES
                )
            )
        return result

    @cached_property
    def scalar_curvature(self) -> sp.Expr:
        return canonical(
            sum(
                self.inverse[first, second] * self.ricci[first, second]
                for first, second in product(INDICES, repeat=2)
            )
        )

    def trace(self, mode: CylinderMode) -> sp.Expr:
        return canonical(
            sum(
                self.inverse[first, second]
                * tensor_get(mode.metric, first, second)
                for first, second in product(INDICES, repeat=2)
            )
        )

    def gauge_image(
        self,
        profile: CylinderMode,
        covector: Mapping[int, sp.Expr],
        weyl_parameter: sp.Expr = sp.Integer(0),
    ) -> CylinderMode:
        """Return ``L_xi g+2 sigma g`` with the common phase suppressed.

        ``profile`` supplies the Fourier weights and common radial power;
        its own metric field is ignored.  The covariant components of
        ``xi`` and ``sigma`` are coefficient functions multiplying that same
        common factor.  This represents the full linear Diff x Weyl map
        before trace gauge is chosen.
        """

        gamma = self.christoffel

        def nabla(first: int, second: int) -> sp.Expr:
            return canonical(
                profile.phase_derivative(first, covector.get(second, 0))
                - sum(
                    tensor_get(gamma, contracted, first, second)
                    * covector.get(contracted, 0)
                    for contracted in INDICES
                )
            )

        metric = dense_tensor(
            2,
            lambda first, second: nabla(first, second)
            + nabla(second, first)
            + 2 * weyl_parameter * self.metric[first, second],
        )
        return CylinderMode(
            family="K",
            energy=profile.energy,
            spin_left=profile.spin_left,
            spin_right=profile.spin_right,
            magnetic_left=profile.magnetic_left,
            magnetic_right=profile.magnetic_right,
            radial_exponent=profile.radial_exponent,
            amplitude=sp.Integer(1),
            metric=metric,
        )

    def delta_inverse(self, mode: CylinderMode) -> sp.Matrix:
        h = mode.metric
        return sp.Matrix(
            DIMENSION,
            DIMENSION,
            lambda first, second: canonical(
                -sum(
                    self.inverse[first, alpha]
                    * tensor_get(h, alpha, beta)
                    * self.inverse[beta, second]
                    for alpha, beta in product(INDICES, repeat=2)
                )
            ),
        )

    def delta_christoffel(self, mode: CylinderMode) -> Tensor:
        h = mode.metric
        delta_inverse = self.delta_inverse(mode)
        g = self.metric
        inverse = self.inverse

        def entry(upper: int, first: int, second: int) -> sp.Expr:
            background_part = sum(
                delta_inverse[upper, contracted]
                * (
                    self.background_partial(first, g[contracted, second])
                    + self.background_partial(second, g[contracted, first])
                    - self.background_partial(contracted, g[first, second])
                )
                / 2
                for contracted in INDICES
            )
            perturbation_part = sum(
                inverse[upper, contracted]
                * (
                    mode.phase_derivative(
                        first, tensor_get(h, contracted, second)
                    )
                    + mode.phase_derivative(
                        second, tensor_get(h, contracted, first)
                    )
                    - mode.phase_derivative(
                        contracted, tensor_get(h, first, second)
                    )
                )
                / 2
                for contracted in INDICES
            )
            return background_part + perturbation_part

        return dense_tensor(3, entry)

    def delta_riemann_mixed(self, mode: CylinderMode) -> Tensor:
        gamma = self.christoffel
        delta_gamma = self.delta_christoffel(mode)

        def entry(upper: int, lower: int, first: int, second: int) -> sp.Expr:
            value = mode.phase_derivative(
                first, tensor_get(delta_gamma, upper, second, lower)
            ) - mode.phase_derivative(
                second, tensor_get(delta_gamma, upper, first, lower)
            )
            value += sum(
                tensor_get(delta_gamma, upper, first, contracted)
                * tensor_get(gamma, contracted, second, lower)
                + tensor_get(gamma, upper, first, contracted)
                * tensor_get(delta_gamma, contracted, second, lower)
                - tensor_get(delta_gamma, upper, second, contracted)
                * tensor_get(gamma, contracted, first, lower)
                - tensor_get(gamma, upper, second, contracted)
                * tensor_get(delta_gamma, contracted, first, lower)
                for contracted in INDICES
            )
            return value

        return dense_tensor(4, entry)

    def delta_ricci(self, mode: CylinderMode) -> sp.Matrix:
        delta_riemann = self.delta_riemann_mixed(mode)
        return sp.Matrix(
            DIMENSION,
            DIMENSION,
            lambda first, second: canonical(
                sum(
                    tensor_get(delta_riemann, upper, first, upper, second)
                    for upper in INDICES
                )
            ),
        )

    def delta_scalar(self, mode: CylinderMode) -> sp.Expr:
        delta_inverse = self.delta_inverse(mode)
        delta_ricci = self.delta_ricci(mode)
        return canonical(
            sum(
                delta_inverse[first, second] * self.ricci[first, second]
                + self.inverse[first, second] * delta_ricci[first, second]
                for first, second in product(INDICES, repeat=2)
            )
        )

    def delta_riemann_lower(self, mode: CylinderMode) -> Tensor:
        delta_riemann = self.delta_riemann_mixed(mode)

        def entry(first: int, second: int, third: int, fourth: int) -> sp.Expr:
            return sum(
                tensor_get(mode.metric, first, contracted)
                * tensor_get(
                    self.riemann_mixed, contracted, second, third, fourth
                )
                + self.metric[first, contracted]
                * tensor_get(
                    delta_riemann, contracted, second, third, fourth
                )
                for contracted in INDICES
            )

        return dense_tensor(4, entry)

    def linearized_weyl(self, mode: CylinderMode) -> Tensor:
        """Return ``C_1 h`` with all indices lowered and common factor removed."""

        h = mode.metric
        g = self.metric
        ricci = self.ricci
        scalar = self.scalar_curvature
        delta_riemann = self.delta_riemann_lower(mode)
        delta_ricci = self.delta_ricci(mode)
        delta_scalar = self.delta_scalar(mode)

        def entry(a: int, b: int, c: int, d: int) -> sp.Expr:
            value = tensor_get(delta_riemann, a, b, c, d)
            value -= (
                tensor_get(h, a, c) * ricci[d, b]
                + g[a, c] * delta_ricci[d, b]
                - tensor_get(h, a, d) * ricci[c, b]
                - g[a, d] * delta_ricci[c, b]
                - tensor_get(h, b, c) * ricci[d, a]
                - g[b, c] * delta_ricci[d, a]
                + tensor_get(h, b, d) * ricci[c, a]
                + g[b, d] * delta_ricci[c, a]
            ) / 2
            value += delta_scalar * (g[a, c] * g[d, b] - g[a, d] * g[c, b]) / 6
            value += scalar * (
                tensor_get(h, a, c) * g[d, b]
                + g[a, c] * tensor_get(h, d, b)
                - tensor_get(h, a, d) * g[c, b]
                - g[a, d] * tensor_get(h, c, b)
            ) / 6
            return value

        return dense_tensor(4, entry)

    def covariant_derivative(
        self, mode: CylinderMode, tensor: Tensor, rank: int
    ) -> Tensor:
        gamma = self.christoffel

        def entry(derivative: int, *indices: int) -> sp.Expr:
            value = mode.phase_derivative(
                derivative, tensor_get(tensor, *indices)
            )
            for slot in range(rank):
                value -= sum(
                    tensor_get(gamma, contracted, derivative, indices[slot])
                    * tensor_get(
                        tensor,
                        *(
                            indices[:slot]
                            + (contracted,)
                            + indices[slot + 1 :]
                        ),
                    )
                    for contracted in INDICES
                )
            return value

        return dense_tensor(rank + 1, entry)

    def bach_from_weyl(self, mode: CylinderMode, weyl: Tensor) -> sp.Matrix:
        first = self.covariant_derivative(mode, weyl, 4)

        # V_{mu,nu,sigma}=nabla^rho U_{mu,rho,nu,sigma}.
        first_divergence = dense_tensor(
            3,
            lambda mu, nu, sigma: sum(
                self.inverse[rho, derivative]
                * tensor_get(first, derivative, mu, rho, nu, sigma)
                for rho, derivative in product(INDICES, repeat=2)
            ),
        )
        second = self.covariant_derivative(mode, first_divergence, 3)

        ricci_up = self.inverse * self.ricci * self.inverse
        return sp.Matrix(
            DIMENSION,
            DIMENSION,
            lambda mu, nu: canonical(
                sum(
                    self.inverse[sigma, derivative]
                    * tensor_get(second, derivative, mu, nu, sigma)
                    for sigma, derivative in product(INDICES, repeat=2)
                )
                + sum(
                    ricci_up[rho, sigma]
                    * tensor_get(weyl, mu, rho, nu, sigma)
                    / 2
                    for rho, sigma in product(INDICES, repeat=2)
                )
            ),
        )

    @cached_property
    def volume_density(self) -> sp.Expr:
        """Positive coordinate density ``sqrt(abs(det g))`` in the r chart."""

        return canonical(sp.sqrt(-self.metric.det()))

    def hodge_first_pair(self, tensor: Tensor) -> Tensor:
        """Lorentzian Hodge star on the first antisymmetric index pair."""

        inverse = self.inverse
        volume = self.volume_density

        def entry(first: int, second: int, third: int, fourth: int) -> sp.Expr:
            return sum(
                volume
                * sp.LeviCivita(first, second, raised_first, raised_second)
                * inverse[raised_first, lower_first]
                * inverse[raised_second, lower_second]
                * tensor_get(tensor, lower_first, lower_second, third, fourth)
                / 2
                for raised_first, raised_second, lower_first, lower_second in product(
                    INDICES, repeat=4
                )
            )

        return dense_tensor(4, entry)

    def weyl_trace(self, tensor: Tensor) -> sp.Matrix:
        """Contract the first and third indices of an all-lowered tensor."""

        return sp.Matrix(
            DIMENSION,
            DIMENSION,
            lambda second, fourth: canonical(
                sum(
                    self.inverse[first, third]
                    * tensor_get(tensor, first, second, third, fourth)
                    for first, third in product(INDICES, repeat=2)
                )
            ),
        )
