#!/usr/bin/env python3
"""Export the exact scalar-BV apparatus q2 PBW block on 108 rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW.json"
SCHEMA = P / "schema/berger-108-row-apparatus-scalar-bv-q2-pbw-v1.schema.json"
REPORT = P / "reports/berger-108-row-apparatus-scalar-bv-q2-pbw.md"
GRAVITY_Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "scalar_template": GRAVITY_Q2,
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_apparatus_scalar_bv_q2_pbw.py", P / "tests/test_berger_108_row_apparatus_scalar_bv_q2_pbw.py", SCHEMA, REPORT]

TEMPLATE_FIELD = 16
TEMPLATE_DUAL = 38
GHOSTS = (0, 1, 2)
GHOST_DUALS = (49, 50, 51)
APPARATUS_PAIRS = tuple(zip(range(64, 74), range(74, 84), strict=True))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scalar_template() -> list[list[Any]]:
    payload = json.loads(GRAVITY_Q2.read_text())
    rows = {row["output"]: row["terms"] for row in payload["rows"]}
    support = set(GHOSTS) | {TEMPLATE_FIELD, TEMPLATE_DUAL}
    output_support = {TEMPLATE_FIELD, TEMPLATE_DUAL, *GHOST_DUALS}
    terms = []
    for output in sorted(output_support):
        for term in rows[output]:
            if term[0] in support and term[2] in support:
                terms.append([output, *term])
    if len(terms) != 24:
        raise AssertionError(f"certified scalar template changed: {len(terms)}")
    return terms


def clone_term(term: list[Any], field: int, dual: int) -> list[Any]:
    mapping = {TEMPLATE_FIELD: field, TEMPLATE_DUAL: dual}
    output, first, first_pbw, second, second_pbw, coefficient = term
    return [mapping.get(output, output), mapping.get(first, first), first_pbw, mapping.get(second, second), second_pbw, coefficient]


def payload(*, delete_last_term: bool = False) -> dict[str, Any]:
    template = scalar_template()
    blocks = []
    all_terms = []
    for field, dual in APPARATUS_PAIRS:
        terms = [clone_term(term, field, dual) for term in template]
        blocks.append({"field_row": field, "cotangent_row": dual, "terms": terms, "term_count": len(terms), "canonical_sha256": canonical_sha256(terms)})
        all_terms.extend(terms)
    if delete_last_term:
        all_terms.pop()
    return {
        "shape": [108, 108, 108],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "source_action": "integral sum R_plus L_c R + sum(m_plus L_c m+p_plus L_c p)",
        "template_rows": {"field": TEMPLATE_FIELD, "cotangent": TEMPLATE_DUAL, "ghosts": list(GHOSTS), "ghost_cotangents": list(GHOST_DUALS)},
        "blocks": blocks,
        "terms": all_terms,
        "block_count": len(blocks),
        "term_count": len(all_terms),
        "canonical_sha256": canonical_sha256(all_terms),
    }


def pairing_isometry_audit(value: dict[str, Any]) -> dict[str, Any]:
    contract = json.loads(DEPENDENCIES["component_contract"].read_text())
    pairing = {(row, partner): terms[0][1] for row, partner, terms in contract["carrier_contract"]["pairing_entries"]}
    template_signs = pairing[(TEMPLATE_FIELD, TEMPLATE_DUAL)], pairing[(TEMPLATE_DUAL, TEMPLATE_FIELD)]
    defects = 0
    block_defects = 0
    template = scalar_template()
    for block, (field, dual) in zip(value["blocks"], APPARATUS_PAIRS, strict=True):
        if (pairing[(field, dual)], pairing[(dual, field)]) != template_signs:
            defects += 1
        expected = [clone_term(term, field, dual) for term in template]
        if block["terms"] != expected or block["canonical_sha256"] != canonical_sha256(expected):
            block_defects += 1
    return {
        "template_pairing_signs": list(template_signs),
        "apparatus_pairing_isometry_defect_count": defects,
        "term_bijection_defect_count": block_defects,
        "cyclicity_transfer": "each clone is the image of the certified Theta/Theta_star scalar-BV lowered cubic tensor under a signed-pairing isometry fixing c_i and c_i_star",
    }


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if dependencies["component_contract"]["flags"]["NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED"] is not True:
        raise AssertionError("108-row pairing gate dropped")
    if dependencies["combined_clock_chart"]["flags"]["SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED"] is not True:
        raise AssertionError("combined chart has not authorized interaction work")
    if not all(dependencies["apparatus_action"]["flags"].get(flag) is True for flag in ("APPARATUS_Q2_ACTION_JET_EXPORTED", "APPARATUS_Q3_ACTION_JET_EXPORTED")):
        raise AssertionError("apparatus action jets dropped")
    value = payload()
    audit = pairing_isometry_audit(value)
    mutation = payload(delete_last_term=True)
    if value["block_count"] != 10 or value["term_count"] != 240:
        raise AssertionError("scalar-BV apparatus support changed")
    if audit["apparatus_pairing_isometry_defect_count"] or audit["term_bijection_defect_count"]:
        raise AssertionError("scalar-BV clone ceased to preserve cyclic pairing")
    if mutation["term_count"] == value["term_count"] or mutation["canonical_sha256"] == value["canonical_sha256"]:
        raise AssertionError("term-deletion mutation was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the first executable apparatus interaction block on the "
        "canonical 108-row carrier. The ten even apparatus scalars—six rods and four memory/readout variables—share "
        "the universal BV master term integral phi_star L_c phi. The certified 54-row gravity-clock q2 already "
        "contains this complete scalar semidirect tensor for Theta/Theta_star. Each apparatus block is generated by "
        "the unique row relabeling Theta->phi, Theta_star->phi_star that fixes the three spatial diffeomorphism ghosts "
        "and their cotangents. The 108-row pairing contract proves every relabeling is a signed-pairing isometry. "
        "Consequently the certified graded symmetry and lowered cyclicity transfer termwise rather than being inferred "
        "from a narrative action label. The result contains ten hashed 24-term blocks, hence 240 exact q2 PBW terms, "
        "and a deletion mutation is detected. This is a real component payload for the scalar-BV sector only. It does "
        "not export rod metric-interaction, memory transport, normalized readout, emitter or their cotangent q2 blocks; "
        "it exports no q3, does not replay the complete q1q2 or q2q2+q1q3 identities, prove K_Berger equivariance or "
        "observer-morphism stability, restrict detector response to Z2, promote nonlinear rank, activate physical "
        "Bridge 3, establish finite-parameter causality, or make a quantum claim. No compact-product mode is identified "
        "with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-apparatus-scalar-bv-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW",
        "setting_id": dependencies["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_BV_APPARATUS_Q2_PBW_SUBBLOCK",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name].get("result_id", "BERGER_SUPPORT_LOCAL_Q2_PAYLOAD"), "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload": value,
        "pairing_and_cyclicity_audit": audit,
        "mutation_results": [{"name": "delete_last_scalar_BV_term", "detected": mutation["canonical_sha256"] != value["canonical_sha256"], "mutated_term_count": mutation["term_count"]}],
        "activation_disposition": {"scalar_BV_q2_subblock_exported": True, "complete_apparatus_q2_exported": False, "complete_emitter_q2_exported": False, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_SCALAR_BV_Q2_PBW_EXPORTED": True, "APPARATUS_SCALAR_BV_Q2_GRADED_SYMMETRIC": True, "APPARATUS_SCALAR_BV_Q2_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_ROD_METRIC_MEMORY_TRANSPORT_AND_NORMALIZED_READOUT_Q2_PBW_BLOCKS",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale apparatus scalar-BV q2 PBW certificate")
    print("BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
