#!/usr/bin/env python3
"""Independently replay the quadratic nonlinear auxiliary shift."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def matrix(value: object) -> list[list[Fraction]]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError
    rows = [[Fraction(entry) for entry in row] for row in value]
    if any(len(row) != 4 for row in rows):
        raise ValueError
    return rows


def add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(4)] for i in range(4)]


def scale(factor: Fraction, value: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[factor * entry for entry in row] for row in value]


def contract(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction(0))


def exact_replay(fixture: dict[str, Any]) -> bool:
    try:
        metric = matrix(fixture["normal_frame_metric"])
        inverse = matrix(fixture["normal_frame_inverse_metric"])
        vector = [Fraction(entry) for entry in fixture["v_direction_covariant"]]
        f_hat = matrix(fixture["f_hat_direction_contravariant"])
        v2 = sum((inverse[i][j] * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))
        outer = [[vector[i] * vector[j] for j in range(4)] for i in range(4)]
        g2 = add(scale(Fraction(1, 2), outer), scale(Fraction(1, 4) * v2, metric))
        tr_g2 = contract(inverse, g2)
        ainv = add(scale(-2, g2), scale(Fraction(2, 3) * tr_g2, metric))
        mass_ainv = add(scale(-Fraction(1, 2), ainv), scale(Fraction(1, 2) * contract(inverse, ainv), metric))
        pairing = contract(f_hat, g2)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
    serialize = lambda value: [[str(entry) for entry in row] for row in value]
    return (
        len(vector) == 4
        and fixture.get("v_squared") == str(v2) == "1"
        and fixture.get("G_b_quadratic_tensor") == serialize(g2)
        and fixture.get("trace_G_b_quadratic") == str(tr_g2) == "3/2"
        and fixture.get("A_g_inverse_G_b_quadratic") == serialize(ainv)
        and fixture.get("source_to_split_quadratic_shift") == serialize(scale(-1, ainv))
        and mass_ainv == g2
        and fixture.get("A_g_of_A_g_inverse_G_b_quadratic_equals_G_b_quadratic") is True
        and fixture.get("f_hat_pair_G_b_quadratic") == str(pairing) == "1/2"
        and fixture.get("source_f_hat_v_v_mixed_polarization") == str(-2 * pairing) == "-1"
        and fixture.get("inverse_shift_mass_cross_mixed_polarization") == str(2 * pairing) == "1"
        and fixture.get("corrected_channel_residual") == "0"
    )


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    action, split, predecessor = (json.loads(path.read_text()) for path in (ACTION, SPLIT, PREDECESSOR))
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1" or value.get("result_state") != "QUADRATIC_VECTOR_COMPONENT_EXPORTED_ONE_CUBIC_CHANNEL_CANCELED_FULL_CYCLIC_EQUIVALENCE_OPEN":
        errors.append("result identity/state")
    if value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("lifecycle/dependency")
    qmap = value.get("quadratic_auxiliary_map", {})
    if qmap.get("full_source_to_split_map") != "phi_hat=phi-A_g^{-1}G^b(g,b)" or qmap.get("source_to_split_homogeneous_quadratic_component") != "F_(2)(v)=v tensor v-(1/2)g v^2":
        errors.append("quadratic map formula")
    if not exact_replay(qmap.get("fixture", {})):
        errors.append("exact fixture replay")
    disposition = value.get("disposition", {})
    if disposition.get("first_required_quadratic_component_constructed") is not True or disposition.get("f_hat_v_v_channel_canceled_after_inverse_pullback") is not True or disposition.get("full_candidate_L_infinity_equivalence_constructed") is not False or "h-f_hat-f_hat" not in disposition.get("reason_full_equivalence_open", ""):
        errors.append("equivalence boundary")
    flags = value.get("claim_flags", {})
    for key in ("AUTHORITATIVE_QUADRATIC_AUXILIARY_MAP_EXPORTED", "LOCAL_BV_CANONICAL_LIFT_AVAILABLE", "F_HAT_V_V_CHANNEL_CANCELED_BY_PULLBACK"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("USES_GREEN_OPERATOR", "USES_CHOICE_PRINCIPLE", "FULL_NONMINIMAL_Q2_PULLBACK_REPLAYED", "FULL_NONMINIMAL_Q3_PULLBACK_REPLAYED", "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    if value.get("canonical_hashes") != {"quadratic_auxiliary_map_sha256": digest(qmap), "disposition_sha256": digest(disposition)}:
        errors.append("canonical hashes")
    expected = {
        (str(ACTION.relative_to(ROOT)), action["schema"], sha(ACTION)),
        (str(SPLIT.relative_to(ROOT)), split["schema"], sha(SPLIT)),
        (str(PREDECESSOR.relative_to(ROOT)), predecessor["result_id"], sha(PREDECESSOR)),
    }
    actual = {(item.get("path"), item.get("schema", item.get("result_id")), item.get("sha256")) for item in value.get("provenance", {}).get("inputs", [])}
    if actual != expected:
        errors.append("provenance")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
