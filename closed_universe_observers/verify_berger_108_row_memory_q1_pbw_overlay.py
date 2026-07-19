#!/usr/bin/env python3
"""Independently verify the scalar Berger memory q1 first-jet overlay."""

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from closed_universe_observers.berger_108_row_component_jet_contract import (
    add,
    derivative,
    generator,
    normalize,
    scale,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY.json"
SCHEMA = P / "schema/berger-108-row-memory-q1-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-memory-q1-pbw-overlay-payload-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scalar(value):
    return (
        Fraction(value["rational"]["numerator"], value["rational"]["denominator"]),
        Fraction(value["sqrt10"]["numerator"], value["sqrt10"]["denominator"]),
    )


def polynomial(term):
    factors = tuple(
        generator(
            factor["kind"], factor["name"], factor["vertical_multiindex"], factor["spacetime_multiindex"]
        )
        for factor in term["coefficient_factors"]
    )
    return normalize([(scalar(term["coefficient"]), factors)])


def operator(block):
    value = {}
    for entry in block["entries"]:
        for term in entry["terms"]:
            word = tuple(axis for axis, count in enumerate(term["input_pbw_multiindex"]) for _ in range(count))
            key = entry["output_row"], entry["input_row"], word
            value[key] = add(value.get(key, {}), polynomial(term))
    return value


def signature(value):
    rows = []
    for key, polynomial_value in sorted(value.items()):
        for term in serialize(polynomial_value):
            rows.append((key, json.dumps(term, sort_keys=True, separators=(",", ":"))))
    return Counter(rows)


def transpose(value, *, source_row, target_rows, extra_sign):
    output = {}
    for (_row, column, word), coefficient in value.items():
        target = target_rows[column - 55] if 55 <= column <= 58 else target_rows[0]
        if not word:
            pieces = [((), coefficient)]
        else:
            assert len(word) == 1
            axis = word[0]
            pieces = [
                ((axis,), scale(coefficient, (Fraction(-1), Fraction(0)))),
                ((), scale(derivative(coefficient, axis), (Fraction(-1), Fraction(0)))),
            ]
        for target_word, target_coefficient in pieces:
            key = target, source_row, target_word
            output[key] = add(
                output.get(key, {}),
                scale(target_coefficient, (Fraction(extra_sign), Fraction(0))),
            )
    return output


def factor_names(block):
    return {
        factor["name"]
        for entry in block["entries"]
        for term in entry["terms"]
        for factor in term["coefficient_factors"]
    }


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    overlay = value["memory_overlay"]
    payload_ref = overlay["payload_ref"]
    payload_path = ROOT / payload_ref["path"]
    assert sha256(payload_path) == payload_ref["sha256"]
    payload = json.loads(payload_path.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    assert payload["result_id"] == payload_ref["result_id"]
    for key, expected in overlay.items():
        if key != "payload_ref":
            assert payload[key] == expected
    blocks = payload["blocks"]
    assert canonical_sha256(blocks) == overlay["entries_canonical_sha256"]
    assert overlay["block_count"] == 16
    assert overlay["row_support"] == [59, 60, 61, 62, 80, 81, 82, 83]
    assert overlay["column_support"] == [55, 56, 57, 58, 70, 71, 72, 73]
    assert all(
        len({(entry["output_row"], entry["input_row"]) for entry in block["entries"]}) == len(block["entries"])
        for block in blocks
    )
    positions = {(entry["output_row"], entry["input_row"]) for block in blocks for entry in block["entries"]}
    terms = sum(len(entry["terms"]) for block in blocks for entry in block["entries"])
    assert len(positions) == overlay["nonzero_matrix_position_count"]
    assert terms == overlay["serialized_term_count"]

    by_id = {block["id"]: block for block in blocks}
    for channel in (0, 1):
        # The transport blocks must be exact formal transposes.
        for degree in ("Q00", "Q10"):
            forward = operator(by_id[f"memory{channel}_transport_{degree}"])
            actual = operator(by_id[f"memory{channel}_transport_adjoint_{degree}"])
            expected = transpose(forward, source_row=72 + channel, target_rows=[80 + channel], extra_sign=1)
            assert signature(actual) == signature(expected)

        # The opposite odd-pairing signs make the profile q1 adjoint minus the
        # formal transpose of its already-signed forward block.
        for degree in ("Q01", "Q11"):
            forward_block = by_id[f"memory{channel}_profile_{degree}"]
            actual_block = by_id[f"memory{channel}_profile_adjoint_{degree}"]
            expected = transpose(
                operator(forward_block), source_row=72 + channel,
                target_rows=[59, 60, 61, 62], extra_sign=-1,
            )
            assert signature(operator(actual_block)) == signature(expected)
            names = factor_names(forward_block)
            assert {f"f{channel}", f"rho{channel}", f"J{channel}", ("R0_1", "R1_2")[channel]} <= names
            if degree == "Q01":
                assert "kappa" in names and not any(name.startswith("Phi2_") for name in names)
            else:
                assert {"kappa", "epsilon_R_squared"} <= names
                assert any(name.startswith("Phi2_") for name in names)

        mixed_forward_operator = operator(by_id[f"memory{channel}_profile_Q11"])
        assert mixed_forward_operator[82 + channel, 58, ()] == scale(
            mixed_forward_operator[82 + channel, 57, (1,)],
            (Fraction(0), Fraction(-3, 20)),
        )
        phi00_terms = [
            (monomial, coefficient)
            for monomial, coefficient in mixed_forward_operator[82 + channel, 56, (0,)].items()
            if any(factor[1] == "Phi2_00" for factor in monomial)
        ]
        assert len(phi00_terms) == 1
        assert phi00_terms[0][1] == (Fraction(3, 8), Fraction(0))

        q00 = by_id[f"memory{channel}_transport_Q00"]["entries"]
        assert len(q00) == 1 and q00[0]["terms"][0]["input_pbw_multiindex"] == [1, 0, 0, 0]
        q10_names = factor_names(by_id[f"memory{channel}_transport_Q10"])
        assert {"epsilon_R_squared", "Phi2_01", "Phi2_02", "Phi2_03"} <= q10_names

    assert not value["flags"]["SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
