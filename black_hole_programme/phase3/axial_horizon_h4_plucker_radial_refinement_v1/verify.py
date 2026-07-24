#!/usr/bin/env python3
"""Independent verifier for the bounded radial-refinement experiment."""
from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPSTREAM = (
    HERE.parent / "axial_horizon_h4_plucker_correlated_functional_v1"
)
UPSTREAM_CERTIFICATE = UPSTREAM / "certificate.json"
UPSTREAM_MANIFEST = UPSTREAM / "correlated_manifest.json"
EXPECTED_UPSTREAM_CERTIFICATE_SHA256 = (
    "14fb85004516b03e6ecfffa566ac2a2ee8080168ddd125b3754cedb6391f4003"
)
EXPECTED_UPSTREAM_MANIFEST_SHA256 = (
    "7fbd0ef15ea0d1442ff03b93b06b24c05f2ac5c60e3dfb1784b0c6a28b7881e3"
)
RADIAL_WIDTHS = {2: "1/134217728", 4: "1/268435456"}
MANIFEST = HERE / "refinement_manifest.json"
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"


class VerificationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_hash(payload: dict) -> str:
    body = {
        key: value for key, value in payload.items()
        if key != "payload_sha256"
    }
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def heartbeat_hashes(text: str) -> list[str]:
    lines = [
        line for line in text.splitlines()
        if line.startswith("PLUCKER_SEGMENT ")
    ][:19]
    return [
        hashlib.sha256((line + "\n").encode()).hexdigest()
        for line in lines
    ]


def verify_upstream() -> dict:
    require(
        sha256(UPSTREAM_CERTIFICATE)
        == EXPECTED_UPSTREAM_CERTIFICATE_SHA256,
        "upstream certificate hash drift",
    )
    require(
        sha256(UPSTREAM_MANIFEST)
        == EXPECTED_UPSTREAM_MANIFEST_SHA256,
        "upstream manifest hash drift",
    )
    certificate = json.loads(UPSTREAM_CERTIFICATE.read_text())
    manifest = json.loads(UPSTREAM_MANIFEST.read_text())
    require(
        certificate.get("status")
        == "CERTIFIED_CORRELATED_FUNCTIONAL_OBSTRUCTION",
        "upstream status drift",
    )
    require(manifest.get("status") == "CORRELATED_REFUSED",
            "upstream manifest drift")
    require(len(manifest.get("children", [])) == 2,
            "upstream child count drift")
    return manifest


def verify_source(factor: int, child: int, entry: dict) -> None:
    path = HERE / entry["source_path"]
    metadata_path = HERE / entry["metadata_path"]
    compile_path = HERE / entry["compile_log_path"]
    require(
        path.is_file() and metadata_path.is_file() and compile_path.is_file(),
        "attempt source, metadata, or compile log absent",
    )
    source = path.read_text()
    metadata = json.loads(metadata_path.read_text())
    require(sha256(path) == entry["source_sha256"],
            "attempt source hash drift")
    require(metadata.get("factor") == factor, "metadata factor drift")
    require(metadata.get("child_index") == child,
            "metadata child drift")
    require(metadata.get("source_sha256") == entry["source_sha256"],
            "metadata source hash drift")
    compile_text = compile_path.read_text()
    require(
        re.findall(
            r"^COMPILE_PROCESS_EXIT=(\d+)$",
            compile_text,
            flags=re.MULTILINE,
        ) == ["0"],
        "attempt compile did not pass",
    )
    compile_elapsed = re.findall(
        r"^COMPILE_ELAPSED_MILLISECONDS=(\d+)$",
        compile_text,
        flags=re.MULTILINE,
    )
    require(
        len(compile_elapsed) == 1 and int(compile_elapsed[0]) > 0,
        "compile elapsed time absent",
    )
    markers = (
        "fn pl_hybrid_refined_attempt(shell:i64,segment:i64,",
        "let count:i64=32*factor;",
        "rat_clone(hr_panel_width(shell))/rat(factor,1)",
        "if(raw.refusal_code!=32){return raw;}",
        "pl_correlated_projective_normalize(stepped.value)",
        f"pl_hybrid_refined_attempt(4,3,cell,state,{factor})",
    )
    for marker in markers:
        require(marker in source, f"source marker absent: {marker}")
    require(
        source.count(
            f"pl_hybrid_refined_attempt(4,3,cell,state,{factor})"
        ) == 1,
        "refined target call count drift",
    )
    require(
        "pl_correlated_attempt(4,3,cell,state)" not in source,
        "unrefined target call remains",
    )


REFUSAL_RE = re.compile(
    r"^RADIAL_REFINEMENT_REFUSE factor=(\d+) panel=(\d+) "
    r"raw_code=(\d+) correlated_code=(\d+)$",
    flags=re.MULTILINE,
)
DEFECT_RE = re.compile(
    r"^CORRELATED_FUNCTIONAL_DEFECT lo=([^ ]+) hi=([^ ]+) "
    r"norm=([^ ]+)$",
    flags=re.MULTILINE,
)


def verify_log(
    factor: int, child: int, entry: dict, baseline_hashes: list[str]
) -> dict:
    path = HERE / entry["run_log_path"]
    require(path.is_file(), "attempt run log absent")
    require(sha256(path) == entry["run_log_sha256"],
            "attempt run-log hash drift")
    text = path.read_text()
    require("trap() reached" not in text, "attempt trapped")
    require("PLUCKER_RELATION_DEFECT" not in text,
            "attempt relation defect")
    require(heartbeat_hashes(text) == baseline_hashes,
            "pre-boundary heartbeat drift")
    require(entry["prefix_heartbeat_hashes"] == baseline_hashes,
            "manifest heartbeat hash drift")
    source_hashes = re.findall(
        r"^PLUCKER_SOURCE_SHA256=([0-9a-f]{64})$",
        text,
        flags=re.MULTILINE,
    )
    require(source_hashes == [entry["source_sha256"]],
            "runtime source hash drift")
    require(entry["factor"] == factor and entry["child_index"] == child,
            "attempt coordinate drift")
    require(
        entry["radial_panel_width"] == RADIAL_WIDTHS[factor],
        "radial width drift",
    )
    if entry["status"] == "PASS":
        require(entry["process_exit"] == 42, "passing exit drift")
        require("RADIAL_REFINEMENT_PASS" in text,
                "passing witness absent")
        require(entry["pass_witness"] is not None,
                "passing witness manifest absent")
        return {"status": "PASS"}
    require(entry["status"] == "REFUSED", "attempt status drift")
    require(entry["process_exit"] == 3, "refusal exit drift")
    refusals = REFUSAL_RE.findall(text)
    defects = DEFECT_RE.findall(text)
    require(len(refusals) == 1 and len(defects) == 1,
            "typed refusal evidence absent")
    rf, panel, raw, correlated = map(int, refusals[0])
    require(rf == factor and raw == 32 and correlated == 35,
            "typed refusal code drift")
    require(entry["refusal"] == {
        "panel": panel, "raw_code": raw, "correlated_code": correlated
    }, "manifest refusal drift")
    lo, hi, norm = map(float, defects[0])
    require(all(math.isfinite(value) for value in (lo, hi, norm)),
            "nonfinite defect")
    require(lo <= 0 <= hi and norm > 0,
            "refused functional does not straddle zero")
    defect = entry["defect"]
    require(
        [defect["lo"], defect["hi"], defect["norm"]]
        == list(defects[0]),
        "manifest defect drift",
    )
    require(
        math.isclose(float(defect["interval_width"]), hi - lo,
                     rel_tol=0, abs_tol=1e-21),
        "defect width drift",
    )
    left = Fraction(1, 262144) + panel * Fraction(
        entry["radial_panel_width"]
    )
    return {
        "status": "REFUSED",
        "panel": panel,
        "left": str(left),
        "width": defect["interval_width"],
    }


def verify_manifest(manifest: dict) -> dict:
    upstream = verify_upstream()
    require(
        manifest.get("schema")
        == "phase3-axial-h4-plucker-radial-refinement-manifest-v1",
        "manifest schema drift",
    )
    require(manifest.get("payload_sha256") == payload_hash(manifest),
            "manifest payload hash drift")
    require(
        manifest.get("upstream_certificate_sha256")
        == EXPECTED_UPSTREAM_CERTIFICATE_SHA256,
        "manifest upstream certificate drift",
    )
    require(
        manifest.get("upstream_manifest_sha256")
        == EXPECTED_UPSTREAM_MANIFEST_SHA256,
        "manifest upstream manifest drift",
    )
    scope = manifest.get("scope", {})
    require(scope.get("factors_in_order") == [2, 4],
            "refinement factor order drift")
    require(scope.get("radial_boundary") == {"shell": 4, "segment": 3},
            "radial boundary drift")
    require(scope.get("no_later_shell") is True,
            "later-shell scope drift")
    baselines = manifest.get("baseline_prefix_heartbeat_hashes", [])
    require(len(baselines) == 2, "baseline heartbeat child count drift")
    for child in (0, 1):
        upstream_text = (
            UPSTREAM_MANIFEST.parent
            / upstream["children"][child]["run_log_path"]
        ).read_text()
        require(baselines[child] == heartbeat_hashes(upstream_text),
                "baseline heartbeat provenance drift")
        require(len(baselines[child]) == 19,
                "baseline heartbeat count drift")
    attempts = manifest.get("attempts", [])
    require([value.get("factor") for value in attempts] == [2, 4],
            "attempt factor coverage drift")
    results = []
    for attempt in attempts:
        factor = attempt["factor"]
        require(attempt.get("radial_panel_width")
                == RADIAL_WIDTHS[factor],
                "factor radial width drift")
        require(attempt.get("cover_pass") is False,
                "unexpected cover-pass drift")
        children = attempt.get("children", [])
        require(len(children) == 2, "attempt child coverage drift")
        for child, entry in enumerate(children):
            verify_source(factor, child, entry)
            results.append(
                verify_log(factor, child, entry, baselines[child])
            )
    require(
        manifest.get("status")
        == "CERTIFIED_RADIAL_REFINEMENT_OBSTRUCTION",
        "manifest terminal status drift",
    )
    require(manifest.get("decisive_factor") is None,
            "obstruction has a decisive pass factor")
    require({value["left"] for value in results}
            == {"725/134217728"},
            "refinements do not share the refusal left boundary")
    return {
        "status": manifest["status"],
        "attempts": results,
        "common_left_boundary": "725/134217728",
    }


def verify_certificate(certificate: dict, result: dict) -> None:
    require(
        certificate.get("schema")
        == "phase3-axial-h4-plucker-radial-refinement-certificate-v1",
        "certificate schema drift",
    )
    require(certificate.get("status") == result["status"],
            "certificate status drift")
    require(
        certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency tags drift",
    )
    require(
        certificate.get("result", {}).get("rank_loss_established") is False,
        "refusal promoted to rank loss",
    )
    require(
        certificate.get("result", {}).get(
            "common_refusal_left_boundary"
        ) == result["common_left_boundary"],
        "certificate refusal boundary drift",
    )
    for relative, expected in certificate.get("hashes", {}).items():
        path = HERE / relative
        require(path.is_file(), f"hashed artifact absent: {relative}")
        require(sha256(path) == expected,
                f"artifact hash drift: {relative}")


def verify_receipt(receipt: dict) -> None:
    require(
        receipt.get("schema")
        == "phase3-axial-h4-plucker-radial-refinement-receipt-v1",
        "receipt schema drift",
    )
    require(
        receipt.get("certificate_sha256") == sha256(CERTIFICATE),
        "receipt certificate hash drift",
    )
    commands = receipt.get("commands", [])
    require(len(commands) == 3, "receipt command count drift")
    require(
        [entry.get("status") for entry in commands]
        == ["PASS_EXPECTED_TYPED_OBSTRUCTION", "PASS", "PASS"],
        "receipt command status drift",
    )
    require(
        all(entry.get("elapsed_milliseconds", 0) > 0 for entry in commands),
        "receipt elapsed time absent",
    )


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    receipt = json.loads(RECEIPT.read_text())
    result = verify_manifest(manifest)
    verify_certificate(certificate, result)
    verify_receipt(receipt)
    print(
        f"verified=true status={result['status']} "
        f"attempts={len(result['attempts'])} "
        f"common_left={result['common_left_boundary']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
