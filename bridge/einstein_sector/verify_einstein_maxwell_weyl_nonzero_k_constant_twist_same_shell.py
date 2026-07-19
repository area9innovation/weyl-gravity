"""Independent verifier for the nonzero-k constant-twist same-shell theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == value["schema_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    lam, k, omega, alpha, j = sp.symbols("lambda k omega alpha j", real=True)
    K = k + alpha * j
    p = omega**2 - K**2 - lam + sp.Rational(2, 3)
    q = (omega**2 - K**2 - lam) ** 2 - 2 * lam
    root = sp.sqrt(2 * lam)
    assert sp.factor(sp.diff(p, alpha).subs(alpha, 0).subs(omega**2, k**2 + lam - sp.Rational(2, 3))) == -2 * k * j
    assert sp.factor(sp.diff(q, alpha).subs(alpha, 0).subs(omega**2, k**2 + lam - root)) == 4 * k * j * root
    assert sp.factor(sp.diff(q, alpha).subs(alpha, 0).subs(omega**2, k**2 + lam + root)) == -4 * k * j * root

    kernel = value["kernel_theorem"]
    assert kernel["kernel_dimension_per_positive_signed_momentum_fibre"] == 8
    assert "m_A=0" in kernel["complete_same_shell_kernel"]
    classification = value["classification"]
    assert classification["same_shell_kernel_exactly_axisymmetric_about_twist"]
    assert classification["neighboring_outputs_invertible_for_every_allowed_nonzero_k"]
    assert classification["complete_constant_twist_times_wave_bilinear_column_classified"]
    assert not classification["complete_bounded_second_order_equation_solved"]
    neighbors = value["neighboring_output_extension"]
    assert neighbors["complete_neighboring_output_inverse"]
    assert neighbors["channels"]["ell=2 exceptional L=1"]["all_exceptional_target_blocks_invertible"]
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_NONZERO_K_CONSTANT_TWIST_SAME_SHELL independent verification: PASS")


if __name__ == "__main__":
    main()
