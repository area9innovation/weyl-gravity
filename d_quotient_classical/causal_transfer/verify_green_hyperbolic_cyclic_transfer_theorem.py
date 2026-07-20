#!/usr/bin/env python3
"""Independent replay of the sharp cyclic Green-homotopy transfer theorem."""

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
    "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "green-hyperbolic-cyclic-transfer-theorem-v1.schema.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sharp(a: sp.Matrix, j_domain: sp.Matrix, j_codomain: sp.Matrix) -> sp.Matrix:
    return j_domain.inv() * a.T * j_codomain


def _rank(a: sp.Matrix) -> int:
    return int(a.rank())


def _zero(a: sp.Matrix) -> bool:
    return all(sp.simplify(item) == 0 for item in a)


def _nonzero(a: sp.Matrix) -> list[dict[str, int]]:
    return [
        {"row": i, "column": j, "coefficient": int(item)}
        for i in range(a.rows)
        for j in range(a.cols)
        if (item := sp.simplify(a[i, j])) != 0
    ]


def verify(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise AssertionError(
            "schema failure: "
            + "; ".join(error.message for error in errors[:8])
        )
    for reference in value["dependency_refs"].values():
        path = ROOT / reference["path"]
        if _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
    for source in value["source_manifest"].values():
        path = ROOT / source["path"]
        if _sha(path) != source["sha256"]:
            raise AssertionError(f"source hash mismatch: {path}")

    # Independent positive fixture.
    q_e = sp.zeros(4)
    q_e[1, 0] = 1
    q_e[3, 2] = 1
    h_e = sp.zeros(4)
    h_e[0, 1] = 1
    h_e[2, 3] = 1
    k = sp.zeros(4)
    k[0, 2] = 1
    k[1, 3] = -1
    lambda_e_plus = h_e + k
    lambda_e_minus = h_e - k
    j_e = sp.zeros(4)
    j_e[0, 3] = 1
    j_e[3, 0] = -1
    j_e[1, 2] = -1
    j_e[2, 1] = 1
    sigma_e = sp.diag(1, -1, 1, -1)

    q_a = sp.Matrix([[0, 0], [1, 0]])
    h_a = sp.Matrix([[0, 1], [0, 0]])
    j_a = sp.Matrix([[0, 1], [-1, 0]])
    sigma_a = sp.diag(1, -1)
    q_c = sp.diag(q_e, q_a)
    j_c = sp.diag(j_e, j_a)
    sigma_c = sp.diag(sigma_e, sigma_a)
    inclusion = sp.zeros(6, 4)
    inclusion[:4, :4] = sp.eye(4)
    projection = sp.zeros(4, 6)
    projection[:4, :4] = sp.eye(4)
    homotopy = sp.zeros(6)
    homotopy[4:, 4:] = h_a
    plus = homotopy + inclusion * lambda_e_plus * projection
    minus = homotopy + inclusion * lambda_e_minus * projection
    delta_e = lambda_e_plus - lambda_e_minus
    delta_c = plus - minus

    positive = [
        q_c * inclusion - inclusion * q_e,
        projection * q_c - q_e * projection,
        projection * inclusion - sp.eye(4),
        q_c * homotopy
        + homotopy * q_c
        - (sp.eye(6) - inclusion * projection),
        q_c * plus + plus * q_c - sp.eye(6),
        q_c * minus + minus * q_c - sp.eye(6),
        delta_c - inclusion * delta_e * projection,
        _sharp(inclusion, j_e, j_c) - projection,
        _sharp(plus, j_c, j_c) - sigma_c * minus * sigma_c,
        j_c * delta_c - projection.T * j_e * delta_e * projection,
    ]
    if not all(_zero(item) for item in positive):
        raise AssertionError("independent positive fixture failed")
    if _rank(delta_e) != value["toy_fixture"]["causal_difference_rank"]:
        raise AssertionError("toy causal-difference rank drifted")

    # Independent failure fixtures.
    d = sp.Matrix([[0, 0], [1, 0]])
    h = sp.Matrix([[0, 1], [0, 0]])
    identity2 = sp.eye(2)
    expected: dict[str, tuple[int, list[dict[str, int]] | None]] = {}
    expected["CHAIN_MAPS_ARE_ESSENTIAL"] = (
        _rank(-identity2),
        _nonzero(-identity2),
    )
    expected["DEFORMATION_IDENTITY_IS_ESSENTIAL"] = (
        _rank(d * (2 * h) + (2 * h) * d - identity2),
        _nonzero(d * (2 * h) + (2 * h) * d - identity2),
    )
    expected["RETRACTION_IS_ESSENTIAL_FOR_DESCENT"] = (
        _rank(-identity2),
        _nonzero(-identity2),
    )

    q_two = sp.diag(d, d)
    lambda_two = sp.diag(h, h)
    n = sp.zeros(4)
    n[2, 0] = 1
    u = sp.eye(4) + n
    ui = sp.eye(4) - n
    q_nonlocal = u * q_two * ui
    lambda_nonlocal = u * lambda_two * ui
    if not _zero(
        q_nonlocal * lambda_nonlocal
        + lambda_nonlocal * q_nonlocal
        - sp.eye(4)
    ):
        raise AssertionError("support control lost its algebraic control")
    cross = [
        item
        for item in _nonzero(lambda_nonlocal)
        if item["row"] // 2 != item["column"] // 2
    ]
    expected["SUPPORT_LOCALITY_IS_ESSENTIAL"] = (0, cross)

    j_bad = sp.diag(2 * j_e, j_a)
    pairing_defect = (
        j_bad * delta_c - projection.T * j_e * delta_e * projection
    )
    expected["PAIRING_ADJOINTNESS_IS_ESSENTIAL"] = (
        _rank(pairing_defect),
        _nonzero(pairing_defect),
    )
    endpoint_bad = (
        _sharp(h_e, j_e, j_e)
        - sigma_e * (h_e + k) * sigma_e
    )
    expected["ENDPOINT_ADJOINT_REVERSAL_IS_ESSENTIAL"] = (
        _rank(endpoint_bad),
        _nonzero(endpoint_bad),
    )

    u_sign = sp.eye(4)
    u_sign[1:3, 1:3] = sp.Matrix([[1, 1], [0, 1]])
    ui_sign = u_sign.inv()
    if not _zero(_sharp(u_sign, j_e, j_e) - ui_sign):
        raise AssertionError("sign counterexample shear is not cyclic")
    q_sign = u_sign * q_e * ui_sign
    plus_sign = u_sign * lambda_e_plus * ui_sign
    minus_sign = u_sign * lambda_e_minus * ui_sign
    if not _zero(q_sign * plus_sign + plus_sign * q_sign - sp.eye(4)):
        raise AssertionError("sign counterexample lost its chain identity")
    sign_defect = (
        _sharp(plus_sign, j_e, j_e)
        - sigma_e * minus_sign * sigma_e
    )
    expected["SIGN_INTERTWINING_IS_ESSENTIAL_FOR_FIXED_SIGMA"] = (
        _rank(sign_defect),
        _nonzero(sign_defect),
    )

    rows = {
        row["counterexample_id"]: row
        for row in value["necessity_counterexamples"]
    }
    if set(rows) != set(expected):
        raise AssertionError("counterexample ledger changed")
    for name, (rank, entries) in expected.items():
        row = rows[name]
        if row["defect"]["rank"] != rank:
            raise AssertionError(f"counterexample rank drifted: {name}")
        if entries is not None and row["defect"]["nonzero_entries"] != entries:
            raise AssertionError(f"counterexample entries drifted: {name}")

    # Independent read-only consumer checks.
    refs = value["dependency_refs"]
    cylinder_green = json.loads(
        (ROOT / refs["cylinder_green_homotopy"]["path"]).read_text()
    )
    cylinder_quasi = json.loads(
        (
            ROOT / refs["cylinder_causal_quasi_isomorphism"]["path"]
        ).read_text()
    )
    cylinder_pairing = json.loads(
        (ROOT / refs["cylinder_pairing"]["path"]).read_text()
    )
    nariai = json.loads(
        (ROOT / refs["nariai_curved_consumer"]["path"]).read_text()
    )
    if (
        cylinder_green["dimension_ledger"]["identity"] != "386=356+30"
        or cylinder_quasi["terminal_gate"]["status"] is not True
        or cylinder_pairing["Green_pairing_equals_current_pairing"]
        is not True
        or nariai["carrier"]["total_rank"] != 310
        or nariai["flags"]["NARIAI_REPAIRED_310_ADJOINT_REVERSAL"]
        is not True
    ):
        raise AssertionError("consumer replay drifted")
    if not all(value["exact_checks"].values()):
        raise AssertionError("certificate exact check dropped")
    if value["background_scope"]["cross_background_identification"] is not False:
        raise AssertionError("cross-background mode identification promoted")
    print(
        "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1 "
        "independent verification: PASS"
    )


def main() -> None:
    verify(json.loads(CERTIFICATE.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
