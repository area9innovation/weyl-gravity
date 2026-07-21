#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SOURCE=ROOT/"d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json"; OUTPUT=ROOT/"residual_atlas/two-phase-counterflow-charge-clock-complementarity-fragment-v1.json"; GENERATOR=Path(__file__).resolve()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cl(s,t): return {"status":s,"statement":t}
def build():
 s=json.loads(SOURCE.read_text()); ev=[{"path":str(SOURCE.relative_to(ROOT)),"result_id":s["result_id"],"sha256":sha(SOURCE)}]
 def entry(i,sector,symp):
  return {"id":i,"scope":{"theory":"selected two-phase counterflow action","background":"stationary Berger R x S3, a=1, c_squared=9/40","boundaries":"none; closed S3 Cauchy slices","charge_sector":sector,"carrier":"global relative phase-charge sector of 70-row parent","degree":0,"parity":"scalar zero mode","ell":0,"m":0,"k":"NOT_APPLICABLE","omega":"zero-frequency linearized root; background Omega=3/4"},"descriptions":{"causal":"CERTIFIED","symplectic":symp,"nonlinear":"NO_CERTIFIED_MAP","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},"mode_data":{"dispersion":cl("OBSTRUCTED" if "unrestricted" in sector else "NO_CERTIFIED_MAP","lambda^2 with a size-two Jordan block on unrestricted branch; fixed branch removes the pair."),"lee_wald":cl(symp,"Darboux rank two unrestricted; rank zero after fixed-charge quotient."),"taub_maps":cl("NO_CERTIFIED_MAP","Not computed after first exact health failure."),"resonance":cl("NO_CERTIFIED_MAP","No nonlinear promotion."),"second_order":{"equation":"L_barPhi v = -(1/2) D^2 E_barPhi[u,u]","bounded_or_finite_quasiperiodic":cl("OBSTRUCTED" if "unrestricted" in sector else "NO_CERTIFIED_MAP","Unrestricted charge perturbations produce secular phase drift; fixed branch has no clock."),"smooth_secular":cl("CERTIFIED" if "unrestricted" in sector else "NO_CERTIFIED_MAP","delta psi=t delta Q/I on unrestricted branch."),"causal_retarded":cl("NO_CERTIFIED_MAP","Unary causality is not stability or nonlinear response.")}},"evidence":ev,"claim_boundary":"Fixed and unrestricted charge sectors are distinct. No observer or quantum mode is inferred."}
 return {"schema":"pure-weyl-residual-atlas-fragment-v1","schema_version":"1.0.0","team":"classical","generated_by":str(GENERATOR.relative_to(ROOT)),"generated_by_sha256":sha(GENERATOR),"status_vocabulary":["CERTIFIED","OBSTRUCTED","OPEN","NOT_APPLICABLE","NO_CERTIFIED_MAP"],"description_axes":["causal","symplectic","nonlinear","observational","quantum"],"entries":[entry("classical.counterflow.fixed_charge_clock","derived fixed-Q_rel quotient","OBSTRUCTED"),entry("classical.counterflow.unrestricted_charge_clock","unrestricted variable-Q_rel physical branch","CERTIFIED")],"verification_commands":["python3 d_quotient_classical/compensator/two_phase_counterflow_charge_clock_complementarity.py --check","python3 d_quotient_classical/compensator/verify_two_phase_counterflow_charge_clock_complementarity.py","python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-charge-clock-complementarity-fragment-v1.json"]}
def main():
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");x=a.parse_args()
 if x.check:
  if json.loads(OUTPUT.read_text())!=build(): raise AssertionError("atlas drift")
  print("CHARGE_CLOCK_COMPLEMENTARITY_ATLAS: PASS")
 else: OUTPUT.write_text(json.dumps(build(),indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
