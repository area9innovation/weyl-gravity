"""Independent reconstruction of the compact-Cauchy symbol gate."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
import jsonschema
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
CERTIFICATE=ROOT/"bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json"
ATLAS=ROOT/"residual_atlas/einstein-weyl-compact-cauchy-constraint-fredholm-gate-fragment-v1.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-constraint-fredholm-gate-v1.schema.json"
EXPECTED_INPUTS={
"bridge/certificates/EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1.json":"4768cfaef309b27300bac7ac4fc3c8eee9d850d97c49dd5527494b3569918b78",
"bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json":"935a3c264858c4f425025f2f1adf50886739bb84cdc86331120058c9ce7bd545",
"bridge/certificates/einstein_maxwell_product_incidence.json":"6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
"bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json":"7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8",
"bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json":"442d4bbd0de7b02215f13b4dc3b8f5becf1cdc99f57bba7c7b58586405c48821",
"bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json":"d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd"}
class IndependentCompactCauchyVerificationError(RuntimeError): pass
def _require(c:bool,m:str)->None:
    if not c: raise IndependentCompactCauchyVerificationError(m)
def _sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def _load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def _matrix()->tuple[list[str],sp.Matrix,sp.Matrix]:
    s=["11","22","33","12","13","23"]
    v=[f"h{x}" for x in s]+[f"K{x}" for x in s]+[f"pi{x}" for x in s]+[f"P{x}" for x in s]+["a1","a2","a3","E1","E2","E3"]
    rows=[{"h11":-1,"P11":1},{"pi11":-2,"K11":2,"K22":1,"K33":1},{"pi12":-2,"K12":4},{"pi13":-2,"K13":4},{"P11":1,"P22":1,"P33":1,"h11":-2,"h22":1,"h33":1},{"pi11":2,"pi22":2,"pi33":2,"K11":-2,"K22":1,"K33":1},{"E1":1},{"h11":sp.Rational(2,3),"h22":sp.Rational(-1,3),"h33":sp.Rational(-1,3)},{"h12":1},{"h13":1},{"K11":sp.Rational(2,3),"K22":sp.Rational(-1,3),"K33":sp.Rational(-1,3)},{"h11":1,"h22":1,"h33":1},{"K11":1,"K22":1,"K33":1},{"a1":1}]
    M=sp.zeros(14,30)
    for i,row in enumerate(rows):
        for n,x in row.items():M[i,v.index(n)]=x
    return v,sp.Matrix(M[:7,:]),sp.Matrix(M)
def verify_certificate(certificate_path:Path=CERTIFICATE,atlas_path:Path=ATLAS)->None:
    p=_load(certificate_path);jsonschema.Draft202012Validator(_load(SCHEMA)).validate(p)
    _require(p["schema_sha256"]==_sha(SCHEMA),"schema drift")
    imports={x["path"]:x["sha256"] for x in p["provenance"]["imported_artifacts"]};_require(imports==EXPECTED_INPUTS,"input ledger")
    for path,d in EXPECTED_INPUTS.items():_require(_sha(ROOT/path)==d,f"input drift {path}")
    v,raw,M=_matrix();recorded=sp.Matrix([[sp.sympify(x) for x in r] for r in p["douglis_nirenberg_symbol"]["combined_symbol"]])
    _require(p["douglis_nirenberg_symbol"]["variables"]==v and recorded==M,"independent matrix mismatch")
    _require(raw.rank()==7 and M.rank()==14 and M.cols-M.rank()==16,"rank/nullity")
    cross=sp.zeros(30,1);cross[v.index("P23")]=1
    plus=sp.zeros(30,1);plus[v.index("P22")]=1;plus[v.index("P33")]=-1
    _require(M*cross==sp.zeros(14,1) and M*plus==sp.zeros(14,1),"TT witness")
    cols=["P11","pi11","pi12","pi13","P22","pi22","E1"]
    _require(raw[:,[v.index(x) for x in cols]].det()==-16,"raw minor")
    _require(sp.diag(sp.Rational(4,3),1,1,sp.Rational(-2,3),6,3,1).det()==-16,"gauge orbit")
    mut=M.col_join(sp.zeros(1,30));mut[14,v.index("P23")]=1;_require(mut.rank()==15 and mut*cross!=sp.zeros(15,1),"mutation")
    for k in ("two_sided_ellipticity","fredholm_constraint_plus_gauge_operator","adjoint_kernel_exactly_five","sobolev_momentum_map_normal_form","finite_EP_theorem_promoted_by_density","global_evolution_or_stability_claim","lorentzian_causal_claim","quantum_claim"):_require(p["classification"][k] is False,f"promotion {k}")
    e=_load(atlas_path)["entries"][0];_require(e["evidence"][0]["sha256"]==_sha(certificate_path),"atlas hash")
    _require(e["descriptions"]=={"causal":"NO_CERTIFIED_MAP","symplectic":"NO_CERTIFIED_MAP","nonlinear":"OBSTRUCTED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},"atlas statuses")
def main()->int:verify_certificate();print("independent compact-Cauchy constraint/Fredholm gate verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
