import copy
import json

import pytest

from black_hole_programme.phase3.axial_null_infinity_trace_preflight.verify import (
    CERTIFICATE,
    VerificationError,
    verify_document,
)


def document():
    return json.loads(CERTIFICATE.read_text())


def test_certificate_passes():
    verify_document(document())


@pytest.mark.parametrize("mutation", ["matrix", "endpoint", "promotion"])
def test_decisive_mutations_fail(mutation):
    doc = copy.deepcopy(document())
    if mutation == "matrix":
        doc["exact_radial_current"]["matrix_without_pi_alpha"][0][0] = "1"
    elif mutation == "endpoint":
        doc["endpoint_polarizations"]["Iplus_outgoing_rate_minus_2Iomega"][0] = "XI0"
    else:
        doc["claim_flags"]["wavepacket_trace_constructed"] = True
    with pytest.raises(VerificationError):
        verify_document(doc, verify_hashes=False)
