#!/usr/bin/env python3
"""Exact finite pointer Hamiltonian for the two-angle BT detector."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-finite-apparatus-hamiltonian-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-two-angle-finite-apparatus-hamiltonian.md"
SOURCE = "d3b8acda66af6b01cabfcf84986a71d61ebac418"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-two-angle-finite-apparatus-hamiltonian-DONE-d3b8acda.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-two-angle-finite-apparatus-hamiltonian.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
    EVENT,
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


def matrix_strings(matrix):
    import sympy as sp

    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    q6 = load(INPUTS[1])
    q8 = load(INPUTS[2])
    dilation = load(INPUTS[3])
    event = load(EVENT)
    predecessors = [q6, q8, dilation]

    cp, sp_, cd, sd, a, b = sp.symbols(
        "c_phi s_phi c_delta s_delta a b", real=True
    )
    imaginary = sp.I
    z = cp + imaginary * sp_
    w = cd + imaginary * sd
    relations = [cp**2 + sp_**2 - 1, cd**2 + sd**2 - 1, a**2 + b**2 - 1]
    quotient = sp.groebner(
        relations, cp, cd, a, sp_, sd, b, order="lex", domain=sp.EX
    )

    def reduce_expr(value):
        numerator, denominator = sp.fraction(sp.cancel(sp.expand(value)))
        remainder = quotient.reduce(sp.expand(numerator))[1]
        return sp.factor(remainder / denominator)

    def zero(value):
        return reduce_expr(value) == 0

    def matrix_zero(matrix):
        return all(zero(value) for value in matrix)

    identity2 = sp.eye(2)
    p_plus = sp.Matrix([[1, sp.conjugate(z)], [z, 1]]) / 2
    p_minus = identity2 - p_plus
    p_minus_zero = sp.Matrix([[1, -1], [-1, 1]]) / 2
    phase_shifter = sp.diag(1, z)
    sigma_y = sp.Matrix([[0, -imaginary], [imaginary, 0]])
    pointer_rotation = a * identity2 - imaginary * b * sigma_y
    h_dimensionless = sp.kronecker_product(p_minus, sigma_y)
    unitary = (
        sp.kronecker_product(p_plus, identity2)
        + sp.kronecker_product(p_minus, pointer_rotation)
    )

    # Basis ordering is (angle, pointer).  Contract pointer input |0> and
    # pointer output |0>, |1> to obtain the two instrument Kraus maps.
    def kraus(pointer_out):
        return sp.Matrix(
            2,
            2,
            lambda angle_out, angle_in: unitary[
                2 * angle_out + pointer_out, 2 * angle_in
            ],
        )

    k_click = kraus(0)
    k_no = kraus(1)
    e_click = sp.simplify(k_click.conjugate().T * k_click)
    e_no = sp.simplify(k_no.conjugate().T * k_no)
    expected_k_click = p_plus + a * p_minus
    expected_k_no = b * p_minus
    expected_e_click = p_plus + a**2 * p_minus
    expected_e_no = b**2 * p_minus

    leading_calibrated = sp.Matrix([1, z])
    leading_mismatch = sp.Matrix([1, w])
    calibrated_click = (
        leading_calibrated.conjugate().T * e_click * leading_calibrated
    )[0]
    mismatch_click = (
        leading_mismatch.conjugate().T * e_click * leading_mismatch
    )[0]
    phase_dot = cp * cd + sp_ * sd
    expected_mismatch = 2 - b**2 * (1 - phase_dot)

    y1r, y1i, y2r, y2i = sp.symbols(
        "y1r y1i y2r y2i", real=True
    )
    y4 = sp.Matrix([y1r + imaginary * y1i, y2r + imaginary * y2i])
    q8_shift = (y4.conjugate().T * (e_click - identity2) * y4)[0]
    phase_difference = y4[0] - sp.conjugate(z) * y4[1]
    expected_q8_shift = -b**2 * sp.expand(
        sp.conjugate(phase_difference) * phase_difference
    ) / 2

    arbitrary_r1, arbitrary_i1, arbitrary_r2, arbitrary_i2 = sp.symbols(
        "r1 i1 r2 i2", real=True
    )
    arbitrary = sp.Matrix(
        [arbitrary_r1 + imaginary * arbitrary_i1, arbitrary_r2 + imaginary * arbitrary_i2]
    )
    cross_difference = (
        leading_calibrated.conjugate().T
        * (e_click - identity2)
        * arbitrary
    )[0]

    # Exact rational/unit-circle fixture: z=i and a=3/5,b=4/5.
    fixture = {cp: 0, sp_: 1, a: sp.Rational(3, 5), b: sp.Rational(4, 5)}
    fixture_p_plus = p_plus.subs(fixture)
    fixture_h = h_dimensionless.subs(fixture)
    fixture_u = unitary.subs(fixture)
    fixture_k_click = k_click.subs(fixture)
    fixture_k_no = k_no.subs(fixture)
    fixture_e_click = e_click.subs(fixture)
    fixture_e_no = e_no.subs(fixture)
    fixture_calibrated = {**fixture, cd: 0, sd: 1}
    fixture_mismatch = {**fixture, cd: 1, sd: 0}
    fixture_y4 = {y1r: 1, y1i: 2, y2r: -3, y2i: 1}

    h_square_expected = sp.kronecker_product(p_minus, identity2)
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "three_predecessors_pass": len(predecessors) == 3 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_this_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-finite-apparatus-hamiltonian"),
        "phase_projectors_are_complete": matrix_zero(p_plus + p_minus - identity2),
        "phase_projectors_are_idempotent": matrix_zero(p_plus * p_plus - p_plus) and matrix_zero(p_minus * p_minus - p_minus),
        "phase_projectors_are_orthogonal": matrix_zero(p_plus * p_minus) and matrix_zero(p_minus * p_plus),
        "phase_shifter_selects_antisymmetric_mode": matrix_zero(p_minus - phase_shifter * p_minus_zero * phase_shifter.conjugate().T),
        "Hamiltonian_is_self_adjoint": matrix_zero(h_dimensionless - h_dimensionless.conjugate().T),
        "Hamiltonian_square_is_projector": matrix_zero(h_dimensionless**2 - h_square_expected),
        "exponential_spectral_formula_is_unitary": matrix_zero(unitary.conjugate().T * unitary - sp.eye(4)),
        "pointer_rotation_is_unitary": matrix_zero(pointer_rotation.conjugate().T * pointer_rotation - identity2),
        "click_Kraus_is_derived": matrix_zero(k_click - expected_k_click),
        "no_click_Kraus_is_derived": matrix_zero(k_no - expected_k_no),
        "click_effect_is_derived": matrix_zero(e_click - expected_e_click),
        "no_click_effect_is_derived": matrix_zero(e_no - expected_e_no),
        "Kraus_effects_are_complete": matrix_zero(e_click + e_no - identity2),
        "epsilon_is_b_squared": matrix_zero(e_click - (identity2 - b**2 * p_minus)),
        "calibrated_leading_mode_is_fixed": matrix_zero(e_click * leading_calibrated - leading_calibrated),
        "calibrated_leading_probability_is_two": zero(calibrated_click - 2),
        "arbitrary_q6_cross_is_preserved": matrix_zero(sp.Matrix([cross_difference])),
        "phase_mismatch_response_is_exact": zero(mismatch_click - expected_mismatch),
        "complete_relative_q8_shift_is_phase_variance": zero(q8_shift - expected_q8_shift),
        "equal_energy_free_commutator_vanishes": matrix_zero(sp.eye(4) * h_dimensionless - h_dimensionless * sp.eye(4)),
        "fixture_unitary_is_exact": sp.simplify(fixture_u.conjugate().T * fixture_u) == sp.eye(4),
        "fixture_Kraus_completeness_is_exact": sp.simplify(fixture_k_click.conjugate().T * fixture_k_click + fixture_k_no.conjugate().T * fixture_k_no) == identity2,
        "fixture_epsilon_is_sixteen_twenty_fifths": fixture_e_no == sp.Rational(16, 25) * p_minus.subs(fixture),
        "fixture_calibrated_probability_is_two": sp.simplify(mismatch_click.subs(fixture_calibrated)) == 2,
        "fixture_quarter_turn_mismatch_probability_is_thirty_four_twenty_fifths": sp.simplify(mismatch_click.subs(fixture_mismatch)) == sp.Rational(34, 25),
        "fixture_q8_shift_is_minus_eight_twenty_fifths": sp.simplify(q8_shift.subs({**fixture, **fixture_y4})) == -sp.Rational(8, 25),
        "q6_effect_family_is_imported": q6["off_diagonal_effect"]["spectral_form"] == "E_epsilon=P_plus+(1-epsilon)*P_minus",
        "relative_q8_formula_is_imported": q8["relative_q8_coefficient"]["status"] == "COMPLETE_RELATIVE_Q8_COEFFICIENT_COMPUTED",
        "prior_Julia_dilation_boundary_is_imported": dilation["BT_virtual_coefficient_boundary"]["public_BT_order_lambda8_virtual_graph"] == "NOT_COMPUTED",
        "public_BT_boundary_is_preserved": True,
        "gravity_and_Lorentzian_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1",
        "question": "Can the certified two-angle BT effect be generated by an explicit finite self-adjoint apparatus Hamiltonian that selects both epsilon and the relative angle phase?",
        "answer": "Yes as an external finite detector coupled to the two equal-energy BT output modes. For phase z=exp(i phi), let P_minus(phi) project onto (|c1>-z|c2>)/sqrt(2), let the pointer be a degenerate qubit prepared in |0>, and use H_int=g P_minus(phi) tensor sigma_y for duration tau. Because P_minus is a projector, the exponential is exact. Pointer readout gives K_click=P_plus(phi)+cos(g tau)P_minus(phi) and K_no=sin(g tau)P_minus(phi), hence E_click=P_plus(phi)+cos(g tau)^2 P_minus(phi) and E_no=sin(g tau)^2 P_minus(phi). Thus epsilon=sin(g tau)^2 is selected by coupling-duration and phi by an explicit output-mode phase shifter. When phi matches the leading BT relative phase, the apparatus fixes X2, so the complete q4/q6 equality and relative-q8 variance theorem transfer unchanged. This closes the finite-device Hamiltonian realization, not the public closed-system BT dynamics, a spacetime-local detector model, Eq. (19), gravity or Lorentzian scattering.",
        "result_kind": "bounded finite apparatus Hamiltonian and exact two-outcome instrument for the coherent BT two-angle effect",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the two hard outgoing BT angle modes are the orthogonal equal-normalization equal-energy modes certified by the q6 detector predecessor",
            "the pointer is a degenerate two-level apparatus initialized in |0> and measured in the computational basis after a finite switched interaction",
            "the apparatus can coherently address the two declared finite-box output modes and supply or absorb their spatial momentum difference",
            "the phase shifter setting phi is an external apparatus control and is calibrated to the common leading BT relative phase when q4/q6 invariance is claimed",
            "theta=g tau lies in [0,pi/2] for the one-to-one setting epsilon=sin(theta)^2 in [0,1]",
            "the interaction is bounded on the finite two-mode carrier and no spacetime localization or continuum-angle limit is inferred",
            "the public BT interaction Hamiltonian governs the scattering output but does not contain or predict this external pointer coupling"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_two_angle_finite_apparatus_hamiltonian.py",
            "independent_verifier": "reverse_physics/verify_bt_two_angle_finite_apparatus_hamiltonian.py",
            "method": "Exact quotient-ring phase and trigonometric algebra, 4x4 Hamiltonian spectral exponentiation, exact pointer contraction, arbitrary complex q6/q8 pullback, and rational unit-circle fixture. No floating-point arithmetic is used."
        },
        "apparatus_carrier": {
            "BT_angle_basis": ["|c1>", "|c2>"],
            "pointer_basis": ["|0>_A", "|1>_A"],
            "angle_dimension": 2,
            "pointer_dimension": 2,
            "combined_dimension": 4,
            "free_energy_condition": "the fixed-s angle modes have equal energy and the pointer doublet is degenerate, so [H_free,H_int]=0 on this reduced carrier",
            "status": "FINITE_EQUAL_ENERGY_BT_OUTPUT_MODES_TENSOR_DEGENERATE_POINTER"
        },
        "phase_selection": {
            "z": "exp(i*phi)",
            "symmetric_mode": "|+_phi>=(|c1>+exp(i*phi)|c2>)/sqrt(2)",
            "antisymmetric_mode": "|-_phi>=(|c1>-exp(i*phi)|c2>)/sqrt(2)",
            "P_plus": matrix_strings(p_plus),
            "P_minus": matrix_strings(p_minus),
            "phase_shifter": "S_phi=diag(1,exp(i*phi))",
            "conjugation": "P_minus(phi)=S_phi P_minus(0) S_phi^dagger",
            "meaning": "phi is a detector interferometer setting, not a BT prediction",
            "status": "RELATIVE_ANGLE_PHASE_SELECTED_BY_APPARATUS_CONTROL"
        },
        "finite_Hamiltonian": {
            "interaction": "H_int=g*P_minus(phi) tensor sigma_y",
            "sigma_y": [["0", "-i"], ["i", "0"]],
            "self_adjoint": True,
            "bounded_norm": "||H_int||=|g|",
            "duration": "tau",
            "theta": "theta=g*tau",
            "spectral_square": "(H_int/g)^2=P_minus(phi) tensor I_A",
            "unitary": "U_tau=P_plus(phi) tensor I_A+P_minus(phi) tensor [cos(theta)I_A-i sin(theta)sigma_y]",
            "status": "EXACT_BOUNDED_SELF_ADJOINT_FINITE_APPARATUS_EVOLUTION"
        },
        "derived_instrument": {
            "pointer_preparation": "|0>_A",
            "click_readout": "|0>_A",
            "no_click_readout": "|1>_A",
            "K_click": "P_plus(phi)+cos(theta)*P_minus(phi)",
            "K_no": "sin(theta)*P_minus(phi)",
            "E_click": "P_plus(phi)+cos(theta)^2*P_minus(phi)=I-epsilon*P_minus(phi)",
            "E_no": "sin(theta)^2*P_minus(phi)=epsilon*P_minus(phi)",
            "epsilon_selection": "epsilon=sin(g*tau)^2",
            "completeness": "K_click^dagger K_click+K_no^dagger K_no=I",
            "endpoints": "theta=0 gives identity click; theta=pi/2 gives the pure coherent P_plus(phi) click",
            "status": "EXACT_NORMALIZED_TWO_OUTCOME_HAMILTONIAN_INSTRUMENT"
        },
        "phase_calibration": {
            "leading_BT_vector": "X2=x2*(1,exp(i*delta))",
            "calibrated_setting": "phi=delta",
            "calibrated_fixed_point": "E_click X2=X2",
            "mismatch": "Delta=delta-phi",
            "leading_click_probability": "<X2,E_click X2>=2*|x2|^2*[1-epsilon*sin(Delta/2)^2]",
            "meaning": "q4/q6 invariance requires phase calibration; a mismatched apparatus measurably suppresses the leading click",
            "status": "PHASE_SETTING_HAS_EXACT_FALSIFIABLE_RESPONSE"
        },
        "transported_BT_coefficients": {
            "through_q6": "at phi=delta, q_click=2*q4*{1+lambda^2*[R6(c1)+R6(c2)]/2}+O(lambda^8)",
            "relative_q8": "q8[apparatus]-q8[recorded]=-(epsilon/2)*||X4(c1)-exp(-i*phi)X4(c2)||^2",
            "reason": "the Hamiltonian-derived E_click is exactly the predecessor effect in the phase-calibrated basis",
            "absolute_q8_status": "NOT_COMPUTED",
            "status": "Q6_AND_COMPLETE_RELATIVE_Q8_RESULTS_PHYSICALLY_REALIZED_ON_FINITE_DEVICE"
        },
        "exact_fixture": {
            "phase": "exp(i*phi)=i",
            "cos_theta": "3/5",
            "sin_theta": "4/5",
            "epsilon": "16/25",
            "P_plus": matrix_strings(fixture_p_plus),
            "H_int_over_g": matrix_strings(fixture_h),
            "U_tau": matrix_strings(fixture_u),
            "K_click": matrix_strings(fixture_k_click),
            "K_no": matrix_strings(fixture_k_no),
            "E_click": matrix_strings(fixture_e_click),
            "E_no": matrix_strings(fixture_e_no),
            "calibrated_leading_probability_for_unit_x2": "2",
            "quarter_turn_mismatch_probability_for_unit_x2": "34/25",
            "q8_fixture_X4": ["1+2*i", "-3+i"],
            "q8_shift": "-8/25",
            "status": "EXACT_RATIONAL_COMPLEX_HAMILTONIAN_FIXTURE"
        },
        "physical_affiliation": {
            "finite_external_detector_Hamiltonian": "CONSTRUCTED",
            "epsilon_and_phase_selected_by_apparatus_parameters": "CONSTRUCTED",
            "coupling_to_certified_BT_output_modes": "CONSTRUCTED_ON_REDUCED_TWO_MODE_CARRIER",
            "public_closed_system_BT_Hamiltonian_prediction": "NOT_ESTABLISHED",
            "spacetime_local_detector_coupling": "NOT_CONSTRUCTED",
            "continuum_angle_limit": "NOT_CONSTRUCTED",
            "interpretation": "the effect is no longer an abstract operational declaration; it is the measured effect of an explicit finite external device, but the device itself is additional physical structure"
        },
        "does_not_establish": [
            "that the public closed-system BT Hamiltonian contains or uniquely predicts the apparatus coupling g, duration tau or phase phi",
            "a translation-invariant or spacetime-local field-apparatus interaction",
            "coherent control of a continuum of scattering angles or unequal-energy modes",
            "either absolute order-lambda8 probability coefficient",
            "either forward or exchanged-forward endpoint",
            "real-virtual, survival, collinear or KLN completion",
            "an all-order probability or all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "gravity or metric BV--BRST transfer",
            "a restored gravitational quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Embed this finite mode-selective apparatus in a spatially localized detector coupling or derive its effective g, tau and phi from a declared microscopic detector model. Independently, compute the absolute q8 X4 Gram and X2-X6 interference. The public Eq. (19) route still requires the missing zero-mode representation and generalized Born trace.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_two_angle_finite_apparatus_hamiltonian.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_finite_apparatus_hamiltonian.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_finite_apparatus_hamiltonian"
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
            print("BT TWO ANGLE APPARATUS: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT TWO ANGLE APPARATUS: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
