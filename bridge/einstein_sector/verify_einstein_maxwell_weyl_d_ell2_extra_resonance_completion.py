#!/usr/bin/env python3
"""Independent operator replay for the complete d-cross resonance theorem."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator


CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.schema.json"


def parse_matrix(values: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}) for value in row] for row in values])


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    operator, (eigenvalue, momentum, frequency) = _action_operator()
    hessian = operator.subs({eigenvalue: 6, momentum: 0, frequency: 4 / sp.sqrt(3)}).applyfunc(sp.factor)
    stored_hessian = parse_matrix(value["polar_theorem"]["action_hessian"])
    if hessian != stored_hessian or hessian.rank() != 2:
        raise AssertionError("polar p-shell Hessian replay failed")
    witnesses = parse_matrix(value["polar_theorem"]["adjoint_basis"])
    sources = parse_matrix(value["polar_theorem"]["source_columns_e1_e2"])
    pairing = (witnesses.T * sources).applyfunc(sp.factor)
    if hessian.T * witnesses != sp.zeros(4, 2):
        raise AssertionError("stored adjoint basis is incomplete")
    if pairing != sp.diag(-6 * sp.sqrt(3) * sp.I, 552 * sp.sqrt(3) * sp.I):
        raise AssertionError("polar pairing replay failed")
    if sp.factor(pairing.det()) != 9936 or 832 * 9936 != 8266752:
        raise AssertionError("parity-completion determinant failed")
    print("EINSTEIN_MAXWELL_WEYL_D_ELL2_EXTRA_RESONANCE_COMPLETION independent verification: PASS")


if __name__ == "__main__":
    main()
