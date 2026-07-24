#!/usr/bin/env python3
"""Independent verifier for the first correlated affine horizon successor."""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "correlated-affine-seed-successor-certificate.json"
SCHEMA = HERE / "correlated-affine-seed-successor-schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify_model(model: dict) -> None:
    payload = dict(model)
    expected = payload.pop("content_sha256")
    if canonical_hash(payload) != expected:
        raise SystemExit(f"model content hash drift: {model['stage']}")
    required = {
        "omega_model",
        "dual_tau_state",
        "polynomial_coefficients",
        "affine_generators",
        "shared_noise_domain",
        "residual_norm_ball",
        "radial_taylor_coefficients",
    }
    if not required <= set(model):
        raise SystemExit(f"incomplete correlated model: {model['stage']}")
    if model["residual_norm_ball"]["componentwise_independent_boxes"]:
        raise SystemExit("Cartesian remainder regression")
    if not model["dual_tau_state"]["same_omega_parameter_for_both_rails"]:
        raise SystemExit("dual rails no longer share omega")
    degrees = [row["degree"] for row in model["polynomial_coefficients"]]
    if degrees != [0, 1, 2, 3, 4]:
        raise SystemExit("omega polynomial degree drift")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if certificate["status"] != "ONE_CORRELATED_RADIAL_SUCCESSOR_CERTIFIED":
        raise SystemExit("status drift")
    for row in certificate["imports"].values():
        path = ROOT / row["path"]
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"import hash drift: {path}")
    for row in certificate["source"].values():
        path = ROOT / row["path"]
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"source hash drift: {path}")

    initial = certificate["initial_model"]
    successor = certificate["successor_model"]
    verify_model(initial)
    verify_model(successor)
    if successor["parent_sha256"] != initial["content_sha256"]:
        raise SystemExit("model parent drift")
    for normalization in (
        certificate["initial_normalization"],
        certificate["successor_normalization"],
    ):
        if Fraction(normalization["full_denominator_modulus_lower"]) <= 0:
            raise SystemExit("pivot does not exclude zero")
        if normalization["exact_base_pivot"] != "1":
            raise SystemExit("base pivot identity drift")
        if normalization["exact_tangent_pivot"] != "0":
            raise SystemExit("tangent pivot identity drift")
    step = certificate["radial_step"]
    if Fraction(step["cauchy_scaled_norm"]) >= 1:
        raise SystemExit("radial Cauchy gate drift")
    if Fraction(successor["residual_norm_ball"]["radius"]) >= 1:
        raise SystemExit("successor residual is not bounded below pivot scale")
    if not certificate["terminal"]["one_radial_successor_certified"]:
        raise SystemExit("terminal success flag drift")
    print("horizon correlated affine seed successor verifier: PASS")


if __name__ == "__main__":
    main()
