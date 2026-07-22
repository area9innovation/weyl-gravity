#!/usr/bin/env python3
"""Independent exact verifier for the canonical polar finite-depth frontier.

This rail intentionally does not import the recurrence producer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp
from sympy.polys.domains import QQ_I
from sympy.polys.matrices import DomainMatrix


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
LAMBDA, OMEGA = sp.symbols("Lambda omega", real=True)
LOCALS = {"Lambda": LAMBDA, "omega": OMEGA, "I": sp.I}


def canonical_hash(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def expr(value: str) -> sp.Expr:
    return sp.cancel(sp.sympify(value, locals=LOCALS))


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[expr(value) for value in row] for row in rows])


def inverse_series(expression: sp.Expr, r: sp.Symbol, depth: int) -> dict[int, sp.Expr]:
    """Independent Laurent expansion at infinity for one rational coefficient."""
    expression = sp.cancel(sp.together(expression))
    if expression == 0:
        return {}
    numerator, denominator = sp.fraction(expression)
    pnum, pden = sp.Poly(sp.expand(numerator), r), sp.Poly(sp.expand(denominator), r)
    nmax = max(monomial[0] for monomial in pnum.monoms())
    dmax = max(monomial[0] for monomial in pden.monoms())
    den = [pden.coeff_monomial(r ** (dmax-k)) if dmax-k >= 0 else 0 for k in range(depth+1)]
    inv = [sp.cancel(1 / den[0])]
    for k in range(1, depth+1):
        inv.append(sp.cancel(-sum(den[j]*inv[k-j] for j in range(1, k+1))/den[0]))
    num = [pnum.coeff_monomial(r ** (nmax-k)) if nmax-k >= 0 else 0 for k in range(depth+1)]
    return {
        k-(nmax-dmax): sp.expand(sum(num[j]*inv[k-j] for j in range(k+1)))
        for k in range(depth+1)
    }


def derivative_tower(values: list[sp.Expr], rate: sp.Expr, power: sp.Expr, order: int) -> list[list[sp.Expr]]:
    tower = [values]
    for _ in range(order):
        previous = tower[-1]
        tower.append([
            sp.cancel(rate*previous[n] + ((power-(n-1))*previous[n-1] if n else 0))
            for n in range(len(previous))
        ])
    return tower


def exact_rref(source: sp.Matrix) -> tuple[sp.Matrix, tuple[int, ...]]:
    domain = QQ_I.frac_field(LAMBDA, OMEGA)
    reduced, pivots = DomainMatrix.from_Matrix(source).convert_to(domain).rref(method="FF")
    return reduced.to_Matrix(), pivots


def replay_seven_rows(branch: dict, v1: dict) -> None:
    """Substitute serialized jets into the seven committed Ricci rows afresh."""
    r = sp.Symbol("r", positive=True)
    functions = {name: sp.Function(name) for name in ("a", "bc", "cc", "f", "Ah", "Bh", "Ch", "Kh")}
    local = {**functions, "r": r, "m": sp.Integer(1), "Lambda": LAMBDA, "omega": OMEGA, "I": sp.I, "Derivative": sp.Derivative}
    reconstruction = v1["exact_symbolic_lambda_result"]["ricci_to_metric_reconstruction"]
    metric_rows = {key: sp.sympify(value, locals=local) for key, value in reconstruction["metric_rows"].items()}
    dependent = {key: sp.sympify(value, locals=local) for key, value in reconstruction["source_dependent_components"].items()}
    source_fields = [functions[name](r) for name in ("a", "bc", "cc", "f")]
    metric_fields = [functions[name](r) for name in ("Ah", "Bh", "Ch", "Kh")]
    equations = {
        "vv": metric_rows["vv"]-source_fields[0], "vr": metric_rows["vr"]-source_fields[1],
        "rr": metric_rows["rr"]-source_fields[2], "vx": metric_rows["vx"]-dependent["D"],
        "rx": metric_rows["rx"]-dependent["Ec"], "angP": metric_rows["angP"]-source_fields[3],
        "angW": metric_rows["angW"]-dependent["Gc"],
    }
    zero = {}
    for field in source_fields + metric_fields:
        zero[field] = 0
        for order in range(1, 5):
            zero[sp.Derivative(field, (r, order))] = 0
    rate, sigma = expr(branch["rate"]), expr(branch["sigma"])
    base = expr(branch["metric_reconstruction"]["base"])
    depth = branch["metric_depth"]
    carrier = [[expr(value) for value in row] for row in branch["carrier_jet"]]
    aseq = [row[0] for row in carrier]
    bseq = [row[2] for row in carrier]
    cseq = [row[4] for row in carrier]
    fseq = [-bseq[n]-cseq[n]/2+(cseq[n-1] if n else 0) for n in range(len(carrier))]
    source_towers = [derivative_tower(values, rate, sigma, 4) for values in (aseq, bseq, cseq, fseq)]
    metric_values = [[expr(value) for value in row] for row in branch["metric_reconstruction"]["canonical_metric_jets"][0]]
    metric_towers = [derivative_tower([row[field] for row in metric_values], rate, base, 3) for field in range(4)]
    delta = int(sp.simplify(base-sigma))
    for row_name, equation in equations.items():
        coefficients = [sp.Integer(0)]*(depth+1)
        for field_index, field in enumerate(metric_fields):
            for order in range(4):
                target = field if order == 0 else sp.Derivative(field, (r, order))
                coefficient = sp.diff(equation, target).subs(zero)
                for ck, cv in inverse_series(coefficient, r, depth+10).items():
                    for n, value in enumerate(metric_towers[field_index][order]):
                        q = ck+n
                        if 0 <= q <= depth:
                            coefficients[q] += cv*value
        for field_index, field in enumerate(source_fields):
            for order in range(5):
                target = field if order == 0 else sp.Derivative(field, (r, order))
                coefficient = sp.diff(equation, target).subs(zero)
                for ck, cv in inverse_series(coefficient, r, depth+10).items():
                    for n, value in enumerate(source_towers[field_index][order]):
                        q = ck+n+delta
                        if 0 <= q <= depth:
                            coefficients[q] += cv*value
        defects = [sp.cancel(value) for value in coefficients]
        if any(value != 0 for value in defects):
            raise RuntimeError(f"fresh seven-row replay failed: {branch['sector']}:{branch['index']}:{row_name}")


def verify_rref_shape(reduced: sp.Matrix, pivots: list[int]) -> None:
    last = -1
    for row, pivot in enumerate(pivots):
        if pivot <= last or reduced[row, pivot] != 1:
            raise RuntimeError("invalid serialized RREF pivot")
        if any(reduced[other, pivot] != 0 for other in range(reduced.rows) if other != row):
            raise RuntimeError("serialized RREF pivot column not reduced")
        if any(reduced[row, column] != 0 for column in range(pivot)):
            raise RuntimeError("serialized RREF has a leading entry before its pivot")
        last = pivot


def verify_branch(branch: dict, schema: dict, imported_v1: dict, v1: dict) -> None:
    jsonschema.validate(branch, schema)
    if branch["imported_v1"] != imported_v1:
        raise RuntimeError("branch provenance binding drift")
    payload = {key: branch[key] for key in branch["payload_sha256_scope"]}
    if canonical_hash(payload) != branch["payload_sha256"]:
        raise RuntimeError("branch payload SHA drift")
    metric = branch["metric_reconstruction"]
    depth = branch["metric_depth"]
    if branch["carrier_depth"] - depth != 4:
        raise RuntimeError("safe-tail depth margin drift")
    for witness in metric["per_order_affine_rank_witnesses"]:
        augmented = matrix(witness["compact_augmented_matrix"])
        reduced = matrix(witness["rref_augmented_matrix"])
        variables = witness["variable_count"]
        if augmented.shape != (witness["equation_count"], variables + 1):
            raise RuntimeError("compact witness shape drift")
        if reduced.shape != augmented.shape:
            raise RuntimeError("RREF witness shape drift")
        pivots = witness["pivot_columns"]
        verify_rref_shape(reduced, pivots)
        independently_reduced, independent_pivots = exact_rref(augmented)
        if independent_pivots != tuple(pivots) or independently_reduced != reduced:
            raise RuntimeError("independent exact RREF replay disagrees with witness")
        if variables in pivots:
            raise RuntimeError("serialized affine system is inconsistent")
        if witness["rank"] != len(witness["variable_pivot_columns"]):
            raise RuntimeError("rank witness drift")
        if witness["nullity"] != variables - witness["rank"]:
            raise RuntimeError("nullity witness drift")
        left, rhs = augmented[:, :variables], augmented[:, variables]
        particular = sp.Matrix([expr(value) for value in witness["particular_solution"]])
        if any(sp.cancel(value) != 0 for value in left * particular - rhs):
            raise RuntimeError("particular affine witness fails")
        for serialized in witness["nullspace_basis"]:
            vector = sp.Matrix([expr(value) for value in serialized])
            if any(sp.cancel(value) != 0 for value in left * vector):
                raise RuntimeError("nullspace affine witness fails")
    splitting = metric["final_affine_splitting"]
    jets = metric["canonical_metric_jets"][0]
    for n in range(depth + 1):
        for field in range(4):
            index = str(4 * n + field)
            expected = splitting.get(index, {"particular": "0"})["particular"]
            if expr(jets[n][field]) != expr(expected):
                raise RuntimeError("canonical jet/final splitting mismatch")
    if set(metric["seven_original_ricci_rows"]) != {"vv", "vr", "rr", "vx", "rx", "angP", "angW"}:
        raise RuntimeError("seven-row label set drift")
    if any(value != "0" for rows in metric["seven_row_residual_intervals"].values() for value in rows.values()):
        raise RuntimeError("nonzero seven-row residual serialized")
    if metric["physical_domain_exceptional_set"]:
        raise RuntimeError("physical pivot wall was not excluded")
    replay_seven_rows(branch, v1)


def verify_domain_identities() -> None:
    x = sp.symbols("x", positive=True)
    delta = (
        LAMBDA**3 - 24 * LAMBDA**2 * OMEGA**2 - 5 * LAMBDA**2
        + 48 * LAMBDA * OMEGA**2 + 12 * sp.I * LAMBDA * OMEGA + 6 * LAMBDA
        + 2048 * OMEGA**6 - 1536 * sp.I * OMEGA**5 - 256 * OMEGA**4
        - 288 * sp.I * OMEGA**3 - 36 * sp.I * OMEGA
    )
    imaginary = sp.im(delta.expand(complex=True))
    expected_imaginary = 12 * OMEGA * (LAMBDA - 128 * OMEGA**4 - 24 * OMEGA**2 - 3)
    if sp.expand(imaginary - expected_imaginary) != 0:
        raise RuntimeError("Delta imaginary-part identity drift")
    real_on_zero_imag = sp.re(delta.expand(complex=True)).subs({OMEGA**2: x, LAMBDA: 128*x**2 + 24*x + 3})
    expected_real = 128*x**2*(16384*x**4 + 6144*x**3 + 1088*x**2 + 112*x + 1)
    if sp.expand(real_on_zero_imag - expected_real) != 0:
        raise RuntimeError("Delta positive real-part identity drift")
    defect = 3 * LAMBDA - 48 * OMEGA**2 + 15 + 12 * sp.I * OMEGA
    if sp.im(defect.expand(complex=True)) != 12 * OMEGA:
        raise RuntimeError("v1 terminal-jet nonextendibility identity drift")


def verify_v1_shallow_nonextendibility(v1: dict) -> None:
    """Rebuild the v1 depth-2 carrier and test its next compatibility row."""
    r = sp.Symbol("r", positive=True)
    carrier = v1["exact_symbolic_lambda_result"]["generic_carrier_asymptotics"]
    local = {"r": r, "m": sp.Integer(1), "Lambda": LAMBDA, "omega": OMEGA, "I": sp.I, "Derivative": sp.Derivative}
    system = sp.Matrix([[sp.sympify(value, locals=local) for value in row] for row in carrier["full_first_order_system"]])
    series = [
        sp.Matrix(6, 6, lambda i, j: inverse_series(system[i, j], r, 10).get(k, 0))
        for k in range(11)
    ]
    rate = -2*sp.I*OMEGA
    sigma = -2-4*sp.I*OMEGA
    matches = [
        values for key, values in carrier["leading_modes"]["oscillatory"].items()
        if sp.simplify(sp.sympify(key, locals=local)-sigma) == 0
    ]
    if len(matches) != 1:
        raise RuntimeError("v1 oscillatory branch-one leading vector drift")
    c0 = sp.Matrix([sp.sympify(value, locals=local) for value in matches[0]])
    unknowns = list(sp.symbols("u0:12"))
    c1, c2 = sp.Matrix(unknowns[:6]), sp.Matrix(unknowns[6:])
    shifted = series[0]-rate*sp.eye(6)
    equations = []
    vectors = [c0, c1, c2]
    for n in (0, 1):
        residual = (sigma-n)*vectors[n]-shifted*vectors[n+1]
        for k in range(1, n+2):
            residual -= series[k]*vectors[n+1-k]
        equations.extend(residual)
    left, rhs = sp.linear_eq_to_matrix(equations, unknowns)
    augmented = left.row_join(rhs)
    reduced, pivots = exact_rref(augmented)
    if left.cols in pivots:
        raise RuntimeError("v1 depth-2 carrier unexpectedly inconsistent")
    solution = sp.zeros(left.cols, 1)
    for row, pivot in enumerate(pivots):
        if pivot < left.cols:
            solution[pivot] = reduced[row, left.cols]
    c1 = solution[:6, :]
    c2 = solution[6:, :]
    rhs3 = (sigma-2)*c2-series[1]*c2-series[2]*c1-series[3]*c0
    projections = [sp.factor(sp.cancel((left_vector.T*rhs3)[0])) for left_vector in shifted.T.nullspace()]
    expected_first = 3*(LAMBDA-16*OMEGA**2+4*sp.I*OMEGA+5)
    if not projections or sp.cancel(projections[0]-expected_first) != 0:
        raise RuntimeError("v1 next-order carrier obstruction replay drift")
    if sp.im(projections[0].expand(complex=True)) != 12*OMEGA:
        raise RuntimeError("v1 next-order carrier obstruction lost physical nonwall")


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    data = json.loads(CERT.read_text())
    jsonschema.validate(data, schema)
    if data["result_id"] != "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_CANONICAL_LOG_FREE_FRONTIER_V1":
        raise RuntimeError("wrong frontier result")
    imported = data["imported_v1"]
    v1_path = ROOT / imported["certificate"]["path"]
    v1_raw = v1_path.read_bytes()
    if hashlib.sha256(v1_raw).hexdigest() != imported["certificate"]["sha256"]:
        raise RuntimeError("v1 certificate hash drift")
    v1 = json.loads(v1_raw)
    branches = data["canonical_log_free_frontier"]
    if {(row["sector"], row["branch_index"]) for row in branches} != {
        (sector, index) for sector in ("zero", "oscillatory") for index in range(3)
    }:
        raise RuntimeError("six-branch frontier drift")
    for row in branches:
        path = ROOT / row["artifact_path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["artifact_sha256"]:
            raise RuntimeError("branch file hash drift")
        branch = json.loads(raw)
        verify_branch(branch, schema, imported, v1)
    verify_domain_identities()
    verify_v1_shallow_nonextendibility(v1)
    required_missing = {
        "complete resonant log-degree and carrier-splitting classification",
        "branch-specialized EE/EX/XX leading table",
        "exact current exceptional set",
    }
    if not required_missing <= set(data["unavailable_theorem_fields"]):
        raise RuntimeError("partial frontier overpromoted")
    print("PASS: independent six-branch canonical polar frontier and claim boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
