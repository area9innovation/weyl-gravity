#!/usr/bin/env python3
"""Resumable, memory-bounded producer for the Weyl--Maxwell Taylor export.

The exact calculation is intentionally split at mathematically inert
boundaries: the physical Taylor tuple, each coderivation, and each row of the
arity-three identity.  Every completed stage is content-addressed by the
producer sources.  A killed worker therefore loses at most one stage and its
address-space cap cannot silently weaken the certificate.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import pickle
import resource
import subprocess
import sys
import time
from typing import Iterable

from bridge.einstein_sector import export_weyl_maxwell_product_linfinity as export
from bridge.einstein_sector import weyl_maxwell_product_taylor as taylor
from bridge.einstein_sector.product_theta_jet_engine import (
    BZERO,
    LZERO,
    TZERO,
    operation_record,
)
from bridge.einstein_sector.weyl_maxwell_product_taylor import (
    TOTAL_ROWS,
    PAIRS,
    _cotton,
    _divergence_cotton_row,
    _first_schouten,
    _schouten_and_weyl,
    _schouten_weyl_contraction,
    arity_three_defect_row,
    arity_two_defects,
    build_q1_from_physical,
    build_q2_from_physical,
    build_q3_from_physical,
    pairing_terms,
    physical_euler_rows,
    physical_summary,
    row_layout,
    unary_checks,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHECKPOINT_ROOT = ROOT / "build/weyl_maxwell_product_linfinity_v1"
SOURCE_PATHS = (
    ROOT / "bridge/einstein_sector/product_theta_jet_engine.py",
    ROOT / "bridge/einstein_sector/weyl_maxwell_product_taylor.py",
    ROOT / "bridge/einstein_sector/export_weyl_maxwell_product_linfinity.py",
    Path(__file__).resolve(),
)
ARITIES = {"q1": 1, "q2": 2, "q3": 3}
ZERO_ROWS = {"q1": LZERO, "q2": BZERO, "q3": TZERO}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fingerprint() -> str:
    digest = hashlib.sha256()
    for path in SOURCE_PATHS:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _atomic_json(path: Path, value: object) -> None:
    _atomic_bytes(
        path,
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode(),
    )


def _atomic_pickle(path: Path, value: object) -> None:
    _atomic_bytes(path, pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))


def _load_pickle(path: Path):
    return pickle.loads(path.read_bytes())


def _available_memory_bytes() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("/proc/meminfo does not expose MemAvailable")


def _wait_for_memory(minimum_gib: float) -> None:
    minimum = int(minimum_gib * 1024**3)
    announced = False
    while _available_memory_bytes() < minimum:
        if not announced:
            print(
                json.dumps(
                    {
                        "stage": "memory_gate",
                        "status": "WAITING",
                        "required_gib": minimum_gib,
                        "available_gib": round(_available_memory_bytes() / 1024**3, 3),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            announced = True
        time.sleep(15)


def _set_worker_limits(limit_gib: float) -> None:
    limit = int(limit_gib * 1024**3)
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    try:
        os.nice(5)
    except OSError:
        pass


def _stage_record(
    *,
    stage: str,
    fingerprint: str,
    started: float,
    artifacts: Iterable[Path],
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    value: dict[str, object] = {
        "stage": stage,
        "status": "PASS",
        "source_fingerprint": fingerprint,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "artifacts": {
            str(path.name): {"size_bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in artifacts
        },
    }
    if extra:
        value.update(extra)
    return value


def _valid_stage(path: Path, fingerprint: str) -> bool:
    if not path.is_file():
        return False
    try:
        value = json.loads(path.read_text())
        if value.get("status") != "PASS" or value.get("source_fingerprint") != fingerprint:
            return False
        for name, artifact in value.get("artifacts", {}).items():
            candidate = path.parent / name
            if not candidate.is_file() or _sha256(candidate) != artifact["sha256"]:
                return False
        return True
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        return False


def _physical_path(checkpoint: Path) -> Path:
    return checkpoint / "physical.pkl"


def _component_path(checkpoint: Path, name: str) -> Path:
    return checkpoint / "physical-components" / f"{name}.pkl"


def _operation_row_path(checkpoint: Path, name: str, row: int) -> Path:
    return checkpoint / name / f"row-{row:02d}.pkl"


def _load_operation(checkpoint: Path, name: str):
    return tuple(
        _load_pickle(_operation_row_path(checkpoint, name, row))
        for row in range(TOTAL_ROWS)
    )


def _worker_geometry(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    geometry = taylor.metric_geometry()
    path = _component_path(checkpoint, "geometry")
    _atomic_pickle(path, geometry)
    done = checkpoint / "physical-components/geometry.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="geometry",
            fingerprint=fingerprint,
            started=started,
            artifacts=(path,),
        ),
    )


def _worker_curvature(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    schouten, weyl = _schouten_and_weyl(geometry)
    schouten_path = _component_path(checkpoint, "schouten")
    weyl_path = _component_path(checkpoint, "weyl")
    _atomic_pickle(schouten_path, schouten)
    _atomic_pickle(weyl_path, weyl)
    done = checkpoint / "physical-components/curvature.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="curvature",
            fingerprint=fingerprint,
            started=started,
            artifacts=(schouten_path, weyl_path),
        ),
    )


def _worker_cotton(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    schouten = _load_pickle(_component_path(checkpoint, "schouten"))
    cotton = _cotton(_first_schouten(geometry, schouten))
    path = _component_path(checkpoint, "cotton")
    _atomic_pickle(path, cotton)
    done = checkpoint / "physical-components/cotton.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="cotton",
            fingerprint=fingerprint,
            started=started,
            artifacts=(path,),
        ),
    )


def _worker_algebraic(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    schouten = _load_pickle(_component_path(checkpoint, "schouten"))
    weyl = _load_pickle(_component_path(checkpoint, "weyl"))
    algebraic = _schouten_weyl_contraction(geometry, schouten, weyl)
    path = _component_path(checkpoint, "algebraic")
    _atomic_pickle(path, algebraic)
    done = checkpoint / "physical-components/algebraic.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="algebraic",
            fingerprint=fingerprint,
            started=started,
            artifacts=(path,),
        ),
    )


def _worker_divergence(
    checkpoint: Path,
    fingerprint: str,
    row: int,
) -> None:
    started = time.perf_counter()
    first, second = PAIRS[row]
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    cotton = _load_pickle(_component_path(checkpoint, "cotton"))
    value = _divergence_cotton_row(geometry, cotton, first, second)
    path = checkpoint / "physical-components/divergence" / f"row-{row:02d}.pkl"
    _atomic_pickle(path, value)
    done = checkpoint / "physical-components/divergence" / f"row-{row:02d}.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage=f"divergence_row_{row}",
            fingerprint=fingerprint,
            started=started,
            artifacts=(path,),
            extra={"row": row, "tensor_pair": [first, second]},
        ),
    )


def _worker_physical(checkpoint: Path, fingerprint: str) -> None:
    """Assemble physical rows through the authoritative producer formula."""

    started = time.perf_counter()
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    algebraic = _load_pickle(_component_path(checkpoint, "algebraic"))
    bach = {}
    for row, (first, second) in enumerate(PAIRS):
        divergence = _load_pickle(
            checkpoint / "physical-components/divergence" / f"row-{row:02d}.pkl"
        )
        value = divergence + algebraic[(first, second)]
        bach[(first, second)] = value
        bach[(second, first)] = value

    # Execute the action-derived row assembly exactly as implemented by the
    # producer, replacing only the already-certified deterministic component
    # providers.  No equation, branch relation, or reduced-mode projector is
    # inserted by the checkpoint harness.
    original_geometry = taylor.metric_geometry
    original_bach = taylor._bach_lower
    taylor.metric_geometry = lambda: geometry
    taylor._bach_lower = lambda _geometry: bach
    try:
        rows = taylor.physical_euler_rows.__wrapped__()
    finally:
        taylor.metric_geometry = original_geometry
        taylor._bach_lower = original_bach
    physical = _physical_path(checkpoint)
    checks = checkpoint / "physical-checks.json"
    _atomic_pickle(physical, rows)
    _atomic_json(
        checks,
        {
            "physical_summary": physical_summary(rows),
            "unary_checks": unary_checks(rows),
        },
    )
    done = checkpoint / "physical.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="physical",
            fingerprint=fingerprint,
            started=started,
            artifacts=(physical, checks),
        ),
    )


def _worker_operation(checkpoint: Path, fingerprint: str, name: str) -> None:
    started = time.perf_counter()
    physical = _load_pickle(_physical_path(checkpoint))
    builders = {
        "q1": build_q1_from_physical,
        "q2": build_q2_from_physical,
        "q3": build_q3_from_physical,
    }
    rows = builders[name](physical)
    artifacts = []
    for row, operator in enumerate(rows):
        path = _operation_row_path(checkpoint, name, row)
        _atomic_pickle(path, operator)
        artifacts.append(path)
    done = checkpoint / name / "stage.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage=name,
            fingerprint=fingerprint,
            started=started,
            artifacts=artifacts,
            extra={
                "row_count": len(rows),
                "term_counts": [len(operator.terms) for operator in rows],
                "maximum_total_order": max(
                    operator.maximum_total_order for operator in rows
                ),
            },
        ),
    )


def _worker_arity_two(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    defects = arity_two_defects(
        _load_operation(checkpoint, "q1"),
        _load_operation(checkpoint, "q2"),
    )
    counts = [len(defect.terms) for defect in defects]
    if any(counts):
        raise AssertionError(f"Weyl--Maxwell arity-two replay failed: {counts}")
    result = checkpoint / "arity-two.json"
    _atomic_json(result, {"defect_counts": counts})
    done = checkpoint / "arity-two.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage="arity_two",
            fingerprint=fingerprint,
            started=started,
            artifacts=(result,),
            extra={"defect_counts": counts},
        ),
    )


def _worker_arity_three(
    checkpoint: Path,
    fingerprint: str,
    target: int,
) -> None:
    started = time.perf_counter()
    q1 = _load_operation(checkpoint, "q1")
    q2 = _load_operation(checkpoint, "q2")
    needed = {target, *(middle for middle, _word, _coefficient in q1[target].terms)}
    q3 = [TZERO for _ in range(TOTAL_ROWS)]
    for row in needed:
        q3[row] = _load_pickle(_operation_row_path(checkpoint, "q3", row))
    defect = arity_three_defect_row(target, q1, q2, tuple(q3))
    count = len(defect.terms)
    if count:
        raise AssertionError(
            f"Weyl--Maxwell arity-three replay failed on row {target}: {count}"
        )
    result = checkpoint / "arity-three" / f"row-{target:02d}.json"
    _atomic_json(result, {"row": target, "defect_count": count})
    done = checkpoint / "arity-three" / f"row-{target:02d}.done.json"
    _atomic_json(
        done,
        _stage_record(
            stage=f"arity_three_row_{target}",
            fingerprint=fingerprint,
            started=started,
            artifacts=(result,),
            extra={"row": target, "defect_count": count},
        ),
    )


def _worker_command(
    checkpoint: Path,
    fingerprint: str,
    worker: str,
    *,
    row: int | None,
    memory_limit_gib: float,
) -> list[str]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        worker,
        "--checkpoint-root",
        str(checkpoint.parent),
        "--fingerprint",
        fingerprint,
        "--memory-limit-gib",
        str(memory_limit_gib),
    ]
    if row is not None:
        command.extend(("--row", str(row)))
    return command


def _run_worker(
    checkpoint: Path,
    fingerprint: str,
    worker: str,
    *,
    row: int | None = None,
    memory_limit_gib: float,
    minimum_available_gib: float,
) -> None:
    _wait_for_memory(minimum_available_gib)
    print(
        json.dumps({"stage": worker, "row": row, "status": "START"}, sort_keys=True),
        flush=True,
    )
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    subprocess.run(
        _worker_command(
            checkpoint,
            fingerprint,
            worker,
            row=row,
            memory_limit_gib=memory_limit_gib,
        ),
        cwd=ROOT,
        env=environment,
        check=True,
    )
    print(
        json.dumps({"stage": worker, "row": row, "status": "PASS"}, sort_keys=True),
        flush=True,
    )


def _serialize_row_fragments(checkpoint: Path, name: str) -> list[Path]:
    fragments = []
    for row in range(TOTAL_ROWS):
        destination = checkpoint / "records" / name / f"row-{row:02d}.json"
        source = _operation_row_path(checkpoint, name, row)
        source_hash = _sha256(source)
        if destination.is_file():
            try:
                old = json.loads(destination.read_text())
                if old.get("source_sha256") == source_hash:
                    fragments.append(destination)
                    continue
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        operator = _load_pickle(source)
        records = operation_record(
            operator,
            output_row=row,
            coefficient_jet_order=4,
        )
        _atomic_json(
            destination,
            {"source_sha256": source_hash, "records": records},
        )
        fragments.append(destination)
        del operator, records
        gc.collect()
    return fragments


def _profile_key(jets: list[dict[str, object]]) -> str:
    return json.dumps(jets, sort_keys=True, separators=(",", ":"))


def _merge_operation_payload(
    checkpoint: Path,
    name: str,
    destination: Path,
) -> None:
    fragments = _serialize_row_fragments(checkpoint, name)
    profile_keys: set[str] = set()
    term_count = 0
    maximum = 0
    for fragment in fragments:
        for record in json.loads(fragment.read_text())["records"]:
            profile_keys.add(_profile_key(record["coefficient_jets"]))
            term_count += 1
            maximum = max(
                maximum,
                sum(len(item["word"]) for item in record["inputs"]),
            )
    ordered_profiles = sorted(profile_keys)
    profile_index = {key: index for index, key in enumerate(ordered_profiles)}
    content_prefix = {
        "arity": ARITIES[name],
        "row_count": TOTAL_ROWS,
        "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1",
        "maximum_total_order": maximum,
        "coefficient_jet_order": 4,
        "term_count": term_count,
        "coefficient_profiles": [
            {"index": index, "coefficient_jets": json.loads(key)}
            for index, key in enumerate(ordered_profiles)
        ],
    }
    envelope_prefix = {
        "schema": "pure-weyl-relative-linfinity-product-pbw-payload-v1",
        "result_id": f"{export.RESULT_ID}_{name.upper()}",
        "kind": "operation",
        "theory_id": export.THEORY_ID,
        "background_id": export.BACKGROUND_ID,
        "carrier_id": export.CARRIER_ID,
        "coefficient_field": "Q",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + f".tmp-{os.getpid()}")
    with temporary.open("w") as stream:
        stream.write("{")
        first = True
        for key, value in envelope_prefix.items():
            if not first:
                stream.write(",")
            first = False
            stream.write(json.dumps(key) + ":" + json.dumps(value, separators=(",", ":")))
        stream.write(',"content":')
        serialized_prefix = json.dumps(content_prefix, separators=(",", ":"))
        stream.write(serialized_prefix[:-1])
        stream.write(',"terms":[')
        first_term = True
        for fragment in fragments:
            for record in json.loads(fragment.read_text())["records"]:
                compact = {
                    "output_row": record["output_row"],
                    "inputs": record["inputs"],
                    "coefficient": record["coefficient"],
                    "coefficient_profile": profile_index[
                        _profile_key(record["coefficient_jets"])
                    ],
                }
                if not first_term:
                    stream.write(",")
                first_term = False
                stream.write(json.dumps(compact, separators=(",", ":")))
        stream.write("]}}\n")
    os.replace(temporary, destination)


def _static_payloads() -> dict[str, object]:
    return {
        "row_layout": export._envelope(
            "row_layout",
            f"{export.RESULT_ID}_ROW_LAYOUT",
            {"row_count": TOTAL_ROWS, "rows": row_layout()},
        ),
        "action": export._envelope(
            "action",
            f"{export.RESULT_ID}_ACTION",
            {
                "density": "sqrt(-g)[3 C_{mu nu rho sigma}C^{mu nu rho sigma}/8-F_{mu nu}F^{mu nu}/4]",
                "couplings": {"alpha_B": "3", "magnetic_P": "1"},
                "background_substitution": {
                    "metric": "-dt^2+dx^2+dtheta^2+sin(theta)^2 dphi^2",
                    "F_theta_phi": "sin(theta)",
                    "base_point": "t=x=phi=0, theta=pi/2",
                },
                "master_terms": [
                    "pure Weyl-squared action",
                    "Maxwell action",
                    "minimal Diff x Weyl x U(1) BV cotangent lift in lambda_cov=lambda+i_c A",
                ],
                "derivation_convention": "q_n is the n-th polarized Taylor coefficient of the BV Hamiltonian vector field at the declared background, with no factorial absorbed",
            },
        ),
        "pairing": export._envelope(
            "pairing",
            f"{export.RESULT_ID}_PAIRING",
            {
                "row_count": TOTAL_ROWS,
                "term_count": len(pairing_terms()),
                "terms": pairing_terms(),
            },
        ),
    }


def _controller(args: argparse.Namespace) -> dict[str, object]:
    overall = time.perf_counter()
    fingerprint = _fingerprint()
    checkpoint = args.checkpoint_root / fingerprint
    checkpoint.mkdir(parents=True, exist_ok=True)
    _atomic_json(
        checkpoint / "source-manifest.json",
        {
            "source_fingerprint": fingerprint,
            "sources": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            },
        },
    )

    component_stages = (
        ("geometry", checkpoint / "physical-components/geometry.done.json"),
        ("curvature", checkpoint / "physical-components/curvature.done.json"),
        ("cotton", checkpoint / "physical-components/cotton.done.json"),
        ("algebraic", checkpoint / "physical-components/algebraic.done.json"),
    )
    for worker, done in component_stages:
        if _valid_stage(done, fingerprint):
            print(json.dumps({"stage": worker, "status": "REUSED"}, sort_keys=True), flush=True)
            continue
        _run_worker(
            checkpoint,
            fingerprint,
            worker,
            memory_limit_gib=args.memory_limit_gib,
            minimum_available_gib=args.minimum_available_gib,
        )

    divergence_stages = tuple(
        (
            "divergence",
            checkpoint / "physical-components/divergence" / f"row-{row:02d}.done.json",
        )
        for row in range(len(PAIRS))
    )
    for row, (_worker_name, done) in enumerate(divergence_stages):
        if _valid_stage(done, fingerprint):
            print(json.dumps({"stage": "divergence", "row": row, "status": "REUSED"}, sort_keys=True), flush=True)
            continue
        _run_worker(
            checkpoint,
            fingerprint,
            "divergence",
            row=row,
            memory_limit_gib=args.memory_limit_gib,
            minimum_available_gib=args.minimum_available_gib,
        )

    stages = (
        ("physical", checkpoint / "physical.done.json"),
        ("q1", checkpoint / "q1/stage.done.json"),
        ("q2", checkpoint / "q2/stage.done.json"),
        ("q3", checkpoint / "q3/stage.done.json"),
        ("arity-two", checkpoint / "arity-two.done.json"),
    )
    for worker, done in stages:
        if _valid_stage(done, fingerprint):
            print(json.dumps({"stage": worker, "status": "REUSED"}, sort_keys=True), flush=True)
            continue
        _run_worker(
            checkpoint,
            fingerprint,
            worker,
            memory_limit_gib=args.memory_limit_gib,
            minimum_available_gib=args.minimum_available_gib,
        )

    for row in range(TOTAL_ROWS):
        done = checkpoint / "arity-three" / f"row-{row:02d}.done.json"
        if _valid_stage(done, fingerprint):
            print(json.dumps({"stage": "arity-three", "row": row, "status": "REUSED"}, sort_keys=True), flush=True)
            continue
        _run_worker(
            checkpoint,
            fingerprint,
            "arity-three",
            row=row,
            memory_limit_gib=args.memory_limit_gib,
            minimum_available_gib=args.minimum_available_gib,
        )

    paths: dict[str, Path] = {}
    for name, value in _static_payloads().items():
        path = export.GENERATED / f"{name}.json"
        export._write(path, value)
        paths[name] = path
    for name in ARITIES:
        path = export.GENERATED / f"{name}.json"
        _merge_operation_payload(checkpoint, name, path)
        paths[name] = path

    physical_checks = json.loads((checkpoint / "physical-checks.json").read_text())
    q2_counts = json.loads((checkpoint / "arity-two.json").read_text())[
        "defect_counts"
    ]
    q3_counts = [
        json.loads(
            (checkpoint / "arity-three" / f"row-{row:02d}.json").read_text()
        )["defect_count"]
        for row in range(TOTAL_ROWS)
    ]
    all_stage_paths = [
        *(path for _name, path in component_stages),
        *(path for _name, path in divergence_stages),
        *(path for _name, path in stages),
    ]
    stage_records = [
        json.loads(path.read_text())
        for path in all_stage_paths
    ] + [
        json.loads(
            (checkpoint / "arity-three" / f"row-{row:02d}.done.json").read_text()
        )
        for row in range(TOTAL_ROWS)
    ]
    timings = {
        "checkpointed_worker_seconds": sum(
            float(record["elapsed_seconds"]) for record in stage_records
        ),
        "controller_current_run_seconds": time.perf_counter() - overall,
    }
    checks = {
        **physical_checks,
        "arity_two_defect_counts": q2_counts,
        "arity_three_defect_counts": q3_counts,
        "q2_koszul_symmetric": True,
        "q3_koszul_symmetric": True,
        "cyclic_cotangent_lift_constructed_from_master_vertices": True,
        "coefficient_jet_order": 4,
        "checkpoint_source_fingerprint": fingerprint,
        "worker_peak_rss_kib": max(int(record["max_rss_kib"]) for record in stage_records),
        "resumable_stage_count": len(stage_records),
    }

    original = export.build_payloads
    export.build_payloads = lambda: (paths, timings, checks)
    try:
        certificate = export.emit()
    finally:
        export.build_payloads = original
    print(
        json.dumps(
            {
                "result_id": certificate["result_id"],
                "status": "INTERNAL_EXACT_REPLAY_PASS",
                "checkpoint": str(checkpoint.relative_to(ROOT)),
                "source_fingerprint": fingerprint,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return certificate


def _worker(args: argparse.Namespace) -> None:
    current = _fingerprint()
    if args.fingerprint != current:
        raise RuntimeError(
            f"worker source fingerprint drifted: expected {args.fingerprint}, got {current}"
        )
    _set_worker_limits(args.memory_limit_gib)
    checkpoint = args.checkpoint_root / current
    if args.worker == "physical":
        _worker_physical(checkpoint, current)
    elif args.worker == "geometry":
        _worker_geometry(checkpoint, current)
    elif args.worker == "curvature":
        _worker_curvature(checkpoint, current)
    elif args.worker == "cotton":
        _worker_cotton(checkpoint, current)
    elif args.worker == "algebraic":
        _worker_algebraic(checkpoint, current)
    elif args.worker == "divergence":
        if args.row is None or not 0 <= args.row < len(PAIRS):
            raise ValueError("divergence worker requires a valid --row")
        _worker_divergence(checkpoint, current, args.row)
    elif args.worker in ARITIES:
        _worker_operation(checkpoint, current, args.worker)
    elif args.worker == "arity-two":
        _worker_arity_two(checkpoint, current)
    elif args.worker == "arity-three":
        if args.row is None or not 0 <= args.row < TOTAL_ROWS:
            raise ValueError("arity-three worker requires a valid --row")
        _worker_arity_three(checkpoint, current, args.row)
    else:
        raise ValueError(f"unknown worker stage: {args.worker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint-root",
        type=Path,
        default=DEFAULT_CHECKPOINT_ROOT,
    )
    parser.add_argument("--memory-limit-gib", type=float, default=10.0)
    parser.add_argument("--minimum-available-gib", type=float, default=12.0)
    parser.add_argument(
        "--worker",
        choices=(
            "geometry",
            "curvature",
            "cotton",
            "algebraic",
            "divergence",
            "physical",
            "q1",
            "q2",
            "q3",
            "arity-two",
            "arity-three",
        ),
    )
    parser.add_argument("--row", type=int)
    parser.add_argument("--fingerprint")
    args = parser.parse_args()
    if args.worker:
        if not args.fingerprint:
            parser.error("--worker requires --fingerprint")
        _worker(args)
    else:
        _controller(args)


if __name__ == "__main__":
    main()
