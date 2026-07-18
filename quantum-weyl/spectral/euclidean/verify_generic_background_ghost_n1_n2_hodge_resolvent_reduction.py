#!/usr/bin/env python3
"""Independent replay of the ghost n=1/n=2 Hodge-resolvent reduction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n1-n2-hodge-resolvent-reduction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _f(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction()) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def _tr(*factors: list[list[Fraction]]) -> Fraction:
    product = factors[0]
    for factor in factors[1:]:
        product = _mul(product, factor)
    return sum((product[i][i] for i in range(len(product))), Fraction())


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if _sha256(path) != reference["sha256"] or dependency.get("result_id") != reference["result_id"]:
            raise ValueError("n=1/n=2 dependency drifted")

    # Direct integration of the finite Endo interval:
    # int_0^inf dt int_t^(3t/2) ds exp(-lambda s)
    # = lambda^-2 (1-2/3) = 1/(3 lambda^2).
    if Fraction(1) - Fraction(2, 3) != Fraction(1, 3):
        raise ValueError("finite proper-time Fubini weight drifted")

    fixture = value["exact_fixture"]
    lam = _f(fixture["lambda"])
    ident = [[Fraction(int(i == j)) for j in range(4)] for i in range(4)]
    pl = [[Fraction() for _ in range(4)] for _ in range(4)]
    pl[3][3] = Fraction(1)
    gf = [[entry / lam for entry in row] for row in ident]
    ell = [[entry / lam for entry in row] for row in pl]
    gh0 = [[gf[i][j] - ell[i][j] / 3 for j in range(4)] for i in range(4)]
    h0 = [[Fraction() for _ in range(4)] for _ in range(4)]
    for i in range(3):
        h0[i][i] = lam
    h0[3][3] = Fraction(3, 2) * lam
    if _mul(h0, gh0) != ident:
        raise ValueError("flat Hodge inverse failed")
    w = [[_f(entry) for entry in row] for row in fixture["symmetric_noncommuting_W"]]
    if w != [list(row) for row in zip(*w, strict=True)]:
        raise ValueError("Ricci-endomorphism fixture is not self-adjoint")

    n1 = _tr(gh0, w)
    n1_reduced = _tr(gf, w) - Fraction(1, 3) * _tr(ell, w)
    n2 = -Fraction(1, 2) * _tr(gh0, w, gh0, w)
    n2_reduced = (
        -Fraction(1, 2) * _tr(gf, w, gf, w)
        + Fraction(1, 3) * _tr(gf, w, ell, w)
        - Fraction(1, 18) * _tr(ell, w, ell, w)
    )
    c3 = [Fraction(1, 3), Fraction(-1, 3), Fraction(1, 9), Fraction(-1, 81)]
    n3 = Fraction(1, 3) * _tr(gh0, w, gh0, w, gh0, w)
    n3_reduced = (
        c3[0] * _tr(gf, w, gf, w, gf, w)
        + c3[1] * _tr(gf, w, gf, w, ell, w)
        + c3[2] * _tr(gf, w, ell, w, ell, w)
        + c3[3] * _tr(ell, w, ell, w, ell, w)
    )
    if (
        n1 != n1_reduced
        or n2 != n2_reduced
        or n3 != n3_reduced
        or n1 != _f(fixture["n1_direct_and_reduced"])
        or n2 != _f(fixture["n2_direct_and_reduced"])
        or n3 != _f(fixture["n3_direct_and_reduced"])
        or c3 != [_f(item) for item in fixture["n3_cyclic_longitudinal_coefficients"]]
    ):
        raise ValueError("noncommuting Hodge trace fixture failed")

    n1_coefficients = [_f(row["coefficient"]) for row in value["log_determinant_expansion"]["n1_carriers"]]
    n2_coefficients = [_f(row["coefficient"]) for row in value["log_determinant_expansion"]["n2_carriers"]]
    if n1_coefficients != [Fraction(1), Fraction(-1, 3)] or n2_coefficients != [Fraction(-1, 2), Fraction(1, 3), Fraction(-1, 18)]:
        raise ValueError("stored Hodge carrier coefficients failed")
    if value["claim_flags"]["GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"] is not False or value["claim_flags"]["GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"] is not False:
        raise ValueError("unevaluated minimal carriers were promoted")
    return value


def main() -> int:
    verify()
    print("independent generic ghost n=1/n=2 Hodge-resolvent reduction: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
