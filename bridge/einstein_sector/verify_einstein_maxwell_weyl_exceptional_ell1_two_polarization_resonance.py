"""Independent verifier for the axisymmetric exceptional two-polarization no-go."""

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


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    theorem = payload["resonance_theorem"]
    local = {"I": sp.I, "sqrt": sp.sqrt}
    polar_source = sp.Matrix([sp.sympify(value, locals=local) for value in theorem["polar_self_source"]])
    axial_source = sp.Matrix([sp.sympify(value, locals=local) for value in theorem["axial_polar_cross_source"]])
    polar_rows, polar_symbols = _polar_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = polar_symbols
    polar_names = ["metric_00", "metric_01", "metric_11", "sphere_trace", "metric_0a", "metric_1a", "sphere_tracefree", "maxwell_axial_density"]
    polar_matrix = sp.Matrix([polar_rows[name] for name in polar_names]).jacobian([at, mixed, ct, maxwell])
    polar_matrix = polar_matrix.subs({eigenvalue: 6, momentum: 0, frequency: 4 / sp.sqrt(3)})
    polar_witnesses = [
        sp.Matrix([sp.Rational(3, 16), 0, sp.Rational(3, 16), 0, 0, 0, 1, 0]),
        sp.Matrix([sp.Rational(1, 72), 0, sp.Rational(1, 8), 0, 0, 0, 0, 1]),
    ]
    assert polar_matrix.T * polar_witnesses[0] == sp.zeros(4, 1)
    assert polar_matrix.T * polar_witnesses[1] == sp.zeros(4, 1)
    assert [sp.factor((witness.T * polar_source)[0]) for witness in polar_witnesses] == [sp.Rational(1, 8), -sp.Rational(1, 4)]

    axial_rows, axial_symbols = _axial_rows()
    axial_names = ["metric_t", "metric_x", "metric_angular", "maxwell_t", "maxwell_x", "maxwell_angular"]
    axial_matrix = sp.Matrix([axial_rows[name] for name in axial_names]).jacobian([axial_symbols["h_t"], axial_symbols["h_x"], axial_symbols["q_t"], axial_symbols["q_x"]])
    axial_matrix = axial_matrix.subs({axial_symbols["lambda"]: 6, axial_symbols["k"]: 0, axial_symbols["omega"]: 4 / sp.sqrt(3)})
    axial_witness = sp.Matrix([sp.sympify(value, locals=local) for value in theorem["axial_cross_adjoint_witness"]])
    assert axial_matrix.T * axial_witness == sp.zeros(4, 1)
    assert sp.factor((axial_witness.T * axial_source)[0]) == -8 * sp.sqrt(3) / 9

    classification = payload["classification"]
    assert classification["self_pairing_vectors_can_formally_cancel"] is True
    assert classification["cross_channel_blocks_every_nonzero_two_polarization_cancellation"] is True
    assert classification["complete_axisymmetric_exceptional_ell1_two_polarization_cone_second_order_obstructed"] is True
    assert classification["all_m_exceptional_cone_classified"] is False


if __name__ == "__main__":
    main()
