#!/usr/bin/env python3
"""Independent verifier for exact endpoint recurrence/divisor certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
Q, R, W = sp.symbols("q r omega")
N = sp.symbols("n", integer=True, nonnegative=True)
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(
        value,
        locals={"q": Q, "r": R, "omega": W, "n": N, "I": I},
    )


def zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def derive(
    g: sp.Expr, ell: sp.Expr, u: sp.Expr, multiplier: sp.Expr
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    return tuple(
        sp.cancel(value)
        for value in (
            multiplier * g**2,
            multiplier * (g * sp.diff(g, Q) + 2 * g**2 * ell),
            multiplier * (
                g * sp.diff(g, Q) * ell
                + g**2 * (sp.diff(ell, Q) + ell**2)
                + u
            ),
        )
    )


def verify() -> list[str]:
    errors: list[str] = []
    doc = json.loads(CERTIFICATE.read_text())
    if doc.get("schema") != "phase3-axial-qnm-endpoint-germ-divisor-v1":
        errors.append("schema drift")
    if doc.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency-tag drift")
    imported: dict[str, dict] = {}
    for name, ref in doc.get("imports", {}).items():
        path = ROOT / ref["path"]
        if not path.is_file() or sha256(path) != ref["sha256"]:
            errors.append(f"input hash drift: {name}")
        else:
            imported[name] = json.loads(path.read_text())

    f = (R - 2) / R
    v = 6 * (R - 2) * (R - 1) / R**4
    if "rw_factor" in imported:
        rw = imported["rw_factor"]["operators"]["L_RW"]
        if not zero(
            parse(rw["a"]) - (sp.diff(f, R) / f + 2 * I * W / f)
        ):
            errors.append("imported RW a coefficient mismatch")
        if not zero(parse(rw["b"]) + v / f**2):
            errors.append("imported RW b coefficient mismatch")
    rh = 2 / (1 - Q)
    gh = Q * (1 - Q)**2 / 2
    ah, bh, ch = derive(
        gh, 2 * I * W / Q, (W**2 - v).subs(R, rh), 4 / Q
    )
    ri = 1 / Q
    gi = -(1 - 2 * Q) * Q**2
    ai, bi, ci = derive(
        gi,
        I * W / Q**2 + 2 * I * W / Q,
        (W**2 - v).subs(R, ri),
        1 / Q**2,
    )
    for section, derived in (
        ("horizon_germ", (ah, bh, ch)),
        ("infinity_germ", (ai, bi, ci)),
    ):
        for key, value in zip(("A", "B", "C"), derived):
            if not zero(parse(doc[section][key]) - value):
                errors.append(f"{section} {key} mismatch")

    n = N
    horizon_divisor = (
        sp.Poly(ah, Q).nth(1) * n * (n + 1)
        + sp.Poly(bh, Q).nth(0) * (n + 1)
    )
    infinity_divisor = (
        sp.Poly(ai, Q).nth(1) * n * (n + 1)
        + sp.Poly(bi, Q).nth(0) * (n + 1)
    )
    if not zero(
        horizon_divisor - (n + 1) * (n + 1 + 4 * I * W)
    ):
        errors.append("horizon divisor derivation failed")
    if not zero(infinity_divisor - 2 * I * W * (n + 1)):
        errors.append("infinity divisor derivation failed")
    if not zero(parse(doc["horizon_germ"]["divisor"]) - horizon_divisor):
        errors.append("recorded horizon divisor mismatch")
    if not zero(parse(doc["infinity_germ"]["divisor"]) - infinity_divisor):
        errors.append("recorded infinity divisor mismatch")

    disk = doc["seed_disk"]
    cr = sp.Rational(disk["center_re"])
    ci = sp.Rational(disk["center_im"])
    radius = sp.Rational(disk["radius"])
    left = -cr - radius
    upper = ci - radius
    if left <= 0 or upper <= 0:
        errors.append("seed disk quadrant margin failed")
    if sp.Rational(disk["strict_left_half_plane_margin"]) != left:
        errors.append("left margin drift")
    if sp.Rational(disk["strict_upper_half_plane_margin"]) != upper:
        errors.append("upper margin drift")

    flags = doc["claim_flags"]
    required_true = (
        "endpoint_reduced_equations_exact",
        "endpoint_formal_recurrence_divisors_exact",
        "seed_disk_divisor_noncollision_exact",
        "horizon_nonresonant_frobenius_germ_exists",
    )
    required_false = (
        "horizon_convergent_germ_remainder_enclosed",
        "infinity_asymptotic_remainder_enclosed",
        "complex_ball_endpoint_columns_constructed",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
        "QNM_enclosed",
        "beta_or_EP2_established",
    )
    if any(flags.get(key) is not True for key in required_true):
        errors.append("positive claim flag drift")
    if any(flags.get(key) is not False for key in required_false):
        errors.append("fail-closed claim flag drift")

    receipt = json.loads(RECEIPT.read_text())
    if receipt.get("certificate_sha256") != sha256(CERTIFICATE):
        errors.append("certificate receipt hash drift")
    for name, digest in receipt.get("artifact_sha256", {}).items():
        path = HERE / name
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"artifact receipt hash drift: {name}")
    return errors


def main() -> None:
    errors = verify()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: exact endpoint recurrence/divisor certificate verified")


if __name__ == "__main__":
    main()
