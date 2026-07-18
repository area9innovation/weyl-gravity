#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_correlated_diagonal_fraction_stream import (
    CERTIFICATE,
    DEPENDENCIES,
    EXPECTED_ROWS,
    ROOT,
    SCHEMA,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["result_id"] == json.loads(path.read_text())["result_id"]
        assert reference["sha256"] == _sha256(path)
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == _sha256(ROOT / source["path"])
    rows = value["even_fraction_rows"] + value["odd_companion_rows"]
    assert [(row["two_j"], row["basis_index"]) for row in rows] == list(EXPECTED_ROWS)
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)
    assert value["coverage_mutation"]["detected"] is True
    assert value["coverage_mutation"]["expected_row_count"] == len(EXPECTED_ROWS)
    missing = value["sobolev_tail_preflight"]["missing_input_ledger"]
    assert len(missing) == 4 and all(item["available"] is False for item in missing)
    assert value["sobolev_tail_preflight"]["route_status"] == "OPEN"
    assert value["flags"]["COMPLETE_DIAGONAL_STREAM_EXPORTED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("correlated diagonal-fraction stream verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
