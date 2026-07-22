"""Formal generic-Lambda sourced polar metric-lift classification."""

from __future__ import annotations

import sympy as sp
from sympy.polys.domains import QQ_I
from sympy.polys.matrices import DomainMatrix


def _cancel(expression: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(expression))


def _domain_rref_solve(matrix: sp.Matrix, rhs: sp.Matrix) -> sp.Matrix | None:
    """Solve a symbolic linear system once over its exact fraction field.

    Free variables are fixed to zero.  ``None`` denotes inconsistency.  This
    avoids the separate symbolic rank and Gauss--Jordan passes that trigger
    multivariate polynomial-GCD blowups in the sourced-jet staircase.
    """
    symbols = sorted(matrix.free_symbols | rhs.free_symbols, key=lambda item: item.name)
    domain = QQ_I.frac_field(*symbols)
    left = DomainMatrix.from_Matrix(matrix).convert_to(domain)
    right = DomainMatrix.from_Matrix(rhs).convert_to(domain)
    reduced_domain, pivots = left.hstack(right).rref(method="GJ")
    reduced = reduced_domain.to_Matrix()
    columns = matrix.cols
    for row in range(matrix.rows):
        if all(reduced[row, column] == 0 for column in range(columns)) and reduced[row, columns] != 0:
            return None
    solution = sp.zeros(columns, rhs.cols)
    for row, pivot in enumerate(pivots):
        if pivot < columns:
            solution[pivot, 0] = reduced[row, columns]
    return solution


def _inverse_series(expression: sp.Expr, r: sp.Symbol, depth: int) -> dict[int, sp.Expr]:
    expression = _cancel(expression)
    if expression == 0:
        return {}
    numerator, denominator = sp.fraction(expression)
    pnum, pden = sp.Poly(sp.expand(numerator), r), sp.Poly(sp.expand(denominator), r)
    nmax = max(monomial[0] for monomial in pnum.monoms())
    dmax = max(monomial[0] for monomial in pden.monoms())
    den_coefficients = [pden.coeff_monomial(r ** (dmax - k)) if dmax - k >= 0 else 0 for k in range(depth + 1)]
    inverse = [1 / den_coefficients[0]]
    for k in range(1, depth + 1):
        inverse.append(_cancel(-sum(den_coefficients[j] * inverse[k - j] for j in range(1, k + 1)) / den_coefficients[0]))
    num_coefficients = [pnum.coeff_monomial(r ** (nmax - k)) if nmax - k >= 0 else 0 for k in range(depth + 1)]
    return {
        k - (nmax - dmax): sp.expand(sum(num_coefficients[j] * inverse[k - j] for j in range(k + 1)))
        for k in range(depth + 1)
    }


def _column_jets(coefficients: list[sp.Matrix], rate: sp.Expr, sigma: sp.Expr, depth: int) -> list[list[list[sp.Expr]]]:
    dimension = coefficients[0].rows
    leading = coefficients[0] - rate * sp.eye(dimension)
    augmented = leading.row_join(sp.eye(dimension)).rref()[0]
    reduced, eliminator = augmented[:, :dimension], augmented[:, dimension:]
    zero_rows = [i for i in range(dimension) if all(reduced[i, j] == 0 for j in range(dimension))]
    pivots = []
    for i in range(dimension):
        if i not in zero_rows:
            pivots.append((i, next(j for j in range(dimension) if reduced[i, j] != 0)))
    kernel = leading.nullspace()
    kernel_matrix = sp.Matrix.hstack(*kernel)

    def particular(rhs: sp.Matrix) -> sp.Matrix:
        transformed = eliminator * rhs
        result = sp.zeros(dimension, rhs.cols)
        for i, j in pivots:
            result[j, :] = transformed[i, :]
        return result

    jets = [kernel_matrix]
    width = kernel_matrix.cols
    for n in range(depth):
        rhs = (sigma - n) * jets[n]
        for k in range(1, n + 2):
            j = n + 1 - k
            if j < len(jets):
                rhs -= coefficients[k] * jets[j]
        rhs = rhs.applyfunc(_cancel)
        conditions = (eliminator * rhs).applyfunc(_cancel)
        nonzero = [conditions[i, :] for i in zero_rows if any(conditions[i, c] != 0 for c in range(conditions.cols))]
        if nonzero:
            condition_matrix = sp.Matrix.vstack(*nonzero)
            nullspace = condition_matrix.nullspace()
            transform = sp.Matrix.hstack(*nullspace) if nullspace else sp.zeros(condition_matrix.cols, 0)
            jets = [(jet * transform).applyfunc(_cancel) for jet in jets]
            rhs = (rhs * transform).applyfunc(_cancel)
        jets.append(particular(rhs).applyfunc(_cancel).row_join(kernel_matrix))
        width = jets[-1].cols
        jets = [jet.row_join(sp.zeros(dimension, width - jet.cols)) for jet in jets]
    solutions = []
    for column in range(width):
        solution = [[_cancel(jets[n][i, column]) for i in range(dimension)] for n in range(depth + 1)]
        first = next((n for n, vector in enumerate(solution) if any(value != 0 for value in vector)), None)
        if first == 0:
            solutions.append(solution)
    return solutions


def _simple_jet(coefficients: list[sp.Matrix], rate: sp.Expr, sigma: sp.Expr, leading_vector: sp.Matrix, depth: int) -> list[list[sp.Expr]]:
    """Solve one simple projected carrier branch with its leading vector fixed."""
    dimension = coefficients[0].rows
    shifted = coefficients[0] - rate * sp.eye(dimension)
    unknowns = [sp.Symbol(f"u_{n}_{i}") for n in range(1, depth + 1) for i in range(dimension)]

    def vector(n: int) -> sp.Matrix:
        if n == 0:
            return leading_vector
        offset = dimension * (n - 1)
        return sp.Matrix(dimension, 1, unknowns[offset:offset + dimension])

    equations = []
    for n in range(depth):
        residual = (sigma - n) * vector(n) - shifted * vector(n + 1)
        for k in range(1, n + 2):
            residual -= coefficients[k] * vector(n + 1 - k)
        equations.extend(sp.expand(value) for value in residual)
    matrix, rhs = sp.linear_eq_to_matrix(equations, unknowns)
    solution = _domain_rref_solve(matrix, rhs)
    if solution is None:
        raise RuntimeError("simple carrier jet is inconsistent")
    jets = [[_cancel(value) for value in leading_vector]]
    for n in range(1, depth + 1):
        jets.append([_cancel(solution[dimension * (n - 1) + i]) for i in range(dimension)])
    return jets


def _derive_sourced_lift_selected(
    reconstruction: dict,
    carrier: dict,
    depth: int,
    selections: set[tuple[str, int]],
) -> dict:
    r = sp.Symbol("r", positive=True)
    mass = sp.Symbol("m", positive=True)
    lam = sp.Symbol("Lambda")
    omega = sp.Symbol("omega", real=True, nonzero=True)
    functions = {name: sp.Function(name) for name in ("a", "bc", "cc", "f", "Ah", "Bh", "Ch", "Kh")}
    local = {**functions, "r": r, "m": mass, "Lambda": lam, "omega": omega, "I": sp.I, "Derivative": sp.Derivative}
    carrier_system = sp.Matrix([[sp.sympify(value, locals=local) for value in row] for row in carrier["full_first_order_system"]])
    carrier_series = [
        sp.Matrix(6, 6, lambda i, j: _inverse_series(carrier_system[i, j], r, depth + 4).get(k, 0))
        for k in range(depth + 5)
    ]
    metric_master = reconstruction["homogeneous_metric_master"]
    metric_system = sp.Matrix([[sp.sympify(value, locals=local) for value in row] for row in metric_master["matrix"]])
    metric_series = [
        sp.Matrix(4, 4, lambda i, j: _inverse_series(metric_system[i, j], r, depth + 6).get(k, 0))
        for k in range(depth + 7)
    ]
    rec = {key: sp.sympify(reconstruction["reconstruction"][key], locals=local) for key in ("Ah_prime", "Kh_prime", "Ch_second")}
    metric_fields = [functions[name](r) for name in ("Ah", "Ch", "Kh")]
    zero_metric: dict[sp.Expr, sp.Expr] = {field: 0 for field in metric_fields}
    for expression in rec.values():
        for derivative in expression.atoms(sp.Derivative):
            if derivative.expr in metric_fields:
                zero_metric[derivative] = 0
    forcing_expressions = [
        _cancel(rec["Ah_prime"].subs(zero_metric)),
        sp.Integer(0),
        _cancel(rec["Ch_second"].subs(zero_metric)),
        _cancel(rec["Kh_prime"].subs(zero_metric)),
    ]
    source_fields = [functions[name](r) for name in ("a", "bc", "cc", "f")]
    u = sp.Symbol("u")
    sigma_symbol = sp.Symbol("sigma_source")

    def forcing_series(jet: list[list[sp.Expr]], rate: sp.Expr, sigma: sp.Expr) -> list[dict[int, sp.Expr]]:
        free = []
        for state_index in (0, 2, 4):
            free.append(sum(jet[n][state_index] * u**n for n in range(len(jet))))
        b0_series = sum(_inverse_series(1 - 2 * mass / r, r, depth + 4).get(k, 0) * u**k for k in range(depth + 5))
        free.append(-free[1] - b0_series * free[2] / 2)
        substitution: dict[sp.Expr, sp.Expr] = {}
        for field, polynomial in zip(source_fields, free):
            factor = polynomial.subs(u, 1 / r)
            substitution[field] = factor
            current = factor
            for order in range(1, 5):
                current = sp.diff(current, r) + (rate + sigma_symbol / r) * current
                substitution[sp.Derivative(field, (r, order))] = current
        result = []
        for expression in forcing_expressions:
            factored = _cancel(expression.subs(substitution).doit().subs(sigma_symbol, sigma))
            result.append(_inverse_series(factored, r, depth + 4))
        return result

    def staircase(source: list[dict[int, sp.Expr]], rate: sp.Expr, sigma: sp.Expr, extra: int, logs: int):
        leading = metric_series[0] - rate * sp.eye(4)
        minimum = min([min(series) for series in source if series] + [0])
        shift = 1 - minimum
        base = sigma + shift + extra
        njet = depth + extra
        unknowns = [sp.Symbol(f"z_{level}_{n}_{i}") for level in range(logs + 1) for n in range(njet + 1) for i in range(4)]

        def vector(level: int, n: int) -> sp.Matrix:
            offset = 4 * ((njet + 1) * level + n)
            return sp.Matrix(4, 1, unknowns[offset:offset + 4])

        equations = []
        for n in range(-1, njet):
            for level in range(logs + 1):
                lhs = sp.zeros(4, 1)
                if 0 <= n <= njet:
                    lhs = (base - n) * vector(level, n)
                    if level < logs:
                        lhs += (level + 1) * vector(level + 1, n)
                rhs = sp.zeros(4, 1)
                for k in range(n + 2):
                    j = n + 1 - k
                    if 0 <= j <= njet:
                        rhs += (leading if k == 0 else metric_series[k]) * vector(level, j)
                source_vector = sp.zeros(4, 1)
                if level == 0:
                    key = n + 1 - shift - extra
                    source_vector = sp.Matrix(4, 1, lambda i, _: source[i].get(key, 0))
                equations.extend(sp.expand(value) for value in lhs - rhs - source_vector)
        matrix, rhs = sp.linear_eq_to_matrix(equations, unknowns)
        solution = _domain_rref_solve(matrix, rhs)
        if solution is None:
            return None
        metric_jets = {
            str(level): [
                [sp.sstr(_cancel(solution[4 * ((njet + 1) * level + n) + i])) for i in range(4)]
                for n in range(njet + 1)
            ]
            for level in range(logs + 1)
        }
        return {
            "base_power": sp.sstr(base),
            "extra_power": extra,
            "log_degree": logs,
            "metric_state_order": ["Ah", "Ch", "Ch_prime", "Kh"],
            "metric_jets_by_log_power": metric_jets,
        }

    sectors = {}
    for name, rate, powers in (
        ("zero", sp.Integer(0), [sp.Integer(-1), sp.Integer(-2), sp.Integer(-3)]),
        ("oscillatory", -2 * sp.I * omega, [-1 - 4 * sp.I * mass * omega, -2 - 4 * sp.I * mass * omega, -3 - 4 * sp.I * mass * omega]),
    ):
        classes = []
        for branch_index, sigma in enumerate(powers):
            if (name, branch_index) not in selections:
                continue
            serialized_modes = carrier["leading_modes"][name]
            matches = [values for key, values in serialized_modes.items() if sp.simplify(sp.sympify(key, locals=local) - sigma) == 0]
            if len(matches) != 1:
                raise RuntimeError(f"{name} carrier power {sigma} leading-vector match changed")
            leading_vector = sp.Matrix([sp.sympify(value, locals=local) for value in matches[0]])
            jet = _simple_jet(carrier_series, rate, sigma, leading_vector, depth)
            source = forcing_series(jet, rate, sigma)
            found = None
            for extra in (0, 1):
                for logs in (0, 1, 2):
                    found = staircase(source, rate, sigma, extra, logs)
                    if found is not None:
                        break
                if found is not None:
                    break
            if found is None:
                raise RuntimeError(f"{name} sourced lift has no class in bounded search")
            found["carrier_power"] = sp.sstr(sigma)
            classes.append(found)
        sectors[name] = classes
    return {
        "depth": depth,
        "sectors": sectors,
        "bounded_search": {"extra_power": [0, 1], "log_degree": [0, 1, 2]},
        "declared_input_domain": "Lambda*(Lambda-2)*omega != 0",
        "rref_pivot_wall_audit": "NOT_EXPOSED_BY_THIS_SOLVER",
    }


def derive_sourced_lift_branch(
    reconstruction: dict,
    carrier: dict,
    sector: str,
    branch_index: int,
    depth: int = 1,
) -> dict:
    """Solve and serialize one exact sourced carrier branch."""
    if sector not in {"zero", "oscillatory"}:
        raise ValueError(f"unknown sourced-lift sector: {sector}")
    if branch_index not in {0, 1, 2}:
        raise ValueError(f"unknown sourced-lift branch index: {branch_index}")
    result = _derive_sourced_lift_selected(
        reconstruction,
        carrier,
        depth,
        {(sector, branch_index)},
    )
    branch = result["sectors"][sector][0]
    return {
        "depth": depth,
        "sector": sector,
        "branch_index": branch_index,
        "declared_input_domain": result["declared_input_domain"],
        "rref_pivot_wall_audit": result["rref_pivot_wall_audit"],
        **branch,
    }


def derive_sourced_lift_classes(reconstruction: dict, carrier: dict, depth: int = 5) -> dict:
    """Solve the six simple sourced carrier branches independently."""
    selections = {(sector, index) for sector in ("zero", "oscillatory") for index in range(3)}
    return _derive_sourced_lift_selected(reconstruction, carrier, depth, selections)


def derive_leading_lift_preflight(reconstruction: dict, carrier: dict) -> dict:
    """Exact leading forcing data; deliberately stops before jet promotion."""
    r = sp.Symbol("r", positive=True)
    mass = sp.Symbol("m", positive=True)
    lam = sp.Symbol("Lambda")
    omega = sp.Symbol("omega", real=True, nonzero=True)
    functions = {name: sp.Function(name) for name in ("a", "bc", "cc", "f", "Ah", "Ch", "Kh")}
    local = {**functions, "r": r, "m": mass, "Lambda": lam, "omega": omega, "I": sp.I, "Derivative": sp.Derivative}
    rec = {key: sp.sympify(reconstruction["reconstruction"][key], locals=local) for key in ("Ah_prime", "Kh_prime", "Ch_second")}
    metric_fields = [functions[name](r) for name in ("Ah", "Ch", "Kh")]
    zero_metric: dict[sp.Expr, sp.Expr] = {field: 0 for field in metric_fields}
    for expression in rec.values():
        for derivative in expression.atoms(sp.Derivative):
            if derivative.expr in metric_fields:
                zero_metric[derivative] = 0
    forcing = [_cancel(rec["Ah_prime"].subs(zero_metric)), 0, _cancel(rec["Ch_second"].subs(zero_metric)), _cancel(rec["Kh_prime"].subs(zero_metric))]
    source_fields = [functions[name](r) for name in ("a", "bc", "cc", "f")]

    def radial_power(expression: sp.Expr) -> int:
        numerator, denominator = sp.fraction(_cancel(expression))
        return int(sp.degree(numerator, r) - sp.degree(denominator, r))

    entries = []
    for sector, rate, powers in (
        ("zero", 0, [-1, -2, -3]),
        ("oscillatory", -2 * sp.I * omega, [-1 - 4 * sp.I * mass * omega, -2 - 4 * sp.I * mass * omega, -3 - 4 * sp.I * mass * omega]),
    ):
        serialized_modes = carrier["leading_modes"][sector]
        for power in powers:
            matches = [values for key, values in serialized_modes.items() if sp.simplify(sp.sympify(key, locals=local) - power) == 0]
            if len(matches) != 1:
                raise RuntimeError("leading lift preflight mode match failed")
            vector = [sp.sympify(value, locals=local) for value in matches[0]]
            amplitudes = [vector[0], vector[2], vector[4]]
            factors = [amplitudes[0], amplitudes[1], amplitudes[2], -amplitudes[1] - (1 - 2 * mass / r) * amplitudes[2] / 2]
            substitutions: dict[sp.Expr, sp.Expr] = {}
            for field, factor in zip(source_fields, factors):
                substitutions[field] = factor
                current = factor
                for order in range(1, 5):
                    current = _cancel(sp.diff(current, r) + (rate + power / r) * current)
                    substitutions[sp.Derivative(field, (r, order))] = current
            factored = [_cancel(expression.subs(substitutions).doit()) if expression != 0 else sp.Integer(0) for expression in forcing]
            shifts = [radial_power(expression) for expression in factored if expression != 0]
            shift = max(shifts)
            leading = [sp.sstr(sp.simplify(sp.limit(expression / r**shift, r, sp.oo))) for expression in factored]
            entries.append({
                "sector": sector,
                "carrier_power": sp.sstr(power),
                "forcing_shift": shift,
                "forcing_power": sp.sstr(sp.simplify(power + shift)),
                "leading_state_forcing": leading,
                "candidate_metric_power": "2" if sector == "zero" else "1-4*I*m*omega",
            })
    return {
        "entries": entries,
        "common_representation_denominator": "Lambda*(Lambda-2)",
        "declared_domain": "Lambda=l(l+1), integer l>=2; real omega!=0; m>0",
        "does_not_establish": "log degree, all-seven constraint closure, or a nonzero F^v EE/EX/XX leading coefficient",
    }
