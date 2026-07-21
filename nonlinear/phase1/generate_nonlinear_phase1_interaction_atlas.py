#!/usr/bin/env python3
"""Generate fail-closed Phase-1 nonlinear atlas entries without cross-scope identification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT_REL = "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json"
GEN_REL = "nonlinear/phase1/generate_nonlinear_phase1_interaction_atlas.py"
OUT = ROOT / "residual_atlas/nonlinear-phase1-interaction-disposition-fragment-v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict:
    return {"status": status, "statement": statement}


def second_order(bounded: dict, secular: dict, causal: dict) -> dict:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": bounded,
        "smooth_secular": secular,
        "causal_retarded": causal,
    }


def evidence() -> list[dict]:
    return [{"path": CERT_REL, "result_id": "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1", "sha256": digest(ROOT / CERT_REL)}]


def build() -> dict:
    entries = [
        {
            "id": "nonlinear.berger.gravity_maxwell.phase1.interaction_disposition",
            "scope": {
                "theory": "gravity-clock-Maxwell BV action",
                "background": "frozen positive rational Berger-clock fixture",
                "boundaries": "closed compact Cauchy slice",
                "charge_sector": "fixed magnetic/background bundle of the pinned carrier",
                "carrier": "typed 64-row BV complex and one cyclic retained 36-row SDR",
                "degree": "action-derived q2/q3 and retained ell3",
                "parity": "complete pinned retained carrier; no branch-parity projection",
                "ell": "NOT_APPLICABLE_NO_HARMONIC_CROSSWALK",
                "m": "NOT_APPLICABLE_NO_HARMONIC_CROSSWALK",
                "k": "NOT_APPLICABLE_NO_HARMONIC_CROSSWALK",
                "omega": "NOT_APPLICABLE_NO_HARMONIC_CROSSWALK",
            },
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": claim("NOT_APPLICABLE", "This representative-level interaction synthesis does not construct a harmonic dispersion relation."),
                "lee_wald": claim("NOT_APPLICABLE", "The certified pairing is the retained odd BV cyclic pairing, not a new Lee-Wald mode theorem."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "No Taub map is used to decide the retained cyclic deformation class."),
                "resonance": claim("OPEN", "The complete bounded cyclic full-BV class through input order two remains open after invalidation of the former witness."),
                "second_order": second_order(
                    claim("NOT_APPLICABLE", "This is a cyclic deformation problem rather than a second-order solution-extension claim."),
                    claim("NOT_APPLICABLE", "No secular correction class is declared for this interaction representative."),
                    claim("NO_CERTIFIED_MAP", "Unary causal compatibility does not construct interacting retarded products."),
                ),
            },
            "evidence": evidence(),
            "claim_boundary": "Exact retained representative and full-BV cyclicity are certified, physical-action removal is certified through input order two, but survival on cohomology or modulo the complete declared cyclic complex and every branch-resolved interpretation remain open.",
        },
        {
            "id": "nonlinear.counterflow.phase1.q2_charge.nonactivation",
            "scope": {
                "theory": "repaired q70 two-phase counterflow action",
                "background": "selected positive Berger fixture and connected trace-healthy same-field stationary family",
                "boundaries": "closed compact Cauchy slice; selected-fixture causal parent only",
                "charge_sector": "unrestricted and fixed-Q_rel explicitly distinct",
                "carrier": "repaired q70 parent before any action-specific q2 derivation",
                "degree": "requested q2 and charge-sector consistency",
                "parity": "j=1/2 both-k physical health obstruction precedes nonlinear activation",
                "ell": "j=1/2 isotype; not identified with the gravity-Maxwell retained carrier",
                "m": "+/-1/2",
                "k": "+/-1/2",
                "omega": "Hamiltonian-Hopf quartet throughout the connected family",
            },
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": "OBSTRUCTED",
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": claim("OBSTRUCTED", "The familywide j=1/2 Hamiltonian-Hopf factor prevents selection of a robust stationary clock candidate."),
                "lee_wald": claim("CERTIFIED", "The obstructing physical sector is nonradical; it is not deleted as gauge."),
                "taub_maps": claim("NOT_APPLICABLE", "No counterflow q2 was activated, so no Taub map is inferred."),
                "resonance": claim("NOT_APPLICABLE", "Candidate-specific nonlinear resonance was not activated after the earlier health obstruction."),
                "second_order": second_order(
                    claim("NOT_APPLICABLE", "The q2/charge calculation is NOT_ACTIVATED, not a missing pass."),
                    claim("NOT_APPLICABLE", "No secular counterflow extension was attempted after terminal nonselection."),
                    claim("NO_CERTIFIED_MAP", "The selected-fixture Green result is not a familywide nonlinear retarded theorem."),
                ),
            },
            "evidence": evidence(),
            "claim_boundary": "The counterflow q2/charge calculation is NOT_ACTIVATED because the declared same-field candidate fails the prior robust linear-health gate. This is not a nonlinear no-go and does not apply to changed action architectures.",
        },
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "nonlinear",
        "generated_by": GEN_REL,
        "generated_by_sha256": digest(ROOT / GEN_REL),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "verification_commands": [
            "python3 nonlinear/phase1/generate_nonlinear_phase1_interaction_disposition.py --check",
            "python3 nonlinear/phase1/verify_nonlinear_phase1_interaction_disposition.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/nonlinear-phase1-interaction-disposition-fragment-v1.json",
        ],
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUT.write_text(rendered, encoding="utf-8")
        return 0
    if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
        raise SystemExit("FAIL: stale nonlinear Phase-1 atlas fragment")
    print("PASS: nonlinear Phase-1 atlas fragment is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
