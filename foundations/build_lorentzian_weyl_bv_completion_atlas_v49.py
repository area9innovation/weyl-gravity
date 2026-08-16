#!/usr/bin/env python3
"""Build Atlas V49 after strict nonlinear Green and BRST Hadamard closure."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48.json"
CAUSAL = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
HADAMARD = ROOT / "quantum-weyl/lorentzian/certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v49.schema.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v49.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v30_reconciliation", "strict_m1b_action_dual_lift",
        "strict_m1b_typed_cyclic_composite", "strict_m1c_common_snapshot",
        "strict_m2_q2_q3_typed_green_compatibility",
        "strict_386_brst_hadamard_two_point", "route_selection",
        "research_queue", "claim_flags", "does_not_establish",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(row for row in value["branches"] if row["id"] == branch_id)
    return next(row for row in branch["stages"] if row["stage"] == stage_id)


def old_route(previous: dict[str, Any], name: str, rank: int) -> dict[str, Any]:
    row = deepcopy(next(item for item in previous["route_selection"] if item["route"] == name))
    row["rank"] = rank
    return row


def new_route(rank: int, name: str, recommendation: str, tractability: str) -> dict[str, Any]:
    return {
        "rank": rank,
        "route": name,
        "branch": "STRICT_PURE_WEYL_386",
        "scientific_leverage": "VERY_HIGH",
        "tractability": tractability,
        "dependency_depth": "HIGH",
        "recommendation": recommendation,
    }


def build() -> dict[str, Any]:
    previous, causal, hadamard = map(load, (PREDECESSOR, CAUSAL, HADAMARD))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48":
        raise ValueError("Atlas V48 predecessor drift")
    if causal.get("result_id") != "STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1":
        raise ValueError("strict nonlinear Green authority drift")
    if hadamard.get("result_id") != "STRICT_386_BRST_HADAMARD_TWO_POINT_V1":
        raise ValueError("strict Hadamard authority drift")
    if causal["claim_flags"]["NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED"] is not True:
        raise ValueError("nonlinear Green gate is not certified")
    hflags = hadamard["claim_flags"]
    if not all(hflags[key] for key in (
        "STRICT_386_FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED",
        "STRICT_386_HADAMARD_WAVEFRONT_CONDITION_CERTIFIED",
        "STRICT_386_BRST_WARD_IDENTITIES_CERTIFIED",
        "STRICT_386_GRADED_CCR_CERTIFIED",
    )):
        raise ValueError("BRST Hadamard gate is not certified")
    if any(hflags[key] for key in (
        "STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED",
        "STRICT_386_PHYSICAL_COHOMOLOGY_POSITIVITY_CERTIFIED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
        "LORENTZIAN_QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    )):
        raise ValueError("Hadamard downstream boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v49",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49",
        "created": "2026-08-16",
        "question": "What becomes the strict pure-Weyl frontier after nonlinear typed Green compatibility and a full-complex BRST Hadamard pair are certified?",
        "answer": "Atlas V49 closes the classical-to-Hadamard bridge on the same immutable 386-row Gate-A snapshot. Both q2 and q3 compose with the retarded and advanced Green homotopies; every finite same-orientation q2/q3 tree is typed, and the general second nonlinear source is closed. A whole-projector cylinder spectral split then gives a full-row BRST-compatible Hadamard two-point pair with exact graded CCR, both Ward identities, retained scalar zero mode and the required wavefront relation. The result is deliberately a pseudo-state: positivity on physical cohomology is neither satisfied by the selected split nor inferred. Renormalized Lorentzian products, QME restoration, residual transfer and a complete quantum theory remain open.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": str(REPORT.relative_to(ROOT)),
    })

    compatibility = causal["compatibility_replay"]
    trees = causal["polarized_finite_tree_theorem"]
    source2 = causal["lambda2_general_source_cocycle"]
    value["strict_m2_q2_q3_typed_green_compatibility"] = {
        "result_id": causal["result_id"],
        "content_sha256": causal["content_sha256"],
        "snapshot_id": causal["scope"]["snapshot_id"],
        "snapshot_sha256": causal["scope"]["snapshot_sha256"],
        "carrier_rows": causal["scope"]["carrier_rows"],
        "orientations_checked": compatibility["green_homotopy_orientations_checked"],
        "nonlinear_arities": causal["scope"]["nonlinear_arities"],
        "exact_or_structural_defects": compatibility["total_exact_or_structural_defects"],
        "all_finite_same_orientation_q2_q3_trees": trees["all_finite_same_orientation_trees"],
        "general_second_source_cocycle_closed": source2["structural_defects"] == 0,
        "arbitrary_mixed_orientation_trees": trees["arbitrary_mixed_orientation_trees"],
        "infinite_tree_series_convergence": trees["infinite_tree_sum_or_convergence"],
    }
    obligations = hadamard["proof_obligations"]
    value["strict_386_brst_hadamard_two_point"] = {
        "result_id": hadamard["result_id"],
        "content_sha256": hadamard["content_sha256"],
        "hadamard_snapshot_sha256": hadamard["hadamard_snapshot"]["sha256"],
        "classical_snapshot_id": hadamard["scope"]["classical_snapshot_id"],
        "classical_snapshot_sha256": hadamard["scope"]["classical_snapshot_sha256"],
        "carrier_rows": 386,
        "parent_rank_profile": hadamard["parent_BRST_proof"]["parent_rank_profile"],
        "proof_obligations": len(obligations) - 1,
        "proof_defects": sum(row["defects"] for key, row in obligations.items() if key != "sha256"),
        "zero_mode_retained": hflags["STRICT_386_ZERO_MODE_RETAINED_AND_SPLIT"],
        "BRST_Ward_exact": hflags["STRICT_386_BRST_WARD_IDENTITIES_CERTIFIED"],
        "graded_CCR_exact": hflags["STRICT_386_GRADED_CCR_CERTIFIED"],
        "Hadamard_wavefront_exact": hflags["STRICT_386_HADAMARD_WAVEFRONT_CONDITION_CERTIFIED"],
        "object_type": hadamard["state_and_positivity_boundary"]["object_type"],
        "positive_state_constructed": hflags["STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED"],
        "physical_cohomology_positivity": hflags["STRICT_386_PHYSICAL_COHOMOLOGY_POSITIVITY_CERTIFIED"],
    }

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "CERTIFIED_TYPED_Q2_Q3_GREEN_COMPATIBILITY",
        "statement": "The complete Gate-A q2/q3 operations compose with both typed Lorentzian Green orientations. Exact q1/q2, arity-three, cyclic and adjoint defects vanish; all finite same-orientation trees are defined and the general second nonlinear source is a cocycle.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], causal["result_id"]])),
        "boundary": "Arbitrary mixed-sign trees, an infinite convergent Moller series and a nonperturbative inverse remain open.",
    })
    hadamard_stage = stage(value, "STRICT_PURE_WEYL_386", "S4_HADAMARD_CCR")
    hadamard_stage.update({
        "status": "CERTIFIED_FULL_386_HADAMARD_CCR_PSEUDO_STATE",
        "statement": "A whole-Hodge-projector spectral split constructs a Hadamard two-point pair on all 386 BV rows. Both modal wave equations, the graded CCR, the vector-valued Hadamard wavefront relation, stationarity and the retained scalar zero mode are certified.",
        "evidence": list(dict.fromkeys([*hadamard_stage["evidence"], hadamard["result_id"]])),
        "boundary": "The pair is an indefinite BRST pseudo-state. It is not a positive Hadamard state and does not decide positivity on physical cohomology.",
    })
    ward_stage = stage(value, "STRICT_PURE_WEYL_386", "S5_BRST_WARD")
    ward_stage.update({
        "status": "CERTIFIED_EXACT_FULL_386_BRST_WARD",
        "statement": "Whole-projector Hodge spectral calculus intertwines the parent BRST differential and witness. Exact chain and cyclic transport therefore give both BRST Ward identities on the complete graph carrier.",
        "evidence": list(dict.fromkeys([*ward_stage["evidence"], hadamard["result_id"]])),
        "boundary": "Free Ward compatibility does not construct renormalized time-ordered products or restore the interacting local QME.",
    })
    final_stage = stage(value, "STRICT_PURE_WEYL_386", "S10_LORENTZIAN_CERTIFIED")
    final_stage.update({
        "status": "FREE_HADAMARD_LAYER_CERTIFIED_FULL_THEORY_FAIL_CLOSED",
        "statement": "The free full-complex causal and BRST Hadamard layer is Lorentzian-certified on the unit cylinder. The complete interacting Lorentzian quantum lifecycle is not certified.",
        "evidence": list(dict.fromkeys([*final_stage["evidence"], causal["result_id"], hadamard["result_id"]])),
        "boundary": "Physical positivity, renormalized products, QME restoration, residual quantum transfer and a complete Lorentzian theory remain open.",
    })

    routes = [
        new_route(
            1,
            "STRICT_PHYSICAL_COHOMOLOGY_POSITIVITY_DECISION",
            "Determine whether any BRST Hadamard representative descends to a positive physical cohomology covariance, or prove a scoped positivity obstruction that keeps the Krein boundary explicit.",
            "LOW",
        ),
        new_route(
            2,
            "STRICT_LORENTZIAN_RENORMALIZED_TIME_ORDERED_PRODUCTS",
            "Use the certified Hadamard pair to define the first local covariant Wick and time-ordered products on the same 386-row carrier, with wavefront and scaling-degree receipts.",
            "LOW",
        ),
        new_route(
            3,
            "STRICT_LOCAL_ANOMALY_CLASSIFICATION_AND_QME_RESTORATION",
            "Reconcile the existing local anomaly classification with the Lorentzian product scheme, compute only the surviving coefficients, and restore or obstruct the local QME before residual transfer.",
            "LOW",
        ),
        old_route(previous, "STRICT_D_CARTAN_AND_CHARGE_DECISION", 4),
        old_route(previous, "STRICT_ANALYTIC_MOLLER_CONVERGENCE", 5),
        old_route(previous, "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", 6),
        old_route(previous, "DIRECT_SPACETIME_Q26_HADAMARD", 7),
    ]
    value["route_selection"] = routes
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": row["recommendation"]}
        for row in routes
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_PHYSICAL_COHOMOLOGY_POSITIVITY_DECISION",
        "route_count": 7,
        "completed_since_v48": [
            "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY",
            "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
            "STRICT_BRST_HADAMARD_TWO_POINT",
            "STRICT_FULL_386_BRST_WARD",
        ],
        "new_positive_result": "The immutable Gate-A complex now has a post-freeze typed nonlinear causal envelope and a full-row BRST Hadamard pseudo-state pair with eleven passed obligations.",
        "surprise": "The scalar Hodge zero mode is not an obstruction to Hadamard regularity: the scale-free stationary split +/- i(t-t')/2 supplies the commutator as a smooth finite-rank term. It is instead a clean witness that the selected pair is not positive.",
        "hard_boundary": "Hadamard regularity, graded CCR and Ward identities do not imply positivity, renormalized products or the QME. The result is a free pseudo-state layer, not a complete quantum theory.",
    }
    value["claim_flags"].update({
        "v48_preserved": True,
        "strict_386_q2_q3_green_compatibility_certified": True,
        "strict_386_lambda2_general_source_cocycle_closed": True,
        "strict_386_full_bv_hadamard_two_point_constructed": True,
        "strict_386_full_bv_brst_ward_certified": True,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_386_physical_cohomology_positivity_certified": False,
        "renormalized_lorentzian_products_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "residual_quantum_transfer_authorized": False,
        "lorentzian_full_theory_certified": False,
    })
    closed_nonclaims = {
        "q2/q3 compatibility with both typed advanced and retarded Lorentzian Green homotopies",
        "general lambda-squared source-cocycle closure or an analytic Moller inverse",
        "a full-complex BRST-compatible Hadamard two-point function or a no-go theorem for one",
    }
    value["does_not_establish"] = [
        item for item in previous["does_not_establish"] if item not in closed_nonclaims
    ] + [
        "arbitrary mixed-orientation nonlinear Green trees or convergence of an infinite Moller series",
        "a positive full-complex Hadamard state or positive covariance on physical cohomology",
        "renormalized Lorentzian Wick or time-ordered products and a causal perturbative AQFT construction",
        "Lorentzian QME restoration, residual quantum transfer, particles, scattering or unitarity",
        "a complete interacting Lorentzian quantum theory",
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(PREDECESSOR),
            "role": "immutable Atlas V48 predecessor",
        },
        {
            "path": str(CAUSAL.relative_to(ROOT)),
            "result_or_artifact_id": causal["result_id"],
            "sha256": sha(CAUSAL),
            "role": "typed q2/q3 nonlinear Green compatibility and second-source closure",
        },
        {
            "path": str(HADAMARD.relative_to(ROOT)),
            "result_or_artifact_id": hadamard["result_id"],
            "sha256": sha(HADAMARD),
            "role": "full-row BRST Hadamard two-point pair with pseudo-state boundary",
        },
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v49.py",
        "checks": [
            "V48 predecessor and 77-cell preservation",
            "independent nonlinear Green and Hadamard receiver replays",
            "S3/S4/S5/free-layer stage promotion",
            "eleven Hadamard obligations and retained zero mode",
            "positivity/products/QME/full-theory firewalls",
            "post-Hadamard route retirement and ranking",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def report(value: dict[str, Any]) -> str:
    causal = value["strict_m2_q2_q3_typed_green_compatibility"]
    hadamard = value["strict_386_brst_hadamard_two_point"]
    routes = "\n".join(
        f"{row['rank']}. `{row['route']}` — {row['recommendation']}"
        for row in value["route_selection"]
    )
    return f"""# Lorentzian Weyl BV completion atlas v49

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Classical-to-Hadamard bridge

The immutable Gate-A snapshot `{causal['snapshot_id']}` now has both nonlinear
typed Green compatibility and a full-complex BRST Hadamard pair.  The nonlinear
receiver checks arities {causal['nonlinear_arities']} in both causal orientations
with {causal['exact_or_structural_defects']} exact or structural defects.  All
finite same-orientation q2/q3 trees are defined, and the general second source is
a cocycle.

The Hadamard receiver covers {hadamard['carrier_rows']} rows through the parent
rank profile `{hadamard['parent_rank_profile']}`.  All {hadamard['proof_obligations']}
bisolution, CCR, wavefront, Ward, reality, stationarity, zero-mode, policy and
coverage obligations pass with {hadamard['proof_defects']} defects.  The scalar
zero mode is retained as a smooth finite-rank term.

## Exact boundary

The constructed object is a BRST Hadamard pseudo-state pair, not a positive
Hadamard state.  Positivity on physical cohomology remains undecided.  No
renormalized Lorentzian product, causal perturbative AQFT construction, restored
QME, residual quantum transfer or complete quantum theory follows.

## Ranked routes

{routes}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n", report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
