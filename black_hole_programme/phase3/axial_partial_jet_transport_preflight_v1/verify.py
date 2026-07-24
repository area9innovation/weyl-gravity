#!/usr/bin/env python3
"""Independent verifier for the bounded partial-jet microfactor preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .produce import (
    CERTIFICATE,
    COMPILE_LOG,
    INPUTS,
    IVTAYLOR,
    ROOT,
    RUN_LOG,
    SOURCE,
    block_matrices,
    render_source,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-partial-jet-transport-preflight-v1"
    ):
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("lifecycle") != "CLASSIFIED":
        errors.append("lifecycle promotion")
    if document.get("status") != "CERTIFIED_BOUNDED_PREFLIGHT_SHORTFALL":
        errors.append("bounded shortfall was promoted or changed")

    imported: dict[str, dict] = {}
    for name, expected in INPUTS.items():
        reference = document.get("imports", {}).get(name)
        if not reference:
            errors.append(f"missing import: {name}")
            continue
        path = ROOT / reference["path"]
        if path.resolve() != expected.resolve():
            errors.append(f"import path drift: {name}")
            continue
        if not path.is_file() or sha256(path) != reference["sha256"]:
            errors.append(f"input hash drift: {name}")
            continue
        imported[name] = json.loads(path.read_text())
    if len(imported) != len(INPUTS):
        return errors

    crosswalk = imported["partial_jet_crosswalk"]
    if crosswalk["claim_flags"][
        "exact_full_six_state_factor_gauge_crosswalk"
    ] is not True:
        errors.append("exact crosswalk dependency demoted")
    base, tangent, direct = block_matrices(crosswalk)
    if base.shape != (8, 8) or tangent.shape != (8, 8):
        errors.append("real base/tangent shape mismatch")
    if direct.shape != (12, 12):
        errors.append("real six-state reference shape mismatch")

    attempt = document["attempt"]
    artifacts = {
        SOURCE: attempt["source_sha256"],
        COMPILE_LOG: attempt["compile_log_sha256"],
        RUN_LOG: attempt["run_log_sha256"],
    }
    for path, digest in artifacts.items():
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"attempt artifact hash drift: {path.name}")
    if SOURCE.is_file() and SOURCE.read_text() != render_source(crosswalk):
        errors.append("rendered Forge source drift")
    if sha256(IVTAYLOR) != document["forge_substrate"]["ivtaylor_sha256"]:
        errors.append("IvTaylor4 substrate hash drift")
    source = SOURCE.read_text() if SOURCE.is_file() else ""
    for marker in (
        "pub type DualT4",
        "ivtm4_mul_checked",
        "dual_series",
        "dual_expand",
        "difference_contains_zero",
    ):
        if marker not in source:
            errors.append(f"missing source marker: {marker}")

    if attempt["compile_exit"] != 0 or attempt["run_exit"] != 3:
        errors.append("typed compile/run disposition drift")
    result = attempt["parsed_result"]
    if result is None:
        errors.append("missing parsed refusal")
    else:
        if (
            result["status"] != "REFUSED"
            or result["refusal"] != "ANALYTIC_TAIL_NONCONTRACTIVE"
            or result["tail"] != "-1"
        ):
            errors.append("tail refusal drift")
        alpha = float(result["alpha"])
        scaled = float(result["scaled_norm"])
        if alpha <= 0.0 or scaled <= 1.0:
            errors.append("noncontractive tail witness lost")
        expected_scaled = alpha / 1073741824.0
        if abs(expected_scaled - scaled) > 1e-8 * scaled:
            errors.append("scaled coefficient norm mismatch")
        if (
            result["coefficient_equal"] is not None
            or result["difference_contains_zero"] is not None
        ):
            errors.append("post-refusal comparison was fabricated")

    comparison = document["comparison"]
    if comparison["passed"]:
        errors.append("microfactor comparison was promoted")
    flags = document["claim_flags"]
    if flags["shared_omega_dual_tau_arithmetic_exercised"] is not True:
        errors.append("exercised mixed arithmetic flag demoted")
    for name in (
        "one_microfactor_bounded_partial_jet_pass",
        "expanded_six_state_reference_compared",
        "whole_q00_child_transport_certified",
        "H4_pass_certified",
        "endpoint_partial_jet_frames_constructed",
        "T_plus_recovered",
        "scattering_identity_certified",
        "bounded_global_transport_certified",
    ):
        if flags[name] is not False:
            errors.append(f"open claim promoted: {name}")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(1)
    print(
        "verified=true status=CERTIFIED_BOUNDED_PREFLIGHT_SHORTFALL "
        "refusal=ANALYTIC_TAIL_NONCONTRACTIVE"
    )
