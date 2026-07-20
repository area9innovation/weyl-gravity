"""Structurally independent verifier for BH2C_METRIC_ALL_ORDERS.

Re-runs the all-orders metric reconstruction on the VbGeo pipeline (the
verifier-side Schouten/Kulkarni--Nomizu curvature engine, structurally
distinct from weyl_geometry.Geometry / linearized_bach used by the producer)
and cross-checks every recorded object: the unified master ODE, both branch
exponents, the recurrence theorem coefficient, the positive control against
the certified sigma0, the degree-1 polynomial (log-free, unramified) mu=0
mode, the omega=0 exceptional classification, and the leading matrices.  It
also re-affirms that the leading matrices agree with BH2C_METRIC_LEADING and
validates the certificate against its schema and content hashes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2c_metric_all_orders import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_METRIC_ALL_ORDERS.json"
SCHEMA = HERE / "schema" / "bh2c-metric-all-orders-v1.schema.json"
LEADING = HERE / "certificates" / "BH2C_METRIC_LEADING.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate():
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")

    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]),
           "engine hash mismatch")
    _check(prov["linearized_bach_sha256"]
           == _sha256(ROOT / prov["linearized_bach_path"]),
           "linearized_bach hash mismatch")
    _check(prov["leading_certificate_sha256"]
           == _sha256(ROOT / prov["leading_certificate"]),
           "leading certificate hash mismatch")
    _check(prov["indicial_certificate_sha256"]
           == _sha256(ROOT / prov["indicial_certificate"]),
           "indicial certificate hash mismatch")
    for comp in payload["companions"]:
        _check(comp["certificate_sha256"] == _sha256(ROOT / comp["certificate"]),
               f"companion hash mismatch: {comp['certificate']}")

    # independent geometry rail
    res = run_analysis(VbGeo)

    _check(payload["master_ode"] == res["master_ode"], "master ODE mismatch")
    _check(payload["exponents"] == res["exponents"], "exponents mismatch")
    _check(payload["recurrence"] == res["recurrence"], "recurrence mismatch")
    _check(payload["positive_control"] == res["positive_control"],
           "positive control mismatch")
    _check(payload["polynomial_mode"] == res["polynomial_mode"],
           "polynomial mode mismatch")
    _check(payload["omega_zero"] == res["omega_zero"],
           "omega=0 classification mismatch")
    _check(payload["leading_matrix"] == res["leading_matrix"],
           "leading matrix mismatch")

    # scientific invariants must hold on the independent rail
    _check(res["master_ode"]["unified_across_parities"] is True,
           "parities not unified on independent rail")
    _check(res["exponents"]["oscillatory_branch"] == "-4*I*omega + 1",
           "oscillatory exponent drifted")
    _check(res["recurrence"]["diagonal_coeff"] == "-2*I*omega*(k - 3)",
           "recurrence coefficient drifted")
    _check(res["recurrence"]["lam0_all_orders_determined"] is True,
           "all-orders determination failed on independent rail")
    _check(res["recurrence"]["log_forced_omega_nonzero"] is False,
           "spurious log on independent rail")
    _check(res["polynomial_mode"]["degree"] == 1
           and res["polynomial_mode"]["logarithm"] is False
           and res["polynomial_mode"]["ramified"] is False,
           "polynomial-mode structure drifted")
    _check(res["positive_control"]["match"] is True,
           "positive control failed on independent rail")

    # leading matrices must equal BH2C_METRIC_LEADING
    lead = json.loads(LEADING.read_text(encoding="utf-8"))
    _check(res["leading_matrix"]["polar_B0h"] == lead["polar"]["B0h"],
           "polar B0h != BH2C_METRIC_LEADING")
    _check(res["leading_matrix"]["axial_B0h"] == lead["axial"]["B0h"],
           "axial B0h != BH2C_METRIC_LEADING")

    # claim-flag discipline
    cf = payload["claim_flags"]
    for flag in ("all_orders_reconstruction_certified",
                 "one_power_polynomial_certified", "log_free_certified",
                 "ramification_excluded_certified",
                 "recurrence_theorem_certified", "omega_zero_excluded"):
        _check(cf[flag] is True, f"claim flag {flag} not True")
    for flag in ("general_l_certified", "finite_flux_boundary_class_certified"):
        _check(cf[flag] is False, f"claim flag {flag} not False")

    print("BH2C_METRIC_ALL_ORDERS: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
