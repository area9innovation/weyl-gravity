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
    verify_document(json.loads((HERE / "certificate.json").read_text()), deep=False)


def test_suppressed_wavepacket_result_rejected():
    document = build_document()
    document["claim_flags"]["wavepacket_trace_constructed"] = False
    with pytest.raises(SystemExit):
        verify_document(document, deep=False)


def test_false_flux_gram_promotion_rejected():
    document = build_document()
    document["claim_flags"]["endpoint_flux_Gram_certified"] = True
    with pytest.raises(SystemExit):
        verify_document(document, deep=False)


def test_endpoint_swap_rejected():
    document = build_document()
    document["matching_direction_wavepacket_trace"]["Iminus"]["basis"] = ["XI2", "XI3", "EI2"]
    with pytest.raises(SystemExit):
        verify_document(document, deep=False)
