#!/usr/bin/env python3
"""Independent consumer for BERGER_Q3_ACTION_SECTOR_CROSSCHECK."""

from __future__ import annotations

from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_Q3_ACTION_SECTOR_CROSSCHECK.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q3-action-sector-crosscheck-v1.schema.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _coefficient(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    if value["sqrt10"] != 0:
        raise AssertionError("selected sector is not rational")
    rational = value["rational"]
    if isinstance(rational, int):
        return Fraction(rational)
    return Fraction(rational["numerator"], rational["denominator"])


def _direct_values() -> dict[tuple[int, int], Fraction]:
    h, r = sp.symbols("h r")
    q = sp.Rational(9, 40)
    k = 1 - 2 * r
    lapse = sp.sqrt(1 - h - 2 * r)
    rho = 1 + r
    density = lapse * k ** sp.Rational(3, 2) * (
        5 * (sp.Rational(4, 3) * (1 - q) ** 2) / (8 * k**2)
        + rho**2 * sp.Rational(3, 4) ** 2 / (2 * lapse**2)
        - ((4 - q) / 2) * rho**2 / (12 * k)
        - sp.Rational(119, 480) * rho**4 / 4
    )
    values: dict[tuple[int, int], Fraction] = {}
    for output in (27, 37):
        for input_h in range(4):
            dh = input_h + (output == 27)
            dr = 3 - input_h + (output == 37)
            value = sp.factor(2 * sp.diff(density, h, dh, r, dr).subs({h: 0, r: 0}))
            values[(output, input_h)] = Fraction(int(value.p), int(value.q))
    return values


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    for record in certificate["source_manifest"].values():
        if _sha256(ROOT / record["path"]) != record["sha256"]:
            raise AssertionError(f"source hash mismatch: {record['path']}")

    direct = _direct_values()
    recorded = {
        (entry["output"], entry["input_h_count"]): Fraction(
            entry["expected_from_direct_action"]
        )
        for entry in certificate["coefficients"]
    }
    if direct != recorded:
        raise AssertionError("recorded direct-action derivatives drifted")

    for output in (27, 37):
        path = ROOT / certificate["source_manifest"][f"q3_row_{output}"]["path"]
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            row = json.load(handle)
        selected = [
            term
            for term in row["terms"]
            if {term[0], term[2], term[4]} <= {5, 15}
            and term[1] == term[3] == term[5] == [0, 0, 0, 0]
        ]
        if len(selected) != 8:
            raise AssertionError(f"row {output} selected-sector coverage drifted")
        for term in selected:
            input_h = (term[0], term[2], term[4]).count(5)
            if _coefficient(term[6]) != direct[(output, input_h)]:
                raise AssertionError(f"row {output} action/payload mismatch")

    if certificate["flags"]["FULL_INDEPENDENT_Q3_REDERIVATION"] is not False:
        raise AssertionError("strategic cross-check was overstated")
    print("BERGER_Q3_ACTION_SECTOR_CROSSCHECK independent audit: PASS")
    print("schema, hashes, direct action derivatives, and 16 ordered payload coefficients: exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
