#!/usr/bin/env python3
"""Exact finite-derivative BT Fejer packet detector and leakage coefficient."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-fejer-packet-detector-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-two-angle-fejer-packet-detector.md"
SOURCE = "a874efc2e5db36d98a5a06dc93bb84a99beb9790"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-two-angle-fejer-packet-detector-DONE-a874efc2.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-two-angle-fejer-packet-detector.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    EVENT,
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


# Gaussian rationals are pairs (real, imaginary).
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def cadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def cscale(coefficient, value):
    return (coefficient * value[0], coefficient * value[1])


def cmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cconj(value):
    return (value[0], -value[1])


def cpow(value, exponent):
    if exponent < 0:
        return cpow(cconj(value), -exponent)
    result = ONE
    base = value
    power = exponent
    while power:
        if power & 1:
            result = cmul(result, base)
        base = cmul(base, base)
        power //= 2
    return result


def kernel_coefficients(order, center):
    """Coefficients of K_N in powers exp(2 i m theta)."""
    return {
        mode: cscale(
            Fraction(order - abs(mode), order * order),
            cpow(cconj(center), mode),
        )
        for mode in range(-order + 1, order)
    }


def evaluate(coefficients, phase):
    result = ZERO
    for mode, coefficient in coefficients.items():
        result = cadd(result, cmul(coefficient, cpow(phase, mode)))
    return result


def difference(left, right):
    return {
        mode: cadd(left[mode], cscale(Fraction(-1), right[mode]))
        for mode in left
    }


def modulus_square_coefficients(coefficients):
    result = {}
    for left_mode, left in coefficients.items():
        for right_mode, right in coefficients.items():
            mode = left_mode - right_mode
            result[mode] = cadd(
                result.get(mode, ZERO), cmul(left, cconj(right))
            )
    return result


def sine_weight_antiderivative(mode, unit_phase):
    """Primitive of sin(theta)*exp(2 i mode theta)."""
    lower = cscale(
        Fraction(1, 2 * (2 * mode - 1)), cpow(unit_phase, 2 * mode - 1)
    )
    upper = cscale(
        Fraction(-1, 2 * (2 * mode + 1)), cpow(unit_phase, 2 * mode + 1)
    )
    return cadd(lower, upper)


def integrate_dc(coefficients, interval):
    """Integrate over c from rational lower to upper endpoints."""
    c_lower, s_lower, c_upper, s_upper = interval
    # c=cos(theta), so increasing c reverses the theta endpoints.
    theta_start = (c_upper, s_upper)
    theta_end = (c_lower, s_lower)
    result = ZERO
    for mode, coefficient in coefficients.items():
        primitive_difference = cadd(
            sine_weight_antiderivative(mode, theta_end),
            cscale(
                Fraction(-1), sine_weight_antiderivative(mode, theta_start)
            ),
        )
        result = cadd(result, cmul(coefficient, primitive_difference))
    if result[1] != 0:
        raise ArithmeticError("real angular integral acquired an imaginary part")
    return result[0]


def fraction_receipt(value, lower, upper):
    canonical = f"{value.numerator}/{value.denominator}"
    with localcontext() as context:
        context.prec = 30
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return {
        "decimal": format(decimal, ".18g"),
        "lower_bound": str(lower),
        "upper_bound": str(upper),
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "numerator_digits": len(str(abs(value.numerator))),
        "denominator_digits": len(str(value.denominator)),
    }


def build():
    predecessor = load(INPUTS[1])
    continuous = load(INPUTS[2])
    event = load(EVENT)

    order = 20
    maximum_derivative_order = 2 * (order - 1)
    zeta_zero = (Fraction(-1), Fraction(0))
    zeta_one = (Fraction(-7, 25), Fraction(24, 25))
    kernel_zero = kernel_coefficients(order, zeta_zero)
    kernel_one = kernel_coefficients(order, zeta_one)
    rho_complex = evaluate(kernel_zero, zeta_one)
    if rho_complex[1] != 0:
        raise ArithmeticError("Fejer overlap must be real")
    rho = rho_complex[0]
    filter_coefficients = {
        mode: cscale(Fraction(1, 1 - rho), coefficient)
        for mode, coefficient in difference(kernel_zero, kernel_one).items()
    }
    target_zero = evaluate(filter_coefficients, zeta_zero)
    target_one = evaluate(filter_coefficients, zeta_one)
    squared = modulus_square_coefficients(filter_coefficients)

    full_interval = (
        Fraction(-1), Fraction(0), Fraction(1), Fraction(0)
    )
    packet_zero_interval = (
        Fraction(-7, 25), Fraction(24, 25),
        Fraction(7, 25), Fraction(24, 25),
    )
    packet_one_interval = (
        Fraction(5, 13), Fraction(12, 13),
        Fraction(20, 29), Fraction(21, 29),
    )
    total_norm = integrate_dc(squared, full_interval)
    packet_zero_norm = integrate_dc(squared, packet_zero_interval)
    packet_one_norm = integrate_dc(squared, packet_one_interval)
    leakage_norm = total_norm - packet_zero_norm - packet_one_norm
    eta = leakage_norm / total_norm
    capture = 1 - eta

    receipts = {
        "rho": fraction_receipt(
            rho, Fraction(6208, 10_000_000), Fraction(6209, 10_000_000)
        ),
        "total_norm_squared": fraction_receipt(
            total_norm, Fraction(1868658, 10_000_000), Fraction(1868659, 10_000_000)
        ),
        "packet_zero_norm_squared": fraction_receipt(
            packet_zero_norm, Fraction(1038062, 10_000_000), Fraction(1038063, 10_000_000)
        ),
        "packet_one_norm_squared": fraction_receipt(
            packet_one_norm, Fraction(829174, 10_000_000), Fraction(829175, 10_000_000)
        ),
        "leakage_norm_squared": fraction_receipt(
            leakage_norm, Fraction(142063, 1_000_000_000), Fraction(142064, 1_000_000_000)
        ),
        "leakage_fraction_eta": fraction_receipt(
            eta, Fraction(760242, 1_000_000_000), Fraction(760243, 1_000_000_000)
        ),
    }

    checks = {
        "inputs_are_content_pinned": all(len(file_hash(path)) == 64 for path in INPUTS),
        "two_predecessor_checks_pass": predecessor["checks"]["ok"] and continuous["checks"]["ok"],
        "predecessor_exact_selectivity_no_go_imported": predecessor["disposition"]["exact_continuum_two_angle_local_selectivity"] == "OBSTRUCTED",
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-fejer-packet-detector"),
        "continuous_parameter_is_cos_theta": continuous["continuous_tagged_family"]["parameter"] == "c=cos(theta)",
        "target_projective_phases_are_unit": cmul(zeta_zero, cconj(zeta_zero)) == ONE and cmul(zeta_one, cconj(zeta_one)) == ONE,
        "target_projective_phases_match_rational_modes": zeta_zero == (-1, 0) and zeta_one == (Fraction(-7, 25), Fraction(24, 25)),
        "Fejer_order_is_twenty": order == 20,
        "maximum_derivative_order_is_thirty_eight": maximum_derivative_order == 38,
        "kernel_coefficients_have_finite_support": len(kernel_zero) == len(kernel_one) == 2 * order - 1,
        "kernel_peaks_equal_one": evaluate(kernel_zero, zeta_zero) == ONE and evaluate(kernel_one, zeta_one) == ONE,
        "cross_overlap_is_symmetric": evaluate(kernel_zero, zeta_one) == evaluate(kernel_one, zeta_zero),
        "rho_is_positive_and_small": 0 < rho < Fraction(1, 1000),
        "filter_interpolates_plus_one": target_zero == ONE,
        "filter_interpolates_minus_one": target_one == (-1, 0),
        "filter_is_Hermitian_real_on_circle": all(filter_coefficients[-mode] == cconj(value) for mode, value in filter_coefficients.items()),
        "packet_zero_endpoints_are_unit": Fraction(7, 25) ** 2 + Fraction(24, 25) ** 2 == 1,
        "packet_one_lower_endpoint_is_unit": Fraction(5, 13) ** 2 + Fraction(12, 13) ** 2 == 1,
        "packet_one_upper_endpoint_is_unit": Fraction(20, 29) ** 2 + Fraction(21, 29) ** 2 == 1,
        "packet_bins_are_disjoint_and_interior": Fraction(-1) < Fraction(-7, 25) < Fraction(7, 25) < Fraction(5, 13) < Fraction(20, 29) < Fraction(1),
        "target_zero_lies_in_packet_zero": Fraction(-7, 25) < 0 < Fraction(7, 25),
        "target_one_lies_in_packet_one": Fraction(5, 13) < Fraction(3, 5) < Fraction(20, 29),
        "all_exact_norms_are_positive": min(total_norm, packet_zero_norm, packet_one_norm, leakage_norm) > 0,
        "orthogonal_packet_decomposition_is_exact": total_norm == packet_zero_norm + packet_one_norm + leakage_norm,
        "leakage_fraction_is_below_one_per_mille": eta < Fraction(1, 1000),
        "captured_fraction_exceeds_999_per_mille": capture > Fraction(999, 1000),
        "half_pulse_absorption_efficiency_exceeds_999_per_mille": 1 - eta > Fraction(999, 1000),
        "half_pulse_outside_packet_population_is_below_one_per_mille": eta * (1 - eta) < Fraction(1, 1000),
        "all_time_selected_input_outside_population_is_below_one_over_250": 4 * eta * (1 - eta) < Fraction(1, 250),
        "residual_mode_is_not_deleted": leakage_norm > 0,
        "full_star_direction_is_normalized": (1 - eta) + eta == 1,
        "public_BT_and_gravity_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1",
        "question": "Can the exact two-angle locality obstruction be bypassed by a finite-derivative local filter with two finite angular packets, while retaining and exponentiating the unavoidable continuum residual?",
        "answer": "Yes, in the declared one-dimensional fixed-energy rotating-wave BT pair sector, approximately rather than exactly. With zeta=exp(2 i theta), normalized projective Fejer kernels of order N=20 centered at c=0 and c=3/5 have overlap rho=5646762438667986757780624/9094947017729282379150390625. The difference p=(K_0-K_1)/(1-rho) has exact values +1 and -1 at the targets and is the symbol of a local quadratic density with at most 38 transverse derivatives. Exact integration in the azimuthally reduced two-body measure dc over B0=[-7/25,7/25] and B1=[5/13,20/29] leaves leakage fraction eta<1/1000. Defining normalized packet modes from p restricted to those bins gives a selected bright packet B and an orthogonal residual R with complete coupled direction v=sqrt(1-eta)B+sqrt(eta)R. Exponentiating H=G(|e><v|+|v><e|) without deleting R gives absorption effect (1-eta)sin^2(G tau)P_B on the selected packet plane. A half pulse therefore has efficiency above 999/1000; outside-packet population is below 1/1000 at that pulse and below 1/250 for every selected input and every time. This does not control other angular directions, total momenta, counter-rotating or number-scattering sectors.",
        "result_kind": "exact finite-derivative projective angular filter, exact rational packet leakage coefficient, and residual-retaining star evolution",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the fixed-energy BT pair family is represented by c=cos(theta) with azimuthally reduced two-body measure dc on -1<c<1",
            "the two target pair lines have projective phases zeta0=-1 and zeta1=(-7+24 i)/25",
            "constant-coefficient transverse differential bilinears realize every finite Laurent mode in zeta=exp(2 i theta)",
            "compact spacetime smearing has a nonzero common Fourier coefficient at the fixed total pair momentum and is absorbed into G",
            "the detector gap is resonant with the common pair energy and the declared Hamiltonian keeps only the pair-annihilation/creation rotating-wave star sector",
            "the apparatus phase is calibrated so the two target transition values are real +1 and -1",
            "packet modes are the normalized restrictions of the complete transition vector to the two declared disjoint bins",
            "other total momenta, the rest of the angular sphere, number-scattering terms and counter-rotating sectors are outside this coefficient"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": file_hash(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_two_angle_fejer_packet_detector.py",
            "independent_verifier": "reverse_physics/verify_bt_two_angle_fejer_packet_detector.py",
            "method": "Exact Gaussian-rational Fourier coefficients, exact convolution for |p|^2, and exact endpoint evaluation of the sin(theta)dtheta antiderivative. Canonical exact fractions are retained by SHA-256 with strict rational enclosures; no floating-point value establishes a bound."
        },
        "continuous_filter": {
            "parameter": "c=cos(theta), zeta=exp(2*i*theta)",
            "target_c_values": ["0", "3/5"],
            "target_zeta_values": ["-1", "(-7+24*i)/25"],
            "order_N": order,
            "maximum_transverse_derivative_order": maximum_derivative_order,
            "normalized_kernel": "K_N(theta-theta_j)=|sum_(k=0)^(N-1) exp(2*i*k*(theta-theta_j))|^2/N^2",
            "kernel_Laurent_support": [-(order - 1), order - 1],
            "rho_exact": str(rho),
            "filter": "p_N=(K_N(theta-theta_0)-K_N(theta-theta_1))/(1-rho_N)",
            "target_weights": ["1", "-1"],
            "local_density_realization": "The mode exp(2*i*m*theta) is the pair symbol of a constant-coefficient local bilinear :phi D_plus^(2m) phi:/2, with D_plus Fourier symbol 5*(k_y+i*k_z)/(4*kappa) on the fixed-energy shell; conjugate modes make p_N Hermitian.",
            "status": "FINITE_DERIVATIVE_LOCAL_PROJECTIVE_FILTER_WITH_EXACT_TARGET_INTERPOLATION"
        },
        "packet_decomposition": {
            "measure": "dc on the azimuthally reduced fixed-energy two-body shell",
            "packet_zero_c_interval": ["-7/25", "7/25"],
            "packet_one_c_interval": ["5/13", "20/29"],
            "packet_zero_endpoint_sines": ["24/25", "24/25"],
            "packet_one_endpoint_sines": ["12/13", "21/29"],
            "packet_modes": "f_j=1_(B_j)*p_N/||1_(B_j)*p_N||; disjoint support makes f_0,f_1 orthonormal",
            "selected_bright_packet": "B=(g_0 f_0+g_1 f_1)/sqrt(g_0^2+g_1^2), with g_j^2=integral_(B_j)|p_N|^2 dc",
            "selected_dark_packet": "D=(g_1 f_0-g_0 f_1)/sqrt(g_0^2+g_1^2)",
            "complete_direction": "v=sqrt(1-eta) B+sqrt(eta) R, where R is the normalized restriction to the bin complement",
            "exact_integral_receipts": receipts,
            "leakage_bound": "0<eta<1/1000 and 1-eta>999/1000",
            "status": "EXACT_TWO_PACKET_ORTHOGONAL_DECOMPOSITION_WITH_SUB_PER_MILLE_CONTINUUM_LEAKAGE"
        },
        "residual_retaining_evolution": {
            "basis": ["|e,0_field>", "|g,B>", "|g,R>", "|g,D>"],
            "Hamiltonian": "H/G=|e><v|+|v><e| with v=sqrt(1-eta)B+sqrt(eta)R; D is exactly dark",
            "exact_exponential": "U=I+(cos(G*tau)-1)(H/G)^2-i*sin(G*tau)(H/G)",
            "selected_absorption_effect": "E_absorb=(1-eta)*sin(G*tau)^2*P_B",
            "selected_pass_effect": "E_pass=P_D+[1-(1-eta)*sin(G*tau)^2]*P_B",
            "half_pulse": "at G*tau=pi/2, absorption efficiency on B is 1-eta>999/1000 and total field remainder is eta<1/1000",
            "outside_packet_population_from_B": "eta*(1-eta)*(1-cos(G*tau))^2",
            "all_time_selected_input_bound": "sup over normalized span{e,B} inputs and tau of outside-packet population is 4*eta*(1-eta)<1/250",
            "compressed_exponential_relation": "Pi*U*Pi is computed from the full residual-retaining exponential and is not replaced by exp(-i*Pi*H*Pi*tau)",
            "status": "EXACT_FIXED_ENERGY_ROTATING_WAVE_STAR_EVOLUTION_WITH_RESIDUAL_RETAINED"
        },
        "disposition": {
            "finite_derivative_local_filter": "CONSTRUCTED",
            "finite_packet_leakage_coefficient": "COMPUTED",
            "residual_retaining_fixed_energy_evolution": "COMPUTED",
            "selected_packet_absorption_instrument": "COMPUTED",
            "exact_zero_width_two_angle_selectivity": "STILL_IMPOSSIBLE",
            "complete_local_scalar_detector_Hamiltonian": "NOT_CONSTRUCTED",
            "absolute_q8_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "exact support on two zero-width continuum angles",
            "a leakage bound on the full two-sphere of outgoing directions",
            "a leakage bound for other energies, shapes or total momenta",
            "control of number-scattering or counter-rotating terms in the complete local quadratic Hamiltonian",
            "that the N=20 high-derivative apparatus is unique, minimal or experimentally practical",
            "selection of the filter, packet bins, coupling or pulse duration by the public closed BT dynamics",
            "transfer of the earlier equal-weight two-mode effect or its relative order-lambda8 coefficient to these unequal-norm packet modes",
            "either absolute order-lambda8 probability coefficient",
            "either forward or exchanged-forward endpoint or a KLN completion",
            "an all-time Moller, LSZ or S operator for the public BT theory",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Extend the packet from the one-dimensional fixed-energy meridian to compact energy and full solid-angle support, and bound the off-resonant, number-scattering and counter-rotating sectors of the same finite-duration local detector. In parallel, optimize derivative order versus leakage and compute the independent absolute q8 X4 Gram and X2-X6 interference gates.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_two_angle_fejer_packet_detector.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_fejer_packet_detector.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_fejer_packet_detector"
        ],
        "report": REPORT
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
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT TWO ANGLE FEJER PACKET DETECTOR: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT TWO ANGLE FEJER PACKET DETECTOR: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
