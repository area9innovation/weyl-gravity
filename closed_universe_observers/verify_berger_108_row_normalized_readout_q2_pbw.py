#!/usr/bin/env python3
"""Independently verify the normalized-readout q2 PBW payload."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_normalized_readout_q2_pbw import (
    CERTIFICATE,
    DEPENDENCIES,
    J_VERTICAL_ORDER,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    action_blocks,
    canonical_sha256,
    component_first_jet_replay_audit,
    merge_blocks,
    serialize_tensor,
    symbolic_first_jet_audit,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    rebuilt = serialize_tensor(merge_blocks(action_blocks()))
    assert payload["rows"] == rebuilt
    assert payload["canonical_sha256"] == canonical_sha256(rebuilt)
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert payload["J_vertical_coordinate_order"] == list(J_VERTICAL_ORDER)
    assert symbolic_first_jet_audit()["direct_symbolic_defect_count"] == 0
    assert all(component_first_jet_replay_audit(channel)["component_replay_defect_count"] == 0 for channel in (0, 1))
    assert symbolic_first_jet_audit(delete_jacobian_variation=True)["jacobian_deletion_defect_count"] == 1
    assert value["flags"]["COMPLETE_APPARATUS_Q2_SUBBLOCKS_EXPORTED"] is True
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q2_EXPORTED"] is False
    print("BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
