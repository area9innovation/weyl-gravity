#!/usr/bin/env python3
"""Certify the nonlinear placement of the relative Taub-zero pullback."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-derived-taub-zero-pullback-preflight.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-derived-taub-zero-pullback-preflight-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_derived_taub_zero_pullback_preflight.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_derived_taub_zero_pullback_preflight.py"
DEPENDENCIES = {
    "charge_koszul": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
    "current_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "current_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
    "cotangent_316": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json",
    "block_q2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1.json",
    "complete_five_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    deps = {name: _load(path) for name, path in DEPENDENCIES.items()}
    koszul = deps["charge_koszul"]
    current = deps["current_q2"]
    if koszul["derived_zero_locus"]["quadratic_origin"] != "mu_rel(0)=0 and d mu_rel|_0=0":
        raise AssertionError("moment-map Taylor order changed")
    if koszul["derived_zero_locus"]["plain_linear_subcomplex_restriction_valid"]:
        raise AssertionError("quadratic zero locus was linearized incorrectly")
    if not current["classification"]["current_interface_q1q2_identity_exact"]:
        raise AssertionError("support-local current q2 changed")
    if not deps["complete_five_charge_q2"]["classification"]["complete_standard_source_five_charge_q2"]:
        raise AssertionError("complete standard charge q2 changed")
    return {
        "schema": "pure-weyl-relative-derived-taub-zero-pullback-preflight-v1",
        "result_id": RESULT_ID,
        "result_state": "DERIVED_TAUB_ZERO_PULLBACK_IS_QUADRATIC_AND_RELATIVE_FACTORIZATION_REMAINS_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": deps["cotangent_316"]["scope"],
        "dependencies": {name: _artifact(path, deps[name]) for name, path in DEPENDENCIES.items()},
        "taylor_placement": {
            "relative_moment_map_constant_term": 0,
            "relative_moment_map_linear_term": 0,
            "first_nonzero_term": "mu_rel^(2)(u,v)=B_rel(u,v)",
            "unary_tangent_complex_unchanged": True,
            "plain_linear_taub_zero_subcomplex_valid": False,
            "canonical_local_equation": "d_H B_X + j_X(u,u)/2 = 0 for X=H,P_x,J_1,J_2,J_3",
            "canonical_new_operation": "q2_current(u,v)=j_X(u,v)/2",
            "nonzero_unary_cross_incidence_is_part_of_canonical_pullback": False,
        },
        "pullback_carrier": {
            "local_current_resolution_rows": 160,
            "cyclic_unary_ambient_rows": 316,
            "current_q1q2_interface_rows": 188,
            "support_local": True,
            "uses_mode_projector": False,
            "global_koszul_descent_generators": 5,
            "constant_u1_is_taub_generator": False,
        },
        "relative_morphism_gate": {
            "full_domain_block_diagonal_q2_obstructed": True,
            "required_derived_factorization": "[Delta2]=A o mu_rel in target q1 cohomology on the declared source-pair module",
            "equivalent_kernel_condition": "ker(mu_rel) subset ker([Delta2])",
            "charge_projection_alone_proves_factorization": False,
            "complete_standard_charge_basis_available": True,
            "off_shell_local_current_representatives_available": True,
            "factorization_matrix_computed": False,
            "support_local_lift_of_factorization_computed": False,
        },
        "classification": {
            "canonical_quadratic_derived_pullback_architecture_certified": True,
            "linear_tangent_must_be_restricted": False,
            "unary_cross_incidence_required_by_taub_zero_condition": False,
            "relative_q2_on_derived_pullback_certified": False,
            "factorization_obstructed": False,
            "causal_or_quantum_claim": False,
        },
        "next_gate": "COMPUTE_THE_REDUCED_MODE_FACTORIZATION_OF_DELTA2_THROUGH_THE_COMPLETE_FIVE_CHARGE_MAP_THEN_TEST_A_SUPPORT_LOCAL_CURRENT_LIFT",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_derived_taub_zero_pullback_preflight --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_derived_taub_zero_pullback_preflight",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_derived_taub_zero_pullback_preflight"
            ],
        },
        "claim_boundary": "This preflight certifies the categorical and Taylor-degree placement of the relative Taub-zero derived source. Because the relative moment map has vanishing constant and linear terms, the canonical derived pullback preserves the full unary tangent complex and enters through the support-local current q2 equation d_H B+j/2=0. It therefore rejects a plain linear Taub-zero subcomplex and does not require a nonzero unary cross-incidence merely to impose the quadratic constraint. It does not yet prove that the relative arity-two obstruction class factors through the complete five-charge map, construct the support-local lift of such a factorization, repair the relative f2, compare the cotangent and action pairings, or establish causal, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Derived Taub-zero pullback preflight

The relative moment map begins quadratically:

\[
\mu_{\rm rel}(0)=0,\qquad d\mu_{\rm rel}|_0=0,
\qquad \mu_{\rm rel}^{(2)}(u,v)=B_{\rm rel}(u,v).
\]

Consequently its derived zero locus is not a linear subcomplex and does not
remove any first-order tangent.  The canonical local presentation keeps the
full unary complex and adds, at arity two,

\[
d_HB_X+\frac12j_X(u,u)=0,
\qquad X=H,P_x,J_1,J_2,J_3.
\]

The 160-row de Rham/cotangent carrier and its 188-row physical-current q2
interface already realize this equation support-locally.  The 316-row odd
cotangent carrier supplies the cyclic unary ambient complex.

What is not yet proved is the relative morphism on this derived source.  Its
finite algebraic gate is

\[
[\Delta_2]=A\circ\mu_{\rm rel},
\]

or equivalently

\[
\ker\mu_{\rm rel}\subseteq\ker[\Delta_2].
\]

The complete five-charge operation and local current representatives are
available, but their factorization through the full obstruction module has
not been computed.  That factorization must be settled before seeking its
support-local lift.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("linear_tangent_must_be_restricted", "unary_cross_incidence_required_by_taub_zero_condition", "relative_q2_on_derived_pullback_certified", "factorization_obstructed", "causal_or_quantum_claim"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value)); REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("derived pullback outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
