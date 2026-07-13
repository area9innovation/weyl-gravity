#!/usr/bin/env python3
"""Fail-closed exchange rail for the conformal ``AA <-> EL`` contact entry.

The contact calculation fixes a nonzero cross entry in the common energy-six
``(2,2)`` block.  This file determines the *finite* exact exchange problem
that must be solved before that contact number has any deformation-theory
meaning.  It does four things without pretending to supply missing dynamics:

1. derives the unique SO(4) irrep and cylinder Fourier frequency in each of
   the s, t, and u current pairings;
2. constructs the complete scalar-type metric component basis, its indefinite
   field-component Gram matrix, the linearized diffeomorphism-plus-Weyl gauge
   generators, and a conformal de-Donder/Weyl bordered slice;
3. proves that each gauge quotient is one-dimensional and, when its covariant
   Hessian coefficient is nonzero, reduces a complete Ward-satisfying
   exchange to ``a_minus*a_plus/kappa``;
4. exposes an exact archive interface that rejects incomplete currents,
   Hessians, gauge checks, reverse data, or floating-point entries.

The independently generated quadratic coefficients are ``kappa_s=131712``,
``kappa_t=0``, and ``kappa_u=960``.  The t block is Hessian-null and must be
handled by a separate compact-cylinder BRST/Taub/linearization-stability
reduction; it is never treated as an ordinary propagator.  The raw chiral
oscillator currents in that block are now known to be nonzero, so simple
zero-current decoupling is not available before the global-state audit.  No
exchange number is asserted in staging mode.  Synthetic non-null fixtures
test only algebra, signs, inverse-Gram conventions, and bordered solves.
``--require-data`` fails until the global reduction, all retained physics
currents, independently generated reverse data, and the stationary
action-to-Born map are present.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping, Sequence

import sympy as sp


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


Rep = tuple[int, int]  # doubled SU(2)_L x SU(2)_R spins


def su2_product(first2: int, second2: int) -> tuple[int, ...]:
    return tuple(range(abs(first2 - second2), first2 + second2 + 1, 2))


def so4_product(first: Rep, second: Rep) -> set[Rep]:
    return {
        (left, right)
        for left in su2_product(first[0], second[0])
        for right in su2_product(first[1], second[1])
    }


# Chiral seed used by the exact contact calculation.
A_PLUS: Rep = (3, 1)
A_MINUS: Rep = (1, 3)
E_PLUS: Rep = (4, 0)
L_MINUS: Rep = (0, 4)


@dataclass(frozen=True)
class ExchangeSpec:
    label: str
    minus_pair: tuple[str, str]
    plus_pair: tuple[str, str]
    minus_reps: tuple[Rep, Rep]
    plus_reps: tuple[Rep, Rep]
    omega: int
    expected_rep: Rep

    @property
    def common_reps(self) -> set[Rep]:
        return so4_product(*self.minus_reps) & so4_product(*self.plus_reps)

    @property
    def ell(self) -> int:
        if self.expected_rep[0] != self.expected_rep[1]:
            raise ValueError("exchange is not in a scalar-type SO(4) irrep")
        return self.expected_rep[0]


# Signed external frequencies are A ket=-3, E bra=+2, L bra=+4.
EXCHANGE_SPECS = (
    ExchangeSpec(
        "s",
        ("A3+", "A3-"),
        ("E2+", "L4-"),
        (A_PLUS, A_MINUS),
        (E_PLUS, L_MINUS),
        6,
        (4, 4),
    ),
    ExchangeSpec(
        "t",
        ("E2+", "A3+"),
        ("L4-", "A3-"),
        (E_PLUS, A_PLUS),
        (L_MINUS, A_MINUS),
        1,
        (1, 1),
    ),
    ExchangeSpec(
        "u",
        ("E2+", "A3-"),
        ("L4-", "A3+"),
        (E_PLUS, A_MINUS),
        (L_MINUS, A_PLUS),
        1,
        (3, 3),
    ),
)


@dataclass(frozen=True)
class ScalarMetricBlock:
    """Scalar-type metric components for one ``(j,j)`` cylinder harmonic.

    ``ell=2j`` and ``lambda=ell(ell+2)``.  The coefficient basis is

        h00 = x0 Y,
        h0i = x1 nabla_i Y,
        hij = x2 gamma_ij Y + x3 Q_ij[Y],

    where ``Q_ij = nabla_i nabla_j Y + lambda gamma_ij Y/3``.  For ell=1,
    ``Q`` vanishes identically and the last component is omitted.

    The Gram matrix below is the spacetime field-component pairing
    ``int h_mn h^mn``.  It is not the physical conformal Krein form.
    """

    ell: int
    omega: int

    @property
    def laplacian(self) -> int:
        return self.ell * (self.ell + 2)

    @property
    def dimension(self) -> int:
        return 3 if self.ell == 1 else 4

    @property
    def gram(self) -> sp.Matrix:
        lam = sp.Integer(self.laplacian)
        entries = [1, -2 * lam, 3]
        if self.dimension == 4:
            # int Q_ij Q^ij = (2/3) lambda (lambda-3).
            entries.append(R(2, 3) * lam * (lam - 3))
        return sp.diag(*entries)

    def gauge_generator(self, omega: int | None = None) -> sp.Matrix:
        """Columns are (xi_0, longitudinal xi_i, Weyl sigma)."""

        w = sp.Integer(self.omega if omega is None else omega)
        lam = sp.Integer(self.laplacian)
        rows = [
            [-2 * I * w, 0, -2],
            [1, -I * w, 0],
            [0, -R(2, 3) * lam, 2],
        ]
        if self.dimension == 4:
            rows.append([0, 2, 0])
        return sp.Matrix(rows)

    def full_constraints(self, omega: int | None = None) -> sp.Matrix:
        """Projected F_0, longitudinal F_i, and trace constraints.

        ``F_mu = nabla^nu h_munu - nabla_mu h/4`` and ``h=0``.  At
        ``ell=omega=1`` one conformal-Killing gauge parameter and one
        constraint row are redundant; ``constraints`` removes them exactly.
        """

        w = sp.Integer(self.omega if omega is None else omega)
        lam = sp.Integer(self.laplacian)
        tail0: list[sp.Expr] = [] if self.dimension == 3 else [0]
        tail1: list[sp.Expr] = (
            [] if self.dimension == 3 else [-R(2, 3) * (lam - 3)]
        )
        tail2: list[sp.Expr] = [] if self.dimension == 3 else [0]
        return sp.Matrix(
            [
                [R(3, 4) * I * w, -lam, R(3, 4) * I * w, *tail0],
                [R(1, 4), I * w, R(1, 4), *tail1],
                [-1, 0, 3, *tail2],
            ]
        )

    def reduced_gauge_generator(self, omega: int | None = None) -> sp.Matrix:
        generator = self.gauge_generator(omega)
        if self.ell == 1 and abs(self.omega if omega is None else omega) == 1:
            # The null parameter (xi0,xiL,sigma)=(i,1,1) is a conformal
            # Killing reducibility.  Columns 0,1 span the actual gauge orbit.
            return generator[:, (0, 1)]
        return generator

    def constraints(self, omega: int | None = None) -> sp.Matrix:
        constraints = self.full_constraints(omega)
        if self.ell == 1 and abs(self.omega if omega is None else omega) == 1:
            # F_long = -(i/3) F_0 on this harmonic.  F_0 plus trace is a
            # nonsingular slice for the two-dimensional gauge orbit.
            return constraints[(0, 2), :]
        return constraints

    @property
    def B_plus(self) -> sp.Matrix:
        return self.reduced_gauge_generator(self.omega)

    @property
    def B_minus(self) -> sp.Matrix:
        return self.reduced_gauge_generator(-self.omega)

    @property
    def C_plus(self) -> sp.Matrix:
        return self.constraints(self.omega)

    @property
    def C_minus(self) -> sp.Matrix:
        return self.constraints(-self.omega)

    @property
    def current_minus_basis(self) -> sp.Matrix:
        nullspace = self.B_plus.T.nullspace()
        if len(nullspace) != 1:
            raise ValueError("minus-current Ward quotient is not one-dimensional")
        return nullspace[0]

    @property
    def current_plus_basis(self) -> sp.Matrix:
        nullspace = self.B_minus.T.nullspace()
        if len(nullspace) != 1:
            raise ValueError("plus-current Ward quotient is not one-dimensional")
        return nullspace[0]

    @property
    def alternate_C_plus(self) -> sp.Matrix:
        """Gram-orthogonal slice, independent of conformal de Donder."""

        return sp.simplify(self.B_minus.T * self.gram)

    @property
    def alternate_C_minus(self) -> sp.Matrix:
        return sp.simplify(self.B_plus.T * self.gram)


BLOCKS = {
    spec.label: ScalarMetricBlock(spec.ell, spec.omega)
    for spec in EXCHANGE_SPECS
}

# Independently generated by ``verify_conformal_quartic_hessian.py`` from the
# exact two-wave curved-cylinder action.  These are covariant action Hessians,
# not yet stationary Born denominators.
COVARIANT_KAPPA = {
    "s": sp.Integer(131712),
    "t": sp.Integer(0),
    "u": sp.Integer(960),
}
NULL_CONSTRAINT_CHANNELS = frozenset({"t"})

def proportionality(vector: sp.Matrix, basis: sp.Matrix) -> sp.Expr:
    if vector.shape != basis.shape:
        raise ValueError("proportionality shape mismatch")
    ratios: list[sp.Expr] = []
    for value, reference in zip(vector, basis):
        if reference == 0:
            if sp.simplify(value) != 0:
                raise ValueError("vector is not in the declared one-dimensional space")
            continue
        ratios.append(sp.simplify(value / reference))
    if not ratios:
        raise ValueError("zero basis")
    if any(sp.simplify(ratio - ratios[0]) != 0 for ratio in ratios[1:]):
        raise ValueError("vector is not proportional to the declared basis")
    return ratios[0]


def kinetic_proportionality(
    matrix: sp.Matrix, plus_basis: sp.Matrix, minus_basis: sp.Matrix
) -> sp.Expr:
    outer = plus_basis * minus_basis.T
    if matrix.shape != outer.shape:
        raise ValueError("kinetic matrix shape mismatch")
    ratios: list[sp.Expr] = []
    for value, reference in zip(matrix, outer):
        if reference == 0:
            if sp.simplify(value) != 0:
                raise ValueError("Hessian has a component outside the Ward quotient")
            continue
        ratios.append(sp.simplify(value / reference))
    if not ratios:
        raise ValueError("zero kinetic basis")
    if any(sp.simplify(ratio - ratios[0]) != 0 for ratio in ratios[1:]):
        raise ValueError("Hessian does not factor through the one-dimensional quotient")
    return ratios[0]


@dataclass(frozen=True)
class DirectionData:
    current_minus: sp.Matrix  # covector stored as a column
    current_plus: sp.Matrix   # covector stored as a column


@dataclass(frozen=True)
class ChannelData:
    hessian: sp.Matrix
    forward: DirectionData
    reverse: DirectionData


@dataclass(frozen=True)
class ExchangeEvaluation:
    subtraction: sp.Expr
    bordered_subtraction: sp.Expr
    alternate_bordered_subtraction: sp.Expr
    minus_amplitude: sp.Expr
    plus_amplitude: sp.Expr
    kinetic_amplitude: sp.Expr
    current_minus_components: sp.Matrix
    current_plus_components: sp.Matrix


def bordered_inverse_action(
    block: ScalarMetricBlock,
    hessian: sp.Matrix,
    source_plus: sp.Matrix,
    C_plus: sp.Matrix | None = None,
    C_minus: sp.Matrix | None = None,
) -> sp.Matrix:
    """Gauge-bordered inverse of K from plus-current covector to h(+omega)."""

    plus = block.C_plus if C_plus is None else C_plus
    minus = block.C_minus if C_minus is None else C_minus
    if plus.cols != block.dimension or minus.cols != block.dimension:
        raise ValueError("gauge-slice dimension mismatch")
    if plus.rows != minus.rows:
        raise ValueError("plus/minus gauge slices have different ranks")
    zero = sp.zeros(plus.rows, minus.rows)
    bordered = hessian.row_join(minus.T).col_join(
        plus.row_join(zero)
    )
    rhs = source_plus.col_join(sp.zeros(plus.rows, 1))
    if bordered.det() == 0:
        raise ValueError("gauge-bordered quadratic Hessian is singular")
    solution = bordered.inv() * rhs
    field = solution[: block.dimension, :]
    if sp.simplify(plus * field) != sp.zeros(plus.rows, 1):
        raise ValueError("bordered solution violates the gauge slice")
    return field


def evaluate_direction(
    block: ScalarMetricBlock,
    hessian: sp.Matrix,
    direction: DirectionData,
) -> ExchangeEvaluation:
    d = block.dimension
    if hessian.shape != (d, d):
        raise ValueError("wrong Hessian dimension")
    if direction.current_minus.shape != (d, 1) or direction.current_plus.shape != (d, 1):
        raise ValueError("wrong current dimension")

    # Ward identities use ordinary transpose because +/- frequency currents
    # have already been supplied as independent action covectors.
    if sp.simplify(direction.current_minus.T * block.B_plus) != sp.zeros(
        1, block.B_plus.cols
    ):
        raise ValueError("minus-frequency current violates diffeomorphism/Weyl Ward")
    if sp.simplify(block.B_minus.T * direction.current_plus) != sp.zeros(
        block.B_minus.cols, 1
    ):
        raise ValueError("plus-frequency current violates diffeomorphism/Weyl Ward")
    if sp.simplify(hessian * block.B_plus) != sp.zeros(d, block.B_plus.cols):
        raise ValueError("quadratic Hessian has a right gauge variation")
    if sp.simplify(block.B_minus.T * hessian) != sp.zeros(
        block.B_minus.cols, d
    ):
        raise ValueError("quadratic Hessian has a left gauge variation")

    minus_amplitude = proportionality(
        direction.current_minus, block.current_minus_basis
    )
    plus_amplitude = proportionality(
        direction.current_plus, block.current_plus_basis
    )
    kinetic_amplitude = kinetic_proportionality(
        hessian, block.current_plus_basis, block.current_minus_basis
    )
    if kinetic_amplitude == 0:
        raise ValueError("zero scalar-quotient Hessian")
    subtraction = sp.simplify(
        minus_amplitude * plus_amplitude / kinetic_amplitude
    )
    field = bordered_inverse_action(block, hessian, direction.current_plus)
    bordered = sp.simplify((direction.current_minus.T * field)[0, 0])
    if sp.simplify(subtraction - bordered) != 0:
        raise ValueError("one-line quotient and bordered exchange disagree")
    alternate_field = bordered_inverse_action(
        block,
        hessian,
        direction.current_plus,
        block.alternate_C_plus,
        block.alternate_C_minus,
    )
    alternate = sp.simplify(
        (direction.current_minus.T * alternate_field)[0, 0]
    )
    if sp.simplify(subtraction - alternate) != 0:
        raise ValueError("conformal-de-Donder and Gram-orthogonal gauges disagree")

    # Direct action derivatives are covectors.  Multiplication by G^{-1}
    # exposes the corresponding component vectors and, in particular, the
    # negative h0i sign.  No physical Krein sign is inserted here.
    inverse_gram = block.gram.inv()
    return ExchangeEvaluation(
        subtraction,
        bordered,
        alternate,
        minus_amplitude,
        plus_amplitude,
        kinetic_amplitude,
        sp.simplify(inverse_gram * direction.current_minus),
        sp.simplify(inverse_gram * direction.current_plus),
    )


def synthetic_channel(block: ScalarMetricBlock) -> ChannelData:
    """Algebra fixture with unit one-line exchange; not Weyl vertex data."""

    qm = block.current_minus_basis
    qp = block.current_plus_basis
    hessian = qp * qm.T
    forward = DirectionData(qm, qp)
    reverse = DirectionData(qm, qp)
    return ChannelData(hessian, forward, reverse)


def staging_checks() -> None:
    """Fast algebra checks; deliberately invoked only by the CLI."""

    for spec in EXCHANGE_SPECS:
        check(
            f"P4-exchange: {spec.label} pairing has one common SO(4) irrep",
            spec.common_reps == {spec.expected_rep},
        )
        block = BLOCKS[spec.label]
        Bp, Bm, Cp, Cm = (
            block.B_plus,
            block.B_minus,
            block.C_plus,
            block.C_minus,
        )
        check(
            f"P4-exchange: {spec.label} field Gram is exact and nondegenerate",
            block.gram.det() != 0
            and block.gram.inv() * block.gram == sp.eye(block.dimension),
        )
        check(
            f"P4-exchange: {spec.label} diffeo/Weyl orbit and slice have codimension one",
            Bp.rank() == Bm.rank() == block.dimension - 1
            and Cp.rank() == Cm.rank() == block.dimension - 1,
        )
        check(
            f"P4-exchange: {spec.label} bordered gauge slice is transverse",
            (Cp * Bp).det() != 0 and (Cm * Bm).det() != 0,
        )
        check(
            f"P4-exchange: {spec.label} independent Gram-orthogonal slice is transverse",
            (block.alternate_C_plus * Bp).det() != 0
            and (block.alternate_C_minus * Bm).det() != 0,
        )
        check(
            f"P4-exchange: {spec.label} Ward current spaces are one-dimensional",
            len(Bp.T.nullspace()) == len(Bm.T.nullspace()) == 1,
        )

        if spec.label in NULL_CONSTRAINT_CHANNELS:
            null_hessian = sp.zeros(block.dimension)
            try:
                bordered_inverse_action(
                    block, null_hessian, block.current_plus_basis
                )
            except ValueError as error:
                singular_rejected = "singular" in str(error)
            else:
                singular_rejected = False
            check(
                "P4-exchange: t covariant kappa is zero and no ordinary propagator is fabricated",
                COVARIANT_KAPPA[spec.label] == 0 and singular_rejected,
            )
        else:
            fixture = synthetic_channel(block)
            forward = evaluate_direction(block, fixture.hessian, fixture.forward)
            reverse = evaluate_direction(block, fixture.hessian, fixture.reverse)
            check(
                f"P4-exchange: {spec.label} synthetic bordered and one-line contractions agree",
                forward.subtraction == forward.bordered_subtraction == 1
                and forward.alternate_bordered_subtraction == 1
                and reverse.subtraction == reverse.bordered_subtraction == 1
                and reverse.alternate_bordered_subtraction == 1,
            )
            check(
                f"P4-exchange: {spec.label} inverse-Gram current conversion is exact",
                block.gram * forward.current_minus_components
                == fixture.forward.current_minus
                and block.gram * forward.current_plus_components
                == fixture.forward.current_plus,
            )


REQUIRED_RAILS = (
    "pair_projection_and_parity",
    "cubic_minus_currents_independently_generated",
    "cubic_plus_currents_independently_generated",
    "quadratic_hessian_independently_generated",
    "diffeomorphism_and_weyl_ward_identities",
    "component_gram_and_inverse_signs",
    "conformal_de_donder_weyl_bordered_solve",
    "alternate_internal_gauge_independence",
    "constraint_and_auxiliary_components_complete",
    "t_global_brst_taub_reduction",
    "all_s_t_u_pairings",
    "reverse_currents_independently_generated",
    "reverse_physical_adjoint",
    "stationary_action_to_born_mapping",
)


def exact_matrix(rows: Sequence[Sequence[str]]) -> sp.Matrix:
    matrix = sp.Matrix([[sp.sympify(value) for value in row] for row in rows])
    if any(value.has(sp.Float) for value in matrix):
        raise ValueError("floating-point exchange data are forbidden")
    return matrix


def load_archive(path: Path) -> tuple[dict[str, ChannelData], Mapping[str, object]]:
    payload = json.loads(path.read_text())
    rails = payload.get("rails", {})
    missing = [name for name in REQUIRED_RAILS if rails.get(name) is not True]
    if missing:
        raise ValueError("incomplete exchange rails: " + ", ".join(missing))
    records = payload.get("channels", {})
    if set(records) != set(BLOCKS):
        raise ValueError("archive must contain exactly the s, t, and u channels")

    output: dict[str, ChannelData] = {}
    for label, block in BLOCKS.items():
        record = records[label]
        if int(record["ell"]) != block.ell or int(record["omega"]) != block.omega:
            raise ValueError(f"{label}: wrong irrep/frequency block")
        archived_gram = exact_matrix(record["gram"])
        if archived_gram != block.gram:
            raise ValueError(f"{label}: field-component Gram convention mismatch")
        hessian = exact_matrix(record["hessian"])
        forward = DirectionData(
            exact_matrix(record["forward_current_minus"]),
            exact_matrix(record["forward_current_plus"]),
        )
        reverse = DirectionData(
            exact_matrix(record["reverse_current_minus"]),
            exact_matrix(record["reverse_current_plus"]),
        )
        expected_hessian = sp.simplify(
            COVARIANT_KAPPA[label]
            * block.current_plus_basis
            * block.current_minus_basis.T
        )
        if hessian != expected_hessian:
            raise ValueError(
                f"{label}: quadratic Hessian disagrees with the exact covariant certificate"
            )
        if label in NULL_CONSTRAINT_CHANNELS:
            currents = (
                forward.current_minus,
                forward.current_plus,
                reverse.current_minus,
                reverse.current_plus,
            )
            if record.get("global_constraint_reduced") is not True:
                raise ValueError(
                    "t: global BRST/Taub reduction must be declared explicitly"
                )
            if any(current != sp.zeros(block.dimension, 1) for current in currents):
                raise ValueError(
                    "t: a retained Hessian-null block is admissible only after "
                    "global reduction gives a certified zero current"
                )
        output[label] = ChannelData(hessian, forward, reverse)
    return output, payload


def evaluate_archive(data: Mapping[str, ChannelData]) -> tuple[sp.Expr, sp.Expr]:
    forward_total = sp.Integer(0)
    reverse_total = sp.Integer(0)
    for label in ("s", "t", "u"):
        block = BLOCKS[label]
        record = data[label]
        if label in NULL_CONSTRAINT_CHANNELS:
            print(
                "t exchange subtraction: 0 by the archived BRST/constraint "
                "global-reduction certificate; no inverse Hessian used"
            )
            continue
        forward = evaluate_direction(block, record.hessian, record.forward)
        reverse = evaluate_direction(block, record.hessian, record.reverse)
        print(
            f"{label} one-line exchange subtraction:",
            forward.minus_amplitude,
            "*",
            forward.plus_amplitude,
            "/",
            forward.kinetic_amplitude,
            "=",
            forward.subtraction,
        )
        print(f"{label} inverse-Gram minus current:", forward.current_minus_components.T)
        print(f"{label} inverse-Gram plus current:", forward.current_plus_components.T)
        forward_total += forward.subtraction
        reverse_total += reverse.subtraction
    forward_total = sp.simplify(forward_total)
    reverse_total = sp.simplify(reverse_total)
    if sp.simplify(reverse_total - sp.conjugate(forward_total)) != 0:
        raise ValueError("independently supplied reverse exchange is not the physical adjoint")
    return forward_total, reverse_total


def report_blocks() -> None:
    for spec in EXCHANGE_SPECS:
        block = BLOCKS[spec.label]
        print(
            f"{spec.label}: pair frequencies (-{spec.omega},+{spec.omega}), "
            f"rep=({R(spec.expected_rep[0],2)},{R(spec.expected_rep[1],2)}), "
            f"ell={block.ell}, components={block.dimension}"
        )
        print(f"{spec.label} component Gram:", block.gram)
        print(f"{spec.label} reduced gauge generator B(+):", block.B_plus)
        print(f"{spec.label} reduced gauge slice C(+):", block.C_plus)
        print(f"{spec.label} minus-current Ward basis:", block.current_minus_basis.T)
        print(f"{spec.label} plus-current Ward basis:", block.current_plus_basis.T)
        print(f"{spec.label} exact covariant action kappa:", COVARIANT_KAPPA[spec.label])
        if spec.label in NULL_CONSTRAINT_CHANNELS:
            print(
                f"{spec.label} inverse status: Hessian-null constraint block; "
                "ordinary one-line propagator formula is inapplicable"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--require-data", action="store_true")
    args = parser.parse_args()
    staging_checks()
    report_blocks()

    if args.archive is None:
        print(
            "P4 EXCHANGE STATUS: STAGED. Exact covariant Hessians are fixed, but "
            "no complete cubic-current/stationary-Born archive was supplied; no "
            "exchange number, V_eff, or obstruction is claimed."
        )
        if args.require_data:
            raise SystemExit("complete exact AA<->EL exchange data are required but absent")
        return

    data, payload = load_archive(args.archive)
    forward, reverse = evaluate_archive(data)
    print("Exchange archive provenance:", payload.get("provenance", {}))
    print("Complete s+t+u forward exchange subtraction:", forward)
    print("Complete s+t+u reverse exchange subtraction:", reverse)
    print(
        "P4 EXCHANGE STATUS: TARGET ENTRY COMPLETE AT THE ARCHIVED SCOPE. "
        "Combine with contact only through the parent P4 assembly rail."
    )


if __name__ == "__main__":
    main()
