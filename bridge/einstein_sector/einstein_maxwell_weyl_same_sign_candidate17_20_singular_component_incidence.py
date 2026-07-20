"""Certify that candidate-17/20 singular components meet physically."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.schema.json"
INPUTS = {
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    singular = records["singular_locus"]
    product = singular["two_parity_product"]
    if product["irreducible_components"] != 2 or product["intersection_complex_dimension"] != 8:
        raise AssertionError("candidate-17/20 singular incidence changed")
    sections = records["sections"]
    section_flags = sections["classification"]
    if not (
        section_flags["candidate17_every_positive_occupation_has_singular_rotation_zero_point"]
        and section_flags["candidate20_every_positive_occupation_has_singular_rotation_zero_point"]
    ):
        raise AssertionError("candidate-17/20 positive-occupation sections changed")
    witness = sections["candidate17_20_section"]
    if "S_plus x S_minus" not in witness["singularity_witness"]:
        raise AssertionError("candidate-17/20 section no longer lies in the component intersection")
    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-singular-component-incidence-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_COMPONENT_INCIDENCE",
        "result_state": "CANDIDATE17_20_SINGULAR_ROTATION_ZERO_COMPONENT_IMAGES_INTERSECT_AT_EVERY_POSITIVE_OCCUPATION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_POSITIVE_ACTIVE_OCCUPATION_PAIR_ON_CANDIDATES_17_AND_20",
        "scope": {
            **singular["scope"],
            "carrier": "the complete singular locus of both third-transvectant parity factors on every positive fixed-active-occupation level",
        },
        "incidence_theorem": {
            "singular_components": [
                "Sigma_plus=S_plus x K_minus",
                "Sigma_minus=K_plus x S_minus",
            ],
            "intersection": "Sigma_plus intersect Sigma_minus=S_plus x S_minus",
            "intersection_complex_dimension": 8,
            "positive_occupation_intersection_witness": witness["amplitudes"],
            "witness_membership": witness["singularity_witness"],
            "occupation_checks": witness["occupation_check"],
            "rotation_moment_maps": sections["universal_section"]["rotation_moment_maps"],
            "node_phase_actions_free": sections["universal_section"]["node_phase_actions_free"],
        },
        "group_descent": {
            "intersection_is_invariant": "S_plus x S_minus is invariant under both common node phases and lifted diagonal SO(3)",
            "quotient_images_intersect": "the images of Sigma_plus and Sigma_minus in the singular rotation-zero quotient meet at the orbit of the explicit positive-occupation intersection witness",
            "component_label_separation_lower_bound": 1,
            "contrast_candidate18": "candidate 18 excludes its singular-component intersection when N_minus>0; candidates 17/20 retain theirs",
        },
        "classification": {
            "candidate17_positive_occupation_singular_component_images_intersect": True,
            "candidate20_positive_occupation_singular_component_images_intersect": True,
            "candidate17_20_component_labels_prove_quotient_separation": False,
            "candidate17_20_each_singular_component_connected": False,
            "candidate17_20_complete_singular_rotation_zero_quotient_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Unlike candidate 18, candidates 17 and 20 retain a physical positive-occupation intersection of their two algebraic singular components. Their quotient images meet on an explicit rotation-zero orbit, so component labels alone cannot prove disconnection. Complete connectedness remains open.",
        "next_gate": "classify connectedness inside each candidate-17/20 singular rotation-zero component and determine whether every component meets the explicit intersection orbit",
        "claim_boundary": "This proves component incidence at every positive occupation, not connectedness of either singular component or of the complete singular rotation-zero quotient. It does not glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence",
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
        raise AssertionError("candidate-17/20 singular incidence certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_COMPONENT_INCIDENCE: PASS")


if __name__ == "__main__":
    main()
