from __future__ import annotations

import copy

import pytest

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.point_carrier_factor_artifact import (
    build_payload,
    verify_carrier_factor,
)
from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_handoff import (
    HandoffError,
    canonical_sha256,
)


ZERO_BITS = "0000000000000000"
ONE_BITS = "3ff0000000000000"


def _identity_payload() -> dict:
    center = [
        ["1/1" if i == j else "0/1" for j in range(8)]
        for i in range(8)
    ]
    linear = [["0/1" for _ in range(8)] for _ in range(8)]
    remainder = [
        [[ZERO_BITS, ZERO_BITS] for _ in range(8)] for _ in range(8)
    ]
    hull = [
        [
            [ONE_BITS, ONE_BITS] if i == j
            else [ZERO_BITS, ZERO_BITS]
            for j in range(8)
        ]
        for i in range(8)
    ]
    return build_payload(
        0,
        {
            "center": center,
            "linear": linear,
            "remainder": remainder,
            "hull": hull,
        },
        child=None,
        split=1,
        trace_id=400_000,
        width="0.0",
        source_kind="complete-block-lower",
        source_sha256="0" * 64,
        log_sha256="1" * 64,
    )


def test_point_carrier_factor_accepts_exact_identity() -> None:
    assert verify_carrier_factor(_identity_payload())


def test_point_factor_rejects_nonzero_frequency_linear_mutation() -> None:
    mutated = copy.deepcopy(_identity_payload())
    mutated["matrix"]["linear"][0][0] = "1/2"
    unhashed = dict(mutated)
    unhashed.pop("payload_sha256")
    mutated["payload_sha256"] = canonical_sha256(unhashed)
    with pytest.raises(HandoffError):
        verify_carrier_factor(mutated)
