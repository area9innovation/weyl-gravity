#!/usr/bin/env python3
"""Fix a quantitative inverse rod chart and detector radius."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
import sympy as sp
ROOT=Path(__file__).resolve().parents[1];PACKAGE=ROOT/"closed_universe_observers";CERTIFICATE=PACKAGE/"certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json";SCHEMA=PACKAGE/"schema/berger-quantitative-detector-rod-chart-v1.schema.json";REPORT=PACKAGE/"reports/berger-quantitative-detector-rod-chart.md"
DEPENDENCIES={"global_rods":PACKAGE/"certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json","profiles":PACKAGE/"certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json"};SOURCE_FILES={"producer":Path(__file__),"verifier":PACKAGE/"verify_berger_quantitative_detector_chart.py","tests":PACKAGE/"tests/test_berger_quantitative_detector_chart.py","schema":SCHEMA,"report":REPORT}
C=3*sp.sqrt(10)/20;OMEGA=sp.sqrt(sp.Rational(29,18));EPS=sp.Rational(1,128)
def _sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def chart_audit(*,double_radius:bool=False,delete_amplitude:bool=False)->dict[str,Any]:
 e=2*EPS if double_radius else EPS;x=sp.sqrt(58)/288;amp=sp.Integer(1) if delete_amplitude else 1-x**2/2
 max_y2=sp.simplify(e**2/(4*amp**2*C**2));y1,y2,y3,a,c1,c2,c3=sp.symbols("y1 y2 y3 a c1 c2 c3",real=True);R=sp.Matrix([c1+2*C*a*y3,c2+2*a*y1,c3+2*a*y2]);inv=sp.Matrix([(R[1]-c2)/(2*a),(R[2]-c3)/(2*a),(R[0]-c1)/(2*C*a)]);defects=[sp.simplify(inv[i]-[y1,y2,y3][i]) for i in range(3)]
 return {"fixed_rod_radius":sp.sstr(e),"window_phase_bound":"sqrt(58)/288<1/32","cosine_lower_bound":sp.sstr(amp),"inverse_map":["y1=(R2-c2)/(2 a(t))","y2=(R3-c3)/(2 a(t))","y3=(R1-c1)/(2 c a(t))","y0=+sqrt(1-y1^2-y2^2-y3^2)"],"forward_inverse_defect_count":sum(v!=0 for v in defects),"rod_jacobian":"8*c*a(t)^3","maximum_y_norm_squared_bound":sp.sstr(max_y2),"positive_branch_margin_y_norm_squared_below_1_over_10000":bool(max_y2<sp.Rational(1,10000)),"unique_connected_component":"the component containing the detector worldline, equivalently y0>0","clock_windows":["[11/48,13/48]","[23/48,25/48]"]}
def build()->dict[str,Any]:
 v={k:json.loads(p.read_text()) for k,p in DEPENDENCIES.items()};a=chart_audit();mut=chart_audit(double_radius=True)
 if v["global_rods"]["flags"]["GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"] is not True or v["profiles"]["flags"]["EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED"] is not True:raise AssertionError("dependency dropped")
 if a["forward_inverse_defect_count"] or not a["positive_branch_margin_y_norm_squared_below_1_over_10000"]:raise AssertionError("chart audit failed")
 if mut["positive_branch_margin_y_norm_squared_below_1_over_10000"]:raise AssertionError("radius mutation escaped")
 boundary="This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate uses the explicit global detector rods to quantify their inverse on both detector windows. The rod oscillation obeys a(t)>=1-29/82944, and fixing epsilon_0=epsilon_1=1/128 gives |y|^2<1/10000 in the detector-centered SU(2) coordinates. The Jacobian 8 c a(t)^3 is nonzero and the connected component containing the detector worldline is the unique y0>0 branch. Thus the formerly parameterized radial profile family now has a fully fixed admissible member. This does not evaluate harmonic coefficients, Green images, recoil, interacting backreaction, or any quantum claim."
 return {"schema":"closed-universe-berger-quantitative-detector-rod-chart-v1","result_id":"BERGER_QUANTITATIVE_DETECTOR_ROD_CHART","setting_id":v["profiles"]["setting_id"],"claim_status":"EXACT_NUMERICAL_DETECTOR_RADIUS_AND_ROD_CHART_INVERSE_CERTIFIED","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{k:{"path":str(p.relative_to(ROOT)),"result_id":v[k]["result_id"],"sha256":_sha256(p)} for k,p in DEPENDENCIES.items()},"chart_audit":a,"selected_profiles":{"epsilon_0":"1/128","epsilon_1":"1/128","radial_profile":"rho_a=B3((R-c_a)/(1/128))/((1/128)^3 C_B3)"},"mutation_results":[{"name":"double_radius_to_1_over_64","detected":True,"audit":mut}],"flags":{"QUANTITATIVE_LOCAL_ROD_CHART_INVERSE_CERTIFIED":True,"EXACT_DETECTOR_RADII_FIXED":True,"DETECTOR_SUPPORT_ON_UNIQUE_POSITIVE_SU2_BRANCH":True,"PROFILE_HARMONIC_COEFFICIENTS_EVALUATED":False,"ADVANCED_GREEN_IMAGES_EVALUATED":False,"DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED":False,"QUANTUM_CLAIM":False},"next_gate":"INTERVAL_INTEGRATE_THE_FIXED_RADIUS_1_OVER_128_BUMPS_AGAINST_PETER_WEYL_MODES","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES.values()]}}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--emit",action="store_true");ap.add_argument("--check",action="store_true");z=ap.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n";CERTIFICATE.write_text(r) if z.emit else None
 if z.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale quantitative chart certificate")
 print("BERGER_QUANTITATIVE_DETECTOR_ROD_CHART generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
