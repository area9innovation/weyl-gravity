#!/usr/bin/env python3
"""Independent verifier for the BT full-phase g6 current reconciliation."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G6_CURRENT_RECONCILIATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-g6-current-reconciliation-v1.schema.json")
MOTIF = {(0, 0, 0, 0): -1, (0, 1, 0, 0): 1, (1, 0, 0, 0): 1, (1, 2, 0, 0): -1}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def reconstruct_bridge() -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    length = 5
    points = list(itertools.product(range(length), repeat=4))

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    field = {point: Fraction(MOTIF.get(point, 0)) for point in points}
    direction = {point: Fraction((3 * point[0] + 2 * point[1] + point[2] - point[3] + 1) % 7 - 3) for point in points}
    a, b, c, da, db, dc = {}, {}, {}, {}, {}, {}
    for point in points:
        ys, dys = [], []
        for axis in range(4):
            for step in (-1, 1):
                other = shift(point, axis, step)
                ys.append(field[other] - field[point])
                dys.append(direction[other] - direction[point])
        a[point], b[point], c[point] = sum(ys, Fraction(0)), sum((y**2 for y in ys), Fraction(0)), sum((y**3 for y in ys), Fraction(0))
        da[point] = sum(dys, Fraction(0))
        db[point] = 2 * sum((y * dy for y, dy in zip(ys, dys)), Fraction(0))
        dc[point] = 3 * sum((y**2 * dy for y, dy in zip(ys, dys)), Fraction(0))
    derivatives = (
        sum((a[x] * da[x] for x in points), Fraction(0)),
        sum((da[x] * b[x] + a[x] * db[x] for x in points), Fraction(0)) / 2,
        sum((da[x] * c[x] + a[x] * dc[x] for x in points), Fraction(0)) / 6 + sum((b[x] * db[x] for x in points), Fraction(0)) / 4,
    )
    fluxes = [Fraction(0), Fraction(0), Fraction(0)]
    for point in points:
        for axis in range(4):
            other = shift(point, axis, 1)
            delta, delta_h = field[other] - field[point], direction[other] - direction[point]
            currents = (
                a[point] - a[other],
                b[point] / 2 - b[other] / 2 + delta * (a[point] + a[other]),
                c[point] / 6 - c[other] / 6 + delta * (b[point] + b[other]) / 2 + delta**2 * (a[point] - a[other]) / 2,
            )
            for order, current in enumerate(currents):
                fluxes[order] += delta_h * current
    return derivatives, tuple(fluxes)


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")
        derivatives, fluxes = reconstruct_bridge()
        require(derivatives == fluxes == (Fraction(493), Fraction(689, 2), Fraction(5107, 6)), "lattice bridge drift")
        values = cert["exact_lattice_bridge_fixture"]["values"]
        require(tuple(frac(values[name]) for name in ("D_h_S0", "D_h_S1", "D_h_S2")) == derivatives, "certified derivatives drift")
        require(tuple(frac(values[name]) for name in ("flux_J1", "flux_J2", "flux_J3")) == fluxes, "certified fluxes drift")
        vector = cert["complete_full_phase_M4"]["exact_vector_fixture"]
        require(frac(vector["z2"]) == Fraction(4, 3), "vector normalization drift")
        require(frac(vector["M4_direct"]) == frac(vector["M4_square_root"]) == Fraction(26, 3), "vector M4 identity drift")
        order = cert["coupling_order_dictionary"]
        require("D_h S2=sum dh*J3" in order["coefficient_matching"], "J3/B matching omitted")
        require("[g^6]" in order["variance_order_map"] and "M4_full_phase" in order["variance_order_map"], "variance order map drift")
        scope = cert["conditioning_scope"]
        require("{0,+p,-p}" in scope["full_phase_free_covariance"], "full-phase deletion drift")
        require("rank-one" in scope["older_M4_scope"], "one-cosine scope omitted")
        disposition = cert["method_disposition"]
        require(disposition["complete_full_phase_M4_formula"] == "PROVED", "formula weakened")
        require(disposition["complete_full_phase_M4_finite_volume_value"] == "OPEN", "finite-volume value promoted")
        require(disposition["complete_full_phase_M4_large_volume_scaling"] == "OPEN", "large-volume result promoted")
        require(disposition["one_cosine_M4_sign_transfer_to_full_phase"] == "FORBIDDEN_SCOPE_MISMATCH", "scope boundary weakened")
        require(disposition["nonperturbative_background_current_susceptibility"] == "OPEN", "susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError) as error:
        if os.environ.get("BT_G6_VERIFY_DEBUG"):
            print(f"verification detail: {error}")
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT full-phase g6 current reconciliation: PASS" if ok else "BT full-phase g6 current reconciliation: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
