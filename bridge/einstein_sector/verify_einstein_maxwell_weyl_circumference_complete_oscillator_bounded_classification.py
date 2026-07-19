"""Independent verifier for the complete circumference oscillator column."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    t, k, c, omega = sp.symbols("t k c omega", real=True, nonzero=True)
    mode = sp.exp(-sp.I * omega * t)
    secular = sp.I * c * k**2 * t * mode / (2 * omega)
    assert sp.simplify(sp.diff(secular, t, 2) + omega**2 * secular - c * k**2 * mode) == 0

    bounded = value["bounded_classification"]
    assert bounded["k_zero"]["status"] == "CERTIFIED"
    assert bounded["k_nonzero"]["status"] == "OBSTRUCTED"
    assert bounded["k_nonzero"]["polynomial_source"] is False
    assert bounded["k_nonzero"]["ledger_location"] == "R_(j,a), not P_(j,r)"
    classification = value["classification"]
    assert classification["circumference_obstruction_is_resonant_not_polynomial"] is True
    assert classification["finite_sum_c_column_zero_locus_classified"] is True
    assert classification["complete_bounded_cone_solved"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
