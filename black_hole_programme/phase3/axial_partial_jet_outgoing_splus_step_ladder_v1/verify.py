#!/usr/bin/env python3
"""Independent verifier for the outgoing S+ step ladder."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(data: dict) -> None:
    jsonschema.validate(data, json.loads((HERE / "schema.json").read_text()))
    if data["status"] != "FINITE_LADDER_1_OVER_128_ADMISSIBLE":
        raise RuntimeError("step ladder did not pass")
    for item in data["imports"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("import hash drift")
    for name in ("source", "compile_log", "run_log"):
        item = data["artifacts"][name]
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("artifact hash drift")
    cases = data["transport"]["cases"]
    if set(cases) != {"128", "64", "32"}:
        raise RuntimeError("step set drift")
    if any(case["status"] != "PASS" for case in cases.values()):
        raise RuntimeError("a ladder step is not certified")
    if cases["128"]["operationally_admissible"] is not True:
        raise RuntimeError("1/128 step is not operationally admissible")
    if cases["64"]["operationally_admissible"] is not False:
        raise RuntimeError("1/64 step was over-promoted")
    if cases["32"]["operationally_admissible"] is not False:
        raise RuntimeError("1/32 step was over-promoted")
    flags = data["claim_flags"]
    if not all(
        flags[key]
        for key in (
            "common_generator_preserved",
            "step_1_over_128_certified",
            "step_1_over_64_certified",
            "step_1_over_32_certified",
            "step_1_over_128_operationally_admissible",
        )
    ):
        raise RuntimeError("positive ladder flag missing")
    if (
        flags["step_1_over_64_operationally_admissible"]
        or flags["step_1_over_32_operationally_admissible"]
    ):
        raise RuntimeError("wide step was called operationally admissible")
    if any(
        flags[key]
        for key in (
            "transport_to_r31_certified",
            "joint_E_R_S_frame_certified",
            "K_plus_certified",
            "T_plus_certified",
        )
    ):
        raise RuntimeError("downstream claim promoted")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent outgoing S+ step-ladder verifier")


if __name__ == "__main__":
    main()
