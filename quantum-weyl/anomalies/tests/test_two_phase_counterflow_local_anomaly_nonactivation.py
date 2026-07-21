from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_outputs_are_current() -> None:
    generator = load("counterflow_nonactivation_generator", "quantum-weyl/anomalies/two_phase_counterflow_local_anomaly_nonactivation.py")
    cert, atlas, materiality, _ = generator.build()
    assert json.loads(generator.CERT.read_text()) == cert
    assert json.loads(generator.ATLAS.read_text()) == atlas
    assert json.loads(generator.MATERIALITY.read_text()) == materiality


def test_independent_verifier_accepts_current_outputs() -> None:
    verifier = load("counterflow_nonactivation_verifier", "quantum-weyl/anomalies/verify_two_phase_counterflow_local_anomaly_nonactivation.py")
    verifier.verify(json.loads(verifier.CERT.read_text()), json.loads(verifier.ATLAS.read_text()), json.loads(verifier.MATERIALITY.read_text()))


def test_quantum_rows_are_not_activated() -> None:
    cert = json.loads((ROOT / "quantum-weyl/anomalies/certificates/TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1.json").read_text())
    assert set(cert["local_anomaly_disposition"].values()) <= {"NOT_COMPUTED", "NOT_ACTIVATED", "NOT_DECLARED_BECAUSE_COMPUTATION_NOT_ACTIVATED"}
    assert cert["strict_weyl_import"]["C2_coefficient"] is None
