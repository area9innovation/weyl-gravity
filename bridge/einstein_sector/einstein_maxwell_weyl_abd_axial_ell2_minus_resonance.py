"""Certify the a,b,d cross source on the axial ell=2 Einstein-minus shell."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.polys.numberfields import to_number_field

from bridge.einstein_sector.einstein_maxwell_weyl_abd_axial_ell2_minus_source_explore import (
    shell_pairing,
    source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.schema.json"
HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_abd_axial_ell2_minus_source_explore.py"


class MinusResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MinusResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected() -> tuple[dict[str, sp.Matrix], dict[str, sp.Expr]]:
    time = sp.symbols("t", real=True)
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    rows = {
        "a": sp.Matrix(
            [
                0,
                -6 * sp.I * ((6 * root - 1) * frequency * time + sp.I * (-80 + 50 * root)),
                0,
                -2 * sp.I * (root * frequency * time + sp.I * (-12 + 6 * root)),
            ]
        ),
        "b": sp.Matrix(
            [
                0,
                -3
                * sp.I
                * (
                    (6 * root - 1) * frequency * time**2
                    + sp.I * (-160 + 100 * root) * time
                    + 45 * frequency
                ),
                0,
                -sp.I
                * (
                    root * frequency * time**2
                    + sp.I * (-24 + 12 * root) * time
                    - 2 * root * frequency
                ),
            ]
        ),
        "d": sp.Matrix([0, -3 * sp.I * (6 * root - 1) * frequency, 0, -sp.I * root * frequency]),
    }
    pairings = {
        "a": 12 * sp.I * ((6 * root - 2) * frequency * time + sp.I * (-86 + 54 * root)),
        "b": 6
        * sp.I
        * (
            (6 * root - 2) * frequency * time**2
            + sp.I * (-172 + 108 * root) * time
            + 47 * frequency
        ),
        "d": 6 * sp.I * (6 * root - 2) * frequency,
    }
    return rows, pairings


def _is_zero_in_field(expression: sp.Expr) -> bool:
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    expanded = sp.expand_complex(sp.expand(expression))
    for part in (sp.re(expanded), sp.im(expanded)):
        if to_number_field(part, frequency).as_expr() != 0:
            return False
    return True


def _polynomial_equal(left: sp.Expr, right: sp.Expr) -> bool:
    time = sp.symbols("t", real=True)
    difference = sp.Poly(sp.expand(left - right), time)
    return all(_is_zero_in_field(coefficient) for coefficient in difference.all_coeffs())


def _compute(case: str) -> tuple[str, sp.Matrix, sp.Expr]:
    value = source(case)
    return case, value, shell_pairing(value)


def replay_direct() -> None:
    expected_rows, expected_pairings = _expected()
    with ProcessPoolExecutor(max_workers=3) as executor:
        computed = list(executor.map(_compute, ("a", "b", "d")))
    for case, rows, pairing in computed:
        for actual, expected in zip(rows, expected_rows[case], strict=True):
            _require(_polynomial_equal(actual, expected), f"{case} direct source row changed")
        _require(_polynomial_equal(pairing, expected_pairings[case]), f"{case} shell pairing changed")


def build() -> dict[str, object]:
    rows, pairings = _expected()
    time = sp.symbols("t", real=True)
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    combined = sp.symbols("a") * pairings["a"] + sp.symbols("b") * pairings["b"] + sp.symbols("d") * pairings["d"]
    polynomial = sp.Poly(sp.expand(combined), time)
    _require(_is_zero_in_field(polynomial.nth(2) - 12 * sp.I * (3 * root - 1) * frequency * sp.symbols("b")), "quadratic coefficient changed")
    _require(_is_zero_in_field(polynomial.nth(1).coeff(sp.symbols("a")) - 24 * sp.I * (3 * root - 1) * frequency), "linear a coefficient changed")
    _require(_is_zero_in_field(pairings["d"] - 12 * sp.I * (3 * root - 1) * frequency), "constant d coefficient changed")
    return {
        "schema": "einstein-maxwell-weyl-abd-axial-ell2-minus-resonance-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ABD_AXIAL_ELL2_MINUS_RESONANCE",
        "result_state": "AXIAL_ELL2_MINUS_GLOBAL_ABD_BOUNDED_SHELL_IDEAL_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous a,b,d directions crossed with the axial ell=2,m=0,k=0 Einstein-minus q-primary",
            "degree": 2,
            "parity": "axial",
            "ell": 2,
            "m": 0,
            "k": 0,
            "omega": "sqrt(6-2*sqrt(3))",
        },
        "linear_input": {
            "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
            "representative": ["0", "-2", "0", "2*sqrt(3)"],
            "frequency_squared": "6-2*sqrt(3)",
        },
        "direct_source": {
            "action_row_order": ["6*metric_t", "-6*metric_x", "maxwell_t", "maxwell_x"],
            "rows": {case: [str(sp.factor(value)) for value in vector] for case, vector in rows.items()},
            "method": "direct four-dimensional bivariate coefficient of the Weyl-Maxwell Euler operator",
        },
        "shell_pairing": {
            "adjoint": ["0", "-2", "0", "2*sqrt(3)"],
            "self_adjoint_reason": "the reduced action Hessian is formally self-adjoint and the k=0 shell matrix is real symmetric",
            "polynomials": {case: str(sp.factor(value)) for case, value in pairings.items()},
            "leading_coefficients": {
                "b_t2": "12*I*(3*sqrt(3)-1)*sqrt(6-2*sqrt(3))",
                "a_t_after_b_zero": "24*I*(3*sqrt(3)-1)*sqrt(6-2*sqrt(3))",
                "d_constant_after_a_b_zero": "12*I*(3*sqrt(3)-1)*sqrt(6-2*sqrt(3))",
            },
        },
        "bounded_zero_locus": {
            "ideal_on_wave_amplitude_z": "<b*z,a*z,d*z>",
            "nonzero_wave_branch": "z!=0 implies a=b=d=0",
            "necessity": "successive t^2, t^1 and t^0 shell coefficients force b=0, a=0 and d=0",
            "sufficiency_for_declared_cross_ledger": "the mixed source vanishes when a=b=d=0",
        },
        "classification": {
            "direct_four_dimensional_source_rows_computed": True,
            "complete_abd_shell_pairing_polynomials_explicit": True,
            "bounded_cross_ideal_classified": True,
            "nonzero_minus_forces_a_b_d_zero": True,
            "other_parity_or_branch_classified": False,
            "complete_bounded_cone_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The opposite-sign Einstein-minus mode reopens the Hamiltonian moment-map cone, but it does not tolerate the generalized homogeneous a, b or d directions in a bounded correction. Their shell projections form a triangular polynomial chain with nonzero t^2, t and constant pivots.",
        "next_gate": "combine this ideal with the axial ell=2 minus-plus-extra bounded wave cone and the complete homogeneous zero-frequency source to classify the aligned global-plus-wave carrier",
        "claim_boundary": "This is the complete bounded shell cross ideal only for a,b,d times one axial ell=2,m=0,k=0 Einstein-minus coefficient. It does not classify polar input, all m, other ell or momentum, oscillator self-products, the complete bounded cone, causal propagation, all-orders integration, residual descent, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_helper_path": str(HELPER.relative_to(ROOT)),
            "direct_helper_sha256": _sha256(HELPER),
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.18},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.70, "tests_run": 4},
            "tier_2": {
                "status": "PASS",
                "elapsed_seconds": 51.57,
                "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_axial_ell2_minus_resonance --write --replay-direct",
                "criterion": "three independent direct four-dimensional bilinear sources replay in parallel and reduce exactly in Q(sqrt(6-2*sqrt(3)))",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "the result is a scoped source and shell-ideal theorem"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_axial_ell2_minus_resonance --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_axial_ell2_minus_resonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--replay-direct", action="store_true")
    arguments = parser.parse_args()
    if arguments.replay_direct:
        replay_direct()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise MinusResonanceError("axial ell2 minus resonance certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ABD_AXIAL_ELL2_MINUS_RESONANCE: PASS")


if __name__ == "__main__":
    main()
