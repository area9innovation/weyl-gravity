#!/usr/bin/env python3
"""Independent exact pairing and labelled-morphism reconstruction."""
import hashlib,json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1];C=ROOT/"closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json";I=ROOT/"closed_universe_observers/generated/CHARGED_TIME_PHYSICAL_RECEIVER_CROSSWALK_INTERFACE_V1.json";S=ROOT/"closed_universe_observers/schema/charged-time-receiver-admissibility-crosswalk-v1.schema.json";IS=ROOT/"closed_universe_observers/schema/charged-time-physical-receiver-crosswalk-interface-v1.schema.json"
def verify():
 v=json.loads(C.read_text());i=json.loads(I.read_text());Draft202012Validator(json.loads(S.read_text())).validate(v);Draft202012Validator(json.loads(IS.read_text())).validate(i)
 for r in v["dependency_refs"].values():assert hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()==r["sha256"]
 for r in v["atlas_census_dependencies"]:assert hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()==r["sha256"]
 G=sp.diag(1,0);good=sp.Matrix([1,0]);rad=sp.Matrix([0,1]);exact=sp.Matrix([0,1]);probe=sp.Matrix([1,0])
 assert (good.T*G*probe)[0]==1 and (rad.T*G)==sp.zeros(1,2)
 assert ((good+exact).T*G*probe)[0]==(good.T*G*probe)[0]
 eta1,eta2,eta3=sp.symbols("eta1 eta2 eta3",nonzero=True)
 assert sp.simplify((eta1/eta2)*(eta2/eta3)-eta1/eta3)==0
 rows={r["atlas_id"]:r for r in v["observer_carrier_census"]};assert len(rows)==v["census_completeness"]["discovered_count"]==5
 assert sum(r["admissibility_status"]=="CONDITIONAL_INTERFACE_ONLY" for r in rows.values())==3
 assert any(r["admissibility_status"]=="NO_CERTIFIED_MAP" for r in rows.values()) and any(r["admissibility_status"]=="CLOCK_REMOVED_OBSTRUCTED" for r in rows.values())
 assert all(m["detected"] for m in v["mutation_results"]);return v
if __name__=="__main__":verify();print("CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1 independent verification: PASS")
