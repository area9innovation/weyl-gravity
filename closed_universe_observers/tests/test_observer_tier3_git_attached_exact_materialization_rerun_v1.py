from __future__ import annotations

import copy
import json

import pytest

from closed_universe_observers.verify_observer_tier3_git_attached_exact_materialization_rerun_v1 import (
    RECEIPT,
    verify_value,
)


def value() -> dict:
    return json.loads(RECEIPT.read_text())


def test_git_attached_first_frontier_verifies() -> None:
    verified = verify_value(value())
    assert verified["disposition"]["status"] == "OBSTRUCTED"
    assert verified["flags"]["AUTHORITATIVE_RUN_GREEN"] is False
    assert verified["flags"]["STALE_COMPARISON_LEDGER_PIN"] is True


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("materialization", "kind"), "DETACHED_ARCHIVE"),
        (("materialization", "repo_prefix_from_scope"), ""),
        (("materialization", "blob_hash_mismatch_count"), 1),
        (("resource_preflight", "status"), "FAIL"),
        (("authoritative_run", "run_count"), 2),
        (("authoritative_run", "prior_partial_passes_credited"), True),
        (("authoritative_run", "passed_before_first_failure"), 827),
        (("first_failure", "classification"), "SCIENTIFIC_CONTRADICTION"),
        (("first_failure", "ledger_pinned_artifact_sha256"), "1adce4fe647af299c68382a9761020dc11aa9d746a6f4e897dd4a91089a862db"),
        (("first_failure", "actual_claim_boundary_sha256_at_selected_commit"), "785149617ad60326a9af75b4b62eadcbd5e8bddaa30f8a6c6344beceb62b2a55"),
        (("first_failure", "claim_boundary_drift"), False),
        (("first_failure", "scientific_contradiction"), True),
        (("flags", "AUTHORITATIVE_RUN_GREEN"), True),
        (("flags", "PAPER9_THEOREM_FROZEN"), True),
        (("disposition", "smallest_successor"), "BLIND_HASH_REPIN"),
    ],
)
def test_git_attached_frontier_mutations_fail_closed(path: tuple[str, str], replacement: object) -> None:
    mutated = copy.deepcopy(value())
    mutated[path[0]][path[1]] = replacement
    with pytest.raises(AssertionError):
        verify_value(mutated)
