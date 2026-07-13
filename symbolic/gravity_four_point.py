#!/usr/bin/env python3
"""Reusable exact four-point assembly for Einstein--Weyl gravity.

This is the compact, import-safe part of the G15 construction.  It builds
the quadratic operator and cubic currents directly from the perturbiner,
fixes the internal gauge with a bordered solve, and returns the quartic
contact and each of the three exchange terms separately.  Keeping those
pieces exposed is needed by G17: the quarter-turn must be transported
through the complete connected second-order operator, not applied only to
the final summed number.

The action contains only two- and four-derivative terms, so its quadratic
kernel is even under P -> -P.  The calculator deliberately caches the two
signs separately, allowing a reversed-process check to verify that fact
rather than assume it.
"""
from dataclasses import dataclass

import sympy as sp

from gravity_perturbiner import ETA, R, amplitude, as_eps


SYM10 = tuple((a, b) for a in range(4) for b in range(a, 4))
CHANNELS = (((0, 1), (2, 3)),
            ((0, 2), (1, 3)),
            ((0, 3), (1, 2)))


def basis_tensor(ab):
    """Symmetric-tensor coordinate basis used by the bordered solve."""
    a, b = ab
    tensor = {(a, b): 1}
    if a != b:
        tensor[(b, a)] = 1
    return tensor


def tensor_vector(tensor):
    """Coordinates of a symmetric tensor in ``SYM10`` convention."""
    return sp.Matrix([tensor.get(ab, 0) for ab in SYM10])


def de_donder_constraint(momentum):
    """P^a X_{a mu} - P_mu tr(X)/2 as a 4 x 10 matrix."""
    constraint = sp.zeros(4, 10)
    for mu in range(4):
        for j, ab in enumerate(SYM10):
            tensor = basis_tensor(ab)
            value = sum(ETA[a]*momentum[a]*tensor.get((a, mu), 0)
                        for a in range(4))
            value -= R(1, 2)*momentum[mu]*sum(
                ETA[a]*tensor.get((a, a), 0) for a in range(4))
            constraint[mu, j] = value
    return constraint


def axial_constraint(momentum, normal=(1, 0, 0, 0)):
    """n^a X_{a mu} as a 4 x 10 matrix (``momentum`` fixes the API)."""
    del momentum
    constraint = sp.zeros(4, 10)
    for nu in range(4):
        for j, ab in enumerate(SYM10):
            tensor = basis_tensor(ab)
            constraint[nu, j] = sum(
                ETA[a]*normal[a]*tensor.get((a, nu), 0)
                for a in range(4))
    return constraint


@dataclass(frozen=True)
class ChannelReport:
    constraint_zero: bool
    residual_zero: bool


@dataclass(frozen=True)
class FourPointDecomposition:
    contact: sp.Expr
    exchanges: tuple
    reports: tuple

    @property
    def total(self):
        return sp.simplify(self.contact + sum(self.exchanges, sp.S.Zero))


class FourPointCalculator:
    """Exact contact-plus-exchange calculator with quadratic-kernel cache."""

    def __init__(self):
        self._quadratic_cache = {}

    def quadratic(self, momentum):
        key = tuple(momentum)
        if key in self._quadratic_cache:
            return self._quadratic_cache[key]
        opposite = tuple(-entry for entry in momentum)
        kernel = sp.Matrix(10, 10, lambda i, j: amplitude(
            [basis_tensor(SYM10[i]), basis_tensor(SYM10[j])],
            [list(momentum), list(opposite)]))
        self._quadratic_cache[key] = kernel
        return kernel

    @staticmethod
    def current(eps_a, momentum_a, eps_b, momentum_b, internal_momentum):
        """Cubic current J_A obtained by internal basis insertion."""
        return sp.Matrix([
            amplitude([as_eps(eps_a), as_eps(eps_b), basis_tensor(ab)],
                      [list(momentum_a), list(momentum_b),
                       list(internal_momentum)])
            for ab in SYM10
        ])

    @staticmethod
    def linearized_eom(eps, momentum):
        """Two-point coefficient against every tensor basis direction."""
        opposite = [-entry for entry in momentum]
        return sp.Matrix([
            amplitude([as_eps(eps), basis_tensor(ab)],
                      [list(momentum), opposite])
            for ab in SYM10
        ])

    def decompose(self, polarizations, momenta,
                  constraint=de_donder_constraint):
        """Return contact, s/t/u exchanges, and exact solve residuals."""
        if len(polarizations) != 4 or len(momenta) != 4:
            raise ValueError("four external polarizations and momenta required")

        contact = amplitude([as_eps(eps) for eps in polarizations],
                            [list(momentum) for momentum in momenta])
        exchanges = []
        reports = []
        for (a, b), (c, d) in CHANNELS:
            momentum = [momenta[a][mu] + momenta[b][mu]
                        for mu in range(4)]
            opposite = [-entry for entry in momentum]
            current_ab = self.current(
                polarizations[a], momenta[a], polarizations[b], momenta[b],
                opposite)
            current_cd = self.current(
                polarizations[c], momenta[c], polarizations[d], momenta[d],
                momentum)
            kernel = self.quadratic(momentum)
            gauge = constraint(momentum)

            bordered = sp.zeros(14, 14)
            bordered[:10, :10] = kernel
            bordered[:10, 10:] = gauge.T
            bordered[10:, :10] = gauge
            rhs = sp.zeros(14, 1)
            rhs[:10, 0] = -current_cd
            solution = bordered.LUsolve(rhs)
            field = solution[:10, 0]
            multiplier = solution[10:, 0]

            residual = sp.simplify(
                kernel*field + gauge.T*multiplier + current_cd)
            reports.append(ChannelReport(
                sp.simplify(gauge*field) == sp.zeros(4, 1),
                residual == sp.zeros(10, 1)))
            exchanges.append(sp.simplify((current_ab.T*field)[0, 0]))

        return FourPointDecomposition(
            sp.simplify(contact), tuple(exchanges), tuple(reports))
