#!/usr/bin/env python3
"""Independent verifier for the retained-26 bikernel support gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-26-row-smooth-bikernel-homotopy-support-gate-v1.schema.json"
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = load(CERT)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    dependencies = {}
    for name, record in value["dependencies"].items():
        path = ROOT / record["path"]
        if sha(path) != record["sha256"]:
            raise AssertionError(f"dependency hash drifted: {name}")
        dependencies[name] = load(path)

    classical = dependencies["classical_homotopy"]
    proof = dependencies["classical_proof"]
    ward = dependencies["quantum_Ward_reduction"]
    if (
        classical["support_category"]["globally_hyperbolic"] is not True
        or "compact spatial Cauchy surface"
        not in classical["support_category"]["boundary_conditions"]
        or any(
            check["status"] != "VERIFIED"
            for check in classical["green_proof_checks"].values()
        )
    ):
        raise AssertionError("classical causal support input failed")
    if (
        "same-sided" not in proof["support_proof"]["ghost_and_identity"]
        or "Lambda26,+^sharp" not in proof["cyclicity"]["identity"]
    ):
        raise AssertionError("causal support or cyclic adjoint proof missing")

    exported = {
        "smoothness": (
            ward["ward_reduction"]["smooth_defect"]
            == "C26=[H26_plus,q26] is a smooth kernel"
        ),
        "support_profile": any(
            key in ward["candidate_status"]
            for key in (
                "C26_x_past_compact",
                "C26_x_future_compact",
                "C26_x_time_compact",
                "C26_mode_support",
            )
        ),
    }
    if exported != {"smoothness": True, "support_profile": False}:
        raise AssertionError(f"independent C26 export audit failed: {exported}")

    rows = {row["class_id"]: row for row in value["support_classes"]}
    if set(rows) != {
        "K_PC_X",
        "K_FC_X",
        "K_TC_X",
        "K_SC_X_EQUALS_ALL_SMOOTH",
    }:
        raise AssertionError("support-class ledger incomplete")
    if not all(
        rows[name]["continuous_extension"]
        for name in ("K_PC_X", "K_FC_X", "K_TC_X")
    ):
        raise AssertionError("one-sided extension was dropped")
    if (
        rows["K_SC_X_EQUALS_ALL_SMOOTH"]["continuous_extension"] is not False
        or rows["K_SC_X_EQUALS_ALL_SMOOTH"]["C26_membership"]
        != "YES_BY_SMOOTHNESS_ONLY"
    ):
        raise AssertionError("full-smooth boundary was promoted")

    negative = value["negative_fixture"]
    retarded = negative["retarded_sequence"]
    advanced = negative["advanced_sequence"]
    if (
        "f_n tends to 0" not in retarded["source_limit"]
        or "tends to h" not in retarded["image_limit"]
        or "no continuous extension" not in retarded["conclusion"]
        or "tends to 0" not in advanced["source_limit"]
        or "tends to h" not in advanced["image_limit"]
        or "no continuous extension" not in advanced["conclusion"]
    ):
        raise AssertionError("cutoff-escape discontinuity fixture failed")

    flags = value["classification"]
    if (
        flags["C26_in_positive_extension_domain_certified"]
        or flags["smooth_Ward_correction_constructed"]
        or flags["retained_BRST_Hadamard_promoted"]
        or flags["positivity_or_quantum_claim"]
    ):
        raise AssertionError("support gate overpromoted")

    for path_text, digest in value["provenance"]["source_manifest"].items():
        if sha(ROOT / path_text) != digest:
            raise AssertionError(f"source manifest drifted: {path_text}")

    mutant = deepcopy(value)
    mutant["classification"][
        "C26_in_positive_extension_domain_certified"
    ] = True
    try:
        Draft202012Validator(schema).validate(mutant)
    except Exception:
        pass
    else:
        raise AssertionError("unsupported C26 membership mutation accepted")
    return value


def main() -> None:
    verify()
    print(
        "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1 "
        "independent verification: PASS"
    )


if __name__ == "__main__":
    main()
