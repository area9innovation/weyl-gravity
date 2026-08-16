#!/usr/bin/env python3
"""Audit the grading namespaces required before the M1A row ledger can exist."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.md"

FIELD_DICTIONARY = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/field_dictionary.json"
ATOM_MANIFEST = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/atom_basis_manifest.json"
LOCAL_386 = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPRESENTED = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
FORMAL_COTANGENT = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"

INPUTS = (
    (FIELD_DICTIONARY, "CLASSICAL_MINIMAL_BV_FIELD_DICTIONARY_V2", "authoritative local BV generator semantics"),
    (ATOM_MANIFEST, "CLASSICAL_MINIMAL_BV_KT_ADAPTED_ATOM_BASIS_V2", "authoritative intrinsic jet orders"),
    (LOCAL_386, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "authoritative local 386-row ordering and chain degree"),
    (DFINITE, "STRICT_DFINITE_RESIDUAL_SDR_V1", "finite harmonic comparison carrier and legacy grading labels"),
    (REPRESENTED, "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1", "represented 470-mode residual basis"),
    (FORMAL_COTANGENT, "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1", "formal 8,980-to-940 cotangent comparison"),
    (ACTION_DUAL, "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1", "represented action-support dual target"),
    (ZERO_MODES, "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1", "conformal zero-mode compact weights"),
    (CENTERED, "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1", "centered CE cochain gradings"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def endpoint_atom_id(row: dict[str, Any]) -> str:
    block = row["block"]
    if block == "ENDPOINT_G":
        return "xi" if row["local_index"] < 4 else "omega"
    if block == "ENDPOINT_M":
        return "g"
    if block == "ENDPOINT_E":
        return "g_star"
    if block == "ENDPOINT_I":
        return "xi_star" if row["local_index"] < 4 else "omega_star"
    raise ValueError(f"not an endpoint row: {row['row_id']}")


def sector_at(block: dict[str, Any], index: int) -> dict[str, Any]:
    return next(row for row in block["full_sectors"] if row["start"] <= index < row["stop"])


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        actual = values[path].get("result_id") or values[path].get("schema")
        if actual != expected:
            raise ValueError(f"dependency identity drift: {path}")

    field_dictionary = values[FIELD_DICTIONARY]
    atom_manifest = values[ATOM_MANIFEST]
    local = values[LOCAL_386]
    dfinite = values[DFINITE]
    represented = values[REPRESENTED]
    formal = values[FORMAL_COTANGENT]
    action = values[ACTION_DUAL]
    zero = values[ZERO_MODES]
    centered = values[CENTERED]

    generators = {row["symbol"]: row for row in field_dictionary["generators"]}
    atoms = {row["atom_id"]: row for row in atom_manifest["atoms"]}
    local_rows = local["component_basis"]["rows"]
    if len(local_rows) != 386 or [row["index"] for row in local_rows] != list(range(386)):
        raise ValueError("local 386-row order drift")

    endpoint_rows: list[dict[str, Any]] = []
    for row in local_rows[:30]:
        atom_id = endpoint_atom_id(row)
        generator = generators[atom_id]
        atom = atoms[atom_id]
        typed = {
            "index": row["index"],
            "row_id": row["row_id"],
            "block": row["block"],
            "role": generator["role"],
            "bv_ghost_number": generator["ghost_number"],
            "chain_degree": row["degree"],
            "antifield_number": generator["antifield_number"],
            "form_degree": generator["form_degree"],
            "Grassmann_parity": generator["Grassmann_parity"],
            "mass_dimension": generator["mass_dimension"],
            "Weyl_weight": generator["Weyl_weight"],
            "intrinsic_jet_order_bound": atom["covariant_derivative_order"],
            "conformal_compact_weight": None,
            "ce_ghost_number": None,
            "authority": {
                "generator": f"{FIELD_DICTIONARY.relative_to(ROOT)}#/generators/{generator['symbol']}",
                "atom": f"{ATOM_MANIFEST.relative_to(ROOT)}#/atoms/{atom['canonical_order']}",
                "chain_row": f"{LOCAL_386.relative_to(ROOT)}#/component_basis/rows/{row['index']}",
            },
        }
        if typed["chain_degree"] != -typed["bv_ghost_number"]:
            raise ValueError(f"endpoint chain/BV grading mismatch: {row['row_id']}")
        if typed["Grassmann_parity"] != typed["bv_ghost_number"] % 2:
            raise ValueError(f"endpoint parity mismatch: {row['row_id']}")
        endpoint_rows.append(typed)

    local_degree_counts = {
        str(degree): sum(row["degree"] == degree for row in local_rows)
        for degree in sorted({row["degree"] for row in local_rows})
    }
    endpoint_nonzero_ghost_rows = sum(row["bv_ghost_number"] != 0 for row in endpoint_rows)

    dfinite_coordinate_count = sum(block["full_dimension"] for block in dfinite["blocks"])
    if dfinite_coordinate_count != dfinite["global_direct_sum"]["full_dimension"]:
        raise ValueError("D-finite carrier count drift")
    q_degree_defects = 0
    for block in dfinite["blocks"]:
        for target, source, _ in block["matrices"]["q0"]["entries"]:
            target_degree = sector_at(block, target)["ghost_number"]
            source_degree = sector_at(block, source)["ghost_number"]
            q_degree_defects += int(target_degree != source_degree + 1)
    if q_degree_defects:
        raise ValueError("D-finite legacy grading is not the q-chain degree")

    minimal_sector_to_generator = {
        "diff_ghost": "xi",
        "weyl_ghost": "omega",
        "metric_trace": "g",
        "metric_tf": "g",
        "metric_antifield": "g_star",
        "trace_antifield": "g_star",
        "diff_ghost_antifield": "xi_star",
        "weyl_ghost_antifield": "omega_star",
    }
    dfinite_minimal_coordinates = 0
    dfinite_minimal_sign_defects = 0
    dfinite_test_nonminimal_coordinates = 0
    for block in dfinite["blocks"]:
        for sector in block["full_sectors"]:
            if sector["name"] in minimal_sector_to_generator:
                dfinite_minimal_coordinates += sector["dimension"]
                expected = -generators[minimal_sector_to_generator[sector["name"]]]["ghost_number"]
                dfinite_minimal_sign_defects += sector["dimension"] * int(sector["ghost_number"] != expected)
            else:
                dfinite_test_nonminimal_coordinates += sector["dimension"]
    if dfinite_minimal_sign_defects:
        raise ValueError("D-finite minimal-sector sign bridge drift")

    represented_rows = represented["ordered_residual_basis"]
    formal_summary = formal["formal_cotangent_completion"]
    zero_basis = zero["zero_mode_basis"]
    centered_degrees = centered["ordered_centered_cochain_basis"]["degrees"]
    centered_dimension = sum(centered_degrees[key]["dimension"] for key in ("3", "4", "5"))
    action_dimension = action["action_pairing_identification"]["phase_space_dimension"]

    carrier_audit = [
        {
            "carrier": "LOCAL_GRAPH_BV_386",
            "rows": 386,
            "category": "LOCAL_COMPONENT_JET",
            "fully_namespaced_rows": 30,
            "partially_namespaced_rows": 356,
            "available_now": ["structural_role", "chain_degree"],
            "additional_endpoint_fields": ["bv_ghost_number", "antifield_number", "form_degree", "Grassmann_parity", "mass_dimension", "Weyl_weight", "intrinsic_jet_order_bound"],
            "missing_for_completion": "Declare action-derived auxiliary weights and the mapping-cone grading functor, including typed not-applicable values where no conformal or CE grading exists.",
        },
        {
            "carrier": "REPRESENTED_ENDPOINT_DFINITE_4080",
            "rows": 4080,
            "category": "REDUCED_MODE_GLOBAL_HARMONIC",
            "fully_namespaced_rows": 0,
            "partially_namespaced_rows": 4080,
            "available_now": ["energy", "sector role", "legacy q-chain degree", "antifield_number"],
            "missing_for_completion": "Replace the misleading legacy ghost_number key by chain_degree and bind every represented endpoint species to one local typed species.",
        },
        {
            "carrier": "DFINITE_COMPARISON_4490",
            "rows": dfinite_coordinate_count,
            "category": "REDUCED_MODE_GLOBAL_HARMONIC",
            "fully_namespaced_rows": 0,
            "partially_namespaced_rows": dfinite_coordinate_count,
            "available_now": ["energy", "sector role", "legacy q-chain degree", "antifield_number"],
            "missing_for_completion": "Separate the 4,080 represented endpoint coordinates from the 410-coordinate scalar test nonminimal doublet and give the latter an explicit source dictionary or exclude it from the authoritative source.",
        },
        {
            "carrier": "FORMAL_COTANGENT_COMPARISON_8980",
            "rows": formal_summary["full_dimension"],
            "category": "FORMAL_SHIFTED_COTANGENT",
            "fully_namespaced_rows": 0,
            "partially_namespaced_rows": formal_summary["full_dimension"],
            "available_now": ["primal/dual category", "shifted dual degree rule"],
            "missing_for_completion": "Retain as a formal comparison carrier; do not use it as the authoritative full local BV source.",
        },
        {
            "carrier": "ACTION_RESIDUAL_940",
            "rows": action_dimension,
            "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY",
            "fully_namespaced_rows": 0,
            "partially_namespaced_rows": action_dimension,
            "available_now": ["represented primal/action-dual role", "energy", "chirality", "E/A/L family", "support class"],
            "missing_for_completion": "Bind the 470 primal and 470 action-dual rows to namespaced chain/BV degrees without identifying the finite represented dual with the full continuous dual.",
        },
        {
            "carrier": "ZERO_MODE_15_PLUS_15",
            "rows": len(zero_basis["canonical_generator_order"]) + len(zero_basis["canonical_dual_order"]),
            "category": "RESIDUAL_ZERO_MODE",
            "fully_namespaced_rows": 30,
            "partially_namespaced_rows": 0,
            "available_now": ["generator/action-dual role", "conformal compact weight"],
            "missing_for_completion": "None for its declared zero-mode namespace; local BV and CE gradings must be explicit not-applicable values rather than zeros.",
        },
        {
            "carrier": "CENTERED_C3_C4_C5",
            "rows": centered_dimension,
            "category": "RESIDUAL_COCHAIN",
            "fully_namespaced_rows": centered_dimension,
            "partially_namespaced_rows": 0,
            "available_now": ["CE ghost number", "total conformal compact weight", "sector", "basis monomial"],
            "missing_for_completion": "None for its declared CE namespace; it is a cochain carrier and not a local field/antifield dictionary.",
        },
    ]

    namespace_contract = {
        "rule": "Every grading is a tagged semantic field. A grading that does not apply is serialized as NOT_APPLICABLE with a reason; it is never silently set to zero.",
        "fields": [
            {"name": "bv_ghost_number", "meaning": "standard local BV ghost number from the action-derived generator dictionary", "applies_to": ["LOCAL_COMPONENT_JET and rows explicitly crosswalked to it"]},
            {"name": "chain_degree", "meaning": "degree raised by the unary chain differential q1", "applies_to": ["local and finite harmonic chain carriers"]},
            {"name": "antifield_number", "meaning": "Koszul-Tate antifield filtration degree", "applies_to": ["local BV rows and explicitly crosswalked harmonic rows"]},
            {"name": "form_degree", "meaning": "spacetime differential-form degree of the local BV generator or density", "applies_to": ["local BV rows"]},
            {"name": "Grassmann_parity", "meaning": "Z2 parity of the local coordinate", "applies_to": ["graded local and transported rows"]},
            {"name": "mass_dimension", "meaning": "engineering dimension in the action convention", "applies_to": ["local action-derived rows"]},
            {"name": "Weyl_weight", "meaning": "coefficient in gamma X=Lie_xi X+w omega X", "applies_to": ["local conformal-covariant rows"]},
            {"name": "conformal_compact_weight", "meaning": "eigenweight of the compact conformal D grading", "applies_to": ["zero modes and residual CE cochains"]},
            {"name": "ce_ghost_number", "meaning": "exterior degree in the residual Chevalley-Eilenberg complex", "applies_to": ["residual CE cochains"]},
            {"name": "intrinsic_jet_order_bound", "meaning": "maximum derivative order represented by the coordinate itself", "applies_to": ["local jet rows"]},
            {"name": "operator_order_bounds", "meaning": "per-arrow differential-order metadata; never conflated with a row grading", "applies_to": ["serialized q1, inclusion, projection, homotopy and Green names"]},
        ],
        "forbidden_aliases": [
            "ghost_number=chain_degree",
            "compact_degree=chain_degree",
            "compact_degree=conformal_compact_weight",
            "row_derivative_order=operator_order",
            "not_applicable=0",
        ],
    }

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-m1a-carrier-grading-convention-audit-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m1a-carrier-grading-convention-audit-v1.schema.json",
        "result_id": "STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1",
        "result_kind": "M1A_TYPED_CARRIER_SEMANTIC_NAMESPACE_AUDIT",
        "result_state": "CONVENTION_COLLISION_CERTIFIED_M1A_LEDGER_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "4ada117a5a856ed219bcc77330d57ffae04ce3e7",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can M1A safely flatten the existing local, harmonic, cotangent, zero-mode and centered grading labels into one row dictionary?",
        "answer": "No. Thirty local endpoint rows can already be typed exactly, and all 386 local rows have an authoritative chain degree. But the local action dictionary uses standard BV ghost number while the D-finite SDR's field named ghost_number is the q-chain degree and has the opposite sign on every nonzero minimal BV degree. The phrase compact degree also denotes two different objects: local chain degree and conformal D weight. A safe M1A ledger therefore needs tagged grading namespaces and explicit NOT_APPLICABLE values before the remaining 356 local rows and represented carriers can be serialized.",
        "scope": {
            "theory": "strict pure-Weyl classical BV import",
            "background": "unit conformal cylinder",
            "task": "M1A semantic namespace and source-authority audit",
            "arithmetic": "exact integer gradings and content hashes",
        },
        "counts": {
            "local_rows_total": 386,
            "local_endpoint_rows_fully_namespaced": len(endpoint_rows),
            "local_rows_partially_namespaced": 386 - len(endpoint_rows),
            "local_endpoint_nonzero_bv_ghost_rows": endpoint_nonzero_ghost_rows,
            "dfinite_full_coordinates": dfinite_coordinate_count,
            "dfinite_minimal_coordinates_with_sign_bridge": dfinite_minimal_coordinates,
            "dfinite_test_nonminimal_coordinates_without_local_source_dictionary": dfinite_test_nonminimal_coordinates,
            "represented_residual_rows": len(represented_rows),
            "formal_cotangent_rows": formal_summary["full_dimension"],
            "action_residual_rows": action_dimension,
            "zero_mode_rows": 30,
            "centered_cochain_rows": centered_dimension,
            "dfinite_q_degree_defects": q_degree_defects,
            "dfinite_minimal_sign_bridge_defects": dfinite_minimal_sign_defects,
        },
        "convention_collision_witness": {
            "local_bv_examples": [
                {"row": "c_0", "bv_ghost_number": 1, "chain_degree": -1},
                {"row": "h_star_00", "bv_ghost_number": -1, "chain_degree": 1},
                {"row": "c_star_0", "bv_ghost_number": -2, "chain_degree": 2},
            ],
            "endpoint_rows_satisfy_chain_degree_equals_minus_bv_ghost_number": True,
            "dfinite_legacy_key": "ghost_number",
            "dfinite_semantic_value": "chain_degree",
            "dfinite_q_raises_legacy_value_by_one": True,
            "dfinite_minimal_value_equals_minus_local_bv_ghost_number": True,
            "compact_degree_collision": {
                "local_meaning": "q-chain degree",
                "zero_mode_and_centered_meaning": "conformal D eigenweight",
                "same_semantic_field": False,
            },
        },
        "namespace_contract": namespace_contract,
        "local_endpoint_typed_rows": endpoint_rows,
        "local_chain_degree_counts": local_degree_counts,
        "carrier_audit": carrier_audit,
        "m1a_repair_plan": [
            {"order": 1, "id": "M1A1_NAMESPACED_GRADING_SCHEMA", "status": "READY", "deliverable": "Adopt the tagged namespace contract with explicit NOT_APPLICABLE records and prohibit the five unsafe aliases."},
            {"order": 2, "id": "M1A2_LOCAL_356_SEMANTIC_EXTENSION", "status": "OPEN", "deliverable": "Derive auxiliary and mapping-cone weights, form roles and intrinsic jet bounds from the action and the mapping-cone functor, with an independent receiver."},
            {"order": 3, "id": "M1A3_REPRESENTED_CROSSWALK", "status": "OPEN", "deliverable": "Crosswalk the 4,080 represented endpoint rows, isolate the 410 test-nonminimal rows, and type the 470+470 action residual without promoting the formal 8,980 source."},
            {"order": 4, "id": "M1A4_LEDGER_FREEZE", "status": "BLOCKED_BY_M1A2_M1A3", "deliverable": "Serialize every row, hash the field dictionary and gradings, and rerun the M1A receiver."},
        ],
        "foundational_strength": {
            "logic": "primitive-recursive finite scans and exact integer equalities",
            "choice_used": False,
            "excluded_middle_used": "decidable finite equality only",
            "analysis_used": False,
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": sha(path), "role": role}
                for path, result_id, role in INPUTS
            ],
            "producer": str(Path(__file__).resolve().relative_to(ROOT)),
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m1a_carrier_grading_convention_audit.py",
            "method": "Reconstruct the endpoint source crosswalk, scan every D-finite q0 entry against sector degrees, and recompute carrier counts and collision witnesses without importing the producer.",
            "expected_digest": "",
        },
        "claim_flags": {
            "M1A_CONVENTION_COLLISION_AUDITED": True,
            "LOCAL_ENDPOINT_30_FULLY_NAMESPACED": True,
            "LOCAL_386_FULLY_TYPED": False,
            "DFINITE_LEGACY_GHOST_NUMBER_IS_SAFE_TO_IMPORT_AS_BV_GHOST_NUMBER": False,
            "CHAIN_DEGREE_AND_CONFORMAL_COMPACT_WEIGHT_IDENTICAL": False,
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "the completed M1A carrier ledger",
            "an authoritative source dictionary for the 410-coordinate scalar test nonminimal sector",
            "mass dimensions or Weyl weights for the 356 auxiliary and mapping-cone rows",
            "the M1B represented composite contraction",
            "the M1C immutable manifest or any replayed final Gate-A check",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Adopt M1A1, then derive M1A2 from the action and mapping-cone functor and M1A3 from the represented endpoint/action-dual crosswalk; only their union may be frozen as M1A4.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.md",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    counts = value["counts"]
    rows = "\n".join(
        f"| `{item['carrier']}` | {item['rows']:,} | {item['fully_namespaced_rows']:,} | {item['partially_namespaced_rows']:,} | {item['missing_for_completion']} |"
        for item in value["carrier_audit"]
    )
    return f"""# M1A carrier-grading convention audit

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Lifecycle:** `CLASSIFIED`; M1A remains `OPEN` and Gate A remains `FAIL_CLOSED`.

## Result

M1A cannot safely flatten the current grading labels.  The local BV source uses
standard BV ghost number, while the D-finite comparison uses a field named
`ghost_number` as its q-chain degree.  On the thirty common endpoint rows,
`chain_degree = -bv_ghost_number`; the two conventions have opposite sign on
{counts['local_endpoint_nonzero_bv_ghost_rows']} rows.  Every D-finite q0 arrow raises its legacy value by
one, with {counts['dfinite_q_degree_defects']} defects, confirming its chain
meaning.  Separately, conformal compact weight in the zero-mode and centered CE
payload is not the local q-chain degree.

The audit reconstructs all thirty endpoint rows from the authoritative action
dictionary and atom manifest.  Their BV ghost number, chain degree, antifield
number, form degree, parity, mass dimension, Weyl weight and intrinsic jet order
are now source-linked explicitly.  The remaining 356 local rows still need an
action/mapping-cone semantic extension; this audit does not guess those values.

## Carrier coverage

| Carrier | Rows | Fully namespaced | Partial | Remaining work |
|---|---:|---:|---:|---|
{rows}

The 4,490-coordinate D-finite comparison contains
{counts['dfinite_minimal_coordinates_with_sign_bridge']:,} minimal coordinates
with an exact sign bridge and
{counts['dfinite_test_nonminimal_coordinates_without_local_source_dictionary']:,}
scalar test-nonminimal coordinates without a local source dictionary.  The
formal 8,980-coordinate cotangent source remains a comparison object, not the
authoritative original BV source.

## Required schema repair

M1A must use distinct tagged fields: `bv_ghost_number`, `chain_degree`,
`antifield_number`, `form_degree`, `Grassmann_parity`, `mass_dimension`,
`Weyl_weight`, `conformal_compact_weight`, `ce_ghost_number`, and
`intrinsic_jet_order_bound`.  Per-arrow `operator_order_bounds` is a separate
object.  A grading that does not apply must be marked `NOT_APPLICABLE` with a
reason, never silently zeroed.

## Boundary

This is a convention and source-authority audit.  It completes none of M1A,
M1B or M1C, replays no final Gate-A check, and establishes no Hadamard,
renormalized-product, QME or residual-transfer result.

## Next construction

{value['next_gate']}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {
        RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        REPORT: report(value),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print("STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
