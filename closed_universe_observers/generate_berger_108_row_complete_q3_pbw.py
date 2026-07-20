#!/usr/bin/env python3
"""Assemble all certified Berger q3 sources on the 108-row PBW carrier."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_COMPLETE_Q3_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_COMPLETE_Q3_PBW_PAYLOAD.json"
GENERATED = P / "generated/berger_108_row_complete_q3_pbw"
SCHEMA = P / "schema/berger-108-row-complete-q3-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-complete-q3-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-complete-q3-pbw.md"
SOURCES = {
    "base_gravity_clock": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json",
    "base_maxwell_typed": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json",
    "rod_metric": P / "certificates/BERGER_108_ROW_ROD_METRIC_Q3_PBW_PAYLOAD.json",
    "memory_transport": P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW_PAYLOAD.json",
    "normalized_readout": P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW_PAYLOAD.json",
    "emitter_physical": P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW_PAYLOAD.json",
    "structural_zeros": P / "certificates/BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER.json",
}
GATES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "base_gravity_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json",
    "base_maxwell_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "rod_metric_q3": P / "certificates/BERGER_108_ROW_ROD_METRIC_Q3_PBW.json",
    "memory_transport_q3": P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW.json",
    "normalized_readout_q3": P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW.json",
    "emitter_physical_q3": P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW.json",
    "structural_zeros": P / "certificates/BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_complete_q3_pbw.py", P / "tests/test_berger_108_row_complete_q3_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]
SOURCE_ORDER = tuple(SOURCES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def normalized_number(value: int | dict[str, int]) -> dict[str, int]:
    fraction = Fraction(value) if isinstance(value, int) else Fraction(value["numerator"], value["denominator"])
    return {"numerator": fraction.numerator, "denominator": fraction.denominator}


def normalized_coefficient(value: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {"rational": normalized_number(value["rational"]), "sqrt10": normalized_number(value["sqrt10"])}


def normalized_standard_term(term: dict[str, Any]) -> dict[str, Any]:
    return {
        "first_input_row": term["first_input_row"],
        "first_pbw_multiindex": term["first_pbw_multiindex"],
        "second_input_row": term["second_input_row"],
        "second_pbw_multiindex": term["second_pbw_multiindex"],
        "third_input_row": term["third_input_row"],
        "third_pbw_multiindex": term["third_pbw_multiindex"],
        "coefficient": normalized_coefficient(term["coefficient"]),
        "coefficient_factors": term["coefficient_factors"],
    }


def normalized_base_term(term: list[Any]) -> dict[str, Any]:
    return {
        "first_input_row": term[0],
        "first_pbw_multiindex": term[1],
        "second_input_row": term[2],
        "second_pbw_multiindex": term[3],
        "third_input_row": term[4],
        "third_pbw_multiindex": term[5],
        "coefficient": normalized_coefficient(term[6]),
        "coefficient_factors": [],
    }


def gzip_document(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()))


def chunk_paths(document: dict[str, Any]) -> dict[int, Path]:
    return {chunk["output"]: ROOT / chunk["path"] for chunk in document["chunks"] if chunk.get("serialized_term_count", chunk.get("term_count", 0))}


def source_documents() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in SOURCES.items()}


def source_indices(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "base_gravity_clock": chunk_paths(documents["base_gravity_clock"]),
        "base_maxwell_typed": chunk_paths(documents["base_maxwell_typed"]),
        "rod_metric": chunk_paths(documents["rod_metric"]),
        "memory_transport": {row["output"]: row for row in documents["memory_transport"]["rows"]},
        "normalized_readout": chunk_paths(documents["normalized_readout"]),
        "emitter_physical": chunk_paths(documents["emitter_physical"]),
        "structural_zeros": {},
    }


def source_row(name: str, output: int, index: dict[str, Any]) -> list[dict[str, Any]]:
    if output not in index[name]:
        return []
    if name == "memory_transport":
        document = index[name][output]
    else:
        document = gzip_document(index[name][output])
    if name in {"base_gravity_clock", "base_maxwell_typed"}:
        return [normalized_base_term(term) for term in document["terms"]]
    return [normalized_standard_term(term) for term in document["terms"]]


def operator_key(term: dict[str, Any]) -> tuple[Any, ...]:
    return (
        term["first_input_row"], tuple(term["first_pbw_multiindex"]),
        term["second_input_row"], tuple(term["second_pbw_multiindex"]),
        term["third_input_row"], tuple(term["third_pbw_multiindex"]),
    )


def gzip_bytes(value: Any) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as handle:
        handle.write((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
    return buffer.getvalue()


def source_outputs(index: dict[str, Any]) -> list[int]:
    return sorted(set().union(*(set(index[name]) for name in SOURCE_ORDER)))


def assemble_row(output: int, index: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    owners: dict[tuple[Any, ...], str] = {}
    collisions = []
    source_blocks = []
    source_term_counts = {}
    source_operator_counts = {}
    maximum_total_jet_order = 0
    for name in SOURCE_ORDER:
        terms = source_row(name, output, index)
        if not terms:
            continue
        keys = set()
        for term in terms:
            key = operator_key(term)
            keys.add(key)
            previous = owners.get(key)
            if previous is not None and previous != name:
                collisions.append({"operator_key": [key[0], list(key[1]), key[2], list(key[3]), key[4], list(key[5])], "sources": [previous, name]})
            else:
                owners[key] = name
            maximum_total_jet_order = max(maximum_total_jet_order, sum(key[1]) + sum(key[3]) + sum(key[5]))
        source_term_counts[name] = len(terms)
        source_operator_counts[name] = len(keys)
        source_blocks.append({"source": name, "operator_key_count": len(keys), "serialized_term_count": len(terms), "canonical_sha256": canonical_sha256(terms), "terms": terms})
    body = {"output": output, "source_blocks": source_blocks}
    row = {**body, "canonical_sha256": canonical_sha256(body)}
    audit = {
        "operator_key_count": len(owners),
        "serialized_term_count": sum(source_term_counts.values()),
        "source_term_counts": source_term_counts,
        "source_operator_key_counts": source_operator_counts,
        "cross_source_operator_key_collision_count": len(collisions),
        "cross_source_operator_key_collisions": collisions,
        "maximum_total_jet_order": maximum_total_jet_order,
    }
    return row, audit


def composition_hash(*, omit_source: str | None = None) -> str:
    refs = [(name, sha256(path)) for name, path in SOURCES.items() if name != omit_source]
    return canonical_sha256(refs)


def payload_bundle() -> tuple[dict[str, Any], dict[int, bytes]]:
    documents = source_documents()
    index = source_indices(documents)
    encoded = {}
    chunks = []
    row_hashes = {}
    total_terms: dict[str, int] = defaultdict(int)
    total_operators: dict[str, int] = defaultdict(int)
    operator_total = 0
    serialized_total = 0
    collision_total = 0
    outputs = source_outputs(index)
    for output in outputs:
        row, audit = assemble_row(output, index)
        data = gzip_bytes(row)
        encoded[output] = data
        row_hashes[output] = row["canonical_sha256"]
        operator_total += audit["operator_key_count"]
        serialized_total += audit["serialized_term_count"]
        collision_total += audit["cross_source_operator_key_collision_count"]
        for name, count in audit["source_term_counts"].items():
            total_terms[name] += count
        for name, count in audit["source_operator_key_counts"].items():
            total_operators[name] += count
        chunks.append({
            "output": output,
            "path": str((GENERATED / f"row_{output:03d}.json.gz").relative_to(ROOT)),
            "file_sha256": hashlib.sha256(data).hexdigest(),
            "canonical_sha256": row["canonical_sha256"],
            "operator_key_count": audit["operator_key_count"],
            "serialized_term_count": audit["serialized_term_count"],
            "maximum_total_jet_order": audit["maximum_total_jet_order"],
        })
    total_terms["structural_zeros"] = 0
    total_operators["structural_zeros"] = 0
    payload = {
        "schema": "closed-universe-berger-108-row-complete-q3-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_COMPLETE_Q3_PBW_PAYLOAD",
        "shape": [108, 108, 108, 108],
        "coefficient_field": "differential coefficient-jet algebra over Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "composition": "source-labelled additive sum of the separate gravity-clock q3 payload, typed Maxwell mixed-q3 overlay, four apparatus/emitter tensors, and the explicit two-source structural-zero ledger; shared operator keys retain every coefficient monomial",
        "storage": "deterministic-gzip-strict-json-row-chunks-with-source-blocks",
        "source_payload_refs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for name, path in SOURCES.items()},
        "source_term_counts": dict(total_terms),
        "source_operator_key_counts": dict(total_operators),
        "chunks": chunks,
        "nonzero_output_rows": outputs,
        "operator_key_count": operator_total,
        "serialized_term_count": serialized_total,
        "cross_source_operator_key_collision_count": collision_total,
        "composition_sha256": composition_hash(),
        "canonical_sha256": canonical_sha256(row_hashes),
    }
    return payload, encoded


def payload_document() -> dict[str, Any]:
    return payload_bundle()[0]


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    gates = {name: json.loads(path.read_text()) for name, path in GATES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "base_gravity_q3": "CLASSICAL_SUPPORT_LOCAL_Q3",
        "base_maxwell_q3": "BERGER_ACTION_DERIVED_MIXED_Q3",
        "rod_metric_q3": "APPARATUS_ROD_METRIC_Q3_PBW_EXPORTED",
        "memory_transport_q3": "APPARATUS_MEMORY_TRANSPORT_Q3_PBW_EXPORTED",
        "normalized_readout_q3": "APPARATUS_NORMALIZED_READOUT_Q3_PBW_EXPORTED",
        "emitter_physical_q3": "EMITTER_PHYSICAL_Q3_PBW_EXPORTED",
        "structural_zeros": "STRUCTURAL_Q3_ZERO_LEDGER_COMPLETE",
    }
    for name, flag in required.items():
        if gates[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    payload = payload or payload_document()
    expected_counts = {
        "base_gravity_clock": 5812130,
        "base_maxwell_typed": 59598,
        "rod_metric": 181344,
        "memory_transport": 5196,
        "normalized_readout": 1085112,
        "emitter_physical": 107988,
        "structural_zeros": 0,
    }
    if payload["source_term_counts"] != expected_counts:
        raise AssertionError("complete q3 source term counts changed")
    deletions = {name: {"detected": composition_hash(omit_source=name) != payload["composition_sha256"]} for name in SOURCE_ORDER}
    if not all(item["detected"] for item in deletions.values()):
        raise AssertionError("q3 source-deletion mutation was not detected")
    payload_sha256 = payload_sha256 or sha256(PAYLOAD)
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate assembles the complete scalar q3 tensor on the canonical 108-row Berger carrier. It imports the certified 64-row gravity-clock q3 payload and its separate typed Maxwell mixed-q3 overlay, zero-extends both, and adds the independently certified rod-metric, memory-transport, normalized-readout and physical-emitter q3 tensors. The Maxwell file is an additive overlay and is never treated as a materialized replacement for gravity. The apparatus scalar-BV and emitter Diff--BV sources are included through their explicit structural-zero ledger rather than silently omitted. Every nonzero term is normalized into one trilinear differential coefficient-jet PBW grammar and retained in a source-labelled row block. Exact coefficient-monomial, operator-key and overlap counts are recorded in the payload. Shared operator keys retain all source blocks and add during coderivation evaluation, so no contribution is overwritten. Deterministic gzip row hashes, source payload hashes, the global composition hash and deletion of each of the seven source references are checked. This exports the complete q3 payload only. It does not by itself replay the component q1q2 or q2q2+q1q3 identities, prove K_Berger equivariance or observer-morphism stability on the completed carrier, restrict detector response to Z2, classify linearly detectable nonlinear obstructions or balanced combinations, promote nonlinear response rank, activate physical Bridge 3, establish finite-parameter causal propagation or make a quantum claim. The certified base arity and equivariance results remain scoped to their 64-row carrier until the new 108-row replays pass. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-complete-q3-pbw-v1",
        "result_id": "BERGER_108_ROW_COMPLETE_Q3_PBW",
        "setting_id": gates["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_SCALAR_108_ROW_Q3_PBW_PAYLOAD",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "gate_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": gates[name]["result_id"], "sha256": sha256(path)} for name, path in GATES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": payload_sha256, "canonical_sha256": payload["canonical_sha256"], "composition_sha256": payload["composition_sha256"], "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"]},
        "assembly_audit": {"source_term_counts": payload["source_term_counts"], "source_operator_key_counts": payload["source_operator_key_counts"], "cross_source_operator_key_collision_count": payload["cross_source_operator_key_collision_count"], "source_deletion_mutations": deletions},
        "activation_disposition": {"complete_scalar_q3_payload_assembled": True, "structural_q3_zero_ledger_complete": True, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": True, "Q3_SOURCE_PROVENANCE_COMPLETE": True, "Q3_ADDITIVE_OVERLAPS_EXPLICIT": True, "Q3_CROSS_SOURCE_OPERATOR_KEYS_DISJOINT": payload["cross_source_operator_key_collision_count"] == 0, "STRUCTURAL_Q3_ZERO_LEDGER_COMPLETE": True, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "K_BERGER_EQUIVARIANCE_ON_COMPLETE_Q3_CERTIFIED": False, "OBSERVER_MORPHISM_STABILITY_ON_COMPLETE_Q3_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "REPLAY_COMPLETE_108_ROW_COMPONENT_ARITY_IDENTITIES",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload, encoded = payload_bundle()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for output, data in encoded.items():
            (GENERATED / f"row_{output:03d}.json.gz").write_bytes(data)
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale complete q3 artifact")
        for output, data in encoded.items():
            path = GENERATED / f"row_{output:03d}.json.gz"
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f"stale complete q3 row {output}")
    print("BERGER_108_ROW_COMPLETE_Q3_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
