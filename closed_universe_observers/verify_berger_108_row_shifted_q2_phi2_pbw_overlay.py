#!/usr/bin/env python3
"""Independently reconstruct the scalar shifted q2(Phi2,-) PBW overlay."""

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY.json"
SCHEMA = P / "schema/berger-108-row-shifted-q2-phi2-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-shifted-q2-phi2-pbw-overlay-payload-v1.schema.json"
GRAVITY = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
MAXWELL = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
ROD_UNARY = P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def q(value) -> Fraction:
    return Fraction(value) if isinstance(value, int) else Fraction(value["numerator"], value["denominator"])


def scalar(value):
    return q(value["rational"]), q(value["sqrt10"])


def reconstruct():
    result = defaultdict(lambda: (Fraction(0), Fraction(0)))
    raw = 0
    for path in (GRAVITY, MAXWELL):
        for row in json.loads(path.read_text())["rows"]:
            for first, first_word, second, second_word, coefficient in row["terms"]:
                value = scalar(coefficient)
                if 5 <= first <= 14:
                    key = row["output"], second, tuple(second_word), first - 5, tuple(first_word)
                    old = result[key]
                    result[key] = old[0] + value[0], old[1] + value[1]
                    raw += 1
    return {key: value for key, value in result.items() if value != (0, 0)}, raw


def payload_terms(payload):
    return {
        (row["output"], term[0], tuple(term[1]), term[2], tuple(term[3])): scalar(term[4])
        for row in payload["rows"]
        for term in row["terms"]
    }


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]
    ref = value["payload_ref"]
    path = ROOT / ref["path"]
    assert sha256(path) == ref["sha256"]
    payload = json.loads(path.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    assert payload["result_id"] == ref["result_id"]
    assert canonical_sha256(payload["rows"]) == payload["rows_canonical_sha256"] == ref["rows_canonical_sha256"]

    expected, raw = reconstruct()
    actual = payload_terms(payload)
    assert actual == expected
    assert raw == payload["raw_contraction_count"] == 92965
    assert len(actual) == payload["normalized_term_count"] == 92965
    assert len({(key[0], key[1]) for key in actual}) == payload["nonzero_matrix_position_count"] == 310

    # Re-evaluate the published physical fourth-order witness from the new
    # abstract-Phi2 payload and the independent physical zero-mode vector.
    physical = json.loads(ROD_UNARY.read_text())["physical_phi2_tensor"]
    zero = {
        index: sp.sympify(coefficient, locals={"I": sp.I})
        for index, coefficient in physical["assembled_sparse_coefficients"]["zero"]
    }
    witness = sp.S.Zero
    for (output, input_row, input_word, component, background_word), coefficient in actual.items():
        if output == 27 and input_row == 5 and input_word == (0, 0, 0, 4) and sum(background_word) == 0:
            exact_coefficient = sp.Rational(coefficient[0].numerator, coefficient[0].denominator)
            exact_coefficient += sp.sqrt(10) * sp.Rational(coefficient[1].numerator, coefficient[1].denominator)
            witness += exact_coefficient * zero.get(10 * component, 0)
    assert sp.simplify(witness) == sp.Rational(623, 324)
    assert value["identity_disposition"]["both_symmetric_slots_mutation_detected"] is True
    assert not value["flags"]["SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
