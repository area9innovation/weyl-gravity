from __future__ import annotations

from closed_universe_observers.generate_berger_cg4_record_poisson_algebra import algebra_audit, build


def test_phase_plane_record_map_is_invertible() -> None:
    audit = algebra_audit()
    assert audit["rank"] == 2
    assert audit["inverse_coordinates_x_y"] is not None
    assert algebra_audit(clone_detector_polarization=True)["rank"] == 1


def test_record_product_and_poisson_algebra_close() -> None:
    value = build()
    assert value["detector_window_positivity"]["strictly_positive"]
    assert value["record_algebra"]["product_closed"]
    assert value["record_algebra"]["poisson_closed"]
    assert value["record_algebra"]["record_bracket_nonzero"]


def test_scope_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["CG4_QUADRATURES_AND_REDSHIFT_EMBEDDED"]
    assert not flags["FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED"]
    assert not flags["COMPLETE_HARMONIC_SIGNAL_ALGEBRA_CERTIFIED"]
    assert not flags["FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
