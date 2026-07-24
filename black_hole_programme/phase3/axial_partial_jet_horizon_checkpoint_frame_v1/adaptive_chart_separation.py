#!/usr/bin/env python3
"""Sharp chart-separation audit at the multipanel pivot obstruction."""
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
from . import shared_remainder_multipanel_successor as successor

HERE = Path(__file__).resolve().parent
SOURCE_RUN = HERE / "shared-remainder-multipanel-successor-run.json"
RUN = HERE / "adaptive-chart-separation-run.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def reconstruct_terminal_raw() -> tuple[
    transport.DualLine, Fraction, dict, sp.Matrix
]:
    line, rho, cumulative_chart, symbolic_generator = retry.replay_to_panel_30()
    generator = transport.compile_matrix(symbolic_generator)
    full_step = transport.RHO0 / transport.PANELS

    # Reconstruct the shared-reciprocal panel-31 source.
    next_state, meta = transport.taylor_step(
        generator, line.packed(), rho, full_step
    )
    if next_state is None or not all(value.is_finite() for value in next_state):
        raise RuntimeError(f"source panel-31 replay drift: {meta}")
    line = transport.DualLine.unpacked(
        next_state, line.amplitude, line.amplitude_tangent
    )
    normalization = shared.shared_reciprocal_normalize(line, 2)
    if not normalization["passed"] or not retry.line_finite(line):
        raise RuntimeError("source shared normalization drift")
    rho += full_step

    substep = full_step / successor.SUBDIVISIONS
    for index in range(9):
        next_state, meta = transport.taylor_step(
            generator, line.packed(), rho, substep
        )
        if next_state is None or not all(value.is_finite() for value in next_state):
            raise RuntimeError(f"accepted substep replay drift: {index}")
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        normalization = shared.shared_reciprocal_normalize(line, 2)
        if not normalization["passed"] or not retry.line_finite(line):
            raise RuntimeError(f"accepted normalization replay drift: {index}")
        rho += substep

    terminal_state, terminal_meta = transport.taylor_step(
        generator, line.packed(), rho, substep
    )
    if terminal_state is None or not all(
        value.is_finite() for value in terminal_state
    ):
        raise RuntimeError("terminal raw Taylor state drift")
    terminal = transport.DualLine.unpacked(
        terminal_state, line.amplitude, line.amplitude_tangent
    )
    return terminal, rho + substep, terminal_meta, cumulative_chart


def linear_form(row: tuple[sp.Rational, ...], vector: list[acb]) -> acb:
    return sum(
        (
            transport.cf(row[index]) * vector[index]
            for index in range(len(vector))
        ),
        acb(0),
    )


def midpoint_pair(value: acb) -> tuple[str, str]:
    return str(value.real.mid()), str(value.imag.mid())


def compute() -> dict:
    ctx.prec = 256
    source = json.loads(SOURCE_RUN.read_text())
    terminal, endpoint_rho, terminal_meta, cumulative_chart = (
        reconstruct_terminal_raw()
    )
    source_terminal = source["terminal"]
    if str(endpoint_rho) != source_terminal["attempted_endpoint_rho"]:
        raise RuntimeError("terminal endpoint drift")
    if terminal_meta != source_terminal["step"]:
        raise RuntimeError("terminal Taylor metadata drift")

    zero_membership = [
        value.real.contains(0) and value.imag.contains(0)
        for value in terminal.base
    ]
    if not all(zero_membership):
        raise RuntimeError("universal Cartesian zero-membership drift")

    # Deterministic midpoint-derived row: round the dominant midpoint pattern
    # (0,0,1,-1/2) to half-integers.  It is completed to a determinant-one GL.
    midpoint_row = (
        sp.Rational(0),
        sp.Rational(0),
        sp.Rational(1),
        sp.Rational(-1, 2),
    )
    midpoint_chart = sp.eye(4)
    midpoint_chart[2, :] = sp.Matrix([midpoint_row])
    if midpoint_chart.det() != 1:
        raise RuntimeError("midpoint-derived chart determinant drift")

    candidates = {
        "midpoint_rounded_half_integer": midpoint_row,
        "e2": (sp.Rational(0), sp.Rational(0), sp.Rational(1), sp.Rational(0)),
        "e3": (sp.Rational(0), sp.Rational(0), sp.Rational(0), sp.Rational(1)),
        "e2-e3": (
            sp.Rational(0),
            sp.Rational(0),
            sp.Rational(1),
            sp.Rational(-1),
        ),
        "e2+e3": (
            sp.Rational(0),
            sp.Rational(0),
            sp.Rational(1),
            sp.Rational(1),
        ),
    }
    candidate_results = {}
    for name, row in candidates.items():
        denominator = linear_form(row, terminal.base)
        candidate_results[name] = {
            "row": [str(value) for value in row],
            "denominator": str(denominator),
            "midpoint": list(midpoint_pair(denominator)),
            "midpoint_modulus_nonzero": (
                denominator.real.mid() != 0 or denominator.imag.mid() != 0
            ),
            "modulus_lower": str(denominator.abs_lower()),
            "excludes_zero": denominator.abs_lower() > 0,
        }
    if any(row["excludes_zero"] for row in candidate_results.values()):
        raise RuntimeError("candidate atlas unexpectedly separates zero")
    midpoint_candidate = candidate_results["midpoint_rounded_half_integer"]
    if not midpoint_candidate["midpoint_modulus_nonzero"]:
        raise RuntimeError("midpoint mutation witness drift")

    enclosure_payload = {
        "base": transport.serialize_vector(terminal.base),
        "tangent": transport.serialize_vector(terminal.tangent),
        "cumulative_chart": [
            [str(cumulative_chart[i, j]) for j in range(4)] for i in range(4)
        ],
    }
    return {
        "schema": "phase3-axial-horizon-adaptive-chart-separation-run-v1",
        "frequency": source["frequency"],
        "precision_bits": ctx.prec,
        "source": {
            "path": str(SOURCE_RUN.relative_to(HERE.parents[2])),
            "sha256": hashlib.sha256(SOURCE_RUN.read_bytes()).hexdigest(),
            "accepted_substeps": source["accepted_substeps"],
            "rho": source["reached_rho"],
        },
        "terminal_raw_enclosure": {
            "rho": str(endpoint_rho),
            "state_finite": retry.line_finite(terminal),
            "base_component_zero_membership": zero_membership,
            "zero_vector_in_cartesian_base_enclosure": all(zero_membership),
            "payload": enclosure_payload,
            "content_sha256": canonical_hash(enclosure_payload),
            "taylor_gate": terminal_meta,
        },
        "midpoint_adaptive_chart": {
            "rule": (
                "round the terminal base midpoint direction to half-integers"
            ),
            "matrix": [
                [str(midpoint_chart[i, j]) for j in range(4)] for i in range(4)
            ],
            "determinant": str(midpoint_chart.det()),
            "candidate": midpoint_candidate,
            "certified": False,
        },
        "finite_candidate_atlas": candidate_results,
        "universal_linear_separation": {
            "certified": True,
            "premise": "0 belongs to the Cartesian enclosure of the base vector",
            "conclusion": (
                "for every fixed complex row m, 0=m*0 belongs to the "
                "enclosure image m(B); no fixed GL/Mobius denominator can "
                "be certified nonzero from this enclosure"
            ),
            "scope": (
                "the current rectangular Cartesian enclosure only; a stronger "
                "affine/Taylor-model set may exclude the zero vector"
            ),
        },
        "mutation_witness": {
            "mutant_rule": "accept if the candidate midpoint is nonzero",
            "mutant_accepts": midpoint_candidate["midpoint_modulus_nonzero"],
            "correct_full_ball_gate_accepts": midpoint_candidate["excludes_zero"],
            "mutation_killed": (
                midpoint_candidate["midpoint_modulus_nonzero"]
                and not midpoint_candidate["excludes_zero"]
            ),
        },
        "terminal": {
            "gate": "UNIVERSAL_FIXED_LINEAR_CHART_SEPARATION_OBSTRUCTION",
            "successor_substeps_accepted": 0,
            "rho": source["reached_rho"],
            "attempted_endpoint_rho": str(endpoint_rho),
        },
        "claim_flags": {
            "midpoint_candidate_constructed": True,
            "midpoint_candidate_denominator_excludes_zero": False,
            "finite_candidate_atlas_exhausted": True,
            "universal_fixed_linear_obstruction_certified": True,
            "midpoint_only_mutant_killed": True,
            "successor_substep_certified": False,
            "next_base_panel_completed": False,
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
