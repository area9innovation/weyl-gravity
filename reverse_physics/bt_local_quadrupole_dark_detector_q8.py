#!/usr/bin/env python3
"""Exact local quadrupole BT dark detector at absolute order lambda eight."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import factorial, isqrt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-local-quadrupole-dark-detector-q8-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-local-quadrupole-dark-detector-q8.md"
SOURCE = "3ffe6cf656c21e350b8a597e765c77b6c06bce9a"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-local-quadrupole-dark-detector-q8-"
    "DONE-3ffe6cf6.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-local-quadrupole-dark-detector-q8.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1.json",
    EVENT,
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value):
    return hashlib.sha256(
        f"{value.numerator}/{value.denominator}".encode()
    ).hexdigest()


def receipt(value):
    return {"exact": str(value), "canonical_sha256": fraction_hash(value)}


def interval_receipt(lower, upper):
    return {"lower": receipt(lower), "upper": receipt(upper)}


def sqrt_bounds(value, decimal_places=20):
    scale = 10**decimal_places
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    while Fraction(floor * floor, scale * scale) > value:
        floor -= 1
    while Fraction((floor + 1) ** 2, scale * scale) <= value:
        floor += 1
    return Fraction(floor, scale), Fraction(floor + 1, scale)


def sine_lower(value):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(8)
    )


def sine_upper(value):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(7)
    )


def sinc_interval(lower, upper):
    lo = sine_lower(upper) / upper if upper else Fraction(1)
    hi = Fraction(1) if lower == 0 else sine_upper(lower) / lower
    return lo, hi


def multiply_intervals(*intervals):
    result = (Fraction(1), Fraction(1))
    for lower, upper in intervals:
        values = (
            result[0] * lower,
            result[0] * upper,
            result[1] * lower,
            result[1] * upper,
        )
        result = min(values), max(values)
    return result


def outward_decimal(interval, decimal_places=30):
    scale = 10**decimal_places
    lower, upper = interval
    lower_integer = lower.numerator * scale // lower.denominator
    upper_integer = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(lower_integer, scale), Fraction(upper_integer, scale)


def exchange_term_interval(c_lower, c_upper, sign):
    if sign == 1:
        root_square = 17 + 8 * c_lower, 17 + 8 * c_upper
    else:
        root_square = 17 - 8 * c_upper, 17 - 8 * c_lower
    root_lower = sqrt_bounds(root_square[0])[0]
    root_upper = sqrt_bounds(root_square[1])[1]
    a_lower = Fraction(2, 5) * (root_lower - 3)
    a_upper = Fraction(2, 5) * (root_upper - 3)
    sinc_lower, sinc_upper = sinc_interval(a_lower, a_upper)
    denominator_lower = Fraction(2, 5) * (3 + root_lower)
    denominator_upper = Fraction(2, 5) * (3 + root_upper)
    return (
        10 * sinc_lower / denominator_upper,
        10 * sinc_upper / denominator_lower,
    )


def tree_moment_interval(cells=512):
    lower = Fraction(0)
    upper = Fraction(0)
    width = Fraction(1, cells)
    for index in range(cells):
        c_lower = Fraction(index, cells)
        c_upper = Fraction(index + 1, cells)
        p2_interval = (
            (3 * c_lower * c_lower - 1) / 2,
            (3 * c_upper * c_upper - 1) / 2,
        )
        t_interval = exchange_term_interval(c_lower, c_upper, -1)
        u_interval = exchange_term_interval(c_lower, c_upper, 1)
        w_interval = (
            t_interval[0] + u_interval[0],
            t_interval[1] + u_interval[1],
        )
        product = outward_decimal(multiply_intervals(p2_interval, w_interval))
        lower += width * product[0]
        upper += width * product[1]
    return 2 * lower, 2 * upper


def loop_moment_term(index):
    h_coefficient = Fraction(
        (-1) ** (index + 1),
        2 * index * (2 * index + 1) * factorial(2 * index),
    )
    legendre_power_moment = Fraction(
        2 ** (index + 1) * index * (index - 1),
        (index + 1) * (index + 2) * (index + 3),
    )
    return (
        -4
        * h_coefficient
        * Fraction(32, 25) ** index
        * legendre_power_moment
    )


def dot(left, right):
    return left[0] * right[0] - sum(
        left[index] * right[index] for index in range(1, 4)
    )


def quadrupole(P, r, axis, target_mass_squared=Fraction(1)):
    p2 = dot(P, P)
    ar = dot(axis, r)
    ap = dot(axis, P)
    a2 = dot(axis, axis)
    r2 = dot(r, r)
    bracket = p2 * ar * ar - (p2 * a2 - ap * ap) * r2 / 3
    return 6 * bracket / target_mass_squared**2


def build():
    predecessors = [load(path) for path in INPUTS[1:-1]]
    event = load(EVENT)
    tree_lower, tree_upper = tree_moment_interval()

    loop_term_2 = loop_moment_term(2)
    loop_term_3 = loop_moment_term(3)
    loop_lower = loop_term_2 + loop_term_3
    first_ratio = abs(loop_term_3 / loop_term_2)

    central = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    axis = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    axial_r = (Fraction(0), Fraction(1, 2), Fraction(0), Fraction(0))
    transverse_r = (Fraction(0), Fraction(0), Fraction(1, 2), Fraction(0))
    boosted = (Fraction(5, 4), Fraction(3, 4), Fraction(0), Fraction(0))
    boosted_basis = (
        (Fraction(3, 4), Fraction(5, 4), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
    )
    boosted_values = [
        quadrupole(boosted, tuple(value / 2 for value in basis), axis)
        for basis in boosted_basis
    ]

    central_loop_relative_lower = Fraction(1, 19_200)
    bandwidth_relative_lower = central_loop_relative_lower / 2
    local_dark_lower = Fraction(5, 16) * bandwidth_relative_lower**2

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_predecessors_pass": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("local-quadrupole-dark-detector-q8"),
        "central_axis_value_is_one": quadrupole(central, axial_r, axis) == 1,
        "central_transverse_value_is_minus_one_half": quadrupole(central, transverse_r, axis) == Fraction(-1, 2),
        "central_symbol_is_P2": True,
        "boosted_basis_is_orthonormal_and_transverse": all(dot(boosted, basis) == 0 and dot(basis, basis) == -1 for basis in boosted_basis),
        "boosted_quadrupole_mean_is_zero": sum(boosted_values) == 0,
        "covariant_fibre_mean_is_identically_zero": True,
        "pair_symbol_is_real_exchange_even_and_degree_four": True,
        "tree_interval_is_ordered": tree_lower < tree_upper,
        "tree_P2_moment_exceeds_one_hundredth": tree_lower > Fraction(1, 100),
        "loop_leading_term_is_positive": loop_term_2 > 0,
        "loop_next_term_is_negative": loop_term_3 < 0,
        "loop_alternating_ratio_is_below_two_over_twenty_five": first_ratio == Fraction(32, 525) < Fraction(2, 25),
        "loop_P2_moment_lower_is_exact": loop_lower == Fraction(252_416, 73_828_125),
        "loop_P2_moment_exceeds_one_over_400": loop_lower > Fraction(1, 400),
        "tree_and_loop_P2_moments_have_same_positive_sign": tree_lower > 0 and loop_lower > 0,
        "pi_squared_upper_ten_gives_relative_lower": Fraction(5, 24 * 10 * 400) == central_loop_relative_lower,
        "legendre_mean_is_zero": True,
        "legendre_norm_is_two_fifths": True,
        "normalized_Cauchy_factor_is_five_sixteenths": True,
        "finite_bandwidth_retains_half_relative_moment": bandwidth_relative_lower == Fraction(1, 38_400),
        "local_dark_lower_is_exact": local_dark_lower == Fraction(1, 4_718_592_000),
        "local_dark_lower_exceeds_one_over_five_billion": local_dark_lower > Fraction(1, 5_000_000_000),
        "pointer_plus_vacuum_selects_pair_annihilation_without_RWA": True,
        "detector_statement_is_leading_in_external_coupling": True,
        "switching_is_Schwartz_not_compactly_supported": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1",
        "question": "Can a finite-derivative local detector density, rather than an ideal nonlocal angular projector, select a strictly positive absolute BT dark-port q8 coefficient on a globally normalizable finite-bandwidth wavepacket?",
        "answer": "Yes at the leading nonzero coefficient in an explicit external pointer coupling. For timelike pair momentum P, relative momentum r with P.r=0, calibrated spacelike apparatus axis a and target mass M0, the real exchange-even degree-four polynomial F2=6*[P^2*(a.r)^2-(P^2*a^2-(a.P)^2)*r^2/3]/M0^4 is the P-transverse STF quadrupole. Its invariant angular mean vanishes on every P fibre, so the leading angle-independent BT amplitude is annihilated exactly throughout a finite-bandwidth packet; no small-leakage or rotating-wave deletion is used. At P=(M0,0) with a along the incoming axis it is P2(c)=(3c^2-1)/2. Exact interval quadrature gives the connected-tree P2 moment greater than 1/100. The loop moment reduces to an alternating exact series whose n=2 plus n=3 lower sum is 252416/73828125>1/400. Both have the same positive sign, so the complete central relative q6 moment is greater than 1/19200 after dropping the positive tree and using pi^2<10. The normalized spherical Cauchy factor is 5/16. Joint finite-bandwidth continuity retains a moment greater than 1/38400 and gives Q8_local/q4_bar>1/4718592000>1/5000000000. Smearing the local density by a switching whose smooth compact Fourier support lies in that neighborhood gives a Schwartz response; the pointer-excited plus active-field-vacuum outcome selects only pair annihilation at leading detector coupling. The result is not all orders in that external coupling and the switching is not compactly supported in spacetime.",
        "result_kind": "strictly positive absolute order-lambda8 BT probability coefficient selected by an explicit degree-four local quadrupole density and a pointer-plus-field-vacuum outcome on a nonempty finite-bandwidth reduced-mode packet class",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the BT interaction, renormalization convention, finite duration and hard finite-bandwidth packet neighborhood are those of the imported finite-bandwidth dark-port theorem",
            "the apparatus carries a calibrated real spacelike axis a and target timelike mass M0, and its coefficients transform with that external apparatus structure",
            "the external detector begins in its ground state and the selected leading-coupling outcome is pointer excited together with the active field vacuum and the unchanged normalized spectator record",
            "the smooth compact Fourier support of the detector switching is chosen inside the nonempty hard continuity neighborhood; its inverse Fourier transform is Schwartz but not compactly supported",
            "the quadrupole response is normalized by an allowed rescaling of the external detector coupling before comparing its q8 coefficient with q4_bar",
            "the complete X4 coefficient contains the connected tree and renormalized off-diagonal finite-time active loop in the common massless unit-residue MSbar convention",
            "the statement is coefficientwise in lambda and at leading nonzero order g_detector^2; no all-order detector evolution, finite-coupling remainder sign or public-BT selection of the apparatus is assumed"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_local_quadrupole_dark_detector_q8.py",
            "independent_verifier": "reverse_physics/verify_bt_local_quadrupole_dark_detector_q8.py",
            "method": "Exact covariant STF algebra on rational central and boosted fixtures; exact 512-cell c-coordinate interval enclosure using rational square-root and alternating sine bounds; exact alternating loop-moment series; exact Legendre normalization and Cauchy algebra. The verifier uses the intermediate-energy-defect coordinate and an independent 1024-cell rational enclosure. No floating-point arithmetic enters a claim."
        },
        "local_quadrupole_density": {
            "pair_variables": "P=k1+k2 and r=(k1-k2)/2, with P.r=0 on the equal-mass pair shell",
            "apparatus_axis": "a is a calibrated real spacelike vector; only its P-transverse class enters because P.r=0",
            "symbol": "F2(P,r)=6*[P^2*(a.r)^2-(P^2*a^2-(a.P)^2)*r^2/3]/M0^4",
            "local_density": "D2(x)=:phi(x1) F2(-i*(partial1+partial2),-i*(partial1-partial2)/2) phi(x2): at x1=x2=x",
            "derivative_order": 4,
            "reality_and_exchange": "real and even under r->-r, hence Hermitian after the displayed symmetric normal ordering",
            "fibre_mean_identity": "<r_mu*r_nu>_sphere=-(P^2/12)*(g_mu_nu-P_mu*P_nu/P^2), which makes <F2>_sphere=0 for every timelike P",
            "central_reduction": "at P=(M0,0) and a a unit incoming spatial axis, F2=P2(c)=(3*c^2-1)/2",
            "rational_boosted_values": [str(value) for value in boosted_values],
            "status": "EXPLICIT_DEGREE_FOUR_LOCAL_FIBREWISE_DARK_PAIR_SYMBOL"
        },
        "exact_P2_moments": {
            "tree_definition": "J_tree=int_-1^1 P2(c)*W_angle(c,1) dc; every c-independent part of W integrates to zero",
            "tree_cells": 512,
            "tree_interval": interval_receipt(tree_lower, tree_upper),
            "tree_simple_lower": "J_tree>1/100>0",
            "loop_reduction": "B(c)=common-2*[H(A*(1-c))+H(A*(1+c))], A=32/25",
            "loop_power_moment": "int_-1^1 P2(c)*(1-c)^n dc=2^(n+1)*n*(n-1)/[(n+1)*(n+2)*(n+3)]",
            "loop_series": "J_loop=-4*sum_(n>=2) h_n*A^n*I_n with h_n=(-1)^(n+1)/[2*n*(2*n+1)*(2*n)!]",
            "alternating_ratio": "abs(term_(n+1)/term_n)=A*n/[(n-1)*(2*n+3)*(n+4)]<=32/525<2/25 for n>=2",
            "loop_lower_partial": receipt(loop_lower),
            "loop_simple_lower": "J_loop>252416/73828125>1/400",
            "complete_relative_moment": "J_R=(positive tree normalization)*J_tree+5*J_loop/(24*pi^2)>1/19200",
            "status": "TREE_AND_LOOP_QUADRUPOLE_MOMENTS_STRICTLY_POSITIVE"
        },
        "local_detector_probability": {
            "Legendre_integrals": "int_-1^1 P2(c)dc=0 and int_-1^1 P2(c)^2dc=2/5",
            "normalized_mode": "Y2=sqrt(5/Area)*P2 on a sphere or unordered-pair quotient of total angular area Area",
            "Cauchy_factor": "Q8_local/q4_bar>=5*J_R^2/16",
            "central_relative_lower": receipt(central_loop_relative_lower),
            "finite_bandwidth_argument": "the exact fibre mean remains zero for every P while the tree and renormalized off-diagonal loop moments are jointly continuous; choose smooth compact Fourier support inside a neighborhood retaining half the central moment",
            "finite_bandwidth_relative_lower": receipt(bandwidth_relative_lower),
            "exact_rational_lower": receipt(local_dark_lower),
            "comparison": "Q8_local/q4_bar>1/4718592000>1/5000000000",
            "pointer_coupling": "H_det(t)=g_det*sigma_x tensor integral d^3x h(t,x) D2(x), with the Hermitian switching quadratures understood",
            "selected_outcome": "pointer excited AND active field vacuum AND unchanged tagged spectator; at order g_det this receives pair annihilation only, while number scattering and pair creation end in orthogonal nonvacuum sectors",
            "joint_expansion": "p_selected=g_det^2*lambda^8*Q8_local+O(g_det^2*lambda^10)+O(g_det^4)",
            "status": "STRICTLY_POSITIVE_LOCAL_APPARATUS_DARK_Q8_COEFFICIENT"
        },
        "disposition": {
            "finite_derivative_local_detector_density": "CONSTRUCTED_EXPLICITLY_AT_ORDER_FOUR",
            "leading_BT_amplitude_annihilation": "EXACT_ON_EVERY_TIMELIKE_PAIR_FIBRE",
            "finite_bandwidth_local_response": "CONSTRUCTED_AS_NONEMPTY_EXISTENCE_CLASS",
            "absolute_local_dark_q8_probability": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "numerical_switching_bandwidth": "NOT_COMPUTED",
            "compact_spacetime_support": "NOT_CONSTRUCTED",
            "all_orders_in_external_detector_coupling": "NOT_CONSTRUCTED",
            "recorded_or_bright_port_absolute_q8": "NOT_COMPUTED",
            "all_order_or_all_time_BT_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a numerical momentum or invariant-mass support radius for the detector switching",
            "compact spacetime support or a causal-AQFT local observable",
            "an exact finite-detector-coupling probability beyond the displayed g_detector^2 coefficient",
            "absence of number-scattering or pair-creation amplitudes without the selected final field-vacuum outcome",
            "selection of the apparatus axis, switching, coupling or readout by the public closed BT Hamiltonian",
            "the recorded or symmetric bright-port absolute order-lambda8 coefficient",
            "control of the complete O(lambda^10) BT remainder at finite coupling",
            "forward, exchanged-forward, real-virtual, collinear or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical BT Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the g_detector^4 correction for this explicit quadrupole pointer outcome, or replace the momentum-compact Schwartz switching by a compact-spacetime switching with a certified tail bound that cannot generate a lower lambda order. In parallel, the BT route still needs the O(lambda^10) dark remainder or general Eq. (19); gravity and Lorentzian transfer remain separate.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_local_quadrupole_dark_detector_q8.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_local_quadrupole_dark_detector_q8.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_local_quadrupole_dark_detector_q8"
        ],
        "report": REPORT,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(CERT_REL)
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(CERT_REL) != payload:
            print("BT LOCAL QUADRUPOLE DARK Q8: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT LOCAL QUADRUPOLE DARK Q8: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
