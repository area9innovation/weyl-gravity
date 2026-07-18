#!/usr/bin/env python3
"""Apply detector polarization to adaptive clock powers p=12,...,28."""
from __future__ import annotations
import argparse,hashlib,json,struct
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any,Iterator
from jsonschema import Draft202012Validator
import sympy as sp
from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import _fast_complex_interval,_supported_pairs,_width,_overlap
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CZERO,_cadd,_clock_even_moments,_gradient,_mul,_weighted_coefficient,radial_moment_intervals,representation_matrix
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import _component_rules,axial_scalar_recurrence

ROOT=Path(__file__).resolve().parents[1];PACKAGE=ROOT/"closed_universe_observers"
CERTIFICATE=PACKAGE/"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_POLARIZATION_STREAM_P12_TO_P28_TWO_J138.json"
SCHEMA=PACKAGE/"schema/berger-adaptive-clock-weighted-polarization-stream-p12-p28-v1.schema.json";REPORT=PACKAGE/"reports/berger-adaptive-clock-weighted-polarization-stream-p12-p28.md"
POWERS=tuple(range(12,29,2));MAX_TWO_J=138
DEPENDENCIES={"recurrence":PACKAGE/"certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json","moments":PACKAGE/"certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",**{f"s{p}":PACKAGE/f"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{p}_TWO_J139.json" for p in POWERS}}
SOURCE_FILES=[Path(__file__),PACKAGE/"verify_berger_adaptive_clock_weighted_polarization_stream.py",PACKAGE/"tests/test_berger_adaptive_clock_weighted_polarization_stream.py",SCHEMA,REPORT]
def _sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def _scalar(streams,p,tj,index):
 index=min(index,tj-index);x=streams[p][tj]["unique_diagonal"][index]["clock_weighted_local_amplitude"];return ((Fraction(x["lower"]),Fraction(x["upper"])),(Fraction(0),Fraction(0)))
def polarization_intervals(streams:dict[int,Any],detector:str,component:int,tj:int,row:int,column:int):
 coordinate,prefactor=_component_rules()[detector][component];terms=axial_scalar_recurrence(tj,row,column,coordinate);coeffs=[(t,_fast_complex_interval(prefactor*sp.sympify(t["coefficient"]))) for t in terms];answers={p:CZERO for p in POWERS}
 for term,coef in coeffs:
  for p in POWERS:
   scalar=_scalar(streams,p,term["next_two_j"],term["diagonal_index"])[0];answers[p]=_cadd(answers[p],(_mul(coef[0],scalar),_mul(coef[1],scalar)))
 return answers,len(terms)
def _encint(v:int)->bytes:
 b=abs(v).to_bytes(max(1,(abs(v).bit_length()+7)//8),"big");return bytes((v<0,))+len(b).to_bytes(2,"big")+b
def _encfrac(v:Fraction)->bytes:return _encint(v.numerator)+_encint(v.denominator)
def _canonical(detector,component,row,column,values):
 out=bytearray(struct.pack(">BBBB",int(detector[1]),component+1,row,column))
 for p in POWERS:
  out.append(p)
  for axis in values[p]:out.extend(_encfrac(axis[0]));out.extend(_encfrac(axis[1]))
 return bytes(out)
def _direct_p12_audit(streams,moments):
 radial=radial_moment_intervals(moments);clock=_clock_even_moments(moments);checked=defects=0
 for detector in ("D0","D1"):
  gradients=_gradient(detector)
  for tj in range(5):
   matrix=representation_matrix(tj).conjugate().T
   for component,gradient in enumerate(gradients):
    for row in range(tj+1):
     for column in range(tj+1):
      recurrence,_=polarization_intervals(streams,detector,component,tj,row,column);direct=_weighted_coefficient(matrix[row,column]*gradient,radial,clock,12);checked+=1;defects+=not _overlap(recurrence[12],direct)
 return {"clock_power":12,"audited_two_j_maximum":4,"interval_comparison_count":checked,"nonoverlap_defect_count":defects}
@lru_cache(maxsize=1)
def build()->dict:
 v={n:json.loads(p.read_text()) for n,p in DEPENDENCIES.items()}
 for p in POWERS:
  if v[f"s{p}"]["flags"].get("ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_DIAGONAL_SCALAR_STREAM_EXPORTED") is not True:raise AssertionError(f"adaptive S{p} dropped")
 streams={p:v[f"s{p}"]["modes"] for p in POWERS};full=hashlib.sha256();modes=[];total_entries=total_terms=0;widths={p:Fraction(0) for p in POWERS}
 for tj in range(MAX_TWO_J+1):
  d=tj+1;mh=hashlib.sha256();ec=tc=0;mw={p:Fraction(0) for p in POWERS}
  for detector,rules in _component_rules().items():
   for component,(coordinate,_) in enumerate(rules):
    for row,column in _supported_pairs(d,coordinate):
     values,terms=polarization_intervals(streams,detector,component,tj,row,column)
     if not terms:continue
     encoded=_canonical(detector,component,row,column,values);mh.update(encoded);full.update(encoded);ec+=1;tc+=terms
     for p in POWERS:mw[p]=max(mw[p],_width(values[p]));widths[p]=max(widths[p],mw[p])
  total_entries+=ec;total_terms+=tc;modes.append({"two_j":tj,"dimension":d,"detector_component_entry_count":ec,"scalar_term_application_count":tc,"maximum_interval_width_by_clock_power":{str(p):str(mw[p]) for p in POWERS},"canonical_stream_sha256":mh.hexdigest()})
 if (total_entries,total_terms)!=(86736,231018):raise AssertionError("adaptive polarization coverage failed")
 audit=_direct_p12_audit(streams,v["moments"])
 if audit["nonoverlap_defect_count"]:raise AssertionError("adaptive recurrence lost direct p12 coefficients")
 boundary="This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate applies the exact detector-prefactored polarization recurrence to all nine adaptive external-clock scalar streams p=12,14,...,28 through form two_j=138. It covers 86,736 detector-component entries, 231,018 scalar-term applications and 780,624 clock-power intervals with canonical hashes. All direct p=12 form comparisons through two_j=4 overlap. Together with the published p=0,...,10 stream this closes polarization inputs for common series order 14. Charge-block polynomial application and its remainder, the spatial tail, full images, recoil, tangent-cone restriction, Bridge 3 and quantum claims remain open."
 return {"schema":"closed-universe-berger-adaptive-clock-weighted-polarization-stream-p12-p28-v1","result_id":"BERGER_ADAPTIVE_CLOCK_WEIGHTED_POLARIZATION_STREAM_P12_TO_P28_TWO_J138","setting_id":v["recurrence"]["setting_id"],"claim_status":"VALIDATED_ADAPTIVE_DETECTOR_POLARIZATION_STREAM_P12_TO_P28_EXPORTED_ORDER14_GREEN_APPLICATION_OPEN","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":v[n]["result_id"],"sha256":_sha256(p)} for n,p in DEPENDENCIES.items()},"stream_convention":{"clock_powers":list(POWERS),"maximum_form_two_j":MAX_TWO_J,"scalar_neighbor_maximum_two_j":139,"detectors":["D0","D1"]},"coverage":{"detector_component_entry_count":total_entries,"detector_component_scalar_term_application_count":total_terms,"clock_power_interval_count":total_entries*len(POWERS)},"maximum_interval_width_by_clock_power":{str(p):str(widths[p]) for p in POWERS},"canonical_full_stream_sha256":full.hexdigest(),"mode_summaries":modes,"direct_p12_compatibility_audit":audit,"flags":{"ADAPTIVE_DETECTOR_PREFACTORED_POLARIZATION_STREAM_P12_TO_P28_EXPORTED":True,"COMMON_ORDER14_POLARIZATION_INPUTS_P0_TO_P28_COMPLETE":True,"TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED":False,"GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED":False,"FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED":False,"QUANTUM_CLAIM":False},"next_gate":"APPLY_COMMON_ORDER14_TEMPORAL_GREEN_POLYNOMIAL_IN_EXACT_CHARGE_BLOCKS_THROUGH_TWO_J138","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES]}}
def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n"
 if a.emit:CERTIFICATE.write_text(r)
 if a.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale adaptive polarization stream")
 print("BERGER_ADAPTIVE_CLOCK_WEIGHTED_POLARIZATION_STREAM generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
