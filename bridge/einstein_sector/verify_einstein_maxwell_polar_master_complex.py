"""Independent verifier for the arbitrary-harmonic polar master theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str, symbols: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=symbols)


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX"
    assert payload["generality_level"] == "G2_POLAR_ALL_N_ELL_M_ELL_GE2"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    eigenvalue, momentum, frequency, mass = sp.symbols(
        "lambda k omega s", real=True
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
    symbols = {
        "lam": eigenvalue,
        "k": momentum,
        "omega": frequency,
        "I": sp.I,
    }
    stored = sp.Matrix(
        [
            [_parse(value, symbols) for value in row]
            for row in payload["algebraic_and_singular_audit"]["coefficient_matrix"]
        ]
    )
    assert (stored - matrix).applyfunc(sp.simplify) == sp.zeros(8, 5)

    singular_minor = sp.factor(matrix[[0, 1, 2, 6, 7], :].det())
    at_s_zero = sp.factor(singular_minor.subs(frequency**2, momentum**2))
    assert at_s_zero == eigenvalue**3 * (eigenvalue - 2) / 8
    for value in (6, 12, 20):
        assert at_s_zero.subs(eigenvalue, value) != 0

    K, U = sp.symbols("K U")
    wave_mass = frequency**2 - momentum**2
    radial = K - 2 * U
    reconstructed = sp.Matrix(
        [
            -(frequency**2 + momentum**2) * radial / wave_mass,
            2 * momentum * frequency * radial / wave_mass,
            -(frequency**2 + momentum**2) * radial / wave_mass,
            K,
            U,
        ]
    )
    equations = (matrix * reconstructed).applyfunc(sp.factor)
    first_master = K * (wave_mass - eigenvalue) + 2 * eigenvalue * U
    second_master = K + U * (wave_mass - eigenvalue)
    assert sp.simplify(equations[0] - momentum**2 * first_master / wave_mass) == 0
    assert sp.simplify(equations[1] + momentum * frequency * first_master / wave_mass) == 0
    assert sp.simplify(equations[2] - frequency**2 * first_master / wave_mass) == 0
    assert all(sp.simplify(equations[index]) == 0 for index in (3, 4, 6))
    assert sp.simplify(equations[5] - second_master) == 0
    assert sp.simplify(equations[7] - second_master) == 0

    master = sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]])
    characteristic = sp.factor((mass * sp.eye(2) - master).det())
    assert sp.expand(characteristic - ((mass - eigenvalue) ** 2 - 2 * eigenvalue)) == 0
    symmetrizer = sp.diag(1, 2 * eigenvalue)
    assert symmetrizer * master == master.T * symmetrizer
    assert sp.simplify(eigenvalue - sp.sqrt(2 * eigenvalue)).subs(eigenvalue, 6) > 0

    derivative_t, derivative_x = sp.symbols("d_t d_x")
    gauge_fixing_map = sp.Matrix(
        [[2, 0, 0], [derivative_t, 1, 0], [derivative_x, 0, 1]]
    )
    assert gauge_fixing_map.det() == 2
    assert sp.factor(eigenvalue * (eigenvalue - 2) / 2).subs(eigenvalue, 6) != 0

    tensor = payload["exact_tensor_identity"]
    assert [row["column"] for row in tensor["column_checks"]] == [
        "A",
        "B",
        "C",
        "K",
        "U",
    ]
    assert all(
        row["Einstein_component_remainders"] == "0"
        and row["Maxwell_density_remainders"] == "0"
        for row in tensor["column_checks"]
    )
    assert tensor["all_unlisted_tensor_components"] == "0"

    classification = payload["classification"]
    assert classification["arbitrary_lambda_full_tensor_identity"] is True
    assert classification["all_n_ell_ge2_m_polar_master_complex"] is True
    assert classification["ell_ge2_gauge_complete"] is True
    assert classification["s_zero_locus_complete"] is True
    assert classification["ell0_ell1_complete"] is False
    assert classification["covariant_symplectic_matching"] is False
    assert classification["full_polar_including_exceptions"] is False


if __name__ == "__main__":
    verify_certificate()
