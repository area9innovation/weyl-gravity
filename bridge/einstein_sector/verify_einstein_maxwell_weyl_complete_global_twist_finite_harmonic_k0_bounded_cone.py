"""Independent verifier for the complete finite-harmonic global/twist cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(schema_path.read_bytes()).hexdigest()
    generator = ROOT / value["provenance"]["generator_path"]
    assert value["provenance"]["generator_sha256"] == hashlib.sha256(generator.read_bytes()).hexdigest()
    inputs = {}
    for name, record in value["provenance"]["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        inputs[name] = json.loads(path.read_text(encoding="utf-8"))
    assert inputs["finite_wave"]["classification"]["complete_common_stabilizer_zero_cone_second_order_extendible"]
    assert inputs["twist_wave"]["classification"]["every_fixed_ell_neighbor_output_invertible"]
    assert inputs["partial_global"]["global_wave_separation"]["consequence"] == "every nonzero bounded wave branch forces a=b=d=0"
    proof = value["finite_additivity_proof"]
    assert proof["mixed_source_identity"] == "D2E[A,sum_ell u_ell]=sum_ell D2E[A,u_ell]"
    assert "linearity of L" in proof["overlapping_output_channels"]
    assert proof["moment_map_independence"].startswith("the A-wave mixed inverse is available coefficientwise")
    locus = value["complete_bounded_zero_locus"]
    assert locus["union_is_necessary_and_sufficient"]
    assert "c,d,W_x,A arbitrary" in locus["static_stratum"]
    assert "a=b=d=Q_e=B=0" in locus["wave_stratum"]
    assert "total mu_H=mu_J1=mu_J2=mu_J3=0" in locus["wave_stratum"]
    classification = value["classification"]
    assert classification["finite_multi_ell_constant_twist_column_classified"]
    assert classification["constant_twist_position_free_on_finite_wave_stratum"]
    assert not classification["infinite_harmonic_completion_classified"]
    assert not classification["nonzero_momentum_classified"]
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FINITE_HARMONIC_K0_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
