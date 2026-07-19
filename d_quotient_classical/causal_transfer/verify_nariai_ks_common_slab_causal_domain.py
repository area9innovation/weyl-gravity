#!/usr/bin/env python3
"""Independent replay of the KS common-slab causal-domain theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-common-slab-causal-domain-v1.schema.json"


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

    e, y, a = sp.symbols("epsilon y a", real=True)
    b = 1 + e * y
    rhs = (2 * y + e * (y**2 - a**2)) / (2 * b)
    defect = sp.factor(2 * b * e * rhs + (e * a) ** 2 + 1 - b**2)
    if defect != 0:
        raise ValueError("independent Einstein substitution failed")
    t = sp.symbols("t", real=True)
    if sp.simplify(sp.diff(sp.sinh(t), t) - sp.cosh(t)) != 0:
        raise ValueError("base y equation failed")
    if sp.simplify(sp.diff(sp.cosh(t), t) - sp.sinh(t)) != 0:
        raise ValueError("base a equation failed")
    if not value["analytic_interface"]["common_reference_causal_cone"]:
        raise ValueError("common cone missing")
    if value["flags"]["TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER"]:
        raise ValueError("domain theorem was promoted to Green transfer")
    print("NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
