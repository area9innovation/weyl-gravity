import copy
import json

import pytest

from closed_universe_observers import generate_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation as producer
from closed_universe_observers.verify_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation import main as verify_main, verify


def inputs():
    cert = json.loads(producer.CERT.read_text())
    payload = json.loads(producer.PAYLOAD.read_text())
    health = json.loads(producer.HEALTH.read_text())
    hp = json.loads(producer.HEALTH_PAYLOAD.read_text())
    return cert, payload, health, hp


def test_artifacts_are_current():
    payload = producer.build_payload()
    certificate = producer.build_certificate(payload)
    assert json.loads(producer.PAYLOAD.read_text()) == payload
    assert json.loads(producer.CERT.read_text()) == certificate


def test_independent_replay():
    assert verify_main() == 0


def test_unstable_block_as_healthy_receiver_mutation_is_rejected():
    cert, payload, health, hp = inputs()
    mutated = copy.deepcopy(hp)
    mutated["certified_block_ledger"][0]["unrestricted_status"] = "CERTIFIED_HEALTHY"
    with pytest.raises(AssertionError):
        verify(cert, payload, health, mutated)


def test_unknown_higher_j_as_receiver_mutation_is_rejected():
    cert, payload, health, hp = inputs()
    mutated = copy.deepcopy(health)
    mutated["remaining_carrier"]["physical_quotient_status"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        verify(cert, payload, mutated, hp)


def test_coordinate_ratio_promotion_mutation_is_rejected():
    cert, payload, health, hp = inputs()
    mutated = copy.deepcopy(payload)
    mutated["frequency_ratio_partial_function"]["coordinate_ratio_promoted"] = True
    mutated["frequency_ratio_partial_function"]["redshift"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        verify(cert, mutated, health, hp)
