#!/usr/bin/env python3
"""Independent verifier for the dynamical-emitter recoil order/input gate."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_dynamical_emitter_recoil_preflight import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("dynamical-emitter recoil preflight is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    p, e0, e1, v0, v1 = sp.symbols("p e0 e1 v0 v1", nonzero=True)
    leading0 = v0 / (e0 * p)
    expected0 = sp.factor(leading0 * (v0**2 / (p * e0) + v1**2 / (p * e1)))
    saved0 = sp.sympify(
        value["order_audit"]["emitter_to_Maxwell_first_recoil_g3"][0],
        locals={"p": p, "e0": e0, "e1": e1, "v0": v0, "v1": v1},
    )
    if sp.simplify(saved0 - expected0) != 0:
        raise ValueError("independent absolute-g3 coefficient replay failed")
    if value["order_audit"]["emitter_to_Maxwell_absolute_g2"] != ["0", "0"]:
        raise ValueError("spurious absolute-g2 term accepted")
    if value["formal_rank_stability"]["constant_term"] != "kappa_0*kappa_1":
        raise ValueError("independent formal rank constant replay failed")
    for key in ("DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED", "EMITTER_STRESS_BACKREACTION_INCLUDED", "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED", "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED", "QUANTUM_CLAIM"):
        if value["flags"][key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
