#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the repaired graded q70 parent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json"
RECEIVER = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-causal-bv-parent-v2-fragment.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    receiver = json.loads(RECEIVER.read_text())
    evidence = [
        {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)},
        {"path": str(RECEIVER.relative_to(ROOT)), "result_id": receiver["result_id"], "sha256": _sha(RECEIVER)},
    ]
    entry = {
        "id": "classical.counterflow.berger.q70_graded_cyclic_parent_v2",
        "scope": {
            "theory": "selected fixed-action two-phase counterflow theory with repaired diagonal-U1 chain",
            "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices with compactly supported spacetime sources",
            "charge_sector": "unrestricted parent retains Q_rel; receiver activation may declare the fixed-Q_rel leaf; D and R_rel are not quotiented",
            "carrier": "explicit 70-row graded cyclic BV parent, degree ranks 6/29/29/6, with q54 plus repaired contractible q16",
            "degree": "compact degree -ghost number; all 317 q70 operator blocks have degree +1",
            "parity": "real graded BV carrier with explicit nondegenerate odd pairing",
            "ell": "all spatial harmonics retained; no physical isotypical quotient in this certificate",
            "m": "all left labels retained; conjugate labels governed by the imported q54 real structure",
            "k": "all right weights retained; no Hodge or weight truncation",
            "omega": "full time-differential operator; no characteristic root or positive-frequency selection here",
        },
        "descriptions": {
            "causal": "CERTIFIED",
            "symplectic": "CERTIFIED",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("NO_CERTIFIED_MAP", "The repaired q70 unary is certified, but no physical harmonic quotient or characteristic/Jordan census is computed here."),
            "lee_wald": _claim("CERTIFIED", "The chain-level odd BV pairing is explicit, nondegenerate, real and q70-cyclic; this is not a physical Hilbert or per-mode Gram form."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No q2 or tangent-cone map has yet been rederived against the V2 hash."),
            "resonance": _claim("NO_CERTIFIED_MAP", "Resonance and Jordan data wait for the repaired-parent physical quotient."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("OPEN", "The V2 unary is now an admissible input, but the q2 bounded-correction problem must be recomputed."),
                "smooth_secular": _claim("OPEN", "No V1 q2 hash is accepted automatically by the V2 receiver."),
                "causal_retarded": _claim("CERTIFIED", "Lambda70,+/- is the certified q54 homotopy direct-summed with the support-local repaired S16 block."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "This is the convention-correct degree-plus-one real cyclic causal q70 parent and V2 receiver contract. V1 remains immutable historical evidence. Physical cohomology, mode signs, q2, observers, Hadamard data, anomalies, QME, particles, positivity and unitarity remain open or unmapped.",
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [entry],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_causal_bv_parent_v2.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_causal_bv_parent_v2.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-causal-bv-parent-v2-fragment.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("repaired q70 V2 atlas drifted")
        print("COUNTERFLOW_CAUSAL_BV_PARENT_V2_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
