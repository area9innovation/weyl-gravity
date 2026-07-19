#!/usr/bin/env python3
"""Independent replay of the physical curvature-squared Hessian import."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-curvature-squared-v1.schema.json"

EXPECTED = [
    ("H201", Fraction(1), "(R^2/6-Ric^2+Riem^2/2)(g_mn g_ab-g_ma g_nb)", True, False, False),
    ("H202", Fraction(1), "R g_nb Ric_ma", False, False, False),
    ("H203", Fraction(-1, 2), "R g_ab Ric_mn", False, True, False),
    ("H204", Fraction(-1, 2), "R g_mn Ric_ab", False, True, False),
    ("H205", Fraction(1, 3), "R Riem_manb", False, False, False),
    ("H206", Fraction(4), "g_ab Ric_mr Ric_n^r", True, True, False),
    ("H207", Fraction(0), "Ric_ma Ric_nb", True, False, True),
    ("H208", Fraction(2, 3), "Ric_mn Ric_ab", True, False, False),
    ("H209", Fraction(-2), "g_nb Ric_mr Ric_a^r", True, False, False),
    ("H210", Fraction(2), "g_ab Ric^rl Riem_rm ln", True, True, False),
    ("H211", Fraction(-4), "g_nb Ric^rl Riem_mr al", True, False, False),
    ("H212", Fraction(12), "Ric^r_m Riem_rabn", True, False, False),
    ("H213", Fraction(8), "Riem_ram l Riem_nb^rl", True, False, False),
    ("H214", Fraction(-3, 2), "g_ab Riem_mrls Riem_n^rls", True, True, False),
    ("H215", Fraction(-2), "Riem_ram l Riem^r_nb^l", True, False, False),
    ("H216", Fraction(6), "Riem_rm ln Riem^r_a^l_b", True, False, False),
    ("H217", Fraction(3), "g_nb Riem_m^rls Riem_a rls", True, False, False),
    ("H218", Fraction(-3, 2), "g_mn Riem_a rls Riem_b rls", True, True, False),
]


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    source = stored["source_provenance"]
    if (
        source["source_archive_sha256"]
        != "f340a38925ea92a23b8ec0b08d0a871a77f549c79d7c41962158bcac6787fe39"
        or source["decompressed_tex_sha256"]
        != "03b79eb2fa03754c04aa1e1d653d4690e7a44a7f48f9ad402826ea670a8529e0"
    ):
        raise ValueError("physical H2 source digest drifted")

    couplings = stored["coupling_specialization"]
    if (
        _fraction(couplings["pure_Weyl_choice"]["alpha"]) != Fraction(1, 6)
        or _fraction(couplings["pure_Weyl_choice"]["beta"]) != -1
        or _fraction(couplings["pure_Weyl_choice"]["gamma"]) != Fraction(1, 2)
        or _fraction(couplings["leading_K_on_traceless_bundle"]) != Fraction(1, 4)
        or _fraction(couplings["monic_left_factor"]) != 4
    ):
        raise ValueError("pure-Weyl H2 specialization drifted")

    rows = stored["source_operator"]["coefficient_rows"]
    actual = [
        (
            row["term_id"],
            _fraction(row["coefficient"]),
            row["seed"],
            row["scalar_flat_survives"],
            row["tracefree_null"],
            row["source_cancellation"],
        )
        for row in rows
    ]
    if actual != EXPECTED or any(
        row["curvature_order"] != 2
        or row["operator_derivatives"] != 0
        or row["total_engineering_order"] != 4
        for row in rows
    ):
        raise ValueError("projected H2 coefficient row drifted")
    if stored["source_operator"]["formula_digest"] != _digest(rows):
        raise ValueError("physical H2 formula digest drifted")

    gauge = stored["gauge_ordering_crosswalk"]
    if (
        _fraction(gauge["source_ordering"]["c"]) != Fraction(2, 3)
        or _fraction(gauge["source_ordering"]["d"]) != 1
        or _fraction(gauge["repository_ordering"]["c"]) != Fraction(-1, 3)
        or _fraction(gauge["repository_ordering"]["d"]) != 0
    ):
        raise ValueError("physical H2 gauge-ordering crosswalk drifted")
    for fixture in gauge["exact_fixture_ledger"]:
        if (
            _fraction(fixture["repository_minus_source"])
            != 2 * _fraction(fixture["G_Ric"])
            or _fraction(fixture["ratio"]) != 2
        ):
            raise ValueError("H1 commutator fixture failed")

    scalar_flat = stored["scalar_flat_restriction"]
    replay_ids = [
        row["term_id"]
        for row in rows
        if row["scalar_flat_survives"]
        and not row["tracefree_null"]
        and _fraction(row["coefficient"]) != 0
    ]
    if replay_ids != scalar_flat["effective_nonzero_tracefree_term_ids"] or len(replay_ids) != 9:
        raise ValueError("scalar-flat H2 restriction drifted")

    round_s4 = stored["round_S4_crosscheck"]
    round_rows = [
        (row["term_id"], _fraction(row["coefficient"]))
        for row in round_s4["source_W_term_contributions_to_TT_eigenvalue"]
    ]
    if (
        round_s4["algebraic_U2_on_TT"] != "+24 K^2 identity"
        or [value for _, value in round_rows]
        != [18, -8, -6, 6, 36, 0, 32, 0, 0, -18, 0, 0, -36]
        or sum(value for _, value in round_rows) != 24
        or round_s4["linear_block_commutator_contribution_at_order_K2"]
        != "-16 K^2 identity"
        or round_s4["sum"] != "+24 K^2-16 K^2=+8 K^2"
    ):
        raise ValueError("round-S4 H2/commutator split drifted")

    flags = stored["claim_flags"]
    positive = sorted(name for name, enabled in flags.items() if enabled)
    if positive != sorted(
        [
            "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED",
            "GAUGE_ORDERING_COMMUTATOR_CROSSWALK_CERTIFIED",
            "GAUGE_ORDERING_DOES_NOT_CHANGE_ALGEBRAIC_H2",
            "ROUND_S4_H2_COMMUTATOR_SPLIT_CERTIFIED",
            "SCALAR_FLAT_H2_VERTEX_READY",
        ]
    ):
        raise ValueError("physical H2 claim boundary drifted")
    if stored["third_curvature_applicability"]["status"] != "H2_VERTEX_READY_MIXED_TRACE_NOT_COMPUTED":
        raise ValueError("physical H2 activation gate drifted")

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise ValueError(f"physical H2 dependency drifted: {reference['path']}")
    return stored


def main() -> int:
    verify()
    print("independent generic physical-Hessian curvature-squared replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
