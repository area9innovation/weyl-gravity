#!/usr/bin/env python3
"""Independent verifier for the typed outgoing reduced frame at r=31."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path

import jsonschema

sys.set_int_max_str_digits(1_000_000)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tagged(text: str, tag: str) -> dict:
    match = re.search(rf"^{re.escape(tag)} (.+)$", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"missing {tag}")
    return json.loads(match.group(1))


def endpoint(bits: str) -> Fraction:
    return Fraction.from_float(struct.unpack(">d", bytes.fromhex(bits))[0])


def hull(model: dict, row: int) -> tuple[Fraction, Fraction]:
    values = [
        Fraction(model["coefficients"][degree][row][0])
        for degree in range(5)
    ]
    radius = sum(abs(value) for value in values[1:])
    lo_bits, hi_bits = model["remainder_bits"][row][0]
    return values[0] - radius + endpoint(lo_bits), (
        values[0] + radius + endpoint(hi_bits)
    )


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    if document["status"] != (
        "JOINT_REDUCED_FRAME_RANK3_KPLUS_ANALYTIC_OPEN"
    ):
        raise RuntimeError("joint reduced frame did not pass")
    for item in document["imports"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {item['path']}")

    imports = document["imports"]
    r_text = (ROOT / imports["R_reference_run"]["path"]).read_text()
    restart_text = (
        ROOT / imports["R_independent_restart_run"]["path"]
    ).read_text()
    r_base = tagged(r_text, "REFERENCE_BASE")
    r_tangent = tagged(r_text, "REFERENCE_TANGENT")
    if r_base != tagged(restart_text, "RESTART_BASE"):
        raise RuntimeError("R base restart mismatch")
    if r_tangent != tagged(restart_text, "RESTART_TANGENT"):
        raise RuntimeError("R tangent restart mismatch")
    s_document = json.loads(
        (ROOT / imports["S_r31_checkpoint"]["path"]).read_text()
    )
    s_payload = s_document["payload"]
    s_base = s_payload["base"]
    s_tangent = s_payload["tangent"]
    if s_payload["radius"] != "31":
        raise RuntimeError("S radius mismatch")
    for model, rows in (
        (r_base, 4),
        (r_tangent, 4),
        (s_base, 8),
        (s_tangent, 8),
    ):
        if (
            model["schema"] != "ivtaylor-degree4-v1"
            or model["generator"] != 7315
            or model["degree"] != 4
            or model["rows"] != rows
            or model["cols"] != 1
            or model["refusal_code"] != 0
        ):
            raise RuntimeError("typed model metadata mismatch")

    r_re = hull(r_base, 0)
    s_z_re = hull(s_base, 2)
    if not (r_re[0] > 0 and s_z_re[0] > 0):
        raise RuntimeError("triangular pivot did not exclude zero")
    minor = document["triangular_minor"]
    if minor["determinant_factorization"] != (
        "R_base[0]**2*S_base_Z[0]"
    ):
        raise RuntimeError("minor factorization drift")
    if not minor["determinant_nonzero"] or minor["complex_rank"] != 3:
        raise RuntimeError("rank-three flag missing")

    zero_rows = (2, 3, 6, 7)
    if not all(
        Fraction(s_tangent["coefficients"][degree][row][0]) == 0
        for degree in range(5)
        for row in zero_rows
    ):
        raise RuntimeError("frozen spin-one tangent coefficient drift")
    if not all(hull(s_tangent, row)[0] <= 0 <= hull(s_tangent, row)[1]
               for row in zero_rows):
        raise RuntimeError("padding no longer contains exact frozen zero")

    typed = document["typed_columns"]
    if typed["E"]["complex_blocks"] != ["R_base", "0", "0"]:
        raise RuntimeError("E epsilon-copy layout drift")
    if typed["R"]["complex_blocks"] != [
        "R_tangent",
        "R_base",
        "0",
    ]:
        raise RuntimeError("R layout drift")
    if typed["S"]["complex_blocks"] != [
        "S_tangent_X",
        "S_base_Y",
        "S_base_Z",
    ]:
        raise RuntimeError("S layout drift")

    flags = document["claim_flags"]
    for key in (
        "common_generator_preserved",
        "typed_E_R_S_reduced_columns_constructed",
        "joint_reduced_frame_rank_three_certified",
        "formal_K_plus_zero_preserved",
    ):
        if not flags[key]:
            raise RuntimeError(f"positive flag missing: {key}")
    for key in (
        "validated_analytic_K_plus_certified",
        "common_amplitude_outgoing_frame_certified",
        "T_plus_certified",
        "scattering_or_flux_certified",
    ):
        if flags[key]:
            raise RuntimeError(f"downstream claim promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent typed outgoing joint-frame verifier")


if __name__ == "__main__":
    main()
