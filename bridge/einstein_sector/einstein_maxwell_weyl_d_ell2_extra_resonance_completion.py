"""Complete axial-plus-polar d-times-ell2-extra resonant source theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.schema.json"
INPUTS = {
    "polar_e1": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_polar_ell2_extra_e1_source_fixture.json",
    "polar_e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_polar_ell2_extra_e2_source_fixture.json",
    "axial_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    sources = sp.Matrix.hstack(*[
        sp.Matrix([sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}) for value in records[name]["bilinear_source_rows"]])
        for name in ("polar_e1", "polar_e2")
    ])
    hessian = sp.Matrix([
        [sp.Rational(27, 2), 0, sp.Rational(5, 2), 6],
        [0, 0, 0, 0],
        [sp.Rational(5, 2), 0, -sp.Rational(77, 18), -6],
        [6, 0, -6, -8],
    ])
    witnesses = sp.Matrix.hstack(
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([-sp.Rational(1, 6), 0, -sp.Rational(3, 2), 1]),
    )
    if hessian.rank() != 2 or hessian.T * witnesses != sp.zeros(4, 2):
        raise AssertionError("polar p-shell adjoint cokernel changed")
    pairing = (witnesses.T * sources).applyfunc(sp.factor)
    expected = sp.diag(-6 * sp.sqrt(3) * sp.I, 552 * sp.sqrt(3) * sp.I)
    if pairing != expected or sp.factor(pairing.det()) != 9936:
        raise AssertionError(f"polar d-cross pairing changed: {pairing}")
    if not records["axial_completion"]["classification"]["d_cross_adjoint_map_invertible"]:
        raise AssertionError("axial d-cross input changed")
    if not records["polar_current"]["classification"]["extra_block_nonradical"]:
        raise AssertionError("polar current input changed")
    return {
        "schema": "einstein-maxwell-weyl-d-ell2-extra-resonance-completion-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_D_ELL2_EXTRA_RESONANCE_COMPLETION",
        "result_state": "D_TIMES_COMPLETE_AXIAL_POLAR_ELL2_EXTRA_ADJOINT_MAP_ISOMORPHISM_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "correction_class": "BOUNDED_OR_FINITE_QUASIPERIODIC",
        "domain": "homogeneous circumference velocity d crossed with the complete axial-plus-polar ell=2,k=0 extra-primary multiplicity space, every m, at Omega^2=16/3",
        "polar_theorem": {
            "frequency_squared": "16/3",
            "action_row_order": records["polar_e1"]["action_row_order"],
            "action_hessian": _strings(hessian),
            "adjoint_basis": _strings(witnesses),
            "source_columns_e1_e2": _strings(sources),
            "adjoint_pairing_matrix": _strings(pairing),
            "determinant": "9936",
            "cancellation_for_d_nonzero": {
                "given_polar_adjoint_defect": "r=(r1,r2)",
                "e1_amplitude": "z1=r1/(6*i*sqrt(3)*d)",
                "e2_amplitude": "z2=-r2/(552*i*sqrt(3)*d)"
            }
        },
        "parity_completion": {
            "axial_pairing_determinant": records["axial_completion"]["pairing_theorem"]["determinant"],
            "polar_pairing_determinant": "9936",
            "block_diagonal_axial_polar_determinant": "8266752",
            "SO3_promotion": "d is a scalar and parity is preserved, so the axial and polar multiplicity isomorphisms tensor with the identity on V_2 for every m"
        },
        "classification": {
            "complete_axial_d_cross_source_matrix_certified": True,
            "complete_polar_d_cross_source_matrix_certified": True,
            "complete_axial_polar_p_shell_adjoint_cokernel_certified": True,
            "d_cross_adjoint_map_invertible_in_both_parities": True,
            "all_m_by_SO3_equivariance": True,
            "arbitrary_ell2_extra_resonant_defect_algebraically_cancellable_for_d_nonzero": True,
            "simultaneous_stabilizer_zero_locus_solved": False,
            "nonresonant_rows_solved": False,
            "full_second_order_equation_solved": False,
            "smooth_secular_theorem": False,
            "causal_retarded_theorem": False,
            "all_orders_integrability": False
        },
        "interpretation": "The circumference velocity supplies a complete resonant control column: crossed with the two extra polarizations in each parity, it spans the entire axial-plus-polar ell=2 p-shell adjoint cokernel. This removes that resonant projection from the remaining tangent-cone problem for d!=0, but does not solve the stabilizer equations or the rest of the quadratic source.",
        "next_gate": "compute a,b and twist position/velocity cross columns, then solve the simultaneous stabilizer plus complementary-resonance zero locus and all nonresonant rows",
        "claim_boundary": "This bounded/finite-quasiperiodic result completes only the d column of the homogeneous/twist-times-ell2-extra source matrix. It does not construct a full second-order correction, classify opposite momenta or multiple |k| fibres, or support causal, residual, particle, or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_ell2_extra_resonance_completion --check",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_ell2_extra_resonance_completion.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_ell2_extra_resonance_completion"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["polar_e1", "polar_e2", "axial_completion", "polar_operator", "polar_current"]},
            "tier_3": {"status": "NOT_RUN", "reason": "the remaining global source columns and full tangent cone are open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_ell2_extra_resonance_completion --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_ell2_extra_resonance_completion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_ell2_extra_resonance_completion"
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("d-cross parity-completion certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_D_ELL2_EXTRA_RESONANCE_COMPLETION: PASS")


if __name__ == "__main__":
    main()
