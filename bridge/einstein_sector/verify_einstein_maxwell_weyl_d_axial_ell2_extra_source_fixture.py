"""Independent reduced-form verifier for d-times-axial-extra source fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture.schema.json"
CERTIFICATES = {
    "e1": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e1_source_fixture.json",
    "e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e2_source_fixture.json",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CERTIFICATES), required=True)
    arguments = parser.parse_args()
    payload = json.loads(CERTIFICATES[arguments.case].read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    assert provenance["tensor_helper_sha256"] == hashlib.sha256((ROOT / provenance["tensor_helper_path"]).read_bytes()).hexdigest()

    omega = 4 / sp.sqrt(3)
    representatives = {
        "e1": (-6, 0, 6, 0),
        "e2": (0, -sp.Rational(2, 3), 0, 6),
    }
    h_time, h_space, _q_time, q_space = representatives[arguments.case]
    # Independently reduced d-cross formulas obtained by varying the
    # one-dimensional axial action rows before substituting the p shell.
    reduced = [
        9 * sp.I * omega * h_time,
        sp.Rational(3, 2) * sp.I * omega * h_space,
        0,
        -sp.I * omega * q_space / 2,
    ]
    expected = [sp.factor(value) for value in reduced]
    locals_ = {"I": sp.I, "sqrt": sp.sqrt}
    stored = [sp.sympify(value, locals=locals_) for value in payload["bilinear_source_rows"]]
    assert [sp.factor(stored[index] - expected[index]) for index in range(4)] == [0] * 4
    assert payload["action_row_order"] == ["6*metric_t", "-6*metric_x", "maxwell_t", "maxwell_x"]


if __name__ == "__main__":
    main()
