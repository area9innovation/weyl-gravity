"""Classify the one-parity common-square rotation quotient on candidates 17/20."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.schema.json"
INPUTS = {
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "singular_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json",
    "restricted_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
}

SQRT3 = sp.sqrt(3)
MASS_SQUARED = {
    "q_minus_n1": 6 - 2 * SQRT3,
    "q_minus_n2": 6 - 2 * SQRT3,
    "q_plus_n1": 6 + 2 * SQRT3,
    "q_plus_n2": 6 + 2 * SQRT3,
    "p_extra_n1": sp.Rational(16, 3),
    "p_extra_n2": sp.Rational(16, 3),
}
NODE_DATA = {
    "q_minus_n2": (-1, 2),
    "p_extra_n2": (1, 2),
    "q_plus_n2": (1, 2),
    "q_minus_n1": (-1, 1),
    "p_extra_n1": (1, 1),
    "q_plus_n1": (1, 1),
}
CANDIDATES = {
    17: {
        "rho": 10 * (9 * SQRT3 + 77) / 8529,
        "negative_node": "q_minus_n1",
        "positive_node": "q_plus_n2",
        "active_rays": ("R3", "R4"),
        "inactive_rays": ("R1", "R2"),
    },
    20: {
        "rho": -10 * (-77 + 9 * SQRT3) / 8529,
        "negative_node": "q_minus_n2",
        "positive_node": "q_plus_n1",
        "active_rays": ("R2", "R4"),
        "inactive_rays": ("R1", "R3"),
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_binary_square_audit() -> dict[str, object]:
    a, b, c = sp.symbols("a b c")
    q = sp.Matrix([a, b, c])
    square = sp.Matrix([a**2, a * b, (a * c + 2 * b**2) / 3, b * c, c**2])
    derivative = square.jacobian(q)
    spin_one = {
        "J0": sp.diag(1, 0, -1),
        "Jplus": sp.Matrix([[0, 2, 0], [0, 0, 1], [0, 0, 0]]),
        "Jminus": sp.Matrix([[0, 0, 0], [1, 0, 0], [0, 2, 0]]),
    }
    spin_two = {
        "J0": sp.diag(2, 1, 0, -1, -2),
        "Jplus": sp.Matrix(
            [[0, 4, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 2, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]]
        ),
        "Jminus": sp.Matrix(
            [[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 2, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 4, 0]]
        ),
    }
    for name in spin_one:
        if sp.simplify(derivative * spin_one[name] * q - spin_two[name] * square) != sp.zeros(5, 1):
            raise AssertionError(f"binary-square {name} equivariance changed")
    quadratic_invariant = a * c - b**2
    gradient = sp.Matrix([sp.diff(quadratic_invariant, item) for item in q])
    for name, generator in spin_one.items():
        if sp.expand((gradient.T * generator * q)[0]) != 0:
            raise AssertionError(f"spin-one invariant failed for {name}")

    z = sp.Matrix(sp.symbols("z0:3"))
    zb = sp.Matrix(sp.symbols("zb0:3"))
    norm = (zb.T * z)[0]
    symmetric_tracefree = z * z.T - (z.T * z)[0] * sp.eye(3) / 3
    adjoint = zb * zb.T - (zb.T * zb)[0] * sp.eye(3) / 3
    commutator = sp.simplify(symmetric_tracefree * adjoint - adjoint * symmetric_tracefree)
    expected = sp.simplify(norm * (z * zb.T - zb * z.T))
    if sp.simplify(commutator - expected) != sp.zeros(3, 3):
        raise AssertionError("symmetric-tracefree commutator identity changed")
    return {
        "binary_basis": "[a,b,c] and [f0,f1,f2,f3,f4] in descending weight order",
        "common_square_map": "[a^2,a*b,(a*c+2*b^2)/3,b*c,c^2]",
        "equivariance_checked_for": ["J0", "Jplus", "Jminus"],
        "spin_one_quadratic_invariant": "Q=a*c-b^2",
        "cartan_model": "S(z)=z*z^T-(z^T*z/3)I in Sym^2_0(C^3)",
        "commutator_identity": "[S(z),S(z)^dagger]=(z^dagger*z)*(z*z^dagger-conjugate(z)*z^T)",
        "zero_criterion": "mu_SO3([S(z)])=0 iff [S,S^dagger]=0 iff [z] is phase-real",
    }


def ray_weight(node: str, support: list[str], rho: sp.Expr) -> sp.Expr:
    sign, momentum = NODE_DATA[node]
    x = {
        name: sp.sqrt(rho + MASS_SQUARED[name] / NODE_DATA[name][1] ** 2)
        for name in support
    }
    denominator = sign * momentum**2
    denominator *= sp.prod(x[node] - x[other] for other in support if other != node)
    return sp.factor(1 / denominator)


def node_frequency(node: str, rho: sp.Expr) -> sp.Expr:
    _, momentum = NODE_DATA[node]
    return sp.sqrt(momentum**2 * rho + MASS_SQUARED[node])


def rotation_coefficient(node_minus: str, node_plus: str, support: list[str], rho: sp.Expr) -> sp.Expr:
    """The coefficient of the common angular moment map on a circuit ray."""

    negative = node_frequency(node_minus, rho) * ray_weight(node_minus, support, rho)
    positive = node_frequency(node_plus, rho) * ray_weight(node_plus, support, rho)
    return sp.factor(positive - negative)


def exact_candidate_rows(ray_supports: dict[str, list[str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    deltas: dict[int, dict[str, sp.Expr]] = {}
    for candidate, spec in CANDIDATES.items():
        rho = spec["rho"]
        negative = spec["negative_node"]
        positive = spec["positive_node"]
        ray_rows = []
        deltas[candidate] = {}
        for ray_id in spec["active_rays"]:
            value = rotation_coefficient(negative, positive, ray_supports[ray_id], rho)
            if value.is_zero is not False:
                raise AssertionError(f"candidate {candidate} {ray_id} rotation coefficient became zero")
            deltas[candidate][ray_id] = value
            ray_rows.append(
                {
                    "ray_id": ray_id,
                    "coefficient_formula": "omega_plus*y_plus-omega_minus*y_minus",
                    "exact_expression": sp.sstr(value),
                    "strict_sign": "POSITIVE" if value.is_positive is True else "NEGATIVE",
                    "decimal": str(sp.N(value, 18)),
                }
            )
        if candidate == 17 and not all(value.is_negative is True for value in deltas[candidate].values()):
            raise AssertionError("candidate 17 lost strict negative imbalance")
        if candidate == 20 and not (
            deltas[candidate]["R2"].is_negative is True
            and deltas[candidate]["R4"].is_positive is True
        ):
            raise AssertionError("candidate 20 balance crossing changed")
        rows.append(
            {
                "candidate_index": candidate,
                "rho": sp.sstr(rho),
                "negative_node": negative,
                "positive_node": positive,
                "active_ray_coefficients": ray_rows,
                "inactive_ray_effect": "each inactive ray adds only negative-node occupation and therefore contributes -omega_minus*y_minus<0",
            }
        )
    balance_ratio = sp.factor(deltas[20]["R4"] / (-deltas[20]["R2"]))
    if balance_ratio.is_positive is not True:
        raise AssertionError("candidate 20 balance ratio lost positivity")
    next(row for row in rows if row["candidate_index"] == 20)["balance_witness"] = {
        "occupation_ray_combination": "t20*R2+R4",
        "t20_formula": "-delta_R4/delta_R2",
        "t20_exact_expression": sp.sstr(balance_ratio),
        "t20_strictly_positive": True,
        "t20_decimal": str(sp.N(balance_ratio, 18)),
        "rotation_coefficient": "t20*delta_R2+delta_R4=0",
    }
    return rows


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    singular = records["singular_locus"]
    if singular["one_factor_singular_locus"]["projectivization"] != "P^2 x P^1 embedded by O(2,1)":
        raise AssertionError("common-square singular carrier changed")
    if not records["singular_sections"]["universal_section"]["node_phase_actions_free"]:
        raise AssertionError("node-phase freeness changed")
    restricted = records["restricted_current"]["classification"]
    if not restricted["all_four_active_ray_occupation_gaps_exactly_positive"]:
        raise AssertionError("occupation input changed")
    moment = records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]["J_a"]
    if "sum omega" not in moment:
        raise AssertionError("frequency-weighted rotation moment-map convention changed")
    ray_supports = {
        row["ray_id"]: [item["node_id"] for item in row["weight_formula"]]
        for row in records["scalar_rays"]["extreme_rays"]
    }
    expected_supports = {
        "R1": ["q_minus_n2", "p_extra_n2", "q_minus_n1", "p_extra_n1"],
        "R2": ["q_minus_n2", "p_extra_n2", "q_minus_n1", "q_plus_n1"],
        "R3": ["q_minus_n2", "q_plus_n2", "q_minus_n1", "p_extra_n1"],
        "R4": ["q_minus_n2", "q_plus_n2", "q_minus_n1", "q_plus_n1"],
    }
    if ray_supports != expected_supports:
        raise AssertionError("same-sign ray supports changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-common-square-rotation-quotient-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMMON_SQUARE_ROTATION_QUOTIENT",
        "result_state": "ONE_PARITY_COMMON_SQUARE_ROTATION_QUOTIENT_CLASSIFIED_WITH_CANDIDATE20_BALANCE_DIVISOR",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ONE_PARITY_COMMON_SQUARE_CARRIER_AT_EVERY_POSITIVE_ACTIVE_OCCUPATION",
        "scope": {
            **singular["scope"],
            "carrier": "one declared parity factor with both active nodes proportional to one nonzero square quartic and the other parity factor at zero, after the two free node phases",
            "correction_class": "bounded or finite-quasiperiodic second-order tangent cone",
        },
        "cartan_square_certificate": exact_binary_square_audit(),
        "fixed_occupation_reduction": {
            "phase_reduced_carrier": "P(V1)=CP^2; fixed active norms determine the two scalar moduli and the free node phases remove their arguments",
            "rotation_coefficient": "delta=omega_plus*N_plus-omega_minus*N_minus",
            "moment_map_factorization": "mu_total=positive_normalization*delta*mu_CartanSquare",
            "nonzero_delta_zero_locus": "RP^2, the phase-real projective directions",
            "nonzero_delta_quotient": "RP^2/SO(3) is one point",
            "zero_delta_zero_locus": "all CP^2",
            "zero_delta_quotient": "CP^2/SO(3) is the closed interval eta in [0,1]",
            "orbit_parameter": "eta=|z^T*z|/(z^dagger*z); eta=1 is phase-real and eta=0 is the isotropic orbit",
            "orbit_classification_proof": "write z=x+i*y, use projective phase to impose x dot y=0, then rotate the orthogonal pair and normalize; eta=abs(|x|^2-|y|^2)/(|x|^2+|y|^2) is the remaining complete invariant",
        },
        "candidate_rows": exact_candidate_rows(ray_supports),
        "classification": {
            "one_parity_common_square_fixed_occupation_rotation_quotient_classified": True,
            "candidate17_rotation_coefficient_strictly_negative_on_complete_nonzero_active_cone": True,
            "candidate17_common_square_rotation_zero_quotient_always_one_point": True,
            "candidate20_rotation_balance_divisor_nonempty": True,
            "candidate20_off_balance_common_square_rotation_zero_quotient_one_point": True,
            "candidate20_on_balance_common_square_rotation_zero_quotient_closed_interval": True,
            "unweighted_occupation_gap_sufficient_for_rotation_imbalance": False,
            "candidate20_all_positive_occupations_have_point_quotient": False,
            "complete_two_parity_singular_union_quotient_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The common-square singular carrier has a sharp frequency-weighted bifurcation. Candidate 17 never reaches it, so its one-parity singular rotation quotient is a point at every nonzero active occupation. Candidate 20 crosses the balance divisor: away from it the quotient is again a point, while on it the rotation equation vanishes identically and an interval of inequivalent square directions survives.",
        "next_gate": "extend this coefficient-sensitive reduction from the one-parity common-square carrier to both components of (S_plus x K_minus) union (K_plus x S_minus), retaining the candidate-20 balance divisor",
        "claim_boundary": "This is a complete fixed-occupation rotation quotient only for the one-parity common-square carrier. It does not classify the complete two-parity singular union, glue occupation strata, construct a global leaf space, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient",
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
        raise AssertionError("common-square rotation-quotient certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMMON_SQUARE_ROTATION_QUOTIENT: PASS")


if __name__ == "__main__":
    main()
