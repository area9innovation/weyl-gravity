"""Independent claim-boundary verifier for the v5 chunking shortfall."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
CERTIFICATE = HERE / "certificate.json"
ADAPTER = HERE / "validated_global_connection.forge"


class VerifyError(RuntimeError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _import_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else PHYSICS / path


def verify_data(data: dict, adapter_text: str | None = None) -> bool:
    if data.get("schema") != "phase3-black-hole-axial-global-connection-matrix-v5-v1":
        raise VerifyError("schema mismatch")
    if data.get("result_token") != "BH_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5":
        raise VerifyError("result token mismatch")
    if data.get("stop_condition_disposition") != "SHORTFALL":
        raise VerifyError("terminal disposition was silently promoted")
    declaration = data["declaration"]
    if list(map(Fraction, declaration["target_frequency_cover"])) != [
        Fraction(1, 2), Fraction(3, 4)
    ]:
        raise VerifyError("target frequency cover changed")
    if list(map(Fraction, declaration["tested_required_cell"])) != [
        Fraction(1, 2), Fraction(129, 256)
    ]:
        raise VerifyError("tested cell changed")
    for item in data["imports"].values():
        path = _import_path(item["path"])
        if not path.exists() or digest(path) != item["sha256"]:
            raise VerifyError(f"import drift: {path}")

    gate = data["table_backed_runtime_gate"]
    if gate["forge_commit"] != "f2ab419230f03003580d885735e029ce2deed71e":
        raise VerifyError("table substrate pin changed")
    if gate["coefficient_table_entries"] != 1792:
        raise VerifyError("coefficient coverage changed")
    if not gate["coefficient_table_materialized"]:
        raise VerifyError("table materialization pass missing")
    if gate["carrier_flow_returned_within_20_minutes"]:
        raise VerifyError("runtime shortfall silently promoted")
    if gate["mathematical_refusal_reached"]:
        raise VerifyError("runtime stop was relabelled mathematical")
    chunks = data["chunk_successor"]
    if chunks["radial_chunks"] != 28 or chunks["panels_per_chunk"] != 64:
        raise VerifyError("bounded-runtime decomposition changed")
    if chunks["shared_generator"] != 7315:
        raise VerifyError("shared affine generator changed")
    reset = data["reset_runtime_gate"]
    if reset["carrier_returned"] or reset["mathematical_refusal_reached"]:
        raise VerifyError("reset runtime cutoff was silently promoted")

    flags = data["claim_flags"]
    for name in (
        "full_frequency_cover_certified",
        "lower_lift_certified",
        "global_connection_certified",
        "radial_current_conservation_certified",
        "endpoint_flux_or_scattering_claim",
    ):
        if flags[name]:
            raise VerifyError(f"claim promoted: {name}")

    text = ADAPTER.read_text() if adapter_text is None else adapter_text
    required = [
        "ivlin_param_affine_fundamental_tables",
        "gc_inward_coeff_table",
        "gc_horizon_runtime",
        "raw=0,1,2",
    ]
    if any(token not in text for token in required):
        raise VerifyError("compact table/crosswalk consumer incomplete")
    forbidden = ["ivm_inverse", "scattering_matrix", "null flux"]
    if any(token in text for token in forbidden):
        raise VerifyError("forbidden inverse/flux surface entered adapter")
    return True


def main() -> None:
    verify_data(json.loads(CERTIFICATE.read_text()))
    print("PASS independent v5 bounded-runtime SHORTFALL boundary")


if __name__ == "__main__":
    main()
