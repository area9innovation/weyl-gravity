#!/usr/bin/env python3
"""Independent verifier for the pair-block order-lambda4 connected ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_CONNECTED_LEDGER_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-connected-ledger-v1.schema.json",
)
ORIGIN = (0, 0, 0, 0)
EDGE = (1, 0, 0, 0)
INSIDE = {ORIGIN: (1, 0), EDGE: (0, 1)}
STEPS = tuple(
    tuple(sign if index == axis else 0 for index in range(4))
    for axis in range(4)
    for sign in (-1, 1)
)
COV = ((Fraction(9, 616), Fraction(1, 308)), (Fraction(1, 308), Fraction(9, 616)))


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def plus(left, right):
    return tuple(a + b for a, b in zip(left, right))


def poly_sum(*rows):
    out = defaultdict(Fraction)
    for row in rows:
        for key, value in row.items():
            out[key] += value
    return {key: value for key, value in out.items() if value}


def poly_scale(row, scalar):
    scalar = Fraction(scalar)
    return {key: scalar * value for key, value in row.items() if scalar * value}


def poly_product(left, right):
    out = defaultdict(Fraction)
    for (a, b), x in left.items():
        for (c, d), y in right.items():
            out[(a + c, b + d)] += x * y
    return {key: value for key, value in out.items() if value}


def poly_power(row, power):
    out = {(0, 0): Fraction(1)}
    for _ in range(power):
        out = poly_product(out, row)
    return out


def dual_sum(*rows):
    return poly_sum(*(row[0] for row in rows)), poly_sum(*(row[1] for row in rows))


def dual_scale(row, scalar):
    return poly_scale(row[0], scalar), poly_scale(row[1], scalar)


def dual_product(left, right):
    return poly_product(left[0], right[0]), poly_sum(
        poly_product(left[1], right[0]), poly_product(left[0], right[1])
    )


def dual_power(row, power):
    out = ({(0, 0): Fraction(1)}, {})
    for _ in range(power):
        out = dual_product(out, row)
    return out


def edge(vertex, neighbour, axis):
    value = defaultdict(Fraction)
    if neighbour in INSIDE:
        value[INSIDE[neighbour]] += 1
    if vertex in INSIDE:
        value[INSIDE[vertex]] -= 1
    derivative = neighbour[axis] ** 2 - vertex[axis] ** 2
    return ({key: item for key, item in value.items() if item}, {(0, 0): Fraction(derivative)} if derivative else {})


def action(axis):
    affected = {ORIGIN, EDGE}
    for site in (ORIGIN, EDGE):
        affected.update(plus(site, step) for step in STEPS)
    result = [({}, {}) for _ in range(4)]
    for site in affected:
        jets = []
        for power in range(1, 6):
            jets.append(dual_sum(*(dual_power(edge(site, plus(site, step), axis), power) for step in STEPS)))
        a, b, c, d, e = jets
        local = (
            dual_scale(dual_product(a, b), Fraction(1, 2)),
            dual_sum(dual_scale(dual_product(b, b), Fraction(1, 8)), dual_scale(dual_product(a, c), Fraction(1, 6))),
            dual_sum(dual_scale(dual_product(b, c), Fraction(1, 12)), dual_scale(dual_product(a, d), Fraction(1, 24))),
            dual_sum(dual_scale(dual_product(c, c), Fraction(1, 72)), dual_scale(dual_product(b, d), Fraction(1, 48)), dual_scale(dual_product(a, e), Fraction(1, 120))),
        )
        result = [dual_sum(old, new) for old, new in zip(result, local)]
    return result, len(affected)


@lru_cache(maxsize=None)
def moment(a, b):
    if a + b == 0:
        return Fraction(1)
    if (a + b) % 2:
        return Fraction()
    if a:
        same = (a - 1) * COV[0][0] * moment(a - 2, b) if a >= 2 else 0
        cross = b * COV[0][1] * moment(a - 1, b - 1)
        return same + cross
    return (b - 1) * COV[1][1] * moment(0, b - 2)


def average(poly, observed=False):
    return sum(value * moment(a + int(observed), b) for (a, b), value in poly.items())


def direct_response(axis):
    u, affected = action(axis)
    u1, u2, u3, u4 = u
    one = ({(0, 0): Fraction(1)}, {})
    e = [
        one,
        dual_scale(u1, -1),
        dual_sum(dual_scale(dual_power(u1, 2), Fraction(1, 2)), dual_scale(u2, -1)),
        dual_sum(dual_scale(u3, -1), dual_product(u1, u2), dual_scale(dual_power(u1, 3), Fraction(-1, 6))),
        dual_sum(dual_scale(u4, -1), dual_product(u1, u3), dual_scale(dual_power(u2, 2), Fraction(1, 2)), dual_scale(dual_product(dual_power(u1, 2), u2), Fraction(-1, 2)), dual_scale(dual_power(u1, 4), Fraction(1, 24))),
    ]
    z = [average(row[0]) for row in e]
    dz = [average(row[1]) for row in e]
    n = [average(row[0], True) for row in e]
    dn = [average(row[1], True) for row in e]
    m = [Fraction()] * 5
    dm = [Fraction()] * 5
    for order in range(5):
        m[order] = n[order] - sum(z[j] * m[order - j] for j in range(1, order + 1))
        dm[order] = dn[order] - sum(dz[j] * m[order - j] + z[j] * dm[order - j] for j in range(1, order + 1))
    return dm, affected, [len(row[0]) for row in u]


def partitions(total, floor=1):
    if total == 0:
        return [()]
    out = []
    for first in range(floor, total + 1):
        for tail in partitions(total - first, first):
            out.append((first,) + tail)
    return out


def coefficient(parts):
    counts = Counter(parts)
    return Fraction((-1) ** len(parts), math.prod(math.factorial(value) for value in counts.values()))


def expected_outer_rows():
    rows = []
    for i in range(1, 5):
        for parts in partitions(4 - i):
            s = len(parts)
            fields = 4 + 2 * s
            rows.append((i, parts, coefficient(parts), fields, fields // 2 - (1 + s) + 1))
    return rows


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if list(Draft202012Validator(schema).iter_errors(cert)):
        return False
    inputs = cert["provenance"]["inputs"]
    if any(file_hash(row["path"]) != row["sha256"] for row in inputs):
        return False
    longitudinal, affected_l, counts_l = direct_response(0)
    transverse, affected_t, counts_t = direct_response(1)
    checkpoint = cert["zero_background_checkpoint"]
    exact = {
        "longitudinal_lambda2": longitudinal[2],
        "transverse_lambda2": transverse[2],
        "orientation_averaged_lambda2": longitudinal[2] / 8 + 3 * transverse[2] / 8,
        "longitudinal_lambda4": longitudinal[4],
        "transverse_lambda4": transverse[4],
        "orientation_averaged_lambda4": longitudinal[4] / 8 + 3 * transverse[4] / 8,
    }
    if any(decode(checkpoint[key]) != value for key, value in exact.items()):
        return False
    truncated = Fraction(4, 25) * exact["orientation_averaged_lambda2"] + Fraction(16, 625) * exact["orientation_averaged_lambda4"]
    if decode(checkpoint["lambda_two_plus_four_at_two_fifths"]) != truncated or truncated >= 0:
        return False
    if affected_l != affected_t or affected_l != cert["scaled_action"]["affected_residual_sites"]:
        return False
    if counts_l != counts_t or counts_l != cert["scaled_action"]["zero_fiber_monomial_counts"]:
        return False
    actual_rows = cert["annealed_connected_g4"]["labeled_partition_table"]
    expected = expected_outer_rows()
    if len(actual_rows) != len(expected):
        return False
    for row, (i, parts, factor, fields, loops) in zip(actual_rows, expected):
        if (row["center_order"], tuple(row["parts"]), decode(row["coefficient"]), row["maximum_background_fields"], row["maximum_loop_rank"]) != (i, parts, factor, fields, loops):
            return False
    if any(row["maximum_loop_rank"] != 2 for row in actual_rows):
        return False
    disposition = cert["method_disposition"]
    forbidden = {"PROVED", "COEFFICIENT_COMPUTED", "LORENTZIAN_CERTIFIED"}
    for key in ("full_gibbs_finite_volume_g4_coefficient", "large_volume_g4_power_or_log", "actual_interacting_h_minus_one"):
        if disposition[key] in forbidden:
            return False
    print("[PASS] independent BT pair-block g4 ledger verifier (16/16)")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
