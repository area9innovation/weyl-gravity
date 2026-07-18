import json
from fractions import Fraction

from closed_universe_observers.generate_berger_adaptive_peter_weyl_route_preflight import (
    CERTIFICATE,
    build,
    minimum_dimension,
    unweighted_mutation_capacity,
    weighted_capacity,
)


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_two_j138_is_a_necessary_capacity_rail():
    value = build()
    energy = Fraction(value["capacity_convention"]["profile_energy_lower"])
    assert weighted_capacity(138) < Fraction(99, 100) * energy <= weighted_capacity(139)


def test_missing_multiplicity_mutation_changes_cutoff():
    value = build()
    energy = Fraction(value["capacity_convention"]["profile_energy_lower"])
    assert minimum_dimension(energy, unweighted_mutation_capacity) != 139


def test_route_remains_fail_closed():
    flags = build()["flags"]
    assert flags["STREAMED_ADAPTIVE_PETER_WEYL_ROUTE_SELECTED"] is True
    assert flags["TWO_J138_CONVERGENCE_CERTIFIED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
