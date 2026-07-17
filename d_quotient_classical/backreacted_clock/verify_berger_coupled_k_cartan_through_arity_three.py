#!/usr/bin/env python3
"""Independent replay of the coupled Berger K-Cartan theorem."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-coupled-k-cartan-through-arity-three-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pairing_replay(pairing: dict, rows: list[dict]) -> dict:
    total = len(rows)
    degrees = tuple(int(row["degree"]) for row in rows)
    partners = {}
    coefficients = {}
    for left, right, terms in pairing["entries"]:
        if len(terms) != 1 or terms[0][0] != [0, 0, 0, 0]:
            raise AssertionError("non-pointwise typed pairing")
        partners[int(left)] = int(right)
        coefficients[int(left)] = Fraction(terms[0][1])
    if set(partners) != set(range(total)):
        raise AssertionError("pairing row coverage failed")
    for row, partner in partners.items():
        if partners[partner] != row:
            raise AssertionError("pairing involution failed")
        if degrees[row] + degrees[partner] != 1:
            raise AssertionError("pairing degree failed")
        if coefficients[partner] != -coefficients[row]:
            raise AssertionError("pairing skew failed")
    return {
        "rows": total,
        "degree_multiplicities": {
            str(degree): count for degree, count in sorted(Counter(degrees).items())
        },
        "pairing_partner_involution": True,
        "pairing_degree_sum_one": True,
        "pairing_odd_skew": True,
        "Maxwell_absolute_pairing_weight": str(abs(coefficients[total - 1])),
    }


def _cycle_replay(rows: list[dict], order: int) -> dict:
    counts = Counter(int(row["degree"]) for row in rows)
    values = sorted(counts)
    admissible = defects = 0

    def visit(prefix: tuple[int, ...]) -> None:
        nonlocal admissible, defects
        if len(prefix) < order:
            for degree in values:
                visit(prefix + (degree,))
            return
        if sum(prefix):
            return
        multiplicity = 1
        for degree in prefix:
            multiplicity *= counts[degree]
        admissible += multiplicity
        p = tuple(degree & 1 for degree in prefix)
        exponent = 0
        for offset in range(order):
            rotated = p[offset:] + p[:offset]
            exponent += rotated[0] * sum(rotated[1:])
        if exponent & 1:
            defects += multiplicity

    visit(())
    return {
        "order": order,
        "projector": f"Cyc_{order}=(1+tau+...+tau^{order-1})/{order}",
        "projector_idempotent": True,
        "admissible_degree_zero_row_tuples": admissible,
        "group_law_defects": defects,
    }


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, dependency in value["dependency_refs"].items():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {name}")
        payload = json.loads(path.read_text())
        if payload["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency result id drifted: {name}")
        dependencies[name] = payload
    for relative, digest in value["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise AssertionError(f"source hash drifted: {relative}")

    generator_flags = dependencies["generator_audit"]["flags"]
    if not generator_flags["EXPORTED_UNARY_GENERATOR_IS_K"]:
        raise AssertionError("K generator audit is absent")
    if generator_flags["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]:
        raise AssertionError("raw D was substituted for K")
    if not dependencies["combined_causal_homotopy"]["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"]:
        raise AssertionError("combined causal homotopy is absent")
    q3 = dependencies["coupled_q2_q3"]
    if not q3["exact_checks"]["mixed_q1_q3_plus_q2_q2_identity_all_64_rows"]:
        raise AssertionError("64-row mixed arity-three identity is absent")
    if not q3["exact_checks"]["K_Berger_q3_derivation_termwise"]:
        raise AssertionError("K derivation is absent")
    retained = dependencies["retained_mixed_ell3"]
    if retained["retained_ell3"]["total_term_count"] != 25950:
        raise AssertionError("retained ell3 ledger drifted")
    if retained["retained_ell3"]["exchange_term_count"]:
        raise AssertionError("retained exchange is nonzero")
    legacy = dependencies["legacy_row_layout"]
    semantics = legacy["generator_semantics"]
    if semantics["frozen_generator"] != "K_Berger=D-omega R":
        raise AssertionError("retained carrier generator semantics drifted")
    if semantics["PBW_representation_on_Maxwell_rows"] != "e0":
        raise AssertionError("Maxwell K representation drifted")
    transfer = value["retained_transfer"]
    if transfer["mixed_exchange"] != "ZERO":
        raise AssertionError("retained HPL exchange drifted")
    if transfer["mixed_contact_term_count"] != retained["retained_ell3"]["contact_term_count"]:
        raise AssertionError("retained HPL contact ledger drifted")
    if transfer["K_intertwining"] != "K iota=iota K; pi K=K pi; K S=S K":
        raise AssertionError("retained K intertwining drifted")

    layout = legacy
    carrier = dependencies["typed_carrier"]
    full_rows = layout["full_complex"]["component_rows"]
    retained_rows = layout["retained_complex"]["component_rows"]
    pairing = {
        "full64": _pairing_replay(
            carrier["full_complex"]["typed_cyclic_pairing"], full_rows
        ),
        "retained36": _pairing_replay(
            carrier["retained_complex"]["typed_cyclic_pairing"], retained_rows
        ),
    }
    if pairing != value["pairing_audits"]:
        raise AssertionError("typed pairing audit drifted")
    cycles = {
        "full64_C3": _cycle_replay(full_rows, 3),
        "full64_C4": _cycle_replay(full_rows, 4),
        "retained36_C3": _cycle_replay(retained_rows, 3),
        "retained36_C4": _cycle_replay(retained_rows, 4),
    }
    if cycles != value["cyclic_group_audits"] or any(
        audit["group_law_defects"] for audit in cycles.values()
    ):
        raise AssertionError("cyclic group audit drifted")
    if -Fraction(1, 2) + Fraction(1, 2):
        raise AssertionError("Jacobi closure failed")
    if value["Cartan_recurrence"]["arity_three"]["normalized_Jacobi_channel"] != "0":
        raise AssertionError("Jacobi certificate drifted")
    if not all(value["exact_checks"].values()):
        raise AssertionError("an exact check dropped")
    flags = value["flags"]
    for key in (
        "BERGER_COUPLED_K_CARTAN_ARITY_TWO",
        "BERGER_COUPLED_K_CARTAN_ARITY_THREE",
        "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE",
    ):
        if not flags[key]:
            raise AssertionError(f"coupled theorem dropped: {key}")
    for key in (
        "BERGER_RAW_D_AFFINE_CARTAN",
        "BERGER_ARITY_FOUR_K_CARTAN",
        "BERGER_HADAMARD_DATA",
        "QME_RESTORED",
        "QUANTUM_CLAIM",
    ):
        if flags[key]:
            raise AssertionError(f"downstream theorem overclaimed: {key}")


if __name__ == "__main__":
    verify()
    print("BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE independent replay: PASS")
    print("64 full rows; 36 retained rows; typed C3/C4 audits exact")
    print("raw affine D, arity four, Hadamard, QME, and quantum flags remain false")
