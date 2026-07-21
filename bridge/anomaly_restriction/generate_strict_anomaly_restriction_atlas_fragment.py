#!/usr/bin/env python3
"""Generate the fail-closed residual-atlas fragment for anomaly restriction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = Path(__file__).resolve()
CERT_PATH = (
    ROOT
    / "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json"
)
OUTPUT = ROOT / "residual_atlas/strict-anomaly-sector-restriction-obstruction-fragment-v1.json"
VOCABULARY = [
    "CERTIFIED",
    "OBSTRUCTED",
    "OPEN",
    "NOT_APPLICABLE",
    "NO_CERTIFIED_MAP",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict:
    return {"status": status, "statement": statement}


def second_order() -> dict:
    na = claim("NOT_APPLICABLE", "This entry classifies an anomaly restriction chain map, not a second-order field-equation correction.")
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": na,
        "smooth_secular": na,
        "causal_retarded": na,
    }


def mode_data(taub_status: str, taub_statement: str) -> dict:
    return {
        "dispersion": claim("NOT_APPLICABLE", "No harmonic dispersion claim is made by this carrier-map obstruction."),
        "lee_wald": claim("NOT_APPLICABLE", "No new Lee-Wald pairing claim is made."),
        "taub_maps": claim(taub_status, taub_statement),
        "resonance": claim("NOT_APPLICABLE", "No resonance calculation is part of this restriction-map gate."),
        "second_order": second_order(),
    }


def quantum_data(crosswalk_status: str, dependency_status: str, statement: str) -> dict:
    return {
        "entry_kind": "CARRIER_IMPORT_GAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "classical_mode_imported": claim("CERTIFIED", "The declared classical sector artifacts are imported by exact hash."),
        "BRST_cocycle": claim("CERTIFIED", "The three strict local anomaly source classes are certified on the regular Bach locus."),
        "BRST_exactness": claim("NO_CERTIFIED_MAP", "No restricted exactness verdict exists without the missing full chain map."),
        "pairing_status": claim("NOT_APPLICABLE", "This gate does not compare quantum pairings."),
        "compatible_complex_structure": claim("NOT_APPLICABLE", "No quantum complex structure is selected."),
        "Hadamard_two_point_function": claim("NO_CERTIFIED_MAP", "No Hadamard carrier is supplied."),
        "state_space_status": claim("NO_CERTIFIED_MAP", "No state-space transfer follows from local anomaly data."),
        "anomaly_QME_dependency": claim(dependency_status, statement),
        "lifecycle_state": claim("CERTIFIED", "The carrier obstruction itself is exactly classified."),
        "particle_interpretation": claim("NOT_APPLICABLE", "Local anomaly classes are not one-particle states."),
        "carrier_crosswalk": claim(crosswalk_status, statement),
    }


def build() -> dict:
    cert = json.loads(CERT_PATH.read_text())
    evidence = [
        {
            "path": str(CERT_PATH.relative_to(ROOT)),
            "result_id": cert["result_id"],
            "sha256": sha(CERT_PATH),
        }
    ]
    cylinder_statement = (
        "The 15-charge Taub-zero sector is a derived quadratic fibre. "
        "The pinned carrier lacks its Koszul/BFV generators and bulk-to-time-slice transgression."
    )
    berger_statement = (
        "The strict pure-Weyl identity-jet full-BV map is obstructed on the matter-supported Berger "
        "background by the exact metric-antifield defect 961/1920."
    )
    entries = [
        {
            "id": "bridge.anomaly.cylinder_taub_zero_restriction_carrier_gap",
            "scope": {
                "theory": "strict pure-Weyl local BV source to pure-Weyl compact-cylinder derived sector",
                "background": "unit conformal cylinder R x S3",
                "boundaries": "closed oriented S3; temporal/support descent policy not supplied",
                "charge_sector": "derived common zero fibre of all fifteen SO(4,2) Taub moment maps",
                "carrier": "full local Diff x Weyl BV jets to a missing 15-generator BFV/Koszul receiver",
                "degree": "full field/ghost/antifield complex",
                "parity": "even and odd anomaly classes kept distinct",
                "ell": "not harmonic-reduced",
                "m": "not harmonic-reduced",
                "k": "not applicable on S3",
                "omega": "not frequency-reduced",
            },
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "NOT_APPLICABLE",
                "nonlinear": "NO_CERTIFIED_MAP",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": mode_data(
                "CERTIFIED",
                "All fifteen endpoint moment maps and their quadratic Taub interpretation are pinned; their local time-slice lift is not.",
            ),
            "quantum_data": quantum_data(
                "NO_CERTIFIED_MAP", "NO_CERTIFIED_MAP", cylinder_statement
            ),
            "evidence": evidence,
            "claim_boundary": (
                cylinder_statement
                + " No anomaly image, Cartan defect, QME, state, particle or causal claim follows."
            ),
        },
        {
            "id": "bridge.anomaly.berger_strict_pure_weyl_full_bv_map_obstruction",
            "scope": {
                "theory": "strict pure-Weyl local BV source versus matter-coupled Weyl-clock(-Maxwell) target",
                "background": "positive rotating-scalar Berger fixture q=9/40, alpha_B=5",
                "boundaries": "closed Berger S3; temporal/support descent policy not reached",
                "charge_sector": "fixed alpha_B and lambda with delta Q_R=0",
                "carrier": "identity-jet full Diff x Weyl field/ghost/antifield map into the coupled 64-row BV complex",
                "degree": "full field/ghost/antifield complex",
                "parity": "even and odd anomaly classes kept distinct",
                "ell": "not harmonic-reduced",
                "m": "not harmonic-reduced",
                "k": "not applicable on S3",
                "omega": "not frequency-reduced",
            },
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "NOT_APPLICABLE",
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "OBSTRUCTED",
            },
            "mode_data": mode_data(
                "NOT_APPLICABLE",
                "The obstruction occurs before a restricted Taub or resonance calculation.",
            ),
            "quantum_data": quantum_data(
                "OBSTRUCTED", "OBSTRUCTED", berger_statement
            ),
            "evidence": evidence,
            "claim_boundary": (
                berger_statement
                + " An AFN0 density evaluation is not a full BV pullback; the actual coupled anomaly complex remains open."
            ),
        },
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "Einstein/nonlinear bridge",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": sha(GENERATOR),
        "status_vocabulary": VOCABULARY,
        "description_axes": [
            "causal",
            "symplectic",
            "nonlinear",
            "observational",
            "quantum",
        ],
        "entries": entries,
        "verification_commands": [
            "python3 -m bridge.anomaly_restriction.generate_strict_anomaly_restriction_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/strict-anomaly-sector-restriction-obstruction-fragment-v1.json",
            "python3 -m bridge.anomaly_restriction.verify_strict_anomaly_sector_restriction_chain_map_obstruction"
        ],
    }


def text(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = text(build())
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.exists() or OUTPUT.read_text() != expected:
        raise SystemExit("atlas fragment drift")
    print("strict anomaly restriction atlas fragment: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
