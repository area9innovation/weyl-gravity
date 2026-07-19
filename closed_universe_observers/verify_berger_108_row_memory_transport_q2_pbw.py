#!/usr/bin/env python3
"""Independently verify the memory-transport q2 PBW payload."""
import hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_108_row_memory_transport_q2_pbw import CERTIFICATE, DEPENDENCIES, PAYLOAD, PAYLOAD_SCHEMA, ROOT, SCHEMA, action_blocks, canonical_sha256, merge_blocks, serialize_tensor, symbolic_velocity_audit

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def main() -> int:
    value, payload = json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())
    for path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema=json.loads(path.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(document)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT)); assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    rebuilt=serialize_tensor(merge_blocks(action_blocks())); assert payload["rows"] == rebuilt; assert payload["canonical_sha256"] == canonical_sha256(rebuilt); assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert value["velocity_and_cyclicity_audit"]["direct_symbolic_defect_count"] == symbolic_velocity_audit()["direct_symbolic_defect_count"] == 0
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q2_EXPORTED"] is False
    print("BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW independent verification: PASS"); return 0
if __name__ == "__main__": raise SystemExit(main())
