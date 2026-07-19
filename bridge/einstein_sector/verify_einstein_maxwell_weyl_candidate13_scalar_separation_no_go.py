"""Independent verifier for the candidate-13 scalar-separation no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != sha(schema_path):
        raise AssertionError("scalar-separation schema hash changed")
    records = {}
    for name, item in payload["provenance"]["inputs"].items():
        path = ROOT / item["path"]
        if item["sha256"] != sha(path):
            raise AssertionError(f"stale scalar-separation input: {path}")
        records[name] = json.loads(path.read_text(encoding="utf-8"))
    moment = records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]
    if not moment["H"].startswith("mu_H=-(L/4) sum omega^2") or not moment["P_x"].startswith("mu_Px=(L/4) sum k*omega"):
        raise AssertionError("moment-map normalization changed")
    if records["pressure"]["primary_action_identity"]["pressure_functional"] != "R_c(u)=(1/2) sum k_j^2 h_j":
        raise AssertionError("pressure normalization changed")

    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    if not (bool(rho > sp.Rational(1, 2)) and bool(rho < sp.Rational(3, 5))):
        raise AssertionError("candidate-13 rho interval changed")
    wm1_sq = rho + 6 - 2 * sp.sqrt(3)
    wp1_sq = rho + sp.Rational(16, 3)
    wm2_sq = 4 * rho + 6 - 2 * sp.sqrt(3)
    wp2_sq = 4 * rho + sp.Rational(16, 3)
    if not (
        bool(wm1_sq < sp.Rational(9, 5)**2)
        and bool(wp1_sq > sp.Rational(12, 5)**2)
        and bool(wm2_sq < sp.Rational(9, 4)**2)
        and bool(wp2_sq > sp.Rational(8, 3)**2)
    ):
        raise AssertionError("frequency endpoint bounds changed")
    w = sp.symbols("w", positive=True)
    functions = {
        "qminus_n1": 1 + sp.Rational(3, 8) * w - sp.Rational(2, 5) * w**2,
        "p_n1": sp.Rational(2, 5) * w**2 - sp.Rational(3, 8) * w - 1,
        "qminus_nminus2": 4 - sp.Rational(3, 4) * w - sp.Rational(2, 5) * w**2,
        "p_nminus2": sp.Rational(2, 5) * w**2 + sp.Rational(3, 4) * w - 4,
    }
    endpoints = {"qminus_n1": sp.Rational(9, 5), "p_n1": sp.Rational(12, 5), "qminus_nminus2": sp.Rational(9, 4), "p_nminus2": sp.Rational(8, 3)}
    expected = {"qminus_n1": sp.Rational(379, 1000), "p_n1": sp.Rational(101, 250), "qminus_nminus2": sp.Rational(23, 80), "p_nminus2": sp.Rational(38, 45)}
    for name, function in functions.items():
        if sp.factor(function.subs(w, endpoints[name])) != expected[name] or expected[name] <= 0:
            raise AssertionError(f"positive endpoint witness changed: {name}")
    if not (
        sp.diff(functions["p_n1"], w).subs(w, sp.Rational(12, 5)) > 0
        and sp.diff(functions["qminus_n1"], w).subs(w, 1) < 0
        and sp.diff(functions["p_nminus2"], w) > 0
        and sp.diff(functions["qminus_nminus2"], w) < 0
    ):
        raise AssertionError("coefficient monotonicity changed")
    if 12 * 625 - 84**2 != 444 or 12 * 6400 - 267**2 != 5511:
        raise AssertionError("radical bound witness changed")
    if payload["theorem"]["complete_bounded_cone"] != "Z2_candidate13_bounded={0}":
        raise AssertionError("bounded origin theorem changed")
    flags = payload["classification"]
    if not flags["candidate13_complete_bounded_cone_is_origin"] or flags["candidate13_nonzero_bounded_point_exists"]:
        raise AssertionError("candidate-13 bounded lifecycle changed")
    if flags["smooth_cone_collapses_to_origin"] or flags["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("scalar no-go exceeded its scope")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_SCALAR_SEPARATION_NO_GO verifier: PASS")


if __name__ == "__main__":
    verify()
