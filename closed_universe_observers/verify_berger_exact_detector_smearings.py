#!/usr/bin/env python3
"""Independent verifier for exact detector profiles and advanced covectors."""

import json
from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_exact_detector_smearings import (
    CERTIFICATE, DEPENDENCIES, INPUT, INPUT_SCHEMA, SCHEMA, _sha256,
    adjoint_chain_audit, profile_audit,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    data = json.loads(INPUT.read_text())
    Draft202012Validator(json.loads(INPUT_SCHEMA.read_text())).validate(data)
    if value["authoritative_input"]["sha256"] != _sha256(INPUT):
        raise AssertionError("detector profile input drifted")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency drifted: {name}")
    base = profile_audit(data)
    if not base["unit_spatial_rod_integrals"] or not base["clock_supports_disjoint"]:
        raise AssertionError("base detector profiles failed")
    if profile_audit(data, omit_spatial_scale=True)["unit_spatial_rod_integrals"]:
        raise AssertionError("spatial normalization mutation escaped")
    if profile_audit(data, duplicate_clock=True)["clock_supports_disjoint"]:
        raise AssertionError("clock duplication mutation escaped")
    if profile_audit(data, clone_polarization=True)["polarizations_distinct"]:
        raise AssertionError("polarization mutation escaped")
    if adjoint_chain_audit(delete_outer_coderivative=True)["maxwell_gauge_adjoint_well_typed"]:
        raise AssertionError("coderivative mutation escaped")
    print("BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
