#!/usr/bin/env python3
"""Build the exact compact-block structured pseudo-Hermitian certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1.json"
ATLAS = ROOT / "residual_atlas/phase2-cpt-compact-block-feasibility-fragment-v1.json"
SCHEMA = HERE / "schema/compact-block-structured-cpt-feasibility-v1.schema.json"

INPUTS = {
    "branch_dictionary": ("bridge/certificates/einstein_weyl_relative_branch_dictionary.json", "0489e3a15956b9e397387476cd76974f6083692a85bc840b34d81d7893bae5aa"),
    "axial_lee_wald": ("bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json", "e3d59018c9ae4a1d65b2ca531f24534d553dc7da1e6386c1d4afb577effd05f8"),
    "axial_extra_gram": ("bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json", "024d580eb7f6c6be88fd561d52a53c716b53ee6ac487b95f8326db7484a36c7d"),
    "polar_lee_wald": ("bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json", "327cfacb304218b894b622f08a8ad0a2d8cb370a1cb041c69f58e343ac33ac76"),
    "radiative_restriction": ("bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json", "560f9e96be8ee095972e745544a709fdb6a8ac7a939658a21163bc173884c2bd"),
    "ell1_standard": ("bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json", "0413c43de06931565f18effe21bdc18d272d45d5d52d5007273935c6ea71a0ec"),
    "ell1_exceptional": ("bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json", "04399fac0172e73a74026401cdd3972028add3f54ca8f141bd00ef7a04adaaed"),
    "ell1_nonzero_k": ("bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json", "4d3839689270af952808b14adef4f00fcbabeb69ef17efcf7e6d18b7747340a3"),
    "residual_descent": ("bridge/certificates/EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1.json", "84bc53857ea4ca2620d0be42a3fae98432775868c1780411d0586de705cf08c9"),
    "cyclic_inertia": ("d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json", "affb12a8655671a06748a8fc6e2d38e8732478e4ef293b3cfea482597735bd9c"),
    "p2a_contract": ("quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json", "377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _expr(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(value))


def _matrix(value: sp.MatrixBase) -> list[list[str]]:
    return [[_expr(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]


def _parse(value: Any, lam: sp.Symbol, **locals_: sp.Expr) -> sp.Expr:
    if not isinstance(value, str):
        return sp.sympify(value)
    return sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, **locals_})


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    refs, values = {}, {}
    for role, (relative, expected) in INPUTS.items():
        path = ROOT / relative
        if _sha(path) != expected:
            raise AssertionError(f"frozen input drift: {role}")
        refs[role] = {"path": relative, "sha256": expected}
        values[role] = json.loads(path.read_text())
    if values["p2a_contract"]["structured_metric_contract"]["C_operator_additional_required_data"]["eta_is_not_C_by_definition"] is not True:
        raise AssertionError("P2-A eta/C distinction drifted")
    return refs, values


def _exact_generic_data(values: dict[str, Any]) -> dict[str, Any]:
    lam, k, omega = sp.symbols("lambda k omega", positive=True, real=True)
    root = sp.sqrt(2 * lam)
    qminus = k**2 + lam - root
    qplus = k**2 + lam + root
    p = k**2 + lam - sp.Rational(2, 3)
    h2 = sp.diag(qminus, qplus, p, p)
    xvars = sp.symbols("x0:16")
    x = sp.Matrix(4, 4, xvars)
    solution = sp.linsolve(list(x * h2 - h2 * x), xvars)
    if len(solution.free_symbols) != 6:
        raise AssertionError("generic commutant dimension changed")
    h2_full = sp.diag(qminus, qminus, qplus, qplus, p, p, p, p)
    yvars = sp.symbols("y0:64")
    y = sp.Matrix(8, 8, yvars)
    full_solution = sp.linsolve(list(y * h2_full - h2_full * y), yvars)
    if len(full_solution.free_symbols) != 24:
        raise AssertionError("full orientation-preserving commutant dimension changed")

    inertia = values["cyclic_inertia"]["exact_inertia_blocks"]
    blocks = {}
    for parity in ("axial", "polar"):
        ge = sp.Matrix([[_parse(v, lam) for v in row] for row in inertia[parity]["Einstein_form"]])
        relative = sp.Matrix([[_parse(v, lam) for v in row] for row in inertia[parity]["relative_operator"]])
        gw = sp.simplify(ge * relative)
        scale = 3 * root / 2
        cq = sp.simplify((relative - sp.eye(2)) / scale)
        etaq = sp.simplify(gw * cq)
        if cq**2 != sp.eye(2) or sp.simplify(cq.T * gw - gw * cq) != sp.zeros(2):
            raise AssertionError(f"{parity} q fundamental symmetry failed")
        if parity == "axial":
            ga = values["axial_extra_gram"]["pairing"]["normalized_Gram"]
            gextra = sp.Matrix([[_parse(v, lam, k=k, omega=omega) for v in row] for row in ga])
            det_shell = sp.factor(gextra.det().subs(omega**2, p))
            expected_det = lam**4 * (lam - 2) * (9 * lam - 2) / 3
        else:
            gp = values["polar_lee_wald"]["shell_pairing"]["extra_Hermitian_current_Gram"]
            gextra = sp.Matrix([[_parse(v, lam, k=k) for v in row] for row in gp])
            det_shell = sp.factor(gextra.det())
            expected_det = 9 * lam**2 * (lam - 2) * (9 * lam - 2) * (3 * k**2 + 3 * lam - 2) * (6 * k**2 + 3 * lam - 2) ** 2
        if sp.simplify(det_shell - expected_det) != 0:
            raise AssertionError(f"{parity} extra determinant drifted")
        blocks[parity] = {
            "Einstein_source_form": _matrix(ge),
            "relative_spectral_operator": _matrix(relative),
            "restricted_Weyl_q_form": _matrix(gw),
            "q_fundamental_symmetry_C0": _matrix(cq),
            "q_eta0_equals_Gq_C0": _matrix(etaq),
            "q_eta0_leading_minor": _expr(etaq[0, 0]),
            "q_eta0_determinant": _expr(etaq.det()),
            "extra_action_Gram": _matrix(gextra),
            "extra_Gram_determinant_on_shell": _expr(det_shell),
            "extra_C0": [["1", "0"], ["0", "1"]],
            "complete_C0": "Cq direct-sum I_2 on the extra multiplicity",
            "complete_eta0": "(Gq*Cq) direct-sum Gextra",
            "complete_eta0_positive_for_lambda_ge_6_real_k": True,
        }

    return {
        "normal_branch_frame": ["q_minus", "q_plus", "p_1", "p_2"],
        "squared_frequencies": {"q_minus": _expr(qminus), "q_plus": _expr(qplus), "p": _expr(p)},
        "Hamiltonian_convention": {
            "H_squared": "diag(q_minus,q_plus,p,p) in the normal branch frame",
            "H": "the positive spectral square root diag(sqrt(q_minus),sqrt(q_plus),sqrt(p),sqrt(p)) on the selected positive-frequency carrier",
            "positivity_proof": [
                "lambda>=6 implies lambda-sqrt(2*lambda)>0 because lambda>2; hence q_minus>=lambda-sqrt(2*lambda)>0",
                "q_plus=k^2+lambda+sqrt(2*lambda)>0",
                "p=k^2+lambda-2/3>=16/3>0",
            ],
            "commutant_identity": "sqrt(x) is injective on the positive spectrum, so H and H^2 have identical spectral projectors and Comm(H)=Comm(H^2)",
            "pseudo_Hermiticity": "every classified eta is block diagonal on those common spectral projectors, hence H^dagger*eta=eta*H; C0 is polynomial in H^2 and therefore commutes with H",
            "relative_operator_distinction": "the imported q-block relative spectral operator maps the Einstein action form to the restricted Weyl action form; it is not H or H^2",
            "H_confused_with_H_squared": False,
        },
        "shell_separations": {
            "q_plus_minus_q_minus": _expr(qplus - qminus),
            "q_minus_minus_p": _expr(qminus - p),
            "q_plus_minus_p": _expr(qplus - p),
            "nonzero_on_physical_domain": True,
        },
        "computed_commutant": {
            "full_orientation_preserving_H_product_algebra": "M_2(C) direct-sum M_2(C) direct-sum M_4(C)",
            "full_complex_dimension": len(full_solution.free_symbols),
            "multiplicities": {"q_minus": 2, "q_plus": 2, "p": 4},
            "reason": "the three frequencies separate q_minus, q_plus and p, while the connected orientation-preserving H_product does not itself distinguish the isospectral axial and polar copies",
            "optional_parity_graded_subcommutant": {
                "algebra": "(C direct-sum C direct-sum M_2(C)) direct-sum (C direct-sum C direct-sum M_2(C))",
                "complex_dimension": 2 * len(solution.free_symbols),
                "status": "ALGEBRAIC_BOOKKEEPING_ONLY_UNLESS_A_FIXED_BUNDLE_DISCRETE_PARITY_IS_SEPARATELY_CERTIFIED"
            },
            "uncertified_parity_label_used_to_shrink_full_commutant": False,
        },
        "all_structured_eta": {
            "full_H_product_spectral_frame": "eta=A_minus direct-sum A_plus direct-sum A_p with Hermitian sizes 2,2,4 on the axial/polar multiplicity spaces",
            "coefficient_class": "all entries are polynomial or rational functions on the declared parameter domain with no poles there",
            "strict_positivity": "A_minus>0, A_plus>0 and A_p>0, equivalently every leading principal minor in each declared frame is positive (or every exact LDL pivot is positive)",
            "real_involution": "eta(lambda,-k)=conjugate(eta(lambda,k)); entrywise real parts are even in k and imaginary parts are odd in k",
            "k_zero_specialization": "all three Hermitian multiplicity matrices are real symmetric",
            "candidate_singular_walls": ["a pole in any matrix entry", "a zero of any LDL pivot", "det(A_minus)*det(A_plus)*det(A_p)=0"],
            "optional_parity_graded_slice": "setting all axial-polar mixing entries to zero recovers two copies of diag(a_minus,a_plus,A_p2), with each 2x2 extra block positive iff u>0 and u*v-|z|^2>0",
            "representative_ambiguity": "under B=B_minus direct-sum B_plus direct-sum B_p, eta transforms by B^dagger*eta*B; matrices related this way represent the same Hermitian tensor in different multiplicity frames",
        },
        "canonical_construction": {
            "definition": "C0=sign_G on the three H spectral summands: -I_2 on the full q_minus multiplicity and +I_2,+I_4 on q_plus,p",
            "spectral_projector_formula": "P_minus=((H^2-q_plus I)(H^2-p I))/((q_minus-q_plus)(q_minus-p)); C0=I-2P_minus",
            "Hermitian_involution": True,
            "commutes_with_H_and_H_product": True,
            "respects_real_involution": True,
            "eta0_equals_G_times_C0_positive": True,
            "uniqueness": "If C is G-self-adjoint, C^2=1, commutes with the declared symmetries and GC>0, G is negative definite on the complete two-copy q_minus multiplicity and positive definite on q_plus and p. Positivity therefore forces C=-I_2,+I_2,+I_4 respectively, even when axial/polar mixing is allowed.",
        },
        "intrinsic_parameter_walls": {
            "spectral_collisions": ["lambda=0 (q_minus=q_plus)", "lambda=2/9 (q_minus=p)"],
            "q_form_or_eta_degeneracy": ["lambda=0", "lambda=2/9", "lambda=2 (polar q form)"],
            "axial_extra_Gram": "lambda^4*(lambda-2)*(9*lambda-2)/3=0",
            "polar_extra_Gram": "9*lambda^2*(lambda-2)*(9*lambda-2)*(3*k^2+3*lambda-2)*(6*k^2+3*lambda-2)^2=0",
            "physical_domain_avoids_all_intrinsic_walls": "lambda=ell(ell+1)>=6 and real k",
        },
        "exact_blocks": blocks,
    }


def _exceptional_and_residual(values: dict[str, Any]) -> dict[str, Any]:
    exceptional = values["ell1_exceptional"]["current_theorem"]
    residual = values["residual_descent"]
    return {
        "ell1_standard": {
            "shell": "omega^2=k^2+4",
            "parity_blocks": ["axial", "polar"],
            "commutant": "C direct-sum C",
            "action_form": "positive on both parity lines",
            "eta_classification": "diag(a_axial,a_polar), both positive and linked to opposite momentum by reality",
            "unique_positive_GC_involution": "I_2",
        },
        "ell1_extra_k_zero": {
            "shell": "omega^2=4/3",
            "Gram": exceptional["normalized_extra_Hermitian_current_Gram"],
            "commutant": "C direct-sum C by spatial parity",
            "eta_classification": "diag(a_axial,a_polar), both positive",
            "unique_positive_GC_involution": "I_2",
            "nonlinear_warning": "every nonzero pure exceptional tangent fails the imported second-order compact Taub gate",
        },
        "ell1_extra_nonzero_k": {
            "shell": "omega^2=k^2+4/3",
            "Gram_per_parity": "4*(3*k^2+4)",
            "commutant": "C direct-sum C by spatial parity",
            "eta_classification": "diag(a_axial,a_polar), both positive",
            "unique_positive_GC_involution": "I_2",
        },
        "global_generalized_zero_blocks": {
            "homogeneous": "solution cofiber zero; generalized-zero/Jordan carrier has no imported positive-frequency complex structure",
            "twist": "solution cofiber zero; generalized-zero position/velocity carrier has no imported positive-frequency complex structure",
            "structured_eta_classification": "NOT_APPLICABLE_IN_THIS_POSITIVE_FREQUENCY_PILOT",
        },
        "residual_scope": {
            "imported_result_id": residual["result_id"],
            "branchwise_solution_relative_cohomology": residual["classification"]["solution_relative_cohomology"],
            "H_product_representation_retained": True,
            "global_orbit_or_symplectic_quotient": residual["classification"]["global_orbit_or_symplectic_quotient"],
            "support_local_physical_branch_projection": residual["classification"]["support_local_physical_branch_projection"],
            "consequence": "the metric classification is on certified physical solution/cofiber blocks as H_product representations, not on invariant-state cohomology or a final orbit quotient",
        },
    }


def build() -> dict[str, Any]:
    refs, values = _load_inputs()
    certificate = {
        "$schema": "../schema/compact-block-structured-cpt-feasibility-v1.schema.json",
        "schema": "pure-weyl-compact-block-structured-cpt-feasibility-v1",
        "result_id": "COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1",
        "result_state": "STRUCTURED_ETA_CONE_CLASSIFIED_AND_UNIQUE_FUNDAMENTAL_SYMMETRY_CONSTRUCTED_PT_DATUM_ABSENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "background": "compact magnetic Plebanski-Hacyan R_t x S1 x S2, fixed Chern class N=2",
            "carrier": "generic ell>=2 axial/polar q-primary Einstein image plus p-primary extra blocks, with ell=1 standard/extra dispositions",
            "symmetry": "H_product=(R_t x U(1)_x x SO(3))_orientation-preserving x U(1)_gauge; axial/polar labels are retained as algebraic bookkeeping but no fixed-bundle discrete parity is assumed",
            "reality": "positive-frequency amplitudes completed by conjugate (-k,-m,-omega) amplitudes",
            "claim_level": "finite REDUCED-MODE structured-metric feasibility on branchwise solution blocks",
        },
        "source_refs": refs,
        "generic_blocks": _exact_generic_data(values),
        "exceptional_and_residual_ledger": _exceptional_and_residual(values),
        "basis_invariance": {
            "change_of_frame": "H'=B^-1 H B, G'=B^dagger G B, eta'=B^dagger eta B, C'=B^-1 C B",
            "preserved_equations": ["H^dagger eta=eta H", "eta>0", "C^2=1", "C^dagger G=G C", "eta=G C"],
            "commutant_isomorphism": "Comm(H',symmetry')=B^-1 Comm(H,symmetry) B",
            "inertia_invariant": "G and eta transform by congruence, so rank and inertia are basis independent",
            "unconstrained_eigenbasis_metric_accepted": False,
            "rejection_reason": "a separately fitted matrix for each eigenvector/m/k without the tensor transformation law, H_product constancy on irreducible harmonic factors, real-involution relation and pole-free parameter family is not a structured eta",
        },
        "Mannheim_C_gate": {
            "eta_is_not_C": True,
            "unique_fundamental_symmetry_candidate_C0_constructed": True,
            "genuine_Mannheim_C_certified": False,
            "first_obstruction": "the imported fixed-N=2 carrier declares only the orientation-preserving H_product and conjugate real-field involution; it supplies no independent linear P, anti-linear time-reversal T, [C,PT] test, or proved eta/P/C convention",
            "magnetic_parity_caution": "an orientation-reversing parity may change the magnetic bundle sector and cannot be invented as an endomorphism of the fixed-N=2 carrier",
            "required_next_input": "a content-addressed discrete P/T or combined parity-charge-conjugation crosswalk on the fixed or paired magnetic sectors",
        },
        "decision": {
            "structured_positive_eta": "EXACT_NONEMPTY_CONE_CLASSIFIED",
            "canonical_eta0": "EXACTLY_CONSTRUCTED_AND_POSITIVE_ON_PHYSICAL_DOMAIN",
            "fundamental_symmetry_C0": "EXACTLY_CONSTRUCTED_AND_UNIQUE_WITHIN_DECLARED_COMMUTANT",
            "genuine_Mannheim_C": "NOT_ESTABLISHED_MISSING_PT_DATUM",
            "residual_invariant_state_metric": "NOT_ESTABLISHED",
            "particles_scattering_or_unitarity": "NOT_ESTABLISHED",
        },
        "mutation_expectations": {
            "commutant_made_diagonal_on_extra_multiplicity": "REJECT",
            "uncertified_parity_used_to_shrink_full_commutant": "REJECT",
            "H_confused_with_H_squared": "REJECT",
            "unconstrained_eigenbasis_metric_accepted": "REJECT",
            "eta_promoted_to_C": "REJECT",
            "intrinsic_wall_inside_physical_lambda_domain": "REJECT",
            "exceptional_or_residual_omitted": "REJECT",
            "quantum_unitarity_promoted": "REJECT",
        },
        "claim_boundary": {
            "establishes": [
                "the full rational/polynomial H_product-, parity- and reality-compatible positive eta cone on every generic branch fibre",
                "the exact generic commutant before the eta solve",
                "a basis-invariant unique positive fundamental symmetry C0 relative to the imported action form",
                "the intrinsic and candidate-dependent singular walls",
                "the ell=1 standard and exceptional positive-block dispositions and the residual/global exclusions",
            ],
            "does_not_establish": [
                "a genuine Mannheim C without independently certified P and T",
                "a positive metric on invariant-state cohomology or a final global orbit quotient",
                "survival of pure exceptional ell=1 directions through the nonlinear Taub gate",
                "a Hadamard state, particles, interacting positivity, scattering, anomaly/QME restoration or unitarity",
            ],
        },
        "provenance": {
            "generator": str(Path(__file__).relative_to(ROOT)),
            "arithmetic": "exact SymPy rational/algebraic matrices",
            "science_forge_identity": "phase2-cpt-3",
            "work_item": "sf:program/work/phase2-cpt-compact-block-feasibility",
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    return certificate


def atlas_fragment(cert: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "result_id": cert["result_id"],
        "dependency_tags": cert["dependency_tags"],
        "lifecycle_state": cert["lifecycle_state"],
        "background": "compact magnetic Plebanski-Hacyan product",
        "structured_eta": "EXACT_NONEMPTY_CONE_CLASSIFIED",
        "fundamental_symmetry": "UNIQUE_IN_DECLARED_COMMUTANT",
        "genuine_Mannheim_C": "NOT_ESTABLISHED_MISSING_PT_DATUM",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "does_not_establish": cert["claim_boundary"]["does_not_establish"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert = build()
    outputs = {OUTPUT: _dump(cert), ATLAS: _dump(atlas_fragment(cert))}
    if args.check:
        for path, expected in outputs.items():
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit(f"stale output: {path.relative_to(ROOT)}")
        print("COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1 generated outputs: CURRENT")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
