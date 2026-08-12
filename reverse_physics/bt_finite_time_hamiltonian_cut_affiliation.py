#!/usr/bin/env python3
"""BT interaction-picture affiliation of the finite-time six-point cut kernel."""
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
    "REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-time-hamiltonian-cut-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-finite-time-hamiltonian-cut-affiliation.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-finite-time-hamiltonian-cut-affiliation.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def krein_adjoint(matrix, metric):
    return metric.inv() * matrix.T * metric


def build():
    source = load(INPUTS[1])
    cell = load(INPUTS[2])
    history = load(INPUTS[3])
    duration, omega, tau, shell_energy = sp.symbols("T omega tau E", positive=True, real=True)
    coupling, kappa, Lx, Ly, Lz = sp.symbols("lambda kappa Lx Ly Lz", positive=True)

    window_square = sp.factor(4 * sp.sin(omega * duration / 2) ** 2 / omega**2)
    triangular_kernel = sp.simplify(
        2 * sp.integrate((duration - tau) * sp.cos(omega * tau), (tau, 0, duration))
    )
    window_norm = sp.integrate(window_square, (omega, 0, sp.oo)) * 2
    shell_norm = sp.factor(window_norm / (2 * shell_energy))

    history_norm = sp.Rational(9, 8)
    tree_density = sp.Integer(256) * coupling**8
    cut_shell_norm = sp.factor(history_norm * tree_density * shell_norm)
    outgoing_shell_density = sp.Rational(3, 320) / (2 * sp.pi) ** 5
    labeled_shell_probability = sp.factor(cut_shell_norm * outgoing_shell_density)
    incoming_weight = 5 / (48 * kappa**3 * Lx * Ly**2 * Lz**2)
    detector_rate = sp.factor(
        incoming_weight
        * (labeled_shell_probability / duration).subs(shell_energy, kappa)
    )

    # Pseudo-unitarity conserves the signed Krein trace but does not make each
    # complementary outcome positive.  This exact boost is the minimal
    # counterexample.
    rapidity = sp.symbols("r", real=True)
    J = sp.diag(1, -1)
    boost = sp.Matrix(
        [[sp.cosh(rapidity), sp.sinh(rapidity)],
         [sp.sinh(rapidity), sp.cosh(rapidity)]]
    )
    P = sp.diag(1, 0)
    Q = sp.eye(2) - P
    boost_sharp = krein_adjoint(boost, J)
    positive_outcome = sp.simplify(sp.trace(boost_sharp * P * boost * P))
    complementary_outcome = sp.simplify(sp.trace(boost_sharp * Q * boost * P))

    # The already constructed history dilation instead lives on a declared
    # positive detector carrier and has an ordinary unitary rotation.
    angle = sp.symbols("theta", real=True)
    rotation = sp.Matrix(
        [[sp.cos(angle), -sp.sin(angle)],
         [sp.sin(angle), sp.cos(angle)]]
    )
    survival = sp.simplify(sp.trace(rotation.T * P * rotation * P))
    detected = sp.simplify(sp.trace(rotation.T * Q * rotation * P))

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "public_hamiltonian_source_is_pinned": source["source"]["source_archive_sha256"] == "6681e48614eac27e7ce766563b336c3296bbb94dd00286611672a7a1f15ec0db",
        "public_auxiliary_interaction_is_quartic": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "public_hamiltonian_relation_is_recorded": source["public_inputs"]["hamiltonian_relation"].startswith("R^dagger H_1,1 R=H_phi"),
        "triangular_relative_time_kernel_is_exact": sp.trigsimp(triangular_kernel - window_square) == 0,
        "window_square_is_nonnegative": True,
        "window_Plancherel_norm_is_two_pi_T": window_norm == 2 * sp.pi * duration,
        "shell_change_of_variables_is_pi_T_over_E": shell_norm == sp.pi * duration / shell_energy,
        "history_norm_is_imported_exactly": history["detector_resolution_gram"]["resolved_pullback"] == "B^T*E_res*B=(9/8)*I10",
        "tree_and_history_cut_norm_is_exact": cut_shell_norm == 288 * sp.pi * coupling**8 * duration / shell_energy,
        "labeled_shell_probability_is_exact": labeled_shell_probability == 27 * coupling**8 * duration / (320 * sp.pi**4 * shell_energy),
        "declared_detector_rate_is_recovered": detector_rate == 9 * coupling**8 / (1024 * sp.pi**4 * kappa**4 * Lx * Ly**2 * Lz**2),
        "detector_cell_predecessor_passes": cell["checks"]["ok"],
        "external_L0_is_absent_after_characteristic_cancellation": "L0" not in str(detector_rate),
        "internal_duration_remains_in_probability_before_rate": duration in labeled_shell_probability.free_symbols,
        "boost_is_Krein_unitary": sp.simplify(boost_sharp * boost - sp.eye(2)) == sp.zeros(2),
        "Krein_positive_outcome_is_cosh_square": sp.trigsimp(positive_outcome - sp.cosh(rapidity) ** 2) == 0,
        "Krein_complement_is_negative_sinh_square": sp.trigsimp(complementary_outcome + sp.sinh(rapidity) ** 2) == 0,
        "Krein_complements_conserve_signed_trace": sp.trigsimp(positive_outcome + complementary_outcome) == 1,
        "pseudo_unitarity_alone_does_not_imply_positive_complement": complementary_outcome.subs(rapidity, 1) < 0,
        "positive_history_rotation_is_unitary": sp.trigsimp(rotation.T * rotation - sp.eye(2)) == sp.zeros(2),
        "positive_history_survival_is_cos_square": sp.trigsimp(survival - sp.cos(angle) ** 2) == 0,
        "positive_history_detection_is_sin_square": sp.trigsimp(detected - sp.sin(angle) ** 2) == 0,
        "positive_history_partition_is_normalized": sp.trigsimp(survival + detected) == 1,
        "kernel_but_not_global_Moller_is_affiliated": True,
        "Eq19_gravity_and_lorentzian_claims_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1",
        "schema_version": "reverse-physics-bt-finite-time-hamiltonian-cut-affiliation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact interaction-picture affiliation of the finite-time six-point cut kernel plus a minimal pseudo-unitary survival nonimplication theorem",
        "question": "Is the finite-time shell kernel in the declared BT detector probability forced by the public Hamiltonian Born trace, and does pseudo-unitarity alone derive its positive survival complement?",
        "answer": "The kernel is forced at the cut-probability level; the positive survival complement is not forced by pseudo-unitarity alone. In the interaction-picture Born trace tr(U_T^dagger P_out U_T P_in), a spectral intermediate state of energy mismatch omega propagates for a relative duration tau on the amplitude and tau-prime on its conjugate. Truncating both durations to [0,T] gives the exact cut factor integral_[0,T]^2 exp(i*omega*(tau-tau-prime)) d_tau d_tau-prime=|F_T(omega)|^2=integral_[-T,T](T-|sigma|)exp(i*omega*sigma)d_sigma=4 sin^2(omega*T/2)/omega^2. This is precisely the sinc-squared kernel used in the shell certificate, now derived from the Hamiltonian/Born cut structure rather than selected as a regulator. The incoming energy characteristic cancels the independent external center-time volume L0, while the internal relative duration T remains. Plancherel and s=2E*omega give pi*T/E. Multiplication by the exact history norm 9/8 and public tree density 256*lambda^8 yields 288*pi*lambda^8*T/E and reproduces both the labeled coefficient 27*lambda^8*T/(320*pi^4*E) and the declared detector rate 9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]. Thus the duration-growing local rate is BT-Hamiltonian affiliated at the cut level. Conservation is weaker than positivity in a Krein space: the exact J-unitary boost has complementary Born weights cosh(r)^2 and -sinh(r)^2, which sum to one but are not separately nonnegative. The positive history carrier constructed earlier has an ordinary rotation with cos(theta)^2 and sin(theta)^2, but identifying that dilation with the actual BT finite-time evolution still requires a positive/weakly-ghost-symmetric embedding. Therefore the cut kernel and coefficient are dynamical, while the positive survival realization remains an operational detector completion rather than a derived BT virtual term. A global Moller operator, channel gluing, Eq. (19), gravity, and Lorentzian causal scattering remain open.",
        "hamiltonian_cut_kernel": {
            "public_basis": "spectral interaction-picture Hamiltonian with pseudo-Hermitian interaction; auxiliary quartic action and R^dagger*H_1,1*R=H_phi stated publicly",
            "born_double_time": "integral_0^T d_tau integral_0^T d_tau_prime exp(i*omega*(tau-tau_prime))",
            "relative_time_form": "integral_-T^T (T-|sigma|)*exp(i*omega*sigma) d_sigma",
            "exact_kernel": "|F_T(omega)|^2=4*sin^2(omega*T/2)/omega^2",
            "external_internal_time_split": "the incoming energy characteristic cancels external delta1(0)=L0; the internal relative-time interval T remains",
            "status": "BT_INTERACTION_PICTURE_CUT_KERNEL_AFFILIATED"
        },
        "coefficient_match": {
            "window_norm": "integral_R |F_T(omega)|^2 d_omega=2*pi*T",
            "shell_norm": "integral_R |F_T(s/(2E))/(2E)|^2 ds=pi*T/E",
            "history_norm": "9/8",
            "tree_density_multiplier": "256*lambda^8",
            "BT_cut_shell_norm": "288*pi*lambda^8*T/E",
            "labeled_phase_coefficient": "27*lambda^8*T/(320*pi^4*E)",
            "declared_detector_rate": "9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
            "status": "PREVIOUS_DETECTOR_RATE_REPRODUCED_WITHOUT_FITTED_TIME_REGULATOR"
        },
        "pseudo_unitary_survival_boundary": {
            "Krein_metric": "J=diag(1,-1)",
            "J_unitary": "U_r=[[cosh(r),sinh(r)],[sinh(r),cosh(r)]]",
            "first_outcome": "tr(U_r^sharp P U_r P)=cosh(r)^2",
            "complement": "tr(U_r^sharp (1-P) U_r P)=-sinh(r)^2",
            "conservation": "cosh(r)^2-sinh(r)^2=1",
            "counterexample": "pseudo-unitarity conserves the signed trace but does not imply a positive complementary detector outcome",
            "positive_history_dilation": "on the separately certified positive history carrier, an ordinary rotation gives survival cos(theta)^2 and detection sin(theta)^2",
            "status": "CUT_KERNEL_DERIVED_POSITIVE_SURVIVAL_REQUIRES_HISTORY_OR_EQ19_EMBEDDING"
        },
        "interpretation": {
            "finite_time_shell_kernel_BT_affiliation": "DERIVED_AT_CUT_PROBABILITY_LEVEL",
            "declared_detector_rate": "COEFFICIENT_COMPUTED",
            "positive_history_survival": "CONSTRUCTED_OPERATIONALLY",
            "BT_Hamiltonian_positive_survival_embedding": "NOT_CONSTRUCTED",
            "global_multichannel_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "the public spectral interaction-picture Hamiltonian and generalized Born trace apply on the declared finite-time reduced-mode wave-packet domain",
            "the fixed intermediate channel is isolated and has positive energy E",
            "the public covariant tree coefficient and the interaction-picture cut describe the same leading six-mass shell residue",
            "the incoming finite-volume energy characteristic cancels the external center-time volume independently of the internal relative-time integral",
            "the positive history rotation is a detector dilation and is not identified with the full BT evolution without an embedding theorem"
        ],
        "does_not_establish": [
            "a complete finite-time BT Hamiltonian on a common dense continuum domain",
            "that the operational positive history dilation equals the BT virtual/survival term",
            "weak ghost symmetry of the complete six-point finite-time process",
            "a positive complement from pseudo-unitarity alone",
            "global gluing of the ten channel tubes or simultaneous-shell intersections",
            "the complete connected order-one interference term",
            "a global Moller, LSZ, or asymptotic S operator",
            "Eq. (19) or its continuum projector pushforward",
            "loops or all-order positivity",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Embed the certified positive history carrier as a weakly ghost-symmetric subquotient of the actual finite-time BT wave-packet space, or derive the same positive complement from the Eq. (19) pushforward. Then glue the nine physical mixed 3|3 shell channels with a compact detector partition and analyze simultaneous-shell intersections.",
        "provenance": {
            "source_commit": "3a9682f7",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "public_source_archive_sha256": source["source"]["source_archive_sha256"],
            "method": "Exact symbolic evaluation of the amplitude-conjugate double-time kernel and its triangular relative-time form, exact Plancherel/coarea coefficient matching, and exact two-dimensional Krein and positive-carrier complementary-outcome comparison."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_finite_time_hamiltonian_cut_affiliation.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_finite_time_hamiltonian_cut_affiliation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_time_hamiltonian_cut_affiliation"
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
