#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_topos_weyl_bv_obstructions import check

RESULT=ROOT/"foundations/results/FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0.json"
SCHEMA=ROOT/"foundations/schema/foundational-topos-weyl-bv-obstruction-ledger-v0.schema.json"
REPORT=ROOT/"foundations/reports/topos-weyl-bv-obstruction-ledger.md"

def load(path:Path):return json.loads(path.read_text())
def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(*,result=None,ledgers=None,report=None):
    r=load(RESULT) if result is None else result
    ledger_data={x["path"]:load(ROOT/x["path"]) for x in r.get("provenance",{}).get("ledgers",[])} if ledgers is None else ledgers
    text=REPORT.read_text() if report is None else report
    load(SCHEMA);errors=[];checks=["artifacts parse"]
    if r.get("result_id")!="FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0" or r.get("lifecycle")!="LITERATURE_SCOPED" or r.get("dependency_tags")!=["LOCAL-ALGEBRAIC"]:errors.append("identity/lifecycle/tags")
    context=r.get("programme_context",{})
    if context.get("opportunity_realized")!="OP-TOPOS-WEYL-BV" or "glossary and obstruction ledger" not in context.get("prescribed_first_artifact",""):errors.append("opportunity scope")
    checks.append("scoped first artifact")
    checker_errors,summary=check(r);errors.extend("checker "+x for x in checker_errors)
    if summary.get("glossary_count")!=15 or summary.get("obstruction_count")!=12 or summary.get("topological_nodes")!=12:errors.append("checker counts")
    checks.append("glossary and acyclic obstruction graph")
    for pin in r.get("provenance",{}).get("ledgers",[]):
        path=ROOT/pin.get("path","")
        if not path.is_file() or sha(path)!=pin.get("sha256"):errors.append("ledger provenance")
    for pin in r.get("provenance",{}).get("local_inputs",[]):
        path=ROOT/pin.get("path","")
        if not path.is_file() or sha(path)!=pin.get("sha256"):errors.append("local provenance")
    for dep in r.get("source_dependencies",[]):
        ledger=ledger_data.get(dep.get("ledger"),{})
        entry=next((x for x in ledger.get("entries",[]) if x.get("id")==dep.get("source_id")),None)
        if entry is None or entry.get("artifact",{}).get("sha256")!=dep.get("pinned_pdf_sha256"):errors.append("source pin "+str(dep.get("source_id")))
    checks.append("literature and local provenance")
    flags=r.get("claim_flags",{})
    for key in ("glossary_complete_for_first_artifact","obstruction_dag_closed"):
        if flags.get(key) is not True:errors.append("positive flag "+key)
    for key in ("ambient_topos_selected","internal_weyl_bv_constructed","internal_green_operators_constructed","internal_krein_completion_constructed","internal_physical_state_selected","internal_renormalization_constructed","internal_qme_restored","external_equivalence_proved","lorentzian_claim"):
        if flags.get(key) is not False:errors.append("boundary flag "+key)
    if r.get("lowest_risk_candidate",{}).get("constructed_internally") is not False:errors.append("candidate promotion")
    checks.append("fail-closed construction flags")
    for token in ("FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0","LITERATURE_SCOPED","OP-TOPOS-WEYL-BV","O3-FINITE-BV-ALGEBRA","Heyting","locale","wavefront","QME","LORENTZIAN-CAUSAL","not yet a"):
        if token not in text:errors.append("report token "+token)
    checks.append("human report")
    return errors,checks

def main():
    errors,checks=verify();print("FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0: "+("PASS" if not errors else "FAIL"))
    for item in (checks if not errors else errors):print("  - "+item)
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
