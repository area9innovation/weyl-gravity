#!/usr/bin/env python3
"""Produce the fail-closed axial one-sided Krein scattering preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"

IMPORT_PATHS = {
    "incoming_extended_domain": (
        "black_hole_programme/phase3/"
        "axial_incoming_extended_domain_audit/certificate.json"
    ),
    "incoming_connection": (
        "black_hole_programme/phase3/"
        "axial_incoming_connection_analytic/certificate.json"
    ),
    "future_horizon_gram": (
        "black_hole_programme/phase3/"
        "axial_horizon_grassmann_mobius_to_r4_taylor2/"
        "future_horizon_outward_gram.json"
    ),
    "future_horizon_factor_quotient": (
        "black_hole_programme/phase3/"
        "axial_horizon_grassmann_mobius_to_r4_taylor2/"
        "future_horizon_factor_quotient.json"
    ),
    "global_channel_gate": (
        "black_hole_programme/phase3/"
        "axial_global_finite_flux_channel_classification/certificate.json"
    ),
}
SOURCE_PATHS = {
    "horizon_gram_producer": (
        "black_hole_programme/phase3/"
        "axial_horizon_grassmann_mobius_to_r4_taylor2/"
        "horizon_gram_laurent.py"
    ),
    "horizon_recurrence_producer": (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/produce.py"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_imports() -> tuple[dict[str, dict], dict[str, dict]]:
    documents: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    for name, relative in IMPORT_PATHS.items():
        path = ROOT / relative
        documents[name] = json.loads(path.read_text())
        provenance[name] = {
            "path": relative,
            "sha256": sha256(path),
        }
    return documents, provenance


def conjugate(value: sp.Expr, omega: sp.Symbol) -> sp.Expr:
    return sp.conjugate(value).subs(sp.conjugate(omega), omega)


def parse_matrix(rows: list[list[str]], omega: sp.Symbol) -> sp.Matrix:
    local = {"omega": omega, "I": sp.I}
    return sp.Matrix([
        [sp.sympify(value, locals=local) for value in row]
        for row in rows
    ])


def produce() -> dict:
    imports, provenance = load_imports()
    source_provenance = {
        name: {"path": relative, "sha256": sha256(ROOT / relative)}
        for name, relative in SOURCE_PATHS.items()
    }
    horizon_document = imports["future_horizon_gram"]
    incoming_document = imports["incoming_extended_domain"]
    connection_document = imports["incoming_connection"]
    gate_document = imports["global_channel_gate"]

    omega = sp.Symbol("omega", real=True, positive=True)
    horizon = parse_matrix(
        horizon_document["gram_without_pi_alpha_W"], omega
    )
    incoming_factor = parse_matrix(
        incoming_document["factor_adapted_Iminus_gram"][
            "gram_over_pi_alpha_W"
        ],
        omega,
    )
    # The displayed factor-adapted incoming change has determinant -3 i omega.
    # Tminus is recorded in the determinant-one raw Iminus factor frame, so
    # undo that congruence before comparing determinants.
    factor_change_determinant_modulus_squared = 9 * omega ** 2
    det_horizon = sp.factor(horizon.det())
    det_incoming_factor = sp.factor(incoming_factor.det())
    det_incoming_raw = sp.factor(
        det_incoming_factor / factor_change_determinant_modulus_squared
    )
    determinant_ratio = sp.factor(det_horizon / det_incoming_raw)

    prefactor_modulus_squared = sp.sympify(
        incoming_document["uniform_pilot_margin"][
            "prefactor_modulus_squared_in_x"
        ],
        locals={"x": omega ** 2},
    )
    prefactor_modulus_squared = sp.factor(prefactor_modulus_squared)
    if sp.cancel(determinant_ratio - prefactor_modulus_squared) != 0:
        raise RuntimeError("endpoint determinant ratio does not match Tminus")

    j0 = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    jsigma = sp.diag(1, -1, -1)
    q = sp.Matrix([
        [1 / sp.sqrt(2), 1 / sp.sqrt(2), 0],
        [1 / sp.sqrt(2), -1 / sp.sqrt(2), 0],
        [0, 0, 1],
    ])
    if sp.simplify(q.conjugate().T * j0 * q - jsigma) != sp.zeros(3):
        raise RuntimeError("null/signature congruence changed")

    gate_flags = gate_document["claim_flags"]
    physical_activation = (
        gate_document["lifecycle"] == "CLASSIFIED"
        and gate_flags["global_connection_imported"]
        and gate_flags["current_conservation_on_populated_quotient"]
        and gate_flags["one_sided_J_isometry_certified"]
    )
    if physical_activation:
        raise RuntimeError("preflight expected the global gate to remain closed")

    document = {
        "schema": "phase3-axial-one-sided-krein-scattering-preflight-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_ONE_SIDED_KREIN_PREFLIGHT",
        "result_token": "BH_PHASE3_AXIAL_ONE_SIDED_KREIN_METHOD_SHORTFALL",
        "lifecycle": "CLASSIFIED",
        "status": "METHOD_SHORTFALL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "frequency_scope": "real omega in [1/2,3/4]",
            "phase": "exp(+I*omega*t)",
            "normalization": "all endpoint Grams divided by pi*alpha_W",
        },
        "basis_contract": {
            "signature_basis": {
                "name": "J_sigma",
                "matrix": [["1", "0", "0"], ["0", "-1", "0"], ["0", "0", "-1"]],
            },
            "triangular_null_basis": {
                "name": "J0",
                "matrix": [["0", "1", "0"], ["1", "0", "0"], ["0", "0", "-1"]],
            },
            "null_to_signature_columns": [
                ["1/sqrt(2)", "1/sqrt(2)", "0"],
                ["1/sqrt(2)", "-1/sqrt(2)", "0"],
                ["0", "0", "1"],
            ],
            "congruence": "Q^dagger*J0*Q=J_sigma",
            "warning": (
                "J_sigma and J0 are congruent but not equal; triangular "
                "component identities are stated only in J0."
            ),
        },
        "conditional_exact_theorem": {
            "hypotheses": [
                "Gminus, Gplus and Hout are nondegenerate Hermitian 3x3 forms of inertia (1,2,0)",
                "Tminus is invertible",
                "the typed raw Stokes identity Hout+Tplus^dagger*Gplus*Tplus-Tminus^dagger*Gminus*Tminus=0 holds",
                "Nminus^dagger*Gminus*Nminus=Nplus^dagger*Gplus*Nplus=N_H^dagger*Hout*N_H=J for one common J in {J0,J_sigma}",
            ],
            "raw_maps": {
                "Rraw": "Tplus*Tminus^(-1)",
                "raw_defect": (
                    "Gminus-Rraw^dagger*Gplus*Rraw="
                    "Tminus^(-dagger)*Hout*Tminus^(-1)"
                ),
            },
            "normalized_maps": {
                "Tminus_hat": "Nminus^(-1)*Tminus*N_H",
                "Tplus_hat": "Nplus^(-1)*Tplus*N_H",
                "normalized_frame_shorthand": (
                    "after hats are adopted, R=Tplus*Tminus^(-1) "
                    "and A=Tminus^(-1)"
                ),
                "R": "Nplus^(-1)*Tplus*Tminus^(-1)*Nminus",
                "A": "N_H^(-1)*Tminus^(-1)*Nminus",
                "Sstack": "vertical_stack(R,A)",
                "target_form": "J direct_sum J",
                "identity": "Sstack^dagger*(J direct_sum J)*Sstack=J",
            },
            "reflection_defect": {
                "D": "J-R^dagger*J*R=A^dagger*J*A",
                "inertia": [1, 2, 0],
                "reason": "A is invertible, so D is congruent to J",
                "determinant_general": (
                    "det(D)=abs(det(Nminus))^2/"
                    "(abs(det(NH))^2*abs(det(Tminus))^2)"
                ),
                "determinant_endpoint_ratio": (
                    "det(D)=det(Hout)/(det(Gminus)*abs(det(Tminus))^2)"
                ),
                "determinant_axial_simplified": (
                    "det(D)=1/(abs(A_in_2)^4*abs(A_in_1)^2)"
                ),
                "normalized_Tminus_formula": (
                    "det(D)=abs(det(Tminus_hat))^(-2)"
                ),
                "rejected_bare_formula": (
                    "det(D)=abs(det(Tminus_raw))^(-2)"
                ),
                "rejection_reason": (
                    "the endpoint normalizer determinant ratio is the "
                    "nonunit rational prefactor modulus squared"
                ),
            },
            "completion": {
                "statement": (
                    "The nondegenerate J-isometric embedding Sstack has a "
                    "(J direct_sum J)-orthogonal complement of inertia "
                    "(1,2,0); choosing any J-isometry C onto that complement "
                    "makes U=[Sstack C] an element of U(2,4)."
                ),
                "existence": "ALGEBRAIC_CONDITIONAL",
                "canonical": False,
                "physical_full_scattering_matrix": False,
            },
        },
        "determinant_audit": {
            "horizon_raw_determinant": sp.sstr(det_horizon),
            "incoming_factor_basis_determinant": sp.sstr(det_incoming_factor),
            "incoming_factor_to_raw_determinant_modulus_squared": "9*omega**2",
            "incoming_raw_determinant": sp.sstr(det_incoming_raw),
            "endpoint_normalizer_determinant_ratio": sp.sstr(determinant_ratio),
            "Tminus_rational_prefactor_modulus_squared": sp.sstr(
                prefactor_modulus_squared
            ),
            "ratio_matches_prefactor": True,
            "consequence": (
                "the normalization ratio cancels the rational Tminus "
                "prefactor, leaving the inverse Jost-amplitude product"
            ),
        },
        "triangular_J0_identities": {
            "scope": (
                "pure algebra only; no imported certificate proves that the "
                "normalized physical R and A have this triangular form"
            ),
            "upper_triangular_convention": (
                "X=[[a_X,b_X,d_X],[0,c_X,e_X],[0,0,f_X]], X in {R,A}"
            ),
            "independent_equations": [
                "sum_X conjugate(a_X)*c_X=1",
                "sum_X conjugate(a_X)*e_X=0",
                "sum_X (conjugate(b_X)*c_X+conjugate(c_X)*b_X)=0",
                "sum_X (conjugate(b_X)*e_X+conjugate(c_X)*d_X)=0",
                "sum_X (conjugate(d_X)*e_X+conjugate(e_X)*d_X-abs(f_X)^2)=-1",
            ],
            "lower_triangular_convention": (
                "X=[[a_X,0,0],[b_X,c_X,0],[d_X,e_X,f_X]], X in {R,A}"
            ),
            "lower_independent_equations": [
                "sum_X (conjugate(a_X)*b_X+conjugate(b_X)*a_X-abs(d_X)^2)=0",
                "sum_X (conjugate(a_X)*c_X-conjugate(d_X)*e_X)=1",
                "sum_X conjugate(d_X)*f_X=0",
                "sum_X abs(e_X)^2=0, hence e_R=e_A=0",
                "sum_X abs(f_X)^2=1",
            ],
            "alpha_gamma_mu_reduction": "REFUSED_NOT_PROVED",
            "reason": (
                "triangularity in the normalized J0 frame, the off-diagonal "
                "entries, and the full typed Tplus entries are not certified; "
                "the conservation equations do not reduce to three diagonal "
                "parameters by themselves"
            ),
        },
        "Tplus_disposition": {
            "scalar_outgoing_coefficients_exist_in_Jost_expansions": True,
            "typed_full_3x3_Tplus_entries_certified": False,
            "typed_Tplus_normalization_certified": False,
            "Tplus_rank_certified": connection_document["claim_flags"][
                "Tplus_rank_certified"
            ],
            "reflection_nonvanishing_certified": connection_document[
                "claim_flags"
            ]["reflection_amplitudes_nonzero_certified"],
            "global_current_conservation_defect_certified": gate_flags[
                "current_conservation_on_populated_quotient"
            ],
        },
        "horizon_positive_real_scope_audit": {
            "printed_gram_pivots_sign_regular_for_every_real_omega_gt_0": True,
            "printed_factor_quotient_sign_regular_for_every_real_omega_gt_0": True,
            "upstream_certificate_scope": horizon_document["frequency_interval"],
            "exact_local_formula_domain": "every real omega>0",
            "promoted_beyond_pilot": True,
            "symbolic_recurrence_audit": {
                "residue_rates": [
                    "0",
                    "0",
                    "0",
                    "-4*I*omega",
                    "-1-4*I*omega",
                    "-2-4*I*omega",
                ],
                "residue_eigenbasis_determinant": "-I*(2*omega-I)/8",
                "basis_denominator_factors": [
                    "2*omega-I",
                    "4*omega-I",
                    "4*omega-3*I",
                    "4*omega-5*I",
                    "omega-I",
                ],
                "positive_real_collisions": [],
                "compatible_resonances": [
                    "column=4 order=1 free=1 residual=0",
                    "column=5 order=1 free=1 residual=0",
                    "column=5 order=2 free=1 residual=0",
                ],
                "minimum_omitted_exact_cross_current_order": horizon_document[
                    "order_three_sufficiency"
                ]["minimum_omitted/exact_cross_current_order"],
                "constant_term_affected": horizon_document[
                    "order_three_sufficiency"
                ]["constant_term_affected"],
            },
            "reason": (
                "the recurrence and omitted-head power count are symbolic in "
                "omega; all actual basis denominators and the residue "
                "eigenbasis determinant are collision-free on omega>0; the "
                "three integer resonances have exact zero residual; and every "
                "printed inertia pivot and factor quotient has fixed sign "
                "there. This widens only the local horizon algebra, not the "
                "global scattering gate."
            ),
        },
        "activation": {
            "status": gate_document["activation"]["status"],
            "physical_one_sided_J_isometry_certified": False,
            "physical_reflection_defect_inertia_certified": False,
            "physical_U_2_4_completion_certified": False,
            "missing": [
                "the typed global 3x3 Tplus entries in the certified endpoint frames",
                "the orientation-correct global Stokes defect certificate",
                "the same-frame normalizer crosswalk consumed by the global handoff",
            ],
        },
        "claim_flags": {
            "J0_Jsigma_distinction_certified": True,
            "conditional_one_sided_Krein_theorem_certified": True,
            "conditional_reflection_defect_inertia_certified": True,
            "conditional_algebraic_U_2_4_completion_certified": True,
            "determinant_normalization_ratio_certified": True,
            "physical_one_sided_J_isometry_certified": False,
            "physical_reflection_defect_inertia_certified": False,
            "physical_full_scattering_matrix_constructed": False,
            "alpha_gamma_mu_reduction_certified": False,
            "horizon_gram_all_positive_real_provenance_promoted": True,
        },
        "imports": provenance,
        "source_provenance": source_provenance,
        "verification": {
            "command": (
                "python3 -m black_hole_programme.phase3."
                "axial_one_sided_krein_scattering_preflight.verify"
            ),
            "tests": (
                "python3 -m unittest -v black_hole_programme.phase3."
                "axial_one_sided_krein_scattering_preflight.tests.test_preflight"
            ),
        },
        "does_not_establish": [
            "a typed or numerically evaluated Tplus matrix",
            "the global Stokes identity on populated pilot-band channels",
            "a physical one-sided J-isometry or reflection defect",
            "a physical full scattering matrix or canonical U(2,4) completion",
            "an alpha/gamma/mu scattering parameterization",
            "stability, CPT positivity, particles, ghosts or quantum unitarity",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(
        f"status={result['status']} "
        "conditional_theorem=true physical_activation=false"
    )
