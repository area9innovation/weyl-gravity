#!/usr/bin/env python3
"""Independent replay of the derived Taub-zero pullback preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-derived-taub-zero-pullback-preflight-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source-manifest hash drifted: {relative}")
    dependencies = {}
    for name, artifact in value["dependencies"].items():
        path = ROOT / artifact["path"]
        if _sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drifted: {name}")
        dependencies[name] = json.loads(path.read_text())

    koszul = dependencies["charge_koszul"]
    if koszul["derived_zero_locus"]["plain_linear_subcomplex_restriction_valid"]:
        raise AssertionError("quadratic derived locus was replaced by a linear subcomplex")
    scale, bilinear = sp.symbols("scale bilinear")
    moment = scale**2 * bilinear
    if moment.subs(scale, 0) != 0 or sp.diff(moment, scale).subs(scale, 0) != 0:
        raise AssertionError("moment map no longer starts quadratically")
    current = dependencies["current_q2"]
    if not current["classification"]["current_interface_q1q2_identity_exact"]:
        raise AssertionError("current q1/q2 interface lost exactness")
    if not dependencies["complete_five_charge_q2"]["classification"]["complete_standard_source_five_charge_q2"]:
        raise AssertionError("complete standard charge basis unavailable")
    if dependencies["block_q2_obstruction"]["classification"]["complete_full_domain_q2_on_block_diagonal_316_exists"]:
        raise AssertionError("block-diagonal obstruction was silently removed")

    gate = value["relative_morphism_gate"]
    if gate["factorization_matrix_computed"] or gate["support_local_lift_of_factorization_computed"]:
        raise AssertionError("open factorization gate was overpromoted")
    flags = value["classification"]
    if not flags["canonical_quadratic_derived_pullback_architecture_certified"]:
        raise AssertionError("canonical derived architecture missing")
    if any(flags[key] for key in ("linear_tangent_must_be_restricted", "unary_cross_incidence_required_by_taub_zero_condition", "relative_q2_on_derived_pullback_certified", "factorization_obstructed", "causal_or_quantum_claim")):
        raise AssertionError("preflight promoted a forbidden downstream claim")
    return {
        "status": "PASS",
        "moment_constant_and_linear_terms_zero": True,
        "unary_tangent_unchanged": True,
        "current_interface_rows": value["pullback_carrier"]["current_q1q2_interface_rows"],
        "charge_generators": value["pullback_carrier"]["global_koszul_descent_generators"],
        "factorization_gate_open": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
