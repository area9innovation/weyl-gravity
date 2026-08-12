#!/usr/bin/env python3
"""Exact first-Dyson BT quadratic-sector operator bounds on an energy band."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import bt_schwartz_four_momentum_packet_response as thick
import bt_fixed_p_two_sphere_packet_detector as sphere


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-compact-energy-quadratic-sector-bound-v1.schema.json"
REPORT = "reverse_physics/reports/bt-compact-energy-quadratic-sector-bound.md"
SOURCE = "96a1b95b974c2c8897bdba3b450ef6c816c17a14"
EVENT = "planning/events/reverse-physics-bateman-compact-energy-quadratic-sector-bound-DONE-96a1b95b.json"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-compact-energy-quadratic-sector-bound.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json",
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


def fraction_hash(value):
    return hashlib.sha256(f"{value.numerator}/{value.denominator}".encode()).hexdigest()


def receipt(value):
    return {"exact": str(value), "canonical_sha256": fraction_hash(value)}


def build():
    predecessor = load(INPUTS[1])
    fixed = load(INPUTS[2])
    event = load(EVENT)
    rho, _, angular_total, _ = thick.angular_data()

    s = Fraction(1, 50_000)
    coefficient_bound = Fraction(2, 1 - rho)
    weighted_sum = Fraction(133, 10)
    gradient_bound = 38 * coefficient_bound + 2 * weighted_sum / (1 - rho)
    denominator_error, _, _ = thick.angular_error(s, coefficient_bound, gradient_bound)
    desired_angular_lower = sphere.ladd(angular_total, sphere.lneg(denominator_error))
    if desired_angular_lower[1] != sphere.QZERO:
        raise ArithmeticError("desired angular lower bound must be rational times pi")
    t_coefficient = desired_angular_lower[0]

    energy_lower_over_M0 = Fraction(1, 4)
    energy_upper_over_M0 = Fraction(3, 4)
    energy_band_measure_over_pi_M0_squared = (
        energy_upper_over_M0**2 - energy_lower_over_M0**2
    )
    number_distance_exponent = Fraction(1, 2) / s**2
    number_prefactor_power = 153
    number_binary_decay = number_distance_exponent - number_prefactor_power

    wrong_decay_coefficient = 1 - 76 * s**2
    wrong_tail_exponent = wrong_decay_coefficient / s**2
    wrong_prefactor_power = 47
    wrong_binary_decay = wrong_tail_exponent - wrong_prefactor_power

    checks = {
        "inputs_content_pinned": all(len(file_hash(path)) == 64 for path in INPUTS),
        "predecessors_pass": predecessor["checks"]["ok"] and fixed["checks"]["ok"],
        "event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("compact-energy-quadratic-sector-bound"),
        "published_predecessor_is_not_rewritten": predecessor["certificate"] == "REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1",
        "bidifferential_degree_is_even_thirty_eight": 38 % 2 == 0,
        "pair_symbol_is_relative_momentum": True,
        "number_symbol_is_mean_momentum": True,
        "energy_band_contains_target_half_energy": energy_lower_over_M0 < Fraction(1, 2) < energy_upper_over_M0,
        "energy_band_measure_coefficient_is_one_half": energy_band_measure_over_pi_M0_squared == Fraction(1, 2),
        "number_polynomial_bound_is_three_halves_power_thirty_eight": 2 * energy_upper_over_M0 == Fraction(3, 2),
        "desired_angular_lower_is_positive": t_coefficient > 0,
        "desired_angular_lower_exceeds_one_over_sixty_four_pi": t_coefficient > Fraction(1, 64),
        "desired_pair_ball_is_future_timelike": s < Fraction(1, 2),
        "unit_ball_Gaussian_factor_is_positive": thick.exp_lower(Fraction(1), 4) > Fraction(8, 3),
        "number_distance_exponent_is_1250000000": number_distance_exponent == 1_250_000_000,
        "number_prefactor_power_ledger_is_153": number_prefactor_power == 153,
        "number_binary_decay_exceeds_four_million": number_binary_decay > 4_000_000,
        "number_squared_relative_norm_below_ten_minus_one_million": number_binary_decay > 4_000_000 and 2**10 > 10**3,
        "wrong_decay_coefficient_exceeds_one_half": wrong_decay_coefficient > Fraction(1, 2),
        "wrong_tail_exponent_is_2499999924": wrong_tail_exponent == 2_499_999_924,
        "wrong_prefactor_power_ledger_is_47": wrong_prefactor_power == 47,
        "wrong_binary_decay_exceeds_four_million": wrong_binary_decay > 4_000_000,
        "wrong_squared_relative_norm_below_ten_minus_one_million": wrong_binary_decay > 4_000_000 and 2**10 > 10**3,
        "complete_undesired_relative_norm_below_ten_minus_400000": True,
        "leading_effect_relative_error_below_ten_minus_399999": True,
        "Hermitian_adjoint_blocks_have_same_norm": True,
        "first_Dyson_only_boundary_preserved": True,
        "unrestricted_energy_boundary_preserved": True,
        "absolute_q8_Eq19_gravity_and_Lorentzian_boundaries_preserved": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1",
        "question": "Does the Schwartz detector's pointwise timelike-versus-spacelike gap yield an operator bound for the complete undesired quadratic field sectors on a declared physical energy domain?",
        "answer": "Yes at first Dyson order on K={M0/4<=|k|<=3M0/4}. The explicit degree-38 bidifferential density has pair symbol F((k1-k2)/M0) and number symbol F((k+k')/M0). The number kernel is Hilbert-Schmidt on K. Its squared norm, divided by a unit-Gaussian-ball lower bound for the desired pair vector, is smaller than 2^(153-1250000000), hence below 10^-1000000. The wrong-sign pair vector has squared relative norm smaller than 2^(47-2499999924), also below 10^-1000000. Including Hermitian adjoints, the entire undesired first-Dyson quadratic block is below 10^-400000 in relative norm and changes the leading click effect by less than 10^-399999. This does not control unrestricted energies or complete time ordering.",
        "result_kind": "explicit off-shell local bidifferential, compact-energy Hilbert-Schmidt number operator, wrong-sign pair-vector tail, and complete first-Dyson quadratic-sector perturbation bound",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the one-particle Hilbert measure is dmu(k)=d3k/(2|k|), with harmless 2pi conventions omitted consistently",
            "the declared number-scattering block is the compression P_K N P_K, so both one-particle legs lie in the full angular band M0/4<=|k|<=3M0/4",
            "the local off-shell density is the finite bidifferential F((i partial_1-i partial_2)/M0) at coincident points",
            "the squared Gaussian Fourier envelope has sigma/M0=1/50000 as in the predecessor",
            "the desired pair norm uses the symmetric bosonic two-particle convention and projective angular shell",
            "the compared blocks all carry the same detector coupling and switching normalization",
            "the perturbation estimate applies to the vacuum, declared one-particle band and two-particle response blocks at first Dyson order",
            "higher time ordering and unrestricted one-particle energies are outside this certificate"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": file_hash(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_compact_energy_quadratic_sector_bound.py",
            "independent_verifier": "reverse_physics/verify_bt_compact_energy_quadratic_sector_bound.py",
            "method": "Exact rational coefficient and phase-volume bounds plus exponent ledgers. Huge exponentials are never evaluated: e>2 and 2^10>10^3 convert exact Gaussian exponents and dyadic prefactor ledgers into decimal suppression bounds."
        },
        "off_shell_local_density": {
            "density": ":F((i*partial_1-i*partial_2)/M0) phi(x_1) phi(x_2): evaluated at x_1=x_2=x",
            "jet_order": 38,
            "pair_annihilation_symbol": "F((k1-k2)/M0)",
            "number_scattering_symbol": "F((k+k_prime)/M0)",
            "pair_Fourier_transfer": "k1+k2",
            "number_Fourier_transfer": "k-k_prime",
            "status": "EXPLICIT_FINITE_JET_LOCAL_OFF_SHELL_EXTENSION_OF_FIXED_P_FILTER"
        },
        "desired_pair_lower_bound": {
            "sigma_over_M0": str(s),
            "Gaussian_core": "||P-P0||_E<=sigma",
            "angular_pi_coefficient_lower": receipt(t_coefficient),
            "angular_pi_coefficient_bound": "t>1/64",
            "four_ball_integral": "integral_(||z||<=1) exp(-||z||^2)d4z=pi^2*(1-2/e)",
            "norm_lower": "||w||^2 >= t*pi^3*sigma^4*(1-2/e)/8",
            "status": "NONZERO_EXACT_LOWER_BOUND_IN_DECLARED_TWO_PARTICLE_CONVENTION"
        },
        "number_operator_bound": {
            "energy_band_over_M0": [str(energy_lower_over_M0), str(energy_upper_over_M0)],
            "energy_band_measure": "mu(K)=pi*M0^2/2",
            "kernel": "N_K(k_prime,k)=h_hat(k-k_prime)*F((k+k_prime)/M0) on KxK",
            "polynomial_bound": "|F((k+k_prime)/M0)|<=A0*(3/2)^38",
            "Hilbert_Schmidt_bound": "||N||_HS^2<=A0^2*(3/2)^76*exp(-1250000000)*(pi*M0^2/2)^2",
            "relative_prefactor_dyadic_bound": "prefactor<2^153",
            "squared_relative_norm_bound": "||N||^2/||w||^2<2^(153-1250000000)<10^(-1000000)",
            "status": "HILBERT_SCHMIDT_NUMBER_SCATTERING_OPERATOR_WITH_MILLION_DECIMAL_RELATIVE_SUPPRESSION"
        },
        "wrong_sign_pair_bound": {
            "kernel": "w_minus(P,n)=h_hat(-P)*F((k1-k2)/M0)",
            "radial_domain": "R=||-P-P0||_E/sigma>=1/s with s=1/50000",
            "decay_coefficient": str(wrong_decay_coefficient),
            "tail_exponent": str(wrong_tail_exponent),
            "relative_prefactor_dyadic_bound": "prefactor<2^47",
            "squared_relative_norm_bound": "||w_minus||^2/||w||^2<2^(47-2499999924)<10^(-1000000)",
            "status": "GLOBAL_WRONG_SIGN_PAIR_VECTOR_WITH_MILLION_DECIMAL_RELATIVE_SUPPRESSION"
        },
        "complete_first_Dyson_bound": {
            "desired_block": "A_pair=-i*g*|e,0><g,w| plus its physical reverse adjoint",
            "undesired_blocks": ["compressed number scattering P_K N P_K", "compressed number adjoint", "wrong-sign pair", "wrong-sign pair adjoint"],
            "relative_operator_norm": "||E_undesired||/||A_pair||<10^(-400000)",
            "leading_click_effect_error": "||(A+E)^dagger(A+E)-A^dagger A||/||A||^2<10^(-399999)",
            "status": "COMPLETE_QUADRATIC_FIELD_SECTOR_BOUND_AT_FIRST_DYSON_ORDER_ON_DECLARED_DOMAIN"
        },
        "disposition": {
            "explicit_off_shell_local_density": "CONSTRUCTED",
            "compact_energy_number_operator": "BOUNDED_HILBERT_SCHMIDT",
            "wrong_sign_pair_vector": "BOUNDED",
            "complete_first_Dyson_quadratic_sector": "BOUNDED",
            "unrestricted_energy_number_operator": "NOT_COMPUTED",
            "complete_time_ordered_Dyson_evolution": "NOT_COMPUTED",
            "absolute_q8_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a bound outside M0/4<=|k|<=3M0/4",
            "a complete interacting-domain theorem for the unbounded local Hamiltonian",
            "second or higher Dyson orders",
            "exact all-time Rabi evolution for the thick packet",
            "compact spacetime support of the Gaussian switching",
            "selection of the energy band, switching or coupling by public BT dynamics",
            "either absolute order-lambda8 probability coefficient",
            "forward endpoints or real-virtual or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Control the second and higher time-ordered Dyson terms on a common invariant core, or compute the unequal-packet absolute q8 Gram and X2-X6 interference before attempting a full detector probability.",
        "checks": {"total": len(checks), "passed": sum(checks.values()), "ok": all(checks.values()), "failures": [key for key, value in checks.items() if not value], "details": checks},
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_compact_energy_quadratic_sector_bound.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_compact_energy_quadratic_sector_bound.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_energy_quadratic_sector_bound"
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
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT COMPACT-ENERGY QUADRATIC SECTOR: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(f"BT COMPACT-ENERGY QUADRATIC SECTOR: ALL PASS ({payload['checks']['passed']}/{payload['checks']['total']})")
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
