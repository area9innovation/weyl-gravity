"""Certify the Weyl--Maxwell pullback on the homogeneous global block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_homogeneous_global_lee_wald_fixture.py"
INPUTS = {
    "direct_fixture": ROOT / "bridge/certificates/weyl_maxwell_homogeneous_global_lee_wald_fixture.json",
    "einstein_global_form": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
}


class HomogeneousRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HomogeneousRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pfaffian_six(matrix: sp.Matrix) -> sp.Expr:
    # Recursive exact Pfaffian, used independently of det=square(Pf).
    if matrix.rows == 0:
        return sp.Integer(1)
    total = sp.Integer(0)
    for column in range(1, matrix.cols):
        keep = [index for index in range(matrix.rows) if index not in (0, column)]
        total += (-1) ** (column + 1) * matrix[0, column] * _pfaffian_six(matrix.extract(keep, keep))
    return sp.expand(total)


def _theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_row = records["einstein_global_form"]["ell0_global_theorem"]
    target_row = records["direct_fixture"]["direct_current"]
    source = sp.Matrix([[sp.sympify(value) for value in row] for row in source_row["dimensionless_matrix_after_factor_2piL"]])
    coordinate = sp.Matrix([[sp.sympify(value, locals={"pi": sp.pi}) for value in row] for row in target_row["coordinate_current_matrix"]])
    target = sp.simplify(-coordinate / (2 * sp.pi))
    expected_target = sp.Matrix([
        [0, 2, 0, -1, 0, 0],
        [-2, 0, 1, 0, 0, 0],
        [0, -1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, -2],
        [0, 0, 0, 0, 2, 0],
    ])
    _require(target == expected_target, "homogeneous target Cauchy matrix changed")
    _require(source == -source.T and target == -target.T, "homogeneous form is not antisymmetric")
    _require(source.rank() == target.rank() == 6, "homogeneous restriction lost rank")
    _require(source.det() == target.det() == 4, "homogeneous determinant changed")
    _require(_pfaffian_six(source) == _pfaffian_six(target) == 2, "homogeneous Pfaffian changed")

    relative = source.inv() * target
    nilpotent = relative - sp.eye(6)
    _require(nilpotent.rank() == 2 and nilpotent**2 == sp.zeros(6), "relative nilpotent invariants changed")
    shear = sp.eye(6) + nilpotent / 2
    _require(sp.simplify(shear.T * source * shear - target) == sp.zeros(6), "symplectic shear identity failed")
    _require(shear.det() == 1, "symplectic shear orientation changed")
    return {
        "parameter_order": target_row["parameter_order"],
        "representative": target_row["representative"],
        "current_convention": records["direct_fixture"]["current_convention"],
        "full_time_conservation": {
            "integrated_coordinate_current_per_unit_x": target_row["integrated_coordinate_current_per_unit_x"],
            "coefficientwise_time_derivative": target_row["time_derivative"],
            "verified_on_full_polynomial_representatives_not_only_t0": True,
        },
        "cauchy_forms_after_common_factor_2piL": {
            "einstein_maxwell": [[str(value) for value in source.row(row)] for row in range(6)],
            "weyl_maxwell": [[str(value) for value in target.row(row)] for row in range(6)],
            "both_rank": 6,
            "both_determinant": "4",
            "both_pfaffian": "2",
            "identity_inclusion_symplectic": False,
        },
        "relative_endomorphism": {
            "definition": "R=Omega_EM^(-1)*Omega_WM",
            "matrix": [[str(value) for value in relative.row(row)] for row in range(6)],
            "R_equals_I_plus_N": True,
            "rank_N": 2,
            "N_squared": "0",
            "characteristic_polynomial": "(x-1)^6",
            "minimal_polynomial": "(x-1)^2",
            "jordan_blocks": "two size-2 blocks and two size-1 blocks",
            "R_is_Omega_EM_self_adjoint": bool(relative.T * source == source * relative),
        },
        "explicit_linear_symplectomorphism": {
            "S_equals_I_plus_N_over_2": [[str(value) for value in shear.row(row)] for row in range(6)],
            "identity": "S^T*Omega_EM*S=Omega_WM",
            "determinant_S": "1",
            "meaning": "the identity inclusion changes the form, but a declared unipotent shear gives a linear symplectomorphism of the two six-dimensional blocks",
        },
        "topology_and_function_space": {
            "fixed_magnetic_bundle": True,
            "uniform_magnetic_variation_included": False,
            "flat_holonomy_W_x_retained": True,
            "bounded_in_time_restriction_imposed": False,
            "reason": "the certified generalized solution block contains polynomial Jordan partners; deleting them would make a different, generally degenerate phase space",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(records["direct_fixture"]["result_id"] == "WEYL_MAXWELL_HOMOGENEOUS_GLOBAL_LEE_WALD_FIXTURE", "direct fixture changed")
    _require(records["einstein_global_form"]["classification"]["ell0_metric_global_form_nondegenerate"] is True, "Einstein global input changed")
    theorem = _theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-homogeneous-global-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION",
        "result_state": "HOMOGENEOUS_GLOBAL_PULLBACK_NONDEGENERATE_UNIPOTENT_SHEAR",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_FIXED_BUNDLE_HOMOGENEOUS_GENERALIZED_BLOCK",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "direct_implementation": {
                "current_engine": {"path": str(CURRENT_ENGINE.relative_to(ROOT)), "sha256": _sha256(CURRENT_ENGINE)},
                "fixture_generator": {"path": str(FIXTURE_GENERATOR.relative_to(ROOT)), "sha256": _sha256(FIXTURE_GENERATOR)},
            },
        },
        "domain": "the six-dimensional homogeneous generalized Einstein-Maxwell solution block on R_t x S1_L x S2 at fixed magnetic bundle, before the final residual SO(4,2) quotient",
        "theorem": theorem,
        "classification": {
            "homogeneous_restriction_computed": True,
            "full_polynomial_time_conservation_verified": True,
            "restricted_target_form_nondegenerate": True,
            "identity_inclusion_symplectic": False,
            "linear_symplectomorphism_exhibited": True,
            "flat_holonomy_retained": True,
            "axial_twist_restriction_computed": False,
            "complete_standard_harmonic_restriction": False,
            "final_residual_quotient_computed": False,
            "one_particle_or_quantum_theorem": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "The entire homogeneous Einstein-Maxwell generalized block survives with a nondegenerate Weyl-Maxwell pullback. The identity map is not symplectic: the gravitational global coordinates acquire a rank-two nilpotent shear, while the electric-charge/flat-holonomy pair is unchanged. Nevertheless an explicit determinant-one unipotent change of variables identifies the two symplectic vector spaces. This is a global reduced-mode statement, not a particle or scattering theorem.",
        "next_gate": "compute the separate axial ell=1 twist pullback and then assemble the complete fixed-bundle standard-harmonic restriction theorem",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers only the declared homogeneous generalized block at fixed bundle and retains W_x. It does not impose bounded-in-time data, cover the twist or radiative blocks, classify extra fourth-order solutions, compute the final residual quotient, or establish causal scattering or quantum unitarity.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.weyl_maxwell_homogeneous_global_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_homogeneous_global_lee_wald_fixture.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_global_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_global_symplectic_restriction",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale homogeneous restriction certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
