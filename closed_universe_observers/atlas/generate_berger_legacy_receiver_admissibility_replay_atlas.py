#!/usr/bin/env python3
"""Generate the residual-atlas row for the legacy receiver replay."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = Path(__file__).resolve()
CERT = ROOT / "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json"
OUT = ROOT / "residual_atlas/berger-legacy-receiver-admissibility-replay-fragment-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict:
    return {"status": status, "statement": statement}


def build() -> dict:
    cert = json.loads(CERT.read_text())
    evidence = [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha256(CERT)}]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "observer",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": sha256(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "observer.berger.legacy_receiver_admissibility_replay",
            "scope": {
                "theory": "legacy positive-Berger-clock Maxwell probe and massive-two-form emitter fixtures, audited separately; no common action-derived receiver unary theory",
                "background": "positive Berger clock laboratory inside each content-addressed fixture; no identification by background name across setting_id values",
                "boundaries": "compact S3 spatial slices and certificate-specific compact source/detector clock windows; no receiver boundary-flux quotient",
                "charge_sector": "fixed-coupling and apparatus-extension probe sectors with no common receiver charge-fibre map",
                "carrier": "seven exact legacy certificates plus the charged-time physical-receiver interface; no cross-setting mode identification",
                "degree": 0,
                "parity": "even detector functionals; receiver coorientation and primitive clock orientation are not jointly mapped",
                "ell": "NOT_APPLICABLE to localized profiles; homogeneous e1/e2 source sector retained only in its own certificate",
                "m": "NOT_APPLICABLE to localized profiles; no harmonic-name crosswalk",
                "k": "NOT_APPLICABLE to the receiver census",
                "omega": "beta=2*sqrt(10)/3 only in the homogeneous Maxwell transfer; no receiver denominator frequency is certified",
            },
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": "NO_CERTIFIED_MAP",
                "nonlinear": "OBSTRUCTED",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": claim("NOT_APPLICABLE", "The census preserves only certificate-scoped source-to-probe propagation data."),
                "lee_wald": claim("NO_CERTIFIED_MAP", "No legacy row exports a descended nonradical receiver pairing."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "No receiver class is available for a second-order source restriction."),
                "resonance": claim("NO_CERTIFIED_MAP", "The empty common-action completion supplies no operational resonant receiver signature."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": claim("NO_CERTIFIED_MAP", "No receiver is populated on this correction class."),
                    "smooth_secular": claim("NO_CERTIFIED_MAP", "No receiver is populated on this correction class."),
                    "causal_retarded": claim("NO_CERTIFIED_MAP", "Three retarded maps exist only before receiver quotient and pairing descent."),
                },
            },
            "evidence": evidence,
            "claim_boundary": cert["claim_boundary"],
        }],
        "verification_commands": [
            "python3 closed_universe_observers/generate_berger_legacy_receiver_admissibility_replay.py --check",
            "python3 closed_universe_observers/verify_berger_legacy_receiver_admissibility_replay.py",
            "python3 -m pytest -q closed_universe_observers/tests/test_berger_legacy_receiver_admissibility_replay.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/berger-legacy-receiver-admissibility-replay-fragment-v1.json",
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
        raise AssertionError("legacy receiver atlas drift")
    print("BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_ATLAS: PASS")
