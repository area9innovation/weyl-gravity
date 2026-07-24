#!/usr/bin/env python3
"""Generate Paper 16's claim map and append-only coverage overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl.tex"
OUTPUT = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl-claim-map.json"
COVERAGE = ROOT / "planning/paper-coverage/phase4-paper16-endpoint-nonselection-overlay-2026-07-24.json"

AUTHORITIES = {
    "axial_operator": "black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json",
    "factor_filtration": "black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json",
    "endpoint_flux": "black_hole_programme/phase3/axial_null_flux_gram/certificate.json",
    "incoming_global": "black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json",
    "no_growth": "black_hole_programme/phase3/axial_boundary_devissage_no_growth/certificate.json",
    "outgoing_cell": "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/certificate.json",
    "finite_flux": "black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3/certificate.json",
    "threshold": "black_hole_programme/phase4/axial_threshold_exact_structure_v1/certificate.json",
    "qnm_winding": "black_hole_programme/phase3/axial_qnm_projective_evans_contour_completion/full_contour_winding_v1/certificate.json",
    "qnm_selector": "black_hole_programme/phase3/axial_qnm_projective_evans_contour_completion/local_selector_v1/certificate.json",
    "qnm_spin_one_unit": "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json",
    "polar_reach": "black_hole_programme/certificates/BH2B_POLAR_REACH.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def write_or_check(path: Path, payload: dict, check: bool) -> None:
    wanted = encoded(payload)
    if check:
        if not path.exists() or path.read_bytes() != wanted:
            raise SystemExit(f"REFUSED: generated artifact drift: {path.relative_to(ROOT)}")
        print(f"PASS {path.relative_to(ROOT)}")
        return
    path.write_bytes(wanted)
    print(path.relative_to(ROOT))


def authority_map() -> dict:
    result = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text())
        result[name] = {
            "path": relative,
            "sha256": digest(path),
            "result_id": payload.get("result_id"),
            "status": payload.get("status"),
            "result_token": payload.get("result_token"),
        }
    return result


def claim_map() -> dict:
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_16_LORENTZIAN_ENDPOINT_NONSELECTION",
        "result_id": "PAPER16_FOCUSED_ENDPOINT_NONSELECTION_WITH_CONNECTION_EP2",
        "lifecycle_state": "DRAFT_ALLOWED",
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "authorities": authority_map(),
        "certified_scope": {
            "axial_l2_factor_filtration": True,
            "incoming_gram_inertia_1_2_0_all_positive_real": True,
            "Tminus_invertible_all_positive_real": True,
            "outgoing_population_on_declared_cell": True,
            "generic_outgoing_population_off_discrete_set": True,
            "band_limited_pseudo_isometry": True,
            "no_growing_separated_axial_mode": True,
            "exact_scalar_threshold_nonresonance": True,
            "one_connection_level_smith_0_0_2": True,
            "polar_local_horizon_nonselection": True,
        },
        "fail_closed_scope": {
            "explicit_Tplus_band": False,
            "all_positive_real_Tplus_invertibility": False,
            "punctured_threshold_Tplus_interval": False,
            "physical_fredholm_realization": False,
            "green_resolvent_second_order_pole": False,
            "generalized_ringdown": False,
            "time_domain_stability": False,
            "polar_global_connection": False,
            "quantum_positivity_or_unitarity": False,
        },
        "split": {
            "mathematical_structure": "paper/17-pure-weyl-schwarzschild-extension-structure.tex",
            "static_sector": "paper/18-static-bach-flat-black-hole-thermodynamics.tex",
            "computational_supplement": "paper/16-endpoint-nonselection-computational-supplement.tex",
            "source_archive": "paper/14-pure-weyl-black-hole-radiation.tex",
        },
    }


def coverage(claim_sha: str) -> dict:
    claims = [
        (
            "incoming-populated-krein-space",
            "Every positive-real incoming axial trace direction is populated; the action Gram has inertia (1,2,0).",
            "LORENTZIAN-CAUSAL",
        ),
        (
            "outgoing-band-and-genericity",
            "Outgoing population is certified on the declared cell and generic off a locally finite positive-real set.",
            "REDUCED-MODE",
        ),
        (
            "no-growing-separated-mode",
            "The complete filtered axial system has no growing separated mode in the declared half-plane convention.",
            "LORENTZIAN-CAUSAL",
        ),
        (
            "connection-ep2",
            "One enclosed damped QNM has complete connection Smith valuations (0,0,2).",
            "REDUCED-MODE",
        ),
        (
            "threshold-nonresonance",
            "Both scalar factors have exact horizon-regular zero modes and no bounded zero-energy resonance.",
            "LOCAL-ALGEBRAIC",
        ),
    ]
    return {
        "ir": "science-forge-ir-v0",
        "claim_map": str(OUTPUT.relative_to(ROOT)),
        "claim_map_sha256": claim_sha,
        "nodes": [
            {
                "id": f"paper:16-lorentzian-endpoint-nonselection/claim/{slug}",
                "kind": "paper_claim",
                "body": {
                    "paper": "paper:16-lorentzian-endpoint-nonselection",
                    "asserts_lifecycle": "CLASSIFIED",
                    "dependency_tag": tag,
                    "boundary": text,
                    "material": True,
                },
            }
            for slug, text, tag in claims
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    claims = claim_map()
    claim_bytes = encoded(claims)
    claim_sha = hashlib.sha256(claim_bytes).hexdigest()
    write_or_check(OUTPUT, claims, args.check)
    write_or_check(COVERAGE, coverage(claim_sha), args.check)


if __name__ == "__main__":
    main()
