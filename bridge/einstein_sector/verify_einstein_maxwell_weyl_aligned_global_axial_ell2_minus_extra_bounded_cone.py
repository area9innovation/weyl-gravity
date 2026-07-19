"""Independent verifier for the aligned global-wave bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    generator = ROOT / provenance["generator_path"]
    assert provenance["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    root = sp.sqrt(3)
    tau_minus = sp.Rational(48, 5) * (-6 + 5 * root)
    assert tau_minus > 0
    x1, x2 = sp.symbols("x1 x2", nonnegative=True)
    xminus = (972 * x1 + 52 * x2) / (27 * (-6 + 5 * root))
    remainder = sp.factor(tau_minus * xminus - sp.Rational(1728, 5) * x1 - sp.Rational(832, 45) * x2)
    assert remainder == 0
    cone = value["complete_bounded_cone"]
    assert cone["union_is_necessary_and_sufficient"] is True
    assert "Q_e=B_z=0" in cone["static_branch"]
    assert "a=b=d=Q_e=B_z=0" in cone["wave_branch"]
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    assert value["classification"]["polar_or_all_m_input_classified"] is False


if __name__ == "__main__":
    main()
