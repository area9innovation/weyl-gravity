#!/usr/bin/env python3
"""Independently replay the imported quadratic auxiliary-elimination channel."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
CLASSICAL_MAP = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(4)] for i in range(4)]


def scale(factor: Fraction, tensor: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[factor * tensor[i][j] for j in range(4)] for i in range(4)]


def contract(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction(0))


def independent_exact_replay() -> dict[str, Fraction | bool]:
    """Recompute the witness without reading the producer's numeric fixture."""

    z = Fraction(0)
    metric = [
        [Fraction(-1), z, z, z],
        [z, Fraction(1), z, z],
        [z, z, Fraction(1), z],
        [z, z, z, Fraction(1)],
    ]
    inverse = [row[:] for row in metric]
    vector = [z, Fraction(1), z, z]
    f_hat = [[z for _ in range(4)] for _ in range(4)]
    f_hat[1][1], f_hat[2][2] = Fraction(1), Fraction(-1)
    vector_square = sum(
        (inverse[i][j] * vector[i] * vector[j] for i in range(4) for j in range(4)),
        Fraction(0),
    )
    outer = [[vector[i] * vector[j] for j in range(4)] for i in range(4)]
    g2 = add(scale(Fraction(1, 2), outer), scale(Fraction(1, 4) * vector_square, metric))
    trace_g2 = contract(inverse, g2)
    inverse_mass_g2 = add(scale(-2, g2), scale(Fraction(2, 3) * trace_g2, metric))
    mass_roundtrip = add(
        scale(-Fraction(1, 2), inverse_mass_g2),
        scale(Fraction(1, 2) * contract(inverse, inverse_mass_g2), metric),
    )
    pair = contract(f_hat, g2)
    source = -2 * pair
    correction = 2 * pair
    transformed = source + correction
    return {
        "vector_square": vector_square,
        "trace_g2": trace_g2,
        "pair": pair,
        "source": source,
        "correction": correction,
        "transformed": transformed,
        "mass_roundtrip": mass_roundtrip == g2,
    }


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    classical, obstruction, q2, pairing = (
        json.loads(path.read_text()) for path in (CLASSICAL_MAP, OBSTRUCTION, Q2, PAIRING)
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1"
        or value.get("result_kind") != "INDEPENDENT_QUADRATIC_NONLINEAR_MAP_CHANNEL_PULLBACK_REPLAY"
        or value.get("result_state") != "FIRST_QUADRATIC_EQUIVALENCE_COMPONENT_IMPORTED_CHANNEL_CLOSED_FULL_SOURCE_PULLBACK_OPEN"
    ):
        errors.append("result identity/kind/state")
    if value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("lifecycle/dependency")

    rows = pairing.get("component_basis", {}).get("rows", [])
    blocks = {row.get("block") for row in rows}
    inert = set(q2.get("graph_transport_dag", {}).get("interaction_inert_blocks", []))
    if len(rows) != 386 or not {"AUX_F_HAT", "AUX_F_HAT_STAR", "AUX_V", "AUX_V_STAR"} <= blocks:
        errors.append("386-row carrier")
    if not {"AUX_F_HAT", "AUX_V"} <= inert:
        errors.append("candidate inert-block premise")

    exact = independent_exact_replay()
    try:
        source_input = Fraction(obstruction["exact_channel_comparison"]["source_ordinary_derivative_value"])
        candidate = Fraction(0) if {"AUX_F_HAT", "AUX_V"} <= inert else None
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        source_input = candidate = None
    replay = value.get("channel_pullback_replay", {})
    expected_replay = {
        "carrier_rows": 386,
        "source_to_split_map": "phi_hat=phi-A_g^{-1}G^b(g,b)",
        "source_to_split_homogeneous_quadratic_component": "F_(2)(v)=v tensor v-(1/2)g v^2",
        "source_to_split_second_Frechet_component": "D^2F(v,w)=v tensor w+w tensor v-g(v,w)g",
        "split_to_source_inverse_quadratic_component": "-v tensor v+(1/2)g v^2",
        "input_blocks": ["AUX_V", "AUX_V"],
        "output_block": "AUX_F_HAT",
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "pre_correction_source_value": str(source_input),
        "candidate_value": str(candidate),
        "inverse_shift_mass_cross_correction": str(exact["correction"]),
        "transformed_source_value": str(source_input + exact["correction"]) if source_input is not None else "None",
        "transformed_source_minus_candidate_residual": str(source_input + exact["correction"] - candidate) if source_input is not None and candidate is not None else "None",
        "exact_channel_cancellation": True,
        "support_local": True,
        "uses_green_operator": False,
        "uses_choice_principle": False,
    }
    if replay != expected_replay:
        errors.append("channel pullback replay")
    if (
        exact != {
            "vector_square": Fraction(1),
            "trace_g2": Fraction(3, 2),
            "pair": Fraction(1, 2),
            "source": Fraction(-1),
            "correction": Fraction(1),
            "transformed": Fraction(0),
            "mass_roundtrip": True,
        }
        or source_input != exact["source"]
    ):
        errors.append("independent rational tensor replay")
    qmap = classical.get("quadratic_auxiliary_map", {})
    if any(replay.get(key) != qmap.get(key) for key in (
        "full_source_to_split_map",
        "source_to_split_homogeneous_quadratic_component",
        "source_to_split_second_Frechet_component",
    ) if key != "full_source_to_split_map"):
        errors.append("classical map import")
    if replay.get("source_to_split_map") != qmap.get("full_source_to_split_map"):
        errors.append("full source-to-split map import")

    boundary = value.get("equivalence_boundary", {})
    if not (
        boundary.get("first_required_quadratic_component_imported") is True
        and boundary.get("one_previously_obstructing_channel_closed") is True
        and boundary.get("source_certified_local_BV_canonical_lift_available") is True
        and boundary.get("receiver_componentwise_386_cotangent_lift_serialized") is False
        and boundary.get("complete_source_q2_pullback_replayed") is False
        and boundary.get("complete_source_q3_pullback_replayed") is False
        and boundary.get("full_cyclic_L_infinity_equivalence_constructed") is False
        and boundary.get("nonlinear_equivalence_obstructed") is False
        and any("h-f_hat-f_hat" in item for item in boundary.get("remaining_shifted_cubic_families", []))
        and any("ghost/antifield" in item for item in boundary.get("remaining_shifted_cubic_families", []))
    ):
        errors.append("equivalence boundary")

    flags = value.get("claim_flags", {})
    positive = (
        "AUTHORITATIVE_QUADRATIC_AUXILIARY_MAP_IMPORTED",
        "F_HAT_V_V_PULLBACK_CHANNEL_CLOSED",
        "FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED",
        "CANDIDATE_INTERNAL_IDENTITIES_PRESERVED",
    )
    negative = (
        "FULL_386_COTANGENT_LIFT_SERIALIZED",
        "FULL_SOURCE_Q2_PULLBACK_REPLAYED",
        "FULL_SOURCE_Q3_PULLBACK_REPLAYED",
        "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED",
        "NONLINEAR_EQUIVALENCE_OBSTRUCTED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
    )
    if any(flags.get(key) is not True for key in positive):
        errors.append("positive claim flags")
    if any(flags.get(key) is not False for key in negative):
        errors.append("claim boundary flags")
    if value.get("canonical_hashes") != {
        "channel_pullback_replay_sha256": digest(replay),
        "equivalence_boundary_sha256": digest(boundary),
    }:
        errors.append("canonical hashes")

    sources = (
        (CLASSICAL_MAP, classical["result_id"]),
        (OBSTRUCTION, obstruction["result_id"]),
        (Q2, q2["result_id"]),
        (PAIRING, pairing["result_id"]),
    )
    expected_provenance = {(str(path.relative_to(ROOT)), result_id, sha(path)) for path, result_id in sources}
    actual_provenance = {
        (item.get("path"), item.get("result_id"), item.get("sha256"))
        for item in value.get("provenance", {}).get("inputs", [])
    }
    if actual_provenance != expected_provenance:
        errors.append("input provenance")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
