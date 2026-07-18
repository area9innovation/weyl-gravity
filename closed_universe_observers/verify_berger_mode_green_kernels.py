#!/usr/bin/env python3
import json,sympy as sp
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_mode_green_kernels import CERTIFICATE,DEPENDENCIES,SCHEMA,_sha256,wave_audit
def main()->int:
 v=json.loads(CERTIFICATE.read_text());s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v)
 for n,p in DEPENDENCIES.items():assert v["dependency_refs"][n]["sha256"]==_sha256(p)
 m0,m1=sp.symbols("m0_squared m1_squared",positive=True);expected=[]
 for j in range(3):
  for p,m in [(0,0),(1,0),(1,m0),(2,m1)]:
   a=wave_audit(j,p,m);assert not a["initial_value_defect_count"];assert not a["initial_derivative_defect_count"];assert not a["ode_coefficient_defect_count_through_tau9"];expected.append(a)
 assert v["audited_kernels"]==expected
 mutation=wave_audit(1,1,wrong_sign=True)["ode_coefficient_defect_count_through_tau9"];assert mutation
 assert v["mutation_results"]==[{"name":"flip_sine_kernel_recurrence_sign","detected":True,"defect_count":mutation}]
 print("BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
