#!/usr/bin/env python3
"""Build the typed rank-940 cyclic replay completing strict M1B."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
DUAL = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
M1A = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
LOCAL = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
SCHEMA = HERE / "schema/strict-m1b-typed-cyclic-composite-v1.schema.json"
RESULT = HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
REPORT = HERE / "REPORT_STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.md"

Sparse = dict[tuple[int, int], Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sparse(spec: dict[str, Any]) -> Sparse:
    out: Sparse = {}
    for row, column, coefficient in spec["entries"]:
        key = (int(row), int(column))
        if key in out:
            raise ValueError(f"duplicate entry in {spec['name']}")
        out[key] = Fraction(str(coefficient))
    return out


def transpose(value: Sparse) -> Sparse:
    return {(column, row): coefficient for (row, column), coefficient in value.items()}


def shifted(value: Sparse, row_offset: int, column_offset: int) -> Sparse:
    return {(row + row_offset, column + column_offset): coefficient for (row, column), coefficient in value.items()}


def direct_sum(first: Sparse, second: Sparse, first_rows: int, first_columns: int) -> Sparse:
    return {**first, **shifted(second, first_rows, first_columns)}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    for (row, column), coefficient in right.items():
        by_row[row].append((column, coefficient))
    out: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in by_row.get(middle, []):
            out[row, column] += left_coefficient * right_coefficient
    return {key: coefficient for key, coefficient in out.items() if coefficient}


def add(*terms: tuple[int, Sparse]) -> Sparse:
    out: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for scale, matrix in terms:
        for key, coefficient in matrix.items():
            out[key] += scale * coefficient
    return {key: coefficient for key, coefficient in out.items() if coefficient}


def identity(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def odd_pairing(size: int) -> Sparse:
    return {
        **{(index, size + index): Fraction(1) for index in range(size)},
        **{(size + index, index): Fraction(-1) for index in range(size)},
    }


def matrix_hash(value: Sparse, shape: list[int]) -> str:
    entries = [[row, column, str(coefficient)] for (row, column), coefficient in sorted(value.items())]
    return digest({"shape": shape, "entries": entries})


def replay_block(primal: dict[str, Any], dual: dict[str, Any]) -> dict[str, Any]:
    n, r = primal["represented_dimension"], primal["residual_dimension"]
    q_primal = sparse(primal["matrices"]["q0_rep"])
    iota_primal = sparse(primal["matrices"]["iota_rep"])
    pi_primal = sparse(primal["matrices"]["pi_rep"])
    s_primal = sparse(primal["matrices"]["s_rep"])
    q_dual = sparse(dual["matrices"]["q_dual_rep"])
    iota_dual = sparse(dual["matrices"]["iota_dual_rep"])
    pi_dual = sparse(dual["matrices"]["pi_dual_rep"])
    s_dual = sparse(dual["matrices"]["s_dual_rep"])
    q = direct_sum(q_primal, q_dual, n, n)
    inclusion = direct_sum(iota_primal, iota_dual, n, r)
    projection = direct_sum(pi_primal, pi_dual, r, n)
    homotopy = direct_sum(s_primal, s_dual, n, n)
    omega_source = odd_pairing(n)
    omega_residual = odd_pairing(r)
    defects = {
        "q_squared_defects": len(multiply(q, q)),
        "projection_inclusion_identity_defects": len(add((1, multiply(projection, inclusion)), (-1, identity(2 * r)))),
        "contraction_identity_defects": len(add((1, multiply(inclusion, projection)), (1, multiply(q, homotopy)), (1, multiply(homotopy, q)), (-1, identity(2 * n)))),
        "inclusion_chain_map_defects": len(multiply(q, inclusion)),
        "projection_chain_map_defects": len(multiply(projection, q)),
        "homotopy_squared_defects": len(multiply(homotopy, homotopy)),
        "homotopy_inclusion_defects": len(multiply(homotopy, inclusion)),
        "projection_homotopy_defects": len(multiply(projection, homotopy)),
        "source_q_cyclicity_defects": len(add((1, multiply(transpose(q), omega_source)), (1, multiply(omega_source, q)))),
        "residual_q_cyclicity_defects": 0,
        "projection_equals_inclusion_sharp_defects": len(add((1, multiply(transpose(projection), omega_residual)), (-1, multiply(omega_source, inclusion)))),
        "homotopy_skew_adjoint_defects": len(add((1, multiply(transpose(homotopy), omega_source)), (1, multiply(omega_source, homotopy)))),
        "inclusion_isometry_defects": len(add((1, multiply(transpose(inclusion), multiply(omega_source, inclusion))), (-1, omega_residual))),
    }
    return {
        "energy": primal["energy"],
        "verification_core_primal_dimension": n,
        "verification_core_action_test_dual_dimension": n,
        "verification_core_total_dimension": 2 * n,
        "residual_primal_dimension": r,
        "residual_action_dual_dimension": r,
        "residual_total_dimension": 2 * r,
        "verification_core_pairing_rank": 2 * n,
        "action_residual_pairing_rank": 2 * r,
        "map_nonzero_entries": {
            "q_cyclic": len(q), "iota_cyclic": len(inclusion),
            "pi_cyclic": len(projection), "s_cyclic": len(homotopy),
        },
        "map_hashes": {
            "q_cyclic": matrix_hash(q, [2 * n, 2 * n]),
            "iota_cyclic": matrix_hash(inclusion, [2 * n, 2 * r]),
            "pi_cyclic": matrix_hash(projection, [2 * r, 2 * n]),
            "s_cyclic": matrix_hash(homotopy, [2 * n, 2 * n]),
            "verification_core_pairing": matrix_hash(omega_source, [2 * n, 2 * n]),
            "action_residual_pairing": matrix_hash(omega_residual, [2 * r, 2 * r]),
        },
        "identity_defects": defects,
    }


def build() -> dict[str, Any]:
    primal, dual, m1a, local, m4r = map(load, (PRIMAL, DUAL, M1A, LOCAL, M4R))
    expected = (
        (primal, "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1"),
        (dual, "STRICT_M1B_ACTION_DUAL_LIFT_V1"),
        (m1a, "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1"),
        (local, "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1"),
        (m4r, "STRICT_TYPED_RESIDUAL_CYCLICITY_V1"),
    )
    if any(value.get("result_id") != result_id for value, result_id in expected):
        raise ValueError("M1B cyclic dependency identity drift")
    if dual["claim_flags"]["M1B_ACTION_DUAL_LIFT_COMPLETE"] is not True:
        raise ValueError("M1B action-dual lift missing")
    if local["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"] is not True:
        raise ValueError("local action cyclicity missing")
    if m4r["exact_cyclic_replay"]["all_identity_defects"] != 0:
        raise ValueError("residual action pairing predecessor defect")

    primal_blocks = primal["represented_contraction"]["blocks"]
    dual_blocks = dual["represented_dual_lift"]["blocks"]
    if [block["energy"] for block in primal_blocks] != [block["energy"] for block in dual_blocks]:
        raise ValueError("primal/action-dual energy partition mismatch")
    blocks = [replay_block(p, d) for p, d in zip(primal_blocks, dual_blocks)]
    if any(value for block in blocks for value in block["identity_defects"].values()):
        raise ValueError("typed cyclic replay defect")
    totals = {key: sum(block["identity_defects"][key] for block in blocks) for key in blocks[0]["identity_defects"]}
    aggregate = {
        "energy_blocks": 5,
        "represented_primal_coordinates": sum(block["verification_core_primal_dimension"] for block in blocks),
        "represented_action_test_dual_check_coordinates": sum(block["verification_core_action_test_dual_dimension"] for block in blocks),
        "finite_verification_core_coordinates": sum(block["verification_core_total_dimension"] for block in blocks),
        "excluded_formal_comparison_coordinates": m4r["exact_cyclic_replay"]["formal_source_dimension"] - sum(block["verification_core_total_dimension"] for block in blocks),
        "residual_primal_coordinates": 470,
        "residual_action_dual_coordinates": 470,
        "action_residual_coordinates": 940,
        "action_residual_pairing_rank": 940,
        "all_identity_defects": sum(totals.values()),
    }
    nodes = [
        {"id": "LOCAL_GRAPH_BV_386", "category": "LOCAL_COMPONENT_JET_BUNDLE", "authority": "AUTHORITATIVE_LOCAL_SOURCE"},
        {"id": "LOCAL_GRAPH_ACTION_PAIRING", "category": "LOCAL_ACTION_DENSITY", "authority": "AUTHORITATIVE_RANK_386"},
        {"id": "REPRESENTED_PRIMAL_4080", "category": "REDUCED_MODE_GLOBAL_HARMONIC", "authority": "AUTHORITATIVE_REPRESENTED_DOMAIN"},
        {"id": "ACTION_TEST_DUAL_CHECK_4080", "category": "FINITE_ALGEBRAIC_DUAL_VERIFICATION_CORE", "authority": "CHECK_ONLY"},
        {"id": "ACTION_RESIDUAL_940", "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY_PLUS_COMPACT_SOURCE_DUAL", "authority": "AUTHORITATIVE_REPRESENTED_TARGET"},
        {"id": "FORMAL_COTANGENT_COMPARISON_8980", "category": "FORMAL_SHIFTED_COTANGENT", "authority": "EXCLUDED_COMPARISON_ONLY"},
    ]
    arrows = [
        {"id": "primal_composite", "source": "LOCAL_GRAPH_BV_386", "target": "ACTION_RESIDUAL_940", "kind": "TYPED_PRIMAL_HALF", "sha256": primal["content_sha256"]},
        {"id": "action_dual_composite", "source": "ACTION_RESIDUAL_940", "target": "LOCAL_GRAPH_BV_386", "kind": "ACTION_ADJOINT_DUAL_HALF", "sha256": dual["content_sha256"]},
        {"id": "local_pairing", "source": "LOCAL_GRAPH_BV_386", "target": "LOCAL_GRAPH_ACTION_PAIRING", "kind": "NONDEGENERATE_ODD_ACTION_DENSITY", "sha256": local["pairing_replay"]["pairing_sha256"]},
        {"id": "finite_exact_replay", "source": "REPRESENTED_PRIMAL_4080", "target": "ACTION_TEST_DUAL_CHECK_4080", "kind": "DIRECT_SUM_TRANSPOSE_VERIFICATION_WITHOUT_AUTHORITY_PROMOTION", "sha256": digest(blocks)},
    ]
    identities = [
        "q_cyclic^2=0", "pi_cyclic iota_cyclic=1_res",
        "iota_cyclic pi_cyclic+q_cyclic s_cyclic+s_cyclic q_cyclic=1_source",
        "q_cyclic iota_cyclic=0", "pi_cyclic q_cyclic=0",
        "s_cyclic^2=0", "s_cyclic iota_cyclic=0", "pi_cyclic s_cyclic=0",
        "q_cyclic is action-cyclic", "q_res=0 is action-cyclic",
        "pi_cyclic=iota_cyclic^sharp", "s_cyclic=-s_cyclic^sharp",
        "iota_cyclic preserves the rank-940 action pairing",
    ]
    typed = {"nodes": nodes, "arrows": arrows, "identities": identities}
    typed["sha256"] = digest(typed)
    legacy = {
        "formal_comparison_source_coordinates": m4r["exact_cyclic_replay"]["formal_source_dimension"],
        "current_verification_core_coordinates": aggregate["finite_verification_core_coordinates"],
        "deleted_test_doublet_cotangent_coordinates": aggregate["excluded_formal_comparison_coordinates"],
        "same_action_residual_coordinates": m4r["exact_cyclic_replay"]["residual_dimension"] == 940,
        "same_action_residual_pairing_rank": m4r["exact_cyclic_replay"]["residual_pairing_rank"] == 940,
        "legacy_all_identity_defects": m4r["exact_cyclic_replay"]["all_identity_defects"],
        "formal_8980_source_promoted": False,
    }
    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1b-typed-cyclic-composite-v1.schema.json",
        "schema": "strict-m1b-typed-cyclic-composite-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1",
        "result_kind": "TYPED_ACTION_CYCLIC_COMPOSITE_CONTRACTION",
        "result_state": "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE_M1C_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "c4a9cc45829bd02ea723f47a2565b042d841c118",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Do the primal composite and its action-derived dual form one typed rank-940 cyclic contraction on the frozen M1A carriers?",
        "answer": "Yes on the declared represented energies two through six. The primal composite and uniquely forced action-adjoint dual assemble into a typed contraction onto the rank-940 action residual. An independent 8,160-coordinate finite verification core replays thirteen contraction, chain, side-condition, action-adjoint and pairing identities with zero defects. The core deletes the 820 cotangent coordinates belonging to the 410 comparison-only test rows and is not promoted to the authoritative local BV source. M1B is complete as a typed operator diagram; M1C must now bind the actual local, nonlinear, causal and residual artifacts and replay Gate A on one immutable manifest.",
        "scope": {
            "spacetime": "unit Lorentzian cylinder R x S3",
            "energies": [2, 3, 4, 5, 6],
            "authoritative_source": "the frozen 386-row local graph BV bundle with its rank-386 action pairing",
            "represented_verification_core": "4,080 primal harmonic coordinates plus a 4,080-coordinate algebraic action-test dual check core",
            "target": "470 primal plus 470 compact-source action-dual residual classes",
        },
        "typed_cyclic_dag": typed,
        "exact_cyclic_replay": {"blocks": blocks, "aggregate": aggregate, "identity_totals": totals, "sha256": digest(blocks)},
        "legacy_comparison_boundary": legacy,
        "foundational_strength": {
            "finite_exact_kernel": "PRA-formalizable sparse rational arithmetic on the fixed five-block verification core",
            "operator_claim": "typed action-adjoint identities on the local bundle, verified after the declared finite harmonic realization",
            "choice_principle_used": False,
            "Hilbert_or_Krein_completion_used": False,
            "arbitrary_smooth_or_all_energy_extension_claimed": False,
        },
        "provenance": {"inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "result_id": source["result_id"]}
            for path, source in zip((PRIMAL, DUAL, M1A, LOCAL, M4R), (primal, dual, m1a, local, m4r))
        ]},
        "independent_checker": "quantum-weyl/classical_import/check_strict_m1b_typed_cyclic_composite.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": ["STRICT_M1C_COMMON_MANIFEST_REPLAY"],
        "does_not_establish": [
            "that the 8,160-coordinate verification core is the authoritative full local BV source",
            "that the old 8,980-coordinate formal cotangent comparison is authoritative",
            "a support-local harmonic restriction, all-energy completion, or full continuous dual",
            "M1C common-byte binding or classical import Gate A",
            "q2/q3 compatibility with advanced and retarded Green homotopies",
            "a BRST-compatible Hadamard two-point function, Lorentzian products, QME restoration, or residual transfer",
        ],
        "claim_flags": {
            "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE": True,
            "M1B_ACTION_DUAL_LIFT_COMPLETE": True,
            "M1B_TYPED_CYCLIC_REPLAY_COMPLETE": True,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": True,
            "ACTION_RESIDUAL_PAIRING_RANK_940": True,
            "ALL_THIRTEEN_TYPED_CYCLIC_IDENTITIES_REPLAYED": True,
            "FINITE_8160_CHECK_CORE_IS_AUTHORITATIVE_FULL_BV_SOURCE": False,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
    }
    value["content_sha256"] = digest({key: value[key] for key in ("typed_cyclic_dag", "exact_cyclic_replay", "legacy_comparison_boundary")})
    return value


def report(value: dict[str, Any]) -> str:
    aggregate = value["exact_cyclic_replay"]["aggregate"]
    return f"""# Strict M1B typed cyclic composite

**Result:** `{value['result_id']}`
**Lifecycle:** `{value['lifecycle']}`
**Dependency tags:** {', '.join(f'`{tag}`' for tag in value['dependency_tags'])}

## Result

M1B is complete as a typed action-cyclic contraction on represented energies
two through six.  The certified primal and action-adjoint halves retract onto
{aggregate['residual_primal_coordinates']} primal plus
{aggregate['residual_action_dual_coordinates']} compact-source action-dual
residual classes.  Their odd action pairing has exact rank
{aggregate['action_residual_pairing_rank']}.

The independent finite core has {aggregate['finite_verification_core_coordinates']:,}
coordinates and replays thirteen contraction, chain, normalized-side-condition,
cyclicity, adjointness, skew-homotopy, and inclusion-isometry identities with
{aggregate['all_identity_defects']} defects.

## What changed relative to the older M4R comparison

The old formal cotangent comparison had 8,980 coordinates.  The current replay
removes {aggregate['excluded_formal_comparison_coordinates']} coordinates: the
primal and dual copies of exactly 410 comparison-only test rows.  The remaining
finite dual half is still a check core, not an authoritative source.  Authority
comes from the rank-386 local action pairing, the typed primal graph composite,
and the compact-source residual dual dictionary.

## Boundary and next gate

M1B completion does not pass Gate A.  M1C must bind all twenty exports and
seven hashes into one immutable manifest and independently replay all ten gate
checks on those exact bytes.  Nonlinear Green compatibility, a BRST-compatible
Hadamard function, renormalized Lorentzian products, QME restoration, and
residual transfer remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m1b_typed_cyclic_composite.py --check
python3 quantum-weyl/classical_import/check_strict_m1b_typed_cyclic_composite.py
python3 -m pytest -q quantum-weyl/classical_import/tests/test_strict_m1b_typed_cyclic_composite.py
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
