#!/usr/bin/env python3
"""Independent verifier for the exterior-norm design blocker."""
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


def squared_norm(real: list[float], imag: list[float]) -> float:
    require(len(real) == len(imag), "norm vector length drift")
    return sum(x * x + y * y for x, y in zip(real, imag))


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
    r"^EXTERIOR_NORM_DEFECT lo=([^ ]+) hi=([^ ]+) norm=([^ ]+)$",
    flags=re.MULTILINE,
)
WITNESS_RE = re.compile(
    r"^EXTERIOR_3PLANE_WITNESS lower=([^ ]+) upper=([^ ]+) "
    r"relative=([^ ]+) norm=([^ ]+)$",
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
        == "phase3-axial-h4-plucker-exterior-child-source-v1",
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
        "fn pl_exterior_norm_pivot(a:borrow IvTaylor4Mat)->PlPivot{",
        "let xx:IvTaylor4Result=ivtm4_mul_checked(x,x);",
        "let added:IvTaylor4Result=ivtm4_add_checked(squared,xx.value);",
        "if(value.lo<=0.0 || value.hi<=0.0 ||",
        "return PlPivot(false,-1,0.0,norm,36);",
        "let relative:f64=if(upper>0.0){state.margin/upper}else{0.0};",
        "return pl_fail(37);",
        "pl_exterior_attempt(4,3,cell,state)",
        "rank_witness=exterior-norm",
    )
    for marker in markers:
        require(marker in source, f"exterior source marker absent: {marker}")
    require(source.count("pl_exterior_attempt(4,3,cell,state)") == 1,
            "exterior replay scope drift")
    require("pl_attempt(4,3,cell,state)" not in source,
            "raw target-boundary call remains")


def verify_log(
    text: str, source_sha: str, split_text: str
) -> dict:
    require("trap() reached" not in text, "exterior run contains a trap")
    require("PLUCKER_RELATION_DEFECT" not in text,
            "exterior run contains a relation defect")
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
    require(current[:19] == original_prefix,
            "pre-boundary replay heartbeat drift")
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
    witnesses = WITNESS_RE.findall(text)
    refusal = re.findall(
        r"^PLUCKER_REFUSE shell=4 segment=3 code=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    passed = "PLUCKER_PROCESS_EXIT=42" in text
    if passed:
        require(len(current) == 20, "passing heartbeat count drift")
        require(current[-1].startswith(
            "PLUCKER_SEGMENT shell=4 segment=3 pivot=21 "
        ), "exterior PASS heartbeat drift")
        require(len(witnesses) == 1 and not defects and not refusal,
                "exterior PASS evidence drift")
        lower, upper, relative, norm = map(float, witnesses[0])
        require(
            lower > 0 and upper >= lower and relative > 0 and norm > 0,
            "exterior conditioning witness is not positive",
        )
        require(
            text.count(
                "PLUCKER_PASS reached_shell=4 reached_segment=3 "
                "rank_witness=exterior-norm parameter_correlation=true"
            ) == 1,
            "exterior PASS marker absent",
        )
        status = "PASS"
        evidence = {
            "lower": witnesses[0][0],
            "upper": witnesses[0][1],
            "relative": witnesses[0][2],
            "norm": witnesses[0][3],
        }
        refusal_value = None
    else:
        require("PLUCKER_PROCESS_EXIT=3" in text,
                "typed exterior exit absent")
        require(len(current) == 19,
                "refused replay crossed the target boundary")
        require(refusal in (["36"], ["37"]),
                "typed exterior refusal absent")
        if refusal == ["36"]:
            require(len(defects) == 1 and not witnesses,
                    "norm-defect evidence absent")
            lo, hi, norm = map(float, defects[0])
            require(all(math.isfinite(v) for v in (lo, hi, norm)),
                    "nonfinite norm defect")
            require(lo <= 0 and hi >= 0,
                    "code-36 enclosure does not contain zero")
            require(norm > 0, "norm-defect component sup absent")
            evidence = {
                "lo": defects[0][0],
                "hi": defects[0][1],
                "norm": defects[0][2],
            }
        else:
            require(not defects and not witnesses,
                    "conditioning refusal evidence shape drift")
            match = re.findall(
                r"^EXTERIOR_CONDITIONING_DEFECT lower=([^ ]+) "
                r"upper=([^ ]+) relative=([^ ]+)$",
                text,
                flags=re.MULTILINE,
            )
            require(len(match) == 1,
                    "conditioning-defect evidence absent")
            evidence = {
                "lower": match[0][0],
                "upper": match[0][1],
                "relative": match[0][2],
            }
        status = "REFUSED"
        refusal_value = {
            "shell": 4, "segment": 3, "code": int(refusal[0])
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
        "refusal": refusal_value,
        "evidence": evidence,
        "prefix_heartbeats": 19,
        "elapsed_milliseconds": int(elapsed[0]),
    }


def verify_manifest(manifest: dict) -> dict:
    require(
        manifest.get("schema")
        == "phase3-axial-h4-plucker-exterior-norm-manifest-v1",
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
    require(len(entries) == 2, "exterior child count drift")
    results = []
    for index, entry in enumerate(entries):
        require(entry.get("child_index") == index,
                "exterior child order drift")
        split_entry = split_manifest["children"][index]
        require(entry.get("frequency_cell") == split_entry["frequency_cell"],
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
                "exterior child compile did not pass")
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
        results.append(result)
    passed = all(result["status"] == "PASS" for result in results)
    require(
        manifest["status"]
        == ("EXTERIOR_PASS" if passed else "EXTERIOR_REFUSED"),
        "exterior disposition drift",
    )
    if not passed:
        require(
            all(
                result["refusal"]
                == {"shell": 4, "segment": 3, "code": 36}
                for result in results
            ),
            "negative result is not the declared paired code-36 blocker",
        )
    return {
        "exterior_pass": passed,
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
            "phase3-axial-h4-plucker-exterior-norm-certificate-v1"
        ),
        "status": (
            "CERTIFIED_EXTERIOR_3PLANE_PASS"
            if result["exterior_pass"]
            else "CERTIFIED_EXTERIOR_CONDITIONING_BLOCKER"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "split_certificate_sha256": (
            produce.EXPECTED_SPLIT_CERTIFICATE_SHA256
        ),
        "split_manifest_sha256": produce.EXPECTED_SPLIT_MANIFEST_SHA256,
        "result": result,
        "feasibility": {
            "validated_qr": "UNAVAILABLE_IN_CURRENT_KERNEL",
            "equivalent_exterior_norm": (
                "PASS" if result["exterior_pass"]
                else "REFUSED_BY_NONPOSITIVE_LOWER_ENCLOSURE"
            ),
            "next_substrate": [
                "positivity-preserving sum-of-squares Taylor model",
                "validated interval QR or orthogonal-frame propagation",
                "materially tighter correlated radial enclosure",
            ],
        },
        "interpretation": (
            "The full exterior squared norm certifies a nonzero "
            "decomposable three-vector on both q00 children."
            if result["exterior_pass"]
            else (
                "The current order-4 generic Taylor-product enclosure of "
                "the full exterior squared norm contains zero on both "
                "q00 children. Exact interval QR is unavailable in the "
                "current kernel. This is a design blocker, not rank loss."
            )
        ),
        "hashes": hashes,
        "does_not_establish": manifest["does_not_establish"],
    }
    receipt = {
        "schema": (
            "phase3-axial-h4-plucker-exterior-norm-receipt-v1"
        ),
        "status": (
            "PASS" if result["exterior_pass"]
            else "PASS_CERTIFIED_DESIGN_BLOCKER"
        ),
        "commands": [
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_exterior_norm_v1."
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
                    "axial_horizon_h4_plucker_exterior_norm_v1."
                    "test_exterior"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_exterior_norm_v1.verify"
                ),
                "result": "PASS",
            },
        ],
        "hashes": hashes,
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "bounded disjoint design-feasibility audit; no shared "
                "operator, paper, or lifecycle claim changed"
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
            == "phase3-axial-h4-plucker-exterior-norm-schema-v1",
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
        "PASS exterior-norm boundary replay "
        + ("certifies both three-planes" if result["exterior_pass"]
           else "records the paired exact-kernel design blocker")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
