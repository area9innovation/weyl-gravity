"""Exact/validated code-generation helpers for the v5 affine connection rail.

This module deliberately separates three roles:

* SymPy supplies the exact rational Bach coefficient and its derivatives.
* SciPy supplies *only* moving-frame scouts and their omega sensitivities.
  Every emitted scout is quantized to an exact rational affine frame and is
  subsequently rank/solve certified by Forge.
* exact rational rectangle arithmetic supplies outward Taylor remainders.

No floating-point scout is itself evidence.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    CI,
    RI,
    eval_rational_rect,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    eval_rect,
)


class AffineCodegenError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AffineCodegenError(message)


def realify_symbolic(a: sp.Matrix) -> sp.Matrix:
    """Standard realification ordered Re(n), Im(n)."""
    re = a.applyfunc(lambda x: sp.factor(sp.re(sp.expand_complex(x))))
    im = a.applyfunc(lambda x: sp.factor(sp.im(sp.expand_complex(x))))
    return re.row_join(-im).col_join(im.row_join(re))


def realify_numeric(a: np.ndarray) -> np.ndarray:
    return np.block([[a.real, -a.imag], [a.imag, a.real]])


def _fraction(value: sp.Expr) -> Fraction:
    value = sp.cancel(value)
    require(bool(value.is_Rational), f"non-rational exact value {value}")
    return Fraction(int(value.p), int(value.q))


def _sup_abs(x: RI) -> Fraction:
    return max(abs(x.lo), abs(x.hi))


def _real_imag_boxes(
    expr: sp.Expr,
    env: dict[sp.Symbol, CI],
) -> tuple[RI, RI]:
    z = eval_rational_rect(sp.cancel(expr), env)
    return z.re, z.im


@dataclass(frozen=True)
class TaylorMatrix:
    center: tuple[tuple[Fraction, ...], ...]
    derivative: tuple[tuple[Fraction, ...], ...]
    remainder: tuple[tuple[RI, ...], ...]

    @property
    def rows(self) -> int:
        return len(self.center)

    @property
    def cols(self) -> int:
        return len(self.center[0]) if self.center else 0


@dataclass(frozen=True)
class PreparedTaylorMatrix:
    matrix: sp.Matrix
    bx: sp.Matrix
    bw: sp.Matrix
    bxw: sp.Matrix
    bww: sp.Matrix
    bx_rect: tuple[tuple[tuple, ...], ...]
    bxw_rect: tuple[tuple[tuple, ...], ...]
    bww_rect: tuple[tuple[tuple, ...], ...]
    real_matrix: sp.Matrix
    real_bw: sp.Matrix


def _prepare_rect(expr: sp.Expr) -> tuple:
    numerator, denominator = sp.fraction(sp.cancel(expr))
    coefficient, factors = sp.factor_list(denominator)
    return numerator, coefficient, tuple(factors)


def _prepare_rect_matrix(a: sp.Matrix) -> tuple[tuple[tuple, ...], ...]:
    return tuple(tuple(_prepare_rect(a[i, j]) for j in range(a.cols))
                 for i in range(a.rows))


def _eval_prepared_rect(item: tuple, env: dict[sp.Symbol, CI]) -> CI:
    numerator, coefficient, factors = item
    out = eval_rect(numerator, env) / eval_rect(coefficient, env)
    for factor, multiplicity in factors:
        out = out / eval_rect(factor, env).power(multiplicity)
    return out


def prepare_taylor_matrix(
    matrix: sp.Matrix,
    x: sp.Symbol,
    omega: sp.Symbol,
) -> PreparedTaylorMatrix:
    bx = matrix.applyfunc(lambda z: sp.cancel(sp.diff(z, x)))
    bw = matrix.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    bxw = bx.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    bww = bw.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    return PreparedTaylorMatrix(
        matrix, bx, bw, bxw, bww,
        _prepare_rect_matrix(bx),
        _prepare_rect_matrix(bxw),
        _prepare_rect_matrix(bww),
        realify_symbolic(matrix),
        realify_symbolic(bw),
    )


def coefficient_taylor_model(
    matrix: sp.Matrix,
    x: sp.Symbol,
    omega: sp.Symbol,
    x_cell: tuple[Fraction, Fraction],
    omega_cell: tuple[Fraction, Fraction],
    *,
    prepared: PreparedTaylorMatrix | None = None,
) -> TaylorMatrix:
    """First-order omega Taylor model with a rigorous joint-panel remainder.

    For X=[xc-dx,xc+dx] and W=[wc-dw,wc+dw], each complex coefficient uses

      |B-B0-Bw(w-wc)|
        <= sup|B_x| dx + sup|B_xw| dx dw
           + 1/2 sup|B_ww| dw^2.

    The slightly redundant mixed term is intentionally retained: it matches
    the consumer contract requested for this certificate and is a sound
    outward allowance for moving the omega derivative across the time panel.
    """
    xlo, xhi = x_cell
    wlo, whi = omega_cell
    xc, wc = (xlo + xhi) / 2, (wlo + whi) / 2
    dx, dw = (xhi - xlo) / 2, (whi - wlo) / 2
    subs = {
        x: sp.Rational(xc.numerator, xc.denominator),
        omega: sp.Rational(wc.numerator, wc.denominator),
    }
    env = {
        x: CI(RI(xlo, xhi)),
        omega: CI(RI(wlo, whi)),
    }
    n, m = matrix.rows, matrix.cols
    prepared = prepared or prepare_taylor_matrix(matrix, x, omega)
    c = prepared.real_matrix.subs(subs).applyfunc(sp.cancel)
    d = prepared.real_bw.subs(subs).applyfunc(sp.cancel)

    rem_complex: list[list[tuple[Fraction, Fraction]]] = []
    bx = prepared.bx
    bxw = prepared.bxw
    bww = prepared.bww
    for i in range(n):
        row: list[tuple[Fraction, Fraction]] = []
        for j in range(m):
            txz = _eval_prepared_rect(prepared.bx_rect[i][j], env)
            txwz = _eval_prepared_rect(prepared.bxw_rect[i][j], env)
            twwz = _eval_prepared_rect(prepared.bww_rect[i][j], env)
            tx = txz.re, txz.im
            txw = txwz.re, txwz.im
            tww = twwz.re, twwz.im
            bounds = []
            for k in range(2):
                bounds.append(
                    _sup_abs(tx[k]) * dx
                    + _sup_abs(txw[k]) * dx * dw
                    + _sup_abs(tww[k]) * dw * dw / 2
                )
            row.append((bounds[0], bounds[1]))
        rem_complex.append(row)

    rr = [[RI(Fraction(0)) for _ in range(2 * m)] for _ in range(2 * n)]
    for i in range(n):
        for j in range(m):
            bre, bim = rem_complex[i][j]
            rre, rim = RI(-bre, bre), RI(-bim, bim)
            rr[i][j] = rre
            rr[i][j + m] = rim
            rr[i + n][j] = rim
            rr[i + n][j + m] = rre
    return TaylorMatrix(
        tuple(tuple(_fraction(c[i, j]) for j in range(2 * m))
              for i in range(2 * n)),
        tuple(tuple(_fraction(d[i, j]) for j in range(2 * m))
              for i in range(2 * n)),
        tuple(tuple(rr[i][j] for j in range(2 * m))
              for i in range(2 * n)),
    )


def parameter_taylor_model(
    matrix: sp.Matrix,
    omega: sp.Symbol,
    omega_cell: tuple[Fraction, Fraction],
) -> TaylorMatrix:
    dummy = sp.Symbol("_unused_panel_coordinate", real=True)
    return coefficient_taylor_model(
        matrix,
        dummy,
        omega,
        (Fraction(0), Fraction(0)),
        omega_cell,
    )


def quantize_matrix(a: np.ndarray, bits: int) -> tuple[tuple[Fraction, ...], ...]:
    scale = 1 << bits
    return tuple(
        tuple(Fraction(int(np.rint(float(a[i, j]) * scale)), scale)
              for j in range(a.shape[1]))
        for i in range(a.shape[0])
    )


@dataclass(frozen=True)
class FrameTaylor:
    center: tuple[tuple[Fraction, ...], ...]
    derivative: tuple[tuple[Fraction, ...], ...]


def numerical_frames_with_sensitivity(
    matrix: sp.Matrix,
    x: sp.Symbol,
    omega: sp.Symbol,
    omega_center: Fraction,
    x0: Fraction,
    x1: Fraction,
    resets: int,
    *,
    bits: int = 34,
) -> tuple[FrameTaylor, ...]:
    """Scout F and dF/domega at every reset, then quantize exactly."""
    require(matrix.rows == matrix.cols, "frame coefficient is not square")
    require(resets > 0 and x1 > x0, "bad frame interval")
    n = matrix.rows
    dm = matrix.diff(omega)
    fn = sp.lambdify((x, omega), matrix, "numpy")
    dfn = sp.lambdify((x, omega), dm, "numpy")
    w = float(omega_center)

    def rhs(xx: float, packed: np.ndarray) -> np.ndarray:
        y = packed.view(np.complex128)
        f = y[: n * n].reshape(n, n)
        g = y[n * n :].reshape(n, n)
        b = np.asarray(fn(xx, w), dtype=np.complex128)
        bw = np.asarray(dfn(xx, w), dtype=np.complex128)
        out = np.concatenate(((b @ f).reshape(-1),
                              (bw @ f + b @ g).reshape(-1)))
        return out.view(np.float64)

    init = np.concatenate((
        np.eye(n, dtype=np.complex128).reshape(-1),
        np.zeros((n, n), dtype=np.complex128).reshape(-1),
    )).view(np.float64)
    sol = solve_ivp(
        rhs,
        (float(x0), float(x1)),
        init,
        method="DOP853",
        rtol=2e-13,
        atol=2e-15,
        dense_output=True,
    )
    require(sol.success, f"frame sensitivity integration failed: {sol.message}")
    out = []
    for k in range(resets + 1):
        xx = float(x0 + (x1 - x0) * Fraction(k, resets))
        y = sol.sol(xx).copy().view(np.complex128)
        f = y[: n * n].reshape(n, n)
        g = y[n * n :].reshape(n, n)
        out.append(FrameTaylor(
            quantize_matrix(realify_numeric(f), bits),
            quantize_matrix(realify_numeric(g), bits),
        ))
    return tuple(out)


def block_extract(
    frames: Sequence[FrameTaylor],
    rows: Sequence[int],
    cols: Sequence[int],
) -> tuple[FrameTaylor, ...]:
    return tuple(FrameTaylor(
        tuple(tuple(f.center[i][j] for j in cols) for i in rows),
        tuple(tuple(f.derivative[i][j] for j in cols) for i in rows),
    ) for f in frames)


def taylor_extract(
    model: TaylorMatrix,
    rows: Sequence[int],
    cols: Sequence[int],
) -> TaylorMatrix:
    return TaylorMatrix(
        tuple(tuple(model.center[i][j] for j in cols) for i in rows),
        tuple(tuple(model.derivative[i][j] for j in cols) for i in rows),
        tuple(tuple(model.remainder[i][j] for j in cols) for i in rows),
    )


def rat_literal(x: Fraction) -> str:
    return f'big("{x.numerator}/{x.denominator}")'


def _float_outward(x: Fraction, sign: int) -> float:
    return math.nextafter(float(x), -math.inf if sign < 0 else math.inf)


def iv_literal(x: RI) -> str:
    return f"iv({_float_outward(x.lo,-1)!r},{_float_outward(x.hi,1)!r})"


def rat_expr(expr: sp.Expr, env: dict[sp.Symbol, str]) -> str:
    expr = sp.factor(expr)
    if expr.is_Integer or expr.is_Rational:
        return rat_literal(Fraction(int(expr.p), int(expr.q)))
    if expr.is_Symbol:
        return env[expr]
    if expr.is_Add:
        args = [rat_expr(x, env) for x in expr.args]
        return "(" + "+".join(args) + ")"
    if expr.is_Mul:
        args = [rat_expr(x, env) for x in expr.args]
        return "(" + "*".join(args) + ")"
    if expr.is_Pow and expr.exp.is_Integer:
        n = int(expr.exp)
        base = rat_expr(expr.base, env)
        if n == 0:
            return rat_literal(Fraction(1))
        if n < 0:
            return f"({rat_literal(Fraction(1))}/{rat_expr(expr.base ** (-n), env)})"
        return "(" + "*".join([base] * n) + ")"
    raise AffineCodegenError(f"unsupported rational expression {expr!r}")


def interval_expr(expr: sp.Expr, env: dict[sp.Symbol, str]) -> str:
    expr = sp.factor(expr)
    if expr.is_Integer or expr.is_Rational:
        return f"iv_from_rat({rat_literal(Fraction(int(expr.p), int(expr.q)))})"
    if expr.is_Symbol:
        return env[expr]
    if expr.is_Add:
        args = [interval_expr(x, env) for x in expr.args]
        out = args[0]
        for arg in args[1:]:
            out = f"iv_add({out},{arg})"
        return out
    if expr.is_Mul:
        args = [interval_expr(x, env) for x in expr.args]
        out = args[0]
        for arg in args[1:]:
            out = f"iv_mul({out},{arg})"
        return out
    if expr.is_Pow and expr.exp.is_Integer:
        n = int(expr.exp)
        if n == 0:
            return "iv_point(1.0)"
        base = interval_expr(expr.base, env)
        if n < 0:
            return f"iv_div(iv_point(1.0),{interval_expr(expr.base ** (-n), env)})"
        out = base
        for _ in range(1, n):
            out = f"iv_mul({out},{base})"
        return out
    raise AffineCodegenError(f"unsupported interval expression {expr!r}")


def _real_imag_expr(expr: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    z = sp.expand_complex(expr)
    return sp.factor(sp.re(z)), sp.factor(sp.im(z))


def render_runtime_taylor_builder(
    name: str,
    matrix: sp.Matrix,
    coordinate: sp.Symbol,
    omega: sp.Symbol,
    omega_center: Fraction,
    parameter_halfwidth: Fraction,
) -> list[str]:
    """Emit one compact action-specific Taylor builder used by every panel."""
    n = matrix.rows
    require(matrix.cols == n, "runtime Taylor coefficient is not square")
    bw = matrix.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    bx = matrix.applyfunc(lambda z: sp.cancel(sp.diff(z, coordinate)))
    bxw = bx.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    bww = bw.applyfunc(lambda z: sp.cancel(sp.diff(z, omega)))
    # Rat is an owned arbitrary-precision value in Forge.  Every generated
    # occurrence must clone the two runtime coordinates rather than consuming
    # them on first use.
    qenv = {coordinate: "rat_clone(xc)", omega: "rat_clone(wc)"}
    ienv = {coordinate: "xbox", omega: "wbox"}
    lines = [
        f"fn {name}(xc:Rat,xbox:Iv,xhalf:Rat,cell:borrow IvAffineCell)->IvAffineMat{{",
        f"  let c:QMat=qm_new({2*n},{2*n});let d:QMat=qm_new({2*n},{2*n});",
        f"  let rem:IvMat=ivm_zeros({2*n},{2*n});",
        f"  let wc:Rat={rat_literal(omega_center)};",
        f"  let wlo:Iv=iv_from_rat({rat_literal(omega_center-parameter_halfwidth)});",
        f"  let whi:Iv=iv_from_rat({rat_literal(omega_center+parameter_halfwidth)});",
        "  let wbox:Iv=iv(wlo.lo,whi.hi);",
        "  let dx:Iv=iv_from_rat(xhalf);",
        f"  let dw:Iv=iv_from_rat({rat_literal(parameter_halfwidth)});",
    ]
    for i in range(n):
        for j in range(n):
            cr, ci = _real_imag_expr(matrix[i, j])
            dr, di = _real_imag_expr(bw[i, j])
            tx = _real_imag_expr(bx[i, j])
            txw = _real_imag_expr(bxw[i, j])
            tww = _real_imag_expr(bww[i, j])
            for part, (ce, de, xe, xwe, wwe) in enumerate(
                ((cr, dr, tx[0], txw[0], tww[0]),
                 (ci, di, tx[1], txw[1], tww[1]))
            ):
                if ce != 0:
                    q = rat_expr(ce, qenv)
                    if part == 0:
                        lines += [f"  c=qm_set(c,{i},{j},{q});",
                                  f"  c=qm_set(c,{i+n},{j+n},{q});"]
                    else:
                        lines += [f"  c=qm_set(c,{i+n},{j},{q});",
                                  f"  c=qm_set(c,{i},{j+n},rat(0,1)-({q}));"]
                if de != 0:
                    q = rat_expr(de, qenv)
                    if part == 0:
                        lines += [f"  d=qm_set(d,{i},{j},{q});",
                                  f"  d=qm_set(d,{i+n},{j+n},{q});"]
                    else:
                        lines += [f"  d=qm_set(d,{i+n},{j},{q});",
                                  f"  d=qm_set(d,{i},{j+n},rat(0,1)-({q}));"]
                terms = []
                if xe != 0:
                    terms.append(f"iv_mul(iv_abs({interval_expr(xe, ienv)}),dx)")
                if xwe != 0:
                    terms.append(
                        f"iv_mul(iv_mul(iv_abs({interval_expr(xwe, ienv)}),dx),dw)"
                    )
                if wwe != 0:
                    terms.append(
                        f"iv_mul(iv_mul(iv_abs({interval_expr(wwe, ienv)}),dw),"
                        "iv_mul(dw,iv_point(0.5)))"
                    )
                if terms:
                    z = terms[0]
                    for term in terms[1:]:
                        z = f"iv_add({z},{term})"
                    v = f"gc_sym({z})"
                    if part == 0:
                        lines += [f"  ivm_set(rem,{i},{j},{v});",
                                  f"  ivm_set(rem,{i+n},{j+n},{v});"]
                    else:
                        lines += [f"  ivm_set(rem,{i+n},{j},{v});",
                                  f"  ivm_set(rem,{i},{j+n},{v});"]
    lines += [
        "  let z:IvAffineResult=ivam_taylor1(cell,c,d,rem);",
        "  if(!z.ok){trap();}return ivam_clone(z.value);",
        "}",
        "",
    ]
    return lines


def render_qmat(name: str, a: Sequence[Sequence[Fraction]]) -> list[str]:
    nr, nc = len(a), len(a[0]) if a else 0
    lines = [f"fn {name}() -> QMat {{",
             f"  let a: QMat = qm_new({nr},{nc});"]
    for i, row in enumerate(a):
        for j, value in enumerate(row):
            if value:
                lines.append(
                    f"  a=qm_set(a,{i},{j},{rat_literal(value)});"
                )
    lines += ["  return a;", "}", ""]
    return lines


def render_ivmat(name: str, a: Sequence[Sequence[RI]]) -> list[str]:
    nr, nc = len(a), len(a[0]) if a else 0
    lines = [f"fn {name}() -> IvMat {{",
             f"  let a: IvMat = ivm_zeros({nr},{nc});"]
    for i, row in enumerate(a):
        for j, value in enumerate(row):
            if value.lo or value.hi:
                lines.append(f"  ivm_set(a,{i},{j},{iv_literal(value)});")
    lines += ["  return a;", "}", ""]
    return lines


def render_taylor_matrix(name: str, model: TaylorMatrix) -> list[str]:
    lines: list[str] = []
    lines += render_qmat(f"{name}_center", model.center)
    lines += render_qmat(f"{name}_derivative", model.derivative)
    lines += render_ivmat(f"{name}_remainder", model.remainder)
    lines += [
        f"fn {name}(cell: borrow IvAffineCell) -> IvAffineMat {{",
        f"  let z:IvAffineResult=ivam_taylor1(cell,{name}_center(),",
        f"    {name}_derivative(),{name}_remainder());",
        "  if(!z.ok){trap();}",
        "  return ivam_clone(z.value);",
        "}",
        "",
    ]
    return lines


def render_frame(name: str, frame: FrameTaylor) -> list[str]:
    lines: list[str] = []
    lines += render_qmat(f"{name}_center", frame.center)
    lines += render_qmat(f"{name}_derivative", frame.derivative)
    nr, nc = len(frame.center), len(frame.center[0])
    lines += [
        f"fn {name}(cell: borrow IvAffineCell) -> IvAffineMat {{",
        f"  let z:IvAffineResult=ivam_taylor1(cell,{name}_center(),",
        f"    {name}_derivative(),ivm_zeros({nr},{nc}));",
        "  if(!z.ok){trap();}",
        "  return ivam_clone(z.value);",
        "}",
        "",
    ]
    return lines


def render_dispatch(
    name: str,
    targets: Iterable[str],
    signature: str,
    call_suffix: str,
) -> list[str]:
    targets = tuple(targets)
    require(bool(targets), "empty dispatch")
    expr = " else ".join(
        [f"if(k=={i}){{{target}{call_suffix}}}" for i, target in enumerate(targets[:-1])]
        + [f"{{{targets[-1]}{call_suffix}}}"]
    )
    return [f"fn {name}({signature}) -> IvAffineMat {{ return {expr}; }}", ""]
