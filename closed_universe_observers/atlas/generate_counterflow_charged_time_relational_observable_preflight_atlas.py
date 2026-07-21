#!/usr/bin/env python3
"""Generate atlas row for the charged-time Observer preflight."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = Path(__file__).resolve()
CERT = ROOT / "closed_universe_observers/certificates/COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1.json"
OUT = ROOT / "residual_atlas/counterflow-charged-time-relational-observable-preflight-fragment-v1.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def claim(status, statement): return {"status": status, "statement": statement}

def build():
    v=json.loads(CERT.read_text())
    if not v["flags"]["CHARGED_TIME_EVENT_MAP_CONTRACT_CERTIFIED"]: raise AssertionError("preflight unavailable")
    return {"schema":"pure-weyl-residual-atlas-fragment-v1","schema_version":"1.0.0","team":"observer","generated_by":str(GEN.relative_to(ROOT)),"generated_by_sha256":sha(GEN),"status_vocabulary":["CERTIFIED","OBSTRUCTED","OPEN","NOT_APPLICABLE","NO_CERTIFIED_MAP"],"description_axes":["causal","symplectic","nonlinear","observational","quantum"],"entries":[{
      "id":"observer.two_phase_counterflow.unrestricted_charged_time_event_map_contract",
      "scope":{"theory":"selected two-phase counterflow action; theorem-first receiver contract only","background":"stationary Berger R x S3, a=1, c_squared=9/40","boundaries":"closed S3; compact receiver support; lifted phase chart","charge_sector":"unrestricted Q_rel; R_rel and raw D charged physical symmetries","carrier":"global Darboux pair (psi_rel,Q_rel) plus a conditional compact local gauge-neutral receiver three-form","degree":0,"parity":"relative scalar clock; no gravitational parity crosswalk","ell":"global clock ell=0; receiver all-Hodge class not yet supplied","m":0,"k":"NOT_APPLICABLE","omega":"clock velocity 3/4+sqrt(10)q/(24*pi^2)"},
      "descriptions":{"causal":"CERTIFIED","symplectic":"CERTIFIED","nonlinear":"NO_CERTIFIED_MAP","observational":"OPEN","quantum":"NO_CERTIFIED_MAP"},
      "mode_data":{"dispersion":claim("CERTIFIED","The unrestricted global pair has exact charged-time Hamiltonian flow and a monotone lifted chart when total Q_rel>0."),"lee_wald":claim("CERTIFIED","The global Darboux pairing has rank two; the nonhomogeneous descended receiver pairing remains missing."),"taub_maps":claim("NO_CERTIFIED_MAP","No selected-action q2 observer receiver is imported."),"resonance":claim("NO_CERTIFIED_MAP","The global clock has a secular zero Jordan block; no detector resonance claim follows."),"second_order":{"equation":"L_barPhi v = -(1/2) D^2 E_barPhi[u,u]","bounded_or_finite_quasiperiodic":claim("NO_CERTIFIED_MAP","Unrestricted bounded health fails already in the global Jordan block and no observer q2 is supplied."),"smooth_secular":claim("NO_CERTIFIED_MAP","No action-derived receiver source is supplied."),"causal_retarded":claim("OPEN","The parent is causal and the event-map contract is local-gauge closed, but no nontrivial physical receiver class is certified.")}},
      "evidence":[{"path":str(CERT.relative_to(ROOT)),"result_id":v["result_id"],"sha256":sha(CERT)}],"claim_boundary":v["claim_boundary"]}],
      "verification_commands":["python3 closed_universe_observers/generate_counterflow_charged_time_relational_observable_preflight.py --check","python3 closed_universe_observers/verify_counterflow_charged_time_relational_observable_preflight.py","python3 -m pytest -q closed_universe_observers/tests/test_counterflow_charged_time_relational_observable_preflight.py","python3 residual_atlas/validate_fragment.py residual_atlas/counterflow-charged-time-relational-observable-preflight-fragment-v1.json"]}

def render(v): return json.dumps(v,indent=2,sort_keys=True)+"\n"
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--emit",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); v=build()
    if a.emit: OUT.write_text(render(v))
    if a.check and OUT.read_text()!=render(v): raise AssertionError("atlas drift")
    print("COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_ATLAS: PASS")
