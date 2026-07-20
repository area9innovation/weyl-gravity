#!/usr/bin/env python3
"""Assemble the certified Berger q2 subblocks into one 108-row PBW payload."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-complete-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-complete-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-complete-q2-pbw.md"
SOURCES = {
    "base_gravity_clock": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
    "base_maxwell_typed": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json",
    "apparatus_scalar_BV": P / "certificates/BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW.json",
    "rod_metric": P / "certificates/BERGER_108_ROW_ROD_METRIC_Q2_PBW_PAYLOAD.json",
    "memory_transport": P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW_PAYLOAD.json",
    "normalized_readout": P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW_PAYLOAD.json",
    "emitter_physical": P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW_PAYLOAD.json",
    "emitter_Diff_BV": P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD.json",
}
GATES = {
    "base_gravity_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "base_typed_q2_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "emitter_Diff_BV": P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_complete_q2_pbw.py", P / "tests/test_berger_108_row_complete_q2_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def number(value: Any) -> dict[str, int]:
    fraction = Fraction(value) if isinstance(value, int) else Fraction(value["numerator"], value["denominator"])
    return {"numerator": fraction.numerator, "denominator": fraction.denominator}


def coefficient(value: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {"rational": number(value["rational"]), "sqrt10": number(value["sqrt10"])}


def normalized_term(
    source: str,
    output: int,
    left: int,
    left_pbw: Iterable[int],
    right: int,
    right_pbw: Iterable[int],
    value: dict[str, Any],
    factors: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source": source,
        "output": output,
        "left_input_row": left,
        "left_pbw_multiindex": list(left_pbw),
        "right_input_row": right,
        "right_pbw_multiindex": list(right_pbw),
        "coefficient": coefficient(value),
        "coefficient_factors": factors,
    }


def source_terms(name: str, document: dict[str, Any]) -> list[dict[str, Any]]:
    terms = []
    if name in {"base_gravity_clock", "base_maxwell_typed"}:
        for row in document["rows"]:
            for left, left_pbw, right, right_pbw, value in row["terms"]:
                terms.append(normalized_term(name, row["output"], left, left_pbw, right, right_pbw, value, []))
    elif name == "apparatus_scalar_BV":
        for output, left, left_pbw, right, right_pbw, value in document["payload"]["terms"]:
            terms.append(normalized_term(name, output, left, left_pbw, right, right_pbw, value, []))
    else:
        for row in document["rows"]:
            for term in row["terms"]:
                terms.append(normalized_term(name, row["output"], term["left_input_row"], term["left_pbw_multiindex"], term["right_input_row"], term["right_pbw_multiindex"], term["coefficient"], term["coefficient_factors"]))
    return terms


def operator_key(term: dict[str, Any]) -> tuple[Any, ...]:
    return term["output"], term["left_input_row"], tuple(term["left_pbw_multiindex"]), term["right_input_row"], tuple(term["right_pbw_multiindex"])


def composition_hash(*, omit_source: str | None = None) -> str:
    refs = [(name, sha256(path)) for name, path in SOURCES.items() if name != omit_source]
    return canonical_sha256(refs)


def assemble(*, omit_source: str | None = None) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, Any]]:
    documents = {name: json.loads(path.read_text()) for name, path in SOURCES.items() if name != omit_source}
    by_source = {name: source_terms(name, document) for name, document in documents.items()}
    owners: dict[tuple[Any, ...], str] = {}
    collisions = []
    all_terms = []
    for name, terms in by_source.items():
        for term in terms:
            key = operator_key(term)
            if key in owners and owners[key] != name:
                collisions.append({"operator_key": [key[0], key[1], list(key[2]), key[3], list(key[4])], "sources": sorted((owners[key], name))})
            owners[key] = name
            all_terms.append(term)
    all_terms.sort(key=lambda term: json.dumps(term, sort_keys=True, separators=(",", ":")))
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for term in all_terms:
        copy = dict(term); output = copy.pop("output"); rows[output].append(copy)
    serialized = [{"output": output, "terms": values} for output, values in sorted(rows.items())]
    audit = {
        "cross_source_operator_key_collision_count": len(collisions),
        "cross_source_operator_key_collisions": collisions,
        "operator_key_count": len(owners),
        "serialized_term_count": len(all_terms),
        "nonzero_output_rows": sorted(rows),
    }
    return serialized, {name: len(terms) for name, terms in by_source.items()}, audit


@lru_cache(maxsize=1)
def payload_document() -> dict[str, Any]:
    rows, counts, audit = assemble()
    return {
        "schema": "closed-universe-berger-108-row-complete-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_COMPLETE_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "differential coefficient-jet algebra over Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "composition": "source-labelled additive sum of the separate gravity-clock q2 payload, typed Maxwell q2 overlay, and six apparatus/emitter tensors after zero-extension to 108 rows; shared operator keys retain every coefficient monomial",
        "source_term_counts": counts,
        "source_payload_refs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for name, path in SOURCES.items()},
        "composition_sha256": composition_hash(),
        "assembly_audit": audit,
        "rows": rows,
        "canonical_sha256": canonical_sha256(rows),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    gates = {name: json.loads(path.read_text()) for name, path in GATES.items()}
    required = {"base_gravity_q2": "CLASSICAL_SUPPORT_LOCAL_Q2", "base_typed_q2_q3": "BERGER_TYPED_COUPLED_Q2", "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED", "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED", "emitter_Diff_BV": "COMPLETE_EMITTER_Q2_PBW_EXPORTED"}
    for name, flag in required.items():
        if gates[name]["flags"].get(flag) is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    payload = payload or payload_document()
    deletion_audits = {
        source: {
            "detected": composition_hash(omit_source=source) != payload["composition_sha256"],
            "remaining_term_count": payload["assembly_audit"]["serialized_term_count"] - payload["source_term_counts"][source],
        }
        for source in SOURCES
    }
    if not all(item["detected"] for item in deletion_audits.values()):
        raise AssertionError("source-deletion mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate assembles the complete scalar q2 tensor on the canonical 108-row Berger carrier. It zero-extends and adds eight independently certified, content-addressed sources: the 64-row gravity-clock q2 payload, its separate typed Maxwell overlay, the universal apparatus scalar-BV orbit, six-rod metric interaction, memory transport, normalized two-detector readout, physical massive-emitter stress/switch interaction, and the massive-two-form Diff--BV cotangent orbit. The Maxwell file is an additive overlay and is never treated as a materialized replacement for the gravity payload. The typed base presentation is required for nonlinear coderivation composition; it has the same lowered cubic action as the legacy output-normalized tensor but is not identified with it as an operator. Every source is normalized into one differential coefficient-jet PBW grammar with an explicit source label. The exact assembly counts and overlap audit are recorded in the payload. Shared operator keys are retained as separate source-labelled coefficient monomials and therefore add in coderivation evaluation; no contribution is overwritten. Deleting any source changes the exact term count. All 108 rows share the same signed odd pairing and suspended graded-symmetric factorial convention through their certified dependencies. This certificate exports scalar q2 only; complete q3 is a separate certificate. It does not replay q1q2 or q2q2+q1q3 coefficientwise, prove K_Berger equivariance or observer-morphism stability, restrict detector response to Z2, promote nonlinear rank, activate physical Bridge 3, establish finite-parameter causal propagation or make a quantum claim. No compact-product mode is identified with a Berger row."
    )
    payload_sha256 = payload_sha256 or sha256(PAYLOAD)
    return {
        "schema": "closed-universe-berger-108-row-complete-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_COMPLETE_Q2_PBW",
        "setting_id": gates["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_SCALAR_108_ROW_Q2_PBW_PAYLOAD",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "gate_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": gates[name]["result_id"], "sha256": sha256(path)} for name, path in GATES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": payload_sha256, "canonical_sha256": payload["canonical_sha256"], **payload["assembly_audit"]},
        "assembly_audit": {"source_term_counts": payload["source_term_counts"], "source_deletion_mutations": deletion_audits, "cross_source_operator_key_collision_count": payload["assembly_audit"]["cross_source_operator_key_collision_count"]},
        "activation_disposition": {"complete_scalar_q2_payload_assembled": True, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": True, "Q2_SOURCE_PROVENANCE_COMPLETE": True, "Q2_ADDITIVE_OVERLAPS_EXPLICIT": True, "Q2_CROSS_SOURCE_OPERATOR_KEYS_DISJOINT": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "REPLAY_COMPLETE_TYPED_108_ROW_Q1Q2_AND_Q2Q2_PLUS_Q1Q3",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    payload = payload_document(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text()); Draft202012Validator.check_schema(payload_schema); Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest()); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: PAYLOAD.write_text(rendered_payload); CERTIFICATE.write_text(rendered)
    if args.check and (not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale complete q2 artifact")
    print("BERGER_108_ROW_COMPLETE_Q2_PBW generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
