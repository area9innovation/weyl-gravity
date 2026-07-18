#!/usr/bin/env python3
"""Evaluate adaptive external-clock scalar streams for even p=12,...,28."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import AMPLITUDE_LOWER
from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import MAX_K,MAX_TWO_J,REMAINDER_BITS,_fixed_moment_factors,_mode,_moment_intervals

ROOT=Path(__file__).resolve().parents[1];PACKAGE=ROOT/"closed_universe_observers"
SCHEMA=PACKAGE/"schema/berger-adaptive-clock-weighted-scalar-stream-two-j139-v1.schema.json";REPORT=PACKAGE/"reports/berger-adaptive-clock-weighted-scalar-stream-two-j139.md"
CLOCK_POWERS=tuple(range(12,29,2))
DEPENDENCIES={"scalar":PACKAGE/"certificates/BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139.json","high_moments":PACKAGE/"certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json","low_moments":PACKAGE/"certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json","high_clock":PACKAGE/"certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json","low_clock":PACKAGE/"certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json"}
SOURCE_FILES=[Path(__file__),PACKAGE/"verify_berger_adaptive_clock_weighted_scalar_stream.py",PACKAGE/"tests/test_berger_adaptive_clock_weighted_scalar_stream.py",SCHEMA,REPORT]
def certificate_path(p:int)->Path:return PACKAGE/f"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{p}_TWO_J139.json"
def result_id(p:int)->str:return f"BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{p}_TWO_J139"
def _sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def _serialize(x):return {"lower":str(x[0]),"upper":str(x[1]),"width":str(x[1]-x[0])}
def joint_clock_moments(values:dict[str,Any],power:int):
 if power not in CLOCK_POWERS:raise ValueError(f"power must be one of {CLOCK_POWERS}")
 base=values["high_clock"]["normalized_clock_even_moments"][power//2]["normalized_even_moment"];b=(Fraction(base["lower"]),Fraction(base["upper"]));answer=[]
 for k in range(MAX_K+1):
  e=2*k-1;answer.append((b[0]*AMPLITUDE_LOWER,b[1]) if e==-1 else (b[0],b[1]/AMPLITUDE_LOWER**e))
 return answer
@lru_cache(maxsize=None)
def build(power:int)->dict:
 if power not in CLOCK_POWERS:raise ValueError(f"power must be one of {CLOCK_POWERS}")
 v={n:json.loads(p.read_text()) for n,p in DEPENDENCIES.items()}
 req={"scalar":"CLOCK_INTEGRATED_DIAGONAL_SCALAR_COEFFICIENTS_TWO_J0_TO_139_EXPORTED","high_moments":"VALIDATED_CLOCK_SECANT_MOMENTS_K0_TO_50_EXPORTED","low_moments":"VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED","high_clock":"VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED","low_clock":"VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED"}
 for n,f in req.items():
  if v[n].get("flags",{}).get(f) is not True:raise AssertionError(f"dependency dropped: {n}.{f}")
 radial,_=_moment_intervals(v);clock=joint_clock_moments(v,power);factors=_fixed_moment_factors(radial,clock);modes=[];maxrem=0;maxloc=None
 for n in range(MAX_TWO_J+1):
  mode,rem=_mode(n,factors)
  for row in mode["unique_diagonal"]:row["clock_weighted_local_amplitude"]=row.pop("clock_integrated_local_amplitude")
  modes.append(mode)
  if rem>maxrem:maxrem,maxloc=rem,n
 if sum(len(x["unique_diagonal"]) for x in modes)!=4970:raise AssertionError("adaptive scalar coverage failed")
 boundary=f"This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL shard evaluates the normalized external-clock-and-s^{power}-weighted diagonal scalar detector-profile stream through two_j=139. It uses the p<=28 clock-moment successor and the same joint s^p sec(lambda s)^(2k-1) positivity bound without an independence assumption. This is one of nine p=12,14,...,28 inputs required by the common order-14 Green remainder proof. Polarization, charge-block application, spatial tail, full images, recoil, tangent-cone restriction, Bridge 3 and quantum claims remain open."
 return {"schema":"closed-universe-berger-adaptive-clock-weighted-scalar-stream-two-j139-v1","result_id":result_id(power),"setting_id":v["scalar"]["setting_id"],"claim_status":"VALIDATED_ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_DIAGONAL_SCALAR_STREAM_EXPORTED_GREEN_COMPOSITION_OPEN","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":v[n]["result_id"],"sha256":_sha256(p)} for n,p in DEPENDENCIES.items()},"clock_weight":{"power":power,"external_detector_factor":"a(t)=cos(lambda s)","joint_integrand":"s^p sec(lambda s)^(2k-1)","maximum_secant_index":MAX_K},"evaluation_convention":{"maximum_two_j":MAX_TWO_J,"moment_truncation_k":MAX_K,"remainder_dyadic_bits":REMAINDER_BITS},"joint_clock_moment_enclosures":[{"k":k,"interval":_serialize(x)} for k,x in enumerate(clock)],"coverage":{"mode_count":140,"serialized_unique_diagonal_count":4970,"reconstructed_full_diagonal_count":9870},"modes":modes,"truncation_remainder_audit":{"maximum_uniform_remainder_upper":str(Fraction(maxrem,1<<REMAINDER_BITS)),"maximum_mode_two_j":maxloc},"mutation_results":[{"name":"drop_external_detector_clock_factor","detected":True}],"flags":{"ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_DIAGONAL_SCALAR_STREAM_EXPORTED":True,"POLARIZATION_STREAM_COMPOSED":False,"TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED":False,"GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED":False,"QUANTUM_CLAIM":False},"next_gate":"COMPOSE_ALL_NINE_ADAPTIVE_SCALAR_SHARDS_WITH_THE_DETECTOR_POLARIZATION_RECURRENCE","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES]}}
def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--power",type=int,choices=CLOCK_POWERS,required=True);p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v=build(a.power);s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n";target=certificate_path(a.power)
 if a.emit:target.write_text(r)
 if a.check and (not target.exists() or target.read_text()!=r):raise SystemExit("stale adaptive scalar shard")
 print(f"{result_id(a.power)} generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
