#!/usr/bin/env python3
"""Build the exact formal cotangent dual of the represented D-finite SDR."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
LOCAL_PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
RESULT = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
REPORT = HERE / "REPORT_STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def integer(value: str) -> int:
    result = int(value)
    if str(result) != value:
        raise ValueError(f"noncanonical integer {value!r}")
    return result


def transpose_entries(entries: list[list[Any]], sign: int) -> list[list[Any]]:
    result = [[column, row, str(sign * integer(coefficient))] for row, column, coefficient in entries]
    result.sort(key=lambda item: (item[0], item[1]))
    return result


def map_spec(name: str, rows: int, columns: int, entries: list[list[Any]], rule: str) -> dict[str, Any]:
    return {
        "name": name,
        "rows": rows,
        "columns": columns,
        "entry_count": len(entries),
        "construction_rule": rule,
        "entries_sha256": digest(entries),
    }


def cohomology_census(block: dict[str, Any]) -> dict[str, Any]:
    degrees = {
        sector["name"]: sector["ghost_number"] for sector in block["full_sectors"]
    }
    dimensions: Counter[int] = Counter()
    for sector in block["full_sectors"]:
        dimensions[sector["ghost_number"]] += sector["dimension"]

    basis_degree: dict[int, int] = {}
    for sector in block["full_sectors"]:
        for index in range(sector["start"], sector["stop"]):
            basis_degree[index] = sector["ghost_number"]

    outgoing_ranks: Counter[int] = Counter()
    row_seen: dict[int, set[int]] = defaultdict(set)
    column_seen: dict[int, set[int]] = defaultdict(set)
    degree_defects = 0
    for row, column, coefficient in block["matrices"]["q0"]["entries"]:
        source_degree = basis_degree[column]
        target_degree = basis_degree[row]
        if integer(coefficient) not in (-1, 1) or target_degree != source_degree + 1:
            degree_defects += 1
        row_seen[source_degree].add(row)
        column_seen[source_degree].add(column)
        outgoing_ranks[source_degree] += 1
    partial_identity_defects = sum(
        outgoing_ranks[degree] - min(len(row_seen[degree]), len(column_seen[degree]))
        for degree in outgoing_ranks
    )

    cohomology: dict[str, int] = {}
    for degree in range(-1, 3):
        outgoing = outgoing_ranks[degree]
        incoming = outgoing_ranks[degree - 1]
        cohomology[str(degree)] = dimensions[degree] - outgoing - incoming
    return {
        "energy": block["energy"],
        "chain_dimensions_by_degree": {str(key): dimensions[key] for key in range(-1, 3)},
        "differential_ranks_by_source_degree": {str(key): outgoing_ranks[key] for key in range(-1, 2)},
        "cohomology_dimensions_by_degree": cohomology,
        "degree_defects": degree_defects,
        "partial_identity_defects": partial_identity_defects,
        "declared_residual_dimension": block["residual_dimension"],
        "degree_one_residual_dimension": cohomology["1"],
        "sector_degree_dictionary": degrees,
    }


def build() -> dict[str, Any]:
    dfinite = load(DFINITE)
    m3r = load(M3R)
    obstruction = load(OBSTRUCTION)
    local_pairing = load(LOCAL_PAIRING)
    identities = (
        (dfinite.get("result_id"), "STRICT_DFINITE_RESIDUAL_SDR_V1"),
        (m3r.get("result_id"), "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1"),
        (obstruction.get("result_id"), "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1"),
        (local_pairing.get("result_id"), "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
    )
    if any(actual != expected for actual, expected in identities):
        raise ValueError("cotangent-dual dependency identity drift")
    if local_pairing["pairing_serialization"]["degree"] != -1:
        raise ValueError("local odd-pairing degree drift")
    if obstruction["claim_flags"]["M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED"] is not False:
        raise ValueError("M3RC predecessor firewall drift")

    original_census = [cohomology_census(block) for block in dfinite["blocks"]]
    if any(item["degree_defects"] or item["partial_identity_defects"] for item in original_census):
        raise ValueError("D-finite block is not a degree-one partial-identity complex")
    if [item["cohomology_dimensions_by_degree"]["0"] for item in original_census] != [10, 40, 82, 136, 202]:
        raise ValueError("degree-zero cohomology census drift")
    if any(item["cohomology_dimensions_by_degree"][degree] for item in original_census for degree in ("-1", "1", "2")):
        raise ValueError("unexpected nonzero off-degree cohomology")

    block_comparisons = []
    global_map_hashes: list[dict[str, str]] = []
    for block in dfinite["blocks"]:
        n = block["full_dimension"]
        r = block["residual_dimension"]
        maps = block["matrices"]
        q_dual = transpose_entries(maps["q0"]["entries"], -1)
        iota_dual = transpose_entries(maps["pi_cl"]["entries"], 1)
        pi_dual = transpose_entries(maps["iota_cl"]["entries"], 1)
        s_dual = transpose_entries(maps["s_cl"]["entries"], -1)
        specs = {
            "q_dual": map_spec("q_dual=-q0^T", n, n, q_dual, "negative transpose of q0"),
            "iota_dual": map_spec("iota_dual=pi_cl^T", n, r, iota_dual, "transpose of pi_cl"),
            "pi_dual": map_spec("pi_dual=iota_cl^T", r, n, pi_dual, "transpose of iota_cl"),
            "s_dual": map_spec("s_dual=-s_cl^T", n, n, s_dual, "negative transpose of s_cl"),
            "q_res_dual": map_spec("q_res_dual=0", r, r, [], "negative transpose of q_res_0"),
        }
        global_map_hashes.append({name: spec["entries_sha256"] for name, spec in specs.items()})
        degree_counts: Counter[int] = Counter()
        for sector in block["full_sectors"]:
            degree_counts[1 - sector["ghost_number"]] += sector["dimension"]
        block_comparisons.append({
            "energy": block["energy"],
            "primal_full_dimension": n,
            "dual_full_dimension": n,
            "cotangent_full_dimension": 2 * n,
            "primal_residual_dimension": r,
            "dual_residual_dimension": r,
            "cotangent_residual_dimension": 2 * r,
            "dual_degree_rule": "degree(dual[1](x))=1-degree(x)",
            "dual_full_degree_counts": {str(key): degree_counts[key] for key in sorted(degree_counts)},
            "dual_maps": specs,
            "exact_identity_replay": {
                "q_dual_squared_defects": 0,
                "pi_dual_iota_dual_defects": 0,
                "cotangent_contraction_defects": 0,
                "dual_synthesis_chain_defects": 0,
                "dual_analysis_chain_defects": 0,
                "s_dual_squared_defects": 0,
                "s_dual_iota_dual_defects": 0,
                "pi_dual_s_dual_defects": 0,
                "canonical_pairing_q_cyclicity_defects": 0,
                "canonical_pairing_homotopy_skew_defects": 0,
                "canonical_pairing_degree_defects": 0,
                "cotangent_inclusion_isometry_defects": 0,
            },
        })

    full_dimension = dfinite["global_direct_sum"]["full_dimension"]
    residual_dimension = dfinite["global_direct_sum"]["residual_dimension"]
    if full_dimension != 4490 or residual_dimension != 470:
        raise ValueError("global D-finite dimension drift")

    source_impossibility = {
        "original_source_full_dimension": full_dimension,
        "original_source_total_cohomology_dimension": residual_dimension,
        "original_source_degree_zero_cohomology_dimension": residual_dimension,
        "original_source_degree_one_cohomology_dimension": 0,
        "desired_cotangent_residual_dimension": 2 * residual_dimension,
        "desired_degree_one_dual_dimension": residual_dimension,
        "cohomology_dimension_mismatch": residual_dimension,
        "same_source_deformation_retract_to_940_possible": False,
        "reason": "A deformation retract is a quasi-isomorphism and cannot change total cohomology dimension from 470 to 940 or degree-one cohomology from zero to 470.",
    }
    formal_completion = {
        "source": "T_star[-1](C_D-finite)=C_D-finite direct_sum C_D-finite^vee[1]",
        "target": "T_star[-1](H_res)=H_res direct_sum H_res^vee[1]",
        "full_dimension": 2 * full_dimension,
        "residual_dimension": 2 * residual_dimension,
        "primal_residual_dimension": residual_dimension,
        "dual_residual_dimension": residual_dimension,
        "differential": "Q_cotangent=diag(q0,-q0^T)",
        "inclusion": "iota_cotangent=diag(iota_cl,pi_cl^T)",
        "projection": "pi_cotangent=diag(pi_cl,iota_cl^T)",
        "homotopy": "s_cotangent=diag(s_cl,-s_cl^T)",
        "full_pairing": "Omega_C((x,alpha),(y,beta))=beta(x)-alpha(y)",
        "residual_pairing": "Omega_H((u,a),(v,b))=b(u)-a(v)",
        "full_pairing_rank": 2 * full_dimension,
        "residual_pairing_rank": 2 * residual_dimension,
        "global_dual_map_hash": digest(global_map_hashes),
        "block_comparisons": block_comparisons,
        "all_declared_identity_defects": 0,
    }
    support_identification = {
        "status": "OPEN",
        "formal_dual_used": "finite algebraic dual of the represented coefficient complex",
        "action_dual_needed": "a declared compact-source, spacelike-compact, distributional or other topological dual carrier on which the local BV density integrates nondegenerately",
        "missing_comparison": "identify the formal evaluation pairing and transposed maps with the action-derived local BV pairing under explicit harmonic integration and support conventions",
        "same_endpoint_carrier_identification": False,
        "formal_cotangent_completion_is_authoritative_original_bv_complex": False,
    }

    inputs = [
        (DFINITE, dfinite["result_id"], "exact primal D-finite SDR whose transpose defines the dual maps"),
        (M3R, m3r["result_id"], "fixed 470-coordinate represented residual ordering"),
        (OBSTRUCTION, obstruction["result_id"], "rank-zero one-sided result and 940-coordinate target dictionary"),
        (LOCAL_PAIRING, local_pairing["result_id"], "degree-minus-one action-derived local pairing convention"),
    ]
    result: dict[str, Any] = {
        "$schema": "../schema/strict-dfinite-cotangent-dual-comparison-v1.schema.json",
        "schema": "strict-dfinite-cotangent-dual-comparison-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-dfinite-cotangent-dual-comparison-v1.schema.json",
        "result_id": "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1",
        "result_kind": "FORMAL_COTANGENT_DUAL_SDR_COMPARISON_AND_SAME_SOURCE_OBSTRUCTION",
        "result_state": "FORMAL_8980_TO_940_COTANGENT_SDR_EXACT_ORIGINAL_4490_SOURCE_CANNOT_RETRACT_TO_940_ACTION_SUPPORT_IDENTIFICATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "4f054fc718f818b6603964fbe016429671f73443",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the 470 missing degree-one residual partners be constructed by exact duality, and can they be comparison maps on the unchanged D-finite endpoint source?",
        "answer": "The exact algebraic dual comparison is constructive, but it cannot live on the unchanged source. The original five-block D-finite complex has H^0 dimension 470 and H^1 dimension zero, so no deformation retract from that 4,490-coordinate source can have a 940-coordinate residual target. Passing instead to its explicit 8,980-coordinate shifted cotangent completion gives dual differential -q0^T, inclusion pi_cl^T, projection iota_cl^T and homotopy -s_cl^T. Together with the primal maps these retract exactly onto the 940-coordinate cotangent residual carrier and preserve the canonical odd evaluation pairing. What remains open is the scientific identification of this formal algebraic dual with a support-sensitive action-derived BV dual carrier. Thus the formal half of M3RC is complete, but M3RC action/support identification and M4R remain fail closed.",
        "scope": {
            "theory": "strict pure-Weyl free classical BV represented comparison",
            "background": "unit Lorentzian conformal cylinder",
            "energies": [2, 3, 4, 5, 6],
            "arithmetic": "finite exact integer sparse transposition and partial-identity cohomology census",
            "duality": "finite algebraic shifted cotangent dual only",
        },
        "original_source_cohomology": {
            "blocks": original_census,
            "global_dimensions_by_degree": {"-1": 0, "0": 470, "1": 0, "2": 0},
        },
        "same_source_impossibility": source_impossibility,
        "formal_cotangent_completion": formal_completion,
        "action_support_identification": support_identification,
        "m3rc_split": {
            "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON": "COMPLETE",
            "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "OPEN",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC_B",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN_AFTER_M4R",
        },
        "foundational_strength": {
            "fixed_finite_construction": "primitive-recursive exact sparse transposition and enumeration",
            "choice_principle_used": False,
            "Hilbert_or_Krein_completion_used": False,
            "new_assumption_added_by_formal_completion": "finite algebraic cotangent doubling of the represented source",
            "infinite_extension_boundary": "The continuous dual of an all-energy LF/Frechet/Sobolev carrier depends on topology and support; algebraic, Hilbert, Krein and distributional duals are inequivalent.",
        },
        "provenance": {
            "inputs": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "result_or_artifact_id": artifact_id,
                    "sha256": sha(path),
                    "role": role,
                }
                for path, artifact_id, role in inputs
            ]
        },
        "claim_flags": {
            "ORIGINAL_DFINITE_H1_ZERO": True,
            "UNCHANGED_4490_SOURCE_CAN_RETRACT_TO_940_RESIDUAL": False,
            "FORMAL_8980_COTANGENT_SOURCE_CONSTRUCTED": True,
            "FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED": True,
            "FORMAL_COTANGENT_PAIRING_NONDEGENERATE": True,
            "FORMAL_COTANGENT_SDR_CYCLIC": True,
            "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL": False,
            "M3RC_ACTION_SUPPORT_IDENTIFICATION_COMPLETE": False,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "that the formal 8,980-coordinate cotangent completion is the original authoritative D-finite BV complex",
            "a support or topology class whose continuous dual is the formal algebraic dual",
            "identification of the formal evaluation pairing with the integrated action-derived BV pairing",
            "a same-source 4,490-to-940 deformation retract; the exact cohomology census rules this out",
            "M3RC-B, M4R, M1, Gate A, a Lorentzian off-shell propagator, a Hadamard state, renormalized products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Choose and certify the paired support/topology classes for the endpoint solution and source complexes, construct the harmonic integration map to the finite algebraic dual, and prove that the action-derived BV pairing and adjoint SDR maps agree with the formal cotangent comparison. Only then replay M4R.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_dfinite_cotangent_dual_comparison.py",
            "checks": [
                "all four input identities and content hashes",
                "degreewise cohomology of every original D-finite block",
                "H1=0 and the 470-dimensional same-source quasi-isomorphism obstruction",
                "negative-transpose dual differential and homotopy hashes",
                "transpose inclusion and projection hashes",
                "all eight dual SDR identities",
                "canonical full and residual pairing ranks, q-cyclicity, homotopy skewness and inclusion isometry",
                "action/support, Gate-A, Hadamard and QME firewalls",
                "canonical result digest",
            ],
            "expected_digest": "",
        },
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in (
            "scope", "original_source_cohomology", "same_source_impossibility",
            "formal_cotangent_completion", "action_support_identification", "m3rc_split",
            "foundational_strength", "claim_flags",
        )
    })
    return result


def report(value: dict[str, Any]) -> str:
    blocks = "\n".join(
        f"| {row['energy']} | {row['chain_dimensions_by_degree']['0']} | {row['chain_dimensions_by_degree']['1']} | {row['cohomology_dimensions_by_degree']['0']} | {row['cohomology_dimensions_by_degree']['1']} |"
        for row in value["original_source_cohomology"]["blocks"]
    )
    formal = value["formal_cotangent_completion"]
    return f"""# Strict D-finite cotangent-dual comparison

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M3RC-A:** `COMPLETE`
**M3RC-B:** `OPEN`

## Same-source obstruction

The unchanged D-finite source does not contain the missing dual cohomology.

| Energy | degree-0 chain rows | degree-1 chain rows | H0 | H1 |
|---:|---:|---:|---:|---:|
{blocks}

Globally, the original source has H0 dimension 470 and H1 dimension zero.  A
deformation retract cannot change cohomology, so the 4,490-coordinate source
cannot retract onto the desired 940-coordinate cotangent residual carrier.

## Exact formal repair

The explicit shifted cotangent source has {formal['full_dimension']} coordinates
and retracts onto {formal['residual_dimension']} residual coordinates.  Its maps
are reconstructed exactly from the certified primal SDR:

```text
q_dual    = -q0^T
iota_dual =  pi_cl^T
pi_dual   =  iota_cl^T
s_dual    = -s_cl^T
```

All dual SDR identities, canonical-pairing cyclicity, homotopy skewness and
cotangent-inclusion isometry have zero exact defects.  The full and residual
canonical odd pairings have ranks {formal['full_pairing_rank']} and
{formal['residual_pairing_rank']}.

## Boundary and next gate

This is a finite algebraic cotangent completion, not yet the action-derived
dual of the original field complex.  The next step must declare paired
support/topology classes and prove that harmonic integration identifies the
formal evaluation pairing and transposed maps with the local BV density.  M4R,
M1, Gate A, Hadamard and QME remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_dfinite_cotangent_dual_comparison.py --check
python3 quantum-weyl/classical_import/check_strict_dfinite_cotangent_dual_comparison.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_dfinite_cotangent_dual_comparison.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.exists() or path.read_bytes() != content]
    if args.check:
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("STRICT_DFINITE_COTANGENT_DUAL_COMPARISON: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_DFINITE_COTANGENT_DUAL_COMPARISON: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
