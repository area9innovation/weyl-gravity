#!/usr/bin/env python3
"""Independent audit of the globally parameterized five-form-factor family."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY.json"
)
SCHEMA = (
    HERE / "schema/parameterized-parity-even-five-form-factor-family-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_value(value: dict[str, Any], *, validate_schema: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    if validate_schema:
        Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
        payload = json.loads(path.read_text())
        if payload["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result-id drifted: {name}")
        dependencies[name] = payload
    assembly = dependencies["assembly"]
    nonunique = dependencies["kernel_nonuniqueness"]

    coordinates = value["canonical_quotient_section"]["coordinates"]
    raw = assembly["maximal_determined_quotient"]["quotient_ledger"][
        "raw_channel_order"
    ]
    if len(coordinates) != 10 or set(coordinates) != set(raw) - {"I28_231"}:
        raise ValueError("canonical quotient section is not the imported section")
    matrix = sp.Matrix(value["ambiguity_module"]["matrix"])
    if matrix.shape != (10, 10) or matrix.rank() != 10:
        raise ValueError("finite Schur ambiguity is not rank ten")
    if matrix.T.nullspace():
        raise ValueError("a nonzero universal finite Schur combination survived")
    if matrix != sp.eye(10):
        raise ValueError("stored dual unit-shift basis is not normalized")

    family = value["parameterized_family"]
    partial = assembly["maximal_determined_quotient"]
    if (
        family["universal_partial_BV_formula_digest"] != partial["formula_digest"]
        or family["universal_partial_BV_channel_row_digests"]
        != partial["channel_row_digests"]
        or family["Schur_scale_response"]
        != assembly["longitudinal_Schur_boundary"]["scale_density"]
    ):
        raise ValueError("universal partial/scale summand crosswalk failed")
    if nonunique["third_curvature_row_witness"][
        "mixed_third_variation_shifts"
    ]["Delta_d123_log_Det_3_R"] != {"numerator": 1, "denominator": 1}:
        raise ValueError("unit smoothing ambiguity source drifted")
    if any(
        row["folded_into_nonlocal_functions"] is not False
        for row in value["local_normalizations"].values()
    ):
        raise ValueError("a local normalization entered the nonlocal family")
    if value["holdouts"]["interpolation_used"] is not False:
        raise ValueError("special-background interpolation was used")


def mutation_suite(stored: dict[str, Any]) -> int:
    schema = json.loads(SCHEMA.read_text())
    mutations: list[dict[str, Any]] = []
    mutation = deepcopy(stored)
    mutation["ambiguity_module"]["matrix"][0][0] = 0
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["ambiguity_module"]["rank"] = 9
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["holdouts"]["interpolation_used"] = True
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["local_normalizations"]["strict_C2"][
        "folded_into_nonlocal_functions"
    ] = True
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["claim_flags"]["COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED"] = True
    mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            Draft202012Validator(schema).validate(mutation)
            verify_value(mutation, validate_schema=False)
        except Exception:
            rejected += 1
        else:
            raise ValueError("parameterized-family mutation was accepted")
    return rejected


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    verify_value(stored)
    rejected = mutation_suite(stored)
    print(
        "PARAMETERIZED PARITY-EVEN FIVE-FORM-FACTOR FAMILY AUDIT: "
        f"PASS ({rejected} mutations rejected)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
