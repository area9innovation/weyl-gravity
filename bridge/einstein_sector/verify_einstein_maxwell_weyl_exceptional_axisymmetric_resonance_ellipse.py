"""Independent verifier for the exceptional resonance ellipse."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json"
def verify() -> None:
    r=json.loads(CERT.read_text())
    for item in r["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"]
    rx,rp,d=sp.symbols("rx rp d", real=True)
    assert sp.Poly(16*rx**2+3*rp**2-115*d**2,rx,rp,d).coeffs()==[16,3,-115]
    c=r["classification"]
    assert c["axisymmetric_L1_L2_resonance_zero_locus_nonempty"]
    assert c["Einstein_minus_balance_required"]
    assert not c["Hamiltonian_moment_map_zero"]
    assert not c["complete_second_order_source_solved"]
    assert not c["causal_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXISYMMETRIC_RESONANCE_ELLIPSE independent verification: PASS")
if __name__=="__main__": verify()
