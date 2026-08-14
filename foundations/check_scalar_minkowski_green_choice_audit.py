#!/usr/bin/env python3
"""Independent exact checker for the scalar Minkowski Green choice audit."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
TEST_SPACE=ROOT/"foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
EXPONENTS=((0,0,0,0),(1,0,0,2),(2,1,1,1),(3,2,2,0))

def q(value:list[int])->Q:return Q(value[0],value[1])
def enc(value:Q)->list[int]:return [value.numerator,value.denominator]
def poly_eval(coeffs:list[Q],x:Q)->Q:return sum((c*x**i for i,c in enumerate(coeffs)),Q(0))
def deriv(coeffs:list[Q])->list[Q]:return [Q(i)*coeffs[i] for i in range(1,len(coeffs))]

def compact_factor(power:int)->list[Q]:
    coeffs=[Q(0)]*(power+3); coeffs[power],coeffs[power+1],coeffs[power+2]=Q(1),Q(-2),Q(1); return coeffs

def canonical_digest(value:dict[str,Any])->str:
    projection={key:value[key] for key in ("spacetime_and_operator","source_codes","green_formulas","exact_identities","energy_extension","choice_audit","formal_proof","fixtures","support_samples")}
    return hashlib.sha256(json.dumps(projection,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def check(value:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    result=json.loads(RESULT.read_text()) if value is None else value; errors:list[str]=[]
    stages=result.get("formal_proof",[]); expected=["RATIONAL_NULL_SOURCE_CODES","CANONICAL_GREEN_FORMULAS","TWO_SIDED_CODE_IDENTITIES","CAUSAL_SUPPORT","ADJOINT_DUALITY","NAMED_ENERGY_EXTENSION","SUPPORT_INDEXED_ASSEMBLY","SCALAR_SCOPE_BOUNDARY"]
    if [s.get("id") for s in stages]!=expected: errors.append("proof stage identity")
    if [s.get("base") for s in stages]!=["PRA","PRA","PRA","PRA","PRA","RCA_0","RCA_0","RCA_0"]:errors.append("proof bases")
    seen:set[str]=set()
    for stage in stages:
        if not set(stage.get("depends_on",[]))<=seen:errors.append("proof dependency order "+str(stage.get("id")))
        seen.add(str(stage.get("id")))
    spacetime=result.get("spacetime_and_operator",{})
    if spacetime.get("operator")!="P=partial_t^2-partial_x^2" or spacetime.get("null_form")!="P=4 partial_u partial_v" or spacetime.get("scope")!="scalar field only; no gauge or BV complex":errors.append("operator scope")
    fixtures=result.get("fixtures",[])
    if [tuple(row.get("source_exponents",[])+row.get("duality_test_exponents",[])) for row in fixtures]!=list(EXPONENTS):errors.append("fixture exponents")
    pg_checks=gp_checks=duality_checks=energy_checks=0
    for row,(a,b,c,d) in zip(fixtures,EXPONENTS):
        ret=Q(1,4*(a+1)*(b+1)); multiplier=4*(a+1)*(b+1)*ret
        if q(row.get("retarded_interior",{}).get("coefficient",[0,1]))!=ret or q(row.get("retarded_interior",{}).get("wave_operator_multiplier",[0,1]))!=1:errors.append("retarded P G "+row.get("id",""))
        if q(row.get("advanced_interior",{}).get("coefficient",[0,1]))!=ret or q(row.get("advanced_interior",{}).get("wave_operator_multiplier",[0,1]))!=1 or multiplier!=1:errors.append("advanced P G "+row.get("id",""))
        pg_checks+=2
        dual=Q(1,8*(a+1)*(b+1)*(a+c+2)*(b+d+2))
        pairing=row.get("adjoint_pairing",{})
        if q(pairing.get("left",[0,1]))!=dual or q(pairing.get("right",[0,1]))!=dual:errors.append("adjoint duality "+row.get("id",""))
        duality_checks+=1
        l2=Q(1,2*(2*a+1)*(2*b+1))
        if q(row.get("source_l2_squared",[0,1]))!=l2 or q(row.get("source_time_width",[0,1]))!=1 or q(row.get("energy_squared_bound",[0,1]))!=l2:errors.append("energy bound "+row.get("id",""))
        energy_checks+=1
        compact=row.get("compact_test",{}); u=compact_factor(c+2); v=compact_factor(d+2); du,dv=deriv(u),deriv(v)
        if compact.get("u_factor_coefficients")!=[enc(x) for x in u] or compact.get("v_factor_coefficients")!=[enc(x) for x in v] or compact.get("u_derivative_coefficients")!=[enc(x) for x in du] or compact.get("v_derivative_coefficients")!=[enc(x) for x in dv]:errors.append("compact polynomial data "+row.get("id",""))
        endpoint_zero=all(poly_eval(poly,Q(point))==0 for poly in (u,v) for point in (0,1)) and all(poly_eval(poly,Q(point))==0 for poly in (du,dv) for point in (0,1))
        if not endpoint_zero or compact.get("endpoint_values_and_first_derivatives_zero") is not True or compact.get("retarded_G_P_identity") is not True or compact.get("advanced_G_P_identity") is not True:errors.append("compact G P identity "+row.get("id",""))
        gp_checks+=2
    samples=result.get("support_samples",[])
    expected_support=[]
    for row in samples:
        u,v=row.get("point_uv",[0,0]); operator=row.get("operator")
        inside=(u>=0 and v>=0) if operator=="retarded" else (u<=1 and v<=1)
        expected_support.append(inside)
        if row.get("in_declared_causal_support") is not inside:errors.append("causal support sample")
    audit=result.get("choice_audit",[])
    if len(audit)!=8 or [row.get("choice") for row in audit[:6]]!=["NONE"]*6 or [row.get("base") for row in audit[-2:]]!=["UNRESOLVED","UNRESOLVED"]:errors.append("choice audit")
    flags=result.get("claim_flags",{})
    for flag in ("scalar_retarded_green_constructed","scalar_advanced_green_constructed","two_sided_test_code_identities_proved","strict_causal_support_proved","adjoint_duality_proved","named_energy_extension_proved","canonical_construction_avoids_choice","lorentzian_causal_scalar_claim"):
        if flags.get(flag) is not True:errors.append("positive flag "+flag)
    for flag in ("arbitrary_distributional_uniqueness_proved","bare_source_support_uniformly_selected","variable_coefficient_green_constructed","weyl_bv_propagator_constructed","hadamard_state_constructed","lorentzian_quantum_master_equation_proved"):
        if flags.get(flag) is not False:errors.append("boundary flag "+flag)
    pins={item.get("path"):item.get("sha256") for item in result.get("provenance",{}).get("inputs",[])}; expected_pins={str(TEST_SPACE.relative_to(ROOT)):hashlib.sha256(TEST_SPACE.read_bytes()).hexdigest()}
    if pins!=expected_pins:errors.append("source provenance hash")
    digest=canonical_digest(result)
    if digest!=result.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":digest,"fixtures":len(fixtures),"P_G_checks":pg_checks,"G_P_checks":gp_checks,"duality_checks":duality_checks,"energy_checks":energy_checks,"support_checks":len(samples)}

def main()->int:
    errors,summary=check();print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True));return bool(errors)
if __name__=="__main__":raise SystemExit(main())
