#!/usr/bin/env python3
"""Project the translator, represented-union comparison, and scalar Green audit into cube v14."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1];F=ROOT/"foundations"
V13=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json"
TRANSLATOR=F/"results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json"
TEST_SPACE=F/"results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
GREEN=F/"results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
OUTPUT=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json";REPORT=F/"reports/refined-intersection-cube-v14.md"
TID="FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1";LID="FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1";GID="FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1"
DECISIONS=[
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|KINEMATICS_OBSERVABLES","previous_status":"LOCAL_RESULT","new_status":"LOCAL_RESULT","evidence":{TID:"DIRECT_LOCAL",LID:"DIRECT_LOCAL"},"finding":"Support-advised smooth names now translate exactly into the rational H2 carrier, and their fixed-support stages assemble coherently as a represented compact-test union.","boundary":"This is name-level and carrier-level kinematics; it does not identify the full locally convex LF topology."},
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS","previous_status":"LOCAL_RESULT","new_status":"LOCAL_RESULT","evidence":{LID:"SUPPORTING",GID:"DIRECT_LOCAL"},"finding":"The named weak-wave rail now has a canonical flat scalar 1+1 retarded/advanced evolution with an explicit energy modulus and zero-data uniqueness in the represented energy image.","boundary":"The Green result is scalar and flat; arbitrary-distribution uniqueness, variable coefficients, gauge systems, and Weyl/BV evolution remain open."},
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN","previous_status":"PIECES_ONLY","new_status":"LOCAL_RESULT","evidence":{LID:"SUPPORTING",GID:"DIRECT_LOCAL"},"finding":"Canonical exact retarded and advanced Green maps for the flat 1+1 scalar wave operator satisfy both inverse identities on their code domains, strict causal support, and adjoint duality; supplied source names extend the construction over RCA_0.","boundary":"The LORENTZIAN-CAUSAL claim is confined to the scalar benchmark and is not a Weyl/BV propagator or quantum causal construction."},
 {"coordinate":"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|RECONSTRUCTION_LIMITS","previous_status":"PIECES_ONLY","new_status":"LOCAL_RESULT","evidence":{TID:"DIRECT_LOCAL",LID:"DIRECT_LOCAL",GID:"SUPPORTING"},"finding":"The previously open representation bridge is now explicit: fixed-support smooth names translate to rational H2 names, conventional support advice is equivalent to a tagged represented union, and the exact boundary with the classical LF topology is recorded.","boundary":"This comparison does not metrize the LF space, make the H2 embedding surjective, select support advice, or reconstruct a complete physical theory."},
]
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def key(c:dict[str,Any])->str:return "|".join(c[n] for n in ("foundation","carrier","obligation"))
def digest(cells:list[dict[str,Any]],interfaces:list[dict[str,Any]],carrier_interfaces:list[dict[str,Any]])->str:
    proj={"cells":[(key(c),c["status"],c["evidence"],c["evidence_roles"],c["migration_status"],c.get("vertical_slice_revision")) for c in cells],"interfaces":interfaces,"carrier_interfaces":carrier_interfaces}
    return hashlib.sha256(json.dumps(proj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def build()->dict[str,Any]:
    old,translator,test_space,green=map(load,(V13,TRANSLATOR,TEST_SPACE,GREEN))
    if translator.get("result_id")!=TID or test_space.get("result_id")!=LID or green.get("result_id")!=GID:raise ValueError("certificate identity")
    if not translator["claim_flags"]["fixed_support_smooth_name_translated"] or translator["claim_flags"]["full_lf_topology_identified"]:raise ValueError("translator boundary")
    if not test_space["claim_flags"]["conventional_and_tagged_names_equivalent"] or test_space["claim_flags"]["full_lf_locally_convex_topology_identified"]:raise ValueError("test-space boundary")
    if not green["claim_flags"]["strict_causal_support_proved"] or green["claim_flags"]["weyl_bv_propagator_constructed"]:raise ValueError("Green boundary")
    decisions={d["coordinate"]:d for d in DECISIONS};cells=json.loads(json.dumps(old["cells"]));found=set()
    for cell in cells:
        coordinate=key(cell);d=decisions.get(coordinate)
        if d is None:continue
        found.add(coordinate)
        if cell["status"]!=d["previous_status"]:raise ValueError("unexpected v13 status "+coordinate)
        cell["status"]=d["new_status"]
        for evidence,role in d["evidence"].items():
            if evidence not in cell["evidence"]:cell["evidence"].append(evidence)
            cell["evidence_roles"][evidence]=role
        cell["summary"],cell["boundary"]=d["finding"],d["boundary"]
        cell["vertical_slice_revision"]={"previous_status":d["previous_status"],"new_status":d["new_status"],"evidence":d["evidence"]}
    if found!=set(decisions):raise ValueError("decision closure")
    counts=Counter(c["status"] for c in cells);migrations=Counter(c["migration_status"] for c in cells);roles=Counter(r for c in cells for r in c["evidence_roles"].values())
    for status in ("LOCAL_RESULT","LITERATURE_RESULT","PIECES_ONLY","PRIORITY_GAP","REVIEWED_GAP","NOT_MAPPED"):counts.setdefault(status,0)
    interfaces,carrier_interfaces=old["certified_interfaces"],old["certified_carrier_interfaces"]
    value:dict[str,Any]={
      "schema_version":"foundational-intersection-cube-v14","result_id":"FOUNDATIONAL_INTERSECTION_CUBE_V14","result_kind":"FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_REPRESENTATION_TO_CAUSAL_VERTICAL_SLICE","lifecycle":"EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE","created":"2026-08-14","repository_base_commit":"8d2ceae41e73b748f4f6ca53277423e82697a29c","dependency_tags":old["dependency_tags"],
      "purpose":"Preserve cube v13 while importing the fixed-support smooth-name translator, the support-indexed represented-union comparison, and the exact flat scalar 1+1 Green benchmark as a single assumption-audited vertical slice.",
      "compatibility":{**old["compatibility"],"v13_full_surface_preserved":True,"v13_cells_preserved_except_four_declared_vertical_slice_decisions":True,"v13_interfaces_preserved":True,"fixed_support_translator":TID,"support_indexed_comparison":LID,"scalar_green_audit":GID},
      "axes":old["axes"],"cell_statuses":old["cell_statuses"],"migration_statuses":old["migration_statuses"],"evidence_role_vocabulary":old["evidence_role_vocabulary"],"evidence_role_rule":old["evidence_role_rule"],
      "dimensions":{**old["dimensions"],"vertical_slice_augmented_cells":4,"vertical_slice_status_changes":2,"vertical_slice_certificates":3,"status_counts":dict(sorted(counts.items())),"migration_status_counts":dict(sorted(migrations.items())),"evidence_role_counts":dict(sorted(roles.items())),"dual_direct_cells":sum({"DIRECT_LOCAL","DIRECT_LITERATURE"}<=set(c["evidence_roles"].values()) for c in cells)},
      "certified_interfaces":interfaces,"certified_carrier_interfaces":carrier_interfaces,"cells":cells,
      "provenance":{"inputs":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in (V13,TRANSLATOR,TEST_SPACE,GREEN)]},
      "independent_checker":{"path":"foundations/check_refined_intersection_cube_v14.py","checks":["exact 576-cell surface","572 v13 cells unchanged","four declared multi-certificate augmentations","two status promotions","evidence-role closure","all interfaces preserved","scalar causal versus Weyl/BV boundary","canonical digest"],"expected_digest":digest(cells,interfaces,carrier_interfaces)},
      "claim_flags":{"v13_surface_preserved":True,"all_576_coordinates_assessed":True,"fixed_support_translator_imported":True,"support_indexed_comparison_imported":True,"scalar_green_audit_imported":True,"represented_name_equivalence_established":True,"scalar_causal_green_established":True,"full_lf_test_topology_established":False,"arbitrary_distributional_uniqueness_established":False,"variable_coefficient_green_established":False,"weyl_bv_green_established":False,"hadamard_or_quantum_causal_construction_established":False,"empirical_agreement_assessed":False,"complete_physical_theory_established":False,"new_lorentzian_claim":True},
      "does_not_establish":["a support or convergence modulus selected from a bare extensional function","the full locally convex LF topology or a single metrization of C_c-infinity","surjectivity of the smooth-test embedding onto H2","uniqueness among arbitrary distributional weak solutions","a variable-coefficient or curved-spacetime Green operator","a Lorentzian Weyl/BV propagator","a Hadamard state, causal perturbative AQFT construction, or Lorentzian quantum master equation","empirical calibration or observational agreement","that all 576 coordinates are jointly realizable","a complete physical theory"],
      "human_report":"foundations/reports/refined-intersection-cube-v14.md"
    }
    return value
def render(value:dict[str,Any])->str:
    counts=value["dimensions"]["status_counts"]
    return "\n".join(["# Foundations cube v14: representation-to-causality vertical slice","",f"**Result:** `{value['result_id']}`","","## Outcome","","Cube v14 preserves all 576 v13 coordinates and augments exactly four weak-arithmetic smooth/distributional cells with three independently certified results: a fixed-support smooth-to-H2 translator, a support-indexed represented-union comparison, and a canonical scalar 1+1 Minkowski Green construction.","","Reconstruction/limits and causal propagation/Green become scoped local results. The causal promotion is real but narrow: it certifies the displayed scalar flat-spacetime operator, not a Lorentzian Weyl/BV propagator or quantum causal theory.","",f"The surface contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.","","## Reproduction","","```text","python3 foundations/refine_intersection_cube_v14.py --check","python3 foundations/check_refined_intersection_cube_v14.py","python3 foundations/verify_refined_intersection_cube_v14.py","python3 -m unittest foundations.tests.test_refined_intersection_cube_v14","```","","## Boundaries","",*["- This does not establish "+x+"." for x in value["does_not_establish"]],""])
def generated()->tuple[bytes,bytes]:
    value=build();return (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode(),render(value).encode()
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();rb,mb=generated();outputs=((OUTPUT,rb),(REPORT,mb));stale=[str(path.relative_to(ROOT)) for path,data in outputs if not path.is_file() or path.read_bytes()!=data]
    if a.check:print("FOUNDATIONAL_INTERSECTION_CUBE_V14: "+("generated artifacts current" if not stale else "stale: "+", ".join(stale)));return bool(stale)
    for path,data in outputs:path.write_bytes(data)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V14: wrote result and report");return 0
if __name__=="__main__":raise SystemExit(main())
