"""Independent verifier for the d-enlarged twist/ell2 cone."""
import hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
CERTIFICATE=ROOT/"bridge/certificates/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.schema.json"

def main()->None:
 v=json.loads(CERTIFICATE.read_text()); s=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(v)
 assert v["schema_sha256"]==hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
 p=v["provenance"]; assert p["generator_sha256"]==hashlib.sha256((ROOT/p["generator_path"]).read_bytes()).hexdigest()
 inputs={}
 for name,r in p["inputs"].items():
  path=ROOT/r["path"]; assert r["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest(); inputs[name]=json.loads(path.read_text())
 assert inputs["axial_minus"]["bounded_zero_locus"]["nonzero_wave_branch"]=="z!=0 implies a=b=d=0"
 assert inputs["polar_minus"]["bounded_zero_locus"]["nonzero_wave_branch"]=="z!=0 implies a=b=d=0"
 assert "any nonzero Einstein-minus vector forces a=b=d=0" in inputs["global_ell2"]["equivariant_promotion"]["all_m_consequence"]
 assert "- omega_minus^2*A_minus" in inputs["moment_cone"]["density_cone_theorem"]["common_zero_equations"]["H"]
 assert v["complete_bounded_zero_locus"]["union_is_necessary_and_sufficient"] is True
 assert v["classification"]["nonzero_wave_forces_d_zero"] is True
 assert v["classification"]["static_d_branch_retained"] is True
 assert v["classification"]["radion_or_electric_tangent_classified"] is False
 print("EINSTEIN_MAXWELL_WEYL_D_TWIST_ELL2_COMPLETE_BOUNDED_CONE independent verification: PASS")
if __name__=="__main__": main()
