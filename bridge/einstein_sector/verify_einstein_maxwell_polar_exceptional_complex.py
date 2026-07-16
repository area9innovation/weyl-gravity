"""Independent verifier for exceptional polar complexes."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
CERTIFICATE=ROOT/"bridge/certificates/einstein_maxwell_polar_exceptional_complex.json"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_certificate(path:Path=CERTIFICATE)->None:
    p=json.loads(path.read_text())
    assert p["result_id"]=="COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX"
    assert sha(ROOT/p["schema_path"])==p["schema_sha256"]
    for relative,digest in p["provenance"]["inputs"].items():assert sha(ROOT/relative)==digest
    w,k=sp.symbols("omega k",real=True)
    m0=sp.Matrix([[0,0,0,k**2],[0,0,0,-k*w],[0,0,0,w**2],[k**2/2,k*w,w**2/2,(w**2-k**2+2)/2]])
    g0=sp.Matrix([[-2*sp.I*w,0],[sp.I*k,-sp.I*w],[0,2*sp.I*k],[0,0]])
    assert m0*g0==sp.zeros(4,2)
    assert sp.factor(m0[[0,3],[3,0]].det())==k**4/2
    assert sp.factor(m0[[2,3],[3,2]].det())==w**4/2
    assert p["ell0_complex"]["generalized_zero_frequency_equations"]==["ddot K=0","ddot C=2K","dot E=0"]
    m1=sp.Matrix([[0,0,1,k**2+1,-2],[0,1,0,-k*w,0],[1,0,0,w**2-1,2],[0,sp.I*k/2,sp.I*w/2,sp.I*w/2,-sp.I*w],[sp.I*k/2,sp.I*w/2,0,-sp.I*k/2,sp.I*k],[(k**2+1)/2,k*w,(w**2-1)/2,(w**2-k**2+2)/2,-2],[sp.Rational(1,2),0,-sp.Rational(1,2),1,w**2-k**2-2]])
    gauge=sp.Matrix([2*w**2,-2*k*w,2*k**2,-2,-1]);assert (m1*gauge).applyfunc(sp.simplify)==sp.zeros(7,1)
    q=m1[:,[0,1,2,4]];v=sp.Matrix([-2,0,2,1])
    assert (q*v).applyfunc(lambda z:sp.factor(z.subs(w**2,k**2+4)))==sp.zeros(7,1)
    assert p["ell1_complex"]["quotient_characteristic"]=="-k**2 + omega**2 - 4"
    c=p["classification"];assert c["all_polar_ell_linear_complex"] and not c["covariant_symplectic_matching"]
if __name__=="__main__":verify_certificate()
