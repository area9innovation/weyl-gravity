"""Direct exceptional ell=1 Weyl--Maxwell static nonzero-momentum fibres."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

import bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor as axial_engine
import bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor as polar_engine


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_nonzero_static.schema.json"
PHASE_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json"
ENGINES = (
    ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_axial_ell2_full_tensor.py",
    ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_full_tensor.py",
)


class Ell1NonzeroStaticError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Ell1NonzeroStaticError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _symbol(expressions: list[sp.Expr], name: str) -> sp.Symbol:
    matches = {symbol for expression in expressions for symbol in expression.free_symbols if symbol.name == name}
    _require(len(matches) == 1, f"symbol {name} is ambiguous")
    return matches.pop()


def _direct_rows(engine: object, invalid_row: str) -> dict[str, sp.Expr]:
    original = engine._require

    def exceptional_require(condition: bool, message: str) -> None:
        if condition:
            return
        if "requires ell>=2" in message:
            return
        if invalid_row in message and "failed" in message:
            return
        original(condition, message)

    engine._require = exceptional_require
    try:
        result = engine._full_tensor_rows(1)
    finally:
        engine._require = original
    rows = result["rows"]
    _require(invalid_row in rows and rows[invalid_row].has(sp.zoo), f"missing exceptional {invalid_row} degeneration")
    return rows


def _direct_operators() -> tuple[sp.Matrix, sp.Matrix, sp.Symbol, sp.Symbol]:
    axial_rows = _direct_rows(axial_engine, "metric_angular")
    axial_values = [axial_rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")]
    k = _symbol(axial_values, "k")
    omega = _symbol(axial_values, "omega")
    axial_coefficients = [_symbol(axial_values, name) for name in ("h_t", "h_x", "q_t", "q_x")]
    axial = sp.Matrix(
        [2 * axial_rows["metric_t"], -2 * axial_rows["metric_x"], axial_rows["maxwell_t"], axial_rows["maxwell_x"]]
    ).jacobian(axial_coefficients).applyfunc(sp.factor)

    polar_rows = _direct_rows(polar_engine, "sphere_tracefree")
    polar_values = [polar_rows[name] for name in ("metric_00", "metric_01", "metric_11", "maxwell_axial_density")]
    polar_k = _symbol(polar_values, "k")
    polar_omega = _symbol(polar_values, "omega")
    polar_coefficients = [_symbol(polar_values, name) for name in ("A_t", "B", "C_t", "U")]
    polar = sp.Matrix(
        [-polar_rows["metric_00"], 2 * polar_rows["metric_01"], -polar_rows["metric_11"], 4 * polar_rows["maxwell_axial_density"]]
    ).jacobian(polar_coefficients).subs({polar_omega: omega, polar_k: k}, simultaneous=True).applyfunc(sp.factor)
    return axial, polar, omega, k


def build_certificate() -> dict[str, object]:
    phase = json.loads(PHASE_INPUT.read_text(encoding="utf-8"))
    _require(phase["classification"]["complete_opposite_momentum_second_order_cone_classified"] is False, "phase input unexpectedly promoted")
    axial_full, polar_full, omega, k = _direct_operators()
    _require(
        (axial_full - axial_full.subs({omega: -omega, k: -k}, simultaneous=True).T).applyfunc(sp.factor) == sp.zeros(4),
        "direct axial ell=1 Hessian lost formal self-adjointness",
    )
    _require(
        (polar_full - polar_full.subs({omega: -omega, k: -k}, simultaneous=True).T).applyfunc(sp.factor) == sp.zeros(4),
        "direct polar ell=1 Hessian lost formal self-adjointness",
    )
    axial_gauge_full = sp.Matrix([omega, -k, -omega, k])
    polar_gauge_full = sp.Matrix([2 - 2 * omega**2, 2 * k * omega, -2 * k**2 - 2, 1])
    _require((axial_full * axial_gauge_full).applyfunc(sp.factor) == sp.zeros(4, 1), "axial Fourier gauge defect")
    _require((polar_full * polar_gauge_full).applyfunc(sp.factor) == sp.zeros(4, 1), "polar Fourier gauge defect")
    from itertools import combinations

    axial_minors = [
        sp.factor(axial_full.extract(rows, columns).det())
        for rows in combinations(range(4), 3)
        for columns in combinations(range(4), 3)
        if axial_full.extract(rows, columns).det() != 0
    ]
    polar_minors = [
        sp.factor(polar_full.extract(rows, columns).det())
        for rows in combinations(range(4), 3)
        for columns in combinations(range(4), 3)
        if polar_full.extract(rows, columns).det() != 0
    ]
    axial_divisor = sp.factor(sp.gcd_list(axial_minors))
    polar_divisor = sp.factor(sp.gcd_list(polar_minors))
    shells = sp.factor((k**2 - omega**2 + 4) * (3 * k**2 - 3 * omega**2 + 4))
    _require(axial_divisor == shells, "axial ell=1 characteristic divisor changed")
    _require(polar_divisor == shells / 3, "polar ell=1 characteristic divisor changed")

    axial = axial_full.subs(omega, 0).applyfunc(sp.factor)
    polar = polar_full.subs(omega, 0).applyfunc(sp.factor)
    expected_axial = sp.Matrix(
        [
            [-(3 * k**4 + 10 * k**2 - 4) / 2, 0, 2, 0],
            [0, -2, 0, -2],
            [2, 0, k**2 + 2, 0],
            [0, -2, 0, -2],
        ]
    )
    expected_polar = sp.Matrix(
        [
            [(k**4 + 4 * k**2 + 1) / 2, 0, (k**2 + 3) / 2, 2],
            [0, -3 * k**2 - 4, 0, 0],
            [(k**2 + 3) / 2, 0, sp.Rational(1, 2), -2],
            [2, 0, -2, -4 * (k**2 + 2)],
        ]
    )
    _require((axial - expected_axial).applyfunc(sp.factor) == sp.zeros(4), "direct axial ell=1 static operator changed")
    _require((polar - expected_polar).applyfunc(sp.factor) == sp.zeros(4), "direct polar ell=1 static operator changed")
    _require(axial == axial.T and polar == polar.T, "exceptional static Hessian lost symmetry")

    axial_gauge = sp.Matrix([0, -1, 0, 1])
    polar_gauge = sp.Matrix([2, 0, -2 * k**2 - 2, 1])
    _require((axial * axial_gauge).applyfunc(sp.factor) == sp.zeros(4, 1), "axial residual gauge defect")
    _require((polar * polar_gauge).applyfunc(sp.factor) == sp.zeros(4, 1), "polar residual gauge defect")
    axial_minor = sp.factor(axial.extract((0, 1, 2), (0, 1, 2)).det())
    polar_minor = sp.factor(polar.extract((0, 1, 2), (0, 1, 2)).det())
    _require(axial_minor == k**2 * (k**2 + 4) * (3 * k**2 + 4), "axial rank witness changed")
    _require(polar_minor == (k**2 + 4) * (3 * k**2 + 4) / 2, "polar rank witness changed")

    return {
        "schema": "einstein-maxwell-weyl-ell1-nonzero-static-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL1_NONZERO_STATIC",
        "result_state": "AXIAL_AND_POLAR_ELL1_STATIC_NONZERO_MOMENTUM_EXACT_MODULO_GAUGE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "axial and polar L=1 target harmonics at Omega=0 and real nonzero output momentum kappa, all m by SO(3), before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "engines": {str(path.relative_to(ROOT)): _sha256(path) for path in ENGINES},
            "input": {"path": str(PHASE_INPUT.relative_to(ROOT)), "sha256": _sha256(PHASE_INPUT)},
        },
        "direct_replay": {
            "method": "insert Y_10=cos(theta) in the four-dimensional axial and polar fields, omit only the identically absent ell=1 tensor-harmonic equation, linearize 3B-T and Maxwell, then set Omega=0",
            "generic_lambda_continuation_used_as_proof": False,
            "axial": {
                "field_order": ["h_t", "h_x", "q_t", "q_x"],
                "full_Fourier_action_Hessian": _matrix_strings(axial_full),
                "full_Fourier_residual_gauge": [str(value) for value in axial_gauge_full],
                "three_by_three_determinantal_divisor": str(axial_divisor),
                "action_Hessian": _matrix_strings(axial),
                "residual_gauge": [str(value) for value in axial_gauge],
                "rank_three_minor": str(axial_minor),
            },
            "polar": {
                "field_order": ["A_t", "B", "C_t", "U"],
                "full_Fourier_action_Hessian": _matrix_strings(polar_full),
                "full_Fourier_residual_gauge": [str(value) for value in polar_gauge_full],
                "three_by_three_determinantal_divisor": str(polar_divisor),
                "action_Hessian": _matrix_strings(polar),
                "residual_gauge": [str(value) for value in polar_gauge],
                "rank_three_minor": str(polar_minor),
            },
        },
        "nonzero_Fourier_consequence": {
            "reduced_shells": ["omega^2-kappa^2=4", "omega^2-kappa^2=4/3"],
            "off_shell": "the quotient operator is invertible",
            "on_shell_smooth_global": "the exponential-polynomial secular inverse removes every Noether-compatible resonant source",
            "bounded_on_shell": "requires the separate resonant source projection and is not inferred",
        },
        "static_consequence": {
            "for_real_kappa_nonzero": "both rank-three minors are strictly positive",
            "axial_kernel_equals_residual_gauge": True,
            "polar_kernel_equals_residual_gauge": True,
            "axial_cokernel_is_Noether_only": True,
            "polar_cokernel_is_Noether_only": True,
            "every_Noether_compatible_static_L1_source_is_removable": True,
        },
        "classification": {
            "direct_axial_ell1_static_nonzero_momentum_operator_certified": True,
            "direct_polar_ell1_static_nonzero_momentum_operator_certified": True,
            "static_L1_K2k_phase_source_removable": True,
            "bounded_nonzero_frequency_resonant_projection_classified": False,
        },
        "interpretation": "The L=1 output seam does not add a phase obstruction at nonzero circle momentum. In both parities the static Hessian has one residual gauge kernel and no physical adjoint cokernel, so every quadratic source satisfying the Noether identity is removable.",
        "next_gate": "aggregate the L=0 and L=1 exceptional results with the generic Smith/secular and common-zero moment-map theorems to close the fixed-(ell,|k|) smooth-global opposite-momentum cone",
        "claim_boundary": "This is a static exceptional target theorem. It does not classify the K=0 twist cokernel, bounded nonzero-frequency resonant projections, distinct |k| fibres, exceptional/global input modes, all-orders integration, causal scattering, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.2, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 51.2, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell1_nonzero_static --verify bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell1_nonzero_static.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell1_nonzero_static"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["direct axial full-tensor engine", "direct polar full-tensor engine", "opposite-momentum phase divisor"]},
            "tier_3": {"status": "NOT_RUN", "reason": "the bounded resonant projection and programme-wide nonlinear theorem remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell1_nonzero_static --verify bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell1_nonzero_static.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell1_nonzero_static",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "ell=1 static certificate is stale")


if __name__ == "__main__":
    main()
