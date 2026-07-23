"""Produce the practical R=32 axial infinity transfer certificate.

The proof deliberately avoids a monolithic symbolic inverse.  The normalized
formal frame has the exact block form ``[[C,0],[M,D]]``.  On dyadic
``(z,omega)`` cells we certify the two diagonal solves by rational-centre
Neumann bounds.  Residuals are scaled before interval evaluation, so the
continuous ``z=0`` extension is proved rather than sampled.

The generated Forge adapter integrates the resulting twelve-real-dimensional
correction flow with ``math/ivlinode``.  Oscillatory cross-rate phases are
bounded by the unit circle and are never evaluated at ``z=0``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    CI,
    RI,
    CELLS as OLD_OMEGA_CELLS,
    exact_blocks,
    eval_rational_rect,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import eval_rect
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_metric_heads import (
    _parse,
    build_data as build_head_data,
)


HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
FORGE = Path("/home/alstrup/area9/tango/forge")
OUTPUT = HERE / "certificate.json"
ADAPTER = HERE / "validated_infinity_transfer.forge"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipt.json"
RESULT_TOKEN = "BH_PHASE3_AXIAL_INFINITY_PRACTICAL_TRANSFER_V1"
R_INIT = 32
Z_END = Fraction(1, R_INIT)
# The formal lower lift is sensitive to omega even though its carrier/kernel
# diagonal blocks are well conditioned.  Narrow exact cells keep the inverse
# proof honest without pointwise shooting.
OMEGA_CELLS = tuple(
    (Fraction(128 + i, 256), Fraction(129 + i, 256)) for i in range(64)
)
Z_CELLS = tuple(
    (Fraction(i, 1024), Fraction(i + 1, 1024)) for i in range(32)
)
LABELS = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")
RAW_CARRIER = (3, 3, 3, 2)


class TransferError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TransferError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ftext(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def dyadic_upper(value: Fraction, bits: int = 96) -> Fraction:
    """Small, exact, outward rational serialization for a nonnegative bound."""
    require(value >= 0, "dyadic upper bound requires a nonnegative value")
    scale = 1 << bits
    numerator = (value.numerator * scale + value.denominator - 1) // value.denominator
    return Fraction(numerator, scale)


def upper_float(value: Fraction) -> float:
    require(value >= 0, "upper float requires a nonnegative rational")
    x = float(value)
    require(math.isfinite(x), "rational bound overflows f64")
    return math.nextafter(x, math.inf)


def iv_literal(value: CI) -> str:
    return (
        f"CI_NOT_USED"  # complex boxes are realified before Forge emission
    )


def ri_literal(value: RI) -> str:
    lo = math.nextafter(float(value.lo), -math.inf)
    hi = math.nextafter(float(value.hi), math.inf)
    return f"iv({lo!r}, {hi!r})"


def rat_literal(value: Fraction) -> str:
    return f'big("{ftext(value)}")'


def ci_add(a: CI, b: CI) -> CI:
    return a + b


def ci_abs(a: CI) -> Fraction:
    return a.norm_one_hi()


def ci_hull_radius(a: CI, radius: Fraction) -> CI:
    return CI(RI(a.re.lo - radius, a.re.hi + radius),
              RI(a.im.lo - radius, a.im.hi + radius))


def point_ci(expr: sp.Expr) -> CI:
    value = sp.expand_complex(expr)
    re = sp.re(value)
    im = sp.im(value)
    require(bool(re.is_Rational) and bool(im.is_Rational), f"non-rational centre {expr}")
    return CI(Fraction(int(re.p), int(re.q)), Fraction(int(im.p), int(im.q)))


def mat_eval(matrix: sp.Matrix, env: dict[sp.Symbol, CI]) -> list[list[CI]]:
    return [[eval_rational_rect(sp.cancel(matrix[i, j]), env)
            for j in range(matrix.cols)] for i in range(matrix.rows)]


def prepare_expr(expr: sp.Expr) -> tuple[sp.Expr, sp.Expr, tuple[tuple[sp.Expr, int], ...]]:
    numerator, denominator = sp.fraction(sp.cancel(expr))
    coefficient, factors = sp.factor_list(denominator)
    return numerator, coefficient, tuple(factors)


def mat_prepare(matrix: sp.Matrix):
    return [[prepare_expr(matrix[i, j]) for j in range(matrix.cols)]
            for i in range(matrix.rows)]


def eval_prepared(item, env: dict[sp.Symbol, CI]) -> CI:
    numerator, coefficient, factors = item
    out = eval_rect(numerator, env) / eval_rect(coefficient, env)
    for factor, multiplicity in factors:
        out = out / eval_rect(factor, env).power(multiplicity)
    return out


def mat_eval_prepared(matrix, env: dict[sp.Symbol, CI]) -> list[list[CI]]:
    return [[eval_prepared(item, env) for item in row] for row in matrix]


def mat_point(matrix: sp.Matrix) -> list[list[CI]]:
    return [[point_ci(matrix[i, j]) for j in range(matrix.cols)]
            for i in range(matrix.rows)]


def mat_sub(a: list[list[CI]], b: list[list[CI]]) -> list[list[CI]]:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))]
            for i in range(len(a))]


def mat_mul(a: list[list[CI]], b: list[list[CI]]) -> list[list[CI]]:
    rows, inner, cols = len(a), len(b), len(b[0])
    require(len(a[0]) == inner, "interval matrix shape mismatch")
    return [[sum((a[i][k] * b[k][j] for k in range(inner)), CI())
             for j in range(cols)] for i in range(rows)]


def mat_inf_norm(a: list[list[CI]]) -> Fraction:
    return max((sum((ci_abs(x) for x in row), Fraction(0)) for row in a),
               default=Fraction(0))


def neumann_factor(
    matrix: sp.Matrix,
    matrix_box: list[list[CI]],
    centre_subs: dict[sp.Symbol, sp.Rational],
) -> tuple[list[list[CI]], Fraction]:
    centre = matrix.subs(centre_subs).applyfunc(sp.cancel)
    inverse = centre.inv(method="DM")
    inverse_point = mat_point(inverse)
    centre_point = mat_point(centre)
    defect = mat_mul(inverse_point, mat_sub(matrix_box, centre_point))
    q = mat_inf_norm(defect)
    require(q < 1, f"Neumann inverse failed: q={q}")
    return inverse_point, q


def neumann_apply(
    inverse_point: list[list[CI]], q: Fraction, rhs_box: list[list[CI]]
) -> tuple[list[list[CI]], Fraction]:
    """Enclose the factored matrix inverse applied to an interval RHS."""
    y = mat_mul(inverse_point, rhs_box)
    ynorm = mat_inf_norm(y)
    radius = q * ynorm / (1 - q)
    return [[ci_hull_radius(x, radius) for x in row] for row in y], radius


def scaled_exact_expressions() -> dict:
    blocks = exact_blocks()
    z, omega, r = blocks["z"], blocks["omega"], blocks["r"]
    flow = blocks["system"]["flow6"].subs(r, 1 / z)
    basis = sp.Matrix.hstack(*(column for _, column in blocks["columns"]))
    C, M, D = basis[:4, :4], basis[4:, :4], basis[4:, 4:]
    # Reduce one column at a time.  A monolithic 6x6 symbolic residual/inverse
    # is both unnecessary and dramatically more expensive.
    rc_columns = []
    rm = []
    for j in range(4):
        column = blocks["columns"][j][1]
        rate, power = blocks["rates"][j], blocks["powers"][j]
        residual = (
            column.applyfunc(lambda value: -z**2 * sp.diff(value, z))
            + (rate + power * z) * column
            - flow * column
        )
        rc_columns.append(residual[:4, :].applyfunc(
            lambda value: sp.cancel(value / z**6)
        ))
        raw = RAW_CARRIER[j]
        rm.append(residual[4:, :].applyfunc(
            lambda value, q=raw: sp.cancel(value / z**q)
        ))
    rc6 = sp.Matrix.hstack(*rc_columns)
    rk_columns = []
    for j in range(4, 6):
        column = blocks["columns"][j][1]
        rate, power = blocks["rates"][j], blocks["powers"][j]
        residual = (
            column.applyfunc(lambda value: -z**2 * sp.diff(value, z))
            + (rate + power * z) * column
            - flow * column
        )
        rk_columns.append(residual[4:, :].applyfunc(
            lambda value: sp.cancel(value / z**5)
        ))
    rk5 = sp.Matrix.hstack(*rk_columns)
    # The oscillatory metric columns must contain the derivative-forced F4.
    heads = build_head_data()["branches"]
    for label in ("XI2", "XI3"):
        h = heads[label]
        hpower = _parse(h["H1"]["power"], omega)
        h3 = _parse(h["H1"]["coefficients_through_inverse_order_3"][3], omega)
        f = [_parse(x, omega) for x in
             h["F_equals_dH1_dr"]["coefficients_through_inverse_order_3"]]
        require(len(f) == 5 and sp.cancel(f[4] - (hpower - 3) * h3) == 0,
                f"{label} derivative-forced F4 is absent")
    return {
        "blocks": blocks,
        "z": z,
        "omega": omega,
        "basis": basis,
        "C": C,
        "M": M,
        "D": D,
        "rc6": rc6,
        "rm": rm,
        "rk5": rk5,
        "prepared": {
            "basis": mat_prepare(basis),
            "C": mat_prepare(C),
            "D": mat_prepare(D),
            "rc6": mat_prepare(rc6),
            "rm": [mat_prepare(x) for x in rm],
            "mz": [mat_prepare(M.applyfunc(
                lambda value, e=6 - RAW_CARRIER[j]: sp.cancel(value * z**e)
            )) for j in range(4)],
            "rk5": mat_prepare(rk5),
        },
    }


def bound_cell(data: dict, omega_cell, z_cell) -> dict:
    z, omega = data["z"], data["omega"]
    wlo, whi = omega_cell
    zlo, zhi = z_cell
    wc, zc = (wlo + whi) / 2, (zlo + zhi) / 2
    env = {omega: CI(RI(wlo, whi)), z: CI(RI(zlo, zhi))}
    subs = {omega: sp.Rational(wc.numerator, wc.denominator),
            z: sp.Rational(zc.numerator, zc.denominator)}

    prepared = data["prepared"]
    c_box = mat_eval_prepared(prepared["C"], env)
    d_box = mat_eval_prepared(prepared["D"], env)
    cinv, qc = neumann_factor(data["C"], c_box, subs)
    dinv, qd = neumann_factor(data["D"], d_box, subs)
    rc_box = mat_eval_prepared(prepared["rc6"], env)
    top6, top_radius = neumann_apply(cinv, qc, rc_box)

    bottom_bounds: list[list[CI]] = [[CI() for _ in range(4)] for _ in range(2)]
    lower_radii = []
    for j, raw in enumerate(RAW_CARRIER):
        rm_box = mat_eval_prepared(prepared["rm"][j], env)
        # M has poles in the oscillatory columns.  Multiplication by
        # z^(6-raw) is formed symbolically first and is regular at z=0.
        forcing = mat_mul(mat_eval_prepared(prepared["mz"][j], env),
                          [[top6[i][j]] for i in range(4)])
        rhs = [[rm_box[i][0] - forcing[i][0]] for i in range(2)]
        solved, rad = neumann_apply(dinv, qd, rhs)
        lower_radii.append(rad)
        for i in range(2):
            bottom_bounds[i][j] = solved[i][0]

    kernel_box = mat_eval_prepared(prepared["rk5"], env)
    kernel5, kernel_radius = neumann_apply(dinv, qd, kernel_box)

    powers = [[99 for _ in range(6)] for _ in range(6)]
    constants = [[Fraction(0) for _ in range(6)] for _ in range(6)]
    real_powers = [0, -1, 0, -1, 0, 1]
    rates = [0, 0, -2, -2, 0, -2]
    for i in range(4):
        for j in range(4):
            powers[i][j] = 6 + real_powers[i] - real_powers[j]
            constants[i][j] = ci_abs(top6[i][j]) * Fraction(R_INIT) ** (
                real_powers[i] - real_powers[j]
            )
    for i in range(2):
        for j, raw in enumerate(RAW_CARRIER):
            powers[i + 4][j] = raw + real_powers[i + 4] - real_powers[j]
            constants[i + 4][j] = ci_abs(bottom_bounds[i][j]) * Fraction(R_INIT) ** (
                real_powers[i + 4] - real_powers[j]
            )
        for j in range(2):
            powers[i + 4][j + 4] = 5 + real_powers[i + 4] - real_powers[j + 4]
            constants[i + 4][j + 4] = ci_abs(kernel5[i][j]) * Fraction(R_INIT) ** (
                real_powers[i + 4] - real_powers[j + 4]
            )

    cross_min = min(
        powers[i][j] for i in range(6) for j in range(6)
        if powers[i][j] < 99 and rates[i] != rates[j]
    )
    same_min = min(
        powers[i][j] for i in range(6) for j in range(6)
        if powers[i][j] < 99 and rates[i] == rates[j]
    )
    require(cross_min >= 3, f"cross-rate decay fell to {cross_min}")
    require(same_min >= 3, f"same-rate decay fell to {same_min}")
    return {
        "omega_cell": [ftext(wlo), ftext(whi)],
        "z_cell": [ftext(zlo), ftext(zhi)],
        "powers": powers,
        "constants": [[ftext(dyadic_upper(x)) for x in row] for row in constants],
        "cross_rate_minimum_p": cross_min,
        "same_rate_minimum_p": same_min,
        "neumann": {
            "carrier_q": ftext(dyadic_upper(qc)),
            "kernel_q_max": ftext(dyadic_upper(qd)),
            "carrier_solution_radius": ftext(dyadic_upper(top_radius)),
            "lower_solution_radius_max": ftext(dyadic_upper(max(lower_radii + [kernel_radius]))),
        },
    }


def build_data_from(data: dict, cells: list[dict]) -> dict:
    imports = {
        "reconstruction_certificate": HERE.parent / "axial_complete_reconstruction_repair/certificate.json",
        "reconstruction_source": HERE.parent / "axial_complete_reconstruction_repair/produce.py",
        "endpoint_certificate": HERE.parent / "axial_endpoint_remainder_enclosures/certificate.json",
        "infinity_heads": HERE.parent / "axial_endpoint_remainder_enclosures/infinity-metric-heads.json",
        "infinity_envelope": HERE.parent / "axial_endpoint_remainder_enclosures/infinity-volterra-envelope.json",
        "forge_ivlinode": FORGE / "lib/math/ivlinode.forge",
        "forge_ivendpoint": FORGE / "lib/math/ivendpoint.forge",
    }
    return {
        "schema": "phase3-axial-infinity-practical-transfer-v1",
        "result_token": RESULT_TOKEN,
        "scope": {
            "background": "Schwarzschild M=1 in ingoing EF coordinates",
            "sector": "axial ell=2",
            "frequency": "real omega in [1/2,3/4] on four rational cells",
            "z_interval": "[0,1/32]",
            "state_order": "Re(P,P_prime,Q,Q_prime,H1,F),Im(P,P_prime,Q,Q_prime,H1,F)",
        },
        "imports": {
            "reconstruction_commit": "d5d5d6de648795203604d62ce7bc4f4ce6fea510",
            "endpoint_commit": "ed3d95901",
            "files": {
                key: {"path": str(path.relative_to(PHYSICS)) if path.is_relative_to(PHYSICS) else str(path),
                      "sha256": sha256(path)}
                for key, path in imports.items()
            },
        },
        "normalization": (
            "each phase is exp(rate*(r-32))*(r/32)^power, hence the formal frame equals B at R=32"
        ),
        "structural_proof": {
            "formal_frame": "B=[[C,0],[M,D]]",
            "carrier_scaled_residual_order": 6,
            "forced_lower_scaled_residual_orders": list(RAW_CARRIER),
            "kernel_scaled_residual_order": 5,
            "XI2_XI3_derivative_consistency": "F4=(hpower-3)*H1_3",
            "z_flow": "dZ/dz=z^-2*K(1/z,omega)*Z",
            "z_zero_extension": "all entries are zero; same-rate and cross-rate p are at least 3",
        },
        "interval_cells": cells,
        "forge_adapter": "validated_infinity_transfer.forge",
        "claim": {
            "statement": (
                "The phase-normalized correction generator has a continuous zero extension at z=0 and an exact outward interval extension on z in [0,1/32]."
            ),
            "lifecycle": "NUMERIC-ENCLOSURE",
            "does_not_establish": [
                "horizon-to-infinity matching",
                "Lee-Wald current or flux",
                "scattering, poles, stability or CPT",
            ],
        },
        "claim_flags": {
            "continuous_z_zero_extension_certified": True,
            "full_rank_R32_initializer_certified": True,
            "direct_ivlinode_compatible": True,
            "global_matching_certified": False,
            "flux_certified": False,
        },
    }


def build_data() -> dict:
    data = scaled_exact_expressions()
    cells = [bound_cell(data, wc, zc) for wc in OMEGA_CELLS for zc in Z_CELLS]
    return build_data_from(data, cells)


def compact_cell(cell: dict) -> dict:
    """Outward-round a fully exact cell to compact 96-bit dyadic bounds."""
    out = dict(cell)
    out["constants"] = [
        [ftext(dyadic_upper(Fraction(x))) for x in row]
        for row in cell["constants"]
    ]
    n = dict(cell["neumann"])
    for key in n:
        n[key] = ftext(dyadic_upper(Fraction(n[key])))
    out["neumann"] = n
    return out


def ci_matrix_realify(matrix: list[list[CI]]) -> list[list[RI]]:
    rows, cols = len(matrix), len(matrix[0])
    out = [[RI(0) for _ in range(2 * cols)] for _ in range(2 * rows)]
    for i in range(rows):
        for j in range(cols):
            x = matrix[i][j]
            out[i][j] = x.re
            out[i][j + cols] = -x.im
            out[i + rows][j] = x.im
            out[i + rows][j + cols] = x.re
    return out


def qmat_realify(matrix: sp.Matrix) -> list[list[Fraction]]:
    rows, cols = matrix.rows, matrix.cols
    out = [[Fraction(0) for _ in range(2 * cols)] for _ in range(2 * rows)]
    for i in range(rows):
        for j in range(cols):
            x = sp.expand_complex(matrix[i, j])
            re, im = sp.re(x), sp.im(x)
            require(bool(re.is_Rational) and bool(im.is_Rational), "non-rational QMat centre")
            qr = Fraction(int(re.p), int(re.q))
            qi = Fraction(int(im.p), int(im.q))
            out[i][j] = qr
            out[i][j + cols] = -qi
            out[i + rows][j] = qi
            out[i + rows][j + cols] = qr
    return out


def render_ivmat(name: str, matrix: list[list[RI]]) -> list[str]:
    lines = [f"fn {name}() -> IvMat {{",
             f"  let a: IvMat = ivm_zeros({len(matrix)}, {len(matrix[0])});"]
    for i, row in enumerate(matrix):
        for j, x in enumerate(row):
            if x.lo != 0 or x.hi != 0:
                lines.append(f"  ivm_set(a, {i}, {j}, {ri_literal(x)});")
    lines += ["  return a;", "}", ""]
    return lines


def render_qmat(name: str, matrix: list[list[Fraction]]) -> list[str]:
    lines = [f"fn {name}() -> QMat {{",
             f"  let a: QMat = qm_new({len(matrix)}, {len(matrix[0])});"]
    for i, row in enumerate(matrix):
        for j, x in enumerate(row):
            if x:
                lines.append(f"  a = qm_set(a, {i}, {j}, {rat_literal(x)});")
    lines += ["  return a;", "}", ""]
    return lines


def render_adapter(certificate: dict, exact: dict) -> str:
    """Render the direct ``IvEndpointCert``/``ivlinode`` consumer."""
    z, omega = exact["z"], exact["omega"]
    prepared = exact["prepared"]
    lines = [
        "// Generated by axial_infinity_practical_transfer/produce.py.",
        "// NUMERIC-ENCLOSURE only; no matching, flux, pole or stability claim.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivlinode;",
        "import math/ivendpoint;",
        "import ds/vec;",
        "import text/parse;",
        "",
        "fn big(s: string) -> Rat {",
        "  return match (parse<Rat>(bytes(s), 0)) { ok(r) => r, err(_) => trap() };",
        "}",
        "",
        "fn zpow(x: Iv, n: i64) -> Iv {",
        "  let y: Iv = iv_point(1.0);",
        "  let k: i64 = 0;",
        "  while (k < n) { y = iv_mul(y, x); k = k + 1; }",
        "  return y;",
        "}",
        "",
        "fn symmetric_scaled(c: f64, z: Iv, e: i64) -> Iv {",
        "  let zp: Iv = zpow(z, e);",
        "  let m: Iv = iv_mul(iv(0.0, c), zp);",
        "  return iv(0.0 - m.hi, m.hi);",
        "}",
        "",
    ]

    # Aggregate exact rational coefficient bounds over omega for each z slab.
    by_z = []
    nz = len(Z_CELLS)
    for zi in range(nz):
        group = [certificate["interval_cells"][oi * nz + zi]
                 for oi in range(len(OMEGA_CELLS))]
        powers = group[0]["powers"]
        constants = [[max(Fraction(c["constants"][i][j]) for c in group)
                      for j in range(6)] for i in range(6)]
        by_z.append((powers, constants))
        lines += [f"fn coeff_{zi}(z: Iv) -> IvMat {{",
                  "  let a: IvMat = ivm_zeros(12, 12);",
                  "  if (z.lo == 0.0 && z.hi == 0.0) { return a; }"]
        for i in range(6):
            for j in range(6):
                p = powers[i][j]
                if p >= 99 or constants[i][j] == 0:
                    continue
                e = p - 2
                c = upper_float(constants[i][j])
                lines += [
                    f"  let x_{i}_{j}: Iv = symmetric_scaled({c!r}, z, {e});",
                    f"  ivm_set(a, {i}, {j}, x_{i}_{j});",
                    f"  ivm_set(a, {i}, {j + 6}, x_{i}_{j});",
                    f"  ivm_set(a, {i + 6}, {j}, x_{i}_{j});",
                    f"  ivm_set(a, {i + 6}, {j + 6}, x_{i}_{j});",
                ]
        lines += ["  return a;", "}", ""]

    lines += [
        "fn matrices_overlap(a: borrow IvMat, b: borrow IvMat) -> bool {",
        "  let i: i64 = 0;",
        "  while (i < ivm_rows(a)) {",
        "    let j: i64 = 0;",
        "    while (j < ivm_cols(a)) {",
        "      match (iv_meet(ivm_at(a,i,j), ivm_at(b,i,j))) {",
        "        some(_) => {}, none => { return false; },",
        "      }",
        "      j = j + 1;",
        "    }",
        "    i = i + 1;",
        "  }",
        "  return true;",
        "}",
        "",
        "fn correction_flow(steps: i64) -> IvMat {",
        "  let total: IvMat = ivm_identity(12);",
    ]
    for zi, (lo, hi) in enumerate(Z_CELLS):
        lines += [
            f"  let f_{zi}: IvLinFlow = ivlin_fundamental(coeff_{zi}, 12, {float(lo)!r}, {float(hi)!r}, steps, 10, true, true);",
            f"  if (!f_{zi}.ok) {{ return ivm_zeros(12,12); }}",
            f"  total = ivm_mul(f_{zi}.endpoint, total);",
        ]
    lines += ["  return total;", "}", ""]

    # Formal endpoint boxes, exact rational centres and physical radial flow.
    basis = exact["basis"]
    r = exact["blocks"]["r"]
    flow = exact["blocks"]["system"]["flow6"].subs(r, R_INIT)
    for oi, (lo, hi) in enumerate(OMEGA_CELLS):
        env = {omega: CI(RI(lo, hi)), z: CI(RI(Z_END))}
        bbox = ci_matrix_realify(mat_eval_prepared(prepared["basis"], env))
        abox = ci_matrix_realify(mat_eval(flow, {omega: CI(RI(lo, hi))}))
        mid = (lo + hi) / 2
        carrier_center = qmat_realify(basis[:4, :4].subs({
            z: sp.Rational(1, R_INIT),
            omega: sp.Rational(mid.numerator, mid.denominator),
        }))
        kernel_center = qmat_realify(basis[4:, 4:].subs({
            z: sp.Rational(1, R_INIT),
            omega: sp.Rational(mid.numerator, mid.denominator),
        }))
        lines += render_ivmat(f"formal_{oi}", bbox)
        lines += render_ivmat(f"radial_flow_{oi}", abox)
        lines += render_qmat(f"carrier_center_{oi}", carrier_center)
        lines += render_qmat(f"kernel_center_{oi}", kernel_center)

    formal_dispatch = " else ".join(
        [f"if (which == {i}) {{ formal_{i}() }}" for i in range(len(OMEGA_CELLS)-1)]
        + [f"{{ formal_{len(OMEGA_CELLS)-1}() }}"]
    )
    flow_dispatch = " else ".join(
        [f"if (which == {i}) {{ radial_flow_{i}() }}" for i in range(len(OMEGA_CELLS)-1)]
        + [f"{{ radial_flow_{len(OMEGA_CELLS)-1}() }}"]
    )
    carrier_center_dispatch = " else ".join(
        [f"if (which == {i}) {{ carrier_center_{i}() }}" for i in range(len(OMEGA_CELLS)-1)]
        + [f"{{ carrier_center_{len(OMEGA_CELLS)-1}() }}"]
    )
    kernel_center_dispatch = " else ".join(
        [f"if (which == {i}) {{ kernel_center_{i}() }}" for i in range(len(OMEGA_CELLS)-1)]
        + [f"{{ kernel_center_{len(OMEGA_CELLS)-1}() }}"]
    )
    lines += [
        "fn exact_unit(n: i64, j: i64) -> Vec<Rat> {",
        "  let v: Vec<Rat> = vec_new<Rat>(system_allocator(), usize(n));",
        "  let i: i64 = 0;",
        "  while (i < n) {",
        "    if (i == j) { vec_push<Rat>(v, rat(1,1)); } else { vec_push<Rat>(v, rat(0,1)); }",
        "    i = i + 1;",
        "  }",
        "  return v;",
        "}",
        "",
        "fn rank_box(center: borrow QMat, enclosure: borrow IvMat, n: i64) -> bool {",
        "  let j: i64 = 0;",
        "  while (j < n) {",
        "    let bq: Vec<Rat> = exact_unit(n,j);",
        "    let bi: IvVec = ivv_from_rat_vec(bq);",
        "    match (ivm_solve_certified(center,bq,enclosure,bi)) {",
        "      some(c) => {",
        "        let unique: bool = c.unique;",
        "        drop(c); drop(bi); drop(bq);",
        "        if (!unique) { return false; }",
        "      },",
        "      none => { drop(bi); drop(bq); return false; },",
        "    }",
        "    j = j + 1;",
        "  }",
        "  return true;",
        "}",
        "",
        "fn carrier_block(a: borrow IvMat) -> IvMat {",
        "  let b: IvMat = ivm_zeros(8,8);",
        "  let i: i64 = 0;",
        "  while (i < 8) {",
        "    let si: i64 = if (i < 4) { i } else { i + 2 };",
        "    let j: i64 = 0;",
        "    while (j < 8) {",
        "      let sj: i64 = if (j < 4) { j } else { j + 2 };",
        "      ivm_set(b,i,j,ivm_at(a,si,sj));",
        "      j = j + 1;",
        "    }",
        "    i = i + 1;",
        "  }",
        "  return b;",
        "}",
        "",
        "fn kernel_block(a: borrow IvMat) -> IvMat {",
        "  let b: IvMat = ivm_zeros(4,4);",
        "  let i: i64 = 0;",
        "  while (i < 4) {",
        "    let si: i64 = if (i < 2) { i + 4 } else { i + 8 };",
        "    let j: i64 = 0;",
        "    while (j < 4) {",
        "      let sj: i64 = if (j < 2) { j + 4 } else { j + 8 };",
        "      ivm_set(b,i,j,ivm_at(a,si,sj));",
        "      j = j + 1;",
        "    }",
        "    i = i + 1;",
        "  }",
        "  return b;",
        "}",
        "",
        "fn make_cert(which: i64, correction: borrow IvMat) -> IvEndpointCert {",
        f"  if (which < 0 || which >= {len(OMEGA_CELLS)}) {{",
        "    return new IvEndpointCert(false, IVEND_BAD_ARGUMENT, 12, ivm_zeros(12,12), ivm_zeros(12,12), iv_point(0.0), iv_point(0.0), iv_point(0.0), false, false, true);",
        "  }",
        f"  let f: IvMat = {formal_dispatch};",
        f"  let a: IvMat = {flow_dispatch};",
        f"  let cc: QMat = {carrier_center_dispatch};",
        f"  let kc: QMat = {kernel_center_dispatch};",
        "  let value: IvMat = ivm_mul(f, correction);",
        "  let derivative: IvMat = ivm_mul(a, value);",
        "  let cb: IvMat = carrier_block(value);",
        "  let kb: IvMat = kernel_block(value);",
        "  let rank: bool = rank_box(cc, cb, 8) && rank_box(kc, kb, 4);",
        "  if (!rank) {",
        "    return new IvEndpointCert(false, IVEND_RANK_UNCERTIFIED, 12, value, derivative, iv_point(0.0), iv_point(0.0), iv_point(0.0), false, true, true);",
        "  }",
        "  return new IvEndpointCert(true, IVEND_OK, 12, value, derivative, iv_point(0.0), iv_point(0.0), iv_point(0.0), true, true, true);",
        "}",
        "",
        "pub fn axial_infinity_initializer(which: i64) -> IvEndpointCert {",
        "  let correction: IvMat = correction_flow(4);",
        "  return make_cert(which, correction);",
        "}",
        "",
        "pub fn main() -> i64 {",
        "  let fine: IvMat = correction_flow(4);",
        "  let coarse: IvMat = correction_flow(2);",
        "  if (!matrices_overlap(fine,coarse)) { return 1; }",
        "  let pass: i64 = 0;",
        "  let k: i64 = 0;",
        f"  while (k < {len(OMEGA_CELLS)}) {{",
        "    let c: IvEndpointCert = make_cert(k,fine);",
        "    if (c.ok && c.rank_certified && c.parameter_uniform && c.n == 12) { pass = pass + 1; }",
        "    drop(c);",
        "    k = k + 1;",
        "  }",
        "  drop(coarse); drop(fine);",
        f"  if (pass == {len(OMEGA_CELLS)}) {{ return 42; }}",
        "  return pass + 1;",
        "}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reuse-cells", action="store_true",
                        help="reuse a prior exact cell run and only compact/render it")
    args = parser.parse_args()
    exact = scaled_exact_expressions()
    if args.reuse_cells:
        require(OUTPUT.exists(), "--reuse-cells requires an existing exact certificate")
        prior = json.loads(OUTPUT.read_text())
        require(len(prior.get("interval_cells", [])) == len(OMEGA_CELLS) * len(Z_CELLS),
                "prior exact subdivision does not match")
        cells = [compact_cell(c) for c in prior["interval_cells"]]
    else:
        cells = [bound_cell(exact, wc, zc) for wc in OMEGA_CELLS for zc in Z_CELLS]
    data = build_data_from(exact, cells)
    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    adapter = render_adapter(data, exact)
    if args.check:
        require(OUTPUT.exists() and OUTPUT.read_text() == encoded, "certificate drift")
        require(ADAPTER.exists() and ADAPTER.read_text() == adapter, "Forge adapter drift")
        print("PASS practical infinity coefficient certificate reproduces")
    else:
        OUTPUT.write_text(encoded)
        ADAPTER.write_text(adapter)
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
