#!/usr/bin/env python3
"""Independent verifier for the public-BT polynomial positive quadrupole."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
EXPECTED_SOURCE = "11b1bcf6a7a94ac4f908d1a558a181a2fe4df263"
EXPECTED_INPUTS = [
    "planning/work-items/reverse-physics-bateman-auxiliary-polynomial-quadrupole-positive-detector.json",
    "planning/events/reverse-physics-bateman-auxiliary-polynomial-quadrupole-positive-detector-DONE-11b1bcf6.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
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


def parse_matrix(value):
    try:
        matrix = [[Fraction(entry) for entry in row] for row in value]
    except (TypeError, ValueError, ZeroDivisionError):
        return []
    if not matrix or any(len(row) != len(matrix[0]) for row in matrix):
        return []
    return matrix


def zeros(rows, columns):
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)] if matrix else []


def matmul(left, right):
    if not left or not right or len(left[0]) != len(right):
        return []
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matvec(matrix, vector):
    if not matrix or len(matrix[0]) != len(vector):
        return []
    return [sum((x * y for x, y in zip(row, vector)), Fraction(0)) for row in matrix]


def quadratic(vector, gram):
    image = matvec(gram, vector)
    if not image:
        return None
    return sum((x * y for x, y in zip(vector, image)), Fraction(0))


def complement_matrix(size):
    matrix = zeros(size, size)
    for column in range(size):
        matrix[size - 1 - column][column] = Fraction(1)
    return matrix


def block_diagonal(left, right):
    result = zeros(len(left) + len(right), len(left) + len(right))
    for i, row in enumerate(left):
        for j, value in enumerate(row):
            result[i][j] = value
    for i, row in enumerate(right):
        for j, value in enumerate(row):
            result[len(left) + i][len(left) + j] = value
    return result


def verify(certificate):
    checks = {}
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-auxiliary-polynomial-quadrupole-positive-detector-v1.schema.json"
    checks["schema_version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]
    provenance = certificate.get("provenance", {})
    checks["source_commit"] = provenance.get("source_commit") == EXPECTED_SOURCE
    inputs = provenance.get("inputs", [])
    checks["input_paths"] = [row.get("path") for row in inputs] == EXPECTED_INPUTS
    checks["input_hashes"] = len(inputs) == len(EXPECTED_INPUTS) and all(row.get("sha256") == sha256(path) for row, path in zip(inputs, EXPECTED_INPUTS))
    checks["producer"] = provenance.get("generated_by") == "reverse_physics/bt_auxiliary_polynomial_quadrupole_positive_detector.py"
    checks["independent_verifier"] = provenance.get("independent_verifier") == "reverse_physics/verify_bt_auxiliary_polynomial_quadrupole_positive_detector.py"
    local_predecessor = load(EXPECTED_INPUTS[5])
    compact_predecessor = load(EXPECTED_INPUTS[6])
    angle_predecessor = load(EXPECTED_INPUTS[8])
    six_predecessor = load(EXPECTED_INPUTS[9])

    classification = certificate.get("quadratic_species_classification", {})
    k1 = parse_matrix(classification.get("fundamental_symmetry", []))
    diagonal = parse_matrix(classification.get("responding_tensor", []))
    cross = parse_matrix(classification.get("neutral_tensor", []))
    checks["species_kappa"] = k1 == [[0, 1], [1, 0]] and matmul(k1, k1) == eye(2)
    checks["responding_tensor"] = diagonal == eye(2)
    checks["neutral_tensor"] = cross == k1
    checks["responding_parity"] = matmul(matmul(k1, diagonal), k1) == diagonal
    checks["neutral_parity"] = matmul(matmul(k1, cross), k1) == cross
    checks["classification_formula"] = classification.get("general_real_symmetric_ghost_even_tensor") == "C(a,b)=[[a,b],[b,a]]"
    checks["neutral_response_zero"] = classification.get("neutral_pure_pair_response") == ["0", "0"]
    checks["responding_charges"] = classification.get("responding_charge_support") == ["+2", "-2"]
    checks["regularity"] = classification.get("regularity") == "POLYNOMIAL_ON_THE_PUBLIC_PERTURBATIVE_VACUUM_CHART_WITH_NO_LOGARITHM_OR_INVERSE_FIELD"
    checks["classification_status"] = classification.get("status") == "RESPONDING_GHOST_EVEN_PUBLIC_POLYNOMIAL_CONSTRUCTED_WITH_EXCHANGED_CHARGE_BRANCHES"

    pointer = certificate.get("charge_balanced_pointer", {})
    k3 = parse_matrix(pointer.get("three_particle_kappa", []))
    kout = parse_matrix(pointer.get("pointer_spectator_kappa", []))
    mapping = parse_matrix(pointer.get("pair_map", []))
    interaction = parse_matrix(pointer.get("truncated_interaction", []))
    hilbert = parse_matrix(pointer.get("Hilbert_Gram", []))
    expected_k3 = complement_matrix(8)
    expected_kout = complement_matrix(4)
    expected_map = zeros(4, 8)
    expected_map[0][0] = Fraction(1)
    expected_map[3][7] = Fraction(1)
    checks["three_kappa"] = k3 == expected_k3 and matmul(k3, k3) == eye(8)
    checks["output_kappa"] = kout == expected_kout and matmul(kout, kout) == eye(4)
    checks["pair_map"] = mapping == expected_map
    checks["parity_intertwiner"] = matmul(mapping, k3) == matmul(kout, mapping)
    qin = zeros(8, 8)
    for index in range(8):
        qin[index][index] = Fraction(2 * bin(index).count("1") - 3)
    qout = zeros(4, 4)
    for index, value in enumerate((-3, -1, 1, 3)):
        qout[index][index] = Fraction(value)
    checks["charge_intertwiner"] = matmul(qout, mapping) == matmul(mapping, qin)
    adjoint = matmul(matmul(k3, transpose(mapping)), kout)
    checks["pair_adjoint"] = adjoint == transpose(mapping)
    effect = matmul(adjoint, mapping)
    expected_effect = zeros(8, 8)
    expected_effect[0][0] = expected_effect[7][7] = Fraction(1)
    checks["effect"] = effect == expected_effect
    checks["effect_parity"] = matmul(matmul(k3, effect), k3) == effect
    source = [Fraction(int(index in (0, 7))) for index in range(8)]
    output = matvec(mapping, source)
    checks["source_parity"] = matvec(k3, source) == source
    checks["output_parity"] = matvec(kout, output) == output
    checks["norms"] = quadratic(source, k3) == quadratic(output, kout) == 2
    checks["isometry_on_source"] = matvec(effect, source) == source
    total_gram = block_diagonal(k3, kout)
    checks["positive_Hilbert_Gram"] = hilbert == eye(12) == matmul(total_gram, total_gram)
    expected_interaction = zeros(12, 12)
    for i in range(4):
        for j in range(8):
            expected_interaction[8 + i][j] = mapping[i][j]
            expected_interaction[j][8 + i] = mapping[i][j]
    checks["interaction_matrix"] = interaction == expected_interaction
    checks["interaction_Hilbert_adjoint"] = transpose(interaction) == interaction
    checks["interaction_Krein_adjoint"] = matmul(matmul(total_gram, transpose(interaction)), total_gram) == interaction
    checks["interaction_parity"] = matmul(matmul(total_gram, interaction), total_gram) == interaction
    checks["operator_identities"] = pointer.get("operator_identities") == [
        "V^sharp=V", "V*=V", "kappa_total V kappa_total=V"
    ]
    checks["neutral_branches"] = pointer.get("branch_charge_sums") == ["-2+2=0", "+2-2=0"]
    checks["pointer_status"] = pointer.get("status") == "FINITE_CHARGE_NEUTRAL_GHOST_EVEN_POSITIVE_SELECTED_POINTER_COUPLING_CONSTRUCTED"

    response = certificate.get("compact_q8_response", {})
    channel_rows = angle_predecessor.get("ten_channel_kinematics", {}).get("rows", [])
    channels = six_predecessor.get("universal_complement_formula", {}).get("channels", [])
    pure_mask = channels[0] if channels else None
    pure_rows = [row for row in channel_rows if row.get("mask") != pure_mask]
    t_count = sum(row.get("family") == "T_EXCHANGE" for row in pure_rows)
    u_count = sum(row.get("family") == "U_EXCHANGE" for row in pure_rows)
    t_weight = sum(row.get("weight", 0) for row in channel_rows if row.get("family") == "T_EXCHANGE")
    u_weight = sum(row.get("weight", 0) for row in channel_rows if row.get("family") == "U_EXCHANGE")
    try:
        imported_tree_lower = Fraction(local_predecessor["exact_P2_moments"]["tree_interval"]["lower"]["exact"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        imported_tree_lower = Fraction(0)
    checks["pure_channel"] = response.get("pure_channel") == "S=7 and S^c=56, corresponding to the two all-pure three-particle branches"
    checks["tree_ratio"] = response.get("connected_tree_relation") == "after P2 removes all c-independent terms, J_tree,pure=(2/10)*J_tree=J_tree/5"
    checks["tree_weights_reconstructed"] = pure_mask == 7 and t_count == u_count == 2 and t_weight == u_weight == 10
    checks["nonexchange_rows_are_angle_independent"] = all(
        row.get("family") in ("RESONANT_NULL", "SPACELIKE_AXIS")
        for row in pure_rows
        if row.get("family") not in ("T_EXCHANGE", "U_EXCHANGE")
    )
    checks["tree_lower"] = response.get("connected_tree_lower") == "J_tree,pure>1/500>0" and imported_tree_lower / 5 > Fraction(1, 500)
    checks["loop_lower"] = response.get("loop_lower") == "J_loop>252416/73828125>1/400" and Fraction(252416, 73828125) > Fraction(1, 400)
    checks["relative_lower"] = response.get("complete_relative_lower") == "J_R,aux>1/19200"
    checks["local_lower"] = response.get("local_lower") == "Q8_aux,local/q4_bar>1/4718592000"
    checks["compact_lower"] = response.get("compact_lower") == "Q8_aux,compact/q4_bar>1/18874368000"
    checks["compact_lower_matches_predecessor"] = compact_predecessor.get("exact_darkness_and_probability", {}).get("compact_lower", {}).get("exact") == "1/18874368000"
    checks["probability_order"] = response.get("probability") == "p_click=g_det^2*lambda^8*Q8_aux,compact+O(g_det^2*lambda^10)+O(g_det^4)"
    checks["response_status"] = response.get("status") == "STRICTLY_POSITIVE_PUBLIC_AUXILIARY_COMPACT_SPACETIME_Q8_COEFFICIENT"

    disposition = certificate.get("disposition", {})
    checks["detector_constructed"] = disposition.get("regular_public_auxiliary_polynomial_detector") == "CONSTRUCTED"
    checks["scalar_projection_not_reopened"] = disposition.get("same_chart_scalar_hidden_parity_projection") == "NOT_USED_AND_REMAINS_OBSTRUCTED"
    checks["charged_pointer_declared"] = disposition.get("boost_neutral_total_pointer_coupling") == "CONSTRUCTED_WITH_A_CHARGED_CLICK_DOUBLET"
    checks["q8_promoted_only_scoped"] = disposition.get("absolute_compact_public_auxiliary_q8") == "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE"
    checks["affiliation_open"] = disposition.get("full_selfadjoint_local_net_affiliation") == "NOT_CONSTRUCTED"
    checks["all_orders_open"] = disposition.get("all_orders_in_detector_or_BT_coupling") == "NOT_CONSTRUCTED"
    checks["Eq19_open"] = disposition.get("general_Eq19") == "NOT_PROVED_AND_NOT_USED"
    checks["gravity_open"] = disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
    checks["Lorentzian_open"] = disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    boundaries = certificate.get("does_not_establish", [])
    checks["operator_nonidentity_boundary"] = any("operator identity" in item for item in boundaries)
    checks["domain_boundary"] = any("essential self-adjointness" in item for item in boundaries)
    checks["Eq19_boundary"] = any("Eq. (19)" in item for item in boundaries)
    checks["Lorentzian_boundary"] = any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    checks["priority_boundary"] = any("literature priority" in item for item in boundaries)
    checks["next_gate"] = "self-adjoint closure" in certificate.get("next_gate", "") and "g_det^4" in certificate.get("next_gate", "")
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-auxiliary-polynomial-quadrupole-positive-detector.md"
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
