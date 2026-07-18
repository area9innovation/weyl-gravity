#!/usr/bin/env python3
"""Independent verifier for dynamical-emitter Cauchy rank two."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_dynamical_emitter_rank_two import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("dynamical-emitter Cauchy rank certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    k0, k1, mu = sp.symbols("kappa_0 kappa_1 mu", nonzero=True)
    matrix = sp.Matrix([[k0, 0], [mu, k1]])
    if sp.factor(matrix.det()) != k0 * k1 or matrix.rank() != 2:
        raise ValueError("independent triangular rank replay failed")
    k, mass = sp.symbols("k m", positive=True)
    omega = sp.sqrt(k**2 + mass**2)
    momentum = sp.Matrix([omega, 0, 0, k])
    two_form = sp.zeros(4)
    two_form[0, 1], two_form[1, 0] = k, -k
    two_form[3, 1], two_form[1, 3] = -omega, omega
    if sp.simplify(momentum.T * two_form) != sp.zeros(1, 4) or two_form[0, 1] == 0:
        raise ValueError("independent massive-polarization reconstruction failed")
    polarization = value["local_massive_polarization"]
    if polarization["mass_shell_defect"] != "0" or polarization["constraint_defect_count"] != 0 or not polarization["switched_current_polarization_nonzero"]:
        raise ValueError("independent polarization replay failed")
    for key in ("ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED", "DETECTOR_RECOIL_G2_COEFFICIENT_EVALUATED", "EMITTER_STRESS_BACKREACTION_INCLUDED", "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED", "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED", "QUANTUM_CLAIM"):
        if value["flags"][key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
