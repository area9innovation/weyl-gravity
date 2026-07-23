#!/usr/bin/env python3
"""Independent verifier for the bounded correlated-functional replay."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_h4_plucker_q00_split_v1 import (
    produce as split,
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


def hermitian_real(
    midpoint: list[complex], value: list[complex]
) -> float:
    """Reference real part of sum conjugate(midpoint_j) value_j."""
    require(len(midpoint) == len(value), "reference vector length drift")
    return float(sum(
        (p.conjugate() * q).real for p, q in zip(midpoint, value)
    ))


def coordinate_real(
    midpoint: list[complex], value: list[complex]
) -> float:
    """The real-coordinate formula implemented by the Forge source."""
    require(len(midpoint) == len(value), "coordinate vector length drift")
    return float(sum(
        p.real * q.real + p.imag * q.imag
        for p, q in zip(midpoint, value)
    ))


def verify_dependencies() -> dict:
    require(
        sha256(produce.SPLIT_CERTIFICATE)
        == produce.EXPECTED_SPLIT_CERTIFICATE_SHA256,
        "split certificate hash drift",
    )
    require(
        sha256(produce.SPLIT_MANIFEST)
        == produce.EXPECTED_SPLIT_MANIFEST_SHA256,
        "split manifest hash drift",
    )
    certificate = json.loads(produce.SPLIT_CERTIFICATE.read_text())
    manifest = json.loads(produce.SPLIT_MANIFEST.read_text())
    require(
        certificate.get("status") == "CERTIFIED_SPLIT_COVER_NEGATIVE",
        "split negative result is not certified",
    )
    require(manifest.get("status") == "COVER_REFUSED",
            "split refusal manifest drift")
    require(len(manifest.get("children", [])) == 2,
            "split child count drift")
    return manifest


SEGMENT_RE = re.compile(
    r"^PLUCKER_SEGMENT shell=(\d+) segment=(\d+) pivot=(\d+) "
    r"margin=([^ ]+) norm=([^ ]+) relations=(\d+)$",
    flags=re.MULTILINE,
)
DEFECT_RE = re.compile(
    r"^CORRELATED_FUNCTIONAL_DEFECT "
    r"lo=([^ ]+) hi=([^ ]+) norm=([^ ]+)$",
    flags=re.MULTILINE,
)


def heartbeat_lines(text: str) -> list[str]:
    return [
        line for line in text.splitlines()
        if line.startswith("PLUCKER_SEGMENT ")
    ]


def verify_source(
    index: int, source_path: Path, metadata: dict, split_entry: dict
) -> None:
    source = source_path.read_text()
    require(
        metadata.get("schema")
        == "phase3-axial-h4-plucker-correlated-child-source-v1",
        "child source schema drift",
    )
    require(metadata.get("child_index") == index,
            "child source index drift")
    require(metadata.get("frequency_cell") == split_entry["frequency_cell"],
            "child frequency cell drift")
    require(
        metadata.get("split_source_sha256")
        == split_entry["source_sha256"],
        "split source provenance drift",
    )
    require(
        metadata.get("split_run_log_sha256")
        == split_entry["run_log_sha256"],
        "split run provenance drift",
    )
    require(
        hashlib.sha256(source.encode()).hexdigest()
        == metadata.get("source_sha256"),
        "child source hash drift",
    )
    require(source == produce.render_child(index),
            "child source is not the exact bounded derivation")
    markers = (
        "fn pl_correlated_pivot(a:borrow IvTaylor4Mat)->PlPivot{",
        "let ar:Rat=rat_clone(qm_get(a.c0,i,0));",
        "let ai:Rat=rat_clone(qm_get(a.c0,i+20,0));",
        "let tx:IvTaylor4Result=ivtm4_scale_rat_checked(xr,ar);",
        "let ty:IvTaylor4Result=ivtm4_scale_rat_checked(xi,ai);",
        "CORRELATED_FUNCTIONAL_DEFECT lo={} hi={} norm={}",
        "return PlPivot(false,-1,0.0,norm,35);",
        "pl_correlated_attempt(4,3,cell,state)",
        "rank_witness=midpoint-hermitian",
    )
    for marker in markers:
        require(marker in source, f"correlated source marker absent: {marker}")
    require(
        source.count("pl_correlated_attempt(4,3,cell,state)") == 1,
        "correlated replay scope drift",
    )
    require(
        "pl_attempt(4,3,cell,state)" not in source,
        "raw target-boundary call remains",
    )


def verify_log(
    text: str, source_sha: str, split_text: str
) -> dict:
    require("trap() reached" not in text, "correlated run contains a trap")
    require("PLUCKER_RELATION_DEFECT" not in text,
            "correlated run contains a relation defect")
    hashes = re.findall(
        r"^PLUCKER_SOURCE_SHA256=([0-9a-f]{64})$",
        text,
        flags=re.MULTILINE,
    )
    require(hashes == [source_sha], "runtime source hash drift")

    original_prefix = heartbeat_lines(split_text)
    current = heartbeat_lines(text)
    require(len(original_prefix) == 19,
            "split prefix heartbeat count drift")
    require(
        current[:19] == original_prefix,
        "pre-boundary replay heartbeat drift",
    )
    for shell, segment, pivot, margin, norm, relations in SEGMENT_RE.findall(
        text
    ):
        require(float(margin) > 0 and math.isfinite(float(margin)),
                "positive witness margin absent")
        require(float(norm) > 0 and math.isfinite(float(norm)),
                "positive projective norm absent")
        require(int(relations) == 45, "relation count drift")
        if (int(shell), int(segment)) != (4, 3):
            require(0 <= int(pivot) < 20, "raw pivot index drift")

    defects = DEFECT_RE.findall(text)
    refusal = re.findall(
        r"^PLUCKER_REFUSE shell=4 segment=3 code=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    passed = "PLUCKER_PROCESS_EXIT=42" in text
    if passed:
        require(len(current) == 20, "passing heartbeat count drift")
        require(current[-1].startswith(
            "PLUCKER_SEGMENT shell=4 segment=3 pivot=20 "
        ), "correlated PASS witness drift")
        require(not defects and not refusal,
                "passing run contains refusal evidence")
        require(
            text.count(
                "PLUCKER_PASS reached_shell=4 reached_segment=3 "
                "rank_witness=midpoint-hermitian "
                "parameter_correlation=true"
            ) == 1,
            "correlated PASS marker absent",
        )
        status = "PASS"
        defect = None
    else:
        require("PLUCKER_PROCESS_EXIT=3" in text,
                "typed correlated exit absent")
        require(len(current) == 19,
                "refused replay crossed the target boundary")
        require(refusal == ["35"], "typed code-35 refusal absent")
        require(len(defects) == 1,
                "correlated functional defect evidence absent")
        lo, hi, norm = map(float, defects[0])
        require(
            all(math.isfinite(value) for value in (lo, hi, norm)),
            "nonfinite correlated defect",
        )
        require(lo <= 0 <= hi, "code-35 interval does not contain zero")
        require(norm > 0, "correlated defect projective norm absent")
        status = "REFUSED"
        defect = {
            "lo": defects[0][0],
            "hi": defects[0][1],
            "norm": defects[0][2],
        }
    elapsed = re.findall(
        r"^PLUCKER_ELAPSED_MILLISECONDS=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    require(len(elapsed) == 1 and int(elapsed[0]) > 0,
            "elapsed-time receipt absent")
    return {
        "status": status,
        "refusal": (
            None if passed else {"shell": 4, "segment": 3, "code": 35}
        ),
        "defect": defect,
        "prefix_heartbeats": 19,
        "elapsed_milliseconds": int(elapsed[0]),
    }


def verify_manifest(manifest: dict) -> dict:
    require(
        manifest.get("schema")
        == "phase3-axial-h4-plucker-correlated-functional-manifest-v1",
        "manifest schema drift",
    )
    require(manifest.get("payload_sha256") == payload_hash(manifest),
            "manifest payload hash drift")
    require(
        manifest.get("split_certificate_sha256")
        == produce.EXPECTED_SPLIT_CERTIFICATE_SHA256,
        "manifest split certificate drift",
    )
    require(
        manifest.get("split_manifest_sha256")
        == produce.EXPECTED_SPLIT_MANIFEST_SHA256,
        "manifest split manifest drift",
    )
    require(
        manifest.get("scope") == {
            "children": [0, 1],
            "replayed_boundary": {"shell": 4, "segment": 3},
            "no_later_shell": True,
        },
        "bounded replay scope drift",
    )
    split_manifest = verify_dependencies()
    entries = manifest.get("children", [])
    require(len(entries) == 2, "correlated child count drift")
    results = []
    for index, entry in enumerate(entries):
        require(entry.get("child_index") == index,
                "correlated child order drift")
        split_entry = split_manifest["children"][index]
        require(entry.get("frequency_cell")
                == split_entry["frequency_cell"],
                "manifest child frequency cell drift")
        source_path = HERE / entry["source_path"]
        metadata_path = HERE / entry["metadata_path"]
        compile_path = HERE / entry["compile_log_path"]
        run_path = HERE / entry["run_log_path"]
        metadata = json.loads(metadata_path.read_text())
        require(sha256(source_path) == entry["source_sha256"],
                "manifest source hash drift")
        require(sha256(run_path) == entry["run_log_sha256"],
                "manifest run-log hash drift")
        require("COMPILE_PROCESS_EXIT=0" in compile_path.read_text(),
                "correlated child compile did not pass")
        verify_source(index, source_path, metadata, split_entry)
        split_log = (split.HERE / split_entry["run_log_path"]).read_text()
        result = verify_log(
            run_path.read_text(), entry["source_sha256"], split_log
        )
        require(
            entry["process_exit"]
            == (42 if result["status"] == "PASS" else 3),
            "manifest process exit drift",
        )
        expected_terminal = (
            [] if result["status"] == "PASS"
            else [
                "CORRELATED_FUNCTIONAL_DEFECT "
                f"lo={result['defect']['lo']} "
                f"hi={result['defect']['hi']} "
                f"norm={result['defect']['norm']}",
                "PLUCKER_REFUSE shell=4 segment=3 code=35",
            ]
        )
        require(entry["terminal_evidence"] == expected_terminal,
                "manifest terminal evidence drift")
        results.append(result)
    passed = all(result["status"] == "PASS" for result in results)
    require(
        manifest["status"]
        == ("CORRELATED_PASS" if passed else "CORRELATED_REFUSED"),
        "correlated disposition drift",
    )
    if not passed:
        require(
            all(result["status"] == "REFUSED" for result in results),
            "mixed child disposition is not this declared result",
        )
    return {
        "correlated_pass": passed,
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
    certificate = {
        "schema": (
            "phase3-axial-h4-plucker-correlated-functional-certificate-v1"
        ),
        "status": (
            "CERTIFIED_CORRELATED_FUNCTIONAL_PASS"
            if result["correlated_pass"]
            else "CERTIFIED_CORRELATED_FUNCTIONAL_OBSTRUCTION"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "split_certificate_sha256": (
            produce.EXPECTED_SPLIT_CERTIFICATE_SHA256
        ),
        "split_manifest_sha256": produce.EXPECTED_SPLIT_MANIFEST_SHA256,
        "result": result,
        "interpretation": (
            "The midpoint-Hermitian functional certifies a projective "
            "section on both q00 children at shell 4 segment 3."
            if result["correlated_pass"]
            else (
                "On both exact q00 children, the validated enclosure of "
                "the midpoint-Hermitian functional contains zero at shell "
                "4 segment 3. This is an enclosure obstruction, not a "
                "rank-loss theorem."
            )
        ),
        "hashes": hashes,
        "does_not_establish": manifest["does_not_establish"],
    }
    receipt = {
        "schema": (
            "phase3-axial-h4-plucker-correlated-functional-receipt-v1"
        ),
        "status": (
            "PASS" if result["correlated_pass"]
            else "PASS_CERTIFIED_NEGATIVE_RESULT"
        ),
        "commands": [
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_correlated_functional_v1."
                    "run_children"
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
                    "axial_horizon_h4_plucker_correlated_functional_v1."
                    "test_correlated"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_correlated_functional_v1."
                    "verify"
                ),
                "result": "PASS",
            },
        ],
        "hashes": hashes,
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "bounded disjoint projective-coordinate experiment; no "
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
            == (
                "phase3-axial-h4-plucker-correlated-functional-schema-v1"
            ),
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
    except (
        OSError, KeyError, ValueError, json.JSONDecodeError,
        VerificationError,
    ) as exc:
        print(f"REFUSE {exc}")
        return 3
    print(
        "PASS correlated midpoint-Hermitian replay "
        + ("certifies both children" if result["correlated_pass"]
           else "records the paired code-35 enclosure obstruction")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
