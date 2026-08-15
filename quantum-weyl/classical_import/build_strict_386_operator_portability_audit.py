#!/usr/bin/env python3
"""Classify the serialization contract for every strict 386 unary operator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.md"

PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
ENDPOINT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
ENDPOINT_WITNESS = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
GENERALIZED = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
MAPPING_KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
MAPPING = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
GREEN_TRANSFER = ROOT / "covariant_completion/certificates/adjoint_tractor_green_transfer.json"
CURVED_PBW = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_curved_pbw.json"
FULL_GREEN = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"

SOURCE_PATHS = (
    ROOT / "covariant_completion/auxiliary_equivalence/generalized_retract.py",
    ROOT / "covariant_completion/curved_retract/curvature_auxiliary_chain_map.py",
    ROOT / "covariant_completion/curved_retract/curvature_mapping_cylinder_kernel.py",
    ROOT / "covariant_completion/curved_operator/prolonged_hybrid_algebraic_projector.py",
    ROOT / "covariant_completion/curved_operator/full_prolonged_green_homotopy_assembly.py",
)

AUTHORITIES = (
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed 386-row basis and pairing"),
    (ENDPOINT, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "portable endpoint q1 summary"),
    (ENDPOINT_WITNESS, "strict-cylinder-coordinate-to-covariant-symmetric-four-jet-v1", "endpoint coefficient tables"),
    (GENERALIZED, "pure-weyl-support-local-generalized-auxiliary-retract-v1", "executable auxiliary differential and SDR hashes"),
    (MAPPING_KERNEL, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "mapping-cylinder operator-word matrices"),
    (MAPPING, "pure-weyl-curvature-mapping-cylinder-substitution-v1", "coefficientwise-complete producer summary"),
    (HYBRID, "pure-weyl-prolonged-hybrid-algebraic-projector-v1", "hybrid local SDR formulas and hashes"),
    (GREEN_TRANSFER, "pure-weyl-adjoint-tractor-green-transfer-v1", "trace-free Green transfer theorem"),
    (CURVED_PBW, "adjoint-tractor-bgg-curved-pbw-v1", "curved BGG/PBW transfer dependency"),
    (FULL_GREEN, "pure-weyl-full-prolonged-green-homotopy-assembly-v1", "full causal homotopy theorem"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def identity(value: dict[str, Any]) -> str | None:
    if value.get("result_id"):
        return value["result_id"]
    if value.get("schema"):
        return value["schema"]
    if value.get("schema_version") == 1 and "curved_HPL" in value:
        return "adjoint-tractor-bgg-curved-pbw-v1"
    return None


def build() -> dict[str, Any]:
    loaded = {path: json.loads(path.read_text()) for path, _, _ in AUTHORITIES}
    for path, expected, _ in AUTHORITIES:
        if identity(loaded[path]) != expected:
            raise ValueError(f"authority identity drift: {path}")

    pairing = loaded[PAIRING]
    endpoint = loaded[ENDPOINT]
    endpoint_witness = loaded[ENDPOINT_WITNESS]
    generalized = loaded[GENERALIZED]
    mapping_kernel = loaded[MAPPING_KERNEL]
    mapping = loaded[MAPPING]
    hybrid = loaded[HYBRID]
    transfer = loaded[GREEN_TRANSFER]
    pbw = loaded[CURVED_PBW]
    full_green = loaded[FULL_GREEN]

    if pairing["component_basis"]["dimension"] != 386:
        raise ValueError("component basis drift")
    if endpoint["coefficientwise_identification"]["arrow_table_counts"]["total"] != 80:
        raise ValueError("endpoint table drift")
    if not mapping["coefficientwise_complete_prolonged_Q"]:
        raise ValueError("mapping producer is no longer coefficientwise complete")
    if not hybrid["composite_SDR"]["support_local"]:
        raise ValueError("hybrid local SDR drift")
    if not full_green["causal_green_homotopy"]:
        raise ValueError("source causal theorem drift")

    contracts = [
        {
            "id": "FINITE_COMPONENT_JET_TABLE",
            "applies_to": "finite-order local differential operators on the fixed component carrier",
            "required_fields": [
                "source and target basis digests",
                "source row, target row and derivative multiindex",
                "exact rational or declared algebraic coefficient",
                "maximum differential order and complete multiindex coverage",
                "formal-adjoint convention and canonical content digest",
            ],
            "independent_replay": "The receiver reconstructs the sparse jet matrix and replays composition, nilpotency and adjoint identities without running the producer.",
        },
        {
            "id": "FINITE_SPARSE_COMPONENT_MAP",
            "applies_to": "support-local algebraic maps, inclusions, projections and contracting homotopies",
            "required_fields": [
                "source and target basis digests",
                "source row, target row and exact coefficient or local operator entry",
                "degree, support-locality and complete row coverage",
                "canonical content digest",
            ],
            "independent_replay": "The receiver reconstructs the map and checks SDR, projector, chain-map and cyclic identities on the serialized entries.",
        },
        {
            "id": "ANALYTIC_GREEN_ACTION",
            "applies_to": "nonlocal advanced or retarded continuous operators",
            "required_fields": [
                "represented source and target test/distribution spaces and topology",
                "receiver-executable action, convergent operator name, or distribution-kernel representation",
                "advanced or retarded orientation and causal-support theorem",
                "domain, continuity and uniqueness statement",
                "pairing convention, adjoint action and homotopy identities",
                "analytic assumptions, dependency tag and canonical provenance",
            ],
            "independent_replay": "A theorem-level formula may prove existence, but component replay requires an imported action or kernel on declared represented spaces; a finite jet table cannot encode a genuinely nonlocal Green map.",
        },
    ]

    coefficient_tables = mapping["coefficient_tables"]
    operator_inventory = [
        {
            "id": "ENDPOINT_Q1_30",
            "kind": "FINITE_COMPONENT_JET_TABLE",
            "status": "PORTABLE_COMPONENT_BYTES",
            "carrier_rows": 30,
            "evidence": [endpoint["result_id"], endpoint_witness["schema"]],
            "present": {
                "arrow_tables": endpoint["coefficientwise_identification"]["arrow_table_counts"]["total"],
                "common_nonzero_coefficients": endpoint["coefficientwise_identification"]["common_nonzero_coefficients"],
                "Bach_columns_checked": endpoint["coefficientwise_identification"]["gate_bach_columns_matching"],
            },
            "missing": [],
            "boundary": "This is the thirty-row endpoint only, not the 356-row complement.",
        },
        {
            "id": "FULL_Q1_386",
            "kind": "FINITE_COMPONENT_JET_TABLE",
            "status": "PRODUCER_COEFFICIENTWISE_COMPLETE_RECEIVER_TABLE_ABSENT",
            "carrier_rows": 386,
            "evidence": [mapping["schema"], generalized["schema"], endpoint["result_id"]],
            "present": {
                "endpoint_rows_portable": 30,
                "complement_rows_declared": 356,
                "mapping_block_rows": len(mapping_kernel["complete_16_block_degree_ledger"]),
                "attachment_table_multiindices": {
                    key: value["coefficient_multiindices"] for key, value in coefficient_tables.items()
                },
                "prolonged_Q_digest": mapping_kernel["matrix_sha256"]["prolonged_Q"],
                "auxiliary_original_differential_digest": generalized["matrix_sha256"]["original_differential"],
            },
            "missing": [
                "one receiver-readable 386-row sparse jet table",
                "serialized generalized-auxiliary differential entries",
                "serialized T_state, A_equation, B_identity and formal-adjoint entries",
                "serialized autonomous curvature differential entries",
            ],
            "boundary": "Producer completeness and matrix hashes do not let an independent receiver reconstruct the component operator.",
        },
        {
            "id": "H_ALG_AND_PROJECTORS_386",
            "kind": "FINITE_SPARSE_COMPONENT_MAP",
            "status": "EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT",
            "carrier_rows": 386,
            "evidence": [hybrid["schema"], generalized["schema"], mapping_kernel["schema"]],
            "present": {
                "composite_formula": hybrid["composite_SDR"]["homotopy_in_project_convention"],
                "H_alg_formula": hybrid["composite_SDR"]["H_alg"],
                "auxiliary_H_alg_digest": hybrid["component_projectors"]["auxiliary"]["sha256"]["H_alg"],
                "mapping_homotopy_digest": mapping_kernel["matrix_sha256"]["homotopy"],
                "projector_identities_exact": True,
            },
            "missing": ["386-row H_alg, P_alg and P_end entry tables"],
            "boundary": "Exact executable matrices and their hashes are reproduction inputs, not portable receiver bytes.",
        },
        {
            "id": "ENDPOINT_INCLUSION_PROJECTION_386_30",
            "kind": "FINITE_SPARSE_COMPONENT_MAP",
            "status": "EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT",
            "carrier_rows": 386,
            "evidence": [hybrid["schema"], generalized["schema"], mapping_kernel["schema"]],
            "present": {
                "inclusion_formula": hybrid["composite_SDR"]["inclusion"],
                "projection_formula": hybrid["composite_SDR"]["projection"],
                "auxiliary_inclusion_digest": generalized["matrix_sha256"]["inclusion"],
                "auxiliary_projection_digest": generalized["matrix_sha256"]["projection"],
                "mapping_inclusion_digest": mapping_kernel["matrix_sha256"]["inclusion"],
                "mapping_projection_digest": mapping_kernel["matrix_sha256"]["projection"],
            },
            "missing": ["386-by-30 inclusion and 30-by-386 projection entry tables"],
            "boundary": "The formulas establish the SDR, but the receiver cannot replay i_end^sharp=p_end from hashes alone.",
        },
        {
            "id": "ENDPOINT_GREEN_PLUS_MINUS_30",
            "kind": "ANALYTIC_GREEN_ACTION",
            "status": "THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT",
            "carrier_rows": 30,
            "evidence": [transfer["schema"], "adjoint-tractor-bgg-curved-pbw-v1", full_green["schema"]],
            "present": {
                "tracefree_transfer_formula": transfer["transfer_theorem"]["formula"],
                "tracefree_causal_green_homotopy": transfer["tracefree_causal_green_homotopy"],
                "curved_BGG_keys_exact": transfer["curved_BGG_gate"]["all_required_keys_true"],
                "parent_green_homotopy_transferred_in_PBW_file": pbw["theorem_boundary"]["parent_green_homotopy_transferred"],
                "endpoint_assembly_formula": full_green["endpoint_channel_assembly"]["homotopy_formula"],
            },
            "missing": [
                "represented endpoint source and target spaces",
                "receiver-executable advanced and retarded action or kernel",
                "component action ledger for adjoint and homotopy replay",
            ],
            "boundary": "The causal transfer theorem remains valid; this audit records only that its operator action is not a portable component artifact.",
        },
        {
            "id": "FULL_GREEN_PLUS_MINUS_386",
            "kind": "ANALYTIC_GREEN_ACTION",
            "status": "THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT",
            "carrier_rows": 386,
            "evidence": [full_green["schema"], pairing["result_id"]],
            "present": {
                "causal_green_homotopy_theorem": full_green["causal_green_homotopy"],
                "assembly_formula": full_green["full_hybrid_assembly"]["formula"],
                "homotopy_identity_exact_conditionally": full_green["full_hybrid_assembly"]["algebraic_identity_exact_conditionally"],
                "graded_adjoint_exact_conditionally": full_green["full_hybrid_assembly"]["graded_adjoint_exact_conditionally"],
                "projector_level_suspended_adjoint_replayed": pairing["operator_adjoint_disposition"]["projector_level_suspended_green_adjoint_replayed"],
            },
            "missing": [
                "portable endpoint Green action",
                "portable H_alg, inclusion and projection tables",
                "receiver-executable full advanced and retarded action or kernel",
                "componentwise full homotopy and suspended-adjoint replay",
            ],
            "boundary": "Formal composition and support transfer certify the theorem but are not a serialized nonlocal operator action.",
        },
    ]

    status_counts: dict[str, int] = {}
    for item in operator_inventory:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-operator-portability-audit-v1",
        "result_id": "STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1",
        "result_kind": "TYPED_OPERATOR_SERIALIZATION_AND_ANALYTIC_PORTABILITY_AUDIT",
        "result_state": "LOCAL_OPERATOR_SERIALIZATION_TRACTABLE_GREEN_ACTION_REPRESENTATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "2d92392e9840eed7a2da81551a25e33d7f0815d1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "What must be serialized for independent replay of every strict 386-row unary operator, and which current authorities already provide portable bytes rather than formulas or producer hashes?",
        "answer": "The operator gate must split by mathematical type. The endpoint q1 is already a portable finite jet table. The full q1, H_alg, projectors, inclusion and projection are exact and executable in current producers, but only their formulas, summaries and hashes cross the certificate boundary; they need finite sparse component or jet tables. Advanced and retarded Green homotopies are nonlocal analytic maps. The current causal theorem and its support/adjoint transfer remain valid, but no receiver-executable kernel, convergent name or represented action is serialized. Asking for a finite Green coefficient table is therefore the wrong contract. The next route is: serialize full local q1 first, serialize H_alg/i/p second, then import an analytic endpoint Green action on declared represented spaces and assemble the full action. Gate A, local D, q2, Hadamard and QME remain fail closed.",
        "carrier": {
            "basis_result": pairing["result_id"],
            "basis_digest": pairing["canonical_hashes"]["component_basis_sha256"],
            "pairing_digest": pairing["canonical_hashes"]["pairing_serialization_sha256"],
            "rows": 386,
            "split": "386=30+36+320",
        },
        "portability_contracts": contracts,
        "operator_inventory": operator_inventory,
        "status_counts": dict(sorted(status_counts.items())),
        "route_split": [
            {"rank": 1, "route": "STRICT_386_FULL_Q1_JET_TABLE", "kind": "FINITE_COMPONENT_JET_TABLE", "reason": "Every source calculation exists; the receiver table and common digest are the missing objects."},
            {"rank": 2, "route": "STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "kind": "FINITE_SPARSE_COMPONENT_MAP", "reason": "H_alg, P_alg, P_end, i_end and p_end are exact executable local maps and can be emitted without solving a new PDE."},
            {"rank": 3, "route": "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "kind": "ANALYTIC_GREEN_ACTION", "reason": "The theorem exists, but portability requires represented spaces and an action/kernel object rather than another finite matrix."},
            {"rank": 4, "route": "STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "kind": "ANALYTIC_GREEN_ACTION", "reason": "Assemble only after the local maps and endpoint action share the fixed 386-row convention."},
        ],
        "foundational_strength": {
            "finite_local_serialization_upper_bound": "PRA",
            "finite_local_choice_operation_added": False,
            "current_analytic_environment": "CLASSICAL_STANDARD_SMOOTH_DISTRIBUTIONAL",
            "weakest_base_for_analytic_green_action": "NOT_ESTABLISHED",
            "physics_implies_choice_principle": False,
            "note": "The finite tables add no infinite selection. The causal theorem's weakest foundational calibration cannot be inferred from that finite wrapper.",
        },
        "claim_flags": {
            "STRICT_386_OPERATOR_PORTABILITY_TYPES_CLASSIFIED": True,
            "STRICT_ENDPOINT_Q1_PORTABLE_COMPONENT_BYTES": True,
            "STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES": False,
            "STRICT_FULL_386_LOCAL_SDR_PORTABLE_COMPONENT_BYTES": False,
            "STRICT_ENDPOINT_GREEN_PORTABLE_ACTION_SERIALIZED": False,
            "STRICT_FULL_GREEN_PORTABLE_ACTION_SERIALIZED": False,
            "STRICT_CAUSAL_GREEN_HOMOTOPY_THEOREM_PRESERVED": True,
            "STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "portable full q1, H_alg, projector, inclusion or projection component tables",
            "a receiver-executable endpoint or full advanced/retarded Green action or distribution kernel",
            "that the existing causal Green-homotopy theorem is false or incomplete as an existence theorem",
            "componentwise replay of every homotopy, projector and suspended-adjoint identity",
            "the weakest foundational base for the imported analytic Green theorem",
            "a passed Gate A, local D, q2 compatibility, Hadamard state, Ward theorem, QME restoration or Lorentzian quantum theory",
        ],
        "next_gate": "Emit one canonical full-q1 finite component jet table on the fixed 386-row basis from the existing generalized-auxiliary, curvature-cylinder and endpoint producers. Independently reconstruct q1 and replay q1 squared and pairing adjointness before serializing the local SDR maps. Treat Lambda_plus/minus under the separate ANALYTIC_GREEN_ACTION contract.",
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in AUTHORITIES
            ]
            + [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": "EXECUTABLE_SOURCE", "sha256": sha(path), "role": "exact producer source inspected for serialization availability"}
                for path in SOURCE_PATHS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_operator_portability_audit.py",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.md",
    }
    projection_keys = (
        "carrier", "portability_contracts", "operator_inventory", "status_counts",
        "route_split", "foundational_strength", "claim_flags", "does_not_establish", "next_gate",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection_keys})
    return value


def render(value: dict[str, Any]) -> str:
    by_id = {item["id"]: item for item in value["operator_inventory"]}
    lines = [
        "# Strict 386-row operator portability audit v1", "", "## Outcome", "", value["answer"], "",
        "## Why there are two serialization problems", "",
        "A local differential operator is determined by finitely many component jet coefficients on the fixed background. A Green operator is nonlocal: portability requires a represented action, convergent name, or distribution kernel together with its topology and causal-support theorem. A finite jet table is not an honest representation of that object.", "",
        "## Operator inventory", "", "| object | mathematical type | current state | decisive missing artifact |", "|---|---|---|---|",
    ]
    for item in value["operator_inventory"]:
        lines.append(f"| `{item['id']}` | `{item['kind']}` | `{item['status']}` | {item['missing'][0] if item['missing'] else 'none'} |")
    lines += ["", "## What is already portable", "", f"The endpoint q1 has **{by_id['ENDPOINT_Q1_30']['present']['arrow_tables']}** exact arrow tables, **{by_id['ENDPOINT_Q1_30']['present']['common_nonzero_coefficients']}** nonzero coefficients and all **{by_id['ENDPOINT_Q1_30']['present']['Bach_columns_checked']}** Bach four-jet columns checked. The 386-row basis and pairing are separately portable.", "", "## What is exact but trapped behind producer hashes", "", "The full q1 and local SDR maps are executable and exact in the existing classical producers. Their certificates expose formulas and content hashes, not row/column coefficient entries. Re-running those producers is reproduction; it does not give the quantum receiver a stable input object.", "", "## What remains analytic", "", "The endpoint and full Green homotopies have theorem-level causal, support and adjoint transfer. The causal transfer theorem remains valid; this audit does not revoke it. It records the narrower fact that an independent receiver cannot apply or inspect the advanced/retarded maps from the current JSON artifacts alone.", "", "## Ranked route", ""]
    for item in value["route_split"]:
        lines.append(f"{item['rank']}. `{item['route']}` — {item['reason']}")
    lines += ["", "## Reproduction", "", "```text", "python3 quantum-weyl/classical_import/build_strict_386_operator_portability_audit.py --check", "python3 quantum-weyl/classical_import/check_strict_386_operator_portability_audit.py", "python3 quantum-weyl/classical_import/verify_strict_386_operator_portability_audit.py", "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_operator_portability_audit.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], ""]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
