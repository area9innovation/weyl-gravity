#!/usr/bin/env python3
"""Export the complete-standard-source relative five-charge q2 operation."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-complete-standard-five-charge-q2.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-complete-standard-five-charge-q2-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_complete_standard_charge_q2.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_complete_standard_charge_q2.py"

DEPENDENCIES = {
    "standard_radiative_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1.json",
    "standard_inclusion": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "physical_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "mixed_orthogonality": ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
    "exceptional_global_moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "complete_smooth_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "relative_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in rows])


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(matrix[i, j])) for j in range(matrix.cols)] for i in range(matrix.rows)]


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    standard_q2 = records["standard_radiative_q2"]
    inclusion = records["standard_inclusion"]
    physical = records["physical_ell1"]
    homogeneous = records["homogeneous"]
    twist = records["twist"]
    mixed = records["mixed_orthogonality"]
    moments = records["exceptional_global_moments"]
    complete = records["complete_smooth_taub"]
    dictionary = records["relative_dictionary"]

    if standard_q2["classification"]["five_charge_q2_on_standard_radiative_cohomology"] is not True:
        raise AssertionError("standard-radiative charge q2 is not certified")
    if inclusion["classification"]["complete_standard_harmonic_linear_restriction"] is not True:
        raise AssertionError("complete standard tangent is not certified")
    if inclusion["classification"]["complete_standard_mixed_block_orthogonality_directly_certified"] is not True:
        raise AssertionError("cross-block orthogonality is not certified")
    if mixed["classification"]["all_standard_mixed_blocks_zero"] is not True:
        raise AssertionError("dedicated mixed-block zero theorem is not certified")
    if mixed["theorem"]["conclusion"]["mixed_matrix_between_four_declared_block_families"] != "0":
        raise AssertionError("mixed-block matrix is nonzero")
    if complete["classification"]["complete_smooth_adjoint_cokernel_equals_five_stabilizers"] is not True:
        raise AssertionError("five-charge cokernel is not complete")
    if complete["classification"]["exceptional_and_global_inputs_included"] is not True:
        raise AssertionError("exceptional/global inputs are not included")

    block_ids = [row["id"] for row in dictionary["branch_rows"]]
    required_rows = {
        "ph.generic.axial.relative",
        "ph.generic.polar.relative",
        "ph.exceptional.ell1.relative",
        "ph.exceptional.ell1.nonzero_k.relative",
        "ph.global.homogeneous.relative",
        "ph.global.twist.relative",
    }
    if not required_rows.issubset(block_ids):
        raise AssertionError("relative branch dictionary is incomplete")

    physical_operator = physical["theorem"]["normalized_direct_sum_theorem"]["relative_operator"]
    if physical_operator != [["4", "0"], ["0", "4"]]:
        raise AssertionError("physical ell1 relative operator drifted")
    ell1_relative_multiplier = sp.Integer(4) - 1
    ell1_q2_multiplier = 2 * ell1_relative_multiplier

    homogeneous_forms = homogeneous["theorem"]["cauchy_forms_after_common_factor_2piL"]
    omega_em = _matrix(homogeneous_forms["einstein_maxwell"])
    omega_wm = _matrix(homogeneous_forms["weyl_maxwell"])
    omega_rel = omega_wm - omega_em
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
    if homogeneous_hessian != homogeneous_hessian.T:
        raise AssertionError("homogeneous relative H Hessian is not symmetric")
    expected_homogeneous_hessian = sp.zeros(6)
    expected_homogeneous_hessian[1, 1] = -3
    if homogeneous_hessian != expected_homogeneous_hessian:
        raise AssertionError("homogeneous relative H Hessian drifted")

    twist_forms = twist["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]
    twist_em = _matrix(twist_forms["einstein_maxwell"])
    twist_wm = _matrix(twist_forms["weyl_maxwell"])
    twist_rel = twist_wm - twist_em
    d_twist = sp.Matrix([[0, 1], [0, 0]])
    twist_hessian = sp.simplify(twist_rel * d_twist)
    if twist_hessian != twist_hessian.T or twist_hessian != sp.diag(0, 6):
        raise AssertionError("twist relative H Hessian drifted")
    if moments["axial_twist"]["mu_H"] != "2*|B|^2":
        raise AssertionError("target twist H moment drifted")
    if moments["axial_twist"]["mu_J"] != "-4*A cross B in an oriented orthonormal real ell=1 basis":
        raise AssertionError("target twist rotation moment drifted")

    output_basis = ["H", "P_x", "J_1", "J_2", "J_3"]
    return {
        "schema": "pure-weyl-relative-complete-standard-five-charge-q2-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_STANDARD_SOURCE_FIVE_CHARGE_Q2_EXACT_REDUCED_MODE",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1_L x S2",
            "boundaries": "closed Cauchy slice S1_L x S2 before final stabilizer quotient",
            "charge_sector": "fixed compact U(1) bundle P_N with N=2",
            "carrier": "complete certified standard Einstein-Maxwell solution cohomology",
            "degree": "symmetric arity-two output in the five-dimensional relative charge row",
            "parity": "generic axial/polar, physical ell1 axial/polar, homogeneous scalar and axial twist",
            "ell": "all certified standard blocks: ell>=2, physical ell=1, twist ell=1 and homogeneous ell=0",
            "m": "all real SO(3) multiplicities",
            "k": "all compact Fourier momenta where the corresponding standard block exists",
            "omega": "both generic Einstein branches, physical ell1 shell and generalized-zero blocks",
        },
        "dependencies": {name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()},
        "operation": {
            "name": "q2_relative_charge_complete_standard",
            "input": "two classes in the complete standard Einstein-Maxwell solution cohomology",
            "output_basis": output_basis,
            "output_dimension": 5,
            "definition": "q2_charge,X(u,v)=D^2[mu_WM,X(iota u)-mu_EM,X(u)]|_0(u,v)=<zeta_X,Delta2(u,v)>",
            "quadratic_relation": "mu_rel,X(u)=1/2*q2_charge,X(u,u)",
            "direct_sum_rule": "q2_charge is the orthogonal direct sum of the four displayed block operations; every cross-block coefficient is zero",
            "blocks": {
                "generic_radiative_ell_ge_2": {
                    "status": "IMPORTED_EXACT",
                    "formula": "the complete standard-radiative five-charge q2 artifact, with relative multipliers r_+=+(3/2)*sqrt(2*lambda) and r_-=-(3/2)*sqrt(2*lambda)",
                    "source": standard_q2["result_id"],
                },
                "physical_ell1_all_k": {
                    "status": "EXACT",
                    "relative_operator": "R_rel=4*I-I=3*I in source-normalized axial/polar quotient coordinates",
                    "formula": "q2_charge,X=6*B_EM,X for X in {H,P_x,J_1,J_2,J_3}",
                    "q2_multiplier_on_source_moment_polarization": str(ell1_q2_multiplier),
                    "source_normalized_current_matrix_Y10": physical["theorem"]["normalized_direct_sum_theorem"]["einstein_matrix"],
                    "target_normalized_current_matrix_Y10": physical["theorem"]["normalized_direct_sum_theorem"]["weyl_maxwell_matrix"],
                    "dispersion": physical["theorem"]["dispersion"],
                },
                "homogeneous_ell0": {
                    "status": "EXACT",
                    "coordinate_order": homogeneous["theorem"]["parameter_order"],
                    "omega_relative_after_common_factor_2piL": _matrix_strings(omega_rel),
                    "H_action_matrix": _matrix_strings(d_hom),
                    "q2_H_bilinear_matrix_after_common_factor_2piL": _matrix_strings(homogeneous_hessian),
                    "formula": "q2_charge,H(u,v)=-3*b_u*b_v; q2_charge,P_x=q2_charge,J_a=0",
                    "quadratic_relative_moment": "mu_rel,H=-3*b^2/2 after the common factor 2*pi*L",
                },
                "axial_twist_ell1_k0": {
                    "status": "EXACT",
                    "coordinate_order_per_real_harmonic": ["A", "B"],
                    "omega_relative_after_common_factor_L_N1m": _matrix_strings(twist_rel),
                    "H_action_matrix": _matrix_strings(d_twist),
                    "q2_H_bilinear_matrix_after_common_factor_L_N1m": _matrix_strings(twist_hessian),
                    "formula_H": "q2_charge,H(u,v)=6*B_u dot B_v",
                    "formula_Px": "q2_charge,P_x=0",
                    "formula_J": "q2_charge,J(u,v)=-6*(A_u cross B_v+A_v cross B_u)",
                    "quadratic_relative_moments": "mu_rel,H=3*|B|^2 and mu_rel,J=-6*A cross B",
                },
            },
            "constant_u1_component": "zero: constant U1 reducibility is not in the five-dimensional Taub cokernel",
        },
        "identities": {
            "symmetry": True,
            "reduced_arity_two_chain_identity": "q1*q2_charge+q2_charge(q1,.)+q2_charge(.,q1)=0 on the declared solution cohomology",
            "cohomology_domain": inclusion["theorem"]["solution_space_decomposition"]["identity"],
            "cross_block_orthogonality": inclusion["theorem"]["cross_block_orthogonality"]["conclusion"],
            "five_charge_completeness": complete["complete_output_cokernel_theorem"]["decomposition"],
            "taub_identity": complete["Taub_identification"]["formula"],
            "constant_u1_output": "zero",
        },
        "classification": {
            "complete_standard_source_five_charge_q2": True,
            "generic_radiative_included": True,
            "physical_ell1_all_momenta_included": True,
            "homogeneous_generalized_block_included": True,
            "axial_twist_block_included": True,
            "all_cross_block_terms_certified_zero": True,
            "constant_u1_charge_output": False,
            "extra_weyl_target_cofiber_inputs_included": False,
            "bounded_or_smooth_tangent_cone_solved_by_this_artifact": False,
            "off_shell_local_jet_charge_q2": False,
            "support_local_bv_koszul_extension": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "DERIVE_OR_OBSTRUCT_SUPPORT_LOCAL_CURRENT_DENSITY_BV_KOSZUL_LIFT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_complete_standard_charge_q2 --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_complete_standard_charge_q2",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_complete_standard_charge_q2",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-complete-standard-five-charge-q2-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact REDUCED-MODE operation covers the complete certified standard Einstein-Maxwell solution cohomology before the final stabilizer quotient. It includes generic radiative, physical ell1, homogeneous and twist inputs and outputs only the five connected-isometry Taub charges. It does not take extra Weyl target-cofiber modes as inputs, solve a bounded or smooth tangent cone, define an off-shell local-current or support-local BV/Koszul operation, repair the direct f2 obstruction, authorize arity three, or imply causal, observational, particle or quantum equivalence."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["classification"]["complete_standard_source_five_charge_q2"] is not True:
        raise AssertionError("complete-standard charge q2 theorem dropped")
    if value["classification"]["off_shell_local_jet_charge_q2"] is not False:
        raise AssertionError("reduced operation was promoted to an off-shell local operator")


def _report() -> str:
    return r"""# Complete-standard relative five-charge q2

The relative charge receiver now has an exact arity-two operation on the
complete certified standard Einstein--Maxwell solution cohomology:

\[
q^{\rm charge}_{2,X}(u,v)
=D^2\!\left[\mu_{{\rm WM},X}(\iota u)-\mu_{{\rm EM},X}(u)\right]_{0}(u,v)
=\langle\zeta_X,\Delta_2(u,v)\rangle .
\]

The five outputs are (H,P_x,J_1,J_2,J_3).  The certified standard tangent is
the orthogonal direct sum of four blocks, so the operation is block diagonal:

* generic radiative (ell>=2): the previously certified branch coefficients
  (r_\pm=\pm\frac32\sqrt{2\lambda});
* physical (ell=1), every compact momentum: the target pullback is (4) times
  the Einstein form, hence (q_2^{\rm charge}=6B_{\rm EM});
* homogeneous generalized block: after the common factor (2\pi L),
  (q_{2,H}(u,v)=-3b_ub_v), with the other four outputs zero;
* axial twist: after the declared harmonic factor,
  (q_{2,H}(u,v)=6B_u\!\cdot B_v) and
  (q_{2,J}(u,v)=-6(A_u\!\times B_v+A_v\!\times B_u)), while (P_x) is zero.

This closes the exceptional/global gap for **standard source cohomology**.
Extra fourth-order Weyl cofiber modes are target-only and are not inputs to
this relative source operation.  The result is still reduced-mode and global:
it does not construct a local current density, an off-shell BV/Koszul lift, a
repaired (f_2), or a causal nonlinear morphism.
"""


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _guards(value: dict) -> None:
    for key in (
        "extra_weyl_target_cofiber_inputs_included",
        "bounded_or_smooth_tangent_cone_solved_by_this_artifact",
        "off_shell_local_jet_charge_q2",
        "support_local_bv_koszul_extension",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("complete-standard charge q2 outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
