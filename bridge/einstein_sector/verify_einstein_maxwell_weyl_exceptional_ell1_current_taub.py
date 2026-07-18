"""Independent verifier for the exceptional ell=1 current/Taub theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import _generic_current_matrix  # noqa: E402
from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import _time_current_matrix  # noqa: E402


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_current_taub.schema.json"


def _weight(matrix: sp.Matrix, representative: sp.Matrix, frequency: sp.Expr) -> sp.Expr:
    return sp.factor((representative.T * matrix * representative)[0] / (-sp.I * frequency))


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

    eigenvalue, momentum, first, second = sp.symbols("lambda k omega_1 omega_2", real=True)
    extra_frequency = sp.sqrt(sp.Rational(4, 3))
    standard_frequency = sp.Integer(2)
    axial = _generic_current_matrix(eigenvalue, momentum, first, second).subs({eigenvalue: 2, momentum: 0})
    axial_extra = sp.Matrix([0, 1, 0, -3])
    axial_standard = sp.Matrix([0, 1, 0, 1])
    assert _weight(axial.subs({first: extra_frequency, second: extra_frequency}), axial_extra, extra_frequency) == 16
    assert _weight(axial.subs({first: standard_frequency, second: standard_frequency}), axial_standard, standard_frequency) == 16
    assert sp.factor((axial_extra.T * axial.subs({first: extra_frequency, second: standard_frequency}) * axial_standard)[0]) == 0

    polar, symbols = _time_current_matrix()
    polar = (polar / 2).subs({symbols["lambda"]: 2, symbols["k"]: 0})
    polar_extra = sp.Matrix([0, 1, 0, 0])
    polar_standard = sp.Matrix([1, 0, 1, 0])
    assert _weight(polar.subs({symbols["omega_1"]: extra_frequency, symbols["omega_2"]: extra_frequency}), polar_extra, extra_frequency) == 3
    assert _weight(polar.subs({symbols["omega_1"]: standard_frequency, symbols["omega_2"]: standard_frequency}), polar_standard, standard_frequency) == 1
    assert sp.factor((polar_extra.T * polar.subs({symbols["omega_1"]: extra_frequency, symbols["omega_2"]: standard_frequency}) * polar_standard)[0]) == 0

    theorem = payload["current_theorem"]
    assert theorem["normalized_extra_Hermitian_current_Gram"] == [["16", "0"], ["0", "3"]]
    assert theorem["extra_positive_frequency_inertia"] == [2, 0]
    classification = payload["classification"]
    assert classification["pure_exceptional_ell1_nonzero_tangents_second_order_obstructed"] is True
    assert classification["isolated_physical_plus_exceptional_ell1_common_zero_is_origin"] is True
    assert classification["mixed_balance_with_opposite_sign_sector_classified"] is False


if __name__ == "__main__":
    main()
