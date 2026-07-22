#!/usr/bin/env python3
"""Read-only Phase-2 polar per-order recurrence prototype.

This lives in /tmp and imports only frozen/active inputs from the repository.
It deliberately does not write programme artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ_I
from sympy.polys.matrices import DomainMatrix

from black_hole_programme.phase2.general_l_polar.sourced_lift import (
    _cancel,
    _inverse_series,
)


ROOT = Path("/home/alstrup/area9/bp2transformer/physics/symplectic-reconstruction")
V1_IMPORT = {
    "commit": "e5e372f0feabb5faaf91888241d04efab66d46c1",
    "certificate": {
        "path": "black_hole_programme/phase2/general_l_polar/certificate.json",
        "git_blob": "324fe1839d1c5e9d8e6257f409204fd7d74abee5",
        "sha256": "49b224aec8ee358dd4f0c096063d83ee00b2571b222009f73eadd84241a23ab2",
    },
    "subobjects": {
        "carrier_conventions": {
            "json_pointer": "/exact_symbolic_lambda_result/generic_carrier_asymptotics",
            "canonical_json_sha256": "19d366a23c4130a763926a36a83afc37aa5ef1db8f5a08259ca477a01dbf43d1",
        },
        "ricci_reconstruction": {
            "json_pointer": "/exact_symbolic_lambda_result/ricci_to_metric_reconstruction",
            "canonical_json_sha256": "98959867cb94dfb739e6ee05d136f6400762f8b52b08ec7dea86d44b06344cc4",
        },
        "seven_metric_rows": {
            "json_pointer": "/exact_symbolic_lambda_result/ricci_to_metric_reconstruction/metric_rows",
            "canonical_json_sha256": "02a034fb0cf8218bce77a5d3f37b5ea0a18c45875580e75a8d9c3212b96ce009",
        },
        "dependent_source_rows": {
            "json_pointer": "/exact_symbolic_lambda_result/ricci_to_metric_reconstruction/source_dependent_components",
            "canonical_json_sha256": "5d6a6e651d8413fc5d44fb8557ccd71d29e92aba1e1a5d0701657af919093708",
        },
        "depth2_pilot": {
            "json_pointer": "/exact_symbolic_lambda_result/bounded_sourced_lift_depth2_pilot",
            "canonical_json_sha256": "64a90838487b83a3a3ed03a95e75e43d0b16f40aba82cbf1c194a8af051cceb7",
        },
    },
}


DELTA_FACTOR = (
    "Lambda**3 - 24*Lambda**2*omega**2 - 5*Lambda**2 + "
    "48*Lambda*omega**2 + 12*I*Lambda*omega + 6*Lambda + "
    "2048*omega**6 - 1536*I*omega**5 - 256*omega**4 - "
    "288*I*omega**3 - 36*I*omega"
)


def classify_physical_domain_factors(factors: list[str]) -> list[dict]:
    known_nonconstant = {
        "Lambda": "Lambda=ell*(ell+1)>=6",
        "Lambda - 2": "Lambda-2>=4",
        "Lambda - 3": "Lambda-3>=3",
        "omega": "declared real omega!=0",
        "Lambda**2 - 2*Lambda - 12*I*omega": "imaginary part -12*omega is nonzero",
        "Lambda**2 - 2*Lambda - 256*omega**4 + 64*I*omega**3 + 12*I*omega":
            "imaginary part 4*omega*(16*omega**2+3) is nonzero",
        DELTA_FACTOR: (
            "Let x=omega**2>0. Im(Delta)=12*omega*(Lambda-128*x**2-24*x-3). "
            "If Im(Delta)=0, substitution into Re(Delta) gives "
            "128*x**2*(16384*x**4+6144*x**3+1088*x**2+112*x+1)>0."
        ),
    }
    classification = []
    factor_locals = {"Lambda": sp.Symbol("Lambda"), "omega": sp.Symbol("omega"), "I": sp.I}
    for factor in factors:
        if sp.sympify(factor, locals=factor_locals).is_number:
            classification.append({"factor": factor, "class": "NONZERO_RATIONAL_UNIT"})
        elif factor in known_nonconstant:
            classification.append({
                "factor": factor, "class": "PROVED_NONZERO_ON_PHYSICAL_DOMAIN",
                "proof": known_nonconstant[factor],
            })
        else:
            raise RuntimeError(f"unclassified pivot denominator factor: {factor}")
    return classification


def affine_solve(equations: list[sp.Expr], old: list[sp.Symbol], new: list[sp.Symbol]):
    """Solve one order and return all variables in a fresh free basis."""
    variables = old + new
    matrix, rhs = sp.linear_eq_to_matrix(equations, variables)
    symbols = sorted((matrix.free_symbols | rhs.free_symbols) - set(variables), key=lambda x: x.name)
    domain = QQ_I.frac_field(*symbols)
    joined = DomainMatrix.from_Matrix(matrix.row_join(rhs)).convert_to(domain)
    reduced_dm, pivots = joined.rref(method="GJ")
    reduced = reduced_dm.to_Matrix()
    ncols = len(variables)
    for row in range(reduced.rows):
        if all(reduced[row, col] == 0 for col in range(ncols)) and reduced[row, ncols] != 0:
            return None
    variable_pivots = [p for p in pivots if p < ncols]
    free_cols = [j for j in range(ncols) if j not in variable_pivots]
    fresh = list(sp.symbols(f"t0:{len(free_cols)}"))
    solution = {variables[col]: fresh[k] for k, col in enumerate(free_cols)}
    pivot_rows = {pivot: row for row, pivot in enumerate(pivots) if pivot < ncols}
    for pivot, row in pivot_rows.items():
        value = reduced[row, ncols]
        for k, col in enumerate(free_cols):
            value -= reduced[row, col] * fresh[k]
        solution[variables[pivot]] = _cancel(value)
    return solution, fresh, (matrix.rows, matrix.cols), len(variable_pivots)


def setup(branch_sector: str, branch_index: int, carrier_depth: int, metric_depth: int):
    print("stage certificate", flush=True)
    cert = json.loads((ROOT / "black_hole_programme/phase2/general_l_polar/certificate.json").read_text())
    exact = cert["exact_symbolic_lambda_result"]
    reconstruction = exact["ricci_to_metric_reconstruction"]
    carrier = exact["generic_carrier_asymptotics"]
    r = sp.Symbol("r", positive=True)
    # Schwarzschild scaling allows M=1; retain generic Lambda and omega.
    mass = sp.Integer(1)
    lam = sp.Symbol("Lambda")
    omega = sp.Symbol("omega", real=True, nonzero=True)
    functions = {name: sp.Function(name) for name in ("a", "bc", "cc", "f", "Ah", "Bh", "Ch", "Kh")}
    local = {**functions, "r": r, "m": mass, "Lambda": lam, "omega": omega, "I": sp.I, "Derivative": sp.Derivative}
    carrier_system = sp.Matrix([[sp.sympify(v, locals=local) for v in row] for row in carrier["full_first_order_system"]])
    print("stage carrier-series", flush=True)
    carrier_series = [
        sp.Matrix(6, 6, lambda i, j: _inverse_series(carrier_system[i, j], r, carrier_depth + 5).get(k, 0))
        for k in range(carrier_depth + 6)
    ]
    rate = sp.Integer(0) if branch_sector == "zero" else -2 * sp.I * omega
    powers = {
        "zero": [-1, -2, -3],
        "oscillatory": [-1 - 4 * sp.I * mass * omega, -2 - 4 * sp.I * mass * omega, -3 - 4 * sp.I * mass * omega],
    }
    sigma = powers[branch_sector][branch_index]
    matches = [v for k, v in carrier["leading_modes"][branch_sector].items() if sp.simplify(sp.sympify(k, locals=local) - sigma) == 0]
    leading_vector = sp.Matrix([sp.sympify(v, locals=local) for v in matches[0]])
    print("stage carrier-recurrence", flush=True)
    # Simple projected powers are solved one order at a time.  This is the
    # carrier analogue of the metric recurrence below and avoids one 6D global
    # fraction-field RREF.
    t0 = time.perf_counter()
    carrier_jet = [[_cancel(v) for v in leading_vector]]
    carrier_order_timings = []
    shifted = carrier_series[0] - rate * sp.eye(6)
    for n in range(carrier_depth):
        # The rate eigenspace has dimension three and its projected powers
        # differ by integers.  A three-order moving window exposes all such
        # compatibility conditions without retaining an ever-growing global
        # parameter list.
        window = 2
        unknowns = list(sp.symbols(f"cu0:{6*window}"))

        def cvector(index: int) -> sp.Matrix:
            if index <= n:
                return sp.Matrix(6, 1, carrier_jet[index])
            offset = 6 * (index - n - 1)
            return sp.Matrix(6, 1, unknowns[offset:offset+6])

        residuals = []
        for order_n in range(n, n + window):
            residual = (sigma - order_n) * cvector(order_n) - shifted * cvector(order_n + 1)
            for k in range(1, order_n + 2):
                index = order_n + 1 - k
                if index >= 0:
                    residual -= carrier_series[k] * cvector(index)
            residuals.extend(sp.expand(v) for v in residual)
        started_order = time.perf_counter()
        solved = affine_solve(residuals, [], unknowns)
        if solved is None:
            raise RuntimeError(f"carrier incompatible at order {n}")
        mapping, fresh, shape, pivots = solved
        zero_fresh = {p: 0 for p in fresh}
        carrier_jet.append([_cancel(mapping[u].subs(zero_fresh)) for u in unknowns[:6]])
        carrier_order_timings.append({"order": n, "seconds": time.perf_counter()-started_order, "shape": shape, "free": len(fresh)})
    carrier_seconds = time.perf_counter() - t0
    print("carrier raw timings", carrier_order_timings, flush=True)
    return {
        "rate": rate,
        "sigma": sigma,
        "carrier_jet": carrier_jet,
        "carrier_seconds": carrier_seconds,
        "carrier_order_timings": carrier_order_timings,
        "reconstruction": reconstruction,
        "local": local,
        "symbols": (r, lam, omega),
    }


def direct_all_seven(data, depth: int, logs: int, shift: int):
    """Build a small exact all-seven coefficient system, without triangular elimination."""
    reconstruction = data["reconstruction"]
    local = data["local"]
    r, lam, omega = data["symbols"]
    rate, sigma = data["rate"], data["sigma"]
    base = sigma + shift
    frac = QQ_I.frac_field(lam, omega)
    nlevels = depth + 3
    nvars = 4 * nlevels * (logs + 1)
    rate_k, base_k, sigma_k = map(frac.from_sympy, (rate, base, sigma))

    def variable(level: int, n: int, field_index: int) -> int:
        return 4 * (level * nlevels + n) + field_index

    def derivative_tower_maps(field_index: int, max_order=2):
        initial = [
            [{variable(level, n, field_index): frac.one} for n in range(nlevels)]
            for level in range(logs + 1)
        ]
        tower = [initial]
        for _ in range(max_order):
            previous = tower[-1]
            current = [[] for _ in range(logs + 1)]
            for level in range(logs + 1):
                for n in range(nlevels):
                    result = {key: rate_k * value for key, value in previous[level][n].items()}
                    if n:
                        scale = base_k - frac(n - 1)
                        for key, value in previous[level][n-1].items():
                            result[key] = result.get(key, frac.zero) + scale * value
                        if level < logs:
                            for key, value in previous[level+1][n-1].items():
                                result[key] = result.get(key, frac.zero) + frac(level+1) * value
                    current[level].append({key: value for key, value in result.items() if value != frac.zero})
            tower.append(current)
        return tower

    metric_towers = [derivative_tower_maps(i) for i in range(4)]
    carrier = data["carrier_jet"]
    aseq = [frac.from_sympy(row[0]) for row in carrier]
    bseq = [frac.from_sympy(row[2]) for row in carrier]
    cseq = [frac.from_sympy(row[4]) for row in carrier]
    fseq = [-bseq[n] - cseq[n] / 2 + (cseq[n-1] if n else frac.zero) for n in range(len(carrier))]

    def derivative_tower_values(values, max_order=4):
        tower = [values]
        for _ in range(max_order):
            previous = tower[-1]
            tower.append([
                rate_k * previous[n] + ((sigma_k - frac(n - 1)) * previous[n-1] if n else frac.zero)
                for n in range(len(previous))
            ])
        return tower

    source_towers = [derivative_tower_values(seq) for seq in (aseq, bseq, cseq, fseq)]
    functions = {name: sp.Function(name) for name in ("a", "bc", "cc", "f", "Ah", "Bh", "Ch", "Kh")}
    metric_fields = [functions[name](r) for name in ("Ah", "Bh", "Ch", "Kh")]
    source_fields = [functions[name](r) for name in ("a", "bc", "cc", "f")]
    metric_rows = {k: sp.sympify(v, locals=local) for k, v in reconstruction["metric_rows"].items()}
    deps = {k: sp.sympify(v, locals=local) for k, v in reconstruction["source_dependent_components"].items()}
    equations = {
        "vv": metric_rows["vv"] - source_fields[0],
        "vr": metric_rows["vr"] - source_fields[1],
        "rr": metric_rows["rr"] - source_fields[2],
        "vx": metric_rows["vx"] - deps["D"],
        "rx": metric_rows["rx"] - deps["Ec"],
        "angP": metric_rows["angP"] - source_fields[3],
        "angW": metric_rows["angW"] - deps["Gc"],
    }
    all_fields = metric_fields + source_fields
    zero = {}
    for field in all_fields:
        zero[field] = 0
        for order in range(1, 5):
            zero[sp.Derivative(field, (r, order))] = 0

    rows_by_q = {}
    coeff_depth = depth + 10
    delta = sp.simplify(base - sigma)
    if not delta.is_integer:
        raise RuntimeError(f"noninteger base-source offset {delta}")
    delta = int(delta)
    for row_name, expression in equations.items():
        output = {}
        for level in range(logs + 1):
            for field_index, field in enumerate(metric_fields):
                for order in range(3):
                    target = field if order == 0 else sp.Derivative(field, (r, order))
                    coefficient = sp.diff(expression, target).subs(zero)
                    if coefficient == 0:
                        continue
                    for ck, cv_expr in _inverse_series(coefficient, r, coeff_depth).items():
                        cv = frac.from_sympy(cv_expr)
                        for n, svmap in enumerate(metric_towers[field_index][order][level]):
                            q_key = ck + n
                            if q_key > depth:
                                continue
                            row = output.setdefault((level,q_key), [frac.zero] * (nvars + 1))
                            for variable_index, sv in svmap.items():
                                row[variable_index] += cv * sv
        for field_index, field in enumerate(source_fields):
            for order in range(5):
                target = field if order == 0 else sp.Derivative(field, (r, order))
                coefficient = sp.diff(expression, target).subs(zero)
                if coefficient == 0:
                    continue
                for ck, cv_expr in _inverse_series(coefficient, r, coeff_depth).items():
                    cv = frac.from_sympy(cv_expr)
                    for n, sv in enumerate(source_towers[field_index][order]):
                        q_key = ck + n + delta
                        if q_key > depth:
                            continue
                        row = output.setdefault((0,q_key), [frac.zero] * (nvars + 1))
                        row[-1] -= cv * sv
        for (level, q), row in output.items():
            if q <= depth:
                if any(value != frac.zero for value in row):
                    rows_by_q.setdefault(q, []).append((f"{row_name}:log{level}", row))
    selected = []
    timing = []
    order_witnesses = []
    affine = {}
    param_count = 0
    for q in sorted(rows_by_q):
        current_row_records = rows_by_q[q]
        current_rows = [row for _, row in current_row_records]
        selected.extend(current_rows)
        started = time.perf_counter()
        new_indices = sorted({j for row in current_rows for j, value in enumerate(row[:-1]) if value != frac.zero and j not in affine})
        compact_rows = []
        for row in current_rows:
            left = [frac.zero] * (param_count + len(new_indices))
            rhs = row[-1]
            for index, coefficient in enumerate(row[:-1]):
                if coefficient == frac.zero:
                    continue
                if index in affine:
                    constant, parameters = affine[index]
                    rhs -= coefficient * constant
                    for j, value in enumerate(parameters):
                        left[j] += coefficient * value
                else:
                    left[param_count + new_indices.index(index)] += coefficient
            compact_rows.append(left + [rhs])
        matrix = DomainMatrix.from_list(compact_rows, frac)
        reduced, pivots = matrix.rref(method="FF")
        reduced_rows = reduced.to_list()
        compact_nvars = param_count + len(new_indices)
        inconsistent = compact_nvars in pivots
        variable_pivots = [p for p in pivots if p < compact_nvars]
        free_columns = [j for j in range(compact_nvars) if j not in variable_pivots]
        fresh_count = len(free_columns)
        solutions = [(frac.zero, [frac.one if j == k else frac.zero for j in range(fresh_count)]) for k in range(fresh_count)]
        by_column = {column: solutions[k] for k, column in enumerate(free_columns)}
        for row_index, pivot in enumerate(pivots):
            if pivot >= compact_nvars:
                continue
            coefficients = [-reduced_rows[row_index][column] for column in free_columns]
            by_column[pivot] = (reduced_rows[row_index][compact_nvars], coefficients)

        updated = {}
        for index, (constant, parameters) in affine.items():
            new_constant = constant
            new_parameters = [frac.zero] * fresh_count
            for j, coefficient in enumerate(parameters):
                sol_constant, sol_parameters = by_column[j]
                new_constant += coefficient * sol_constant
                for k, value in enumerate(sol_parameters):
                    new_parameters[k] += coefficient * value
            updated[index] = (new_constant, new_parameters)
        for offset, index in enumerate(new_indices):
            updated[index] = by_column[param_count + offset]
        affine = updated
        param_count = fresh_count
        active_columns = sorted({j for row in current_rows for j, value in enumerate(row[:-1]) if value != frac.zero})
        record = {"q": q, "rows": matrix.shape[0], "compact_cols": compact_nvars, "new": new_indices, "free": param_count, "active_minmax": [min(active_columns), max(active_columns)] if active_columns else [], "rank": len(variable_pivots), "inconsistent": inconsistent, "seconds": time.perf_counter()-started}
        timing.append(record)
        particular = [by_column[column][0] for column in range(compact_nvars)]
        nullspace_columns = [
            [by_column[column][1][k] for column in range(compact_nvars)]
            for k in range(fresh_count)
        ]
        order_witnesses.append({
            "q": q,
            "row_labels": [name for name, _row in current_row_records],
            "coordinate_labels": [f"prior_free_{j}" for j in range(compact_nvars - len(new_indices))]
            + [f"metric_variable_{index}" for index in new_indices],
            "compact_augmented_matrix": [
                [sp.sstr(frac.to_sympy(value)) for value in row]
                for row in compact_rows
            ],
            "rref_augmented_matrix": [
                [sp.sstr(frac.to_sympy(value)) for value in row]
                for row in reduced_rows
            ],
            "pivot_columns": list(pivots),
            "variable_pivot_columns": variable_pivots,
            "free_columns": free_columns,
            "equation_count": matrix.shape[0],
            "variable_count": compact_nvars,
            "rank": len(variable_pivots),
            "nullity": fresh_count,
            "particular_solution": [sp.sstr(frac.to_sympy(value)) for value in particular],
            "nullspace_basis": [
                [sp.sstr(frac.to_sympy(value)) for value in column]
                for column in nullspace_columns
            ],
            "rref_is_exact_rank_witness": True,
        })
        print("metric order", record, flush=True)
        if inconsistent:
            break
    canonical = {index: value[0] for index, value in affine.items()}
    residual_defects = []
    for row in selected:
        defect = -row[-1]
        for index, coefficient in enumerate(row[:-1]):
            defect += coefficient * canonical.get(index, frac.zero)
        residual_defects.append(defect)
    if any(defect != frac.zero for defect in residual_defects):
        raise RuntimeError("canonical final-parameter-zero representative fails an original row")

    def factor_denominators(values):
        factors = set()
        factored_denominators = {}
        for value in values:
            denominator = sp.denom(sp.cancel(frac.to_sympy(value)))
            if denominator == 1:
                continue
            denominator_key = sp.sstr(denominator)
            if denominator_key not in factored_denominators:
                factored_denominators[denominator_key] = sp.factor_list(denominator, gens=(lam, omega))
            coefficient, factor_list = factored_denominators[denominator_key]
            if coefficient not in (1, -1):
                factors.add(sp.sstr(coefficient))
            for factor, _multiplicity in factor_list:
                factors.add(sp.sstr(sp.factor(factor)))
        return sorted(factors)

    affine_values = []
    for constant, parameters in affine.values():
        affine_values.append(constant)
        affine_values.extend(parameters)
    denominator_factors = factor_denominators(affine_values)
    canonical_metric_jets = []
    for level in range(logs + 1):
        level_jets = []
        for n in range(depth + 1):
            level_jets.append([
                sp.sstr(frac.to_sympy(canonical.get(variable(level, n, field), frac.zero)))
                for field in range(4)
            ])
        canonical_metric_jets.append(level_jets)
    final_affine_splitting = {
        str(index): {
            "particular": sp.sstr(frac.to_sympy(constant)),
            "free_coefficients": [sp.sstr(frac.to_sympy(value)) for value in parameters],
        }
        for index, (constant, parameters) in sorted(affine.items())
    }
    row_residual_intervals = {
        str(q): {row_name: "0" for row_name in equations}
        for q in range(depth + 1)
    }

    return {
        "base": sp.sstr(base),
        "logs": logs,
        "q_counts": {str(q): len(v) for q, v in rows_by_q.items()},
        "timing": timing,
        "final_homogeneous_parameter_count": param_count,
        "final_affine_splitting": final_affine_splitting,
        "canonical_metric_jets": canonical_metric_jets,
        "per_order_affine_rank_witnesses": order_witnesses,
        "pivot_denominator_factors": denominator_factors,
        "original_seven_row_residuals_zero": True,
        "original_row_count": len(selected),
        "seven_original_ricci_rows": list(equations),
        "seven_row_residual_intervals": row_residual_intervals,
    }


def branch_artifact(branch_sector: str, branch_index: int, carrier_depth: int,
                    metric_depth: int, shift: int, logs: int) -> dict:
    """Produce one deterministic exact branch artifact.

    Runtime timings are deliberately excluded.  The artifact is a stable
    mathematical checkpoint; performance measurements belong in the final
    receipt.
    """
    data = setup(branch_sector, branch_index, carrier_depth, metric_depth)
    result = direct_all_seven(data, metric_depth, logs, shift)
    exact_result = {key: value for key, value in result.items() if key != "timing"}

    exact_result["physical_domain_pivot_classification"] = classify_physical_domain_factors(
        exact_result["pivot_denominator_factors"]
    )
    exact_result["physical_domain_exceptional_set"] = []
    carrier_payload = {
        "sector": branch_sector,
        "index": branch_index,
        "rate": sp.sstr(data["rate"]),
        "sigma": sp.sstr(data["sigma"]),
        "carrier_depth": carrier_depth,
        "metric_depth": metric_depth,
        "shift": shift,
        "carrier_state_order": ["a", "a_prime", "b", "b_prime", "c", "c_prime"],
        "source_field_order": ["a", "b", "c", "f"],
        "metric_field_order": ["Ah", "Bh", "Ch", "Kh"],
        "jet_axis_order": ["log_power", "inverse_radial_order", "field"],
        "source_f_map": "f_n=-b_n-c_n/2+c_(n-1), with c_(-1)=0, at M=1",
        "equation_linked_variable_map": {
            "metric_variable_index": "4*((depth+3)*log_power+inverse_radial_order)+field_index",
            "row_order": ["vv", "vr", "rr", "vx", "rx", "angP", "angW"],
            "row_equations": {
                "vv": "metric_rows.vv-a", "vr": "metric_rows.vr-b",
                "rr": "metric_rows.rr-c", "vx": "metric_rows.vx-D",
                "rx": "metric_rows.rx-Ec", "angP": "metric_rows.angP-f",
                "angW": "metric_rows.angW-Gc",
            },
        },
        "actual_power_depth_mapping": {
            "carrier": f"exp(({sp.sstr(data['rate'])})*r) * r^({sp.sstr(data['sigma'])}-n), 0<=n<={carrier_depth}",
            "metric": f"exp(({sp.sstr(data['rate'])})*r) * r^({sp.sstr(data['sigma'] + shift)}-n) * log(r)^j, 0<=n<={metric_depth}, 0<=j<={logs}",
            "carrier_to_metric_power_shift": shift,
        },
        "carrier_jet": [[sp.sstr(value) for value in row] for row in data["carrier_jet"]],
        "metric_reconstruction": exact_result,
        "constructed_log_degree": logs,
        "complete_log_classification": False,
        "safe_tail_ledger": {
            "carrier_orders_serialized": [0, carrier_depth],
            "metric_orders_verified": [0, metric_depth],
            "maximum_source_derivative_order": 4,
            "carrier_minus_metric_depth": carrier_depth - metric_depth,
            "reading": "Every coefficient used by the seven-row checks through the declared metric depth lies inside the serialized carrier jet; no all-order tail is claimed.",
        },
        "physical_conjugation": {
            "map": "I -> -I",
            "fixed_symbols": ["Lambda", "m", "omega", "alpha"],
            "omega_is_not_negated": True,
            "rate_effect": "-2*I*omega -> +2*I*omega",
        },
        "imported_v1": V1_IMPORT,
    }
    canonicalization = "UTF-8 json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False)"
    canonical = json.dumps(
        carrier_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return {
        "schema_version": "phase2-polar-branch-artifact-v1",
        "result_id": f"PHASE2_POLAR_{branch_sector.upper()}_{branch_index}_EXACT_LIFT_V1",
        "field": "QQ(I)(Lambda,omega)",
        "mass_normalization": "M=1",
        "generic_assumptions": [
            "omega is real and nonzero", "Lambda is real",
            "Lambda = ell*(ell+1)", "ell is an integer >= 2",
            "m=1 in the serialized recurrence",
        ],
        **carrier_payload,
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "payload_sha256_scope": sorted(carrier_payload),
        "payload_sha256_canonicalization": canonicalization,
        "resonant_log_discrepancy": {
            "applies_directly": branch_sector == "oscillatory" and branch_index == 1,
            "v1_depth2_result": "oscillatory branch 1 required log_degree=1 with nonzero log coefficients in the triangular eliminated splitting",
            "this_result": "the constructed direct-seven-row representative has log_degree=0 after the moving carrier recurrence fixes faster-mode freedoms",
            "v1_terminal_carrier_reconciliation": {
                "agreement": "v1 and the extendible carrier agree at n=0,1 and differ at the terminal n=2 coefficient",
                "first_next_order_left_null_defect": "3*Lambda - 48*omega**2 + 15 + 12*I*omega",
                "physical_domain_proof": "its imaginary part is 12*omega, nonzero for real omega!=0",
                "reading": "the v1 terminal carrier jet is nowhere extendible on the declared physical domain; its log is not evidence for an extendible logarithmic branch",
            },
            "disposition": "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT; complete all-order log classification is still not claimed",
        },
        "does_not_establish": [
            "physical finite-norm boundary admissibility",
            "exceptional loci where a listed pivot denominator vanishes",
            "a branch-specialized EE/EX/XX Lee-Wald table by itself",
            "complete resonant log-module classification or invariance under carrier splitting",
        ],
    }


def harden_existing_checkpoint(path: Path) -> dict:
    """Add deterministic metadata to an already completed exact checkpoint.

    This path never reruns the expensive recurrence.  It preserves the
    serialized carrier, metric jets, affine witnesses and denominator list,
    then recomputes the scoped payload hash.  The independent verifier still
    replays the committed equations and RREFs from scratch.
    """
    branch = json.loads(path.read_text())
    sector, index = branch["sector"], branch["index"]
    depth, carrier_depth = branch["metric_depth"], branch["carrier_depth"]
    metric = branch["metric_reconstruction"]
    for witness in metric["per_order_affine_rank_witnesses"]:
        witness["equation_count"] = len(witness["compact_augmented_matrix"])
        witness["variable_count"] = len(witness["compact_augmented_matrix"][0])-1
        witness["rank"] = len(witness["variable_pivot_columns"])
        witness["nullity"] = witness["variable_count"]-witness["rank"]
    metric["physical_domain_pivot_classification"] = classify_physical_domain_factors(
        metric["pivot_denominator_factors"]
    )
    metric["physical_domain_exceptional_set"] = []
    branch.update({
        "carrier_state_order": ["a", "a_prime", "b", "b_prime", "c", "c_prime"],
        "source_field_order": ["a", "b", "c", "f"],
        "metric_field_order": ["Ah", "Bh", "Ch", "Kh"],
        "jet_axis_order": ["log_power", "inverse_radial_order", "field"],
        "source_f_map": "f_n=-b_n-c_n/2+c_(n-1), with c_(-1)=0, at M=1",
        "equation_linked_variable_map": {
            "metric_variable_index": "4*((depth+3)*log_power+inverse_radial_order)+field_index",
            "row_order": ["vv", "vr", "rr", "vx", "rx", "angP", "angW"],
            "row_equations": {
                "vv": "metric_rows.vv-a", "vr": "metric_rows.vr-b", "rr": "metric_rows.rr-c",
                "vx": "metric_rows.vx-D", "rx": "metric_rows.rx-Ec",
                "angP": "metric_rows.angP-f", "angW": "metric_rows.angW-Gc",
            },
        },
        "constructed_log_degree": 0,
        "complete_log_classification": False,
        "safe_tail_ledger": {
            "carrier_orders_serialized": [0, carrier_depth], "metric_orders_verified": [0, depth],
            "maximum_source_derivative_order": 4,
            "carrier_minus_metric_depth": carrier_depth-depth,
            "reading": "Every coefficient used by the seven-row checks through the declared metric depth lies inside the serialized carrier jet; no all-order tail is claimed.",
        },
        "imported_v1": V1_IMPORT,
        "resonant_log_discrepancy": {
            "applies_directly": sector == "oscillatory" and index == 1,
            "v1_depth2_result": "oscillatory branch 1 required log_degree=1 with nonzero log coefficients in the triangular eliminated splitting",
            "this_result": "the constructed direct-seven-row representative has log_degree=0 after the moving carrier recurrence fixes faster-mode freedoms",
            "v1_terminal_carrier_reconciliation": {
                "agreement": "v1 and the extendible carrier agree at n=0,1 and differ at the terminal n=2 coefficient",
                "first_next_order_left_null_defect": "3*Lambda - 48*omega**2 + 15 + 12*I*omega",
                "physical_domain_proof": "its imaginary part is 12*omega, nonzero for real omega!=0",
                "reading": "the v1 terminal carrier jet is nowhere extendible on the declared physical domain; its log is not evidence for an extendible logarithmic branch",
            },
            "disposition": "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT; complete all-order log classification is still not claimed",
        },
    })
    scope = [
        "actual_power_depth_mapping", "carrier_depth", "carrier_jet", "carrier_state_order",
        "complete_log_classification", "constructed_log_degree", "equation_linked_variable_map",
        "imported_v1", "index", "jet_axis_order", "metric_depth", "metric_field_order",
        "metric_reconstruction", "physical_conjugation", "rate", "safe_tail_ledger", "sector",
        "shift", "sigma", "source_f_map", "source_field_order",
    ]
    payload = {key: branch[key] for key in scope}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    branch["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
    branch["payload_sha256_scope"] = scope
    branch["payload_sha256_canonicalization"] = "UTF-8 json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False)"
    branch.setdefault("does_not_establish", []).append(
        "complete resonant log-module classification or invariance under carrier splitting"
    )
    branch["does_not_establish"] = list(dict.fromkeys(branch["does_not_establish"]))
    path.write_text(json.dumps(branch, indent=2, sort_keys=True)+"\n")
    return branch


def old_triangular_setup(branch_sector: str, branch_index: int, carrier_depth: int, metric_depth: int):
    """Retained only as a comparison with the eliminated reconstruction."""
    data = setup(branch_sector, branch_index, carrier_depth, metric_depth)
    reconstruction = data["reconstruction"]
    carrier_jet = data["carrier_jet"]
    rate, sigma = data["rate"], data["sigma"]
    r, lam, omega = data["symbols"]
    mass = sp.Integer(1)
    functions = data["local"]
    local = data["local"]
    print("stage metric-series", flush=True)

    metric_system = sp.Matrix([[sp.sympify(v, locals=local) for v in row] for row in reconstruction["homogeneous_metric_master"]["matrix"]])
    metric_series = [
        sp.Matrix(4, 4, lambda i, j: _inverse_series(metric_system[i, j], r, metric_depth + 8).get(k, 0))
        for k in range(metric_depth + 9)
    ]
    print("stage forcing", flush=True)
    rec = {key: sp.sympify(reconstruction["reconstruction"][key], locals=local) for key in ("Ah_prime", "Kh_prime", "Ch_second")}
    metric_fields = [functions[name](r) for name in ("Ah", "Ch", "Kh")]
    zero_metric = {field: 0 for field in metric_fields}
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
    # Apply the source differential operator directly to coefficient arrays.
    # This avoids constructing/cancelling one enormous rational expression.
    frac = QQ_I.frac_field(lam, omega)
    zero_k = frac.zero
    rate_k, sigma_k = frac.from_sympy(rate), frac.from_sympy(sigma)
    aseq = [frac.from_sympy(row[0]) for row in carrier_jet]
    bseq = [frac.from_sympy(row[2]) for row in carrier_jet]
    cseq = [frac.from_sympy(row[4]) for row in carrier_jet]
    fseq = []
    for n in range(len(carrier_jet)):
        previous_c = cseq[n - 1] if n else zero_k
        fseq.append(-bseq[n] - cseq[n] / 2 + previous_c)
    sequences = [aseq, bseq, cseq, fseq]

    def derivative_sequence(values):
        return [
            rate_k * values[n] + ((sigma_k - frac(n - 1)) * values[n - 1] if n else zero_k)
            for n in range(len(values))
        ]

    derivatives: list[list[list[sp.Expr]]] = []
    for values in sequences:
        tower = [values]
        for _ in range(4):
            tower.append(derivative_sequence(tower[-1]))
        derivatives.append(tower)

    source = []
    zero_source = {field: 0 for field in source_fields}
    for field in source_fields:
        for order in range(1, 5):
            zero_source[sp.Derivative(field, (r, order))] = 0
    for expression in forcing_expressions:
        total = {}
        for field_index, field in enumerate(source_fields):
            for order in range(5):
                target = field if order == 0 else sp.Derivative(field, (r, order))
                coefficient = sp.diff(expression, target).subs(zero_source)
                if coefficient == 0:
                    continue
                cseries = {k: frac.from_sympy(v) for k, v in _inverse_series(coefficient, r, carrier_depth + 5).items()}
                for ck, cv in cseries.items():
                    for n, sv in enumerate(derivatives[field_index][order]):
                        if cv != 0 and sv != 0:
                            key = ck + n
                            total[key] = total.get(key, zero_k) + cv * sv
        source.append({key: frac.to_sympy(value) for key, value in total.items() if value != zero_k})
    minimum = min([min(series) for series in source if series] + [0])
    shift = 1 - minimum
    return {
        "rate": rate, "sigma": sigma, "source": source, "shift": shift,
        "metric_series": metric_series, "carrier_seconds": carrier_seconds,
        "carrier_order_timings": carrier_order_timings,
    }


def incremental(data, depth: int, extra: int, logs: int):
    rate, sigma = data["rate"], data["sigma"]
    source, shift, matrices = data["source"], data["shift"], data["metric_series"]
    leading = matrices[0] - rate * sp.eye(4)
    base = sigma + shift + extra
    params: list[sp.Symbol] = []
    jets: list[list[sp.Matrix]] = [[] for _ in range(logs + 1)]
    timing = []
    # n=-1 produces coefficient zero; n=depth-1 produces coefficient depth.
    for n in range(-1, depth):
        unknowns = list(sp.symbols(f"u0:{4*(logs+1)}"))
        vectors = [sp.Matrix(4, 1, unknowns[4*l:4*(l+1)]) for l in range(logs + 1)]
        equations = []
        for level in range(logs + 1):
            lhs = sp.zeros(4, 1)
            if n >= 0:
                lhs = (base - n) * jets[level][n]
                if level < logs:
                    lhs += (level + 1) * jets[level + 1][n]
            rhs = leading * vectors[level]
            for k in range(1, n + 2):
                j = n + 1 - k
                if 0 <= j < len(jets[level]):
                    rhs += matrices[k] * jets[level][j]
            src = sp.zeros(4, 1)
            if level == 0:
                key = n + 1 - shift - extra
                src = sp.Matrix(4, 1, lambda i, _: source[i].get(key, 0))
            equations.extend([sp.expand(x) for x in lhs - rhs - src])
        started = time.perf_counter()
        solved = affine_solve(equations, params, unknowns)
        elapsed = time.perf_counter() - started
        if solved is None:
            return None, {"failed_order": n, "timing": timing + [elapsed]}
        mapping, fresh, shape, pivots = solved
        old_sub = {p: mapping[p] for p in params}
        for level in range(logs + 1):
            jets[level] = [v.applyfunc(lambda x: _cancel(x.subs(old_sub))) for v in jets[level]]
            current = vectors[level].applyfunc(lambda x: _cancel(mapping[x]))
            jets[level].append(current)
        params = fresh
        timing.append({"order": n, "seconds": elapsed, "shape": shape, "pivots": pivots, "free": len(params)})
    return {"base": base, "jets": jets, "params": params}, {"timing": timing}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sector", choices=["zero", "oscillatory"])
    parser.add_argument("index", type=int)
    parser.add_argument("--carrier-depth", type=int, default=7)
    parser.add_argument("--metric-depth", type=int, default=3)
    parser.add_argument("--shift", type=int, default=2)
    parser.add_argument("--logs", type=int, default=0)
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    artifact = branch_artifact(
        args.sector, args.index, args.carrier_depth, args.metric_depth,
        args.shift, args.logs,
    )
    if args.artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
        print("artifact", args.artifact, artifact["payload_sha256"], flush=True)
    else:
        print("artifact-result", artifact, flush=True)
    print("total", time.perf_counter()-started, flush=True)


if __name__ == "__main__":
    main()
