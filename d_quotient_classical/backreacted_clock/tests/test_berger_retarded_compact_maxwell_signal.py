from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    verify_berger_retarded_compact_maxwell_signal as independent,
)


def test_compact_source_and_signal_scope() -> None:
    certificate = json.loads(independent.CERTIFICATE.read_text())
    assert certificate["flags"]["BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE"] is True
    assert certificate["flags"]["BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"] is True
    assert certificate["exact_checks"]["current_is_closed"] is True
    assert certificate["exact_checks"]["retarded_field_strength_nonzero"] is True
    for flag in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        assert certificate["flags"][flag] is False


def test_independent_compact_source_signal_replay() -> None:
    assert independent.main() == 0
