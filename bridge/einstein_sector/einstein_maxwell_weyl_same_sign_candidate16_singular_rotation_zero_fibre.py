"""Classify candidate 16's singular strata and lifted-rotation zero fibre."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre.schema.json"
INPUTS = {
    "candidate16_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current.json",
    "target_doublet": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "bounded_witnesses": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_one_jacobian_data() -> dict[str, object]:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    equations = [f[i] * g[j] - f[j] * g[i] for i in range(5) for j in range(i + 1, 5)]
    jacobian = sp.Matrix(equations).jacobian((*f, *g))
    vertex = {value: 0 for value in (*f, *g)}
    e0 = (0, 0, 1, 0, 0)
    rank_one = dict(zip((*f, *g), e0 + e0))
    if jacobian.subs(vertex).rank() != 0 or jacobian.subs(rank_one).rank() != 4:
        raise AssertionError("rank-one determinantal singularity changed")

    product_smooth = sp.diag(jacobian.subs(rank_one), jacobian.subs(rank_one))
    product_endpoint = sp.diag(jacobian.subs(vertex), jacobian.subs(rank_one))
    if product_smooth.rank() != 8 or product_endpoint.rank() != 4:
        raise AssertionError("candidate-16 product stratification changed")
    return {
        "one_factor_equations": [sp.sstr(value) for value in equations],
        "one_factor_ambient_complex_dimension": 10,
        "one_factor_dimension": 6,
        "one_factor_smooth_rank": 4,
        "one_factor_vertex_rank": 0,
        "one_factor_singular_locus": "the origin only",
        "product_smooth_J_rank": product_smooth.rank(),
        "product_smooth_dimension": 20 - product_smooth.rank(),
        "product_endpoint_J_rank": product_endpoint.rank(),
        "product_endpoint_zariski_tangent_dimension": 20 - product_endpoint.rank(),
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    current = records["candidate16_current"]
    if current["component"]["factorization"] != [
        "T1(A_a-sqrt(3)A_p,B_a+sqrt(3)B_p)=0",
        "T1(A_a+sqrt(3)A_p,B_a-sqrt(3)B_p)=0",
    ]:
        raise AssertionError("candidate-16 rank-one factorization changed")
    if not current["restricted_current_theorem"]["every_complex_smooth_stratum_restricted_current_nondegenerate"]:
        raise AssertionError("candidate-16 definite current theorem changed")
    if records["stabilizer"]["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("candidate-16 lifted stabilizer changed")

    witness = next(
        row for row in records["bounded_witnesses"]["witness_rows"]
        if row["candidate_index"] == 16
    )
    if witness["bounded_verdict"] != "NONZERO_POINT_IN_Z2_BOUNDED_CERTIFIED":
        raise AssertionError("candidate-16 bounded axisymmetric witness disappeared")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate16-singular-rotation-zero-fibre-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_SINGULAR_ROTATION_ZERO_FIBRE",
        "result_state": "CANDIDATE16_SINGULAR_STRATA_CLASSIFIED_AND_LIFTED_ROTATION_ZERO_FIBRE_CONNECTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_FIXED_OCCUPATION_CANDIDATE16_ACTIVE_LINK",
        "scope": {
            **current["scope"],
            "carrier": "the complete candidate-16 active fixed-positive-node-norm link, including both singular endpoint strata, after the two node-phase quotients",
            "m": "all m=-2,...,2 through the spin-two incidence resolution",
        },
        "rank_one_product": rank_one_jacobian_data(),
        "singular_stratification": {
            "smooth_open_stratum": "both rank-one factors have nonzero 5x2 matrix",
            "first_endpoint": "the first rank-one factor is the vertex and the second has rank one",
            "second_endpoint": "the second rank-one factor is the vertex and the first has rank one",
            "endpoint_intersection": "empty on the positive two-node-norm link",
            "endpoint_projective_isomorphism_type": "CP^4 for each endpoint",
            "endpoint_complex_dimension": 4,
            "ambient_projective_complex_dimension": 10,
            "complete_singular_locus": "two disjoint CP^4 endpoint strata",
        },
        "incidence_resolution": {
            "one_factor": "Tot(O_CP4(-1) direct_sum O_CP4(-1)) -> RankLeq1(5x2)",
            "two_factor": "the product of the two one-factor incidence resolutions",
            "complex_dimension": 12,
            "exceptional_fibre_over_one_vertex": "CP^4",
            "surjective": True,
            "proper_after_positive_node_norm_reduction": True,
            "connected_fibres": True,
            "equivariant_for_lifted_SO3": True,
            "node_norm_level": "positive weighted ellipsoids in (a1,a2) and (b1,b2) over CP^4 x CP^4",
            "node_phase_action": "U(1)_A x U(1)_B, free because both physical node norms are positive",
            "reduced_resolution": "compact connected Kahler manifold of complex dimension 10",
        },
        "rotation_zero_fibre": {
            "moment_map": "the lifted diagonal SO(3) moment map pulled back through the equivariant incidence resolution",
            "nonempty_witness": "the imported all-m=0 bounded candidate-16 point",
            "connectedness_input": "Kirwan connectedness for every fibre of the moment map on a compact connected Hamiltonian K-manifold",
            "resolved_zero_fibre_connected": True,
            "target_zero_fibre_is_continuous_image": True,
            "target_zero_fibre_connected": True,
            "singular_target_treated_as_orbifold": False,
        },
        "classification": {
            "candidate16_complete_singular_locus_classified": True,
            "two_endpoint_CP4_strata": True,
            "positive_norm_incidence_resolution_compact_connected_kahler": True,
            "incidence_resolution_fibres_connected": True,
            "lifted_rotation_zero_fibre_nonempty": True,
            "lifted_rotation_zero_fibre_connected": True,
            "global_orbifold_claim": False,
            "occupation_strata_glued": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 16's singularity is not a current degeneracy. It consists of two endpoint CP4 strata created when one transformed rank-one factor collapses. A smooth compact incidence resolution retains the lifted Hamiltonian SO(3) action; connectedness of its zero fibre descends through connected resolution fibres to the singular target. Thus the fixed-occupation rotation-zero link is connected without declaring the target an orbifold.",
        "next_gate": "glue candidate-16 across its scalar occupation cone, then combine with the phase-reduced candidate-17/18/20 divisors without identifying backgrounds",
        "claim_boundary": "This classifies candidate 16 at each fixed positive active occupation after node-phase quotient. It does not construct a global orbifold, glue different occupation strata, perform final residual descent, prove all-orders integration, or supply causal, observational or quantum transport.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre",
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
        raise AssertionError("candidate-16 singular rotation-zero certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_SINGULAR_ROTATION_ZERO_FIBRE: PASS")


if __name__ == "__main__":
    main()
