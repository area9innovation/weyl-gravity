"""Generate atlas row for the maximal parity-complete exact sequence."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json"
OUTPUT = ROOT / "residual_atlas/einstein-weyl-parity-complete-residual-exact-sequence-fragment-v1.json"

def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def build_fragment() -> dict:
    c = json.loads(CERTIFICATE.read_text())
    return {"schema":"pure-weyl-residual-atlas-fragment-v1","schema_version":"1.0.0","team":"einstein_nonlinear","generated_by":str(Path(__file__).relative_to(ROOT)),"generated_by_sha256":_sha(Path(__file__)),"description_axes":["causal","symplectic","nonlinear","observational","quantum"],"status_vocabulary":["CERTIFIED","OBSTRUCTED","OPEN","NOT_APPLICABLE","NO_CERTIFIED_MAP"],"entries":[{
        "id":"einstein.ph.wm.parity_complete.maximal_exact_sequence",
        "scope":{"theory":"Einstein-Maxwell -> Weyl-Maxwell -> extra","background":"compactified magnetically supported Plebanski-Hacyan","boundaries":"closed S1_L times S2 before any global stabilizer reduction","charge_sector":"fixed magnetic bundle; Q_e and W_x retained","carrier":"noncyclic all-row mapping cofiber and H0 solution modules","degree":1,"parity":"axial and polar, separately typed","ell":"generic >=2, exceptional 1, homogeneous 0","m":"all certified labels","k":"all allowed compact momenta with zero/nonzero endpoints split","omega":"q, p, exceptional and generalized-zero branches"},
        "descriptions":{"causal":"NO_CERTIFIED_MAP","symplectic":"OBSTRUCTED","nonlinear":"OPEN","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
        "mode_data":{"dispersion":{"status":"CERTIFIED","statement":"All seven authoritative rows have exact Einstein/Weyl/extra dimensions."},"lee_wald":{"status":"CERTIFIED","statement":"Pre-residual pairing ranks add exactly; generic extra blocks have inertia (2,0) and complete blocks (3,1), with zero radicals."},"taub_maps":{"status":"OPEN","statement":"A common moment-map-zero derived carrier is required before residual reduction."},"resonance":{"status":"NOT_APPLICABLE","statement":"Linear exact-sequence theorem only."},"second_order":{"equation":"L_barPhi v = -(1/2) D^2 E_barPhi[u,u]","bounded_or_finite_quasiperiodic":{"status":"OPEN","statement":"Not promoted."},"smooth_secular":{"status":"OPEN","statement":"Not promoted."},"causal_retarded":{"status":"NO_CERTIFIED_MAP","statement":"No retarded carrier."}}},
        "evidence":[{"path":str(CERTIFICATE.relative_to(ROOT)),"result_id":c["result_id"],"sha256":_sha(CERTIFICATE)}],"claim_boundary":c["claim_boundary"]}],
        "verification_commands":["python3 -m bridge.einstein_sector.generate_parity_complete_residual_exact_sequence_atlas --check","python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-parity-complete-residual-exact-sequence-fragment-v1.json"]}

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); f=build_fragment()
    if a.write: OUTPUT.write_text(json.dumps(f,indent=2,sort_keys=True)+"\n")
    if a.check: assert json.loads(OUTPUT.read_text())==f
    if not a.write and not a.check: p.error("one of --write or --check is required")

if __name__=="__main__": main()
