#!/usr/bin/env python3
"""Project the scalar biwave theorem and Weyl-BV delta into cube v15."""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];F=ROOT/"foundations"
V14=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json";BIWAVE=F/"results/FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1.json";DELTA=F/"results/FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1.json"
OUTPUT=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json";REPORT=F/"reports/refined-intersection-cube-v15.md"
BID="FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1";DID="FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1"
DECISIONS=[
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS","evidence":{BID:"DIRECT_LOCAL"},"summary":"The flat scalar rail now includes both the wave equation and its fourth-order biwave square, with canonical retarded/advanced maps, four past-zero Cauchy data, and a finite-horizon two-stage energy modulus.","boundary":"The biwave extension is flat and scalar; it proves no variable-coefficient tensor or Weyl BV evolution theorem."},
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN","evidence":{BID:"DIRECT_LOCAL",DID:"SUPPORTING"},"summary":"Canonical exact Green maps now cover P and P^2 on the declared flat scalar code domains. A separate fail-closed delta identifies sixteen gates between this benchmark and a Lorentzian Weyl BV propagator.","boundary":"Two scalar factors do not transfer across tensor, gauge, chain, microlocal, or classical-import gates."},
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|GAUGE_BV_COHOMOLOGY","evidence":{DID:"SUPPORTING"},"summary":"The continuum BV gap now has a typed missing-object ledger, including carrier, gauge-fixing, degreewise inverse, BRST-compatibility, constraint, microlocal, and classical-freeze gates.","boundary":"A classified dependency gap remains a PRIORITY_GAP, not a constructed continuum BV complex."}]
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def key(c:dict[str,Any])->str:return "|".join(c[x] for x in ("foundation","carrier","obligation"))
def digest(cells:list[dict[str,Any]],i:list[dict[str,Any]],ci:list[dict[str,Any]])->str:
    return hashlib.sha256(json.dumps({"cells":[(key(c),c["status"],c["evidence"],c["evidence_roles"],c["migration_status"],c.get("biwave_delta_revision")) for c in cells],"interfaces":i,"carrier_interfaces":ci},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def build()->dict[str,Any]:
    old,biwave,delta=map(load,(V14,BIWAVE,DELTA))
    if not biwave["claim_flags"]["strict_causal_support_proved"] or biwave["claim_flags"]["weyl_bv_propagator_constructed"]:raise ValueError("biwave boundary")
    if not delta["claim_flags"]["transfer_requirements_classified"] or delta["claim_flags"]["full_weyl_bv_propagator_constructed"]:raise ValueError("delta boundary")
    decisions={x["coordinate"]:x for x in DECISIONS};cells=json.loads(json.dumps(old["cells"]));found=set()
    for cell in cells:
        coordinate=key(cell);d=decisions.get(coordinate)
        if not d:continue
        found.add(coordinate);prior=cell["status"]
        for evidence,role in d["evidence"].items():
            if evidence not in cell["evidence"]:cell["evidence"].append(evidence)
            cell["evidence_roles"][evidence]=role
        cell["summary"],cell["boundary"]=d["summary"],d["boundary"]
        cell["biwave_delta_revision"]={"previous_status":prior,"new_status":prior,"evidence":d["evidence"]}
    if found!=set(decisions):raise ValueError("decision closure")
    counts=Counter(c["status"] for c in cells);roles=Counter(r for c in cells for r in c["evidence_roles"].values());migrations=Counter(c["migration_status"] for c in cells)
    for status in ("LOCAL_RESULT","LITERATURE_RESULT","PIECES_ONLY","PRIORITY_GAP","REVIEWED_GAP","NOT_MAPPED"):counts.setdefault(status,0)
    value={"schema_version":"foundational-intersection-cube-v15","result_id":"FOUNDATIONAL_INTERSECTION_CUBE_V15","result_kind":"FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_SCALAR_BIWAVE_TO_WEYL_BV_DELTA","lifecycle":"EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE","created":"2026-08-14","repository_base_commit":"b5601e3e7f616cc03ea094be3ea6cc577043931d","dependency_tags":old["dependency_tags"],"purpose":"Preserve cube v14 while importing the exact flat scalar biwave construction and its fail-closed dependency delta to the Lorentzian Weyl BV target.","compatibility":{**old["compatibility"],"v14_full_surface_preserved":True,"v14_cells_preserved_except_three_declared_evidence_augmentations":True,"v14_interfaces_preserved":True,"scalar_biwave":BID,"weyl_bv_dependency_delta":DID},"axes":old["axes"],"cell_statuses":old["cell_statuses"],"migration_statuses":old["migration_statuses"],"evidence_role_vocabulary":old["evidence_role_vocabulary"],"evidence_role_rule":old["evidence_role_rule"],"dimensions":{**old["dimensions"],"biwave_delta_augmented_cells":3,"biwave_delta_status_changes":0,"biwave_delta_certificates":2,"status_counts":dict(sorted(counts.items())),"migration_status_counts":dict(sorted(migrations.items())),"evidence_role_counts":dict(sorted(roles.items())),"dual_direct_cells":sum({"DIRECT_LOCAL","DIRECT_LITERATURE"}<=set(c["evidence_roles"].values()) for c in cells)},"certified_interfaces":old["certified_interfaces"],"certified_carrier_interfaces":old["certified_carrier_interfaces"],"cells":cells,"provenance":{"inputs":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in (V14,BIWAVE,DELTA)]},"independent_checker":{"path":"foundations/check_refined_intersection_cube_v15.py","checks":["exact 576-cell surface","573 v14 cells unchanged","three declared evidence augmentations","zero status changes","evidence-role closure","all interfaces preserved","Weyl/BV fail-closed boundary","canonical digest"],"expected_digest":""},"claim_flags":{"v14_surface_preserved":True,"all_576_coordinates_assessed":True,"scalar_biwave_imported":True,"weyl_bv_dependency_delta_imported":True,"scalar_biwave_green_established":True,"weyl_bv_gap_classified":True,"weyl_bv_green_established":False,"classical_import_gate_passed":False,"hadamard_or_quantum_causal_construction_established":False,"complete_physical_theory_established":False,"new_lorentzian_claim":True},"does_not_establish":["a variable-coefficient or curved-spacetime tensor Green operator","a full off-shell Lorentzian Weyl BV propagator","a passed classical import freeze gate","BRST-compatible causal homotopies","a Hadamard state or microlocal spectrum theorem","renormalized Lorentzian products, causal pAQFT, or a Lorentzian QME","that scoped no-go results rule out neighboring architectures","a weakest-base reversal","empirical adequacy","a complete physical theory"],"human_report":"foundations/reports/refined-intersection-cube-v15.md"}
    value["independent_checker"]["expected_digest"]=digest(cells,value["certified_interfaces"],value["certified_carrier_interfaces"]);return value
def render(v:dict[str,Any])->str:
    counts=v["dimensions"]["status_counts"]
    return "\n".join(["# Foundations cube v15: scalar biwave to Weyl BV delta","",f"**Result:** `{v['result_id']}`","","## Outcome","","Cube v15 preserves all 576 v14 coordinates and their statuses. It adds the exact flat scalar biwave theorem to evolution and causality, then adds a fail-closed sixteen-gate dependency delta to the continuum gauge/BV gap.","","The cube therefore gains depth without pretending to gain Weyl-BV coverage. The causal scalar result is real; the full continuum BV coordinate remains a priority gap.","",f"Counts remain **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.","","## Reproduction","","```text","python3 foundations/refine_intersection_cube_v15.py --check","python3 foundations/check_refined_intersection_cube_v15.py","python3 foundations/verify_refined_intersection_cube_v15.py","python3 -m unittest foundations.tests.test_refined_intersection_cube_v15","```","","## Boundaries","",*["- This does not establish "+x+"." for x in v["does_not_establish"]],""])
def generated()->tuple[bytes,bytes]:
    v=build();return (json.dumps(v,indent=2,ensure_ascii=False)+"\n").encode(),render(v).encode()
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();rb,mb=generated();outputs=((OUTPUT,rb),(REPORT,mb));stale=[str(p.relative_to(ROOT)) for p,c in outputs if not p.is_file() or p.read_bytes()!=c]
    if a.check:print("FOUNDATIONAL_INTERSECTION_CUBE_V15: "+("generated artifacts current" if not stale else "stale: "+", ".join(stale)));return bool(stale)
    for p,c in outputs:p.write_bytes(c)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V15: wrote result and report");return 0
if __name__=="__main__":raise SystemExit(main())
