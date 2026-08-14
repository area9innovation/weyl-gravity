#!/usr/bin/env python3
"""Independent fail-closed checker for the scalar-to-Weyl dependency delta."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1.json"
EXPECTED_IDS=[f"D{i:02d}_{name}" for i,name in enumerate(("SCALAR_FACTOR","FOURTH_ORDER_COMPOSITION","TENSOR_CARRIER","GAUGE_FIXING","CURVED_LOWER_ORDER","CONSTRAINT_PROPAGATION","DEGREEWISE_INVERSES","BRST_COMPATIBILITY","SUPPORT_MICROLOCAL","CLASSICAL_FREEZE","NARIAI_POSITIVE_SLICE","BERGER_ROUTE","24_FIELD_NO_GO","46_PARAMETER_NO_GO","RESIDUAL_CLASSES","QUANTUM_CAUSAL"),1)]
ALLOWED={"PROVED_SCALAR","SCOPED_WEYL_RESULT","OPEN_SEEDED","MISSING_CERTIFICATE","FAIL_CLOSED_IMPORT","SCOPED_NO_GO","FORBIDDEN_TRANSFER"}
FALSE_FLAGS=("classical_import_gate_passed","full_weyl_bv_propagator_constructed","brst_compatible_hadamard_state_constructed","renormalized_lorentzian_products_constructed","causal_paqft_constructed","lorentzian_qme_restored","residual_quantum_transfer_completed","lorentzian_full_complex_certified")
def digest(v:dict[str,Any])->str:
    keys=("status_vocabulary","dependency_delta","existing_scoped_architectures","classical_import_gate","lifecycle_gate","forbidden_inferences")
    return hashlib.sha256(json.dumps({k:v[k] for k in keys},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def check(v:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    v=json.loads(RESULT.read_text()) if v is None else v;e=[];rows=v.get("dependency_delta",[])
    if [x.get("id") for x in rows]!=EXPECTED_IDS:e.append("gate identity/order")
    vocab={x.get("id") for x in v.get("status_vocabulary",[])}
    if vocab!=ALLOWED:e.append("status vocabulary")
    if any(x.get("status") not in vocab for x in rows):e.append("status closure")
    expected_status=["PROVED_SCALAR","PROVED_SCALAR","MISSING_CERTIFICATE","MISSING_CERTIFICATE","MISSING_CERTIFICATE","MISSING_CERTIFICATE","MISSING_CERTIFICATE","MISSING_CERTIFICATE","MISSING_CERTIFICATE","FAIL_CLOSED_IMPORT","SCOPED_WEYL_RESULT","OPEN_SEEDED","SCOPED_NO_GO","SCOPED_NO_GO","FORBIDDEN_TRANSFER","MISSING_CERTIFICATE"]
    if [x.get("status") for x in rows]!=expected_status:e.append("fail-closed status assignment")
    for row in rows:
        if not row.get("missing_certificate") or not row.get("does_not_establish"):e.append("missing boundary field")
    gate=v.get("classical_import_gate",{})
    if gate.get("status")!="FAIL_CLOSED" or gate.get("claim_state")!="CLASSICAL_IMPORT_PENDING" or gate.get("publishable_quantum_results_allowed") is not False:e.append("classical gate")
    if len(gate.get("blocked_or_failed_checks",[]))!=10 or len(gate.get("missing_exports",[]))!=17:e.append("classical gate ledger counts")
    if v.get("lifecycle_gate",{}).get("states_reached_for_full_weyl_bv")!=[]:e.append("lifecycle promoted")
    if v.get("lifecycle_gate",{}).get("target_order")!=["CLASSIFIED","COEFFICIENT_COMPUTED","QME_RESTORED","RESIDUAL_TRANSFERRED","LORENTZIAN_CERTIFIED"]:e.append("lifecycle order")
    flags=v.get("claim_flags",{})
    if not all(flags.get(x) is True for x in ("scalar_biwave_green_imported","transfer_requirements_classified","scoped_nariai_weyl_result_recorded","scoped_architectural_no_gos_recorded")):e.append("positive classification flags")
    for name in FALSE_FLAGS:
        if flags.get(name) is not False:e.append("forbidden promotion "+name)
    if len(v.get("forbidden_inferences",[]))!=7:e.append("forbidden inference ledger")
    pins=v.get("provenance",{}).get("inputs",[])
    for pin in pins:
        p=ROOT/pin.get("path","")
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=pin.get("sha256"):e.append("provenance "+str(pin.get("path")))
    d=digest(v)
    if d!=v.get("independent_checker",{}).get("expected_digest"):e.append("digest")
    return e,{"digest":d,"gates":len(rows),"missing":sum(x.get("status")=="MISSING_CERTIFICATE" for x in rows),"scoped_positive":sum(x.get("status")=="SCOPED_WEYL_RESULT" for x in rows),"scoped_no_go":sum(x.get("status")=="SCOPED_NO_GO" for x in rows),"classical_blocked_checks":len(gate.get("blocked_or_failed_checks",[]))}
def main()->int:
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
