"""Independent verifier for the fail-closed channel-classifier disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def verify_document(document: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: list(error.path),
    )
    if errors:
        fail("schema: " + errors[0].message)

    basis = document["basis_contract"]
    raw = basis["raw_horizon_order"]
    public = basis["public_horizon_order"]
    public_to_raw = basis["public_index_to_raw_index"]
    raw_to_public = basis["raw_index_to_public_index"]
    if [raw[index] for index in public_to_raw] != public:
        fail("public-to-raw crosswalk")
    if [public[index] for index in raw_to_public] != raw:
        fail("raw-to-public crosswalk")
    if basis["raw_future_regular_selector"] != [0, 1, 2]:
        fail("raw future-regular selector")
    if basis["public_future_regular_selector"] != [0, 1, 4]:
        fail("public future-regular selector")
    if [raw[index] for index in basis["raw_future_regular_selector"]] != [
        "XH0a", "XH0b", "EH0"
    ]:
        fail("future-regular origin labels")
    if basis["additional_origin_columns"] != [0, 1]:
        fail("additional origin deleted")
    if basis["einstein_origin_columns"] != [2]:
        fail("Einstein origin changed")
    if basis["infinity_order"] != [
        "XI0", "XI1", "XI2", "XI3", "EI0", "EI2"
    ]:
        fail("infinity order")
    if basis["Iminus_selector"] != [0, 1, 4]:
        fail("Iminus selector")
    if basis["Iplus_selector"] != [2, 3, 5]:
        fail("Iplus selector")

    endpoint = document["endpoint_input"]
    path = ROOT / endpoint["path"]
    payload = json.loads(path.read_text())
    if sha256(path) != endpoint["sha256"]:
        fail("endpoint hash drift")
    if payload["result_id"] != endpoint["result_id"]:
        fail("endpoint result identity")
    if not payload["claim_flags"]["endpoint_rank_radical_inertia_certified"]:
        fail("endpoint input not certified")
    if endpoint["Iminus_basis"] != ["XI0", "XI1", "EI0"]:
        fail("Iminus basis import")
    if endpoint["Iplus_basis"] != ["XI2", "XI3", "EI2"]:
        fail("Iplus basis import")
    if endpoint["Iminus_inertia"] != [1, 2, 0]:
        fail("Iminus endpoint inertia")
    if endpoint["Iplus_inertia"] != [1, 2, 0]:
        fail("Iplus endpoint inertia")

    activation = document["activation"]
    expected = ROOT / activation["expected_handoff_path"]
    if activation["path_present"] != expected.exists():
        fail("connection-presence disposition")
    expected_status = (
        "INCOMPATIBLE_GLOBAL_CONNECTION"
        if expected.exists()
        else "MISSING_GLOBAL_CONNECTION"
    )
    if activation["status"] != expected_status:
        fail("activation status")
    required_phrases = (
        "6x3 connection", "raw/public", "ranks", "kernels",
        "realified", "horizon", "conservation", "multiplier",
    )
    joined = " ".join(activation["missing_or_unverified_fields"])
    for phrase in required_phrases:
        if phrase not in joined:
            fail("missing-field ledger omitted " + phrase)

    if document["classification"] != {
        "status": "NOT_COMPUTED",
        "frequency_cells": [],
        "exceptional_cells": [],
        "global_additional_channel_status": "UNPOPULATED_NOT_ZERO",
        "reason": "validated global connection handoff is absent",
    }:
        fail("invented channel classification")
    flags = document["claim_flags"]
    if not flags["endpoint_grams_imported"]:
        fail("endpoint import hidden")
    if any(value for key, value in flags.items() if key != "endpoint_grams_imported"):
        fail("claim promoted without global connection")
    if any(document["forbidden_promotions"].values()):
        fail("forbidden promotion activated")
    if "GHplus+gplus-gminus=0" != document["classifier_contract"]["conservation"]:
        fail("orientation-correct conservation changed")
    if "radial Wronskian" in document["classifier_contract"]["wavepacket_extension"]:
        fail("radial current identified with null flux")


def main() -> None:
    verify_document(json.loads(CERT.read_text()))
    print("PASS: fail-closed axial global finite-flux classifier verified")


if __name__ == "__main__":
    main()

