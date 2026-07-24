"""Exact Taylor-model operations used by the moving-frame producer."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import sys
from copy import deepcopy
from fractions import Fraction


CORRECTION = Fraction(93, 4)
sys.set_int_max_str_digits(1_000_000)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tagged_model(text: str, tag: str) -> dict:
    match = re.search(rf"^{re.escape(tag)} (.+)$", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"missing serialized model {tag}")
    return json.loads(match.group(1))


def fraction_from_bits(bits: str) -> Fraction:
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise RuntimeError("nonfinite interval endpoint")
    return Fraction.from_float(value)


def bits_from_float(value: float) -> str:
    return struct.pack(">d", value).hex()


def outward_float(value: Fraction, direction: int) -> float:
    result = float(value)
    exact = Fraction.from_float(result)
    if direction < 0 and exact > value:
        result = math.nextafter(result, -math.inf)
    elif direction > 0 and exact < value:
        result = math.nextafter(result, math.inf)
    if not math.isfinite(result):
        raise RuntimeError("nonfinite outward-rounded endpoint")
    return result


def validate_model(model: dict, rows: int) -> None:
    expected = {
        "schema": "ivtaylor-degree4-v1",
        "generator": 7315,
        "degree": 4,
        "rows": rows,
        "cols": 1,
        "refusal_code": 0,
    }
    for key, value in expected.items():
        if model.get(key) != value:
            raise RuntimeError(f"Taylor model field drift: {key}")
    if len(model["coefficients"]) != 5:
        raise RuntimeError("degree-four coefficient rail missing")
    if any(len(block) != rows for block in model["coefficients"]):
        raise RuntimeError("Taylor coefficient row count drift")
    if len(model["remainder_bits"]) != rows:
        raise RuntimeError("Taylor remainder row count drift")


def add_scaled_rows(
    tangent: dict,
    base: dict,
    row_pairs: tuple[tuple[int, int], ...],
    scale: Fraction = CORRECTION,
) -> dict:
    """Return tangent + scale*base on selected rows with exact/outward math."""
    result = deepcopy(tangent)
    for tangent_row, base_row in row_pairs:
        for degree in range(5):
            left = Fraction(
                tangent["coefficients"][degree][tangent_row][0]
            )
            right = Fraction(base["coefficients"][degree][base_row][0])
            result["coefficients"][degree][tangent_row][0] = str(
                left + scale * right
            )
        tan_lo_bits, tan_hi_bits = tangent["remainder_bits"][tangent_row][0]
        base_lo_bits, base_hi_bits = base["remainder_bits"][base_row][0]
        exact_lo = (
            fraction_from_bits(tan_lo_bits)
            + scale * fraction_from_bits(base_lo_bits)
        )
        exact_hi = (
            fraction_from_bits(tan_hi_bits)
            + scale * fraction_from_bits(base_hi_bits)
        )
        if exact_lo > exact_hi:
            raise RuntimeError("invalid corrected interval")
        result["remainder_bits"][tangent_row][0] = [
            bits_from_float(outward_float(exact_lo, -1)),
            bits_from_float(outward_float(exact_hi, +1)),
        ]
    return result


def exact_hull(model: dict, row: int) -> tuple[Fraction, Fraction]:
    coefficients = [
        Fraction(model["coefficients"][degree][row][0])
        for degree in range(5)
    ]
    radius = sum(abs(value) for value in coefficients[1:])
    lo_bits, hi_bits = model["remainder_bits"][row][0]
    lo = coefficients[0] - radius + fraction_from_bits(lo_bits)
    hi = coefficients[0] + radius + fraction_from_bits(hi_bits)
    if lo > hi:
        raise RuntimeError("invalid exact Taylor hull")
    return lo, hi


def interval_record(interval: tuple[Fraction, Fraction]) -> dict:
    lo, hi = interval
    text = f"{lo}|{hi}"
    return {
        "lower_decimal": float(lo),
        "upper_decimal": float(hi),
        "lower_sign": (lo > 0) - (lo < 0),
        "upper_sign": (hi > 0) - (hi < 0),
        "exact_pair_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "excludes_zero": lo > 0 or hi < 0,
    }


def correction_row_receipt(
    tangent: dict,
    base: dict,
    corrected: dict,
    tangent_row: int,
    base_row: int,
) -> dict:
    tan_lo, tan_hi = (
        fraction_from_bits(value)
        for value in tangent["remainder_bits"][tangent_row][0]
    )
    base_lo, base_hi = (
        fraction_from_bits(value)
        for value in base["remainder_bits"][base_row][0]
    )
    exact_lo = tan_lo + CORRECTION * base_lo
    exact_hi = tan_hi + CORRECTION * base_hi
    out_lo, out_hi = (
        fraction_from_bits(value)
        for value in corrected["remainder_bits"][tangent_row][0]
    )
    if not (out_lo <= exact_lo <= exact_hi <= out_hi):
        raise RuntimeError("outward correction enclosure failed")
    exact_coefficients = [
        str(
            Fraction(tangent["coefficients"][degree][tangent_row][0])
            + CORRECTION
            * Fraction(base["coefficients"][degree][base_row][0])
        )
        for degree in range(5)
    ]
    if exact_coefficients != [
        corrected["coefficients"][degree][tangent_row][0]
        for degree in range(5)
    ]:
        raise RuntimeError("exact coefficient correction failed")
    return {
        "tangent_row": tangent_row,
        "base_row": base_row,
        "scale": "93/4",
        "exact_coefficients_sha256": canonical_sha256(exact_coefficients),
        "exact_remainder_pair_sha256": hashlib.sha256(
            f"{exact_lo}|{exact_hi}".encode()
        ).hexdigest(),
        "emitted_remainder_contains_exact_sum": True,
    }
