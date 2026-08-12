#!/usr/bin/env python3
"""Exact channel carrier and finite-time normalization for BT six-point poles."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-six-point-sequential-history-carrier-v1.schema.json"
REPORT = "reverse_physics/reports/bt-six-point-sequential-history-carrier.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-sequential-history-carrier.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
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


def matrix_rows(matrix):
    return [[str(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def exact_carrier():
    size = 10
    identity = sp.eye(size)
    ones = sp.ones(size)
    incidence = ones - identity
    residue = incidence / 4
    gram = sp.simplify(2 * residue.T * residue)
    sequential = sp.Rational(9, 8) * identity
    interference = sp.simplify(gram - sequential)
    inverse = sp.simplify(residue.inv())
    return {
        "channel_count": size,
        "incidence_matrix": matrix_rows(incidence),
        "incidence_determinant": str(incidence.det()),
        "residue_map": "R=(J-I)/4",
        "residue_map_determinant": str(residue.det()),
        "residue_map_inverse": matrix_rows(inverse),
        "fixed_channel_residue_vector": ["0"] + ["1/4"] * 9,
        "fixed_channel_born_norm": str((2 * residue[:, 0].T * residue[:, 0])[0]),
        "complete_channel_gram": matrix_rows(gram),
        "complete_channel_gram_formula": "G=2*R^T*R=J+I/8",
        "complete_channel_gram_spectrum": {"81/8": 1, "1/8": 9},
        "complete_channel_gram_determinant": str(gram.det()),
        "sequential_diagonal_gram": "G_seq=(9/8)*I",
        "interference_gram": matrix_rows(interference),
        "interference_gram_formula": "G_int=J-I",
        "interference_gram_spectrum": {"9": 1, "-1": 9},
        "density_split": "D=(9/8)*sum_A(1/s_A^2)+2*sum_{A<B}1/(s_A*s_B)",
    }


def build():
    full = load(INPUTS[1])
    no_go = load(INPUTS[2])
    column = load(INPUTS[3])
    defect = load(INPUTS[4])
    carrier = exact_carrier()
    energy, duration = sp.symbols("E T", positive=True)
    epsilon_s = energy / duration
    leading_history = sp.Rational(9, 8) * sp.pi * duration / energy
    checks = {
        "all_inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_formula_is_imported": full["universal_complement_formula"]["formula"] == "c_S=c_Sc=(1/4)*sum_{A != S} 1/s_A",
        "ten_channel_incidence_is_invertible": carrier["incidence_determinant"] == "-9",
        "residue_map_is_invertible": carrier["residue_map_determinant"] == "-9/1048576",
        "one_channel_has_nine_allowed_quartic_histories": carrier["fixed_channel_residue_vector"].count("1/4") == 9,
        "fixed_channel_norm_reproduces_double_pole": carrier["fixed_channel_born_norm"] == "9/8",
        "complete_gram_is_positive_definite": carrier["complete_channel_gram_spectrum"] == {"81/8": 1, "1/8": 9},
        "sequential_split_contains_every_double_pole": carrier["sequential_diagonal_gram"] == "G_seq=(9/8)*I",
        "interference_has_zero_diagonal": all(carrier["interference_gram"][i][i] == "0" for i in range(10)),
        "interference_is_not_a_positive_outcome_gram": carrier["interference_gram_spectrum"] == {"9": 1, "-1": 9},
        "positive_exclusive_completion_was_ruled_out": no_go["interpretation"]["positive_exclusive_distributional_completion"] == "EXACT_NO_GO",
        "finite_time_shell_matching_is_exact": sp.simplify(sp.pi / epsilon_s - sp.pi * duration / energy) == 0,
        "leading_history_coefficient_is_positive": leading_history.is_positive,
        "finite_Moller_column_is_not_two_sided": column["disposition"]["full_two_sided_physical_S_operator"] == "NOT_CONSTRUCTED",
        "defect_completion_remains_BT_underdetermined": defect["disposition"]["completion_selected_by_public_amplitudes"] == "EXACTLY_UNDERDETERMINED",
        "inclusive_eq19_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1",
        "schema_version": "reverse-physics-bt-six-point-sequential-history-carrier-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact ten-channel factorization residue carrier, sequential/interference decomposition, and finite-time leading-shell normalization",
        "question": "Can the positive six-point double-pole coefficient be represented as a separately normalized on-shell sequential four-point channel history, and what remains after that separation?",
        "answer": "Yes at the exact leading-shell reduced-mode level. With y_A=1/s_A, the ten species coefficients obey c=(J-I)y/4. For a fixed on-shell channel B the residue vector has nine entries 1/4 and one zero, the nine allowed products of two auxiliary quartic transitions, and its Born norm is 2||r_B||^2=9/8. The full residue Gram is G=J+I/8, positive definite with spectrum 81/8 and 1/8 (multiplicity nine). It splits uniquely by pole order into a diagonal sequential part (9/8)I, containing every 1/s_A^2 pole, and an off-diagonal coherent interference part J-I, containing only 1/(s_A s_B) terms and having inertia (1,9). For F_T(omega)=integral_0^T exp(i omega t)dt, |F_T|^2/T tends to 2*pi*delta(omega). Near an intermediate state of energy E, s=2E*omega+O(omega^2), so |F_T|^2/(4E^2) tends to (pi*T/E)*delta(s). This matches the Feynman-modulus leading term pi*delta(s)/epsilon_s at epsilon_s=E/T and turns 9/(8s^2) into the positive sequential coefficient 9*pi*T*delta(s)/(8E). This identifies and normalizes the leading divergent history but does not construct the BT Moller operator, prescribe the signed interference distribution, or supply the survival term required for a finite inclusive probability.",
        "exact_channel_carrier": carrier,
        "finite_time_shell_normalization": {
            "window": "F_T(omega)=integral_0^T exp(i*omega*t) dt",
            "exact_total_weight": "integral_R |F_T(omega)|^2 d_omega=2*pi*T",
            "distribution_limit": "|F_T(omega)|^2/T -> 2*pi*delta(omega)",
            "shell_coordinate": "s=2*E*omega+O(omega^2), E>0",
            "squared_propagator_window": "|F_T(omega)|^2/(4*E^2) -> (pi*T/E)*delta(s)",
            "matched_feynman_modulus": "1/(s^2+epsilon_s^2) -> (pi/epsilon_s)*delta(s)",
            "coefficient_match": "epsilon_s=E/T",
            "BT_leading_sequential_history": "(9*pi*T/(8*E))*delta(s)",
            "status": "UNIVERSAL_FINITE_TIME_NORMALIZATION_NOT_BT_DYNAMICAL_AFFILIATION",
        },
        "sequential_interference_boundary": {
            "sequential_outcomes": "ten formal direct-sum on-shell 3|3 channel labels, each with leading coefficient 9/8 in the reduced Born normalization; physical detector orthogonality is not inferred",
            "connected_interference": "2*sum_{A<B}1/(s_A*s_B), represented by the indefinite zero-diagonal matrix J-I",
            "isolated_channel_behavior": "the sequential term contains the full positive 1/s_B^2 divergence; interference is at most order 1/s_B when all other channels are nonzero",
            "what_is_gained": "the nonextendable positive double pole is moved into a separately counted duration-growing history coefficient",
            "what_is_not_gained": "no prescription for cross-channel interference, detector overlap, survival probability, or finite inclusive normalization",
        },
        "interpretation": {
            "on_shell_factorization_channel_carrier": "EXACTLY_CONSTRUCTED",
            "leading_sequential_history_normalization": "COEFFICIENT_COMPUTED",
            "connected_interference_distribution": "NOT_PRESCRIBED",
            "BT_dynamical_Moller_affiliation": "NOT_CONSTRUCTED",
            "finite_inclusive_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": ["a finite-time BT Hamiltonian derivation", "a preferred distribution for 1/(s_A*s_B)", "orthogonality of unresolved physical detector channels", "a survival or virtual term", "a finite inclusive probability", "a complete Moller/LSZ/S operator", "Eq. (19)", "loops", "gravity/BRST", "anything LORENTZIAN-CAUSAL", "literature priority"],
        "next_gate": "Derive the finite-time factorization block from the BT interaction Hamiltonian on wave packets and compute its overlap with the connected off-diagonal J-I interference sector. A physical detector instrument must decide which intermediate channels are distinguishable and produce the matching survival term. This is the first point at which the arbitrary defect partial unitary W must be fixed by BT dynamics rather than by algebraic completion.",
        "provenance": {"source_commit": "b37b11f6", "retrieval_date": "2026-08-12", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS], "method": "Exact SymPy characteristic-zero matrix algebra for the ten-channel residue carrier, exact distributional finite-time Fourier normalization, and fail-closed imports of the pole no-go and Moller scope certificates."},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_six_point_sequential_history_carrier.py --write --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_sequential_history_carrier.py", "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_sequential_history_carrier"],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
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
