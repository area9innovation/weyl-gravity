"""Fail-closed receiving contract for the retained mixed-ell3 branch projection."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACCEPTANCE = HERE / "certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json"
INPUT_SCHEMA = HERE / "schema/berger-residual-ell3-branch-basis-input-v1.schema.json"
READINESS_SCHEMA = HERE / "schema/berger-residual-ell3-branch-projection-readiness-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matmul(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _identity(rank: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(i == j)) for j in range(rank)]
        for i in range(rank)
    ]


def _synthetic_receipt() -> dict[str, object]:
    """Exercise the exact contraction and parity checks on a tiny branch model."""

    inclusion = [
        [Fraction(int(i == j)) for j in range(3)]
        for i in range(4)
    ]
    projection = [
        [Fraction(int(i == j)) for j in range(4)]
        for i in range(3)
    ]
    parity_ambient = [
        [Fraction((1, -1, 1, -1)[i] if i == j else 0) for j in range(4)]
        for i in range(4)
    ]
    parity_branch = [
        [Fraction((1, -1, 1)[i] if i == j else 0) for j in range(3)]
        for i in range(3)
    ]
    checks = {
        "projection_inclusion_identity": _matmul(projection, inclusion) == _identity(3),
        "parity_ambient_involution": _matmul(parity_ambient, parity_ambient) == _identity(4),
        "parity_branch_involution": _matmul(parity_branch, parity_branch) == _identity(3),
        "parity_inclusion_intertwines": _matmul(parity_ambient, inclusion)
        == _matmul(inclusion, parity_branch),
        "parity_projection_intertwines": _matmul(projection, parity_ambient)
        == _matmul(parity_branch, projection),
    }
    if not all(checks.values()):
        raise ValueError("synthetic branch-projection contraction failed")
    mutant = [row[:] for row in projection]
    mutant[0][0] = Fraction()
    if _matmul(mutant, inclusion) == _identity(3):
        raise ValueError("synthetic projection-normalization mutation escaped")
    return {
        "ambient_rank": 4,
        "branch_rank": 3,
        "branch_ids": [
            "Einstein_like",
            "extra_Weyl",
            "Maxwell_physical",
        ],
        "deformation_vertex_basis_ids": [
            "e_C2_dynamical",
            "o_C_dual_C_topological",
        ],
        "Euler_Lagrange_rank_by_deformation": {
            "e_C2_dynamical": 1,
            "o_C_dual_C_topological": 0,
        },
        "exact_checks": checks,
        "projection_normalization_mutation_rejected": True,
        "receipt_sha256": _canonical_hash(checks),
    }


def build() -> dict[str, object]:
    acceptance = json.loads(ACCEPTANCE.read_text())
    flags = acceptance.get("claim_flags", {})
    if (
        acceptance.get("result_state")
        != "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED_RESIDUAL_BRANCH_PROJECTION_OPEN"
        or flags.get("RETAINED_MIXED_ELL3_CONTACT_INDEPENDENTLY_REPLAYED") is not True
        or flags.get("EINSTEIN_EXTRA_WEYL_BRANCH_MIXING_COMPUTED") is not False
        or flags.get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("retained ell3 readiness dependency boundary drifted")

    source_paths = (
        "quantum-weyl/transfer/berger_residual_ell3_branch_projection_readiness.py",
        "quantum-weyl/transfer/berger_residual_ell3_branch_projection_readiness_certificate.py",
        "quantum-weyl/transfer/verify_berger_residual_ell3_branch_projection_readiness.py",
        "quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v1.schema.json",
        "quantum-weyl/transfer/schema/berger-residual-ell3-branch-projection-readiness-v1.schema.json",
        "quantum-weyl/transfer/tests/test_berger_residual_ell3_branch_projection_readiness.py",
        "quantum-weyl/reports/berger-residual-ell3-branch-projection-readiness.md",
    )
    source_manifest = {path: _sha256(ROOT / path) for path in source_paths}
    return {
        "schema": "quantum-weyl-berger-residual-ell3-branch-projection-readiness-v1",
        "result_id": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS",
        "result_state": "CONSUMER_READY_RESIDUAL_BRANCH_BASIS_INPUT_NOT_SUPPLIED",
        "lifecycle_layer": "CLASSICAL_RESIDUAL_INTERACTION_IMPORT_READINESS",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_ref": {
            "artifact_id": acceptance["result_id"],
            "path": "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json",
            "sha256": _sha256(ACCEPTANCE),
        },
        "input_contract": {
            "required_result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1",
            "manifest_schema": {
                "path": "quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v1.schema.json",
                "sha256": _sha256(INPUT_SCHEMA),
            },
            "ambient_retained_rank": 36,
            "coefficient_field": "Q(sqrt(10))",
            "factorial_convention": "suspended-graded-symmetric-factorial-v1",
            "required_artifact_ids": [
                "retained_q1",
                "dynamical_branch_ledger",
                "dynamical_branch_inclusion",
                "dynamical_branch_projection",
                "dynamical_branch_pairing_gram",
                "parity_operator",
                "real_structure",
                "K_Berger_weight_operator",
                "deformation_vertex_basis",
                "deformation_Euler_Lagrange_map",
                "topological_transgression_witness",
            ],
            "required_dynamical_gravity_branch_ids": [
                "Einstein_like",
                "extra_Weyl",
            ],
            "required_deformation_vertex_basis_ids": [
                "e_C2_dynamical",
                "o_C_dual_C_topological",
            ],
            "Maxwell_branch_carrier_required": True,
            "category_separation": "topological is a local deformation/vertex class, not a dynamical residual mode",
            "content_addressing": "git_commit_plus_blob_sha256_plus_internal_canonical_sha256",
        },
        "exact_acceptance_conditions": [
            "retained_row_order_matches_accepted_36_row_complex",
            "branch_labels_have_explicit_degree_parity_K_weight_and_sector",
            "dynamical_gravity_and_Maxwell_branch_lists_are_exhaustive_for_declared_projection_sector",
            "dynamical_branch_projection_times_inclusion_is_identity",
            "retained_q1_intertwines_inclusion_and_projection",
            "parity_is_an_involution_and_intertwines_both_maps",
            "K_Berger_weights_intertwine_both_maps",
            "real_structure_is_an_involution_and_intertwines_both_maps",
            "dynamical_branch_pairing_is_exact_nondegenerate_and_equals_the_pairing_pullback",
            "deformation_vertex_basis_is_exactly_e_and_o_without_particle_mode_identification",
            "Euler_Lagrange_map_has_rank_one_with_e_dynamical_and_o_topological",
            "topological_direction_has_a_normalized_transgression_or_nonmembership_witness",
            "ell3_mixing_entries_are_computed_by_exact_precomposition_and_postcomposition",
            "every_zero_mixing_entry_has_a_support_or_cancellation_witness",
            "graded_symmetry_and_cyclicity_are_replayed_in_branch_coordinates",
        ],
        "required_output": {
            "result_id": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_AND_MIXING_TABLE",
            "dynamical_mixing_axes": ["output_branch", "input_branch_1", "input_branch_2", "input_branch_3"],
            "deformation_vertex_axes": ["e_C2_dynamical", "o_C_dual_C_topological"],
            "required_ledgers": [
                "exact_nonzero_mixing_entries",
                "exact_zero_witnesses",
                "Einstein_like_extra_Weyl_mixing",
                "Maxwell_input_output_sectors",
                "parity_selection",
                "K_Berger_weight_selection",
                "cyclicity_defects",
                "deformation_vertex_action",
                "topological_transgression_and_centrality",
            ],
            "kinetic_or_pairing_health_inference_from_ell3_alone": "FORBIDDEN",
        },
        "synthetic_consumer_receipt": _synthetic_receipt(),
        "claim_flags": {
            "RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY": True,
            "EXACT_CONTRACTION_MUTATION_WITNESS": True,
            "RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE": False,
            "RESIDUAL_BRANCH_BASIS_ACCEPTED": False,
            "RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED": False,
            "RESIDUAL_ELL3_MIXING_TABLE_COMPUTED": False,
            "DEFORMATION_VERTEX_PROJECTION_COMPUTED": False,
            "TOPOLOGICAL_DEFORMATION_DIRECTION_CLASSIFIED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1_MANIFEST",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC readiness result freezes the exact receiving contract for "
            "projecting the independently accepted 25,950-coefficient retained mixed ell3 onto "
            "declared residual branches. The contract requires exact dynamical gravity and Maxwell "
            "branch carriers, inclusion and projection maps, pairing, parity, real structure and "
            "K_Berger weights. Separately, it requires the local deformation basis "
            "e=(W_+^2+W_-^2)/sqrt(2) and o=(W_+^2-W_-^2)/sqrt(2), its rank-one "
            "Euler-Lagrange map and a Pontryagin transgression witness. The topological o direction "
            "is not admitted as a third particle or dynamical branch. Every mixing entry is computed "
            "from the accepted tensor and every claimed zero to carry an exact witness. No branch "
            "basis manifest is supplied or accepted here, so no Einstein-like/extra-Weyl mixing, "
            "deformation-vertex action, topological centrality or branch-space ell3 has been computed. The finite classical "
            "interaction tensor cannot by itself change a unary kinetic signature or establish "
            "physical positivity. This is not residual quantum transfer, QME restoration, a "
            "Hadamard construction, a particle statement or a quantum result."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_residual_ell3_branch_projection_readiness_certificate --check", "status": "PASS"},
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_residual_ell3_branch_projection_readiness", "status": "PASS"},
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_residual_ell3_branch_projection_readiness.py -v", "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v1.schema.json", "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-residual-ell3-branch-projection-readiness-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS.json", "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "No residual branch-basis input exists in this change. Tier 1 validates the strict receiving contract, exact synthetic contraction and a rejected projection-normalization mutation; the full affected exact chain is mandatory when the manifest arrives.",
            "tier_3": "No shared PBW engine, classical source tensor, quantum lifecycle, paper theorem, Lorentzian analytic construction, QME status or release boundary changes in this readiness result.",
        },
    }
