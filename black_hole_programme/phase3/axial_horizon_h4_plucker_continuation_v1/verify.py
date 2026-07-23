#!/usr/bin/env python3
"""Independent join verifier for the bounded Plücker continuation."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from fractions import Fraction
from pathlib import Path

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


STATE_RE = re.compile(
    r"^PLSTATE row=(\d+) c0=([^ ]+) c1=([^ ]+) c2=([^ ]+) "
    r"c3=([^ ]+) c4=([^ ]+) rlo=(-?\d+) rhi=(-?\d+)$",
    flags=re.MULTILINE,
)


def parse_log_state(text: str) -> list[dict]:
    matches = STATE_RE.findall(text)
    require(len(matches) == 40, "shared-state row count drift")
    output = []
    for expected, match in enumerate(matches):
        row, *fields = match
        require(int(row) == expected, "shared-state row order drift")
        coefficients = fields[:5]
        try:
            for coefficient in coefficients:
                Fraction(coefficient)
        except (ValueError, ZeroDivisionError) as exc:
            raise VerificationError("invalid exact state coefficient") from exc
        lo_bits, hi_bits = int(fields[5]), int(fields[6])
        lo = struct.unpack(">d", struct.pack(">q", lo_bits))[0]
        hi = struct.unpack(">d", struct.pack(">q", hi_bits))[0]
        require(
            math.isfinite(lo) and math.isfinite(hi) and lo <= hi,
            "invalid shared-state interval",
        )
        output.append(
            {
                "row": expected,
                "coefficients": coefficients,
                "remainder_bits": [lo_bits, hi_bits],
            }
        )
    return output


def verify_predecessor(expected_hash: str) -> dict:
    require(
        sha256(produce.PREDECESSOR_CERTIFICATE) == expected_hash,
        "predecessor certificate hash drift",
    )
    certificate = json.loads(produce.PREDECESSOR_CERTIFICATE.read_text())
    require(certificate.get("status") == "CERTIFIED",
            "predecessor not certified")
    require(
        sha256(produce.PREDECESSOR_SOURCE)
        == produce.EXPECTED_PREDECESSOR_SOURCE_SHA256,
        "predecessor source hash drift",
    )
    require(
        certificate["hashes"]["plucker_q00_preflight.forge"]
        == produce.EXPECTED_PREDECESSOR_SOURCE_SHA256,
        "predecessor certificate/source binding drift",
    )
    return certificate


def verify_state(
    state: dict,
    expected_position: dict,
    expected_input_hash: str | None,
    source: Path,
    log: Path,
) -> None:
    require(
        state.get("schema")
        == "phase3-axial-h4-plucker-shared-state-v1",
        "shared-state schema drift",
    )
    require(state.get("status") == "CERTIFIED_ENCLOSURE_HANDOFF",
            "shared-state status drift")
    require(state.get("payload_sha256") == payload_hash(state),
            "shared-state payload hash drift")
    require(state.get("position") == expected_position,
            "shared-state position drift")
    require(state.get("input_state_sha256") == expected_input_hash,
            "shared-state predecessor join drift")
    require(state.get("producer_source_sha256") == sha256(source),
            "shared-state producer source drift")
    require(state.get("producer_log_sha256") == sha256(log),
            "shared-state producer log drift")
    require(state.get("rows") == parse_log_state(log.read_text()),
            "shared-state/log content drift")


COEFFICIENT_RE = re.compile(
    r'^\s+c([0-4])=qm_set\(c\1,(\d+),0,big\("([^"]+)"\)\);$',
    flags=re.MULTILINE,
)
REMAINDER_RE = re.compile(
    r"^\s+ivm_set\(rem,(\d+),0,iv\(f64_from_bits\((-?\d+)\),"
    r"f64_from_bits\((-?\d+)\)\)\);$",
    flags=re.MULTILINE,
)


def parse_source_builder(source: str) -> list[dict]:
    coefficients: dict[int, dict[int, str]] = {}
    for degree, row, value in COEFFICIENT_RE.findall(source):
        coefficients.setdefault(int(row), {})[int(degree)] = value
    remainders = {
        int(row): [int(lo), int(hi)]
        for row, lo, hi in REMAINDER_RE.findall(source)
    }
    require(
        set(coefficients) == set(range(40))
        and set(remainders) == set(range(40)),
        "chunk input builder row inventory drift",
    )
    output = []
    for row in range(40):
        require(
            set(coefficients[row]) == set(range(5)),
            "chunk input builder degree inventory drift",
        )
        output.append(
            {
                "row": row,
                "coefficients": [
                    coefficients[row][degree] for degree in range(5)
                ],
                "remainder_bits": remainders[row],
            }
        )
    return output


SEGMENT_RE = re.compile(
    r"^PLCHUNK_SEGMENT shell=(\d+) segment=(\d+) pivot=(\d+) "
    r"margin=([^ ]+) norm=([^ ]+) relations=(\d+)$",
    flags=re.MULTILINE,
)


def segment_records(text: str) -> list[tuple[int, int, int, float, float]]:
    records = []
    for shell, segment, pivot, margin, norm, relations in (
        SEGMENT_RE.findall(text)
    ):
        require(0 <= int(pivot) < 20, "chunk pivot index drift")
        require(float(margin) > 0 and math.isfinite(float(margin)),
                "chunk nonzero pivot witness absent")
        require(float(norm) > 0 and math.isfinite(float(norm)),
                "chunk projective norm drift")
        require(int(relations) == 45, "chunk relation count drift")
        records.append(
            (int(shell), int(segment), int(pivot),
             float(margin), float(norm))
        )
    return records


def verify_exporter(manifest: dict) -> dict:
    exporter = manifest["exporter"]
    source = HERE / exporter["source_path"]
    log = HERE / exporter["log_path"]
    state_path = HERE / exporter["output_state_path"]
    require(sha256(source) == exporter["source_sha256"],
            "exporter source hash drift")
    require(sha256(log) == exporter["log_sha256"],
            "exporter log hash drift")
    source_text = source.read_text()
    require(source_text == produce.render_exporter(),
            "exporter is not the exact instrumented predecessor")
    predecessor_segments = re.findall(
        r"^PLUCKER_SEGMENT .*$",
        produce.PREDECESSOR_LOG.read_text(),
        flags=re.MULTILINE,
    )
    exporter_segments = re.findall(
        r"^PLUCKER_SEGMENT .*$", log.read_text(), flags=re.MULTILINE
    )
    require(exporter_segments == predecessor_segments,
            "exporter did not reproduce predecessor checkpoints")
    require("PLUCKER_PROCESS_EXIT=42" in log.read_text(),
            "exporter success exit absent")
    state = json.loads(state_path.read_text())
    verify_state(
        state, {"shell": 3, "segment": 0}, None, source, log
    )
    require(state["payload_sha256"] == exporter["output_state_sha256"],
            "exporter state binding drift")
    return state


def verify_chunk(
    entry: dict,
    input_state: dict,
) -> tuple[str, dict | None, list[tuple[int, int, int, float, float]]]:
    source_path = HERE / entry["source_path"]
    metadata_path = HERE / entry["metadata_path"]
    compile_log = HERE / entry["compile_log_path"]
    run_log = HERE / entry["run_log_path"]
    source = source_path.read_text()
    metadata = json.loads(metadata_path.read_text())
    log = run_log.read_text()
    require(sha256(source_path) == entry["source_sha256"],
            "chunk source hash drift")
    require(sha256(run_log) == entry["run_log_sha256"],
            "chunk run-log hash drift")
    require("COMPILE_PROCESS_EXIT=0" in compile_log.read_text(),
            "chunk compile did not pass")
    require(metadata["source_sha256"] == entry["source_sha256"],
            "chunk metadata/source drift")
    require(metadata["input_state_sha256"] == input_state["payload_sha256"],
            "chunk metadata input join drift")
    require(
        source.startswith(produce.support_prefix()),
        "chunk support prefix drift",
    )
    require(
        hashlib.sha256(produce.support_prefix().encode()).hexdigest()
        == metadata["support_prefix_sha256"],
        "chunk support-prefix hash drift",
    )
    require(parse_source_builder(source) == input_state["rows"],
            "chunk input builder/state drift")
    hashes = re.findall(
        r"^PLUCKER_SOURCE_SHA256=([0-9a-f]{64})$",
        log,
        flags=re.MULTILINE,
    )
    require(hashes == [entry["source_sha256"]],
            "chunk runtime source provenance drift")
    begin = (
        f"PLCHUNK_BEGIN label={entry['label']} "
        f"input_state_sha256={input_state['payload_sha256']} "
        "predecessor_certificate_sha256="
        f"{produce.EXPECTED_PREDECESSOR_CERTIFICATE_SHA256}"
    )
    require(log.count(begin) == 1, "chunk runtime input join absent")
    records = segment_records(log)
    expected = [tuple(value) for value in entry["segments"]]

    if entry["process_exit"] == 42:
        require(
            [(value[0], value[1]) for value in records] == expected,
            "passing chunk segment sequence drift",
        )
        require("PLCHUNK_REFUSE" not in log,
                "passing chunk contains refusal")
        require(
            log.count(f"PLCHUNK_PASS label={entry['label']}") == 1,
            "chunk PASS absent",
        )
        require("PLUCKER_PROCESS_EXIT=42" in log,
                "chunk success exit absent")
        output_path = HERE / entry["output_state_path"]
        output_state = json.loads(output_path.read_text())
        final = expected[-1]
        verify_state(
            output_state,
            {"shell": final[0], "segment": final[1]},
            input_state["payload_sha256"],
            source_path,
            run_log,
        )
        require(
            output_state["payload_sha256"]
            == entry["output_state_sha256"],
            "chunk output state binding drift",
        )
        return "PASS", output_state, records

    require(entry["process_exit"] == 3,
            "unexpected chunk process exit")
    refusals = re.findall(
        r"^PLCHUNK_REFUSE (.+)$", log, flags=re.MULTILINE
    )
    require(len(refusals) == 1, "typed terminal refusal absent")
    refuse = re.fullmatch(
        r"shell=(\d+) segment=(\d+) code=(\d+)", refusals[0]
    )
    require(refuse is not None, "unexpected terminal refusal format")
    failed = (int(refuse.group(1)), int(refuse.group(2)))
    require(failed in expected, "refusal lies outside chunk scope")
    failed_index = expected.index(failed)
    require(
        [(value[0], value[1]) for value in records]
        == expected[:failed_index],
        "refusal checkpoint prefix drift",
    )
    require(int(refuse.group(3)) == 32,
            "unexpected projective refusal code")
    require("PLCHUNK_PASS" not in log, "refusal coexists with PASS")
    require("PLUCKER_PROCESS_EXIT=3" in log,
            "refusal process exit absent")
    require(not STATE_RE.search(log),
            "refusing chunk emitted an uncertified output state")
    return "HONEST_REFUSAL", None, records


def verify_manifest(manifest: dict) -> dict:
    require(
        manifest.get("schema")
        == "phase3-axial-h4-plucker-join-manifest-v1",
        "join manifest schema drift",
    )
    require(manifest.get("payload_sha256") == payload_hash(manifest),
            "join manifest payload hash drift")
    require(
        manifest.get("predecessor_certificate_sha256")
        == produce.EXPECTED_PREDECESSOR_CERTIFICATE_SHA256,
        "join manifest predecessor hash drift",
    )
    verify_predecessor(manifest["predecessor_certificate_sha256"])
    current = verify_exporter(manifest)
    all_records = []
    terminal = None
    for expected_index, entry in enumerate(manifest["chunks"]):
        require(entry["index"] == expected_index,
                "chunk index sequence drift")
        require(entry["input_state_sha256"] == current["payload_sha256"],
                "chunk state chain drift")
        status, output, records = verify_chunk(entry, current)
        all_records.extend(records)
        if status == "HONEST_REFUSAL":
            terminal = entry
            break
        require(output is not None, "passing chunk lacks output state")
        current = output
    require(terminal is not None, "expected bounded refusal absent")
    require(
        manifest["status"] == "HONEST_REFUSAL"
        and manifest["terminal"]["chunk"] == terminal["label"],
        "manifest terminal disposition drift",
    )
    require(
        manifest["terminal"]["detail"]
        == "shell=4 segment=3 code=32",
        "manifest terminal detail drift",
    )
    require(len(manifest["chunks"]) == terminal["index"] + 1,
            "work continued after first refusal")
    require(
        all_records[-1][:2] == (4, 2),
        "last certified checkpoint drift",
    )
    refusal_log = (
        HERE / terminal["run_log_path"]
    ).read_text()
    require(
        "PLCHUNK_REFUSE shell=4 segment=3 code=32" in refusal_log,
        "expected shell4/segment3 pivot refusal absent",
    )
    return {
        "passing_chunks": terminal["index"],
        "executed_chunks": len(manifest["chunks"]),
        "certified_segments_after_predecessor": len(all_records),
        "reached": {"shell": 4, "segment": 2},
        "refused": {"shell": 4, "segment": 3, "code": 32},
        "last_pivot": all_records[-1][2],
        "last_margin": all_records[-1][3],
        "last_norm": all_records[-1][4],
    }


def artifact_hashes() -> dict:
    names = (
        "produce.py",
        "run_bounded.py",
        "verify.py",
        "test_continuation.py",
        "schema.json",
        "README.md",
        "report.md",
        "join_manifest.json",
        "boundary_exporter.forge",
        "boundary_exporter_run.txt",
    )
    hashes = {name: sha256(HERE / name) for name in names}
    for directory in ("chunks", "states"):
        for path in sorted((HERE / directory).glob("*")):
            if path.is_file():
                hashes[str(path.relative_to(HERE))] = sha256(path)
    compile_log = HERE / "boundary_exporter_compile.txt"
    if compile_log.exists():
        hashes[compile_log.name] = sha256(compile_log)
    return hashes


def build_outputs(manifest: dict, result: dict) -> tuple[dict, dict]:
    hashes = artifact_hashes()
    certificate = {
        "schema": "phase3-axial-h4-plucker-continuation-certificate-v1",
        "status": "CERTIFIED_BOUNDED_SHORTFALL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "predecessor_certificate_sha256": (
            produce.EXPECTED_PREDECESSOR_CERTIFICATE_SHA256
        ),
        "result": result,
        "interpretation": (
            "No raw Pluecker real/imaginary coordinate interval excludes "
            "zero at shell 4 segment 3; this is a projective-pivot "
            "enclosure refusal, not a certified rank loss."
        ),
        "hashes": hashes,
        "does_not_establish": manifest["does_not_establish"],
    }
    elapsed = {}
    for entry in manifest["chunks"]:
        log = (HERE / entry["run_log_path"]).read_text()
        value = re.findall(
            r"^PLUCKER_ELAPSED_MILLISECONDS=(\d+)$",
            log,
            flags=re.MULTILINE,
        )
        require(len(value) == 1, "chunk elapsed-time receipt absent")
        elapsed[entry["label"]] = int(value[0])
    receipt = {
        "schema": "phase3-axial-h4-plucker-continuation-receipt-v1",
        "status": "PASS_CERTIFIED_SHORTFALL",
        "commands": [
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_continuation_v1.run_bounded"
                ),
                "result": "HONEST_REFUSAL_RECORDED",
                "chunk_elapsed_milliseconds": elapsed,
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m unittest -v "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_continuation_v1."
                    "test_continuation"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_continuation_v1.verify"
                ),
                "result": "PASS",
            },
        ],
        "hashes": hashes,
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "bounded disjoint continuation shortfall; no shared "
                "operator, paper theorem, or lifecycle state changed"
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
            == "phase3-axial-h4-plucker-continuation-schema-v1",
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
        "PASS certified bounded shortfall reached shell 4 segment 2; "
        "refused shell 4 segment 3 code 32"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
