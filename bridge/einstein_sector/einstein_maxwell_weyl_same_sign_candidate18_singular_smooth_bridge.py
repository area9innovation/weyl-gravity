"""Certify a smooth rotation-zero bridge between candidate 18 singular pieces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.schema.json"
INPUTS = {
    "separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.json",
    "current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_path_check() -> dict[str, str]:
    a, c, beta, np, nm, theta = sp.symbols("a c beta N_plus N_minus theta", positive=True, real=True)
    w = sp.Matrix([sp.cos(theta), sp.sin(theta)])
    A = sp.Matrix([[a, c], [c, a]])
    denominator = sp.simplify((w.T * A * w)[0])
    u = sp.sqrt(6 * np / denominator) * w
    v = sp.sqrt(6 * nm / beta) * w
    if sp.simplify((u.T * A * u)[0] / 6 - np) != 0:
        raise AssertionError("positive occupation path changed")
    if sp.simplify(beta * (v.T * v)[0] / 6 - nm) != 0:
        raise AssertionError("negative occupation path changed")
    return {
        "positive_denominator": str(sp.expand_trig(denominator)),
        "positive_amplitude": "sqrt(6*N_plus/(w(theta)^T*A*w(theta)))*w(theta)",
        "negative_amplitude": "sqrt(6*N_minus/beta)*w(theta)",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    separation = records["separation"]["classification"]
    if not separation["candidate18_singular_rotation_zero_quotient_at_least_two_components"]:
        raise AssertionError("singular separation input changed")
    phase = records["current"]["candidate18"]["ambient_current"]
    if "A tensor W" not in phase or "-b*I_2 tensor W" not in phase:
        raise AssertionError("candidate-18 current block changed")
    exact = exact_path_check()
    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate18-singular-smooth-bridge-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_SMOOTH_BRIDGE",
        "result_state": "CANDIDATE18_TWO_SINGULAR_COMPONENTS_CONNECTED_THROUGH_SMOOTH_ROTATION_ZERO_CARRIER",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_POSITIVE_ACTIVE_OCCUPATION_PAIR_ON_CANDIDATE18",
        "scope": {
            **records["separation"]["scope"],
            "carrier": "an explicit central-m axisymmetric path in the complete candidate-18 fixed-positive-occupation resonance variety",
        },
        "path": {
            "parameter": "0<=theta<=pi/2",
            "angular_vector": "e_0=(0,0,1,0,0)",
            "internal_unit_vector": "w(theta)=(cos(theta),sin(theta))",
            "positive_metric": "A=[[a,c],[c,a]], with a+c=w_y/2>0 and a-c=w_x/6>0",
            "negative_metric": "beta*I_2, beta=6*h_minus>0",
            **exact,
            "field_assignment": "f_plus=u_1*e_0, f_minus=u_2*e_0, g_plus=v_1*e_0, g_minus=v_2*e_0; all ten spectators vanish",
            "fixed_occupations": "u(theta)^T*A*u(theta)/6=N_plus and beta*v(theta)^T*v(theta)/6=N_minus exactly",
            "rotation_moment_maps": "all three vanish for every theta because only m=0 is occupied",
            "endpoint_zero_pi_over_2": ["Sigma_minus endpoint with the minus factor zero", "Sigma_plus endpoint with the plus factor zero"],
            "interior": "for 0<theta<pi/2 both 5x2 factors are nonzero rank one, so the complex resonance carrier is smooth",
        },
        "classification": {
            "candidate18_singular_components_joined_in_full_rotation_zero_fibre": True,
            "bridge_exists_at_every_positive_occupation_pair": True,
            "bridge_interior_complex_smooth": True,
            "node_phase_actions_free_along_bridge": True,
            "full_rotation_zero_fibre_connected": False,
            "all_singular_points_connected_to_bridge": False,
            "global_leaf_space_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 18's disconnected singular subquotient does not disconnect the complete fixed-occupation rotation-zero carrier: its two labelled singular pieces are joined by an explicit smooth axisymmetric path. This removes one topology obstruction but is not a global connectedness theorem.",
        "next_gate": "determine whether every candidate-18 rotation-zero component meets this central bridge, including current-degenerate strata and all ten spectator directions",
        "claim_boundary": "This connects one certified point in each singular component through the smooth carrier at every positive occupation. It does not prove the entire zero fibre connected, classify the global leaf space, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge",
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
        raise AssertionError("candidate-18 singular smooth-bridge certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_SMOOTH_BRIDGE: PASS")


if __name__ == "__main__":
    main()
