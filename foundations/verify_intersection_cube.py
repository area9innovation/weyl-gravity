#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_intersection_cube import check

RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
SCHEMA=ROOT/"foundations/schema/foundational-intersection-cube-v0.schema.json"
REPORT=ROOT/"foundations/reports/completion-matrix.md"
LEDGERS=(ROOT/"foundations/literature-ledger.json",ROOT/"foundations/literature-supplement-known-attempts-v1.json",ROOT/"foundations/literature-expansion-v2.json")

def load(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(*,result=None,report=None):
    r=load(RESULT) if result is None else result;text=REPORT.read_text() if report is None else report;load(SCHEMA);errors=[];checks=["artifacts parse"]
    if r.get("result_id")!="FOUNDATIONAL_INTERSECTION_CUBE_V0" or r.get("lifecycle")!="LITERATURE_SCOPED" or r.get("dependency_tags")!=["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"]:errors.append("identity/lifecycle/tags")
    checker_errors,summary=check(r);errors.extend("checker "+x for x in checker_errors)
    if summary.get("declared_cells")!=162 or summary.get("total_cells")!=216 or summary.get("default_not_mapped")!=54 or summary.get("status_counts")!={"LITERATURE_RESULT":55,"LOCAL_RESULT":43,"PIECES_ONLY":47,"PRIORITY_GAP":17}:errors.append("cube counts")
    checks.append("6 x 6 x 6 coordinates and counts")
    for pin in r.get("provenance",{}).get("inputs",[]):
        path=ROOT/pin.get("path","")
        if not path.is_file() or sha(path)!=pin.get("sha256"):errors.append("provenance "+str(pin.get("path")))
    literature_ids=set()
    for ledger in LEDGERS:literature_ids|={x["id"] for x in load(ledger)["entries"]}
    result_ids={load(path).get("result_id") for path in (ROOT/"foundations/results").glob("*.json")}
    known=literature_ids|result_ids
    for cube_cell in r.get("cells",[]):
        if not set(cube_cell.get("evidence",[]))<=known:errors.append("unknown evidence identifier")
    checks.append("provenance and evidence references")
    by_coordinate={(x.get("foundation"),x.get("carrier"),x.get("obligation")):x for x in r.get("cells",[])}
    promoted=(
        ("CLASSICAL_STANDARD","KREIN_INDEFINITE","STATES_PROBABILITY"),
        ("WEAK_CHOICE_ZF","KREIN_INDEFINITE","STATES_PROBABILITY"),
        ("CLASSICAL_STANDARD","ALGEBRAIC_CSTAR","STATES_PROBABILITY"),
    )
    for coordinate in promoted:
        cell=by_coordinate.get(coordinate,{})
        if cell.get("status")!="LOCAL_RESULT" or "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1" not in cell.get("evidence",[]):errors.append("state promotion "+"/".join(coordinate))
    checks.append("three state-cell promotions")
    dynamics_promoted=(
        ("CLASSICAL_STANDARD","KREIN_INDEFINITE","DYNAMICS_PROPAGATION"),
        ("CLASSICAL_STANDARD","ALGEBRAIC_CSTAR","DYNAMICS_PROPAGATION"),
        ("WEAK_CHOICE_ZF","KREIN_INDEFINITE","DYNAMICS_PROPAGATION"),
        ("WEAK_CHOICE_ZF","ALGEBRAIC_CSTAR","DYNAMICS_PROPAGATION"),
    )
    for coordinate in dynamics_promoted:
        cell=by_coordinate.get(coordinate,{})
        if cell.get("status")!="LOCAL_RESULT" or "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1" not in cell.get("evidence",[]):errors.append("dynamics promotion "+"/".join(coordinate))
    checks.append("four dynamics-cell promotions")
    closure_promoted=(
        ("CLASSICAL_STANDARD","SMOOTH_DISTRIBUTIONAL","GAUGE_BV_COHOMOLOGY"),
        ("CLASSICAL_STANDARD","SMOOTH_DISTRIBUTIONAL","INTERACTION_RENORMALIZATION_QME"),
        ("FINITE_DISCRETE","FINITE_EXACT","DYNAMICS_PROPAGATION"),
    )
    for coordinate in closure_promoted:
        cell=by_coordinate.get(coordinate,{})
        if cell.get("status")!="LOCAL_RESULT" or "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1" not in cell.get("evidence",[]):errors.append("closure promotion "+"/".join(coordinate))
    checks.append("three bounded closure-audit promotions")
    flags=r.get("claim_flags",{})
    for key in ("three_axis_product_defined","one_hundred_sixty_two_cells_deliberately_assessed","seventy_five_percent_assessed","three_low_hanging_state_cells_promoted","four_low_hanging_dynamics_cells_filled","three_stale_open_cells_closed_by_scope_audit","twenty_two_assessed_open_cells_remain"):
        if flags.get(key) is not True:errors.append("positive flag "+key)
    for key in ("all_216_cells_claimed_assessed","cell_status_means_complete_solution","literature_complete","new_physical_theorem","new_lorentzian_claim"):
        if flags.get(key) is not False:errors.append("boundary flag "+key)
    checks.append("navigation-not-completeness boundary")
    for token in ("Simplified three-dimensional overview","6 mathematical regimes × 6 carriers × 6 physical obligations","**162 of 216 cells (75.0%)**","Local result","Literature result","Pieces only","Priority gap","Not mapped","The six cube slices","The five missing faces to investigate thoroughly","constructive/internal gauge-QFT face","nonstandard carriers × physical probability"):
        if token not in text:errors.append("report token "+token)
    checks.append("generated cube report")
    return errors,checks

def main():
    errors,checks=verify();print("FOUNDATIONAL_INTERSECTION_CUBE_V0: "+("PASS" if not errors else "FAIL"))
    for item in (checks if not errors else errors):print("  - "+item)
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
