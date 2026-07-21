#!/usr/bin/env python3
"""Independent exact replay of charge-clock complementarity."""
import hashlib, json
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json"
PAYLOAD=ROOT/"d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json"

def main():
    c,p=json.loads(CERT.read_text()),json.loads(PAYLOAD.read_text())
    for row in c["imports"].values():
        if hashlib.sha256((ROOT/row["path"]).read_bytes()).hexdigest()!=row["sha256"]: raise AssertionError("import drift")
    omega=sp.Rational(3,4); I=sp.Rational(12,5)*sp.pi**2*sp.sqrt(10)
    A=sp.Matrix([[0,1/I],[0,0]])
    if A.rank()!=1 or A**2!=sp.zeros(2) or A.nullspace()[0]!=sp.Matrix([1,0]): raise AssertionError("Jordan replay")
    cases=[(sp.Matrix([[1]]),sp.Matrix([omega]),True),(sp.Matrix([[1,0]]),sp.Matrix([omega,0]),True),(sp.Matrix([[1,0]]),sp.Matrix([0,omega]),False)]
    for C,v,expected in cases:
        if (C.col_join(v.T).rank()==C.rank())!=expected: raise AssertionError("complementarity rank replay")
    if p["unrestricted_global_clock_health"]["bounded_or_finite_quasiperiodic_stability"] or p["unrestricted_global_clock_health"]["real_exponential_growing_roots"]!=0: raise AssertionError("health boundary")
    if not p["branch_dichotomy"]["no_averaging"]: raise AssertionError("branches conflated")
    print("INDEPENDENT CHARGE-CLOCK COMPLEMENTARITY VERIFIER: PASS")
if __name__=="__main__": main()
