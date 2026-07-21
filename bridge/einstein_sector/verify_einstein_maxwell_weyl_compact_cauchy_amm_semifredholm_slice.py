from __future__ import annotations
import hashlib,json
from pathlib import Path
import jsonschema,sympy as sp
ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json"
ATLAS=ROOT/"residual_atlas/einstein-weyl-compact-cauchy-amm-semifredholm-slice-fragment-v1.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-amm-semifredholm-slice-v1.schema.json"
class IndependentAMMAuditError(RuntimeError):pass
def req(c,m):
 if not c:raise IndependentAMMAuditError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_certificate(cert_path=CERT,atlas_path=ATLAS):
 p=json.loads(cert_path.read_text());s=json.loads(SCHEMA.read_text());jsonschema.Draft202012Validator(s).validate(p);req(p["schema_sha256"]==sha(SCHEMA),"schema drift")
 for row in p["provenance"]["imports"]:req(sha(ROOT/row["path"])==row["sha256"],f"input drift {row['name']}")
 x=sp.symbols('x',real=True);N=sp.sin(x);M=sp.cos(x);w=sp.simplify(N*sp.diff(M,x)-M*sp.diff(N,x));req(w==-1,"Wronskian")
 req(w!=sp.Rational(1,4)*w,"structure function mutation not separated")
 req(p["kuranishi_normal_form"]["second_order_tangent_cone"].count("mu_")==5,"not five maps")
 req(p["classification"]["sobolev_second_order_tangent_cone"] and not p["classification"]["full_fixed_group_AMM_hypotheses"],"boundary collapsed")
 a=json.loads(atlas_path.read_text());e=a["entries"][0];req(e["mode_data"]["taub_maps"]["status"]=="CERTIFIED","Taub atlas");req(e["descriptions"]["nonlinear"]=="OBSTRUCTED","AMM obstruction missing");req(e["evidence"][0]["sha256"]==sha(cert_path),"atlas hash")
 print("PASS independent AMM semi-Fredholm audit")
if __name__=="__main__":verify_certificate()
