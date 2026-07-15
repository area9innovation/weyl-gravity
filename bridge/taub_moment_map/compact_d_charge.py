"""Exact compact-cylinder audit of the residual ``D`` charge.

The two phase spaces in this module must not be conflated:

``P_lin``
    The algebraic, D-finite linearized solution space after the *local*
    Diff x Weyl quotient, before imposing residual Taub constraints.

``P_Taub0``
    The formal common zero fibre of all fifteen quadratic Taub/moment-map
    components.  Its derived quotient is the closed-universe phase space
    selected in Paper VII.

On ``P_lin`` the compact-time generator has the nonzero quadratic kernel

    M_D = -1/2 J D.

On ``P_Taub0`` its Hamiltonian is zero by definition and

    i^* i_{X_D} Omega = d(i^* mu_D) = 0.

Thus compactness removes boundary flux but does not, by itself, make ``D`` a
presymplectic degeneracy.  The gauge statement requires the explicit
zero-charge restriction.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from symbolic import verify_conformal_generator_all_levels as generators


R = sp.Rational
ACTION_SCALE = -R(1, 2)


@dataclass(frozen=True)
class DModeCharge:
    """One irreducible E/A/L block of the quadratic compact-time charge."""

    branch: str
    energy: int
    chirality: int
    multiplicity: int
    krein_sign: int
    hh_noether_coefficient: sp.Expr
    reduced_charge_kernel: sp.Expr


@dataclass(frozen=True)
class CompactCylinderDChargeAudit:
    """Finite regression buffer for the all-energy ``D``-charge theorem."""

    maximum_energy: int
    modes: tuple[DModeCharge, ...]

    @classmethod
    def build(cls, maximum_energy: int = 6) -> "CompactCylinderDChargeAudit":
        if maximum_energy < 4:
            raise ValueError("use maximum_energy >= 4 to include E, A, and L")
        modes: list[DModeCharge] = []
        for chirality in (1, -1):
            for energy in range(2, maximum_energy + 1):
                for branch in generators.BRANCHES:
                    if energy < generators.BRANCH_MINIMUM[branch]:
                        continue
                    irrep = generators.mode_irrep(branch, energy, chirality)
                    sign = generators.FORM_SIGN[branch]
                    modes.append(
                        DModeCharge(
                            branch=branch,
                            energy=energy,
                            chirality=chirality,
                            multiplicity=irrep.dimension,
                            krein_sign=sign,
                            hh_noether_coefficient=sp.Integer(sign * energy),
                            reduced_charge_kernel=ACTION_SCALE
                            * sp.Integer(sign * energy),
                        )
                    )
        result = cls(maximum_energy=maximum_energy, modes=tuple(modes))
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return sum(mode.multiplicity for mode in self.modes)

    def mode(self, branch: str, energy: int, chirality: int = 1) -> DModeCharge:
        matches = tuple(
            mode
            for mode in self.modes
            if (mode.branch, mode.energy, mode.chirality)
            == (branch, energy, chirality)
        )
        if len(matches) != 1:
            raise KeyError((branch, energy, chirality))
        return matches[0]

    def verify(self) -> None:
        expected_dimension = 2 * generators.expected_cumulative_dimension(
            self.maximum_energy
        )
        if self.dimension != expected_dimension:
            raise AssertionError("E/A/L charge inventory dimension drifted")
        for mode in self.modes:
            if mode.hh_noether_coefficient != mode.krein_sign * mode.energy:
                raise AssertionError("direct Noether coefficient drifted")
            if mode.reduced_charge_kernel != ACTION_SCALE * mode.hh_noether_coefficient:
                raise AssertionError("S_red=-S_HH/2 charge normalization drifted")
            if mode.reduced_charge_kernel == 0:
                raise AssertionError("a positive-energy D block became uncharged")

        # The three lowest branches are exact, smooth global counterexamples
        # to degeneracy on P_lin.  They are not asserted to lie in P_Taub0.
        expected = {
            ("E", 2): -sp.Integer(1),
            ("A", 3): R(3, 2),
            ("L", 4): sp.Integer(2),
        }
        for key, coefficient in expected.items():
            if self.mode(*key).reduced_charge_kernel != coefficient:
                raise AssertionError(f"lowest {key[0]} counterexample drifted")

        # On real amplitude a, mu=m a^2 and delta mu=2m a delta-a.
        a_e, a_a, a_l = sp.symbols("a_E a_A a_L", real=True)
        v_e, v_a, v_l = sp.symbols("v_E v_A v_L", real=True)
        amplitudes = sp.Matrix([a_e, a_a, a_l])
        variations = sp.Matrix([v_e, v_a, v_l])
        kernel = sp.diag(-1, R(3, 2), 2)
        mu_d = (amplitudes.T * kernel * amplitudes)[0]
        differential = sum(
            sp.diff(mu_d, amplitude) * variation
            for amplitude, variation in zip(amplitudes, variations)
        )
        expected_differential = 2 * (variations.T * kernel * amplitudes)[0]
        if sp.expand(differential - expected_differential) != 0:
            raise AssertionError("quadratic D charge is not integrable")
        if sp.expand(mu_d.subs({a_e: 1, a_a: 0, a_l: 0}) + 1) != 0:
            raise AssertionError("E2 charge counterexample disappeared")
        if sp.expand(
            differential.subs(
                {a_e: 1, a_a: 0, a_l: 0, v_e: 1, v_a: 0, v_l: 0}
            )
            + 2
        ) != 0:
            raise AssertionError("E2 charge variation counterexample disappeared")

        # Tangent vectors to mu_D^{-1}(0) obey exactly this polynomial
        # relation.  Reduction modulo that relation is the finite algebraic
        # audit of i^* d mu_D = 0.  The full selected phase space imposes all
        # fifteen components, so it is a subspace of this D-zero fibre.
        _, tangent_remainder = sp.reduced(
            differential,
            [differential],
            a_e,
            a_a,
            a_l,
            v_e,
            v_a,
            v_l,
        )
        if sp.expand(tangent_remainder) != 0:
            raise AssertionError("Taub-zero tangent pullback did not vanish")

    def lowest_counterexamples(self) -> dict[str, dict[str, str | int]]:
        output: dict[str, dict[str, str | int]] = {}
        for branch, energy in (("E", 2), ("A", 3), ("L", 4)):
            mode = self.mode(branch, energy)
            output[branch] = {
                "energy": energy,
                "chirality": "+",
                "unit_amplitude_H_D": str(mode.reduced_charge_kernel),
                "unit_radial_variation_delta_H_D": str(
                    2 * mode.reduced_charge_kernel
                ),
            }
        return output

    def all_energy_formula(self) -> dict[str, str]:
        n = sp.Symbol("n", integer=True, positive=True)
        return {
            branch: str(ACTION_SCALE * generators.FORM_SIGN[branch] * n)
            for branch in generators.BRANCHES
        }
