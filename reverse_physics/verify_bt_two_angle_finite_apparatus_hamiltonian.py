#!/usr/bin/env python3
"""Fraction verifier for the finite two-angle BT apparatus Hamiltonian."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-finite-apparatus-hamiltonian-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
I = (Fraction(0), Fraction(1))


def cadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def cneg(value):
    return (-value[0], -value[1])


def cmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cconj(value):
    return (value[0], -value[1])


def cscale(value, scalar):
    return (value[0] * scalar, value[1] * scalar)


def matrix(rows, columns, fill=ZERO):
    return [[fill for _ in range(columns)] for _ in range(rows)]


def identity(size):
    result = matrix(size, size)
    for index in range(size):
        result[index][index] = ONE
    return result


def madd(left, right):
    return [
        [cadd(left[row][column], right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def mscale(scalar, value):
    return [[cscale(entry, scalar) for entry in row] for row in value]


def mmul(left, right):
    result = matrix(len(left), len(right[0]))
    for row in range(len(left)):
        for column in range(len(right[0])):
            value = ZERO
            for middle in range(len(right)):
                value = cadd(value, cmul(left[row][middle], right[middle][column]))
            result[row][column] = value
    return result


def dagger(value):
    return [
        [cconj(value[column][row]) for column in range(len(value))]
        for row in range(len(value[0]))
    ]


def kron(left, right):
    result = matrix(len(left) * len(right), len(left[0]) * len(right[0]))
    for left_row in range(len(left)):
        for left_column in range(len(left[0])):
            for right_row in range(len(right)):
                for right_column in range(len(right[0])):
                    result[left_row * len(right) + right_row][left_column * len(right[0]) + right_column] = cmul(
                        left[left_row][left_column], right[right_row][right_column]
                    )
    return result


def matvec(value, vector):
    return [
        sum_complex(cmul(entry, component) for entry, component in zip(row, vector))
        for row in value
    ]


def sum_complex(values):
    result = ZERO
    for value in values:
        result = cadd(result, value)
    return result


def inner(left, right):
    return sum_complex(cmul(cconj(lhs), rhs) for lhs, rhs in zip(left, right))


def projector_pair(z):
    half = Fraction(1, 2)
    p_plus = [
        [cscale(ONE, half), cscale(cconj(z), half)],
        [cscale(z, half), cscale(ONE, half)],
    ]
    p_minus = madd(identity(2), mscale(Fraction(-1), p_plus))
    return p_plus, p_minus


def apparatus(z, cosine, sine):
    p_plus, p_minus = projector_pair(z)
    sigma_y = [[ZERO, cneg(I)], [I, ZERO]]
    rotation = madd(mscale(cosine, identity(2)), mscale(sine, [[ZERO, (-1, 0)], [ONE, ZERO]]))
    h = kron(p_minus, sigma_y)
    unitary = madd(kron(p_plus, identity(2)), kron(p_minus, rotation))
    k_click = [
        [unitary[2 * row][2 * column] for column in range(2)] for row in range(2)
    ]
    k_no = [
        [unitary[2 * row + 1][2 * column] for column in range(2)] for row in range(2)
    ]
    e_click = mmul(dagger(k_click), k_click)
    e_no = mmul(dagger(k_no), k_no)
    return p_plus, p_minus, h, unitary, k_click, k_no, e_click, e_no


def norm_square(value):
    result = inner(value, value)
    assert result[1] == 0
    return result[0]


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessors = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )
    q6 = next(
        row for row in predecessors if row["certificate"].endswith("TWO_ANGLE_COHERENT_Q6_DETECTOR_V1")
    )
    q8 = next(
        row for row in predecessors if row["certificate"].endswith("TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1")
    )
    dilation = next(
        row for row in predecessors if row["certificate"].endswith("COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1")
    )

    phases = [
        ONE,
        I,
        (-1, 0),
        (Fraction(3, 5), Fraction(4, 5)),
    ]
    rotations = [
        (Fraction(1), Fraction(0)),
        (Fraction(3, 5), Fraction(4, 5)),
        (Fraction(5, 13), Fraction(12, 13)),
        (Fraction(0), Fraction(1)),
    ]
    y_values = [
        (Fraction(1), Fraction(2)),
        (Fraction(-3), Fraction(1)),
        (Fraction(7, 4), Fraction(-2, 3)),
    ]
    all_projectors = True
    all_hamiltonians = True
    all_unitaries = True
    all_kraus = True
    all_effects = True
    all_calibrated = True
    all_mismatch = True
    all_q8 = True
    for z, (cosine, sine) in itertools.product(phases, rotations):
        p_plus, p_minus, h, unitary, k_click, k_no, e_click, e_no = apparatus(
            z, cosine, sine
        )
        all_projectors &= (
            mmul(p_plus, p_plus) == p_plus
            and mmul(p_minus, p_minus) == p_minus
            and mmul(p_plus, p_minus) == matrix(2, 2)
            and madd(p_plus, p_minus) == identity(2)
        )
        all_hamiltonians &= (
            dagger(h) == h
            and mmul(h, h) == kron(p_minus, identity(2))
        )
        all_unitaries &= mmul(dagger(unitary), unitary) == identity(4)
        all_kraus &= (
            k_click == madd(p_plus, mscale(cosine, p_minus))
            and k_no == mscale(sine, p_minus)
        )
        all_effects &= (
            e_click == madd(p_plus, mscale(cosine * cosine, p_minus))
            and e_no == mscale(sine * sine, p_minus)
            and madd(e_click, e_no) == identity(2)
        )
        leading = [ONE, z]
        all_calibrated &= matvec(e_click, leading) == leading
        for w in phases:
            mismatch = [ONE, w]
            actual = inner(mismatch, matvec(e_click, mismatch))
            phase_dot = cmul(cconj(z), w)[0]
            expected = Fraction(2) - sine * sine * (Fraction(1) - phase_dot)
            all_mismatch &= actual == (expected, Fraction(0))
        for y1, y2 in itertools.product(y_values, repeat=2):
            y = [y1, y2]
            shift = inner(y, matvec(madd(e_click, mscale(Fraction(-1), identity(2))), y))
            phase_difference = cadd(y1, cneg(cmul(cconj(z), y2)))
            expected_shift = -sine * sine * norm_square([phase_difference]) / 2
            all_q8 &= shift == (expected_shift, Fraction(0))

    fixture_expected = {
        "P_plus": [["1/2", "-I/2"], ["I/2", "1/2"]],
        "K_click": [["4/5", "-I/5"], ["I/5", "4/5"]],
        "K_no": [["2/5", "2*I/5"], ["-2*I/5", "2/5"]],
        "E_click": [["17/25", "-8*I/25"], ["8*I/25", "17/25"]],
        "E_no": [["8/25", "8*I/25"], ["-8*I/25", "8/25"]],
    }
    fixture = certificate["exact_fixture"]
    instrument = certificate["derived_instrument"]
    phase_selection = certificate["phase_selection"]
    phase = certificate["phase_calibration"]
    transport = certificate["transported_BT_coefficients"]
    affiliation = certificate["physical_affiliation"]
    scope = certificate["does_not_establish"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1",
        "input_hashes_recomputed": hashes_ok,
        "three_predecessor_pass_flags_rechecked": len(predecessors) == 3 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-finite-apparatus-hamiltonian"),
        "four_unit_circle_phases_checked": len(phases) == 4 and all(norm_square([row]) == 1 for row in phases),
        "four_Pythagorean_rotations_checked": len(rotations) == 4 and all(c * c + s * s == 1 for c, s in rotations),
        "projector_algebra_recomputed": all_projectors,
        "recorded_phase_projectors_match": phase_selection["P_plus"] == [["1/2", "(c_phi - I*s_phi)/2"], ["(c_phi + I*s_phi)/2", "1/2"]] and phase_selection["P_minus"] == [["1/2", "-(c_phi - I*s_phi)/2"], ["-(c_phi + I*s_phi)/2", "1/2"]],
        "Hamiltonian_self_adjointness_and_square_recomputed": all_hamiltonians,
        "spectral_unitaries_recomputed": all_unitaries,
        "pointer_Kraus_maps_recomputed": all_kraus,
        "effect_completeness_recomputed": all_effects,
        "calibrated_leading_modes_fixed": all_calibrated,
        "phase_mismatch_formula_recomputed": all_mismatch,
        "phase_covariant_q8_shift_recomputed": all_q8,
        "epsilon_selection_recorded": instrument["epsilon_selection"] == "epsilon=sin(g*tau)^2",
        "Kraus_claims_recorded": instrument["K_click"] == "P_plus(phi)+cos(theta)*P_minus(phi)" and instrument["K_no"] == "sin(theta)*P_minus(phi)",
        "effects_recorded": instrument["E_click"].endswith("I-epsilon*P_minus(phi)") and instrument["E_no"].endswith("epsilon*P_minus(phi)"),
        "phase_calibration_recorded": phase["calibrated_setting"] == "phi=delta" and phase["calibrated_fixed_point"] == "E_click X2=X2",
        "mismatch_response_recorded": phase["leading_click_probability"] == "<X2,E_click X2>=2*|x2|^2*[1-epsilon*sin(Delta/2)^2]",
        "q6_transport_recorded": transport["through_q6"].startswith("at phi=delta, q_click=2*q4"),
        "q8_transport_recorded": transport["relative_q8"] == "q8[apparatus]-q8[recorded]=-(epsilon/2)*||X4(c1)-exp(-i*phi)X4(c2)||^2",
        "absolute_q8_remains_open": transport["absolute_q8_status"] == "NOT_COMPUTED",
        "fixture_core_matrices_match": all(fixture[key] == value for key, value in fixture_expected.items()),
        "fixture_scalar_responses_match": fixture["epsilon"] == "16/25" and fixture["calibrated_leading_probability_for_unit_x2"] == "2" and fixture["quarter_turn_mismatch_probability_for_unit_x2"] == "34/25" and fixture["q8_shift"] == "-8/25",
        "q6_input_effect_rechecked": q6["off_diagonal_effect"]["status"] == "POSITIVE_NORMALIZED_GENUINELY_OFF_DIAGONAL_ANGLE_EFFECT",
        "q8_input_relative_status_rechecked": q8["relative_q8_coefficient"]["status"] == "COMPLETE_RELATIVE_Q8_COEFFICIENT_COMPUTED",
        "Julia_input_public_boundary_rechecked": dilation["BT_virtual_coefficient_boundary"]["public_BT_order_lambda8_virtual_graph"] == "NOT_COMPUTED",
        "finite_external_affiliation_is_precise": affiliation["finite_external_detector_Hamiltonian"] == "CONSTRUCTED" and affiliation["public_closed_system_BT_Hamiltonian_prediction"] == "NOT_ESTABLISHED",
        "spacetime_and_continuum_remain_open": affiliation["spacetime_local_detector_coupling"] == "NOT_CONSTRUCTED" and affiliation["continuum_angle_limit"] == "NOT_CONSTRUCTED",
        "Eq19_boundary_present": any("Eq. (19)" in row for row in scope),
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
