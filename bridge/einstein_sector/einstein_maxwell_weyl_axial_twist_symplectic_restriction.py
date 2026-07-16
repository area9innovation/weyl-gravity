"""Certify the Weyl--Maxwell pullback on the axial ell=1 twist block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_twist_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_axial_twist_lee_wald_fixture.py"
INPUTS = {
    "direct_fixture": ROOT / "bridge/certificates/weyl_maxwell_axial_twist_lee_wald_fixture.json",
    "einstein_global_form": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
}


class AxialTwistRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialTwistRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    target_row = records["direct_fixture"]["direct_current"]
    coordinate = sp.Matrix([[sp.sympify(value, locals={"pi": sp.pi}) for value in row] for row in target_row["coordinate_current_matrix"]])
    # Omega=-L int omega^t. Divide by the positive common L*N_10.
    norm = sp.Rational(4, 3) * sp.pi
    source = sp.Matrix([[0, 2], [-2, 0]])
    target = sp.simplify(-coordinate / norm)
    _require(target == sp.Matrix([[0, -4], [4, 0]]), "twist target matrix changed")
    _require(target == -2 * source, "twist factor changed")
    _require(source.rank() == target.rank() == 2, "twist restriction lost rank")
    _require(source.det() == 4 and target.det() == 16, "twist determinant changed")
    return {
        "representative": target_row["representative"],
        "harmonic_normalization": target_row["harmonic"],
        "all_m_extension": target_row["all_m_extension"],
        "full_time_conservation": {
            "integrated_coordinate_current_per_unit_x": target_row["integrated_coordinate_current_per_unit_x"],
            "coefficientwise_time_derivative": target_row["time_derivative"],
            "verified_on_A_plus_Bt_not_only_t0": True,
        },
        "cauchy_forms_after_common_factor_L_N_1m": {
            "einstein_maxwell": [["0", "2"], ["-2", "0"]],
            "weyl_maxwell": [["0", "-4"], ["4", "0"]],
            "identity": "Omega_WM|twist=-2*Omega_EM|twist",
            "source_rank": 2,
            "target_rank": 2,
            "source_determinant": "4",
            "target_determinant": "16",
            "orientation_relative_to_source": "reversed",
        },
        "mode_counting": {
            "real_harmonic_multiplicity": 3,
            "darboux_pairs": 3,
            "real_phase_space_dimension": 6,
            "cross_m_pairing": "0 in an orthogonal real ell=1 harmonic basis by SO(3) invariance",
        },
        "exceptional_status": {
            "mu_to_zero_radiative_limit_used": False,
            "reason": "the twist is a zero-frequency generalized Jordan block with A+B*t; substituting mu=0 in an oscillatory radiative formula would incorrectly erase its conserved pairing",
            "periodic_gauge_audit_inherited": "the would-be generator is proportional to x*(A+B*t) and is not periodic on S1",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(records["direct_fixture"]["result_id"] == "WEYL_MAXWELL_AXIAL_TWIST_LEE_WALD_FIXTURE", "direct twist fixture changed")
    _require(records["einstein_global_form"]["classification"]["axial_ell1_twist_generalized_pair_complete"] is True, "Einstein twist input changed")
    theorem = _theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-axial-twist-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION",
        "result_state": "AXIAL_TWIST_ALL_M_GENERALIZED_PULLBACK_NONDEGENERATE_FACTOR_MINUS_TWO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_AXIAL_ELL1_TWIST_ALL_REAL_M",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "direct_implementation": {
                "current_engine": {"path": str(CURRENT_ENGINE.relative_to(ROOT)), "sha256": _sha256(CURRENT_ENGINE)},
                "fixture_generator": {"path": str(FIXTURE_GENERATOR.relative_to(ROOT)), "sha256": _sha256(FIXTURE_GENERATOR)},
            },
        },
        "domain": "the generalized zero-frequency axial ell=1 twist Einstein-Maxwell block for all three real harmonics on R_t x S1_L x S2, before the final residual SO(4,2) quotient",
        "theorem": theorem,
        "classification": {
            "axial_twist_restriction_computed": True,
            "all_three_real_m_by_SO3": True,
            "full_linear_time_conservation_verified": True,
            "restricted_target_form_nondegenerate": True,
            "pullback_equals_minus_two_times_einstein": True,
            "radiative_mu_zero_continuation_used": False,
            "homogeneous_restriction_computed": False,
            "complete_standard_harmonic_restriction": False,
            "final_residual_quotient_computed": False,
            "one_particle_or_quantum_theorem": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "Every global axial twist and its time-linear partner survive as a nondegenerate Weyl-Maxwell Darboux pair. The pullback is exactly minus twice the Einstein-Maxwell form, so the identity inclusion reverses the relative symplectic orientation on this block but does not remove it. The result is exceptional and comes from the direct generalized current, not a zero-frequency limit of a radiative formula.",
        "next_gate": "combine the twist, homogeneous, physical ell=1, and standard ell>=2 results into a complete fixed-bundle standard-harmonic restriction theorem",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers only the generalized axial ell=1 twist pairs. It does not classify homogeneous or radiative modes, extra fourth-order solutions, the final residual quotient, a one-particle norm, causal scattering, or quantum unitarity.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.weyl_maxwell_axial_twist_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_axial_twist_lee_wald_fixture.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_twist_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_twist_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_twist_symplectic_restriction",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale twist restriction certificate: {path}")


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
