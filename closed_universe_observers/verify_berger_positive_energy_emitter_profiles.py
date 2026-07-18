#!/usr/bin/env python3
"""Independent verifier for positive-energy selected emitter profiles."""
import json
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_positive_energy_emitter_profiles import CERTIFICATE, DEPENDENCIES, SCHEMA, _sha256, energy_dual_audit, support_audit

def main() -> int:
    value=json.loads(CERTIFICATE.read_text()); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)
    for name,path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"]!=_sha256(path): raise AssertionError(f"dependency drifted: {name}")
    if not energy_dual_audit()["strictly_positive_for_nonzero_covector_data"]: raise AssertionError("energy dual failed")
    if energy_dual_audit(flip_dual_sign=True)["strictly_positive_for_nonzero_covector_data"]: raise AssertionError("sign mutation escaped")
    if energy_dual_audit(delete_configuration_term=True)["strictly_positive_for_nonzero_covector_data"]: raise AssertionError("configuration mutation escaped")
    if not support_audit()["compact_and_constraint_compatible"]: raise AssertionError("support audit failed")
    print("BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
