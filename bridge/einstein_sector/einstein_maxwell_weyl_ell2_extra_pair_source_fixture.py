#!/usr/bin/env python3
"""Generate the canonical C4 ell=2 extra-pair source ledger."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_extra_pair_source import (
    FREQUENCY,
    MODES,
    pair_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_pair_source_fixture.json"
ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_ell2_extra_pair_source.py"
FRAGMENT_DIR = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_extra_pair_sources_v1"
MODE_ORDER = tuple(MODES)
PAIRS = tuple(
    (MODE_ORDER[left], MODE_ORDER[right])
    for left in range(len(MODE_ORDER))
    for right in range(left, len(MODE_ORDER))
)
CASES = tuple((left, right, channel) for channel in ("sum", "zero") for left, right in PAIRS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): _strings(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_strings(item) for item in value]
    return value


def _case(case: tuple[str, str, str]) -> tuple[str, dict[str, object]]:
    left, right, channel = case
    return f"{channel}:{left}:{right}", pair_source(left, right, channel)


def _fragment_path(case: tuple[str, str, str]) -> Path:
    left, right, channel = case
    return FRAGMENT_DIR / f"{channel}_{left}_{right}.json"


def _fragment(case: tuple[str, str, str], value: dict[str, object]) -> dict[str, object]:
    return {
        "schema": "einstein-maxwell-weyl-ell2-extra-pair-source-fragment-v1",
        "case": list(case),
        "engine_sha256": _sha256(ENGINE),
        "source": _strings(value),
    }


def _valid_fragment(case: tuple[str, str, str]) -> bool:
    path = _fragment_path(case)
    if not path.exists():
        return False
    value = json.loads(path.read_text(encoding="utf-8"))
    return value.get("case") == list(case) and value.get("engine_sha256") == _sha256(ENGINE)


def replay(workers: int, *, force: bool = False) -> dict[str, object]:
    FRAGMENT_DIR.mkdir(parents=True, exist_ok=True)
    pending = [case for case in CASES if force or not _valid_fragment(case)]
    if workers == 1:
        for case in pending:
            _, value = _case(case)
            _fragment_path(case).write_text(
                json.dumps(_fragment(case, value), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"completed {':'.join(case)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_case, case): case for case in pending}
            for future in as_completed(futures):
                case = futures[future]
                _, value = future.result()
                _fragment_path(case).write_text(
                    json.dumps(_fragment(case, value), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                print(f"completed {':'.join(case)}", flush=True)
    records = {}
    for case in CASES:
        if not _valid_fragment(case):
            raise AssertionError(f"missing or stale pair fragment: {case}")
        fragment = json.loads(_fragment_path(case).read_text(encoding="utf-8"))
        records[f"{case[2]}:{case[0]}:{case[1]}"] = fragment["source"]
    return records


def build(records: dict[str, object]) -> dict[str, object]:
    expected = {f"{channel}:{left}:{right}" for left, right, channel in CASES}
    if set(records) != expected:
        raise AssertionError("extra-pair case ledger is incomplete")
    return {
        "schema": "einstein-maxwell-weyl-ell2-extra-pair-source-fixture-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_EXTRA_PAIR_SOURCE_FIXTURE",
        "result_state": "CANONICAL_C4_COMPLEX_BILINEAR_EXTRA_SELF_SOURCE_LEDGER_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": "canonical axial/polar ell=2,m=0,k=0 extra p-primary C4 basis; all ten symmetric positive-frequency sums and all ten positive-negative Hermitian generators",
        "mode_order": list(MODE_ORDER),
        "canonical_representatives": {
            name: {"parity": parity, "components": [str(value) for value in mode]}
            for name, (parity, mode) in MODES.items()
        },
        "frequency": str(FREQUENCY),
        "bilinear_sources": records,
        "reality_assembly": {
            "real_field": "Phi=Re(sum_i x_i e_i exp(-i*omega_e*t))",
            "sum_diagonal_factor": "x_i**2/8",
            "sum_offdiagonal_factor": "x_i*x_j/4",
            "zero_diagonal_factor": "|x_i|**2/4",
            "zero_offdiagonal_factor": "(x_i*conjugate(x_j)*S_ij+conjugate(x_i)*x_j*conjugate(S_ij))/4",
        },
        "classification": {
            "all_twenty_complex_bilinear_generators_computed": True,
            "same_parity_outputs_polar_L0_L2_L4": True,
            "mixed_parity_outputs_axial_L2_L4": True,
            "complete_allowed_harmonic_basis_and_unused_node_audited": True,
            "corrections_constructed": False,
        },
        "source_manifest": {
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            str(ENGINE.relative_to(ROOT)): _sha256(ENGINE),
        },
        "claim_boundary": "This is the direct source ledger. It does not itself invert target blocks, combine the homogeneous row with the global Taub cone, or certify a complete correction.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_extra_pair_source_fixture --check",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_extra_pair_source_fixture --replay --workers 4",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--replay", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    arguments = parser.parse_args()
    if arguments.write:
        payload = build(replay(arguments.workers))
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif arguments.replay:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if stored != build(replay(arguments.workers, force=True)):
            raise AssertionError("extra-pair source fixture failed full replay")
    else:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if stored["source_manifest"] != {
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            str(ENGINE.relative_to(ROOT)): _sha256(ENGINE),
        }:
            raise AssertionError("extra-pair source manifest is stale")
        if set(stored["bilinear_sources"]) != {f"{channel}:{left}:{right}" for left, right, channel in CASES}:
            raise AssertionError("extra-pair stored case ledger is incomplete")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_EXTRA_PAIR_SOURCE_FIXTURE: PASS")


if __name__ == "__main__":
    main()
