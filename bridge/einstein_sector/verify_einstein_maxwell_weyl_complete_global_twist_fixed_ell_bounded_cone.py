"""Independent verifier for the acyclic complete fixed-ell global successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(schema_path.read_bytes()).hexdigest()
    assert value["provenance"]["generator_sha256"] == hashlib.sha256((ROOT / value["provenance"]["generator_path"]).read_bytes()).hexdigest()
    inputs = {}
    for name, record in value["provenance"]["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        inputs[name] = json.loads(path.read_text(encoding="utf-8"))
    assert inputs["twist_wave"]["complete_bounded_zero_locus"]["necessity_and_sufficiency"]
    assert inputs["partial_global"]["global_necessity"]["electric_E11_replay"] == "Q_e**2/2"
    assert inputs["circumference"]["classification"]["k0_circumference_cross_bounded_removable"]
    assert inputs["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"]
    assert value["acyclic_dependency_audit"]["successor_is_separate"]
    assert value["acyclic_dependency_audit"]["successor_absent_from_transitive_predecessors"]
    assert value["acyclic_dependency_audit"]["transitive_predecessor_count"] > len(inputs)
    assert value["acyclic_dependency_audit"]["transitive_dependency_edge_count"] > 0
    locus = value["complete_bounded_zero_locus"]
    assert locus["union_is_necessary_and_sufficient"]
    assert "c,d,W_x,A arbitrary" in locus["static_stratum"]
    assert "a=b=d=Q_e=B=0" in locus["wave_stratum"]
    assert "c,W_x,A arbitrary" in locus["wave_stratum"]
    assert not value["classification"]["finite_multi_ell_twist_cone_classified"]
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FIXED_ELL_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
