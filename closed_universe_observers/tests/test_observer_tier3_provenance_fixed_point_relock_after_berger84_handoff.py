import copy
import json

import pytest

from closed_universe_observers.verify_observer_tier3_provenance_fixed_point_relock_after_berger84_handoff import (
    MANIFEST,
    verify_manifest,
)


def test_shortfall_manifest_verifies_independently():
    verify_manifest(json.loads(MANIFEST.read_text()))


def test_mutated_final_hash_fails_closed():
    manifest = json.loads(MANIFEST.read_text())
    mutated = copy.deepcopy(manifest)
    mutated["relocks"][0]["new_sha256"] = "0" * 64
    with pytest.raises(AssertionError):
        verify_manifest(mutated)


def test_shortfall_never_promotes_tier3_or_paper9():
    manifest = json.loads(MANIFEST.read_text())
    flags = manifest["flags"]
    assert manifest["disposition"] == "SHORTFALL"
    assert not flags["OBSERVER_STREAM_TIER3_GREEN"]
    assert not flags["PAPER_9_FREEZE_GATE_ACTIVATED"]

