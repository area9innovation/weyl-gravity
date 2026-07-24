#!/usr/bin/env python3
"""Fail-closed audit of the terminated correlated multipanel prototype."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "correlated_affine_multipanel_successor.py"
ONE_STEP = HERE / "correlated-affine-seed-successor-certificate.json"
ABSENT_RUN = HERE / "correlated-affine-multipanel-successor-run.json"
RUN = HERE / "correlated-multipanel-throughput-shortfall-run.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    return {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }


def compute() -> dict:
    one_step = json.loads(ONE_STEP.read_text())
    if one_step["status"] != "ONE_CORRELATED_RADIAL_SUCCESSOR_CERTIFIED":
        raise RuntimeError("one-step source certificate drift")
    if not one_step["claim_flags"]["one_radial_taylor_step_certified"]:
        raise RuntimeError("one-step source gate drift")
    if ABSENT_RUN.exists():
        raise RuntimeError(
            "a multipanel run artifact now exists; classify it independently"
        )

    source_text = SOURCE.read_text()
    names = function_names(SOURCE)
    audit = {
        "requested_steps_is_33": "STEPS = 33" in source_text,
        "joint_symbolic_kernel_exists": (
            "generator_joint_coefficients" in names
        ),
        "gaussian_exact_backend_exists": (
            {"gaussian", "gadd", "gmul", "gscale"} <= names
        ),
        "cached_interval_kernel_exists": (
            {"cached_generator", "cached_row_norm_bound"} <= names
        ),
        "per_step_checkpoint_constructor_exists": "checkpoint" in names,
        "run_is_written_only_after_compute_returns": (
            "RUN.write_text(json.dumps(compute()" in source_text
        ),
        "joint_kernel_is_not_serialized_as_a_reusable_artifact": (
            "joint-generator-kernel.json" not in source_text
        ),
        "per_step_checkpoint_is_not_written_durably": (
            "checkpoint-run-" not in source_text
            and "write_text" not in source_text[
                source_text.index("def checkpoint(") :
                source_text.index("def checkpoint_valid(")
            ]
        ),
        "multipanel_output_absent": not ABSENT_RUN.exists(),
    }
    if not all(audit.values()):
        raise RuntimeError(f"throughput audit drift: {audit}")

    successor = one_step["successor_model"]
    split_contract = {
        "schema": "phase3-correlated-multipanel-split-contract-v1",
        "resume_source": {
            "certificate": str(ONE_STEP.relative_to(ROOT)),
            "model_stage": successor["stage"],
            "rho": successor["rho"],
            "content_sha256": successor["content_sha256"],
        },
        "kernel_stage": {
            "output": "correlated-joint-generator-kernel.json",
            "contents": [
                "joint rho/omega derivative matrices through radial degree 5 and omega degree 4",
                "exact Gaussian-rational coefficients",
                "symbolic generator source hash",
                "frequency center and model orders",
                "content hash over the complete kernel",
            ],
            "independent_gate": (
                "verify exact derivative identities against the symbolic "
                "generator before any checkpoint consumes the kernel"
            ),
        },
        "checkpoint_stage": {
            "work_unit": "exactly one radial step per invocation",
            "input": (
                "one content-addressed parent model plus the verified joint kernel"
            ),
            "output": (
                "one atomic content-addressed correlated checkpoint written "
                "before the process exits"
            ),
            "required_gates": [
                "radial Cauchy scaled norm below one",
                "one coupled residual propagated without component boxes",
                "fixed chart denominator lower modulus positive",
                "parent, kernel, polynomial, affine generator, residual, and step metadata hashed",
            ],
        },
        "driver_stage": {
            "role": (
                "link already verified one-step checkpoints; never recompute "
                "the symbolic kernel or earlier steps"
            ),
            "time_budget_seconds": 60,
            "timeout_disposition": (
                "emit a shortfall at the last durable checkpoint; timeout is not pass"
            ),
        },
    }

    return {
        "schema": "phase3-axial-horizon-correlated-multipanel-throughput-shortfall-run-v1",
        "source": {
            "one_step_certificate": {
                "path": str(ONE_STEP.relative_to(ROOT)),
                "sha256": sha256(ONE_STEP),
                "status": one_step["status"],
            },
            "multipanel_prototype": {
                "path": str(SOURCE.relative_to(ROOT)),
                "sha256": sha256(SOURCE),
            },
        },
        "observed_attempt": {
            "command": (
                "python3 -m black_hole_programme.phase3."
                "axial_partial_jet_horizon_checkpoint_frame_v1."
                "correlated_affine_multipanel_successor"
            ),
            "requested_steps": 33,
            "elapsed_seconds": 344,
            "termination": "FAST_RAIL_TIMEOUT",
            "process_exit": "TERMINATED",
            "run_artifact_written": False,
            "certified_multipanel_radius": None,
            "certified_multipanel_pivot": None,
            "certified_multipanel_residual": None,
        },
        "code_audit": audit,
        "split_contract": split_contract,
        "terminal": {
            "gate": "THROUGHPUT_SHORTFALL",
            "last_certified_rho": successor["rho"],
            "last_certified_model_sha256": successor["content_sha256"],
            "multipanel_result_certified": False,
        },
        "claim_flags": {
            "one_step_correlated_successor_retained": True,
            "multipanel_result_certified": False,
            "former_cartesian_obstruction_crossed": False,
            "cartesian_wrapping_obstruction_removed": False,
            "joint_kernel_cache_required": True,
            "per_step_durable_checkpoint_split_required": True,
            "timeout_treated_as_pass": False,
            "r4_reached": False,
            "H4_certified": False,
            "T_plus_certified": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
