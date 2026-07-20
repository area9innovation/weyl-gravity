"""Classify the smooth active-current divisors on candidates 17, 18 and 20."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.schema.json"
INPUTS = {
    "candidate17_20": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json",
    "candidate18": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json",
    "zero_varieties_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "zero_varieties_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def string_matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def third_transvectant_divisor() -> dict[str, object]:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    matrix = sp.Matrix(
        [
            [-f[3], 3 * f[2], -3 * f[1], f[0], 0],
            [-f[4], 2 * f[3], 0, -2 * f[1], f[0]],
            [0, -f[4], 3 * f[3], -3 * f[2], f[1]],
        ]
    )
    equations = matrix * sp.Matrix(g)
    jacobian = equations.jacobian((*f, *g))
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    ambient = sp.diag(*list((-angular).diagonal()), *list((sp.Rational(1, 16) * angular).diagonal()))

    point = (1, 0, 0, 0, 1, 1, 0, 1, 0, 1)
    at_point = dict(zip((*f, *g), point))
    jacobian_point = jacobian.subs(at_point)
    conormal_point = sp.simplify(jacobian_point * ambient.inv() * jacobian_point.T)
    tangent = sp.Matrix.hstack(*jacobian_point.nullspace())
    restricted = sp.simplify(tangent.T * ambient * tangent)
    if jacobian_point.rank() != 3 or conormal_point.rank() != 2:
        raise AssertionError("third-transvectant smooth divisor witness changed")
    if restricted.rank() != 6 or restricted.cols != 7:
        raise AssertionError("third-transvectant conormal/radical identity failed")
    if restricted.cols - restricted.rank() != conormal_point.cols - conormal_point.rank():
        raise AssertionError("third-transvectant nullities disagree")

    nondegenerate_point = (-2, -2, -2, -2, -1, 12, 12, 11, 9, 0)
    at_nondegenerate = dict(zip((*f, *g), nondegenerate_point))
    jacobian_nondegenerate = jacobian.subs(at_nondegenerate)
    conormal_nondegenerate = sp.simplify(
        jacobian_nondegenerate * ambient.inv() * jacobian_nondegenerate.T
    )
    if equations.subs(at_nondegenerate) != sp.zeros(3, 1):
        raise AssertionError("third-transvectant nondegenerate witness left the variety")
    if jacobian_nondegenerate.rank() != 3 or conormal_nondegenerate.det() != 8293671904:
        raise AssertionError("third-transvectant proper-divisor witness changed")

    barred = tuple(f"bar_{name}" for name in (*f, *g))
    return {
        "constraint_equations": [sp.sstr(value) for value in equations],
        "variable_order": [str(value) for value in (*f, *g)],
        "barred_variable_order": list(barred),
        "ambient_current_H": string_matrix(ambient),
        "smooth_locus_condition": "rank(J_3)=3",
        "conormal_matrix": "K_3(f,g)=J_3(f,g)*H_3^{-1}*J_3(f,g)^dagger",
        "complete_smooth_divisor_equation": "Delta_3(f,g)=det(K_3(f,g))=0",
        "corank_strata": "nullity(K_3)=r, equivalently all (4-r)-minors vanish and some (3-r)-minor is nonzero",
        "two_parity_product_divisor": "Delta_3(f_plus,g_plus)*Delta_3(f_minus,g_minus)=0",
        "two_parity_radical_dimension": "nullity(K_3^plus)+nullity(K_3^minus)",
        "two_parity_affine_presymplectic_quotient_dimension": "14-nullity(K_3^plus)-nullity(K_3^minus)",
        "exact_smooth_witness": {
            "point_f_g": [str(value) for value in point],
            "J_rank": jacobian_point.rank(),
            "K": string_matrix(conormal_point),
            "K_rank": conormal_point.rank(),
            "K_nullity": conormal_point.cols - conormal_point.rank(),
            "restricted_tangent_rank": restricted.rank(),
            "restricted_tangent_nullity": restricted.cols - restricted.rank(),
        },
        "exact_smooth_nondegenerate_witness": {
            "point_f_g": [str(value) for value in nondegenerate_point],
            "J_rank": jacobian_nondegenerate.rank(),
            "K": string_matrix(conormal_nondegenerate),
            "det_K": str(conormal_nondegenerate.det()),
            "K_rank": conormal_nondegenerate.rank(),
            "proves_divisor_is_proper": True,
        },
        "scope": "each normalized third-transvectant parity factor on candidates 17 and 20; the two factors are a direct product",
    }


def rank_one_divisor() -> dict[str, object]:
    wx, wy, b, r = sp.symbols("w_x w_y b r", positive=True)
    a = wx / 12 + wy / 4
    c = -wx / 12 + wy / 4
    positive = sp.Matrix([[a, c], [c, a]])
    coefficient = sp.simplify(r * positive.inv() - sp.eye(2) / b)
    coefficient_determinant = sp.factor(coefficient.det())
    expected = (2 * b * r - wy) * (6 * b * r - wx) / (b**2 * wx * wy)
    if sp.factor(coefficient_determinant - expected) != 0:
        raise AssertionError("candidate-18 aligned divisor changed")

    e0 = sp.Matrix([0, 0, 1, 0, 0])
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    alpha = 2
    rows = []
    for index in range(5):
        if index == alpha:
            continue
        row = sp.zeros(1, 5)
        row[0, alpha] = -e0[index]
        row[0, index] = e0[alpha]
        rows.append(row)
    chart_derivative = sp.Matrix.vstack(*rows)
    angular_factor = sp.simplify(chart_derivative * angular.inv() * chart_derivative.T)
    if angular_factor.det() == 0 or angular_factor.rank() != 4:
        raise AssertionError("candidate-18 rank-one chart ceased to be regular")

    root_rows = []
    for label, root, vector in (
        ("symmetric", wy / (2 * b), sp.Matrix([1, 1])),
        ("antisymmetric", wx / (6 * b), sp.Matrix([1, -1])),
    ):
        at_root = coefficient.subs(r, root).applyfunc(sp.factor)
        if at_root.rank() != 1 or at_root * vector != sp.zeros(2, 1):
            raise AssertionError(f"candidate-18 {label} divisor branch changed")
        root_rows.append(
            {
                "branch": label,
                "r_equals_abs_t_squared": sp.sstr(root),
                "internal_kernel": [str(value) for value in vector],
                "internal_conormal_rank": at_root.rank(),
                "full_conormal_nullity": 4,
                "full_active_affine_radical_dimension": 4,
                "full_affine_presymplectic_quotient_dimension_including_spectators": 18,
            }
        )

    return {
        "rank_one_chart": {
            "chart_condition": "f_alpha!=0, or the exchanged chart g_alpha!=0",
            "alpha": alpha,
            "equations": "F_i=f_alpha*g_i-f_i*g_alpha for i!=alpha",
            "one_factor_J_rank": 4,
            "two_factor_J_rank": 8,
        },
        "ambient_current": {
            "positive_internal_A": string_matrix(positive),
            "negative_absolute_internal": "b*I_2 with b=6*h_minus>0",
            "angular_W": [sp.sstr(value) for value in angular.diagonal()],
            "complete_H": "diag(A tensor W,-b*I_2 tensor W)",
        },
        "complete_smooth_divisor": {
            "conormal_matrix": "K_18=J_18*H_18^{-1}*J_18^dagger on every regular rank-one chart",
            "equation": "Delta_18=det(K_18)=0",
            "chart_invariance": "on chart overlaps K changes by invertible conormal congruence, so the zero set and nullity strata agree",
            "higher_corank_strata": "nullity(K_18)=r is decided by the determinantal ideals of K_18",
            "radical_map": "lambda maps to H_18^{-1}*J_18^dagger*lambda",
            "affine_presymplectic_quotient_dimension": "22-nullity(K_18), including the ten current-orthogonal positive spectators",
        },
        "aligned_section": {
            "base_angular_vector": [str(value) for value in e0],
            "angular_conormal_factor": string_matrix(angular_factor),
            "internal_conormal_factor": "C(r)=r*A^{-1}-I_2/b, up to invertible diagonal congruence by z",
            "det_C": sp.sstr(coefficient_determinant),
            "distinct_eigenvalue_witness": "3*w_y-w_x>0 from the imported exact interval certificate",
            "divisor_branches": root_rows,
        },
        "scope": "the complete smooth product of the two rank-one binary-quartic cones on candidate 18, with its ten positive current-orthogonal spectators",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    if not records["candidate17_20"]["classification"]["degenerate_points_are_bounded_second_order_tangents"]:
        raise AssertionError("candidate-17/20 bounded smooth witness changed")
    if not records["candidate18"]["classification"]["degenerate_points_are_bounded_second_order_tangents"]:
        raise AssertionError("candidate-18 bounded smooth witness changed")
    return {
        "schema": "einstein-maxwell-weyl-same-sign-active-presymplectic-divisors-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PRESYMPLECTIC_DIVISORS",
        "result_state": "CANDIDATE17_18_20_SMOOTH_CURRENT_DIVISORS_AND_LINEAR_PRESYMPLECTIC_QUOTIENTS_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_SMOOTH_ACTIVE_RESONANCE_VARIETIES_ON_CANDIDATES_17_18_20",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "three distinct compact Plebanski--Hacyan collision backgrounds, candidates 17, 18 and 20",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "complete smooth active resonance varieties only",
            "degree": 2,
            "parity": "both exact factorized parity channels",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "candidate-specific allowed compact momenta, never identified across rho",
            "omega": "candidate-specific certified SUM or DIFFERENCE collision",
        },
        "conormal_divisor_theorem": {
            "hypotheses": "H is an invertible ambient Hermitian current and the smooth resonance tangent is ker(J) with J of full row rank",
            "conormal_matrix": "K=J*H^{-1}*J^dagger",
            "radical_isomorphism": "ker(K) -> rad(H restricted to ker(J)), lambda -> H^{-1}*J^dagger*lambda",
            "radical_dimension": "nullity(K)",
            "nondegenerate_locus": "det(K)!=0",
            "degeneracy_divisor": "det(K)=0",
            "presymplectic_quotient": "ker(J)/rad with induced nondegenerate Hermitian current",
            "quotient_dimension": "dim ker(J)-nullity(K)",
        },
        "candidate17_20_third_transvectant": third_transvectant_divisor(),
        "candidate18_rank_one": rank_one_divisor(),
        "classification": {
            "candidate17_smooth_divisor_classified": True,
            "candidate18_smooth_divisor_classified": True,
            "candidate20_smooth_divisor_classified": True,
            "presymplectic_linear_quotient_on_every_smooth_stratum_classified": True,
            "higher_corank_strata_fail_closed_by_determinantal_ideals": True,
            "bounded_radical_witnesses_retained": True,
            "global_quotient_topology_classified": False,
            "occupation_strata_glued": False,
            "singular_locus_quotient_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The three nonlinear active links are not globally symplectic. Their complete smooth degeneracy loci are nevertheless exact determinantal divisors, and every smooth fibre has a canonical finite-dimensional presymplectic quotient. This is a local linear quotient theorem over the resonance variety, not a Hausdorff global quotient or an occupation-gluing theorem.",
        "next_gate": "classify the singular-locus quotient and occupation-stratum gluing, beginning with candidate 16; keep causal and final residual descent separate",
        "claim_boundary": "The theorem classifies smooth current-degeneracy loci and tangent-space presymplectic quotients on candidates 17, 18 and 20. It does not prove global quotient topology, constant-rank gluing across the divisor, singular-locus reduction, occupation gluing, all-orders integration, or causal, observational or quantum transport.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_presymplectic_divisors --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_active_presymplectic_divisors",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_active_presymplectic_divisors",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("active presymplectic-divisor certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PRESYMPLECTIC_DIVISORS: PASS")


if __name__ == "__main__":
    main()
