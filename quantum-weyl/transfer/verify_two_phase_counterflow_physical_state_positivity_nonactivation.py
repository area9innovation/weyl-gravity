#!/usr/bin/env python3
import copy,hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator,ValidationError
ROOT=Path(__file__).resolve().parents[2]; C=ROOT/"quantum-weyl/transfer/certificates/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1.json"; A=ROOT/"residual_atlas/two-phase-counterflow-physical-state-positivity-nonactivation-fragment-v1.json"; S=ROOT/"quantum-weyl/transfer/schema/two-phase-counterflow-physical-state-positivity-nonactivation-v1.schema.json"
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(c,a,hs=True):
 Draft202012Validator(json.loads(S.read_text())).validate(c)
 if hs:
  for r in c["source_refs"].values():
   p=ROOT/r["path"]; assert sh(p)==r["sha256"] and json.loads(p.read_text())["result_id"]==r["result_id"]
 assert c["activation_gate"]["imported_hadamard_state"]=="NOT_ACTIVATED" and c["activation_gate"]["gate_passed"] is False
 p=c["positivity_disposition"]; assert p["positive_quasifree_state"]=="NOT_ACTIVATED" and p["descended_two_point_form"]=="NOT_COMPUTED" and p["particles"]=="FORBIDDEN" and p["unitarity"]=="FORBIDDEN"; assert a["entries"][0]["descriptions"]["quantum"]=="NO_CERTIFIED_MAP"
def main():
 c=json.loads(C.read_text()); a=json.loads(A.read_text()); verify(c,a); muts=[lambda z:z["activation_gate"].update(gate_passed=True),lambda z:z["activation_gate"].update(imported_hadamard_state="CERTIFIED"),lambda z:z["positivity_disposition"].update(descended_two_point_form="COMPUTED"),lambda z:z["positivity_disposition"].update(positive_quasifree_state="CERTIFIED"),lambda z:z["positivity_disposition"].update(particles="CERTIFIED")]
 for m in muts:
  z=copy.deepcopy(c); m(z)
  try: verify(z,a,False)
  except (AssertionError,ValidationError,KeyError): continue
  raise AssertionError("mutation accepted")
 print(f"TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1 independent verification: PASS ({len(muts)} mutations rejected)")
if __name__=="__main__": main()
