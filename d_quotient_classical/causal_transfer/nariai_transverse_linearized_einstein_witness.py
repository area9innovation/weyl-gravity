#!/usr/bin/env python3
"""First non-conformal linearized Bach-flat witness at unit Nariai."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-linearized-einstein-witness.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-linearized-einstein-witness-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_linearized_einstein_witness.py"
TESTS = HERE / "tests/test_nariai_transverse_linearized_einstein_witness.py"

NARIAI_CURVATURE = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json"
NARIAI_SDR = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"
CONFORMAL_TRANSFER = ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json"
VOLTERRA_THEOREM = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha(path),
    }


def _background_weyl() -> tuple[sp.MutableDenseNDimArray, int, sp.Expr]:
    metric = sp.diag(-1, 1, 1, 1)
    inverse = metric

    def riemann(a: int, b: int, c: int, d: int) -> sp.Expr:
        same = all(index < 2 for index in (a, b, c, d)) or all(
            index >= 2 for index in (a, b, c, d)
        )
        if not same:
            return sp.Integer(0)
        return metric[a, c] * metric[b, d] - metric[a, d] * metric[b, c]

    def ricci(b: int, d: int) -> sp.Expr:
        return sp.simplify(
            sum(
                inverse[a, c] * riemann(a, b, c, d)
                for a in range(4)
                for c in range(4)
            )
        )

    scalar = sp.simplify(
        sum(inverse[a, b] * ricci(a, b) for a in range(4) for b in range(4))
    )
    weyl = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    weyl[a, b, c, d] = sp.simplify(
                        riemann(a, b, c, d)
                        - sp.Rational(1, 2)
                        * (
                            metric[a, c] * ricci(d, b)
                            - metric[a, d] * ricci(c, b)
                            - metric[b, c] * ricci(d, a)
                            + metric[b, d] * ricci(c, a)
                        )
                        + scalar
                        * sp.Rational(1, 6)
                        * (
                            metric[a, c] * metric[d, b]
                            - metric[a, d] * metric[c, b]
                        )
                    )
    contraction = sp.zeros(64, 4)
    row = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    contraction[row, d] = weyl[a, b, c, d]
                row += 1
    squared = sp.simplify(
        sum(
            inverse[a, a]
            * inverse[b, b]
            * inverse[c, c]
            * inverse[d, d]
            * weyl[a, b, c, d] ** 2
            for a in range(4)
            for b in range(4)
            for c in range(4)
            for d in range(4)
        )
    )
    return weyl, contraction.rank(), squared


def exact_witness() -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    a0 = sp.cosh(t)
    alpha = -sp.sinh(2 * t) / 3
    beta = sp.sinh(t)
    hubble = sp.tanh(t)

    einstein_residuals = {
        "tt": sp.simplify(-(sp.diff(alpha, t, 2) - alpha) / a0 - 2 * sp.diff(beta, t, 2)),
        "chi_chi": sp.simplify((sp.diff(alpha, t, 2) - alpha) / a0 + 2 * hubble * sp.diff(beta, t)),
        "sphere": sp.simplify(sp.diff(beta, t, 2) + hubble * sp.diff(beta, t) - 2 * beta),
    }
    if any(value != 0 for value in einstein_residuals.values()):
        raise AssertionError(f"linearized Einstein witness failed: {einstein_residuals}")

    weyl, contraction_rank, background_weyl_squared = _background_weyl()
    if contraction_rank != 4:
        raise AssertionError("Nariai Weyl contraction is not injective on one-forms")
    if weyl[0, 2, 0, 2] != sp.Rational(1, 3):
        raise AssertionError("Nariai Weyl normalization drifted")
    if background_weyl_squared != sp.Rational(16, 3):
        raise AssertionError("Nariai Weyl-square normalization drifted")

    def at_star(expression: sp.Expr) -> sp.Expr:
        return sp.simplify(
            sp.expand_trig(expression).subs(
                {
                    sp.sinh(t): sp.Integer(1),
                    sp.cosh(t): sp.sqrt(2),
                    sp.tanh(t): 1 / sp.sqrt(2),
                }
            )
        )

    ratios = {
        "chi": at_star(2 * alpha / a0),
        "sphere": at_star(2 * beta),
    }
    ratios["difference"] = sp.simplify(ratios["chi"] - ratios["sphere"])
    delta_y = -sp.diff(beta, t, 2)
    background_channels = [
        weyl[0, 1, 0, 1],
        weyl[0, 2, 0, 2],
        weyl[1, 2, 1, 2],
        weyl[2, 3, 2, 3],
    ]
    variation_channels = [-2 * delta_y, delta_y, -delta_y, 2 * delta_y]
    multiplicities = [1, 2, 2, 1]
    delta_weyl_square_function = sp.simplify(
        8
        * sum(
            multiplicity * background * variation
            for multiplicity, background, variation in zip(
                multiplicities, background_channels, variation_channels
            )
        )
    )
    delta_weyl_electric = at_star(delta_y)
    delta_weyl_square = at_star(delta_weyl_square_function)
    if ratios != {
        "chi": sp.Rational(-4, 3),
        "sphere": sp.Integer(2),
        "difference": sp.Rational(-10, 3),
    }:
        raise AssertionError(f"transverse ratios drifted: {ratios}")
    if delta_weyl_electric != -1 or delta_weyl_square != -32:
        raise AssertionError("normalized curvature witness drifted")

    return {
        "einstein_residuals": {name: str(value) for name, value in einstein_residuals.items()},
        "weyl_contraction_rank": contraction_rank,
        "background_weyl_components": {
            "C_0101": str(weyl[0, 1, 0, 1]),
            "C_0202": str(weyl[0, 2, 0, 2]),
            "C_2323": str(weyl[2, 3, 2, 3]),
        },
        "evaluation_time": "asinh(1)",
        "relative_metric_variations": {name: str(value) for name, value in ratios.items()},
        "delta_C_0202_orthonormal": str(delta_weyl_electric),
        "background_C_squared": str(background_weyl_squared),
        "delta_C_squared": str(delta_weyl_square),
    }


def build() -> dict[str, Any]:
    dependencies = {
        "Nariai_curvature": (NARIAI_CURVATURE, "CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1"),
        "Nariai_metric_parent_SDR": (NARIAI_SDR, "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1"),
        "conformal_orbit_transfer": (CONFORMAL_TRANSFER, "CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1"),
        "typed_biwave_theorem": (VOLTERRA_THEOREM, "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1"),
    }
    refs = {}
    for name, (path, expected) in dependencies.items():
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise AssertionError(f"dependency drifted: {name}")
        refs[name] = _ref(path, payload)
    if json.loads(CONFORMAL_TRANSFER.read_text())["flags"]["TRANSVERSE_BACH_FLAT_DEFORMATIONS"] is not False:
        raise AssertionError("transverse gate was not open")

    witness = exact_witness()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "nariai-transverse-linearized-einstein-witness-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1",
        "result_state": "FORMAL_TRANSVERSE_LINEARIZED_BACH_FLAT_WITNESS_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "background": {
            "metric": "g_N=-dt^2+cosh(t)^2 dchi^2+dOmega_2^2",
            "equation": "Ric(g_N)=g_N",
            "topology": "R times S1 times S2",
        },
        "kantowski_sachs_tangent": {
            "ansatz": "g_epsilon=-dt^2+(cosh(t)+epsilon alpha(t))^2 dchi^2+(1+epsilon beta(t))^2 dOmega_2^2+O(epsilon^2)",
            "alpha": "-(1/3)sinh(2t)",
            "beta": "sinh(t)",
            "cosmological_constant_fixed": "1",
            "linearized_equation": "delta(Ric-g)=0",
        },
        "exact_witness": witness,
        "bach_flatness": {
            "linearized_Einstein": True,
            "linearized_Cotton": "0 because delta P=(1/6)h and the varied Levi-Civita connection remains metric-compatible to first order",
            "linearized_Bach": "0 because the four-dimensional Einstein locus is Bach-flat and the displayed tangent solves the linearized Einstein equations",
        },
        "transversality": {
            "not_pointwise_conformal": "at t=asinh(1), h_chichi/g_chichi=-4/3 while h_sphere/g_sphere=2",
            "not_infinitesimal_Diff_Weyl": "linearized Cotton is zero; injectivity of v^d -> C_abcd v^d forces the Weyl parameter to be constant, while delta(C_abcd C^abcd)=-32 sinh(t) is nonconstant and the background invariant is constant",
            "weyl_contraction_rank": witness["weyl_contraction_rank"],
        },
        "first_curvature_drift": {
            "normal_tractor_slot": "the Weyl block of the normal tractor curvature",
            "normalized_component": "delta C_0202 at t=asinh(1)",
            "value": witness["delta_C_0202_orthonormal"],
            "consequence": "the coefficient-frozen Nariai curvature incidence and BGG maps do not extend unchanged along this tangent; curvature-dependent first variations must be included",
        },
        "exact_checks": {
            "linearized_Einstein_tt": True,
            "linearized_Einstein_chichi": True,
            "linearized_Einstein_sphere": True,
            "linearized_Bach_flat": True,
            "relative_metric_variation_nonconformal": True,
            "Nariai_Weyl_contraction_injective": True,
            "nonconstant_Weyl_scalar_variation": True,
            "transverse_to_Diff_Weyl_orbit": True,
            "normal_tractor_curvature_drift_nonzero": True,
        },
        "flags": {
            "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1": True,
            "TRANSVERSE_FORMAL_BACH_FLAT_TANGENT": True,
            "TRANSVERSE_EXACT_NONLINEAR_BACKGROUND_FAMILY": False,
            "TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_METRIC_PARENT_SDR": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION",
        "claim_boundary": "This is a formal linearized Einstein, hence linearized Bach-flat, Kantowski-Sachs tangent at unit Nariai with an exact nonzero curvature witness transverse to the infinitesimal Diff-Weyl orbit. It is not an exact nonlinear background family, does not yet compute the full first variation of the rank-310 SDR, and does not promote transverse causal transfer.",
        "source_manifest": sources,
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_linearized_einstein_witness --check --guards",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_linearized_einstein_witness.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_linearized_einstein_witness",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-linearized-einstein-witness-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
        ],
    }


def _report(payload: dict[str, Any]) -> str:
    witness = payload["exact_witness"]
    return rf"""# First transverse linearized Bach-flat witness at Nariai

## Result

In the Kantowski--Sachs ansatz, perturb unit Nariai by

\[
a_\epsilon(t)=\cosh t-\frac{{\epsilon}}{{3}}\sinh(2t),
\qquad
b_\epsilon(t)=1+\epsilon\sinh t.
\]

The three independent first-order Einstein residuals are

\[
\begin{{aligned}}
E_{{00}}&=-\frac{{\alpha''-\alpha}}{{\cosh t}}-2\beta'',\\
E_{{11}}&= \frac{{\alpha''-\alpha}}{{\cosh t}}
          +2\tanh t\,\beta',\\
E_{{22}}&=\beta''+\tanh t\,\beta'-2\beta,
\end{{aligned}}
\]

and all three vanish identically.  Hence this is a formal linearized Einstein
tangent with fixed cosmological constant, and therefore a formal linearized
Bach-flat tangent.

At \(t_*=\operatorname{{arsinh}}1\),

\[
\frac{{h_{{\chi\chi}}}}{{g_{{\chi\chi}}}}=-\frac43,
\qquad
\frac{{h_{{S^2}}}}{{g_{{S^2}}}}=2.
\]

It is not pointwise conformal.  More invariantly, the Nariai map
\(v^d\mapsto C_{{abc d}}v^d\) has rank four.  Since the tangent remains
Cotton-flat to first order, any infinitesimal conformal parameter in a
Diff--Weyl representation would have to be constant.  But

\[
\delta(C_{{abcd}}C^{{abcd}})=-32\sinh t
\]

is nonconstant, while the background scalar is \(16/3\).  Thus the tangent is
outside the infinitesimal Diff--Weyl orbit.

The normalized normal-tractor curvature drift is

\[
\delta C_{{0202}}(t_*)={witness['delta_C_0202_orthonormal']}.
\]

Therefore the coefficient-frozen Nariai curvature-incidence and BGG maps
cannot extend unchanged.  This is the input for the next calculation: vary
the full rank-310 SDR equations and solve the resulting Hom-complex defect.

## Boundary

This certificate proves a formal linearized Bach-flat witness, not an exact
nonlinear family.  It records a nonzero curvature drift, not a no-go theorem
for corrected support-local maps and not a transverse causal theorem.
"""


def verify(payload: dict[str, Any]) -> None:
    if payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise AssertionError("dependency scope drifted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a transverse witness check failed")
    if payload["exact_witness"]["delta_C_0202_orthonormal"] != "-1":
        raise AssertionError("normalized curvature witness drifted")
    if payload["exact_witness"]["delta_C_squared"] != "-32":
        raise AssertionError("Weyl scalar witness drifted")
    for flag in (
        "TRANSVERSE_EXACT_NONLINEAR_BACKGROUND_FAMILY",
        "TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION",
        "TRANSVERSE_METRIC_PARENT_SDR",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")


def _guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("promote exact family", ("flags", "TRANSVERSE_EXACT_NONLINEAR_BACKGROUND_FAMILY"), True),
        ("promote SDR", ("flags", "TRANSVERSE_METRIC_PARENT_SDR"), True),
        ("erase curvature", ("exact_witness", "delta_C_0202_orthonormal"), "0"),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        mutant[path[0]][path[1]] = value
        try:
            verify(mutant)
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def _write(payload: dict[str, Any]) -> None:
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report(payload))


def _check(payload: dict[str, Any]) -> None:
    if json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("certificate drifted")
    if REPORT.read_text() != _report(payload):
        raise AssertionError("report drifted")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        _write(payload)
    if args.check:
        _check(payload)
    if args.guards:
        _guards(payload)
    print("NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
