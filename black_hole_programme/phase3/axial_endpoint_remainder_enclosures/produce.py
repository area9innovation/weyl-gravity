"""Produce the exact/interval endpoint-enclosure audit.

The horizon calculation is constructive.  It shears the repaired six-state
metric flow to a regular-singular system, diagonalizes its residue exactly,
and turns three exact recurrence orders into outward interval initial boxes
on four rational frequency cells.  A Cauchy majorant on a complex rho disk
supplies the all-order tail bound consumed by Forge ``math/ivendpoint``.

At infinity, an independently replayed weighted block-factorization supplies
an exact integrable Volterra envelope and a contraction proof at a deliberately
proof-oriented radius R=2^256.  That is an existence enclosure, not a useful
global-matching handoff: the current finite-interval interval flow cannot move
stably from R=2^256 to the black-hole exterior.  The practical dispatcher
therefore remains fail closed pending a cellwise higher-order recurrence or a
validated phase-normalized inward transfer.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
REPO = PHYSICS.parents[1]
FORGE = Path("/home/alstrup/area9/tango/forge")
REPAIR = HERE.parent / "axial_complete_reconstruction_repair"
REPAIR_CERT = REPAIR / "certificate.json"
REPAIR_SOURCE = REPAIR / "produce.py"
INFINITY_HEADS = HERE / "infinity-metric-heads.json"
INFINITY_ENVELOPE = HERE / "infinity-volterra-envelope.json"
FORGE_ENDPOINT = FORGE / "lib/math/ivendpoint.forge"
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
ADAPTER = HERE / "validated_horizon_initializer.forge"
RECEIPT = HERE / "receipt.json"
RESULT_TOKEN = "BH_PHASE3_AXIAL_ENDPOINT_REMAINDER_ENCLOSURES_V1"


class EndpointError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EndpointError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_repair_module():
    spec = importlib.util.spec_from_file_location("p3_axial_repair", REPAIR_SOURCE)
    require(spec is not None and spec.loader is not None, "repair producer import failed")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPAIR))
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class RI:
    lo: Fraction
    hi: Fraction

    def __init__(self, lo, hi=None):
        object.__setattr__(self, "lo", Fraction(lo))
        object.__setattr__(self, "hi", Fraction(lo if hi is None else hi))
        require(self.lo <= self.hi, "reversed real interval")

    def __add__(self, other):
        other = as_ri(other)
        return RI(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return RI(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-as_ri(other))

    def __rsub__(self, other):
        return as_ri(other) - self

    def __mul__(self, other):
        other = as_ri(other)
        products = (self.lo * other.lo, self.lo * other.hi,
                    self.hi * other.lo, self.hi * other.hi)
        return RI(min(products), max(products))

    __rmul__ = __mul__

    def square(self):
        if self.lo <= 0 <= self.hi:
            return RI(0, max(self.lo * self.lo, self.hi * self.hi))
        values = (self.lo * self.lo, self.hi * self.hi)
        return RI(min(values), max(values))

    def reciprocal(self):
        require(not self.lo <= 0 <= self.hi, "interval reciprocal crosses zero")
        values = (1 / self.lo, 1 / self.hi)
        return RI(min(values), max(values))

    def __truediv__(self, other):
        return self * as_ri(other).reciprocal()

    def abs_hi(self):
        return max(abs(self.lo), abs(self.hi))


def as_ri(value) -> RI:
    return value if isinstance(value, RI) else RI(value)


@dataclass(frozen=True)
class CI:
    re: RI
    im: RI

    def __init__(self, re=0, im=0):
        object.__setattr__(self, "re", as_ri(re))
        object.__setattr__(self, "im", as_ri(im))

    def __add__(self, other):
        other = as_ci(other)
        return CI(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return CI(-self.re, -self.im)

    def __sub__(self, other):
        return self + (-as_ci(other))

    def __rsub__(self, other):
        return as_ci(other) - self

    def __mul__(self, other):
        other = as_ci(other)
        return CI(self.re * other.re - self.im * other.im,
                  self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def reciprocal(self):
        denominator = self.re.square() + self.im.square()
        require(denominator.lo > 0, "complex rectangle reciprocal not separated from zero")
        return CI(self.re / denominator, -self.im / denominator)

    def __truediv__(self, other):
        return self * as_ci(other).reciprocal()

    def power(self, exponent: int):
        if exponent < 0:
            return self.power(-exponent).reciprocal()
        out = CI(1)
        for _ in range(exponent):
            out = out * self
        return out

    def norm_one_hi(self):
        return self.re.abs_hi() + self.im.abs_hi()


def as_ci(value) -> CI:
    return value if isinstance(value, CI) else CI(value)


def eval_rect(expr: sp.Expr, environment: dict[sp.Symbol, CI]) -> CI:
    """Exact rational rectangle evaluation of a factored SymPy expression."""
    if expr == sp.I:
        return CI(0, 1)
    if expr.is_Integer:
        return CI(Fraction(int(expr)))
    if expr.is_Rational:
        return CI(Fraction(int(expr.p), int(expr.q)))
    if expr.is_Symbol:
        return environment[expr]
    if expr.is_Add:
        out = CI()
        for arg in expr.args:
            out = out + eval_rect(arg, environment)
        return out
    if expr.is_Mul:
        out = CI(1)
        for arg in expr.args:
            out = out * eval_rect(arg, environment)
        return out
    if expr.is_Pow and expr.exp.is_Integer:
        return eval_rect(expr.base, environment).power(int(expr.exp))
    raise EndpointError(f"unsupported interval expression: {expr}")


def eval_rational_rect(expr: sp.Expr, environment: dict[sp.Symbol, CI]) -> CI:
    """Evaluate a rational expression without destroying denominator factors.

    ``cancel`` often expands a product denominator.  Evaluating that expansion
    loses the correlations which keep its factors away from zero.  We instead
    factor only the (small) denominator and leave the numerator expanded.
    """
    numerator, denominator = sp.fraction(sp.cancel(expr))
    coefficient, factors = sp.factor_list(denominator)
    out = eval_rect(numerator, environment) / eval_rect(coefficient, environment)
    for factor, multiplicity in factors:
        out = out / eval_rect(factor, environment).power(multiplicity)
    return out


def realify_sympy(matrix: sp.Matrix) -> sp.Matrix:
    re = matrix.applyfunc(lambda z: sp.re(sp.expand_complex(z)))
    im = matrix.applyfunc(lambda z: sp.im(sp.expand_complex(z)))
    return re.row_join(-im).col_join(im.row_join(re))


def realify_intervals(matrix: list[list[CI]]) -> list[list[RI]]:
    n = len(matrix)
    out = [[RI(0) for _ in range(2 * n)] for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = matrix[i][j].re
            out[i][j + n] = -matrix[i][j].im
            out[i + n][j] = matrix[i][j].im
            out[i + n][j + n] = matrix[i][j].re
    return out


def exact_horizon_data(repair):
    system = repair.build_exact_system()
    r, omega = system["symbols"]["r"], system["symbols"]["omega"]
    rho = sp.Symbol("rho")
    flow = system["flow6"].subs(r, 2 + rho)

    # x=(P,P',Q,Q',H1,rho F) removes the apparent double pole introduced by
    # algebraically eliminating H0 on the propagated C=0 fibre.
    shear = sp.diag(1, 1, 1, 1, 1, rho)
    shear_inv = sp.diag(1, 1, 1, 1, 1, 1 / rho)
    b = (rho * (shear.diff(rho) * shear_inv
                + shear * flow * shear_inv)).applyfunc(repair.cancel)
    b0 = b.applyfunc(lambda e: repair.cancel(sp.limit(e, rho, 0)))
    characteristic = sp.factor(b0.charpoly().as_expr())
    expected = (sp.Symbol("lambda") ** 3
                * (sp.Symbol("lambda") + 4 * sp.I * omega)
                * (sp.Symbol("lambda") + 1 + 4 * sp.I * omega)
                * (sp.Symbol("lambda") + 2 + 4 * sp.I * omega))
    require(sp.expand(characteristic - expected) == 0, "horizon residue spectrum changed")

    null = b0.nullspace()
    require(len(null) == 3, "zero residue eigenspace is not three-dimensional")
    v = sp.Matrix.hstack(
        *null,
        (b0 + 4 * sp.I * omega * sp.eye(6)).nullspace()[0],
        (b0 + (1 + 4 * sp.I * omega) * sp.eye(6)).nullspace()[0],
        (b0 + (2 + 4 * sp.I * omega) * sp.eye(6)).nullspace()[0],
    )
    require(repair.cancel(v.det()) != 0, "residue eigenbasis is singular")
    rates = [sp.Integer(0), sp.Integer(0), sp.Integer(0),
             -4 * sp.I * omega, -1 - 4 * sp.I * omega,
             -2 - 4 * sp.I * omega]
    lam = sp.diag(*rates)
    c = (v.inv() * b * v).applyfunc(repair.cancel)
    require((c.subs(rho, 0) - lam).applyfunc(sp.simplify) == sp.zeros(6),
            "eigenbasis does not diagonalize the residue")

    order = 3
    ck = [c.applyfunc(lambda e, n=n: repair.cancel(
        sp.limit(sp.diff(e, rho, n), rho, 0) / sp.factorial(n)))
          for n in range(order + 1)]
    coefficient_matrices = [sp.eye(6)] + [sp.zeros(6) for _ in range(order)]
    resonance_witnesses = []
    for col, exponent in enumerate(rates):
        vectors = [sp.eye(6).col(col)]
        for n in range(1, order + 1):
            rhs = sum((ck[k] * vectors[n - k] for k in range(1, n + 1)),
                      sp.zeros(6, 1))
            pivot = (exponent + n) * sp.eye(6) - lam
            solution, parameters = pivot.gauss_jordan_solve(rhs)
            solution = solution.subs({p: 0 for p in parameters}).applyfunc(repair.cancel)
            residual = (pivot * solution - rhs).applyfunc(sp.simplify)
            require(residual == sp.zeros(6, 1),
                    f"incompatible horizon recurrence column={col} order={n}")
            if parameters:
                resonance_witnesses.append({"column": col, "order": n,
                                            "free_parameters_set_to_zero": len(parameters),
                                            "residual": "0"})
            vectors.append(solution)
        for n in range(1, order + 1):
            coefficient_matrices[n][:, col] = vectors[n]

    physical_heads = [(v * u).applyfunc(repair.cancel) for u in coefficient_matrices]
    return {
        "rho": rho, "omega": omega, "B": b, "B0": b0, "V": v,
        "C": c, "Lambda": lam, "rates": rates, "order": order,
        "physical_heads": physical_heads,
        "resonance_witnesses": resonance_witnesses,
        "characteristic": characteristic,
    }


def cauchy_majorant(data):
    """Prove a rational row-norm majorant on |rho|<=1/2.

    The rectangle used below contains that complex disk.  Expressions are
    factored before exact rectangle evaluation, so every reciprocal is visibly
    separated from zero.  Cauchy's estimate then bounds every Taylor matrix.
    """
    omega, rho = data["omega"], data["rho"]
    environment = {
        omega: CI(RI(Fraction(1, 2), Fraction(3, 4))),
        rho: CI(RI(Fraction(-1, 2), Fraction(1, 2)),
                RI(Fraction(-1, 2), Fraction(1, 2))),
    }
    delta = data["C"] - data["Lambda"]
    row_bounds = []
    for i in range(6):
        total = Fraction(0)
        for j in range(6):
            total += eval_rational_rect(delta[i, j], environment).norm_one_hi()
        row_bounds.append(total)
    majorant = max(row_bounds)
    require(majorant > 0, "zero Cauchy majorant")

    # Select a power-of-two tau with M*tau/(1/2-tau) <= 1/4.  The endpoint
    # epsilon is another factor 16 smaller, so the analytic tail is tiny while
    # all choices remain exact rationals.
    denominator = 16
    while True:
        tau = Fraction(1, denominator)
        sb = majorant * tau / (Fraction(1, 2) - tau)
        if sb <= Fraction(1, 4):
            break
        denominator *= 2
    epsilon = tau / 16
    return {"disk_radius": Fraction(1, 2), "row_bounds": row_bounds,
            "majorant": majorant, "tau": tau, "epsilon": epsilon,
            "s_b_tau": sb}


def interval_heads(data, cell):
    omega = data["omega"]
    environment = {omega: CI(RI(cell[0], cell[1]))}
    blocks = []
    for head in data["physical_heads"]:
        complex_matrix = [[eval_rational_rect(head[i, j], environment)
                           for j in range(6)] for i in range(6)]
        blocks.append(realify_intervals(complex_matrix))
    return blocks


def midpoint_center(data, midpoint: Fraction):
    omega = data["omega"]
    matrix = data["V"].subs(omega, sp.Rational(midpoint.numerator, midpoint.denominator))
    return realify_sympy(matrix)


def frac_json(value: Fraction):
    return {"num": value.numerator, "den": value.denominator,
            "decimal": float(value)}


def float_outward(value: Fraction, direction: float) -> float:
    nearest = float(value)
    return math.nextafter(nearest, direction)


def iv_literal(interval: RI) -> str:
    lo = float_outward(interval.lo, -math.inf)
    hi = float_outward(interval.hi, math.inf)
    return f"iv({lo!r}, {hi!r})"


def rat_literal(value: Fraction) -> str:
    require(-(2**63) < value.numerator < 2**63 and value.denominator < 2**63,
            "Forge Rat literal exceeds i64 constructor")
    return f"rat({value.numerator}, {value.denominator})"


def qmat_builder(name: str, matrix: sp.Matrix) -> list[str]:
    lines = [f"fn {name}() -> QMat {{", f"  let q: QMat = qm_new({matrix.rows}, {matrix.cols});"]
    for i in range(matrix.rows):
        for j in range(matrix.cols):
            value = sp.cancel(matrix[i, j])
            require(value.is_Rational, f"nonrational center entry {value}")
            if value != 0:
                lines.append(f"  q = qm_set(q, {i}, {j}, rat({int(value.p)}, {int(value.q)}));")
    lines.append("  return q;")
    lines.append("}")
    return lines


def render_adapter(data, majorant, cells):
    n = 12
    order = data["order"]
    lines = [
        "// expect: 42", "// backends: c native",
        "// Generated by produce.py; outward interval Phase-3 axial horizon initializer.",
        "import prelude;", "import math/rational;", "import math/interval;",
        "import math/ivmat;", "import math/qmat;", "import math/ivendpoint;", "",
        "fn qzero(n: i64) -> QMat { return qm_new(n, n); }", "",
    ]
    rates = data["rates"]
    for index, cell in enumerate(cells):
        center = midpoint_center(data, (cell[0] + cell[1]) / 2)
        lines += qmat_builder(f"center_{index}", center) + [""]
        blocks = interval_heads(data, cell)
        lines += [f"fn head_{index}() -> IvMat {{",
                  f"  let h: IvMat = ivm_zeros({n}, {n * (order + 1)});"]
        for k, block in enumerate(blocks):
            for i in range(n):
                for j in range(n):
                    q = block[i][j]
                    if q.lo != 0 or q.hi != 0:
                        lines.append(f"  ivm_set(h, {i}, {k*n+j}, {iv_literal(q)});")
        lines += ["  return h;", "}", ""]

        # Realification of the diagonal complex exponent matrix.
        environment = {data["omega"]: CI(RI(cell[0], cell[1]))}
        diagonal = [[CI() for _ in range(6)] for _ in range(6)]
        for i, rate in enumerate(rates):
            diagonal[i][i] = eval_rect(rate, environment)
        phase = realify_intervals(diagonal)
        lines += [f"fn phase_{index}() -> IvMat {{",
                  f"  let s: IvMat = ivm_zeros({n}, {n});"]
        for i in range(n):
            for j in range(n):
                q = phase[i][j]
                if q.lo != 0 or q.hi != 0:
                    lines.append(f"  ivm_set(s, {i}, {j}, {iv_literal(q)});")
        lines += ["  return s;", "}", ""]

    eps, tau = majorant["epsilon"], majorant["tau"]
    sb = majorant["s_b_tau"]
    # A deliberately conservative physical coefficient bound.  The exact
    # recurrence verifier proves the scaled head norm is below this integer;
    # the Cauchy contraction propagates it to every omitted order.
    coefficient_bound = 8.0
    head_dispatch = " else ".join(
        [f"if (which == {i}) {{ head_{i}() }}" for i in range(len(cells) - 1)]
        + [f"{{ head_{len(cells) - 1}() }}"])
    phase_dispatch = " else ".join(
        [f"if (which == {i}) {{ phase_{i}() }}" for i in range(len(cells) - 1)]
        + [f"{{ phase_{len(cells) - 1}() }}"])
    center_dispatch = " else ".join(
        [f"if (which == {i}) {{ center_{i}() }}" for i in range(len(cells) - 1)]
        + [f"{{ center_{len(cells) - 1}() }}"])
    lines += [
        "fn run_cell(which: i64, bad_witness: bool, bad_remainder: bool) -> IvEndpointCert {",
        f"  let h: IvMat = {head_dispatch};",
        f"  let s: IvMat = {phase_dispatch};",
        f"  let iw: QMat = qzero({n});",
        f"  let rw: QMat = qzero({n});",
        "  if (bad_witness) { rw = qm_set(rw, 0, 0, rat(1, 1)); }",
        f"  let center: QMat = {center_dispatch};",
        f"  let sb: Iv = if (bad_remainder) {{ iv_point(3.0) }} else {{ {iv_literal(RI(sb))} }};",
        f"  return ivend_regular(h, s, iw, rw, center, {rat_literal(eps)}, {rat_literal(tau)}, {order},",
        f"    iv_point(2.0), sb, iv_point({coefficient_bound}), iv_point(0.0), true);",
        "}", "",
        "// Public, fail-closed dispatcher consumed by the validated connection rail.",
        "// The returned basis is in the sheared chart",
        "//   x=(P,P',Q,Q',H1,rho F), rho=r-2,",
        "// at the exact rational epsilon recorded in the JSON certificate.",
        "pub fn axial_horizon_initializer(which: i64) -> IvEndpointCert {",
        f"  if (which < 0 || which >= {len(cells)}) {{",
        "    return run_cell(0, true, false);",
        "  }",
        "  return run_cell(which, false, false);",
        "}", "",
        f"pub fn axial_horizon_epsilon() -> Rat {{ return {rat_literal(eps)}; }}", "",
        "// Convert a sheared realified basis to the standard metric chart at",
        "// any strictly positive rho.  The inverse conversion multiplies rows",
        "// 5 and 11 by rho; no Coulomb or constraint projection is performed.",
        "pub fn axial_horizon_to_standard(x: borrow IvMat, rho: Iv) -> IvMat {",
        "  let y: IvMat = ivm_zeros(ivm_rows(x), ivm_cols(x));",
        "  let i: i64 = 0;",
        "  while (i < ivm_rows(x)) {",
        "    let j: i64 = 0;",
        "    while (j < ivm_cols(x)) {",
        "      let a: Iv = ivm_at(x, i, j);",
        "      if (i == 5 || i == 11) { ivm_set(y, i, j, iv_div(a, rho)); }",
        "      else { ivm_set(y, i, j, a); }",
        "      j = j + 1;",
        "    }",
        "    i = i + 1;",
        "  }",
        "  return y;",
        "}", "",
        "pub fn main() -> i64 {",
        "  let pass: i64 = 0;",
        "  let k: i64 = 0;",
        f"  while (k < {len(cells)}) {{",
        "    let c: IvEndpointCert = axial_horizon_initializer(k);",
        f"    if (c.ok && c.n == {n} && c.rank_certified && c.parameter_uniform &&",
        "        c.contraction_q.hi < 1.0 && c.value_tail.hi >= 0.0 &&",
        "        c.derivative_tail.hi >= 0.0) { pass = pass + 1; }",
        "    k = k + 1;",
        "  }",
        "  let wb: IvEndpointCert = run_cell(0, true, false);",
        "  if (!wb.ok && wb.refusal_code == IVEND_WITNESS_INCOMPATIBLE) { pass = pass + 1; }",
        "  let rb: IvEndpointCert = run_cell(0, false, true);",
        "  if (!rb.ok && rb.refusal_code == IVEND_NONCONTRACTIVE) { pass = pass + 1; }",
        f"  if (pass == {len(cells) + 2}) {{ return 42; }}",
        "  return pass;",
        "}", "",
    ]
    return "\n".join(lines), coefficient_bound


def build_certificate():
    repair_cert = json.loads(REPAIR_CERT.read_text())
    metric_heads = json.loads(INFINITY_HEADS.read_text())
    volterra = json.loads(INFINITY_ENVELOPE.read_text())
    repair = load_repair_module()
    data = exact_horizon_data(repair)
    majorant = cauchy_majorant(data)
    cells = [(Fraction(1, 2), Fraction(9, 16)),
             (Fraction(9, 16), Fraction(5, 8)),
             (Fraction(5, 8), Fraction(11, 16)),
             (Fraction(11, 16), Fraction(3, 4))]
    adapter, coefficient_bound = render_adapter(data, majorant, cells)

    # Exact scaled-head norm gate supporting the declared coefficient bound.
    global_environment = {data["omega"]: CI(RI(Fraction(1, 2), Fraction(3, 4)))}
    scaled_head_bounds = []
    for n, head in enumerate(data["physical_heads"]):
        row_max = Fraction(0)
        for i in range(6):
            total = sum(eval_rational_rect(head[i, j], global_environment).norm_one_hi()
                        for j in range(6))
            row_max = max(row_max, total * majorant["tau"] ** n)
        scaled_head_bounds.append(row_max)
    require(max(scaled_head_bounds) < coefficient_bound,
            "declared coefficient majorant is too small")

    infinity = repair_cert["endpoint_bases"]["infinity"]
    carrier_heads = infinity.get("carrier_coefficient_heads", {})
    require(set(carrier_heads) == {"XI0", "XI1", "XI2", "XI3"},
            "four infinity carrier heads not imported")
    metric_branches = metric_heads.get("branches", {})
    require(set(metric_branches) == {"XI0", "XI1", "XI2", "XI3"},
            "four exact infinity metric heads not imported")
    for label, branch in metric_branches.items():
        require(branch["recurrence"]["forced_log_coefficient"] == "0",
                f"forced infinity logarithm reappeared in {label}")
        if label in {"XI2", "XI3"}:
            require(branch["recurrence"]["oscillatory_n1_obstruction"] == "0",
                    f"oscillatory infinity obstruction reappeared in {label}")
    # A declared C_ij,p_ij envelope is a separate mandatory caller obligation.
    residual_envelope = infinity.get("uniform_residual_decay_envelope")

    certificate = {
        "schema": "phase3-black-hole-axial-endpoint-remainder-enclosures-v1",
        "schema_path": str(SCHEMA.relative_to(PHYSICS)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_ENDPOINT_REMAINDER_ENCLOSURES",
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["REDUCED-MODE", "NUMERIC-ENCLOSURE"],
        "lifecycle": "PARTIAL_ENDPOINT_ENCLOSURE",
        "imports": {
            "reconstruction_repair": {"path": str(REPAIR_CERT.relative_to(PHYSICS)),
                                       "sha256": sha256(REPAIR_CERT),
                                       "result_token": repair_cert["result_token"]},
            "reconstruction_source": {"path": str(REPAIR_SOURCE.relative_to(PHYSICS)),
                                       "sha256": sha256(REPAIR_SOURCE)},
            "infinity_metric_heads": {"path": str(INFINITY_HEADS.relative_to(PHYSICS)),
                                      "sha256": sha256(INFINITY_HEADS),
                                      "schema": metric_heads["schema"]},
            "infinity_volterra_envelope": {
                "path": str(INFINITY_ENVELOPE.relative_to(PHYSICS)),
                "sha256": sha256(INFINITY_ENVELOPE),
                "schema": volterra["schema"],
            },
            "forge_ivendpoint": {"path": str(FORGE_ENDPOINT),
                                 "sha256": sha256(FORGE_ENDPOINT),
                                 "landed_commit": "7d745b65e"},
        },
        "declaration": {
            "theory": "linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild M=1 in ingoing EF coordinates",
            "sector": "axial ell=2, exp(+i omega v)",
            "frequency": "real dimensionless omega=M*omega in [1/2,3/4]",
            "horizon_initializer": "rho=r-2 at epsilon; four exact rational omega cells",
            "infinity_initializer": "existence enclosure at R=2^256; practical dispatcher not promoted",
        },
        "horizon": {
            "state_chart": ["P", "P_prime", "Q", "Q_prime", "H1", "rho*F"],
            "regular_singular_identity": "rho*x'=B(rho,omega)*x",
            "residue_characteristic_polynomial": sp.sstr(data["characteristic"]),
            "complex_dimension": 6,
            "realified_dimension": 12,
            "analytic_radius": "at least 2; nearest rho singularity is rho=-2",
            "cauchy_disk_radius": frac_json(majorant["disk_radius"]),
            "cauchy_row_bounds": [frac_json(x) for x in majorant["row_bounds"]],
            "cauchy_majorant": frac_json(majorant["majorant"]),
            "tau": frac_json(majorant["tau"]),
            "epsilon": frac_json(majorant["epsilon"]),
            "S_B_tau": frac_json(majorant["s_b_tau"]),
            "kappa": 2,
            "recurrence_order": data["order"],
            "scaled_head_row_bounds": [frac_json(x) for x in scaled_head_bounds],
            "coefficient_majorant": coefficient_bound,
            "resonance_witnesses": data["resonance_witnesses"],
            "frequency_cells": [[frac_json(a), frac_json(b)] for a, b in cells],
            "initializer": str(ADAPTER.relative_to(PHYSICS)),
            "forge_disposition": "must return 42 under C and native backends",
            "claim": "all six complex constraint-compatible horizon columns and derivatives have outward finite-radius interval enclosures",
        },
        "infinity": {
            "carrier_heads_imported": sorted(carrier_heads),
            "metric_heads_imported": sorted(metric_branches),
            "metric_heads_log_free": True,
            "oscillatory_n1_obstructions": {
                label: metric_branches[label]["recurrence"]["oscillatory_n1_obstruction"]
                for label in ("XI2", "XI3")
            },
            "missing_metric_normal_form_heads": [],
            "uniform_residual_decay_envelope_present": True,
            "volterra_envelope_schema": volterra["schema"],
            "normalization_radius_R": volterra["scope"]["normalization_radius_R"],
            "basis_normalization": volterra["scope"]["basis_normalization"],
            "decay_p_ij": volterra["volterra_kernel"]["decay_p_ij"],
            "constant_C_ij": volterra["volterra_kernel"]["constant_C_ij"],
            "q_infinity": volterra["volterra_kernel"]["q_infinity"],
            "q_less_than_one_quarter": volterra["volterra_kernel"]["q_less_than_one_quarter"],
            "frequency_cells_enclosed": len(volterra["initializer"]["frequency_cells"]),
            "required_contract": "F_N,F_N_prime,p_ij,C_ij and a proved |K_N,ij(r)|<=C_ij*r^-p_ij for every r>=R",
            "existence_enclosure_disposition": "ENCLOSED_AT_PROOF_RADIUS",
            "practical_handoff_disposition": "NOT_STABLE_FOR_IVLINODE",
            "first_remaining_proof_obligation": (
                "replace the R=2^256 proof radius by a cellwise higher-order interval recurrence "
                "at practical R=32/64/128, or validate the phase-normalized correction flow "
                "in z=1/r from z=0 to a practical handoff radius"
            ),
            "bounded_high_order_attempt": (
                "generic exact N=8 was stopped fail-closed: carrier depth about ten is required "
                "and generic rational-omega expression swell OOMs; no new resonance or "
                "mathematical nonintegrability was found"
            ),
            "disposition": "EXISTENCE_ONLY_NOT_DIRECTLY_CONSUMABLE",
        },
        "claim_flags": {
            "horizon_six_column_initializer_certified": True,
            "horizon_subdivision_uniform_certified": True,
            "infinity_six_column_existence_enclosure_certified": True,
            "infinity_six_column_initializer_certified": False,
            "direct_ivlinode_pair_certified": False,
            "global_matching_certified": False,
            "finite_flux_certified": False,
            "scattering_certified": False,
        },
        "does_not_establish": [
            "a practical infinity initializer, horizon-to-infinity connection matrix or channel",
            "finite flux, scattering, poles, stability or CPT positivity",
            "complex-frequency endpoint enclosures",
            "polar parity or frequencies outside the declared real pilot",
        ],
        "stop_condition_disposition": "SHORTFALL",
        "missing_dependency": (
            "practical-radius phase-normalized infinity initializer "
            "(higher-order cellwise recurrence or validated z=1/r inward transfer)"
        ),
        "verification": {
            "producer": "PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_endpoint_remainder_enclosures/produce.py --check",
            "independent": "PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_endpoint_remainder_enclosures/verify.py",
            "mutations": "PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_endpoint_remainder_enclosures/mutations.py",
            "infinity_envelope": "PYTHONPATH=. python3 black_hole_programme/phase3/axial_endpoint_remainder_enclosures/verify_infinity_volterra_envelope.py",
            "tests": "python3 -m unittest black_hole_programme.phase3.axial_endpoint_remainder_enclosures.tests.test_endpoint_enclosures",
            "forge": "forge verify --full --no-cache black_hole_programme/phase3/axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge",
        },
    }
    return certificate, adapter


def write_receipt(certificate):
    receipt = {
        "schema": "phase3-black-hole-axial-endpoint-remainder-enclosures-receipt-v1",
        "result_token": RESULT_TOKEN,
        "input_sha256": {name: value["sha256"] for name, value in certificate["imports"].items()},
        "source_sha256": {"produce.py": sha256(Path(__file__)), "schema.json": sha256(SCHEMA)},
        "tier0": "Python/JSON parse, exact symbolic identities and scoped diff-check",
        "tier1": ["producer byte reproduction", "method-distinct certificate verifier",
                  "recurrence and remainder mutations", "C/native Forge endpoint gate",
                  "independent infinity weighted-Volterra envelope replay"],
        "tier2": (
            "partial affected chain: exact infinity metric heads and Volterra existence "
            "envelope replayed; practical-radius dispatcher remains fail-closed"
        ),
        "tier3": "not run: no paper theorem, flux or scattering promotion",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, adapter = build_certificate()
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(CERTIFICATE.exists() and CERTIFICATE.read_text() == encoded,
                "certificate drift")
        require(ADAPTER.exists() and ADAPTER.read_text() == adapter,
                "Forge adapter drift")
        print("PASS endpoint enclosure certificate reproduces")
    else:
        CERTIFICATE.write_text(encoded)
        ADAPTER.write_text(adapter)
        write_receipt(certificate)
        print("wrote", CERTIFICATE)


if __name__ == "__main__":
    main()
