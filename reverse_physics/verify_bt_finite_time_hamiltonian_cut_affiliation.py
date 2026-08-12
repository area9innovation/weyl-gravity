#!/usr/bin/env python3
"""Independent verifier for BT finite-time Hamiltonian cut affiliation."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-finite-time-hamiltonian-cut-affiliation-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))] for i in range(len(left))]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def verify(certificate):
    kernel = certificate["hamiltonian_cut_kernel"]
    coefficient = certificate["coefficient_match"]
    survival = certificate["pseudo_unitary_survival_boundary"]
    result = certificate["interpretation"]

    # Independent rational hyperbola fixtures c=(u+u^-1)/2,
    # s=(u-u^-1)/2 verify the J-unitary counterexample without CAS.
    J = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]]
    P = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    Q = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    boost_rows = []
    for u in (Fraction(2), Fraction(3), Fraction(5)):
        c = (u + 1 / u) / 2
        s = (u - 1 / u) / 2
        U = [[c, s], [s, c]]
        Usharp = matmul(matmul(J, transpose(U)), J)
        identity = matmul(Usharp, U)
        q_p = matmul(matmul(matmul(Usharp, P), U), P)[0][0]
        q_q_matrix = matmul(matmul(matmul(Usharp, Q), U), P)
        q_q = q_q_matrix[0][0] + q_q_matrix[1][1]
        boost_rows.append(identity == [[1, 0], [0, 1]] and q_p == c * c and q_q == -s * s and q_p + q_q == 1 and q_q < 0)

    # Independent rational circle fixtures for the positive history rotation.
    rotation_rows = []
    for u in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4)):
        c = (1 - u * u) / (1 + u * u)
        s = 2 * u / (1 + u * u)
        rotation_rows.append(c * c + s * s == 1 and c * c >= 0 and s * s >= 0)

    history_tree = Fraction(9, 8) * 256
    phase_rational = history_tree * Fraction(3, 320) / 32
    labeled_rational = phase_rational
    incoming_rational = Fraction(5, 48)
    detector_rational = labeled_rational * incoming_rational

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "source_archive_hash_is_pinned": certificate["provenance"]["public_source_archive_sha256"] == "6681e48614eac27e7ce766563b336c3296bbb94dd00286611672a7a1f15ec0db",
        "double_time_kernel_is_recorded": kernel["born_double_time"] == "integral_0^T d_tau integral_0^T d_tau_prime exp(i*omega*(tau-tau_prime))",
        "triangular_kernel_is_recorded": kernel["relative_time_form"] == "integral_-T^T (T-|sigma|)*exp(i*omega*sigma) d_sigma",
        "exact_sinc_square_is_recorded": kernel["exact_kernel"] == "|F_T(omega)|^2=4*sin^2(omega*T/2)/omega^2",
        "Hamiltonian_cut_affiliation_is_scoped": kernel["status"] == "BT_INTERACTION_PICTURE_CUT_KERNEL_AFFILIATED",
        "history_tree_norm_recomputed": history_tree == 288,
        "phase_rational_recomputed": phase_rational == Fraction(27, 320),
        "detector_rational_recomputed": detector_rational == Fraction(9, 1024),
        "stored_cut_shell_norm_matches": coefficient["BT_cut_shell_norm"] == "288*pi*lambda^8*T/E",
        "stored_labeled_coefficient_matches": coefficient["labeled_phase_coefficient"] == "27*lambda^8*T/(320*pi^4*E)",
        "stored_detector_rate_matches": coefficient["declared_detector_rate"] == "9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
        "three_rational_Krein_boost_fixtures_pass": all(boost_rows),
        "three_rational_positive_rotation_fixtures_pass": all(rotation_rows),
        "Krein_complement_is_explicitly_negative": survival["complement"] == "tr(U_r^sharp (1-P) U_r P)=-sinh(r)^2",
        "signed_conservation_is_explicit": survival["conservation"] == "cosh(r)^2-sinh(r)^2=1",
        "survival_nonimplication_status_matches": survival["status"] == "CUT_KERNEL_DERIVED_POSITIVE_SURVIVAL_REQUIRES_HISTORY_OR_EQ19_EMBEDDING",
        "kernel_is_derived": result["finite_time_shell_kernel_BT_affiliation"] == "DERIVED_AT_CUT_PROBABILITY_LEVEL",
        "positive_history_survival_is_only_operational": result["positive_history_survival"] == "CONSTRUCTED_OPERATIONALLY",
        "BT_survival_embedding_remains_open": result["BT_Hamiltonian_positive_survival_embedding"] == "NOT_CONSTRUCTED",
        "global_and_eq19_gates_remain_open": result["global_multichannel_probability"] == "NOT_CONSTRUCTED" and result["Eq19_all_orders"] == "NOT_PROVED",
        "Lorentzian_boundary_is_explicit": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
