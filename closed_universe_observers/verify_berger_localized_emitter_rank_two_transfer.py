#!/usr/bin/env python3
"""Independent verifier for the localized-emitter rank-two transfer."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_localized_emitter_rank_two_transfer import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
)


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("localized-emitter certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")

    beta = 2 * sp.sqrt(10) / 3
    s0, c1, mu = sp.symbols("S_0 C_1 mu", positive=True)
    matrix = sp.Matrix([[-beta * s0, 0], [mu, beta * c1]])
    determinant = sp.factor(matrix.det())
    if sp.simplify(determinant + beta**2 * s0 * c1) != 0 or determinant == 0:
        raise ValueError("independent triangular determinant failed")
    if value["transfer_matrix"]["rank"] != 2:
        raise ValueError("rank payload drifted")
    if value["topological_localization"]["H1_dimension"] != 0 or value["topological_localization"]["H2_dimension"] != 0:
        raise ValueError("S3 localization topology drifted")
    if value["causal_support"]["inter_window_gap"] != "5/24":
        raise ValueError("causal gap drifted")
    flags = value["flags"]
    for key in (
        "ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED",
        "DYNAMICAL_EMITTER_RECOIL_INCLUDED",
        "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED",
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if flags[key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
