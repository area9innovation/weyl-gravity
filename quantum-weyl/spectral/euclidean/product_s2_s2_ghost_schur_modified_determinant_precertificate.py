#!/usr/bin/env python3
"""Assemble the coefficient-computed product Schur modified determinant."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
from mpmath.libmp import to_rational


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_MODIFIED_DETERMINANT_PRECERTIFICATE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-modified-determinant-precertificate-v1.schema.json"
DEPENDENCIES = {
    "det3": HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json",
    "weighted_rows": HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json",
}
MP_IV_DPS = 70


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(payload["result_id"]),
        "sha256": _sha256(path),
    }


def _endpoint(interval: Any, index: int) -> str:
    numerator, denominator = to_rational(interval._mpi_[index])
    with localcontext() as context:
        context.prec = MP_IV_DPS + 12
        context.rounding = ROUND_FLOOR if index == 0 else ROUND_CEILING
        return format(Decimal(numerator) / Decimal(denominator), "f")


def _interval(row: dict[str, str]) -> Any:
    return mp.iv.mpf([row["lower"], row["upper"]])


def build() -> dict[str, Any]:
    det3 = json.loads(DEPENDENCIES["det3"].read_text())
    weighted = json.loads(DEPENDENCIES["weighted_rows"].read_text())
    if (
        det3["claim_flags"]["PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"] is not True
        or weighted["claim_flags"]["PRODUCT_WEIGHTED_ROW_RIGOROUS_ENCLOSURES_DERIVED"] is not True
        or weighted["claim_flags"]["PRODUCT_WEIGHTED_R_K_COMPUTED"] is not True
        or weighted["claim_flags"]["PRODUCT_FINITE_PART_R_K2_COMPUTED"] is not True
        or weighted["tier3_promotion_receipt"]["status"] != "PASSED"
    ):
        raise ValueError("product Schur determinant dependency boundary drifted")
    mp.mp.dps = MP_IV_DPS + 30
    mp.iv.dps = MP_IV_DPS
    det3_interval = mp.iv.mpf(
        [
            det3["det3_enclosure"]["lower_endpoint_decimal"],
            det3["det3_enclosure"]["upper_endpoint_decimal"],
        ]
    )
    split_interval = _interval(
        weighted["weighted_rows"]["low_order_split_R_K_minus_half_R_K2"]
    )
    regular = det3_interval + split_interval
    exceptional_log = -6 * mp.iv.log(mp.iv.mpf(3))
    coupled = regular + exceptional_log
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-schur-modified-determinant-precertificate-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_MODIFIED_DETERMINANT_PRECERTIFICATE",
        "result_state": "COUPLED_SCHUR_FACTOR_RIGOROUS_ENCLOSURE_COEFFICIENT_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": weighted["classical_commit"],
        "scope": weighted["scope"],
        "assembly_identity": {
            "regular_modified_determinant": "log det_3(I+K)+R_Delta(K)-(1/2)FP R_Delta(K^2)",
            "matched_exceptional_factor": "3^-6",
            "coupled_schur_log": "regular_modified_determinant-6 log(3)",
            "priming_policy": "the six matched vector-zero/Schur-pole directions occur only through the finite coupled factor 3^-6",
        },
        "directed_enclosures": {
            "regular_modified_determinant": {
                "lower": _endpoint(regular, 0),
                "upper": _endpoint(regular, 1),
            },
            "matched_exceptional_log": {
                "lower": _endpoint(exceptional_log, 0),
                "upper": _endpoint(exceptional_log, 1),
            },
            "coupled_schur_log": {
                "lower": _endpoint(coupled, 0),
                "upper": _endpoint(coupled, 1),
            },
            "arithmetic": f"mpmath directed interval arithmetic at {MP_IV_DPS} decimal digits",
        },
        "claim_flags": {
            "REGULAR_MODIFIED_SCHUR_DETERMINANT_ENCLOSURE_DERIVED": True,
            "MATCHED_EXCEPTIONAL_COUPLED_SCHUR_ENCLOSURE_DERIVED": True,
            "PRODUCT_WEIGHTED_R_K_COMPUTED": True,
            "PRODUCT_FINITE_PART_R_K2_COMPUTED": True,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "tier3_promotion_receipt": weighted["tier3_promotion_receipt"],
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "COMBINE_THE_PROMOTED_COUPLED_SCHUR_FACTOR_WITH_THE_MINIMAL_VECTOR_GHOST_DETERMINANT",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate rigorously combines the regular det_3 enclosure, the coefficient-computed weighted-row enclosures and the matched exceptional factor 3^-6 on S2(1) x S2(2), with the passing 850-test Tier-3 receipt inherited content-addressedly from the weighted rows. The resulting coupled Schur factor is coefficient-computed in this selected special-background weighted prescription; the minimal-vector determinant is assembled separately downstream. No generic-background form factor, complete Gamma1/Q1, restored QME, Lorentzian causal construction, Hadamard state, particle, positivity, scattering or unitarity theorem follows."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale modified determinant precertificate: {OUTPUT}")
    else:
        OUTPUT.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("PRODUCT S2xS2 SCHUR MODIFIED DETERMINANT: COEFFICIENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
