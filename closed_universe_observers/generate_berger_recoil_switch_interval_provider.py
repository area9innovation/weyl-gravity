#!/usr/bin/env python3
"""Certify finite rational cell enclosures of the exact emitter switches."""

from __future__ import annotations

import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path
from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_switch_intervals import emitter_switch_interval

ROOT=Path(__file__).resolve().parents[1]; PACKAGE=ROOT/"closed_universe_observers"
CERTIFICATE=PACKAGE/"certificates/BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER.json"
SCHEMA=PACKAGE/"schema/berger-recoil-switch-interval-provider-v1.schema.json"
REPORT=PACKAGE/"reports/berger-recoil-switch-interval-provider.md"
DEPENDENCIES={"switches":PACKAGE/"certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json","moments":PACKAGE/"certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json","kernels":PACKAGE/"certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json"}
SOURCE_FILES=[Path(__file__),PACKAGE/"berger_recoil_switch_intervals.py",PACKAGE/"verify_berger_recoil_switch_interval_provider.py",PACKAGE/"tests/test_berger_recoil_switch_interval_provider.py",SCHEMA,REPORT]
def _sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    values={name:json.loads(path.read_text()) for name,path in DEPENDENCIES.items()}
    if not values["switches"]["flags"]["EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED"] or not values["moments"]["flags"]["VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED"]: raise AssertionError("switch dependency dropped")
    center=emitter_switch_interval(values["switches"],values["moments"],switch_id="h_0",physical_time_interval=RationalInterval.point(Fraction(1,6)))
    whole=emitter_switch_interval(values["switches"],values["moments"],switch_id="h_1",physical_time_interval=RationalInterval(Fraction(5,16),Fraction(7,16)))
    outside=emitter_switch_interval(values["switches"],values["moments"],switch_id="h_0",physical_time_interval=RationalInterval(Fraction(1,4),Fraction(1,3)))
    if center["physical_time_derivative"]!={"lower":"0","upper":"0","width":"0"} or not outside["structural_zero"]: raise AssertionError("switch fixture drifted")
    boundary="This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports normalized h_0,h_1 value and physical-time-derivative rational intervals on arbitrary rational cells. It imports the directed flat-bump normalization integral, exact supports and clock/physical radii; monotonicity of B and the exact derivative critical equation 1-3s^4=0 control the cell hulls. Centers have zero derivative and disjoint cells are structural zeros. This binds the switch factor only: it does not compose a Green kernel, serialize emitter Cauchy coefficients, contract form blocks, evaluate I_abc, recoil, the cone, Bridge 3 or quantum data."
    return {"schema":"closed-universe-berger-recoil-switch-interval-provider-v1","result_id":"BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER","setting_id":values["switches"]["setting_id"],"claim_status":"NORMALIZED_SWITCH_CELL_INTERVALS_CERTIFIED_GREEN_BINDING_OPEN","atlas_status":"CERTIFIED","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":values[n]["result_id"],"sha256":_sha(p)} for n,p in DEPENDENCIES.items()},"mode_scope":{"theory":"classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters","background":"compact positive Berger clock at fixed coupling","boundaries":"rational physical-time cells on compact h0/h1 supports; no spatial boundary","charge_sector":"fixed-coupling Berger sector","carrier":"normalized switch value and physical-time derivative interval hulls","degree":"scalar clock switch multiplying massive two-forms","parity":"h0/h1 even about their respective centers; derivative odd","ell":"NOT_APPLICABLE temporal provider","m":"NOT_APPLICABLE","k":"NOT_APPLICABLE","omega":"cellwise physical-time interval"},"fixtures":{"h0_center":center,"h1_full_support":whole,"outside_structural_zero":outside},"flags":{"NORMALIZED_SWITCH_AND_TIME_DERIVATIVE_INTERVAL_PROVIDER_EXPORTED":True,"SWITCH_KERNEL_CONVOLUTION_BOUND":False,"EMITTER_CAUCHY_COEFFICIENTS_SERIALIZED":False,"FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED":False,"QUANTUM_CLAIM":False},"next_gate":"BIND_SWITCH_INTERVALS_WITH_FINITE_KERNELS_DETECTOR_PROFILES_AND_TYPED_FORM_BLOCKS","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha(p)} for p in SOURCE_FILES]}}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit",action="store_true"); parser.add_argument("--check",action="store_true"); args=parser.parse_args(); value=build(); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered=json.dumps(value,indent=2,sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale switch interval provider")
    print("BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER generation: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
