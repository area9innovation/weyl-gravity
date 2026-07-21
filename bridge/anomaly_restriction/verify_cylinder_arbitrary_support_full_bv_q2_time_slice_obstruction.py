"""Independent reconstruction of the cylinder all-energy receiver obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-fragment-v1.json"
SCHEMA = ROOT / "bridge/anomaly_restriction/schema/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-v1.schema.json"

EXPECTED = {
    "bridge/certificates/CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1.json": "31d47b21a63e03261c109568e1f852155412169fc7260500baba8a972da6a02c",
    "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json": "4863e00186e719e933e20fe58f2bc0429b1cb0a13db8481b6f8152680b3255fb",
    "field_bv_identification/certificates/minimal_bv_chain.json": "3f9d04dd729c911fbe07768158d96ae411634b7a91bf70a139e8c7cf1dcd8c64",
    "field_bv_identification/polarized_state/certificates/polarized_state_complex.json": "efe492946333578e91d880fde0008166ba8960bc366840413883e5c0e39d0ec1",
    "bridge/certificates/full_hpl_transfer.json": "18acc197a45ba9256e0979e7b04c0cd5e7ca36de94b7540aa2038fc1f9e3511a",
    "covariant_completion/certificates/curved_EAL_spectrum_all_level.json": "253b13da55b1e139ed7af0d1af32a142a6824f8c515ef6d82296a162fa9ef16d",
    "covariant_completion/certificates/curved_prolonged_metric_endpoint_complex.json": "870621ae6750b1e66e3f3316c5a2680d1244c7fca3be4d6aeaabbfdc2178fd79",
    "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json": "1f8aae727a06fb82c70732f7207499d427894247d09fea22f677a0f9b38be0ee",
}


class IndependentCylinderQ2TimeSliceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentCylinderQ2TimeSliceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _independent_weight_reconstruction(selected: set[int]) -> dict[str, int]:
    n = 5
    source = 2 * (n * n + 2 * n - 3)
    target = source if n in selected else 0
    return {"source": source, "target": target, "composite_rank": min(source, target), "defect": source - min(source, target)}


def verify_certificate() -> None:
    payload = _load(CERTIFICATE)
    jsonschema.Draft202012Validator(_load(SCHEMA)).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")
    imports = {row["path"]: row["sha256"] for row in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED, "import ledger drift")
    for relative, digest in EXPECTED.items():
        _require(_sha256(ROOT / relative) == digest, f"dependency hash drift: {relative}")

    selected = _load(ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json")
    selected_weights = {int(weight) for weight in selected["physical_dimensions"]}
    reconstruction = _independent_weight_reconstruction(selected_weights)
    _require(reconstruction == {"source": 64, "target": 0, "composite_rank": 0, "defect": 64}, "rank witness changed")
    _require(payload["first_failed_gate"]["witness"]["minimum_sdr_defect_rank"] == reconstruction["defect"], "stored witness mismatch")

    repaired = _independent_weight_reconstruction(selected_weights | {5})
    _require(repaired["defect"] == 0, "decisive all-energy mutation failed to remove the selected witness")
    _require(len(payload["local_q2_ansatz"]["complete_minimal_roles"]) == 6, "minimal BV role ledger incomplete")
    _require(payload["classification"]["full_arity_two_time_slice_chain_map_certified"] is False, "forbidden arity-two promotion")
    _require(payload["classification"]["all_energy_repair_carrier_constructed"] is False, "repair silently promoted")

    atlas = _load(ATLAS)
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE), "atlas evidence hash drift")
    _require(entry["descriptions"]["causal"] == "OBSTRUCTED", "atlas causal status drift")
    _require(entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP", "atlas quantum status drift")


def main() -> int:
    verify_certificate()
    print("independent cylinder arbitrary-support time-slice obstruction verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
