#!/usr/bin/env python3
"""Independent exact replay of the scoped minimal-compensator synthesis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "compensator-minimal-ladder-synthesis-after-level3b-v1.schema.json"
)
EXPECTED_IMPORTS = {
    "action_preflight": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
    "changed_causal_parent": "be7847102b7c219fd09865b68c4982c84e280e09c73364c509dcb9aaca91d6c4",
    "passive_trace_obstruction": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
    "candidate_A": "889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6",
    "candidate_B": "e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa",
    "candidate_AB": "5e253ebe424dd43e308622044d93af72fd6de911b927f354977413957dbb16c4",
    "minimal_family": "41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a",
    "active_P2": "9ad148d6b632e215cd75636f5fd5b431fa85cf1698a63f725d8b3c9dfe61de89",
    "active_P2_audit": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
    "active_P2_stability": "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
    "braiding_visibility": "bfce9fd2897511d43802c504ce10f9342b85f2e3d89ce9c4cb3e66b788905e10",
    "braiding_level2": "833d7e0266fc81df2d73e9b822db29e451d8df7f0ae9e0cbe06aa391d8dcf584",
    "literal_level3": "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed",
    "correct_level3b": "78258a1a76c81183699e8fe6923c8eccb79c030ec8174c7fe8716a97a923713c",
    "real_connection_level4": "d1037ef2fa9222d02513d093c27a02e6fc5da71ec0b731d3b9b2cd2f51e52652",
}
EXPECTED_FAMILIES = {
    "PASSIVE_TAU_ADIC_STRICT_ACTION",
    "CANDIDATE_A_TUNED_R2_AUXILIARY",
    "CANDIDATE_B_MINIMAL_HT_THREE_FORM",
    "COMPLETE_MINIMAL_POLAR_PLUS_OPTIONAL_HT",
    "ACTIVE_CLOCK_QUADRATIC_P_OF_X",
    "LEVEL2_FIRST_NONEXACT_KINETIC_BRAIDING",
    "LEVEL3_LITERAL_PLUS_FX",
    "LEVEL3B_CONVENTION_CORRECT_LINEAR_F_HORNDESKI",
    "LEVEL4_MINIMAL_REAL_WEYL_CONNECTION",
}
GATE_COLUMNS = {
    "cylinder_stationarity",
    "Berger_stationarity",
    "dressed_trace_disposition",
    "reduced_scalar_inertia",
    "principal_hyperbolicity",
    "raw_D_charge",
    "clock_health",
    "causal_parent_status",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _source_payloads(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if set(value["imports"]) != set(EXPECTED_IMPORTS):
        raise AssertionError("IMPORT_KEY_COVERAGE_MISMATCH")
    payloads = {}
    for key, expected in EXPECTED_IMPORTS.items():
        record = value["imports"][key]
        path = ROOT / record["path"]
        if record["sha256"] != expected or _sha(path) != expected:
            raise AssertionError(f"IMPORT_HASH_MISMATCH:{key}")
        payload = json.loads(path.read_text())
        if (
            payload["result_id"] != record["result_id"]
            or payload["result_state"] != record["result_state"]
        ):
            raise AssertionError(f"IMPORT_SEMANTIC_MISMATCH:{key}")
        payloads[key] = payload
    return payloads


def _independent_exact_replay() -> None:
    # Frozen P2 stacked cylinder/Berger system.
    M = sp.Matrix(
        [
            [0, 36, 3, 1, 0, 0],
            [0, 12, -1, -1, 0, 0],
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                sp.Rational(151, 160),
                1,
                sp.Rational(9, 16),
                -sp.Rational(243, 256),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                -sp.Rational(9, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                -sp.Rational(133, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
            ],
        ]
    )
    ray = sp.Matrix(
        [
            sp.Rational(81, 20),
            sp.Rational(27, 3290),
            -sp.Rational(324, 1645),
            sp.Rational(486, 1645),
            sp.Rational(18, 25),
            1,
        ]
    )
    if M.rank() != 5 or M * ray != sp.zeros(5, 1):
        raise AssertionError("P2_EXACT_LOCUS_REPLAY_MISMATCH")

    # Literal and convention-correct Level-3 coefficient distinction.
    X, Fx, B = sp.symbols("X F_X B")
    det = -36 * X**2 * (B + 2 * Fx) ** 2
    if sp.expand(det.subs(B, Fx) + 324 * X**2 * Fx**2) != 0:
        raise AssertionError("LITERAL_LEVEL3_DETERMINANT_REPLAY_MISMATCH")
    if sp.expand(det.subs(B, -2 * Fx)) != 0:
        raise AssertionError("CORRECT_LEVEL3B_DEGENERACY_REPLAY_MISMATCH")

    # Complete Level-3b cylinder locus and split auxiliary block.
    C = sp.Matrix(
        [[0, 36, 3, 1, 0, 0, 0], [0, 12, -1, -1, 0, 0, 0]]
    )
    if C.rank() != 2 or len(C.nullspace()) != 5:
        raise AssertionError("LEVEL3B_CYLINDER_LOCUS_REPLAY_MISMATCH")
    K = sp.Matrix([[0, -3], [-3, 0]])
    P = sp.Matrix([[1, 1], [1, -1]])
    if P.T * K * P != sp.diag(-6, 6):
        raise AssertionError("LEVEL3B_SPLIT_INERTIA_REPLAY_MISMATCH")

    # Minimal real-Weyl connection rank split.
    a, b = sp.symbols("a b")
    gauge = sp.Matrix([[1, a], [-1, -b], [-1, -a]])
    if sp.factor(gauge.extract([0, 1], [0, 1]).det()) != a - b:
        raise AssertionError("LEVEL4_GAUGE_MINOR_REPLAY_MISMATCH")
    if gauge.subs(b, a) * sp.Matrix([-a, 1]) != sp.zeros(3, 1):
        raise AssertionError("LEVEL4_REDUCIBILITY_REPLAY_MISMATCH")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    sources = _source_payloads(payload)
    _independent_exact_replay()

    rows = payload["theory_space_table"]
    by_id = {row["family_id"]: row for row in rows}
    if set(by_id) != EXPECTED_FAMILIES or len(rows) != len(EXPECTED_FAMILIES):
        raise AssertionError("THEORY_ROW_COVERAGE_MISMATCH")
    if set(payload["theory_space_columns"]) != GATE_COLUMNS:
        raise AssertionError("GATE_COLUMN_COVERAGE_MISMATCH")
    for row in rows:
        if not GATE_COLUMNS.issubset(row):
            raise AssertionError("MISSING_GATE_CELL")
    used = {key for row in rows for key in row["evidence_import_keys"]}
    if used != set(EXPECTED_IMPORTS):
        raise AssertionError("TABLE_IMPORT_COVERAGE_MISMATCH")

    if (
        sources["candidate_A"]["supersession"]["supersedes_result_id"]
        != sources["changed_causal_parent"]["result_id"]
        or by_id["CANDIDATE_A_TUNED_R2_AUXILIARY"]["causal_parent_status"][
            "status"
        ]
        != "SUPERSEDED"
    ):
        raise AssertionError("SUPERSESSION_BOUNDARY_MISMATCH")
    if (
        sources["candidate_AB"]["terminal_selection"] != "NEITHER"
        or sources["minimal_family"]["seven_gate_classification"][
            "all_seven_gate_good_locus"
        ]
        != "EMPTY"
    ):
        raise AssertionError("MINIMAL_TERMINAL_DISPOSITION_MISMATCH")
    if (
        payload["convention_reconciliation"]["literal_level3"]["coefficient"]
        != "+F_X"
        or payload["convention_reconciliation"]["convention_correct_level3b"][
            "coefficient"
        ]
        != "-2F_X"
        or "not rewritten" not in payload["convention_reconciliation"]["relation"]
    ):
        raise AssertionError("CONVENTION_RECONCILIATION_MISMATCH")
    if (
        payload["out_of_order_level4_reconciliation"]["science_commit"]
        != "255c53253d7d846ebbe33418d03bad791945dfd4"
        or sources["real_connection_level4"]["terminal_verdict"][
            "independent_trace_gauge_and_nonzero_clock_charge_intersection"
        ]
        != "EMPTY"
    ):
        raise AssertionError("LEVEL4_RESEQUENCING_MISMATCH")
    if (
        payload["tested_union"]["union_good_locus"]
        != "EMPTY_IN_EACH_DECLARED_COMPONENT"
        or "does not include simultaneous nonzero braiding"
        not in payload["tested_union"]["not_a_closure_under_hybrids"]
        or payload["smallest_representation_level_escape"]["activation"]
        != "PREFLIGHT_ONLY"
        or "U1" not in payload["smallest_representation_level_escape"]["mechanism"]
    ):
        raise AssertionError("SCOPE_OR_ESCAPE_BOUNDARY_MISMATCH")
    if (
        payload["terminal_verdict"]["selected_action"]
        or payload["terminal_verdict"][
            "success_path_causal_completion_activated"
        ]
        or payload["terminal_verdict"]["next_gate"]
        != "SEPARATED_SCALE_U1_CONNECTION_PREFLIGHT"
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("TERMINAL_CLAIM_BOUNDARY_MISMATCH")

    for field, section in (
        ("imports_sha256", "imports"),
        ("table_sha256", "theory_space_table"),
        ("tested_union_sha256", "tested_union"),
        ("conventions_sha256", "convention_reconciliation"),
        ("level4_sha256", "out_of_order_level4_reconciliation"),
        ("untested_sha256", "first_genuinely_untested_mechanisms"),
        ("escape_sha256", "smallest_representation_level_escape"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"CONTENT_HASH_MISMATCH:{field}")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1 "
        "independent exact replay: PASS"
    )


if __name__ == "__main__":
    main()
