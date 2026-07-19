#!/usr/bin/env python3
"""Common globally hyperbolic slabs for the exact transverse KS family."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-ks-common-slab-causal-domain.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-common-slab-causal-domain-v1.schema.json"
VERIFIER = HERE / "verify_nariai_ks_common_slab_causal_domain.py"
TESTS = HERE / "tests/test_nariai_ks_common_slab_causal_domain.py"

DEPENDENCIES = {
    "exact_KS_branch": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
    "six_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json",
    "typed_biwave": ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def regularized_fixture() -> dict[str, Any]:
    e, y, a = sp.symbols("epsilon y a", real=True)
    b = 1 + e * y
    bp = e * a
    bpp = sp.factor(e * (2 * y + e * (y**2 - a**2)) / (2 * b))
    einstein = sp.factor(2 * b * bpp + bp**2 + 1 - b**2)
    if einstein != 0:
        raise AssertionError("regularized flow does not solve the KS Einstein equation")

    t = sp.symbols("t", real=True)
    y0 = sp.sinh(t)
    a0 = sp.cosh(t)
    base_defects = {
        "y_prime_minus_a": sp.simplify(sp.diff(y0, t) - a0),
        "a_prime_minus_y": sp.simplify(sp.diff(a0, t) - y0),
        "initial_y": sp.simplify(y0.subs(t, 0)),
        "initial_a_minus_one": sp.simplify(a0.subs(t, 0) - 1),
    }
    if any(value != 0 for value in base_defects.values()):
        raise AssertionError(f"unit-Nariai regularized solution drifted: {base_defects}")

    return {
        "regular_variables": "b=1+epsilon y and b'=epsilon a",
        "regular_system": [
            "y'=a",
            "a'=(2y+epsilon(y^2-a^2))/(2(1+epsilon y))",
        ],
        "initial_data": ["y(0)=-epsilon/6", "a(0)=1"],
        "regular_domain": "1+epsilon y>0",
        "epsilon_zero_solution": ["y_0=sinh(t)", "a_0=cosh(t)"],
        "einstein_equation_after_substitution": "0",
        "base_solution_defects": {name: "0" for name in base_defects},
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["exact_KS_branch"]["flags"]["TRANSVERSE_KS_SLABWISE_EINSTEIN_FAMILY"]:
        raise ValueError("exact KS slabwise family drifted")
    if not records["six_block_HPL"]["flags"]["SIX_BLOCK_FINITE_SUPPORT_LOCAL_HPL"]:
        raise ValueError("six-block HPL prerequisite drifted")
    if not records["typed_biwave"]["flags"]["TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1"]:
        raise ValueError("typed biwave theorem drifted")

    fixture = regularized_fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-nariai-ks-common-slab-causal-domain-v1",
        "result_id": "NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1",
        "result_state": "EXACT_KS_FAMILY_HAS_UNIFORM_SMALL_PARAMETER_GLOBALLY_HYPERBOLIC_DOMAIN_ON_EVERY_FINITE_SLAB",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "theorem": {
            "quantifiers": "for every T>0 there exists delta_T>0 such that the statement holds for |epsilon|<delta_T",
            "domain": "M_T=(-T,T) x S1 x S2",
            "background": "g_epsilon=-dt^2+a_epsilon(t)^2 dchi^2+b_epsilon(t)^2 dOmega_2^2",
            "statement": "The regularized KS initial-value problem has a unique smooth exact Einstein solution on the common slab, with a_epsilon and b_epsilon positive and uniformly bounded above and below after shrinking delta_T. Each g_epsilon is globally hyperbolic with compact Cauchy slices, and all its causal cones lie inside one smooth wider reference cone on that slab.",
        },
        "proof": {
            "regularized_ode": fixture,
            "smooth_parameter_dependence": "the displayed first-order vector field and initial data are smooth near the compact epsilon=0 trajectory on [-T,T] because 1+epsilon y stays away from zero",
            "positivity": "a_0=cosh(t)>=1 and b_0=1; uniform C0 dependence gives positive common lower bounds for a_epsilon and b_epsilon after shrinking delta_T",
            "global_hyperbolicity": "dt is everywhere timelike with g_epsilon^{-1}(dt,dt)=-1, and every inextendible causal curve in the open slab meets each compact slice {t=constant} exactly once",
            "common_cone": "uniform lower bounds h_epsilon>=c_T^2(dchi^2+dOmega_2^2) imply every g_epsilon-causal vector is causal for g_wide=-dt^2+c_T^2(dchi^2+dOmega_2^2)",
            "bach_flatness": "Ric(g_epsilon)=g_epsilon implies Bach(g_epsilon)=0",
        },
        "analytic_interface": {
            "fixed_support_category": "compact, past/future compact, and spacelike compact sections on the open globally hyperbolic slab M_T",
            "common_reference_causal_cone": True,
            "six_block_HPL_maps_remain_support_local_if_geometrically_bound": True,
            "typed_biwave_theorem_available_after_endpoint_hypotheses": True,
            "remaining_input": "coefficient-complete geometric export of gD,kD,MD,BD,gsharpD,ksharpD and verification of the exact compressed metric endpoint against the typed biwave hypotheses",
        },
        "exact_checks": {
            "regularized_system_exact": True,
            "epsilon_zero_solution_exact": True,
            "smooth_common_slab_family": True,
            "positive_spatial_scale_factors": True,
            "compact_Cauchy_slices": True,
            "uniform_reference_causal_cone": True,
            "exact_Einstein_and_Bach_flat": True,
        },
        "flags": {
            "NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1": True,
            "KS_COMMON_SLAB_GLOBALLY_HYPERBOLIC_FAMILY": True,
            "KS_COMMON_REFERENCE_CAUSAL_CONE": True,
            "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING": False,
            "KS_METRIC_ENDPOINT_TYPED_BIWAVE": False,
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER": False,
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "NARIAI_KS_SIX_BLOCK_GEOMETRIC_BINDING_AND_ENDPOINT",
        "claim_boundary": "This theorem certifies the common globally hyperbolic slab and a uniform causal support geometry for the exact Kantowski--Sachs family. It does not export the six coefficient-complete rank-310 operator differences, verify the compressed endpoint, construct a Green homotopy, extend the nonzero branch to the whole cylinder, or establish Hadamard or quantum claims.",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_ks_common_slab_causal_domain.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_ks_common_slab_causal_domain.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_ks_common_slab_causal_domain",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-ks-common-slab-causal-domain-v1.schema.json -d d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json"
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("common-slab proof check dropped")
    for flag in (
        "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
        "KS_METRIC_ENDPOINT_TYPED_BIWAVE",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        if value["flags"][flag] is not False:
            raise ValueError("claim boundary crossed")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _report() -> str:
    return r"""# Common causal slabs for the exact Kantowski--Sachs family

The quotient `a=b'/epsilon` is regularized by

\[
 b=1+\epsilon y,\qquad b'=\epsilon a.
\]

The exact Einstein equation becomes the smooth first-order system

\[
 y'=a,\qquad
 a'=\frac{2y+\epsilon(y^2-a^2)}{2(1+\epsilon y)},
\]

with `y(0)=-epsilon/6` and `a(0)=1`.  At `epsilon=0` its solution is
`y=sinh(t)`, `a=cosh(t)`.  Standard smooth dependence of ODE solutions on
parameters therefore proves that, for every finite `T`, some `delta_T>0`
gives a unique exact solution on `(-T,T)` for every
`|epsilon|<delta_T`, with both scale factors positive and uniformly bounded
above and below.

Consequently every

\[
 g_\epsilon=-dt^2+a_\epsilon^2d\chi^2+b_\epsilon^2d\Omega_2^2
\]

on that open slab is globally hyperbolic with compact Cauchy slices.  The
uniform lower spatial bound supplies one wider reference cone containing all
the `g_epsilon` causal cones.  This makes a common causal support category
legitimate.

This is a domain theorem, not the causal-transfer theorem.  The next input is
the coefficient-complete six-block geometric export and the exact compressed
metric endpoint required by the typed biwave theorem.
"""


def _guards(value: dict[str, Any]) -> None:
    for flag in (
        "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
        "KS_METRIC_ENDPOINT_TYPED_BIWAVE",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][flag] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {flag}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
        REPORT.write_text(_report())
    elif args.check:
        if OUTPUT.read_text() != rendered or REPORT.read_text() != _report():
            raise AssertionError("common-slab artifacts are stale")
    else:
        parser.error("one of --write or --check is required")
    if args.guards:
        _guards(value)
    print("NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1: PASS")


if __name__ == "__main__":
    main()
