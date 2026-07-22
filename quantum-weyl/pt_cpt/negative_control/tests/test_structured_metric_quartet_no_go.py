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


def test_generated_certificate_is_current():
    producer = _load(
        "structured_metric_producer",
        "quantum-weyl/pt_cpt/negative_control/structured_metric_quartet_no_go.py",
    )
    assert json.loads(producer.OUTPUT.read_text()) == producer.build()


def test_independent_exact_verifier():
    verifier = _load(
        "structured_metric_verifier",
        "quantum-weyl/pt_cpt/negative_control/verify_structured_metric_quartet_no_go.py",
    )
    verifier.verify_certificate(json.loads(verifier.CERTIFICATE.read_text()))


def test_nonzero_nilpotent_positive_metric_mutation_is_rejected():
    verifier = _load(
        "structured_metric_verifier_nilpotent",
        "quantum-weyl/pt_cpt/negative_control/verify_structured_metric_quartet_no_go.py",
    )
    certificate = json.loads(verifier.CERTIFICATE.read_text())
    mutant = copy.deepcopy(certificate)
    mutant["nilpotent_positive_metric_no_go"][
        "nontrivial_BRST_positive_self_adjoint_gate_feasible"
    ] = True
    with pytest.raises(Exception):
        verifier.verify_certificate(mutant, verify_hashes=False)


def test_real_spectrum_and_norm_only_mutations_are_rejected():
    verifier = _load(
        "structured_metric_verifier_spectrum",
        "quantum-weyl/pt_cpt/negative_control/verify_structured_metric_quartet_no_go.py",
    )
    certificate = json.loads(verifier.CERTIFICATE.read_text())
    for field, value in (
        ("root_class", "PURELY_IMAGINARY_REAL_SPECTRUM"),
        ("norm_only_rescue_possible", True),
        ("positive_eta_feasible", True),
    ):
        mutant = copy.deepcopy(certificate)
        mutant["selected_counterflow_negative_control"][field] = value
        with pytest.raises(Exception):
            verifier.verify_certificate(mutant, verify_hashes=False)


def test_receipt_hashes_are_exact():
    verifier = _load(
        "structured_metric_verifier_receipt",
        "quantum-weyl/pt_cpt/negative_control/verify_structured_metric_quartet_no_go.py",
    )
    verifier.verify_receipt(
        json.loads(verifier.RECEIPT.read_text()),
        json.loads(verifier.CERTIFICATE.read_text()),
    )
