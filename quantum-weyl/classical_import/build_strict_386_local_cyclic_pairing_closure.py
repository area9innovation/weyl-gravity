#!/usr/bin/env python3
"""Close the local half of M4 and separate residual cyclicity by type."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
Q2 = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
Q3 = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
BINDING = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
TYPE_AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
GATE = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
RESULT = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def sparse_rank(entries: list[dict[str, Any]], dimension: int) -> int:
    rows: list[dict[int, Fraction]] = [dict() for _ in range(dimension)]
    for entry in entries:
        rows[entry["left_index"]][entry["right_index"]] = Fraction(entry["coefficient"])
    rank = 0
    for column in range(dimension):
        pivot = next((row for row in range(rank, dimension) if rows[row].get(column)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = {key: value / scale for key, value in rows[rank].items()}
        pivot_row = rows[rank]
        for row in range(dimension):
            if row == rank or not rows[row].get(column):
                continue
            coefficient = rows[row][column]
            updated = dict(rows[row])
            for key, value in pivot_row.items():
                new_value = updated.get(key, Fraction(0)) - coefficient * value
                if new_value:
                    updated[key] = new_value
                else:
                    updated.pop(key, None)
            rows[row] = updated
        rank += 1
    return rank


def pin(path: Path, value: dict[str, Any], role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": value["result_id"],
        "sha256": sha(path),
        "role": role,
    }


def build() -> dict[str, Any]:
    pairing, graph, d_action, q2, q3, binding, type_audit, gate = (
        load(path) for path in (PAIRING, GRAPH, D_ACTION, Q2, Q3, BINDING, TYPE_AUDIT, GATE)
    )
    identities = (
        (pairing, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
        (graph, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"),
        (d_action, "STRICT_386_FULL_D_ACTION_V1"),
        (q2, "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1"),
        (q3, "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1"),
        (binding, "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1"),
        (type_audit, "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1"),
        (gate, "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION"),
    )
    if any(value.get("result_id") != expected for value, expected in identities):
        raise ValueError("M4L dependency identity drift")
    if binding["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not True:
        raise ValueError("M3L is not closed")
    if type_audit["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not False:
        raise ValueError("M3R boundary drift")

    basis = pairing["component_basis"]
    serialized = pairing["pairing_serialization"]
    rows = basis["rows"]
    entries = serialized["entries"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("pairing carrier row drift")
    rank = sparse_rank(entries, 386)
    received = {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in entries
    }
    skew_defects = sum(
        received.get((right, left), Fraction(0)) != -coefficient
        for (left, right), coefficient in received.items()
    )
    degree_defects = sum(
        rows[left]["degree"] + rows[right]["degree"] != 1
        for left, right in received
    )
    row_coverage = {index for pair in received for index in pair}
    sector_rows = Counter(row["sector"] for row in rows)
    sector_entries = Counter(
        "endpoint" if rows[entry["left_index"]]["sector"] == "CAUSAL_ENDPOINT_30"
        else "auxiliary_complement" if rows[entry["left_index"]]["sector"] == "ALGEBRAIC_COMPLEMENT_36"
        else "mapping_cone_complement"
        for entry in entries
    )
    pairing_replay = {
        "carrier_rows": len(rows),
        "unique_row_ids": len({row["row_id"] for row in rows}),
        "endpoint_rows": sector_rows["CAUSAL_ENDPOINT_30"],
        "auxiliary_rows": sector_rows["ALGEBRAIC_COMPLEMENT_36"],
        "mapping_cone_and_cotangent_rows": sector_rows["ALGEBRAIC_COMPLEMENT_320"],
        "nonzero_ordered_pairing_entries": len(entries),
        "endpoint_pairing_entries": sector_entries["endpoint"],
        "auxiliary_pairing_entries": sector_entries["auxiliary_complement"],
        "mapping_cone_pairing_entries": sector_entries["mapping_cone_complement"],
        "exact_rational_rank": rank,
        "rows_with_nonzero_partner": len(row_coverage),
        "odd_skew_defects": skew_defects,
        "pairing_degree_defects": degree_defects,
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
    }
    if pairing_replay != {
        **pairing_replay,
        "carrier_rows": 386,
        "unique_row_ids": 386,
        "endpoint_rows": 30,
        "auxiliary_rows": 36,
        "mapping_cone_and_cotangent_rows": 320,
        "nonzero_ordered_pairing_entries": 410,
        "endpoint_pairing_entries": 30,
        "auxiliary_pairing_entries": 60,
        "mapping_cone_pairing_entries": 320,
        "exact_rational_rank": 386,
        "rows_with_nonzero_partner": 386,
        "odd_skew_defects": 0,
        "pairing_degree_defects": 0,
    }:
        raise ValueError("full local pairing replay defect")

    graph_replay = graph["exact_replay"]
    common_replay = binding["exact_replay"]
    local_cyclicity_replay = {
        "pairing_rank_defects": 386 - rank,
        "odd_skew_defects": skew_defects,
        "pairing_degree_defects": degree_defects,
        "graph_q1_suspended_cyclicity_defects_after_PBW_reduction": graph_replay["transported_R_PBW_reduced_cyclicity_defects"],
        "endpoint_homotopy_cyclicity_defects": graph_replay["H_alg_graph_cyclicity_defects"],
        "endpoint_SDR_cyclicity_defects_on_common_manifest": common_replay["endpoint_SDR_cyclicity_defects"],
        "D_formal_skew_adjoint_pairing_entries_checked": d_action["exact_replay"]["formal_skew_adjoint_pairing_entries_checked"],
        "D_formal_skew_adjoint_defects": d_action["exact_replay"]["formal_skew_adjoint_defects"],
        "q2_cyclicity_equalities_checked": q2["q2_cyclicity_replay"]["shifted_mass_equalities_checked"] + q2["q2_cyclicity_replay"]["auxiliary_Diff_master_density_coefficients_checked"],
        "graph_q2_cyclicity_defects": q2["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "q3_cyclicity_equalities_checked": q3["q3_cyclicity_replay"]["auxiliary_q3_equalities_checked"],
        "graph_q3_cyclicity_defects_mod_d": q3["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"],
        "common_manifest_compatibility_defects": common_replay["compatibility_defects"],
    }
    if any(value for key, value in local_cyclicity_replay.items() if key.endswith("defects")):
        raise ValueError("local cyclicity defect")
    if local_cyclicity_replay["D_formal_skew_adjoint_pairing_entries_checked"] != 410:
        raise ValueError("D pairing coverage drift")

    artifact_pins = [
        pin(PAIRING, pairing, "exact rank-386 odd pairing on every local graph row"),
        pin(GRAPH, graph, "graph q1, transported suspension and cyclic endpoint SDR"),
        pin(D_ACTION, d_action, "formal skew-adjoint cylinder-flow action"),
        pin(Q2, q2, "full common-carrier q2 cyclicity"),
        pin(Q3, q3, "full common-carrier q3 cyclicity modulo horizontal boundary"),
        pin(BINDING, binding, "common local endpoint nonlinear manifest"),
        pin(TYPE_AUDIT, type_audit, "local versus reduced-mode carrier decision"),
        pin(GATE, gate, "open unsplit M4 predecessor"),
    ]
    type_split = {
        "old_requirement": "M4_FULL_CYCLIC_PAIRING",
        "old_requirement_disposition": "REJECT_AS_ONE_UNTYPED_LOCAL_AND_RESIDUAL_OBJECT",
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": {
            "category": "LOCAL-ALGEBRAIC",
            "carrier": "386 spacetime-dependent graph component species",
            "status": "COMPLETE",
            "evidence": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
        },
        "M4R_TYPED_RESIDUAL_CYCLICITY": {
            "category": "REDUCED-MODE",
            "carrier": "W+/W- harmonic coefficients after the M3R comparison",
            "status": "NOT_DEFINED_BEFORE_M3R",
            "dependency": "M3R_TYPED_RESIDUAL_COMPARISON",
        },
        "row_type_fact": "The 386 local graph rows comprise 30 endpoint, 36 generalized-auxiliary and 320 mapping-cone/cotangent rows. They contain no W+/W- harmonic residual coefficient rows.",
        "gate_rule": "M4L may close now. M4R remains fail closed until M3R supplies a typed comparison and the induced residual pairing and cyclic side conditions replay.",
    }
    obligation_ledger = [
        {"id": "FULL_LOCAL_PAIRING", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "GRAPH_Q1_CYCLICITY", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "ENDPOINT_SDR_CYCLICITY", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "D_FORMAL_SKEW_ADJOINTNESS", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "FULL_GRAPH_Q2_CYCLICITY", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "FULL_GRAPH_Q3_CYCLICITY_MOD_D", "category": "LOCAL-ALGEBRAIC", "status": "COMPLETE", "defects": 0},
        {"id": "INDUCED_RESIDUAL_PAIRING_AND_CYCLICITY", "category": "REDUCED-MODE", "status": "BLOCKED_BY_M3R_NOT_CONSTRUCTED", "defects": None},
    ]
    result: dict[str, Any] = {
        "$schema": "../schema/strict-386-local-cyclic-pairing-closure-v1.schema.json",
        "schema": "strict-386-local-cyclic-pairing-closure-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-local-cyclic-pairing-closure-v1.schema.json",
        "result_id": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
        "result_kind": "CLASSICAL_IMPORT_TYPED_CYCLIC_PAIRING_CLOSURE",
        "result_state": "M4L_LOCAL_CYCLIC_PAIRING_COMPLETE_M4R_TYPED_RESIDUAL_CYCLICITY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "e8d8b3e8c9870074ffe8122ac49e926880919c91",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Is the open M4 pairing gate really missing one full 386-row local pairing, or does it conflate an already complete local cyclic structure with cyclicity of the not-yet-constructed residual comparison?",
        "answer": "It conflates two mathematical categories. The 386-row local graph carrier already has an exact rank-386 odd pairing with 410 ordered rational entries covering all 30 endpoint, 36 auxiliary and 320 cone/cotangent rows. On the same content-addressed manifest, graph-q1 suspended cyclicity, endpoint-SDR cyclicity, D skew-adjointness, q2 cyclicity and q3 cyclicity modulo horizontal boundary all have zero defects. This closes M4L. The carrier has no W+/W- harmonic residual coefficient rows; induced residual cyclicity is M4R, a REDUCED-MODE obligation that is not even defined until M3R constructs the typed endpoint-to-residual comparison. Gate A therefore remains fail closed.",
        "scope": {
            "theory": "strict pure-Weyl classical BV complex",
            "background": "unit conformal cylinder",
            "local_carrier": "386 graph component species",
            "pairing": "degree-minus-one odd BV pairing with exact rational coefficients",
            "cyclicity_scope": "q1 and endpoint SDR exactly; q2 pointwise/action-derived; q3 modulo horizontal boundary",
        },
        "artifact_pins": artifact_pins,
        "pairing_replay": pairing_replay,
        "local_cyclicity_replay": local_cyclicity_replay,
        "obligation_ledger": obligation_ledger,
        "type_split": type_split,
        "foundational_strength": {
            "pairing_and_fixed_table_replay": "finite exact rational arithmetic formalizable in PRA",
            "q2_q3_cyclicity": "finite exact component checks plus differentiated local action identities; q3 is equality modulo horizontal boundary",
            "choice_dependency_added": "none",
            "Hilbert_or_Krein_completion_used": False,
            "residual_dependency": "M4R requires the separately typed global harmonic comparison M3R and is not promoted by this local result",
        },
        "gate_disposition": {
            "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": "COMPLETE",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN_BLOCKED_BY_M3R",
            "M3R_TYPED_RESIDUAL_COMPARISON": "OPEN",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
            "top_level_gate_a_hashes_accepted_by_this_result": 0,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_386_FULL_LOCAL_ODD_PAIRING_NONDEGENERATE": True,
            "STRICT_386_LOCAL_Q1_SDR_D_Q2_Q3_CYCLICITY_COMPLETE": True,
            "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE": True,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
            "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": False,
            "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED": False,
            "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "a harmonic restriction or endpoint-to-W+/W- residual comparison",
            "an induced pairing on the 470-coordinate W+/W- residual carrier",
            "M4R residual cyclicity or cyclic side conditions for M3R",
            "support-locality of a nonzero harmonic or zero-mode projector",
            "a new accepted Gate-A top-level hash or the common all-object freeze",
            "nonlinear q2/q3 compatibility with advanced or retarded Green homotopies",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration, residual transfer, physical positivity or a Lorentzian quantum theory",
        ],
        "provenance": {"inputs": artifact_pins},
        "next_gate": "Replace the old untyped M4 requirement by completed M4L and open M4R. Construct M3R with explicit section/test/distribution domains, harmonic restriction, W+/W- coefficient maps and zero-mode policy; then derive the residual pairing through that comparison and replay M4R before attempting the M1 freeze.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_local_cyclic_pairing_closure.py",
            "checks": [
                "all eight dependency identities and content hashes",
                "independent sparse exact rank, skew, degree and row-coverage replay",
                "q1/SDR/D/q2/q3 cyclicity projections on the M3L common manifest",
                "386-row local versus 470-coordinate residual type separation",
                "M4L positive flags and M4R/Gate/Hadamard/QME firewalls",
                "canonical result digest",
            ],
            "expected_digest": "",
        },
    }
    projection = (
        "scope", "artifact_pins", "pairing_replay", "local_cyclicity_replay",
        "obligation_ledger", "type_split", "foundational_strength", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate",
    )
    result["independent_checker"]["expected_digest"] = digest({key: result[key] for key in projection})
    return result


def report(value: dict[str, Any]) -> str:
    pairing = value["pairing_replay"]
    cyclic = value["local_cyclicity_replay"]
    return f"""# Strict 386-row local cyclic-pairing closure

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

## Result

M4 was typed too coarsely.  Its local half is complete.  The exact graph
carrier has {pairing['carrier_rows']} rows: {pairing['endpoint_rows']} endpoint,
{pairing['auxiliary_rows']} generalized-auxiliary and
{pairing['mapping_cone_and_cotangent_rows']} mapping-cone/cotangent rows.  Its
odd pairing has {pairing['nonzero_ordered_pairing_entries']} ordered rational
entries, exact rank {pairing['exact_rational_rank']}, every row has a partner,
and the skew and pairing-degree defect counts are zero.

On the same M3L content-addressed manifest, graph-q1 suspended cyclicity,
endpoint-SDR cyclicity, D formal skew-adjointness, q2 cyclicity and q3
cyclicity modulo horizontal boundary all have zero defects.  The q2 and q3
source receivers respectively cover {cyclic['q2_cyclicity_equalities_checked']}
and {cyclic['q3_cyclicity_equalities_checked']} displayed cyclic equalities;
the D receiver checks all {cyclic['D_formal_skew_adjoint_pairing_entries_checked']}
ordered pairing entries.

## Type repair

- `M4L_LOCAL_GRAPH_CYCLIC_PAIRING`: **COMPLETE**, `LOCAL-ALGEBRAIC`.
- `M4R_TYPED_RESIDUAL_CYCLICITY`: **OPEN**, `REDUCED-MODE`, and depends on M3R.

The 386 rows are spacetime-dependent local component species.  They contain
no W+/W- harmonic residual coefficient rows.  Therefore residual cyclicity is
not a final unchecked block of the same matrix: it is the induced structure
of a different carrier, and cannot be defined until the M3R comparison exists.

No new Gate-A hash is accepted.  This result constructs neither M3R nor a
Hadamard state, renormalized products, QME restoration or residual transfer.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_local_cyclic_pairing_closure.py --check
python3 quantum-weyl/classical_import/check_strict_386_local_cyclic_pairing_closure.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_local_cyclic_pairing_closure.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
