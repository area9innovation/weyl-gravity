"""Independent verifier for the compact polar master preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_preflight.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_POLAR_MASTER_PREFLIGHT"
    assert payload["generality_level"] == "G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    eigenvalue, momentum, frequency, mass = sp.symbols(
        "lambda k omega s", nonzero=True, real=True
    )
    matrix = sp.Matrix(
        [
            [0, 0, eigenvalue / 2, momentum**2 + eigenvalue / 2, -eigenvalue],
            [0, eigenvalue / 2, 0, -momentum * frequency, 0],
            [eigenvalue / 2, 0, 0, frequency**2 - eigenvalue / 2, eigenvalue],
            [0, sp.I * momentum / 2, sp.I * frequency / 2, sp.I * frequency / 2, -sp.I * frequency],
            [sp.I * momentum / 2, sp.I * frequency / 2, 0, -sp.I * momentum / 2, sp.I * momentum],
            [(momentum**2 + eigenvalue / 2) / 2, momentum * frequency, (frequency**2 - eigenvalue / 2) / 2, (frequency**2 - momentum**2 + 2) / 2, -eigenvalue],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 0, 0],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, frequency**2 - momentum**2 - eigenvalue],
        ]
    )
    stored = sp.Matrix(
        [
            [
                sp.sympify(
                    value.replace("lambda", "lam"),
                    locals={
                        "lam": eigenvalue,
                        "k": momentum,
                        "omega": frequency,
                        "I": sp.I,
                    },
                )
                for value in row
            ]
            for row in payload["algebraic_master_reduction"]["coefficient_matrix"]
        ]
    )
    assert (stored - matrix).applyfunc(sp.simplify) == sp.zeros(8, 5)

    K, U = sp.symbols("K U")
    wave_mass = frequency**2 - momentum**2
    radial = K - 2 * U
    reconstruction = sp.Matrix(
        [
            -(frequency**2 + momentum**2) * radial / wave_mass,
            2 * momentum * frequency * radial / wave_mass,
            -(frequency**2 + momentum**2) * radial / wave_mass,
            K,
            U,
        ]
    )
    reduced = (matrix * reconstruction).applyfunc(sp.factor)
    first_master = K * (wave_mass - eigenvalue) + 2 * eigenvalue * U
    second_master = K + U * (wave_mass - eigenvalue)
    assert sp.simplify(reduced[0] - momentum**2 * first_master / wave_mass) == 0
    assert sp.simplify(reduced[1] + momentum * frequency * first_master / wave_mass) == 0
    assert sp.simplify(reduced[2] - frequency**2 * first_master / wave_mass) == 0
    assert all(sp.simplify(reduced[index]) == 0 for index in (3, 4, 6))
    assert sp.simplify(reduced[5] - second_master) == 0
    assert sp.simplify(reduced[7] - second_master) == 0

    master = sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]])
    characteristic = sp.factor((mass * sp.eye(2) - master).det())
    assert sp.expand(characteristic - ((mass - eigenvalue) ** 2 - 2 * eigenvalue)) == 0
    symmetrizer = sp.diag(1, 2 * eigenvalue)
    assert symmetrizer * master == master.T * symmetrizer

    fixture = payload["exact_tensor_fixture"]
    assert fixture["Einstein_residual"] == "0"
    assert fixture["Maxwell_density_residual"] == "0"
    assert "0<theta<pi" in fixture["chart_convention"]
    classification = payload["classification"]
    assert classification["generic_polar_matrix"] is True
    assert classification["exact_l2_plus_tensor_solution"] is True
    assert classification["all_ell_arbitrary_lambda_tensor_derivation"] is False
    assert classification["ell0_ell1_complete"] is False
    assert classification["covariant_symplectic_matching"] is False
    assert classification["full_polar_master_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
