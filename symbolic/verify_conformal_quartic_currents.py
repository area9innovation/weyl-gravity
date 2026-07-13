#!/usr/bin/env python3
"""Exact cubic current probes for the conformal energy-six AA <-> EL block.

This certificate supplies the cubic data that the quartic exchange staging
rail deliberately leaves blank.  For each s/t/u partition of the **raw
chiral** ``A_+ A_- <-> E_+ L_-`` seed it evaluates one of two action currents:

* ``negative``: the external pair has frequency ``-omega`` and is completed
  by a bra scalar-metric wave of frequency ``+omega``;
* ``positive``: the pair has frequency ``+omega`` and is completed by a ket
  scalar-metric wave of frequency ``-omega``.

The scalar quotient is one-dimensional.  A slice probe fixes its reduced
current coefficient, while independently assembled pure-gauge probes test
every diffeomorphism/Weyl generator.  At ``kappa_t=0`` no inverse is ever
formed.  The pure-gauge probes vanish but the slice current does not.  The
companion ``verify_conformal_taub_charge.py`` identifies the selected mixed
components exactly as action-normalized Taub charges; the complete global
BRST/Taub reduction remains pending.

All numbers here are stationary covariant-action coefficients.  Conversion
to a time-ordered Born/effective-Hamiltonian convention remains a separate,
fail-closed rail.

The ``E_+L_-`` PairTerm coefficient ``1/sqrt(2)`` is deliberately not folded
into a raw seed current.  A conventional parity-projected oscillator
transition may be formed only after the independently evaluated parity seed
agrees, as

    X_projected = (X_seed + X_parity)/sqrt(2).

Thus equality of two already contracted scalar transition seeds gives
``sqrt(2) X_seed``.  At the uncontracted-current stage the two parity-related
internal components instead retain their explicit ``1/sqrt(2)`` weights in
a direct sum.  A lone seed is never accepted as a projected exchange total.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp

try:
    from symbolic.verify_conformal_quartic_contact import (
        PhysicalMode,
        _load_verified_kernel,
        metric_wave,
        pair_representatives,
    )
    from symbolic.verify_conformal_quartic_exchange import (
        BLOCKS,
        COVARIANT_KAPPA,
    )
    from symbolic.verify_conformal_quartic_hessian import (
        multilinear_reduced_weyl,
        scalar_geometry,
        scalar_metric_wave,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_quartic_contact import (
        PhysicalMode,
        _load_verified_kernel,
        metric_wave,
        pair_representatives,
    )
    from verify_conformal_quartic_exchange import BLOCKS, COVARIANT_KAPPA
    from verify_conformal_quartic_hessian import (
        multilinear_reduced_weyl,
        scalar_geometry,
        scalar_metric_wave,
    )


R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


@dataclass(frozen=True)
class OrientedMode:
    mode: PhysicalMode
    bra: bool

    @property
    def signed_frequency(self) -> int:
        return self.mode.frequency if self.bra else -self.mode.frequency

    def reversed(self) -> "OrientedMode":
        return OrientedMode(self.mode, not self.bra)

    def parity_conjugate(self) -> "OrientedMode":
        return OrientedMode(self.mode.parity_conjugate(), self.bra)


@dataclass(frozen=True)
class CurrentPair:
    modes: tuple[OrientedMode, OrientedMode]
    scalar_magnetic_left: sp.Rational
    scalar_magnetic_right: sp.Rational

    @property
    def signed_frequency(self) -> int:
        return sum(mode.signed_frequency for mode in self.modes)

    def reversed(self) -> "CurrentPair":
        return CurrentPair(
            tuple(mode.reversed() for mode in self.modes),
            self.scalar_magnetic_left,
            self.scalar_magnetic_right,
        )

    def parity_conjugate(self) -> "CurrentPair":
        return CurrentPair(
            tuple(mode.parity_conjugate() for mode in self.modes),
            self.scalar_magnetic_right,
            self.scalar_magnetic_left,
        )


@dataclass(frozen=True)
class ChannelPairs:
    negative: CurrentPair
    positive: CurrentPair

    def reversed(self) -> "ChannelPairs":
        # Reversing all external legs flips the sign of each pair frequency.
        return ChannelPairs(self.positive.reversed(), self.negative.reversed())

    def parity_conjugate(self) -> "ChannelPairs":
        return ChannelPairs(
            self.negative.parity_conjugate(),
            self.positive.parity_conjugate(),
        )


EXPECTED_PROBES: dict[
    tuple[str, str, str, bool, bool],
    tuple[object, sp.Expr, sp.Expr | None],
] = {
    ("t", "negative", "slice", False, False): (
        lambda t: sp.I
        * sp.sqrt(5)
        * t
        * (11 - 7 * t**2)
        / (80 * sp.pi**3 * (1 + t**2) ** 2),
        sp.I * sp.sqrt(5) / (5 * sp.pi),
        sp.I * sp.sqrt(5) / (10 * sp.pi),
    ),
    ("t", "positive", "slice", False, False): (
        lambda t: sp.I
        * sp.sqrt(10)
        * t
        * (11 * t**2 - 3)
        / (160 * sp.pi**3 * (1 + t**2) ** 2),
        sp.I * sp.sqrt(10) / (5 * sp.pi),
        sp.I * sp.sqrt(10) / (10 * sp.pi),
    ),
    ("t", "negative", "slice", False, True): (
        lambda t: sp.I
        * sp.sqrt(5)
        * t
        * (11 - 7 * t**2)
        / (80 * sp.pi**3 * (1 + t**2) ** 2),
        sp.I * sp.sqrt(5) / (5 * sp.pi),
        sp.I * sp.sqrt(5) / (10 * sp.pi),
    ),
    ("t", "positive", "slice", False, True): (
        lambda t: sp.I
        * sp.sqrt(10)
        * t
        * (11 * t**2 - 3)
        / (160 * sp.pi**3 * (1 + t**2) ** 2),
        sp.I * sp.sqrt(10) / (5 * sp.pi),
        sp.I * sp.sqrt(10) / (10 * sp.pi),
    ),
    ("t", "negative", "slice", True, False): (
        lambda t: -sp.I
        * sp.sqrt(10)
        * t
        * (11 * t**2 - 3)
        / (160 * sp.pi**3 * (1 + t**2) ** 2),
        -sp.I * sp.sqrt(10) / (5 * sp.pi),
        -sp.I * sp.sqrt(10) / (10 * sp.pi),
    ),
    ("t", "positive", "slice", True, False): (
        lambda t: -sp.I
        * sp.sqrt(5)
        * t
        * (11 - 7 * t**2)
        / (80 * sp.pi**3 * (1 + t**2) ** 2),
        -sp.I * sp.sqrt(5) / (5 * sp.pi),
        -sp.I * sp.sqrt(5) / (10 * sp.pi),
    ),
    ("t", "negative", "slice", True, True): (
        lambda t: -sp.I
        * sp.sqrt(10)
        * t
        * (11 * t**2 - 3)
        / (160 * sp.pi**3 * (1 + t**2) ** 2),
        -sp.I * sp.sqrt(10) / (5 * sp.pi),
        -sp.I * sp.sqrt(10) / (10 * sp.pi),
    ),
    ("t", "positive", "slice", True, True): (
        lambda t: -sp.I
        * sp.sqrt(5)
        * t
        * (11 - 7 * t**2)
        / (80 * sp.pi**3 * (1 + t**2) ** 2),
        -sp.I * sp.sqrt(5) / (5 * sp.pi),
        -sp.I * sp.sqrt(5) / (10 * sp.pi),
    ),
    ("t", "negative", "gauge-0", False, False): (
        lambda t: 7
        * sp.sqrt(5)
        * t
        * (t**2 - 1)
        / (120 * sp.pi**3 * (1 + t**2) ** 2),
        sp.Integer(0),
        None,
    ),
    ("t", "negative", "gauge-1", False, False): (
        lambda t: 3
        * sp.I
        * sp.sqrt(5)
        * t
        * (t**2 - 1)
        / (20 * sp.pi**3 * (1 + t**2) ** 2),
        sp.Integer(0),
        None,
    ),
    ("t", "positive", "gauge-0", False, False): (
        lambda t: sp.sqrt(10)
        * t
        * (t**2 - 1)
        / (120 * sp.pi**3 * (1 + t**2) ** 2),
        sp.Integer(0),
        None,
    ),
    ("t", "positive", "gauge-1", False, False): (
        lambda t: sp.I
        * sp.sqrt(10)
        * t
        * (t**2 - 1)
        / (40 * sp.pi**3 * (1 + t**2) ** 2),
        sp.Integer(0),
        None,
    ),
}


def channel_pairs() -> dict[str, ChannelPairs]:
    representatives = pair_representatives()
    aa = representatives["AA"].terms[0]
    el = representatives["EL"].terms[0]
    a_plus = aa.first
    a_minus = aa.second
    e_plus = el.first
    l_minus = el.second

    ket = lambda mode: OrientedMode(mode, False)
    bra = lambda mode: OrientedMode(mode, True)
    return {
        "s": ChannelPairs(
            CurrentPair((ket(a_plus), ket(a_minus)), R(2), R(2)),
            CurrentPair((bra(e_plus), bra(l_minus)), R(2), R(2)),
        ),
        "t": ChannelPairs(
            CurrentPair(
                (bra(e_plus), ket(a_plus)), -R(1, 2), R(1, 2)
            ),
            CurrentPair(
                (bra(l_minus), ket(a_minus)), -R(1, 2), R(1, 2)
            ),
        ),
        "u": ChannelPairs(
            CurrentPair(
                (bra(e_plus), ket(a_minus)), -R(3, 2), R(3, 2)
            ),
            CurrentPair(
                (bra(l_minus), ket(a_plus)), -R(3, 2), R(3, 2)
            ),
        ),
    }


def projection_normalization_checks() -> None:
    representatives = pair_representatives()
    aa = representatives["AA"]
    el = representatives["EL"]
    check(
        "P4-current: AA is unit weighted and EL has two 1/sqrt(2) parity seeds",
        len(aa.terms) == 1
        and aa.terms[0].coefficient == 1
        and len(el.terms) == 2
        and all(term.coefficient == 1 / sp.sqrt(2) for term in el.terms),
    )
    raw = sp.Symbol("X_raw")
    check(
        "P4-current: an equal pair of complete transition seeds projects with sqrt(2)",
        sp.simplify((raw + raw) / sp.sqrt(2) - sp.sqrt(2) * raw) == 0,
    )
    parity_even = sp.Matrix([1, 1]) / sp.sqrt(2)
    parity_odd = sp.Matrix([1, -1]) / sp.sqrt(2)
    uncontracted_current = sp.Matrix([raw, raw]) / sp.sqrt(2)
    check(
        "P4-current: uncontracted parity-seed currents retain explicit 1/sqrt(2) weights",
        sp.simplify((parity_even.T * uncontracted_current)[0] - raw) == 0
        and sp.simplify((parity_odd.T * uncontracted_current)[0]) == 0,
    )


def t_zero_mode_audit() -> None:
    """Identify the special t quotient before interpreting its current.

    The ell=omega=1 scalar gauge block carries the conformal-Killing
    reducibility.  Its one-dimensional transverse slice is nevertheless not
    in the reduced gauge orbit, and it pairs nontrivially with the Ward
    cokernel.  Since the covariant Hessian vanishes on that quotient, a
    nonzero slice current is an adjoint-constraint/linearization-stability
    signal.  A companion certificate fixes its selected Taub normalization.
    Calling it BRST-exact or a propagator pole would require additional
    structure not supplied here.
    """

    block = BLOCKS["t"]
    r_plus = sp.Matrix([sp.I, 1, 1])
    r_minus = sp.Matrix([-sp.I, 1, 1])
    check(
        "P4-current: t is the ell=omega=1 conformal-Killing reducibility block",
        block.ell == block.omega == 1
        and block.gauge_generator(1) * r_plus == sp.zeros(3, 1)
        and block.gauge_generator(-1) * r_minus == sp.zeros(3, 1),
    )
    p_minus = block.C_minus.nullspace()[0]
    p_plus = block.C_plus.nullspace()[0]
    check(
        "P4-current: t transverse slices are not reduced pure-gauge vectors",
        block.B_minus.row_join(p_minus).rank() == block.dimension
        and block.B_plus.row_join(p_plus).rank() == block.dimension,
    )
    check(
        "P4-current: t slices pair nontrivially with the adjoint Ward cokernel",
        (p_minus.T * block.current_plus_basis)[0] == 2
        and (block.current_minus_basis.T * p_plus)[0] == 2
        and COVARIANT_KAPPA["t"] == 0,
    )
    # The transverse quotient is the frequency derivative of the reducible
    # conformal-Killing gauge transformation, modulo an ordinary gauge
    # vector.  This is the precise generalized-zero-mode/linearization-
    # stability identification available at the finite component level.
    derivative_plus = sp.Matrix(
        [[-2 * sp.I, 0, 0], [0, -sp.I, 0], [0, 0, 0]]
    )
    derivative_minus = sp.Matrix(
        [[2 * sp.I, 0, 0], [0, sp.I, 0], [0, 0, 0]]
    )
    check(
        "P4-current: t quotient is the frequency derivative of CK reducibility modulo gauge",
        derivative_plus * r_plus
        - 2 * p_plus
        == block.B_plus * sp.Matrix([-2 * sp.I, 1])
        and derivative_minus * r_minus
        - 2 * p_minus
        == block.B_minus * sp.Matrix([2 * sp.I, 1]),
    )


def t_parity_adjoint_regression() -> None:
    def amplitude(side: str, reverse: bool, parity: bool) -> sp.Expr:
        return EXPECTED_PROBES[("t", side, "slice", reverse, parity)][2]

    check(
        "P4-current: t raw parity seeds agree and therefore do not cancel",
        amplitude("negative", False, True)
        == amplitude("negative", False, False)
        and amplitude("positive", False, True)
        == amplitude("positive", False, False),
    )
    check(
        "P4-current: t independently assembled reverse is the physical adjoint",
        amplitude("negative", True, False)
        == sp.conjugate(amplitude("positive", False, False))
        and amplitude("positive", True, False)
        == sp.conjugate(amplitude("negative", False, False))
        and amplitude("negative", True, True)
        == amplitude("negative", True, False)
        and amplitude("positive", True, True)
        == amplitude("positive", True, False),
    )


def probe_vector(label: str, side: str, probe: str) -> sp.Matrix:
    block = BLOCKS[label]
    if side == "negative":
        slice_space = block.C_minus.nullspace()
        generator = block.B_minus
    else:
        slice_space = block.C_plus.nullspace()
        generator = block.B_plus
    if len(slice_space) != 1:
        raise ValueError("scalar quotient slice is not one-dimensional")
    if probe == "slice":
        return slice_space[0]
    if not probe.startswith("gauge-"):
        raise ValueError(probe)
    column = int(probe.removeprefix("gauge-"))
    if not 0 <= column < generator.cols:
        raise ValueError(
            f"{label}/{side} has gauge columns 0..{generator.cols - 1}"
        )
    return generator[:, column]


def reduced_amplitude(label: str, side: str, coefficient: sp.Expr) -> sp.Expr:
    block = BLOCKS[label]
    if side == "negative":
        p_minus = block.C_minus.nullspace()[0]
        denominator = (p_minus.T * block.current_plus_basis)[0]
    else:
        p_plus = block.C_plus.nullspace()[0]
        denominator = (block.current_minus_basis.T * p_plus)[0]
    if denominator == 0:
        raise ValueError("slice does not pair with Ward current")
    return sp.simplify(coefficient / denominator)


def calculate_probe(
    label: str,
    side: str,
    probe: str,
    *,
    reverse: bool,
    parity: bool,
) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    block = BLOCKS[label]
    pairs = channel_pairs()[label]
    if reverse:
        pairs = pairs.reversed()
    if parity:
        pairs = pairs.parity_conjugate()
    pair = pairs.negative if side == "negative" else pairs.positive
    expected_frequency = -block.omega if side == "negative" else block.omega
    check(
        f"P4-current: {label}/{side} external pair has the required signed frequency",
        pair.signed_frequency == expected_frequency,
    )

    kernel = _load_verified_kernel()
    geometry = scalar_geometry(
        kernel,
        block.ell,
        pair.scalar_magnetic_left,
        pair.scalar_magnetic_right,
    )
    coefficients = probe_vector(label, side, probe)
    internal = scalar_metric_wave(
        kernel,
        geometry,
        coefficients,
        block.omega,
        bra=(side == "negative"),
    )
    waves = [
        metric_wave(kernel, oriented.mode, bra=oriented.bra)
        for oriented in pair.modes
    ]
    waves.append(internal)
    print(
        f"[RUN] {label}/{side}/{probe}: exact three-wave current"
        f" (reverse={reverse}, parity={parity})",
        flush=True,
    )
    result = multilinear_reduced_weyl(kernel, waves)
    check(
        f"P4-current: {label}/{side}/{probe} inverse metric is exact",
        result.inverse_verified,
    )
    remaining_symbols = set(result.coefficient.free_symbols) & {
        kernel["time"],
        kernel["alpha"],
        kernel["beta"],
        kernel["gamma"],
    }
    check(
        f"P4-current: {label}/{side}/{probe} is a fully integrated scalar",
        not remaining_symbols and not result.coefficient.has(sp.Integral),
    )
    amplitude = (
        reduced_amplitude(label, side, result.coefficient)
        if probe == "slice"
        else sp.nan
    )
    regression_key = (label, side, probe, reverse, parity)
    if regression_key in EXPECTED_PROBES:
        expected_density, expected_coefficient, expected_amplitude = (
            EXPECTED_PROBES[regression_key]
        )
        tangent = kernel["radial_tangent"]
        check(
            f"P4-current: {label}/{side}/{probe} exact result is regression-fixed",
            sp.cancel(result.density - expected_density(tangent)) == 0
            and result.coefficient == expected_coefficient
            and (
                expected_amplitude is None
                or amplitude == expected_amplitude
            ),
        )
    return (
        result.density,
        result.measured_integrand,
        result.coefficient,
        amplitude,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", choices=tuple(BLOCKS))
    parser.add_argument("side", choices=("negative", "positive"))
    parser.add_argument(
        "probe",
        help="slice or gauge-N; the available N is checked from the block",
    )
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--parity", action="store_true")
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="run normalization/CK/parity-adjoint regressions without curvature",
    )
    parser.add_argument(
        "--require-born-map",
        action="store_true",
        help="fail closed: these are covariant-action, not Born, currents",
    )
    args = parser.parse_args()
    projection_normalization_checks()
    if args.channel == "t":
        t_zero_mode_audit()
        t_parity_adjoint_regression()
    if args.audit_only:
        print(
            "P4 CURRENT AUDIT STATUS: EXACT REGRESSION METADATA ONLY; "
            "no curvature calculation was requested."
        )
        return
    density, measured, coefficient, amplitude = calculate_probe(
        args.channel,
        args.side,
        args.probe,
        reverse=args.reverse,
        parity=args.parity,
    )
    print("Local radial density:", density)
    print("Measured stereographic integrand:", measured)
    print("Integrated cubic action coefficient:", coefficient)
    if args.probe == "slice":
        print("Reduced Ward-quotient current amplitude:", amplitude)
    else:
        check(
            f"P4-current: {args.channel}/{args.side}/{args.probe} direct pure-gauge probe vanishes",
            coefficient == 0,
        )
    print(
        "P4 CURRENT STATUS: EXACT RAW-CHIRAL STATIONARY COVARIANT-ACTION PROBE. "
        "The EL 1/sqrt(2) coefficient and its independently evaluated parity "
        "partner must be restored before any projected transition is formed. "
        "No inverse is formed here and no Born/effective-Hamiltonian value is inferred."
    )
    if args.require_born_map:
        raise SystemExit(
            "stationary covariant-action to effective-Hamiltonian/Born mapping remains required"
        )


if __name__ == "__main__":
    main()
