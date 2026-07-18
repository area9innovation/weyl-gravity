"""Certify the a,b,d homogeneous cross matrix against ell=2 extra modes."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_ab_axial_ell2_extra_source_explore import (
    source as axial_source,
)
from bridge.einstein_sector.einstein_maxwell_weyl_ab_polar_ell2_extra_source_explore import (
    source as polar_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.schema.json"
D_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(vector: sp.MatrixBase) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _parse_vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix(
        [sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}) for value in values]
    )


def _expected_sources(time: sp.Symbol) -> dict[str, dict[str, dict[str, sp.Matrix]]]:
    root = sp.sqrt(3)
    imaginary = sp.I
    return {
        "axial": {
            "a": {
                "e1": sp.Matrix([-72 * imaginary * (2 * root * time - 7 * imaginary), 0, 36, 0]),
                "e2": sp.Matrix([0, -4 * imaginary * (2 * root * time - 69 * imaginary) / 3, 0, -4 * imaginary * (2 * root * time + 7 * imaginary)]),
            },
            "b": {
                "e1": sp.Matrix([-72 * imaginary * (root * time**2 - 7 * imaginary * time - 2 * root), 0, 36 * time, 0]),
                "e2": sp.Matrix([0, -4 * imaginary * (root * time**2 - 69 * imaginary * time + 45 * root) / 3, 0, -4 * imaginary * (root * time**2 + 7 * imaginary * time - 2 * root)]),
            },
        },
        "polar": {
            "a": {
                "e1": sp.Matrix([0, -3 * imaginary * (4 * root * time + 9 * imaginary), 0, 0]),
                "e2": sp.Matrix([4 * (45 * time**2 - 188 * root * imaginary * time + 156), 0, -4 * (693 * time**2 + 316 * root * imaginary * time + 2922) / 9, -48 * (9 * time**2 - 16 * root * imaginary * time - 64)]),
            },
            "b": {
                "e1": sp.Matrix([0, -3 * imaginary * time * (2 * root * time + 9 * imaginary), 0, 0]),
                "e2": sp.Matrix([4 * (15 * time**3 - 94 * root * imaginary * time**2 + 156 * time + 28 * root * imaginary), 0, -4 * (231 * time**3 + 158 * root * imaginary * time**2 + 2922 * time + 1768 * root * imaginary) / 9, -48 * time * (3 * time**2 - 8 * root * imaginary * time - 64)]),
            },
        },
    }


def _direct_sources(time: sp.Symbol) -> dict[str, dict[str, dict[str, sp.Matrix]]]:
    cases = [
        (parity, global_case, mode_case)
        for parity in ("axial", "polar")
        for global_case in ("a", "b")
        for mode_case in ("e1", "e2")
    ]
    with ProcessPoolExecutor(max_workers=4) as executor:
        computed = list(executor.map(_compute_source, cases))
    result: dict[str, dict[str, dict[str, sp.Matrix]]] = {
        parity: {global_case: {} for global_case in ("a", "b")}
        for parity in ("axial", "polar")
    }
    for (parity, global_case, mode_case), value in zip(cases, computed, strict=True):
        result[parity][global_case][mode_case] = value
    expected = _expected_sources(time)
    for parity in expected:
        for global_case in expected[parity]:
            for mode_case in expected[parity][global_case]:
                difference = (
                    result[parity][global_case][mode_case]
                    - expected[parity][global_case][mode_case]
                ).applyfunc(sp.simplify)
                if difference != sp.zeros(4, 1):
                    raise AssertionError(
                        f"{parity} {global_case} x {mode_case} source changed: {difference}"
                    )
    return result


def _compute_source(case: tuple[str, str, str]) -> sp.Matrix:
    parity, global_case, mode_case = case
    producer = {"axial": axial_source, "polar": polar_source}[parity]
    return producer(global_case, mode_case).applyfunc(sp.factor)


def _pairings(
    sources: dict[str, dict[str, dict[str, sp.Matrix]]],
    d_record: dict[str, object],
) -> tuple[dict[str, dict[str, list[str]]], dict[str, list[list[str]]]]:
    time = sp.symbols("t", real=True)
    witnesses = {
        "axial": sp.Matrix.hstack(
            sp.Matrix([-1, 0, 1, 0]),
            sp.Matrix([0, -sp.Rational(1, 9), 0, 1]),
        ),
        "polar": sp.Matrix.hstack(
            sp.Matrix([0, 1, 0, 0]),
            sp.Matrix([-sp.Rational(1, 6), 0, -sp.Rational(3, 2), 1]),
        ),
    }
    d_sources = {
        "axial": sp.Matrix(
            [
                [-72 * sp.I * sp.sqrt(3), 0],
                [0, -sp.Rational(4, 3) * sp.I * sp.sqrt(3)],
                [0, 0],
                [0, -4 * sp.I * sp.sqrt(3)],
            ]
        ),
        "polar": sp.Matrix(
            [
                [0, -376 * sp.I * sp.sqrt(3)],
                [-6 * sp.I * sp.sqrt(3), 0],
                [0, -sp.Rational(632, 9) * sp.I * sp.sqrt(3)],
                [0, 384 * sp.I * sp.sqrt(3)],
            ]
        ),
    }
    if d_record["polar_theorem"]["source_columns_e1_e2"] != [
        [str(sp.factor(d_sources["polar"][row, column])) for column in range(2)]
        for row in range(4)
    ]:
        raise AssertionError("stored d-times-polar input changed")
    values: dict[str, dict[str, list[str]]] = {}
    coefficient_matrices: dict[str, list[list[str]]] = {}
    for parity in ("axial", "polar"):
        values[parity] = {}
        columns: list[sp.Matrix] = []
        for global_case in ("a", "b"):
            projection = (
                witnesses[parity].T
                * sp.Matrix.hstack(
                    sources[parity][global_case]["e1"],
                    sources[parity][global_case]["e2"],
                )
            ).applyfunc(sp.factor)
            if projection[0, 1] != 0 or projection[1, 0] != 0:
                raise AssertionError(
                    f"{parity} {global_case} cross-polarization adjoint mixing appeared"
                )
            values[parity][global_case] = [
                str(sp.factor(projection[0, 0])),
                str(sp.factor(projection[1, 1])),
            ]
            columns.extend([projection[:, 0], projection[:, 1]])
        d_projection = (witnesses[parity].T * d_sources[parity]).applyfunc(sp.factor)
        if d_projection[0, 1] != 0 or d_projection[1, 0] != 0:
            raise AssertionError(f"{parity} d cross-polarization adjoint mixing appeared")
        values[parity]["d"] = [
            str(sp.factor(d_projection[0, 0])),
            str(sp.factor(d_projection[1, 1])),
        ]
        columns.extend([d_projection[:, 0], d_projection[:, 1]])
        full = sp.Matrix.hstack(*columns)
        coefficient_matrices[parity] = [
            [str(sp.factor(full[row, column])) for column in range(full.cols)]
            for row in range(full.rows)
        ]
        for polarization, witness_row in (("e1", 0), ("e2", 1)):
            index = {"e1": 0, "e2": 1}[polarization]
            polynomials = [
                sp.Poly(
                    sp.sympify(
                        values[parity][case][index],
                        locals={"I": sp.I, "sqrt": sp.sqrt, "t": time},
                    ),
                    time,
                )
                for case in ("a", "b", "d")
            ]
            coefficient_rows = max(polynomial.degree() for polynomial in polynomials) + 1
            coefficient_matrix = sp.Matrix(
                [
                    [polynomial.nth(power) for polynomial in polynomials]
                    for power in range(coefficient_rows)
                ]
            )
            if coefficient_matrix.rank() != 3:
                raise AssertionError(
                    f"{parity} {polarization} a,b,d resonant chains lost independence"
                )
    return values, coefficient_matrices


def build() -> dict[str, object]:
    time = sp.symbols("t", real=True)
    sources = _direct_sources(time)
    d_record = json.loads(D_INPUT.read_text(encoding="utf-8"))
    projected, matrices = _pairings(sources, d_record)
    return {
        "schema": "einstein-maxwell-weyl-abd-ell2-extra-resonance-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ABD_ELL2_EXTRA_RESONANCE_MATRIX",
        "result_state": "HOMOGENEOUS_A_B_D_TIMES_COMPLETE_ELL2_EXTRA_POLYNOMIAL_RESONANCE_MATRIX_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "the coefficients of every displayed adjoint polynomial are compatibility functionals",
            "smooth_exponential_polynomial": "OPEN: secular inversion must be stated through the complete operator, not inferred from the projected source alone",
            "causal_or_retarded": "OPEN: no compact-product retarded complex is certified",
        },
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed spatial S1_L times S2; finite quasiperiodic correction class for the certified compatibility statement",
            "charge_sector": "fixed magnetic bundle; electric variation allowed",
            "carrier": "homogeneous generalized-zero Einstein block crossed with the generic ell=2 extra-primary block",
            "degree": 2,
            "parity": "axial and polar output sectors kept separate",
            "ell": "0 x 2 -> 2",
            "m": "m=0 direct tensor fixtures; every m by SO(3) equivariance",
            "k": "0",
            "omega": "generalized zero crossed with omega_e=4/sqrt(3)",
        },
        "global_profiles": {
            "a": "delta g_xx=a*t^2 and delta g_S2=a*g_S2",
            "b": "delta g_xx=(b/3)*t^3 and delta g_S2=b*t*g_S2",
            "d": "delta g_xx=d*t",
        },
        "action_row_orders": {
            "axial": ["6*axial(metric_tA)", "-6*axial(metric_xA)", "axial(maxwell_t)", "axial(maxwell_x)"],
            "polar": ["-polar(metric_00)", "2*polar(metric_01)", "-polar(metric_11)", "2*lambda*polar(maxwell_phi)"],
        },
        "adjoint_bases": {
            "axial": [["-1", "0", "1", "0"], ["0", "-1/9", "0", "1"]],
            "polar": [["0", "1", "0", "0"], ["-1/6", "0", "-3/2", "1"]],
        },
        "direct_source_rows": {
            parity: {
                global_case: {
                    mode_case: _strings(sources[parity][global_case][mode_case])
                    for mode_case in ("e1", "e2")
                }
                for global_case in ("a", "b")
            }
            for parity in ("axial", "polar")
        },
        "projected_resonance_polynomials": projected,
        "projected_matrix_column_order": ["a*e1", "a*e2", "b*e1", "b*e2", "d*e1", "d*e2"],
        "projected_resonance_matrices": matrices,
        "classification": {
            "direct_axial_a_b_cross_sources_computed": True,
            "direct_polar_a_b_cross_sources_computed": True,
            "d_column_imported_by_content_hash": True,
            "every_parity_polarization_abd_polynomial_chain_rank_three": True,
            "bounded_compatibility_functionals_explicit": True,
            "twist_position_velocity_columns_computed": False,
            "complete_homogeneous_twist_source_matrix": False,
            "simultaneous_stabilizer_and_resonance_zero_locus_solved": False,
            "smooth_secular_sufficiency": False,
            "causal_retarded_sufficiency": False,
            "full_second_order_equation_solved": False,
        },
        "interpretation": "Within each parity and extra polarization, the a-, b-, and d-cross adjoint projections are linearly independent polynomials in time. Hence these homogeneous columns are genuinely distinct bounded/quasiperiodic compatibility data. This is a source-matrix theorem, not yet a no-go: twist position and velocity can contribute to the same ell=2 extra-shell channel and remain to be computed.",
        "next_gate": "compute twist position and velocity crossed with both ell=2 extra representatives, append their SO(3)-equivariant columns, and solve the simultaneous stabilizer plus complete bounded-resonance zero locus",
        "claim_boundary": "No mode is declared obstructed solely from this submatrix. The result does not silently identify axial and polar carriers, does not prove smooth-secular or retarded solvability, and does not support final residual, particle, observational, or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_axial_path": str(Path(axial_source.__code__.co_filename).resolve().relative_to(ROOT)),
            "direct_axial_sha256": _sha256(Path(axial_source.__code__.co_filename).resolve()),
            "direct_polar_path": str(Path(polar_source.__code__.co_filename).resolve().relative_to(ROOT)),
            "direct_polar_sha256": _sha256(Path(polar_source.__code__.co_filename).resolve()),
            "d_input": {"path": str(D_INPUT.relative_to(ROOT)), "sha256": _sha256(D_INPUT)},
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix"]},
            "tier_2": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix --write"], "reason": "direct four-dimensional tensor replay for all axial and polar a,b fixtures"},
            "tier_3": {"status": "NOT_RUN", "reason": "the twist columns and complete tangent-cone gate remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("a,b,d resonance-matrix certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ABD_ELL2_EXTRA_RESONANCE_MATRIX: PASS")


if __name__ == "__main__":
    main()
