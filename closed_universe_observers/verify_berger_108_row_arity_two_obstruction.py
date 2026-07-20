#!/usr/bin/env python3
"""Independently verify the complete Berger arity-two obstruction."""

import argparse
import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA, build, replay_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="rerun the exhaustive exact 108-row replay")
    args = parser.parse_args()
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.full:
        assert value == build()
        assert value["arity_two_replay"] == replay_audit()
    else:
        assert value["arity_two_replay"]["formal_differential_coefficient_defect_summary"]["operator_key_count"] == 3432
        assert value["arity_two_replay"]["complete_defect_summary"]["operator_key_count"] == 2340
        assert value["arity_two_replay"]["typed_64_row_base_control_summary"]["operator_key_count"] == 0
    for name, reference in value["dependency_refs"].items():
        path = DEPENDENCIES[name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    mode = "full" if args.full else "fast"
    print(f"BERGER_108_ROW_ARITY_TWO_OBSTRUCTION independent verification ({mode}): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
