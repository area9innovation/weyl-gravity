#!/usr/bin/env python3
"""Independent verifier for the axial threshold certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    if data.get("status") != "EXACT_THRESHOLD_IDENTITIES_PASS":
        raise AssertionError("certificate is not a passing exact result")
    if data.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise AssertionError("dependency tags changed")

    r, omega = sp.symbols("r omega", positive=True, nonzero=True)
    locals_ = {"r": r, "omega": omega, "I": sp.I}
    d_tortoise = lambda value: sp.cancel((r - 2) * sp.diff(value, r) / r)
    v2 = sp.sympify(data["operator"]["V2"], locals=locals_)
    v1 = sp.sympify(data["operator"]["V1"], locals=locals_)
    phi2 = sp.sympify(data["zero_modes"]["spin_two"], locals=locals_)
    phi1 = sp.sympify(data["zero_modes"]["spin_one"], locals=locals_)
    q2 = sp.sympify(data["reduction_of_order"]["spin_two"], locals=locals_)
    q1 = sp.sympify(data["reduction_of_order"]["spin_one"], locals=locals_)
    cocycle = sp.sympify(
        data["projective_cocycle"]["I_reduced"], locals=locals_
    )
    decomposition = sp.sympify(
        data["projective_cocycle"]["threshold_decomposition"], locals=locals_
    )
    primitive = sp.sympify(data["primitive"]["p"], locals=locals_)
    primitive_h = sp.sympify(
        data["primitive"]["p_horizon_fixed"], locals=locals_
    )

    residuals = [
        d_tortoise(d_tortoise(phi2)) - v2 * phi2,
        d_tortoise(d_tortoise(phi1)) - v1 * phi1,
        d_tortoise(d_tortoise(q2)) - v2 * q2,
        d_tortoise(d_tortoise(q1)) - v1 * q1,
        cocycle - decomposition,
        d_tortoise(d_tortoise(primitive)) - v2 * primitive - (r - 2) / r,
        primitive_h.subs(r, 2),
    ]
    if any(sp.simplify(value) != 0 for value in residuals):
        raise AssertionError("an exact residual is nonzero")
    if phi2.subs(r, 2) != 1 or phi1.subs(r, 2) != 1:
        raise AssertionError("horizon normalization failed")
    if data["zero_energy_resonance"] != {
        "reason": "the unique horizon-regular solutions grow as nonzero multiples of r^3",
        "spin_one": False,
        "spin_two": False,
    }:
        raise AssertionError("zero-resonance disposition changed")
    forbidden_promotions = (
        "a punctured positive-real interval on which T_plus is invertible",
        "the normalization-sensitive b/a^2 threshold bound",
    )
    ledger = data.get("does_not_establish", [])
    if any(item not in ledger for item in forbidden_promotions):
        raise AssertionError("fail-closed threshold boundary is incomplete")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate", type=Path, default=HERE / "certificate.json"
    )
    args = parser.parse_args()
    verify(args.certificate)
    print("PASS: independent exact threshold verification")


if __name__ == "__main__":
    main()
