"""Produce the bounded module/current checkpoint."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from .module_audit import master_infinity_audit, polynomial_master_ricci_residual, shallow_log_audit

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build() -> dict:
    completion = ROOT/'black_hole_programme/phase2/general_l_polar_completion/certificate.json'
    polar = ROOT/'black_hole_programme/phase2/general_l_polar/certificate.json'
    branches = sorted((completion.parent/'branch_artifacts').glob('*.json'))
    return {
      "schema_version":"phase2-polar-extendible-current-closure-v1",
      "result_id":"POLAR_EXTENDIBLE_MODULE_CURRENT_CLOSURE_CHECKPOINT_V1",
      "dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
      "imports":{"input_commit":"b9d347d832492d9e39a8cfbd346b041f35f22de7",
        "completion_sha256":sha(completion),"polar_v1_sha256":sha(polar),
        "branch_sha256":{p.name:sha(p) for p in branches}},
      "master_infinity":master_infinity_audit(),
      "polynomial_master_seven_row_crosscheck":polynomial_master_ricci_residual(),
      "shallow_log":shallow_log_audit(),
      "status":{
        "module_reconciliation":"OPEN: Bach-master generalized dimensions cannot be used as source-zero seven-row Einstein dimensions without quotient identification",
        "current":"NOT_COMPUTED",
        "expected_31_entry_table":"NOT_PROMOTED",
        "bounded_frontier":"The optimized GJ seven-row splitting has different finite-depth free counts from the four-state master estimate; basis/quotient identification and new physical pivot-wall factors must be resolved before a representative-invariant Gram table is well typed."},
      "does_not_establish":["generic-ell polar finite-flux selection","31-entry current Gram table","all-order asymptotic solutions","asymptotic phase space","scattering","stability","positivity"]}

def main():
    PKG.mkdir(parents=True,exist_ok=True)
    (PKG/'certificate.json').write_text(json.dumps(build(),indent=2,sort_keys=True)+'\n')
if __name__=='__main__': main()

