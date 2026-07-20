"""Exhibit smooth bounded current radicals on candidate 18's active variety."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.schema.json"
INPUTS = {
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "multiplicity_two_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "L1_current_audit": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json",
    "interval_code": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str, **symbols: sp.Expr) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "I": sp.I, **symbols})


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


def ray_weights(ray: dict[str, object], rho: sp.Expr) -> dict[str, sp.Expr]:
    signs = {"q_minus": -1, "p_extra": 1, "q_plus": 1}
    masses = {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }
    labels = {
        node: (node.rsplit("_n", 1)[0], int(node.rsplit("_n", 1)[1]))
        for node in ray["support"]
    }
    frequencies = {
        node: sp.sqrt(rho + masses[branch] / n**2)
        for node, (branch, n) in labels.items()
    }
    result = {}
    for node, (branch, n) in labels.items():
        denominator = sp.Integer(signs[branch] * n**2)
        for other in labels:
            if other != node:
                denominator *= frequencies[node] - frequencies[other]
        result[node] = sp.factor(1 / denominator)
    return result


def scalar_ratio_one_witness(records: dict[str, dict[str, object]], rho: sp.Expr) -> dict[str, object]:
    rays = {row["ray_id"]: row for row in records["scalar_rays"]["extreme_rays"]}
    r1 = ray_weights(rays["R1"], rho)
    r3 = ray_weights(rays["R3"], rho)
    negative = "q_minus_n2"
    positive = "p_extra_n1"
    ratio_r1 = sp.factor(r1[positive] / r1[negative])
    ratio_r3 = sp.factor(r3[positive] / r3[negative])
    below = exact_interval(ratio_r1 - 1)
    above = exact_interval(ratio_r3 - 1)
    if below["positive"] or not above["positive"]:
        raise AssertionError("candidate-18 active occupation ratio no longer crosses one")
    coefficient = sp.factor((r3[positive] - r3[negative]) / (r1[negative] - r1[positive]))
    coefficient_interval = exact_interval(coefficient)
    if not coefficient_interval["positive"]:
        raise AssertionError("candidate-18 ray-mixture coefficient ceased to be positive")
    positive_total = sp.factor(r3[positive] + coefficient * r1[positive])
    negative_total = sp.factor(r3[negative] + coefficient * r1[negative])
    if sp.cancel(positive_total - negative_total) != 0:
        raise AssertionError("candidate-18 occupation equality failed")
    return {
        "active_positive_node": positive,
        "active_negative_node": negative,
        "ray_mixture": "R3+s18*R1",
        "s18_exact": sp.sstr(coefficient),
        "s18_interval": coefficient_interval,
        "R1_positive_over_negative_minus_one_interval": below,
        "R3_positive_over_negative_minus_one_interval": above,
        "resulting_positive_over_negative_ratio": "1",
        "exact_occupation_difference_remainder": "0",
        "all_six_scalar_constraints_zero": True,
        "all_occupations_nonnegative": True,
        "active_resonant_norms_nonzero": True,
    }


def axial_extra_gram(record: dict[str, object], momentum: sp.Expr, frequency: sp.Expr) -> sp.Matrix:
    lam, k, omega1, omega2, omega_e = sp.symbols("lambda k omega1 omega2 omega_e", real=True)
    current = sp.Matrix(
        [
            [parse(value.replace("lambda", "lam"), lam=lam, k=k, omega1=omega1, omega2=omega2) for value in row]
            for row in record["direct_current_match"]["generic_reduced_Green_matrix"]
        ]
    )
    representatives = sp.Matrix.hstack(
        *[
            sp.Matrix([parse(value.replace("lambda", "lam"), lam=lam, k=k, omega_e=omega_e) for value in column])
            for column in record["full_solution_pairing"]["extra_representatives"]
        ]
    )
    gram = representatives.T * current * representatives / (-sp.I * omega_e)
    gram = gram.subs({lam: 6, k: momentum, omega1: frequency, omega2: frequency, omega_e: frequency})
    expected = sp.Matrix(
        [
            [256 * momentum**2 + 1296, 256 * momentum * frequency],
            [256 * momentum * frequency, 256 * momentum**2 + sp.Rational(208, 3)],
        ]
    )
    reduced = (gram - expected).applyfunc(
        lambda value: sp.factor(value.subs(frequency**2, momentum**2 + sp.Rational(16, 3)))
    )
    if reduced != sp.zeros(2):
        raise AssertionError("axial p-extra action current changed")
    return expected


def polar_extra_gram(record: dict[str, object], momentum: sp.Expr) -> sp.Matrix:
    lam, k = sp.symbols("lambda k", real=True)
    gram = sp.Matrix(
        [
            [parse(value.replace("lambda", "lam"), lam=lam, k=k) for value in row]
            for row in record["shell_pairing"]["extra_Hermitian_current_Gram"]
        ]
    ).subs({lam: 6, k: momentum})
    return gram.applyfunc(sp.factor)


def active_current_reduction(records: dict[str, dict[str, object]], decomposition: dict[str, object], rho: sp.Expr) -> dict[str, object]:
    momentum = sp.sqrt(rho)
    frequency = sp.sqrt(rho + sp.Rational(16, 3))
    axial_gram = axial_extra_gram(records["axial_current"], momentum, frequency)
    polar_gram = polar_extra_gram(records["polar_current"], momentum)
    caa = sp.Matrix([[parse(value) for value in decomposition["coefficient_rows"]["aa"]]])
    cpp = sp.Matrix([[parse(value) for value in decomposition["coefficient_rows"]["pp"]]])
    wx = sp.cancel(1 / (caa * axial_gram.inv() * caa.T)[0])
    wy = sp.cancel(1 / (cpp * polar_gram.inv() * cpp.T)[0])
    wx_interval = exact_interval(wx)
    wy_interval = exact_interval(wy)
    off_diagonal_interval = exact_interval(3 * wy - wx)
    if not (wx_interval["positive"] and wy_interval["positive"] and off_diagonal_interval["positive"]):
        raise AssertionError("candidate-18 positive-node active current changed")

    qminus = records["L1_current_audit"]["parity_current_reduction"]["direct_action_current_shell_audit"]["q_minus"]
    h_axial = -parse(qminus["axial_representative_norm"])
    h_polar = -parse(qminus["polar_representative_norm"])
    if sp.factor(h_polar - 3 * h_axial) != 0 or not exact_interval(h_axial)["positive"]:
        raise AssertionError("q-minus parity current changed")

    Q = sp.Matrix([[sp.sqrt(3), -sp.sqrt(3)], [1, 1]])
    P = Q.inv().T
    wx_symbol, wy_symbol, h_symbol = sp.symbols("w_x w_y h_minus", positive=True)
    generic_positive = sp.simplify(P.T * sp.diag(wx_symbol, wy_symbol) * P)
    generic_negative = sp.simplify(Q.T * sp.diag(h_symbol, 3 * h_symbol) * Q)
    a_symbol = wx_symbol / 12 + wy_symbol / 4
    c_symbol = -wx_symbol / 12 + wy_symbol / 4
    expected_positive = sp.Matrix([[a_symbol, c_symbol], [c_symbol, a_symbol]])
    if generic_positive != expected_positive or generic_negative != 6 * h_symbol * sp.eye(2):
        raise AssertionError("candidate-18 symbolic channel current reduction changed")

    eigen_rows = []
    for sign, label in ((1, "symmetric"), (-1, "antisymmetric")):
        z = sp.Matrix([1, sign])
        symbolic_eigenvalue = sp.factor(a_symbol + sign * c_symbol)
        symbolic_expected = wy_symbol / 2 if sign == 1 else wx_symbol / 6
        if sp.factor(symbolic_eigenvalue - symbolic_expected) != 0 or generic_positive * z != symbolic_expected * z:
            raise AssertionError("candidate-18 current eigenline changed")
        eigenvalue = wy / 2 if sign == 1 else wx / 6
        t_squared = sp.factor(eigenvalue / (6 * h_axial))
        if not exact_interval(t_squared)["positive"]:
            raise AssertionError("candidate-18 node scale is not real")
        symbolic_t_squared = symbolic_expected / (6 * h_symbol)
        if (generic_positive - symbolic_t_squared * generic_negative) * z != sp.zeros(2, 1):
            raise AssertionError("candidate-18 radical cancellation failed")
        eigen_rows.append(
            {
                "channel_eigenline": label,
                "z": [str(value) for value in z],
                "positive_current_eigenvalue_formula": "w_y/2" if sign == 1 else "w_x/6",
                "node_scale_squared_formula": "(w_y/2)/(6*h_minus)" if sign == 1 else "(w_x/6)/(6*h_minus)",
                "node_scale_squared_interval": exact_interval(t_squared),
                "current_cancellation_remainder": ["0", "0"],
                "active_rank_one_factors_nonzero": True,
                "smooth_affine_resonance_dimension_over_C": 22,
                "projective_current_radical_complex_dimension": 4,
            }
        )

    return {
        "active_functional_coordinates": {
            "X": "c_aa applied to the axial p-extra doublet",
            "Y": "c_pp applied to the polar p-extra doublet",
            "U": "axial q-minus amplitude",
            "V": "polar q-minus amplitude",
        },
        "source_normal_form": [
            "T1(X,U)+T1(Y,V)=0",
            "3*T1(X,V)+T1(Y,U)=0",
        ],
        "channel_transforms": {
            "Q": [[sp.sstr(value) for value in row] for row in Q.tolist()],
            "P": [[sp.sstr(value) for value in row] for row in P.tolist()],
            "identities": ["P^T*Q=I", "P^T*[[0,3],[1,0]]*Q=diag(sqrt(3),-sqrt(3))"],
            "resonance_factorization": "T1(f_plus,g_plus)=T1(f_minus,g_minus)=0",
        },
        "active_positive_weights": {
            "w_x_definition": "1/(c_aa*G_axial_extra^{-1}*c_aa^T)",
            "w_y_definition": "1/(c_pp*G_polar_extra^{-1}*c_pp^T)",
            "w_x_interval": wx_interval,
            "w_y_interval": wy_interval,
            "3w_y_minus_w_x_interval": off_diagonal_interval,
        },
        "channel_current_matrices": {
            "positive_node": "[[w_x/12+w_y/4,-w_x/12+w_y/4],[-w_x/12+w_y/4,w_x/12+w_y/4]]",
            "negative_node_absolute": "6*h_minus*I_2",
            "h_minus": sp.sstr(h_axial),
        },
        "smooth_radical_families": eigen_rows,
        "radical_geometry": {
            "base_angular_quartic": "e0=(0,0,1,0,0)",
            "base_channels": "f=z tensor e0; g=t*z tensor e0 with t^2 as displayed",
            "rank_one_smoothness": "both entries of z are nonzero, so both rank-one cone factors are at nonzero proportional pairs and are smooth",
            "transverse_radicals": "delta f=z tensor r; delta g=t*z tensor r for every r in e0-perp",
            "fixed_norm_and_phase_descent": "e0 is orthogonal to r, so the four-complex-dimensional radical is fixed-norm tangent and survives both node-phase quotients",
            "spectator_orthogonality": "the p-extra functional coordinates use the current-orthogonal complements of their kernels",
        },
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items() if name != "interval_code"}
    face = next(row for row in records["resonance_faces"]["face_rows"] if row["candidate_index"] == 18)
    decomposition = next(row for row in records["multiplicity_two_L3"]["decompositions"] if row["candidate_index"] == 18)
    if face["collision"] != {
        "first_node": "p_extra_n1",
        "second_node": "q_minus_n2",
        "output_ell": 3,
        "target_branch": "q_plus",
        "temporal_channel": "SUM",
    }:
        raise AssertionError("candidate-18 collision carrier changed")
    if decomposition["zero_variety"] != {
        "ambient_dimension_over_C": 30,
        "active_dimension_over_C": 12,
        "spectator_dimension_over_C": 10,
        "dimension_over_C": 22,
        "irreducible_components_over_C": 1,
        "description": "A^10 times DetRank1(5x2)_plus times DetRank1(5x2)_minus after invertible internal and parity transformations",
    }:
        raise AssertionError("candidate-18 resonance geometry changed")
    if decomposition["reduced_parity_pencil"]["cross_equation"] != "-24*sqrt(2)*T1(X,V)-8*sqrt(2)*T1(Y,U)=0":
        raise AssertionError("candidate-18 parity pencil changed")
    fibre = next(row for row in records["fibre_product"]["candidate_rows"] if row["candidate_index"] == 18)
    if fibre["bounded_cone_formula"]["necessity_and_sufficiency"].startswith("the complete finite-harmonic") is False:
        raise AssertionError("bounded fibre-product theorem changed")
    if records["stabilizer"]["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("lifted stabilizer changed")

    rho = parse(face["rho"])
    current = active_current_reduction(records, decomposition, rho)
    scalar = scalar_ratio_one_witness(records, rho)
    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate18-active-restricted-current-degeneracy-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_ACTIVE_RESTRICTED_CURRENT_DEGENERACY",
        "result_state": "CANDIDATE18_HAS_TWO_SMOOTH_BOUNDED_ACTIVE_CURRENT_RADICAL_FAMILIES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_EXPLICIT_SMOOTH_DEGENERACY_FAMILIES_ON_CANDIDATE18",
        "scope": {
            **records["resonance_faces"]["scope"],
            "background": "candidate 18 only at its certified compact Plebanski--Hacyan circumference",
            "carrier": "the complete axial/polar p-extra(n=1) x q-minus(n=2) active L=3 resonance variety, including its p-extra kernel spectators, at one exact scalar-cone occupation",
            "parity": "both transformed rank-one parity channels; two exact internal current eigenlines",
            "omega": "positive-frequency p-extra plus q-minus SUM collision into q-plus",
        },
        "rho": face["rho"],
        "active_current_reduction": current,
        "scalar_cone_witness": scalar,
        "full_bounded_witness": {
            "resonant_nodes": "use either displayed z eigenline with e0 angular carrier and scale the q-minus node by the displayed positive t",
            "spectators": "use real m=0 representatives for every other occupied scalar-ray node",
            "stabilizers": "the ratio-one scalar mixture kills H and P_x; e0 resonant carriers and m=0 spectators kill J1,J2,J3",
            "resonance": "both rank-one first-transvectant equations vanish at nonzero proportional pairs",
            "same_fibre_sources": "removable by the imported 864-defect census encoded in the exact fibre-product theorem",
            "bounded_second_order_membership": "CERTIFIED_BY_THE_EXACT_FIBRE_PRODUCT_THEOREM",
        },
        "classification": {
            "candidate18_active_restricted_current_degeneracy": True,
            "two_exact_internal_eigenline_families": True,
            "degenerate_points_are_smooth_on_the_complete_active_resonance_variety": True,
            "projective_radical_complex_dimension_per_family": 4,
            "degeneracy_occurs_inside_the_exact_candidate18_scalar_cone": True,
            "degenerate_points_have_all_five_stabilizer_moment_maps_zero": True,
            "degenerate_points_are_bounded_second_order_tangents": True,
            "candidate18_global_active_component_symplectic_orbifold": False,
            "complete_candidate18_degeneracy_divisor_classified": False,
            "candidate17_20_degeneracy_divisors_classified": False,
            "occupation_strata_glued": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 18 completes the active same-sign current audit at the existence level: like candidates 17 and 20, its irreducible active variety contains smooth bounded projective current radicals. The mechanism is different and simpler: the scalar cone crosses equal positive/negative current occupation, and the two rank-one parity channels expose exact internal eigenlines on which four transverse spin-two directions cancel. The global active link is presymplectic rather than a symplectic orbifold.",
        "next_gate": "classify the candidate-17/18/20 current-degeneracy divisors and their presymplectic quotients; keep candidate-16 singular topology and occupation gluing separate",
        "claim_boundary": "This is an exact smooth bounded degeneracy-family theorem on candidate 18, not a complete degeneracy-divisor, presymplectic-quotient, connected-component or occupation-gluing theorem. Final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy",
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
        raise AssertionError("candidate-18 active restricted-current certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_ACTIVE_RESTRICTED_CURRENT_DEGENERACY: PASS")


if __name__ == "__main__":
    main()
