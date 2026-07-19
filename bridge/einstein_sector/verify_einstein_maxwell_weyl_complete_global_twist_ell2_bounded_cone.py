"""Independent verifier for the complete global/twist ell=2 bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == _sha256(SCHEMA)

    provenance = value["provenance"]
    generator = ROOT / provenance["generator_path"]
    assert provenance["generator_sha256"] == _sha256(generator)
    records = {}
    for name, record in provenance["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == _sha256(path)
        records[name] = json.loads(path.read_text(encoding="utf-8"))

    assert records["d_cone"]["classification"]["bounded_stratified_zero_locus_necessary_and_sufficient"]
    assert records["axial_minus"]["bounded_zero_locus"]["ideal_on_wave_amplitude_z"] == "<b*z,a*z,d*z>"
    assert (
        records["polar_minus"]["bounded_zero_locus"]["full_polynomial_ideal_on_wave_amplitude_z"]
        == "<b*z,a*z,d*z>"
    )

    a, b, d, charge, time = sp.symbols("a b d Q_e t", real=True)
    source = records["homogeneous_source"]["quadratic_source"]
    rows = [
        sp.sympify(text, locals={"a": a, "b": b, "d": d, "Q_e": charge, "t": time})
        for text in source["rows"]
    ]
    pure_electric = sp.Matrix([rows[index] for index in (0, 2, 3, 5)]).subs({a: 0, b: 0, d: 0})
    assert pure_electric == charge**2 * sp.Matrix(
        [-sp.Rational(1, 2), sp.Rational(1, 2), -sp.Rational(1, 2), 0]
    )
    zero_operator = sp.Matrix(
        [
            [sp.sympify(text, locals={"Omega": 0, "I": sp.I}) for text in row]
            for row in records["homogeneous_operator"]["homogeneous_operator"]["matrix"]
        ]
    )
    assert zero_operator == sp.zeros(4, 3)
    scalar_descent = records["wave_cone"]["obstruction_descent"]["scalar_L0"]
    assert "(1,0,1/2,0)" in scalar_descent
    assert pure_electric[1] == charge**2 / 2
    assert records["electric_transport"]["classification"]["Q_e_times_every_oscillator_bounded_removable"]

    cone = value["complete_bounded_zero_locus"]
    assert cone["union_is_necessary_and_sufficient"] is True
    assert "a=b=Q_e=B=0" in cone["static_stratum"]
    assert "a=b=d=Q_e=B=0" in cone["wave_stratum"]
    classification = value["classification"]
    assert classification["radion_and_electric_gates_independently_closed"] is True
    assert classification["older_partial_global_ell2_row_superseded"] is True
    assert classification["other_ell_or_nonzero_momentum_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_ELL2_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
