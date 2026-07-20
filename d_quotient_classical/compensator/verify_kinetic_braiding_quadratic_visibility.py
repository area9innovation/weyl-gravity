#!/usr/bin/env python3
"""Independent indexed-jet replay of minimal kinetic-braiding visibility."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "compensator-kinetic-braiding-quadratic-visibility-v1.schema.json"
)
IMPORTS = {
    "quadratic_active_clock_freeze": (
        ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json",
        "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
    ),
    "background_stability": (
        ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json",
        "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        value[item["row"], item["column"]] = sp.sympify(item["coefficient"])
    return value


def _indexed_first_variations() -> tuple[sp.Expr, sp.Expr]:
    eta = sp.diag(-1, 1, 1, 1)
    nu = sp.Symbol("nu")
    n, Dphi, D2phi, lap = sp.symbols("n Dphi D2phi lap")
    Dn, divs, Dk = sp.symbols("Dn divs Dk")
    h: dict[tuple[int, int], sp.Symbol] = {}
    dh: dict[tuple[int, int, int], sp.Symbol] = {}
    phi1 = sp.symbols("phi1_0:4")
    phi2: dict[tuple[int, int], sp.Symbol] = {}
    for a in range(4):
        for b in range(a, 4):
            h[a, b] = sp.Symbol(f"h{a}{b}")
            for mu in range(4):
                dh[mu, a, b] = sp.Symbol(f"dh{mu}_{a}{b}")
            phi2[a, b] = sp.Symbol(f"p2_{a}{b}")

    def hs(a: int, b: int) -> sp.Symbol:
        return h[min(a, b), max(a, b)]

    def dhs(mu: int, a: int, b: int) -> sp.Symbol:
        return dh[mu, min(a, b), max(a, b)]

    def p2(a: int, b: int) -> sp.Symbol:
        return phi2[min(a, b), max(a, b)]

    v_cov = sp.Matrix([nu, 0, 0, 0])
    v_up = eta * v_cov
    h_up = sp.Matrix(
        4,
        4,
        lambda a, b: sum(
            eta[a, c] * eta[b, d] * hs(c, d)
            for c in range(4)
            for d in range(4)
        ),
    )
    x = -sum(
        h_up[a, b] * v_cov[a] * v_cov[b]
        for a in range(4)
        for b in range(4)
    ) + 2 * sum(v_up[a] * phi1[a] for a in range(4))

    contracted_connection = []
    for lam in range(4):
        value = 0
        for mu in range(4):
            for rho in range(4):
                if eta[mu, rho] == 0:
                    continue
                for sigma in range(4):
                    if eta[lam, sigma] == 0:
                        continue
                    value += (
                        eta[mu, rho]
                        * eta[lam, sigma]
                        * (
                            dhs(mu, rho, sigma)
                            + dhs(rho, mu, sigma)
                            - dhs(sigma, mu, rho)
                        )
                        / 2
                    )
        contracted_connection.append(sp.expand(value))
    box_phi = sum(
        eta[a, b] * p2(a, b)
        for a in range(4)
        for b in range(4)
    )
    b = sp.expand(
        box_phi
        - sum(contracted_connection[lam] * v_cov[lam] for lam in range(4))
    )

    substitutions: dict[sp.Symbol, sp.Expr] = {
        hs(0, 0): -2 * n,
        phi1[0]: Dphi,
        p2(0, 0): D2phi,
        p2(1, 1): lap,
        p2(2, 2): 0,
        p2(3, 3): 0,
        dhs(0, 0, 0): -2 * Dn,
        dhs(1, 0, 1): divs,
        dhs(2, 0, 2): 0,
        dhs(3, 0, 3): 0,
        dhs(0, 1, 1): Dk,
        dhs(0, 2, 2): 0,
        dhs(0, 3, 3): 0,
    }
    retained = {nu, n, Dphi, D2phi, lap, Dn, divs, Dk}
    for symbol in set(x.free_symbols | b.free_symbols) - retained:
        substitutions.setdefault(symbol, 0)
    x_adm = sp.factor(x.subs(substitutions))
    b_adm = sp.factor(b.subs(substitutions))
    expected_x = -2 * nu * (Dphi - nu * n)
    expected_b = -D2phi + lap + nu * Dn + nu * divs - nu * Dk / 2
    if sp.factor(x_adm - expected_x) != 0:
        raise AssertionError("INDEXED_DELTA_X_MISMATCH")
    if sp.factor(b_adm - expected_b) != 0:
        raise AssertionError("INDEXED_DELTA_BOX_MISMATCH")
    return x_adm, b_adm


def _verify_symbol(payload: dict[str, Any]) -> None:
    D, Delta, nu = sp.symbols("D Delta nu")
    expected = sp.Matrix(
        [
            [0, 2 * Delta, -D**2, 2 * D],
            [2 * Delta, 0, -nu * D, 2 * nu],
            [-D**2, nu * D, 0, 0],
            [-2 * D, 2 * nu, 0, 0],
        ]
    )
    actual = _dense(payload["stationary_Berger"]["formal_symbol"]["matrix"])
    if (actual - expected).applyfunc(sp.factor) != sp.zeros(4):
        raise AssertionError("BERGER_SYMBOL_MISMATCH")
    adjoint = {D: -D, Delta: Delta, nu: nu}
    if (expected.T.xreplace(adjoint) - expected).applyfunc(sp.factor) != sp.zeros(4):
        raise AssertionError("FORMAL_ADJOINT_MISMATCH")
    gauge = [
        sp.Matrix([nu, D, 0, -Delta]),
        sp.Matrix([0, 0, 2 * Delta, D * Delta]),
    ]
    if any(expected * vector != sp.zeros(4, 1) for vector in gauge):
        raise AssertionError("GAUGE_KERNEL_MISMATCH")
    for rows in itertools.combinations(range(4), 3):
        for columns in itertools.combinations(range(4), 3):
            if sp.factor(expected.extract(rows, columns).det()) != 0:
                raise AssertionError("RANK_UPPER_BOUND_MISMATCH")
    if (
        sp.factor(expected.extract([0, 1], [0, 1]).det()) != -4 * Delta**2
        or sp.factor(expected.extract([0, 2], [0, 2]).det()) != -D**4
    ):
        raise AssertionError("RANK_LOWER_BOUND_MISMATCH")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for name, (path, expected_hash) in IMPORTS.items():
        if _sha(path) != expected_hash:
            raise AssertionError(f"{name} import hash drifted")
        if payload["imports"][name]["sha256"] != expected_hash:
            raise AssertionError(f"{name} serialized import drifted")
    x, b = _indexed_first_variations()
    if x == 0 or b == 0:
        raise AssertionError("BERGER_INDEXED_VISIBILITY_COLLAPSED")
    _verify_symbol(payload)
    if _dense(payload["unit_cylinder"]["complete_quadratic_Hessian"]) != sp.zeros(11):
        raise AssertionError("CYLINDER_HESSIAN_NOT_ZERO")
    for field, section in (
        ("imports_sha256", "imports"),
        ("action_sha256", "minimal_braiding_action"),
        ("hessian_sha256", "covariant_complete_second_variation"),
        ("cylinder_sha256", "unit_cylinder"),
        ("Berger_sha256", "stationary_Berger"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")
    if (
        payload["terminal_verdict"]["cylinder_quadratic_visibility"]
        != "IDENTICALLY_ZERO"
        or payload["terminal_verdict"]["level_2_cylinder_repair_possible"]
        or payload["terminal_verdict"]["selected_action_exported"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1 "
        "independent indexed replay: PASS"
    )


if __name__ == "__main__":
    main()
