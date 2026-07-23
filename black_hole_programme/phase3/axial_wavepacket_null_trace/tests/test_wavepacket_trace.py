import copy
import json
from pathlib import Path

import pytest

from black_hole_programme.phase3.axial_wavepacket_null_trace.produce import build_document
from black_hole_programme.phase3.axial_wavepacket_null_trace.verify import verify_document


HERE = Path(__file__).resolve().parents[1]


def test_certificate_reproduces():
    assert build_document() == json.loads((HERE / "certificate.json").read_text())


def test_independent_verifier():
    verify_document(json.loads((HERE / "certificate.json").read_text()))


def test_false_wavepacket_promotion_rejected():
    document = build_document()
    document["claim_flags"]["wavepacket_trace_constructed"] = True
    with pytest.raises(SystemExit):
        verify_document(document)


def test_endpoint_swap_rejected():
    document = build_document()
    document["matching_direction_formal_trace"]["Iminus"]["basis"] = ["XI2", "XI3", "EI2"]
    with pytest.raises(SystemExit):
        verify_document(document)
