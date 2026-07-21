#!/usr/bin/env python3
"""Independent exact replay of the two-phase counterflow preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _matrix(rows: list[list[str]], symbols: dict[str, sp.Symbol] | None = None) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals=symbols or {}) for value in row] for row in rows])


def _check_imports(result: dict[str, object]) -> None:
    for row in result["imports"].values():
        path = ROOT / row["path"]
        imported = json.loads(path.read_text())
        if _sha(path) != row["sha256"] or row["actual_sha256"] != row["sha256"]:
            raise AssertionError("import byte hash failed")
        if imported["result_id"] != row["result_id"] or row["oracle_fields_consumed"] != []:
            raise AssertionError("import identity/oracle boundary failed")


def _check_phase_square(payload: dict[str, object]) -> None:
    f1, f2, x1, x2, gauge = sp.symbols("f1 f2 x1 x2 gauge", nonzero=True)
    total = f1 + f2
    chi = (f1 * x1 + f2 * x2) / total
    psi = x1 - x2
    mu = f1 * f2 / total
    difference = f1 * (x1 - gauge) ** 2 + f2 * (x2 - gauge) ** 2
    difference -= total * (chi - gauge) ** 2 + mu * psi**2
    if sp.factor(difference) != 0:
        raise AssertionError("independent square completion failed")
    phase = payload["phase_decomposition"]
    if not phase["no_Maxwell_term"] or phase["diagonal_charge"] != "Q_diag=F*(dot_chi-A0)=0":
        raise AssertionError("phase/Gauss ledger failed")


def _check_stationarity(payload: dict[str, object]) -> None:
    alpha_b, alpha_r, m2, v0, c = sp.symbols("alpha_B alpha_R M2 V0 C")
    r = sp.Rational(151, 80)
    beta = sp.Rational(961, 9600) * alpha_b
    equations = [
        sp.Rational(9, 80) * alpha_b - c,
        v0 - c + beta + alpha_r * r**2,
        m2 - (3 * c - 4 * beta) / r + 4 * alpha_r * r,
    ]
    matrix = sp.linear_eq_to_matrix(equations, [alpha_b, alpha_r, m2, v0, c])[0]
    serialized = payload["stationary_loci"]["berger"]
    local = {str(x): x for x in (alpha_b, alpha_r, m2, v0, c)}
    if _matrix(serialized["stationarity_matrix"], local) != matrix:
        raise AssertionError("Berger stationarity matrix failed")
    rref, pivots = matrix.rref()
    if _matrix(serialized["rref"], local) != rref or serialized["pivot_columns"] != list(pivots):
        raise AssertionError("Berger stationarity RREF failed")
    solution = sp.solve(equations, [alpha_b, alpha_r, m2], dict=True)[0]
    expected = {
        alpha_b: sp.Rational(80, 9) * c,
        alpha_r: sp.Rational(19040, 615627) * c - sp.Rational(6400, 22801) * v0,
        m2: -sp.Rational(80, 151) * c + sp.Rational(320, 151) * v0,
    }
    if solution != expected:
        raise AssertionError("Berger locus solve failed")
    cylinder = payload["stationary_loci"]["cylinder"]["locus"]
    if sp.sympify(cylinder["M_P_squared"]) != c / 2 - 24 * alpha_r:
        raise AssertionError("cylinder M2 locus failed")
    if sp.sympify(cylinder["V0"]) != c - 36 * alpha_r:
        raise AssertionError("cylinder V0 locus failed")


def _check_action_hessian(payload: dict[str, object]) -> None:
    e = sp.symbols("e")
    u, n, z, p = sp.symbols("u n z p")
    du, dz, dp, dc, gauge = sp.symbols("du dz dp dc gauge")
    beta, c, r, omega, alpha_r, f = sp.symbols("beta C R Omega alpha_R F", nonzero=True)
    phi0 = (sp.Rational(3, 2) * c - 2 * beta) / r
    m2 = 2 * phi0 - 4 * alpha_r * r
    v0 = c - beta - alpha_r * r**2
    scale = sp.exp(e * u / 2)
    lapse = sp.exp(e * n)
    phi = phi0 + e * z
    adot = scale * e * du / 2
    phidot = e * dz
    potential = (phi - m2 / 2) ** 2 / (4 * alpha_r) + v0
    density = beta * lapse / scale
    density += -6 * scale * phi * adot**2 / lapse - 6 * scale**2 * adot * phidot / lapse
    density += lapse * scale * r * phi - lapse * scale**3 * potential
    density += scale**3 * (c * (1 + e * dp / omega) ** 2 + f * e**2 * (dc - gauge) ** 2) / (2 * lapse)
    quadratic = sp.expand(sp.diff(density, e, 2).subs(e, 0) / 2)
    expected = f * (gauge - dc) ** 2 / 2 + c * dp**2 / (2 * omega**2) + c * n**2 / 2
    expected += 3 * (beta - sp.Rational(3, 4) * c) * du**2 / r - 3 * du * dz
    expected += (beta - sp.Rational(3, 8) * c) * u**2
    expected += n * (-c * dp / omega - sp.Rational(3, 2) * c * u)
    expected += u * (sp.Rational(3, 2) * c * dp / omega - r * z) - z**2 / (4 * alpha_r)
    if sp.factor(quadratic - expected) != 0:
        raise AssertionError("action-derived raw Hessian failed")

    reduced = sp.factor(expected.subs(gauge, dc).subs(n, dp / omega + sp.Rational(3, 2) * u))
    wanted = 3 * (beta - sp.Rational(3, 4) * c) * du**2 / r - 3 * du * dz
    wanted += (beta - sp.Rational(3, 2) * c) * u**2 - r * u * z - z**2 / (4 * alpha_r)
    if sp.factor(reduced - wanted) != 0:
        raise AssertionError("Dirac/Gauss reduction failed")
    v = sp.hessian(wanted, (du, dz))
    if v.det() != -9 or not (v.det() < 0):
        raise AssertionError("split velocity inertia failed")
    serialized = payload["quadratic_hessian_and_constraints"]
    local = {str(x): x for x in (beta, c, r, omega, alpha_r, f)}
    if any(sp.simplify(x) != 0 for x in (_matrix(serialized["reduced_velocity_hessian"], local) - v)):
        raise AssertionError("serialized reduced Hessian failed")


def _check_selected(payload: dict[str, object]) -> None:
    fixture = payload["selected_fixture"]
    p = fixture["parameters"]
    exact = {key: sp.Rational(value) for key, value in p.items() if key not in {"alpha_R"}}
    if sp.Rational(p["alpha_R"]) != 0 or fixture["Maxwell_term"] != "ABSENT":
        raise AssertionError("selected action branch failed")
    if exact["f1_squared"] != 2 or exact["f2_squared"] != 2:
        raise AssertionError("phase normalization failed")
    if exact["mu_squared"] != exact["f1_squared"] * exact["f2_squared"] / exact["F"]:
        raise AssertionError("relative inertia failed")
    if exact["C"] != exact["mu_squared"] * exact["Omega"] ** 2:
        raise AssertionError("clock energy failed")
    if exact["beta"] != sp.Rational(961, 9600) * exact["alpha_B"]:
        raise AssertionError("Berger Bach density failed")
    a = 3 * (exact["beta"] - sp.Rational(3, 4) * exact["C"]) / exact["R"]
    b = exact["beta"] - sp.Rational(3, 2) * exact["C"]
    if (a, b, -b / a) != (sp.Rational(1, 8), -sp.Rational(659, 1920), sp.Rational(659, 240)):
        raise AssertionError("selected scalar reduction failed")
    if not fixture["Hamiltonian_positive"] or fixture["split_scalar_pair"]:
        raise AssertionError("selected health disposition failed")


def _check_characteristics(payload: dict[str, object]) -> None:
    b, t, y = sp.symbols("b t y", real=True)
    # Independently reconstruct the characteristic polynomial of the
    # dimensionless (u,z) Euler-Lagrange pencil.
    polynomial = 36 * t * y**2 - 3 * (4 * b + 8 * t - 3) * y + 4 * b + 4 * t - 6
    roots = sp.solve(polynomial, y)
    declared = [
        (4 * b + 8 * t - 3 - sp.sqrt((4 * b - 3) ** 2 + 48 * t)) / (24 * t),
        (4 * b + 8 * t - 3 + sp.sqrt((4 * b - 3) ** 2 + 48 * t)) / (24 * t),
    ]
    if not all(any(sp.simplify(left - right) == 0 for right in roots) for left in declared):
        raise AssertionError("general characteristic roots failed")
    disc = sp.discriminant(polynomial, y)
    if len(sp.solve(disc, t)) != 1 or sp.simplify(sp.solve(disc, t)[0] + (4 * b - 3) ** 2 / 48) != 0:
        raise AssertionError("repeated-root threshold failed")
    if len(sp.solve(polynomial.subs(y, 0), t)) != 1 or sp.simplify(sp.solve(polynomial.subs(y, 0), t)[0] - (sp.Rational(3, 2) - b)) != 0:
        raise AssertionError("zero-root threshold failed")
    ledger = payload["characteristic_and_Jordan_ledger"]
    if ledger["cylinder_alpha_R_zero"]["characteristic_roots"] != ["-2", "2"]:
        raise AssertionError("cylinder roots failed")


def _check_charge_boundary(result: dict[str, object]) -> None:
    rows = {row["generator"]: row for row in result["charge_ledger"]}
    if rows["D"]["unrestricted"] != "CHARGED_GLOBAL":
        raise AssertionError("unrestricted D charge erased")
    if rows["U1_diag"]["unrestricted"] != "GAUGE_BY_GAUSS":
        raise AssertionError("diagonal Gauss disposition failed")
    if rows["K=D-Omega*R_rel"]["unrestricted"] != "GAUGE_AND_BACKGROUND_STABILIZER":
        raise AssertionError("K stabilizer failed")
    forbidden = ("FULL_BV_CAUSAL_PARENT", "GREEN_HYPERBOLICITY", "HADAMARD_OR_QUANTUM", "UNRESTRICTED_D_GAUGE", "MAXWELL_TERM")
    if any(result["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary promoted")


def verify() -> None:
    result = json.loads(RESULT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if _sha(PAYLOAD) != result["payload_ref"]["sha256"]:
        raise AssertionError("payload byte hash failed")
    if _digest({k: v for k, v in payload.items() if k != "content_sha256"}) != payload["content_sha256"]:
        raise AssertionError("payload canonical hash failed")
    expected_hashes = {
        "selected_fixture_sha256": _digest(result["selected_fixture"]),
        "charge_ledger_sha256": _digest(result["charge_ledger"]),
        "terminal_sha256": _digest(result["terminal_verdict"]),
        "claim_boundary_sha256": _digest(result["claim_boundary"]),
    }
    if result["content_hashes"] != expected_hashes:
        raise AssertionError("certificate content hashes failed")
    _check_imports(result)
    _check_phase_square(payload)
    _check_stationarity(payload)
    _check_action_hessian(payload)
    _check_characteristics(payload)
    _check_selected(payload)
    _check_charge_boundary(result)
    print("TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1 independent replay: PASS")


if __name__ == "__main__":
    verify()
