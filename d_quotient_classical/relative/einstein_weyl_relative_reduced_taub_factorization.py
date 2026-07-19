#!/usr/bin/env python3
"""Certify reduced smooth obstruction factorization through five Taub charges."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-reduced-taub-factorization.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-reduced-taub-factorization-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_reduced_taub_factorization.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_reduced_taub_factorization.py"
DEPENDENCIES = {
    "pullback_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1.json",
    "complete_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "complete_smooth_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "global_current_replay": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1.json",
    "f2_taub_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    deps = {name: _load(path) for name, path in DEPENDENCIES.items()}
    preflight = deps["pullback_preflight"]
    charges = deps["complete_charge_q2"]
    target = deps["complete_smooth_target"]
    replay = deps["global_current_replay"]
    obstruction = deps["f2_taub_obstruction"]
    basis = charges["operation"]["output_basis"]
    if basis != ["H", "P_x", "J_1", "J_2", "J_3"]:
        raise AssertionError("charge basis drifted")
    if target["complete_output_cokernel_theorem"]["decomposition"] != "coker L_smooth = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}":
        raise AssertionError("complete target obstruction quotient drifted")
    if not target["classification"]["complete_smooth_adjoint_cokernel_equals_five_stabilizers"]:
        raise AssertionError("five-dimensional obstruction completeness lost")
    if not charges["classification"]["complete_standard_source_five_charge_q2"]:
        raise AssertionError("complete charge q2 unavailable")
    if not replay["classification"]["slice_integral_matches_complete_five_charge_q2"]:
        raise AssertionError("local current/global charge replay lost")
    if preflight["relative_morphism_gate"]["factorization_matrix_computed"]:
        raise AssertionError("preflight unexpectedly precomputed factorization")
    identity = sp.eye(5)
    return {
        "schema": "pure-weyl-relative-reduced-taub-factorization-v1",
        "result_id": RESULT_ID,
        "result_state": "REDUCED_SMOOTH_OBSTRUCTION_CLASS_FACTORS_EXACTLY_THROUGH_FIVE_TAUB_CHARGES",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "scope": {
            **charges["scope"],
            "carrier": "symmetric source-pair module of the complete standard Einstein-Maxwell solution cohomology into the finite-harmonic smooth-secular Weyl-Maxwell target obstruction quotient",
            "degree": "arity-two target equation class modulo the smooth finite-harmonic target q1 image",
        },
        "dependencies": {name: _artifact(path, deps[name]) for name, path in DEPENDENCIES.items()},
        "obstruction_quotient": {
            "name": "O_smooth=coker(L_WM) after Noether and local gauge reduction",
            "dimension": 5,
            "adjoint_basis": ["zeta_H", "zeta_Px", "zeta_J1", "zeta_J2", "zeta_J3"],
            "coordinate_basis": basis,
            "coordinate_map": "chi_X([S])=(1/2)<zeta_X,S>",
            "coordinate_map_injective": True,
            "injectivity_reason": "the complete output theorem proves that simultaneous vanishing of all five pairings is necessary and sufficient for S to lie in the smooth finite-harmonic target image",
            "constant_u1_obstruction_coordinate": False,
        },
        "polarized_domain": {
            "definition": "B_standard=Sym^2(H^0(q1_EM)_standard)",
            "contains_all_cross_block_pairs": True,
            "real_structure": "finite real/conjugation-closed standard mode sets, then filtered union",
            "not_the_set_theoretic_quadratic_zero_cone": True,
            "serialized_all_mode_source_pair_matrix": False,
            "serialized_target_primal_obstruction_representatives": False,
        },
        "factorization": {
            "relative_moment_map": "mu_rel,pol,X(u,v)=(1/2)<zeta_X,Delta2(u,v)>",
            "identity": "chi([Delta2(u,v)])=mu_rel,pol(u,v)",
            "factor_map": "A=chi^(-1) on the normalized five-coordinate obstruction quotient",
            "matrix_input_basis": basis,
            "matrix_output_basis": basis,
            "matrix": [[str(identity[i, j]) for j in range(5)] for i in range(5)],
            "kernel_identity": "ker(D:B_standard->O_smooth)=ker(M_pol:B_standard->k^5)",
            "polarization_valid": True,
            "all_standard_blocks": ["generic_radiative_ell_ge_2", "physical_ell1_all_k", "homogeneous_ell0", "axial_twist_ell1_k0"],
            "all_cross_block_terms_zero": True,
        },
        "normalization_witness": {
            "mode": obstruction["local_delta2_normalization"]["fixture"],
            "mu_rel_H_diagonal": obstruction["taub_pairing"]["relative_half_delta2_pairing"],
            "expected": "-54*(1 + sqrt(3))/5",
            "nonzero": True,
        },
        "classification": {
            "reduced_mode_obstruction_factorization_exact": True,
            "normalized_quotient_coordinate_matrix_exact": True,
            "kernel_condition_exact": True,
            "complete_standard_blocks_included": True,
            "support_local_current_representatives_available": True,
            "serialized_all_mode_source_pair_matrix_computed": False,
            "target_primal_obstruction_representatives_exported": False,
            "support_local_relative_lift_constructed": False,
            "full_relative_q2_repaired": False,
            "bounded_correction_factorization_certified": False,
            "causal_retarded_factorization_certified": False,
            "arity_three_authorized": False,
            "observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CONSTRUCT_THE_SUPPORT_LOCAL_CURRENT_LEVEL_LIFT_OF_A_OR_RETURN_A_NORMALIZED_LOCALITY_OR_CYCLICITY_OBSTRUCTION",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_reduced_taub_factorization --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_reduced_taub_factorization",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_reduced_taub_factorization",
            ],
        },
        "claim_boundary": "This theorem is exact only in the complete finite-harmonic REDUCED-MODE source inventory with the SMOOTH_SECULAR target correction module. On the polarized domain Sym^2 H^0 it identifies the five normalized obstruction coordinates of the relative defect with the five polarized relative Taub moment maps and proves equality of their kernels. The displayed I5 is the normalized quotient-coordinate matrix of chi o A, not a serialized all-mode PBW source-pair solve or an export of five primal target representatives. It does not construct the required support-local current-level factor map, repair the full relative q2 on the 316-row carrier, compare the cotangent pairing with the action current, solve the stricter bounded correction problem, authorize arity three, or imply a Lorentzian-causal, observable, particle or quantum theorem.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Reduced Taub factorization

For the finite-harmonic smooth-secular target correction module, the complete
output theorem gives

\[
\mathcal O_{\rm smooth}=\operatorname{coker}L_{\rm WM},\qquad
\mathcal O_{\rm smooth}^{\vee}
=\operatorname{span}\{\zeta_H,\zeta_{P_x},\zeta_{J_1},\zeta_{J_2},\zeta_{J_3}\}.
\]

The normalized coordinate map

\[
\chi_X([S])=\frac12\langle\zeta_X,S\rangle
\]

is injective because the complete target theorem proves that simultaneous
vanishing of the five coordinates is sufficient for a finite source to lie
in the smooth target image.  The complete relative charge theorem and global
current replay give

\[
\chi([\Delta_2(u,v)])=\mu_{{\rm rel},{\rm pol}}(u,v)
\quad\text{on }\operatorname{Sym}^2H^0(q_{1,\rm EM}).
\]

Hence the factor map is `A=chi^(-1)` and its abstract quotient-coordinate
matrix is `I_5` in normalized charge/obstruction coordinates.  In particular,

\[
\ker D=\ker M_{\rm pol}
\]

on the declared symmetric source-pair module.  This is the theorem-level
finite factorization gate.  It is not a serialized all-mode source-pair
matrix, an export of primal obstruction representatives, or the support-local
current-level lift of `A`, and therefore does not repair the complete relative
q2.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("serialized_all_mode_source_pair_matrix_computed", "target_primal_obstruction_representatives_exported", "support_local_relative_lift_constructed", "full_relative_q2_repaired", "bounded_correction_factorization_certified", "causal_retarded_factorization_certified", "arity_three_authorized", "observable_particle_or_quantum_claim"):
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
    value = build(); validate(value)
    if args.write:
        OUTPUT.write_text(_render(value)); REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("reduced Taub factorization outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
