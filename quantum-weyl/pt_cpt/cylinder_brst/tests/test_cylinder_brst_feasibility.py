import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_outputs_are_current():
    producer = _load(
        "cylinder_brst_producer",
        "quantum-weyl/pt_cpt/cylinder_brst/cylinder_brst_feasibility.py",
    )
    certificate = producer.build()
    assert json.loads(producer.OUTPUT.read_text()) == certificate
    assert json.loads(producer.ATLAS.read_text()) == producer.atlas_fragment(certificate)


def test_independent_exact_verifier():
    verifier = _load(
        "cylinder_brst_verifier",
        "quantum-weyl/pt_cpt/cylinder_brst/verify_cylinder_brst_feasibility.py",
    )
    verifier.verify_certificate(json.loads(verifier.CERTIFICATE.read_text()))


def test_chain_and_rank_mutations_are_rejected():
    verifier = _load(
        "cylinder_brst_verifier_mutations",
        "quantum-weyl/pt_cpt/cylinder_brst/verify_cylinder_brst_feasibility.py",
    )
    original = json.loads(verifier.CERTIFICATE.read_text())
    mutants = []
    chain = copy.deepcopy(original)
    chain["BRST_chain_decision"]["C0_chain_map"] = True
    mutants.append(chain)
    rank = copy.deepcopy(original)
    rank["finite_buffer_regression"]["chiralities"]["-1"]["commutator_ranks"]["Kminus_(-1/2,-1/2)"] = 31
    mutants.append(rank)
    positive = copy.deepcopy(original)
    positive["invariant_commutant_search"]["all_energy_result"] = "POSITIVE_C_EXISTS"
    mutants.append(positive)
    for mutant in mutants:
        with pytest.raises(Exception):
            verifier.verify_certificate(mutant, verify_pins=False)


def test_receipt_hashes_are_exact():
    verifier = _load(
        "cylinder_brst_verifier_receipt",
        "quantum-weyl/pt_cpt/cylinder_brst/verify_cylinder_brst_feasibility.py",
    )
    verifier.verify_receipt(
        json.loads(verifier.RECEIPT.read_text()),
        json.loads(verifier.CERTIFICATE.read_text()),
    )
