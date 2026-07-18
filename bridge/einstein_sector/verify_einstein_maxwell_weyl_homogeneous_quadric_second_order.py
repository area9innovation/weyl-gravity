"""Independent verifier for the homogeneous common-zero quadric extension."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_quadric_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in (provenance["engine"], provenance["input"]):
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    a, b, d, charge, t = sp.symbols("a b d Q_e t", real=True)
    local = {"a": a, "b": b, "d": d, "Q_e": charge, "t": t}
    source = sp.Matrix([sp.sympify(value, locals=local) for value in payload["quadratic_source"]["rows"]])
    constraint = a**2 + b**2 - b * d + charge**2
    assert sp.factor(source[0] + constraint / 2) == 0
    assert sp.factor(source[2] + 2 * source[3] + constraint / 2) == 0
    correction = payload["second_order_correction"]
    k2 = sp.sympify(correction["K2"], locals=local)
    u2 = sp.sympify(correction["A_x2"], locals=local)
    image = sp.Matrix([0, 0, sp.diff(k2, t, 4) / 2, -sp.diff(k2, t, 4) / 4, 0, -sp.diff(u2, t, 2)])
    remainder = (image + source).applyfunc(sp.factor)
    assert (
        remainder - sp.Matrix([-constraint / 2, 0, 0, -constraint / 4, 0, 0])
    ).applyfunc(sp.factor) == sp.zeros(6, 1)
    assert payload["classification"]["complete_standard_homogeneous_common_zero_quadric_second_order_extendible"] is True


if __name__ == "__main__":
    main()
