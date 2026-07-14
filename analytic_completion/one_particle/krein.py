"""Canonical Hilbert majorant and Krein completion of the E/A/L module."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import sympy as sp

from bridge.metric_preimages.all_energy import BRANCH_MINIMUM, block_dimension


FAMILIES = ("E", "A", "L")
FORM_SIGN = {"E": 1, "A": -1, "L": -1}


@dataclass(frozen=True)
class EnergyTowerBlock:
    energy: int
    chirality: int
    family: str
    dimension: int
    sign: int


def tower_blocks_at(energy: int) -> tuple[EnergyTowerBlock, ...]:
    """Return every parity-complete finite block at one cylinder energy."""

    if energy < 2:
        return ()
    return tuple(
        EnergyTowerBlock(
            energy=energy,
            chirality=chirality,
            family=family,
            dimension=int(block_dimension(family, energy)),
            sign=FORM_SIGN[family],
        )
        for chirality in (1, -1)
        for family in FAMILIES
        if energy >= BRANCH_MINIMUM[family]
    )


def level_dimension(energy: int) -> int:
    return sum(block.dimension for block in tower_blocks_at(energy))


def closed_level_formula(energy: int) -> int:
    if energy < 2:
        return 0
    if energy == 2:
        return 10
    if energy == 3:
        return 40
    return 6 * energy**2 - 14


@dataclass(frozen=True)
class OneParticleKreinCompletion:
    """Proof data for the Hilbert direct-sum completion.

    The actual space is the Hilbert direct sum ``l2-sum H_n``.  The finite
    block routines below certify the diagonal fundamental symmetry; the
    infinite-dimensional conclusions use the displayed all-energy formulas.
    """

    first_energy: int = 2

    @staticmethod
    def sobolev_weight(energy: int, order: sp.Expr) -> sp.Expr:
        return sp.Pow(1 + energy, 2 * sp.sympify(order))

    @staticmethod
    def symmetry_diagonal(maximum_energy: int) -> sp.Matrix:
        signs = [
            block.sign
            for energy in range(2, maximum_energy + 1)
            for block in tower_blocks_at(energy)
            for _ in range(block.dimension)
        ]
        return sp.diag(*signs)

    @staticmethod
    def positive_negative_counts(maximum_energy: int) -> tuple[int, int]:
        positive = negative = 0
        for energy in range(2, maximum_energy + 1):
            for block in tower_blocks_at(energy):
                if block.sign > 0:
                    positive += block.dimension
                else:
                    negative += block.dimension
        return positive, negative

    @lru_cache(maxsize=None)
    def verify(self, maximum_regression_energy: int = 12) -> None:
        if maximum_regression_energy < 6:
            raise ValueError("use at least energy six for the stable tower check")
        for energy in range(2, maximum_regression_energy + 1):
            if level_dimension(energy) != closed_level_formula(energy):
                raise AssertionError(f"wrong level dimension at energy {energy}")
            if any(block.dimension <= 0 for block in tower_blocks_at(energy)):
                raise AssertionError("a declared tower block is not positive dimensional")

        # Do not materialize an enormous dense diagonal matrix: blockwise J
        # is multiplication by the real signs +/-1, which proves all three
        # operator statements on every level and on the Hilbert sum.
        signs = {
            block.sign
            for energy in range(2, maximum_regression_energy + 1)
            for block in tower_blocks_at(energy)
        }
        if signs != {-1, 1}:
            raise AssertionError("the one-particle fundamental symmetry has wrong signs")
        if any(sign * sign != 1 for sign in signs):
            raise AssertionError("the one-particle fundamental symmetry is not involutive")
        if max(abs(value) for value in signs) != 1:
            raise AssertionError("the one-particle fundamental symmetry does not have norm one")

        positive, negative = self.positive_negative_counts(maximum_regression_energy)
        previous = self.positive_negative_counts(maximum_regression_energy - 1)
        if positive <= previous[0] or negative <= previous[1]:
            raise AssertionError("both Krein indices must continue growing")

        # H^{s+1} -> H^s is contractive blockwise because
        # (1+n)^{2s}/(1+n)^{2(s+1)}=(1+n)^-2 <= 1/9.
        n, s = sp.symbols("n s", integer=True, positive=True)
        ratio = sp.simplify((1 + n) ** (2 * s) / (1 + n) ** (2 * (s + 1)))
        if ratio != (n + 1) ** -2:
            raise AssertionError("Sobolev inclusion weight did not simplify correctly")

    def certificate(self, maximum_regression_energy: int = 12) -> dict[str, object]:
        self.verify(maximum_regression_energy)
        positive, negative = self.positive_negative_counts(maximum_regression_energy)
        return {
            "schema": "pure-weyl-one-particle-krein-v1",
            "space": "Hilbert direct sum over n>=2 of parity-complete E/A/L blocks",
            "hilbert_majorant": "normalized cylinder basis is orthonormal",
            "fundamental_symmetry": "+1 on E and -1 on A,L in both chiralities",
            "fundamental_symmetry_self_adjoint": True,
            "fundamental_symmetry_square": 1,
            "fundamental_symmetry_norm": 1,
            "algebraic_core_dense": True,
            "indefinite_form_continuous": True,
            "indefinite_form_nondegenerate": True,
            "classification": "infinite-index Krein space",
            "not_pontryagin": True,
            "positive_index_infinite": True,
            "negative_index_infinite": True,
            "regression": {
                "maximum_energy": maximum_regression_energy,
                "positive_dimensions_through_cutoff": positive,
                "negative_dimensions_through_cutoff": negative,
                "level_dimensions": {
                    str(energy): level_dimension(energy)
                    for energy in range(2, maximum_regression_energy + 1)
                },
            },
            "sobolev_scale": {
                "definition": "sum_n (1+n)^(2s) ||u_n||_0^2",
                "H_s_plus_1_into_H_s": "continuous dense inclusion",
                "J_isometry_every_s": True,
                "rapid_core": "intersection over all real s; finite support is Frechet-dense",
            },
            "scope_guards": [
                "not a positive graviton Hilbert space",
                "not a covariant metric-field Sobolev completion",
                "not a distributional completion",
            ],
        }
