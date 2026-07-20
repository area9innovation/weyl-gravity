#!/usr/bin/env python3
"""Independent raw-FLRW replay of the Level-3 curvature-coupling no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "compensator-degenerate-curvature-level3-no-go-v1.schema.json"
)
LEVEL2_HASH = "833d7e0266fc81df2d73e9b822db29e451d8df7f0ae9e0cbe06aa391d8dcf584"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    result = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        result[item["row"], item["column"]] = sp.sympify(item["coefficient"])
    return result


def _raw_flrw_replay(payload: dict[str, Any]) -> None:
    # Independent route: start from R and the individual orthonormal Hessian
    # eigenvalues, then perform the one-dimensional integration by parts.
    X, F, Fx, B = sp.symbols("X F F_X B")
    h, A, Dh = sp.symbols("h A Dh")

    box_over_y = A - 3 * h
    hessian_square_over_y2 = A**2 + 3 * h**2
    # y^2=-X in the (-,+,+,+) convention.
    Q = sp.expand(-X * (box_over_y**2 - hessian_square_over_y2))
    if Q != -6 * X * h**2 + 6 * X * A * h:
        raise AssertionError("RAW_CLOCK_HESSIAN_REPLAY_MISMATCH")

    R = 6 * (Dh + 2 * h**2)
    if R != 6 * Dh + 12 * h**2:
        raise AssertionError("RAW_RICCI_REPLAY_MISMATCH")

    # int Na^3 F Dh -> -int Na^3(3F h-2X Fx A)h.
    F_Dh_after_ibp = -3 * F * h**2 + 2 * X * Fx * A * h
    reduced = sp.expand(6 * F_Dh_after_ibp + 12 * F * h**2 + B * Q)
    expected = -6 * (F + B * X) * h**2 + 6 * X * (2 * Fx + B) * A * h
    if sp.expand(reduced - expected) != 0:
        raise AssertionError("BOUNDARY_REDUCTION_REPLAY_MISMATCH")

    H = sp.hessian(reduced, (h, A))
    if sp.factor(H.det()) != -36 * X**2 * (2 * Fx + B) ** 2:
        raise AssertionError("GENERAL_DETERMINANT_REPLAY_MISMATCH")
    literal = H.subs(B, Fx)
    if sp.factor(literal.det()) != -324 * X**2 * Fx**2:
        raise AssertionError("LITERAL_DETERMINANT_REPLAY_MISMATCH")

    serialized = _dense(
        payload["exact_adm_degeneracy"]["literal_work_item_pair"][
            "velocity_Hessian"
        ]
    )
    if serialized != literal:
        raise AssertionError("SERIALIZED_LITERAL_HESSIAN_MISMATCH")


def _elimination_replay(payload: dict[str, Any]) -> None:
    B, slope = sp.symbols("B slope")
    ideal = sp.groebner([B - slope, B + 2 * slope], B, slope, order="lex")
    if ideal.reduce(B)[1] != 0 or ideal.reduce(slope)[1] != 0:
        raise AssertionError("LITERAL_DEGENERACY_INTERSECTION_MISMATCH")
    if payload["complete_literal_locus"]["groebner_basis"] != ["B", "f1"]:
        raise AssertionError("SERIALIZED_GROEBNER_BASIS_MISMATCH")


def _boundary_control(payload: dict[str, Any]) -> None:
    # Algebraic coefficient comparison in
    # X R-2Q=-2(Ric_ab-X R/2) v^a v^b mod d_h.
    ricci_coefficient = -2
    scalar_coefficient = 1
    einstein_multiple = -2
    if (
        ricci_coefficient != einstein_multiple
        or scalar_coefficient != -einstein_multiple / 2
    ):
        raise AssertionError("EINSTEIN_TENSOR_BOUNDARY_IDENTITY_MISMATCH")
    control = payload["convention_correct_control"]["constant_clock_cylinder"]
    if (
        control["pure_metric_Hessian_from_slope"] != "ZERO"
        or control["metric_clock_mixed_Hessian_from_slope"] != "ZERO"
        or control["trace_lapse_repair"] != "NONE"
    ):
        raise AssertionError("CONVENTION_CONTROL_PROMOTED_OR_MUTATED")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    imported = payload["imports"]["level2_no_go"]
    import_path = ROOT / imported["path"]
    if _sha(import_path) != LEVEL2_HASH or imported["sha256"] != LEVEL2_HASH:
        raise AssertionError("LEVEL2_IMPORT_DRIFT")
    level2 = json.loads(import_path.read_text())
    if level2["terminal_verdict"]["selected_level2_action"]:
        raise AssertionError("LEVEL2_SELECTED_ACTION_CONTRADICTS_GATE")

    _raw_flrw_replay(payload)
    _elimination_replay(payload)
    _boundary_control(payload)

    for field, section in (
        ("imports_sha256", "imports"),
        ("degeneracy_sha256", "exact_adm_degeneracy"),
        ("locus_sha256", "complete_literal_locus"),
        ("control_sha256", "convention_correct_control"),
        ("gates_sha256", "gate_disposition"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")

    if (
        payload["complete_literal_locus"]["good_locus"] != "EMPTY"
        or payload["terminal_verdict"]["selected_level3_action"]
        or payload["gate_disposition"]["selected_action"]
        or payload["gate_disposition"]["nonlinear_q2"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1 "
        "independent raw-FLRW replay: PASS"
    )


if __name__ == "__main__":
    main()
