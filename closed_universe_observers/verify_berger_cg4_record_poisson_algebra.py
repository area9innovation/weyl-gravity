#!/usr/bin/env python3
"""Independent verifier for the C-G4 record Poisson algebra."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_cg4_record_poisson_algebra import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def _independent_transport(value: dict) -> None:
    beta = 2 * sp.sqrt(10) / 3
    s0, c0, s1, c1 = sp.symbols("S_0 C_0 S_1 C_1")
    matrix = beta * sp.Matrix([[-s0, -c0], [c1, -s1]])
    delta = sp.factor(matrix.det())
    if sp.simplify(delta - beta**2 * (s0 * s1 + c0 * c1)) != 0:
        raise ValueError("independent determinant failed")
    source_bracket = sp.Matrix([[0, -1 / (32 * sp.pi**2)], [1 / (32 * sp.pi**2), 0]])
    record_bracket = sp.simplify(matrix * source_bracket * matrix.T)
    if sp.simplify(record_bracket[0, 1] + delta / (32 * sp.pi**2)) != 0:
        raise ValueError("independent bracket transport failed")
    inverse = matrix.inv()
    if sp.simplify((inverse * record_bracket * inverse.T - source_bracket).norm()) != 0:
        raise ValueError("independent inverse bracket replay failed")
    if value["phase_plane_to_records"]["rank"] != 2:
        raise ValueError("rank payload drifted")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("C-G4 record algebra certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    _independent_transport(value)
    flags = value["flags"]
    for key in ("FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED", "COMPLETE_HARMONIC_SIGNAL_ALGEBRA_CERTIFIED", "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED", "SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES_CERTIFIED", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    if value["mutation_results"][0]["observed_rank"] != 1:
        raise ValueError("cloned detector mutation drifted")
    return value


def main() -> int:
    verify()
    print("BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
