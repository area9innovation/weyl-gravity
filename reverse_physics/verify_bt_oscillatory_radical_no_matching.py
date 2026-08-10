#!/usr/bin/env python3
"""Independent verifier for the BT oscillatory radical no-matching theorem."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-oscillatory-radical-no-matching-v1.schema.json")
def sha(p):
 d=hashlib.sha256()
 with open(os.path.join(ROOT,p),"rb") as h:
  for b in iter(lambda:h.read(65536),b""):d.update(b)
 return d.hexdigest()
def verify(path):
 c=json.load(open(path,encoding="utf-8"));s=json.load(open(SCHEMA,encoding="utf-8"));checks={"strict_schema":not list(Draft202012Validator(s).iter_errors(c))}
 q=c.get("charge_ledger",{});checks["published_charge_assignments"]=(q.get("q_b_Omega")==1 and q.get("q_b_Upsilon")==-1 and q.get("q_b_Upsilon_dagger")==-1 and q.get("q_Q_t")==-2 and "preserves" in q.get("dagger",""))
 rows=c.get("exact_closure",{}).get("rows",[]);checks["exhaustive_fixture"]=(len(rows)==19 and all(r.get("support")==[-r["oscillatory_power"]-2*r["squeeze_power"]] and r.get("trace")=={"numerator":0,"denominator":1} and r.get("strictly_negative") for r in rows))
 e=c.get("endpoint_comparison",{});checks["neutral_endpoint_cannot_match"]=(e.get("charge")==0 and len(e.get("neutral_basis",[]))==3 and e.get("matching_result")=="NO_OSCILLATORY_OR_Q_T_CONTRIBUTION_TO_NEUTRAL_C0_C1_C2")
 g=c.get("coisometry_gate",{});checks["coisometry_boundary"]=(g.get("published_identity")=="R_t*R_t^dagger=1" and "not stated" in g.get("unpublished_identity","") and "defect/range" in g.get("consequence",""))
 d=c.get("disposition",{});checks["claim_boundary"]=(d.get("oscillatory_endpoint_matching")=="EXACT_CHARGE_OBSTRUCTION" and d.get("three_neutral_endpoint_constants")=="UNDETERMINED" and d.get("physical_nlo_probability")=="NOT_ESTABLISHED")
 ins=c.get("provenance",{}).get("inputs",[]);checks["hashes"]=(len(ins)==3 and all(x.get("sha256")==sha(x.get("path","")) for x in ins));ok=all(checks.values())
 for n,v in checks.items():print(f"[{'PASS' if v else 'FAIL'}] {n}")
 print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})");return ok
def main(argv=None):p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args(argv);return 0 if verify(a.verify) else 1
if __name__=="__main__":sys.exit(main())
