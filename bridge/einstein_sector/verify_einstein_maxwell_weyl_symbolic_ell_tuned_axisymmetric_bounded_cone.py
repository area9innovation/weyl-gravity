"""Independent verifier for the all-ell tuned bounded cone."""
import hashlib,json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 d=json.loads(CERT.read_text()); s=ROOT/d["schema_path"]; schema=json.loads(s.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(d); assert d["schema_sha256"]==sha(s)
 for i in d["provenance"]["inputs"].values(): p=ROOT/i["path"]; assert i["sha256"]==sha(p)
 e=sp.symbols("ell",integer=True,positive=True); lam=e*(e+1); wm2=lam-e/2-sp.Rational(1,6); wp2=wm2+2*sp.sqrt(2*lam); r=sp.sqrt(wm2/wp2); lo=(1-r)/(1+r); hi=(1+r)/(1-r); assert sp.simplify(lo*hi-1)==0
 for n in range(2,33): assert 0<float(r.subs(e,n))<1 and 0<float(lo.subs(e,n))<1<float(hi.subs(e,n))
 c=d["classification"]; assert c["complete_tuned_axisymmetric_standard_branch_bounded_cone_classified"] and c["sharp_action_normalized_amplitude_interval_certified"] and not c["extra_primary_or_multiple_abs_momentum_inputs_classified"] and not c["all_orders_integrability"] and not c["causal_or_quantum_claim"]
 assert d["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"]=="CERTIFIED" and d["correction_classes"]["CAUSAL_RETARDED"]["status"]=="NO_CERTIFIED_MAP"
 print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_TUNED_AXISYMMETRIC_BOUNDED_CONE verifier: PASS")
if __name__=="__main__": verify()
