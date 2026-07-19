#!/usr/bin/env python3
"""Independent replay of the transverse Kantowski--Sachs obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-kantowski-sachs-global-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != ref["sha256"] or payload["result_id"] != ref["artifact_id"]:
            raise ValueError(f"dependency drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source drifted: {relative}")

    e = sp.symbols("epsilon", real=True)
    b0 = 1 - e**2 / 6
    c = sp.factor(b0 * (e**2 - b0**2 / 3 + 1))
    excess = sp.factor(c - sp.Rational(2, 3))
    if str(c) != value["exact_obstruction"]["C_epsilon"]:
        raise ValueError("independent first-integral constant mismatch")
    if str(excess) != value["exact_obstruction"]["C_epsilon_minus_2_over_3"]:
        raise ValueError("independent supercritical excess mismatch")
    if sp.expand(e**4 - 126 * e**2 + 648).subs(e**2, 1) != 523:
        raise ValueError("positivity bound mismatch")
    b = sp.symbols("b", positive=True)
    potential = b**2 / 3 - 1 + c / b
    radial_weyl = sp.simplify((1 + potential) / b**2 - sp.Rational(1, 3))
    if sp.simplify(radial_weyl - c / b**3) != 0:
        raise ValueError("independent Weyl-channel derivation failed")
    w = c / b**3
    channels = [-w, w / 2, w / 2, -w / 2, -w / 2, w]
    if sp.simplify(4 * sum(channel**2 for channel in channels) - 12 * c**2 / b**6) != 0:
        raise ValueError("independent Weyl contraction failed")
    if value["flags"]["TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY"]:
        raise ValueError("singular branch was promoted to a global family")
    if value["flags"]["ALL_TRANSVERSE_BACH_FLAT_FAMILIES_OBSTRUCTED"]:
        raise ValueError("scoped obstruction was overgeneralized")
    print("NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
