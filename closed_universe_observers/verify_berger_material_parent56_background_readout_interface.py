#!/usr/bin/env python3
"""Independent verifier for the material background-readout interface."""
import hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"closed_universe_observers"
C=P/"certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE.json"
X=P/"certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE_PAYLOAD.json"
S=P/"schema/berger-material-parent56-background-readout-interface-v1.schema.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c,p=json.loads(C.read_text()),json.loads(X.read_text()); Draft202012Validator(json.loads(S.read_text())).validate(c)
 assert sha(X)==c["payload_ref"]["sha256"]
 for r in c["dependency_refs"].values(): assert sha(ROOT/r["path"])==r["sha256"]
 refs=c["dependency_refs"]; parent=json.loads((ROOT/refs["parent_payload"]["path"]).read_text())
 sm=json.loads((ROOT/refs["smearings"]["path"]).read_text()); mixed=json.loads((ROOT/refs["normalized_mixed_unary"]["path"]).read_text())
 assert parent["local_action"]["background_polarizations"]==[[1,0],[0,1]]
 assert [x["clock_support"] for x in p["profile_maps"]]==[x["clock_support"] for x in sm["exact_detector_profiles"]["detectors"]]
 lam0,lam1,f00,f01,f10,f11=sp.symbols("lam0 lam1 f00 f01 f10 f11")
 action=-lam0*f00-lam1*f11
 deriv=[sp.diff(action,lam0,f00),sp.diff(action,f00,lam0),sp.diff(action,lam1,f11),sp.diff(action,f11,lam1)]
 assert deriv==[-1,-1,-1,-1] and p["action_hessian_coefficients"]==["-1"]*4
 blocks=p["row_indexed_mixed_unary_blocks"]
 assert [(b["base_target_row"],b["operator"]) for b in blocks]==[(82,"-delta_gHat(Btilde_0)"),([59,60,61,62],"+(delta_gHat(Btilde_0))^sharp"),(83,"-delta_gHat(Btilde_1)"),([59,60,61,62],"+(delta_gHat(Btilde_1))^sharp")]
 imported=mixed["mixed_Q11_profile"]
 assert imported["nonzero_Q11_operator_block_count"]==4 and imported["nilpotency_defect_count"]==0 and imported["cyclicity_defect_count"]==0
 assert all("[dA]" in row["functional"] for row in p["profile_maps"])
 assert all("zero on the constant Maxwell" in row["zero_mode_restriction"] for row in p["profile_maps"])
 assert all(m["detected"] for m in p["mutations"])
 print("BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE independent verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
