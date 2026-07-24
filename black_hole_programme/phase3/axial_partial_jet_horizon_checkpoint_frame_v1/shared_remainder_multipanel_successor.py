#!/usr/bin/env python3
"""Content-addressed continuation of the shared-reciprocal horizon line."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import acb, ctx

from . import checkpoint_transport as transport
from . import pivot_switch as repair
from . import pivot_switch_continuation as continuation
from . import pivot_switch_shared_remainder_preflight as shared
from . import pivot_switch_subdivision_retry as retry

HERE = Path(__file__).resolve().parent
SOURCE_RUN = HERE / "pivot-switch-shared-remainder-preflight-run.json"
RUN = HERE / "shared-remainder-multipanel-successor-run.json"

SUBDIVISIONS = 128
WIDTH_LIMIT = 10**12


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode()
    return sha256_bytes(encoded)


def parse_vector(items: list[dict]) -> list[acb]:
    return [acb(item["ball"]) for item in items]


def parse_line(payload: dict) -> transport.DualLine:
    return transport.DualLine(
        tangent=parse_vector(payload["tangent"]),
        base=parse_vector(payload["base"]),
        amplitude=acb(payload["amplitude"]["ball"]),
        amplitude_tangent=acb(payload["amplitude_tangent"]["ball"]),
        pivot=payload["pivot"],
    )


def packed_width(line: transport.DualLine):
    return max(
        (
            transport.width(value)
            for value in [
                *line.packed(),
                line.amplitude,
                line.amplitude_tangent,
            ]
        ),
        default=transport.arb(0),
    )


def generator_hash(symbolic_generator: sp.Matrix) -> str:
    payload = [
        [str(sp.cancel(symbolic_generator[i, j])) for j in range(symbolic_generator.cols)]
        for i in range(symbolic_generator.rows)
    ]
    return canonical_hash(payload)


def addressed_checkpoint(
    line: transport.DualLine,
    rho: Fraction,
    cumulative_chart: sp.Matrix,
    generator_sha256: str,
    parent_sha256: str,
    substep_index: int,
) -> dict:
    payload = {
        "schema": "phase3-shared-remainder-resume-checkpoint-v1",
        "rho": str(rho),
        "r": str(rho + 2),
        "substep_index": substep_index,
        "parent_sha256": parent_sha256,
        "generator_sha256": generator_sha256,
        "representation": "shared-reciprocal dual projective chart",
        "normalization": {
            "pivot": 2,
            "exact_base_pivot": "1",
            "exact_tangent_pivot": "0",
        },
        "cumulative_chart": [
            [str(cumulative_chart[i, j]) for j in range(4)] for i in range(4)
        ],
        "line": repair.line_payload(line),
    }
    return {**payload, "content_sha256": canonical_hash(payload)}


def compute() -> dict:
    ctx.prec = 256
    source = json.loads(SOURCE_RUN.read_text())
    if not source["claim_flags"]["post_normalization_finite"]:
        raise RuntimeError("source shared-remainder gate drift")
    source_checkpoint = source["checkpoint"]

    # Reconstruct the content-addressed source through its certified producer,
    # because the human-readable ball strings are deliberately not treated as
    # a second interval parser.  Exact serialization below must match the
    # committed checkpoint byte-for-byte.
    line, rho, cumulative_chart, symbolic_generator = retry.replay_to_panel_30()
    generator = transport.compile_matrix(symbolic_generator)
    source_step = transport.RHO0 / transport.PANELS
    source_next, source_meta = transport.taylor_step(
        generator, line.packed(), rho, source_step
    )
    if source_next is None or not all(value.is_finite() for value in source_next):
        raise RuntimeError(f"source panel-31 replay drift: {source_meta}")
    line = transport.DualLine.unpacked(
        source_next, line.amplitude, line.amplitude_tangent
    )
    source_normalization = shared.shared_reciprocal_normalize(line, 2)
    if not source_normalization["passed"] or not retry.line_finite(line):
        raise RuntimeError("source shared-reciprocal normalization drift")
    rho += source_step
    if repair.line_payload(line) != source_checkpoint["line"]:
        raise RuntimeError("source checkpoint serialization drift")
    if str(rho) != source_checkpoint["rho"]:
        raise RuntimeError("source checkpoint rho drift")
    if [
        [str(cumulative_chart[i, j]) for j in range(4)] for i in range(4)
    ] != source_checkpoint["cumulative_chart"]:
        raise RuntimeError("source cumulative chart drift")
    generator_sha256 = generator_hash(symbolic_generator)

    full_step = transport.RHO0 / transport.PANELS
    substep = full_step / SUBDIVISIONS
    parent_sha256 = sha256(SOURCE_RUN)
    checkpoints = []
    gates = []
    terminal = None
    for index in range(SUBDIVISIONS):
        next_state, step_meta = transport.taylor_step(
            generator, line.packed(), rho, substep
        )
        if next_state is None:
            terminal = {
                "gate": "TAYLOR_REFUSAL",
                "substep_index": index,
                "rho": str(rho),
                "detail": step_meta,
            }
            break
        if not all(value.is_finite() for value in next_state):
            terminal = {
                "gate": "NONFINITE_TAYLOR_ENCLOSURE",
                "substep_index": index,
                "rho": str(rho),
                "detail": step_meta,
            }
            break
        raw_line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        selected, atlas_lowers = continuation.choose_chart(raw_line)
        if selected != "e2":
            terminal = {
                "gate": "FIXED_ATLAS_PIVOT_OBSTRUCTION",
                "substep_index": index,
                "rho": str(rho),
                "attempted_endpoint_rho": str(rho + substep),
                "selected": selected,
                "atlas_modulus_lowers": atlas_lowers,
                "step": step_meta,
            }
            break
        normalization = shared.shared_reciprocal_normalize(raw_line, 2)
        if not normalization["passed"] or not retry.line_finite(raw_line):
            terminal = {
                "gate": normalization.get(
                    "gate", "NONFINITE_POST_SHARED_NORMALIZATION"
                ),
                "substep_index": index,
                "rho": str(rho),
                "attempted_endpoint_rho": str(rho + substep),
                "atlas_modulus_lowers": atlas_lowers,
                "normalization": normalization,
                "step": step_meta,
            }
            break
        width = packed_width(raw_line)
        if not width.is_finite() or width > WIDTH_LIMIT:
            terminal = {
                "gate": "WIDTH_LIMIT",
                "substep_index": index,
                "rho": str(rho),
                "attempted_endpoint_rho": str(rho + substep),
                "width_upper": str(width.upper()),
                "width_limit": str(WIDTH_LIMIT),
                "step": step_meta,
            }
            break
        line = raw_line
        rho += substep
        checkpoint = addressed_checkpoint(
            line,
            rho,
            cumulative_chart,
            generator_sha256,
            parent_sha256,
            index,
        )
        parent_sha256 = checkpoint["content_sha256"]
        checkpoints.append(checkpoint)
        gates.append(
            {
                "substep_index": index,
                "rho": str(rho),
                "step": step_meta,
                "atlas_modulus_lowers": atlas_lowers,
                "normalization": normalization,
                "post_normalization_finite": True,
                "width_upper": str(width.upper()),
                "generator_sha256": generator_sha256,
                "checkpoint_sha256": checkpoint["content_sha256"],
            }
        )
    if terminal is None:
        raise RuntimeError("bounded successor unexpectedly completed base panel")
    return {
        "schema": "phase3-axial-horizon-shared-remainder-multipanel-successor-run-v1",
        "frequency": source["frequency"],
        "precision_bits": ctx.prec,
        "source": {
            "path": str(SOURCE_RUN.relative_to(HERE.parents[2])),
            "sha256": sha256(SOURCE_RUN),
            "panel": source["target"]["panel"],
            "rho": source["target"]["rho"],
            "checkpoint_representation": source["representation"]["kind"],
        },
        "controls": {
            "subdivisions_per_base_panel": SUBDIVISIONS,
            "substep": str(substep),
            "width_limit": str(WIDTH_LIMIT),
            "fixed_atlas": list(continuation.ATLAS),
            "required_chart": "e2",
            "normalization": "one shared reciprocal per accepted substep",
            "generator_sha256": generator_sha256,
        },
        "accepted_substeps": len(checkpoints),
        "reached_rho": str(rho),
        "checkpoint_chain": checkpoints,
        "gate_ledger": gates,
        "terminal": terminal,
        "claim_flags": {
            "source_checkpoint_hash_bound": True,
            "generator_hash_stable": True,
            "all_accepted_checkpoints_content_addressed": True,
            "shared_reciprocal_used_at_every_accepted_substep": True,
            "post_normalization_finite_at_every_checkpoint": True,
            "first_obstruction_fail_closed": True,
            "next_base_panel_completed": False,
            "next_dyadic_shell_reached": False,
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
