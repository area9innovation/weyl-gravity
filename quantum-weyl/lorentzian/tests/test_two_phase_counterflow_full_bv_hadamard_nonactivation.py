#!/usr/bin/env python3
"""Tests for the counterflow full-BV Hadamard nonactivation disposition."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GEN = ROOT / "quantum-weyl/lorentzian/two_phase_counterflow_full_bv_hadamard_nonactivation.py"
VERIFY = ROOT / "quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_nonactivation.py"
CERT = ROOT / "quantum-weyl/lorentzian/certificates/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-full-bv-hadamard-nonactivation-fragment-v1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_outputs_are_current() -> None:
    generator = load(GEN, "counterflow_hadamard_nonactivation_generator")
    cert, atlas, _ = generator.build()
    assert cert == json.loads(CERT.read_text())
    assert atlas == json.loads(ATLAS.read_text())


def test_independent_verifier() -> None:
    verifier = load(VERIFY, "counterflow_hadamard_nonactivation_verifier")
    verifier.verify(json.loads(CERT.read_text()), json.loads(ATLAS.read_text()))


def test_classical_and_quantum_rows_remain_distinct() -> None:
    cert = json.loads(CERT.read_text())
    assert cert["classical_quantum_boundary"]["classical_causal_parent"] == "CERTIFIED_SELECTED_FIXTURE_ONLY"
    assert cert["full_bv_hadamard_disposition"]["hadamard_two_point_function"] == "NOT_ACTIVATED"
    assert cert["classical_quantum_boundary"]["classical_causal_propagator_is_quantum_state"] is False


def test_downstream_physical_state_is_not_unlocked() -> None:
    cert = json.loads(CERT.read_text())
    assert cert["downstream_activation"] == {
        "interacting_qme": False,
        "particle_interpretation": False,
        "physical_state_positivity": False,
    }
