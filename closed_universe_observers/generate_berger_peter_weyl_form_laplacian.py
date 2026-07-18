#!/usr/bin/env python3
"""Build exact Berger-S3 Peter-Weyl de Rham and form-Laplacian blocks."""
from __future__ import annotations
import argparse, hashlib, json
from itertools import combinations
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]; PACKAGE=ROOT/"closed_universe_observers"
CERTIFICATE=PACKAGE/"certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json"; SCHEMA=PACKAGE/"schema/berger-peter-weyl-form-laplacian-engine-v1.schema.json"; REPORT=PACKAGE/"reports/berger-peter-weyl-form-laplacian-engine.md"
DEPENDENCIES={"profiles":PACKAGE/"certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json","rods":PACKAGE/"certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json","unary":PACKAGE/"certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json"}
SOURCE_FILES={"producer":Path(__file__),"verifier":PACKAGE/"verify_berger_peter_weyl_form_laplacian.py","tests":PACKAGE/"tests/test_berger_peter_weyl_form_laplacian.py","schema":SCHEMA,"report":REPORT}
C=3*sp.sqrt(10)/20

def _sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def generators(two_j:int)->list[sp.Matrix]:
    n=two_j+1;j=sp.Rational(two_j,2);ms=[-j+k for k in range(n)];jp=sp.zeros(n)
    for k,m in enumerate(ms[:-1]):jp[k+1,k]=sp.sqrt((j-m)*(j+m+1))
    jm=jp.T
    return [-sp.I*(jp+jm)/2,(jm-jp)/2,-sp.I*sp.diag(*ms)/C]
def wedge(a:tuple[int,...],b:tuple[int,...])->tuple[tuple[int,...]|None,int]:
    if set(a)&set(b):return None,0
    seq=list(a)+list(b);inv=sum(seq[x]>seq[y] for x in range(len(seq)) for y in range(x+1,len(seq)))
    return tuple(sorted(seq)),(-1)**inv
DTHETA=[{(1,2):-1/C},{(0,2):1/C},{(0,1):-C}]
def d_basis(form:tuple[int,...])->dict[tuple[int,...],sp.Expr]:
    out={}
    for r,i in enumerate(form):
        for pair,coef in DTHETA[i].items():
            x,s1=wedge(form[:r],pair)
            if x is None:continue
            y,s2=wedge(x,form[r+1:])
            if y is not None:out[y]=sp.simplify(out.get(y,0)+(-1)**r*s1*s2*coef)
    return out
def d_matrix(two_j:int,p:int)->sp.Matrix:
    G=generators(two_j);n=two_j+1;src=list(combinations(range(3),p));dst=list(combinations(range(3),p+1));M=sp.zeros(len(dst)*n,len(src)*n)
    for si,S in enumerate(src):
        for a in range(3):
            T,sg=wedge((a,),S)
            if T is not None:
                di=dst.index(T);M[di*n:(di+1)*n,si*n:(si+1)*n]+=sg*G[a]
        for T,coef in d_basis(S).items():
            di=dst.index(T);M[di*n:(di+1)*n,si*n:(si+1)*n]+=coef*sp.eye(n)
    return sp.simplify(M)
def laplacian(two_j:int,p:int)->sp.Matrix:
    n=(two_j+1)*len(list(combinations(range(3),p)));L=sp.zeros(n)
    if p<3:
        d=d_matrix(two_j,p);L+=d.conjugate().T*d
    if p>0:
        d=d_matrix(two_j,p-1);L+=d*d.conjugate().T
    return sp.simplify(L)
def block_audit(two_j:int)->dict[str,Any]:
    ds=[d_matrix(two_j,p) for p in range(3)];Ls=[laplacian(two_j,p) for p in range(4)]
    defects=[sum(sp.simplify(x)!=0 for x in ds[p+1]*ds[p]) for p in range(2)]
    dual=[sorted([sp.sstr(x) for x,m in Ls[p].eigenvals().items() for _ in range(m)])==sorted([sp.sstr(x) for x,m in Ls[3-p].eigenvals().items() for _ in range(m)]) for p in range(4)]
    scalar=Ls[0].eigenvals()
    return {"two_j":two_j,"dimensions":[x.rows for x in Ls],"d_squared_defect_counts":defects,"laplacian_ranks":[x.rank() for x in Ls],"hodge_dual_spectra_match":all(dual),"scalar_eigenvalues":{sp.sstr(k):v for k,v in scalar.items()},"all_laplacians_hermitian":all(L==L.conjugate().T for L in Ls)}
def build()->dict[str,Any]:
    vals={k:json.loads(p.read_text()) for k,p in DEPENDENCIES.items()}
    req={"profiles":"OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED","rods":"GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED","unary":"MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED"}
    for n,f in req.items():
        if vals[n].get("flags",{}).get(f) is not True:raise AssertionError(f"dependency dropped: {n}.{f}")
    blocks=[block_audit(k) for k in range(5)]
    if any(any(b["d_squared_defect_counts"]) or not b["hodge_dual_spectra_match"] or not b["all_laplacians_hermitian"] for b in blocks):raise AssertionError("Peter-Weyl form block failed")
    if blocks[1]["scalar_eigenvalues"]!={"29/18":2}:raise AssertionError("rod eigenvalue cross-check failed")
    boundary="This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL spectral engine constructs the Berger-S3 de Rham matrices d_p and Hodge Laplacians Delta_p=d^dagger d+d d^dagger in any requested finite SU(2) Peter-Weyl block. It uses the certified squashing c=3 sqrt(10)/20, exact skew-Hermitian spin generators, and the orthonormal coframe equations dtheta1=-c^-1 theta2 theta3, dtheta2=c^-1 theta1 theta3, dtheta3=-c theta1 theta2. Blocks two_j=0..4 have zero d^2 defects, Hermitian Laplacians, Hodge-dual spectra, and the two_j=1 scalar eigenvalue 29/18 matching the global-rod certificate. This is an exact finite-block engine, not a validated expansion of the compact detector bumps: harmonic coefficients, quadrature bounds, spectral-tail bounds, Green images, and the absolute-g3 recoil coefficient remain open. It does not make a finite-parameter interacting or quantum claim."
    return {"schema":"closed-universe-berger-peter-weyl-form-laplacian-engine-v1","result_id":"BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE","setting_id":vals["profiles"]["setting_id"],"claim_status":"EXACT_FINITE_PETER_WEYL_FORM_LAPLACIAN_ENGINE_EXPORTED_PROFILE_EXPANSION_OPEN","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{k:{"path":str(p.relative_to(ROOT)),"result_id":vals[k]["result_id"],"sha256":_sha256(p)} for k,p in DEPENDENCIES.items()},"geometry":{"squashing":"3*sqrt(10)/20","frame":["e1=xi1","e2=xi2","e3=xi3/c"],"scalar_eigenvalue_formula":"j(j+1)+(c^-2-1)m^2=j(j+1)+31*m^2/9"},"audited_blocks":blocks,"flags":{"GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR":True,"EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED":True,"D_SQUARED_ZERO_AUDITED":True,"HODGE_DUAL_SPECTRA_AUDITED":True,"PROFILE_HARMONIC_COEFFICIENTS_EVALUATED":False,"VALIDATED_SPECTRAL_TAIL_BOUND_EXPORTED":False,"ADVANCED_GREEN_IMAGES_EVALUATED":False,"DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED":False,"QUANTUM_CLAIM":False},"next_gate":"COMPUTE_INTERVAL_ENCLOSED_PROFILE_COEFFICIENTS_AND_SUPERALGEBRAIC_TAIL_BOUNDS_THEN_APPLY_MODE_GREEN_KERNELS","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES.values()]}}
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--emit",action="store_true");ap.add_argument("--check",action="store_true");a=ap.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n"
    if a.emit:CERTIFICATE.write_text(r)
    if a.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale Peter-Weyl form certificate")
    print("BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
