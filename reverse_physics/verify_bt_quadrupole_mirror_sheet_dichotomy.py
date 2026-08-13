#!/usr/bin/env python3
"""Independent verifier for the BT quadrupole mirror-sheet dichotomy."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
EXPECTED_SOURCE = "a0527532999cf0b899508f7e2e81644130955886"
EXPECTED_INPUTS = [
    "planning/work-items/reverse-physics-bateman-quadrupole-mirror-sheet-dichotomy.json",
    "planning/events/reverse-physics-bateman-quadrupole-mirror-sheet-dichotomy-DONE-a0527532.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
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


def parse_matrix(value):
    try:
        return [[Fraction(entry) for entry in row] for row in value]
    except (TypeError, ValueError, ZeroDivisionError):
        return []


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


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


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def dot(left, right):
    return left[0] * right[0] - sum(left[i] * right[i] for i in range(1, 4))


def quadrupole(P, r, axis):
    p2 = dot(P, P)
    return 6 * (
        p2 * dot(axis, r) ** 2
        - (p2 * dot(axis, axis) - dot(axis, P) ** 2) * dot(r, r) / 3
    )


def verify(certificate):
    checks = {}
    checks["certificate_identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1"
    checks["schema_identity"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-quadrupole-mirror-sheet-dichotomy-v1.schema.json"
    checks["schema_version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "CLASSIFIED"
    checks["dependency_tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    provenance = certificate.get("provenance", {})
    checks["source_commit"] = provenance.get("source_commit") == EXPECTED_SOURCE
    inputs = provenance.get("inputs", [])
    checks["input_paths"] = [row.get("path") for row in inputs] == EXPECTED_INPUTS
    checks["input_hashes"] = len(inputs) == len(EXPECTED_INPUTS) and all(row.get("sha256") == sha256(path) for row, path in zip(inputs, EXPECTED_INPUTS))
    checks["producer_and_verifier"] = provenance.get("generated_by") == "reverse_physics/bt_quadrupole_mirror_sheet_dichotomy.py" and provenance.get("independent_verifier") == "reverse_physics/verify_bt_quadrupole_mirror_sheet_dichotomy.py"

    image = certificate.get("same_chart_hidden_image", {})
    checks["hidden_field"] = image.get("hidden_field") == "g=lambda^-1*log(psi/lambda)"
    checks["bilinear_expansion"] = image.get("bilinear_formula") == "D[h(phi)]=D[phi]-2*B(phi,g)+D[g]"
    checks["even_projection"] = image.get("even_projection") == "D_even=D[phi]-B(phi,g)+D[g]/2"
    checks["odd_projection"] = image.get("odd_projection") == "D_odd=B(phi,g)-D[g]/2"
    checks["same_chart_status"] = image.get("status") == "OBSTRUCTED" and image.get("conclusion") == "THE_COMPACT_SCALAR_QUADRUPOLE_IS_NOT_A_REGULAR_SAME_CHART_GHOST_EVEN_OBSERVABLE"

    witness = certificate.get("scaled_mirror_jet_witness", {})
    P = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    r = (Fraction(0), Fraction(1, 2), Fraction(0), Fraction(0))
    axis = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    q = quadrupole(P, r, axis)
    checks["quadrupole_recomputed"] = q == 1 == Fraction(witness.get("quadrupole_pair_coefficient", "0"))
    sample_t = [Fraction(value) for value in witness.get("sample_t", [])]
    sample_q = [Fraction(value) for value in witness.get("sample_pair_coefficients", [])]
    checks["scaled_path"] = sample_t == [Fraction(1), Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)]
    checks["path_coefficient_constant"] = sample_q == [q] * 4
    checks["path_limit_is_zero"] = "tends to zero" in witness.get("limit", "")
    checks["directional_nonextension"] = "f=0 gives zero" in witness.get("direction_comparison", "") and witness.get("status") == "PROVED_BY_EXACT_PATH_WITNESS"

    completion = certificate.get("minimal_mirror_sheet_completion", {})
    gram = parse_matrix(completion.get("Krein_Gram_G", []))
    kappa = parse_matrix(completion.get("fundamental_symmetry_kappa", []))
    positive = parse_matrix(completion.get("positive_Hilbert_Gram", []))
    projector = parse_matrix(completion.get("even_sheet_projector", []))
    density = parse_matrix(completion.get("mirrored_density_fixture", []))
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    checks["cross_Gram"] = gram == [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]] == kappa
    checks["positive_Gram"] = multiply(gram, kappa) == positive == identity
    checks["kappa_involution"] = multiply(kappa, kappa) == identity
    checks["projector_idempotent"] = multiply(projector, projector) == projector
    checks["projector_ghost_even"] = multiply(multiply(kappa, projector), kappa) == projector
    checks["density_ghost_even"] = multiply(multiply(kappa, density), kappa) == density
    checks["density_Krein_selfadjoint"] = multiply(multiply(gram, transpose(density)), gram) == density
    checks["density_Hilbert_selfadjoint"] = transpose(density) == density
    checks["changed_theory_status"] = completion.get("status") == "CONSTRUCTED_AS_A_CHANGED_DOUBLED_THEORY"

    response = certificate.get("response_transfer", {})
    amplitude = Fraction(response.get("single_sheet_fixture_amplitude", "0"))
    symmetric = Fraction(response.get("normalized_symmetric_amplitude", "0"))
    checks["response_normalization"] = amplitude == symmetric == Fraction(3, 5)
    checks["probability_normalization"] = Fraction(response.get("single_sheet_fixture_probability", "0")) == Fraction(response.get("symmetric_fixture_probability", "-1")) == Fraction(9, 25)
    checks["q8_bound"] = response.get("inherited_compact_q8_lower") == "Q8_compact/q4_bar>1/18874368000"
    checks["leading_darkness"] = "zero on each sheet" in response.get("leading_scalar_response", "")

    disposition = certificate.get("disposition", {})
    checks["same_chart_not_promoted"] = disposition.get("regular_same_chart_quadrupole_ghost_parity") == "OBSTRUCTED"
    checks["doubled_theory_not_public"] = disposition.get("public_scalar_action_selects_doubling") == "NO" and disposition.get("public_Rt_selects_doubling") == "NO"
    checks["Eq19_open"] = disposition.get("general_Eq19") == "NOT_PROVED"
    checks["positive_net_open"] = disposition.get("positive_BT_Haag_Kastler_net") == "NOT_CONSTRUCTED"
    checks["gravity_open"] = disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
    checks["Lorentzian_open"] = disposition.get("Lorentzian_causal_BT_claim") == "NOT_ESTABLISHED"
    boundaries = certificate.get("does_not_establish", [])
    checks["singular_route_boundary"] = any("singular" in item for item in boundaries)
    checks["doubled_equivalence_boundary"] = any("doubled mirror-sheet theory is equivalent" in item for item in boundaries)
    checks["Eq19_boundary"] = any("Eq. (19)" in item for item in boundaries)
    checks["Lorentzian_boundary"] = any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    checks["priority_boundary"] = any("literature priority" in item for item in boundaries)
    checks["next_gate"] = "polynomial ghost-even auxiliary Omega/Upsilon detector" in certificate.get("next_gate", "")
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-quadrupole-mirror-sheet-dichotomy.md"
    checks["commands"] = len(certificate.get("verification_commands", [])) == 3
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
