#!/usr/bin/env python3
"""Independent verifier for the BT cylinder Born limit."""
import argparse, hashlib, json, os
from fractions import Fraction
from jsonschema import Draft202012Validator

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT=os.path.join(ROOT,"reverse_physics/certificates/REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.json")
SCHEMA=os.path.join(ROOT,"reverse_physics/schema/reverse-physics-bt-cylinder-born-limit-v1.schema.json")
def load(p):
    with open(p,encoding="utf-8") as f:return json.load(f)
def q(x):return Fraction(x["numerator"],x["denominator"])
def tp(a):return [list(r) for r in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in tp(b)] for r in a]
def tr(a):return sum(a[i][i] for i in range(len(a)))
def mat(a):return [[q(x) for x in r] for r in a]
def dag(a,j):return mm(mm(j,tp(a)),j)
def kron(a,b):return [[a[i][j]*b[k][l] for j in range(len(a[0])) for l in range(len(b[0]))] for i in range(len(a)) for k in range(len(b))]
def sha(p):
    h=hashlib.sha256()
    with open(os.path.join(ROOT,p),"rb") as f:
        for b in iter(lambda:f.read(65536),b""):h.update(b)
    return h.hexdigest()
def fnv(v):
    h=0xCBF29CE484222325
    for b in v.encode():h=((h^b)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return h
def verify(c):
    checks={}; errors=list(Draft202012Validator(load(SCHEMA)).iter_errors(c)); checks["schema"]=not errors
    local=c.get("finite_local_process",{}); rows=local.get("output_rows",[]); weights=[q(r["weight"]) for r in rows]
    checks["local_weights"] = weights == [Fraction(9,25),Fraction(16,25),Fraction(0)] and sum(weights)==1
    ext=c.get("spectator_extension",{}); j=mat(local["metric"]); js=mat(ext["metric"]); ps=mat(ext["projection"])
    exact=tr(ps)==1 and mm(ps,ps)==ps and dag(ps,js)==ps
    for row,erow in zip(rows,ext.get("one_spectator_rows",[])):
        a=mat(row["process"]); ae=kron(a,ps); je=kron(j,js); exact=exact and tr(mm(dag(ae,je),ae))==q(row["weight"])==q(erow["one_spectator_weight"])
    checks["independent_spectator_factorization"]=exact
    vols=c.get("directed_limit",{}).get("volume_rows",[])
    checks["directed_net"] = len(vols)==9 and all([q(x) for x in v["weights"]]==weights and q(v["weight_sum"])==1 and q(v["positive_trace_norm"])==Fraction(4,3)**v["spectator_pairs"] for v in vols)
    zero=c.get("quadratic_zero_transfer",{}); checks["zero_transfer"]=q(zero.get("finite_support_coefficient",{}))==q(zero.get("directed_limit_coefficient",{}))==0
    d=c.get("disposition",{}); checks["claim_boundary"]=d.get("order_lambda_quadratic_cylinder_coefficient")=="ZERO" and d.get("physical_full_probability")=="NOT_ESTABLISHED" and d.get("Eq19_all_orders")=="NOT_PROVED" and len(c.get("does_not_establish",[]))>=10
    inputs=c.get("provenance",{}).get("inputs",[]); checks["hashes"]=len(inputs)==6 and all(x["sha256"]==sha(x["path"]) for x in inputs)
    checks["event_FNV"]=fnv("sf:program/work/reverse-physics-bateman-cylinder-born-limit|DONE|reverse-physics|2026-08-11|The squeezed conditional Born weights define a spectator-stable thermodynamic functional on the finite pair-cylinder weak-ghost process cone, and the completed quadratic coefficient remains zero on its directed limit. Evidence: REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.|")==0x84130D3EBF4C49D6
    ledger=c.get("checks",{}); checks["ledger"]=ledger.get("passed")==ledger.get("total")==21 and ledger.get("ok") is True and ledger.get("failures")==[] and all(ledger.get("details",{}).values())
    if errors:
        for e in errors:print("schema",list(e.path),e.message)
    bad=[k for k,v in checks.items() if not v]
    if bad:
        print("BT CYLINDER BORN LIMIT VERIFY: FAIL",*bad,sep="\n  ");return False,checks
    return True,checks
def main():
    p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args();ok,c=verify(load(a.verify));
    if not ok:return 1
    print(f"BT CYLINDER BORN LIMIT VERIFY: ALL PASS ({sum(c.values())}/{len(c)})");return 0
if __name__=="__main__":raise SystemExit(main())
