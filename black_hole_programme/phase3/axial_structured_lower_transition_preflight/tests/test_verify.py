import copy
import json
from pathlib import Path

import pytest

from black_hole_programme.phase3.axial_structured_lower_transition_preflight.verify import (
    VerificationError,
    verify_certificate,
    verify_source,
)


HERE = Path(__file__).resolve().parents[1]


def inputs():
    return (
        json.loads((HERE / "certificate.json").read_text()),
        (HERE / "actual_fixture.forge").read_text(),
        json.loads((HERE / "source_metadata.json").read_text()),
    )


def test_certificate_and_source_pass():
    assert verify_certificate(*inputs())


@pytest.mark.parametrize(
    "old,new",
    [
        (
            "let rl:IvAffineResult=ivam_add_checked(lg.value,lk.value);",
            "let rl:IvAffineResult=ivam_add_checked(lg.value,lg.value);",
        ),
        (
            "let lg:IvAffineResult=ivam_mul_checked(g,oldc);",
            "let lg:IvAffineResult=ivam_mul_checked(oldc,g);",
        ),
        ("ivam_pad_remainder(sl,tl)", "ivam_pad_remainder(sl,0.0)"),
        ("u.generator!=7315", "u.generator!=7316"),
    ],
)
def test_source_mutations_are_rejected(old, new):
    _, source, metadata = inputs()
    assert old in source
    with pytest.raises(VerificationError):
        verify_source(source.replace(old, new, 1), metadata)


def test_fabricated_full_rank_claim_is_rejected():
    cert, source, metadata = inputs()
    cert = copy.deepcopy(cert)
    cert["first_microfactor"]["full_12x12_interval_rank_used"] = True
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata)


def test_dropped_claim_boundary_is_rejected():
    cert, source, metadata = inputs()
    cert = copy.deepcopy(cert)
    cert["does_not_establish"] = []
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata)
