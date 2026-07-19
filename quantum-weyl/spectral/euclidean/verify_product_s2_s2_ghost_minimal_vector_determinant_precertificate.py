#!/usr/bin/env python3
"""Independent verifier for the product minimal-vector determinant enclosure."""

from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-minimal-vector-determinant-precertificate-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _tail(shift: int, cutoff: int) -> Fraction:
    x0 = Fraction(2 * cutoff + 3, 2)
    s3 = x0**-3 + Fraction(1, 2) * x0**-2
    s4 = x0**-4 + Fraction(1, 3) * x0**-3
    lattice = Fraction(1, 2) * s3 + Fraction(125, 162) * s4
    lattice += Fraction(1, 4) * s3 + Fraction(125, 432) * s4
    q_min = x0 * x0 + Fraction(1, 2)
    comparison = 1 - Fraction(3, 4) / q_min
    lambda_min = x0 * x0 - Fraction(1, 4)
    return Fraction(shift**3, 3) * lattice / comparison**3 / (1 - Fraction(shift) / lambda_min)


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for name, reference in payload["dependencies"].items():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        source = json.loads(path.read_text())
        assert source["result_id"] == reference["result_id"]

    for proof in payload["det3_proofs"]:
        assert proof["rectangular_cutoff"] == 2400
        assert proof["large_taylor_order"] == 120
        assert proof["small_taylor_order"] == 8
        assert _q(proof["exterior_tail_bound"]) == _tail(proof["shift"], 2400)
        assert _q(proof["rounding_bound"]) < Fraction(3, 10**9)
        assert _q(proof["small_taylor_remainder_bound"]) == Fraction(1, 445500000000)

    zeta = payload["product_zeta_rows"]
    assert Decimal(zeta["FP_product_zeta_at_1"]["lower"]) < Decimal("-0.616628142085089423") < Decimal(zeta["FP_product_zeta_at_1"]["upper"])
    assert Decimal(zeta["FP_product_zeta_at_2"]["lower"]) < Decimal("0.321997089890338989") < Decimal(zeta["FP_product_zeta_at_2"]["upper"])
    rows = payload["directed_enclosures"]
    expected = {
        "first_component_weighted_modified": Decimal("4.6464226"),
        "second_component_weighted_modified": Decimal("9.6379169"),
        "two_polarization_minimal_vector_weighted": Decimal("28.5686790"),
        "two_polarization_minimal_vector_zeta": Decimal("18.5686790"),
        "full_vector_plus_schur_weighted": Decimal("19.0791630"),
    }
    for name, candidate in expected.items():
        assert Decimal(rows[name]["lower"]) < candidate < Decimal(rows[name]["upper"])
    # The producer serializes 70-digit directed interval endpoints.  Verify
    # interval orientation and the independently assembled enclosure relations
    # at a precision wider than those endpoints; Decimal's process-default 28
    # digits would round the arithmetic first.
    with localcontext() as context:
        context.prec = 100
        for row in rows.values():
            assert Decimal(row["lower"]) < Decimal(row["upper"])
        first = rows["first_component_weighted_modified"]
        second = rows["second_component_weighted_modified"]
        weighted = rows["two_polarization_minimal_vector_weighted"]
        reconstructed_weighted_lower = 2 * (
            Decimal(first["lower"]) + Decimal(second["lower"])
        )
        reconstructed_weighted_upper = 2 * (
            Decimal(first["upper"]) + Decimal(second["upper"])
        )
        assert Decimal(weighted["lower"]) <= reconstructed_weighted_lower
        assert reconstructed_weighted_upper <= Decimal(weighted["upper"])
        assert Decimal(rows["two_polarization_minimal_vector_weighted"]["lower"]) - 10 == Decimal(rows["two_polarization_minimal_vector_zeta"]["lower"])
        assert Decimal(rows["two_polarization_minimal_vector_weighted"]["upper"]) - 10 == Decimal(rows["two_polarization_minimal_vector_zeta"]["upper"])
        schur = json.loads(
            (ROOT / payload["dependencies"]["schur_assembly"]["path"]).read_text()
        )["directed_enclosures"]["coupled_schur_log"]
        full = rows["full_vector_plus_schur_weighted"]
        assert Decimal(full["lower"]) <= Decimal(weighted["lower"]) + Decimal(
            schur["lower"]
        )
        assert Decimal(weighted["upper"]) + Decimal(schur["upper"]) <= Decimal(
            full["upper"]
        )

    flags = payload["claim_flags"]
    assert flags["MINIMAL_VECTOR_RIGOROUS_ENCLOSURE_DERIVED"] is True
    assert flags["FULL_VECTOR_PLUS_SCHUR_WEIGHTED_ENCLOSURE_DERIVED"] is True
    assert flags["MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED"] is False
    assert flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"] is False
    assert payload["tier3_blocker"]["status"] == "FAILED_NOT_A_PASS"
    print("PRODUCT S2xS2 GHOST MINIMAL VECTOR DETERMINANT: INDEPENDENT PRECERTIFICATE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
