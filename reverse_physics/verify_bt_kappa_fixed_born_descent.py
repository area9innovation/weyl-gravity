#!/usr/bin/env python3
"""Independent verifier for the BT kappa-fixed Born descent."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
EXPECTED_SOURCE = "93a5b506545f3079ab63cb7890dce05c447d04fd"
EXPECTED_INPUTS = [
    "planning/work-items/reverse-physics-bateman-kappa-fixed-born-descent.json",
    "planning/events/reverse-physics-bateman-kappa-fixed-born-descent-DONE-93a5b506.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1.json",
]


def sha256(relative):
    digest = hashlib.sha256()
    try:
        with open(os.path.join(ROOT, relative), "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def load(relative):
    try:
        with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def matrix(value):
    try:
        result = [[Fraction(entry) for entry in row] for row in value]
    except (TypeError, ValueError, ZeroDivisionError):
        return []
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        return []
    return result


def transpose(value):
    return [list(row) for row in zip(*value)] if value else []


def multiply(left, right):
    if not left or not right or len(left[0]) != len(right):
        return []
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def add(left, right):
    if not left or len(left) != len(right) or len(left[0]) != len(right[0]):
        return []
    return [[a + b for a, b in zip(x, y)] for x, y in zip(left, right)]


def scale(factor, value):
    return [[factor * entry for entry in row] for row in value]


def trace(value):
    return sum((value[i][i] for i in range(len(value))), Fraction(0))


def alpha(value, kappa):
    return multiply(multiply(kappa, value), kappa)


def hilbert_square(value):
    return trace(multiply(transpose(value), value))


def krein_square(value, kappa):
    sharp = multiply(multiply(kappa, transpose(value)), kappa)
    return trace(multiply(sharp, value))


def verify(certificate):
    checks = {}
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-kappa-fixed-born-descent-v1.schema.json"
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["source"] = provenance.get("source_commit") == EXPECTED_SOURCE
    checks["input_paths"] = [row.get("path") for row in inputs] == EXPECTED_INPUTS
    checks["input_hashes"] = len(inputs) == len(EXPECTED_INPUTS) and all(
        row.get("sha256") == sha256(path) for row, path in zip(inputs, EXPECTED_INPUTS)
    )
    checks["producer"] = provenance.get("generated_by") == "reverse_physics/bt_kappa_fixed_born_descent.py"
    checks["verifier"] = provenance.get("independent_verifier") == "reverse_physics/verify_bt_kappa_fixed_born_descent.py"

    positive = load(EXPECTED_INPUTS[3])
    detector = load(EXPECTED_INPUTS[4])
    pointer = load(EXPECTED_INPUTS[5])
    checks["predecessors"] = all(row.get("checks", {}).get("ok") for row in (positive, detector, pointer))
    weak = positive.get("weak_ghost_Born_separation", {})
    checks["weak_public_weight"] = weak.get("generalized_Krein_Born_weight") == "2"
    checks["weak_Hilbert_weight"] = weak.get("ordinary_Hilbert_Born_weight") == "3"

    theorem = certificate.get("canonical_expectation_theorem", {})
    checks["automorphism"] = theorem.get("automorphism") == "alpha(A)=kappa A kappa, alpha^2=id"
    checks["decomposition"] = "A_even=" in theorem.get("decomposition", "") and "A_odd=" in theorem.get("decomposition", "")
    checks["positive_adjoint"] = "A*=kappa A^sharp kappa" in theorem.get("positive_adjoint", "")
    checks["orthogonality"] = "=0" in theorem.get("orthogonality", "")
    checks["difference_formula"] = theorem.get("public_Born_identity") == "q_K(A)=Tr(A^sharp A)=||A_even||_2^2-||A_odd||_2^2"
    checks["expectation"] = all(term in theorem.get("expectation", "") for term in ("E_kappa", "completely positive", "idempotent"))
    checks["defect"] = theorem.get("weight_defect") == "q_K(E_kappa(A))-q_K(A)=||A_odd||_2^2"
    checks["iff"] = all(term in theorem.get("iff", "") for term in ("iff A_odd=0", "alpha(A)=A"))
    checks["theorem_status"] = theorem.get("status") == "CANONICAL_EXPECTATION_CLASSIFIED_WITH_EXACT_BORN_PRESERVATION_CRITERION"

    witness = certificate.get("exact_rational_witness", {})
    kappa = matrix(witness.get("kappa", []))
    a = matrix(witness.get("A", []))
    even = matrix(witness.get("A_even", []))
    odd = matrix(witness.get("A_odd", []))
    recomputed_even = scale(Fraction(1, 2), add(a, alpha(a, kappa))) if a and kappa else []
    recomputed_odd = scale(Fraction(1, 2), add(a, scale(Fraction(-1), alpha(a, kappa)))) if a and kappa else []
    checks["kappa"] = multiply(kappa, kappa) == [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    checks["witness_split"] = even == recomputed_even and odd == recomputed_odd and add(even, odd) == a
    checks["witness_parities"] = alpha(even, kappa) == even and alpha(odd, kappa) == scale(Fraction(-1), odd)
    checks["witness_cross"] = trace(multiply(transpose(even), odd)) == 0
    q = krein_square(a, kappa)
    he = hilbert_square(even)
    ho = hilbert_square(odd)
    qe = krein_square(even, kappa)
    checks["witness_values"] = (q, he, ho, qe) == (Fraction(20), Fraction(25), Fraction(5), Fraction(25))
    checks["witness_record"] = [witness.get(key) for key in (
        "q_K_A", "Hilbert_square_even", "Hilbert_square_odd", "q_K_E_kappa_A", "weight_defect"
    )] == ["20", "25", "5", "25", "5"]
    checks["witness_status"] = witness.get("status") == "NONZERO_ODD_REMAINDER_CHANGES_WEIGHT_EXACTLY_BY_ITS_POSITIVE_HILBERT_SQUARE"

    remainder = certificate.get("weak_ghost_remainder_disposition", {})
    checks["remainder_fixture"] = "B=I" in remainder.get("imported_fixture", "") and "Q=E21" in remainder.get("imported_fixture", "")
    checks["remainder_obstruction"] = "cannot be removed" in remainder.get("expectation_consequence", "")
    checks["Eq19_boundary"] = "must first show" in remainder.get("Eq19_consequence", "")
    checks["remainder_status"] = remainder.get("status") == "GENERAL_NONFIXED_REMAINDER_DESCENT_OBSTRUCTED"

    selected = certificate.get("selected_pointer_descent", {})
    symmetries = selected.get("symmetries", [])
    checks["four_symmetries"] = len(symmetries) == 4 and all("kappa_total" in row for row in symmetries)
    checks["transition_fixed"] = "alpha(A_g)=A_g" in selected.get("transition", "")
    checks["adjoints_agree"] = selected.get("adjoints") == "A_g^sharp=A_g*"
    checks["effects_agree"] = selected.get("public_effect") == "A_g^sharp A_g=sin^2(g|K|)" and selected.get("positive_Hilbert_effect") == "A_g* A_g=sin^2(g|K|)"
    checks["probability_identity"] = "for every trace-class selected input rho" in selected.get("probability_identity", "")
    checks["pair_intertwining_record"] = selected.get("selected_pair_map_kappa_intertwining") == "M kappa_in=kappa_out M"
    pair = detector.get("charge_balanced_pointer", {})
    m = matrix(pair.get("pair_map", []))
    kin = matrix(pair.get("three_particle_kappa", []))
    kout = matrix(pair.get("pointer_spectator_kappa", []))
    checks["pair_intertwining_exact"] = multiply(m, kin) == multiply(kout, m) and any(any(row) for row in m)
    checks["pointer_predecessor_symmetry"] = "kappa_total V kappa_total=V" in pair.get("operator_identities", [])
    checks["pointer_effect_import"] = pointer.get("local_functional_calculus", {}).get("effects", [])[:1] == ["E_click(g)=sin^2(g|K|)"]
    checks["q8"] = selected.get("strict_bound") == "Q8_aux,compact/q4_bar>1/18874368000"
    checks["selected_status"] = selected.get("status") == "SELECTED_LOCAL_POINTER_PROCESS_HAS_OPERATOR_LEVEL_COMMON_BORN_DESCENT"

    disposition = certificate.get("disposition", {})
    checks["selected_physical"] = disposition.get("selected_pointer_public_vs_Hilbert_Born_equivalence") == "PROVED_AT_OPERATOR_LEVEL" and disposition.get("selected_q8_public_auxiliary_physical_coefficient") == "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE"
    checks["general_not_promoted"] = disposition.get("arbitrary_weak_ghost_process_equivalence") == "NOT_ESTABLISHED" and disposition.get("general_Eq19") == "NOT_PROVED"
    checks["Lorentzian_not_promoted"] = disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 11
    checks["missing"] = len(certificate.get("missing_object_ledger", [])) == 5
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("lambda10", "multi-channel", "alpha(A)=A"))
    checks["commands"] = len(certificate.get("verification_commands", [])) == 3
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-kappa-fixed-born-descent.md"
    return checks


def main():
    with open(CERT, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate)
    failed = [name for name, value in checks.items() if not value]
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    if failed:
        print("failures: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
