#!/usr/bin/env python3
"""Extend validated normalized clock-bump moments through even power 28."""

from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_validated_flat_bump_moments import integral_enclosures, normalized_moments

ROOT=Path(__file__).resolve().parents[1]; PACKAGE=ROOT/"closed_universe_observers"
CERTIFICATE=PACKAGE/"certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json"
SCHEMA=PACKAGE/"schema/berger-high-clock-power-moment-rail-p28-v1.schema.json"
REPORT=PACKAGE/"reports/berger-high-clock-power-moment-rail-p28.md"
DEPENDENCY=PACKAGE/"certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json"
SOURCE_FILES=[Path(__file__),PACKAGE/"verify_berger_high_clock_power_moment_rail.py",PACKAGE/"tests/test_berger_high_clock_power_moment_rail.py",SCHEMA,REPORT]
MAX_K=14

def _sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def build()->dict:
    low=json.loads(DEPENDENCY.read_text())
    if low["flags"].get("VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED") is not True:raise AssertionError("low moment rail dropped")
    rows=normalized_moments(integral_enclosures(max_k=MAX_K),1,max_k=MAX_K)
    compatibility=[]
    for expected,actual in zip(low["normalized_moments"]["clock_core_dimension_1"],rows[:7]):
        old=expected["normalized_even_moment"]; new=actual["normalized_even_moment"]
        overlap=not(Fraction(old["upper"])<Fraction(new["lower"]) or Fraction(new["upper"])<Fraction(old["lower"]))
        compatibility.append({"k":expected["k"],"overlap":overlap})
    if not all(row["overlap"] for row in compatibility):raise AssertionError("low clock moments lost")
    if any(Fraction(row["normalized_even_moment"]["width"])>=Fraction(1,1000) for row in rows):raise AssertionError("high clock moment too wide")
    boundary="This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL successor interval-encloses normalized even moments of the fixed one-dimensional flat clock bump through p=28 on the same 32768-cell dyadic Darboux rail. The p<=12 rows overlap the foundational moment certificate. It supplies the additional temporal inputs required by the common order-14 high-mode Green remainder proof; it does not evaluate external-clock/secant joint moments, scalar or polarization streams, charge-block Green images, the spatial tail, recoil, Bridge 3 or quantum claims."
    return {"schema":"closed-universe-berger-high-clock-power-moment-rail-p28-v1","result_id":"BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28","setting_id":low["setting_id"],"claim_status":"VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED_ADAPTIVE_STREAMS_OPEN","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{"low_moments":{"path":str(DEPENDENCY.relative_to(ROOT)),"result_id":low["result_id"],"sha256":_sha256(DEPENDENCY)}},"rail":{"maximum_even_power":28,"maximum_k":MAX_K,"subdivisions":32768,"method":"exact-unimodality dyadic Darboux enclosure with directed transcendental endpoints"},"normalized_clock_even_moments":rows,"low_order_compatibility_audit":compatibility,"flags":{"VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED":True,"ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_SCALAR_STREAMS_P12_TO_P28_EXPORTED":False,"TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED":False,"QUANTUM_CLAIM":False},"next_gate":"EVALUATE_EXTERNAL_CLOCK_WEIGHTED_SCALAR_STREAMS_FOR_EVEN_P12_TO_P28","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(path.relative_to(ROOT)),"sha256":_sha256(path)} for path in SOURCE_FILES]}}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n"
    if a.emit:CERTIFICATE.write_text(r)
    if a.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale high clock-power moment rail")
    print("BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28 generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
