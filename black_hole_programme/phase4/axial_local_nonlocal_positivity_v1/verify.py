#!/usr/bin/env python3
"""Independent verifier for the local/nonlocal positivity certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(data: dict) -> None:
    assert data["schema"] == "axial-local-nonlocal-positivity-v1"
    assert data["status"] == "EXACT_LOCAL_NONLOCAL_POSITIVITY_DICHOTOMY_PASS"
    for item in data["imports"].values():
        path = ROOT / item["path"]
        assert digest(path) == item["sha256"]

    comm = json.loads((ROOT / data["imports"]["commutant_and_spectral_c"]["path"]).read_text())
    assert comm["claim_flags"]["local_commutant_dual_numbers_exact"]
    assert comm["claim_flags"]["threshold_weighted_completion_exact"]

    a, b, g = sp.symbols("a b g", real=True, nonzero=True)
    G = sp.Matrix([[0, g], [g, 0]])
    eta = sp.Matrix([[a, b], [0, a]])
    assert sp.factor((G * eta).det()) == -a**2 * g**2

    J = sp.diag(1, -1)
    M = sp.Matrix([[1, 1], [0, 1]])
    transported = M.inv() * J * M
    assert transported != transported.T

    flags = data["claim_flags"]
    for key in [
        "no_local_positive_metric_operator_even_without_involution",
        "combined_future_compatible_c_exists",
        "threshold_ir_variables_exact",
        "unique_nilpotent_residue_direction",
        "complex_reducibility_quarter_lattice_confinement",
    ]:
        assert flags[key], key
    for key in [
        "channel_factorized_c_automatic",
        "matrix_sign_canonical_under_general_frames",
        "whole_axis_positive_scattering_bounded",
        "mass_bach_local_equality_implies_global_jost_derivative",
        "mass_bach_local_equality_implies_qnm_slope",
        "complete_complex_reducibility_classification",
        "quantum_statement",
    ]:
        assert not flags[key], key
    assert data["complex_reducibility_confinement"]["status"] == "CONFINEMENT_ONLY_NOT_COMPLETE_CLASSIFICATION"


def main() -> None:
    verify_document(json.loads((HERE / "certificate.json").read_text()))
    print("EXACT_LOCAL_NONLOCAL_POSITIVITY_DICHOTOMY_VERIFIED")


if __name__ == "__main__":
    main()
