#!/usr/bin/env python3
"""Certify the first obstruction to the combined Berger apparatus q1 crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION.json"
)
PAYLOAD = (
    P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_K_OBSTRUCTION_PAYLOAD.json"
)
REPORT = (
    P / "reports/berger-dynamical-apparatus-combined-q1-crosswalk-obstruction.md"
)
DEPENDENCIES = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "component_contract": P
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_unary": P
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "combined_q1_contract": P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT.json",
    "reduction_preflight": P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json",
    "rod_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "K_gate": P
    / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _principal_no_mixing_audit() -> dict[str, Any]:
    """Solve s A B = C s^2 coefficientwise for one detector.

    B mixes three global scalar-wave rods into four material transport rows;
    C is the independently allowed cotangent-side block.  A is invertible.
    The s and s^2 coefficients force B=C=0.
    """

    A = sp.Matrix(
        [
            [0, -1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, -1],
            [0, 0, 1, 0],
        ]
    )
    # Vectorize A*B=0 and C=0 for B,C in Mat(4,3).
    left = sp.kronecker_product(sp.eye(3), A)
    zero = sp.zeros(12)
    constraints = sp.diag(left, sp.eye(12))
    rank = int(constraints.rank())
    return {
        "global_rod_principal_symbol": "s^2 I_3",
        "material_rod_principal_symbol": "s A_4",
        "material_transport_matrix": [
            [int(value) for value in row] for row in A.tolist()
        ],
        "material_transport_determinant": int(A.det()),
        "unknown_constant_mixing_entries": 24,
        "coefficient_constraint_shape": list(constraints.shape),
        "coefficient_constraint_rank": rank,
        "constant_mixing_nullity": 24 - rank,
        "coefficient_equations": ["A_4 B=0 at s^1", "C=0 at s^2"],
        "conclusion": (
            "No constant row map can identify or mix a global scalar-wave "
            "rod with a first-order transported material-frame row."
        ),
    }


def _candidate_pushout(parent_payload: dict[str, Any]) -> dict[str, Any]:
    shared = [
        ("memory_0", 70, "m0"),
        ("memory_multiplier_0", 72, "p0"),
        ("memory_1", 71, "m1"),
        ("memory_multiplier_1", 73, "p1"),
        ("memory_0_plus", 80, "m0_plus"),
        ("memory_multiplier_0_plus", 82, "p0_plus"),
        ("memory_1_plus", 81, "m1_plus"),
        ("memory_multiplier_1_plus", 83, "p1_plus"),
    ]
    parent_rows = (
        parent_payload["carrier"]["physical_even_rows"]
        + parent_payload["carrier"]["odd_cotangent_rows"]
    )
    shared_names = {name for name, _index, _base in shared}
    parent_only = [name for name in parent_rows if name not in shared_names]
    if len(parent_only) != 48:
        raise AssertionError("parent-only row count drifted")
    return {
        "status": "CANDIDATE_REJECTED_AT_K_INTERFACE",
        "base_embedding": "identity on all ordered 108 rows",
        "shared_row_relations": [
            {
                "parent_row": name,
                "base_index": index,
                "base_row": base,
                "relation": "candidate semantic/action-role identification",
            }
            for name, index, base in shared
        ],
        "parent_only_rows": parent_only,
        "parent_only_row_count": len(parent_only),
        "candidate_row_count": 108 + len(parent_only),
        "role_separation": {
            "global_rods_RaI": (
                "six spacetime scalar rod fields with second-order wave "
                "unary blocks and spatial-diffeomorphism action"
            ),
            "material_rod_orientation_momentum": (
                "four detector-local material-frame canonical pairs with "
                "first-order clock transport"
            ),
            "polarization_pairs": (
                "new detector-local material polarization canonical pairs"
            ),
            "emitter_phase_pairs": (
                "new transported material phases; not the massive two-form "
                "emitter components K_b"
            ),
        },
        "unresolved_before_K_failure": [
            "row-level action-normalized compatibility of the four shared memory rows",
            "full sparse 156-row q1",
            "real involution and detector-smearing chain map",
            "zero-mode sectors, ranks, cohomology and contraction",
        ],
    }


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    gate = values["K_gate"]["K_Berger_gate"]
    parent = values["parent_payload"]
    no_mix = _principal_no_mixing_audit()
    if no_mix["constant_mixing_nullity"] != 0:
        raise AssertionError("principal-symbol separation ceased to be exact")
    closure = gate["existing_rod_linear_symmetry_completion"]
    if closure["current_real_rod_span_rank"] != 6:
        raise AssertionError("global rod span rank drifted")
    if closure["time_translation_closure_rank"] != 8:
        raise AssertionError("global rod closure rank drifted")
    if closure["constant_internal_6_by_6_completion_exists"]:
        raise AssertionError("linear K obstruction disappeared")
    witnesses = gate["background_components"]["rod_witnesses"]
    if len(witnesses) != 2 or not all(row["nonzero"] for row in witnesses):
        raise AssertionError("affine K rod witnesses drifted")
    pushout = _candidate_pushout(parent)
    return {
        "schema": (
            "closed-universe-berger-dynamical-apparatus-"
            "combined-q1-k-obstruction-payload-v1"
        ),
        "result_id": (
            "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_K_OBSTRUCTION_PAYLOAD"
        ),
        "coefficient_field": "Q(sqrt(10),sqrt(58),sqrt(145))",
        "declared_identification_class": (
            "constant row identifications and pairing-preserving constant "
            "linear mixing that preserve the typed principal-symbol category"
        ),
        "candidate_pushout": pushout,
        "first_incompatibility": {
            "interface": "row-level background-preserving linear K_Berger",
            "required_identity": "[K_Berger,q1]=0",
            "base_background_preserving": gate[
                "ordinary_linear_action_background_preserving"
            ],
            "affine_background_components": gate["background_components"],
            "global_rod_closure": closure,
            "parent_material_rows_cannot_supply_missing_directions": no_mix,
            "verdict": (
                "NO_COMBINED_LINEAR_K_MATRIX_IN_DECLARED_IDENTIFICATION_CLASS"
            ),
        },
        "minimal_repair": {
            "added_degree_zero_rows": 2,
            "added_degree_one_cotangent_rows": 2,
            "row_types": (
                "two global spacetime scalar rods closing the e0 orbit and "
                "their two signed cyclic cotangents"
            ),
            "repaired_base_row_count": 112,
            "prospective_identified_union_row_count": 160,
            "required_recomputation": [
                "eight-real-rod co-rotating background",
                "rod stress and Phi2",
                "112-row q1 and odd pairing",
                "background differential quotient",
                "row-level K matrix and commutator",
                "then the memory identification and remaining crosswalk interfaces",
            ],
            "not_a_repair": (
                "identifying the missing global rods with parent material "
                "orientation rows; the exact principal-symbol audit has "
                "zero constant mixing nullity"
            ),
        },
        "mutation_results": {
            "force_global_material_rod_identification": {
                "detected": no_mix["constant_mixing_nullity"] == 0,
                "reason": "second-order versus first-order principal symbol",
            },
            "add_only_one_global_real_rod": {
                "resulting_span_upper_bound": 7,
                "required_closure_rank": 8,
                "detected": True,
            },
            "drop_one_affine_rod_witness": {
                "remaining_nonzero_witness_count": 1,
                "detected": True,
            },
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": (
            "closed-universe-berger-dynamical-apparatus-"
            "combined-q1-crosswalk-obstruction-v1"
        ),
        "result_id": (
            "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION"
        ),
        "setting_id": values["parent"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_NO_BACKGROUND_PRESERVING_LINEAR_K_"
            "ON_DECLARED_COMBINED_CARRIER"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "interface_disposition": {
            "ordered_row_table_and_identifications": "PARTIAL_EXACT_CANDIDATE",
            "base_and_parent_embeddings": "PARTIAL_EXACT_CANDIDATE",
            "complete_sparse_combined_q1": "NO_CERTIFIED_MAP",
            "odd_pairing": "NO_CERTIFIED_MAP",
            "cohomological_degrees": "NO_CERTIFIED_MAP",
            "real_involution": "NO_CERTIFIED_MAP",
            "K_Berger_matrix": "OBSTRUCTED",
            "detector_smearing_chain_map": "NO_CERTIFIED_MAP",
            "typed_zero_mode_support": "NO_CERTIFIED_MAP",
            "cohomology_and_contraction": "NO_CERTIFIED_MAP",
        },
        "exact_obstruction": payload["first_incompatibility"],
        "minimal_repair": payload["minimal_repair"],
        "downstream_disposition": {
            "apparatus_physical_cohomology": "NO_CERTIFIED_MAP",
            "descended_pairing": "NO_CERTIFIED_MAP",
            "reduced_rank_two": "NO_CERTIFIED_MAP",
            "Z2_response": "NO_CERTIFIED_MAP",
            "relational_memory": "NO_CERTIFIED_MAP",
            "redshift": "NO_CERTIFIED_MAP",
            "q2_q3_and_quantum": "NO_CERTIFIED_MAP",
        },
        "next_gate": (
            "ADD_TWO_GLOBAL_RODS_AND_TWO_COTANGENTS_RECOMPUTE_"
            "THE_112_ROW_BASE_THEN_RETRY_THE_IDENTIFIED_UNION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction imports the "
            "complete 108-row Berger unary carrier, the 56-row action-derived "
            "material apparatus parent, the combined-q1 contract and the "
            "earlier exact Berger K gate by content hash. A typed candidate "
            "pushout identifies only the two memory fields, two memory "
            "multipliers and their four cotangents; all material orientation, "
            "polarization and emitter-phase rows remain distinct from the "
            "global scalar rods and massive two-form emitters. The candidate "
            "would have 156 rows. It fails before a combined q1 is promoted: "
            "the six global scalar-rod background has time-translation "
            "closure rank eight, no constant internal six-by-six completion, "
            "and explicit nonzero affine K0 witnesses at both detectors. "
            "The parent material rod pairs cannot supply the two missing "
            "global directions. Their unary principal symbol is first-order "
            "s A4 with det(A4)=1, whereas each global rod block is second-"
            "order s^2 I3. Coefficientwise solution of s A4 B=C s^2 has "
            "constraint rank 24 on 24 constant mixing variables and hence "
            "zero nullity per detector. Thus no pairing-preserving constant "
            "row identification or mixing in the declared typed class can "
            "produce a background-preserving linear K_Berger matrix commuting "
            "with q1 while leaving the certified 108-row base unchanged. The "
            "smallest certified repair is two new global degree-zero rod "
            "directions and two cyclic cotangents, giving a prospective "
            "112-row base and 160-row identified union after the rod "
            "background, stress, Phi2, unary and quotient are recomputed. "
            "This is an obstruction to the declared combined linear-K "
            "crosswalk, not to an affine K action or to the parent action. "
            "No isolated 56-row cohomology, reduced memory, Z2 response, "
            "redshift, q2/q3, positivity, particle or quantum claim follows."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_dynamical_apparatus_"
                "combined_q1_crosswalk_obstruction --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_dynamical_apparatus_"
                "combined_q1_crosswalk_obstruction"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger dynamical-apparatus combined-q1 obstruction

The most economical typed candidate identifies the two memories, two memory
multipliers and their cotangents with the existing 108-row memory sector.
Material orientation, polarization and emitter-phase pairs are distinct from
the six global scalar rods and the massive two-form emitters.  The resulting
candidate would have 156 rows.

It fails at the required linear K interface before cohomology is formed.
The six global rods have time-translation closure rank eight and no constant
six-by-six internal completion.  The apparent rod rows in the parent cannot
close this gap: their first-order transport symbol cannot mix by a constant
row map with the second-order scalar-wave symbol.  The exact coefficient
constraint has full rank and zero mixing nullity.

The smallest repair is two new global scalar rods plus their two cotangents,
followed by recomputation of the co-rotating rod background, stress, Phi2,
112-row unary complex and background quotient.  Only then can the prospective
160-row identified union be retried.  No isolated parent reduction or
nonlinear observer claim is promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
