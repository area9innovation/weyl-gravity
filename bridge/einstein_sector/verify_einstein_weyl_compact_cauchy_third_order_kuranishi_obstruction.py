"""Independent audit of the cubic-class missing-input certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-cauchy-third-order-kuranishi-input-obstruction-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict, files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if files:
        assert payload["schema_sha256"] == sha(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
        for item in payload["provenance"]["inputs"].values():
            path = ROOT / item["path"]
            assert sha(path) == item["sha256"]
            assert json.loads(path.read_text())["result_id"] == item["result_id"]

    # Independently enumerate all signed words of length three in the two frequencies.
    pairs = []
    for a in range(-3, 4):
        for b in range(-3, 4):
            weight = abs(a) + abs(b)
            if (a, b) != (0, 0) and weight <= 3 and (3 - weight) % 2 == 0:
                pairs.append([a, b])
    assert pairs == payload["resonance_closed_carrier"]["third_order_frequency_lattice_pairs"]

    root3 = sp.sqrt(3)
    wm = sp.sqrt(6 - 2 * root3)
    wx = 4 / root3
    found = []
    for a, b in pairs:
        frequency_squared = sp.expand((a * wm + b * wx) ** 2)
        for ell in (2, 4, 6):
            lam = ell * (ell + 1)
            for branch, shell in (
                ("q_minus", lam - sp.sqrt(2 * lam)),
                ("p_extra", sp.Rational(lam) - sp.Rational(2, 3)),
                ("q_plus", lam + sp.sqrt(2 * lam)),
            ):
                if sp.simplify(frequency_squared - shell) == 0:
                    found.append({"frequency_lattice": [a, b], "ell": ell, "branch": branch})
    assert found == payload["resonance_closed_carrier"]["kinematic_shell_resonances"]

    # Independently reconstruct the correction-shift map on the balanced slice.
    tau_e = sp.Rational(48, 5) * (-6 + 5 * root3)
    amplitude2 = sp.Rational(27, 52) * (-6 + 5 * root3)
    amplitude = sp.sqrt(amplitude2)
    l2 = sp.zeros(5, 2)
    l2[0, 0] = 2 * tau_e
    l2[0, 1] = -2 * sp.Rational(832, 45) * amplitude
    assert l2.rank() == 1
    assert payload["balanced_slice_ambiguity"]["matrix_l2_u"] == [
        [str(x) for x in row] for row in l2.tolist()
    ]
    assert payload["balanced_slice_ambiguity"]["rank"] == l2.rank() == 1
    assert payload["balanced_slice_ambiguity"]["quotient_dimension"] == 5 - l2.rank() == 4

    correction = json.loads((ROOT / payload["provenance"]["inputs"]["quadratic_source_and_correction"]["path"]).read_text())
    assert correction["classification"]["complete_second_order_extension_constructed"] is True
    assert "bilinear_source_polynomial" in correction
    assert "third_order" not in correction and "cubic_source" not in correction
    assert payload["classification"]["D3_constraint_tensor_present"] is False
    assert payload["classification"]["mixed_D2_first_second_tensor_present"] is False
    assert payload["classification"]["balanced_cubic_class_evaluated"] is False


def main() -> None:
    verify_payload(json.loads(CERT.read_text()))


if __name__ == "__main__":
    main()
