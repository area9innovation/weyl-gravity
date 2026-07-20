"""Classify the node-phase-reduced smooth divisors on candidates 17, 18 and 20."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.schema.json"
INPUTS = {
    "affine_divisors": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.json",
    "candidate17_20": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json",
    "candidate18": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def string_matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def third_transvectant_jacobian() -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], sp.Matrix, sp.Matrix]:
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
    return f, g, equations, equations.jacobian((*f, *g))


def third_transvectant_augmented_matrix(
    first: tuple[sp.Expr, ...],
    second: tuple[sp.Expr, ...],
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    f, g, equations, jacobian = third_transvectant_jacobian()
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    ratio = sp.Rational(1, 16)
    one_channel = sp.diag(*list((-angular).diagonal()), *list((ratio * angular).diagonal()))
    ambient = sp.diag(one_channel, one_channel)
    augmented = sp.zeros(8, 20)
    for channel, point in enumerate((first, second)):
        substitution = dict(zip((*f, *g), point))
        if equations.subs(substitution) != sp.zeros(3, 1):
            raise AssertionError("third-transvectant point left its resonance variety")
        augmented[3 * channel : 3 * channel + 3, 10 * channel : 10 * channel + 10] = jacobian.subs(substitution)
    f_first = sp.Matrix(first[:5])
    g_first = sp.Matrix(first[5:])
    f_second = sp.Matrix(second[:5])
    g_second = sp.Matrix(second[5:])
    augmented[6, :5] = -f_first.T * angular
    augmented[6, 10:15] = -f_second.T * angular
    augmented[7, 5:10] = ratio * g_first.T * angular
    augmented[7, 15:20] = ratio * g_second.T * angular
    normal_gram = sp.simplify(augmented * ambient.inv() * augmented.T)
    return ambient, augmented, normal_gram


def candidate17_20_phase_reduction() -> dict[str, object]:
    witness = (1, 0, 0, 0, 1, 1, 0, 1, 0, 1)
    ambient, augmented, normal = third_transvectant_augmented_matrix(witness, witness)
    horizontal = sp.Matrix.hstack(*augmented.nullspace())
    restricted = sp.simplify(horizontal.T * ambient * horizontal)
    if augmented.rank() != 8 or normal.rank() != 6:
        raise AssertionError("candidate-17/20 phase-reduced witness rank changed")
    if horizontal.cols != 12 or restricted.rank() != 10:
        raise AssertionError("candidate-17/20 horizontal radical changed")
    if normal.cols - normal.rank() != restricted.cols - restricted.rank():
        raise AssertionError("candidate-17/20 augmented conormal nullity mismatch")

    control = (1, 1, 0, 0, 0, 1, 0, 0, 0, 0)
    _, control_augmented, control_normal = third_transvectant_augmented_matrix(control, control)
    control_determinant = sp.factor(control_normal.det())
    if control_augmented.rank() != 8 or control_normal.rank() != 8 or control_determinant == 0:
        raise AssertionError("candidate-17/20 phase-reduced divisor became identically zero")

    return {
        "ambient_coordinate_order": "(f_plus,g_plus,f_minus,g_minus), five angular coefficients per block",
        "ambient_current": "diag(-W,W/16,-W,W/16), W=diag(1,1/4,1/6,1/4,1)",
        "resonance_rows": "the three T3 rows in each parity channel",
        "node_phase_horizontal_rows": [
            "C_minus=(-f_plus^dagger*W,0,-f_minus^dagger*W,0)",
            "C_plus=(0,g_plus^dagger*W/16,0,g_minus^dagger*W/16)",
        ],
        "augmented_matrix": "A_3=stack(J_T3_plus,J_T3_minus,C_minus,C_plus), shape 8x20",
        "complete_regular_reduced_divisor": "det(A_3*H_3^{-1}*A_3^dagger)=0",
        "important_nonfactorization": "the two total-node horizontal rows couple the parity factors, so the reduced equation is the full 8x8 determinant, not the product of the two affine 3x3 determinants",
        "regular_locus": "rank(A_3)=8 with both active node norms nonzero",
        "horizontal_complex_dimension": 12,
        "exact_bounded_witness": {
            "point_in_each_parity_channel": [str(value) for value in witness],
            "A_rank": augmented.rank(),
            "augmented_normal_Gram": string_matrix(normal),
            "augmented_normal_rank": normal.rank(),
            "reduced_current_radical_complex_dimension": normal.cols - normal.rank(),
            "horizontal_restricted_current_rank": restricted.rank(),
            "linear_presymplectic_quotient_complex_dimension": horizontal.cols - (normal.cols - normal.rank()),
            "local_leaf_quotient_real_dimension_on_this_constant_corank_stratum": 2
            * (horizontal.cols - (normal.cols - normal.rank())),
        },
        "exact_nondegenerate_control": {
            "point_in_each_parity_channel": [str(value) for value in control],
            "A_rank": control_augmented.rank(),
            "augmented_normal_rank": control_normal.rank(),
            "augmented_normal_determinant": str(control_determinant),
        },
        "background_scope": "the normalized carrier formula applies separately to candidates 17 and 20; their compact momenta and circumference backgrounds are not identified",
    }


def rank_one_chart_augmented(
    a: sp.Expr,
    c: sp.Expr,
    b: sp.Expr,
    t_first: sp.Expr,
    t_second: sp.Expr,
    *,
    second_sign: int = 1,
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    positive = sp.Matrix([[a, c], [c, a]])
    ambient = sp.diag(
        sp.eye(10),
        sp.kronecker_product(positive, angular),
        sp.kronecker_product(-b * sp.eye(2), angular),
    )
    alpha = 2
    point = sp.zeros(30, 1)
    point[10 + alpha] = 1
    point[15 + alpha] = second_sign
    point[20 + alpha] = t_first
    point[25 + alpha] = second_sign * t_second
    augmented = sp.zeros(10, 30)
    for channel, (f_offset, g_offset) in enumerate(((10, 20), (15, 25))):
        row = 4 * channel
        for index in range(5):
            if index == alpha:
                continue
            augmented[row, g_offset + index] = point[f_offset + alpha]
            augmented[row, f_offset + alpha] = point[g_offset + index]
            augmented[row, f_offset + index] = -point[g_offset + alpha]
            augmented[row, g_offset + alpha] = -point[f_offset + index]
            row += 1
    positive_covector = point.T * ambient
    augmented[8, :20] = positive_covector[:, :20]
    augmented[9, 20:] = positive_covector[:, 20:]
    normal_gram = sp.simplify(augmented * ambient.inv() * augmented.T)
    return ambient, augmented, normal_gram


def candidate18_phase_reduction(record: dict[str, object]) -> dict[str, object]:
    a, c, b, t_first, t_second = sp.symbols("a c b t_1 t_2", nonzero=True, real=True)
    _, augmented, normal = rank_one_chart_augmented(a, c, b, t_first, t_second)
    determinant = sp.factor(normal.det())
    internal = a**2 - a * b * (t_first**2 + t_second**2) + b**2 * t_first**2 * t_second**2 - c**2
    expected = -sp.Rational(128, 9) * (t_first**2 + t_second**2) * internal**4 / (
        b**7 * (a - c) ** 4 * (a + c) ** 3
    )
    if sp.factor(determinant - expected) != 0:
        raise AssertionError("candidate-18 phase-reduced aligned determinant changed")

    branch_rows = []
    for label, sign, root in (
        ("symmetric", 1, (a + c) / b),
        ("antisymmetric", -1, (a - c) / b),
    ):
        _, branch_augmented, branch_normal = rank_one_chart_augmented(
            a,
            c,
            b,
            sp.sqrt(root),
            sp.sqrt(root),
            second_sign=sign,
        )
        if branch_augmented.rank() != 10 or branch_normal.rank() != 6:
            raise AssertionError(f"candidate-18 {label} phase-reduced branch changed")
        branch_rows.append(
            {
                "branch": label,
                "base_internal_line": [1, sign],
                "abs_t_squared": sp.sstr(root),
                "A_rank": branch_augmented.rank(),
                "augmented_normal_rank": branch_normal.rank(),
                "reduced_current_radical_complex_dimension": branch_normal.cols - branch_normal.rank(),
                "horizontal_complex_dimension": 20,
                "linear_presymplectic_quotient_complex_dimension": 16,
                "local_leaf_quotient_real_dimension_on_this_constant_corank_stratum": 32,
            }
        )

    weights = record["active_current_reduction"]["active_positive_weights"]
    wy_upper = Fraction(weights["w_y_interval"]["upper"])
    if not weights["w_x_interval"]["positive"] or not weights["w_y_interval"]["positive"] or not wy_upper < 1:
        raise AssertionError("candidate-18 positive-weight bound changed")
    h_minus = sp.sympify(
        record["active_current_reduction"]["channel_current_matrices"]["h_minus"],
        locals={"sqrt": sp.sqrt},
    )
    b_actual = sp.factor(6 * h_minus)
    if sp.simplify(b_actual - (-6912 + 5760 * sp.sqrt(3))) != 0:
        raise AssertionError("candidate-18 negative current weight changed")
    # sqrt(3)>17/10 proves b>2880>1, while the imported exact interval gives 0<w_y<1.
    control_sign_identity = sp.factor(
        (sp.Symbol("w_x") / 12 + sp.Symbol("w_y") / 4) ** 2
        - sp.Symbol("b") * (sp.Symbol("w_x") / 12 + sp.Symbol("w_y") / 4)
        - (-sp.Symbol("w_x") / 12 + sp.Symbol("w_y") / 4) ** 2
    )
    expected_control = (
        sp.Symbol("w_x") * sp.Symbol("w_y")
        - sp.Symbol("b") * sp.Symbol("w_x")
        - 3 * sp.Symbol("b") * sp.Symbol("w_y")
    ) / 12
    if sp.factor(control_sign_identity - expected_control) != 0:
        raise AssertionError("candidate-18 control sign identity changed")

    return {
        "ambient_coordinate_order": "(ten positive current-orthogonal spectators,f_plus,f_minus,g_plus,g_minus)",
        "ambient_current": "diag(I_10,A tensor W,-b*I_2 tensor W), A=[[a,c],[c,a]], a=w_x/12+w_y/4, c=-w_x/12+w_y/4, b=6*h_minus",
        "rank_one_chart_atlas": {
            "charts_per_factor": 10,
            "product_chart_count": 100,
            "chart_rule": "choose any nonzero entry f_alpha or g_alpha of each rank-one 5x2 matrix and use the four equations f_alpha*g_i-f_i*g_alpha=0 for i!=alpha",
            "resonance_J_rank": 8,
            "node_phase_horizontal_rows": 2,
            "augmented_matrix_shape": "10x30",
            "chart_gluing": "on overlaps the eight conormal rows change by an invertible block matrix while the two node rows are fixed; augmented normal Grams are congruent and have the same determinant zero set and nullity",
        },
        "complete_regular_reduced_divisor": "det(A_18*H_18^{-1}*A_18^dagger)=0 on all 100 charts",
        "regular_locus": "both rank-one factors are nonzero, both total active node norms are nonzero, and rank(A_18)=10",
        "horizontal_complex_dimension": 20,
        "aligned_central_angular_section": {
            "angular_vector": ["0", "0", "1", "0", "0"],
            "augmented_normal_determinant": sp.sstr(determinant),
            "internal_factor": sp.sstr(internal),
            "branch_rows": branch_rows,
            "nondegenerate_control": {
                "t_1": "0",
                "t_2": "1",
                "internal_factor": "a^2-a*b-c^2=(w_x*w_y-b*w_x-3*b*w_y)/12",
                "exact_sign_proof": "the imported bounds give w_x>0 and 0<w_y<1; sqrt(3)>17/10 gives b=5760*sqrt(3)-6912>2880>1, hence w_x*w_y-b*w_x<0 and -3*b*w_y<0",
                "verdict": "STRICTLY_NEGATIVE_AND_NONZERO",
            },
        },
        "spectator_effect": "the ten spectators are included in H and in the total positive-node horizontal row; they are not discarded when forming the reduced divisor",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    affine_flags = records["affine_divisors"]["classification"]
    if not (
        affine_flags["candidate17_smooth_divisor_classified"]
        and affine_flags["candidate18_smooth_divisor_classified"]
        and affine_flags["candidate20_smooth_divisor_classified"]
    ):
        raise AssertionError("affine smooth-divisor input changed")
    if not records["candidate17_20"]["classification"]["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]:
        raise AssertionError("candidate-17/20 bounded witness changed")
    if not records["candidate18"]["classification"]["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]:
        raise AssertionError("candidate-18 bounded witness changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-active-phase-reduced-presymplectic-divisors-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PHASE_REDUCED_PRESYMPLECTIC_DIVISORS",
        "result_state": "CANDIDATE17_18_20_SMOOTH_FIXED_OCCUPATION_NODE_PHASE_REDUCED_DIVISORS_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_SMOOTH_REGULAR_FIXED_OCCUPATION_NODE_PHASE_REDUCTION_ON_CANDIDATES_17_18_20",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "three distinct compact Plebanski--Hacyan collision backgrounds, candidates 17, 18 and 20",
            "boundaries": "closed S1_L times S2 before lifted-rotation or final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "complete smooth active resonance varieties at nonzero fixed active-node occupations, reduced by the two common node phases",
            "degree": 2,
            "parity": "both exact factorized parity channels, with their common node phases retained until this reduction",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "candidate-specific allowed compact momenta, never identified across rho",
            "omega": "candidate-specific certified SUM or DIFFERENCE collision",
        },
        "augmented_conormal_theorem": {
            "hypotheses": "H is invertible, the resonance Jacobian J has full row rank, the active node occupations are nonzero, and the two node-phase actions are free",
            "horizontal_model": "append the two complex Hermitian-orthogonality rows C_minus,C_plus to J; ker(A), A=stack(J,C), is a horizontal model for fixed norms modulo both node phases",
            "augmented_normal_Gram": "K_hat=A*H^{-1}*A^dagger",
            "radical_isomorphism": "ker(K_hat) -> rad(H restricted to ker(A)), lambda -> H^{-1}*A^dagger*lambda",
            "complete_reduced_divisor": "det(K_hat)=0 on every regular chart",
            "corank_strata": "the determinantal ideals of K_hat give the exact reduced-current corank",
            "linear_quotient": "ker(A)/rad carries a nondegenerate Hermitian current",
            "local_leaf_quotient": "on every smooth constant-corank stratum the kernel of the closed reduced Lee-Wald form is involutive; its local simple leaf space is symplectic",
        },
        "candidate17_20": candidate17_20_phase_reduction(),
        "candidate18": candidate18_phase_reduction(records["candidate18"]),
        "classification": {
            "candidate17_regular_fixed_occupation_phase_reduced_divisor_classified": True,
            "candidate18_regular_fixed_occupation_phase_reduced_divisor_classified": True,
            "candidate20_regular_fixed_occupation_phase_reduced_divisor_classified": True,
            "common_node_phase_coupling_retained": True,
            "candidate18_positive_spectators_retained": True,
            "linear_presymplectic_quotient_on_every_regular_reduced_tangent_classified": True,
            "constant_corank_local_leaf_quotient_classified": True,
            "bounded_rotation_zero_witnesses_retained": True,
            "lifted_rotation_reduction_classified": False,
            "global_leaf_space_or_Hausdorff_quotient_classified": False,
            "singular_locus_reduction_classified": False,
            "occupation_strata_glued": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The affine divisor theorem survives the physically relevant fixed-occupation node-phase descent, but its equation changes: the common node phases couple the parity factors, and candidate 18's positive spectators enter the horizontal row. The resulting augmented conormal determinants classify every regular reduced-current corank. Constant-corank strata have canonical local symplectic leaf quotients, while the global leaf space, lifted-rotation reduction and singular/occupation gluing remain open.",
        "next_gate": "classify candidate-16 singular topology and occupation-stratum gluing, then impose and quotient the lifted SO(3) zero fibre without conflating it with the node-phase reduction",
        "claim_boundary": "This is a complete smooth regular fixed-active-occupation, two-node-phase-reduced determinantal theorem on candidates 17, 18 and 20. It is not a lifted-rotation quotient, a global Hausdorff leaf-space theorem, a singular-locus or occupation-gluing theorem, a final residual descent, an all-orders extension, or a causal, observational or quantum map.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors",
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
        raise AssertionError("active phase-reduced presymplectic-divisor certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PHASE_REDUCED_PRESYMPLECTIC_DIVISORS: PASS")


if __name__ == "__main__":
    main()
