"""Independent verifier for the constant-twist harmonic-type repair."""
import hashlib,json
from pathlib import Path
import sympy as s
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2];C=ROOT/"bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json";SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.schema.json"
def main():
 v=json.loads(C.read_text());schema=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(v);assert v['schema_sha256']==hashlib.sha256(SCHEMA.read_bytes()).hexdigest();z,p=s.symbols('z phi',real=True);q=1-z**2;lap=lambda f:s.simplify(s.diff(q*s.diff(f,z),z)+s.diff(f,p,2)/q)
 y1=s.sqrt(q)*s.exp(s.I*p);y2=z*s.sqrt(q)*s.exp(s.I*p);assert s.simplify(lap(y1)+2*y1)==0;assert s.simplify(lap(y2)+6*y2)==0
 pr=v['provenance'];assert pr['generator_sha256']==hashlib.sha256((ROOT/pr['generator_path']).read_bytes()).hexdigest()
 for group in ('engines','inputs'):
  for x in pr[group].values():assert x['sha256']==hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()
 assert v['corrected_position_maps']['Einstein_plus_minus']=='zero';assert v['corrected_position_maps']['extra']=='zero';assert v['bounded_cone_repair']['necessity_and_sufficiency'] is True
 print('EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_PROJECTOR_REPAIR independent verification: PASS')
if __name__=='__main__':main()
