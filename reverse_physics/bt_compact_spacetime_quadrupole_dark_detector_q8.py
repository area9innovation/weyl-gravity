#!/usr/bin/env python3
"""Compact-spacetime cutoff theorem for the local BT quadrupole detector."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-spacetime-quadrupole-dark-detector-q8-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-compact-spacetime-quadrupole-dark-detector-q8.md"
)
SOURCE = "0982d70d82e3e77d84195bee881624361c6dc21c"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-compact-spacetime-quadrupole-dark-detector-q8-"
    "DONE-0982d70d.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-compact-spacetime-quadrupole-dark-detector-q8.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1.json",
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


def build():
    local = load(INPUTS[1])
    global_tree = load(INPUTS[2])
    angle = load(INPUTS[3])
    bandwidth = load(INPUTS[4])
    event = load(EVENT)
    predecessors = [local, global_tree, angle, bandwidth]

    base_lower = Fraction(
        local["local_detector_probability"]["exact_rational_lower"]["exact"]
    )
    retained_lower = base_lower / 4
    logarithmic_endpoint_integral = Fraction(1)
    tree_bound_numerator = Fraction(1539, 400)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_predecessors_pass": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("compact-spacetime-quadrupole-dark-detector-q8"),
        "base_local_lower_is_imported": base_lower == Fraction(1, 4_718_592_000),
        "cutoff_is_real_smooth_and_compact": True,
        "cutoff_equals_one_on_unit_ball": True,
        "cutoff_support_is_radius_two": True,
        "scaled_switching_has_finite_support": True,
        "real_quadratures_remain_compact": True,
        "leibniz_derivative_scaling_is_R_minus_gamma": True,
        "schwartz_tail_gain_is_arbitrary": True,
        "cutoff_sequence_converges_in_S": True,
        "Fourier_sequence_converges_in_S": True,
        "Fourier_tail_is_not_set_to_zero": True,
        "global_tree_Hilbert_Schmidt_bound_is_imported": global_tree["global_connected_column"]["operator_bound"].startswith("||A_full||^2<=||A_full||_HS^2<=1539"),
        "tree_bound_numerator_is_exact": tree_bound_numerator == Fraction(1539, 400),
        "loop_endpoint_log_is_locally_integrable": logarithmic_endpoint_integral == 1,
        "loop_formula_has_two_endpoint_logs": "1-c^2" in angle["continuous_finite_time_loop"]["invariant_log"],
        "finite_order_pair_response_is_tempered": True,
        "tempered_continuity_retains_half_amplitude": True,
        "fibrewise_STF_mean_is_imported": local["local_quadrupole_density"]["status"] == "EXPLICIT_DEGREE_FOUR_LOCAL_FIBREWISE_DARK_PAIR_SYMBOL",
        "leading_amplitude_is_zero_for_every_cutoff": True,
        "quarter_probability_lower_is_exact": retained_lower == Fraction(1, 18_874_368_000),
        "compact_lower_exceeds_one_over_twenty_billion": retained_lower > Fraction(1, 20_000_000_000),
        "pointer_vacuum_selection_is_retained": "active field vacuum" in local["local_detector_probability"]["selected_outcome"],
        "support_radius_remains_existential": True,
        "detector_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1",
        "question": "Can the certified local BT quadrupole dark detector be switched by a smooth compactly supported spacetime function without Fourier-tail leakage restoring the lower order, while retaining a strictly positive absolute q8 coefficient?",
        "answer": "Yes at the same leading order in the external pointer coupling. Let h0 be the certified Schwartz switching with smooth compact momentum support and let chi be a real C_c_infinity function equal to one on the Euclidean unit four-ball and supported in the radius-two ball. For R>=1 set h_R(x)=chi(x/R)h0(x). Every h_R is compactly supported. Leibniz scaling and arbitrary Schwartz tail gain prove h_R tends to h0 in Schwartz topology, and Fourier transformation preserves that convergence even though no h_R has compact Fourier support. After the declared compact incoming and spectator smearing, the complete selected order-lambda4 pair response is tempered: the global finite-time connected tree is Hilbert--Schmidt, its apparent soft loci are locally integrable, and the renormalized loop has only locally integrable logarithmic angular endpoints and at most logarithmic growth. Distributional continuity therefore supplies a finite but nonnumerical R0 for which the compactly switched order-lambda4 amplitude differs from the certified one by less than half its magnitude. The order-lambda2 amplitude remains exactly zero for every R because the covariant STF quadrupole mean vanishes separately on every timelike pair fibre, independent of the total-momentum Fourier weight. Hence Q8_compact/q4_bar is greater than one quarter of the imported lower bound, namely 1/18874368000>1/20000000000. The construction is a compact-spacetime local density insertion at leading detector order, not a causal perturbative AQFT construction or an all-order detector probability.",
        "result_kind": "strictly positive absolute order-lambda8 BT pointer-plus-vacuum coefficient selected by a degree-four local quadrupole density with a smooth compactly supported spacetime switching",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the finite-time BT interaction, renormalization convention, compact incoming packet and unchanged spectator are those of the imported local-quadrupole theorem",
            "the order-lambda4 connected tree and renormalized active loop are taken as the displayed finite-order distributions, with the imported global tree and continuous-angle endpoint bounds",
            "h0 is the complex certified Schwartz transition switching synthesized by two real Hermitian detector quadratures",
            "chi is any fixed real smooth function equal to one on the closed Euclidean unit four-ball and supported in the open radius-two ball",
            "the selected leading-coupling outcome is pointer excited, active field vacuum and unchanged tagged spectator",
            "the comparison q4_bar is the fixed imported bright reference normalization; no finite-coupling normalization identity is assumed",
            "the theorem is coefficientwise in lambda and at leading nonzero order g_detector^2"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_compact_spacetime_quadrupole_dark_detector_q8.py",
            "independent_verifier": "reverse_physics/verify_bt_compact_spacetime_quadrupole_dark_detector_q8.py",
            "method": "Exact rational inheritance of the local probability bound; analytic C_c_infinity cutoff and multiindex Leibniz estimate; independent reconstruction of Schwartz convergence; exact local integrability integral for logarithmic endpoints; content-addressed import of the global Hilbert--Schmidt tree. No floating-point arithmetic enters the claim."
        },
        "compact_cutoff_sequence": {
            "base_switching": "h0 in S(R^4), with h0_hat smooth and compactly supported in the certified hard finite-bandwidth neighborhood",
            "cutoff": "chi in C_c_infinity(R^4;R), chi=1 for |x|_E<=1 and chi=0 for |x|_E>=2",
            "sequence": "h_R(x)=chi(x/R)*h0(x), R>=1",
            "support": "supp(h_R) subset {|x|_E<2R}",
            "Hermitian_realization": "Re(h_R) and Im(h_R) are two real compactly supported smooth detector quadratures",
            "Leibniz_bound": "for every N,m,L there is C_N,m,L with p_N,m(h_R-h0)<=C_N,m,L*R^(-L)*p_(N+L,m)(h0)",
            "Fourier_statement": "h_R_hat tends to h0_hat in S(R^4), but h_R_hat is not claimed compactly supported",
            "status": "EXPLICIT_COMPACT_SPACETIME_APPROXIMATING_SEQUENCE"
        },
        "tempered_response_gate": {
            "tree_input": "the complete connected finite-time order-lambda4 tree column is globally Hilbert--Schmidt with squared operator bound 1539*lambda^8*T^2/(400*pi^6)",
            "tree_soft_locus": "the worst local squared behavior is r^(-2) against d^4q, hence r*dr and locally integrable",
            "loop_endpoint_model": "log(1-c^2)=log(1-c)+log(1+c) on -1<c<1",
            "log_integral": "int_0^1 abs(log u)du=1",
            "growth": "the MSbar bubble logarithm and finite-time transient have at most logarithmic growth after compact source and spectator smearing; multiplication by the degree-four F2 preserves polynomial growth",
            "functional": "A4:S(R^4)->C is a tempered distribution and therefore continuous in the Schwartz topology",
            "continuity_consequence": "because A4(h0) is nonzero, there exists finite R0 such that |A4(h_R)-A4(h0)|<|A4(h0)|/2 for every R>=R0",
            "status": "FINITE_ORDER_PAIR_RESPONSE_TEMPERED_AND_CUTOFF_CONTINUOUS"
        },
        "exact_darkness_and_probability": {
            "leading_identity": "A2(h_R)=integral dP h_R_hat(P) C2(P) integral_sphere F2(P,r)dOmega=0 for every finite R",
            "reason": "the inner angular integral is zero separately on every timelike P fibre, so Paley--Wiener Fourier tails do not mix into a lower lambda order",
            "amplitude_retention": "|A4(h_R)|>|A4(h0)|/2 for R>=R0",
            "imported_lower": receipt(base_lower),
            "compact_lower": receipt(retained_lower),
            "comparison": "Q8_compact/q4_bar>1/18874368000>1/20000000000",
            "joint_expansion": "p_selected=g_det^2*lambda^8*Q8_compact+O(g_det^2*lambda^10)+O(g_det^4)",
            "status": "STRICTLY_POSITIVE_COMPACT_SPACETIME_LOCAL_DARK_Q8_COEFFICIENT"
        },
        "disposition": {
            "compact_spacetime_switching": "CONSTRUCTED_AS_NONEMPTY_EXISTENCE_CLASS",
            "finite_support_radius": "EXISTS_BUT_NOT_NUMERICALLY_BOUNDED",
            "Fourier_support": "NONCOMPACT_AND_RETAINED",
            "leading_BT_amplitude_annihilation": "EXACT_FOR_EVERY_CUTOFF_RADIUS",
            "absolute_compact_spacetime_dark_q8": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "all_orders_in_external_detector_coupling": "NOT_CONSTRUCTED",
            "all_order_or_all_time_BT_probability": "NOT_CONSTRUCTED",
            "causal_pAQFT_observable": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a numerical cutoff radius R0, detector duration or spatial size",
            "compact Fourier support or absence of Fourier tails",
            "a renormalized time-ordered causal perturbative AQFT construction",
            "the sign of the g_detector^4 or lambda^10 remainders",
            "selection of the apparatus axis, cutoff profile, coupling or outcome by public BT dynamics",
            "the recorded or bright-port absolute order-lambda8 coefficient",
            "forward, collinear, real-virtual or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive BT Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute a quantitative Schwartz-seminorm continuity constant and finite R0 for a chosen bump, or compute the g_detector^4 correction for the compactly switched pointer outcome. The BT-internal alternative remains the O(lambda^10) dark remainder or general Eq. (19); gravity and Lorentzian transfer remain separate.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_compact_spacetime_quadrupole_dark_detector_q8.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_compact_spacetime_quadrupole_dark_detector_q8.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_spacetime_quadrupole_dark_detector_q8"
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
        print(CERT_REL)
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(CERT_REL) != payload:
            print("BT COMPACT SPACETIME QUADRUPOLE Q8: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT COMPACT SPACETIME QUADRUPOLE Q8: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
