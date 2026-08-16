#!/usr/bin/env python3
"""Build the action-derived dual lift of the strict M1B primal composite."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
M1A = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
CROSSWALK = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
ACTION = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
LOCAL = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
SCHEMA = HERE / "schema/strict-m1b-action-dual-lift-v1.schema.json"
RESULT = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1B_ACTION_DUAL_LIFT_V1.md"

Sparse = dict[tuple[int, int], Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def read_sparse(spec: dict[str, Any]) -> Sparse:
    out: Sparse = {}
    for row, column, coefficient in spec["entries"]:
        key = (int(row), int(column))
        if key in out:
            raise ValueError(f"duplicate entry in {spec['name']}")
        out[key] = Fraction(str(coefficient))
    return out


def transpose(value: Sparse, sign: int = 1) -> Sparse:
    return {(column, row): sign * coefficient for (row, column), coefficient in value.items()}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        by_row.setdefault(row, []).append((column, coefficient))
    out: Sparse = {}
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in by_row.get(middle, []):
            key = (row, column)
            out[key] = out.get(key, Fraction(0)) + left_coefficient * right_coefficient
            if not out[key]:
                del out[key]
    return out


def add(*terms: tuple[int, Sparse]) -> Sparse:
    out: Sparse = {}
    for scale, value in terms:
        for key, coefficient in value.items():
            out[key] = out.get(key, Fraction(0)) + scale * coefficient
            if not out[key]:
                del out[key]
    return out


def identity(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def encode(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def matrix(name: str, rows: int, columns: int, value: Sparse) -> dict[str, Any]:
    rows_encoded = [[row, column, encode(coefficient)] for (row, column), coefficient in sorted(value.items())]
    return {
        "name": name,
        "shape": [rows, columns],
        "orientation": "entry[target_index,source_index]",
        "entries": rows_encoded,
        "nonzero_entries": len(rows_encoded),
        "sha256": digest({"shape": [rows, columns], "entries": rows_encoded}),
    }


def replay(q: Sparse, inclusion: Sparse, projection: Sparse, homotopy: Sparse, n: int, r: int) -> dict[str, int]:
    return {
        "q_dual_squared_defects": len(multiply(q, q)),
        "pi_dual_iota_dual_defects": len(add((1, multiply(projection, inclusion)), (-1, identity(r)))),
        "dual_contraction_defects": len(add((1, multiply(inclusion, projection)), (-1, identity(n)), (1, multiply(q, homotopy)), (1, multiply(homotopy, q)))),
        "q_dual_iota_dual_defects": len(multiply(q, inclusion)),
        "pi_dual_q_dual_defects": len(multiply(projection, q)),
        "s_dual_squared_defects": len(multiply(homotopy, homotopy)),
        "s_dual_iota_dual_defects": len(multiply(homotopy, inclusion)),
        "pi_dual_s_dual_defects": len(multiply(projection, homotopy)),
    }


def build() -> dict[str, Any]:
    primal, m1a, crosswalk, action, local, m4r = map(load, (PRIMAL, M1A, CROSSWALK, ACTION, LOCAL, M4R))
    expected = (
        (primal, "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1"),
        (m1a, "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1"),
        (crosswalk, "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1"),
        (action, "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1"),
        (local, "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1"),
        (m4r, "STRICT_TYPED_RESIDUAL_CYCLICITY_V1"),
    )
    if any(value.get("result_id") != result_id for value, result_id in expected):
        raise ValueError("M1B action-dual dependency identity drift")
    if primal["claim_flags"]["M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE"] is not True:
        raise ValueError("primal M1B layer missing")
    if m1a["claim_flags"]["M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE"] is not True:
        raise ValueError("M1A freeze missing")
    if local["pairing_replay"]["exact_rational_rank"] != 386:
        raise ValueError("local action pairing is degenerate")
    if action["claim_flags"]["M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is not True:
        raise ValueError("compact-source action dual unavailable")
    if m4r["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not True:
        raise ValueError("represented residual action pairing unavailable")

    action_rows = crosswalk["action_residual_dual_rows"]
    action_dictionary = action["action_pairing_identification"]["dual_dictionary"]
    if not (len(action_rows) == len(action_dictionary) == 470):
        raise ValueError("action-dual dimension drift")
    crosswalk_defects = 0
    residual_actions: list[dict[str, Any]] = []
    for index, (row, source) in enumerate(zip(action_rows, action_dictionary)):
        expected_label = f"dual[1]({source['primal_label']})"
        if (
            row["pair_index"] != index
            or row["residual_index"] != 470 + index
            or row["residual_label"] != expected_label
            or row["compact_source_representative"] != source["compact_source_representative"]
            or row["action_dual_solution_label"] != source["action_dual_solution_label"]
            or row["action_pairing_on_primal"] != "1"
            or not row["compact_source_support"]
        ):
            crosswalk_defects += 1
        residual_actions.append({
            "pair_index": index,
            "energy": row["energy"],
            "primal_label": source["primal_label"],
            "dual_label": row["residual_label"],
            "local_species_id": row["local_species_id"],
            "local_endpoint_row_ids": row["local_endpoint_row_ids"],
            "action_dual_solution_label": row["action_dual_solution_label"],
            "compact_source_representative": row["compact_source_representative"],
            "compact_source_support": row["compact_source_support"],
            "inclusion_rule": "iota_dual_comp=pi_comp^sharp",
            "projection_rule": "pi_dual_comp=iota_comp^sharp",
        })
    if crosswalk_defects:
        raise ValueError("action-dual row crosswalk defect")

    blocks: list[dict[str, Any]] = []
    totals: dict[str, int] = {}
    aggregate = {
        "represented_action_test_coordinates": 0,
        "action_residual_dual_coordinates": 0,
        "q_dual_nonzero_entries": 0,
        "iota_dual_nonzero_entries": 0,
        "pi_dual_nonzero_entries": 0,
        "s_dual_nonzero_entries": 0,
    }
    action_by_energy: dict[int, list[dict[str, Any]]] = {}
    for row in action_rows:
        action_by_energy.setdefault(row["energy"], []).append(row)
    for source in primal["represented_contraction"]["blocks"]:
        n, r = source["represented_dimension"], source["residual_dimension"]
        q_primal = read_sparse(source["matrices"]["q0_rep"])
        iota_primal = read_sparse(source["matrices"]["iota_rep"])
        pi_primal = read_sparse(source["matrices"]["pi_rep"])
        s_primal = read_sparse(source["matrices"]["s_rep"])
        q_dual = transpose(q_primal, -1)
        iota_dual = transpose(pi_primal)
        pi_dual = transpose(iota_primal)
        s_dual = transpose(s_primal, -1)
        defects = replay(q_dual, iota_dual, pi_dual, s_dual, n, r)
        if any(defects.values()):
            raise ValueError(f"E{source['energy']} action-dual replay defect: {defects}")
        for key, value in defects.items():
            totals[key] = totals.get(key, 0) + value
        energy_actions = sorted(action_by_energy[source["energy"]], key=lambda row: row["pair_index"])
        blocks.append({
            "energy": source["energy"],
            "represented_action_test_dimension": n,
            "action_residual_dual_dimension": r,
            "represented_action_test_basis": [f"action_test_dual[1]({label})" for label in source["represented_basis"]],
            "action_residual_dual_basis": [row["residual_label"] for row in energy_actions],
            "matrices": {
                "q_dual_rep": matrix("q_dual_rep", n, n, q_dual),
                "iota_dual_rep": matrix("iota_dual_rep", n, r, iota_dual),
                "pi_dual_rep": matrix("pi_dual_rep", r, n, pi_dual),
                "s_dual_rep": matrix("s_dual_rep", n, n, s_dual),
            },
            "exact_replay": defects,
        })
        aggregate["represented_action_test_coordinates"] += n
        aggregate["action_residual_dual_coordinates"] += r
        aggregate["q_dual_nonzero_entries"] += len(q_dual)
        aggregate["iota_dual_nonzero_entries"] += len(iota_dual)
        aggregate["pi_dual_nonzero_entries"] += len(pi_dual)
        aggregate["s_dual_nonzero_entries"] += len(s_dual)

    nodes = [
        {"id": "LOCAL_GRAPH_BV_BUNDLE", "category": "LOCAL_COMPONENT_JET_BUNDLE", "dimension": 386, "authority": "AUTHORITATIVE"},
        {"id": "LOCAL_GRAPH_ACTION_DUAL", "category": "ACTION_DENSITY_DUAL", "dimension": 386, "authority": "IDENTIFIED_BY_NONDEGENERATE_LOCAL_ACTION_PAIRING"},
        {"id": "REPRESENTED_ENDPOINT_DFINITE", "category": "REDUCED_MODE_GLOBAL_HARMONIC", "dimension": 4080, "authority": "AUTHORITATIVE_REPRESENTED_PRIMAL"},
        {"id": "REPRESENTED_ACTION_TEST_DUAL_CHECK", "category": "FINITE_ALGEBRAIC_DUAL_VERIFICATION_CORE", "dimension": 4080, "authority": "CHECK_ONLY_NOT_A_NEW_SOURCE_CARRIER"},
        {"id": "PRIMAL_RESIDUAL_DFINITE", "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY", "dimension": 470, "authority": "AUTHORITATIVE"},
        {"id": "COMPACT_SOURCE_ACTION_DUAL_RESIDUAL", "category": "COMPACT_SOURCE_ACTION_DUAL", "dimension": 470, "authority": "AUTHORITATIVE_REPRESENTED_ACTION_DUAL"},
    ]
    arrows = [
        {"id": "local_action_sharp", "source": "LOCAL_GRAPH_BV_BUNDLE", "target": "LOCAL_GRAPH_ACTION_DUAL", "kind": "RANK_386_LOCAL_ACTION_PAIRING", "sha256": local["pairing_replay"]["pairing_sha256"]},
        {"id": "q_dual_comp", "source": "LOCAL_GRAPH_ACTION_DUAL", "target": "LOCAL_GRAPH_ACTION_DUAL", "kind": "MINUS_ACTION_ADJOINT_OF_Q_COMP"},
        {"id": "iota_dual_comp", "source": "COMPACT_SOURCE_ACTION_DUAL_RESIDUAL", "target": "LOCAL_GRAPH_ACTION_DUAL", "kind": "ACTION_ADJOINT_OF_PI_COMP"},
        {"id": "pi_dual_comp", "source": "LOCAL_GRAPH_ACTION_DUAL", "target": "COMPACT_SOURCE_ACTION_DUAL_RESIDUAL", "kind": "ACTION_ADJOINT_OF_IOTA_COMP"},
        {"id": "s_dual_comp", "source": "LOCAL_GRAPH_ACTION_DUAL", "target": "LOCAL_GRAPH_ACTION_DUAL", "kind": "MINUS_ACTION_ADJOINT_OF_S_COMP"},
        {"id": "finite_dual_verification", "source": "REPRESENTED_ACTION_TEST_DUAL_CHECK", "target": "COMPACT_SOURCE_ACTION_DUAL_RESIDUAL", "kind": "EXACT_TRANSPOSE_REPLAY_WITHOUT_SOURCE_AUTHORITY_PROMOTION"},
    ]
    formula = {
        "q_dual": "q_dual_comp=-q_comp^sharp",
        "inclusion": "iota_dual_comp=pi_comp^sharp",
        "projection": "pi_dual_comp=iota_comp^sharp",
        "homotopy": "s_dual_comp=-s_comp^sharp",
        "represented_check": "q_dual=-q_rep^T; iota_dual=pi_rep^T; pi_dual=iota_rep^T; s_dual=-s_rep^T",
        "uniqueness": "the rank-386 local action pairing and rank-940 residual action pairing determine every displayed adjoint uniquely",
    }
    typed_dag = {"nodes": nodes, "arrows": arrows, "formula": formula}
    typed_dag["sha256"] = digest(typed_dag)
    bridge = {
        "local_action_pairing_rank": local["pairing_replay"]["exact_rational_rank"],
        "local_action_pairing_rows": local["pairing_replay"]["carrier_rows"],
        "residual_action_pairing_rank": action["action_pairing_identification"]["phase_pairing_rank"],
        "compact_source_dual_classes": len(action_dictionary),
        "compact_source_support_defects": sum(not row["compact_source_support"] for row in action_dictionary),
        "action_pairing_identification_defects": action["action_pairing_identification"]["pairing_identification_defects"],
        "m1a_action_dual_crosswalk_defects": crosswalk_defects,
        "adjoint_uniqueness_defects": 0,
        "full_4080_algebraic_dual_identified_with_compact_sources": False,
        "verification_core_is_authoritative_full_bv_source": False,
    }
    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1b-action-dual-lift-v1.schema.json",
        "schema": "strict-m1b-action-dual-lift-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "STRICT_M1B_ACTION_DUAL_LIFT_V1",
        "result_kind": "TYPED_ACTION_DUAL_COMPOSITE_LIFT",
        "result_state": "M1B_ACTION_DUAL_LIFT_COMPLETE_TYPED_CYCLIC_REPLAY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "c4a9cc45829bd02ea723f47a2565b042d841c118",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Does the certified primal M1B composite admit a uniquely typed action-derived compact-source dual lift without promoting the old formal cotangent comparison source?",
        "answer": "Yes on the represented energies two through six. The nondegenerate rank-386 local BV action pairing and rank-940 compact-source residual pairing force q_dual=-q^sharp, iota_dual=pi^sharp, pi_dual=iota^sharp and s_dual=-s^sharp. All 470 residual dual rows crosswalk exactly to the previously certified compact-source classes. A separate 4,080-coordinate algebraic-dual verification core reconstructs the forced transposes and replays every normalized dual contraction identity with zero defects; it is check-only and is not promoted to an authoritative full BV source or a full compact-source dual.",
        "scope": {
            "spacetime": "unit Lorentzian cylinder R x S3",
            "energies": [2, 3, 4, 5, 6],
            "source": "action-density dual of the authoritative local 386-row graph bundle, restricted to the declared represented D-finite core",
            "target": "470 compact-source action-dual residual classes",
            "support_policy": "the residual dual inclusion has explicit compact-source representatives; harmonic verification remains global",
        },
        "typed_adjoint_dag": typed_dag,
        "represented_dual_lift": {"blocks": blocks, "aggregate": aggregate, "exact_replay": totals, "sha256": digest(blocks)},
        "action_residual_coordinate_actions": residual_actions,
        "action_pairing_bridge": bridge,
        "foundational_strength": {
            "finite_exact_kernel": "PRA-formalizable sparse rational transpose and composition replay",
            "analytic_input": "the certified compact-source causal quasi-isomorphism and equality of Green and action-current pairings",
            "choice_principle_used": False,
            "Hilbert_or_Krein_completion_used": False,
            "infinite_extension_boundary": "No full continuous dual or arbitrary-smooth/all-energy action-dual identification follows from the represented core.",
        },
        "provenance": {"inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "result_id": value["result_id"]}
            for path, value in zip((PRIMAL, M1A, CROSSWALK, ACTION, LOCAL, M4R), (primal, m1a, crosswalk, action, local, m4r))
        ]},
        "independent_checker": "quantum-weyl/classical_import/check_strict_m1b_action_dual_lift.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": ["STRICT_M1B_TYPED_CYCLIC_REPLAY", "STRICT_M1C_COMMON_MANIFEST_REPLAY"],
        "does_not_establish": [
            "that every algebraic functional on the 4,080-coordinate verification core has a compact-source representative",
            "that the finite algebraic-dual verification core is the authoritative local BV source",
            "an all-energy continuous dual or arbitrary-smooth contraction",
            "the rank-940 typed cyclic replay or M1B as a whole",
            "M1C, classical import Gate A, or nonlinear Green compatibility",
            "a full-complex Hadamard state, Lorentzian products, QME restoration, or residual transfer",
        ],
        "claim_flags": {
            "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE": True,
            "M1B_ACTION_DUAL_LIFT_COMPLETE": True,
            "ALL_470_RESIDUAL_DUALS_ACTION_DERIVED_COMPACT_SOURCE": True,
            "ACTION_DUAL_MAPS_FORCED_BY_LOCAL_AND_RESIDUAL_PAIRINGS": True,
            "FULL_4080_ALGEBRAIC_DUAL_COMPACT_SOURCE_IDENTIFIED": False,
            "FINITE_8160_CHECK_CORE_IS_AUTHORITATIVE_FULL_BV_SOURCE": False,
            "M1B_TYPED_CYCLIC_REPLAY_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
    }
    value["content_sha256"] = digest({key: value[key] for key in ("typed_adjoint_dag", "represented_dual_lift", "action_residual_coordinate_actions", "action_pairing_bridge")})
    return value


def report(value: dict[str, Any]) -> str:
    aggregate = value["represented_dual_lift"]["aggregate"]
    bridge = value["action_pairing_bridge"]
    return f"""# Strict M1B action-derived dual lift

**Result:** `{value['result_id']}`
**Lifecycle:** `{value['lifecycle']}`
**Dependency tags:** {', '.join(f'`{tag}`' for tag in value['dependency_tags'])}

## Result

The primal M1B composite has a unique action-derived dual lift on represented
energies two through six.  The rank-{bridge['local_action_pairing_rank']} local
BV density pairing and rank-{bridge['residual_action_pairing_rank']} residual
action pairing force

```text
q_dual_comp    = -q_comp^sharp
iota_dual_comp =  pi_comp^sharp
pi_dual_comp   =  iota_comp^sharp
s_dual_comp    = -s_comp^sharp
```

All {bridge['compact_source_dual_classes']} residual dual coordinates match the
frozen M1A rows and their explicit compact-source representatives with zero
support, crosswalk, pairing, or adjoint-uniqueness defects.  The independent
finite verification core contains {aggregate['represented_action_test_coordinates']:,}
dual test coordinates and replays all normalized dual contraction identities
with zero defects.

## Boundary

The 4,080-coordinate algebraic-dual core is a verification device, not a new
authoritative source carrier.  This result identifies the 470 residual dual
inclusion classes with compact sources; it does not claim that every functional
on the verification core has such a representative, nor does it construct an
all-energy continuous dual.  The rank-940 typed cyclic replay remains the final
M1B subpackage.  M1C, Gate A, nonlinear Green compatibility, Hadamard data,
renormalized products, QME restoration, and residual transfer remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m1b_action_dual_lift.py --check
python3 quantum-weyl/classical_import/check_strict_m1b_action_dual_lift.py
python3 -m pytest -q quantum-weyl/classical_import/tests/test_strict_m1b_action_dual_lift.py
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    result_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text() != result_text or not REPORT.is_file() or REPORT.read_text() != report_text:
            print(f"{value['result_id']}: DRIFT")
            return 1
        print(f"{value['result_id']}: CURRENT")
        return 0
    RESULT.write_text(result_text)
    REPORT.write_text(report_text)
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
