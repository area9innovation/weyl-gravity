#!/usr/bin/env python3
"""Independent verifier for the dynamical-emitter recoil input gate."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_dynamical_emitter_recoil_gate import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("dynamical-emitter recoil gate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")

    lam, m0, m1 = map(sp.Integer, (1, 1, 4))
    difference = sp.factor(1 / (lam + m0) - 1 / (lam + m1))
    if difference != sp.Rational(3, 10):
        raise ValueError("independent recoil specialization failed")
    beta = 2 * sp.sqrt(10) / 3
    s0, c1 = sp.symbols("S_0 C_1", positive=True)
    if sp.factor(sp.Matrix([[-beta * s0, 0], [sp.Symbol("mu"), beta * c1]]).det()) != -40 * s0 * c1 / 9:
        raise ValueError("independent formal determinant failed")
    flags = value["flags"]
    for key in ("SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED", "EMITTER_BV_COMPLEX_CONSTRUCTED", "RECOIL_COEFFICIENT_COMPUTED", "FINITE_PARAMETER_COUPLED_GREEN_HYPERBOLICITY_CERTIFIED", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_DYNAMICAL_EMITTER_RECOIL_INPUT_GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
