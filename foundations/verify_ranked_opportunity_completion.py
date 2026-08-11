#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_ranked_opportunity_completion import check
from foundations.verify_free_bv_energy2_weak_base import verify as verify_bv
from foundations.verify_krein_explicit_j_zf import verify as verify_krein
from foundations.verify_bt_separable_state_chain import verify as verify_cstar
from foundations.verify_explicit_energy_spectral_fragment import verify as verify_spectral
from foundations.verify_hardy_continuity_kn import verify as verify_hardy
from foundations.verify_typed_biwave_green_dependencies import verify as verify_green
from foundations.verify_finite_field_finite_mode import verify as verify_finite
from foundations.verify_topos_weyl_bv_obstructions import verify as verify_topos

RESULT=ROOT/"foundations/results/FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1.json"
SCHEMA=ROOT/"foundations/schema/foundational-ranked-opportunity-completion-matrix-v1.schema.json"
REPORT=ROOT/"foundations/reports/ranked-opportunity-completion-matrix.md"
CHILD_VERIFIERS={"FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1":verify_bv,"FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1":verify_krein,"FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1":verify_cstar,"FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1":verify_spectral,"FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1":verify_hardy,"FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1":verify_green,"FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1":verify_finite,"FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0":verify_topos}

def load(path:Path):return json.loads(path.read_text())
def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(*,result=None,ranking=None,report=None,run_child_verifiers=True):
    r=load(RESULT) if result is None else result
    source=r.get("source_ranking",{});source_path=ROOT/source.get("path","")
    ranking_data=load(source_path) if ranking is None else ranking
    text=REPORT.read_text() if report is None else report
    load(SCHEMA);errors=[];checks=["artifacts parse"]
    if r.get("result_id")!="FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1" or r.get("lifecycle")!="SEPARATED" or r.get("dependency_tags")!=["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"]:errors.append("identity/lifecycle/tags")
    if not source_path.is_file() or sha(source_path)!=source.get("sha256") or ranking_data.get("result_id")!=source.get("result_id"):errors.append("source ranking pin")
    ranked={x.get("id"):x for x in ranking_data.get("opportunities",[])}
    if len(ranked)!=9:errors.append("source ranking count")
    checker_errors,summary=check(r);errors.extend("checker "+x for x in checker_errors)
    if summary.get("entries")!=9 or summary.get("distinct_artifacts")!=8:errors.append("checker summary")
    checks.append("rank/opportunity closure")
    seen_results=set()
    for row in r.get("entries",[]):
        original=ranked.get(row.get("opportunity_id"),{})
        if row.get("rank")!=original.get("rank") or row.get("title")!=original.get("title") or row.get("first_artifact")!=original.get("first_artifact"):errors.append("ranking drift "+str(row.get("opportunity_id")))
        artifact=row.get("artifact",{});path=ROOT/artifact.get("path","")
        if not path.is_file() or sha(path)!=artifact.get("sha256"):errors.append("artifact hash "+str(row.get("rank")));continue
        child=load(path);result_id=artifact.get("result_id")
        if child.get("result_id")!=result_id:errors.append("artifact identity "+str(row.get("rank")))
        context=child.get("programme_context",{});realized=context.get("opportunities_realized",[context.get("opportunity_realized")])
        if row.get("opportunity_id") not in realized:errors.append("artifact opportunity "+str(row.get("rank")))
        seen_results.add(result_id)
    checks.append("content hashes and opportunity claims")
    if run_child_verifiers:
        if seen_results!=set(CHILD_VERIFIERS):errors.append("child verifier coverage")
        for result_id in sorted(seen_results):
            child_errors,_=CHILD_VERIFIERS[result_id]()
            if child_errors:errors.append("child verifier "+result_id)
        checks.append("8/8 child verifiers")
    flags=r.get("claim_flags",{})
    for key in ("all_ranked_first_artifacts_complete","each_artifact_content_pinned","each_artifact_independently_verified"):
        if flags.get(key) is not True:errors.append("positive flag "+key)
    for key in ("all_deeper_programmes_complete","weakest_bases_all_proved","literature_complete","constructive_weyl_qft_constructed","full_lorentzian_bv_propagator_constructed","lorentzian_qme_proved"):
        if flags.get(key) is not False:errors.append("boundary flag "+key)
    checks.append("completion boundary")
    for token in ("FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1","ALL_RANKED_FIRST_ARTIFACTS_COMPLETE","All nine","Ranks 1 and 3","every row retains","off-shell BV propagator","Lorentzian QME"):
        if token not in text:errors.append("report token "+token)
    checks.append("human report")
    return errors,checks

def main():
    errors,checks=verify();print("FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1: "+("PASS" if not errors else "FAIL"))
    for item in (checks if not errors else errors):print("  - "+item)
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
