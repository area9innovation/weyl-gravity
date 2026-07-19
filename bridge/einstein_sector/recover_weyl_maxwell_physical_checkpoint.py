#!/usr/bin/env python3
"""Fine-grained recovery producer for the Weyl--Maxwell physical Taylor rows.

The original checkpoint controller deliberately treated the complete physical
row construction as one stage.  On a busy shared machine that stage can take
long enough that a terminal or aggregate-memory failure loses substantial
work.  This recovery driver evaluates the *same formula* from
``weyl_maxwell_product_taylor.physical_euler_rows`` at smaller, mathematically
inert boundaries and writes a valid ``physical.done.json`` only after the
assembled rows pass the existing Ward and formal-adjoint checks.

It does not alter the scientific source fingerprint.  Instead it verifies the
content hashes of the engine, Taylor producer, exporter, and original
checkpoint runner recorded by that fingerprint and records its own hash in
every recovery-stage receipt.  The final release receipt must include this
driver as an additional producing source.
"""

from __future__ import annotations

import argparse
from itertools import product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

import sympy as sp

from bridge.einstein_sector import weyl_maxwell_product_taylor as taylor
from bridge.einstein_sector.run_weyl_maxwell_product_checkpointed import (
    DEFAULT_CHECKPOINT_ROOT,
    ROOT,
    SOURCE_PATHS,
    _atomic_json,
    _atomic_pickle,
    _component_path,
    _fingerprint,
    _load_pickle,
    _physical_path,
    _set_worker_limits,
    _sha256,
    _stage_record,
    _valid_stage,
    _wait_for_memory,
)
from bridge.einstein_sector.product_theta_jet_engine import sum_jets


PAIRS = taylor.PAIRS
RECOVERY_SOURCE = Path(__file__).resolve()
RAISED_INDICES = tuple(product(range(4), repeat=2))


def _recovery_extra() -> dict[str, object]:
    return {
        "recovery_driver": str(RECOVERY_SOURCE.relative_to(ROOT)),
        "recovery_driver_sha256": _sha256(RECOVERY_SOURCE),
        "formula_source": str(
            Path(taylor.__file__).resolve().relative_to(ROOT)
        ),
        "formula": "physical_euler_rows exact row-sharded evaluation",
    }


def _validate_scientific_sources(checkpoint: Path, fingerprint: str) -> None:
    manifest_path = checkpoint / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("source_fingerprint") != fingerprint:
        raise RuntimeError("checkpoint source fingerprint drifted")
    recorded = manifest.get("sources", {})
    for path in SOURCE_PATHS:
        relative = str(path.relative_to(ROOT))
        if recorded.get(relative) != _sha256(path):
            raise RuntimeError(f"checkpoint scientific source drifted: {relative}")


def _maxwell_root(checkpoint: Path) -> Path:
    return checkpoint / "physical-components/maxwell"


def _raised_path(checkpoint: Path, index: int) -> Path:
    first, second = RAISED_INDICES[index]
    return _maxwell_root(checkpoint) / "raised" / f"row-{first}{second}.pkl"


def _raised_done(checkpoint: Path, index: int) -> Path:
    first, second = RAISED_INDICES[index]
    return _maxwell_root(checkpoint) / "raised" / f"row-{first}{second}.done.json"


def _stress_path(checkpoint: Path, index: int) -> Path:
    first, second = PAIRS[index]
    return _maxwell_root(checkpoint) / "stress" / f"row-{first}{second}.pkl"


def _stress_done(checkpoint: Path, index: int) -> Path:
    first, second = PAIRS[index]
    return _maxwell_root(checkpoint) / "stress" / f"row-{first}{second}.done.json"


def _metric_path(checkpoint: Path, index: int) -> Path:
    first, second = PAIRS[index]
    return _maxwell_root(checkpoint) / "physical" / f"metric-{first}{second}.pkl"


def _metric_done(checkpoint: Path, index: int) -> Path:
    first, second = PAIRS[index]
    return _maxwell_root(checkpoint) / "physical" / f"metric-{first}{second}.done.json"


def _potential_path(checkpoint: Path, target: int) -> Path:
    return _maxwell_root(checkpoint) / "physical" / f"potential-{target}.pkl"


def _potential_done(checkpoint: Path, target: int) -> Path:
    return _maxwell_root(checkpoint) / "physical" / f"potential-{target}.done.json"


def _load_raised(checkpoint: Path) -> dict[tuple[int, int], object]:
    return {
        indices: _load_pickle(_raised_path(checkpoint, index))
        for index, indices in enumerate(RAISED_INDICES)
    }


def _load_stress(checkpoint: Path) -> dict[tuple[int, int], object]:
    output = {}
    for index, (first, second) in enumerate(PAIRS):
        value = _load_pickle(_stress_path(checkpoint, index))
        output[(first, second)] = value
        output[(second, first)] = value
    return output


def _load_bach(checkpoint: Path) -> dict[tuple[int, int], object]:
    algebraic = _load_pickle(_component_path(checkpoint, "algebraic"))
    output = {}
    for index, (first, second) in enumerate(PAIRS):
        divergence = _load_pickle(
            checkpoint
            / "physical-components/divergence"
            / f"row-{index:02d}.pkl"
        )
        value = divergence + algebraic[(first, second)]
        output[(first, second)] = value
        output[(second, first)] = value
    return output


def _write_stage(
    *,
    done: Path,
    stage: str,
    fingerprint: str,
    started: float,
    artifacts: tuple[Path, ...],
    extra: dict[str, object] | None = None,
) -> None:
    merged = _recovery_extra()
    if extra:
        merged.update(extra)
    _atomic_json(
        done,
        _stage_record(
            stage=stage,
            fingerprint=fingerprint,
            started=started,
            artifacts=artifacts,
            extra=merged,
        ),
    )


def _worker_raised(checkpoint: Path, fingerprint: str, index: int) -> None:
    started = time.perf_counter()
    first, second = RAISED_INDICES[index]
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    inverse = geometry["inverse"]
    field_strength = taylor._field_strength()
    value = sum_jets(
        inverse[(first, left)]
        * inverse[(second, right)]
        * field_strength[(left, right)]
        for left, right in product(range(4), repeat=2)
    )
    path = _raised_path(checkpoint, index)
    _atomic_pickle(path, value)
    _write_stage(
        done=_raised_done(checkpoint, index),
        stage=f"maxwell_raised_{first}{second}",
        fingerprint=fingerprint,
        started=started,
        artifacts=(path,),
        extra={"tensor_indices": [first, second]},
    )


def _worker_invariant(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    field_strength = taylor._field_strength()
    raised = _load_raised(checkpoint)
    value = sum_jets(
        field_strength[(first, second)] * raised[(first, second)]
        for first, second in RAISED_INDICES
    )
    path = _maxwell_root(checkpoint) / "invariant.pkl"
    _atomic_pickle(path, value)
    _write_stage(
        done=_maxwell_root(checkpoint) / "invariant.done.json",
        stage="maxwell_invariant",
        fingerprint=fingerprint,
        started=started,
        artifacts=(path,),
    )


def _worker_stress(checkpoint: Path, fingerprint: str, index: int) -> None:
    started = time.perf_counter()
    first, second = PAIRS[index]
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    field_strength = taylor._field_strength()
    invariant = _load_pickle(_maxwell_root(checkpoint) / "invariant.pkl")
    value = sum_jets(
        inverse[(left, right)]
        * field_strength[(first, left)]
        * field_strength[(second, right)]
        for left, right in product(range(4), repeat=2)
    ) - metric[(first, second)] * invariant.scale(sp.Rational(1, 4))
    path = _stress_path(checkpoint, index)
    _atomic_pickle(path, value)
    _write_stage(
        done=_stress_done(checkpoint, index),
        stage=f"maxwell_stress_{first}{second}",
        fingerprint=fingerprint,
        started=started,
        artifacts=(path,),
        extra={"tensor_pair": [first, second]},
    )


def _worker_metric(checkpoint: Path, fingerprint: str, index: int) -> None:
    started = time.perf_counter()
    first, second = PAIRS[index]
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    inverse = geometry["inverse"]
    volume = geometry["volume_ratio"]
    stress = _load_stress(checkpoint)
    bach = _load_bach(checkpoint)
    multiplicity = 1 if first == second else 2
    raised_residual = sum_jets(
        inverse[(first, left)]
        * inverse[(second, right)]
        * (stress[(left, right)] - bach[(left, right)].scale(taylor.ALPHA_B))
        for left, right in product(range(4), repeat=2)
    )
    value = volume * raised_residual.scale(sp.Rational(multiplicity, 2))
    if not value.background.is_zero:
        raise AssertionError(
            f"common product is not on shell in metric row {index}: "
            f"{value.background.values}"
        )
    path = _metric_path(checkpoint, index)
    _atomic_pickle(path, value)
    _write_stage(
        done=_metric_done(checkpoint, index),
        stage=f"physical_metric_{first}{second}",
        fingerprint=fingerprint,
        started=started,
        artifacts=(path,),
        extra={"row": index, "tensor_pair": [first, second]},
    )


def _worker_potential(checkpoint: Path, fingerprint: str, target: int) -> None:
    started = time.perf_counter()
    geometry = _load_pickle(_component_path(checkpoint, "geometry"))
    volume = geometry["volume_ratio"]
    raised = _load_raised(checkpoint)
    value = sum_jets(
        (volume * raised[(axis, target)]).scale(taylor.SIN).derivative(axis)
        for axis in range(4)
    ).scale(taylor.SIN.reciprocal())
    if not value.background.is_zero:
        raise AssertionError(
            f"common product is not on shell in potential row {target}: "
            f"{value.background.values}"
        )
    path = _potential_path(checkpoint, target)
    _atomic_pickle(path, value)
    _write_stage(
        done=_potential_done(checkpoint, target),
        stage=f"physical_potential_{target}",
        fingerprint=fingerprint,
        started=started,
        artifacts=(path,),
        extra={"row": len(PAIRS) + target, "target_index": target},
    )


def _worker_assemble(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    rows = tuple(
        [
            *(_load_pickle(_metric_path(checkpoint, index)) for index in range(len(PAIRS))),
            *(_load_pickle(_potential_path(checkpoint, target)) for target in range(4)),
        ]
    )
    if len(rows) != 14:
        raise AssertionError("physical recovery row count drifted")
    physical = _physical_path(checkpoint)
    _atomic_pickle(physical, rows)
    done = checkpoint / "physical-assembly.done.json"
    _write_stage(
        done=done,
        stage="physical_assembly",
        fingerprint=fingerprint,
        started=started,
        artifacts=(physical,),
        extra={"row_count": len(rows)},
    )


def _worker_checks(checkpoint: Path, fingerprint: str) -> None:
    started = time.perf_counter()
    rows = _load_pickle(_physical_path(checkpoint))
    checks = checkpoint / "physical-checks.json"
    _atomic_json(
        checks,
        {
            "physical_summary": taylor.physical_summary(rows),
            "unary_checks": taylor.unary_checks(rows),
            "recovery_driver": str(RECOVERY_SOURCE.relative_to(ROOT)),
            "recovery_driver_sha256": _sha256(RECOVERY_SOURCE),
        },
    )
    physical = _physical_path(checkpoint)
    _write_stage(
        done=checkpoint / "physical.done.json",
        stage="physical_recovered_sharded",
        fingerprint=fingerprint,
        started=started,
        artifacts=(physical, checks),
        extra={"assembly_receipt": "physical-assembly.done.json"},
    )


def _worker(args: argparse.Namespace) -> None:
    fingerprint = _fingerprint()
    if args.fingerprint != fingerprint:
        raise RuntimeError(
            f"recovery worker source fingerprint drifted: expected "
            f"{args.fingerprint}, got {fingerprint}"
        )
    checkpoint = args.checkpoint_root / fingerprint
    _validate_scientific_sources(checkpoint, fingerprint)
    _set_worker_limits(args.memory_limit_gib)
    if args.worker == "raised":
        if args.index is None or not 0 <= args.index < len(RAISED_INDICES):
            raise ValueError("raised worker requires a valid --index")
        _worker_raised(checkpoint, fingerprint, args.index)
    elif args.worker == "invariant":
        _worker_invariant(checkpoint, fingerprint)
    elif args.worker == "stress":
        if args.index is None or not 0 <= args.index < len(PAIRS):
            raise ValueError("stress worker requires a valid --index")
        _worker_stress(checkpoint, fingerprint, args.index)
    elif args.worker == "metric":
        if args.index is None or not 0 <= args.index < len(PAIRS):
            raise ValueError("metric worker requires a valid --index")
        _worker_metric(checkpoint, fingerprint, args.index)
    elif args.worker == "potential":
        if args.index is None or not 0 <= args.index < 4:
            raise ValueError("potential worker requires a valid --index")
        _worker_potential(checkpoint, fingerprint, args.index)
    elif args.worker == "assemble":
        _worker_assemble(checkpoint, fingerprint)
    elif args.worker == "checks":
        _worker_checks(checkpoint, fingerprint)
    else:
        raise ValueError(f"unknown recovery worker: {args.worker}")


def _command(
    args: argparse.Namespace,
    fingerprint: str,
    worker: str,
    index: int | None = None,
) -> list[str]:
    command = [
        sys.executable,
        str(RECOVERY_SOURCE),
        "--worker",
        worker,
        "--checkpoint-root",
        str(args.checkpoint_root),
        "--fingerprint",
        fingerprint,
        "--memory-limit-gib",
        str(args.memory_limit_gib),
    ]
    if index is not None:
        command.extend(("--index", str(index)))
    return command


def _run(
    args: argparse.Namespace,
    fingerprint: str,
    worker: str,
    done: Path,
    index: int | None = None,
) -> None:
    if _valid_stage(done, fingerprint):
        print(
            json.dumps(
                {"stage": worker, "index": index, "status": "REUSED"},
                sort_keys=True,
            ),
            flush=True,
        )
        return
    _wait_for_memory(args.minimum_available_gib)
    print(
        json.dumps(
            {"stage": worker, "index": index, "status": "START"},
            sort_keys=True,
        ),
        flush=True,
    )
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    subprocess.run(
        _command(args, fingerprint, worker, index),
        cwd=ROOT,
        env=environment,
        check=True,
    )
    print(
        json.dumps(
            {"stage": worker, "index": index, "status": "PASS"},
            sort_keys=True,
        ),
        flush=True,
    )


def _controller(args: argparse.Namespace) -> None:
    fingerprint = _fingerprint()
    checkpoint = args.checkpoint_root / fingerprint
    _validate_scientific_sources(checkpoint, fingerprint)
    for index in range(len(RAISED_INDICES)):
        _run(args, fingerprint, "raised", _raised_done(checkpoint, index), index)
    _run(
        args,
        fingerprint,
        "invariant",
        _maxwell_root(checkpoint) / "invariant.done.json",
    )
    for index in range(len(PAIRS)):
        _run(args, fingerprint, "stress", _stress_done(checkpoint, index), index)
    for index in range(len(PAIRS)):
        _run(args, fingerprint, "metric", _metric_done(checkpoint, index), index)
    for target in range(4):
        _run(
            args,
            fingerprint,
            "potential",
            _potential_done(checkpoint, target),
            target,
        )
    _run(
        args,
        fingerprint,
        "assemble",
        checkpoint / "physical-assembly.done.json",
    )
    _run(
        args,
        fingerprint,
        "checks",
        checkpoint / "physical.done.json",
    )
    print(
        json.dumps(
            {
                "result_id": "WEYL_MAXWELL_PHYSICAL_CHECKPOINT_RECOVERY_V1",
                "source_fingerprint": fingerprint,
                "status": "PASS",
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint-root", type=Path, default=DEFAULT_CHECKPOINT_ROOT
    )
    parser.add_argument("--memory-limit-gib", type=float, default=6.0)
    parser.add_argument("--minimum-available-gib", type=float, default=12.0)
    parser.add_argument(
        "--worker",
        choices=(
            "raised",
            "invariant",
            "stress",
            "metric",
            "potential",
            "assemble",
            "checks",
        ),
    )
    parser.add_argument("--index", type=int)
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
