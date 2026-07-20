#!/usr/bin/env python3
"""Independent replay of the complete order-zero lift obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-zero-lift-obstruction-v1.schema.json"
Q1 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json"
LAYOUT = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json"
DELTA = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_arity_two_defect_v1/delta2.json"


def load(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = load(CERT)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for artifact in certificate["dependencies"].values():
        path = ROOT / artifact["path"]
        if sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {path}")

    q1 = load(Q1)["content"]
    profiles = {
        profile["index"]: {
            tuple(jet["word"]): Fraction(jet["coefficient"])
            for jet in profile["coefficient_jets"]
        }
        for profile in q1["coefficient_profiles"]
    }
    target: dict[tuple[int, int, int], Fraction] = {}
    for term in q1["terms"]:
        incoming = term["inputs"][0]
        if 34 <= term["output_row"] < 40 and 20 <= incoming["row"] < 34 and len(incoming["word"]) == 1:
            value = profiles[term["coefficient_profile"]].get((), Fraction())
            if value != Fraction(term["coefficient"]):
                raise AssertionError("q1 display coefficient disagrees with its authoritative profile")
            key = (incoming["word"][0], term["output_row"] - 34, incoming["row"] - 20)
            target[key] = target.get(key, Fraction()) + value

    layout = load(LAYOUT)
    p3 = sorted(
        [row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 3],
        key=lambda row: row["index"],
    )
    p4 = sorted(
        [row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 4],
        key=lambda row: row["index"],
    )
    p3i = {row["index"]: index for index, row in enumerate(p3)}
    p4i = {row["index"]: index for index, row in enumerate(p4)}
    axis = {"t": 0, "x": 1, "theta": 2, "phi": 3}
    current: dict[tuple[int, int, int], Fraction] = {}
    for term in layout["unary_terms"]:
        if term["source_row"] in p3i and term["target_row"] in p4i:
            key = (axis[term["derivative"]], p4i[term["target_row"]], p3i[term["source_row"]])
            current[key] = current.get(key, Fraction()) + Fraction(term["coefficient"])

    entries: dict[tuple[int, int], sp.Rational] = {}
    records = []
    for mu in range(4):
        for out in range(6):
            for incoming in range(20):
                equation = (mu * 6 + out) * 20 + incoming
                for middle in range(14):
                    value = target.get((mu, out, middle), Fraction())
                    if value:
                        entries[(equation, middle * 20 + incoming)] = sp.Rational(value.numerator, value.denominator)
                for middle in range(5):
                    value = current.get((mu, middle, incoming), Fraction())
                    if value:
                        entries[(equation, 280 + out * 5 + middle)] = -sp.Rational(value.numerator, value.denominator)
    for (equation, unknown), value in sorted(entries.items()):
        if value:
            text = str(int(value.p)) if value.q == 1 else f"{int(value.p)}/{int(value.q)}"
            records.append([equation, unknown, text])
    digest = hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()
    if digest != certificate["exact_linear_system"]["matrix_coo_sha256"]:
        raise AssertionError("matrix digest mismatch")

    matrix = sp.SparseMatrix(480, 310, entries)
    _, pivots = matrix.rref()
    if len(pivots) != 305:
        raise AssertionError(f"independent rank mismatch: {len(pivots)}")
    free = sorted(set(range(310)) - set(pivots))
    if free != [300, 301, 302, 303, 304]:
        raise AssertionError(f"unexpected free columns: {free}")
    nullspace = matrix.nullspace()
    if len(nullspace) != 5:
        raise AssertionError("independent nullity mismatch")
    if any(vector[index] for vector in nullspace for index in range(200)):
        raise AssertionError("metric A1 output survives in the kernel")

    delta = load(DELTA)["content"]["terms"]
    witness = certificate["strict_incidence_obstruction"]["normalized_metric_witness"]
    if witness not in delta:
        raise AssertionError("normalized Delta2 witness absent")
    count = sum(
        1
        for term in delta
        if 20 <= term["output_row"] < 30
        and all(5 <= item["row"] < 19 for item in term["inputs"])
        and sum(len(item["word"]) for item in term["inputs"]) == 4
    )
    if count != certificate["strict_incidence_obstruction"]["metric_order_four_delta2_terms"]:
        raise AssertionError("metric fourth-order count mismatch")

    print(json.dumps({
        "status": "PASS",
        "rank": len(pivots),
        "nullity": len(nullspace),
        "free_columns": free,
        "metric_order_four_delta2_terms": count,
        "positive_order_open": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
