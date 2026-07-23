"""Exact state-order crosswalk for the final axial 12x12 map."""
from __future__ import annotations

from typing import Any

from .verify_handoff import HandoffError, _require, canonical_sha256
from .verify_microfactor import BLOCK_ORDER


STANDARD_REAL_ORDER = (
    "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
    "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
)
STANDARD_TO_BLOCK_INDEX = tuple(BLOCK_ORDER.index(name) for name in STANDARD_REAL_ORDER)


def permutation_payload() -> dict[str, Any]:
    matrix = [
        ["1/1" if block == STANDARD_TO_BLOCK_INDEX[standard] else "0/1"
         for standard in range(12)]
        for block in range(12)
    ]
    payload = {
        "schema": "phase3-axial-block-standard-state-permutation-v1",
        "block_order": list(BLOCK_ORDER),
        "standard_order": list(STANDARD_REAL_ORDER),
        "standard_to_block_index": list(STANDARD_TO_BLOCK_INDEX),
        "standard_to_block_matrix": matrix,
        "block_to_standard_matrix": [
            [matrix[j][i] for j in range(12)] for i in range(12)
        ],
        "physical_restart": False,
    }
    payload["crosswalk_sha256"] = canonical_sha256(payload)
    return payload


def verify_permutation(data: Any) -> bool:
    expected = permutation_payload()
    _require(data == expected, "state permutation: exact crosswalk drift")
    _require(
        sorted(data["standard_to_block_index"]) == list(range(12)),
        "state permutation: not bijective",
    )
    return True


def permute_affine_block_to_standard(matrix: dict) -> dict:
    """Conjugate a block-ordered endpoint map into standard real state order."""
    permutation = STANDARD_TO_BLOCK_INDEX
    out = {
        key: [
            [matrix[key][permutation[i]][permutation[j]] for j in range(12)]
            for i in range(12)
        ]
        for key in ("center", "linear", "remainder", "hull")
    }
    return out
