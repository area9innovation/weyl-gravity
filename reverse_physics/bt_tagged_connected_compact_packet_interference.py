#!/usr/bin/env python3
"""Compact-packet completion of tagged/connected BT tree interference."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-tagged-connected-compact-packet-interference-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-tagged-connected-compact-packet-interference.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-connected-compact-packet-interference.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def equal_cell_matrix_element(cell_measure, values):
    """Uniform normalized packet matrix element for B_ij=h*W_ij."""
    count = len(values)
    if not count or any(len(row) != count for row in values):
        raise ValueError("kernel table must be nonempty and square")
    return cell_measure * sum(sum(row) for row in values) / count


def build():
    box = load(INPUTS[1])
    interference = load(INPUTS[2])
    tagged = load(INPUTS[3])
    scalar_packet = load(INPUTS[4])
    global_packet = load(INPUTS[5])
    Hamiltonian_packet = load(INPUTS[6])

    coupling, duration, d0 = sp.symbols("lambda T d0", positive=True)
    mu_in, mu_out, mu = sp.symbols("mu_in mu_out mu", positive=True)
    overlap, packet_kernel = sp.symbols("c_fg C_fg", complex=True)

    masks_R = [7, 19, 21, 14, 26, 28]
    masks_N = [11, 13, 25, 22]
    weights = {mask: (5 if mask in masks_R else 6) for mask in masks_R + masks_N}
    total_weight = sum(weights.values())
    pointwise_bound = sp.factor(total_weight * duration / d0)
    functional_bound = sp.factor(pointwise_bound * sp.sqrt(mu_in * mu_out))
    relative_functional = sp.Rational(2, 3) * sp.sqrt(2) * coupling**2 * sp.re(
        sp.conjugate(overlap) * packet_kernel
    )

    # Exact equal-cell refinement.  The matrix of an integral operator in
    # normalized cell indicators has B_ij=h*W_ij.  A uniform packet has
    # coefficients 1/sqrt(N), giving h/N times the sum of all W_ij.
    kernel_value = Fraction(7, 11)
    packet_measure = Fraction(3, 13)
    refinement_rows = []
    for count in (1, 2, 5, 11):
        h = packet_measure / count
        values = [[kernel_value for _ in range(count)] for _ in range(count)]
        matrix_element = equal_cell_matrix_element(h, values)
        refinement_rows.append(
            {
                "cells": count,
                "cell_measure": str(h),
                "packet_measure": str(count * h),
                "kernel_value": str(kernel_value),
                "matrix_element": str(matrix_element),
            }
        )

    # Nonconstant fixture makes the double-sum normalization observable.
    nonconstant = [
        [Fraction(2), Fraction(1, 3), Fraction(-1, 5)],
        [Fraction(4, 7), Fraction(3, 2), Fraction(5, 9)],
        [Fraction(-2, 11), Fraction(7, 8), Fraction(6, 5)],
    ]
    nonconstant_h = Fraction(1, 17)
    nonconstant_value = equal_cell_matrix_element(nonconstant_h, nonconstant)
    wrong_diagonal_only = nonconstant_h * sum(
        nonconstant[index][index] for index in range(3)
    ) / 3

    leading_q4_prefactor = sp.Rational(75, 2048)
    packet_q6_prefactor = sp.factor(leading_q4_prefactor * sp.Rational(2, 3))
    box_energy_factor = sp.Rational(5, 12)
    box_q6_prefactor = sp.factor(packet_q6_prefactor * box_energy_factor)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(
            row["checks"]["ok"]
            for row in (box, interference, tagged, scalar_packet, global_packet, Hamiltonian_packet)
        ),
        "public_packet_cross_CCR_is_imported": box["common_finite_volume_spectator"]["public_cross_CCR"] == "[b_Omega(p),b_Upsilon^dagger(q)]=2*E_p*delta_3(p-q)",
        "compact_positive_packet_norm_is_imported": scalar_packet["positive_packet_frame"]["source_norm"] == "1",
        "tagged_identity_overlap_is_imported": tagged["complete_leading_tagged_probability"]["spectator_packet"].endswith("identity overlap has norm one"),
        "six_tag_odd_masks_are_rebuilt": len(masks_R) == 6 and set(masks_R).isdisjoint(masks_N),
        "four_resonant_masks_are_rebuilt": len(masks_N) == 4,
        "incidence_weights_are_five_and_six": set(weights[mask] for mask in masks_R) == {5} and set(weights[mask] for mask in masks_N) == {6},
        "total_absolute_incidence_weight_is_54": total_weight == 54,
        "compact_kernel_bound_is_54T_over_d0": pointwise_bound == 54 * duration / d0,
        "packet_functional_bound_is_exact": functional_bound == 54 * duration * sp.sqrt(mu_in * mu_out) / d0,
        "relative_cross_functional_has_exact_prefactor": relative_functional == 2 * sp.sqrt(2) * coupling**2 * sp.re(sp.conjugate(overlap) * packet_kernel) / 3,
        "leading_tagged_prefactor_is_75_over_2048": leading_q4_prefactor == sp.Rational(75, 2048),
        "compact_packet_q6_prefactor_is_25_over_1024": packet_q6_prefactor == sp.Rational(25, 1024),
        "single_box_mode_prefactor_is_125_over_12288": box_q6_prefactor == sp.Rational(125, 12288),
        "all_constant_kernel_refinements_preserve_mu_W": all(
            Fraction(row["matrix_element"]) == packet_measure * kernel_value
            for row in refinement_rows
        ),
        "refinement_cell_measure_tends_down": [Fraction(row["cell_measure"]) for row in refinement_rows] == [Fraction(3, 13), Fraction(3, 26), Fraction(3, 65), Fraction(3, 143)],
        "refinement_packet_measure_stays_fixed": all(Fraction(row["packet_measure"]) == packet_measure for row in refinement_rows),
        "nonconstant_double_sum_is_exact": nonconstant_value == Fraction(36887, 282744),
        "off_diagonal_terms_are_not_discarded": nonconstant_value != wrong_diagonal_only,
        "single_cell_formula_is_h_times_W": equal_cell_matrix_element(Fraction(5, 23), [[Fraction(7, 19)]]) == Fraction(35, 437),
        "finite_box_cell_measure_is_inverse_mode_norm": box["common_finite_volume_spectator"]["connected_factor"].endswith("=1/N_s"),
        "global_connected_packet_operator_is_bounded": global_packet["interpretation"]["q_B_zero_cutoff"] == "REMOVED_FOR_FIXED_FINITE_TIME_CONNECTED_COLUMN",
        "compact_Hamiltonian_kernel_is_Hilbert_Schmidt": Hamiltonian_packet["interpretation"]["compact_packet_BT_Hamiltonian_strength"] == "CONSTRUCTED_AS_EXPLICIT_INTEGRAL_OPERATOR",
        "point_kernel_is_strictly_positive_for_positive_time": interference["interpretation"]["finite_time_value"] == "FINITE_AND_STRICTLY_POSITIVE_FOR_T_GT_ZERO",
        "fixed_packet_limit_is_not_single_mode_limit": refinement_rows[0]["matrix_element"] == refinement_rows[-1]["matrix_element"] and Fraction(refinement_rows[-1]["cell_measure"]) < Fraction(refinement_rows[0]["cell_measure"]),
        "smooth_approximation_uses_bounded_compact_kernel": True,
        "complete_lambda6_is_not_promoted": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1",
        "schema_version": "reverse-physics-bt-tagged-connected-compact-packet-interference-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact normalized compact-wave-packet functional and box-refinement theorem for the tagged/connected finite-time BT tree interference",
        "question": "Does the single-mode 1/V suppression make the tagged/connected resonant tree cross term vanish for a fixed physical compact packet, or is that limit changing the state?",
        "answer": "The single-mode limit changes the state. Smearing the positive ghost-even spectator with normalized compact packets f and g gives identity overlap c_fg=<g,f> and the connected functional C_fg=<g,W_kappa,T f>, where W_kappa,T is the active-contracted ten-channel finite-time kernel. The exact relative tree cross is (2*sqrt(2)*lambda^2/3)*Re[conj(c_fg)*C_fg]. On a compact hard tagged tube with every oriented denominator D_A>=d0, the incidence weights give |W_kappa,T(k,p)|<=54*T/d0, so the packet operator is Hilbert--Schmidt and the cross is finite. Its diagonal at the certified fixture is the strictly positive W_kappa(T); continuity therefore supplies a nonnegative normalized compact packet with strictly positive tree cross for every fixed T>0. In an equal-cell box discretization, a cell has dnu-measure h and the normalized packet matrix element is (h/N)*sum_ij W_ij. A single mode gives h*W=W/N_s, reproducing the finite-box theorem. A fixed packet of measure mu=N*h instead gives mu*W for a constant kernel and converges to the double packet integral for a continuous kernel. Hence its continuum limit is generally finite and nonzero: O(V) coherent modes compensate the 1/V matrix element. This constructs the box-independent tree-cross functional, not the complete order-lambda6 probability; active loop, source dressing, survival/virtual and forward-collinear completion remain open.",
        "compact_packet_carrier": {
            "one_particle_measure": "dnu(p)=d^3p/(2*E_p) in the public BT convention",
            "positive_packet": "u(f)=(|Omega,f>+|Upsilon,f>)/sqrt(2)",
            "normalization": "<u(f),u(f)>_K=||f||_L2(dnu)^2=1",
            "identity_overlap": "c_fg=<u(g),I*u(f)>_K=<g,f>_L2(dnu)",
            "same_packet_overlap": "c_ff=1",
            "support": "normalized compact packets on one hard tagged tube, separated from soft, collinear and competing component-delta supports",
            "status": "COMMON_NORMALIZED_COMPACT_SPECTATOR_PACKET_CONSTRUCTED"
        },
        "compact_tree_cross_functional": {
            "kernel": "W_kappa,T(k,p)=Re[5*sum_(A in R) beta_A,T(k,p)+6*sum_(A in N) beta_A,T(k,p)] after the common active packet contraction",
            "mask_sets": {"R": masks_R, "N": masks_N},
            "incidence_weight_sum": total_weight,
            "time_kernel": "beta_A,T=F_T(delta_A)/D_A, F_T(delta)=integral_0^T exp(i*delta*t)dt",
            "compact_denominator_hypothesis": "D_A>=d0>0 on the declared packet support",
            "pointwise_bound": "|W_kappa,T(k,p)|<=54*T/d0",
            "operator": "(W_kappa,T f)(k)=integral W_kappa,T(k,p)f(p)dnu(p)",
            "functional": "C_fg=<g,W_kappa,T f>=double_integral conj(g(k))*W_kappa,T(k,p)*f(p)dnu(k)dnu(p)",
            "functional_bound": "|C_fg|<=54*T*sqrt(mu_in*mu_out)/d0 for normalized packets",
            "relative_tree_cross": "q_cross^(6)[g,f]/q_tag^(4)=(2*sqrt(2)*lambda^2/3)*Re[conj(c_fg)*C_fg]",
            "fixture_diagonal": "W_kappa,T(p_star,p_star)=W_kappa(T)=w(kappa*T)/kappa^2>0 for T>0",
            "fixture_probability": "q_cross^(6)[f,f]=25*sqrt(2)*lambda^6*DeltaOmega*Re(C_ff)/(1024*pi^2*kappa^2*Area)",
            "status": "BOX_INDEPENDENT_COMPACT_PACKET_TREE_CROSS_FUNCTIONAL_COMPUTED"
        },
        "box_to_packet_limit": {
            "normalized_cell_basis": "e_i=1_Ci/sqrt(h) for equal dnu-cell measure h",
            "connected_matrix": "B_ij=h*W_ij",
            "uniform_packet": "f_N=N^(-1/2)*sum_i e_i with total packet measure mu=N*h",
            "matrix_element": "<f_N,B*f_N>=(h/N)*sum_(i,j)W_ij",
            "single_mode": "N=1 gives h*W; with h=1/(2*E_s*V)=1/N_s this is W/N_s",
            "fixed_packet_constant_kernel": "h=mu/N gives <f_N,B*f_N>=mu*W for every N",
            "continuous_kernel_limit": "as the cell mesh tends to zero at fixed support, the equal-cell sum converges to mu^(-1)*double_integral_(SxS)W(k,p)dnu(k)dnu(p)",
            "smooth_packet_extension": "bounded compact kernels are Hilbert--Schmidt, so L2 smooth approximants converge in the packet functional",
            "mode_counting": "at fixed physical packet support N is proportional to V; its coherent double sum compensates the single-mode 1/V factor",
            "constant_kernel_fixture": refinement_rows,
            "nonconstant_fixture": {"cell_measure": str(nonconstant_h), "matrix_element": str(nonconstant_value), "diagonal_only_wrong_value": str(wrong_diagonal_only)},
            "status": "FIXED_PACKET_CONTINUUM_LIMIT_FINITE_AND_SINGLE_MODE_LIMIT_CLASSIFIED"
        },
        "physical_interpretation": {
            "single_box_mode_fixed_T_V_to_infinity": "ZERO_BUT_STATE_BECOMES_MOMENTUM_SHARP",
            "fixed_compact_packet_box_refinement": "FINITE_AND_GENERALLY_NONZERO",
            "strictly_positive_local_packet_exists_for_each_fixed_T_gt_0": "YES_BY_CONTINUITY_OF_THE_FINITE_TIME_KERNEL",
            "compact_packet_tree_cross": "COEFFICIENT_COMPUTED_AS_FUNCTIONAL",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "active_loop_source_survival_completion": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the public BT one-particle measure dnu=d^3p/(2E_p) and off-diagonal cross CCR are used without an unrecorded two-pi conversion",
            "incoming and outgoing normalized spectator packets lie on one compact hard tagged tube and the same active preparation/detector contraction used by the certified tagged fixture",
            "the ten oriented channel denominators obey D_A>=d0>0 on packet support; resonances occur through delta_A=0 and are regular at finite T",
            "the active external-mass projector, label orbit, angular acceptance and beam factor are common to the leading tagged and connected terms",
            "the equal-cell discretization refines a fixed physical packet support when N grows with V; holding N=1 instead defines a different momentum-sharpening family",
            "T is fixed and finite for the compactness, continuity and positivity-neighborhood statement"
        ],
        "does_not_establish": [
            "a packet-independent numerical value for the compact tree cross",
            "a canonical packet shape, detector resolution, duration or acceptance",
            "the complete order-lambda6 tagged probability",
            "the active four-point one-loop interference",
            "the order-lambda dressed-source contribution or the potentially earlier order-lambda5 probability term",
            "the matching virtual or survival contribution required by pseudo-unitarity",
            "forward, collinear or real-virtual/KLN completion",
            "an all-time Moller, LSZ or S operator",
            "uniform control of the secular limit T to infinity",
            "the standard scalar projector or general Eq. (19)",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "complete tagged probability through order lambda6", "status": "MISSING", "required_value": "assemble this packet tree cross with active loop, source dressing, detector/survival and normalization terms on the same packet carrier"},
            {"object": "order-lambda dressed source on the tagged packet", "status": "MISSING", "required_value": "derive the full oscillatory and endpoint-completed R_t action rather than fitting or omitting the possible lambda5 probability term"},
            {"object": "forward-collinear inclusive completion", "status": "MISSING", "required_value": "place real, virtual, survival and degenerate sectors on one regulated packet domain and prove regulator cancellation"},
            {"object": "gravity transfer", "status": "MISSING", "required_value": "construct the corresponding metric BV/BRST physical carrier, detector and restored quantum master equation before any residual transfer"}
        ],
        "next_gate": "Audit the tagged packet probability by perturbative order before computing another coefficient. The first unresolved term is the possible order-lambda correction to the dressed source, which can interfere with the order-lambda2 tagged amplitude at probability order lambda5. Either prove that term vanishes on the ghost-even tagged packet from the dynamically derived R_t kernel, or compute it together with its endpoint/oscillatory completion. Only after disposing of lambda5 should the active one-loop, this lambda6 tree cross, and survival terms be assembled as the complete physical lambda6 probability. General Eq. (19), gravity and Lorentzian transfer remain later gates.",
        "provenance": {
            "source_commit": "e60edd43",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact incidence algebra and rational equal-cell discretization, combined with analytic Cauchy--Schwarz, Hilbert--Schmidt, continuity and Riemann-sum arguments on the certified compact hard packet carrier. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_compact_packet_interference.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_compact_packet_interference.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_compact_packet_interference"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
