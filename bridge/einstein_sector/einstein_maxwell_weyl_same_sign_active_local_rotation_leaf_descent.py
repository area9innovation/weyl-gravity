"""Certify local commutation of radical and lifted-rotation reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent.schema.json"
INPUTS = {
    "phase_reduced_divisors": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "bounded_witnesses": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    phase = records["phase_reduced_divisors"]
    flags = phase["classification"]
    required = (
        "candidate17_regular_fixed_occupation_phase_reduced_divisor_classified",
        "candidate18_regular_fixed_occupation_phase_reduced_divisor_classified",
        "candidate20_regular_fixed_occupation_phase_reduced_divisor_classified",
        "constant_corank_local_leaf_quotient_classified",
    )
    if not all(flags[name] for name in required):
        raise AssertionError("phase-reduced constant-corank input changed")
    if flags["lifted_rotation_reduction_classified"]:
        raise AssertionError("input unexpectedly claims the lifted-rotation reduction")

    stabilizer = records["stabilizer"]
    background_stabilizer = stabilizer["background_stabilizer"]
    if (
        background_stabilizer["dimension"] != 5
        or background_stabilizer["basis"][-3:] != ["J_1", "J_2", "J_3"]
        or "patchwise U(1) compensator" not in background_stabilizer["maxwell_bundle_action"]
    ):
        raise AssertionError("lifted rotational stabilizer changed")
    witnesses = records["bounded_witnesses"]
    if not witnesses["classification"]["all_six_rotation_zero_witnesses_exact"]:
        raise AssertionError("rotation-zero witness input changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-active-local-rotation-leaf-descent-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LOCAL_ROTATION_LEAF_DESCENT",
        "result_state": "CANDIDATE17_18_20_LOCAL_RADICAL_AND_LIFTED_ROTATION_REDUCTIONS_COMMUTE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_SMOOTH_CONSTANT_CORANK_FIXED_OCCUPATION_STRATA_ON_CANDIDATES_17_18_20",
        "scope": {
            **phase["scope"],
            "carrier": "every smooth constant-current-corank stratum of the candidate-17, candidate-18 or candidate-20 fixed-active-occupation resonance variety after the two common node-phase quotients",
        },
        "presymplectic_descent_theorem": {
            "data": "a smooth stratum U with closed reduced Lee-Wald form Omega_U of constant rank, radical distribution R=ker(Omega_U), and the lifted diagonal SO(3) action",
            "hamiltonian_identity": "d<mu,xi>=i_{xi_sharp}Omega_U for every xi in so(3)",
            "radical_annihilation": "for r in R, d<mu,xi>(r)=Omega_U(xi_sharp,r)=0",
            "radical_invariance": "the lifted SO(3) action preserves Omega_U and therefore preserves R",
            "basicness": "every component of mu is locally constant on connected radical leaves",
            "local_leaf_space": "on every simple saturated neighbourhood q:U_0->U_bar=U_0/R there are unique Omega_bar and mu_bar with q^*Omega_bar=Omega_U and q^*mu_bar=mu",
            "descended_hamiltonian_identity": "d<mu_bar,xi>=i_{xi_bar_sharp}Omega_bar",
            "zero_fibre_commutation": "(mu^{-1}(0) intersect U_0)/R is canonically mu_bar^{-1}(0)",
            "regular_two_stage_reduction": "where the residual lifted-SO(3) action has a regular local quotient, first removing R and then reducing at mu_bar=0 equals the local presymplectic reduction of U_0 at mu=0",
        },
        "candidate_application": {
            "candidates": [17, 18, 20],
            "node_phase_reduction_precedes_this_theorem": True,
            "parity_channels_remain_coupled": True,
            "candidate18_positive_spectators_remain_present": True,
            "all_constant_corank_smooth_strata_covered": True,
            "certified_rotation_zero_points_nonempty": True,
            "nonempty_source": witnesses["result_id"],
            "consequence": "the Lee-Wald radical cannot carry an additional independent rotational Taub condition; the three lifted rotational moment maps descend to the local symplectic leaf quotient",
        },
        "classification": {
            "candidate17_local_rotation_leaf_descent_classified": True,
            "candidate18_local_rotation_leaf_descent_classified": True,
            "candidate20_local_rotation_leaf_descent_classified": True,
            "moment_map_basic_on_current_radical": True,
            "local_zero_fibre_and_radical_reductions_commute": True,
            "node_phases_identified_with_rotations": False,
            "global_rotation_zero_fibre_connected": False,
            "global_leaf_space_or_Hausdorff_quotient_classified": False,
            "singular_locus_reduction_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "On candidates 17, 18 and 20 the current radical and the lifted rotational constraint are compatible rather than competing reductions. The moment map is constant along radical leaves, so the rotational zero condition survives on each local symplectic leaf quotient. This is a local constant-corank theorem and gives neither connectedness nor a global quotient.",
        "next_gate": "classify the lifted-rotation zero fibres and singular/occupation gluing candidate by candidate; do not infer global topology from this local commutation theorem",
        "claim_boundary": "This theorem covers only smooth constant-corank fixed-occupation strata after the two common node phases. It does not construct a global leaf space, prove connectedness of a complete rotation-zero fibre, reduce singular strata, glue occupations or candidates, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent",
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
        raise AssertionError("local rotation-leaf descent certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LOCAL_ROTATION_LEAF_DESCENT: PASS")


if __name__ == "__main__":
    main()
