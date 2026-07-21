#!/usr/bin/env python3
"""Method-distinct verifier for the Berger complex-clock anomaly theorem."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1.json"
PAYLOAD = HERE / "certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1_PAYLOAD.json"
SCHEMA = HERE / "schema/berger-complex-clock-local-anomaly-complex-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/berger-complex-clock-local-anomaly-receiver-v1.schema.json"

DEPENDENCIES = {
    "strict_restriction_obstruction": ROOT
    / "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json",
    "positive_berger_clock": ROOT
    / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "complex_clock_master_action": ROOT
    / "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
    "extended_local_bv_cohomology": HERE
    / "certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "wess_zumino_primitives": HERE
    / "certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "diff_anomaly_zero": ROOT
    / "quantum-weyl/local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
    "berger_coupled_q2": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "berger_coupled_q3": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _matrix(value: list[list[dict[str, int]]]) -> list[list[Fraction]]:
    return [[_fraction(entry) for entry in row] for row in value]


def _multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _rank(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def _independent_so4_ce_h2() -> dict[str, Any]:
    generators = list(combinations(range(4), 2))
    lookup = {pair: index for index, pair in enumerate(generators)}

    def ordered(left: int, right: int) -> tuple[tuple[int, int] | None, int]:
        if left == right:
            return None, 0
        return ((left, right), 1) if left < right else ((right, left), -1)

    def commutator(i: int, j: int) -> dict[int, int]:
        a, b = generators[i]
        c, d = generators[j]
        answer: dict[int, int] = {}
        for coefficient, left, right in (
            (int(b == c), a, d),
            (-int(a == c), b, d),
            (-int(b == d), a, c),
            (int(a == d), b, c),
        ):
            pair, sign = ordered(left, right)
            if pair is not None and coefficient:
                target = lookup[pair]
                answer[target] = answer.get(target, 0) + coefficient * sign
        return {target: coefficient for target, coefficient in answer.items() if coefficient}

    pairs = list(combinations(range(6), 2))
    triples = list(combinations(range(6), 3))
    pair_lookup = {pair: index for index, pair in enumerate(pairs)}
    first = [[Fraction() for _ in range(6)] for _ in pairs]
    for row, (x, y) in enumerate(pairs):
        for target, coefficient in commutator(x, y).items():
            first[row][target] = -coefficient
    second = [[Fraction() for _ in pairs] for _ in triples]
    for row, (x, y, z) in enumerate(triples):
        for sign, bracket, tail in (
            (-1, commutator(x, y), z),
            (1, commutator(x, z), y),
            (-1, commutator(y, z), x),
        ):
            for target, coefficient in bracket.items():
                pair, wedge_sign = ordered(target, tail)
                if pair is not None:
                    second[row][pair_lookup[pair]] += sign * coefficient * wedge_sign
    render = lambda matrix: [
        [["%d" % entry.numerator, "%d" % entry.denominator] for entry in row]
        for row in matrix
    ]
    return {
        "d1_rank": _rank(first),
        "d2_rank": _rank(second),
        "H2_dimension": len(pairs) - _rank(first) - _rank(second),
        # Convert the independent tuple representation back to the producer's
        # rational-object encoding only at the digest boundary.
        "d1_matrix_sha256": _digest(
            [[{"numerator": int(n), "denominator": int(d)} for n, d in row] for row in render(first)]
        ),
        "d2_matrix_sha256": _digest(
            [[{"numerator": int(n), "denominator": int(d)} for n, d in row] for row in render(second)]
        ),
    }


def verify_values(result: dict[str, Any], payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(result)
    Draft202012Validator(payload_schema).validate(payload)

    if result["receiver_payload_sha256"] != _digest(payload):
        raise ValueError("receiver payload content hash failed")
    if set(result["dependencies"]) != set(DEPENDENCIES):
        raise ValueError("dependency set is not exact")
    for name, path in DEPENDENCIES.items():
        reference = result["dependencies"][name]
        if reference["sha256"] != _sha256(path) or reference["path"] != str(path.relative_to(ROOT)):
            raise ValueError(f"dependency hash/path drifted: {name}")

    obstruction = json.loads(DEPENDENCIES["strict_restriction_obstruction"].read_text())
    row = next(entry for entry in obstruction["sector_dispositions"] if entry["sector_id"] == "Berger_fixed_coupling")
    source_constant = Fraction(row["exact_witness"]["source_metric_antifield_constant_alphaB_B00"])
    target_constant = Fraction(row["exact_witness"]["target_coupled_metric_antifield_constant"])
    separator = result["strict_to_coupled_action_morphism"]["separator"]
    if (
        _fraction(separator["epsilon_0_j_Q_source_gstar00"]) != source_constant
        or _fraction(separator["epsilon_0_Q_target"]) != target_constant
        or _fraction(separator["separation"]) != source_constant - target_constant
        or source_constant - target_constant != Fraction(961, 1920)
    ):
        raise ValueError("constant-term action-morphism witness failed")

    background = json.loads(DEPENDENCIES["positive_berger_clock"].read_text())
    master = json.loads(DEPENDENCIES["complex_clock_master_action"].read_text())
    if (
        background["rational_fixture"]["rho_squared"] != "1"
        or background["rational_fixture"]["scalar_equation"] != "PASS"
        or background["rational_fixture"]["three_independent_metric_equations"] != "PASS"
        or master["exact_checks"]["classical_master_equation"] is not True
        or master["exact_checks"]["Q_squared_zero"] is not True
        or master["transformations"]["BRST_fields"]["Q rho"] != "L_xi rho-omega rho"
        or master["transformations"]["BRST_fields"]["Q theta"] != "L_xi theta"
    ):
        raise ValueError("action-derived classical input is not the declared complex-clock theory")
    q2 = json.loads(DEPENDENCIES["berger_coupled_q2"].read_text())
    q3 = json.loads(DEPENDENCIES["berger_coupled_q3"].read_text())
    if (
        q2["flags"]["BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"] is not True
        or q2["flags"]["BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"] is not False
        or q3["flags"]["BERGER_MIXED_Q3_K_EQUIVARIANT"] is not True
    ):
        raise ValueError("raw-D/K_Berger separation failed")

    q = _matrix(result["quartet_reduction"]["Q_W"])
    h = _matrix(result["quartet_reduction"]["h_W"])
    q2 = _multiply(q, q)
    anticommutator = [
        [left + right for left, right in zip(row_left, row_right)]
        for row_left, row_right in zip(_multiply(q, h), _multiply(h, q))
    ]
    identity = [[Fraction(int(i == j)) for j in range(4)] for i in range(4)]
    if q2 != [[Fraction() for _ in range(4)] for _ in range(4)] or anticommutator != identity:
        raise ValueError("quartet identity failed independently")
    if q[1][0] != 1 or q[3][2] != 1:
        raise ValueError("quartet row orientation drifted")

    boundary = _matrix(result["H14"]["standard_candidate_boundary_matrix"])
    if _rank(boundary) != 4 or result["H14"]["standard_candidate_boundary_rank"] != 4:
        raise ValueError("standard candidate boundary is not surjective")
    if any(
        result["H14"][key] != 0
        for key in (
            "even_quotient_dimension",
            "odd_quotient_dimension",
            "pure_Diff_quotient_dimension",
            "Weyl_and_mixed_quotient_dimension",
            "positive_antifield_quotient_dimension",
        )
    ):
        raise ValueError("zero quotient dimensions failed")
    if [row["status"] for row in result["candidate_completeness"]["ledger"]] != [
        "EXACT",
        "EXACT",
        "EXACT",
        "ZERO",
        "ZERO",
    ]:
        raise ValueError("candidate partition has an unresolved or promoted sector")
    ce_stored = result["candidate_completeness"]["positive_antifield_characteristic_current"]["CE_control"]
    ce_replay = _independent_so4_ce_h2()
    if any(ce_stored[key] != ce_replay[key] for key in ce_replay):
        raise ValueError("global-current CE H2 elimination failed independently")
    if ce_replay["H2_dimension"] != 0:
        raise ValueError("phase current acquired a ghost-number-two lift")
    if result["H14"]["matter_family"]["status"] != "EXACT_FAMILY":
        raise ValueError("matter invariant family lost its quartet primitive")
    if result["symmetry_disposition"]["K_Berger"] != (
        "RIGID_BACKGROUND_SYMMETRY_NOT_A_LOCAL_GAUGE_GHOST; "
        "Q1_Q2_Q3_EQUIVARIANCE IS A SEPARATE CARTAN INPUT"
    ):
        raise ValueError("K_Berger was promoted into the local gauge complex")
    if (
        result["coefficient_and_qme_status"]["coefficient_status"]
        != "NOT_COMPUTED_FOR_GRAVITY_CLOCK_THEORY"
        or result["coefficient_and_qme_status"]["QME_status"]
        != "NOT_RESTORED_FOR_GRAVITY_CLOCK_THEORY"
        or payload["coefficient_status"] != "NOT_COMPUTED_FOR_GRAVITY_CLOCK_THEORY"
        or payload["QME_status"] != "NOT_RESTORED_FOR_GRAVITY_CLOCK_THEORY"
    ):
        raise ValueError("coefficient or QME lifecycle was over-promoted")

    proof_core = {
        "quartet_Q": result["quartet_reduction"]["Q_W"],
        "quartet_h": result["quartet_reduction"]["h_W"],
        "quartet_anticommutator": result["quartet_reduction"]["Qh_plus_hQ"],
        "strict_candidate_boundary": result["H14"]["standard_candidate_boundary_matrix"],
        "candidate_ledger": result["candidate_completeness"]["ledger"],
        "phase_current_CE_H2": ce_stored,
        "constant_separator": separator,
    }
    if (
        result["proof_hashes"]["quartet_and_candidate_partition_sha256"] != _digest(proof_core)
        or result["proof_hashes"]["candidate_ledger_sha256"]
        != _digest(result["candidate_completeness"]["ledger"])
        or result["proof_hashes"]["action_morphism_separator_sha256"] != _digest(separator)
    ):
        raise ValueError("proof digest failed")

    if payload["strict_action_complex_map"] != result["strict_to_coupled_action_morphism"]["verdict"]:
        raise ValueError("receiver action-map verdict drifted")
    if payload["matter_coupled_H14"]["status"] != result["H14"]["status"]:
        raise ValueError("receiver H14 verdict drifted")


def verify() -> dict[str, Any]:
    result = json.loads(OUTPUT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    verify_values(result, payload)
    return result


if __name__ == "__main__":
    verify()
    print("Berger complex-clock local anomaly independent verification: PASS")
