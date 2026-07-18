"""Independent verifier for the collinear homogeneous/twist theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows  # noqa: E402
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows  # noqa: E402


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.schema.json"


def _fourier_row(expression: sp.Expr, fields: dict[sp.Symbol, sp.Expr], frequency: sp.Symbol, time: sp.Symbol) -> sp.Expr:
    result = sp.S.Zero
    for field, value in fields.items():
        polynomial = sp.Poly(sp.expand(expression).coeff(field), frequency)
        for (degree,), coefficient in polynomial.terms():
            result += coefficient * sp.I**degree * sp.diff(value, time, degree)
    return sp.factor(sp.simplify(result))


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    generator = ROOT / provenance["generator_path"]
    assert provenance["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()

    a, position, velocity, d, time = sp.symbols("a A B d t", real=True)
    local = {"a": a, "A": position, "B": velocity, "d": d, "t": time}
    theorem = payload["theorem"]
    assert theorem["circumference_c_absent_from_complete_source"] is True
    source = theorem["projected_source"]
    correction = theorem["correction"]

    homogeneous_k = sp.sympify(correction["homogeneous_L0_K2"], locals=local)
    assert sp.factor(sp.diff(homogeneous_k, time, 4) / 2 + sp.Rational(16, 3) * velocity**2) == 0

    polar, polar_symbols = _polar_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = polar_symbols
    polar_correction = correction["polar_L2"]
    polar_fields = {
        at: sp.sympify(polar_correction["A_t2"], locals=local),
        mixed: sp.sympify(polar_correction["B2"], locals=local),
        ct: sp.sympify(polar_correction["C_t2"], locals=local),
        maxwell: sp.sympify(polar_correction["U2"], locals=local),
    }
    for name, encoded_source in source["polar_L2"].items():
        image = _fourier_row(polar[name].subs({eigenvalue: 6, momentum: 0}), polar_fields, frequency, time)
        assert sp.factor(image + sp.sympify(encoded_source, locals=local)) == 0

    axial, axial_symbols = _axial_rows()
    axial_correction = correction["axial_L1"]
    axial_fields = {
        axial_symbols["h_t"]: 0,
        axial_symbols["h_x"]: sp.sympify(axial_correction["h_x2"], locals=local),
        axial_symbols["q_t"]: 0,
        axial_symbols["q_x"]: sp.sympify(axial_correction["q_x2"], locals=local),
    }
    for name, encoded_source in source["axial_L1"].items():
        image = _fourier_row(axial[name].subs({axial_symbols["lambda"]: 2, axial_symbols["k"]: 0}), axial_fields, axial_symbols["omega"], time)
        assert sp.factor(image + sp.sympify(encoded_source, locals=local)) == 0

    assert all(value == "0" for value in correction["all_polar_remainders"].values())
    assert all(value == "0" for value in correction["all_axial_remainders"].values())
    classification = payload["classification"]
    assert classification["complete_collinear_standard_homogeneous_twist_common_zero_face_second_order_extendible"] is True
    assert classification["full_SO3_covariant_collinear_cone_classified"] is True
    assert classification["physical_or_extra_ell1_inputs_classified"] is False


if __name__ == "__main__":
    main()
