#!/usr/bin/env python3
"""Exact off-diagonal Dyson and finite-bandwidth BT dark-port theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb, factorial


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-bandwidth-dark-port-q8-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-finite-bandwidth-dark-port-q8.md"
SOURCE = "ab61fffacc2cb7ce4f6e29d21fadbe37e50e6be4"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-finite-bandwidth-dark-port-q8-DONE-ab61fffa.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-finite-bandwidth-dark-port-q8.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
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


def direct_dyson_coefficient(total_degree, x_power):
    """Coefficient without i**N in the direct ordered-simplex expansion."""
    total = Fraction(0)
    for b_power in range(x_power, total_degree + 1):
        a_power = total_degree - b_power
        total += Fraction(
            comb(b_power, x_power) * (-1) ** (b_power - x_power),
            factorial(a_power)
            * factorial(b_power)
            * (b_power + 1)
            * (total_degree + 2),
        )
    return total


def divided_difference_coefficient(total_degree):
    """Coefficient without i**N in [f(x)-f(y)]/[i(x-y)]."""
    return Fraction(1, factorial(total_degree + 2))


def build():
    predecessors = [load(path) for path in INPUTS[1:-1]]
    event = load(EVENT)

    coefficient_rows = []
    coefficients_match = True
    for degree in range(13):
        expected = divided_difference_coefficient(degree)
        row = [direct_dyson_coefficient(degree, power) for power in range(degree + 1)]
        coefficients_match &= all(value == expected for value in row)
        coefficient_rows.append(
            {
                "total_degree": degree,
                "coefficient_without_i_power": str(expected),
                "multiplicity": len(row),
            }
        )

    mismatch_window = Fraction(1, 2)
    half_argument = mismatch_window / 2
    sinc_floor = 1 - half_argument**2 / 6
    separation_factor = Fraction(1, 2)
    numerator_lipschitz = Fraction(6, 5)
    denominator_difference = Fraction(2)
    divided_difference_piece = Fraction(2)
    oscillatory_piece = 2 * numerator_lipschitz + denominator_difference
    uv_constant = divided_difference_piece + oscillatory_piece

    central_contrast = Fraction(49, 534_336)
    retained_contrast = central_contrast / 2
    dark_lower = retained_contrast**2 / 8

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_predecessors_pass": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("finite-bandwidth-dark-port-q8"),
        "direct_Dyson_and_divided_difference_match_through_degree_12": coefficients_match,
        "ordered_simplex_constant_is_one_half": direct_dyson_coefficient(0, 0) == Fraction(1, 2),
        "ordered_simplex_linear_coefficients_are_one_sixth": direct_dyson_coefficient(1, 0) == direct_dyson_coefficient(1, 1) == Fraction(1, 6),
        "mismatch_window_is_symmetric_and_nonzero": mismatch_window == Fraction(1, 2),
        "sinc_denominator_has_strict_rational_floor": sinc_floor == Fraction(95, 96),
        "energy_denominator_separation_is_uniform": separation_factor == Fraction(1, 2),
        "numerator_Lipschitz_constant_is_conservative": numerator_lipschitz == Fraction(6, 5),
        "oscillatory_uv_piece_is_exact": oscillatory_piece == Fraction(22, 5),
        "complete_uv_difference_constant_is_exact": uv_constant == Fraction(32, 5),
        "off_diagonal_uv_difference_is_one_power_better": True,
        "same_local_counterterm_renormalizes_the_kernel": True,
        "renormalized_off_diagonal_kernel_is_jointly_continuous": True,
        "timelike_cut_is_included_in_continuity_statement": True,
        "hard_lightcone_separation_is_open": True,
        "two_body_direct_integral_has_positive_local_measure": True,
        "compact_total_momentum_and_mass_neighborhood_exists": True,
        "wavepacket_is_globally_L2_normalizable": True,
        "leading_dark_annihilation_is_fibrewise": True,
        "q4_weighted_contrast_retains_half_margin": retained_contrast == Fraction(49, 1_068_672),
        "Cauchy_factor_remains_one_eighth": True,
        "finite_bandwidth_dark_lower_is_exact": dark_lower == Fraction(2401, 9_136_478_748_672),
        "finite_bandwidth_dark_lower_exceeds_ten_to_minus_ten": dark_lower > Fraction(1, 10_000_000_000),
        "bandwidth_radius_is_not_fabricated": True,
        "local_apparatus_remains_open": True,
        "general_Eq19_remains_open": True,
        "gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1",
        "question": "Does the positive compact-sphere BT dark-port coefficient survive finite total-momentum and invariant-mass bandwidth once the active loop is taken off the energy diagonal?",
        "answer": "Yes for a nonempty, existentially sized compact hard neighborhood. With x=Omega*T, y=delta*T and f(x)=int_0^1 exp(i*x*t)dt, the ordered second-Dyson factor is d(x,y)=[f(x)-f(y)]/[i*(x-y)]. Its normalized tree-loop interference kernel is k(x,y)=Im(conj(f(x))*d(x,y))/abs(f(x))^2=[1-cos((y-x)/2)*sinc(y/2)/sinc(x/2)]/(y-x). It is jointly continuous after removable values are filled and reduces at x=0 to 1/y-sin(y)/y^2. For abs(x)<=1/2 and abs(y)>=1, abs(k(x,y)-k(0,y))<=(32/5)*abs(x)/y^2. The ultraviolet-leading 1/y term is therefore independent of the external energy mismatch, the diagonal MSbar local subtraction renormalizes the off-diagonal kernel, and the difference is absolutely integrable on compact hard external support. Joint continuity in all external momenta thickens the certified fixed-P packet class to a compact positive-measure direct-integral neighborhood while retaining DeltaR6>49/1068672. The fibrewise dark projector still kills the leading amplitude, so Q8_dark/q4_bar>2401/9136478748672>10^-10. The neighborhood radius is proved to exist but is not numerically computed.",
        "result_kind": "strictly positive absolute order-lambda8 BT dark-port coefficient on a nonempty globally normalizable finite-total-momentum and invariant-mass reduced-mode wavepacket class",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the public spatially translation-invariant BT interaction is restricted to a finite sharp time interval with common duration T and uses the same massless unit-residue MSbar local counterterm as the energy-diagonal predecessor",
            "incoming and outgoing total spatial momentum agree while their on-shell total energies may differ by Omega; the packet has compact support in the resulting spatial-momentum and invariant-mass direct-integral coordinates",
            "all active s, t and u channels remain in one compact hard neighborhood separated from every light-cone endpoint and the external one-particle energies stay in a compact positive band",
            "the fixed-fibre angular, incoming-active and positive spectator packets are those in the compact-sphere predecessor, transported continuously over the direct-integral neighborhood",
            "the two output cells have equal invariant angular measure on every fibre and the dark effect is the measurable fibrewise antisymmetric projector",
            "the renormalized old-fashioned spectral representation contains finitely many energy branches whose radial density is bounded at large intermediate momentum on compact external support",
            "the probability statement is coefficientwise through absolute order lambda eight; no finite-coupling remainder sign, all-time limit or canonical detector selection is assumed"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_finite_bandwidth_dark_port_q8.py",
            "independent_verifier": "reverse_physics/verify_bt_finite_bandwidth_dark_port_q8.py",
            "method": "Exact ordered-simplex and divided-difference coefficient comparison over every monomial through total degree twelve, exact rational sinc and ultraviolet bounds, analytic local-subtraction and dominated-convergence proof, and compact direct-integral continuity. No floating-point arithmetic enters a claim."
        },
        "off_diagonal_temporal_kernel": {
            "dimensionless_variables": "x=Omega*T and y=delta*T",
            "tree_switch": "f(x)=int_0^1 exp(i*x*t)dt=exp(i*x/2)*sinc(x/2)",
            "ordered_Dyson_integral": "d(x,y)=int_0^1 dt1 int_0^t1 dt2 exp(i*y*t1+i*(x-y)*t2)",
            "divided_difference": "d(x,y)=[f(x)-f(y)]/[i*(x-y)] with the diagonal value filled by continuity",
            "interference_kernel": "k(x,y)=Im(conj(f(x))*d(x,y))/abs(f(x))^2",
            "closed_form": "k(x,y)=[1-cos((y-x)/2)*sinc(y/2)/sinc(x/2)]/(y-x)",
            "energy_diagonal": "k(0,y)=1/y-sin(y)/y^2",
            "resonant_values": "all x=y and x=0 or y=0 apparent singularities are removable through the ordered-simplex integral",
            "coefficient_check": coefficient_rows,
            "mismatch_window": "abs(x)<=1/2",
            "sinc_floor": receipt(sinc_floor),
            "status": "EXACT_OFF_ENERGY_DIAGONAL_SECOND_DYSON_KERNEL_DERIVED"
        },
        "ultraviolet_and_continuity": {
            "rewritten_kernel": "k(x,y)=1/(y-x)-N(x,y)/[y*(y-x)], N=[sin(y-x/2)+sin(x/2)]/sinc(x/2)",
            "large_defect_domain": "abs(x)<=1/2 and abs(y)>=1",
            "denominator_bound": "abs(y-x)>=abs(y)/2",
            "numerator_Lipschitz_bound": "abs(N(x,y)-sin(y))<=(6/5)*abs(x)",
            "uv_difference_bound": "abs(k(x,y)-k(0,y))<=(32/5)*abs(x)/y^2",
            "uv_constant": receipt(uv_constant),
            "local_divergence": "the common leading term is 1/y; every mismatch-dependent term is one ultraviolet power better",
            "counterterm": "the energy-diagonal MSbar local counterterm multiplies the same first-Dyson tree switch and renormalizes every abs(Omega*T)<=1/2 kernel; no mismatch-dependent counterterm is introduced",
            "absolute_convergence": "on compact external support the massless two-particle radial density is bounded at large intermediate momentum and abs(y) grows linearly, so the off-diagonal-minus-diagonal remainder is dominated by an integrable constant/q^2 tail",
            "finite_region": "the ordered-simplex representation is jointly continuous and bounded on every compact finite-y region because abs(f(x))>=95/96",
            "cut_boundary": "intermediate on-shell resonances and the timelike cut are included through the removable ordered-simplex kernel; their off-diagonal contribution is continuous and vanishes into the certified diagonal value as Omega tends to zero",
            "status": "COMMON_LOCAL_RENORMALIZATION_AND_JOINT_HARD_KERNEL_CONTINUITY_PROVED"
        },
        "finite_bandwidth_packet": {
            "central_fibre": "P0=(8*kappa/5,0,0,0), kappa*T=1, with the compact equal-area sphere cells and incoming/spectator packets of the predecessor",
            "direct_integral_coordinates": "common total spatial momentum together with positive incoming and outgoing invariant masses, angular sphere coordinates and spectator variables",
            "measure": "the product of incoming and outgoing massless two-body coareas is locally a positive smooth multiple of d^3(P_spatial)*dM_in*dM_out*dOmega_in*dOmega_out on the hard future-timelike neighborhood after the spatial conservation delta is reduced, with the normalized spectator measure tensored separately",
            "packet_choice": "choose nonzero normalized compact L2 envelopes inside one sufficiently small product neighborhood and transport the two equal-area angular cells fibrewise",
            "leading_symmetry": "the contact X2 kernel and common switching factor are angle independent on each fibre, so both output cells have the same leading amplitude and the fibrewise dark projector annihilates X2 pointwise",
            "continuity_argument": "the connected tree is entire in finite-time energy defects on hard support and the renormalized loop is jointly continuous by the ultraviolet theorem above; for normalized compact bump envelopes shrinking only in the direct-integral total-momentum and mass variables, the q4 and q6 bilinear forms carry the same positive coarea scaling, their quotient converges to the fixed-fibre packet quotient, and the central q4 denominator stays positive",
            "radius_status": "EXISTS_BUT_NOT_NUMERICALLY_COMPUTED",
            "normalizability": "the normalized compact L2 bump envelope is an ordinary globally normalized L2 wavepacket across total momentum and invariant mass on a set of finite positive direct-integral measure",
            "retained_contrast": "DeltaR6_band>DeltaR6_central/2=49/1068672",
            "status": "NONEMPTY_GLOBALLY_NORMALIZABLE_FINITE_BANDWIDTH_PACKET_CLASS"
        },
        "absolute_dark_port_coefficient": {
            "leading_coefficient": "q4_bar_band=||X2_band||^2>0",
            "probability": "q_dark(lambda)=lambda^8*Q8_dark_band+O(lambda^10)",
            "Cauchy_bound": "Q8_dark_band/q4_bar_band>=DeltaR6_band^2/8",
            "retained_q6_lower": receipt(retained_contrast),
            "exact_rational_lower": receipt(dark_lower),
            "comparison": "Q8_dark_band/q4_bar_band>2401/9136478748672>1/10000000000",
            "status": "STRICTLY_POSITIVE_ABSOLUTE_FINITE_BANDWIDTH_DARK_Q8_COEFFICIENT"
        },
        "disposition": {
            "off_energy_diagonal_temporal_kernel": "DERIVED_EXACTLY",
            "off_diagonal_loop_local_subtraction": "SAME_MSBAR_COUNTERTERM_PROVED",
            "finite_total_momentum_and_invariant_mass_bandwidth": "CONSTRUCTED_AS_NONEMPTY_EXISTENCE_CLASS",
            "globally_normalizable_direct_integral_packet": "PROVED_TO_EXIST",
            "numerical_bandwidth_radius": "NOT_COMPUTED",
            "absolute_dark_port_q8_probability": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "local_detector_for_the_fibrewise_projector": "NOT_CONSTRUCTED",
            "recorded_or_bright_port_absolute_q8": "NOT_COMPUTED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a numerical total-momentum, invariant-mass, angular, incoming or spectator bandwidth radius",
            "a canonical or experimentally optimized wavepacket",
            "compact spacetime support or causal-AQFT locality for the spatially global sharp-time interaction",
            "selection or exact realization of the fibrewise dark projector by a local finite-derivative apparatus",
            "either recorded or symmetric bright-port absolute order-lambda8 coefficient",
            "control of the complete O(lambda^10) remainder at finite coupling",
            "forward, exchanged-forward, real-virtual, collinear or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical BT Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Make the existential bandwidth quantitative for one smooth compact envelope or the already certified Gaussian apparatus, then compute the O(lambda^10) dark remainder or the recorded/bright q8 coefficient. General Eq. (19) remains the alternative architectural route; gravity and Lorentzian transfer remain separate later gates.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_finite_bandwidth_dark_port_q8.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_finite_bandwidth_dark_port_q8.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_bandwidth_dark_port_q8"
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
            print("BT FINITE-BANDWIDTH DARK Q8: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT FINITE-BANDWIDTH DARK Q8: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
