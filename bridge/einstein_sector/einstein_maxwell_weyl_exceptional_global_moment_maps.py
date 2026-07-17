"""Moment maps on the certified standard exceptional and global blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_global_moment_maps.schema.json"
INPUTS = {
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "ell1_physical": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
}


class ExceptionalMomentMapError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalMomentMapError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _homogeneous_theorem(matrix: sp.Matrix) -> dict[str, Any]:
    a, b, c, d, charge, wilson = sp.symbols("a b c d Q_e W_x", real=True)
    vector = sp.Matrix([a, b, c, d, charge, wilson])
    time_action = sp.Matrix([b, 0, d, 2 * a, 0, charge])
    moment_map = sp.factor((vector.T * matrix * time_action)[0] / 2)
    expected = -a**2 - b**2 + b * d - charge**2
    _require(sp.expand(moment_map - expected) == 0, "homogeneous H moment map changed")
    action_matrix = time_action.jacobian(vector)
    _require(matrix * action_matrix + action_matrix.T * matrix == sp.zeros(6), "time action is not symplectic")
    quadratic_matrix = sp.hessian(moment_map, (a, b, d, charge)) / 2
    _require(quadratic_matrix.det() != 0, "homogeneous nonzero quadratic block degenerated")
    return {
        "coordinates": ["a", "b", "c", "d", "Q_e", "W_x"],
        "representative": ["K=a+b*t", "C=a*t^2+(b/3)*t^3+c+d*t", "A_x=W_x+Q_e*t"],
        "time_translation_action": "(a,b,c,d,Q_e,W_x) -> (b,0,d,2a,0,Q_e)",
        "normalized_symplectic_factor": "the displayed formula omits the common positive factor 2*pi*L",
        "mu_H": str(moment_map),
        "mu_Px": "0",
        "mu_J_a": "0",
        "common_zero_locus": "a^2+b^2-b*d+Q_e^2=0, with c and W_x free",
        "quadratic_inertia_on_a_b_d_Qe": {"positive": 1, "negative": 3, "zero": 0},
        "spectator_zero_directions": ["c: static circumference modulus", "W_x: flat U(1) holonomy"],
        "nontrivial_example": "a=Q_e=0, b=d!=0; c and W_x arbitrary",
        "charge_variation": {
            "contribution": "-Q_e^2 to mu_H",
            "pure_extra_effect": "same sign as the positive-current extra and Einstein-plus oscillators, so electric-charge variation alone cannot rescue a pure-extra obstruction",
            "possible_balances": "it can balance a positive-mu_H Einstein-minus or twist-velocity contribution in a larger mixed cone",
            "second_order_warning": "a second-order charge shift cannot alter an adjoint-cokernel pairing; cancellation requires charge variation already in the first-order tangent",
        },
    }


def _twist_theorem(matrix: sp.Matrix) -> dict[str, Any]:
    amplitude, velocity = sp.symbols("A B", real=True)
    vector = sp.Matrix([amplitude, velocity])
    time_action = sp.Matrix([velocity, 0])
    moment_map = sp.factor((vector.T * matrix * time_action)[0] / 2)
    _require(moment_map == 2 * velocity**2, "twist H moment map changed")
    return {
        "representative": "h_(x,a)=(A_a+B_a*t)X_a, a_x=-(A_a+B_a*t)Y_(1a)",
        "normalized_symplectic_factor": "per orthonormal real harmonic, the displayed formula omits L*N_1a",
        "mu_H": "2*|B|^2",
        "mu_Px": "0",
        "mu_J": "-4*A cross B in an oriented orthonormal real ell=1 basis",
        "isolated_common_zero_locus": "B=0 with arbitrary constant twist vector A",
        "interpretation": "the Jordan velocity is charged under time translation; the constant SO(3) holonomy is a common-zero modulus",
        "finite_extension": "constant A is tangent to the exact mapping-torus family obtained by quotienting the universal-cover product by an x-translation composed with a lifted SO(3) rotation; local covariance preserves both field equations",
    }


def _physical_ell1_theorem() -> dict[str, Any]:
    return {
        "dispersion": "omega^2=k_n^2+4",
        "positive_frequency_current": "positive definite in both axial and polar quotient oscillators because Omega_WM=4*Omega_EM on this block",
        "mu_H": "negative definite after the common convention mu_H=-(L/4)*omega^2*c^dagger*G*c",
        "isolated_common_zero_locus": "the origin",
        "mixed_role": "physical ell=1 occupations have the same mu_H sign as generic Einstein-plus and extra modes and may be balanced only by an opposite-sign block",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["ell1_physical"]["classification"]["physical_ell1_pullback_equals_four_times_einstein"], "ell=1 input changed")
    _require(records["homogeneous"]["classification"]["homogeneous_restriction_computed"], "homogeneous input changed")
    _require(records["twist"]["classification"]["pullback_equals_minus_two_times_einstein"], "twist input changed")
    homogeneous_matrix = sp.Matrix([[sp.sympify(value) for value in row] for row in records["homogeneous"]["theorem"]["cauchy_forms_after_common_factor_2piL"]["weyl_maxwell"]])
    twist_matrix = sp.Matrix([[sp.sympify(value) for value in row] for row in records["twist"]["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]["weyl_maxwell"]])
    return {
        "schema": "einstein-maxwell-weyl-exceptional-global-moment-maps-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_STANDARD_EXCEPTIONAL_GLOBAL_MOMENT_MAPS",
        "result_state": "STANDARD_EXCEPTIONAL_AND_GLOBAL_COMMON_ZERO_LOCI_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_STANDARD_ELL1_HOMOGENEOUS_TWIST_BLOCKS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "moment_map_definition": "mu_X(u)=1/2*Omega_WM(u,L_X u), with the same current convention as the generic Taub bridge",
        "physical_ell1": _physical_ell1_theorem(),
        "homogeneous_ell0": _homogeneous_theorem(homogeneous_matrix),
        "axial_twist": _twist_theorem(twist_matrix),
        "combined_cone_rule": "Moment maps add across the certified symplectically orthogonal harmonic blocks. The full standard-plus-generic cone is obtained by summing these exceptional formulas with the generic density-cone charges before imposing H=P_x=J_a=0.",
        "classification": {
            "standard_physical_ell1_common_zero_locus_classified": True,
            "standard_homogeneous_common_zero_locus_classified": True,
            "standard_twist_common_zero_locus_classified": True,
            "electric_charge_first_order_role_classified": True,
            "constant_twist_exact_family_identified": True,
            "extra_fourth_order_exceptional_modes_classified": False,
            "full_combined_quadratic_source_classified": False,
            "uniform_magnetic_charge_variation_in_fixed_bundle": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The exceptional sector does not simply disappear. Physical ell=1 oscillators are sign-definite and obstructed in isolation; constant twists are exact common-zero holonomy moduli; the homogeneous Jordan block has an indefinite quadratic cone with circumference and Wilson-line spectators. Electric charge variation is not a cure for the pure-extra obstruction because it has the same moment-map sign, although it participates in larger mixed balances.",
        "next_gate": "test the nontrivial homogeneous quadric and twist-velocity balances against their full quadratic sources, and separately classify exceptional fourth-order target modes",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies moment maps only on the already certified standard ell=1, homogeneous, and twist blocks. It does not classify exceptional fourth-order Weyl modes, solve the combined quadratic PDE, vary magnetic Chern class, or establish causal or quantum results.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_global_moment_maps --verify bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_global_moment_maps.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_global_moment_maps",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"exceptional/global certificate stale: {path}")


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
