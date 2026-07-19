"""Independent verifier for the global axial ell2 all-m bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.schema.json"


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
    promotion = value["SO3_shell_promotion"]
    assert promotion["all_m"] == [-2, -1, 0, 1, 2]
    assert "identity" in promotion["Schur_lemma"]
    cone = value["complete_bounded_cone"]
    assert cone["union_is_necessary_and_sufficient"] is True
    assert "A in R^3" in cone["static_branch"]
    assert "H,J_a density cone" in cone["wave_branch"]
    classification = value["classification"]
    assert classification["all_wave_m_and_both_axial_extra_polarizations_included"] is True
    assert classification["polar_input_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
