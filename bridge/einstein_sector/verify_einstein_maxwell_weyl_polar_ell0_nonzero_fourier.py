"""Independent verifier for the exceptional polar ell=0 Fourier complex."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.schema.json"


def _matrix(values: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals=symbols) for value in row] for row in values])


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in (provenance["engine"], provenance["input"]):
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    omega, k = sp.symbols("omega k", real=True)
    symbols = {"omega": omega, "k": k}
    raw = _matrix(payload["fourier_complex"]["raw_operator"], symbols)
    action = _matrix(payload["fourier_complex"]["action_Hessian"], symbols)
    gauge = _matrix(payload["fourier_complex"]["gauge_matrix"], symbols)
    assert raw.shape == (6, 6) and action.shape == (6, 6) and gauge.shape == (6, 4)
    assert (raw * gauge).applyfunc(sp.factor) == sp.zeros(6, 4)
    assert (
        action - action.subs({omega: -omega, k: -k}, simultaneous=True).T
    ).applyfunc(sp.factor) == sp.zeros(6)
    metric_vector = sp.Matrix([k**2, 2 * k * omega, omega**2, k**2 - omega**2])
    maxwell_vector = sp.Matrix([k, omega])
    factorized = sp.zeros(6)
    factorized[:4, :4] = metric_vector * metric_vector.T / 2
    factorized[4:, 4:] = maxwell_vector * maxwell_vector.T
    assert (action - factorized).applyfunc(sp.factor) == sp.zeros(6)
    assert sp.factor(gauge[[1, 2, 3, 5], :].det()) == -4 * sp.I * k**3
    assert sp.factor(gauge[[0, 1, 3, 4], :].det()) == 4 * sp.I * omega**3

    static = action.subs(omega, 0)
    static_gauge = gauge.subs(omega, 0)
    assert static.rank() == 2
    assert static_gauge.rank() == 4
    assert static * static_gauge == sp.zeros(6, 4)
    assert len(static.nullspace()) == 4
    assert len(static.T.nullspace()) == 4
    assert sp.Matrix.hstack(*static.nullspace(), *[static_gauge[:, index] for index in range(4)]).rank() == 4

    s_a, s_t = sp.symbols("S_A S_T")
    correction = sp.Matrix([s_a / k**4, 0, 0, s_a / k**4, s_t / k**2, 0])
    source = sp.Matrix([s_a, 0, 0, s_a, s_t, 0])
    assert (static * correction - source).applyfunc(sp.factor) == sp.zeros(6, 1)

    classification = payload["classification"]
    assert classification["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"] is True
    assert classification["static_L0_K2k_exceptional_block_classified"] is True
    assert classification["static_phase_sensitive_source_removable_if_Noether_compatible"] is True
    assert classification["bounded_resonant_projection_classified"] is False


if __name__ == "__main__":
    main()
