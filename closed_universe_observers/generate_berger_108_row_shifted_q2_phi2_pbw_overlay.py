#!/usr/bin/env python3
"""Contract the pinned Berger q2 tensors with the physical Phi2 background."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-shifted-q2-phi2-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-shifted-q2-phi2-pbw-overlay-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-shifted-q2-phi2-pbw-overlay.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "rod_gravity_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "gravity_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
    "maxwell_q2_overlay": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_shifted_q2_phi2_pbw_overlay.py",
    P / "tests/test_berger_108_row_shifted_q2_phi2_pbw_overlay.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

Scalar = tuple[Fraction, Fraction]
ZERO: Scalar = Fraction(0), Fraction(0)
METRIC_COMPONENTS = ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: Any) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def scalar(value: dict[str, Any]) -> Scalar:
    return rational(value["rational"]), rational(value["sqrt10"])


def scalar_add(left: Scalar, right: Scalar) -> Scalar:
    return left[0] + right[0], left[1] + right[1]


def serialize_rational(value: Fraction) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {"numerator": value.numerator, "denominator": value.denominator}


def serialize_scalar(value: Scalar) -> dict[str, Any]:
    return {"rational": serialize_rational(value[0]), "sqrt10": serialize_rational(value[1])}


def contract_payloads(gravity: dict[str, Any], maxwell: dict[str, Any]) -> dict[str, Any]:
    """Evaluate q2(Phi2,-), with epsilon_R_squared implicit in every term."""

    if gravity["shape"] != [54, 54, 54] or maxwell["shape"] != [64, 64, 64]:
        raise AssertionError("pinned q2 carrier shape drifted")
    gravity_ref = maxwell["gravity_base"]
    if gravity_ref["file_sha256"] != sha256(DEPENDENCIES["gravity_q2"]):
        raise AssertionError("64-row overlay no longer pins the selected gravity payload")

    coefficients: dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Scalar]
    coefficients = defaultdict(lambda: ZERO)
    raw_contraction_count = 0
    for source in (gravity, maxwell):
        for row in source["rows"]:
            output = row["output"]
            for first, first_word, second, second_word, raw_coefficient in row["terms"]:
                value = scalar(raw_coefficient)
                if 5 <= first <= 14:
                    key = output, second, tuple(second_word), first - 5, tuple(first_word)
                    coefficients[key] = scalar_add(coefficients[key], value)
                    raw_contraction_count += 1
                if 5 <= second <= 14:
                    key = output, first, tuple(first_word), second - 5, tuple(second_word)
                    coefficients[key] = scalar_add(coefficients[key], value)
                    raw_contraction_count += 1

    normalized = {key: value for key, value in coefficients.items() if value != ZERO}
    rows = []
    for output in range(64):
        terms = [
            [input_row, list(input_word), background_component, list(background_word), serialize_scalar(value)]
            for (term_output, input_row, input_word, background_component, background_word), value
            in sorted(normalized.items())
            if term_output == output
        ]
        rows.append({"output": output, "terms": terms})
    positions = {(output, input_row) for output, input_row, _iw, _bc, _bw in normalized}
    orders = Counter((sum(input_word), sum(background_word)) for _o, _i, input_word, _b, background_word in normalized)
    return {
        "schema": "closed-universe-berger-108-row-shifted-q2-phi2-pbw-overlay-payload-v1",
        "result_id": "BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY_PAYLOAD",
        "scalar_matrix_shape": [108, 108],
        "active_base_shape": [64, 64],
        "factorial_convention": gravity["factorial_convention"],
        "coefficient_field": "Q(sqrt(10))[epsilon_R_squared; Phi2 component jets]",
        "term_decoder": "[input_row,input_PBW_multiindex,Phi2_component_index,Phi2_PBW_multiindex,Q(sqrt(10)) coefficient]; multiply every term by epsilon_R_squared",
        "Phi2_component_order": list(METRIC_COMPONENTS),
        "rows": rows,
        "raw_contraction_count": raw_contraction_count,
        "normalized_term_count": len(normalized),
        "nonzero_matrix_position_count": len(positions),
        "row_support": sorted({key[0] for key in normalized}),
        "column_support": sorted({key[1] for key in normalized}),
        "derivative_order_histogram": [
            {"input_order": pair[0], "Phi2_order": pair[1], "term_count": count}
            for pair, count in sorted(orders.items())
        ],
        "rows_canonical_sha256": canonical_sha256(rows),
    }


@lru_cache(maxsize=1)
def payload_document() -> dict[str, Any]:
    gravity = json.loads(DEPENDENCIES["gravity_q2"].read_text())
    maxwell = json.loads(DEPENDENCIES["maxwell_q2_overlay"].read_text())
    return contract_payloads(gravity, maxwell)


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "background_quotient": "PHYSICAL_PHI2_BACKGROUND_SPECIALIZATION_EXPORTED",
        "rod_gravity_unary": "Q2_PHI2_FOURTH_ORDER_PRINCIPAL_DEFORMATION_AUDITED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    summary_keys = (
        "raw_contraction_count", "normalized_term_count", "nonzero_matrix_position_count",
        "row_support", "column_support", "derivative_order_histogram", "rows_canonical_sha256",
    )
    return {
        "schema": "closed-universe-berger-108-row-shifted-q2-phi2-pbw-overlay-v1",
        "result_id": "BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_SHIFTED_Q2_PHI2_UNARY_OVERLAY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": value.get("result_id", path.stem), "sha256": sha256(path)}
            for (name, path), value in zip(DEPENDENCIES.items(), values.values())
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": payload_sha256,
            **{key: payload[key] for key in summary_keys},
        },
        "contraction_contract": {
            "operator": "epsilon_R_squared q2_64(Phi2,-)",
            "source_composition": "zero-extend the pinned 54-row gravity q2 to 64 rows and add the pinned Maxwell q2 overlay before contraction",
            "Phi2_components": [f"Phi2_{name}" for name in METRIC_COMPONENTS],
            "coefficient_jet_rule": "the derivative word on the contracted metric input becomes the ordered PBW jet of that Phi2 component; the other input and its PBW word remain the unary input",
            "factorial_rule": "sum both ordered metric placements exactly as serialized by the suspended-graded-symmetric source payload",
        },
        "principal_witness": values["rod_gravity_unary"]["coupled_causal_witness"]["q2_principal_order_audit"]["physical_contraction_witness"],
        "identity_disposition": {
            "source_q2_cyclicity_imported": True,
            "contraction_exact": True,
            "complete_108_row_q1_nilpotency_replayed": False,
            "complete_108_row_q1_odd_cyclicity_replayed": False,
        },
        "flags": {
            "SCALAR_SHIFTED_Q2_PHI2_PBW_OVERLAY_EXPORTED": True,
            "SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED": False,
            "SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_SCALAR_ROD_GAUGE_WAVE_AND_LOCAL_HESSIAN_PBW_OVERLAY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate contracts the pinned support-local 54-row gravity q2 tensor and its pinned 64-row Maxwell overlay with the certified physical Phi2 metric background. It exports epsilon_R_squared q2_64(Phi2,-) as a canonical scalar unary PBW payload, retaining every derivative on Phi2 and every derivative on the remaining unary input. Both serialized metric placements are summed with the source factorial convention, and the known nonzero fourth-order physical contraction witness remains pinned. It does not export the six rod gauge/wave blocks, the local gravity--rod Hessian, a complete 108-row q1, an all-row nilpotency or odd-cyclicity replay, scalar q2 on the full 108-row carrier, a solved backreaction, tangent-cone restriction, Bridge 3, finite-parameter causal propagation or any quantum claim."
        ),
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = payload_document()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload:
            raise SystemExit("stale shifted q2(Phi2,-) payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale shifted q2(Phi2,-) certificate")
    print("BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
