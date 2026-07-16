"""Independent verifier for the compact axial master complex."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_AXIAL_MASTER_COMPLEX"
    assert payload["generality_level"] == "G1_AXIAL_ALL_N_ELL_M"
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    matrix = sp.Matrix(
        [
            [momentum**2 + eigenvalue, momentum * frequency, 2, 0],
            [momentum * frequency, frequency**2 - eigenvalue, 0, -2],
            [eigenvalue, 0, momentum**2 + eigenvalue, momentum * frequency],
            [0, -eigenvalue, momentum * frequency, frequency**2 - eigenvalue],
        ]
    )
    expected = sp.factor(
        eigenvalue
        * (eigenvalue - 2)
        * ((frequency**2 - momentum**2 - eigenvalue) ** 2 - 2 * eigenvalue)
    )
    assert sp.expand(matrix.det() - expected) == 0
    gauge = sp.Matrix([-frequency, momentum, frequency, -momentum])
    assert (matrix.subs(eigenvalue, 2) * gauge).applyfunc(sp.simplify) == sp.zeros(4, 1)

    symmetrizer = sp.diag(eigenvalue, 2)
    master = sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]])
    assert symmetrizer * master == master.T * symmetrizer
    assert payload["exact_fourier_equations"]["all_symbolic_remainders"] == "0"
    assert payload["classification"]["all_n_axial_master_complex_ell_ge_2"] is True
    assert payload["classification"]["ell1_periodic_gauge_quotient"] is True
    assert payload["classification"]["covariant_symplectic_matching"] is False
    assert payload["classification"]["polar_master_complex"] is False


if __name__ == "__main__":
    verify_certificate()
