#!/usr/bin/env python3
"""Independent verifier for the 108-row emitter unary and recoil gate."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_108_row_emitter_unary_recoil import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("108-row emitter unary/recoil certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")

    lam, m2 = sp.symbols("lambda m2", positive=True)
    euler = sp.diag(lam + m2, m2)
    candidate = sp.diag(1 / (lam + m2), 1 / m2)
    if sp.simplify(euler * candidate - sp.eye(2)) != sp.zeros(2):
        raise ValueError("independent massive Green replay failed")
    p, e0, e1, v0, v1 = sp.symbols("p e0 e1 v0 v1", nonzero=True)
    expected = v0**2 / (p**2 * e0) + v1**2 / (p**2 * e1)
    saved_recoil = sp.sympify(
        value["coupled_recoil_green"]["fixture"]["Maxwell_block_first_recoil"],
        locals={"p": p, "e0": e0, "e1": e1, "v0": v0, "v1": v1},
    )
    if sp.simplify(saved_recoil - expected) != 0:
        raise ValueError("independent recoil coefficient replay failed")
    rows = value["carrier_and_background"]["ordered_new_rows"]
    if [item["index"] for item in rows] != list(range(84, 108)):
        raise ValueError("emitter row order is not contiguous")
    if len({item["row_id"] for item in rows}) != 24:
        raise ValueError("emitter row identifiers are not unique")
    for key in ("FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED", "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED", "DETECTOR_RECOIL_COEFFICIENT_EVALUATED", "EMITTER_STRESS_BACKREACTION_INCLUDED", "FINITE_PARAMETER_84_ROW_APPARATUS_GREEN_HYPERBOLICITY_CERTIFIED", "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED", "QUANTUM_CLAIM"):
        if value["flags"][key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
