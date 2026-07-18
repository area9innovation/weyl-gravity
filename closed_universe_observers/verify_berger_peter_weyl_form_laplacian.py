#!/usr/bin/env python3
import json
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import CERTIFICATE,DEPENDENCIES,SCHEMA,_sha256,block_audit
def main()->int:
 v=json.loads(CERTIFICATE.read_text());s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v)
 for n,p in DEPENDENCIES.items():
  if v["dependency_refs"][n]["sha256"]!=_sha256(p):raise AssertionError(f"dependency drifted: {n}")
 for k in range(5):
  a=block_audit(k)
  if any(a["d_squared_defect_counts"]) or not a["all_laplacians_hermitian"] or not a["hodge_dual_spectra_match"]:raise AssertionError(f"block failed: {k}")
 print("BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
