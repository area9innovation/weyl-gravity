#!/usr/bin/env python3
"""Export the strict compact-product Einstein--Weyl arity-two defect.

The calculation uses only the frozen source/target q2 tables and the exact
38-to-40-row unary inclusion.  It evaluates the complete PBW operator at the
homogeneous product base point, one target row at a time, and never loads q3.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1"
PAYLOAD_ID = f"{RESULT_ID}_PBW"
SOURCE_CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
TARGET_CERTIFICATE = ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
INCLUSION = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_product_chain_map_pbw_v1/inclusion.json"
INCLUSION_RECEIPT = ROOT / "bridge/einstein_sector/receipts/einstein-weyl-compact-product-chain-map-pbw-v1.json"
OUTPUT_DIR = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_arity_two_defect_v1"
PAYLOAD = OUTPUT_DIR / "delta2.json"
CERTIFICATE = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-arity-two-pbw-defect-v1.schema.json"
CERTIFICATE_SCHEMA = ROOT / "d_quotient_classical/schema/relative-arity-two-defect-v1.schema.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: str) -> Fraction:
    coefficient = Fraction(value)
    if coefficient.denominator <= 0:
        raise ValueError(value)
    return coefficient


def _coefficient(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _operation_rows(payload: dict) -> list[list[dict]]:
    content = payload["content"]
    profiles = {
        profile["index"]: profile["coefficient_jets"]
        for profile in content.get("coefficient_profiles", [])
    }
    rows: list[list[dict]] = [[] for _ in range(content["row_count"])]
    for raw in content["terms"]:
        coefficient_jets = (
            profiles[raw["coefficient_profile"]]
            if "coefficient_profile" in raw
            else raw["coefficient_jets"]
        )
        rows[raw["output_row"]].append(
            {
                "inputs": tuple(
                    (item["row"], tuple(item["word"])) for item in raw["inputs"]
                ),
                "jets": {
                    tuple(item["word"]): _fraction(item["coefficient"])
                    for item in coefficient_jets
                },
            }
        )
    return rows


def _inclusion_rows(payload: dict) -> list[list[dict]]:
    rows: list[list[dict]] = [[] for _ in payload["map"]["target_rows"]]
    for entry in payload["map"]["entries"]:
        for term in entry["terms"]:
            rows[entry["output_index"]].append(
                {
                    "inputs": ((entry["input_index"], tuple(term["word"])),),
                    "jets": {
                        tuple(item["word"]): _fraction(item["coefficient"])
                        for item in term["coefficient_jets"]
                    },
                }
            )
    return rows


def _differentiate(term: dict, word: tuple[int, ...]) -> Iterator[tuple[tuple, Fraction]]:
    arity = len(term["inputs"])
    for assignment in product(range(arity + 1), repeat=len(word)):
        coefficient_word = tuple(
            sorted(axis for axis, bucket in zip(word, assignment) if bucket == 0)
        )
        coefficient = term["jets"].get(coefficient_word, Fraction(0))
        if not coefficient:
            continue
        inputs = []
        for slot, (row, old_word) in enumerate(term["inputs"], start=1):
            added = tuple(
                axis for axis, bucket in zip(word, assignment) if bucket == slot
            )
            inputs.append((row, tuple(sorted((*old_word, *added)))))
        yield tuple(inputs), coefficient


def _add(target: dict, key: tuple, value: Fraction) -> None:
    if value:
        target[key] += value
        if not target[key]:
            del target[key]


def _pullback_row(target: int, q2_target: list[list[dict]], inclusion: list[list[dict]]) -> dict:
    output = defaultdict(Fraction)
    for outer in q2_target[target]:
        coefficient = outer["jets"].get((), Fraction(0))
        if not coefficient:
            continue
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
    output = defaultdict(Fraction)
    for outer in inclusion[target]:
        middle, word = outer["inputs"][0]
        coefficient = outer["jets"].get((), Fraction(0))
        if not coefficient:
            continue
        for inner in q2_source[middle]:
            for inputs, value in _differentiate(inner, word):
                _add(output, inputs, coefficient * value)
    return output


def _q2_path(certificate: dict) -> Path:
    artifact = certificate["taylor_artifacts"]["q2"]
    path = ROOT / artifact["path"]
    if _sha256(path) != artifact["sha256"]:
        raise AssertionError(f"q2 artifact hash drifted: {path}")
    return path


def build_payload() -> dict:
    source_certificate = _load(SOURCE_CERTIFICATE)
    target_certificate = _load(TARGET_CERTIFICATE)
    inclusion_payload = _load(INCLUSION)
    if inclusion_payload["claim_status"] != "EXACT_PBW_CHAIN_MAP_TARGET_Q1_REPLAYED":
        raise AssertionError("unary inclusion has not passed target-q1 replay")
    q2_source = _operation_rows(_load(_q2_path(source_certificate)))
    q2_target = _operation_rows(_load(_q2_path(target_certificate)))
    inclusion = _inclusion_rows(inclusion_payload)
    source_rows = inclusion_payload["map"]["source_rows"]
    target_rows = inclusion_payload["map"]["target_rows"]
    terms = []
    row_counts: list[int] = []
    degree_profile: Counter[tuple[int, int, int]] = Counter()
    maximum_total_order = 0
    for target, target_row in enumerate(target_rows):
        defect = _pullback_row(target, q2_target, inclusion)
        for key, value in _pushforward_row(target, q2_source, inclusion).items():
            _add(defect, key, -value)
        row_counts.append(len(defect))
        for inputs, coefficient in sorted(defect.items()):
            order = sum(len(word) for _row, word in inputs)
            maximum_total_order = max(maximum_total_order, order)
            degrees = sorted(source_rows[row]["degree"] for row, _word in inputs)
            degree_profile[(target_row["degree"], degrees[0], degrees[1])] += 1
            terms.append(
                {
                    "output_row": target,
                    "inputs": [
                        {"row": row, "word": list(word)} for row, word in inputs
                    ],
                    "coefficient": _coefficient(coefficient),
                }
            )
    content = {
        "formula": "Delta2=q2_W(f1,f1)-f1*q2_E",
        "evaluation": "complete_homogeneous_basepoint_PBW_operator",
        "source_row_count": len(source_rows),
        "target_row_count": len(target_rows),
        "maximum_total_order": maximum_total_order,
        "term_count": len(terms),
        "row_defect_counts": row_counts,
        "terms": terms,
    }
    return {
        "schema": "relative-arity-two-pbw-defect-v1",
        "result_id": PAYLOAD_ID,
        "coefficient_field": "Q",
        "background_id": "compact_magnetic_Plebanski_Hacyan_product",
        "source_carrier_id": inclusion_payload["source_carrier_id"],
        "target_carrier_id": inclusion_payload["target_carrier_id"],
        "source_rows": source_rows,
        "target_rows": target_rows,
        "content": content,
        "canonical_sha256": _canonical_sha256(content),
        "degree_profile": [
            {
                "output_degree": key[0],
                "input_degrees": [key[1], key[2]],
                "term_count": count,
            }
            for key, count in sorted(degree_profile.items())
        ],
    }


def build_certificate(payload: dict) -> dict:
    source_certificate = _load(SOURCE_CERTIFICATE)
    target_certificate = _load(TARGET_CERTIFICATE)
    dependencies = {
        "source_taylor_certificate": {"path": str(SOURCE_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(SOURCE_CERTIFICATE)},
        "source_q2": {"path": str(_q2_path(source_certificate).relative_to(ROOT)), "sha256": _sha256(_q2_path(source_certificate))},
        "target_taylor_certificate": {"path": str(TARGET_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(TARGET_CERTIFICATE)},
        "target_q2": {"path": str(_q2_path(target_certificate).relative_to(ROOT)), "sha256": _sha256(_q2_path(target_certificate))},
        "unary_inclusion": {"path": str(INCLUSION.relative_to(ROOT)), "sha256": _sha256(INCLUSION)},
        "unary_inclusion_receipt": {"path": str(INCLUSION_RECEIPT.relative_to(ROOT)), "sha256": _sha256(INCLUSION_RECEIPT)},
    }
    counts = payload["content"]["row_defect_counts"]
    return {
        "schema": "relative-arity-two-defect-v1",
        "result_id": RESULT_ID,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "result_state": "NONZERO_STRICT_ARITY_TWO_DEFECT_F2_SOLVE_REQUIRED",
        "background_id": payload["background_id"],
        "source_carrier_id": payload["source_carrier_id"],
        "target_carrier_id": payload["target_carrier_id"],
        "dependencies": dependencies,
        "defect_payload": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": _sha256(PAYLOAD),
            "result_id": PAYLOAD_ID,
        },
        "checks": {
            "unary_chain_map_replayed": True,
            "strict_arity_two_defect_zero": not any(counts),
            "nonzero_row_count": sum(bool(count) for count in counts),
            "term_count": sum(counts),
            "maximum_total_order": payload["content"]["maximum_total_order"],
            "maxwell_equation_rows_strict": counts[30:34] == [0, 0, 0, 0],
            "u1_identity_row_strict": counts[38] == 0,
        },
        "claim_flags": {
            "STRICT_F1_ARITY_TWO_MORPHISM": not any(counts),
            "F2_SOLVE_REQUIRED": any(counts),
            "F2_EXISTS": False,
            "F2_OBSTRUCTED": False,
            "ARITY_THREE_AUTHORIZED": False,
        },
        "next_gate": "SOLVE_SUPPORT_LOCAL_RELATIVE_F2_OR_CERTIFY_NORMALIZED_OBSTRUCTION",
        "claim_boundary": (
            "Exact strict arity-two PBW defect of the replayed support-local unary inclusion at the complete homogeneous product base point. "
            "Naturality of the source, target and inclusion globalizes the coefficientwise operator statement. A nonzero strict defect requires an allowed f2 homotopy; it is not a nonexistence theorem. "
            "No f2, arity-three morphism, cyclic, causal, cohomological, observable, particle or quantum claim is promoted."
        ),
    }


def write() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    PAYLOAD.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    )
    certificate = build_certificate(payload)
    CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")


def check() -> None:
    payload = build_payload()
    expected_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    if PAYLOAD.read_text() != expected_payload:
        raise AssertionError("stale relative arity-two defect payload")
    expected_certificate = json.dumps(build_certificate(payload), indent=2, sort_keys=True) + "\n"
    if CERTIFICATE.read_text() != expected_certificate:
        raise AssertionError("stale relative arity-two defect certificate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
