"""Independent verifier for the finite-harmonic k0 combined cone theorem."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    assert payload["provenance"]["generator_sha256"] == hashlib.sha256((ROOT / payload["provenance"]["generator_path"]).read_bytes()).hexdigest()
    imported = {}
    for name, record in payload["provenance"]["inputs"].items():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        imported[name] = json.loads(path.read_text())
    assert imported["fixed_ell_cone"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"] is True
    assert imported["generic_cross_ell"]["classification"]["all_nonzero_generic_output_channels_off_target_shells"] is True
    assert imported["exceptional_L1"]["classification"]["no_zero_frequency_collision"] is True
    assert imported["exceptional_L1"]["classification"]["complete_unbounded_cross_ell_nonzero_output_nonresonance"] is True
    classification = payload["classification"]
    assert classification["all_finite_cross_ell_superpositions_classified"] is True
    assert classification["complete_common_stabilizer_zero_cone_second_order_extendible"] is True
    assert classification["cross_ell_source_coefficients_required_for_existence"] is False
    assert classification["infinite_harmonic_completion_classified"] is False
    assert classification["opposite_momentum_phases_classified"] is False


if __name__ == "__main__":
    main()
