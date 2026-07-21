import copy
import json

import pytest

from closed_universe_observers.verify_observer_tier3_fixed_point_after_legacy_crosswalk_extension_v2 import (
    MANIFEST,
    verify_manifest,
)


def test_obstruction_manifest_verifies_independently():
    verify_manifest(json.loads(MANIFEST.read_text()))


def test_crosswalk_hash_mutation_fails_closed():
    manifest = json.loads(MANIFEST.read_text())
    mutated = copy.deepcopy(manifest)
    mutated["terminal_frontier"]["actual_current_crosswalk_sha256"] = "0" * 64
    with pytest.raises(AssertionError):
        verify_manifest(mutated, check_materialization=False)


def test_cycle_boundary_cannot_be_erased():
    manifest = json.loads(MANIFEST.read_text())
    mutated = copy.deepcopy(manifest)
    mutated["terminal_frontier"]["cycle_boundary"] = "ordinary stale pin"
    with pytest.raises(AssertionError):
        verify_manifest(mutated, check_materialization=False)


def test_obstruction_never_promotes_tier3_or_paper9():
    manifest = json.loads(MANIFEST.read_text())
    mutated = copy.deepcopy(manifest)
    mutated["flags"]["OBSERVER_STREAM_TIER3_GREEN"] = True
    with pytest.raises(AssertionError):
        verify_manifest(mutated, check_materialization=False)
    assert not manifest["flags"]["PAPER_9_FREEZE_GATE_ACTIVATED"]
