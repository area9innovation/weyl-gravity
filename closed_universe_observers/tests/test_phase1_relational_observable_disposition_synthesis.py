import copy
import json

import pytest

from closed_universe_observers import generate_phase1_relational_observable_disposition_synthesis as producer
from closed_universe_observers.verify_phase1_relational_observable_disposition_synthesis import main as verify_main, verify


def test_artifacts_are_current():
    payload = producer.build_payload()
    certificate = producer.build_certificate(payload)
    assert json.loads(producer.PAYLOAD.read_text()) == payload
    assert json.loads(producer.CERT.read_text()) == certificate
    assert json.loads(producer.PAPER_DISPOSITION.read_text()) == producer.paper_disposition(payload)


def test_independent_replay():
    assert verify_main() == 0


def test_stale_redshift_promotion_mutation_is_rejected():
    cert = json.loads(producer.CERT.read_text())
    payload = copy.deepcopy(json.loads(producer.PAYLOAD.read_text()))
    payload["claim_crosswalk"][4]["redshift"] = "CERTIFIED"
    payload["claim_crosswalk"][4]["coordinate_ratio_promoted"] = True
    with pytest.raises(AssertionError):
        verify(cert, payload)


def test_local_cocycle_equals_observable_mutation_is_rejected():
    cert = json.loads(producer.CERT.read_text())
    payload = copy.deepcopy(json.loads(producer.PAYLOAD.read_text()))
    payload["claim_crosswalk"][1]["does_not_establish"].remove("observable")
    payload["claim_crosswalk"][4]["status"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        verify(cert, payload)
