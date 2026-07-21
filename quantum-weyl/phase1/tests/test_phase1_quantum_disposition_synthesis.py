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
    generator = load("phase1_quantum_generator", "quantum-weyl/phase1/generate_phase1_quantum_disposition_synthesis.py")
    cert, atlas, materiality, _ = generator.build()
    assert json.loads(generator.CERT.read_text()) == cert
    assert json.loads(generator.ATLAS.read_text()) == atlas
    assert json.loads(generator.MATERIALITY.read_text()) == materiality


def test_independent_verifier_accepts_current_outputs() -> None:
    verifier = load("phase1_quantum_verifier", "quantum-weyl/phase1/verify_phase1_quantum_disposition_synthesis.py")
    verifier.verify(
        json.loads(verifier.CERT.read_text()),
        json.loads(verifier.ATLAS.read_text()),
        json.loads(verifier.MATERIALITY.read_text()),
    )


def test_no_quantum_successor_is_selected() -> None:
    cert = json.loads((ROOT / "quantum-weyl/phase1/certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json").read_text())
    assert cert["phase1_decision"]["phase2_quantum_candidate_selected"] is False
    counterflow = next(row for row in cert["theory_rows"] if row["id"] == "TWO_PHASE_COUNTERFLOW_SUCCESSOR")
    assert set(counterflow["quantum_promotions"].values()) == {"NOT_ACTIVATED"}
