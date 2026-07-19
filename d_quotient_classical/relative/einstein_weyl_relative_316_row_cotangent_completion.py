#!/usr/bin/env python3
"""Build the canonical odd-cotangent completion of the relative carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_316_row_cotangent_completion_v1/layout.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-316-row-cotangent-completion.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-316-row-cotangent-completion-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_316_row_cotangent_completion.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_316_row_cotangent_completion.py"

DEPENDENCIES = {
    "rank_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1.json",
    "triangle": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "einstein_layout": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/row_layout.json",
    "einstein_q1": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/q1.json",
    "weyl_layout": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json",
    "weyl_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
    "inclusion": ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_product_chain_map_pbw_v1/inclusion.json",
    "current_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "current_layout": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return payload["content"]["rows"]


def _parity(degree: int) -> str:
    return "odd" if degree % 2 else "even"


def _artifact(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(payload.get("result_id", payload.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build_layout() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    current = values["current_layout"]
    current_rows = current["rows"]
    if len(current_rows) != 160:
        raise AssertionError("current carrier row count changed")
    weyl = _rows(values["weyl_layout"])
    einstein = _rows(values["einstein_layout"])
    if len(weyl) != 40 or len(einstein) != 38:
        raise AssertionError("minimal source/target row counts changed")

    rows: list[dict[str, Any]] = []
    for old in current_rows:
        row = dict(old)
        row["sector"] = "five_current_de_rham"
        rows.append(row)

    cone: list[dict[str, Any]] = []
    for theory, source in (("weyl", weyl), ("einstein_shifted", einstein)):
        for old in source:
            degree = int(old["degree"]) - (1 if theory == "einstein_shifted" else 0)
            cone.append({
                "cone_index": len(cone),
                "origin": theory,
                "origin_index": int(old["index"]),
                "origin_row_id": str(old["row_id"]),
                "row_id": f"C_{'W' if theory == 'weyl' else 'E1'}_{old['row_id']}",
                "bundle_id": str(old["bundle_id"]),
                "degree": degree,
                "parity": _parity(degree),
            })
    if [sum(row["degree"] == degree for row in cone) for degree in range(-2, 3)] != [5, 20, 28, 19, 6]:
        raise AssertionError("cone degree layout changed")

    cone_offset = len(rows)
    dual_offset = cone_offset + len(cone)
    source_by_origin = {"weyl": weyl, "einstein_shifted": einstein}
    for row in cone:
        global_index = cone_offset + int(row["cone_index"])
        value = dict(row)
        value.update({"index": global_index, "sector": "relative_cone", "dual_row": dual_offset + int(row["cone_index"])})
        rows.append(value)
    for row in cone:
        source = source_by_origin[str(row["origin"])]
        origin = source[int(row["origin_index"])]
        origin_dual = source[int(origin["dual_row"])]
        degree = 1 - int(row["degree"])
        global_index = dual_offset + int(row["cone_index"])
        rows.append({
            "index": global_index,
            "sector": "relative_cone_cotangent",
            "cone_index": int(row["cone_index"]),
            "origin": str(row["origin"]),
            "origin_index": int(row["origin_index"]),
            "origin_row_id": str(row["origin_row_id"]),
            "row_id": f"COT_{row['row_id']}",
            "bundle_id": str(origin_dual["bundle_id"]),
            "degree": degree,
            "parity": _parity(degree),
            "dual_row": cone_offset + int(row["cone_index"]),
        })
    if len(rows) != 316 or [sum(row["degree"] == degree for row in rows) for degree in range(-2, 4)] != [10, 51, 97, 97, 51, 10]:
        raise AssertionError("completed degree layout changed")

    pairing = [dict(term) for term in current["odd_pairing"]]
    for index in range(len(cone)):
        left, right = cone_offset + index, dual_offset + index
        pairing.extend((
            {"left_row": left, "right_row": right, "coefficient": 1},
            {"left_row": right, "right_row": left, "coefficient": -1},
        ))
    if len(pairing) != 316:
        raise AssertionError("pairing term count changed")

    return {
        "schema": "pure-weyl-relative-316-row-cotangent-layout-v1",
        "result_id": f"{RESULT_ID}_LAYOUT",
        "row_count": 316,
        "degree_range": [-2, -1, 0, 1, 2, 3],
        "degree_ranks": [10, 51, 97, 97, 51, 10],
        "sector_ranks": {"five_current_de_rham": 160, "relative_cone": 78, "relative_cone_cotangent": 78},
        "rows": rows,
        "odd_pairing": pairing,
        "unary_operator": {
            "current_block": "the imported 160-row horizontal de Rham differential",
            "cone_block": "q_C=[[q_W,iota],[0,-q_E]] on W direct_sum E[1]",
            "cotangent_block": "-q_C^sharp on C^vee[1] in the declared graded-adjoint convention",
            "block_diagonal_formula": "q_316=q_current direct_sum q_C direct_sum (-q_C^sharp)",
            "formal_adjoint_is_kept_factorized": True,
            "pbw_expansion_of_cotangent_block_emitted": False,
        },
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not dependencies["triangle"]["mapping_cofiber"]["square_zero"]:
        raise AssertionError("relative cone square changed")
    if dependencies["triangle"]["form_exports"]["standard_pairing_cyclic_map_exists"]:
        raise AssertionError("standard pairing obstruction changed")
    if dependencies["rank_obstruction"]["classification"]["minimum_additional_row_lower_bound"] != 28:
        raise AssertionError("rank lower bound changed")
    layout = build_layout()
    certificate = {
        "schema": "pure-weyl-relative-316-row-cotangent-completion-v1",
        "result_id": RESULT_ID,
        "result_state": "CANONICAL_ODD_COTANGENT_UNARY_COMPLETION_SELECTED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "support-local off-shell bundle complex before harmonic or causal reduction",
            "charge_sector": "five connected stabilizers H,P_x,J_1,J_2,J_3",
            "carrier": "160-row five-current carrier plus T*[1] of the complete 78-row relative mapping cofiber",
            "degree": "-2 through 3",
            "parity": "canonical nondegenerate BV odd pairing of cohomological degree one",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "not harmonic-reduced", "omega": "not harmonic-reduced"
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "bundle_classification": {
            "relative_cone_decomposition": "W direct_sum E[1]",
            "relative_cone_degree_ranks": [5, 20, 28, 19, 6],
            "rank_only_addition_lower_bound": 28,
            "rank_only_profile": {"degree_1": 9, "degree_2": 14, "degree_3": 5},
            "rank_only_profile_is_canonical_bundle_completion": False,
            "reason_rank_only_is_not_selected": "rank balance does not supply a covariant dual bundle or absorb the adjoint of the noncyclic inclusion",
            "selected_added_bundle": "C^vee[1] for the entire 78-row cone C",
            "selected_added_degree_ranks_minus1_to3": [6, 19, 28, 20, 5],
            "selected_added_rows": 78,
            "completed_total_rows": 316,
            "completed_degree_ranks": [10, 51, 97, 97, 51, 10],
        },
        "unary_theorem": {
            "formula": "q_316=q_current direct_sum q_C direct_sum (-q_C^sharp)",
            "q_C_formula": "q_C=[[q_W,iota],[0,-q_E]]",
            "q_C_squared_zero_imported": True,
            "cotangent_square_zero": "(-q_C^sharp)^2=(q_C^2)^sharp=0",
            "q1_squared_zero": True,
            "odd_pairing_nondegenerate": True,
            "unary_cyclicity_exact_by_cotangent_lift": True,
            "support_local": True,
            "uses_differential_inverse": False,
            "standard_action_pairings_identified": False,
            "standard_pairing_inertia_obstruction_evaded_by_changing_carrier_not_refuted": True,
        },
        "generated_layout": {"path": str(GENERATED.relative_to(ROOT)), "sha256": _sha_bytes(layout)},
        "classification": {
            "fixed_238_row_carrier_reused": False,
            "canonical_316_row_unary_cyclic_carrier_exists": True,
            "complete_q2_on_316_rows": False,
            "relative_f2_obstruction_repaired": False,
            "action_current_pairing_transport_complete": False,
            "causal_green_data": False,
            "arity_three_or_quantum_claim": False,
        },
        "next_gate": "EXTEND_OR_OBSTRUCT_Q2_ON_THE_316_ROW_COTANGENT_CARRIER_WITHOUT_IDENTIFYING_THE_COTANGENT_PAIRING_WITH_THE_ACTION_CURRENT",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_316_row_cotangent_completion --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_316_row_cotangent_completion",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_316_row_cotangent_completion",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem selects and row-resolves the canonical odd cotangent completion of the entire noncyclic 78-row relative mapping cone, direct-summed with the certified 160-row current carrier. It certifies a nondegenerate degree-one pairing and the factorized support-local unary differential q_C direct_sum (-q_C^sharp), whose square and cyclicity follow exactly from q_C^2=0. It deliberately changes the carrier and pairing, so it does not refute or repair the standard-action-pairing inertia obstruction. The formal adjoint is retained in factorized form rather than re-expanded into PBW coefficients. No complete q2, relative f2 repair, action-current pairing transport, causal Green operator, arity three, observable, particle or quantum claim follows.",
    }
    return certificate, layout


def _sha_bytes(value: object) -> str:
    return hashlib.sha256(_render(value).encode()).hexdigest()


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _guards(value: dict[str, Any]) -> None:
    for key in ("complete_q2_on_316_rows", "relative_f2_obstruction_repaired", "action_current_pairing_transport_complete", "causal_green_data", "arity_three_or_quantum_claim"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def _report() -> str:
    return r"""# Canonical 316-row odd-cotangent completion

The fixed 238-row direct sum cannot carry a nondegenerate degree-one odd
pairing.  Rather than identifying unlike bundles merely to attain the rank
lower bound, this construction takes the canonical odd cotangent completion
of the complete relative cone:

\[
C=\operatorname{Cone}(\iota)=W\oplus E[1],\qquad
T^*[1]C=C\oplus C^\vee[1].
\]

The added 78 dual rows have ranks

\[
(6,19,28,20,5)_{-1,\ldots,3}.
\]

After adjoining the independent 160-row five-current carrier, the completed
degree ranks are

\[
(10,51,97,97,51,10)_{-2,\ldots,3}.
\]

The unary differential is retained in factorized form,

\[
q_{316}=q_{\rm current}\oplus q_C\oplus(-q_C^\sharp),
\qquad
q_C=\begin{pmatrix}q_W&\iota\\0&-q_E\end{pmatrix}.
\]

Because the imported cone is square-zero, its cotangent block is square-zero;
the canonical cross-pairing is nondegenerate and makes this differential
odd-cyclic.  Every block is finite-order and support local.

This changes the carrier and pairing.  It neither contradicts nor repairs the
obstruction to a cyclic Einstein-to-Weyl map with the two standard action
pairings.  The formal adjoint block is not yet expanded into a portable PBW
term table, and no complete arity-two or causal theorem is claimed.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value, layout = build()
    validate(value)
    if args.write:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(_render(layout))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (GENERATED.read_text() != _render(layout) or OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("316-row cotangent outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
