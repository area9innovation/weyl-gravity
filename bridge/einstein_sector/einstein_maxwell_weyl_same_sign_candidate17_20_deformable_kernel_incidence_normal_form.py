"""Certify the deformable-kernel zero-wall incidence normal form."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json"
)
SCHEMA = (
    ROOT
    / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.schema.json"
)
INPUTS = {
    "independent_node_scaling": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.json"
    ),
    "moving_square": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json"
    ),
    "singular_locus": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json"
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_algebra() -> dict[str, object]:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")

    def matrix(vector: tuple[sp.Symbol, ...]) -> sp.Matrix:
        v0, v1, v2, v3, v4 = vector
        return sp.Matrix(
            [
                [-v3, 3 * v2, -3 * v1, v0, 0],
                [-v4, 2 * v3, 0, -2 * v1, v0],
                [0, -v4, 3 * v3, -3 * v2, v1],
            ]
        )

    t_fg = sp.expand(matrix(f) * sp.Matrix(g))
    t_gf = sp.expand(matrix(g) * sp.Matrix(f))
    if sp.simplify(t_fg + t_gf) != sp.zeros(3, 1):
        raise AssertionError("odd third-transvectant antisymmetry changed")
    if sp.simplify(matrix(f) * sp.Matrix(f)) != sp.zeros(3, 1):
        raise AssertionError("third transvectant no longer vanishes on the diagonal")

    a, b, delta, x, y, s = sp.symbols(
        "a b delta x y s", real=True
    )
    c = delta + a * x - b * y
    left_x = sp.cancel(-delta / a)
    right_y = sp.cancel(delta / b)
    if sp.factor(c.subs({x: left_x, y: 0})) != 0:
        raise AssertionError("negative-delta boundary incidence changed")
    if sp.factor(c.subs({x: 0, y: right_y})) != 0:
        raise AssertionError("positive-delta boundary incidence changed")

    c_incidence = sp.factor(
        c.subs({x: s * x, y: s * y}).subs(delta, -a * x + b * y)
    )
    if c_incidence != sp.factor((1 - s) * (-a * x + b * y)):
        raise AssertionError("incidence-to-hub coefficient homotopy changed")

    u, r = sp.symbols("u r", real=True)
    radius = 3 * u / (2 + u**2)
    inverse_equation = sp.expand(r * u**2 - 3 * u + 2 * r)
    inverse_branch = (3 - sp.sqrt(9 - 8 * r**2)) / (2 * r)
    if sp.simplify(inverse_equation.subs(u, inverse_branch)) != 0:
        raise AssertionError("Cartan-square moment-radius inverse changed")
    if radius.subs(u, 0) != 0 or radius.subs(u, 1) != 1:
        raise AssertionError("Cartan-square moment-radius endpoints changed")

    return {
        "third_transvectant": {
            "matrix_A_f": [
                [sp.sstr(entry) for entry in row] for row in matrix(f).tolist()
            ],
            "odd_symmetry": "T3(f,g)=-T3(g,f)",
            "diagonal": "T3(f,f)=0",
            "homogeneity": "T3(sqrt(x)*f,sqrt(y)*g)=sqrt(x*y)*T3(f,g)",
        },
        "coefficient": {
            "formula": "c(F,G)=delta+a*||F||_W^2-b*||G||_W^2",
            "initial_value": "c(f,g)=alpha=delta+a-b for unit node directions",
            "hub_value": "c(0,0)=delta",
            "negative_delta_boundary": "||F||_W^2=-delta/a, G=0",
            "positive_delta_boundary": "F=0, ||G||_W^2=delta/b",
            "incidence_to_hub": "F_s=sqrt(s)F_*, G_s=sqrt(s)G_* gives c_s=(1-s)delta and M_s=0",
        },
        "cartan_square_path_lift": {
            "real_normal_form": "write z=x+i*y, use projective phase to impose x dot y=0, normalize |x|^2+|y|^2=1, and rotate the oriented orthogonal frame (x,y)",
            "moment_direction": "for nonzero moment the direction is the oriented normal x cross y",
            "canonical_radius": "r(u)=3*u/(2+u^2), 0<=u<=1",
            "inverse_branch": "u(r)=(3-sqrt(9-8*r^2))/(2*r), with u(0)=0",
            "inverse_polynomial": sp.sstr(inverse_equation),
            "endpoint_values": {"r(0)": "0", "r(1)": "1"},
            "connected_fibres": "for 0<r<=1 the inverse branch fixes the unordered norm ratio and the fibre is the connected rotation orbit about the moment axis; at r=0 the fibre is the connected phase-real RP2",
            "path_lifting": "on each interval with r>0, trivialize the oriented-frame bundle over the path interval and use u(r); at an isolated zero choose a common limiting real axis and use the connected r=0 fibre; prepend a path in the connected initial fibre",
        },
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    independent = records["independent_node_scaling"]["classification"]
    if not (
        independent["strict_opposite_sign_incidence_necessary"]
        and independent["strict_opposite_sign_incidence_sufficient"]
        and not independent["K_direction_deformation_classified"]
    ):
        raise AssertionError("fixed-direction predecessor changed")
    moving = records["moving_square"]["classification"]
    if not moving["normalized_cartan_square_moment_image_closed_ball"]:
        raise AssertionError("Cartan-square moment ball changed")
    singular = records["singular_locus"]
    if (
        singular["one_factor_singular_locus"]["ambient_kernel"]
        != "K_T3={(f,g) in C^5 x C^5:T3(f,g)=0}, irreducible of complex dimension seven"
    ):
        raise AssertionError("third-transvectant carrier changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-deformable-kernel-incidence-normal-form-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_INCIDENCE_NORMAL_FORM",
        "result_state": "STRICT_OPPOSITE_SIGN_DEFORMABLE_KERNEL_CONTRACTION_REDUCED_TO_ADMISSIBLE_COMPONENT_INCIDENCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_COMPACTIFIED_T3_KERNEL_DIRECTIONS_WITH_OCCUPATION_BOUNDARIES",
        "scope": {
            **records["independent_node_scaling"]["scope"],
            "background": "candidates 17 and 20 separately on their strict alpha*delta<0 fixed-total-occupation strata",
            "carrier": "the complete compactified T3(F,G)=0 kernel-amplitude carrier, including arbitrary direction deformation, zero-node boundaries, the common-square singular locus and all compact stabilizer orbit types",
        },
        "exact_algebra": exact_algebra(),
        "compactified_moduli": {
            "weighted_norm": "W=diag(1,1/4,1/6,1/4,1) on each spin-two node",
            "prequotient": "Kbar={(F,G) in C^5 x C^5:T3(F,G)=0, ||F||_W<=1, ||G||_W<=1}",
            "occupation_coordinates": "x=||F||_W^2 and y=||G||_W^2; no direction is introduced at a zero node",
            "group": "U(1)_F x U(1)_G x SO(3)_lifted",
            "orbit_space": "M=Kbar/(U(1)_F x U(1)_G x SO(3)_lifted)",
            "interior": "x*y>0 gives the projective T3 direction carrier modulo the lifted rotations",
            "one_node_boundaries": "x=0 or y=0 retain the full stabilizer of the vanished node and make T3=0 automatic",
            "origin": "x=y=0 has both node phases in its stabilizer and is the kernel vertex of the double-singular hub",
            "algebraic_singular_stratum": singular["one_factor_singular_locus"]["criterion"],
            "orbit_type_statement": "M is used as a compact stratified semialgebraic orbit space; no freeness, smoothness or division by x or y is assumed",
            "component_path_property": "compact real-algebraic group invariant theory makes M semialgebraic; every connected component is semialgebraically path connected, and the compact-group slice theorem lifts an orbit-space path locally across all orbit types",
        },
        "moment_map_and_admissible_base": {
            "unnormalized_node_moment": "m(F)_a=F^dagger*W*J_a*F and m(G)_a=G^dagger*W*J_a*G in the common normalization",
            "kernel_moment": "M_K(F,G)=-a*m(F)+b*m(G), with a=omega_minus*B_minus>0 and b=omega_plus*B_plus>0 after unit-direction normalization",
            "square_coefficient": "c(F,G)=delta+a*x-b*y",
            "rotation_zero_equation": "M_K+c*mu_square=0",
            "square_image": "mu_square(CP2) is the complete closed unit ball in so(3)^*",
            "admissible_prequotient": "A_tilde={(F,G) in Kbar:||M_K(F,G)||<=|c(F,G)|}",
            "admissible_orbit_space": "A=A_tilde/(U(1)_F x U(1)_G x SO(3)_lifted)",
            "zero_wall_incidence": "I={[F,G] in A:c(F,G)=0 and M_K(F,G)=0}",
            "semialgebraic_path_lifting": "lift the orbit-space path through compact-group slices; along the lifted path, -M_K/c is a semialgebraic path in the closed square-moment ball away from I; the explicit Cartan normal form and connected fibres lift it from the declared initial square direction, while at I the square direction is unconstrained",
        },
        "component_incidence_theorem": {
            "hypothesis": "alpha=c(F_0,G_0) and delta=c(0,0) have strict opposite signs",
            "necessity": "the projection of every rotation-zero contraction from the initial point to the hub is a path in A; c changes from alpha to delta, so at some point c=0 and the rotation equation forces M_K=0, hence the initial component of A meets I",
            "sufficiency_stage_1": "a component meeting I is semialgebraically path connected; lift a path from the initial base point to I through the Cartan-square moment map",
            "sufficiency_stage_2": "at c=M_K=0 the square direction is free, so move it within CP2 to a phase-real zero-moment direction",
            "sufficiency_stage_3": "scale (F_*,G_*) to (0,0); T3 remains zero, M_K remains zero and c=(1-s)delta, so the phase-real square direction completes the path to the connected hub",
            "equivalence": "a strict-opposite-sign rotation-zero point contracts to the double-singular hub if and only if its path component in A meets I",
            "fixed_direction_corollary": "on a fixed pair of projective T3 directions, A intersects I exactly under the previously certified positive-collinearity or one-zero-moment formulas",
        },
        "boundary_incidence": {
            "delta_negative_alpha_positive": {
                "inequality": "alpha=delta+a-b>0 implies 0<-delta/a<1",
                "witness": "choose G=0 and phase-real F with ||F||_W^2=-delta/a; then c=M_K=0",
            },
            "delta_positive_alpha_negative": {
                "inequality": "alpha=delta+a-b<0 implies 0<delta/b<1",
                "witness": "choose F=0 and phase-real G with ||G||_W^2=delta/b; then c=M_K=0",
            },
            "consequence": "I is nonempty in each strict opposite-sign chamber, but nonemptiness alone does not prove that every component of A meets I",
        },
        "candidate_disposition": {
            "candidate17": "on alpha>0, delta<0, contraction is equivalent to the candidate-17 admissible component meeting its nonempty y=0 boundary incidence",
            "candidate20_negative_delta": "on alpha>0, delta<0, contraction is equivalent to the candidate-20 admissible component meeting its nonempty y=0 boundary incidence",
            "candidate20_positive_delta": "on alpha<0, delta>0, contraction is equivalent to the candidate-20 admissible component meeting its nonempty x=0 boundary incidence",
            "separation": "the candidates share the normal-form proof but retain distinct backgrounds, coefficients, scalar-cone strata and atlas identifiers",
        },
        "classification": {
            "compactified_T3_kernel_moduli_defined": True,
            "node_phase_and_lifted_rotation_quotient_defined": True,
            "singular_stabilizers_and_boundary_occupations_retained": True,
            "square_moment_path_lifting_certified": True,
            "strict_opposite_sign_component_incidence_necessary": True,
            "strict_opposite_sign_component_incidence_sufficient": True,
            "candidate17_deformable_kernel_component_criterion_certified": True,
            "candidate20_deformable_kernel_component_criterion_certified": True,
            "both_strict_sign_boundary_incidence_sets_nonempty": True,
            "fixed_direction_theorem_recovered_as_fibrewise_corollary": True,
            "every_admissible_component_meets_incidence": False,
            "candidate17_complete_singular_rotation_zero_fibre_connected": False,
            "candidate20_off_balance_complete_singular_rotation_zero_fibre_connected": False,
            "global_zero_fibre_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Allowing the T3-kernel directions to move replaces the fixed positive-collinearity test by an invariant component-incidence problem. The zero wall is unavoidable, and the full square factor removes every obstruction except failure of the initial admissible component to reach M_K=c=0. Boundary incidence points always exist in both sign chambers, but a global connectedness claim now requires an exact classification of the components of A rather than irreducibility of the complex T3 variety alone.",
        "next_gate": "classify the path components of the compact semialgebraic admissible orbit space A and decide, separately for candidate 17 and the two candidate-20 strict-sign chambers, whether each component meets I; an exact component missing I is the requested counterexample",
        "claim_boundary": "This is an exact finite-carrier necessary-and-sufficient component criterion with all occupation boundaries and compact stabilizer strata retained. It does not assert that every admissible component meets incidence, prove complete candidate-17 or candidate-20 connectedness, identify the two candidates, glue total-occupation strata, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form",
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
        raise AssertionError("deformable-kernel incidence certificate is stale")
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_INCIDENCE_NORMAL_FORM: PASS"
    )


if __name__ == "__main__":
    main()
