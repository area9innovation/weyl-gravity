#!/usr/bin/env python3
"""Independent verifier for the generic axial Weyl--Maxwell operator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_operator.schema.json"


def _expression(value: str, symbols: dict[str, sp.Symbol]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=symbols)


def _matrix(rows: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    return sp.Matrix([[_expression(value, symbols) for value in row] for row in rows])


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for relative_path, digest in payload["provenance"]["inputs"].items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == digest

    lam, momentum, frequency = sp.symbols("lam k omega", real=True)
    symbols = {"lam": lam, "k": momentum, "omega": frequency, "I": sp.I}
    operator = payload["operator_algebra"]
    hessian = _matrix(operator["gauge_fixed_Hessian_operator"], symbols)
    adjoint = hessian.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    assert _zero(hessian - adjoint)
    extra = frequency**2 - momentum**2 - lam + sp.Rational(2, 3)
    einstein = (frequency**2 - momentum**2 - lam) ** 2 - 2 * lam
    expected_determinant = sp.factor(lam**3 * (lam - 2) * 9 * extra**2 * einstein / 16)
    assert sp.factor(hessian.det() - expected_determinant) == 0
    assert operator["Smith_invariant_factors_over_F_omega"] == [
        "1",
        "1",
        "-(3*k**2 + 3*lambda - 3*omega**2 - 2)/3",
        "-(3*k**2 + 3*lambda - 3*omega**2 - 2)*(k**4 + 2*k**2*lambda - 2*k**2*omega**2 + lambda**2 - 2*lambda*omega**2 - 2*lambda + omega**4)/3",
    ]

    noether = payload["ungauged_Noether_lift"]
    gauge = _matrix(noether["Fourier_gauge_map"], symbols)
    ungauged = _matrix(noether["ungauged_Hessian_operator"], symbols)
    gauge_adjoint = gauge.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    ungauged_adjoint = ungauged.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    assert _zero(ungauged * gauge)
    assert _zero(gauge_adjoint * ungauged)
    assert _zero(ungauged - ungauged_adjoint)
    assert payload["source_and_extra_modules"]["canonical_extra_quotient_away_from_resultant"] == "Q_extra_ax=(F[omega]/(p))^2"
    assert payload["rails"]["off_shell_local_Green_current_verified"] is False
    assert payload["classification"]["extra_particle_certified"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR independent verification: PASS")
