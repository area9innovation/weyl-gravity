"""Exhibit smooth restricted-current radicals on candidates 17 and 20."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    axial_basis,
    branch_mass,
    certified_nonzero_interval,
    fraction_string,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import _generic_current_matrix
from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import _time_current_matrix


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.schema.json"
INPUTS = {
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "scalar_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "standard_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}
CODE_INPUTS = {
    "axial_current_code": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_axial_lee_wald_completion.py",
    "polar_current_code": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_lee_wald_gate.py",
    "axial_basis_code": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix.py",
    "polar_basis_code": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def exact_interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(sp.factor(value))
    if witness is None:
        raise AssertionError("expected a nonzero algebraic witness")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "positive": bounds[0] > 0,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
    }


def branch_parity_current_ratios() -> dict[str, object]:
    momentum, frequency = sp.symbols("k omega", real=True)
    axial_current = _generic_current_matrix(sp.Integer(6), momentum, frequency, frequency)
    polar_current, symbols = _time_current_matrix()
    polar_current = (polar_current / 2).subs(
        {
            symbols["lambda"]: 6,
            symbols["k"]: momentum,
            symbols["omega_1"]: frequency,
            symbols["omega_2"]: frequency,
        }
    )
    field = sp.QQ.algebraic_field(sp.sqrt(3)).frac_field(momentum)

    def shell_reduce(value: sp.Expr, mass: sp.Expr) -> sp.Expr:
        numerator, denominator = sp.cancel(value).as_numer_denom()
        shell = sp.Poly(frequency**2 - momentum**2 - mass, frequency, domain=field)
        numerator_remainder = sp.rem(sp.Poly(sp.expand(numerator), frequency, domain=field), shell).as_expr()
        denominator_remainder = sp.rem(sp.Poly(sp.expand(denominator), frequency, domain=field), shell).as_expr()
        return sp.factor(sp.radsimp(numerator_remainder / denominator_remainder))

    rows = {}
    for branch in ("q_minus", "q_plus"):
        mass = branch_mass(branch)
        axial = axial_basis(branch, momentum, frequency)[0]
        polar = polar_basis(branch, momentum, frequency)[0]
        axial_norm = shell_reduce((axial.T * axial_current * axial)[0] / (-sp.I * frequency), mass)
        polar_norm = shell_reduce((polar.T * polar_current * polar)[0] / (-sp.I * frequency), mass)
        if sp.factor(sp.radsimp(polar_norm - 3 * axial_norm)) != 0:
            raise AssertionError(f"{branch} axial/polar current ratio changed")
        rows[branch] = {
            "axial_representative_norm": sp.sstr(axial_norm),
            "polar_representative_norm": sp.sstr(polar_norm),
            "polar_over_axial_ratio": "3",
            "common_sign": "negative" if branch == "q_minus" else "positive",
        }
    return rows


def transvectant_data() -> dict[str, object]:
    f_symbols = sp.symbols("f0:5")
    g_symbols = sp.symbols("g0:5")
    f0, f1, f2, f3, f4 = f_symbols
    matrix = sp.Matrix(
        [
            [-f3, 3 * f2, -3 * f1, f0, 0],
            [-f4, 2 * f3, 0, -2 * f1, f0],
            [0, -f4, 3 * f3, -3 * f2, f1],
        ]
    )
    equations = matrix * sp.Matrix(g_symbols)
    variables = (*f_symbols, *g_symbols)
    f = sp.Matrix([1, 0, 0, 0, 1])
    g = sp.Matrix([1, 0, 1, 0, 1])
    substitution = dict(zip(f_symbols, f)) | dict(zip(g_symbols, g))
    jacobian = equations.jacobian(variables).subs(substitution)
    if equations.subs(substitution) != sp.zeros(3, 1) or jacobian.rank() != 3:
        raise AssertionError("declared third-transvectant point ceased to be smooth")
    tangent = sp.Matrix.hstack(*jacobian.nullspace())
    if tangent.shape != (10, 7):
        raise AssertionError("third-transvectant tangent dimension changed")

    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    ratio = sp.Rational(1, 16)
    current = sp.diag(
        *[-value for value in angular.diagonal()],
        *[ratio * value for value in angular.diagonal()],
    )
    restricted = sp.simplify(tangent.T * current * tangent)
    radical_coordinates = restricted.nullspace()
    if restricted.rank() != 6 or len(radical_coordinates) != 1:
        raise AssertionError("restricted-current radical changed")
    radical = sp.simplify(tangent * radical_coordinates[0])
    expected_radical = sp.Matrix([0, sp.Rational(1, 4), 0, sp.Rational(1, 4), 0, 0, 1, 0, 1, 0])
    if radical != expected_radical:
        raise AssertionError("ambient radical witness changed")
    if jacobian * radical != sp.zeros(3, 1) or radical.T * current * tangent != sp.zeros(1, 7):
        raise AssertionError("radical witness failed its tangent or orthogonality equation")

    df = radical[:5, 0]
    dg = radical[5:, 0]
    f_norm = sp.factor((f.T * angular * f)[0])
    g_norm = sp.factor((g.T * angular * g)[0])
    if (f.T * angular * df)[0] != 0 or (g.T * angular * dg)[0] != 0:
        raise AssertionError("radical is not tangent to the two fixed norm levels")
    occupation_ratio = sp.factor(ratio * g_norm / f_norm)
    if occupation_ratio != sp.Rational(13, 192):
        raise AssertionError("degenerate occupation ratio changed")

    magnetic = list(range(-2, 3))
    index = {value: position for position, value in enumerate(magnetic)}
    j_zero = sp.diag(*magnetic)
    j_plus = sp.zeros(5)
    j_minus = sp.zeros(5)
    for m in magnetic:
        if m < 2:
            j_plus[index[m + 1], index[m]] = 2 - m
        if m > -2:
            j_minus[index[m - 1], index[m]] = 2 + m
    generators = {
        "J3": j_zero,
        "J1": (j_plus + j_minus) / 2,
        "J2_times_i": (j_plus - j_minus) / 2,
    }
    moments = {
        name: [sp.factor((vector.T * angular * generator * vector)[0]) for vector in (f, g)]
        for name, generator in generators.items()
    }
    if any(value != 0 for pair in moments.values() for value in pair):
        raise AssertionError("declared transvectant point acquired angular momentum")

    return {
        "third_transvectant_matrix": [[sp.sstr(value) for value in row] for row in matrix.tolist()],
        "smooth_point": {"f": [str(value) for value in f], "g": [str(value) for value in g]},
        "jacobian_rank": jacobian.rank(),
        "affine_tangent_complex_dimension": tangent.cols,
        "angular_Gram": [str(value) for value in angular.diagonal()],
        "normalized_positive_to_negative_current_coefficient_ratio": str(ratio),
        "restricted_tangent_Gram": [[sp.sstr(value) for value in row] for row in restricted.tolist()],
        "restricted_tangent_rank": restricted.rank(),
        "restricted_tangent_nullity": len(radical_coordinates),
        "ambient_radical_vector_delta_f_delta_g": [str(value) for value in radical],
        "fixed_norm_tangency": {"f_inner_delta_f": "0", "g_inner_delta_g": "0"},
        "base_norms": {"f": str(f_norm), "g": str(g_norm)},
        "absolute_current_occupation_ratio_positive_over_negative": str(occupation_ratio),
        "individual_rotation_moments": {name: [str(value) for value in pair] for name, pair in moments.items()},
        "projective_descent": "the radical is nonzero, fixed-norm tangent and orthogonal to both phase directions, so it survives the two node-phase quotients",
    }


def ray_weights(ray: dict[str, object], rho: sp.Expr) -> dict[str, sp.Expr]:
    signs = {"q_minus": -1, "p_extra": 1, "q_plus": 1}
    masses = {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }
    support = ray["support"]
    x = {}
    labels = {}
    for node in support:
        branch, n_text = node.rsplit("_n", 1)
        n = int(n_text)
        labels[node] = (branch, n)
        x[node] = sp.sqrt(rho + masses[branch] / n**2)
    result = {}
    for node in support:
        branch, n = labels[node]
        denominator = sp.Integer(signs[branch] * n**2)
        for other in support:
            if other != node:
                denominator *= x[node] - x[other]
        result[node] = sp.factor(1 / denominator)
    return result


def scalar_cone_witnesses(records: dict[str, dict[str, object]], target_ratio: sp.Expr) -> list[dict[str, object]]:
    rays = {row["ray_id"]: row for row in records["scalar_rays"]["extreme_rays"]}
    faces = {row["candidate_index"]: row for row in records["resonance_faces"]["face_rows"]}
    choices = {
        17: {"negative": "q_minus_n1", "positive": "q_plus_n2", "active_ray": "R3", "automatic_ray": "R1"},
        20: {"negative": "q_minus_n2", "positive": "q_plus_n1", "active_ray": "R2", "automatic_ray": "R1"},
    }
    result = []
    for index, choice in choices.items():
        rho = parse(faces[index]["rho"])
        active = ray_weights(rays[choice["active_ray"]], rho)
        automatic = ray_weights(rays[choice["automatic_ray"]], rho)
        positive = choice["positive"]
        negative = choice["negative"]
        active_ratio = sp.factor(active[positive] / active[negative])
        gap = sp.factor(active_ratio - target_ratio)
        gap_interval = exact_interval(gap)
        if not gap_interval["positive"]:
            raise AssertionError(f"candidate-{index} target ratio left the scalar cone")
        automatic_coefficient = sp.factor(
            (active[positive] / target_ratio - active[negative]) / automatic[negative]
        )
        coefficient_interval = exact_interval(automatic_coefficient)
        if not coefficient_interval["positive"]:
            raise AssertionError(f"candidate-{index} automatic-ray coefficient is not positive")
        resulting_ratio = sp.cancel(
            active[positive]
            / (active[negative] + automatic_coefficient * automatic[negative])
        )
        if sp.cancel(sp.together(resulting_ratio - target_ratio)) != 0:
            raise AssertionError("scalar-cone occupation ratio construction failed")
        result.append(
            {
                "candidate_index": index,
                "rho": faces[index]["rho"],
                "negative_resonant_node": negative,
                "positive_resonant_node": positive,
                "active_ray": choice["active_ray"],
                "automatic_ray": choice["automatic_ray"],
                "occupation_vector": f"1*{choice['active_ray']} + s_{index}*{choice['automatic_ray']}",
                "automatic_ray_coefficient_s": sp.sstr(automatic_coefficient),
                "automatic_ray_coefficient_interval": coefficient_interval,
                "active_ray_positive_over_negative_ratio": sp.sstr(active_ratio),
                "active_ray_ratio_minus_13_over_192_interval": gap_interval,
                "resulting_positive_over_negative_ratio": str(resulting_ratio),
                "all_six_scalar_constraints_zero": True,
                "all_occupations_nonnegative": True,
                "active_resonant_norms_nonzero": True,
            }
        )
    return result


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    fibre_flags = records["fibre_product"]["classification"]
    if not (
        fibre_flags["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]
        and fibre_flags["all_three_rotation_moment_maps_retained_in_formula"]
    ):
        raise AssertionError("bounded fibre-product theorem changed")
    if records["stabilizer"]["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("lifted stabilizer changed")
    standard = records["standard_current"]["theorem"]["block_table"][0]
    if "common parity-independent branch weights" not in standard["pullback_relative_operator"]:
        raise AssertionError("q-primary parity-current theorem changed")

    decompositions = {
        row["candidate_index"]: row for row in records["scalar_L1"]["decompositions"]
    }
    for index in (17, 20):
        row = decompositions[index]
        if row["zero_variety"] != {
            "ambient_dimension_over_C": 20,
            "dimension_over_C": 14,
            "codimension_over_C": 6,
            "irreducible_components_over_C": 1,
            "defining_equations": "six bilinear equations, three in each parity eigenchannel",
            "factorization": "the Cartesian product K_T3_plus x K_T3_minus of two irreducible dimension-7 third-transvectant kernels",
        }:
            raise AssertionError(f"candidate-{index} L1 active variety changed")
        pencil = row["parity_pencil"]
        if pencil["relations"] != ["c_pp=3*c_aa", "c_ap=c_pa"] or pencil["lambda_squared"] != "128/5":
            raise AssertionError("L1 parity pencil changed")

    transvectant = transvectant_data()
    branch_ratios = branch_parity_current_ratios()
    target_ratio = sp.Rational(13, 192)
    scalar_rows = scalar_cone_witnesses(records, target_ratio)
    return {
        "schema": "einstein-maxwell-weyl-same-sign-L1-active-restricted-current-degeneracy-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_L1_ACTIVE_RESTRICTED_CURRENT_DEGENERACY",
        "result_state": "CANDIDATES_17_AND_20_HAVE_SMOOTH_BOUNDED_ACTIVE_POINTS_WITH_PROJECTIVE_CURRENT_RADICALS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_EXPLICIT_SMOOTH_DEGENERACY_WITNESS_ON_BOTH_L1_ACTIVE_BACKGROUNDS",
        "scope": {
            **records["resonance_faces"]["scope"],
            "background": "candidates 17 and 20 only, retained as distinct compact Plebanski--Hacyan collision backgrounds",
            "carrier": "the complete axial/polar q-minus x q-plus L=1 active resonance varieties K_T3_plus x K_T3_minus at one exact scalar-cone occupation on each background",
            "parity": "both exact real parity eigenchannels, transformed current-orthogonally from axial/polar amplitudes",
            "omega": "candidate-specific positive/negative-frequency DIFFERENCE collision into the exceptional extra target",
        },
        "parity_current_reduction": {
            "q_branch_axial_polar_current_ratio": "h_polar/h_axial=3 on both q_minus and q_plus branch representatives",
            "direct_action_current_shell_audit": branch_ratios,
            "source_pencil_relation": "c_pp=3*c_aa and c_ap=c_pa",
            "current_orthogonal_first_node_matrix": "Q=[[sqrt(3),-sqrt(3)],[1,1]], with Q^T diag(1,3) Q=6 I",
            "current_orthogonal_second_node_matrix": "P is a nonzero scalar multiple of Q, so P^T diag(1,3) P is a positive scalar multiple of I",
            "consequence": "the two third-transvectant eigenchannels are current-orthogonal and carry identical-sign copies of the same negative-node plus positive-node Hermitian problem",
        },
        "universal_smooth_radical": transvectant,
        "scalar_cone_witnesses": scalar_rows,
        "full_bounded_witness": {
            "resonant_channels": "use the displayed smooth (f,g) point in both parity eigenchannels and scale the two nodes to the certified 13/192 absolute-current occupation ratio",
            "spectators": "real m=0 current eigenlines realize the remaining scalar-cone occupations",
            "rotations": "the displayed resonant f and g have zero J1,J2,J3 moments individually; m=0 spectators do too",
            "resonance": "both T3 eigenchannel equations vanish exactly",
            "same_fibre_sources": "removable by the imported 864-defect same-fibre census",
            "bounded_second_order_membership": "CERTIFIED_BY_THE_EXACT_FIBRE_PRODUCT_THEOREM",
        },
        "classification": {
            "candidate17_smooth_active_restricted_current_degeneracy": True,
            "candidate20_smooth_active_restricted_current_degeneracy": True,
            "degeneracy_occurs_inside_each_exact_scalar_cone": True,
            "degenerate_points_have_all_five_stabilizer_moment_maps_zero": True,
            "degenerate_points_are_bounded_second_order_tangents": True,
            "global_active_component_symplectic_orbifold": False,
            "proper_moment_map_connected_fibre_theorem_applicable_globally": False,
            "complete_presymplectic_stratification_classified": False,
            "candidate18_active_restricted_current_classified": False,
            "occupation_strata_glued": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-17/20 active varieties are not globally symplectic after fixed norms and node-phase reduction. The obstruction is not a singular point of the resonance variety: an exact smooth, rotation-neutral bounded point carries a surviving projective current radical. Therefore the ordinary smooth Hamiltonian connected-fibre theorem cannot classify these active links globally; a presymplectic stratification or further quotient is required.",
        "next_gate": "classify the candidate-17/20 current-degeneracy divisor and its presymplectic quotient, and compute the remaining candidate-18 restricted current",
        "claim_boundary": "This is an explicit smooth degeneracy witness on candidates 17 and 20, not a complete degeneracy-divisor or connected-component classification. Candidate 18, occupation gluing, final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in (INPUTS | CODE_INPUTS).items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy",
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
        raise AssertionError("L1 active restricted-current degeneracy certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_L1_ACTIVE_RESTRICTED_CURRENT_DEGENERACY: PASS")


if __name__ == "__main__":
    main()
