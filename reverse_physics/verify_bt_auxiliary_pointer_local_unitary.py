#!/usr/bin/env python3
"""Independent verifier for the BT auxiliary-pointer local unitary."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
EXPECTED_SOURCE = "9a232e13e8ecbc53988daa97201e1794e338b044"
EXPECTED_INPUTS = [
    "planning/work-items/reverse-physics-bateman-auxiliary-pointer-local-unitary.json",
    "planning/events/reverse-physics-bateman-auxiliary-pointer-local-unitary-DONE-9a232e13.json",
    "reverse_physics/data/free_wick_local_operator_sources_v1.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REEH_SCHLIEDER_LOCAL_DETECTOR_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json",
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
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
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


def matadd(left, right):
    if not left or len(left) != len(right) or len(left[0]) != len(right[0]):
        return []
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def block(lt, rt, lb, rb):
    return [lt[i] + rt[i] for i in range(len(lt))] + [
        lb[i] + rb[i] for i in range(len(lb))
    ]


def inverse(matrix):
    if not matrix or len(matrix) != len(matrix[0]):
        return []
    size = len(matrix)
    augmented = [row[:] + eye(size)[i] for i, row in enumerate(matrix)]
    try:
        for column in range(size):
            pivot = next(row for row in range(column, size) if augmented[row][column])
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            scale = augmented[column][column]
            augmented[column] = [value / scale for value in augmented[column]]
            for row in range(size):
                if row != column:
                    scale = augmented[row][column]
                    augmented[row] = [
                        left - scale * right
                        for left, right in zip(augmented[row], augmented[column])
                    ]
    except (StopIteration, ZeroDivisionError):
        return []
    return [row[size:] for row in augmented]


def verify(certificate):
    checks = {}
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-auxiliary-pointer-local-unitary-v1.schema.json"
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == EXPECTED_SOURCE
    checks["input_paths"] = [row.get("path") for row in inputs] == EXPECTED_INPUTS
    checks["input_hashes"] = len(inputs) == len(EXPECTED_INPUTS) and all(
        row.get("sha256") == sha256(path) for row, path in zip(inputs, EXPECTED_INPUTS)
    )
    checks["producer_path"] = provenance.get("generated_by") == "reverse_physics/bt_auxiliary_pointer_local_unitary.py"
    checks["verifier_path"] = provenance.get("independent_verifier") == "reverse_physics/verify_bt_auxiliary_pointer_local_unitary.py"

    positive = load(EXPECTED_INPUTS[4])
    reeh = load(EXPECTED_INPUTS[5])
    detector = load(EXPECTED_INPUTS[6])
    checks["predecessor_passes"] = all(
        row.get("checks", {}).get("ok") for row in (positive, reeh, detector)
    )
    checks["positive_adjoint_import"] = positive.get(
        "kappa_Hilbertization_dictionary", {}
    ).get("field_adjoint_map", [])[:2] == ["Omega*=Upsilon", "Upsilon*=Omega"]
    checks["local_dark_no_go_import"] = reeh.get("disposition", {}).get(
        "nonzero_exactly_vacuum_dark_local_effect"
    ) == "IMPOSSIBLE_UNDER_DECLARED_HYPOTHESES"

    carrier = certificate.get("positive_free_local_carrier", {})
    checks["carrier_fock"] = carrier.get("Hilbert_space") == "H=Gamma_s(H1)"
    checks["carrier_complex_adjoint"] = "Upsilon=Phi_complex*" in carrier.get(
        "field_identification", ""
    )
    checks["carrier_two_real_fields"] = "T=(Omega+Upsilon)/2" in carrier.get(
        "field_identification", ""
    ) and "Y=(Omega-Upsilon)/(2i)" in carrier.get("field_identification", "")
    checks["carrier_dual_net"] = "Fd(O)=F(O')'" in carrier.get("local_net", "")
    checks["carrier_charge"] = any(
        "Omega charge +1" in item for item in carrier.get("internal_symmetries", [])
    )
    checks["carrier_status"] = carrier.get("status") == "POSITIVE_AUXILIARY_FREE_COMPLEX_SCALAR_LOCAL_CARRIER_CONSTRUCTED"

    column = certificate.get("closable_charged_column", {})
    inclusions = column.get("adjoint_inclusions", [])
    checks["two_branches"] = len(column.get("branches", [])) == 2
    checks["dense_domain"] = "dense" in column.get("common_domain", "")
    checks["first_adjoint_inclusion"] = inclusions[:1] == [
        "D_Upsilon(conj h) subset D_Omega(h)*"
    ]
    checks["second_adjoint_inclusion"] = inclusions[1:] == [
        "D_Omega(conj h) subset D_Upsilon(h)*"
    ]
    checks["column_definition"] = column.get("column") == "K_h psi=(D_Omega(h)psi,D_Upsilon(h)psi) from H to H direct_sum H"
    checks["closability_argument"] = all(
        term in column.get("closability_proof", "")
        for term in ("psi_n tends to zero", "x=y=0", "adjoint inclusions")
    )
    checks["no_branch_esa_assumption"] = column.get(
        "separate_branch_essential_selfadjointness"
    ) == "NOT_ASSUMED_AND_NOT_NEEDED"
    checks["column_status"] = column.get("status") == "DENSELY_DEFINED_COLUMN_CLOSABLE"

    block_data = certificate.get("selfadjoint_pointer_block", {})
    witness = block_data.get("finite_rational_witness", {})
    k = parse_matrix(witness.get("K", []))
    v = parse_matrix(witness.get("V", []))
    d = parse_matrix(witness.get("I_plus_V_squared", []))
    d_inverse = parse_matrix(witness.get("inverse_I_plus_V_squared", []))
    left = parse_matrix(witness.get("left_I_plus_KstarK", []))
    right = parse_matrix(witness.get("right_I_plus_KKstar", []))
    kt = transpose(k)
    expected_v = block(zeros(2, 2), kt, k, zeros(3, 3)) if k else []
    expected_left = matadd(eye(2), matmul(kt, k)) if k else []
    expected_right = matadd(eye(3), matmul(k, kt)) if k else []
    expected_d = block(expected_left, zeros(2, 3), zeros(3, 2), expected_right) if k else []
    checks["witness_shape"] = len(k) == 3 and len(k[0]) == 2
    checks["witness_block"] = v == expected_v
    checks["witness_symmetry"] = transpose(v) == v
    checks["witness_square"] = d == matadd(matmul(v, v), eye(5)) == expected_d
    checks["witness_inverse_left"] = matmul(d, d_inverse) == eye(5)
    checks["witness_inverse_right"] = matmul(d_inverse, d) == eye(5)
    checks["left_denominator"] = left == expected_left and matmul(left, inverse(left)) == eye(2)
    checks["right_denominator"] = right == expected_right and matmul(right, inverse(right)) == eye(3)
    checks["abstract_operator"] = block_data.get("operator") == "V_h=[[0,Kbar_h*],[Kbar_h,0]] on H_g direct_sum (H_e_minus direct_sum H_e_plus)"
    checks["abstract_domain"] = block_data.get("domain") == "Dom(Kbar_h) direct_sum Dom(Kbar_h*)"
    checks["abstract_square"] = block_data.get("square") == "V_h^2=diag(Kbar_h* Kbar_h,Kbar_h Kbar_h*)"
    checks["resolvent_has_both_denominators"] = all(
        term in block_data.get("resolvent", "") for term in ("K* K-z^2", "K K*-z^2", "plus or minus i")
    )
    checks["range_criterion"] = "both plus/minus-i ranges" in block_data.get(
        "conclusion", ""
    )
    checks["selfadjoint_status"] = block_data.get("status") == "SELFADJOINT_WITH_EXPLICIT_RESOLVENT"

    calculus = certificate.get("local_functional_calculus", {})
    checks["affiliation"] = all(
        term in calculus.get("affiliation_proof", "")
        for term in ("complement-supported Weyl", "closure", "commutant unitary")
    )
    checks["charge_and_parity"] = all(
        term in calculus.get("symmetry", "") for term in ("kappa", "-2,+2", "+2,-2")
    )
    checks["local_unitary"] = calculus.get("unitary") == "U_g=exp(-i g V_h) belongs to B(C3) tensor Fd(O) for every real g"
    checks["polar_block"] = calculus.get("ground_to_click_block") == "P_click U_g P_g=-i polar(K) sin(g|K|)"
    checks["effects"] = calculus.get("effects") == [
        "E_click(g)=sin^2(g|K|)",
        "E_no(g)=cos^2(g|K|)",
        "E_click+E_no=I and 0<=E_click,E_no<=I",
    ]
    checks["vacuum_boundary"] = "no exactly vacuum-dark local effect" in calculus.get(
        "vacuum_boundary", ""
    )
    checks["calculus_status"] = calculus.get("status") == "EXACT_BOUNDED_LOCAL_UNITARY_AND_NORMALIZED_POINTER_EFFECTS"

    tangent = certificate.get("operational_q8_tangent", {})
    checks["phase_inputs"] = "Psi_theta=" in tangent.get("inputs", "") and "charge-matched" in tangent.get("inputs", "")
    checks["pointer_readout"] = "P_click" in tangent.get("readout", "")
    checks["half_contrast"] = tangent.get("half_contrast") == "C_theta(g)=[p_theta(g)-p_(theta+pi)(g)]/2"
    checks["tangent_formula"] = tangent.get("exact_tangent") == "C_theta(0)=0 and C_theta'(0)=Im(exp(-i theta)<v,K_h u>)"
    checks["phase_optimization"] = tangent.get("phase_optimization") == "max_theta |C_theta'(0)|=|<v,K_h u>|"
    checks["no_field_postselection"] = "no final field-vacuum projector" in tangent.get(
        "locality", ""
    )
    checks["q8_bound"] = tangent.get("strict_bound") == "Q8_aux,compact/q4_bar>1/18874368000" and detector.get(
        "compact_q8_response", {}
    ).get("compact_lower") == "Q8_aux,compact/q4_bar>1/18874368000"
    checks["tangent_status"] = tangent.get("status") == "STRICTLY_POSITIVE_Q8_TRANSITION_HAS_POINTER_ONLY_LOCAL_UNITARY_TANGENT"

    disposition = certificate.get("disposition", {})
    expected_disposition = {
        "positive_auxiliary_free_local_carrier": "CONSTRUCTED",
        "charged_Wick_column": "CLOSABLE",
        "charge_balanced_pointer_block": "SELFADJOINT_AND_AFFILIATED",
        "bounded_local_functional_calculus": "CONSTRUCTED_EXACTLY",
        "finite_detector_strength_unitary": "CONSTRUCTED_EXACTLY",
        "normalized_local_pointer_effects": "CONSTRUCTED_WITH_NONZERO_VACUUM_BASELINE_ALLOWED",
        "selected_q8_operational_tangent": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
        "positive_Hilbert_vs_public_generalized_Born_equivalence": "NOT_ESTABLISHED",
        "interacting_public_BT_local_net": "NOT_CONSTRUCTED",
        "lambda10_and_higher_BT_control": "NOT_CONSTRUCTED",
        "general_Eq19": "NOT_PROVED",
        "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
        "Lorentzian_causal_claim": "NOT_ESTABLISHED",
    }
    checks["disposition"] = disposition == expected_disposition
    boundaries = certificate.get("does_not_establish", [])
    checks["branch_esa_boundary"] = any("separately" in item and "essential self-adjointness" in item for item in boundaries)
    checks["Born_boundary"] = any("generalized Krein Born rule" in item for item in boundaries)
    checks["postselection_boundary"] = any("field-vacuum postselection" in item for item in boundaries)
    checks["interacting_boundary"] = any("interacting BT Haag--Kastler" in item for item in boundaries)
    checks["Eq19_boundary"] = any("Eq. (19)" in item for item in boundaries)
    checks["Lorentzian_boundary"] = any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    checks["priority_boundary"] = any("literature priority" in item for item in boundaries)
    checks["missing_objects"] = len(certificate.get("missing_object_ledger", [])) == 5
    checks["next_gate"] = all(
        term in certificate.get("next_gate", "") for term in ("lambda10", "conditional expectation", "Eq. (19)")
    )
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-auxiliary-pointer-local-unitary.md"
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
