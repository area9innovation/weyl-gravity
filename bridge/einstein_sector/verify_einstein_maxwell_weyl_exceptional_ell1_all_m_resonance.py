"""Independent verifier for the all-m exceptional ell=1 resonance no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.schema.json"


def _stf(matrix: sp.Matrix) -> sp.Matrix:
    return (matrix - sp.trace(matrix) * sp.eye(3) / 3).applyfunc(sp.expand)


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    a_symbols = sp.symbols("a0:3")
    q_symbols = sp.symbols("q0:3")
    axial = sp.Matrix(a_symbols)
    polar = sp.Matrix(q_symbols)
    even = _stf(axial * axial.T - polar * polar.T)
    cross = _stf(axial * polar.T + polar * axial.T)
    equations = []
    for tensor in (even, cross):
        equations.extend([tensor[0, 0], tensor[1, 1], tensor[0, 1], tensor[0, 2], tensor[1, 2]])
    basis = sp.groebner(equations, *(a_symbols + q_symbols), order="grevlex")
    expressions = [sp.factor(polynomial.as_expr()) for polynomial in basis.polys]
    assert basis.is_zero_dimensional
    required = [
        q_symbols[2] ** 5,
        a_symbols[2] ** 3 - 3 * a_symbols[2] * q_symbols[2] ** 2,
        q_symbols[0] ** 3 - 3 * q_symbols[0] * q_symbols[2] ** 2,
        q_symbols[1] ** 3 - 3 * q_symbols[1] * q_symbols[2] ** 2,
        a_symbols[0] ** 2 - a_symbols[2] ** 2 - q_symbols[0] ** 2 + q_symbols[2] ** 2,
        a_symbols[1] ** 2 - a_symbols[2] ** 2 - q_symbols[1] ** 2 + q_symbols[2] ** 2,
    ]
    assert all(
        any(sp.factor(candidate - witness) == 0 for candidate in expressions)
        for witness in required
    )
    classification = payload["classification"]
    assert classification["distinct_m_interference_classified"] is True
    assert classification["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"] is True
    assert classification["same_frequency_nonexceptional_cancellation_classified"] is False


if __name__ == "__main__":
    main()
