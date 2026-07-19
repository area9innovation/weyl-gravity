#!/usr/bin/env python3
"""Certify complex matrix/vector interval Volterra composition."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import ComplexRationalInterval
from closed_universe_observers.berger_recoil_matrix_interval import evaluate_matrix_green_time_convolution_interval

ROOT=Path(__file__).resolve().parents[1]; PACKAGE=ROOT/"closed_universe_observers"
CERTIFICATE=PACKAGE/"certificates/BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION.json"
SCHEMA=PACKAGE/"schema/berger-recoil-matrix-interval-convolution-v1.schema.json"
REPORT=PACKAGE/"reports/berger-recoil-matrix-interval-convolution.md"
DEPENDENCIES={"scalar":PACKAGE/"certificates/BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION.json","kernels":PACKAGE/"certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json","switches":PACKAGE/"certificates/BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER.json","forms":PACKAGE/"certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json"}
SOURCE_FILES=[Path(__file__),PACKAGE/"berger_recoil_matrix_interval.py",PACKAGE/"verify_berger_recoil_matrix_interval_convolution.py",PACKAGE/"tests/test_berger_recoil_matrix_interval_convolution.py",SCHEMA,REPORT]
def _sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def _p(x): return ComplexRationalInterval.point(x)
def _diag(a,b): return [[_p(a),_p(0)],[_p(0),_p(b)]]

def _fixture():
    return evaluate_matrix_green_time_convolution_interval(source_coefficients=[[_p(1),_p(2)]],source_remainder_upper=Fraction(0),kernel_stages=[{"label":"diagonal","coefficient_matrices":[_diag(1,2)]},{"label":"identity","coefficient_matrices":[_diag(1,1)]}],slab_length=Fraction(1),orientation="retarded")

def build():
    values={n:json.loads(p.read_text()) for n,p in DEPENDENCIES.items()}
    required={"scalar":"FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED","kernels":"FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED","switches":"NORMALIZED_SWITCH_AND_TIME_DERIVATIVE_INTERVAL_PROVIDER_EXPORTED","forms":"EXACT_SPACETIME_D_BLOCKS_EXPORTED"}
    for n,flag in required.items():
        if values[n].get("flags",{}).get(flag) is not True: raise AssertionError(f"dependency dropped: {n}.{flag}")
    fixture=_fixture()
    if fixture["polynomial_coefficients"][2][0]["real"]["lower"]!="1/2" or fixture["polynomial_coefficients"][2][1]["real"]["lower"]!="2": raise AssertionError("matrix beta fixture drifted")
    boundary="This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports dimension-checked complex matrix/vector polynomial Volterra composition in retarded and advanced causal coordinates, a direct sparse-to-dense adapter for the certified finite sine-kernel enclosures, pointwise real cell-interval multiplication, exact beta coefficients and induced-infinity-norm uniform remainder propagation. It is the finite execution layer for the certified Berger kernel and switch intervals, but does not yet bind detector polynomials, spacetime d/delta matrices or emitter Cauchy coefficients. No I_abc, recoil record, cone, Bridge 3 or quantum claim is evaluated."
    return {"schema":"closed-universe-berger-recoil-matrix-interval-convolution-v1","result_id":"BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION","setting_id":values["forms"]["setting_id"],"claim_status":"COMPLEX_MATRIX_VECTOR_VOLTERRA_INTERVAL_ENGINE_CERTIFIED_PHYSICAL_FORM_BINDING_OPEN","atlas_status":"CERTIFIED","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":values[n]["result_id"],"sha256":_sha(p)} for n,p in DEPENDENCIES.items()},"mode_scope":{"theory":"classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters","background":"compact positive Berger clock at fixed coupling","boundaries":"one rational finite causal slab; no spatial boundary","charge_sector":"fixed-coupling Berger sector","carrier":"complex interval vector polynomials and square matrix Green-kernel polynomials","degree":"dimension-parametric form block","parity":"retarded or advanced orientation","ell":"one supplied finite mode block","m":"all supplied vector rows","k":"one supplied passive column","omega":"finite polynomial plus uniform remainder"},"fixtures":{"two_stage_sha256":hashlib.sha256(json.dumps(fixture,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"output_x2":["1/2","2"]},"flags":{"COMPLEX_MATRIX_VECTOR_INTERVAL_CONVOLUTION_EXPORTED":True,"FINITE_MODE_KERNEL_ENCLOSURE_ADAPTER_EXPORTED":True,"REAL_CELL_INTERVAL_MULTIPLICATION_EXPORTED":True,"DIMENSION_MISMATCH_FAILS_CLOSED":True,"PHYSICAL_BERGER_FORM_CHAIN_BOUND":False,"EMITTER_CAUCHY_COEFFICIENTS_SERIALIZED":False,"FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED":False,"QUANTUM_CLAIM":False},"next_gate":"BIND_FINITE_DETECTOR_POLYNOMIALS_AND_SPACETIME_FORM_MATRICES","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha(p)} for p in SOURCE_FILES]}}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit",action="store_true"); parser.add_argument("--check",action="store_true"); args=parser.parse_args(); value=build(); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered=json.dumps(value,indent=2,sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale matrix interval convolution certificate")
    print("BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION generation: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
