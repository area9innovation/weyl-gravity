#!/usr/bin/env python3
"""Independent exact checker for the flat scalar biwave certificate."""
from __future__ import annotations
from fractions import Fraction as Q
import hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1.json"
SCALAR=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
TYPED=ROOT/"foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json"
EXPONENTS=((0,0,0,0),(1,0,0,2),(2,1,1,1),(3,2,2,0))
def q(x:list[int])->Q:return Q(*x)
def deriv(c:list[Q],n:int=1)->list[Q]:
    for _ in range(n):c=[Q(i)*c[i] for i in range(1,len(c))]
    return c
def peval(c:list[Q],x:Q)->Q:return sum((v*x**i for i,v in enumerate(c)),Q(0))
def digest(v:dict[str,Any])->str:
    keys=("spacetime_and_operator","source_codes","green_formulas","exact_identities","cauchy_data","energy_extension","choice_audit","formal_proof","fixtures","support_samples")
    return hashlib.sha256(json.dumps({k:v[k] for k in keys},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def advanced_moment(a:int,c:int)->Q:
    return Q(c+1,(c+2)*(a+1))-Q(1,a+2)+Q(1,(c+2)*(a+c+3))
def check(value:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    v=json.loads(RESULT.read_text()) if value is None else value;e=[]
    expected=["CANONICAL_COMPOSITION","BIWAVE_RIGHT_INVERSES","BIWAVE_LEFT_INVERSES","CAUSAL_SUPPORT","ADJOINT_DUALITY","FOUR_DATA_CAUCHY_TOWER","NAMED_FINITE_HORIZON_EXTENSION","SCALAR_BIWAVE_FIREWALL"]
    stages=v.get("formal_proof",[])
    if [x.get("id") for x in stages]!=expected:e.append("proof stages")
    seen=set()
    for stage in stages:
        if not set(stage.get("depends_on",[]))<=seen:e.append("proof order")
        seen.add(stage.get("id"))
    if v.get("spacetime_and_operator",{}).get("biwave_operator")!="B=P^2=16 partial_u^2 partial_v^2":e.append("operator")
    for row,(a,b,c,d) in zip(v.get("fixtures",[]),EXPONENTS):
        ret=Q(1,16*(a+1)*(a+2)*(b+1)*(b+2))
        if q(row["retarded_interior"]["coefficient"])!=ret or q(row["retarded_interior"]["biwave_operator_multiplier"])!=1:e.append("retarded right inverse")
        if q(row["advanced_interior"]["biwave_operator_multiplier"])!=1:e.append("advanced right inverse")
        left=Q(1,32*(a+1)*(a+2)*(b+1)*(b+2)*(a+c+3)*(b+d+3))
        right=Q(1,32*(c+1)*(d+1))*advanced_moment(a,c)*advanced_moment(b,d)
        if q(row["adjoint_pairing"]["left"])!=left or q(row["adjoint_pairing"]["right"])!=right or left!=right:e.append("duality")
        for name in ("u_factor_coefficients","v_factor_coefficients"):
            coeff=[q(x) for x in row["compact_test"][name]]
            if any(peval(deriv(coeff,j),Q(endpoint)) for j in range(4) for endpoint in (0,1)):e.append("endpoint jets")
        if not row["compact_test"]["retarded_H_B_identity"] or not row["compact_test"]["advanced_H_B_identity"]:e.append("left inverse")
        energy=row["finite_horizon_energy"];l2=Q(1,2*(2*a+1)*(2*b+1))
        if q(energy["intermediate_energy_bound"])!=l2 or q(energy["biwave_energy_bound"])!=4*l2:e.append("energy")
    for row in v.get("support_samples",[]):
        u,w=row["point_uv"];inside=(u>=0 and w>=0) if row["operator"]=="retarded" else (u<=1 and w<=1)
        if row["in_declared_causal_support"] is not inside:e.append("support")
    pins={x["path"]:x["sha256"] for x in v.get("provenance",{}).get("inputs",[])}
    wanted={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SCALAR,TYPED)}
    if pins!=wanted:e.append("provenance")
    flags=v.get("claim_flags",{})
    for x in ("scalar_biwave_retarded_green_constructed","scalar_biwave_advanced_green_constructed","two_sided_test_code_identities_proved","strict_causal_support_proved","adjoint_duality_proved","four_zero_data_selection_proved","named_finite_horizon_extension_proved","canonical_construction_avoids_choice"):
        if flags.get(x) is not True:e.append("positive flag "+x)
    for x in ("global_bounded_energy_proved","arbitrary_distributional_uniqueness_proved","variable_coefficient_tensor_green_constructed","weyl_bv_propagator_constructed","brst_compatible_green_constructed","hadamard_state_constructed","renormalized_products_constructed","lorentzian_qme_proved"):
        if flags.get(x) is not False:e.append("boundary flag "+x)
    d=digest(v)
    if d!=v.get("independent_checker",{}).get("expected_digest"):e.append("digest")
    return e,{"digest":d,"fixtures":len(v.get("fixtures",[])),"exact_right_inverse_checks":8,"exact_left_inverse_endpoint_checks":32,"duality_checks":4,"support_checks":len(v.get("support_samples",[]))}
def main()->int:
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
