"""Exact six-state radial Lee--Wald current evaluator.

The literal current is imported from ``BH2A_FLUX_MATRIX.json``.  It is not
retyped as an expected answer.  Radial jets are generated from the repaired
six-state flow in the ingoing-EF chart and transformed to the Schwarzschild
``t`` chart before the literal current is evaluated.  Taylor arithmetic at a
rational match radius prevents the expression swell caused by flattening the
arbitrary-r current.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ_I
from sympy.polys.fields import field

ROOT = Path(__file__).resolve().parents[3]
FLUX_CERT = ROOT / "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json"
REPAIR_CERT = (
    ROOT
    / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json"
)
I = sp.I


@lru_cache(maxsize=1)
def _load_frozen_repaired_system() -> dict:
    """Load the repaired flow and reconstruction row from its certificate."""
    repair = json.loads(REPAIR_CERT.read_text())["complete_reconstruction"]
    r, omega = sp.symbols("r omega")
    state = sp.symbols("P Pp Q Qp H1 F")
    parse_locals = {"r": r, "omega": omega, "I": I}
    flow6 = sp.Matrix([
        [sp.sympify(entry, locals=parse_locals) for entry in row]
        for row in repair["flow6"]
    ])
    h0 = sp.sympify(
        repair["H0_reconstruction"],
        locals={
            **parse_locals,
            **dict(zip(("P", "Pp", "Q", "Qp", "H1", "F"), state)),
        },
    )
    return {
        "symbols": {"r": r, "omega": omega},
        "flow6": flow6,
        "h0_row": sp.Matrix([[sp.diff(h0, variable) for variable in state]]),
    }


@lru_cache(maxsize=None)
def _radial_derivative(expr: sp.Expr, r: sp.Symbol, order: int) -> sp.Expr:
    return sp.diff(expr, r, order)


def _taylor(expr: sp.Expr, r: sp.Symbol, r0: sp.Rational, depth: int) -> list[sp.Expr]:
    return [_radial_derivative(expr, r, n).subs(r, r0) / sp.factorial(n)
            for n in range(depth + 1)]


def derive_rational_radius_current_jet(
    r0: sp.Rational = sp.Integer(4),
    current_depth: int = 1,
    omega0: sp.Rational | None = None,
) -> list[sp.Matrix]:
    """Return exact Taylor coefficients of the literal radial current.

    Coefficient ``n`` is ``J^(n)(r0)/(n!*pi*alpha_W)`` in
    ``F^r(y,bar z)=z^dagger J y``.  The coefficients are rational functions
    of the real symbol ``omega``.  ``r0`` must be rational and outside the
    horizon.
    """
    if not r0.is_Rational or r0 <= 2:
        raise ValueError("r0 must be a rational number greater than two")
    if not isinstance(current_depth, int) or current_depth < 0:
        raise ValueError("current_depth must be a nonnegative integer")
    if omega0 is not None and not omega0.is_Rational:
        raise ValueError("omega0 must be rational when supplied")

    system = _load_frozen_repaired_system()
    r = system["symbols"]["r"]
    omega_source = system["symbols"]["omega"]
    A_source = system["flow6"]
    h0_source = system["h0_row"]
    depth = 3 + current_depth

    rational_field, _omega_f = field("omega", QQ_I)
    zero, one = rational_field.zero, rational_field.one

    def convert(expr: sp.Expr):
        target = sp.Symbol("omega") if omega0 is None else omega0
        return rational_field.from_expr(sp.cancel(expr).subs(omega_source, target))

    i_f = convert(I)
    frequency_f = convert(omega_source)

    def scalar_series(expr: sp.Expr) -> list:
        return [convert(value) for value in _taylor(expr, r, r0, depth)]

    def matrix_series(matrix: sp.Matrix) -> list[list[list]]:
        entry_series = [[scalar_series(matrix[i, j])
                         for j in range(matrix.cols)]
                        for i in range(matrix.rows)]
        return [[[entry_series[i][j][n] for j in range(matrix.cols)]
                 for i in range(matrix.rows)]
                for n in range(depth + 1)]

    A_plus = matrix_series(A_source)
    A_minus = matrix_series(A_source.subs(omega_source, -omega_source))
    h_plus_entries = [scalar_series(h0_source[0, j]) for j in range(6)]
    h_minus_entries = [scalar_series(
        h0_source[0, j].subs(omega_source, -omega_source)) for j in range(6)]
    h_plus = [[h_plus_entries[j][n] for j in range(6)] for n in range(depth + 1)]
    h_minus = [[h_minus_entries[j][n] for j in range(6)] for n in range(depth + 1)]

    inv_B = scalar_series(1 / (1 - 2 / r))
    phase_plus = scalar_series(I * omega_source / (1 - 2 / r))
    phase_minus = scalar_series(-I * omega_source / (1 - 2 / r))
    e_h1 = [[zero] * 6 for _ in range(depth + 1)]
    e_h1[0][4] = one

    def scalar_times_row(scalars: list, rows: list[list]) -> list[list]:
        maximum = min(len(scalars), len(rows))
        return [[sum((scalars[k] * rows[n - k][j] for k in range(n + 1)), zero)
                 for j in range(6)] for n in range(maximum)]

    def add_rows(left: list[list], right: list[list]) -> list[list]:
        return [[left[n][j] + right[n][j] for j in range(6)]
                for n in range(min(len(left), len(right)))]

    h1_plus = add_rows(e_h1, scalar_times_row(inv_B, h_plus))
    h1_minus = add_rows(e_h1, scalar_times_row(inv_B, h_minus))

    def differentiate_row(rows: list[list], A: list[list[list]], phase: list) -> list[list]:
        result = []
        for n in range(len(rows) - 1):
            row = [(n + 1) * rows[n + 1][j] for j in range(6)]
            for k in range(n + 1):
                for j in range(6):
                    row[j] += sum((rows[k][q] * A[n - k][q][j]
                                   for q in range(6)), zero)
                    row[j] += phase[n - k] * rows[k][j]
            result.append(row)
        return result

    def jet_rows(base: dict[str, list[list]], A: list[list[list]], phase: list) -> dict:
        answer = {}
        for field_name, rows in base.items():
            current = rows
            answer[(field_name, 0)] = current
            for order in range(1, 4):
                current = differentiate_row(current, A, phase)
                answer[(field_name, order)] = current
        return answer

    plus = jet_rows({"h0": h_plus, "h1": h1_plus}, A_plus, phase_plus)
    minus = jet_rows({"h0": h_minus, "h1": h1_minus}, A_minus, phase_minus)

    payload = json.loads(FLUX_CERT.read_text())
    expression_text = payload["bilinear"]["F_r"]
    t, r_parse, mass, alpha = sp.symbols("t r m alpha")
    functions = {name: sp.Function(name)
                 for name in ("h0a", "h1a", "h0b", "h1b")}
    expression = sp.sympify(expression_text, locals={
        "t": t, "r": r_parse, "m": mass, "alpha": alpha,
        "pi": sp.pi, "Derivative": sp.Derivative, **functions,
    }) / (sp.pi * alpha)
    expression = expression.subs(mass, 1)

    base_atoms = {functions[name](t, r_parse): name for name in functions}
    atoms = list(base_atoms) + list(expression.atoms(sp.Derivative))
    encoded_symbols = {atom: sp.Symbol(f"jet_{index}")
                       for index, atom in enumerate(atoms)}
    rows_by_symbol = {}
    for atom, symbol in encoded_symbols.items():
        if isinstance(atom, sp.Derivative):
            function = atom.expr
            radial_order = sum(int(pair[1]) for pair in atom.args[1:]
                               if pair[0] == r_parse)
            time_order = sum(int(pair[1]) for pair in atom.args[1:]
                             if pair[0] == t)
        else:
            function = atom
            radial_order = time_order = 0
        name = str(function.func)
        field_name, side = name[:2], name[-1]
        if side == "a":
            rows = [[value * (i_f * frequency_f) ** time_order for value in row]
                    for row in plus[(field_name, radial_order)]]
        else:
            rows = [[value * (-i_f * frequency_f) ** time_order for value in row]
                    for row in minus[(field_name, radial_order)]]
        rows_by_symbol[symbol] = (side, rows)

    encoded = sp.expand(expression.xreplace(encoded_symbols))
    K = [[[zero] * 6 for _ in range(6)] for _ in range(current_depth + 1)]
    jet_symbols = set(rows_by_symbol)
    for term in sp.Add.make_args(encoded):
        present = list(term.free_symbols & jet_symbols)
        if len(present) != 2:
            raise RuntimeError(f"literal current term is not bilinear: {term}")
        left_symbol, right_symbol = present
        if rows_by_symbol[left_symbol][0] == "b":
            left_symbol, right_symbol = right_symbol, left_symbol
        if (rows_by_symbol[left_symbol][0], rows_by_symbol[right_symbol][0]) != ("a", "b"):
            raise RuntimeError("literal current lost its slot grading")
        coefficient = scalar_series(term / (left_symbol * right_symbol))
        left_rows = rows_by_symbol[left_symbol][1]
        right_rows = rows_by_symbol[right_symbol][1]
        for n in range(current_depth + 1):
            for a in range(n + 1):
                for b in range(n - a + 1):
                    c = n - a - b
                    for i in range(6):
                        if not left_rows[a][i]:
                            continue
                        for j in range(6):
                            if right_rows[b][j]:
                                K[n][i][j] += (
                                    coefficient[c]
                                    * left_rows[a][i]
                                    * right_rows[b][j]
                                )

    # F(y,bar z)=y^T K bar(z)=z^dagger K^T y.
    return [
        sp.Matrix(6, 6, lambda i, j: K[n][j][i].as_expr())
        for n in range(current_depth + 1)
    ]


def derive_rational_radius_current(r0: sp.Rational = sp.Integer(4)) -> sp.Matrix:
    """Return ``J(r0)/(pi*alpha_W)`` with ``z^dagger J y=F^r(y,bar z)``."""
    return derive_rational_radius_current_jet(r0, current_depth=0)[0]


def real_conjugate(expr: sp.Expr, omega: sp.Symbol) -> sp.Expr:
    """Conjugate an expression while declaring ``omega`` real."""
    return sp.conjugate(expr).subs(sp.conjugate(omega), omega)
