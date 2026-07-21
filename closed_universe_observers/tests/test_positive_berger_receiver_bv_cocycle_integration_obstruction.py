import json

from closed_universe_observers import generate_positive_berger_receiver_bv_cocycle_integration_obstruction as producer
from closed_universe_observers.verify_positive_berger_receiver_bv_cocycle_integration_obstruction import main as verify


def test_generated_artifacts_are_current():
    payload = producer.build_payload()
    certificate = producer.build_certificate(payload)
    assert json.loads(producer.PAYLOAD.read_text()) == payload
    assert json.loads(producer.CERT.read_text()) == certificate


def test_independent_grading_audit():
    assert verify() == 0
