from __future__ import annotations

import json

import sympy as sp

from spectral.euclidean import generic_background_ghost_longitudinal_schur_resummation as producer
from spectral.euclidean import verify_generic_background_ghost_longitudinal_schur_resummation as verifier


def test_producer_rebuilds_committed_certificate() -> None:
    assert producer.OUTPUT.read_text() == json.dumps(
        producer.build(), indent=2, sort_keys=True
    ) + "\n"


def test_independent_fixture_replays_all_orders() -> None:
    assert all(
        residual == 0 for residual in verifier.independent_fixture_residuals().values()
    )


def test_independent_fixture_rejects_cubic_mutation() -> None:
    residuals = verifier.independent_fixture_residuals(mutate_cubic=True)
    assert residuals["determinant"] == 0
    assert residuals["linear"] == 0
    assert residuals["quadratic"] == 0
    assert residuals["cubic"] != 0


def test_regularization_boundary_is_fail_closed() -> None:
    value = producer.build()
    assert value["regularization_boundary"]["zeta_multiplicative_anomaly"] == "LOCAL_TERM_NOT_EVALUATED"
    assert value["regularization_boundary"]["generic_4d_trace_class_status"] == "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR"
    assert value["claim_flags"]["ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED"] is False
    assert value["claim_flags"]["ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED"] is False
    assert value["claim_flags"]["GENERIC_LONGITUDINAL_SCHUR_FORM_FACTORS_COMPUTED"] is False


def test_completed_cubic_coefficients_are_exact() -> None:
    rows = producer.build()["resolvent_series"]["Hodge_carrier_match"]["completed_n3_longitudinal_coefficients"]
    assert [sp.Rational(row["numerator"], row["denominator"]) for row in rows] == [
        -sp.Rational(1, 3),
        sp.Rational(1, 9),
        -sp.Rational(1, 81),
    ]


def test_full_independent_verifier() -> None:
    verifier.verify(json.loads(producer.OUTPUT.read_text()))
