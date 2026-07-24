#!/usr/bin/env python3
"""Independent verifier for the common moving-frame r=31 checkpoint."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import sys
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import jsonschema

sys.set_int_max_str_digits(1_000_000)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCALE = Fraction(93, 4)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def tagged(text: str, label: str) -> dict:
    match = re.search(rf"^{re.escape(label)} (.+)$", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"missing source model {label}")
    return json.loads(match.group(1))


def exact_endpoint(bits: str) -> Fraction:
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise RuntimeError("nonfinite interval endpoint")
    return Fraction.from_float(value)


def outward(value: Fraction, downward: bool) -> str:
    rounded = float(value)
    exact = Fraction.from_float(rounded)
    if downward and exact > value:
        rounded = math.nextafter(rounded, -math.inf)
    elif not downward and exact < value:
        rounded = math.nextafter(rounded, math.inf)
    return struct.pack(">d", rounded).hex()


def independently_correct(
    tangent: dict,
    base: dict,
    pairs: tuple[tuple[int, int], ...],
) -> dict:
    output = deepcopy(tangent)
    for target, source in pairs:
        for degree in range(5):
            output["coefficients"][degree][target][0] = str(
                Fraction(tangent["coefficients"][degree][target][0])
                + SCALE * Fraction(base["coefficients"][degree][source][0])
            )
        tangent_lo, tangent_hi = (
            exact_endpoint(value)
            for value in tangent["remainder_bits"][target][0]
        )
        base_lo, base_hi = (
            exact_endpoint(value)
            for value in base["remainder_bits"][source][0]
        )
        lower = tangent_lo + SCALE * base_lo
        upper = tangent_hi + SCALE * base_hi
        output["remainder_bits"][target][0] = [
            outward(lower, True),
            outward(upper, False),
        ]
    return output


def hull(model: dict, row: int) -> tuple[Fraction, Fraction]:
    coefficients = [
        Fraction(model["coefficients"][degree][row][0])
        for degree in range(5)
    ]
    radius = sum(abs(value) for value in coefficients[1:])
    low, high = (
        exact_endpoint(value) for value in model["remainder_bits"][row][0]
    )
    return coefficients[0] - radius + low, coefficients[0] + radius + high


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    if document["status"] != (
        "MOVING_FRAME_R31_RANK3_ANALYTIC_KPLUS_ZERO"
    ):
        raise RuntimeError("moving-frame result did not close")
    for item in document["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {item['path']}")

    checkpoint = json.loads((HERE / "checkpoint.json").read_text())
    restart = json.loads((HERE / "restart_manifest.json").read_text())
    if canonical_sha256(checkpoint["payload"]) != (
        checkpoint["payload_sha256"]
    ):
        raise RuntimeError("checkpoint payload hash mismatch")
    if restart["checkpoint_payload_sha256"] != (
        checkpoint["payload_sha256"]
    ):
        raise RuntimeError("restart/checkpoint payload mismatch")
    if restart["roundtrip_payload_sha256"] != (
        checkpoint["payload_sha256"]
    ):
        raise RuntimeError("restart roundtrip hash mismatch")
    if not restart["json_roundtrip_exact"] or not restart["restart_ready"]:
        raise RuntimeError("restart serialization did not close")

    imports = document["imports"]
    reference = (ROOT / imports["R_reference_run"]["path"]).read_text()
    independent = (
        ROOT / imports["R_independent_restart_run"]["path"]
    ).read_text()
    r_base = tagged(reference, "REFERENCE_BASE")
    r_fixed = tagged(reference, "REFERENCE_TANGENT")
    if r_base != tagged(independent, "RESTART_BASE"):
        raise RuntimeError("independent R base restart mismatch")
    if r_fixed != tagged(independent, "RESTART_TANGENT"):
        raise RuntimeError("independent R tangent restart mismatch")
    source_s = json.loads(
        (ROOT / imports["S_checkpoint"]["path"]).read_text()
    )
    if canonical_sha256(source_s["payload"]) != source_s["payload_sha256"]:
        raise RuntimeError("source S checkpoint hash mismatch")
    s_base = source_s["payload"]["base"]
    s_fixed = source_s["payload"]["tangent"]

    expected_r = independently_correct(
        r_fixed, r_base, ((1, 1), (3, 3))
    )
    expected_s = independently_correct(
        s_fixed, s_base, ((1, 1), (5, 5))
    )
    models = checkpoint["payload"]["models"]
    if models["R_base"] != r_base:
        raise RuntimeError("R base checkpoint serialization drift")
    if models["R_tangent_moving"] != expected_r:
        raise RuntimeError("R moving tangent correction mismatch")
    if models["S_base_core"] != s_base:
        raise RuntimeError("S base checkpoint serialization drift")
    if models["S_tangent_moving_core"] != expected_s:
        raise RuntimeError("S moving tangent correction mismatch")
    for name, model in models.items():
        if canonical_sha256(model) != (
            restart["model_canonical_sha256"][name]
        ):
            raise RuntimeError(f"restart model hash mismatch: {name}")
        if model["generator"] != 7315 or model["degree"] != 4:
            raise RuntimeError("shared Taylor generator or degree drifted")

    gauge = checkpoint["payload"]["moving_gauge"]
    h0 = gauge["h0"]
    if h0["expression"] != (
        "(32/31)*exp(I*omega*(64+4*log(32)))"
    ):
        raise RuntimeError("typed h0 expression drifted")
    if not h0["zero_free"] or h0["analytic_on"] != "entire omega plane":
        raise RuntimeError("h0 analytic-unit typing failed")
    if gauge["combined_logarithmic_generator"] != "diag(0,-3/4)":
        raise RuntimeError("moving generator drifted")

    r_interval = hull(r_base, 0)
    s_interval = hull(s_base, 2)
    if not (r_interval[0] > 0 and s_interval[0] > 0):
        raise RuntimeError("rank-three pivot failed")
    minor = document["rank_three_minor"]
    if minor["determinant_factorization"] != (
        "h0*R_base[0]**2*S_base_Z_core[0]"
    ):
        raise RuntimeError("rank minor factorization drifted")
    if not minor["determinant_nonzero"] or minor["complex_rank"] != 3:
        raise RuntimeError("rank-three result not certified")

    normalization = document["endpoint_normalization_audit"]
    if not normalization["complete_moving_factor_extracted"]:
        raise RuntimeError("complete moving factor not extracted")
    if normalization["combined_moving_generator"] != [
        ["0", "0"],
        ["0", "-3/4"],
    ]:
        raise RuntimeError("normalization generator mismatch")
    if (
        not normalization["forced_logs_zero"]
        or not normalization["free_EI2_constants_zero"]
        or not normalization["residual_leading_amplitude_derivative_zero"]
    ):
        raise RuntimeError("endpoint residual normalization did not close")
    if normalization["analytic_first_jet_K_plus"] != [
        ["0", "0"],
        ["0", "0"],
    ]:
        raise RuntimeError("analytic first-jet K-plus is not zero")
    if not normalization["analytic_K_plus_zero_certified"]:
        raise RuntimeError("analytic K-plus flag missing")

    flags = document["claim_flags"]
    for key in (
        "moving_phase_correction_exact",
        "correction_remainder_containment_certified",
        "shared_omega_generator_preserved",
        "typed_h0_analytic_zero_free",
        "restart_serialization_certified",
        "joint_moving_frame_rank_three_certified",
        "common_tau_frame_supplied",
        "analytic_K_plus_zero_certified",
    ):
        if not flags[key]:
            raise RuntimeError(f"positive claim flag missing: {key}")
    for key in ("T_plus_certified", "stokes_or_scattering_certified"):
        if flags[key]:
            raise RuntimeError(f"downstream claim improperly promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent outgoing common moving-frame verifier")


if __name__ == "__main__":
    main()
