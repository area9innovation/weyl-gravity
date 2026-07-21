import json

from closed_universe_observers import generate_positive_berger_local_receiver_action_preflight as producer
from closed_universe_observers.verify_positive_berger_local_receiver_action_preflight import main as verify


def test_generated_artifacts_are_current():
    payload = producer.build_payload()
    contract = producer.build_contract(payload)
    certificate = producer.build_certificate(payload, contract)
    assert json.loads(producer.PAYLOAD.read_text()) == payload
    assert json.loads(producer.CONTRACT.read_text()) == contract
    assert json.loads(producer.CERTIFICATE.read_text()) == certificate


def test_independent_verifier():
    assert verify() == 0
