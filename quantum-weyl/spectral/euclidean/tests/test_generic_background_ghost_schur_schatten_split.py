from __future__ import annotations

import json

from spectral.euclidean import generic_background_ghost_schur_schatten_split as producer
from spectral.euclidean import verify_generic_background_ghost_schur_schatten_split as verifier


def test_producer_rebuilds_committed_certificate() -> None:
    assert producer.OUTPUT.read_text() == json.dumps(
        producer.build(), indent=2, sort_keys=True
    ) + "\n"


def test_independent_det3_series_starts_at_cubic_order() -> None:
    assert all(
        residual == 0
        for residual in verifier.independent_det3_series_residuals().values()
    )


def test_independent_critical_residue_replay() -> None:
    assert verifier.independent_residue_residual() == 0


def test_critical_residue_mutation_is_rejected() -> None:
    assert verifier.independent_residue_residual(mutate=True) != 0


def test_fail_closed_regularization_boundary() -> None:
    value = producer.build()
    flags = value["claim_flags"]
    assert flags["SCHUR_CORRECTION_S3_CLASS_PROVED"] is True
    assert flags["CANONICAL_DET3_TAIL_DEFINED"] is True
    assert flags["CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED"] is True
    assert flags["ORDINARY_TRACE_CLASS_PROVED"] is False
    assert flags["FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"] is False
    assert flags["WODZICKI_RESIDUE_K_COMPUTED"] is False
    assert flags["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"] is False
    assert flags["SCHUR_COVARIANT_FORM_FACTORS_COMPUTED"] is False


def test_full_independent_verifier() -> None:
    verifier.verify(json.loads(producer.OUTPUT.read_text()))
