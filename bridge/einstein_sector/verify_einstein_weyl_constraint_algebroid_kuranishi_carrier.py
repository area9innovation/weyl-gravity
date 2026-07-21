"""Independent two-jet and balanced-projection verifier."""
import hashlib,json
from pathlib import Path
import jsonschema
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein-weyl-constraint-algebroid-kuranishi-carrier-v1.schema.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_payload(p,files=True):
 jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(p)
 if files:
  assert p["schema_sha256"]==sha(SCHEMA)
  assert p["provenance"]["generator_sha256"]==sha(ROOT/p["provenance"]["generator_path"])
  for x in p["provenance"]["inputs"].values():
   q=ROOT/x["path"];assert sha(q)==x["sha256"];assert json.loads(q.read_text())["result_id"]==x["result_id"]
 e,q=sp.symbols("epsilon q")
 inv=1-e*q+e**2*q**2
 assert all(sp.expand((1+e*q)*inv-1).coeff(e,j)==0 for j in range(3))
 assert str(sp.expand(-inv))==p["constraint_algebroid_two_jet"]["fixture"]["shift_jet"]
 te=sp.Rational(48,5)*(-6+5*sp.sqrt(3));tx=-sp.Rational(832,45)*sp.Rational(27,52)*(-6+5*sp.sqrt(3))
 assert sp.simplify(te+tx)==0 and te!=0 and tx!=0
 w=p["functorial_pullback_obstruction"]["exact_balanced_witness"]
 assert sp.simplify(sp.sympify(w["Einstein_projected_mu_H"],locals={"sqrt":sp.sqrt})-te)==0
 assert sp.simplify(sp.sympify(w["extra_projected_mu_H"],locals={"sqrt":sp.sqrt})-tx)==0
 assert p["classification"]["linear_cofiber_projects_derived_zero_fibre"] is False
 assert p["classification"]["two_jet_koszul_nilpotency"] is True
 assert p["functorial_pullback_obstruction"]["conclusion"].startswith("the cofiber projection does not")
def main():verify_payload(json.loads(CERT.read_text()))
if __name__=="__main__":main()
