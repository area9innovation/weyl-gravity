from __future__ import annotations

import copy
import json

import pytest

from closed_universe_observers.verify_paper09_promotion_after_git_attached_tier3_v3 import (
    RECEIPT,
    verify_value,
)


def value() -> dict:
    return json.loads(RECEIPT.read_text())


def test_no_promotion_verifies() -> None:
    verified = verify_value(value())
    assert verified["promotion_gate"]["decision"] == "NO_PROMOTION"
    assert verified["preserved_scientific_disposition"]["paper09_status"] == "DRAFT_ALLOWED"


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("promotion_gate", "certified"), True),
        (("promotion_gate", "decision"), "THEOREM_FROZEN"),
        (("promotion_gate", "passed_before_first_failure"), 827),
        (("preserved_scientific_disposition", "claim_count"), 23),
        (("preserved_scientific_disposition", "theorem_frozen"), True),
        (("preserved_scientific_disposition", "seven_row_receiver_census_count"), 6),
        (("preserved_scientific_disposition", "both_legacy_rows_no_certified_map"), False),
        (("preserved_scientific_disposition", "operational_frequency_ratio_defined"), True),
        (("preserved_scientific_disposition", "coordinate_ratio_promoted_as_redshift"), True),
        (("preserved_scientific_disposition", "repaired_q70_physical_blocks"), "STABLE"),
        (("flags", "OBSERVER_STREAM_TIER3_GREEN"), True),
        (("flags", "PAPER_MAP_REGENERATED"), True),
        (("flags", "PAPER_PDFS_REBUILT"), True),
        (("flags", "PAPER09_THEOREM_FROZEN"), True),
        (("flags", "SCIENTIFIC_CLAIMS_CHANGED"), True),
        (("next_typed_gate",), "BLIND_HASH_REPIN"),
    ],
)
def test_no_promotion_mutations_fail_closed(path: tuple[str, ...], replacement: object) -> None:
    mutated = copy.deepcopy(value())
    if len(path) == 1:
        mutated[path[0]] = replacement
    else:
        mutated[path[0]][path[1]] = replacement
    with pytest.raises(AssertionError):
        verify_value(mutated)
