#!/usr/bin/env python3
"""Run reduced completion plus the fail-closed covariant BV last-mile audit."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.green_complex import (
    BVGreenWitnessStatus,
    ReducedPhysicalGreenRealization,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"

GUARDS = (
    ("verify_conformal_covariant_factorization.py", "--claim-arbitrary-background"),
    ("verify_conformal_covariant_factorization.py", "--claim-local-tt-projector"),
    ("verify_conformal_covariant_factorization.py", "--claim-local-branch-split"),
    ("verify_conformal_covariant_factorization.py", "--claim-causal-branch-split"),
    ("verify_conformal_covariant_factorization.py", "--include-vector-killing-as-a2"),
    ("verify_conformal_covariant_factorization.py", "--claim-full-bv-green"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-vector-residue-order-zero"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-vector-h-half"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-product-sobolev"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-factorization-fixes-pairing"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-covariant-distributional"),
    ("verify_conformal_cauchy_sobolev.py", "--claim-hadamard"),
    ("verify_conformal_minimal_witness.py", "--claim-exact-factorization"),
    ("verify_conformal_auxiliary_green_realization.py", "--claim-direct-factorization"),
    ("verify_conformal_auxiliary_green_realization.py", "--claim-direct-original-causal-homotopy"),
    ("verify_conformal_auxiliary_green_realization.py", "--claim-curved-globalization"),
    ("verify_conformal_auxiliary_green_realization.py", "--claim-causal-homotopy"),
    ("verify_conformal_covariant_bv_last_mile.py", "--claim-complete-covariant-theorem"),
    (
        "verify_conformal_covariant_dependency_report.py",
        "--claim-complete-green-hyperbolicity",
    ),
    ("verify_conformal_covariant_dependency_report.py", "--claim-final-covariant-h4"),
    ("verify_conformal_final_covariant_transport.py", "--claim-final-covariant-h4"),
    ("verify_conformal_final_covariant_transport.py", "--recompute-auxiliary-h4"),
    ("verify_conformal_four_flag_closure.py", "--claim-complete"),
)


def _run(script: str, *arguments: str) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "symbolic" / script), *arguments],
        cwd=ROOT,
        check=True,
    )


def _run_parallel(jobs: tuple[tuple[str, tuple[str, ...]], ...]) -> None:
    """Run independent certificate producers with deterministic output."""

    def execute(job: tuple[str, tuple[str, ...]]) -> subprocess.CompletedProcess[str]:
        script, arguments = job
        return subprocess.run(
            [sys.executable, str(ROOT / "symbolic" / script), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    with ThreadPoolExecutor(max_workers=min(4, len(jobs))) as executor:
        results = tuple(executor.map(execute, jobs))
    for (script, _), result in zip(jobs, results, strict=True):
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, script)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument(
        "--claim-direct-same-bundle-witness",
        action="store_true",
        help="fail closed: H has no certified direct same-bundle factorization",
    )
    parser.add_argument(
        "--claim-covariant-fixed-time-pairing",
        action="store_true",
        help="fail closed: the full BV causal pairing comparison remains open",
    )
    args = parser.parse_args()
    if args.claim_direct_same_bundle_witness:
        raise SystemExit(
            "REFUSED: the exact null-symbol rank theorem rules out the proposed "
            "scalar same-bundle witness on the current 24-field/9-gauge bundle"
        )
    if args.claim_covariant_fixed_time_pairing:
        raise SystemExit(
            "REFUSED: the off-shell current comparison and E/A/L normalization "
            "are proved, but the causal Green realization and Green/current "
            "identification remain open"
        )

    emit_args = ("--emit",) if args.emit else ()
    guarded_args = emit_args + (("--guards",) if args.guards else ())

    # These producers emit disjoint certificates. The older structural
    # verifiers expose their overclaim checks through dedicated flags below
    # and intentionally do not accept ``--guards``.
    _run_parallel(
        (
            ("verify_conformal_covariant_factorization.py", emit_args),
            ("verify_conformal_cauchy_sobolev.py", emit_args),
            ("verify_conformal_minimal_witness.py", guarded_args),
            ("verify_conformal_auxiliary_green_realization.py", emit_args),
            ("verify_conformal_curved_operator_workstream.py", guarded_args),
            ("verify_conformal_curvature_evolution.py", guarded_args),
            ("verify_conformal_curved_retract.py", guarded_args),
            ("verify_conformal_curved_current.py", guarded_args),
        )
    )
    _run("verify_conformal_covariant_bv_last_mile.py", *guarded_args)
    _run("verify_conformal_covariant_dependency_report.py", *guarded_args)
    _run_parallel(
        (
            ("verify_conformal_final_covariant_transport.py", guarded_args),
            ("verify_conformal_four_flag_closure.py", guarded_args),
        )
    )
    physical = ReducedPhysicalGreenRealization().certificate()
    status = BVGreenWitnessStatus().certificate()
    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        for name, value in {
            "reduced_physical_green.json": physical,
            "bv_green_witness_status.json": status,
        }.items():
            path = CERTIFICATE_DIR / name
            path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print("wrote", path.relative_to(ROOT))

    if args.guards:
        for script, flag in GUARDS:
            result = subprocess.run(
                [sys.executable, str(ROOT / "symbolic" / script), flag],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 or "REFUSED:" not in result.stdout + result.stderr:
                raise AssertionError(f"overclaim guard did not fail closed: {script} {flag}")
        for flag in (
            "--claim-direct-same-bundle-witness",
            "--claim-covariant-fixed-time-pairing",
        ):
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), flag],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 or "REFUSED:" not in result.stdout + result.stderr:
                raise AssertionError(f"top-level guard did not fail closed: {flag}")
        print(f"COVARIANT COMPLETION OVERCLAIM GUARDS: {len(GUARDS)+2}/{len(GUARDS)+2} PASS")
    print("CONFORMAL COVARIANT CERTIFICATION STACK: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
