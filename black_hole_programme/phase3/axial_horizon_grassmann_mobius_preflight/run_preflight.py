#!/usr/bin/env python3
"""Run both Forge backends and freeze the first exact one-shell gate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from .produce import (
    GENERATOR,
    HERE,
    METADATA,
    OUTPUT,
    produce,
)


FORGE_ROOT = Path("/home/alstrup/area9/tango/forge")
FORGE = FORGE_ROOT / "forge"
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
ATLAS = (
    HERE.parents[2]
    / "residual_atlas"
    / "phase3-black-hole-axial-horizon-grassmann-mobius-one-shell-fragment-v1.json"
)
PANEL_RE = re.compile(
    r"^PANEL q=(?P<q>\d+) p=(?P<index>\d+) rank=(?P<rank>\d+) "
    r"norm=(?P<norm>[0-9.eE+-]+) width=(?P<width>[0-9.eE+-]+)$"
)
RESULT_RE = re.compile(
    r"^RESULT q=(?P<q>\d+) generator=(?P<generator>\d+) panels=(?P<panels>\d+) "
    r"initial_rank=(?P<initial_rank>\d+) endpoint_rank=(?P<endpoint_rank>\d+) "
    r"max_norm=(?P<max_norm>[0-9.eE+-]+) "
    r"graph_width=(?P<graph_width>[0-9.eE+-]+) "
    r"direct_rechart_width=(?P<direct_width>[0-9.eE+-]+) "
    r"improvement=(?P<improvement>[0-9.eE+-]+) "
    r"direct_intersection=(?P<direct>true|false) "
    r"gauge_invariant=(?P<gauge>true|false)$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, cwd: Path, stdout=None, timeout=1200):
    start = time.perf_counter()
    kwargs = {
        "cwd": cwd,
        "env": {**os.environ, "FORGE_LIB": str(FORGE_ROOT / "lib")},
        "timeout": timeout,
        "check": False,
    }
    if stdout is None:
        kwargs.update(text=True, capture_output=True)
    else:
        kwargs.update(stdout=stdout, stderr=subprocess.PIPE, text=True)
    proc = subprocess.run(command, **kwargs)
    return proc, time.perf_counter() - start


def main() -> int:
    produce()
    tmp = Path("/tmp/phase3_horizon_grassmann_mobius")
    tmp.mkdir(parents=True, exist_ok=True)
    native_bin = tmp / "native"
    c_source = tmp / "gate.c"
    c_bin = tmp / "c"

    native_compile, t_nc = run(
        [str(FORGE), "-incremental", "-o", str(native_bin), str(OUTPUT)],
        cwd=FORGE_ROOT,
    )
    if native_compile.returncode != 0:
        print(native_compile.stdout or "", end="")
        print(native_compile.stderr or "", end="")
        return 3

    native_run, t_nr = run([str(native_bin)], cwd=FORGE_ROOT)

    with c_source.open("w") as handle:
        c_emit, t_ce = run(
            [str(FORGE), "-incremental", "-emit-c", str(OUTPUT)],
            cwd=FORGE_ROOT,
            stdout=handle,
        )
    if c_emit.returncode != 0:
        print(c_emit.stderr or "", end="")
        return 3
    c_compile, t_cc = run(
        [
            "gcc", "-O2", "-w", "-o", str(c_bin), str(c_source),
            "-lm", "-lgmp",
        ],
        cwd=FORGE_ROOT,
    )
    if c_compile.returncode != 0:
        print(c_compile.stdout or "", end="")
        print(c_compile.stderr or "", end="")
        return 3
    c_run, t_cr = run([str(c_bin)], cwd=FORGE_ROOT)

    print(native_run.stdout or "", end="")
    if native_run.stderr:
        print(native_run.stderr, end="")
    backend_agreement = (
        native_run.returncode == c_run.returncode
        and native_run.stdout == c_run.stdout
    )

    panels = []
    results = []
    first_failed_gate = None
    for line in (native_run.stdout or "").splitlines():
        if match := PANEL_RE.match(line):
            panels.append(
                {
                    "index": int(match["index"]),
                    "subcell": int(match["q"]),
                    "rank": int(match["rank"]),
                    "chart_norm_upper": float(match["norm"]),
                    "graph_width": float(match["width"]),
                }
            )
        elif match := RESULT_RE.match(line):
            results.append(match.groupdict())
        elif first_failed_gate is None and (
            line.startswith("REFUSE ") or line == "WIDTH_SHORTFALL"
        ):
            first_failed_gate = line

    passed = (
        backend_agreement
        and native_run.returncode == 42
        and len(results) == 4
        and len(panels) == 64
        and "PASS HORIZON_GRASSMANN_MOBIUS_ALL_SUBCELLS"
        in (native_run.stdout or "")
    )
    status = "PREFLIGHT_PASS" if passed else "METHOD_SHORTFALL"
    if not passed and first_failed_gate is None:
        first_failed_gate = (
            "BACKEND_DIVERGENCE"
            if not backend_agreement
            else f"UNPARSED_RETURN_CODE_{native_run.returncode}"
        )

    metadata_bytes = METADATA.read_bytes()
    certificate = {
        "schema": "phase3-axial-horizon-grassmann-mobius-preflight-v1",
        "result_id": "PHASE3_AXIAL_HORIZON_GRASSMANN_MOBIUS_ONE_SHELL_V1",
        "status": status,
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "scope": {
            "theory": "strict four-dimensional pure Weyl gravity",
            "background": "Schwarzschild",
            "M": 1,
            "ell": 2,
            "parity": "axial",
            "omega_cell": ["1/2", "129/256"],
            "rho_cell": ["1/4194304", "1/2097152"],
        },
        "method": {
            "generator": GENERATOR,
            "complex_chart": {
                "pivot": ["P_prime", "Q", "H1"],
                "graph": ["P", "Q_prime", "rho_F"],
                "pivot_real_block_rows": [1, 2, 8, 5, 6, 10],
                "graph_real_block_rows": [0, 3, 9, 4, 7, 11],
            },
            "mobius_formula": "(Phi_JI+Phi_JJ*Z)*(Phi_II+Phi_IJ*Z)^-1",
            "right_solve": "X*A=B via A^T*X^T=B^T",
            "panels": 16,
            "omega_subcells": 4,
            "local_order": 12,
            "dyadic_rebase_bits": 128,
            "chart_norm_limit": 2.0,
            "minimum_width_improvement": 2.0,
        },
        "gates": {
            "backend_native_c_agreement": backend_agreement,
            "generator_preserved": len(results) == 4
            and all(int(row["generator"]) == GENERATOR for row in results),
            "rank_six_each_panel": len(panels) == 64
            and all(row["rank"] == 6 for row in panels),
            "chart_norm_below_two_each_panel": len(panels) == 64
            and all(row["chart_norm_upper"] < 2.0 for row in panels),
            "direct_endpoint_intersection": len(results) == 4
            and all(row["direct"] == "true" for row in results),
            "column_gauge_invariance": len(results) == 4
            and all(row["gauge"] == "true" for row in results),
            "material_width_improvement": len(results) == 4
            and all(float(row["improvement"]) >= 2.0 for row in results),
        },
        "result": {
            "panels": panels,
            "subcells": [
                {
                    "index": int(row["q"]),
                    "initial_rank": int(row["initial_rank"]),
                    "endpoint_rank": int(row["endpoint_rank"]),
                    "max_chart_norm_upper": float(row["max_norm"]),
                    "graph_width": float(row["graph_width"]),
                    "direct_endpoint_rechart_width": float(row["direct_width"]),
                    "width_improvement": float(row["improvement"]),
                    "direct_endpoint_intersection": row["direct"] == "true",
                    "column_gauge_invariance": row["gauge"] == "true",
                }
                for row in results
            ],
            "first_failed_gate": first_failed_gate,
        },
        "proof_contract": {
            "named_row_selection": True,
            "shared_parameter_generator": True,
            "checked_right_solve": True,
            "right_solve_residual_enclosed": True,
            "dyadic_rebase_after_every_panel": True,
            "independent_direct_state_representation": True,
            "exact_rational_column_gauge": True,
            "mutations_rejected": [
                "wrong-left-solve",
                "drop-Phi_IJ-Z",
                "wrong-standard-interleaved-row-crosswalk",
                "break-generator",
                "erase-column-gauge-invariance",
                "omit-rebase128",
            ],
        },
        "provenance": {
            "source_path": str(OUTPUT.relative_to(HERE.parents[2])),
            "source_sha256": sha256(OUTPUT),
            "source_metadata_path": str(METADATA.relative_to(HERE.parents[2])),
            "source_metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
            "producer_path": str((HERE / "produce.py").relative_to(HERE.parents[2])),
            "producer_sha256": sha256(HERE / "produce.py"),
            "input_commit": "d6b349535",
            "predecessor_certificate_used": False,
        },
        "establishes": (
            [
                "The future-horizon-regular axial three-complex-plane has a certified exact-affine Grassmann/Mobius transport through the first dyadic horizon shell on the declared frequency cell.",
                "The transported plane is invariant under the declared exact rational column gauge and intersects an independently propagated direct endpoint rechart.",
            ]
            if passed
            else [
                "The isolated one-shell Grassmann/Mobius method was executed through the named first failed gate without promoting a transport theorem."
            ]
        ),
        "does_not_establish": [
            "transport beyond the first dyadic horizon shell",
            "horizon-labelled amplitude transport",
            "a horizon-to-r4 map or horizon-to-infinity connection",
            "scattering, flux-sign, stability, ghost, positivity, CPT or unitarity",
            "other frequency cells, ell values or polar parity",
        ],
    }
    CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": "phase3-axial-horizon-grassmann-mobius-receipt-v1",
        "status": status,
        "commands": {
            "produce": "python3 -m black_hole_programme.phase3.axial_horizon_grassmann_mobius_preflight.produce",
            "native_compile": [str(FORGE), "-incremental", "-o", str(native_bin), str(OUTPUT)],
            "native_run": [str(native_bin)],
            "c_emit": [str(FORGE), "-incremental", "-emit-c", str(OUTPUT)],
            "c_compile": [
                "gcc", "-O2", "-w", "-o", str(c_bin), str(c_source),
                "-lm", "-lgmp",
            ],
            "c_run": [str(c_bin)],
        },
        "returncodes": {
            "native_compile": native_compile.returncode,
            "native_run": native_run.returncode,
            "c_emit": c_emit.returncode,
            "c_compile": c_compile.returncode,
            "c_run": c_run.returncode,
        },
        "elapsed_seconds": {
            "native_compile": t_nc,
            "native_run": t_nr,
            "c_emit": t_ce,
            "c_compile": t_cc,
            "c_run": t_cr,
        },
        "backend_stdout_sha256": {
            "native": hashlib.sha256((native_run.stdout or "").encode()).hexdigest(),
            "c": hashlib.sha256((c_run.stdout or "").encode()).hexdigest(),
        },
        "backend_agreement": backend_agreement,
        "tier3_run": False,
        "tier3_reason": "isolated method preflight; scoped both-backend and mutation rails are the falsifying suite",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    headline = (
        "Exact one-shell Grassmann/Mobius preflight passes"
        if passed
        else f"One-shell Grassmann/Mobius preflight stops at `{first_failed_gate}`"
    )
    REPORT.write_text(
        "\n".join(
            [
                "# Phase 3 axial horizon Grassmann/Mobius one-shell preflight",
                "",
                f"## {headline}",
                "",
                "The isolated rail transports the future-horizon-regular axial plane",
                "through only the first dyadic horizon shell while retaining the shared",
                "frequency generator. It does not edit or consume the predecessor's",
                "withdrawn multi-shell composer.",
                "",
                f"* Lifecycle: `{status}`",
                f"* Backend agreement: `{backend_agreement}`",
                f"* First failed gate: `{first_failed_gate}`",
                f"* Panels completed: `{len(panels)}`",
                "",
                "## Claim boundary",
                "",
                "This result does not establish an r=4 map, a global connection,",
                "scattering, flux sign, stability, a physical ghost, positivity, CPT,",
                "or unitarity.",
                "",
                f"CLOSE-OUT: {'DONE' if passed else 'SHORTFALL'} — {headline}",
                f"EVIDENCE: {CERTIFICATE.relative_to(HERE.parents[2])}",
                (
                    ""
                    if passed
                    else f"MISSING-DEP: exact repair of first failed gate {first_failed_gate}"
                ),
            ]
        )
    )
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    ATLAS.write_text(
        json.dumps(
            {
                "schema": "residual-atlas-fragment-v1",
                "result_id": certificate["result_id"],
                "status": status,
                "evidence": str(CERTIFICATE.relative_to(HERE.parents[2])),
                "scope": certificate["scope"],
                "does_not_establish": certificate["does_not_establish"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
