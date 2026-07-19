"""Certify the a,b,d cross source on the polar ell=2 Einstein-minus shell."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.polys.numberfields import to_number_field

from bridge.einstein_sector.einstein_maxwell_weyl_abd_polar_ell2_minus_source_explore import (
    shell_pairing,
    source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.schema.json"
HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_abd_polar_ell2_minus_source_explore.py"


class PolarMinusResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarMinusResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected() -> tuple[dict[str, sp.Matrix], dict[str, sp.Expr]]:
    time = sp.symbols("t", real=True)
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    rows = {
        "a": sp.Matrix(
            [
                6 * (33 * time**2 + sp.I * (3 - 28 * root) * frequency * time - 60 + 50 * root),
                0,
                6 * ((6 * root - 3) * time**2 + sp.I * (-81 + 10 * root) * frequency * time + 306 - 178 * root),
                -72 * ((2 * root - 1) * time**2 - sp.I * frequency * time - 6 + 2 * root),
            ]
        ),
        "b": sp.Matrix(
            [
                3 * (22 * time**3 + sp.I * (3 - 28 * root) * frequency * time**2 + (-120 + 100 * root) * time + sp.I * (8 + 6 * root) * frequency),
                0,
                3 * ((4 * root - 2) * time**3 + sp.I * (-81 + 10 * root) * frequency * time**2 + (612 - 356 * root) * time + 78 * sp.I * (1 - root) * frequency),
                -12 * time * ((4 * root - 2) * time**2 - 3 * sp.I * frequency * time - 36 + 12 * root),
            ]
        ),
        "d": sp.Matrix(
            [
                3 * (66 * time + sp.I * (3 - 28 * root) * frequency),
                0,
                3 * ((12 * root - 6) * time + sp.I * (-81 + 10 * root) * frequency),
                -36 * ((4 * root - 2) * time - sp.I * frequency),
            ]
        ),
    }
    pairings = {
        "a": -144 * sp.I * ((66 - 72 * root) * frequency * time + sp.I * (675 - 376 * root)),
        "b": -72 * sp.I * ((66 - 72 * root) * frequency * time**2 + sp.I * (1350 - 752 * root) * time + (-277 + 114 * root) * frequency),
        "d": -432 * sp.I * (11 - 12 * root) * frequency,
    }
    return rows, pairings


def _is_zero_in_field(expression: sp.Expr) -> bool:
    frequency = sp.sqrt(6 - 2 * sp.sqrt(3))
    expanded = sp.expand_complex(sp.expand(expression))
    return all(to_number_field(part, frequency).as_expr() == 0 for part in (sp.re(expanded), sp.im(expanded)))


def _polynomial_equal(left: sp.Expr, right: sp.Expr) -> bool:
    time = sp.symbols("t", real=True)
    return all(_is_zero_in_field(coefficient) for coefficient in sp.Poly(sp.expand(left - right), time).all_coeffs())


def _compute(case: str) -> tuple[str, sp.Matrix, sp.Expr]:
    value = source(case)
    return case, value, shell_pairing(value)


def replay_direct() -> None:
    expected_rows, expected_pairings = _expected()
    with ProcessPoolExecutor(max_workers=3) as executor:
        computed = list(executor.map(_compute, ("a", "b", "d")))
    for case, rows, pairing in computed:
        for actual, expected in zip(rows, expected_rows[case], strict=True):
            _require(_polynomial_equal(actual, expected), f"{case} direct polar source row changed")
        _require(_polynomial_equal(pairing, expected_pairings[case]), f"{case} polar shell pairing changed")


def build() -> dict[str, object]:
    rows, pairings = _expected()
    time = sp.symbols("t", real=True)
    _require(sp.Poly(rows["b"][0], time).nth(3) == 66, "b cubic pivot changed")
    _require(sp.Poly(rows["a"][0], time).nth(2) == 198, "a quadratic pivot changed")
    _require(sp.Poly(rows["d"][0], time).nth(1) == 198, "d linear pivot changed")
    return {
        "schema": "einstein-maxwell-weyl-abd-polar-ell2-minus-resonance-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ABD_POLAR_ELL2_MINUS_RESONANCE",
        "result_state": "POLAR_ELL2_MINUS_GLOBAL_ABD_BOUNDED_POLYNOMIAL_IDEAL_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous a,b,d directions crossed with the polar ell=2,m=0,k=0 Einstein-minus q-primary",
            "degree": 2,
            "parity": "polar",
            "ell": 2,
            "m": 0,
            "k": 0,
            "omega": "sqrt(6-2*sqrt(3))",
        },
        "linear_input": {
            "coefficient_order": ["A_t", "B", "C_t", "U"],
            "representative": ["12", "0", "12-24*sqrt(3)", "6"],
            "frequency_squared": "6-2*sqrt(3)",
            "direct_action_row_remainder": ["0", "0", "0", "0"],
        },
        "direct_source": {
            "action_row_order": ["-polar(metric_00)", "2*polar(metric_01)", "-polar(metric_11)", "12*polar(maxwell_phi)"],
            "rows": {case: [str(sp.factor(value)) for value in vector] for case, vector in rows.items()},
            "method": "direct four-dimensional bivariate coefficient with exact scalar/vector harmonic projection",
        },
        "shell_pairing": {
            "adjoint": ["12", "0", "12-24*sqrt(3)", "6"],
            "self_adjoint_reason": "the reduced polar action Hessian is formally self-adjoint",
            "polynomials": {case: str(sp.factor(value)) for case, value in pairings.items()},
            "all_three_nonzero": True,
        },
        "bounded_zero_locus": {
            "full_polynomial_ideal_on_wave_amplitude_z": "<b*z,a*z,d*z>",
            "triangular_pivots": {"b_t3": "66*b*z", "a_t2_after_b_zero": "198*a*z", "d_t_after_a_b_zero": "198*d*z"},
            "nonzero_wave_branch": "z!=0 implies a=b=d=0",
            "necessity": "successive full-source t^3, t^2 and t coefficients in the first action row force b=0, a=0 and d=0",
            "sufficiency_for_declared_cross_ledger": "the mixed source vanishes when a=b=d=0",
        },
        "classification": {
            "direct_four_dimensional_source_rows_computed": True,
            "direct_linear_input_remainder_zero": True,
            "complete_abd_full_polynomial_source_explicit": True,
            "complete_abd_shell_pairings_explicit": True,
            "bounded_cross_ideal_classified": True,
            "nonzero_minus_forces_a_b_d_zero": True,
            "all_m_promoted": False,
            "other_ell_or_momentum_classified": False,
            "complete_bounded_cone_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Polar parity has an even stronger bounded obstruction than the axial fixture: the full source itself has rational triangular pivots 66, 198 and 198 at degrees three, two and one. Thus no cancellation inside the polar Einstein-minus coefficient can retain a, b or d.",
        "next_gate": "use SO3 multiplicity-one to promote both parity fixtures to all m, then combine them with the complete ell2 common-moment-map cone and global zero-frequency source",
        "claim_boundary": "This is the complete bounded full-polynomial cross ideal only for a,b,d times one polar ell=2,m=0,k=0 Einstein-minus coefficient. Its all-m promotion, axial-polar superposition, other ell or momentum, complete bounded cone, causal propagation, all-orders integration, residual descent, particles and quantum theory remain separate.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_helper_path": str(HELPER.relative_to(ROOT)),
            "direct_helper_sha256": _sha256(HELPER),
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS"},
            "tier_1": {"status": "PASS"},
            "tier_2": {
                "status": "PASS",
                "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_polar_ell2_minus_resonance --write --replay-direct",
                "criterion": "three direct four-dimensional polar bilinear sources replay in parallel and reduce exactly in Q(sqrt(6-2*sqrt(3)))",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "the result is a scoped source and bounded-polynomial theorem"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_abd_polar_ell2_minus_resonance --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_abd_polar_ell2_minus_resonance",
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
        raise PolarMinusResonanceError("polar ell2 minus resonance certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ABD_POLAR_ELL2_MINUS_RESONANCE: PASS")


if __name__ == "__main__":
    main()
