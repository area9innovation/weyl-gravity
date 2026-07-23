import copy
import json

import pytest

from black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify import (
    CERTIFICATE,
    VerificationError,
    verify_document,
)
from black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify_supersessions import (
    SHORTFALLS,
    SupersessionError,
    verify_superseded_shortfall,
)


def document():
    return json.loads(CERTIFICATE.read_text())


def test_certificate_passes():
    verify_document(document())


def test_superseded_shortfalls_are_fail_closed():
    for path in SHORTFALLS:
        payload = json.loads(path.read_text())
        verify_superseded_shortfall(payload)
        mutated = copy.deepcopy(payload)
        mutated["claim_flags"]["conservation_identity_established"] = True
        with pytest.raises(SupersessionError):
            verify_superseded_shortfall(mutated)


@pytest.mark.parametrize(
    "mutation",
    [
        "matrix",
        "degree_bound",
        "sample",
        "drop_30th",
        "use_29_nodes",
        "delete_minus_factor",
        "delete_plus_factor",
        "promotion",
    ],
)
def test_decisive_mutations_fail(mutation):
    payload = copy.deepcopy(document())
    reconstruction = payload["literal_current_reconstruction"]
    if mutation == "matrix":
        reconstruction["matrix_without_pi_alpha"][0][0] = "1"
    elif mutation == "degree_bound":
        reconstruction["maximum_numerator_r_degree"] = 24
    elif mutation == "sample":
        reconstruction["sample_radii"][0]["literal_matrix_sha256"] = "0" * 64
    elif mutation == "drop_30th":
        reconstruction["sample_radii"].pop()
        reconstruction["sample_count"] = 29
    elif mutation == "use_29_nodes":
        reconstruction["sample_radii"] = reconstruction["sample_radii"][:29]
        reconstruction["sample_count"] = 29
    elif mutation == "delete_minus_factor":
        del reconstruction["denominator_exponents"]["omega_r_minus_2I"]
    elif mutation == "delete_plus_factor":
        del reconstruction["denominator_exponents"]["omega_r_plus_2I"]
    else:
        payload["claim_flags"]["global_connection_constructed"] = True
    with pytest.raises(VerificationError):
        verify_document(payload, verify_hashes=False)
