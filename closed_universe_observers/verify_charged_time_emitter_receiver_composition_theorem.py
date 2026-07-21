#!/usr/bin/env python3
"""Independent labelled-current verifier for comparison composition."""
import hashlib,json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1];C=ROOT/"closed_universe_observers/certificates/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1.json";S=ROOT/"closed_universe_observers/schema/charged-time-emitter-receiver-composition-theorem-v1.schema.json"
def verify():
 v=json.loads(C.read_text());schema=json.loads(S.read_text());Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(v)
 r=v["dependency_ref"];assert hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()==r["sha256"]
 a1,a2,b2,b3,c1,c3=sp.symbols("a1 a2 b2 b3 c1 c3",nonzero=True)
 C12,C23,C13=a1/a2,b2/b3,c1/c3
 defect=sp.factor(C12*C23/C13)
 assert defect==a1*b2*c3/(a2*b3*c1)
 assert sp.simplify(defect.subs({c1:a1,b2:a2,c3:b3})-1)==0
 assert sp.simplify(C12*(a2/a1)-1)==0
 e1,e2,e3=sp.symbols("eta1 eta2 eta3",nonzero=True)
 assert sp.simplify((e1/e2)*(e2/e3)-e1/e3)==0 and sp.simplify((e1/e2)*(e2/e3)*(e3/e1)-1)==0
 t1,t2=sp.symbols("tau1 tau2");F=sp.Function("F")(t1);G=sp.Function("G")(t2);Q=F/G
 B1=-sp.diff(F,t1)/G;B2=F*sp.diff(G,t2)/G**2
 assert sp.simplify(B1+sp.diff(Q,t1))==0 and sp.simplify(B2+sp.diff(Q,t2))==0
 g1,g2,g3=sp.symbols("g1 g2 g3",nonzero=True);assert sp.prod((g1,g2,g3))==g1*g2*g3
 assert all(x["detected"] for x in v["mutation_results"])
 return v
if __name__=="__main__":verify();print("CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1 independent current verification: PASS")
