#!/usr/bin/env python3
"""Independent exact checker for the coded polygonal wave certificate."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"

def load(p):return json.loads(p.read_text())
def q(x):return Q(x[0],x[1])

def value_at(breaks:list[Q],values:list[Q],x:Q)->Q:
    x%=1
    for i,(a,b) in enumerate(zip(breaks,breaks[1:])):
        if a<=x<b:return values[i]
    raise ValueError(x)

def translate(breaks:list[Q],values:list[Q],t:Q)->tuple[list[Q],list[Q]]:
    t%=1
    out_breaks=sorted({Q(),Q(1),*((x+t)%1 for x in breaks[:-1])})
    out_values=[value_at(breaks,values,(a+b)/2-t) for a,b in zip(out_breaks,out_breaks[1:])]
    return out_breaks,out_values

def integral(breaks:list[Q],values:list[Q])->Q:
    return sum(((b-a)*v for a,b,v in zip(breaks,breaks[1:],values)),Q())

def square(breaks:list[Q],values:list[Q])->Q:
    return sum(((b-a)*v*v for a,b,v in zip(breaks,breaks[1:],values)),Q())

def distance(left:tuple[list[Q],list[Q]],right:tuple[list[Q],list[Q]])->Q:
    breaks=sorted(set(left[0]+right[0])); total=Q()
    for a,b in zip(breaks,breaks[1:]):
        mid=(a+b)/2; delta=value_at(*left,mid)-value_at(*right,mid);total+=(b-a)*delta*delta
    return total

def digest(fixtures,proof,diagonal):
    return hashlib.sha256(json.dumps({"fixtures":fixtures,"formal_proof":proof,"diagonal_construction":diagonal},sort_keys=True,separators=(",",":")).encode()).hexdigest()

def check(result:dict[str,Any]|None=None):
    r=load(RESULT) if result is None else result;errors=[];fixtures=r.get("fixtures",[])
    if [x.get("id") for x in fixtures]!=["TRIANGLE_RIGHT","QUARTER_MIXED","NONUNIFORM_MIXED"]:errors.append("fixture closure")
    group_checks=energy_checks=modulus_checks=0
    shifts=[Q(),Q(1,12),Q(1,7),Q(2,5)]
    for item in fixtures:
        breaks=[q(x) for x in item["breaks"]]; right=[q(x) for x in item["right"]];left=[q(x) for x in item["left"]]
        if breaks[0]!=0 or breaks[-1]!=1 or breaks!=sorted(set(breaks)) or len(right)!=len(breaks)-1 or len(left)!=len(right):errors.append("partition "+item["id"]);continue
        if integral(breaks,right)!=0 or integral(breaks,left)!=0 or item.get("zero_mean_checks")!=[[0,1],[0,1]]:errors.append("zero mean "+item["id"])
        initial=square(breaks,right)+square(breaks,left)
        if q(item["total_energy"])!=initial:errors.append("energy record "+item["id"])
        for t in shifts:
            rt=translate(breaks,right,t);lt=translate(breaks,left,-t)
            if square(*rt)+square(*lt)!=initial:errors.append("energy isometry "+item["id"]);break
            energy_checks+=1
            for s in shifts:
                if distance(translate(*rt,s),translate(breaks,right,t+s)) or distance(translate(*lt,-s),translate(breaks,left,-t-s)):errors.append("group law "+item["id"]);break
                group_checks+=2
        constant=q(item["translation_bound_constant"]); base_r=(breaks,right);base_l=(breaks,left)
        for row in item.get("time_continuity_moduli",[]):
            k=row["precision"];h=q(row["certified_delta"]);d2=distance(translate(breaks,right,h),base_r)+distance(translate(breaks,left,-h),base_l)
            if d2>constant*h or d2>Q(1,2**(2*k)):errors.append("time modulus "+item["id"]+":"+str(k))
            modulus_checks+=1
    proof=r.get("formal_proof",[]);ids=[x.get("id") for x in proof];expected=["FINITE_CODE","RATIONAL_GROUP","ENERGY_ISOMETRY","CODE_MODULUS","COMPLETION_NAME","REAL_TIME_EXTENSION","CAUCHY_EXISTENCE_UNIQUENESS"]
    if ids!=expected:errors.append("proof-stage closure")
    seen=set()
    for stage in proof:
        if not set(stage.get("depends_on",[]))<=seen:errors.append("proof dependency order "+str(stage.get("id")))
        seen.add(stage.get("id"))
    if [x.get("base") for x in proof[:4]]!=["PRA"]*4 or [x.get("base") for x in proof[4:]]!=["RCA_0"]*3:errors.append("base assignment")
    proof_text=" ".join(x.get("statement","") for x in proof).lower()
    if any(token in proof_text for token in ("wkl_0","aca_0","choice","compactness","subsequence")):errors.append("forbidden proof principle")
    diagonal=r.get("diagonal_construction",{})
    if set(diagonal)!={"inputs","index_rule","output","adjacent_bound","fast_cauchy_bound","independence","logical_boundary"}:errors.append("diagonal closure")
    for token in ("m(k)>=k+4","2^-2(k+3)","2^-(k+2)","2^-(i+1)"):
        if token not in " ".join(diagonal.values()):errors.append("diagonal token "+token)
    if any(token in diagonal.get("logical_boundary","").lower() for token in ("uses compactness","uses a subsequence","uses choice")):errors.append("diagonal logical boundary")
    calculated=digest(fixtures,proof,diagonal)
    if calculated!=r.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":calculated,"fixtures":len(fixtures),"group_checks":group_checks,"energy_checks":energy_checks,"modulus_checks":modulus_checks}

def main():
    errors,s=check();print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**s},sort_keys=True));return bool(errors)
if __name__=="__main__":raise SystemExit(main())
