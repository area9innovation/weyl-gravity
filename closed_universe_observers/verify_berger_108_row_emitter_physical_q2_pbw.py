#!/usr/bin/env python3
"""Independently verify the physical emitter q2 PBW payload."""
import hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import CERTIFICATE, DEPENDENCIES, PAYLOAD, PAYLOAD_SCHEMA, ROOT, SCHEMA, action_to_q2, canonical_sha256, metric_jet_audit, physical_cubic_action, q1_hessian_recovery_audit, serialize_tensor

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def main() -> int:
    value,payload=json.loads(CERTIFICATE.read_text()),json.loads(PAYLOAD.read_text())
    for path,document in ((SCHEMA,value),(PAYLOAD_SCHEMA,payload)):
        schema=json.loads(path.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(document)
    for name,dependency in value["dependency_refs"].items(): assert dependency["path"]==str(DEPENDENCIES[name].relative_to(ROOT)) and dependency["sha256"]==sha256(DEPENDENCIES[name])
    rebuilt=serialize_tensor(action_to_q2(physical_cubic_action()[0])); assert payload["rows"]==rebuilt and payload["canonical_sha256"]==canonical_sha256(rebuilt); assert value["payload_ref"]["sha256"]==sha256(PAYLOAD)
    assert q1_hessian_recovery_audit()["q1_hessian_recovery_defect_count"]==0; assert metric_jet_audit()["metric_bilinear_first_jet_defect_count"]==0
    print("BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW independent verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
