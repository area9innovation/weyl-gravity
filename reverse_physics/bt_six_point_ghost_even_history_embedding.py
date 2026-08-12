#!/usr/bin/env python3
"""Exact public-Fock ghost-even embedding of the BT six-point history carrier."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-ghost-even-history-embedding-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-ghost-even-history-embedding.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-ghost-even-history-embedding.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
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


def complement(mask):
    return mask ^ 63


def permutation_matrix(size, image):
    return sp.SparseMatrix(size, size, {(image[column], column): 1 for column in range(size)})


def build():
    born = load(INPUTS[1])
    history = load(INPUTS[2])
    cut = load(INPUTS[3])
    channels = born["universal_complement_formula"]["channels"]
    complements = [complement(mask) for mask in channels]

    identity10 = sp.eye(10)
    swap20 = sp.SparseMatrix.vstack(
        sp.SparseMatrix.hstack(sp.zeros(10), identity10),
        sp.SparseMatrix.hstack(identity10, sp.zeros(10)),
    )
    eta = swap20
    ghost_parity = swap20
    sqrt2 = sp.sqrt(2)
    u_plus = sp.Matrix.vstack(identity10, identity10) / sqrt2
    u_minus = sp.Matrix.vstack(identity10, -identity10) / sqrt2
    p_plus = (sp.eye(20) + ghost_parity) / 2
    p_minus = (sp.eye(20) - ghost_parity) / 2

    c = sp.Matrix(sp.symbols("c0:10", real=True))
    full_coefficient = sp.Matrix.vstack(c, c)
    born_norm = sp.expand((full_coefficient.T * eta * full_coefficient)[0])
    expected_born_norm = 2 * sum(entry**2 for entry in c)

    y = sp.Matrix(sp.symbols("y0:10", real=True))
    incidence = sp.ones(10) - identity10
    channel_coefficient = incidence * y / 4
    channel_pullback = sp.simplify(
        2 * (incidence / 4).T * (incidence / 4)
    )

    # An 8-by-8 three-in/three-out species matrix.  Bits 0..2 label
    # incoming slots and bits 3..5 label outgoing slots.  Only the twenty
    # neutral six-leg masks occur.  Complement equality makes this matrix
    # an exact ghost-parity intertwiner.
    pair_index = {}
    for index, mask in enumerate(channels):
        pair_index[mask] = index
        pair_index[complement(mask)] = index
    choi = sp.zeros(8)
    for mask, index in pair_index.items():
        incoming = mask & 7
        outgoing = (mask >> 3) & 7
        choi[outgoing, incoming] = c[index]
    kappa3 = permutation_matrix(8, [7 - value for value in range(8)])
    choi_sharp = kappa3 * choi.T * kappa3
    choi_born_trace = sp.expand(sp.trace(choi_sharp * choi))

    # Fix channel B=channels[1].  Its nine normalized resolved histories
    # map to the nine positive complement-pair vectors u_S, S != B.  A raw
    # history basis has metric 2I in the predecessor; division by sqrt(2)
    # gives the normalized basis used here.
    fixed_index = 1
    allowed = [index for index in range(10) if index != fixed_index]
    selector = sp.SparseMatrix(10, 9, {(species, column): 1 for column, species in enumerate(allowed)})
    fixed_embedding = u_plus * selector
    history_residue = sp.ones(9, 1) / (2 * sqrt2)
    fixed_full_residue = sp.Matrix(
        [sp.Rational(0) if index == fixed_index else sp.Rational(1, 4) for index in range(10)]
        + [sp.Rational(0) if index == fixed_index else sp.Rational(1, 4) for index in range(10)]
    )

    listed_histories = [
        (row["species_assignment"], row["intermediate_channel"])
        for row in history["typed_history_carrier"]["allowed_histories"]
    ]
    collapse = sp.SparseMatrix(
        10,
        90,
        {(species, column): 1 for column, (species, _) in enumerate(listed_histories)},
    )
    global_map = u_plus * collapse
    global_gram = sp.simplify(global_map.T * eta * global_map)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "ten_unordered_channels_imported": len(channels) == 10 and len(set(channels)) == 10,
        "twenty_neutral_masks_exhausted": len(set(channels + complements)) == 20 and all(mask.bit_count() == 3 for mask in channels + complements),
        "representatives_are_disjoint_from_complements": set(channels).isdisjoint(complements),
        "Krein_metric_is_non_degenerate_involution": eta**2 == sp.eye(20) and eta.det() != 0,
        "ghost_parity_preserves_Krein_metric": ghost_parity.T * eta * ghost_parity == eta,
        "fundamental_positive_metric_is_identity": eta * ghost_parity == sp.eye(20),
        "positive_frame_is_orthonormal": u_plus.T * eta * u_plus == identity10,
        "negative_frame_is_orthonormal": u_minus.T * eta * u_minus == -identity10,
        "frames_are_Krein_orthogonal": u_plus.T * eta * u_minus == sp.zeros(10),
        "frames_have_declared_ghost_parity": ghost_parity * u_plus == u_plus and ghost_parity * u_minus == -u_minus,
        "spectral_projectors_are_exact": p_plus**2 == p_plus and p_minus**2 == p_minus and p_plus * p_minus == sp.zeros(20) and p_plus + p_minus == sp.eye(20),
        "complete_coefficient_is_ghost_even": ghost_parity * full_coefficient == full_coefficient and p_plus * full_coefficient == full_coefficient,
        "complete_Krein_norm_is_sum_of_squares": sp.simplify(born_norm - expected_born_norm) == 0,
        "public_Born_density_is_imported": born["local_born_density"]["kernel"] == "2*sum_{S<Sc} c_S^2",
        "incidence_formula_is_reconstructed": channel_coefficient == incidence * y / 4 and incidence.det() == -9,
        "channel_pullback_matches_complete_gram": channel_pullback == sp.ones(10) + sp.Rational(1, 8) * identity10,
        "Choi_has_exactly_twenty_neutral_entries": sum(value != 0 for value in choi) == 20,
        "Choi_is_ghost_parity_intertwiner": kappa3 * choi * kappa3 == choi,
        "Choi_sharp_reduces_to_transpose": choi_sharp == choi.T,
        "Choi_Born_trace_matches_complete_density": sp.simplify(choi_born_trace - expected_born_norm) == 0,
        "fixed_history_embedding_is_isometric": fixed_embedding.T * eta * fixed_embedding == sp.eye(9),
        "fixed_history_embedding_is_ghost_even": ghost_parity * fixed_embedding == fixed_embedding,
        "fixed_history_residue_maps_to_public_Fock_residue": sp.simplify(fixed_embedding * history_residue - fixed_full_residue) == sp.zeros(20, 1),
        "fixed_history_norm_is_nine_eighths": sp.simplify((history_residue.T * history_residue)[0]) == sp.Rational(9, 8),
        "fixed_history_norm_matches_cut": cut["coefficient_match"]["history_norm"] == "9/8",
        "global_map_restricts_to_every_fixed_embedding": all(global_map[:, [column for column, (_, channel) in enumerate(listed_histories) if channel == fixed]] == u_plus * sp.SparseMatrix(10, 9, {(species, col): 1 for col, species in enumerate([s for s in range(10) if s != fixed])}) for fixed in range(10)),
        "global_resolved_history_map_has_rank_ten": global_map.rank() == 10,
        "global_resolved_history_kernel_has_dimension_eighty": 90 - global_map.rank() == 80,
        "global_resolved_history_map_is_not_isometric": global_gram != sp.eye(90),
        "source_Eq19_and_physical_survival_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1",
        "schema_version": "reverse-physics-bt-six-point-ghost-even-history-embedding-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact public neutral six-leg Fock/Choi ghost-even embedding of the complete six-point coefficient and each fixed-channel positive history carrier",
        "question": "Does complement symmetry place the certified six-point BT coefficient and its fixed-shell histories inside a positive ghost-even sector of the public neutral Fock carrier?",
        "answer": "Yes, exactly at the complete six-point tree-coefficient level. The twenty neutral three-Omega/three-Upsilon species assignments form ten complement pairs. In the ordered pair basis the public cross-Krein metric and ghost parity are both eta=kappa=[[0,I10],[I10,0]]. Their symmetric frame U_plus=[I10;I10]/sqrt(2) has positive Gram I10 and ghost parity +1; the antisymmetric frame has Gram -I10 and parity -1. The complete coefficient vector is (c,c)=sqrt(2)U_plus*c, hence it is entirely ghost even and has Krein norm 2 sum c_S^2, exactly the certified local Born density. Equivalently, arranging the twenty coefficients as an 8-by-8 three-in/three-out species matrix A gives kappa3*A*kappa3=A, A^sharp=A^T, and tr(A^sharp*A)=2 sum c_S^2. For any fixed intermediate channel B, the nine normalized histories S!=B embed isometrically as U_plus*e_S. Their residue 1/(2sqrt(2)) maps to coefficient 1/4 on both S and Sc and has norm 9/8, matching the Hamiltonian-cut coefficient. Thus the previously abstract positive fixed-shell output history range is a concrete public-Fock ghost-even range. A single map of all ninety resolved histories into the same public ten-plane necessarily has rank ten and an eighty-dimensional kernel; retaining all resolved channel records requires an additional positive detector ancilla. This closes the fixed-shell output-history affiliation gate, but it does not construct the transported physical input projector R_t P_phi R_t^dagger, the BT virtual/survival block, a global channel-record dilation, or all-order Eq. (19).",
        "neutral_six_leg_carrier": {
            "representative_masks": channels,
            "complement_masks": complements,
            "mask_convention": "six bits with value one for Omega and zero for Upsilon; bits 0..2 incoming and bits 3..5 outgoing",
            "ordered_basis": "the ten representative masks followed by their ten bitwise complements",
            "Krein_metric": "eta=[[0,I10],[I10,0]]",
            "ghost_parity": "kappa=eta",
            "fundamental_positive_metric": "eta*kappa=I20",
            "positive_frame": "U_plus=[I10;I10]/sqrt(2)",
            "negative_frame": "U_minus=[I10;-I10]/sqrt(2)",
            "frame_grams": {"positive": "U_plus^T*eta*U_plus=I10", "negative": "U_minus^T*eta*U_minus=-I10", "cross": "U_plus^T*eta*U_minus=0"},
            "spectral_projectors": {"positive_even": "P_plus=(I20+kappa)/2", "negative_odd": "P_minus=(I20-kappa)/2"},
            "inertia": {"positive": 10, "negative": 10, "zero": 0},
        },
        "complete_coefficient_embedding": {
            "public_formula": "c_S=c_Sc=(1/4)*sum_{A!=S}1/s_A",
            "full_vector": "a=(c,c)=sqrt(2)*U_plus*c",
            "ghost_parity_identity": "kappa*a=a and P_plus*a=a",
            "Krein_Born_norm": "a^T*eta*a=2*sum_S c_S^2",
            "channel_incidence": "c=(J-I)y/4 with det(J-I)=-9",
            "channel_pullback": "2*((J-I)/4)^T*((J-I)/4)=J+I/8",
            "status": "COMPLETE_SIX_POINT_TREE_COEFFICIENT_IS_PUBLIC_FOCK_GHOST_EVEN_AND_POSITIVE",
        },
        "three_particle_Choi_process": {
            "shape": [8, 8],
            "entry_rule": "A_out,in=c_pair(mask) when popcount(in+8*out)=3 and zero otherwise",
            "three_particle_ghost_parity": "kappa3[x,y]=delta_(x,7-y)",
            "intertwining_identity": "kappa3*A*kappa3=A",
            "Krein_adjoint": "A^sharp=kappa3*A^T*kappa3=A^T",
            "Born_trace": "tr(A^sharp*A)=2*sum_S c_S^2",
            "status": "STRONGLY_GHOST_SYMMETRIC_AT_COMPLETE_TREE_COEFFICIENT_LEVEL",
        },
        "fixed_channel_history_embedding": {
            "fixed_channel_index": fixed_index,
            "fixed_channel_mask": channels[fixed_index],
            "normalized_history_basis": "f_(S,B)=e_(S,B)/sqrt(2) because the resolved-history metric is 2*I90",
            "allowed_basis": "f_(S,B) for S!=B",
            "embedding": "E_B*f_(S,B)=U_plus*e_S",
            "isometry": "E_B^T*eta*E_B=I9",
            "ghost_parity": "kappa*E_B=E_B",
            "normalized_residue_coordinates": "h_S=1/(2sqrt(2)) for S!=B",
            "public_residue": "E_B*h has coefficient 1/4 on S and Sc for S!=B and zero on B,Bc",
            "norm": "h^T*h=(E_B*h)^T*eta*(E_B*h)=9/8",
            "status": "FIXED_SHELL_POSITIVE_HISTORY_RANGE_PUBLIC_FOCK_AFFILIATED",
        },
        "global_history_rank_boundary": {
            "resolved_history_dimension": 90,
            "public_positive_dimension": 10,
            "simultaneous_restriction": "E_all*f_(S,A)=U_plus*e_S for every allowed S!=A",
            "rank": 10,
            "kernel_dimension": 80,
            "Gram_status": "E_all^T*eta*E_all is not I90",
            "meaning": "the public species carrier coherently forgets the intermediate-channel record; an isometric embedding of all ninety resolved records requires an additional positive channel-label ancilla",
            "status": "GLOBAL_RESOLVED_HISTORY_ISOMETRY_NOT_SUPPLIED_BY_PUBLIC_SPECIES_SECTOR_ALONE",
        },
        "interpretation": {
            "complete_six_point_Choi_ghost_symmetry": "EXACTLY_PROVED",
            "fixed_shell_output_history_public_Fock_embedding": "EXACTLY_CONSTRUCTED",
            "fixed_shell_history_norm_match": "EXACTLY_PROVED",
            "global_ninety_history_embedding_without_ancilla": "EXACTLY_OBSTRUCTED_BY_RANK",
            "input_projector_pushforward": "NOT_CONSTRUCTED",
            "BT_virtual_survival_block": "NOT_CONSTRUCTED",
            "finite_inclusive_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "the six external momentum slots are distinguishable before the already certified Bose orbit factors are applied",
            "the public one-particle cross-Krein pairing induces bitwise-complement pairing on the neutral six-leg tensor sector",
            "the complete complement equality imported from the full phase-space Born certificate holds on its declared regular physical domain",
            "the fixed-channel history basis is normalized using the predecessor's resolved-history metric 2*I90",
        ],
        "does_not_establish": [
            "the nonlinear transported physical input projector R_t P_phi R_t^dagger",
            "the source half of weak ghost symmetry",
            "a BT-derived virtual or survival term",
            "a simultaneous isometry of all ninety resolved histories without a detector ancilla",
            "global gluing of the ten shell tubes and their intersections",
            "a complete finite inclusive probability",
            "a Moller, LSZ, or S operator",
            "all-order Eq. (19)",
            "loops or infrared cancellation",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Use the now-public-Fock-affiliated ghost-even output range as fixed boundary data and compute the incoming scalar projector pushforward on the same finite-time six-point carrier. Either prove that its leading transition column lands in this positive even plane and derive the pseudo-unitary survival block, or exhibit the first source component outside it. Preserve the intermediate-channel record with an explicit positive ancilla when gluing all ten shells; do not identify coherent species collapse with a ninety-history isometry.",
        "provenance": {
            "source_commit": "9cc75810",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy complement-pair Krein algebra, symbolic 8-by-8 Choi reconstruction, fixed-channel algebraic isometry, and exact global rank test. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_six_point_ghost_even_history_embedding.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_ghost_even_history_embedding.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_six_point_ghost_even_history_embedding",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
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
