from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PRODUCER = ROOT / "d_quotient_classical/compensator/two_phase_counterflow_causal_bv_parent_v2.py"
VERIFIER = ROOT / "d_quotient_classical/compensator/verify_two_phase_counterflow_causal_bv_parent_v2.py"
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json"
RECEIVER = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2.json"


def test_repaired_parent_is_current_and_fail_closed() -> None:
    subprocess.run([sys.executable, str(PRODUCER), "--check"], cwd=ROOT, check=True)
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    receiver = json.loads(RECEIVER.read_text())
    assert certificate["result_state"] == "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT"
    assert payload["grading"]["degree_shift_histogram"] == {"+1": 317}
    assert payload["row_layout"]["degree_ranks"] == [6, 29, 29, 6]
    assert certificate["terminal_verdict"]["physical_quotient_status"] == "OPEN"
    assert receiver["stale_hash_policy"]["V1_q2_or_receiver_hashes"] == "REJECT_FOR_V2_CLAIMS"


def test_independent_action_cotangent_replay() -> None:
    subprocess.run([sys.executable, str(VERIFIER)], cwd=ROOT, check=True)


def test_v1_is_preserved_as_historical_input() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    imports = certificate["imports"]
    assert imports["parent_v1"]["sha256"] == "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7"
    assert certificate["terminal_verdict"]["V1_interface_status"] == "SUPERSEDED_NOT_REWRITTEN"
