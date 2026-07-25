#!/usr/bin/env python3
"""Summarize the amplitude-preserving T+ continuation, fail closed.

This producer does not rerun the expensive Forge stages.  It hashes and
audits their immutable JSON outputs, then records the precise obstruction to
terminal rank certification.
"""

from __future__ import annotations

import hashlib
import json
import platform
import struct
import sys
from fractions import Fraction
from pathlib import Path

from . import amplitude_taylor_transport as transport

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE_DIR = HERE / "amplitude_stages"
MANIFEST = HERE / "amplitude_manifest.json"
CERTIFICATE = HERE / "amplitude_certificate.json"
RECEIPT = HERE / "amplitude_receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def rendered(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def f64_fraction(bits: int) -> Fraction:
    raw = (bits % (1 << 64)).to_bytes(8, "big")
    value = struct.unpack(">d", raw)[0]
    if not (value == value and abs(value) != float("inf")):
        raise AssertionError("non-finite interval endpoint")
    return Fraction.from_float(value)


def frame_diagnostic(model: dict) -> dict:
    center = max(
        abs(Fraction(value))
        for row in model["coefficients"][0]
        for value in row
    )
    linear = max(
        abs(Fraction(value))
        for row in model["coefficients"][1]
        for value in row
    )
    remainder = max(
        max(abs(f64_fraction(lo)), abs(f64_fraction(hi)))
        for row in model["remainder_bits"]
        for lo, hi in row
    )
    if center == 0:
        raise AssertionError("terminal frame has zero coefficient scale")
    ratio = remainder / center
    return {
        "max_center_abs_exact": fraction_text(center),
        "max_linear_abs_exact": fraction_text(linear),
        "max_remainder_abs_exact": fraction_text(remainder),
        "remainder_to_center_ratio_exact": fraction_text(ratio),
        "remainder_to_center_ratio_lower_integer": ratio.numerator
        // ratio.denominator,
    }


def load_stages() -> list[dict]:
    stages = []
    for index in range(7):
        path = STAGE_DIR / f"q00-stage{index}.json"
        document = json.loads(path.read_text())
        declared = document.pop("payload_sha256")
        actual = canonical_sha256(document)
        document["payload_sha256"] = declared
        if declared != actual:
            raise AssertionError(f"stage {index} payload hash mismatch")
        if document["stage"] != index:
            raise AssertionError(f"stage {index} identity mismatch")
        if document["cell"]["omega_interval"] != list(
            transport.TARGET_INTERVAL
        ):
            raise AssertionError(f"stage {index} frequency cell mismatch")
        if document["execution"]["exit_code"] != 42:
            raise AssertionError(f"stage {index} did not pass Forge")
        stages.append(document)
    return stages


def produce() -> None:
    stages = load_stages()
    factor_manifest = (
        ROOT
        / "black_hole_programme/phase3/axial_global_connection_matrix_v5"
        / "chunks/artifacts/infinity_plane_manifests/q00.json"
    )
    for index in range(5):
        if stages[index]["status"] != "CERTIFIED_STAGE":
            raise AssertionError(f"stage {index} lost certified status")
        if stages[index]["terminal_ranks"] != {
            "Iminus": 6,
            "Iplus": 6,
            "combined": 12,
        }:
            raise AssertionError(f"stage {index} rank drift")
    if stages[5]["status"] != "VALIDATED_RAW_TAIL_CHECKPOINT":
        raise AssertionError("stage 5 raw checkpoint drift")
    if stages[6]["status"] != "VALIDATED_INFINITY_FRAME_ENCLOSURE_AT_R4":
        raise AssertionError("stage 6 endpoint status drift")
    if stages[6]["terminal_rank_certified"]:
        raise AssertionError("terminal rank unexpectedly promoted")

    diagnostics = {
        name: frame_diagnostic(model)
        for name, model in stages[6]["raw_frames"].items()
    }
    if any(
        item["remainder_to_center_ratio_lower_integer"] < 1_000_000
        for item in diagnostics.values()
    ):
        raise AssertionError("recorded wrapping obstruction disappeared")

    stage_records = []
    for index, document in enumerate(stages):
        path = STAGE_DIR / f"q00-stage{index}.json"
        stage_records.append(
            {
                "stage": index,
                "path": str(path.relative_to(ROOT)),
                "file_sha256": sha256(path),
                "payload_sha256": document["payload_sha256"],
                "status": document["status"],
                "source_sha256": document["source_sha256"],
            }
        )
    manifest = {
        "schema": "phase4-tplus-amplitude-manifest-v1",
        "method": "amplitude-preserving Grassmann cocycle followed by raw tail",
        "frequency_interval": list(transport.TARGET_INTERVAL),
        "stage_records": stage_records,
        "producer": {
            "path": str(
                Path(__file__).resolve().relative_to(ROOT)
            ),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "transport_source": {
            "path": str(
                Path(transport.__file__).resolve().relative_to(ROOT)
            ),
            "sha256": sha256(Path(transport.__file__).resolve()),
        },
        "pinned_factor_cover": {
            "path": str(factor_manifest.relative_to(ROOT)),
            "sha256": sha256(factor_manifest),
        },
    }
    manifest["payload_sha256"] = canonical_sha256(manifest)
    MANIFEST.write_text(rendered(manifest))

    certificate = {
        "schema": "phase4-tplus-amplitude-shortfall-certificate-v1",
        "status": "FAIL_CLOSED_REPRESENTATION_WRAPPING",
        "dependency_tag": "REDUCED-MODE",
        "frequency_interval": list(transport.TARGET_INTERVAL),
        "validated_result": {
            "physical_endpoint_normalization_preserved_through_stage4": True,
            "dense_crosswalk_applied_without_frame_inversion": True,
            "raw_frame_enclosures_reached_r4": True,
            "terminal_rank_certified": False,
            "diagnostics": diagnostics,
        },
        "interpretation": (
            "The amplitude cocycle reaches r=4, but rectangular Taylor "
            "remainders exceed the coefficient scale by more than 10^6 in "
            "both endpoint frames.  This representation cannot certify the "
            "terminal inverse or explicit T_plus."
        ),
        "claim_flags": {
            "explicit_Tplus_certified": False,
            "reflection_matrix_certified": False,
            "terminal_frame_invertibility_certified": False,
            "title_theorem_dependency": False,
        },
        "does_not_establish": [
            "the entries of T_plus",
            "a reflection matrix",
            "terminal frame invertibility",
            "failure of T_plus to exist",
            "failure of a better-conditioned representation",
        ],
        "manifest_sha256": sha256(MANIFEST),
        "independence_profile": {
            "independent_code": False,
            "independent_representation": False,
            "independent_arithmetic_backend": False,
            "independent_mathematical_derivation": False,
            "role": "producer-output integrity and fail-closed status audit",
        },
    }
    certificate["payload_sha256"] = canonical_sha256(certificate)
    CERTIFICATE.write_text(rendered(certificate))

    receipt = {
        "schema": "phase4-tplus-amplitude-receipt-v1",
        "certificate_sha256": sha256(CERTIFICATE),
        "manifest_sha256": sha256(MANIFEST),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "arithmetic": "exact Fraction plus decoded binary64 endpoints",
        },
        "commands": {
            "produce": (
                "python3 -m black_hole_programme.phase4."
                "axial_explicit_tplus_band_v1.produce_amplitude_summary"
            ),
            "verify": (
                "python3 -m black_hole_programme.phase4."
                "axial_explicit_tplus_band_v1.verify_amplitude_taylor"
            ),
            "test": (
                "python3 -m unittest -v black_hole_programme.phase4."
                "axial_explicit_tplus_band_v1.test_amplitude_taylor"
            ),
        },
        "expected_exit_status": 0,
    }
    RECEIPT.write_text(rendered(receipt))


def main() -> int:
    produce()
    print(
        "PASS fail-closed T+ amplitude shortfall "
        f"certificate={sha256(CERTIFICATE)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
