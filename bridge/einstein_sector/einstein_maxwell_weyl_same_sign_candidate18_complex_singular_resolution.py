"""Classify and resolve candidate 18's complete complex singular carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.schema.json"
INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_one_check() -> dict[str, object]:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    equations = [f[i] * g[j] - f[j] * g[i] for i, j in combinations(range(5), 2)]
    jacobian = sp.Matrix(equations).jacobian((*f, *g))
    rank_one = {f[0]: 1, **{f[i]: 0 for i in range(1, 5)}, **{g[i]: 0 for i in range(5)}}
    at_rank_one = jacobian.subs(rank_one)
    at_origin = jacobian.subs({value: 0 for value in (*f, *g)})
    if at_rank_one.rank() != 4 or at_origin.rank() != 0:
        raise AssertionError("rank-one determinantal Jacobian changed")
    return {
        "equation_count": len(equations),
        "rank_one_jacobian_rank": at_rank_one.rank(),
        "origin_jacobian_rank": at_origin.rank(),
    }


def build() -> dict[str, object]:
    source = json.loads(INPUT.read_text())
    candidate = source["candidate18_rank_one"]
    if candidate["rank_one_chart"]["one_factor_J_rank"] != 4:
        raise AssertionError("candidate-18 chart rank changed")
    exact = rank_one_check()
    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate18-complex-singular-resolution-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_COMPLEX_SINGULAR_RESOLUTION",
        "result_state": "CANDIDATE18_COMPLETE_COMPLEX_SINGULAR_LOCUS_AND_INCIDENCE_RESOLUTION_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_COMPLEX_CARRIER_BEFORE_NORM_AND_GROUP_REDUCTION",
        "scope": {
            **source["scope"],
            "background": "candidate 18 only",
            "carrier": "the complete complex candidate-18 carrier: ten positive current-orthogonal spectators times two rank-at-most-one 5x2 parity factors",
        },
        "one_factor": {
            **exact,
            "variety": "R=Rank_{<=1}(5x2)",
            "complex_dimension": 6,
            "irreducible": True,
            "singular_locus": "the vertex 0 only",
            "proof": "GL(5,C) x GL(2,C) is transitive on nonzero rank-one matrices; the exact canonical Jacobian rank is four, while all ten minor differentials vanish at the origin",
            "incidence_resolution": "Tot(O_{P^4}(-1) direct-sum O_{P^4}(-1)) -> R",
            "exceptional_fibre": "P^4 over the vertex",
        },
        "complete_carrier": {
            "isomorphism": "C^10_spectator x R_plus x R_minus",
            "complex_dimension": 22,
            "singular_locus": "Sigma_plus union Sigma_minus",
            "Sigma_plus": "C^10 x {0} x R_minus",
            "Sigma_minus": "C^10 x R_plus x {0}",
            "irreducible_singular_components": 2,
            "component_complex_dimension": 16,
            "intersection": "C^10 x {0} x {0}",
            "intersection_complex_dimension": 10,
            "global_incidence_resolution": "C^10 x Tot(O_{P^4}(-1)^oplus2) x Tot(O_{P^4}(-1)^oplus2)",
            "resolution_complex_dimension": 22,
            "resolution_smooth_connected": True,
            "resolution_fibres_connected": True,
        },
        "classification": {
            "candidate18_complete_complex_singular_locus_classified": True,
            "candidate18_global_complex_incidence_resolution_constructed": True,
            "ten_positive_spectators_retained": True,
            "fixed_occupation_real_singular_strata_classified": False,
            "node_phase_singular_reduction_classified": False,
            "lifted_rotation_singular_reduction_classified": False,
            "global_zero_fibre_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 18's complex singularities come only from collapse of one or both rank-one parity factors; the ten positive spectators never create singularities and remain explicit in both components. A smooth connected incidence resolution with connected fibres is now available for the later real Hamiltonian analysis.",
        "next_gate": "impose the real fixed-occupation and lifted-rotation equations on the resolved carrier while retaining all ten spectators; do not infer Kirwan connectedness until the resolved fixed-norm current is shown symplectic",
        "claim_boundary": "This classifies and resolves the complete complex carrier only. It does not classify its real Hermitian fixed-occupation strata, current degeneracy on the resolution, node-phase or lifted-rotation quotients, connected zero fibres, occupation gluing, final residual descent, all-orders integration, or causal, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {"active_divisors": {"path": str(INPUT.relative_to(ROOT)), "sha256": sha(INPUT)}},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution",
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
        raise AssertionError("candidate-18 singular-resolution certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_COMPLEX_SINGULAR_RESOLUTION: PASS")


if __name__ == "__main__":
    main()
