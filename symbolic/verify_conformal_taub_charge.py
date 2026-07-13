#!/usr/bin/env python3
"""First exact C2a conformal Taub-charge certificate.

The energy-six ``AA <-> EL`` exchange rail found a Hessian-null scalar block
at ``ell=|omega|=1``.  This script identifies that block with the proper
conformal-Killing reducibility and converts the independently computed cubic
slice and gauge probes into the corresponding *action-normalized* bilinear
Taub functional.

Let ``E^{mn}`` be the lower-metric Euler derivative of

    integral sqrt(-g) (R_mn R^mn - R^2/3).

For the usual Bach-tensor convention this is ``B^{mn}``; retaining the
action-normalized name keeps the certificate independent of an overall Bach
sign convention.  For two external waves define the mixed quadratic
coefficient by

    E(gbar + a h1 + b h2) = a b E^(2)[h1,h2] + ... .

The signed-frequency conformal-Killing parameter ``xi_s`` has ``s=+/-1``
and phase ``exp(-i s time)``.  With future unit normal ``n_m=(-1,0,0,0)``,

    Q_s[h1,h2] = integral_S3 sqrt(gamma) n_m xi_{s,n} E^(2)mn[h1,h2].

The metric probe ``k_s = 2 n_(m xi_{s,n)}`` satisfies

    d_omega (G_s r_s) = i s k_s,

and the exact finite component algebra gives

    d_omega (G_s r_s) = 2 p_s + B_s g_s.

The cubic action coefficient is linear in its third wave, while every column
of ``B_s`` has already been evaluated directly and integrates to zero.
Consequently, if ``C_s`` is the independently computed slice coefficient,

    Q_s = -i s C_s.

This is an operator-normalized equality between the covariant cubic current
and a bilinear Euler/Bach charge.  It is not yet the full 15-component charge
matrix on global BRST cohomology: only the proper-CK component selected by
the low-energy chiral seed and its parity partner are evaluated by direct
curvature here.  The companion ``verify_conformal_taub_multiplets.py``
reconstructs the associated magnetic multiplets by Wigner--Eckart, but still
does not supply the full moment map.  This script therefore has explicit
fail-closed switches for the missing full reduction.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp

try:
    from symbolic.verify_conformal_quartic_currents import EXPECTED_PROBES
    from symbolic.verify_conformal_quartic_exchange import BLOCKS
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_quartic_currents import EXPECTED_PROBES
    from verify_conformal_quartic_exchange import BLOCKS


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


@dataclass(frozen=True)
class ReducibilitySector:
    label: str
    signed_frequency: int
    doubled_representation: tuple[int, int]
    multiplicity: int
    construction_status: str


def conformal_reducibility_sectors() -> tuple[ReducibilitySector, ...]:
    """SO(4) decomposition of the fifteen cylinder CK parameters.

    Doubled representation labels are ``(2 j_L, 2 j_R)``.  The time
    translation and rotations are Killing parameters.  The two ``(1,1)``
    sectors are the proper conformal parameters explicitly realized by the
    scalar gauge block below.
    """

    return (
        ReducibilitySector("time translation", 0, (0, 0), 1, "enumerated"),
        ReducibilitySector("left rotations", 0, (2, 0), 3, "enumerated"),
        ReducibilitySector("right rotations", 0, (0, 2), 3, "enumerated"),
        ReducibilitySector("proper CK +", 1, (1, 1), 4, "constructed"),
        ReducibilitySector("proper CK -", -1, (1, 1), 4, "constructed"),
    )


def enumerate_reducibilities() -> None:
    sectors = conformal_reducibility_sectors()
    check(
        "C2a: cylinder reducibility sectors have exact SO(4,2) dimension fifteen",
        sum(sector.multiplicity for sector in sectors) == 15,
    )
    check(
        "C2a: proper conformal sectors are four scalar ell=1 modes at each signed frequency",
        all(
            sector.doubled_representation == (1, 1)
            and sector.multiplicity == 4
            for sector in sectors
            if abs(sector.signed_frequency) == 1
        ),
    )


@dataclass(frozen=True)
class CKData:
    signed_frequency: int
    parameter: sp.Matrix
    slice_vector: sp.Matrix
    frequency_derivative: sp.Matrix
    gauge_remainder: sp.Matrix
    normal_metric_probe: sp.Matrix


def ck_data(signed_frequency: int) -> CKData:
    if signed_frequency not in (-1, 1):
        raise ValueError("proper CK frequency must be +/-1")
    s = sp.Integer(signed_frequency)
    block = BLOCKS["t"]
    parameter = sp.Matrix([I * s, 1, 1])
    generator = block.gauge_generator(signed_frequency)
    reduced_generator = block.reduced_gauge_generator(signed_frequency)
    constraints = block.constraints(signed_frequency)
    slice_space = constraints.nullspace()
    if len(slice_space) != 1:
        raise AssertionError("proper-CK quotient slice is not one-dimensional")
    slice_vector = slice_space[0]

    # Derivative with respect to the positive frequency magnitude in
    # G(s*omega), evaluated at omega=1.  The common phase derivative drops
    # because G_s r_s=0 at reducibility.
    derivative_matrix = sp.diag(-2 * I * s, -I * s, 0)
    frequency_derivative = derivative_matrix * parameter
    gauge_remainder = sp.Matrix([-2 * I * s, 1])

    # With n_m=(-1,0,0,0), 2 n_(m xi_n) has scalar-component coefficients
    # (-2 xi_0, -xi_L, 0).  Equivalently k_s=-i*s*d_omega(G_s r_s).
    normal_metric_probe = sp.Matrix([-2 * I * s, -1, 0])

    check(
        f"C2a: signed-frequency {signed_frequency:+d} parameter is an exact Diff x Weyl reducibility",
        generator * parameter == sp.zeros(3, 1),
    )
    check(
        f"C2a: signed-frequency {signed_frequency:+d} CK derivative is twice the quotient plus gauge",
        frequency_derivative
        == 2 * slice_vector + reduced_generator * gauge_remainder,
    )
    check(
        f"C2a: signed-frequency {signed_frequency:+d} normal-CK probe has the exact frequency-derivative normalization",
        normal_metric_probe == -I * s * frequency_derivative,
    )
    return CKData(
        signed_frequency,
        parameter,
        slice_vector,
        frequency_derivative,
        gauge_remainder,
        normal_metric_probe,
    )


def expected_probe(
    side: str,
    probe: str,
    *,
    reverse: bool = False,
    parity: bool = False,
) -> tuple[sp.Expr, sp.Expr, sp.Expr | None]:
    density_function, coefficient, amplitude = EXPECTED_PROBES[
        ("t", side, probe, reverse, parity)
    ]
    tangent = sp.symbols("t", positive=True, real=True)
    return density_function(tangent), coefficient, amplitude


@dataclass(frozen=True)
class TaubResult:
    signed_frequency: int
    local_density: sp.Expr
    measured_integrand: sp.Expr
    charge: sp.Expr
    slice_coefficient: sp.Expr


def forward_taub_result(signed_frequency: int) -> TaubResult:
    """Reconstruct a direct forward Taub density from stored curvature runs."""

    s = sp.Integer(signed_frequency)
    side = "positive" if signed_frequency == 1 else "negative"
    tangent = sp.symbols("t", positive=True, real=True)
    slice_density, slice_coefficient, _ = expected_probe(side, "slice")
    gauge0_density, gauge0_coefficient, _ = expected_probe(side, "gauge-0")
    gauge1_density, gauge1_coefficient, _ = expected_probe(side, "gauge-1")

    # k_s=-i*s*(2 p_s + B_s g_s), with
    # (-i*s) g_s = (-2,-i*s).  The third action variation with k_s is
    # twice Q_s because k_s=2 n_(m xi_n).
    local_density = sp.factor(
        (
            -2 * I * s * slice_density
            - 2 * gauge0_density
            - I * s * gauge1_density
        )
        / 2
    )
    measured = sp.factor(2 * local_density / (1 + tangent**2))
    charge = sp.simplify(
        8 * sp.pi**2 * sp.integrate(measured, (tangent, 0, sp.oo))
    )
    algebraic_charge = sp.simplify(-I * s * slice_coefficient)
    check(
        f"C2a: signed-frequency {signed_frequency:+d} direct gauge probes integrate to zero",
        gauge0_coefficient == 0 and gauge1_coefficient == 0,
    )
    check(
        f"C2a: signed-frequency {signed_frequency:+d} local Taub density integrates to -i*s times the slice current",
        charge == algebraic_charge,
    )
    return TaubResult(
        signed_frequency,
        local_density,
        measured,
        charge,
        slice_coefficient,
    )


def charge_from_slice(
    signed_frequency: int,
    *,
    reverse: bool,
    parity: bool = False,
) -> sp.Expr:
    side = "positive" if signed_frequency == 1 else "negative"
    _, coefficient, _ = expected_probe(
        side, "slice", reverse=reverse, parity=parity
    )
    return sp.simplify(-I * signed_frequency * coefficient)


def low_energy_charge_matrices() -> tuple[sp.Matrix, sp.Matrix]:
    """Restricted proper-CK matrices on the four modes touched by P4.

    The ordered chiral basis is ``(E_+, A_+, A_-, L_-)``.  Only entries
    independently supplied by forward/reverse curvature runs are filled.
    These are bilinear Taub matrices on oscillator representatives, not
    operators already descended to global BRST cohomology.
    """

    q_minus_ea = charge_from_slice(-1, reverse=False)
    q_plus_la = charge_from_slice(1, reverse=False)
    q_minus_al = charge_from_slice(-1, reverse=True)
    q_plus_ae = charge_from_slice(1, reverse=True)

    q_minus = sp.zeros(4)
    q_plus = sp.zeros(4)
    q_minus[0, 1] = q_minus_ea  # <E_+|Q_-|A_+>
    q_minus[2, 3] = q_minus_al  # <A_-|Q_-|L_->
    q_plus[3, 2] = q_plus_la  # <L_-|Q_+|A_->
    q_plus[1, 0] = q_plus_ae  # <A_+|Q_+|E_+>

    check(
        "C2a: restricted proper-CK kernels obey the reverse-curvature ordinary dagger relation",
        q_plus == q_minus.conjugate().T,
    )
    check(
        "C2a: parity partners reproduce a second nonzero CK magnetic orbit rather than cancelling",
        all(
            charge_from_slice(s, reverse=reverse, parity=True)
            == charge_from_slice(s, reverse=reverse, parity=False)
            for s in (-1, 1)
            for reverse in (False, True)
        ),
    )
    return q_minus, q_plus


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-full-15",
        action="store_true",
        help="fail closed: only selected proper-CK matrix elements are computed",
    )
    parser.add_argument(
        "--require-global-brst",
        action="store_true",
        help="fail closed: no global-BRST state-space reduction is supplied",
    )
    args = parser.parse_args()

    enumerate_reducibilities()
    for signed_frequency in (-1, 1):
        data = ck_data(signed_frequency)
        print(
            f"signed {signed_frequency:+d} CK parameter:", data.parameter.T
        )
        print(
            f"signed {signed_frequency:+d} normal-CK metric probe:",
            data.normal_metric_probe.T,
        )

    negative = forward_taub_result(-1)
    positive = forward_taub_result(1)
    check(
        "C2a: both selected proper-CK Taub components are exactly nonzero",
        negative.charge == -sp.sqrt(5) / (5 * sp.pi)
        and positive.charge == sp.sqrt(10) / (5 * sp.pi),
    )
    for result in (negative, positive):
        print(
            f"signed {result.signed_frequency:+d} local Taub density:",
            result.local_density,
        )
        print(
            f"signed {result.signed_frequency:+d} measured Taub integrand:",
            result.measured_integrand,
        )
        print(
            f"signed {result.signed_frequency:+d} integrated Taub component:",
            result.charge,
        )

    q_minus, q_plus = low_energy_charge_matrices()
    print("restricted basis: (E_+, A_+, A_-, L_-)")
    print("selected signed-frequency -1 Taub matrix:", q_minus)
    print("selected signed-frequency +1 Taub matrix:", q_plus)
    print(
        "C2a STATUS: EXACT ACTION-NORMALIZED PROPER-CK TAUB COMPONENTS ON "
        "LOW-ENERGY OSCILLATOR REPRESENTATIVES. The equality Q_s=-i*s*C_s "
        "is fixed both locally and after S3 integration. The other CK magnetic "
        "components are not independently curvature-evaluated here; their two "
        "seeded multiplets are reconstructed in the C2b companion. The seven "
        "Killing charges, remaining mode blocks, full moment map, global BRST "
        "cohomology, and nonlinear state-space reduction remain open."
    )
    if args.require_full_15:
        raise SystemExit(
            "full 15-component conformal Taub matrix has not been computed"
        )
    if args.require_global_brst:
        raise SystemExit(
            "global BRST/Taub reduction of the oscillator representatives remains required"
        )


if __name__ == "__main__":
    main()
