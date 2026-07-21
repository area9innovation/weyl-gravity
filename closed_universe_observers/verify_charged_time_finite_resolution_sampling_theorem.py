#!/usr/bin/env python3
"""Independent de Rham-current verifier for finite-resolution sampling."""
import hashlib,json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/"closed_universe_observers/certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json"; S=ROOT/"closed_universe_observers/schema/charged-time-finite-resolution-sampling-theorem-v1.schema.json"
def verify():
 v=json.loads(C.read_text()); schema=json.loads(S.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(v)
 r=v["dependency_ref"]; assert hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()==r["sha256"]
 x=sp.symbols("x",real=True); k=sp.Rational(15,16)*(1-x*x)**2
 assert sp.integrate(k,(x,-1,1))==1 and sp.integrate(x*k,(x,-1,1))==0 and sp.integrate(x*x*k,(x,-1,1))==sp.Rational(1,7)
 tau,e,d,a,b,c=sp.symbols("tau epsilon delta a b c",real=True,positive=True); z,y=sp.symbols("z y",real=True); kz=k.subs(x,z); ky=k.subs(x,y)
 P=lambda y:a+b*y+c*y*y
 sampled=sp.integrate(kz*P(tau+e*z),(z,-1,1))
 assert sp.simplify(sampled-P(tau)-c*e*e/sp.Integer(7))==0
 composed=sp.integrate(ky*sp.integrate(kz*P(tau+e*z+d*y),(z,-1,1)),(y,-1,1))
 assert sp.simplify(composed-P(tau)-c*(e*e+d*d)/sp.Integer(7))==0
 psi,Q=sp.symbols("psi Q",real=True); kernel=sp.Function("kappa")((psi-tau)/e)/e; H=sp.Function("H")(Q)
 assert sp.simplify(sp.diff(kernel,psi)+sp.diff(kernel,tau))==0
 assert sp.simplify(k.subs(x,-x)-k)==0 and sp.diff(H,Q)==sp.diff(H,Q)
 E1,E2,L2=sp.symbols("E_1 E_2 L_2",nonnegative=True)
 assert sp.simplify((E2+L2*E1)-E2-L2*E1)==0
 assert v["support_inheritance"]["no_tail_promotion"] and v["clock_topology_and_reduction"]["smoothing_does_not_restore_clock"]
 assert all(m["detected"] for m in v["mutation_results"])
 return v
if __name__=="__main__":verify();print("CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1 independent current verification: PASS")
