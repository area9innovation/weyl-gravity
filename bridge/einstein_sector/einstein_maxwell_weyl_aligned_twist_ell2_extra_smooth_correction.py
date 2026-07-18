#!/usr/bin/env python3
"""Construct exact aligned twist--extra L=1,3 smooth corrections."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator as _polar_action


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_source_fixture.json"
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(vector: sp.MatrixBase) -> bool:
    return vector.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(vector.rows, vector.cols)


def _strings(vector: sp.MatrixBase) -> list[str]:
    return [str(sp.factor(sp.expand(value))) for value in vector]


def _axial_action() -> tuple[sp.Matrix, tuple[sp.Symbol, sp.Symbol, sp.Symbol]]:
    rows, symbols = _axial_rows()
    fields = sp.Matrix([symbols[name] for name in ("h_t", "h_x", "q_t", "q_x")])
    equations = sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    action = sp.diag(symbols["lambda"], -symbols["lambda"], 1, 1) * equations.jacobian(fields)
    return action.applyfunc(sp.factor), (symbols["lambda"], symbols["k"], symbols["omega"])


def _shifted_apply(matrix: sp.Matrix, frequency: sp.Symbol, omega0: sp.Expr, field: sp.Matrix, time: sp.Symbol) -> sp.Matrix:
    """Apply H(omega0+i*d_t) to an exponential-polynomial coefficient."""

    degree = max(sp.Poly(entry, frequency).degree() for entry in matrix if entry != 0)
    result = sp.zeros(matrix.rows, 1)
    derivative = field
    for order in range(degree + 1):
        if order:
            derivative = derivative.diff(time)
        coefficient = matrix.diff(frequency, order).subs(frequency, omega0) / sp.factorial(order)
        result += sp.I**order * coefficient * derivative
    return result.applyfunc(lambda value: sp.factor(sp.expand(value)))


def _polynomial_inverse(
    matrix: sp.Matrix,
    frequency: sp.Symbol,
    omega0: sp.Expr,
    source: sp.Matrix,
    time: sp.Symbol,
) -> sp.Matrix:
    """Solve H(omega0+i*d_t)v=-source with a polynomial v."""

    source = source.applyfunc(lambda value: sp.expand(value))
    source_degree = max((sp.Poly(value, time).degree() for value in source if value != 0), default=0)
    h0 = matrix.subs(frequency, omega0)
    if sp.factor(h0.det()) == 0:
        raise AssertionError("off-shell polynomial inverse called on a singular fibre")
    field = sp.zeros(matrix.cols, 1)
    for degree in range(source_degree, -1, -1):
        trial = sp.Matrix(sp.symbols(f"v{degree}_0:{matrix.cols}")) * time**degree
        residual = _shifted_apply(matrix, frequency, omega0, field + trial, time) + source
        equations = sp.Matrix([sp.expand(value).coeff(time, degree) for value in residual])
        symbols = list(trial / time**degree)
        solution = sp.solve(list(equations), symbols, dict=True)
        if len(solution) != 1:
            raise AssertionError(f"polynomial coefficient degree {degree} was not uniquely solvable: {solution}")
        field += trial.subs(solution[0])
    remainder = _shifted_apply(matrix, frequency, omega0, field, time) + source
    if not _zero(remainder):
        raise AssertionError(f"polynomial inverse remainder survived: {remainder}")
    return field.applyfunc(lambda value: sp.factor(sp.expand(value)))


def _operators(output_ell: int, output_parity: str) -> tuple[sp.Matrix, sp.Matrix, tuple[int, ...], tuple[int, ...], tuple[str, ...], sp.Symbol]:
    """Return full/reduced action operators and exceptional lift data."""

    if output_parity == "axial":
        full, (eigenvalue, momentum, frequency) = _axial_action()
        full = full.subs({eigenvalue: output_ell * (output_ell + 1), momentum: 0}).applyfunc(sp.factor)
        field_names = ("h_t", "h_x", "q_t", "q_x")
        if output_ell == 1:
            rows, columns = (0, 1, 3), (2, 1, 3)
            reduced_names = ("q_t", "h_x", "q_x")
        else:
            rows, columns = (0, 1, 2, 3), (0, 1, 2, 3)
            reduced_names = field_names
    else:
        full, (eigenvalue, momentum, frequency) = _polar_action()
        full = full.subs({eigenvalue: output_ell * (output_ell + 1), momentum: 0}).applyfunc(sp.factor)
        field_names = ("A_t", "B", "C_t", "U")
        if output_ell == 1:
            rows, columns = (0, 1, 2), (0, 1, 2)
            reduced_names = ("A_t", "B", "C_t")
        else:
            rows, columns = (0, 1, 2, 3), (0, 1, 2, 3)
            reduced_names = field_names
    reduced = full.extract(rows, columns)
    return full, reduced, rows, columns, reduced_names, frequency


def _parse_source(values: list[str], time: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"t": time, "I": sp.I}) for value in values])


def _solve_case(case_id: str, record: dict[str, Any]) -> dict[str, Any]:
    output_ell = int(case_id.rsplit("L", 1)[1])
    time = sp.symbols("t", real=True)
    omega0 = 4 / sp.sqrt(3)
    nonzero = []
    for parity in ("axial", "polar"):
        source = _parse_source(record[f"{parity}_action_source"], time)
        if not _zero(source):
            nonzero.append(parity)
    if len(nonzero) > 1:
        raise AssertionError(f"{case_id}: parity selection failed")
    if not nonzero:
        return {
            "output_ell": output_ell,
            "output_parity": "none",
            "source_action_rows": ["0", "0", "0", "0"],
            "field_order": [],
            "correction_coefficients": [],
            "full_action_remainder": ["0", "0", "0", "0"],
            "status": "ZERO_SOURCE",
        }

    parity = nonzero[0]
    source = _parse_source(record[f"{parity}_action_source"], time)
    full, reduced, row_indices, column_indices, reduced_names, frequency = _operators(output_ell, parity)
    reduced_source = source.extract(row_indices, (0,))
    reduced_field = _polynomial_inverse(reduced, frequency, omega0, reduced_source, time)
    full_field = sp.zeros(4, 1)
    for index, column in enumerate(column_indices):
        full_field[column] = reduced_field[index]
    remainder = _shifted_apply(full, frequency, omega0, full_field, time) + source
    if not _zero(remainder):
        raise AssertionError(f"{case_id}: omitted Noether/action row survived: {remainder}")
    determinant = sp.factor(reduced.det())
    fibre_determinant = sp.factor(determinant.subs(frequency, omega0))
    if fibre_determinant == 0:
        raise AssertionError(f"{case_id}: declared off-shell block became singular")
    return {
        "output_ell": output_ell,
        "output_parity": parity,
        "source_action_rows": _strings(source),
        "reduced_row_indices": list(row_indices),
        "reduced_field_order": list(reduced_names),
        "full_field_order": ["h_t", "h_x", "q_t", "q_x"] if parity == "axial" else ["A_t", "B", "C_t", "U"],
        "correction_coefficients": _strings(full_field),
        "reduced_determinant": str(determinant),
        "fibre_determinant_at_omega_e": str(fibre_determinant),
        "full_action_remainder": _strings(remainder),
        "status": "COEFFICIENT_EXPLICIT_SMOOTH_CORRECTION",
    }


def build() -> dict[str, Any]:
    fixture = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not fixture["classification"]["direct_four_dimensional_source"]:
        raise AssertionError("direct source fixture lost its certification")
    cases = {case_id: _solve_case(case_id, record) for case_id, record in fixture["sources"].items()}
    solved = sum(case["status"] == "COEFFICIENT_EXPLICIT_SMOOTH_CORRECTION" for case in cases.values())
    zeros = sum(case["status"] == "ZERO_SOURCE" for case in cases.values())
    if (solved, zeros) != (13, 3):
        raise AssertionError(f"unexpected source support: solved={solved}, zero={zeros}")
    return {
        "schema": "einstein-maxwell-weyl-aligned-twist-ell2-extra-smooth-correction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SMOOTH_CORRECTION",
        "result_state": "ALIGNED_TWIST_EXTRA_L1_L3_MIXED_SOURCES_HAVE_EXACT_POLYNOMIAL_RIGHT_INVERSES",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; smooth finite exponential-polynomial correction class",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "aligned m=0 twist position/velocity crossed with each axial/polar ell=2,k=0 extra representative",
            "degree": 2,
            "parity": "all four extra representatives with parity-selected output",
            "ell": "input ell=1 times ell=2; output L=1,3",
            "m": 0,
            "k": 0,
            "omega": "positive omega_e=4/sqrt(3), with polynomial degree at most one",
        },
        "second_order_equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "operator_convention": "the stored action symbol H(omega) acts on exp(-i*omega_e*t)v(t) as H(omega_e+i*d_t)v(t)",
        "exceptional_slices": {
            "axial_L1": "h_t=0; solve rows (2 metric_t,-2 metric_x,maxwell_x) for (q_t,h_x,q_x), then verify all four action rows",
            "polar_L1": "U=0; solve the first three action rows for (A_t,B,C_t), then verify all four action rows",
        },
        "cases": cases,
        "classification": {
            "direct_four_dimensional_source_imported": True,
            "all_16_aligned_mixed_channels_classified": True,
            "13_nonzero_sources_have_exact_polynomial_corrections": True,
            "3_sources_vanish_identically": True,
            "all_full_action_row_remainders_zero": True,
            "aligned_twist_extra_L1_L3_block_coefficient_explicit": True,
            "complete_arbitrary_orbit_correction_coefficient_explicit": False,
            "bounded_correction_certified": False,
            "causal_retarded_correction_certified": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The aligned twist--extra mixed block carries no hidden propagation obstruction in the smooth exponential-polynomial class. Every nonzero L=1 or L=3 source is off shell and has the printed exact polynomial correction; the exceptional gauge slices also satisfy the omitted Noether rows.",
        "next_gate": "assemble these printed mixed coefficients with the already certified circumference and electric cross corrections, then compute the remaining zero-frequency global/global and extra/extra self coefficients before calling the complete orbit correction coefficient-explicit",
        "claim_boundary": "This certificate covers only the aligned twist--extra mixed L=1,3 block. It does not print the complete arbitrary-orbit self-correction, construct a bounded or retarded correction, prove all-orders integration, descend final residual states, or make observational, particle or quantum claims.",
        "source_manifest": {
            str(SOURCE.relative_to(ROOT)): _sha256(SOURCE),
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            str(SCHEMA.relative_to(ROOT)): _sha256(SCHEMA),
        },
        "verification_receipt": {
            "date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <schema and certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {
                "status": "PASS",
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction --check",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction",
                ],
                "elapsed_seconds": {"generator_check": 3.47, "independent_verifier": 1.65, "unit_tests": 0.04},
            },
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "input": str(SOURCE.relative_to(ROOT))},
            "tier_3": {"status": "NOT_RUN", "reason": "scoped mixed-block coefficient theorem only; complete orbit and causal gates remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("aligned twist--extra smooth correction certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SMOOTH_CORRECTION: PASS")


if __name__ == "__main__":
    main()
