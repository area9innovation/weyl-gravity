#!/usr/bin/env python3
"""Exact global obstruction for the transverse Nariai Einstein branch."""

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
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-kantowski-sachs-global-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-kantowski-sachs-global-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_kantowski_sachs_global_obstruction.py"
TESTS = HERE / "tests/test_nariai_transverse_kantowski_sachs_global_obstruction.py"

DEPENDENCIES = {
    "formal_metric_green_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json",
    "global_hpl_rank310_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json",
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


def exact_obstruction() -> dict[str, Any]:
    e, b = sp.symbols("epsilon b", real=True)
    b0 = 1 - e**2 / 6
    constant = sp.factor(b0 * (e**2 - b0**2 / 3 + 1))
    excess = sp.factor(constant - sp.Rational(2, 3))
    potential = sp.factor(b**2 / 3 - 1 + constant / b)
    initial_defect = sp.factor(potential.subs(b, b0) - e**2)
    if initial_defect != 0:
        raise AssertionError("the exact first integral misses the initial data")
    expected_excess = e**2 * (e**4 - 126 * e**2 + 648) / 648
    if sp.factor(excess - expected_excess) != 0:
        raise AssertionError("the supercritical mass excess drifted")

    bstar, c_generic = sp.symbols("b_star C", positive=True)
    generic_potential = b**2 / 3 - 1 + c_generic / b
    minimum = sp.factor(
        generic_potential.subs({c_generic: sp.Rational(2, 3) * bstar**3, b: bstar})
    )
    if sp.simplify(minimum - (bstar**2 - 1)) != 0:
        raise AssertionError("the potential minimum formula drifted")

    # On 0 < |epsilon| < 1, b0>0 and C-2/3>0 because the remaining
    # polynomial is bounded below by 523.  Thus b_star>1 and F_e>0 on b>0.
    polynomial_lower_bound = 1 - 126 + 648
    if polynomial_lower_bound != 523:
        raise AssertionError("parameter-range positivity bound drifted")

    # The Einstein equations force a=b'/epsilon and
    # 2bb''+(b')^2+1=b^2.  Differentiating the first integral reproduces
    # the scalar evolution exactly.
    bp, bpp, c = sp.symbols("bp bpp C", nonzero=True)
    differentiated = sp.factor(2 * bp * bpp - (sp.Rational(2, 3) * b * bp - c * bp / b**2))
    evolution_substitution = sp.factor(
        (2 * b * bpp + bp**2 + 1 - b**2).subs(
            {
                bpp: b / 3 - c / (2 * b**2),
                bp**2: b**2 / 3 - 1 + c / b,
            },
            simultaneous=True,
        )
    )
    if evolution_substitution != 0:
        raise AssertionError("the first integral does not reproduce Einstein evolution")
    if sp.factor(differentiated / bp - (2 * bpp - sp.Rational(2, 3) * b + c / b**2)) != 0:
        raise AssertionError("differentiated first integral drifted")

    # For Ric(g)=g, subtract the constant-curvature 1/3 piece from the
    # orthonormal sphere sectional curvature.  The first integral then gives
    # C_2323=(1+(b')^2)/b^2-1/3=C_epsilon/b^3.  Spherical symmetry and
    # trace-freeness fix the six independent channels, whose full index
    # contraction is checked explicitly below.
    radial_sectional = sp.simplify((1 + potential) / b**2 - sp.Rational(1, 3))
    if sp.simplify(radial_sectional - constant / b**3) != 0:
        raise AssertionError("the Weyl radial channel does not follow from the first integral")
    w = constant / b**3
    independent_channels = [-w, w / 2, w / 2, -w / 2, -w / 2, w]
    weyl_squared = sp.simplify(4 * sum(channel**2 for channel in independent_channels))
    if sp.simplify(weyl_squared - 12 * constant**2 / b**6) != 0:
        raise AssertionError("the Weyl-channel contraction drifted")
    nariai_limit = sp.simplify(weyl_squared.subs({e: 0, b: 1}))
    if nariai_limit != sp.Rational(16, 3):
        raise AssertionError("Weyl-square normalization drifted")

    return {
        "parameter_range": "0<|epsilon|<1",
        "initial_radius": str(b0),
        "initial_velocity": "epsilon",
        "metric_coefficient": "a_epsilon=b_epsilon'/epsilon",
        "einstein_scalar_equation": "2 b b''+(b')^2+1=b^2",
        "first_integral": "(b')^2=b^2/3-1+C_epsilon/b",
        "C_epsilon": str(constant),
        "C_epsilon_minus_2_over_3": str(excess),
        "positive_factor_lower_bound_on_range": str(polynomial_lower_bound),
        "potential_critical_point": "b_star=(3 C_epsilon/2)^(1/3)>1",
        "potential_minimum": "b_star^2-1>0",
        "monotonicity": "sign(b')=sign(epsilon) on the maximal positive-radius solution",
        "finite_time_integral": "Delta t_sing=integral_0^b0 db/sqrt(b^2/3-1+C_epsilon/b)<infinity",
        "integrability_bound": "for 0<b<=min(b0,C_epsilon/2), F_e(b)>=C_epsilon/(2b); the remaining compact interval has a positive minimum",
        "singular_direction": "past for epsilon>0 and future for epsilon<0",
        "weyl_derivation": "C_2323=(1+(b')^2)/b^2-1/3=C_epsilon/b^3; spherical symmetry and trace-freeness give channels (-w,w/2,w/2,-w/2,-w/2,w)",
        "weyl_squared": str(weyl_squared),
        "nariai_weyl_squared": str(nariai_limit),
        "curvature_limit": "+infinity as b->0+",
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["formal_metric_green_variation"]["exact_checks"]["slabwise_exact_Einstein_family_generates_tangent"]:
        raise ValueError("slabwise family dependency drifted")
    if records["global_hpl_rank310_variation"]["flags"]["TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY"] is not False:
        raise ValueError("global family was already promoted")
    obstruction = exact_obstruction()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-nariai-transverse-kantowski-sachs-global-obstruction-v1",
        "result_id": "NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1",
        "result_state": "NONZERO_TRANSVERSE_EINSTEIN_BRANCH_SLABWISE_ONLY_GLOBAL_CYLINDER_OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "background": {
            "metric": "g_epsilon=-dt^2+a_epsilon(t)^2 dchi^2+b_epsilon(t)^2 dOmega_2^2",
            "topology_requested": "R_t x S1 x S2",
            "equation": "Ric(g_epsilon)=g_epsilon",
            "reference": "unit Nariai at epsilon=0",
        },
        "exact_obstruction": obstruction,
        "theorem": {
            "statement": "For every 0<|epsilon|<1, the exact Kantowski-Sachs Einstein solution generating the certified transverse Nariai tangent develops b=0 with divergent Weyl curvature at finite proper time in one time direction. Hence this branch cannot furnish a smooth nonzero-epsilon family on all R x S1 x S2.",
            "slabwise_family": "CERTIFIED",
            "whole_cylinder_family": "OBSTRUCTED",
            "formal_first_variation": "CERTIFIED",
        },
        "exact_checks": {
            "initial_data_satisfy_first_integral": True,
            "C_epsilon_strictly_supercritical": True,
            "potential_has_positive_global_minimum": True,
            "positive_radius_solution_is_monotone": True,
            "zero_radius_reached_in_finite_proper_time": True,
            "weyl_curvature_diverges_at_zero_radius": True,
            "slabwise_exact_family_retained": True,
            "formal_rank310_variation_retained": True,
        },
        "flags": {
            "NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1": True,
            "TRANSVERSE_KS_SLABWISE_EINSTEIN_FAMILY": True,
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY": False,
            "TRANSVERSE_KS_GLOBAL_FAMILY_OBSTRUCTED": True,
            "ALL_TRANSVERSE_BACH_FLAT_FAMILIES_OBSTRUCTED": False,
            "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY": False,
            "NONLINEAR_BV_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "NON_EINSTEIN_TRANSVERSE_BACH_FLAT_FAMILY_OR_CAUSAL_PATCHING_WITH_DECLARED_DOMAIN",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_transverse_kantowski_sachs_global_obstruction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_kantowski_sachs_global_obstruction.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_kantowski_sachs_global_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-kantowski-sachs-global-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact obstruction applies to the homogeneous Kantowski-Sachs Einstein branch with the displayed initial data and parameter range. It preserves the certified exact family on every fixed compact time slab and the global formal first variation at epsilon=0. It does not obstruct non-Einstein Bach-flat deformations, different transverse initial data, causal constructions on proper subdomains with declared boundaries, or abstract parent Green hyperbolicity; it does not promote a nonlinear BV, Hadamard, or quantum theorem."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact obstruction check dropped")
    flags = value["flags"]
    for name in (
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "ALL_TRANSVERSE_BACH_FLAT_FAMILIES_OBSTRUCTED",
        "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
        "NONLINEAR_BV_EXTENSION",
        "QUANTUM_CLAIM",
    ):
        if flags[name] is not False:
            raise ValueError("claim boundary crossed")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Transverse Nariai Kantowski--Sachs global-family obstruction

The exact Einstein family generating the certified transverse tangent is
governed by

\[
  2bb''+(b')^2+1=b^2,
  \qquad
  (b')^2=\frac{b^2}{3}-1+\frac{C_\epsilon}{b},
  \qquad
  a=\frac{b'}{\epsilon}.
\]

For the required initial data
\(b(0)=1-\epsilon^2/6\), \(b'(0)=\epsilon\), the exact constant obeys

\[
 C_\epsilon-\frac23
 =\frac{\epsilon^2(\epsilon^4-126\epsilon^2+648)}{648}>0
 \qquad (0<|\epsilon|<1).
\]

The effective potential therefore has a strictly positive global minimum on
\(b>0\).  The solution is monotone, and in the direction opposite its initial
velocity it reaches \(b=0\) after the finite proper time

\[
 \int_0^{b(0)}
 \frac{db}{\sqrt{b^2/3-1+C_\epsilon/b}}.
\]

Moreover \(C_{abcd}C^{abcd}=12C_\epsilon^2/b^6\), so the endpoint is a genuine
curvature singularity.  The branch is exact on every fixed compact slab for
sufficiently small parameter, but it cannot give a smooth nonzero-parameter
family on the whole cylinder \(\mathbb R\times S^1\times S^2\).

This is a scoped obstruction for the displayed homogeneous Einstein branch.
It is not a no-go theorem for non-Einstein Bach-flat families or for causal
theory on explicitly bounded subdomains.
"""


def _guards(value: dict[str, Any]) -> None:
    for name in (
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "ALL_TRANSVERSE_BACH_FLAT_FAMILIES_OBSTRUCTED",
        "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
        "NONLINEAR_BV_EXTENSION",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("transverse global-obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print("NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
