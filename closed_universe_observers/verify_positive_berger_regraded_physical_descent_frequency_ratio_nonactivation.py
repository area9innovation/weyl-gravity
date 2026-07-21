#!/usr/bin/env python3
"""Independent replay of the final regraded-receiver nonactivation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json"
Q = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD.json"
S = P / "schema/positive-berger-regraded-receiver-physical-descent-frequency-ratio-not-activated-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    integration = json.loads((ROOT / cert["dependency_refs"]["regraded_integration"]["path"]).read_text())
    assert integration["atlas_status"] == "OBSTRUCTED"
    assert integration["downstream_disposition"]["physical_descent_input_contract"] == "NO_CERTIFIED_MAP"
    ladder = payload["ordered_admissibility_ladder"]
    assert ladder[2]["first_failure"] and ladder[2]["status"] == "OBSTRUCTED"
    assert all(row["status"] in {"NOT_REACHED", "NOT_ACTIVATED"} for row in ladder[3:])
    classical = payload["independent_classical_dispositions"]
    assert "REMOVES_RELATIVE_CLOCK" in classical["fixed_Q_rel"]["status"]
    assert "SECULAR_ZERO_JORDAN" in classical["unrestricted_Q_rel"]["status"]
    assert "COMPLEX_FREQUENCY" in classical["first_generic_physical_block"]["status"]
    ratio = payload["frequency_ratio_partial_function"]
    assert ratio["domain"] == [] and ratio["value"] == "UNDEFINED"
    assert all(row["rejected"] for row in payload["mutations"].values())
    print("POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
