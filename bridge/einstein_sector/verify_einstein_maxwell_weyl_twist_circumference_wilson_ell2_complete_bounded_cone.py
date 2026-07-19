"""Independent verifier for the c/W_x spectator extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    inputs = {}
    for name, record in provenance["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        inputs[name] = json.loads(path.read_text(encoding="utf-8"))
    assert inputs["circumference"]["classification"]["k0_circumference_cross_bounded_removable"]
    assert inputs["circumference"]["bounded_ledger_consequence"]["surviving_c_face"] == "c remains free on the purely k=0 oscillator carrier"
    assert inputs["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"]
    assert inputs["electric_wilson"]["Wilson_proof"]["mixed_source"] == "D^2 E_barPhi[W_x,(h,f)]=0 for every oscillator"
    assert inputs["global"]["moment_map_intersection"]["complete_bounded_tangent_cone"] == "Z2_global^bounded={(c,d,W_x,A): c,d,W_x real, A in R^3}"
    assert value["complete_bounded_zero_locus"]["twist_velocity"] == "B=0"
    assert value["classification"]["circumference_and_Wilson_are_exact_bounded_spectators"]
    assert value["classification"]["bounded_zero_locus_necessary_and_sufficient"]
    assert value["source_decomposition_proof"]["Wilson_times_wave"] == "CERTIFIED identically zero"
    assert not value["classification"]["radion_circumference_velocity_or_electric_tangents_classified"]
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_TWIST_CIRCUMFERENCE_WILSON_ELL2_COMPLETE_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
