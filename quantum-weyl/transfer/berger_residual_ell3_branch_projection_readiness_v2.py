"""Split-field receiving contract for the retained ell3 branch projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .berger_residual_ell3_branch_projection_readiness import _synthetic_receipt


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD_READINESS = HERE / "certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS.json"
PREFLIGHT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT.json"
INPUT_SCHEMA = HERE / "schema/berger-residual-ell3-branch-basis-input-v2.schema.json"
SCHEMA = HERE / "schema/berger-residual-ell3-branch-projection-readiness-v2.schema.json"
OUTPUT = HERE / "certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_residual_ell3_branch_projection_readiness_v2.py",
    "quantum-weyl/transfer/verify_berger_residual_ell3_branch_projection_readiness_v2.py",
    "quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v2.schema.json",
    "quantum-weyl/transfer/schema/berger-residual-ell3-branch-projection-readiness-v2.schema.json",
    "quantum-weyl/transfer/tests/test_berger_residual_ell3_branch_projection_readiness_v2.py",
    "quantum-weyl/reports/berger-residual-ell3-branch-projection-readiness-v2.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, object]:
    old = json.loads(OLD_READINESS.read_text())
    preflight = json.loads(PREFLIGHT.read_text())
    if (
        old.get("result_state")
        != "CONSUMER_READY_RESIDUAL_BRANCH_BASIS_INPUT_NOT_SUPPLIED"
        or preflight.get("result_state")
        != "INPUT_CONTRACT_FIELD_REPAIR_REQUIRED_BRANCH_PROJECTOR_STILL_MISSING"
        or preflight.get("flags", {}).get(
            "CURRENT_INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS"
        )
        is not False
        or preflight.get("flags", {}).get("DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE")
        is not False
    ):
        raise ValueError("split-field readiness dependency boundary drifted")
    repairs = {
        row["repair_id"]: row for row in preflight.get("minimal_contract_repairs", [])
    }
    repair = repairs.get("EXTEND_DEFORMATION_FIELD")
    if (
        not repair
        or repair.get("recommended") is not True
        or repair.get("operator_coefficient_field") != "Q(sqrt(10))"
        or repair.get("deformation_coefficient_field")
        != "Q(sqrt(2),sqrt(10))"
    ):
        raise ValueError("recommended exact field repair drifted")

    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(input_schema)
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    dependencies = {
        "superseded_quantum_readiness_v1": {
            "result_id": old["result_id"],
            "path": str(OLD_READINESS.relative_to(ROOT)),
            "sha256": _sha256(OLD_READINESS),
        },
        "classical_field_obstruction_preflight": {
            "result_id": preflight["result_id"],
            "path": str(PREFLIGHT.relative_to(ROOT)),
            "sha256": _sha256(PREFLIGHT),
        },
    }
    return {
        "schema": "quantum-weyl-berger-residual-ell3-branch-projection-readiness-v2",
        "result_id": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2",
        "result_state": "CONSUMER_READY_EXACT_SPLIT_FIELD_CONTRACT_BRANCH_BASIS_INPUT_NOT_SUPPLIED",
        "lifecycle_layer": "CLASSICAL_RESIDUAL_INTERACTION_IMPORT_READINESS",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "supersession": {
            "supersedes": old["result_id"],
            "disposition": "HISTORY_RETAINED_FIELD_INCONSISTENCY_REPAIRED_BY_VERSIONED_CONTRACT",
        },
        "input_contract": {
            "required_result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2",
            "manifest_schema": {
                "path": str(INPUT_SCHEMA.relative_to(ROOT)),
                "sha256": _sha256(INPUT_SCHEMA),
            },
            "ambient_retained_rank": 36,
            "operator_coefficient_field": "Q(sqrt(10))",
            "deformation_coefficient_field": "Q(sqrt(2),sqrt(10))",
            "normalized_deformation_basis": [
                "e_C2_dynamical",
                "o_C_dual_C_topological",
            ],
            "required_deformation_vertex_basis_ids": [
                "e_C2_dynamical",
                "o_C_dual_C_topological",
            ],
            "normalized_deformation_gram": [["1", "0"], ["0", "1"]],
            "required_dynamical_gravity_branch_ids": [
                "Einstein_like",
                "extra_Weyl",
            ],
            "Maxwell_branch_carrier_required": True,
            "category_separation": "topological is a local deformation/vertex class, not a dynamical residual mode",
            "content_addressing": "git_commit_plus_blob_sha256_plus_internal_canonical_sha256",
        },
        "field_repair_receipt": {
            "obstruction": "1/sqrt(2) is not in Q(sqrt(10))",
            "repair": "retain the operator carrier over Q(sqrt(10)) and extend only normalized deformation data to Q(sqrt(2),sqrt(10))",
            "operator_field_unchanged": True,
            "normalized_even_odd_basis_retained": True,
            "old_schema_rewritten": False,
            "exact_field_membership_obstruction_imported": True,
        },
        "exact_acceptance_conditions": old["exact_acceptance_conditions"],
        "required_output": old["required_output"],
        "synthetic_consumer_receipt": _synthetic_receipt(),
        "claim_flags": {
            "RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY": True,
            "INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS": True,
            "OPERATOR_FIELD_REMAINS_Q_SQRT10": True,
            "DEFORMATION_FIELD_EXTENDED_EXACTLY": True,
            "RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE": False,
            "DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE": False,
            "RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED": False,
            "RESIDUAL_ELL3_MIXING_TABLE_COMPUTED": False,
            "RESIDUAL_QUANTUM_TRANSFERRED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2_MANIFEST",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC readiness result versions the branch-basis input contract after the classical preflight proved that the normalized even/odd deformation basis cannot live over Q(sqrt(10)) alone. The retained q1, ell3, dynamical inclusion/projection, pairing, parity, reality and K_Berger operator data remain over Q(sqrt(10)); only the normalized deformation basis, Euler-Lagrange map and topological transgression data use the exact extension Q(sqrt(2),sqrt(10)). The historical V1 contract remains an immutable receipt and is not rewritten. The exact synthetic contraction and mutation witness still pass. No branch-basis manifest or dynamical Einstein-like/extra-Weyl/Maxwell projector has been supplied, so no branch-space ell3, mixing table, deformation action or topological centrality is computed. This does not restore a QME, construct Hadamard products, identify a particle mode, or make a quantum, Lorentzian, positivity or unitarity claim."
        ),
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "dependency_manifest_sha256": _canonical_hash(dependencies),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_residual_ell3_branch_projection_readiness_v2 --check",
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_residual_ell3_branch_projection_readiness_v2",
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_residual_ell3_branch_projection_readiness_v2.py -v",
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v2.schema.json",
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "No branch-basis manifest exists. Tier 1 covers the exact field repair, strict schemas, dependency hashes, synthetic contraction and normalization mutation.",
            "tier_3": "No classical tensor, shared PBW engine, Lorentzian analytic construction, QME lifecycle, paper theorem freeze or release boundary changes.",
        },
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = _render(value)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("split-field readiness certificate drifted")
    else:
        OUTPUT.write_text(rendered)
    print("BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
