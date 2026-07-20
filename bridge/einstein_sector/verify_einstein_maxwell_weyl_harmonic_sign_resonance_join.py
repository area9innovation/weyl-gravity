"""Independent structural verifier for the harmonic sign-resonance join."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_harmonic_sign_resonance_join.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == _sha256(SCHEMA)
    inputs = {}
    for name, record in value["provenance"]["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == _sha256(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert record["result_id"] == payload["result_id"]
        inputs[name] = payload

    assert inputs["sign"]["classification"]["finite_pure_extra_harmonic_sums_negative"]
    assert inputs["finite"]["bounded_obstruction_ledger"]["coefficientwise_common_zero_locus"] == "OPEN"
    assert inputs["k0_complete"]["complete_bounded_zero_locus"]["union_is_necessary_and_sufficient"]
    assert inputs["candidate13"]["classification"]["candidate13_complete_bounded_cone_is_origin"]
    assert inputs["opposite_momentum"]["classification"]["two_nonzero_mixed_qminus_components_survive"]

    obstruction = value["branch_labelled_obstruction_map"]
    assert obstruction["bounded_codomain"] == "stab* direct_sum polynomial_growth direct_sum characteristic_shell"
    assert len(obstruction["stabilizer_block"]) == 5
    assert "iff" in obstruction["bounded_necessity_and_sufficiency"]
    assert "P and R admit finite secular primitives" in obstruction["smooth_restriction"]

    cone = value["maximal_complete_mixed_subcarrier"]
    assert cone["necessity_and_sufficiency"] is True
    upstream_cone = inputs["k0_complete"]["complete_bounded_zero_locus"]
    assert cone["bounded_zero_locus"]["wave_free"] == upstream_cone["static_stratum"]
    assert cone["bounded_zero_locus"]["wave_nonzero"] == upstream_cone["wave_stratum"]
    assert cone["bounded_zero_locus"]["intersection"] == upstream_cone["intersection"]
    flags = value["classification"]
    assert flags["pure_extra_face_is_origin"]
    assert flags["maximal_generic_k0_global_mixed_bounded_cone_classified"]
    assert not flags["exceptional_generic_global_arbitrary_k_common_zero_classified"]
    assert not flags["all_orders_causal_residual_observational_or_quantum_claim"]


if __name__ == "__main__":
    verify()
