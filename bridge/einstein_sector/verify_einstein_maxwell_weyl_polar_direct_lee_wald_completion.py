"""Independent verifier for the direct generic polar Lee--Wald completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-polar-direct-lee-wald-completion-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expr(value, local) for value in row] for row in values])


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def verify_payload(payload: dict[str, Any], *, verify_files: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    if verify_files:
        assert payload["schema_sha256"] == _sha256(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
        for record in payload["provenance"]["inputs"].values():
            assert record["sha256"] == _sha256(ROOT / record["path"])

    l, k, w1, w2 = sp.symbols("lambda k omega_1 omega_2", real=True)
    local = {"lam": l, "k": k, "omega_1": w1, "omega_2": w2, "omega_e": sp.symbols("omega_e", positive=True, real=True), "omega_E": sp.symbols("omega_E", real=True), "mu": sp.symbols("mu", real=True), "I": sp.I, "pi": sp.pi}
    generic = _matrix(payload["direct_current"]["generic_direct_current_per_scalar_harmonic_norm"], local)
    expected = sp.Matrix([
        [0, -sp.I*k*(k**2+l)/2, -sp.I*(2*k**2-l)*(w1+w2)/8, 0],
        [-sp.I*k*(k**2+l)/2, -sp.I*(4*k**2+3*l)*(w1+w2)/4, sp.I*k*(l-w1**2-w1*w2-w2**2)/2, 0],
        [-sp.I*(2*k**2-l)*(w1+w2)/8, sp.I*k*(l-w1**2-w1*w2-w2**2)/2, sp.I*(w1+w2)*(2*l-w1**2-w2**2)/4, 0],
        [0, 0, 0, -sp.I*l*(w1+w2)],
    ])
    assert _zero(generic-expected)
    for sample in payload["direct_current"]["samples"]:
        ell = sample["ell"]
        direct = _matrix(sample["direct_integrated_matrix"], local)
        assert _zero(direct - 4*sp.pi/(2*ell+1)*expected.subs(l, ell*(ell+1)))
    assert payload["direct_current"]["spectral_promotion"]["nodes"] == [6, 12, 20]

    witness = payload["delta_nabla_C"]
    nabla_delta = _expr(witness["nabla_delta_C_contribution"], local)
    connection = _expr(witness["delta_connection_on_background_C_contribution"], local)
    complete = _expr(witness["complete_delta_nabla_C_contribution"], local)
    assert sp.factor(nabla_delta+connection-complete) == 0
    assert sp.factor(complete.subs(k, 1) + 7*sp.I*sp.pi/5) == 0
    assert _expr(witness["omission_mutation_remainder_at_k_1"], local) == -7*sp.I*sp.pi/5
    assert witness["retained"] is True

    comparator = _matrix(payload["reduced_gate_comparison"]["remainder"], local)
    assert comparator == sp.zeros(4)
    assert payload["reduced_gate_comparison"]["role"].startswith("post-production comparator")

    gram = _matrix(payload["shell_pullback"]["extra_Hermitian_Gram"], local)
    determinant = 9*l**2*(l-2)*(9*l-2)*(3*k**2+3*l-2)*(6*k**2+3*l-2)**2
    assert sp.factor(gram.det()-determinant) == 0
    assert payload["shell_pullback"]["extra_Gram_determinant"] == str(determinant)
    assert payload["shell_pullback"]["Einstein_extra_cross_block_remainder"] == ["0", "0"]
    assert payload["shell_pullback"]["extra_inertia"] == [2, 0]
    assert payload["shell_pullback"]["complete_polar_inertia"] == [3, 1]
    assert payload["shell_pullback"]["normalization"] == "Omega_WM/(-i*omega_e*L*N_(ell,m))"
    assert payload["shell_pullback"]["physical_collision_locus"].startswith("empty")
    assert payload["parity_comparison"]["axial_extra_inertia"] == [2, 0]
    assert payload["parity_comparison"]["polar_extra_inertia"] == [2, 0]
    assert payload["controls"]["Maxwell_UU_entry"] == "-I*lambda*(omega_1 + omega_2)"
    assert payload["classification"]["final_residual_descent_certified"] is False
    assert payload["classification"]["causal_or_particle_claim"] is False
    assert payload["classification"]["quantum_positivity_or_unitarity_claim"] is False


def verify_certificate() -> None:
    verify_payload(json.loads(CERTIFICATE.read_text(encoding="utf-8")))


if __name__ == "__main__":
    verify_certificate()
