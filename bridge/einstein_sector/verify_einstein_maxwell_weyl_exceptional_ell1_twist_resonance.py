"""Independent verifier for the exceptional ell=1 twist-resonance no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows  # noqa: E402


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.schema.json"


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

    theorem = payload["resonance_theorem"]
    source = sp.Matrix([sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}) for value in theorem["complex_positive_positive_source"]])
    witnesses = [
        sp.Matrix([sp.sympify(value) for value in encoded])
        for encoded in theorem["adjoint_witnesses"]
    ]
    rows, symbols = _generic_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = symbols
    names = theorem["source_row_order"]
    matrix = sp.Matrix([rows[name] for name in names]).jacobian([at, mixed, ct, maxwell])
    matrix = matrix.subs({eigenvalue: 6, momentum: 0, frequency: 4 / sp.sqrt(3)}).applyfunc(sp.factor)
    assert matrix.rank() == 2
    assert matrix.row_join(-source).rank() == 3
    assert matrix.T * witnesses[0] == sp.zeros(4, 1)
    assert matrix.T * witnesses[1] == sp.zeros(4, 1)
    assert [sp.factor((witness.T * source)[0]) for witness in witnesses] == [-sp.Rational(2, 3), sp.Rational(4, 3)]
    classification = payload["classification"]
    assert classification["nonzero_twist_exceptional_common_zero_fixture_constructed"] is True
    assert classification["nonzero_adjoint_cokernel_witness_certified"] is True
    assert classification["twist_balanced_fixture_second_order_extendible"] is False


if __name__ == "__main__":
    main()
