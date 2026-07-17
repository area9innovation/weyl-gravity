from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    verify_berger_maxwell_unary_contraction_transfer as independent,
)


def test_maxwell_contraction_and_transfer_scope() -> None:
    certificate = json.loads(independent.CERTIFICATE.read_text())
    assert certificate["flags"]["BERGER_MAXWELL_UNARY_CONTRACTION"] is True
    assert certificate["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"] is True
    assert certificate["flags"]["BERGER_FIRST_MIXED_Q2_COEFFICIENT_TRANSFER"] is True
    assert certificate["flags"]["BERGER_MIXED_Q2_CYCLICITY"] is False
    assert certificate["flags"]["BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING"] is False
    assert certificate["first_transferred_mixed_vertex"]["term_count"] == 1522
    assert certificate["first_transferred_mixed_vertex"]["mixed_gravity_Maxwell_input_term_count"] > 0
    for flag in (
        "BERGER_MIXED_Q2_CYCLICITY",
        "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
        "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        assert certificate["flags"][flag] is False


def test_independent_maxwell_transfer_replay() -> None:
    assert independent.main() == 0
