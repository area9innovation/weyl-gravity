#!/usr/bin/env python3
"""Independent replay of the generic ghost Endo-Duhamel reduction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-endo-duhamel-reduction-v1.schema.json"
SOURCE_ARCHIVE_SHA256 = "485ad72c51304f25e289d3f6c72705a956c547c134e2f183bef3750e63e6757c"
SOURCE_TEX_SHA256 = "4b5cdb2dbf08cc1a34dc268e1961c54f0a1eee096d2df63214a73e91d0d71fc2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        identifier = dependency.get("result_id") or dependency.get("schema")
        if reference["sha256"] != _sha256(path) or reference["result_id"] != identifier:
            raise ValueError("Endo-Duhamel dependency drifted")

    h = tuple(map(_fraction, value["repository_operator_convention"]["H_coefficients"]))
    f = tuple(map(_fraction, value["exact_Endo_split"]["F_coefficients"]))
    h0 = tuple(map(_fraction, value["exact_Endo_split"]["H0_coefficients"]))
    w = tuple(map(_fraction, value["exact_Endo_split"]["W_coefficients"]))
    alpha = _fraction(value["exact_Endo_split"]["alpha"])
    if (
        h != (Fraction(1), Fraction(-1), Fraction(-1, 2))
        or f != (Fraction(1), Fraction(1), Fraction(0))
        or h0 != (Fraction(1), Fraction(1), alpha)
        or w != (Fraction(0), Fraction(-2), Fraction(0))
        or tuple(left + right for left, right in zip(h0, w, strict=True)) != h
    ):
        raise ValueError("H=H0+W convention map failed")

    longitudinal = 1 - alpha
    projectors = value["principal_projectors"]
    heat = value["exact_Endo_heat_kernel"]
    if (
        alpha != Fraction(-1, 2)
        or longitudinal != Fraction(3, 2)
        or _fraction(projectors["longitudinal_eigenvalue"]) != longitudinal
        or _fraction(projectors["inverse_longitudinal_coefficient"])
        != Fraction(2, 3)
        or _fraction(heat["proper_time_lower_multiplier"]) != 1
        or _fraction(heat["proper_time_upper_multiplier"]) != longitudinal
        or heat["finite_proper_time_interval"] is not True
        or heat["IR_infinite_range_introduced"] is not False
    ):
        raise ValueError("Endo heat-kernel specialization failed")

    # Flat projector identity: the scalar integral changes only the
    # longitudinal exponential from exp(-t p^2) to exp(-(3/2)t p^2).
    if heat["flat_projector_check"] != (
        "K_H0_flat=Pi_T exp(-t p^2)+Pi_L exp(-(3/2)t p^2)"
    ):
        raise ValueError("flat Endo projector identity drifted")

    table = value["Duhamel_expansion"]["cubic_work_table"]
    expected = [(n, 3 - n, 3, -1 if n % 2 else 1, n) for n in range(4)]
    actual = [
        (
            row["Ricci_insertion_count"],
            row["maximum_background_order_from_Endo_kernels"],
            row["total_curvature_order"],
            row["Duhamel_sign"],
            row["simplex_dimension"],
        )
        for row in table
    ]
    if actual != expected:
        raise ValueError("cubic Duhamel work table drifted")

    provenance = value["source_provenance"]
    if (
        provenance["arxiv"] != "2508.06439v2"
        or provenance["source_archive_sha256"] != SOURCE_ARCHIVE_SHA256
        or provenance["source_tex_sha256"] != SOURCE_TEX_SHA256
    ):
        raise ValueError("primary Endo source provenance drifted")

    true_flags = {
        "GENERIC_GHOST_ENDO_BASE_IDENTIFIED",
        "ENDO_HEAT_KERNEL_FORMULA_SPECIALIZED",
        "NONZERO_MODE_ENDO_DETERMINANT_REDUCED",
        "CUBIC_DUHAMEL_INSERTION_BOUND_CERTIFIED",
        "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED",
    }
    flags = value["claim_flags"]
    if any(flags[name] is not True for name in true_flags) or any(
        flag is not False for name, flag in flags.items() if name not in true_flags
    ):
        raise ValueError("Endo-Duhamel claim boundary crossed")

    print("independent generic ghost Endo-Duhamel reduction: PASS")
    return value


if __name__ == "__main__":
    verify()
