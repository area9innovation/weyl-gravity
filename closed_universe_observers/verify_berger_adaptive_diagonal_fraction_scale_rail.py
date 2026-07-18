#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_adaptive_diagonal_fraction_scale_rail import (
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
    rows = value["even_scale_rows"] + value["odd_scale_rows"]
    assert [(row["two_j"], row["basis_index"]) for row in rows] == list(EXPECTED_ROWS)
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)
    assert [row["radial_subdivisions"] for row in value["even_scale_rows"]] == [64, 64, 128]
    mutation = value["anisotropic_resolution_mutation"]
    assert mutation["radial_subdivisions"] == 64 and mutation["angular_subdivisions"] == 128
    assert Fraction(mutation["interval"]["width"]) > Fraction(1, 10)
    assert mutation["detected"] is True
    assert value["flags"]["COMPLETE_DIAGONAL_STREAM_EXPORTED"] is False
    assert value["flags"]["ALL_CLOCK_POWERS_AND_POLARIZED_ROWS_EVALUATED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("adaptive diagonal-fraction scale rail verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
