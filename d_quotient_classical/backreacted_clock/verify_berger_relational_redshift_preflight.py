#!/usr/bin/env python3
"""Independent schema, provenance, and rational replay for the G0 fixture."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-relational-redshift-preflight-v1.schema.json"


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    for record in certificate["dependency_refs"].values():
        source = ROOT / record["path"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {source}")
        if json.loads(source.read_text())["result_id"] != record["result_id"]:
            raise AssertionError(f"dependency result mismatch: {source}")
    for relative_path, expected_hash in certificate["provenance"]["source_manifest"].items():
        source = ROOT / relative_path
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
            raise AssertionError(f"source manifest mismatch: {source}")

    energy = Fraction(3, 4)
    v_emit = Fraction(0)
    v_receive = Fraction(3, 5)
    gamma_emit = Fraction(1)
    gamma_receive = Fraction(5, 4)
    nu_emit = energy * gamma_emit * (1 - v_emit)
    nu_receive = energy * gamma_receive * (1 - v_receive)
    ratio = nu_emit / nu_receive
    travel = Fraction(1, 5) / (1 - v_receive)
    theta_receive = Fraction(3, 4) * travel
    expected = {
        "gamma_emit": "1",
        "gamma_receive": "5/4",
        "nu_emit": str(nu_emit),
        "nu_receive": str(nu_receive),
        "one_plus_z": str(ratio),
        "z": str(ratio - 1),
        "travel_time": str(travel),
        "theta_emit": "0",
        "theta_receive": str(theta_receive),
        "emit_phase_slope": "-1",
        "receive_phase_slope": "-2/5",
    }
    if certificate["rational_fixture"]["results"] != expected:
        raise AssertionError("independent rational replay failed")
    if certificate["activation_gate"]["full_gate"] != "OPEN":
        raise AssertionError("full relational gate was promoted")
    if certificate["flags"]["QUANTUM_CLAIM"] is not False:
        raise AssertionError("G0 classical fixture was promoted to quantum")
    print("BERGER_RELATIONAL_REDSHIFT_PREFLIGHT independent replay: PASS")


if __name__ == "__main__":
    main()
