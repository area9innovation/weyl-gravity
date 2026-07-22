#!/usr/bin/env python3
import copy,hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator,ValidationError
ROOT=Path(__file__).resolve().parents[2]; C=ROOT/"quantum-weyl/transfer/certificates/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1.json"; A=ROOT/"residual_atlas/two-phase-counterflow-physical-state-positivity-nonactivation-fragment-v1.json"; S=ROOT/"quantum-weyl/transfer/schema/two-phase-counterflow-physical-state-positivity-nonactivation-v1.schema.json"; R=ROOT/"quantum-weyl/transfer/receipts/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1_TIER_RECEIPT.json"
OUTPUTS={"generator":ROOT/"quantum-weyl/transfer/two_phase_counterflow_physical_state_positivity_nonactivation.py","verifier":Path(__file__),"schema":S,"certificate":C,"tests":ROOT/"quantum-weyl/transfer/tests/test_two_phase_counterflow_physical_state_positivity_nonactivation.py","report":ROOT/"quantum-weyl/reports/two-phase-counterflow-physical-state-positivity-nonactivation-v1.md","atlas":A,"team_brief":ROOT/"notes/d-quotient-quantum-team-brief.md","closeout":ROOT/"reports/quantum-two-phase-counterflow-v2-physical-state-positivity-closeout-2026-07-21.md"}
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(c,a,hs=True):
 Draft202012Validator(json.loads(S.read_text())).validate(c)
 if hs:
  for r in c["source_refs"].values():
   p=ROOT/r["path"]; assert sh(p)==r["sha256"] and json.loads(p.read_text())["result_id"]==r["result_id"]
 assert c["activation_gate"]["imported_hadamard_state"]=="NOT_ACTIVATED" and c["activation_gate"]["gate_passed"] is False
 p=c["positivity_disposition"]; assert p["positive_quasifree_state"]=="NOT_ACTIVATED" and p["descended_two_point_form"]=="NOT_COMPUTED" and p["particles"]=="FORBIDDEN" and p["unitarity"]=="FORBIDDEN"; assert a["entries"][0]["descriptions"]["quantum"]=="NO_CERTIFIED_MAP"
def verify_receipt(receipt,c):
 assert receipt["subject_result_id"]==c["result_id"]
 pins=receipt["source_pins"]
 for key,ref in c["source_refs"].items(): assert pins[key]==ref["sha256"]
 assert set(receipt["output_hashes"])==set(OUTPUTS)
 for key,path in OUTPUTS.items(): assert receipt["output_hashes"][key]==sh(path), key
def main():
 c=json.loads(C.read_text()); a=json.loads(A.read_text()); receipt=json.loads(R.read_text()); verify(c,a); verify_receipt(receipt,c); muts=[lambda z:z["activation_gate"].update(gate_passed=True),lambda z:z["activation_gate"].update(imported_hadamard_state="CERTIFIED"),lambda z:z["positivity_disposition"].update(descended_two_point_form="COMPUTED"),lambda z:z["positivity_disposition"].update(positive_quasifree_state="CERTIFIED"),lambda z:z["positivity_disposition"].update(particles="CERTIFIED")]
 for m in muts:
  z=copy.deepcopy(c); m(z)
  try: verify(z,a,False)
  except (AssertionError,ValidationError,KeyError): continue
  raise AssertionError("mutation accepted")
 bad=copy.deepcopy(receipt); bad["output_hashes"]["certificate"]="0"*64
 try: verify_receipt(bad,c)
 except AssertionError: pass
 else: raise AssertionError("receipt hash mutation accepted")
 print(f"TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1 independent verification: PASS ({len(muts)+1} mutations rejected)")
if __name__=="__main__": main()
