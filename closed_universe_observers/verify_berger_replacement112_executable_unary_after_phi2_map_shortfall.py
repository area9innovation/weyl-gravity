#!/usr/bin/env python3
"""Independent verifier for the replacement-112 post-Phi2 shortfall."""
import hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL.json"
X = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-executable-unary-after-phi2-map-shortfall-v1.schema.json"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    refs = cert["dependency_refs"]
    replacement = json.loads((ROOT / refs["replacement_payload"]["path"]).read_text())
    phi = json.loads((ROOT / refs["phi2_payload"]["path"]).read_text())
    assert len(replacement["carrier"]["rows"]) == 112
    assert len(replacement["carrier"]["pairing_entries"]) == 112
    evaluated = phi["evaluated_nonrod_D3S"]
    closed = payload["certified_inputs_now_executable"]
    assert closed["dependent_term_count"] == 6171
    assert closed["unaffected_term_count"] == 288
    assert closed["evaluated_changed_nonrod_blocks_canonical_sha256"] == evaluated["blocks_canonical_sha256"]
    assert closed["unaffected_terms_canonical_sha256"] == evaluated["unaffected_terms_canonical_sha256"]
    unary = replacement["complete_unary"]
    mixed = replacement["mixed_action"]
    absent = set(payload["exact_absence_replay"]["required_executable_fields_absent"])
    assert not absent.intersection(unary)
    assert not absent.intersection(mixed)
    assert isinstance(unary["action_variation_rows"]["metric_rows"], str)
    assert "second variation" in unary["action_variation_rows"]["metric_rows"]
    missing = payload["first_missing_action_derivative"]
    assert missing["formula"].startswith("D_g D_R S_R,H")
    assert missing["status"] == "NO_CERTIFIED_MAP"
    assert payload["disposition"]["complete_executable_replacement112_q1"] == "NO_CERTIFIED_MAP"
    print("BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL independent verification: PASS")
    return 0

if __name__ == "__main__": raise SystemExit(main())
