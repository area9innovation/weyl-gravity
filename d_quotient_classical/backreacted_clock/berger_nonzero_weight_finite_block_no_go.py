#!/usr/bin/env python3
"""Exact nonzero-D-weight finite-mode closure obstruction for Berger q2.

The stationary rational Berger action defines a quadratic square map
``Q(v)=q2(v,v)`` from the three homogeneous field directions to their three
equation rows.  This script proves that ``Q(v)=0`` only for ``v=0`` and then
uses cyclic weight duality to rule out every finite, nondegenerate,
q2-closed mode block containing a nonzero-weight field mode.

This is a REDUCED-MODE obstruction.  It is not a support-local q2 theorem and
it is not an arity-two Cartan obstruction: the proposed finite block fails
closure before the Cartan equation is posed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
Q2_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-nonzero-D-weight-finite-block-no-go.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exact_action_cubic() -> tuple[sp.Expr, tuple[sp.Symbol, ...], list[sp.Expr]]:
    u, lapse, rho, omega = sp.symbols("u N rho omega", real=True)
    q0 = sp.Rational(9, 40)
    c0 = sp.sqrt(q0)
    c = c0 * (1 + u)
    alpha_b = sp.Rational(5)
    quartic = sp.Rational(119, 480)
    scalar_curvature = (4 - c**2) / 2
    weyl_squared = 4 * (1 - c**2) ** 2 / 3
    lagrangian = sp.factor(
        lapse * c * (
            alpha_b * weyl_squared / 8
            + rho**2 * omega**2 / (2 * lapse**2)
            - scalar_curvature * rho**2 / 12
            - quartic * rho**4 / 4
        ) / c0
    )
    fields = (u, lapse, rho)
    fixture = {u: 0, lapse: 1, rho: 1, omega: sp.Rational(3, 4)}
    if any(sp.factor(sp.diff(lagrangian, field).subs(fixture)) for field in fields):
        raise AssertionError("Berger rational fixture lost stationarity")
    x = sp.symbols("x_u x_N x_rho", real=True)
    square_map = []
    for output in range(3):
        value = sp.S.Zero
        for left in range(3):
            for right in range(3):
                coefficient = sp.diff(
                    lagrangian, fields[output], fields[left], fields[right]
                ).subs(fixture)
                value += coefficient * x[left] * x[right]
        square_map.append(sp.factor(value))
    return lagrangian, x, square_map


def _homogeneous_monomials(variables: tuple[sp.Symbol, ...], degree: int) -> list[sp.Expr]:
    x, y, z = variables
    return [x**a * y**b * z ** (degree - a - b) for a in range(degree + 1) for b in range(degree - a + 1)]


def _ideal_multipliers(
    generators: list[sp.Expr], target: sp.Expr, variables: tuple[sp.Symbol, ...]
) -> list[sp.Expr]:
    degree = sp.Poly(target, *variables).total_degree()
    monomials = _homogeneous_monomials(variables, degree - 2)
    unknowns = sp.symbols(f"a0:{len(generators) * len(monomials)}")
    expression = sum(
        unknowns[i * len(monomials) + j] * monomial * generators[i]
        for i in range(len(generators))
        for j, monomial in enumerate(monomials)
    ) - target
    equations = sp.Poly(sp.expand(expression), *variables).coeffs()
    solution_set = sp.linsolve(equations, unknowns)
    if solution_set is sp.EmptySet:
        raise AssertionError("ideal membership solve failed")
    solution = next(iter(solution_set))
    free = set().union(*(value.free_symbols for value in solution)) & set(unknowns)
    normalized = [sp.factor(value.subs({symbol: 0 for symbol in free})) for value in solution]
    multipliers = [
        sp.factor(sum(normalized[i * len(monomials) + j] * monomial for j, monomial in enumerate(monomials)))
        for i in range(len(generators))
    ]
    if sp.expand(sum(multiplier * generator for multiplier, generator in zip(multipliers, generators)) - target) != 0:
        raise AssertionError("ideal membership certificate is invalid")
    return multipliers


def _matrix_rows(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


@dataclass(frozen=True)
class BergerNonzeroWeightFiniteBlockNoGo:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerNonzeroWeightFiniteBlockNoGo":
        lagrangian, variables, square_map = _exact_action_cubic()
        u, lapse, rho = variables

        # A short real anisotropy certificate.  The displayed combination is
        # a positive-definite quadratic form by Sylvester's criterion.
        real_combination = sp.factor(-2 * square_map[0] - 2 * square_map[1] + square_map[2])
        gram = sp.hessian(real_combination, variables) / 2
        minors = [sp.factor(gram[:size, :size].det()) for size in range(1, 4)]
        if any(minor <= 0 for minor in minors):
            raise AssertionError("real square-map anisotropy certificate is not positive")

        # Complex anisotropy certificate.  These three ideal elements imply
        # rho=0, then u=0 and N=0, over every characteristic-zero field.
        targets = [
            rho**4,
            (8019 * u**2 + 22992 * u * rho + 9690 * lapse * rho + 21829 * rho**2) / 8019,
            -(2550 * u * rho - 2673 * lapse**2 + 5160 * lapse * rho + 2723 * rho**2) / 2673,
        ]
        multipliers = [_ideal_multipliers(square_map, target, variables) for target in targets]

        # The smallest symmetric candidate W={-1,0,+1} already leaks.
        seed = {u: 1, lapse: 0, rho: 0}
        leakage = [sp.factor(component.subs(seed)) for component in square_map]
        expected_leakage = [sp.Rational(27, 80), -sp.Rational(27, 20), sp.Rational(9, 80)]
        if leakage != expected_leakage:
            raise AssertionError("first nonzero-weight leakage vector drifted")
        witness = [sp.Rational(80, 27), sp.S.Zero, sp.S.Zero]
        if sum(left * right for left, right in zip(witness, leakage)) != 1:
            raise AssertionError("first leakage witness is not normalized")
        forced_weights = [1]
        for _ in range(7):
            forced_weights.append(-2 * forced_weights[-1])

        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-nonzero-D-weight-finite-block-no-go-v1",
            "result_id": "BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO",
            "setting_id": "compact_positive_berger_clock_rational_fixture_homogeneous_weight_lift",
            "claim_status": "CERTIFIED_REDUCED_MODE_CLOSURE_OBSTRUCTION",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "dependency_ref": {
                "result_id": "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK",
                "path": "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json",
                "sha256": _sha256(Q2_CERTIFICATE),
            },
            "action_derivation": {
                "normalized_reduced_lagrangian": str(lagrangian),
                "variables": [str(variable) for variable in variables],
                "q2_square_rule": "Q_i(x)=d_i d_j d_k L_bar x_j x_k at the rational fixture",
                "residual_fit_used": False,
            },
            "D_weight_convention": {
                "field_action": "D x_w = w x_w",
                "equation_action": "D E_w = w E_w",
                "q2_additivity": "q2(x_w,y_v) lies in E_(w+v)",
                "cyclic_pairing": "<x_w,E_v> can be nonzero only when w+v=0",
            },
            "square_map": {
                "input_basis": ["u", "N", "rho"],
                "output_basis": ["E_u", "E_N", "E_rho"],
                "components": [str(component) for component in square_map],
            },
            "real_anisotropy_certificate": {
                "combination_coefficients": ["-2", "-2", "1"],
                "positive_quadratic": str(real_combination),
                "gram_matrix": _matrix_rows(gram),
                "leading_principal_minors": [str(value) for value in minors],
                "conclusion": "Q(x)=0 over R implies x=0",
            },
            "complex_anisotropy_certificate": {
                "targets": [str(target) for target in targets],
                "multipliers_by_target": [[str(value) for value in row] for row in multipliers],
                "identities": ["sum_i multiplier[target,i] Q_i = target" for _ in targets],
                "triangular_conclusion": "rho^4=0; then target_u=u^2=0 and target_N=N^2=0",
                "conclusion": "Q(x)=0 over C implies x=0",
            },
            "first_failed_block": {
                "declared_field_weights": [-1, 0, 1],
                "input": ["u_(+1)", "u_(+1)"],
                "missing_output_weight": 2,
                "leakage_output_basis": ["E_u_(+2)", "E_N_(+2)", "E_rho_(+2)"],
                "leakage_vector": [str(value) for value in leakage],
                "first_failed_row": "E_u_(+2)",
                "first_failed_coefficient": "27/80",
                "normalized_dual_witness": [str(value) for value in witness],
                "witness_evaluation": "1",
            },
            "finite_block_no_go": {
                "hypotheses": [
                    "the block contains a nonzero field mode x_w with w!=0",
                    "the block is closed under the action-derived q2",
                    "the cyclic field-equation pairing restricted to the block is nondegenerate",
                    "the block contains only finitely many D weights",
                ],
                "forced_weight_recurrence": "w_(n+1)=-2 w_n",
                "sample_forced_weights": forced_weights,
                "proof": "anisotropy gives q2(x_w,x_w)!=0 in E_(2w); nondegenerate cyclic pairing forces a nonzero field at -2w; iteration gives unbounded |w_n|",
                "conclusion": "no such finite nonzero-weight cyclic q2-closed block exists",
            },
            "exact_checks": {
                "action_stationary": True,
                "q2_derived_from_action": True,
                "all_coefficients_rational": True,
                "real_positive_combination_exact": True,
                "real_sylvester_minors_positive": True,
                "complex_ideal_memberships_exact": True,
                "complex_square_map_anisotropic": True,
                "first_leakage_exact": True,
                "normalized_leakage_witness_exact": True,
                "forced_weight_sequence_unbounded": True,
            },
            "flags": {
                "BERGER_Q2_SQUARE_MAP_ANISOTROPIC": True,
                "BERGER_NONZERO_WEIGHT_FINITE_BLOCK_NO_GO": True,
                "NONZERO_WEIGHT_MODE_CLOSURE_OBSTRUCTION": True,
                "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION": False,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "ND2_PHYSICAL_EXECUTION_AUTHORIZED": False,
            },
            "next_gate": "INFINITE_WEIGHT_COMPLETION_OR_FULL_SUPPORT_LOCAL_Q2",
            "claim_boundary": "This exact theorem rules out finite pairing-nondegenerate homogeneous nonzero-D-weight blocks closed under the action-derived Berger q2. It does not rule out the infinite all-weight complex, does not construct the full support-local q2, and is not a Cartan-cohomology obstruction.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("nonzero-weight no-go exact check dropped")
        flags = self.payload["flags"]
        for key in (
            "BERGER_Q2_SQUARE_MAP_ANISOTROPIC",
            "BERGER_NONZERO_WEIGHT_FINITE_BLOCK_NO_GO",
            "NONZERO_WEIGHT_MODE_CLOSURE_OBSTRUCTION",
        ):
            if flags[key] is not True:
                raise AssertionError(f"no-go flag dropped: {key}")
        for key in (
            "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION",
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "ND2_PHYSICAL_EXECUTION_AUTHORIZED",
        ):
            if flags[key] is not False:
                raise AssertionError(f"no-go scope crossed: {key}")
        if self.payload["first_failed_block"]["witness_evaluation"] != "1":
            raise AssertionError("normalized leakage witness drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Nonzero-weight finite Berger block: exact closure no-go

The action-derived cubic Taylor tensor on the rational stationary Berger
fixture defines a square map

\[
Q:\mathbb C^3\longrightarrow\mathbb C^3,
\qquad Q(x)=q_2(x,x).
\]

It has no nonzero square-zero direction.  Over the reals, the short
certificate is the positive-definite quadratic combination

\[
-2Q_u-2Q_N+Q_\rho>0,
\]

whose three leading principal minors are

\[
\frac{171}{80},\qquad \frac{44649}{6400},\qquad
\frac{38549}{15360}.
\]

Exact ideal-membership identities additionally prove the same conclusion
over the complex numbers.

Consequently no finite, pairing-nondegenerate homogeneous mode block that
contains a nonzero field mode of weight \(w\ne0\) can be closed under this
\(q_2\).  Squaring the mode produces a nonzero equation at weight \(2w\);
cyclic nondegeneracy forces a field at weight \(-2w\), and iteration forces

\[
w,-2w,4w,-8w,\ldots.
\]

For the smallest attempted block with weights \((-1,0,+1)\), the first
failure is

\[
q_2(u_{+1},u_{+1})=
\frac{27}{80}E_{u,+2}-\frac{27}{20}E_{N,+2}
+\frac9{80}E_{\rho,+2}.
\]

The normalized dual leakage witness is \((80/27,0,0)\).

This is a `REDUCED-MODE` closure obstruction, not a full support-local
theorem and not a nontrivial Cartan-cohomology obstruction.  The correct next
object is the infinite all-weight completion or the full local field complex.
"""


def _write(result: BergerNonzeroWeightFiniteBlockNoGo) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text(), encoding="utf-8")
    REPORT_PATH.write_text(result.report_text(), encoding="utf-8")


def _check(result: BergerNonzeroWeightFiniteBlockNoGo) -> None:
    if CERTIFICATE_PATH.read_text(encoding="utf-8") != result.certificate_text():
        raise AssertionError("nonzero-weight no-go certificate drifted")
    if REPORT_PATH.read_text(encoding="utf-8") != result.report_text():
        raise AssertionError("nonzero-weight no-go report drifted")


def _guards(result: BergerNonzeroWeightFiniteBlockNoGo) -> None:
    for name, path, value in (
        ("promote support local", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("promote Cartan obstruction", ("flags", "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"), True),
        ("promote physical ND2", ("flags", "ND2_PHYSICAL_EXECUTION_AUTHORIZED"), True),
        ("erase witness", ("first_failed_block", "witness_evaluation"), "0"),
    ):
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerNonzeroWeightFiniteBlockNoGo(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerNonzeroWeightFiniteBlockNoGo.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    print("BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
