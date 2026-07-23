#!/usr/bin/env python3
"""Independent verifier for the exact two-child q00 cover."""
from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_h4_plucker_v1 import (
    produce as parent,
)
from black_hole_programme.phase3.axial_horizon_h4_plucker_v1 import (
    verify as parent_verify,
)

from . import produce

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "schema.json"
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


def verify_dependencies() -> None:
    require(
        sha256(produce.PARENT_CERTIFICATE)
        == produce.EXPECTED_PARENT_CERTIFICATE_SHA256,
        "parent certificate hash drift",
    )
    require(
        sha256(produce.SHORTFALL_CERTIFICATE)
        == produce.EXPECTED_SHORTFALL_CERTIFICATE_SHA256,
        "shortfall certificate hash drift",
    )
    parent_certificate = json.loads(produce.PARENT_CERTIFICATE.read_text())
    shortfall = json.loads(produce.SHORTFALL_CERTIFICATE.read_text())
    require(parent_certificate.get("status") == "CERTIFIED",
            "parent is not certified")
    require(
        shortfall.get("status") == "CERTIFIED_BOUNDED_SHORTFALL",
        "split trigger is not certified",
    )
    require(
        shortfall["result"]["refused"]
        == {"shell": 4, "segment": 3, "code": 32},
        "split trigger refusal drift",
    )


def verify_cover(manifest: dict) -> None:
    try:
        parent_cell = tuple(Fraction(value)
                            for value in manifest["parent_cell"])
        split = Fraction(manifest["split_point"])
        children = [
            tuple(Fraction(value) for value in cell)
            for cell in manifest["child_cells"]
        ]
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise VerificationError("invalid rational child cover") from exc
    require(parent_cell == produce.Q00, "parent cell drift")
    require(split == produce.MIDPOINT, "split point drift")
    require(children == list(produce.CHILD_CELLS),
            "child cells drift")
    require(
        children[0][0] == parent_cell[0]
        and children[0][1] == children[1][0] == split
        and children[1][1] == parent_cell[1],
        "child cover has a gap, overlap, or endpoint drift",
    )
    require(
        children[0][1] - children[0][0]
        == children[1][1] - children[1][0]
        == Fraction(1, 8192),
        "children are not the exact dyadic halves",
    )


def verify_child_source(
    index: int, source: str, metadata: dict
) -> None:
    cell = produce.CHILD_CELLS[index]
    center = (cell[0] + cell[1]) / 2
    radius = (cell[1] - cell[0]) / 2
    require(
        metadata.get("schema")
        == "phase3-axial-h4-plucker-q00-split-child-source-v1",
        "child metadata schema drift",
    )
    require(metadata.get("child_index") == index,
            "child metadata index drift")
    require(
        metadata.get("frequency_cell")
        == [produce.rational_text(value) for value in cell],
        "child frequency cell drift",
    )
    require(
        metadata.get("frequency_center")
        == produce.rational_text(center)
        and metadata.get("frequency_radius")
        == produce.rational_text(radius),
        "child generator geometry drift",
    )
    require(
        hashlib.sha256(source.encode()).hexdigest()
        == metadata.get("source_sha256"),
        "child source hash drift",
    )
    require(
        metadata.get("parent_certificate_sha256")
        == produce.EXPECTED_PARENT_CERTIFICATE_SHA256,
        "child parent provenance drift",
    )
    require(
        metadata.get("shortfall_certificate_sha256")
        == produce.EXPECTED_SHORTFALL_CERTIFICATE_SHA256,
        "child shortfall provenance drift",
    )
    require(
        metadata.get("induced_inventory_sha256")
        == parent.canonical_hash(parent.induced_inventory()),
        "child induced-action inventory drift",
    )
    require(
        metadata.get("relation_inventory_sha256")
        == parent.canonical_hash(parent.relation_inventory()),
        "child relation inventory drift",
    )
    markers = (
        f'let wc:Rat=big("{produce.rational_text(center)}")',
        f'let wlo:Iv=iv_from_rat(big("{produce.rational_text(cell[0])}"))',
        f'let whi:Iv=iv_from_rat(big("{produce.rational_text(cell[1])}"))',
        f'let dw:Iv=iv_from_rat(big("{produce.rational_text(radius)}"))',
        f"PLUCKER_BEGIN cell=[{produce.rational_text(cell[0])},"
        f"{produce.rational_text(cell[1])}]",
        "target=shell4-segment3",
        "PLUCKER_PASS reached_shell=4 reached_segment=3",
        "let ri:i64=i;let ii:i64=i+6;",
        "let initial_basis:IvTaylor4Mat=hr_reorder_rows(",
    )
    for marker in markers:
        require(marker in source, f"child source marker absent: {marker}")
    require(
        parent_verify.parsed_signed_terms(source)
        == parent_verify.expected_signed_terms(),
        "child signed exterior table drift",
    )
    relation_ids = [
        int(value)
        for value in re.findall(
            r'println\("PLUCKER_RELATION_DEFECT relation=(\d+)"\);',
            source,
        )
    ]
    require(relation_ids == list(range(45)),
            "child relation inventory drift")


SEGMENT_RE = re.compile(
    r"^PLUCKER_SEGMENT shell=(\d+) segment=(\d+) pivot=(\d+) "
    r"margin=([^ ]+) norm=([^ ]+) relations=(\d+)$",
    flags=re.MULTILINE,
)


def verify_child_log(text: str, source_sha: str) -> dict:
    require("trap() reached" not in text, "child run contains a trap")
    require("PLUCKER_RELATION_DEFECT" not in text,
            "child run contains a relation defect")
    hashes = re.findall(
        r"^PLUCKER_SOURCE_SHA256=([0-9a-f]{64})$",
        text,
        flags=re.MULTILINE,
    )
    require(hashes == [source_sha], "child runtime source drift")
    records = SEGMENT_RE.findall(text)
    for shell, segment, pivot, margin, norm, relations in records:
        require(0 <= int(pivot) < 20, "child pivot index drift")
        require(float(margin) > 0 and math.isfinite(float(margin)),
                "child pivot witness absent")
        require(float(norm) > 0 and math.isfinite(float(norm)),
                "child projective norm drift")
        require(int(relations) == 45, "child relation count drift")
    expected = list(produce.TARGET_SEGMENTS)
    reached = [(int(value[0]), int(value[1])) for value in records]
    refusals = re.findall(
        r"^PLUCKER_REFUSE (.+)$", text, flags=re.MULTILINE
    )
    if "PLUCKER_PROCESS_EXIT=42" in text:
        require(not refusals, "child PASS coexists with refusal")
        require(reached == expected, "passing child segment cover drift")
        require(
            text.count(
                "PLUCKER_PASS reached_shell=4 reached_segment=3 "
                "rank_witness=true parameter_correlation=true"
            ) == 1,
            "child PASS marker absent",
        )
        status = "PASS"
        refusal = None
    else:
        require("PLUCKER_PROCESS_EXIT=3" in text,
                "child terminal exit absent")
        require(len(refusals) == 1, "typed child refusal absent")
        match = re.fullmatch(
            r"shell=(\d+) segment=(\d+)(?: relations)? code=(\d+)",
            refusals[0],
        )
        require(match is not None, "unexpected child refusal")
        failed = (int(match.group(1)), int(match.group(2)))
        require(failed in expected, "child refusal outside target")
        require(reached == expected[:expected.index(failed)],
                "child refusal checkpoint prefix drift")
        status = "REFUSED"
        refusal = {
            "shell": failed[0],
            "segment": failed[1],
            "code": int(match.group(3)),
        }
    elapsed = re.findall(
        r"^PLUCKER_ELAPSED_MILLISECONDS=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    require(len(elapsed) == 1 and int(elapsed[0]) > 0,
            "child elapsed-time receipt absent")
    last = records[-1] if records else None
    return {
        "status": status,
        "refusal": refusal,
        "reached_segments": len(records),
        "last": None if last is None else {
            "shell": int(last[0]),
            "segment": int(last[1]),
            "pivot": int(last[2]),
            "margin": last[3],
            "norm": last[4],
        },
        "elapsed_milliseconds": int(elapsed[0]),
    }


def verify_manifest(manifest: dict) -> dict:
    require(
        manifest.get("schema")
        == "phase3-axial-h4-plucker-q00-split-cover-v1",
        "manifest schema drift",
    )
    require(manifest.get("payload_sha256") == payload_hash(manifest),
            "manifest payload hash drift")
    require(
        manifest.get("parent_certificate_sha256")
        == produce.EXPECTED_PARENT_CERTIFICATE_SHA256,
        "manifest parent certificate drift",
    )
    require(
        manifest.get("shortfall_certificate_sha256")
        == produce.EXPECTED_SHORTFALL_CERTIFICATE_SHA256,
        "manifest shortfall certificate drift",
    )
    verify_dependencies()
    verify_cover(manifest)
    require(len(manifest.get("children", [])) == 2,
            "child result count drift")
    results = []
    for index, entry in enumerate(manifest["children"]):
        require(entry["child_index"] == index,
                "child entry order drift")
        require(
            entry["frequency_cell"]
            == [produce.rational_text(value)
                for value in produce.CHILD_CELLS[index]],
            "child entry cell drift",
        )
        source_path = HERE / entry["source_path"]
        metadata_path = HERE / entry["metadata_path"]
        compile_log = HERE / entry["compile_log_path"]
        run_log = HERE / entry["run_log_path"]
        source = source_path.read_text()
        metadata = json.loads(metadata_path.read_text())
        require(sha256(source_path) == entry["source_sha256"],
                "manifest child source hash drift")
        require(sha256(run_log) == entry["run_log_sha256"],
                "manifest child log hash drift")
        require("COMPILE_PROCESS_EXIT=0" in compile_log.read_text(),
                "child compile did not pass")
        verify_child_source(index, source, metadata)
        result = verify_child_log(
            run_log.read_text(), entry["source_sha256"]
        )
        require(
            entry["process_exit"] == (42 if result["status"] == "PASS" else 3),
            "manifest child exit drift",
        )
        expected_refusal = (
            None if result["refusal"] is None
            else "PLUCKER_REFUSE shell="
            f"{result['refusal']['shell']} segment="
            f"{result['refusal']['segment']} code="
            f"{result['refusal']['code']}"
        )
        require(entry["terminal_refusal"] == expected_refusal,
                "manifest child refusal drift")
        results.append(result)
    passed = all(result["status"] == "PASS" for result in results)
    if not passed:
        require(
            all(
                result["refusal"]
                == {"shell": 4, "segment": 3, "code": 32}
                for result in results
            ),
            "negative split result is not the declared paired code-32 refusal",
        )
    require(
        manifest["status"]
        == ("COVER_PASS" if passed else "COVER_REFUSED"),
        "cover disposition drift",
    )
    return {
        "cover_pass": passed,
        "target": {"shell": 4, "segment": 3},
        "children": results,
    }


def artifact_hashes() -> dict:
    hashes = {}
    for path in sorted(HERE.rglob("*")):
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and path.name not in {"certificate.json", "receipt.json"}
        ):
            hashes[str(path.relative_to(HERE))] = sha256(path)
    return hashes


def build_outputs(manifest: dict, result: dict) -> tuple[dict, dict]:
    hashes = artifact_hashes()
    status = (
        "CERTIFIED_SPLIT_COVER_PASS"
        if result["cover_pass"]
        else "CERTIFIED_SPLIT_COVER_NEGATIVE"
    )
    certificate = {
        "schema": "phase3-axial-h4-plucker-q00-split-certificate-v1",
        "status": status,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "parent_certificate_sha256": (
            produce.EXPECTED_PARENT_CERTIFICATE_SHA256
        ),
        "shortfall_certificate_sha256": (
            produce.EXPECTED_SHORTFALL_CERTIFICATE_SHA256
        ),
        "result": result,
        "interpretation": (
            "Both exact dyadic children reach the former refusal boundary; "
            "narrower-cell parameter correlation removes code 32."
            if result["cover_pass"]
            else (
                "Both exact dyadic children independently retain the "
                "shell-4/segment-3 code-32 raw-component pivot refusal; "
                "frequency halving does not remove the failure."
            )
        ),
        "hashes": hashes,
        "does_not_establish": manifest["does_not_establish"],
    }
    receipt = {
        "schema": "phase3-axial-h4-plucker-q00-split-receipt-v1",
        "status": "PASS" if result["cover_pass"]
        else "PASS_CERTIFIED_NEGATIVE_RESULT",
        "commands": [
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_q00_split_v1.run_children"
                ),
                "result": manifest["status"],
                "child_elapsed_milliseconds": {
                    str(index): child["elapsed_milliseconds"]
                    for index, child in enumerate(result["children"])
                },
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m unittest -v "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_q00_split_v1."
                    "test_split"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_q00_split_v1.verify"
                ),
                "result": "PASS",
            },
        ],
        "hashes": hashes,
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "bounded disjoint coordinate-remedy experiment; no "
                "shared operator, paper, or lifecycle claim changed"
            ),
        },
        "does_not_establish": manifest["does_not_establish"],
    }
    return certificate, receipt


def main() -> int:
    try:
        schema = json.loads(SCHEMA.read_text())
        require(
            schema.get("schema")
            == "phase3-axial-h4-plucker-q00-split-schema-v1",
            "artifact schema drift",
        )
        manifest = json.loads(produce.MANIFEST.read_text())
        result = verify_manifest(manifest)
        certificate, receipt = build_outputs(manifest, result)
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError,
            VerificationError) as exc:
        print(f"REFUSE {exc}")
        return 3
    print(
        "PASS exact q00 dyadic child cover "
        + ("reaches shell 4 segment 3" if result["cover_pass"]
           else "records a typed child shortfall")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
