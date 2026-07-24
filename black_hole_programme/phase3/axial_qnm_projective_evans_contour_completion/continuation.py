#!/usr/bin/env python3
"""Reusable bounded producer and verifier for Evans-contour continuations."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from flint import arb

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as core
from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row


ROOT = Path(__file__).resolve().parents[3]
PANEL_COUNT = 1024
MAX_WORKERS = 8


@dataclass(frozen=True)
class ContinuationConfig:
    here: Path
    start: int
    stop: int
    predecessor: Path
    module: str
    version: str

    @property
    def raw(self) -> Path:
        return self.here / "child-grid-raw-run.json"

    @property
    def aggregate(self) -> Path:
        return self.here / "child-grid-aggregate-run.json"

    @property
    def certificate(self) -> Path:
        return self.here / "certificate.json"

    @property
    def receipt(self) -> Path:
        return self.here / "receipt.json"

    @property
    def report(self) -> Path:
        return self.here / "report.md"

    @property
    def schema(self) -> Path:
        return self.here / "schema.json"

    @property
    def predecessor_certificate(self) -> Path:
        return self.predecessor / "certificate.json"

    @property
    def predecessor_aggregate(self) -> Path:
        return self.predecessor / "child-grid-aggregate-run.json"

    @property
    def panel_label(self) -> str:
        return f"{self.start}-{self.stop - 1}"

    @property
    def source(self) -> str:
        return f"qnm-projective-evans-contour-chunk-{self.version}"

    @property
    def certificate_schema(self) -> str:
        return (
            "phase3-axial-qnm-projective-evans-contour-chunk-"
            f"{self.version}"
        )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _passes(row: dict) -> bool:
    return (
        row["boundary_nonvanishing"]["status"] == "PASS"
        and arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
    )


def _compute_rows(config: ContinuationConfig) -> list[dict]:
    panels = list(range(config.start, config.stop))
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(core._worker, panel, PANEL_COUNT): panel
            for panel in panels
        }
        unordered = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    return [unordered[panel] for panel in panels]


def _build_raw(config: ContinuationConfig) -> dict:
    started = time.monotonic()
    rows = _compute_rows(config)
    observations = [
        core._entry("fixed_child_grid_observation", row, row["panel"] // 2)
        for row in rows
    ]
    accepted = []
    first_failure = None
    for entry in observations:
        if _passes(entry["row"]):
            accepted.append(entry)
            continue
        first_failure = entry
        break
    terminal = {
        "code": (
            "REQUESTED_CHILD_GRID_STOP_REACHED"
            if first_failure is None
            else "FIRST_CHILD_GRID_FAILURE"
        ),
        "first_unmaterialized_child_panel": (
            config.stop if first_failure is None else first_failure["panel"]
        ),
    }
    if first_failure is not None:
        terminal["failure"] = first_failure["row"][
            "boundary_nonvanishing"
        ].get("failure")
    return {
        "schema": (
            "phase3-axial-qnm-projective-evans-contour-raw-run-"
            f"{config.version}"
        ),
        "arithmetic": "python-flint acb/arb, 128 bits",
        "requested_child_range": [config.start, config.stop - 1],
        "child_panel_count": PANEL_COUNT,
        "maximum_parallel_workers": MAX_WORKERS,
        "maximum_subdivision_depth": 1,
        "elapsed_compute_seconds": time.monotonic() - started,
        "horizon_remainder_root": core.STABLE_ROOT,
        "threshold_lowered": False,
        "observations": observations,
        "accepted_segments": accepted,
        "terminal": terminal,
    }


def _checked_predecessor(config: ContinuationConfig) -> dict:
    certificate = json.loads(config.predecessor_certificate.read_text())
    if (
        certificate["runs"]["aggregate"]["sha256"]
        != sha(config.predecessor_aggregate)
    ):
        raise RuntimeError("predecessor aggregate hash mismatch")
    aggregate = json.loads(config.predecessor_aggregate.read_text())
    if Fraction(aggregate["summary"]["coverage_stop"]) != Fraction(
        config.start, PANEL_COUNT
    ):
        raise RuntimeError("predecessor coverage does not meet child block")
    return aggregate


def _build_aggregate(
    config: ContinuationConfig, raw: dict, predecessor: dict
) -> dict:
    segments = list(predecessor["segments"])
    for entry in raw["accepted_segments"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("accepted child failed typed Delta gate")
        segments.append(
            {
                "start": f"{row['panel']}/{row['panel_count']}",
                "stop": f"{row['panel'] + 1}/{row['panel_count']}",
                "source": config.source,
                "source_row_sha256": entry["row_sha256"],
                "typed_row": row,
            }
        )
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    coverage_stop = bounds[-1][1]
    next_child = raw["terminal"]["first_unmaterialized_child_panel"]
    return {
        "schema": (
            "phase3-axial-qnm-projective-evans-contour-aggregate-run-"
            f"{config.version}"
        ),
        "status": "FIXED_CHILD_GRID_PREFIX_EXTENDED_FAIL_CLOSED",
        "predecessor_certificate_sha256": sha(
            config.predecessor_certificate
        ),
        "predecessor_aggregate_sha256": sha(config.predecessor_aggregate),
        "predecessor_coverage_stop": predecessor["summary"]["coverage_stop"],
        "segments": segments,
        "summary": {
            "contiguous_from_zero": (
                bounds[0][0] == 0
                and all(
                    left[1] == right[0]
                    for left, right in zip(bounds, bounds[1:])
                )
            ),
            "segment_count": len(segments),
            "coverage_stop": (
                f"{coverage_stop.numerator}/{coverage_stop.denominator}"
            ),
            "all_materialized_deltas_exclude_zero": all(
                item["typed_row"]["delta"]["excludes_zero"]
                for item in segments
            ),
            "two_sided_interface_gates_pass": all(
                all(item["typed_row"]["interface_gates"].values())
                for item in segments
            ),
            "new_accepted_segment_count": len(raw["accepted_segments"]),
        },
        "terminal": raw["terminal"],
        "next_honest_boundary_gap": {
            "start": f"{next_child}/{PANEL_COUNT}",
            "first_unmaterialized_child_panel": next_child,
            "child_panel_count": PANEL_COUNT,
        },
        "closed_claim_gates": {
            "full_closed_contour": False,
            "argument_principle_run": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
    }


def _build_certificate(
    config: ContinuationConfig, raw: dict, aggregate: dict
) -> dict:
    accepted = [
        {
            "segment": f"{entry['panel']}/{entry['panel_count']}",
            "row_sha256": entry["row_sha256"],
            "delta_modulus_lower": entry["row"][
                "physical_mismatch"
            ]["modulus_lower"],
        }
        for entry in raw["accepted_segments"]
    ]
    return {
        "schema": config.certificate_schema,
        "status": "FIXED_CHILD_GRID_BOUNDARY_PREFIX_EXTENDED_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "materialized_prefix_nonzero_certified": True,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "fixed_child_grid_only": True,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
        "method": {
            "start": f"{config.start}/{PANEL_COUNT}",
            "requested_stop": f"{config.stop}/{PANEL_COUNT}",
            "child_panel_count": PANEL_COUNT,
            "maximum_parallel_workers": MAX_WORKERS,
            "maximum_subdivision_depth": 1,
            "horizon_remainder_root": raw["horizon_remainder_root"],
            "threshold_policy": "unchanged; no threshold relaxation",
            "acceptance_policy": (
                "accept only the ordered contiguous prefix before the first "
                "typed zero-exclusion failure"
            ),
            "performance_disposition": (
                "The eight-panel scoped producer must remain below 60 seconds; "
                "the replayless verifier is the per-commit Tier 1 rail."
            ),
            "generic_adaptive_source": rel(Path(core.__file__)),
            "continuation_source": rel(Path(__file__)),
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "accepted_segments": accepted,
            "new_accepted_segment_count": len(raw["accepted_segments"]),
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "terminal": raw["terminal"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(config.predecessor_certificate),
                "sha256": sha(config.predecessor_certificate),
            },
            "predecessor_aggregate": {
                "path": rel(config.predecessor_aggregate),
                "sha256": sha(config.predecessor_aggregate),
            },
            "generic_adaptive_source": {
                "path": rel(Path(core.__file__)),
                "sha256": sha(Path(core.__file__)),
            },
            "continuation_source": {
                "path": rel(Path(__file__)),
                "sha256": sha(Path(__file__)),
            },
        },
        "runs": {
            "raw": {"path": rel(config.raw), "sha256": sha(config.raw)},
            "aggregate": {
                "path": rel(config.aggregate),
                "sha256": sha(config.aggregate),
            },
        },
        "does_not_establish": [
            "boundary nonvanishing beginning at the stated next gap",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle root count",
            "a QNM location or simple-root certificate",
            "a nonzero Delta_tau or Delta_omega selector",
            "a local Smith branch, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }


def verify(
    config: ContinuationConfig,
    *,
    certificate_path: Path | None = None,
    raw_path: Path | None = None,
) -> None:
    certificate = json.loads(
        (certificate_path or config.certificate).read_text()
    )
    raw = json.loads((raw_path or config.raw).read_text())
    aggregate = json.loads(config.aggregate.read_text())
    predecessor = json.loads(config.predecessor_aggregate.read_text())
    assert certificate["runs"]["raw"]["sha256"] == sha(config.raw)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(
        config.aggregate
    )
    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert Fraction(predecessor["summary"]["coverage_stop"]) == Fraction(
        config.start, PANEL_COUNT
    )
    assert raw["requested_child_range"] == [
        config.start,
        config.stop - 1,
    ]
    assert raw["child_panel_count"] == PANEL_COUNT
    assert 0 < raw["elapsed_compute_seconds"] < 60
    assert not raw["threshold_lowered"]
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in aggregate["segments"]
    ]
    assert bounds[0][0] == 0
    assert all(left[1] == right[0] for left, right in zip(bounds, bounds[1:]))
    assert bounds[-1][1] == Fraction(
        certificate["result"]["coverage_stop"]
    )
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert certificate["result"]["new_accepted_segment_count"] == len(
        raw["accepted_segments"]
    )
    for index, entry in enumerate(raw["accepted_segments"]):
        assert entry["panel"] == config.start + index
        assert entry["panel_count"] == PANEL_COUNT
    for key in (
        "full_contour_nonzero_certified",
        "argument_principle_certified",
        "root_count_certified",
        "QNM_location_certified",
        "Smith_selector_certified",
        "defective_fibre_or_EP2_certified",
    ):
        assert certificate["claim_flags"][key] is False
    print(
        f"Evans contour chunk {config.panel_label} verifier: PASS "
        f"(coverage {certificate['result']['coverage_stop']}; next "
        f"{certificate['result']['next_honest_boundary_gap']['start']})"
    )


def produce(config: ContinuationConfig) -> None:
    started = time.monotonic()
    predecessor = _checked_predecessor(config)
    raw = _build_raw(config)
    config.raw.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    aggregate = _build_aggregate(config, raw, predecessor)
    config.aggregate.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n"
    )
    certificate = _build_certificate(config, raw, aggregate)
    config.certificate.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    config.report.write_text(
        f"# Projective Evans contour continuation panels "
        f"{config.panel_label}\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"The unchanged 1/{PANEL_COUNT} projective transport evaluated "
        f"child panels `{config.start}` through `{config.stop - 1}` with "
        f"`{MAX_WORKERS}` workers and accepted only the ordered contiguous "
        f"prefix. It accepted `{len(raw['accepted_segments'])}/"
        f"{config.stop - config.start}` panels. Exact coverage ends at "
        f"`{aggregate['summary']['coverage_stop']}` and the next honest gap "
        f"begins at `{aggregate['next_honest_boundary_gap']['start']}`. "
        "Full-contour, argument-principle, root-count, QNM, Smith and EP2 "
        "flags remain false.\n"
    )
    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            rel(config.here / "runner.py"),
            rel(config.here / "verify.py"),
            rel(config.here / "test_chunk.py"),
            rel(Path(__file__)),
        ],
        [
            "python3",
            "-m",
            "jsonschema",
            "-i",
            rel(config.certificate),
            rel(config.schema),
        ],
        ["python3", "-m", f"{config.module}.verify"],
        ["python3", "-m", "unittest", f"{config.module}.test_chunk"],
    ]
    checks = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        checks.append(
            {
                "command": " ".join(command),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
    config.receipt.write_text(
        json.dumps(
            {
                "schema": (
                    "phase3-axial-qnm-projective-evans-contour-receipt-"
                    f"{config.version}"
                ),
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    "predecessor_certificate": sha(
                        config.predecessor_certificate
                    ),
                    "predecessor_aggregate": sha(
                        config.predecessor_aggregate
                    ),
                    "generic_adaptive_source": sha(Path(core.__file__)),
                    "continuation_source": sha(Path(__file__)),
                },
                "output_sha256": {
                    "raw": sha(config.raw),
                    "aggregate": sha(config.aggregate),
                    "certificate": sha(config.certificate),
                    "report": sha(config.report),
                },
                "higher_tiers_not_run": (
                    "No closed contour, theorem promotion, freeze or "
                    "release. The bounded transport is the producer; "
                    "replayless verification is the fast Tier 1 rail."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if any(check["returncode"] != 0 for check in checks):
        raise SystemExit("one or more scoped checks failed; see receipt.json")
    print(config.certificate)
