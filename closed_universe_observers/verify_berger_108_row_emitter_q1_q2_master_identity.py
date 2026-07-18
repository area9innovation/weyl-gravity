#!/usr/bin/env python3
"""Independent verifier for the covariant 108-row q1-q2 identity."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_emitter_q1_q2_master_identity import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    _sha256,
    master_identity_audit,
    row_coverage_audit,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        dependency = json.loads(path.read_text())
        if reference["sha256"] != _sha256(path) or reference["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency drifted: {name}")
    if master_identity_audit()["total_defect_count"] != 0:
        raise AssertionError("base master identity failed")
    if not row_coverage_audit()["all_output_rows_covered_exactly_once"]:
        raise AssertionError("base output-row coverage failed")
    mutations = [
        master_identity_audit(remove_outer_codifferential=True),
        master_identity_audit(omit_clock_source=True),
        master_identity_audit(omit_metric_output=True),
        master_identity_audit(omit_clock_output=True),
        master_identity_audit(omit_clock_modulus_partner=True),
        master_identity_audit(delete_diff_cotangent_partner=True),
    ]
    if not all(item["total_defect_count"] > 0 for item in mutations):
        raise AssertionError("master-identity mutation rail failed")
    if row_coverage_audit(delete_last_emitter_row=True)["all_output_rows_covered_exactly_once"]:
        raise AssertionError("row-coverage mutation rail failed")
    if value["pbw_payload_boundary"]["support_local_PBW_q2_payload_exported"] is not False:
        raise AssertionError("PBW payload overclaimed")
    print("BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
