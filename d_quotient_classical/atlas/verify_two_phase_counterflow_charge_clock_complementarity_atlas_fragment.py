#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; A=ROOT/"residual_atlas/two-phase-counterflow-charge-clock-complementarity-fragment-v1.json"
def main():
 d=json.loads(A.read_text());
 if hashlib.sha256((ROOT/d["generated_by"]).read_bytes()).hexdigest()!=d["generated_by_sha256"]: raise AssertionError("generator drift")
 fixed,free=d["entries"]
 if fixed["descriptions"]["symplectic"]!="OBSTRUCTED" or free["descriptions"]["symplectic"]!="CERTIFIED": raise AssertionError("branches conflated")
 if free["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"]!="OBSTRUCTED": raise AssertionError("secular failure promoted")
 print("INDEPENDENT CHARGE-CLOCK ATLAS VERIFIER: PASS")
if __name__=="__main__":main()
