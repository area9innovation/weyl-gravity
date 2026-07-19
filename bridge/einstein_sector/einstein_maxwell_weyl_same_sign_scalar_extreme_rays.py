"""Classify the universal scalar-null occupation cone on same-sign n=(1,2) fibres."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.schema.json"
INPUTS = {
    "scalar_classifier": ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json",
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
}

NODES = [
    {"id": "q_minus_n2", "n": 2, "branch": "q_minus", "current_sign": -1, "mass_over_n_squared": sp.Rational(3, 2) - sp.sqrt(3) / 2},
    {"id": "p_extra_n2", "n": 2, "branch": "p_extra", "current_sign": 1, "mass_over_n_squared": sp.Rational(4, 3)},
    {"id": "q_plus_n2", "n": 2, "branch": "q_plus", "current_sign": 1, "mass_over_n_squared": sp.Rational(3, 2) + sp.sqrt(3) / 2},
    {"id": "q_minus_n1", "n": 1, "branch": "q_minus", "current_sign": -1, "mass_over_n_squared": 6 - 2 * sp.sqrt(3)},
    {"id": "p_extra_n1", "n": 1, "branch": "p_extra", "current_sign": 1, "mass_over_n_squared": sp.Rational(16, 3)},
    {"id": "q_plus_n1", "n": 1, "branch": "q_plus", "current_sign": 1, "mass_over_n_squared": 6 + 2 * sp.sqrt(3)},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alternating_supports() -> list[tuple[int, ...]]:
    result = []
    for support in itertools.combinations(range(6), 4):
        signs = [NODES[index]["current_sign"] for index in support]
        if signs in ([-1, 1, -1, 1], [1, -1, 1, -1]):
            result.append(support)
    return result


def ray_record(ray_index: int, support: tuple[int, ...]) -> dict[str, object]:
    node_ids = [NODES[index]["id"] for index in support]
    weights = []
    for local_index, global_index in enumerate(support):
        node = NODES[global_index]
        others = [node_ids[j] for j in range(4) if j != local_index]
        denominator = "*".join(f"(x_{node['id']}-x_{other})" for other in others)
        weights.append({
            "node_id": node["id"],
            "formula": f"1/(({node['current_sign']})*({node['n']}^2)*{denominator})",
            "strictly_positive_by_order": True,
        })
    return {"ray_id": f"R{ray_index}", "support": node_ids, "weight_formula": weights}


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    scalar = records["scalar_classifier"]
    if scalar["summary"]["positive_farkas_candidate_indices"] != list(range(16, 22)):
        raise AssertionError("same-sign collision set changed")
    ledger = records["candidate_ledger"]["candidate_ledger"]
    rows = ledger["rows"]
    if any(rows[index - 1]["canonical_signed_momenta"] != [1, 2] for index in range(16, 22)):
        raise AssertionError("same-sign momentum scope changed")

    masses = [node["mass_over_n_squared"] for node in NODES]
    if not all(sp.simplify(masses[index + 1] - masses[index]).is_positive is True for index in range(5)):
        raise AssertionError("universal moment-curve node order changed")
    supports = alternating_supports()
    expected = [(0, 1, 3, 4), (0, 1, 3, 5), (0, 2, 3, 4), (0, 2, 3, 5)]
    if supports != expected:
        raise AssertionError("positive circuit supports changed")
    rays = [ray_record(index, support) for index, support in enumerate(supports, 1)]
    candidate_rows = [
        {
            "candidate_index": index,
            "rho": rows[index - 1]["rho"],
            "ray_ids": [ray["ray_id"] for ray in rays],
            "node_substitution": "x_(branch,n)=sqrt(rho+m_branch^2/n^2)",
        }
        for index in range(16, 22)
    ]
    return {
        "schema": "einstein-maxwell-weyl-same-sign-scalar-extreme-rays-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_EXTREME_RAYS",
        "result_state": "UNIVERSAL_FOUR_RAY_SCALAR_NULL_CONE_ON_ALL_SAME_SIGN_FIBRES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_UNIVERSAL_POSITIVE_RHO_SAME_SIGN_SCALAR_OCCUPATION_CONE",
        "scope": {
            **scalar["scope"],
            "background": "arbitrary rho>0 same-sign n=(1,2) compact product fibre; candidates 16--21 instantiated separately",
            "carrier": "six nonnegative absolute-current occupations for q-minus, p-extra and q-plus on n=1,2",
        },
        "moment_curve_reduction": {
            "column_formula": "current_sign(branch)*n^2*(x^2,x,1), x=omega/n=sqrt(rho+m_branch^2/n^2)",
            "ordered_nodes": [
                {**node, "mass_over_n_squared": sp.sstr(node["mass_over_n_squared"])} for node in NODES
            ],
            "strict_order_independent_of_rho": True,
            "middle_gap_witness": "(6-2*sqrt(3))-(6+2*sqrt(3))/4=(9-5*sqrt(3))/2>0 because 81>75",
            "current_sign_sequence": [-1, 1, 1, -1, 1, 1],
            "circuit_identity": "for four ordered nodes, z_i=1/prod_(j!=i)(x_i-x_j) obeys sum_i z_i*x_i^d=0 for d=0,1,2 and has signs (-,+,-,+)",
        },
        "extreme_rays": rays,
        "candidate_rows": candidate_rows,
        "classification": {
            "all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays": True,
            "every_extreme_ray_contains_both_q_minus_nodes": True,
            "every_extreme_ray_chooses_one_positive_branch_per_fibre": True,
            "candidates_16_through_21_instantiated_without_background_identification": True,
            "rotation_or_resonance_zero_loci_joined": False,
            "full_bounded_cones_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The scalar H/Px/Rc common zero on any same-sign fibre is the nonnegative span of four universal support-minimal rays. The remaining bounded problem is a finite lift of those four supports through rotations and the candidate-specific resonance map.",
        "next_gate": "for each of candidates 16--21, lift all four extreme-ray supports through the exact rotation-zero and cross-fibre resonance-zero varieties",
        "claim_boundary": "This classifies only the scalar nonnegative occupation cone. It does not assert that arbitrary sums of lifted ray amplitudes kill the quadratic resonance map, classify the six full real bounded cones, or make higher-lifecycle claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_scalar_extreme_rays --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_scalar_extreme_rays",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_scalar_extreme_rays",
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
        raise AssertionError("same-sign scalar extreme-ray certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_EXTREME_RAYS: PASS")


if __name__ == "__main__":
    main()
