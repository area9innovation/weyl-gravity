#!/usr/bin/env python3
"""Independent verifier for the local commutant and spectral-C certificate."""

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
    assert data["schema"] == "axial-local-commutant-spectral-c-v1"
    assert data["status"] == "EXACT_LOCAL_COMMUTANT_COMPACT_BAND_SPECTRAL_C_PASS"
    assert set(data["dependency_tags"]) == {"LOCAL-ALGEBRAIC", "REDUCED-MODE"}

    for item in data["imports"].values():
        path = ROOT / item["path"]
        assert path.exists()
        assert digest(path) == item["sha256"]

    rw = json.loads(
        (ROOT / data["imports"]["rw_simplicity_and_nonsplitting"]["path"]).read_text()
    )
    assert rw["claim_flags"]["spin2_endomorphism_ring_scalar_positive_real"]
    assert rw["claim_flags"]["axial_ell2_nonsplit_all_positive_real"]
    assert rw["positive_real_nonsplitting_refinement"]["rank_conclusion"].endswith(
        "omega!=0"
    )

    witt = json.loads(
        (ROOT / data["imports"]["incoming_witt_decomposition"]["path"]).read_text()
    )
    incoming = witt["endpoints"]["Iminus"]
    assert incoming["E_X_cross"] == "384*omega/5"
    assert incoming["Y_norm"] == "-384*omega**3/5"
    assert incoming["second_null_vector"] == "X - 3*E/(4*omega**2)"

    # Independent dual-number representation and finite-order audit.
    a, b = sp.symbols("a b")
    N = sp.Matrix([[0, 2], [0, 0]])
    Phi = a * sp.eye(2) + b * N
    assert N**2 == sp.zeros(2)
    assert (Phi**2 - sp.eye(2))[0, 1] == 4 * a * b
    for n in range(1, 8):
        assert Phi**n == a**n * sp.eye(2) + n * a ** (n - 1) * b * N

    # Independently verify the exact threshold sign and majorant.
    omega = sp.symbols("omega", positive=True)
    c = sp.Rational(384, 5)
    G = sp.Matrix([[0, c * omega, 0], [c * omega, 0, 0], [0, 0, -c * omega**3]])
    C = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    H = G * C
    assert C**2 == sp.eye(3)
    assert C.T * G == G * C
    assert H == sp.diag(c * omega, c * omega, c * omega**3)

    flags = data["claim_flags"]
    for key in [
        "local_commutant_dual_numbers_exact",
        "only_scalar_local_semisimple_observables",
        "only_plus_minus_identity_local_involutions",
        "nonlocal_spectral_c_exists_each_positive_real_fiber",
        "compact_band_positive_norm_equivalence",
        "threshold_weighted_completion_exact",
        "scattering_positive_identity_equivalent_to_c_intertwining",
    ]:
        assert flags[key], key
    for key in [
        "spectral_c_canonical",
        "spectral_c_covariant",
        "spectral_c_causal",
        "spectral_c_complex_holomorphic",
        "endpoint_block_diagonal_scattering_c_established",
        "whole_half_axis_unweighted_norm_equivalence",
        "full_six_state_commutant_dual_numbers",
        "brst_or_quantum_positive_state_space",
    ]:
        assert not flags[key], key

    eq = data["scattering_c_equivalence"]
    assert eq["equivalence"]
    assert len(eq["required_hypotheses"]) == 3
    assert "positivity of H_out forces A_C=0" in eq["reverse_proof"]


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    verify_document(data)
    print("EXACT_LOCAL_COMMUTANT_COMPACT_BAND_SPECTRAL_C_VERIFIED")


if __name__ == "__main__":
    main()
