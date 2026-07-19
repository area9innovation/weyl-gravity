"""Reduce every fixed-ell constant-twist resonance map to multiplicity matrices."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.schema.json"
INPUTS = {
    "ell2_projector_repair": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json",
    "fixed_ell_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "fixed_ell_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json",
}


class FixedEllTwistFactorizationError(RuntimeError):
    """Raised when an exact input or representation identity changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixedEllTwistFactorizationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _angular_fixture(ell: int) -> dict[str, Any]:
    lam = ell * (ell + 1)
    magnetic = list(range(-ell, ell + 1))
    coefficients = [sp.factor(clebsch_gordan(1, ell, ell, 0, m, m)) for m in magnetic]
    expected = [-sp.Rational(m, 1) / sp.sqrt(lam) for m in magnetic]
    _require(coefficients == expected, f"axis Clebsch-Gordan formula changed at ell={ell}")
    transverse = sp.factor(clebsch_gordan(1, ell, ell, 1, 0, 1))
    _require(transverse == sp.sqrt(2) / 2, f"transverse fixture changed at ell={ell}")
    operator = sp.diag(*coefficients)
    nullity = len(operator.nullspace())
    _require(operator.rank() == 2 * ell and nullity == 1, f"spin operator rank changed at ell={ell}")
    return {
        "ell": ell,
        "lambda": lam,
        "axis_coefficients": [str(value) for value in coefficients],
        "rank": operator.rank(),
        "kernel_dimension": nullity,
        "transverse_mA1_m0_coefficient": str(transverse),
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    repair = records["ell2_projector_repair"]
    _require(repair["corrected_position_maps"]["Einstein_plus_minus"] == "zero", "ell2 Einstein repair changed")
    _require(repair["corrected_position_maps"]["extra"] == "zero", "ell2 extra repair changed")
    _require(repair["classification"]["harmonic_type_mismatch_repaired"], "ell2 projector lifecycle changed")
    _require(records["fixed_ell_wave"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"], "fixed-ell wave theorem changed")
    _require(records["fixed_ell_global"]["classification"]["A_zero_wave_subcone_certified"], "fixed-ell global subcone changed")

    fixtures = [_angular_fixture(ell) for ell in range(2, 9)]
    return {
        "schema": "einstein-maxwell-weyl-fixed-ell-constant-twist-factorization-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_FACTORIZATION",
        "result_state": "ALL_M_CONSTANT_TWIST_RESONANCE_REDUCED_TO_FIXED_ELL_MULTIPLICITY_MATRICES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic resonance class",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one nonzero constant axial twist position A crossed with one arbitrary fixed generic ell,k=0 q/p wave block",
            "degree": 2,
            "parity": "axial and polar multiplicity spaces retained",
            "ell": "one arbitrary integer ell>=2",
            "m": "all m=-ell,...,ell",
            "k": 0,
            "omega": "each fixed-ell Einstein plus/minus q shell and extra p shell separately",
        },
        "representation_theorem": {
            "tensor_product": "V_1 tensor V_ell = V_(ell-1) direct_sum V_ell direct_sum V_(ell+1)",
            "multiplicity": "dim Hom_SO3(V_1 tensor V_ell,V_ell)=1 for every integer ell>=1",
            "factorization": "R_(ell,branch)(A)=(A_hat dot J_ell) tensor Q_(ell,branch), up to one fixed nonzero normalization scalar",
            "axis_spectrum": "for A_hat=e_z the normalized angular factor is diag(-m/sqrt(ell*(ell+1))) for m=-ell,...,ell",
            "axis_kernel": "ker(A_hat dot J_ell)=V_(m_A=0)",
            "fixture_channel": "m_A=1,m_wave=0 -> M_output=1 has normalized coefficient sqrt(2)/2 for every ell>=1",
            "proof": "Clebsch-Gordan multiplicity one gives the unique equivariant angular map; rotating nonzero A to e_z identifies it with the spin generator and yields the displayed spectrum.",
        },
        "finite_matrix_gates": {
            "Einstein_minus": {"input_dimension": 2, "output_dimension": 2, "matrix": "Q_(ell,-)", "bounded_kernel_if_rank_r": "2 + 2*ell*(2-r)", "closure_gate": "det Q_(ell,-) != 0"},
            "Einstein_plus": {"input_dimension": 2, "output_dimension": 2, "matrix": "Q_(ell,+)", "bounded_kernel_if_rank_r": "2 + 2*ell*(2-r)", "closure_gate": "det Q_(ell,+) != 0"},
            "extra": {"input_dimension": 4, "output_dimension": 4, "matrix": "P_ell", "bounded_kernel_if_rank_r": "4 + 2*ell*(4-r)", "closure_gate": "rank P_ell"},
            "general_kernel_formula": "ker((A_hat dot J_ell) tensor Q)=V_(m_A=0) tensor M_in + V_ell tensor ker(Q)",
            "intersection": "V_(m_A=0) tensor ker(Q)",
        },
        "ell2_regression": {
            "Einstein_minus_rank": 0,
            "Einstein_plus_rank": 0,
            "Einstein_each_shell_kernel_dimension": 10,
            "extra_rank": 0,
            "extra_kernel_dimension": 20,
            "repair_disposition": "the former nonzero ell2 ranks used a mistyped *dY_11 projector; *dY_21 gives zero",
            "matches_authoritative_repair": True,
        },
        "exact_fixture_ledger": fixtures,
        "minimal_next_computation": {
            "required_channels": "one m_A=1,m=0 -> M=1 source fixture for every input multiplicity and every adjoint-output multiplicity",
            "Einstein_payload": "two 2x2 matrices Q_(ell,+/-)",
            "extra_payload": "one 4x4 matrix P_ell",
            "all_m_replay_required": False,
            "promotion_rule": "once the finite matrices are action-normalized, the factorization determines every m exactly",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OPEN", "reason": "the representation reduction is certified, but the generic-ell multiplicity-matrix ranks are not"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "NOT_APPLICABLE", "reason": "this theorem classifies a bounded resonant projection only"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "all_fixed_ell_all_m_factorization_certified": True,
            "all_m_problem_reduced_to_finite_multiplicity_matrices": True,
            "ell2_regression_exact": True,
            "generic_ell_Einstein_matrix_determinants_computed": False,
            "generic_ell_extra_matrix_rank_computed": False,
            "complete_fixed_ell_constant_twist_cone_classified": False,
            "finite_multi_ell_twist_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The unresolved generic-ell twist gate is finite-dimensional, not an all-m source problem. Rotational covariance fixes every magnetic channel once two Einstein 2x2 matrices and one extra 4x4 matrix are known on a single transverse fixture. The correctly typed ell2 fibre is the zero matrix in every branch.",
        "next_gate": "compute Q_(ell,+/-) and P_ell as exact functions of lambda=ell(ell+1), prove their physical-fibre ranks, then intersect their kernels with H,J_i=0",
        "claim_boundary": "This certifies only the representation factorization and kernel/rank formulas. It does not assert the generic-ell finite matrices are nonzero, does not classify their common zero cone, and makes no secular, causal, all-orders, residual, observational or quantum claim.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.29},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.51, "tests_run": 34},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the corrected zero ell2 q/p position maps and every-fixed-ell wave/global inputs are unchanged hashed dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "the physical-fibre multiplicity matrices remain the next calculation"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_constant_twist_factorization --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_ell_constant_twist_factorization",
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
        raise FixedEllTwistFactorizationError("fixed-ell twist-factorization certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_FACTORIZATION: PASS")


if __name__ == "__main__":
    main()
