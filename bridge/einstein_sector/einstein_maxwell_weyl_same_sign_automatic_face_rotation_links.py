"""Certify the fixed-occupation rotation-zero links on automatic resonance faces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_links.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_automatic_face_rotation_links.schema.json"
INPUTS = {
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "standard_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    fibre = records["fibre_product"]["classification"]
    faces = records["face_fibres"]
    sections = records["sections"]["classification"]
    stabilizer = records["stabilizer"]
    if not (
        fibre["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]
        and fibre["all_three_rotation_moment_maps_retained_in_formula"]
    ):
        raise AssertionError("bounded fibre-product theorem changed")
    if not faces["classification"]["all_optional_branch_zero_faces_identified"]:
        raise AssertionError("automatic-face theorem changed")
    if not sections["all_rotation_moment_maps_zero_on_sections"]:
        raise AssertionError("nonempty zero-level sections changed")
    if stabilizer["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("rotation stabilizer changed")
    standard_block = records["standard_current"]["theorem"]["block_table"][0]
    if "common parity-independent branch weights" not in standard_block["pullback_relative_operator"]:
        raise AssertionError("standard branch current changed")
    if not records["axial_current"]["classification"]["generic_extra_direct_Lee_Wald_signature_positive_two"]:
        raise AssertionError("axial extra definiteness changed")
    if not records["polar_current"]["classification"]["extra_block_positive_frequency_inertia_2_0"]:
        raise AssertionError("polar extra definiteness changed")

    rows = []
    for face in faces["face_rows"]:
        index = face["candidate_index"]
        automatic = face["automatic_zero_face"]
        if index == 16:
            if automatic["condition"] != "scalar-cone origin only":
                raise AssertionError("candidate 16 acquired a nonzero automatic face")
            rows.append({
                "candidate_index": index,
                "automatic_face": automatic,
                "verdict": "NOT_APPLICABLE",
                "reason": "the automatic face is only the cone vertex, so there is no nonzero fixed-occupation link",
            })
            continue
        if not automatic["ray_generators"]:
            raise AssertionError(f"candidate {index} lost its automatic two-ray face")
        rows.append({
            "candidate_index": index,
            "automatic_face": automatic,
            "fixed_occupation_domain": "every nonzero occupation in every relative support stratum of the automatic two-ray face",
            "amplitude_link": "product over occupied branch/momentum nodes of fixed positive Hermitian-current norm spheres",
            "node_phase_reduction": "quotient by the connected product of node U(1) phases gives a compact connected product of complex projective spaces",
            "symplectic_form": "the action-derived current induces a nonzero signed Fubini-Study form on every occupied factor; negative q_minus factors reverse symplectic orientation but remain nondegenerate",
            "rotation_action": "the diagonal lifted SO(3) action is Hamiltonian and its moment map is the imported (mu_J1,mu_J2,mu_J3)",
            "properness": "automatic because the projective product is compact",
            "nonemptiness": "the certified axisymmetric scalar-cone section lies in the zero fibre",
            "connectedness": "Lerman-Meinrenken-Tolman-Woodward Theorem 1.1(b) makes the projective moment-map zero fibre connected; its preimage under the connected node-phase torus bundle is connected",
            "verdict": "CONNECTED_ON_EVERY_NONZERO_FIXED_OCCUPATION_SUPPORT_STRATUM",
        })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-automatic-face-rotation-links-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_LINKS",
        "result_state": "FIVE_AUTOMATIC_FACE_FIXED_OCCUPATION_ROTATION_ZERO_LINKS_CONNECTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_NONZERO_FIXED_OCCUPATIONS_ON_FIVE_AUTOMATIC_RESONANCE_FACES",
        "scope": {
            **faces["scope"],
            "carrier": "the automatic-resonance two-ray faces on candidates 17--21, stratified by fixed nonzero occupation support",
            "quotient": "before final residual quotient; node phases are used only as an auxiliary symplectic reduction and the connected preimage is restored",
        },
        "theorem": {
            "statement": "For every nonzero fixed occupation on every support stratum of the automatic resonance faces of candidates 17--21, the complete lifted-rotation zero link is nonempty and connected.",
            "proof_steps": [
                "B_i vanishes identically because one complete bilinear factor is zero on the automatic face",
                "fixed nonzero node norms followed by node-phase reduction give a compact connected symplectic product of projective spaces",
                "the lifted SO(3) action is Hamiltonian with proper moment map because the reduced space is compact",
                "non-abelian moment-map connectedness makes the zero fibre connected",
                "the axisymmetric section proves nonemptiness, and the connected torus preimage restores the unquotiented amplitude link",
            ],
            "external_theorem": {
                "authors": "Eugene Lerman, Eckhard Meinrenken, Sue Tolman, Chris Woodward",
                "title": "Non-abelian convexity by symplectic cuts",
                "journal": "Topology 37 (1998) 245--259",
                "doi": "10.1016/S0040-9383(97)00030-X",
                "arxiv": "dg-ga/9603015",
                "theorem": "Theorem 1.1(b): every fibre of a proper moment map on a connected Hamiltonian orbifold for a compact Lie group is connected",
            },
        },
        "candidate_rows": rows,
        "classification": {
            "candidate_16_nonzero_automatic_link": "NOT_APPLICABLE",
            "candidates_17_through_21_automatic_faces_classified": True,
            "all_nonzero_fixed_occupation_rotation_zero_links_nonempty": True,
            "all_nonzero_fixed_occupation_rotation_zero_links_connected": True,
            "negative_current_factors_handled_as_signed_symplectic_forms": True,
            "active_resonance_strata_classified": False,
            "projectivized_active_component_topology_classified": False,
            "singular_strata_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Five automatic resonance faces have no hidden phase-induced splitting after the lifted rotation constraint at fixed occupations: each support-stratum link is one connected nonempty piece. The active resonance components remain the only unresolved real phase/parity topology.",
        "next_gate": "test whether each active resonance component is a connected symplectic orbifold after fixed-norm phase reduction; do not apply moment-map connectedness until nondegeneracy of the restricted current is certified",
        "claim_boundary": "This theorem covers fixed-occupation links only on the automatic resonance faces. It does not classify active resonance components, glue different occupation support strata, compute singularities, perform the final residual quotient, prove all-orders integration, or construct causal, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_rotation_links --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_automatic_face_rotation_links",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_automatic_face_rotation_links",
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
        raise AssertionError("automatic-face rotation-link certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_LINKS: PASS")


if __name__ == "__main__":
    main()
