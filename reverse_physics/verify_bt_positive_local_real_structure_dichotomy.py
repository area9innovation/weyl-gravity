#!/usr/bin/env python3
"""Independent verifier for the BT positive-local real-structure dichotomy."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-positive-local-real-structure-dichotomy-v1.schema.json"
)
PREDECESSOR = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json"
)
PUBLIC_DIGEST = "notes/bateman-turok-embedding.md"


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def add(left, right):
    return [[a + b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def subtract(left, right):
    return [[a - b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def matvec(matrix, vector):
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def quadratic(vector, matrix):
    image = matvec(matrix, vector)
    return sum((a * b for a, b in zip(vector, image)), Fraction(0))


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def sharp(matrix, kappa):
    return multiply(multiply(kappa, transpose(matrix)), kappa)


def star(matrix, kappa):
    return multiply(multiply(kappa, sharp(matrix, kappa)), kappa)


def parse_matrix(rows):
    return [[Fraction(value) for value in row] for row in rows]


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["schema_validation"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["certificate_identity"] = certificate.get("certificate") == (
        "REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1"
    )
    checks["lifecycle_is_classified"] = certificate.get("lifecycle_state") == "CLASSIFIED"
    checks["dependency_is_local_algebraic"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["four_input_hashes_recomputed"] = len(inputs) == 4 and all(
        os.path.isfile(os.path.join(ROOT, row.get("path", "")))
        and row.get("sha256") == sha256(row["path"])
        for row in inputs
    )
    paths = [row.get("path", "") for row in inputs]
    checks["predecessor_is_pinned"] = PREDECESSOR in paths
    checks["public_digest_is_pinned"] = PUBLIC_DIGEST in paths
    predecessor = load(PREDECESSOR)
    checks["predecessor_pass_rechecked"] = predecessor["checks"]["ok"]
    checks["predecessor_net_boundary_rechecked"] = (
        predecessor["disposition"]["positive_BT_Haag_Kastler_net"]
        == "NOT_CONSTRUCTED"
    )
    event_paths = [path for path in paths if "/events/" in path]
    checks["done_event_rechecked"] = len(event_paths) == 1 and (
        lambda event: event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith(
            "positive-local-real-structure-dichotomy"
        )
    )(load(event_paths[0]))

    obstruction = certificate.get("positive_Wightman_obstruction", {})
    gram = parse_matrix(obstruction.get("factored_public_Gram", []))
    checks["public_Gram_reconstructed"] = gram == [
        [Fraction(0), Fraction(1)],
        [Fraction(1), Fraction(0)],
    ]
    checks["public_Gram_is_symmetric"] = len(gram) == 2 and transpose(gram) == gram
    determinant = (
        gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
        if len(gram) == 2 else Fraction(0)
    )
    checks["negative_principal_determinant_recomputed"] = determinant == -1
    checks["positive_species_direction_recomputed"] = (
        len(gram) == 2 and quadratic([Fraction(1), Fraction(1)], gram) == 2
    )
    checks["negative_species_direction_recomputed"] = (
        len(gram) == 2 and quadratic([Fraction(1), Fraction(-1)], gram) == -2
    )
    checks["positive_type_conclusion_is_scoped"] = (
        obstruction.get("scalar_factor") == "w(f,f)>0"
        and obstruction.get("conclusion")
        == "NO_POSITIVE_HILBERT_REPRESENTATION_PRESERVING_BOTH_PUBLIC_REAL_FIELDS_AND_THE_PUBLIC_TWO_POINT_MATRIX"
        and obstruction.get("status") == "PROVED_EXACTLY"
    )

    dictionary = certificate.get("kappa_Hilbertization_dictionary", {})
    kappa = parse_matrix(dictionary.get("fundamental_symmetry_kappa", []))
    positive_gram = parse_matrix(dictionary.get("positive_Hilbert_Gram_G_kappa", []))
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    checks["kappa_involution_recomputed"] = len(kappa) == 2 and multiply(kappa, kappa) == identity
    checks["positive_Gram_recomputed"] = len(gram) == len(kappa) == 2 and multiply(gram, kappa) == identity == positive_gram
    checks["adjoint_relation_is_exact"] = dictionary.get("adjoint_relation") == "A*=kappa A^sharp kappa"
    checks["field_adjoint_map_is_exact"] = dictionary.get("field_adjoint_map") == [
        "Omega*=Upsilon", "Upsilon*=Omega", "T*=T", "X*=-X", "(iX)*=iX"
    ]
    checks["Hilbertization_is_not_ruled_out"] = dictionary.get("status") == "CONSTRUCTED_EXACTLY"

    born = certificate.get("weak_ghost_Born_separation", {})
    b_even = parse_matrix(born.get("B", []))
    q_negative = parse_matrix(born.get("Q_negative", []))
    stored_q_sharp = parse_matrix(born.get("Q_sharp", []))
    stored_q_star = parse_matrix(born.get("Q_star", []))
    zero2 = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    q_sharp = sharp(q_negative, kappa) if len(q_negative) == len(kappa) == 2 else []
    q_star = star(q_negative, kappa) if len(q_negative) == len(kappa) == 2 else []
    checks["negative_charge_matrix_unit_reconstructed"] = q_negative == [
        [Fraction(0), Fraction(0)], [Fraction(1), Fraction(0)]
    ]
    checks["Q_Krein_adjoint_recomputed"] = q_sharp == q_negative == stored_q_sharp
    checks["Q_Hilbert_adjoint_recomputed"] = q_star == [
        [Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]
    ] == stored_q_star
    checks["Q_nilpotence_recomputed"] = multiply(q_negative, q_negative) == zero2
    checks["Q_is_not_ghost_even_recomputed"] = multiply(multiply(kappa, q_negative), kappa) != q_negative
    krein_null = trace(multiply(q_sharp, q_negative))
    krein_cross = trace(multiply(sharp(b_even, kappa), q_negative))
    hilbert_q = trace(multiply(q_star, q_negative))
    process = add(b_even, q_negative)
    generalized = trace(multiply(sharp(process, kappa), process))
    ordinary = trace(multiply(star(process, kappa), process))
    checks["Krein_nullity_recomputed"] = krein_null == 0 == Fraction(born.get("Krein_null_weight", "9"))
    checks["Krein_orthogonality_recomputed"] = krein_cross == 0 == Fraction(born.get("Krein_cross_weight", "9"))
    checks["positive_Hilbert_Q_weight_recomputed"] = hilbert_q == 1 == Fraction(born.get("positive_Hilbert_remainder_weight", "9"))
    checks["generalized_Born_weight_recomputed"] = generalized == 2 == Fraction(born.get("generalized_Krein_Born_weight", "9"))
    checks["ordinary_Hilbert_weight_recomputed"] = ordinary == 3 == Fraction(born.get("ordinary_Hilbert_Born_weight", "9"))
    checks["Born_functionals_are_separated"] = generalized != ordinary and born.get("status") == "PROVED_BY_EXACT_FIXTURE"

    parity = certificate.get("observable_parity_theorem", {})
    transform = multiply(multiply(kappa, process), kappa)
    even = scale(Fraction(1, 2), add(process, transform))
    odd = scale(Fraction(1, 2), subtract(process, transform))
    checks["process_is_Krein_selfadjoint"] = sharp(process, kappa) == process
    checks["even_part_Hilbert_selfadjoint_recomputed"] = star(even, kappa) == even
    checks["odd_part_Hilbert_anti_selfadjoint_recomputed"] = star(odd, kappa) == scale(Fraction(-1), odd)
    checks["observable_iff_is_recorded"] = parity.get("iff_statement") == "A*=A iff kappa A kappa=A"
    checks["local_escape_keeps_domain_boundary"] = (
        "common kappa-invariant domain" in parity.get("local_escape_condition", "")
        and parity.get("status") == "PROVED_EXACTLY"
    )

    consequence = certificate.get("Eq19_and_detector_consequence", {})
    checks["Eq19_Q_positive_norm_gate_is_present"] = (
        "not automatically null in the positive Hilbert norm" in consequence.get("Eq19_role", "")
        and "local dynamics-compatible quotient" in consequence.get("physical_quotient_gate", "")
    )
    checks["quadrupole_parity_gate_is_present"] = (
        "kappa-even" in consequence.get("quadrupole_gate", "")
        and consequence.get("current_quadrupole_status")
        == "KAPPA_PARITY_AND_INVARIANT_DOMAIN_NOT_ESTABLISHED"
    )

    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])
    checks["positive_BT_net_is_not_promoted"] = (
        disposition.get("positive_BT_Haag_Kastler_net") == "NOT_CONSTRUCTED"
        and any("Haag--Kastler" in item for item in boundaries)
    )
    checks["Eq19_is_not_promoted"] = (
        disposition.get("general_Eq19") == "NOT_PROVED"
        and any("Eq. (19)" in item for item in boundaries)
    )
    checks["quadrupole_affiliation_is_not_promoted"] = (
        disposition.get("compact_quadrupole_kappa_parity") == "NOT_ESTABLISHED"
        and any("quadrupole density" in item for item in boundaries)
    )
    checks["generalized_Born_rule_is_not_rejected"] = any(
        "generalized Krein Born rule is inconsistent" in item for item in boundaries
    )
    checks["Hilbertization_is_not_rejected"] = any(
        "kappa-Hilbertization is mathematically impossible" in item for item in boundaries
    )
    checks["gravity_is_not_promoted"] = (
        disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and any("metric BV--BRST" in item for item in boundaries)
    )
    checks["Lorentzian_boundary_is_present"] = (
        disposition.get("Lorentzian_causal_BT_claim") == "NOT_ESTABLISHED"
        and any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    )
    literature = certificate.get("literature_context", {})
    checks["current_public_version_boundary_is_recorded"] = (
        literature.get("stable_url") == "https://arxiv.org/abs/2607.00096"
        and "v1" in literature.get("current_public_version_checked", "")
        and "deferred" in literature.get("current_public_version_checked", "")
    )
    checks["literature_priority_is_forbidden"] = (
        literature.get("priority_status") == "NOT_CLAIMED"
        and "literature priority" in boundaries
    )
    return checks


def main():
    certificate = load(CERT_REL)
    checks = verify(copy.deepcopy(certificate))
    for name, passed in checks.items():
        print(("PASS: " if passed else "FAIL: ") + name)
    if all(checks.values()):
        print("RESULT: PASS")
        return 0
    print("RESULT: FAIL", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
