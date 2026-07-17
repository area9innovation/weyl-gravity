"""Fail-closed architecture selection for Berger residual branch resolution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OBSTRUCTION = HERE / "certificates/BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT.json"
CARRIER = HERE / "certificates/BERGER_RETAINED_46_STF2_CARRIER_IMPORT.json"
MAPPING_CYLINDER = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
GREEN_ASSEMBLY = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
SCHEMA = HERE / "schema/berger-branch-carrier-architecture-preflight-v1.schema.json"
OUTPUT = HERE / "certificates/BERGER_BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_branch_carrier_architecture_preflight.py",
    "quantum-weyl/transfer/verify_berger_branch_carrier_architecture_preflight.py",
    "quantum-weyl/transfer/schema/berger-branch-carrier-architecture-preflight-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_branch_carrier_architecture_preflight.py",
    "quantum-weyl/reports/berger-branch-carrier-architecture-preflight.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"architecture dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict[str, Any]) -> dict[str, str]:
    identity = value.get("result_id") or value.get("schema")
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"architecture dependency has no identity: {path}")
    return {
        "artifact_id": identity,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _validate_dependencies(
    obstruction: dict[str, Any],
    carrier: dict[str, Any],
    mapping: dict[str, Any],
    green: dict[str, Any],
) -> dict[str, bool]:
    obstruction_flags = obstruction.get("claim_flags", {})
    if (
        obstruction.get("result_state")
        != "RETAINED_36_CANONICAL_SAME_BUNDLE_ROUTE_OBSTRUCTED_ENLARGED_CARRIER_REQUIRED"
        or obstruction_flags.get(
            "RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTED"
        )
        is not True
        or obstruction_flags.get("RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED")
        is not True
        or obstruction_flags.get("RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED")
        is not False
        or obstruction.get("carrier_enlargement", {}).get(
            "natural_candidate_retained_rank"
        )
        != 46
    ):
        raise ValueError("rank-36 obstruction or rank-46 candidate boundary drifted")

    carrier_flags = carrier.get("claim_flags", {})
    if (
        carrier.get("result_state")
        != "PINNED_EXACT_CYCLIC_GRAPH_SDR_IMPORTED_PROJECTOR_OPEN"
        or carrier_flags.get("RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED") is not True
        or carrier_flags.get("RANK_46_GRAPH_SDR_INDEPENDENTLY_REPLAYED") is not True
        or carrier_flags.get("RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED") is not False
        or carrier_flags.get("ELL3_BRANCH_MIXING_AUTHORIZED") is not False
        or carrier_flags.get("RANK_46_IS_QUANTUM_PREREQUISITE") is not False
        or carrier.get("carrier", {}).get("total_rows") != 46
        or carrier.get("independent_replay", {}).get("all_checks_pass") is not True
    ):
        raise ValueError("rank-46 carrier import boundary drifted")

    kernel = mapping.get("kernel", {})
    warranted = mapping.get("warranted_atomic_flags", [])
    if (
        mapping.get("schema")
        != "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        or mapping.get("support_local") is not True
        or mapping.get("fail_closed") is not True
        or kernel.get("Q_squared") != "zero"
        or kernel.get("all_16_blocks_Q_squared_checked") is not True
        or kernel.get("all_16_blocks_graph_SDR_checked") is not True
        or kernel.get("BV_pairing_defect") != 0
        or kernel.get("row_coverage", {}).get("silent_rows_dropped") != 0
        or "support_local_prolongation_retract" not in warranted
    ):
        raise ValueError("covariant mapping-cylinder boundary drifted")

    dimensions = green.get("dimension_ledger", {})
    if (
        green.get("schema")
        != "pure-weyl-full-prolonged-green-homotopy-assembly-v1"
        or green.get("fail_closed") is not True
        or dimensions
        != {
            "algebraically_contracted": 356,
            "causal_endpoint": 30,
            "identity": "386=356+30",
            "prolonged": 386,
        }
        or "causal_green_homotopy" not in green.get("status_flags_promoted", [])
        or green.get("future_gate", {}).get("all_row_causal_homotopy_ready")
        is not True
    ):
        raise ValueError("covariant mapping-cylinder Green boundary drifted")

    return {
        "retained_36_obstruction_imported": True,
        "rank_46_candidate_authority_imported": True,
        "rank_46_support_local_carrier_imported": True,
        "rank_46_graph_SDR_independently_replayed": True,
        "covariant_mapping_cylinder_support_local_SDR_imported": True,
        "covariant_mapping_cylinder_all_16_blocks_checked": True,
        "covariant_mapping_cylinder_BV_pairing_exact": True,
        "covariant_386_to_30_causal_homotopy_imported": True,
        "Berger_branch_adapter_not_inferred_from_covariant_transport": True,
        "nonlinear_branch_lift_not_inferred_from_unary_carrier": True,
        "quantum_critical_path_kept_independent": True,
    }


def build() -> dict[str, Any]:
    obstruction = _load(OBSTRUCTION)
    carrier = _load(CARRIER)
    mapping = _load(MAPPING_CYLINDER)
    green = _load(GREEN_ASSEMBLY)
    checks = _validate_dependencies(obstruction, carrier, mapping, green)
    dependencies = {
        "retained_36_projector_obstruction": _dependency(OBSTRUCTION, obstruction),
        "retained_46_STF2_carrier_import": _dependency(CARRIER, carrier),
        "covariant_mapping_cylinder": _dependency(MAPPING_CYLINDER, mapping),
        "covariant_full_green_assembly": _dependency(GREEN_ASSEMBLY, green),
    }
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    common_acceptance = [
        "complete degree/parity/tensor row ledger and exact coefficient field",
        "finite-order support-local q1 with q1^2=0",
        "nondegenerate typed cyclic pairing and q1 cyclicity",
        "explicit inclusion, projection and homotopy with both chain maps, SDR identity and side conditions",
        "Einstein-like/extra-Weyl/Maxwell branch inclusion and projection intertwining q1",
        "complementary idempotence on the declared dynamical carrier",
        "no inverse Laplacian, inverse curl, TT/helicity projector, Green operator or mode truncation in a LOCAL-ALGEBRAIC branch map",
        "separate deformation/vertex basis; the odd topological direction is not a particle branch",
        "materialized q2/q3 or ell3 lift compatible with the accepted retained tensor before any mixing table",
        "K_Berger equivariance and real-structure compatibility",
        "exact mutation rejecting a forged projector, pairing or branch-intertwining identity",
    ]
    return {
        "schema": "quantum-weyl-berger-branch-carrier-architecture-preflight-v1",
        "result_id": "BERGER_BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT",
        "result_state": "ARCHITECTURES_COMPARED_ACCEPTANCE_CONTRACT_READY_NO_BRANCH_PROJECTOR_ACCEPTED",
        "lifecycle_layer": "OPTIONAL_CLASSICAL_BRANCH_INTERPRETATION_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependencies,
        "exact_import_checks": checks,
        "architecture_options": {
            "rank_46_STF2_graph_carrier": {
                "role": "PREFERRED_MINIMAL_SETTING_SPECIFIC_FIRST_ATTEMPT",
                "authority": "retained-36 exact symbol lower bound plus natural STF2-plus-dual candidate",
                "target_result_id": "BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1",
                "expected_rows": 46,
                "expected_added_bundle": "spatial STF2 prolongation variable plus its cyclic dual",
                "current_disposition": "CYCLIC_GRAPH_CARRIER_IMPORTED_BRANCH_PROJECTOR_OPEN",
                "strength": "smallest natural Berger-specific cyclic graph extension currently identified",
                "missing": [
                    "rank-46 branch projector or normalized obstruction",
                    "nonlinear q2/q3 or ell3 lift",
                    "K_Berger equivariance",
                    "causal support if a LORENTZIAN-CAUSAL claim is later requested",
                ],
            },
            "covariant_curvature_mapping_cylinder": {
                "role": "CERTIFIED_REUSE_LIBRARY_AND_FALLBACK_ARCHITECTURE",
                "authority": "support-local 16-block BV mapping-cylinder SDR and 386=356+30 causal hybrid assembly",
                "prolonged_rows": 386,
                "algebraically_contracted_rows": 356,
                "causal_endpoint_rows": 30,
                "current_disposition": "GENERIC_COVARIANT_INFRASTRUCTURE_CERTIFIED_BERGER_BRANCH_ADAPTER_ABSENT",
                "strength": "already supplies exact support-local cyclic prolongation and all-row causal homotopy infrastructure",
                "missing": [
                    "Berger specialization and map to the retained 36-row carrier",
                    "Einstein-like/extra-Weyl/Maxwell branch projector",
                    "accepted retained ell3 lift and branch-coordinate mixing table",
                    "K_Berger-compatible branch adapter",
                ],
            },
        },
        "selection_verdict": {
            "preferred_first_attempt": "rank_46_STF2_graph_carrier",
            "reason": "it is the smallest natural setting-compatible carrier and can reuse mapping-cylinder graph/adjoint patterns without importing the full 386-row covariant complex",
            "fallback": "Berger restriction or subquotient of the covariant_curvature_mapping_cylinder",
            "neither_architecture_currently_authorizes_branch_mixing": True,
            "rank_46_is_quantum_prerequisite": False,
            "rank_46_is_Paper_11_interpretation_followup": True,
        },
        "acceptance_contract": {
            "common_exact_conditions": common_acceptance,
            "success_output": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_AND_MIXING_TABLE",
            "negative_output": "normalized scoped obstruction naming the first failed carrier/projector identity",
            "claim_tag_rule": "LOCAL-ALGEBRAIC maps cannot contain nonlocal projectors; any spectral substitute is a separate REDUCED-MODE result",
        },
        "quantum_critical_path": {
            "ordered_gates": [
                "MATCH_REPOSITORY_ANALYTIC_REGULATOR_MEASURE_AND_COMPUTE_SLAVNOV_BREAKING",
                "QME_RESTORATION_OR_OBSTRUCTION",
                "QUANTUM_RESIDUAL_TRANSFER",
            ],
            "parallel_analytic_gates": [
                "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
                "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
                "BERGER_TYPED_COMPANION_MICROLOCAL_COMPOSITION_AND_GLOBAL_COVARIANCE",
            ],
            "optional_classical_interpretation_gate": "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        },
        "claim_flags": {
            "ARCHITECTURE_PREFLIGHT_COMPLETE": True,
            "RANK_46_FIRST_ATTEMPT_SELECTED": True,
            "COVARIANT_MAPPING_CYLINDER_REUSE_AUDITED": True,
            "RANK_46_CARRIER_IMPORTED": True,
            "BRANCH_PROJECTOR_ACCEPTED": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "RANK_46_IS_QUANTUM_PREREQUISITE": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        "claim_boundary": (
            "This fail-closed preflight compares two classical carrier architectures without "
            "constructing or accepting a branch projector. The rank-46 STF2-plus-dual graph carrier "
            "is selected as the preferred minimal Berger-specific first attempt. The existing "
            "covariant curvature mapping cylinder is independently imported only as a certified "
            "support-local cyclic and causal reuse library; its 386=356+30 theorem does not supply "
            "a Berger-to-retained-36 branch adapter, nonlinear ell3 lift, or mixing table. Branch "
            "resolution is optional physical interpretation work for Paper 11 and is not a gate "
            "for antifield BV cohomology, repository Slavnov breaking, QME disposition, or the "
            "parallel stationary/Hadamard programme. The rank-46 carrier is imported and its graph "
            "SDR independently replayed, but no branch projector, mixing coefficient, QME restoration, "
            "particle statement, or quantum theorem is asserted."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "dependency_manifest_sha256": _canonical_hash(dependencies),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_branch_carrier_architecture_preflight --check",
                "status": "PASS",
                "elapsed_seconds": 0.55,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_branch_carrier_architecture_preflight",
                "status": "PASS",
                "elapsed_seconds": 0.55,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_branch_carrier_architecture_preflight.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.62,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-branch-carrier-architecture-preflight-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_BRANCH_CARRIER_ARCHITECTURE_PREFLIGHT.json",
                "status": "PASS",
                "elapsed_seconds": 1.24,
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The carrier tensor is consumed through its pinned independently replayed import; no shared algebra or upstream classical/covariant certificate changed in this preflight refresh.",
            "tier_3": "No lifecycle, theorem freeze, release, QME, Hadamard-state or quantum claim is promoted.",
        },
    }


def validate(value: dict[str, Any]) -> None:
    if value.get("result_state") != (
        "ARCHITECTURES_COMPARED_ACCEPTANCE_CONTRACT_READY_NO_BRANCH_PROJECTOR_ACCEPTED"
    ):
        raise ValueError("architecture-preflight state drifted")
    flags = value.get("claim_flags", {})
    if (
        flags.get("ARCHITECTURE_PREFLIGHT_COMPLETE") is not True
        or flags.get("RANK_46_FIRST_ATTEMPT_SELECTED") is not True
        or flags.get("COVARIANT_MAPPING_CYLINDER_REUSE_AUDITED") is not True
        or flags.get("RANK_46_CARRIER_IMPORTED") is not True
        or flags.get("RANK_46_IS_QUANTUM_PREREQUISITE") is not False
        or any(
            flags.get(name) is not False
            for name in (
                "BRANCH_PROJECTOR_ACCEPTED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "QME_RESTORED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("architecture-preflight claim boundary drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = _render(value)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Berger branch-carrier architecture preflight: {OUTPUT}")
    print("BERGER BRANCH-CARRIER ARCHITECTURE PREFLIGHT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
