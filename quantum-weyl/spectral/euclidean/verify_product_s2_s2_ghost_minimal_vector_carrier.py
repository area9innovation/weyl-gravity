#!/usr/bin/env python3
"""Independent verifier for the product minimal-vector carrier."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_CARRIER.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-minimal-vector-carrier-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    reference = payload["dependencies"]["product_schur_carrier"]
    source_path = ROOT / reference["path"]
    assert source_path.is_file()
    assert _sha256(source_path) == reference["sha256"]
    source = json.loads(source_path.read_text())
    assert source["result_id"] == reference["result_id"]

    exceptional_dimension = 0
    for row in payload["selected_exact_modes"]:
        if row["status"] == "REGULAR":
            ratio = Fraction(1)
            factors = {}
            for polarization in row["polarizations"]:
                assert polarization["status"] == "REGULAR"
                key = polarization["factor"]
                factors.setdefault(key, [])
                factors[key].append(polarization["polarization"])
                ratio *= _q(polarization["relative_eigenvalue"])
            assert all(sorted(values) == ["coexact", "exact"] for values in factors.values())
            assert ratio == _q(row["regular_minimal_vector_ratio"])
        else:
            exceptional_dimension += row["degeneracy"]
            statuses = {item["status"] for item in row["polarizations"]}
            assert statuses == {"MATCHED_WITH_SCHUR_POLE", "KILLING_ZERO_PRIMED_OUT"}
            assert _q(row["paired_exact_vector_times_schur_ratio"]) == Fraction(1, 3)
    assert exceptional_dimension == 6
    priming = payload["priming_policy"]
    assert priming["Killing_zero_dimension"] == 6
    assert priming["matched_exact_exceptional_dimension"] == 6

    defect = payload["zeta_weighted_local_defect"]
    assert _q(defect["scalar_a0_per_polarization"]) == Fraction(1, 2)
    assert _q(defect["Wres_F_inverse_square"]) == 1
    assert _q(defect["first_defect_per_polarization"]) == -1
    assert _q(defect["second_defect_per_polarization"]) == -4
    assert _q(defect["two_polarization_total_defect"]) == -10

    flags = payload["claim_flags"]
    assert flags["PRODUCT_MINIMAL_VECTOR_MODE_CARRIER_SUPPLIED"] is True
    assert flags["KILLING_ZERO_PRIMING_COMPUTED"] is True
    assert flags["MINIMAL_VECTOR_ZETA_WEIGHTED_LOCAL_DEFECT_COMPUTED"] is True
    assert flags["MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED"] is False
    assert flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 GHOST MINIMAL VECTOR: INDEPENDENT CARRIER PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
