#!/usr/bin/env python3
"""Independent structural consumer of the 84-row apparatus handoff."""

from __future__ import annotations

import hashlib
import json

import jsonschema
import sympy as sp

from closed_universe_observers import generate_berger_84_row_apparatus_handoff as result


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    payload = json.loads(result.CERTIFICATE.read_text())
    schema = json.loads(result.SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    for name, reference in payload["dependency_refs"].items():
        path = result.ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if _sha256(path) != reference["sha256"] or dependency["result_id"] != reference["result_id"]:
            raise AssertionError(f"dependency drifted: {name}")

    carrier = payload["carrier"]
    rows = carrier["component_rows"]
    if [row["index"] for row in rows] != list(range(84)):
        raise AssertionError("84-row indices are not canonical")
    if [row["row_id"] for row in rows[64:74]] != result.NEW_FIELDS:
        raise AssertionError("new field row order drifted")
    if [row["row_id"] for row in rows[74:84]] != result.NEW_PLUS:
        raise AssertionError("new antifield row order drifted")
    pairing = sp.zeros(20)
    for entry in carrier["new_pairing_entries"]:
        pairing[entry["left"] - 64, entry["right"] - 64] = sp.Rational(entry["coefficient"])
    if pairing.rank() != 20 or pairing + pairing.T != sp.zeros(20):
        raise AssertionError("new odd cotangent pairing is degenerate or has the wrong sign")

    synthesis = payload["physical_backreaction_synthesis"]
    z0, z1 = sp.sqrt(10) / 12, sp.sqrt(10) / 6
    t0, t1, frequency = sp.Rational(1, 4), sp.Rational(1, 2), sp.sqrt(58) / 3
    phase = lambda z: sp.Matrix([sp.cos(z) ** 2, sp.sin(z) ** 2, sp.cos(z) * sp.sin(z)])
    expected_zero = phase(z0) + phase(z1)
    expected_positive = sp.exp(-sp.I * frequency * t0) * phase(z0) + sp.exp(-sp.I * frequency * t1) * phase(z1)
    persisted_zero = sp.Matrix([sp.sympify(value) for value in synthesis["zero_frequency_coefficients"]])
    persisted_positive = sp.Matrix([sp.sympify(value) for value in synthesis["positive_frequency_coefficients"]])
    if (persisted_zero - expected_zero).applyfunc(sp.simplify) != sp.zeros(3, 1):
        raise AssertionError("physical zero-frequency Phi2 coefficients drifted")
    if (persisted_positive - expected_positive).applyfunc(sp.simplify) != sp.zeros(3, 1):
        raise AssertionError("physical positive-frequency Phi2 coefficients drifted")

    requirements = result.evaluate(json.loads(result.INPUT.read_text()))
    if not all(requirements.values()):
        raise AssertionError("declared handoff input no longer satisfies its requirements")
    for mutation in json.loads(result.INPUT.read_text())["mutations"]:
        observed = result.evaluate(result._patched(json.loads(result.INPUT.read_text()), mutation["patch"]))
        if observed[mutation["expected_failed_requirement"]] is not False:
            raise AssertionError(f"mutation did not fail closed: {mutation['name']}")
    flags = payload["flags"]
    if not flags["AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"]:
        raise AssertionError("84-row forward authority dropped")
    for forbidden in (
        "84_ROW_Q1_CERTIFIED", "84_ROW_RETARDED_GREEN_CERTIFIED", "84_ROW_Q2_Q3_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED", "DEFORMED_RANK_TWO_RESPONSE_CERTIFIED",
        "FULL_APPARATUS_RECOIL_CERTIFIED", "QUANTUM_CLAIM",
    ):
        if flags[forbidden]:
            raise AssertionError(f"construction gate over-promoted: {forbidden}")
    print("BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
