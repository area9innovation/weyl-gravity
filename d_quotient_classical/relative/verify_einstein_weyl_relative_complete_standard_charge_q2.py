#!/usr/bin/env python3
"""Independent consumer for the complete-standard relative charge q2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-complete-standard-five-charge-q2-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in rows])


def _record(value: dict, name: str) -> dict:
    artifact = value["dependencies"][name]
    path = ROOT / artifact["path"]
    if _sha(path) != artifact["sha256"]:
        raise AssertionError(f"dependency hash drifted: {artifact['path']}")
    return json.loads(path.read_text())


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source hash drifted: {relative}")
    for artifact in value["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drifted: {artifact['path']}")

    standard = _record(value, "standard_radiative_q2")
    if standard["operation"]["output_basis"] != value["operation"]["output_basis"]:
        raise AssertionError("generic and complete charge bases disagree")

    inclusion = _record(value, "standard_inclusion")
    expected_decomposition = (
        "T_EM^std=T_rad^(ell>=2) direct_sum T_phys^(ell=1) direct_sum "
        "T_hom^(ell=0) direct_sum T_twist^(axial ell=1,omega=0)"
    )
    if inclusion["theorem"]["solution_space_decomposition"]["identity"] != expected_decomposition:
        raise AssertionError("complete standard source decomposition drifted")
    if inclusion["theorem"]["cross_block_orthogonality"]["conclusion"] != (
        "the target pullback is the displayed block-diagonal direct sum"
    ):
        raise AssertionError("cross-block orthogonality drifted")
    mixed = _record(value, "mixed_orthogonality")
    if mixed["classification"]["all_standard_mixed_blocks_zero"] is not True:
        raise AssertionError("mixed-block classification drifted")
    if mixed["theorem"]["conclusion"]["mixed_matrix_between_four_declared_block_families"] != "0":
        raise AssertionError("mixed-block matrix replay failed")

    physical = _record(value, "physical_ell1")
    rel_phys = _matrix(physical["theorem"]["normalized_direct_sum_theorem"]["relative_operator"])
    if rel_phys != 4 * sp.eye(2):
        raise AssertionError("physical ell1 pullback replay failed")
    physical_q2_multiplier = 2 * (rel_phys[0, 0] - 1)
    if physical_q2_multiplier != 6:
        raise AssertionError("physical ell1 q2 multiplier replay failed")

    homogeneous = _record(value, "homogeneous")
    forms = homogeneous["theorem"]["cauchy_forms_after_common_factor_2piL"]
    omega_rel = _matrix(forms["weyl_maxwell"]) - _matrix(forms["einstein_maxwell"])
    d_hom = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
        ]
    )
    homogeneous_hessian = sp.simplify(omega_rel * d_hom)
    expected_homogeneous = sp.zeros(6)
    expected_homogeneous[1, 1] = -3
    if homogeneous_hessian != expected_homogeneous:
        raise AssertionError("homogeneous q2 replay failed")

    twist = _record(value, "twist")
    twist_forms = twist["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]
    twist_rel = _matrix(twist_forms["weyl_maxwell"]) - _matrix(twist_forms["einstein_maxwell"])
    twist_hessian = sp.simplify(twist_rel * sp.Matrix([[0, 1], [0, 0]]))
    if twist_hessian != sp.diag(0, 6):
        raise AssertionError("twist H q2 replay failed")
    moments = _record(value, "exceptional_global_moments")
    if moments["axial_twist"]["mu_J"] != "-4*A cross B in an oriented orthonormal real ell=1 basis":
        raise AssertionError("target twist rotation moment drifted")
    # Omega_WM=-2 Omega_EM, so mu_EM,J=2 A x B and mu_rel,J=-6 A x B.
    if value["operation"]["blocks"]["axial_twist_ell1_k0"]["formula_J"] != (
        "q2_charge,J(u,v)=-6*(A_u cross B_v+A_v cross B_u)"
    ):
        raise AssertionError("twist rotation Hessian replay failed")

    complete = _record(value, "complete_smooth_taub")
    if complete["complete_output_cokernel_theorem"]["decomposition"] != (
        "coker L_smooth = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}"
    ):
        raise AssertionError("five-charge completeness drifted")
    dictionary = _record(value, "relative_dictionary")
    required_rows = {
        "ph.generic.axial.relative",
        "ph.generic.polar.relative",
        "ph.exceptional.ell1.relative",
        "ph.exceptional.ell1.nonzero_k.relative",
        "ph.global.homogeneous.relative",
        "ph.global.twist.relative",
    }
    if not required_rows.issubset({row["id"] for row in dictionary["branch_rows"]}):
        raise AssertionError("relative dictionary block coverage drifted")

    flags = value["classification"]
    forbidden = (
        "constant_u1_charge_output",
        "extra_weyl_target_cofiber_inputs_included",
        "bounded_or_smooth_tangent_cone_solved_by_this_artifact",
        "off_shell_local_jet_charge_q2",
        "support_local_bv_koszul_extension",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    )
    if any(flags[key] is not False for key in forbidden):
        raise AssertionError("forbidden downstream promotion")
    return {
        "status": "PASS",
        "standard_blocks": 4,
        "charge_outputs": 5,
        "physical_ell1_q2_multiplier": str(physical_q2_multiplier),
        "homogeneous_H_hessian_rank": homogeneous_hessian.rank(),
        "twist_H_hessian_rank_per_real_harmonic": twist_hessian.rank(),
        "cross_block_terms": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
