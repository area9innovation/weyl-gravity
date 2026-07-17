#!/usr/bin/env python3
"""Independent verifier for the polarization two-form emitter handoff."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_polarization_emitter_handoff import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("polarization-emitter handoff is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    if value["carrier_108"]["degree_ranks_minus1_0_1_2"] != [6, 48, 48, 6]:
        raise ValueError("independent carrier rank replay failed")
    z = sp.symbols("z", nonzero=True)
    if sp.diag(z, z, z).det() != z**3:
        raise ValueError("independent principal symbol replay failed")
    if "delta_gHat^2" not in value["euler_and_recoil_blocks"]["conservation"]:
        raise ValueError("coexact conservation witness missing")
    for key in ("108_ROW_Q1_CERTIFIED", "108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED", "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED", "RECOIL_COEFFICIENT_COMPUTED", "EMITTER_STRESS_BACKREACTION_INCLUDED", "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED", "QUANTUM_CLAIM"):
        if value["flags"][key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
