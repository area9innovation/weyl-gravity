#!/usr/bin/env python3
"""Generate fail-closed atlas rows for the Bridge Phase-1 synthesis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST_REL = "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json"
OUT = ROOT / "residual_atlas/bridge-phase1-einstein-extra-contribution-fragment-v1.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict: return {"status": status, "statement": statement}


def build() -> dict:
    manifest = json.loads((ROOT / MANIFEST_REL).read_text())
    evidence = [{"path": MANIFEST_REL, "result_id": manifest["result_id"], "sha256": sha(ROOT / MANIFEST_REL)}]
    entries = []
    for trace in manifest["branch_traces"]:
        branch = trace["branch_id"]
        parity = "axial" if "axial" in branch else "polar"
        carrier = "Einstein-image q-primary" if branch.startswith("einstein") else "extra p-primary cofiber"
        third_status = "CERTIFIED" if branch == "extra_axial" else "NO_CERTIFIED_MAP"
        entries.append({
            "id": f"einstein.ph.wm.phase1.{branch}",
            "scope": {
                "theory": "Einstein-Maxwell source inside Weyl-Maxwell target",
                "background": "compactified magnetically supported Plebanski-Hacyan product",
                "boundaries": "closed S1_L x S2 before final stabilizer reduction",
                "charge_sector": "fixed N=2 and Q_e; total charge cancellation kept distinct from separate neutrality",
                "carrier": carrier, "degree": "linear through scoped third order", "parity": parity,
                "ell": "generic >=2; lower strata only where separately certified", "m": "all certified labels",
                "k": "all certified compact momenta; third-order fixture k=0", "omega": "q/p primary shells; third-order fixture four occupied original shells",
            },
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": third_status, "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": claim("CERTIFIED", trace["linear"]),
                "lee_wald": claim("CERTIFIED", trace["pairing"]),
                "taub_maps": claim("CERTIFIED", trace["taub"]),
                "resonance": claim(third_status, trace["third_order"]),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": claim("OPEN", "The complete bounded common zero remains open; the exact blockwise criterion is certified."),
                    "smooth_secular": claim("CERTIFIED", "The finite exponential-polynomial five-covector criterion is theorem-frozen."),
                    "causal_retarded": claim("NO_CERTIFIED_MAP", "No causal/retarded correction carrier is imported by this synthesis."),
                },
            },
            "evidence": evidence,
            "claim_boundary": "Publication-independent Phase-1 structural crosswalk only. Einstein inclusion is not symplectic equivalence; total charge cancellation is not separate neutrality; smooth secular solvability is not bounded or causal solvability; no particle or quantum claim is made.",
        })
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "einstein_bridge",
        "generated_by": "bridge/phase1/generate_bridge_phase1_atlas_fragment.py", "generated_by_sha256": sha(SCRIPT),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": entries,
        "verification_commands": ["python3 bridge/phase1/generate_bridge_phase1_atlas_fragment.py --check", "python3 residual_atlas/validate_fragment.py residual_atlas/bridge-phase1-einstein-extra-contribution-fragment-v1.json"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true"); g.add_argument("--check", action="store_true"); args = ap.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit: OUT.write_text(rendered); return 0
    if not OUT.exists() or OUT.read_text() != rendered: raise SystemExit("FAIL: stale Bridge Phase-1 atlas fragment")
    print("PASS: Bridge Phase-1 atlas fragment is current"); return 0


if __name__ == "__main__": raise SystemExit(main())
