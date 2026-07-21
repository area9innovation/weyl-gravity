from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"


def test_stored_generic_isotypical_obstruction_is_current() -> None:
    certificate = json.loads(CERT.read_text())
    assert certificate["payload_ref"]["sha256"] == hashlib.sha256(PAYLOAD.read_bytes()).hexdigest()
    assert certificate["carrier"]["all_k_closure"] is True


def test_factor_field_and_residue_audits_are_complete() -> None:
    payload = json.loads(PAYLOAD.read_text())
    audits = payload["physical_quotient"]["factor_audits"]
    assert len(audits) == 4
    assert all(row["physical_matrix_rank_over_factor_field"] == 12 for row in audits)
    assert all(row["residue_nondegenerate"] is True for row in audits)


def test_physical_instability_is_not_a_gauge_or_charge_direction() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    assert certificate["result_state"].startswith("OBSTRUCTED_FIRST_NONSTABILIZER")
    assert payload["terminal_verdict"]["physical_multiplicity_per_root"] == 2
    assert payload["physical_quotient"]["cohomology_pairing_radical_dimension"] == 0
    assert payload["unstable_sector"]["two_copy_inertia_positive_negative_zero"] == [4, 4, 0]
    assert "zero tangent action" in payload["charge_actions"]["R_rel"]
    assert payload["charge_actions"]["action_angle_tangent"].startswith("NOT_PRESENT")
