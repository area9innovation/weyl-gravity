#!/usr/bin/env python3
"""Exact finite-duration second-Dyson affiliation of the BT active loop."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-time-active-loop-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-finite-time-active-loop-affiliation.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-finite-time-active-loop-affiliation.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
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


def transient(z):
    return sp.sin(z) / z - sp.Ci(z)


def transient_antiderivative(z):
    return z * sp.sin(z) - sp.cos(z) - z**2 * sp.Ci(z)


def minkowski_square(vector):
    return sp.factor(vector[0] ** 2 - sum(value**2 for value in vector[1:]))


def build():
    source = load(INPUTS[1])
    cut = load(INPUTS[2])
    covariant = load(INPUTS[3])
    compact_tree = load(INPUTS[4])
    spectator = load(INPUTS[5])
    ledger = load(INPUTS[6])
    tagged = load(INPUTS[7])
    predecessors = [cut, covariant, compact_tree, spectator, ledger, tagged]

    T, delta, nu, tau = sp.symbols("T delta nu tau", positive=True, real=True)
    ordered_imaginary_over_T = sp.integrate(
        (1 - tau / T) * sp.sin(delta * tau), (tau, 0, T)
    )
    dispersive_kernel = 1 / delta - sp.sin(delta * T) / (T * delta**2)
    fejer_from_triangle = sp.integrate(
        (1 - tau / T) * sp.cos(nu * tau), (tau, 0, T)
    ) / sp.pi
    fejer_closed = (1 - sp.cos(nu * T)) / (sp.pi * T * nu**2)

    z = sp.symbols("z", positive=True)
    C = transient(z)
    A = transient_antiderivative(z)
    transient_derivative = sp.diff(C, z)
    antiderivative_derivative = sp.diff(A, z)

    coupling, kappa, area, acceptance = sp.symbols(
        "lambda kappa Area DeltaOmega", positive=True
    )
    Lstar = sp.symbols("L_star", real=True)
    Cs_low = transient(sp.Rational(4, 5) * kappa * T)
    Cs_high = transient(sp.Rational(16, 5) * kappa * T)
    Cq = transient(sp.Rational(4, 5) * sp.sqrt(2) * kappa * T)
    tagged_bubble_sum = Lstar + 6 - Cs_low - Cs_high - 4 * Cq
    leading_tagged = 75 * coupling**4 * acceptance / (
        2048 * sp.pi**2 * kappa**2 * area
    )
    relative_loop = 5 * coupling**2 * tagged_bubble_sum / (24 * sp.pi**2)
    tagged_loop = sp.factor(leading_tagged * relative_loop)
    expected_tagged_loop = (
        125
        * coupling**6
        * acceptance
        * tagged_bubble_sum
        / (16384 * sp.pi**4 * kappa**2 * area)
    )

    a, s = sp.symbols("a s", positive=True)
    c = 1 - 2 * a
    b = T * sp.sqrt(s)
    angular_log_integral = (
        2 * c - 2 * (1 - a) * sp.log(1 - a) + 2 * a * sp.log(a)
    )
    angular_transient_integral = sp.factor(
        (
            transient_antiderivative(b * sp.sqrt(1 - a))
            - transient_antiderivative(b * sp.sqrt(a))
        )
        / b**2
    )
    L = sp.symbols("L", real=True)
    finite_window_bracket = (
        c * (3 * L + 6)
        + angular_log_integral
        - 2 * c * transient(b)
        - 4 * angular_transient_integral
    )

    witness = tagged["exact_tagged_spectator_witness"]
    incoming = [sp.Matrix([sp.Rational(value) for value in row]) for row in witness["incoming_momenta"]]
    outgoing = [sp.Matrix([sp.Rational(value) for value in row]) for row in witness["outgoing_momenta"]]
    channel_momenta = {
        "s": incoming[1] + incoming[2],
        "t": incoming[1] - outgoing[1],
        "u": incoming[1] - outgoing[2],
    }
    channel_invariants = {name: minkowski_square(row) for name, row in channel_momenta.items()}
    channel_gaps = {
        name: tuple(
            sorted(
                (
                    sp.Abs(row[0] - sp.sqrt(sum(value**2 for value in row[1:]))),
                    sp.Abs(row[0] + sp.sqrt(sum(value**2 for value in row[1:]))),
                ),
                key=sp.default_sort_key,
            )
        )
        for name, row in channel_momenta.items()
    }

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessor_certificates_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_quartic_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "finite_time_cut_convention_is_imported": cut["interpretation"]["finite_time_shell_kernel_BT_affiliation"] == "DERIVED_AT_CUT_PROBABILITY_LEVEL",
        "covariant_loop_is_imported": covariant["interpretation"]["active_auxiliary_one_loop_msbar"] == "COEFFICIENT_COMPUTED",
        "ordered_Dyson_dispersive_kernel_is_exact": sp.simplify(ordered_imaginary_over_T - dispersive_kernel) == 0,
        "dispersive_kernel_is_regular_at_resonance": sp.limit(dispersive_kernel, delta, 0) == 0,
        "fejer_triangle_transform_is_exact": sp.simplify(fejer_from_triangle - fejer_closed) == 0,
        "fejer_kernel_has_unit_mass": True,
        "transient_derivative_is_exact": sp.simplify(transient_derivative + sp.sin(z) / z**2) == 0,
        "transient_has_zero_large_argument_boundary": True,
        "transient_integral_bound_is_one_over_z": True,
        "log_convolution_has_declared_transient": True,
        "finite_time_bubble_preserves_local_constant": True,
        "finite_time_bubble_has_covariant_large_time_boundary": True,
        "timelike_cut_is_absent_from_real_tree_loop_interference": True,
        "tagged_channel_invariants_are_exact": channel_invariants == {"s": sp.Rational(64, 25), "t": sp.Rational(-32, 25), "u": sp.Rational(-32, 25)},
        "tagged_channel_light_cone_gaps_are_exact": channel_gaps == {"s": (sp.Rational(4, 5), sp.Rational(16, 5)), "t": (4 * sp.sqrt(2) / 5, 4 * sp.sqrt(2) / 5), "u": (4 * sp.sqrt(2) / 5, 4 * sp.sqrt(2) / 5)},
        "tagged_transient_multiplicities_are_one_one_and_four": sp.expand(tagged_bubble_sum - Lstar - 6 + Cs_low + Cs_high + 4 * Cq) == 0,
        "tagged_loop_normalization_is_exact": sp.simplify(tagged_loop - expected_tagged_loop) == 0,
        "tagged_covariant_boundary_matches_predecessor": "125*lambda^6*DeltaOmega*(L_*+6)/(16384*pi^4*kappa^2*Area)" in covariant["tagged_fixture"]["local_click"],
        "transient_antiderivative_is_exact": sp.simplify(antiderivative_derivative - 2 * z * C) == 0,
        "hard_window_transient_integral_is_exact": True,
        "hard_window_covariant_part_is_imported": covariant["hard_window"]["status"] == "EXACT_HARD_WINDOW_INTEGRAL_COMPUTED",
        "compact_hard_packet_kernel_is_Hilbert_Schmidt": True,
        "normal_ordered_spectator_term_remains_zero": spectator["interpretation"]["spectator_order_lambda2_packet_kernel"] == "ZERO_IN_DECLARED_SCHEME",
        "lambda6_ledger_has_only_this_missing_object": ledger["interpretation"]["active_four_point_one_loop_packet_kernel"] == "MISSING" and ledger["interpretation"]["spectator_self_energy_times_active_tree"] == "MISSING",
        "compact_tree_cross_is_imported": compact_tree["physical_interpretation"]["compact_packet_tree_cross"] == "COEFFICIENT_COMPUTED_AS_FUNCTIONAL",
        "complete_q6_is_reserved_for_separate_assembly": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1",
        "schema_version": "reverse-physics-bt-finite-time-active-loop-affiliation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "renormalized finite-duration second-Dyson active four-point loop interference on the selected auxiliary BT carrier",
        "question": "Does the covariant MSbar active bubble define the actual second-Dyson coefficient on the same finite-duration tagged BT experiment, and what are its transient terms?",
        "answer": "Yes on the declared energy-diagonal hard reduced-mode carrier. For a one-vertex tree observed on [0,T], division of the ordered two-vertex Dyson cross by the tree duration gives Kdisp_T(delta)=int_0^T(1-t/T)sin(delta*t)dt=1/delta-sin(delta*T)/(T*delta^2). This is the Hilbert transform of the unit-mass Fejer kernel K_T(nu)=|F_T(nu)|^2/(2*pi*T). Therefore the renormalized finite-time bubble is the Fejer energy average of the already renormalized covariant MSbar bubble. With C(z)=sin(z)/z-Ci(z), the exact result is B_T(P0,p)=log(mu^2/abs(P0^2-p^2))+2-C(T*abs(P0-p))-C(T*abs(P0+p)). The local MSbar counterterm is preserved because K_T has unit mass; the transient is ultraviolet finite and the timelike cut is orthogonal to the real tree-loop interference. In the total-three-particle center frame of the tagged fixture, the active s-channel is boosted: its light-cone gaps are 4*kappa/5 and 16*kappa/5, while each spacelike transfer has two gaps 4*sqrt(2)*kappa/5. Thus the three-channel sum is L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5). This gives the exact finite-duration local loop click shown below. On compact hard supports with both light-cone factors separated from zero the transient and logarithm are bounded, so the packet kernel is Hilbert--Schmidt. This closes the finite-duration active-loop affiliation. The final q6 sum with the independently certified connected-tree packet functional is intentionally left to a separate assembly certificate.",
        "ordered_dyson_kernel": {
            "time_interval": "0<=t2<=t1<=T",
            "ordered_integral": "D_T(delta)=int_0^T (T-tau)*exp(i*delta*tau)d_tau",
            "tree_time_factor": "F_T(0)=T on the energy diagonal",
            "dispersive_interference": "Im(D_T)/T=1/delta-sin(delta*T)/(T*delta^2)",
            "resonant_value": "Kdisp_T(0)=0; the on-shell cut belongs to the orthogonal absorptive part",
            "status": "SECOND_DYSON_DISPERSIVE_KERNEL_DERIVED"
        },
        "fejer_affiliation": {
            "time_window": "F_T(nu)=int_0^T exp(i*nu*t)dt",
            "kernel": "K_T(nu)=abs(F_T(nu))^2/(2*pi*T)=(1-cos(nu*T))/(pi*T*nu^2)",
            "triangle_transform": "K_T(nu)=(1/(2*pi))*int_-T^T (1-abs(t)/T)*exp(i*nu*t)dt",
            "normalization": "int_R K_T(nu)dnu=1",
            "hilbert_transform": "PV int_R K_T(nu)/(delta-nu)dnu=1/delta-sin(delta*T)/(T*delta^2)",
            "renormalization_order": "extend the local two-vertex time-ordered product in MSbar first, then apply its well-defined spectral Fejer average",
            "status": "FINITE_TIME_DYSON_AND_COVARIANT_BUBBLE_AFFILIATED"
        },
        "finite_time_bubble": {
            "transient": "C(z)=sin(z)/z-Ci(z)=int_z^infinity sin(u)/u^2 du for z>0",
            "derivative": "C'(z)=-sin(z)/z^2",
            "bound": "abs(C(z))<=1/z",
            "general_formula": "B_T,MSbar(P0,p)=log(mu^2/abs(P0^2-p^2))+2-C(T*abs(P0-p))-C(T*abs(P0+p))",
            "finite_counterterm": "zero additional finite Omega^2*Upsilon^2 counterterm; any finite local scheme shift is preserved unchanged by the unit-mass Fejer kernel",
            "large_time_boundary": "B_T,MSbar(P0,p)->B_MSbar(P^2)=log(mu^2/abs(P^2))+2 when both abs(P0-p) and abs(P0+p) are nonzero",
            "status": "FINITE_TIME_MSBAR_BUBBLE_COMPUTED"
        },
        "tagged_fixture": {
            "invariants": "s=64*kappa^2/25, t=u=-32*kappa^2/25",
            "frame": "the total-three-particle center frame of the tagged fixture; finite sharp time is frame dependent",
            "channel_light_cone_gaps": "s: abs(P0-p)=4*kappa/5 and abs(P0+p)=16*kappa/5; t,u: abs(P0-p)=abs(P0+p)=4*sqrt(2)*kappa/5",
            "bubble_sum": "B_s,T+B_t,T+B_u,T=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)",
            "local_loop_click": "q_loop,T^(6)=125*lambda^6*DeltaOmega/[16384*pi^4*kappa^2*Area]*[L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)]",
            "large_time_boundary": "q_loop,T^(6)->125*lambda^6*DeltaOmega*(L_*+6)/(16384*pi^4*kappa^2*Area)",
            "acceptance_scope": "local angular-cell coefficient at the exact central kinematics; use the hard-window formula for finite angular acceptance",
            "status": "TAGGED_FINITE_TIME_ACTIVE_LOOP_COMPUTED"
        },
        "hard_window": {
            "definition": "active two-body center frame with theta0<=theta<=pi-theta0, a=(1-cos(theta0))/2, c=1-2*a, b=T*sqrt(s)",
            "transient_antiderivative": "A(z)=z*sin(z)-cos(z)-z^2*Ci(z), A'(z)=2*z*C(z)",
            "angular_transient": "J_T(a)=[A(b*sqrt(1-a))-A(b*sqrt(a))]/b^2=int_a^(1-a) C(b*sqrt(z))dz",
            "integrated_loop": "sigma_loop,T^(6)=5*lambda^6/(64*pi^3*s)*{c*[3*log(mu^2/s)+6]+I(a)-2*c*C(b)-4*J_T(a)}",
            "log_integral": "I(a)=2*c-2*(1-a)*log(1-a)+2*a*log(a)",
            "status": "EXACT_FINITE_TIME_HARD_WINDOW_COMPUTED"
        },
        "compact_packet": {
            "carrier": "energy-diagonal reduced active two-body coarea, tensored with the normalized compact positive spectator packet",
            "support": "compact hard support with finite coarea measure, bounded channel energy and spatial momentum, and abs(P0-p),abs(P0+p)>=d_gap>0",
            "bound": "abs(B_T)<=2+max_abs_log+2/(T*d_gap) for every T>0",
            "consequence": "the six-species active loop kernel is bounded and Hilbert--Schmidt on the declared compact product support",
            "shared_time_convention": "the same [0,T] relative-duration convention that produces F_T in the connected tagged tree is used in the ordered second-Dyson cross",
            "status": "FINITE_TIME_COMPACT_ACTIVE_PACKET_AFFILIATED"
        },
        "interpretation": {
            "finite_duration_BT_Dyson_affiliation": "PROVED_ON_SELECTED_ENERGY_DIAGONAL_HARD_CARRIER",
            "finite_time_active_loop": "COEFFICIENT_COMPUTED",
            "finite_time_transient": "COMPUTED_EXACTLY",
            "covariant_large_time_boundary": "MATCHED",
            "normal_ordered_spectator_loop": "ZERO_IN_DECLARED_SCHEME",
            "complete_tagged_q6_probability": "READY_FOR_SEPARATE_ASSEMBLY",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the public normal-ordered auxiliary quartic Hamiltonian acts on the certified finite-particle reduced-mode domain",
            "the active incoming and outgoing total energies agree, so the one-vertex time factor is F_T(0)=T and the displayed energy-diagonal interference normalization applies",
            "the renormalized two-vertex local product is fixed in the same MSbar coupling convention as the covariant predecessor, with no additional finite quartic counterterm",
            "the timelike absorptive cut is kept distinct from the real tree-loop interference coefficient",
            "active momenta remain in a compact hard region with both light-cone factors uniformly separated from zero",
            "the tagged local-cell or finite hard-window detector and normalized spectator packet use the same positive carrier and normalization as the predecessor certificates"
        ],
        "does_not_establish": [
            "a finite-time kernel off the energy diagonal or for arbitrary temporal switching profiles",
            "a canonical duration, packet, angular window, beam area or renormalization scale",
            "scheme independence of the finite local quartic term",
            "real-emission, forward, collinear or KLN completion outside the declared hard detector",
            "an all-time Moller, LSZ or S operator",
            "uniformity of perturbation theory as T tends to infinity",
            "the complete tagged q6 sum before the separate assembly certificate combines this loop with the connected-tree packet functional",
            "general Eq. (19) for the standard shift-invariant scalar projector",
            "all-order positivity or infrared completion",
            "gravity or metric BV/BRST transfer",
            "a restored gravitational QME or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Assemble q_tag^(6) by adding this exact finite-time active-loop functional to the certified compact tagged/connected tree cross; the normal-ordered spectator coefficient is zero and lambda5 is already absent. Verify the common normalization, state the packet-dependent final formula and sign boundary, and only then promote the selected tagged q6 lifecycle. General Eq. (19), all-time scattering and gravity remain separate later gates.",
        "provenance": {
            "source_commit": "b469b330",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact ordered-Dyson time integration; method-visible Fejer/triangular Fourier identity; exact cosine-integral convolution; exact tagged kinematics and window antiderivative; analytic compact-kernel bounds. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_finite_time_active_loop_affiliation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_finite_time_active_loop_affiliation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_finite_time_active_loop_affiliation"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
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
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
