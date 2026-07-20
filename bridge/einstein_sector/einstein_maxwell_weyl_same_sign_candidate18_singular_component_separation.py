"""Certify candidate 18's positive-occupation singular-component separation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.schema.json"
INPUTS = {
    "singular_resolution": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json",
    "sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    singular = records["singular_resolution"]
    complete = singular["complete_carrier"]
    if complete["irreducible_singular_components"] != 2 or complete["intersection_complex_dimension"] != 10:
        raise AssertionError("candidate-18 singular components changed")
    sections = records["sections"]["classification"]
    if not sections["candidate18_every_positive_occupation_has_singular_rotation_zero_point"]:
        raise AssertionError("candidate-18 rotation-zero section changed")
    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate18-singular-component-separation-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_COMPONENT_SEPARATION",
        "result_state": "CANDIDATE18_POSITIVE_OCCUPATION_SINGULAR_ROTATION_QUOTIENT_HAS_AT_LEAST_TWO_COMPONENTS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_STRICTLY_POSITIVE_NEGATIVE_NODE_OCCUPATION_ON_CANDIDATE18",
        "scope": {
            **singular["scope"],
            "carrier": "the candidate-18 singular locus on every fixed level with strictly positive negative-current active-node occupation, before final residual descent",
        },
        "separation_theorem": {
            "singular_components": ["Sigma_plus=C^10 x {0} x R_minus", "Sigma_minus=C^10 x R_plus x {0}"],
            "intersection": "C^10 x {0} x {0}",
            "negative_node_support": "the negative-current active-node norm is carried only by the g columns of R_plus and R_minus; the ten spectators are positive-current directions",
            "intersection_excluded": "on Sigma_plus intersect Sigma_minus both g columns vanish, so N_minus=0; hence the intersection misses every N_minus>0 level",
            "relative_topology": "the singular fixed-positive-occupation locus is the disjoint union of two nonempty clopen subsets",
            "nonempty_witnesses": "occupy the minus factor or, symmetrically, the plus factor with the certified central m=0 rank-one section",
        },
        "group_descent": {
            "node_phase_invariance": "both vanishing-factor conditions are invariant under the two common node phases",
            "rotation_invariance": "both are invariant under lifted diagonal SO(3)",
            "no_orbit_identification": "neither connected group action exchanges the labelled parity factors; an orbit cannot meet both components without meeting their empty positive-occupation intersection",
            "rotation_zero_nonempty_in_each_component": True,
            "singular_rotation_zero_quotient_component_lower_bound": 2,
        },
        "contrast": {
            "candidate17_20": "their product singular components meet in S_plus x S_minus at positive occupations, so this separation proof does not apply",
            "cross_background_identification": False,
        },
        "classification": {
            "candidate18_positive_occupation_singular_components_separated": True,
            "candidate18_both_singular_components_rotation_zero_nonempty": True,
            "candidate18_singular_rotation_zero_quotient_at_least_two_components": True,
            "candidate18_each_component_connected": False,
            "candidate18_full_rotation_zero_fibre_disconnected": False,
            "smooth_strata_connect_components_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 18's singular quotient is intrinsically componentwise: positive negative-node occupation removes the intersection of its two determinantal singular components, and the physical connected symmetries do not exchange them. The full rotation-zero fibre may still be connected through smooth strata; that question remains open.",
        "next_gate": "determine whether smooth fixed-occupation rotation-zero paths connect the two singular quotient components, while tracking the Lee-Wald radical and all ten spectators",
        "claim_boundary": "This proves a two-component lower bound only for the singular rotation-zero quotient. It does not prove either component connected, disconnect the full smooth-plus-singular zero fibre, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation",
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
        raise AssertionError("candidate-18 singular separation certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_COMPONENT_SEPARATION: PASS")


if __name__ == "__main__":
    main()
