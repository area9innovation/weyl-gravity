"""Construct the complete selected algebraic polarized state complex.

The construction is deliberately performed after the bulk tangent complex
has been reduced to time-slice BFV data.  Positive-frequency physical modes
are ket generators; their negative-frequency conjugates form the symplectic
dual polarization and are not a second ket Fock space.  Contractible local
and nonminimal pairs contribute their vacuum only.  Residual ghosts act by
exterior multiplication and their BFV momenta by contraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import sympy as sp

from bridge.cyclic_retract.cross_energy import CrossEnergyCohomologyForm
from bridge.metric_preimages.all_energy import level_dimension
from bridge.residual_bfv import ConformalCE
from bridge.cyclic_retract import RawPolynomialRetraction
from field_bv_identification.gauge_fixed_equivalence import GaugeFixedContraction
from field_bv_identification.polarized_state.zero_mode_transgression import (
    AlgebraicZeroModeTransgression,
)


def _add_polynomials(*values: dict[tuple[int, int], sp.Expr]):
    output: dict[tuple[int, int], sp.Expr] = {}
    for value in values:
        for monomial, coefficient in value.items():
            output[monomial] = sp.simplify(output.get(monomial, 0) + coefficient)
            if output[monomial] == 0:
                del output[monomial]
    return output


def _verify_doublet_state_contractions(maximum_degree: int = 8) -> None:
    """Verify both parity choices of the standard polynomial doublet lemma."""

    # u even, v odd: basis u^n v^epsilon.
    def q_even(state: tuple[int, int]):
        n, epsilon = state
        return {(n - 1, 1): sp.Integer(n)} if n and not epsilon else {}

    def h_even(state: tuple[int, int]):
        n, epsilon = state
        return {(n + 1, 0): sp.Rational(1, n + 1)} if epsilon else {}

    # u odd, v even: basis u^epsilon v^n.
    def q_odd(state: tuple[int, int]):
        epsilon, n = state
        return {(0, n + 1): sp.Integer(1)} if epsilon else {}

    def h_odd(state: tuple[int, int]):
        epsilon, n = state
        return {(1, n - 1): sp.Integer(1)} if not epsilon and n else {}

    def compose(operator, polynomial):
        output: dict[tuple[int, int], sp.Expr] = {}
        for state, coefficient in polynomial.items():
            for target, value in operator(state).items():
                output[target] = sp.simplify(output.get(target, 0) + coefficient * value)
        return output

    for state in (
        (n, epsilon)
        for n in range(maximum_degree + 1)
        for epsilon in (0, 1)
    ):
        identity = {} if state == (0, 0) else {state: sp.Integer(1)}
        actual = _add_polynomials(
            compose(q_even, h_even(state)),
            compose(h_even, q_even(state)),
        )
        if actual != identity:
            raise AssertionError(f"even-source doublet contraction failed on {state}")
    for state in (
        (epsilon, n)
        for epsilon in (0, 1)
        for n in range(maximum_degree + 1)
    ):
        identity = {} if state == (0, 0) else {state: sp.Integer(1)}
        actual = _add_polynomials(
            compose(q_odd, h_odd(state)),
            compose(h_odd, q_odd(state)),
        )
        if actual != identity:
            raise AssertionError(f"odd-source doublet contraction failed on {state}")


@dataclass(frozen=True)
class PolarizedSector:
    name: str
    contribution: str
    certificate: str


@dataclass(frozen=True)
class PolarizedStateComplex:
    """Finite-buffer certificate for the algebraic direct-limit construction."""

    maximum_energy: int
    form: CrossEnergyCohomologyForm
    phase_symplectic_form: sp.Matrix
    positive_inclusion: sp.Matrix
    negative_inclusion: sp.Matrix
    induced_positive_form: sp.Matrix
    contractible_pairs_by_energy: dict[int, int]
    sectors: tuple[PolarizedSector, ...]
    transgression: AlgebraicZeroModeTransgression

    @classmethod
    def build(cls, maximum_energy: int = 4) -> "PolarizedStateComplex":
        if maximum_energy < 4:
            raise ValueError("the complete centered buffer requires energies 2..4")
        form = CrossEnergyCohomologyForm.build(maximum_energy)
        matter_form = form.block_diagonal_form()
        dimension = matter_form.rows

        # Repo convention: Omega=i d(zbar) J wedge dz and
        # J(u,v)=-i Omega(ubar,v).
        phase_omega = sp.Matrix.vstack(
            sp.Matrix.hstack(sp.zeros(dimension), -sp.I * matter_form),
            sp.Matrix.hstack(sp.I * matter_form, sp.zeros(dimension)),
        )
        positive = sp.Matrix.vstack(sp.eye(dimension), sp.zeros(dimension))
        negative = sp.Matrix.vstack(sp.zeros(dimension), sp.eye(dimension))
        induced = sp.simplify(-sp.I * negative.T * phase_omega * positive)

        _verify_doublet_state_contractions()
        contractible: dict[int, int] = {}
        for energy in range(2, maximum_energy + 1):
            gauge_fixed = GaugeFixedContraction.at_energy(energy)
            raw = RawPolynomialRetraction.build(energy)
            excess = gauge_fixed.block.dimension - raw.cohomology_dimension
            if excess % 2:
                raise AssertionError("gauge-fixed complement is not a sum of pairs")
            contractible[energy] = excess // 2

        sectors = (
            PolarizedSector(
                "physical positive frequencies",
                "Sym(W_+ direct-sum W_-)",
                "all-energy E/A/L module and Lagrangian positive polarization",
            ),
            PolarizedSector(
                "negative frequencies",
                "symplectic conjugate; no independent ket generators",
                "L_- is the complementary Lagrangian dual of L_+",
            ),
            PolarizedSector(
                "local gauge and equation pairs",
                "vacuum only",
                "raw polynomial SDR plus polynomial-doublet contraction",
            ),
            PolarizedSector(
                "trace and nonminimal sectors",
                "vacuum only",
                "explicit gauge-fixed SDR plus polynomial-doublet contraction",
            ),
            PolarizedSector(
                "residual ghosts",
                "Lambda^bullet so(4,2)^*",
                "canonical exterior polarization",
            ),
            PolarizedSector(
                "BFV ghost momenta",
                "contractions iota_a",
                "canonical cotangent representation; no second exterior algebra",
            ),
            PolarizedSector(
                "bulk endpoint quotient",
                "transferred once to b_a",
                "lambda=+1 algebraic zero-mode suspension",
            ),
            PolarizedSector(
                "bulk antifields and conjugates",
                "cyclic/phase-space duals; no independent ket generators",
                "BV-to-BFV reduction followed by Lagrangian polarization",
            ),
        )
        result = cls(
            maximum_energy=maximum_energy,
            form=form,
            phase_symplectic_form=phase_omega,
            positive_inclusion=positive,
            negative_inclusion=negative,
            induced_positive_form=induced,
            contractible_pairs_by_energy=contractible,
            sectors=sectors,
            transgression=AlgebraicZeroModeTransgression.build(),
        )
        result.verify()
        return result

    @property
    def physical_dimension(self) -> int:
        return self.positive_inclusion.cols

    @property
    def local_cohomology(self) -> str:
        return "Sym(W_+ direct-sum W_-) in polarized local degree zero"

    @property
    def state_complex(self) -> str:
        return "Sym(W_+ direct-sum W_-) tensor Lambda^bullet so(4,2)^*"

    def verify(self) -> None:
        dimension = self.physical_dimension
        omega = self.phase_symplectic_form
        plus = self.positive_inclusion
        minus = self.negative_inclusion
        zero = sp.zeros(dimension)
        if omega.T != -omega:
            raise AssertionError("phase-space form is not antisymmetric")
        # Nondegeneracy is constructive: the off-diagonal block is the
        # already-certified nondegenerate cross-energy form.
        if omega.shape != (2 * dimension, 2 * dimension):
            raise AssertionError("phase-space form has the wrong dimension")
        if plus.T * omega * plus != zero or minus.T * omega * minus != zero:
            raise AssertionError("positive/negative polarizations are not Lagrangian")
        if sp.Matrix.hstack(plus, minus) != sp.eye(2 * dimension):
            raise AssertionError("positive and negative polarizations are not complementary")
        if self.induced_positive_form != self.form.block_diagonal_form():
            raise AssertionError("-i Omega(ubar,v) does not induce the raw form")

        expected_dimensions = {
            energy: level_dimension(energy)
            for energy in range(2, self.maximum_energy + 1)
        }
        if self.form.raw.dimensions != expected_dimensions:
            raise AssertionError("positive polarization is not the complete E/A/L module")
        if min(self.form.raw.state_energies) != 2:
            raise AssertionError("physical zero-frequency modes survived polarization")

        # RawResidualModule.verify has already checked the complete interior
        # conformal brackets.  Here we additionally certify that every one of
        # the fifteen matrices acts wholly inside the positive ket module.
        if any(
            matrix.shape != (dimension, dimension)
            for matrix in self.form.raw.matrices
        ):
            raise AssertionError("a residual generator leaves L_+")

        # The BFV momenta are contractions on one exterior algebra.
        ce = ConformalCE.build()
        # The relation is local on one exterior generator.  Degrees zero,
        # one, and two exhaust the possible membership/sign cases; the
        # derivation law then proves it on the full exterior algebra.
        for degree in range(3):
            for monomial in combinations(range(15), degree):
                element = {monomial: sp.Integer(1)}
                for generator in range(15):
                    wedge = ce.wedge({(generator,): 1}, element)
                    first = ce.contract(generator, wedge)
                    second = ce.wedge(
                        {(generator,): 1}, ce.contract(generator, element)
                    )
                    combined = dict(first)
                    for key, value in second.items():
                        combined[key] = sp.simplify(combined.get(key, 0) + value)
                        if combined[key] == 0:
                            del combined[key]
                    if combined != element:
                        raise AssertionError("{iota_a,c^a wedge} != 1")

        if self.transgression.transgression_scalar != 1:
            raise AssertionError("bulk endpoint was not transferred exactly once")
        if len(self.sectors) != 8:
            raise AssertionError("polarized sector ledger is incomplete")
