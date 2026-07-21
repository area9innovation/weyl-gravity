"""Independent coordinate verifier for the compact symplectic extension theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-symplectic-extension-classification-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(rows: list[list[str]], local: dict[str, Any] | None = None) -> sp.Matrix:
    names = {"lam": sp.Symbol("lambda", real=True), "k": sp.Symbol("k", real=True)}
    if local:
        names.update(local)
    return sp.Matrix([[sp.sympify(value.replace("lambda", "lam"), locals=names) for value in row] for row in rows])


def verify_payload(payload: dict[str, Any], *, verify_files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if verify_files:
        assert payload["schema_sha256"] == _sha256(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
        for imported in payload["provenance"]["inputs"].values():
            path = ROOT / imported["path"]
            assert imported["sha256"] == _sha256(path)
            assert imported["result_id"] == json.loads(path.read_text())["result_id"]

    lam = sp.Symbol("lambda", real=True)
    expected = {
        "axial": (sp.diag(lam, 2), sp.Matrix([[1, 3], [sp.Rational(3, 2) * lam, 1]]), sp.diag(1296, sp.Rational(208, 3))),
        "polar": (sp.Matrix([[1, -2], [-2, 2 * lam]]), sp.Matrix([[1, -3 * lam], [-sp.Rational(3, 2), 1]]), sp.diag(22464, 12288)),
    }
    for parity, (source, relative, extra) in expected.items():
        block = payload["generic_parity_blocks"][parity]
        image = source * relative
        assert _matrix(block["source_positive_frequency_Gram"]) == source
        assert _matrix(block["relative_operator_R"]) == relative
        assert _matrix(block["target_image_Gram"]) == image
        assert sp.factor(source.det().subs(lam, 6)) > 0 and source[0, 0].subs(lam, 6) > 0
        assert sp.factor(image.det().subs(lam, 6)) < 0
        fixture_image = image.subs(lam, 6)
        shear = _matrix(block["sign_flip_shear_A"])
        cross = fixture_image * shear
        raw = extra + shear.T * fixture_image * shear
        assert _matrix(block["sheared_cross_block"]) == cross
        assert _matrix(block["sheared_raw_extra_Gram"]) == raw
        assert raw[0, 0] < 0
        assert raw - cross.T * fixture_image.inv() * cross == extra
        assert _matrix(block["sheared_Schur_complement"]) == extra

    # Independent symbolic shear identity with unconstrained entries.
    e1, e2, c1, c2, x1, x2, a, b, c, d = sp.symbols("e1 e2 c1 c2 x1 x2 a b c d", nonzero=True)
    ge = sp.diag(e1, e2)
    cross0 = sp.diag(c1, c2)
    gx = sp.diag(x1, x2)
    shear = sp.Matrix([[a, b], [c, d]])
    cross1 = cross0 + ge * shear
    gx1 = gx + shear.T * ge * shear + shear.T * cross0 + cross0.T * shear
    assert sp.simplify(gx1 - cross1.T * ge.inv() * cross1 - (gx - cross0.T * ge.inv() * cross0)) == sp.zeros(2)

    endpoints = {row["scope"]: row for row in payload["endpoint_table"]}
    assert endpoints["exceptional ell=1 axial and polar"]["corrected_solution_identification"].startswith("AVAILABLE")
    assert "det(S)=-2" in endpoints["twist ell=1, k=0 per real SO(3) component"]["corrected_solution_identification"]
    assert payload["classification"]["target_internal_orthogonal_split"] is True
    assert payload["classification"]["admissible_corrected_parity_complete_cyclic_split"] is False
    assert payload["extension_classification"]["final_residual"].startswith("NO_CERTIFIED_MAP")


def verify_certificate() -> None:
    verify_payload(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    verify_certificate()
