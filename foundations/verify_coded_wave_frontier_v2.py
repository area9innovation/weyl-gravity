#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.build_coded_wave_frontier_v2 import generated
from foundations.check_coded_wave_frontier_v2 import check
RESULT=ROOT/"foundations/results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json";LEDGER=ROOT/"foundations/literature-coded-wave-frontier-v2.json";REPORT=ROOT/"foundations/reports/coded-wave-frontier-v2.md";RS=ROOT/"foundations/schema/foundational-coded-wave-frontier-v2.schema.json";LS=ROOT/"foundations/schema/foundational-coded-wave-literature-v2.schema.json"
def verify(*,result=None,ledger=None,report=None):
    r=json.loads(RESULT.read_text()) if result is None else result;l=json.loads(LEDGER.read_text()) if ledger is None else ledger;text=REPORT.read_text() if report is None else report;errors=["result schema "+e.message for e in Draft202012Validator(json.loads(RS.read_text())).iter_errors(r)]+["ledger schema "+e.message for e in Draft202012Validator(json.loads(LS.read_text())).iter_errors(l)];ce,s=check(r,l);errors += ["checker "+x for x in ce];el,er,ep=generated()
    if (json.dumps(l,indent=2,ensure_ascii=False)+"\n").encode()!=el:errors.append("deterministic ledger drift")
    if (json.dumps(r,indent=2,ensure_ascii=False)+"\n").encode()!=er:errors.append("deterministic result drift")
    if text.encode()!=ep:errors.append("deterministic report drift")
    for pin in r.get("provenance",{}).get("inputs",[]):
        p=ROOT/pin.get("path","")
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=pin.get("sha256"):errors.append("provenance "+str(pin.get("path")))
    flags=r.get("claim_flags",{})
    for k in ("weakest_base_proved","reverse_lower_bound_proved","bishop_hyperbolic_theorem_found","zf_choice_free_pde_found","computable_causal_support_proved","new_lorentzian_claim"):
        if flags.get(k) is not False:errors.append("boundary flag "+k)
    return errors,["two schemas","independent source/framework audit","deterministic artifacts","input hashes","claim boundaries"]
def main():
    e,c=verify();print("FOUNDATIONAL_CODED_WAVE_FRONTIER_V2: "+("PASS" if not e else "FAIL"));[print("  - "+x) for x in (c if not e else e)];return bool(e)
if __name__=="__main__":raise SystemExit(main())
