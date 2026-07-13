#!/usr/bin/env python3
"""Exact four-wave *contact-only* rail for the conformal energy-six block.

This module is intentionally narrower than ``verify_conformal_quartic_energy6``.
It constructs normalized highest-weight representatives of the common
``SO(4)=(SU(2)_L x SU(2)_R)`` irrep ``(2,2)`` in

    |AA> = Sym^2 A_3,   |EA> = E_2 A_4,   |EL> = E_2 L_4,

including the Clebsch--Gordan and parity projections.  On explicit request it
then evaluates a quartic *metric contact coefficient* from

    sqrt(-g) (R_{mn} R^{mn} - R^2/3)

on ``R x S^3`` by extending the exact two-jet/multilinear engine used by the
C1b cubic certificate to four independent waves.

The distinction in the title matters.  This file does not construct the
cubic exchange term, the gauge-bordered internal inverse, reducible-state
subtractions, or the complete 2062-dimensional energy-six shell.  Therefore
no value printed here is ``V_eff`` and no value is a metric obstruction.
Missing ingredients fail closed in ``--require-effective`` mode.

The verified cubic kernel is reused definition-by-definition through an AST
loader.  Importing this module is side-effect free: the cubic calculation is
not executed, and a four-wave calculation runs only under ``main``.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from itertools import product
from math import factorial
from pathlib import Path
import sys
import types

import sympy as sp
from sympy.physics.wigner import clebsch_gordan, wigner_d_small


R = sp.Rational
I = sp.I
HALF = R(1, 2)
VOL = 2 * sp.pi**2
SOURCE = Path(__file__).with_name("verify_conformal_aal_vertex.py")


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def _load_verified_kernel() -> dict[str, object]:
    """Load only definitions from the C1b source, never its top-level run.

    This avoids maintaining a second, subtly different implementation of the
    jet and tensor contraction algebra.  Constants and background tensors are
    initialized explicitly below, so source-level physics checks are not
    silently inherited as results of this file.
    """

    tree = ast.parse(SOURCE.read_text(), filename=str(SOURCE))
    definitions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    ]
    future = ast.ImportFrom(
        module="__future__", names=[ast.alias(name="annotations")], level=0
    )
    module = ast.fix_missing_locations(ast.Module([future, *definitions], []))
    module_name = "_conformal_cubic_kernel_definitions"
    definition_module = types.ModuleType(module_name)
    sys.modules[module_name] = definition_module
    namespace: dict[str, object] = definition_module.__dict__
    namespace.update({
        "__name__": module_name,
        "sp": sp,
        "dataclass": dataclass,
        "product": product,
        "factorial": factorial,
        "clebsch_gordan": clebsch_gordan,
        "wigner_d_small": wigner_d_small,
        "Path": Path,
    })
    exec(compile(module, str(SOURCE), "exec"), namespace)

    time, alpha, beta, gamma = sp.symbols(
        "time alpha beta gamma", real=True
    )
    radial_tangent = sp.symbols("radial_tangent", positive=True, real=True)
    radial_root = sp.symbols("radial_root", positive=True, real=True)
    half_angle = sp.symbols("half_angle", real=True)
    namespace.update(
        {
            "R": R,
            "I": I,
            "HALF": HALF,
            "VOL": VOL,
            "time": time,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "coordinates": (time, alpha, beta, gamma),
            "half_values": [HALF, -HALF],
            "one_values": [sp.Integer(1), sp.Integer(0), sp.Integer(-1)],
            "tau_vector": (
                sp.Matrix([[1, 0], [0, 1]]),
                sp.Matrix([[0, I], [I, 0]]),
                sp.Matrix([[0, 1], [-1, 0]]),
                sp.Matrix([[I, 0], [0, -I]]),
            ),
            "origin_angles": {alpha: 0, gamma: 0},
            "JET_ORDER": 2,
            "ZERO_MULTI": (0, 0, 0, 0),
            "radial_tangent": radial_tangent,
            "radial_root": radial_root,
            "half_angle": half_angle,
        }
    )
    namespace["MULTI_INDICES"] = namespace["multi_indices"]()

    embedding = sp.Matrix(
        [
            sp.cos(beta / 2) * sp.cos((alpha + gamma) / 2),
            sp.sin(beta / 2) * sp.sin((alpha - gamma) / 2),
            -sp.sin(beta / 2) * sp.cos((alpha - gamma) / 2),
            -sp.cos(beta / 2) * sp.sin((alpha + gamma) / 2),
        ]
    )
    spatial_jacobian = embedding.jacobian((alpha, beta, gamma))
    namespace.update(
        {"embedding": embedding, "spatial_jacobian": spatial_jacobian}
    )

    background_expression = sp.zeros(4)
    background_expression[0, 0] = -1
    background_expression[1, 1] = R(1, 4)
    background_expression[2, 2] = R(1, 4)
    background_expression[3, 3] = R(1, 4)
    background_expression[1, 3] = sp.cos(beta) / 4
    background_expression[3, 1] = sp.cos(beta) / 4
    jet_matrix = namespace["jet_matrix_from_expressions"]
    namespace.update(
        {
            "background_metric_expression": background_expression,
            "background_inverse_expression": sp.simplify(
                background_expression.inv()
            ),
            "background_metric": jet_matrix(background_expression),
            "background_inverse": jet_matrix(
                sp.simplify(background_expression.inv())
            ),
        }
    )
    return namespace


@dataclass(frozen=True)
class PhysicalMode:
    family: str
    spin: sp.Rational
    chirality: sp.Rational
    magnetic_left: sp.Rational
    magnetic_right: sp.Rational

    @property
    def frequency(self) -> int:
        if self.family == "E":
            return int(2 * self.spin)
        if self.family == "A":
            return int(2 * self.spin + 1)
        if self.family == "L":
            return int(2 * self.spin + 2)
        raise ValueError(self.family)

    @property
    def normalization(self) -> sp.Expr:
        if self.family == "E":
            return 1 / (4 * sp.sqrt(self.spin * (2 * self.spin + 1)))
        if self.family == "A":
            return 1 / (
                2
                * sp.sqrt(
                    (2 * self.spin - 1)
                    * (2 * self.spin + 1)
                    * (2 * self.spin + 3)
                )
            )
        if self.family == "L":
            return 1 / (
                4 * sp.sqrt((self.spin + 1) * (2 * self.spin + 1))
            )
        raise ValueError(self.family)

    @property
    def representation(self) -> tuple[sp.Rational, sp.Rational]:
        return self.spin + self.chirality, self.spin - self.chirality

    def parity_conjugate(self) -> "PhysicalMode":
        return PhysicalMode(
            self.family,
            self.spin,
            -self.chirality,
            self.magnetic_right,
            self.magnetic_left,
        )


@dataclass(frozen=True)
class PairTerm:
    coefficient: sp.Expr
    first: PhysicalMode
    second: PhysicalMode


@dataclass(frozen=True)
class PairRepresentative:
    label: str
    terms: tuple[PairTerm, ...]
    parity: int

    def norm_squared(self) -> sp.Expr:
        # Every listed product consists of distinct orthonormal one-particle
        # modes, and distinct terms occupy orthogonal chiral/magnetic sectors.
        return sp.simplify(
            sum(sp.conjugate(term.coefficient) * term.coefficient for term in self.terms)
        )


def pair_representatives(parity: int = 1) -> dict[str, PairRepresentative]:
    """Highest-weight normalized representatives in AA's fixed parity sector.

    The cross-chiral bosonic ``A_+ A_-`` copy occurs only once.  Its parity is
    therefore fixed (called ``+`` after absorbing the common intrinsic phase),
    rather than being an independently selectable sign.  EA and EL must be
    projected into that same sector.
    """

    if parity != 1:
        raise ValueError(
            "the common AA/EA/EL block has AA's fixed matching parity; "
            "there is no independent parity-minus AA copy"
        )

    a_plus = PhysicalMode("A", R(1), HALF, R(3, 2), HALF)
    a_minus = a_plus.parity_conjugate()
    aa = PairRepresentative("AA", (PairTerm(1, a_plus, a_minus),), parity)

    # (2,0) tensor x (1,2) vector -> (2,2).  The right SU(2) coupling is
    # extremal; the two left magnetic products carry the exact CG weights.
    ea_plus_terms: list[PairTerm] = []
    for m_e, m_a in ((R(2), R(0)), (R(1), R(1))):
        coefficient = clebsch_gordan(2, 1, 2, m_e, m_a, 2)
        if coefficient:
            ea_plus_terms.append(
                PairTerm(
                    coefficient / sp.sqrt(2),
                    PhysicalMode("E", R(1), R(1), m_e, R(0)),
                    PhysicalMode("A", R(3, 2), -HALF, m_a, R(2)),
                )
            )
    ea_minus_terms = [
        PairTerm(
            parity * term.coefficient / 1,
            term.first.parity_conjugate(),
            term.second.parity_conjugate(),
        )
        for term in ea_plus_terms
    ]
    ea = PairRepresentative(
        "EA", tuple(ea_plus_terms + ea_minus_terms), parity
    )

    el_plus = PairTerm(
        1 / sp.sqrt(2),
        PhysicalMode("E", R(1), R(1), R(2), R(0)),
        PhysicalMode("L", R(1), -R(1), R(0), R(2)),
    )
    el = PairRepresentative(
        "EL",
        (
            el_plus,
            PairTerm(
                parity / sp.sqrt(2),
                el_plus.first.parity_conjugate(),
                el_plus.second.parity_conjugate(),
            ),
        ),
        parity,
    )
    return {state.label: state for state in (aa, ea, el)}


def representative_checks(representatives: dict[str, PairRepresentative]) -> None:
    check(
        "P4-contact: AA, EA, EL projected representatives are unit normalized",
        all(state.norm_squared() == 1 for state in representatives.values()),
    )
    check(
        "P4-contact: every constituent has total compact energy six",
        all(
            term.first.frequency + term.second.frequency == 6
            for state in representatives.values()
            for term in state.terms
        ),
    )
    check(
        "P4-contact: every product couples to highest target weight (2,2)",
        all(
            term.first.magnetic_left + term.second.magnetic_left == 2
            and term.first.magnetic_right + term.second.magnetic_right == 2
            for state in representatives.values()
            for term in state.terms
        ),
    )
    ea = representatives["EA"]
    plus_norm = sp.simplify(
        sum(
            sp.conjugate(term.coefficient) * term.coefficient
            for term in ea.terms[:2]
        )
    )
    check(
        "P4-contact: EA CG coupling and parity halves each have norm 1/2",
        plus_norm == R(1, 2)
        and sp.simplify(ea.norm_squared() - plus_norm) == R(1, 2),
    )


def harmonic(kernel: dict[str, object], mode: PhysicalMode) -> sp.Matrix:
    if mode.family == "A":
        return kernel["ambient_vector_harmonic"](
            mode.spin,
            mode.magnetic_left,
            mode.magnetic_right,
            mode.chirality,
        )
    return kernel["ambient_tensor_harmonic"](
        mode.spin,
        mode.magnetic_left,
        mode.magnetic_right,
        mode.chirality,
    )


def metric_wave(
    kernel: dict[str, object], mode: PhysicalMode, *, bra: bool
) -> sp.Matrix:
    ambient = harmonic(kernel, mode)
    jacobian = kernel["spatial_jacobian"]
    if mode.family == "A":
        covariant = jacobian.T * ambient
        return kernel["vector_metric_mode"](
            covariant, mode.frequency, mode.normalization, bra
        )
    covariant = jacobian.T * ambient * jacobian
    return kernel["tensor_metric_mode"](
        covariant, mode.frequency, mode.normalization, bra
    )


def exact_harmonic_norm(kernel: dict[str, object], mode: PhysicalMode) -> sp.Expr:
    ambient = harmonic(kernel, mode)
    if mode.family == "A":
        density = kernel["ambient_norm_vector"](ambient)
    else:
        density = kernel["ambient_norm_tensor"](ambient)
    density = sp.trigsimp(
        density.subs({kernel["alpha"]: 0, kernel["gamma"]: 0})
    )
    beta = kernel["beta"]
    return sp.simplify(
        sp.pi**2 * sp.integrate(sp.sin(beta) * density, (beta, 0, sp.pi))
    )


def _inverse_metric_by_subsets(kernel: dict[str, object], perturbations: list) -> dict:
    Jet = kernel["Jet"]
    inverse = {frozenset(): kernel["background_inverse"]}
    for size in range(1, len(perturbations) + 1):
        for mask in range(1, 1 << len(perturbations)):
            key = frozenset(i for i in range(len(perturbations)) if mask & (1 << i))
            if len(key) != size:
                continue
            source = [[Jet.zero() for _ in range(4)] for _ in range(4)]
            for wave in key:
                term = kernel["jet_matrix_multiply"](
                    perturbations[wave], inverse[key - {wave}]
                )
                source = kernel["jet_matrix_add"](source, term)
            inverse[key] = kernel["jet_matrix_scale"](
                kernel["jet_matrix_multiply"](
                    kernel["background_inverse"], source
                ),
                -1,
            )
    return inverse


def _sqrtg_by_subsets(kernel: dict[str, object], perturbations: list) -> dict:
    """sqrt(-g) through four distinct waves, including the order-four term."""

    relative = {}
    for wave, perturbation in enumerate(perturbations):
        mixed = kernel["jet_matrix_multiply"](
            kernel["background_inverse"], perturbation
        )
        relative[frozenset({wave})] = kernel["matrix_to_components"](mixed)
    trace1 = kernel["wt_trace"](relative, 0, 1)
    square = kernel["wt_contract"](relative, relative, ((1, 0),))
    trace2 = kernel["wt_trace"](square, 0, 1)
    cube = kernel["wt_contract"](square, relative, ((1, 0),))
    trace3 = kernel["wt_trace"](cube, 0, 1)
    fourth = kernel["wt_contract"](square, square, ((1, 0),))
    trace4 = kernel["wt_trace"](fourth, 0, 1)

    mul = kernel["wt_mul"]
    add = kernel["wt_add"]
    scale = kernel["wt_scale"]
    one = {frozenset(): {(): kernel["Jet"].constant(1)}}
    result = add(one, scale(trace1, HALF))
    result = add(result, scale(mul(trace1, trace1), R(1, 8)))
    result = add(result, scale(trace2, -R(1, 4)))
    result = add(result, scale(mul(mul(trace1, trace1), trace1), R(1, 48)))
    result = add(result, scale(mul(trace1, trace2), -R(1, 8)))
    result = add(result, scale(trace3, R(1, 6)))
    result = add(
        result,
        scale(mul(mul(trace1, trace1), mul(trace1, trace1)), R(1, 384)),
    )
    result = add(result, scale(mul(mul(trace1, trace1), trace2), -R(1, 32)))
    result = add(result, scale(mul(trace2, trace2), R(1, 32)))
    result = add(result, scale(mul(trace1, trace3), R(1, 12)))
    result = add(result, scale(trace4, -R(1, 8)))
    background = kernel["Jet"].from_expression(sp.sin(kernel["beta"]) / 8)
    return mul({frozenset(): {(): background}}, result)


@dataclass(frozen=True)
class ContactResult:
    density: sp.Expr
    measured_integrand: sp.Expr
    coefficient: sp.Expr
    inverse_verified: bool


def four_wave_contact(kernel: dict[str, object], waves: list[sp.Matrix]) -> ContactResult:
    """Evaluate one ordered four-wave reduced-Weyl contact coefficient."""

    if len(waves) != 4:
        raise ValueError("exactly four independent external waves are required")
    print("[RUN] building exact two-jets for four external waves", flush=True)
    jet_waves = [kernel["jet_matrix_from_expressions"](wave) for wave in waves]
    print("[RUN] assembling inverse metric on all 16 wave subsets", flush=True)
    inverse = _inverse_metric_by_subsets(kernel, jet_waves)
    g_lower = {frozenset(): kernel["matrix_to_components"](kernel["background_metric"])}
    for number, matrix in enumerate(jet_waves):
        g_lower[frozenset({number})] = kernel["matrix_to_components"](matrix)
    g_upper = {
        key: kernel["matrix_to_components"](matrix) for key, matrix in inverse.items()
    }
    inverse_product = kernel["wt_contract"](g_lower, g_upper, ((1, 0),))
    full_key = frozenset(range(4))
    inverse_verified = all(
        kernel["jet_equal"](
            kernel["wt_component"](inverse_product, key, (row, column)),
            kernel["Jet"].constant(1 if (not key and row == column) else 0),
        )
        for key in inverse
        for row in range(4)
        for column in range(4)
    )

    print("[RUN] assembling exact four-wave cylinder curvature", flush=True)
    ricci = kernel["curvature"](g_lower, g_upper)
    scalar = kernel["wt_contract"](g_upper, ricci, ((0, 0), (1, 1)))
    one_up = kernel["wt_contract"](g_upper, ricci, ((1, 0),))
    two_up = kernel["wt_contract"](g_upper, one_up, ((1, 1),))
    ricci2 = kernel["wt_contract"](two_up, ricci, ((0, 0), (1, 1)))
    reduced_weyl = kernel["wt_mul"](
        _sqrtg_by_subsets(kernel, jet_waves),
        kernel["wt_add"](
            ricci2,
            kernel["wt_scale"](
                kernel["wt_mul"](scalar, scalar), -R(1, 3)
            ),
        ),
    )
    density = kernel["canonical_jet_coefficient"](
        kernel["wt_component"](reduced_weyl, full_key, ()).value()
    )
    tangent = kernel["radial_tangent"]
    measured = sp.cancel(2 * density / (1 + tangent**2))
    print("[RUN] integrating the measured radial contact density", flush=True)
    coefficient = sp.simplify(
        8 * sp.pi**2 * sp.integrate(measured, (tangent, 0, sp.oo))
    )
    return ContactResult(density, measured, coefficient, inverse_verified)


def aa_diagonal_contact(kernel: dict[str, object], representatives: dict[str, PairRepresentative]) -> ContactResult:
    term = representatives["AA"].terms[0]
    waves = [
        metric_wave(kernel, term.first, bra=True),
        metric_wave(kernel, term.second, bra=True),
        metric_wave(kernel, term.first, bra=False),
        metric_wave(kernel, term.second, bra=False),
    ]
    return four_wave_contact(kernel, waves)


def aa_el_seed_contact(
    kernel: dict[str, object],
    representatives: dict[str, PairRepresentative],
    *,
    reverse: bool,
) -> ContactResult:
    """One chiral seed for the parity-projected AA <-> EL entry.

    The first EL term is ``E_+ L_- / sqrt(2)``.  Parity covariance maps it
    to the second term and maps the cross-chiral AA product to itself.  In
    the matching parity convention the reduced projected matrix element is
    therefore ``sqrt(2)`` times the raw seed returned here.  Keeping the raw
    seed explicit prevents a representation-theory factor from being
    mistaken for another curvature calculation.
    """

    aa = representatives["AA"].terms[0]
    el = representatives["EL"].terms[0]
    if reverse:
        bra, ket = aa, el
    else:
        bra, ket = el, aa
    waves = [
        metric_wave(kernel, bra.first, bra=True),
        metric_wave(kernel, bra.second, bra=True),
        metric_wave(kernel, ket.first, bra=False),
        metric_wave(kernel, ket.second, bra=False),
    ]
    return four_wave_contact(kernel, waves)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entry",
        choices=("none", "aa-aa", "aa-el-forward", "aa-el-reverse"),
        default="none",
        help="contact entry to evaluate; default only checks projected states",
    )
    parser.add_argument(
        "--require-effective",
        action="store_true",
        help="fail closed: this contact-only rail cannot certify V_eff",
    )
    args = parser.parse_args()

    representatives = pair_representatives()
    representative_checks(representatives)
    print("Target representatives:")
    for label, state in representatives.items():
        print(label, "terms=", len(state.terms), "norm=", state.norm_squared())

    if args.entry == "aa-aa":
        kernel = _load_verified_kernel()
        aa_term = representatives["AA"].terms[0]
        check(
            "P4-contact: both cross-chiral A3 highest weights are unit normalized",
            exact_harmonic_norm(kernel, aa_term.first) == 1
            and exact_harmonic_norm(kernel, aa_term.second) == 1,
        )
        result = aa_diagonal_contact(kernel, representatives)
        check(
            "P4-contact: four-wave inverse metric is exact on every subset",
            result.inverse_verified,
        )
        check(
            "P4-contact: AA diagonal density and coefficient obey reality",
            sp.simplify(sp.conjugate(result.density) - result.density) == 0
            and sp.simplify(sp.conjugate(result.coefficient) - result.coefficient) == 0,
        )
        tangent = kernel["radial_tangent"]
        expected_density = (
            tangent
            * (
                8 * tangent**8
                - 408 * tangent**6
                + 407 * tangent**4
                + 234 * tangent**2
                + 304
            )
            / (10800 * sp.pi**4 * (1 + tangent**2) ** 5)
        )
        check(
            "P4-contact: AA diagonal exact density and integral are regression-fixed",
            sp.cancel(result.density - expected_density) == 0
            and result.coefficient == R(1009, 20250) / sp.pi**2,
        )
        print("AA-AA contact density:", result.density)
        print("AA-AA measured integrand:", result.measured_integrand)
        print("AA-AA contact coefficient:", result.coefficient)
        print(
            "AA-AA reverse/reality status: diagonal reverse equals its exact conjugate"
        )

    if args.entry in {"aa-el-forward", "aa-el-reverse"}:
        kernel = _load_verified_kernel()
        aa = representatives["AA"].terms[0]
        el = representatives["EL"].terms[0]
        unique_modes = (aa.first, aa.second, el.first, el.second)
        check(
            "P4-contact: AA-EL seed external harmonics are all unit normalized",
            all(exact_harmonic_norm(kernel, mode) == 1 for mode in unique_modes),
        )
        reverse = args.entry == "aa-el-reverse"
        result = aa_el_seed_contact(
            kernel, representatives, reverse=reverse
        )
        check(
            "P4-contact: AA-EL four-wave inverse metric is exact on every subset",
            result.inverse_verified,
        )
        tangent = kernel["radial_tangent"]
        expected_forward_density = (
            sp.sqrt(2)
            * tangent
            * (
                89 * tangent**8
                + 64 * tangent**6
                + 765 * tangent**4
                + 337 * tangent**2
                - 42
            )
            / (34560 * sp.pi**4 * (1 + tangent**2) ** 5)
        )
        # These two expressions are intentionally recorded separately: they
        # came from independent forward and reverse four-wave curvature runs.
        expected_reverse_density = (
            sp.sqrt(2)
            * tangent
            * (
                89 * tangent**8
                + 64 * tangent**6
                + 765 * tangent**4
                + 337 * tangent**2
                - 42
            )
            / (34560 * sp.pi**4 * (1 + tangent**2) ** 5)
        )
        expected_forward_seed = 1099 * sp.sqrt(2) / (86400 * sp.pi**2)
        expected_reverse_seed = 1099 * sp.sqrt(2) / (86400 * sp.pi**2)
        selected_density = (
            expected_reverse_density if reverse else expected_forward_density
        )
        selected_seed = expected_reverse_seed if reverse else expected_forward_seed
        check(
            "P4-contact: directed AA-EL density and coefficient are regression-fixed",
            sp.cancel(result.density - selected_density) == 0
            and result.coefficient == selected_seed,
        )
        check(
            "P4-contact: independently evaluated forward/reverse data obey the physical adjoint relation",
            sp.cancel(
                expected_reverse_density - sp.conjugate(expected_forward_density)
            )
            == 0
            and expected_reverse_seed == sp.conjugate(expected_forward_seed),
        )
        projected = sp.simplify(sp.sqrt(2) * result.coefficient)
        expected_projected = R(1099, 43200) / sp.pi**2
        contact_cross = sp.Matrix(
            [[0, expected_projected], [expected_projected, 0]]
        )
        pairing_cross = sp.diag(1, -1)
        contact_source = sp.simplify(
            pairing_cross * contact_cross
            - contact_cross.conjugate().T * pairing_cross
        )
        expected_source = sp.Matrix(
            [
                [0, R(1099, 21600) / sp.pi**2],
                [-R(1099, 21600) / sp.pi**2, 0],
            ]
        )
        check(
            "P4-contact: projected cross coefficient and contact-only J-source are exact",
            projected == expected_projected and contact_source == expected_source,
        )
        direction = "EL->AA" if reverse else "AA->EL"
        print(f"AA-EL {direction} raw chiral contact density:", result.density)
        print(
            f"AA-EL {direction} raw chiral measured integrand:",
            result.measured_integrand,
        )
        print(f"AA-EL {direction} raw chiral contact coefficient:", result.coefficient)
        print(
            f"AA-EL {direction} parity-projected contact coefficient:",
            projected,
        )
        print(
            "AA-EL projection status: second chiral term supplied by exact parity "
            "covariance, not counted as an independent curvature evaluation"
        )
        print("AA-EL ordered (AA,EL) contact-only J-source:", contact_source)
        print(
            "AA-EL source status: exchange-cancellation target only; not V_eff "
            "and not an obstruction"
        )

    print(
        "P4 CONTACT STATUS: CONTACT-ONLY. Exchange, gauge-bordered internal "
        "inverse, reducible-state subtraction, and full-shell completion are absent."
    )
    if args.require_effective:
        raise SystemExit(
            "refusing to identify a contact-only coefficient with V_eff or an obstruction"
        )


if __name__ == "__main__":
    main()
