from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PRODUCER = ROOT / "d_quotient_classical/compensator/two_phase_counterflow_berger_full_isotypical_q70_grading_obstruction.py"
VERIFIER = ROOT / "d_quotient_classical/compensator/verify_two_phase_counterflow_berger_full_isotypical_q70_grading_obstruction.py"
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1.json"


def test_stored_artifacts_are_current_and_fail_closed() -> None:
    subprocess.run([sys.executable, str(PRODUCER), "--check"], cwd=ROOT, check=True)
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    assert certificate["terminal_verdict"]["graded_q70_import"] == "OBSTRUCTED"
    assert certificate["terminal_verdict"]["ungraded_isotypical_closure"] == "CERTIFIED_FINITE_COMPLETE"
    assert payload["q54_grading_audit"]["degree_shift_histogram"] == {"+1": 309}
    assert payload["u1_grading_audit"]["serialized_degree_shift_histogram"] == {"-1": 8}
    assert payload["repair_candidate"]["promotion_status"] == "NOT_APPLIED_TO_PINNED_PARENT"


def test_independent_exact_replay() -> None:
    subprocess.run([sys.executable, str(VERIFIER)], cwd=ROOT, check=True)
