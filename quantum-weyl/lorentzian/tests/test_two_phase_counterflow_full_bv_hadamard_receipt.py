import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "hadamard_receipt_verifier",
    ROOT / "quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_receipt.py",
)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def receipt():
    return json.loads(VERIFIER.RECEIPT.read_text())


def test_committed_blob_replay():
    VERIFIER.verify(receipt())


def test_hash_mutation_rejected():
    mutated = copy.deepcopy(receipt())
    mutated["output_hashes"]["atlas"] = "f" * 64
    with pytest.raises(AssertionError):
        VERIFIER.verify(mutated)
