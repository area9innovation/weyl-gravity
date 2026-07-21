#!/usr/bin/env python3
"""Generate the atlas row for operational frequency-ratio nonactivation."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = Path(__file__).resolve()
CERT = ROOT / "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json"
OUT = ROOT / "residual_atlas/berger-legacy-receiver-operational-frequency-ratio-nonactivation-fragment-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict:
    return {"status": status, "statement": statement}


def build() -> dict:
    cert = json.loads(CERT.read_text())
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "observer",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": sha256(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "observer.berger.legacy_receiver_operational_frequency_ratio_nonactivation",
            "scope": {
                "theory": "three incomparable legacy positive-Berger linear source-to-probe carriers; no common action-derived receiver unary theory",
                "background": "positive Berger clock fixture within each exact source certificate; no cross-setting background-name identification",
                "boundaries": "compact S3 slices and certificate-specific source/detector clock windows; no descended receiver boundary quotient",
                "charge_sector": "unmapped legacy fixed-coupling/apparatus-extension sectors; unrestricted receiver charge fibre absent",
                "carrier": "terminal seven-row receiver census, three maximal nonempty linear candidates and one minimal producer request",
                "degree": 0,
                "parity": "even source-to-probe responses; receiver coorientation and primitive clock orientation not jointly mapped",
                "ell": "NOT_APPLICABLE to localized candidates; homogeneous e1/e2 control is confined to its source certificate",
                "m": "NOT_APPLICABLE to localized candidates; no harmonic-name crosswalk",
                "k": "NOT_APPLICABLE to the nonactivation theorem",
                "omega": "coordinate beta=2*sqrt(10)/3 in both homogeneous control channels; no operational receiver frequency",
            },
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": "NO_CERTIFIED_MAP",
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": claim("NOT_APPLICABLE", "The equal homogeneous coordinate frequencies are a control only."),
                "lee_wald": claim("NO_CERTIFIED_MAP", "No receiver class or descended nonradical period is available."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "No operational receiver exists on which to restrict a second-order source."),
                "resonance": claim("NO_CERTIFIED_MAP", "No operational frequency record exists for a resonant signature."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": claim("NOT_APPLICABLE", "This theorem is strictly linear and fail-closed before receiver descent."),
                    "smooth_secular": claim("NOT_APPLICABLE", "This theorem is strictly linear and fail-closed before receiver descent."),
                    "causal_retarded": claim("NO_CERTIFIED_MAP", "Retarded source-to-probe maps do not descend to a physical receiver record."),
                },
            },
            "evidence": [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha256(CERT)}],
            "claim_boundary": cert["claim_boundary"],
        }],
        "verification_commands": [
            "python3 closed_universe_observers/generate_berger_legacy_receiver_operational_frequency_ratio_nonactivation.py --check",
            "python3 closed_universe_observers/verify_berger_legacy_receiver_operational_frequency_ratio_nonactivation.py",
            "python3 -m pytest -q closed_universe_observers/tests/test_berger_legacy_receiver_operational_frequency_ratio_nonactivation.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/berger-legacy-receiver-operational-frequency-ratio-nonactivation-fragment-v1.json",
        ],
    }


def render(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        OUT.write_text(render(value))
    if args.check and OUT.read_text() != render(value):
        raise AssertionError("operational frequency-ratio atlas drift")
    print("BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_ATLAS: PASS")
