#!/usr/bin/env python3
"""Independent verifier for the replacement-112 variational input shortfall."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL.json"
X = P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement-112-executable-unary-variational-input-shortfall-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    old = json.loads((ROOT / cert["dependency_refs"]["old_108_payload"]["path"]).read_text())
    replacement = json.loads((ROOT / cert["dependency_refs"]["replacement_payload"]["path"]).read_text())
    names = {
        factor["name"]
        for block in old["blocks"] for entry in block["entries"]
        for term in entry["terms"] for factor in term["coefficient_factors"]
        if factor["name"].startswith("Phi2_")
    }
    assert names == set(payload["exact_absence_replay"]["old_local_Phi2_symbols"])
    assert "Phi2_00" in names
    assert "retained_to_component_jet_crosswalk" not in replacement["background_equation"]
    assert payload["first_missing_variational_derivative"]["status"] == "NO_CERTIFIED_MAP"
    assert payload["disposition"]["material_parent_56_export"] == "NOT_REACHED"
    print("BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
