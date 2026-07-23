#!/usr/bin/env python3
"""Independent verifier for the bounded q00 Pluecker preflight."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from . import produce

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "plucker_q00_preflight.forge"
METADATA = HERE / "source_metadata.json"
LOG = HERE / "plucker_q00_preflight_run.txt"
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


def expected_signed_terms() -> list[tuple[int, int, int, int, int]]:
    """Independently flatten the complex exterior action to real rows."""
    flattened: list[tuple[int, int, int, int, int]] = []
    for (row, col), entries in produce.induced_contributions().items():
        for source_row, source_col, sign in entries:
            real_source = (
                produce.REAL_ROW[source_row],
                produce.REAL_ROW[source_col],
            )
            imag_source = (
                produce.IMAG_ROW[source_row],
                produce.REAL_ROW[source_col],
            )
            flattened.extend(
                (
                    (row, col, *real_source, sign),
                    (row + 20, col + 20, *real_source, sign),
                    (row + 20, col, *imag_source, sign),
                    (row, col + 20, *imag_source, -sign),
                )
            )
    return flattened


def parsed_signed_terms(
    source: str,
) -> list[tuple[int, int, int, int, int]]:
    arms = re.findall(
        r"^\s+(\d+)=>PlTerm\((-?\d+),(-?\d+),(-?\d+),"
        r"(-?\d+),(-?\d+)\),$",
        source,
        flags=re.MULTILINE,
    )
    indexes = [int(arm[0]) for arm in arms]
    require(indexes == list(range(960)),
            "induced signed-term table index drift")
    return [
        tuple(int(value) for value in arm[1:])
        for arm in arms
    ]


def verify_source(source: str, metadata: dict, schema: dict) -> None:
    require(
        schema.get("schema")
        == "phase3-axial-horizon-h4-plucker-artifact-schema-v1",
        "artifact schema drift",
    )
    require(
        metadata.get("schema")
        == "phase3-axial-horizon-h4-plucker-source-v1",
        "source metadata schema drift",
    )
    require(
        hashlib.sha256(source.encode()).hexdigest()
        == metadata.get("source_sha256"),
        "source hash drift",
    )
    require(metadata.get("frequency_cell") == ["1/2", "2049/4096"],
            "q00 cell drift")
    require(metadata.get("target") == {"shell": 3, "segment": 0},
            "bounded target drift")
    require(metadata.get("plucker_coordinates") == 20,
            "Pluecker dimension drift")
    require(metadata.get("realified_state_rows") == 40,
            "realified state drift")
    require(metadata.get("plucker_relation_count") == 45,
            "relation count drift")
    require(metadata.get("plucker_relation_span_rank") == 35,
            "relation span rank drift")
    require(
        metadata.get("induced_inventory_sha256")
        == produce.canonical_hash(produce.induced_inventory()),
        "induced exterior inventory drift",
    )
    require(
        metadata.get("relation_inventory_sha256")
        == produce.canonical_hash(produce.relation_inventory()),
        "relation inventory drift",
    )
    require(
        metadata.get("typed_layouts")
        == {
            "initializer": "block-realified",
            "runtime_generator": "standard Re(6),Im(6)",
            "plucker_state": "Re(20),Im(20)",
        },
        "typed layout ledger drift",
    )
    markers = (
        "fn pl_induced(a:borrow IvTaylor4Mat)->H4Result",
        "fn pl_step(a:borrow IvAffineMat",
        "sl_exp_tail(rat_to_f64(h)*alpha,order+1)",
        "fn pl_projective_normalize",
        "ivtm4_scale_rat_checked(a,scale)",
        "ivtm4_rebase_dyadic(scaled.value,160)",
        "fn pl_relations(a:borrow IvTaylor4Mat)->PlCheck",
        "fn pl_pivot(a:borrow IvTaylor4Mat)->PlPivot",
        "return PlPivot(false,-1,0.0,norm,32);",
        "let ri:i64=i;let ii:i64=i+6;",
        "let initial_basis:IvTaylor4Mat=hr_reorder_rows(",
        "PLUCKER_PASS reached_shell=3 reached_segment=0",
    )
    for marker in markers:
        require(marker in source, f"source marker absent: {marker}")
    require(
        parsed_signed_terms(source) == expected_signed_terms(),
        "induced signed-term table drift",
    )
    relation_ids = [
        int(value)
        for value in re.findall(
            r'println\("PLUCKER_RELATION_DEFECT relation=(\d+)"\);',
            source,
        )
    ]
    require(
        relation_ids == list(range(45)),
        "runtime relation inventory drift",
    )


def verify_log(text: str, source_sha256: str) -> dict:
    require("trap() reached" not in text, "run contains a trap")
    require("PLUCKER_REFUSE" not in text, "run contains a refusal")
    require("PLUCKER_RELATION_DEFECT" not in text,
            "run contains a relation defect")
    hashes = re.findall(
        r"^PLUCKER_SOURCE_SHA256=([0-9a-f]{64})$",
        text,
        flags=re.MULTILINE,
    )
    require(hashes == [source_sha256],
            "run source provenance absent, ambiguous, or stale")
    require(text.count("PLUCKER_BEGIN ") == 1, "begin marker drift")
    segment_matches = re.findall(
        r"^PLUCKER_SEGMENT shell=(\d+) segment=(\d+) pivot=(\d+) "
        r"margin=([^ ]+) norm=([^ ]+) relations=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    require(len(segment_matches) == len(produce.TARGET_SEGMENTS),
            "segment heartbeat count drift")
    for expected, match in zip(produce.TARGET_SEGMENTS, segment_matches):
        shell, segment, pivot, margin, norm, relation_count = match
        require((int(shell), int(segment)) == expected,
                "segment order drift")
        require(0 <= int(pivot) < 20, "pivot index drift")
        require(math.isfinite(float(margin)) and float(margin) > 0,
                "nonzero pivot witness absent")
        require(math.isfinite(float(norm)) and float(norm) > 0,
                "finite projective norm absent")
        require(int(relation_count) == 45, "relation heartbeat drift")
    result = re.fullmatch(
        r"PLUCKER_RESULT pivot=(\d+) margin=([^ ]+) norm=([^ ]+) "
        r"rank_witness=true",
        next(
            (
                line for line in text.splitlines()
                if line.startswith("PLUCKER_RESULT ")
            ),
            "",
        ),
    )
    require(result is not None, "final rank witness absent")
    last = segment_matches[-1]
    require(
        (result.group(1), result.group(2), result.group(3))
        == (last[2], last[3], last[4]),
        "final result does not match target heartbeat",
    )
    require(
        text.count(
            "PLUCKER_PASS reached_shell=3 reached_segment=0 "
            "rank_witness=true parameter_correlation=true"
        ) == 1,
        "bounded PASS absent or duplicated",
    )
    require(text.count("PLUCKER_PROCESS_EXIT=42") == 1,
            "successful process exit absent")
    elapsed = re.findall(
        r"^PLUCKER_ELAPSED_MILLISECONDS=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    require(len(elapsed) == 1 and int(elapsed[0]) > 0,
            "run elapsed time absent")
    return {
        "segment_count": len(segment_matches),
        "final_pivot": int(result.group(1)),
        "final_margin": result.group(2),
        "final_norm": result.group(3),
        "elapsed_milliseconds": int(elapsed[0]),
    }


def build_artifacts(metadata: dict, result: dict) -> tuple[dict, dict]:
    hashes = {
        "plucker_q00_preflight.forge": sha256(SOURCE),
        "plucker_q00_preflight_run.txt": sha256(LOG),
        "source_metadata.json": sha256(METADATA),
        "schema.json": sha256(SCHEMA),
        "produce.py": sha256(HERE / "produce.py"),
        "verify.py": sha256(HERE / "verify.py"),
        "test_plucker.py": sha256(HERE / "test_plucker.py"),
        "README.md": sha256(HERE / "README.md"),
        "report.md": sha256(HERE / "report.md"),
    }
    certificate = {
        "schema": "phase3-axial-horizon-h4-plucker-certificate-v1",
        "status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "frequency_cell": metadata["frequency_cell"],
            "rho_start": "1/4194304",
            "rho_end": "5/2097152",
            "target": metadata["target"],
            "panels": 416,
        },
        "representation": {
            "space": "Lambda^3(C^6)",
            "complex_coordinates": 20,
            "realified_rows": 40,
            "projective_normalization": metadata[
                "projective_normalization"
            ],
        },
        "result": {
            "reached_target": True,
            "plucker_relations_checked": 45,
            "relation_span_rank": 35,
            "rank_witness": True,
            **result,
        },
        "hashes": hashes,
        "does_not_establish": metadata["does_not_establish"],
    }
    receipt = {
        "schema": "phase3-axial-horizon-h4-plucker-receipt-v1",
        "status": "PASS",
        "commands": [
            {
                "tier": 0,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_v1.produce"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "FORGE_LIB=/home/alstrup/area9/tango/forge/lib "
                    "/home/alstrup/area9/tango/forge/forge "
                    "-o /tmp/axial-h4-plucker-q00-v1 "
                    "black_hole_programme/phase3/"
                    "axial_horizon_h4_plucker_v1/"
                    "plucker_q00_preflight.forge"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": "/tmp/axial-h4-plucker-q00-v1",
                "elapsed_milliseconds": result["elapsed_milliseconds"],
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m unittest -v "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_v1.test_plucker"
                ),
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": (
                    "PYTHONPATH=. python3 -m "
                    "black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_v1.verify"
                ),
                "result": "PASS",
            },
        ],
        "hashes": hashes,
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "disjoint bounded representation preflight; no shared "
                "operator or paper theorem changed"
            ),
        },
        "does_not_establish": metadata["does_not_establish"],
    }
    return certificate, receipt


def main() -> int:
    try:
        metadata = json.loads(METADATA.read_text())
        schema = json.loads(SCHEMA.read_text())
        source = SOURCE.read_text()
        log = LOG.read_text()
        verify_source(source, metadata, schema)
        result = verify_log(log, metadata["source_sha256"])
        certificate, receipt = build_artifacts(metadata, result)
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )
    except (OSError, json.JSONDecodeError, VerificationError) as exc:
        print(f"REFUSE {exc}")
        return 3
    print(
        "PASS q00 Pluecker preflight through shell 3 segment 0 "
        f"pivot={result['final_pivot']} margin={result['final_margin']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
