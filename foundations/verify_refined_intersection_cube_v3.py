#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from foundations.check_refined_intersection_cube_v3 import check
from foundations.refine_intersection_cube_v3 import generated
RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json"; REPORT=ROOT/"foundations/reports/refined-intersection-cube-v3.md"; SCHEMA=ROOT/"foundations/schema/foundational-intersection-cube-v3.schema.json"
def verify(*,result=None,report=None):
    value=json.loads(RESULT.read_text()) if result is None else result; text=REPORT.read_text() if report is None else report; errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    ce,summary=check(value); errors += ["checker "+e for e in ce]; er,ep=generated()
    if (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode()!=er: errors.append("deterministic result drift")
    if text.encode()!=ep: errors.append("deterministic report drift")
    for pin in value.get("provenance",{}).get("inputs",[]):
        p=ROOT/pin.get("path","")
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=pin.get("sha256"): errors.append("provenance "+str(pin.get("path")))
    flags=value.get("claim_flags",{})
    if flags.get("atlas_actions_applied") is not True or flags.get("weakest_base_proved") is not False or flags.get("new_lorentzian_claim") is not False: errors.append("claim boundary")
    return errors,["schema","independent v2-preservation audit","deterministic artifacts","input hashes","claim boundary"]
def main():
    errors,checks=verify(); print("FOUNDATIONAL_INTERSECTION_CUBE_V3: "+("PASS" if not errors else "FAIL")); [print("  - "+x) for x in (checks if not errors else errors)]; return bool(errors)
if __name__=="__main__": raise SystemExit(main())
