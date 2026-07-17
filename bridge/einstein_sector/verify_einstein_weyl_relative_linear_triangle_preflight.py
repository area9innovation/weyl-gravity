"""Independent structural verifier for the relative linear preflight."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_relative_linear_triangle_preflight.schema.json"


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["principal_mapping_cofiber"]["nonnull_fixture"]["cohomology_dimensions"] == [0, 0, 0, 0, 0]
    assert payload["principal_mapping_cofiber"]["null_fixture"]["cohomology_dimensions"] == [0, 0, 4, 4, 0]
    assert payload["generic_axial_offshell_triangle"]["denominators"] == ["1", "2", "4"]
    assert "k" in payload["generic_axial_offshell_triangle"]["does_not_invert"]
    assert payload["global_curved_cofiber_gate"]["strict_short_exact_sequence"] is False
    assert payload["classification"]["full_curved_chain_map_obstructed"] is False
    assert payload["classification"]["relative_linear_triangle_V1_certified"] is False

    eigenvalue, momentum, frequency = sp.symbols("lambda k omega")
    source = sp.Matrix([
        [momentum**2 + eigenvalue, momentum * frequency, 2, 0],
        [momentum * frequency, frequency**2 - eigenvalue, 0, -2],
        [eigenvalue, 0, momentum**2 + eigenvalue, momentum * frequency],
        [0, -eigenvalue, momentum * frequency, frequency**2 - eigenvalue],
    ])
    row_map = sp.Matrix([
        [
            -eigenvalue * (3 * momentum**2 + 3 * eigenvalue - 3 * frequency**2 - 2) / 4,
            0,
            3 * (eigenvalue - frequency**2) / 2,
            3 * momentum * frequency / 2,
        ],
        [
            0,
            -eigenvalue * (3 * momentum**2 + 3 * eigenvalue - 3 * frequency**2 - 2) / 4,
            -3 * momentum * frequency / 2,
            3 * (momentum**2 + eigenvalue) / 2,
        ],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    displayed = sp.Matrix([
        [sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue, "k": momentum, "omega": frequency}) for value in row]
        for row in payload["generic_axial_offshell_triangle"]["reduced_equation_map"]
    ])
    assert (displayed - row_map).applyfunc(sp.factor) == sp.zeros(4)
    assert sp.factor((row_map * source).det()) == sp.factor(row_map.det() * source.det())
    assert payload["generic_axial_offshell_triangle"]["degreewise_map_ranks"] == [2, 6, 4, 0]
    assert payload["generic_axial_offshell_triangle"]["degreewise_injective"] is False


if __name__ == "__main__":
    verify_certificate()
