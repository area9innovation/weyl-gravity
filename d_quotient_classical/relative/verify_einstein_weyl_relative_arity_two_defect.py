#!/usr/bin/env python3
"""Independent consumer for the strict relative arity-two PBW defect."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.verify_einstein_maxwell_product_linfinity import (
    _add,
    _differentiate,
    _terms,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json"
CERTIFICATE_SCHEMA = ROOT / "d_quotient_classical/schema/relative-arity-two-defect-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-arity-two-pbw-defect-v1.schema.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _inclusion_rows(payload: dict) -> list[list[dict]]:
    rows: list[list[dict]] = [[] for _ in payload["map"]["target_rows"]]
    for entry in payload["map"]["entries"]:
        for term in entry["terms"]:
            rows[entry["output_index"]].append(
                {
                    "inputs": ((entry["input_index"], tuple(term["word"])),),
                    "jets": {
                        tuple(item["word"]): sp.Rational(item["coefficient"])
                        for item in term["coefficient_jets"]
                    },
                }
            )
    return rows


def _pullback_row(target: int, q2_target: list[list[dict]], inclusion: list[list[dict]]) -> dict:
    output = defaultdict(lambda: sp.S.Zero)
    for outer in q2_target[target]:
        coefficient = outer["jets"].get((), sp.S.Zero)
        (middle_left, word_left), (middle_right, word_right) = outer["inputs"]
        for left in inclusion[middle_left]:
            for replaced_left, left_value in _differentiate(left, word_left):
                for right in inclusion[middle_right]:
                    for replaced_right, right_value in _differentiate(right, word_right):
                        _add(
                            output,
                            (replaced_left[0], replaced_right[0]),
                            coefficient * left_value * right_value,
                        )
    return output


def _pushforward_row(target: int, q2_source: list[list[dict]], inclusion: list[list[dict]]) -> dict:
    output = defaultdict(lambda: sp.S.Zero)
    for outer in inclusion[target]:
        middle, word = outer["inputs"][0]
        coefficient = outer["jets"].get((), sp.S.Zero)
        for inner in q2_source[middle]:
            for inputs, value in _differentiate(inner, word):
                _add(output, inputs, coefficient * value)
    return output


def _serialized_rows(payload: dict) -> list[dict]:
    rows = [defaultdict(lambda: sp.S.Zero) for _ in payload["target_rows"]]
    for term in payload["content"]["terms"]:
        inputs = tuple(
            (item["row"], tuple(item["word"])) for item in term["inputs"]
        )
        _add(rows[term["output_row"]], inputs, sp.Rational(term["coefficient"]))
    return rows


def verify() -> dict:
    certificate = _load(CERTIFICATE)
    certificate_schema = _load(CERTIFICATE_SCHEMA)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(certificate_schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(certificate_schema).validate(certificate)
    for dependency in certificate["dependencies"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {path}")
    payload_path = ROOT / certificate["defect_payload"]["path"]
    if _sha256(payload_path) != certificate["defect_payload"]["sha256"]:
        raise AssertionError("defect payload hash drifted")
    payload = _load(payload_path)
    Draft202012Validator(payload_schema).validate(payload)
    if payload["canonical_sha256"] != _canonical_sha256(payload["content"]):
        raise AssertionError("canonical content hash drifted")

    source_certificate = _load(
        ROOT / certificate["dependencies"]["source_taylor_certificate"]["path"]
    )
    target_certificate = _load(
        ROOT / certificate["dependencies"]["target_taylor_certificate"]["path"]
    )
    q2_source, source_arity = _terms(
        _load(ROOT / source_certificate["taylor_artifacts"]["q2"]["path"])
    )
    q2_target, target_arity = _terms(
        _load(ROOT / target_certificate["taylor_artifacts"]["q2"]["path"])
    )
    if source_arity != 2 or target_arity != 2:
        raise AssertionError("q2 arity drifted")
    inclusion_payload = _load(
        ROOT / certificate["dependencies"]["unary_inclusion"]["path"]
    )
    if not inclusion_payload["checks"]["target_q1_composition_replayed"]:
        raise AssertionError("unary inclusion is not replayed")
    inclusion = _inclusion_rows(inclusion_payload)
    expected = _serialized_rows(payload)
    counts = []
    for target in range(len(expected)):
        actual = _pullback_row(target, q2_target, inclusion)
        for key, value in _pushforward_row(target, q2_source, inclusion).items():
            _add(actual, key, -value)
        if dict(actual) != dict(expected[target]):
            difference = defaultdict(lambda: sp.S.Zero, actual)
            for key, value in expected[target].items():
                _add(difference, key, -value)
            raise AssertionError(
                f"serialized Delta2 mismatch on row {target}: "
                f"{next(iter(difference.items()), None)}"
            )
        counts.append(len(actual))
    if counts != payload["content"]["row_defect_counts"]:
        raise AssertionError("row defect counts drifted")
    if sum(counts) != certificate["checks"]["term_count"]:
        raise AssertionError("certificate term count drifted")
    return {
        "result_id": certificate["result_id"],
        "status": "PASS",
        "row_defect_counts": counts,
        "term_count": sum(counts),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
