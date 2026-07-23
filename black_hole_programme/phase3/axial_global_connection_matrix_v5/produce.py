"""Generate the separated-block validated global-connection Forge rail.

The generated program consumes the two certified endpoint initializers and
the repaired six-state radial system.  It never flattens the physical flow
into one uncontrolled shooting matrix: carrier and Einstein-kernel factors
are enclosed separately, while the forced lower block is accumulated from
the retained local Peano--Baker factors by the block variation-of-constants
recurrence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import sympy as sp
import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
FORGE = Path("/home/alstrup/area9/tango/forge")
PRACTICAL = HERE.parent / "axial_infinity_practical_transfer/validated_infinity_transfer.forge"
HORIZON = HERE.parent / "axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge"
OUTPUT = HERE / "certificate.json"
ADAPTER = HERE / "validated_global_connection.forge"
RESULT_TOKEN = "BH_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5"
OMEGA_CELLS = tuple((Fraction(128+i, 256), Fraction(129+i, 256)) for i in range(64))
DIAGNOSTIC_CELL = OMEGA_CELLS[0]
RESET_DEN = 64
RECON_CERT = HERE.parent / "axial_complete_reconstruction_repair/certificate.json"


class BuildError(RuntimeError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise BuildError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outward_fraction(x: Fraction) -> tuple[float, float]:
    y = float(x)
    return math.nextafter(y, -math.inf), math.nextafter(y, math.inf)


def iv_rat(x: Fraction) -> str:
    lo, hi = outward_fraction(x)
    return f"iv({lo!r}, {hi!r})"


def iv_real_expr(expr: sp.Expr, env: dict[sp.Symbol, str]) -> str:
    """Render a real rational SymPy expression as outward Iv operations."""
    expr = sp.factor(expr)
    if expr.is_Integer or expr.is_Rational:
        return iv_rat(Fraction(int(expr.p), int(expr.q)))
    if expr.is_Symbol:
        return env[expr]
    if expr.is_Add:
        args = [iv_real_expr(x, env) for x in expr.args]
        out = args[0]
        for arg in args[1:]:
            out = f"iv_add({out}, {arg})"
        return out
    if expr.is_Mul:
        args = [iv_real_expr(x, env) for x in expr.args]
        out = args[0]
        for arg in args[1:]:
            out = f"iv_mul({out}, {arg})"
        return out
    if expr.is_Pow and expr.exp.is_Integer:
        n = int(expr.exp)
        base = iv_real_expr(expr.base, env)
        if n < 0:
            return f"iv_div(iv_point(1.0), {iv_pow(base, -n)})"
        return iv_pow(base, n)
    raise BuildError(f"unsupported interval expression {expr!r}")


def iv_pow(base: str, n: int) -> str:
    if n == 0:
        return "iv_point(1.0)"
    out = base
    for _ in range(1, n):
        out = f"iv_mul({out}, {base})"
    return out


def real_imag(expr: sp.Expr, r: sp.Symbol, omega: sp.Symbol) -> tuple[sp.Expr, sp.Expr]:
    z = sp.expand_complex(expr)
    return (sp.factor(sp.re(z)), sp.factor(sp.im(z)))


def render_matrix_callback(name: str, matrix: sp.Matrix, r: sp.Symbol,
                           omega: sp.Symbol, cell: tuple[Fraction, Fraction],
                           inward: bool = True) -> list[str]:
    """Render the realified coefficient for t=32-r (inward)."""
    n = matrix.rows
    require(matrix.cols == n, "coefficient is not square")
    lo, hi = cell
    lines = [f"fn {name}(t: Iv) -> IvMat {{",
             f"  let a: IvMat = ivm_zeros({2*n}, {2*n});",
             "  let rr: Iv = iv_sub(iv_point(32.0), t);" if inward else "  let rr: Iv = t;",
             f"  let ww: Iv = iv({math.nextafter(float(lo),-math.inf)!r}, {math.nextafter(float(hi),math.inf)!r});"]
    env = {r: "rr", omega: "ww"}
    for i in range(n):
        for j in range(n):
            re_part, im_part = real_imag((-matrix[i, j] if inward else matrix[i, j]), r, omega)
            if re_part != 0:
                e = iv_real_expr(re_part, env)
                lines += [f"  ivm_set(a,{i},{j},{e});", f"  ivm_set(a,{i+n},{j+n},{e});"]
            if im_part != 0:
                e = iv_real_expr(im_part, env)
                lines += [f"  ivm_set(a,{i+n},{j},{e});", f"  ivm_set(a,{i},{j+n},iv_neg({e}));"]
    lines += ["  return a;", "}", ""]
    return lines


def realify_numeric(a: np.ndarray) -> np.ndarray:
    return np.block([[a.real, -a.imag], [a.imag, a.real]])


def midpoint_centers(matrix: sp.Matrix, r: sp.Symbol, omega: sp.Symbol,
                     midpoint: Fraction) -> list[np.ndarray]:
    """Uncontrolled centers only: every use is later interval-certified."""
    fn = sp.lambdify((r, omega), matrix, "numpy")
    n = matrix.rows
    w = float(midpoint)
    def rhs(t, y):
        rr = 32.0 - t
        x = y.view(np.complex128).reshape(n, n)
        return (-(np.asarray(fn(rr, w), dtype=np.complex128) @ x)).reshape(-1).view(np.float64)
    y0 = np.eye(n, dtype=np.complex128).reshape(-1).view(np.float64)
    sol = solve_ivp(rhs, (0.0, 28.0), y0, method="DOP853", rtol=2e-13,
                    atol=2e-15, dense_output=True)
    require(sol.success, f"midpoint flow failed: {sol.message}")
    return [realify_numeric(sol.sol(float(k) / RESET_DEN).copy().view(np.complex128).reshape(n,n))
            for k in range(28 * RESET_DEN + 1)]


def qmat_numeric(name: str, matrix: np.ndarray, bits: int = 30) -> list[str]:
    scale = 1 << bits
    q = np.rint(matrix * scale).astype(object)
    lines = [f"fn {name}() -> QMat {{", f"  let a: QMat = qm_new({matrix.shape[0]}, {matrix.shape[1]});"]
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            num = int(q[i, j])
            if num:
                lines.append(f"  a = qm_set(a,{i},{j},rat({num},{scale}));")
    lines += ["  return a;", "}", ""]
    return lines


def structured_lower_data(full: list[np.ndarray], carrier: list[np.ndarray],
                          kernel: list[np.ndarray]) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Midpoint scouts for the cumulative lower frames and local corrections.

    The standard realification is ordered Re(6),Im(6); the block order used
    by the separated affine chain is carrier=(0..3,6..9), kernel=(4,5,10,11).
    These are only rational centres.  The generated consumer independently
    encloses every local G_j and certifies every solve.
    """
    ci = (0, 1, 2, 3, 6, 7, 8, 9)
    ki = (4, 5, 10, 11)
    d = [x[np.ix_(ki, ci)] for x in full]
    answer: list[np.ndarray] = []
    for j in range(len(full) - 1):
        u = full[j + 1] @ np.linalg.inv(full[j])
        g = u[np.ix_(ki, ci)]
        uc = u[np.ix_(ci, ci)]
        uk = u[np.ix_(ki, ki)]
        wc = np.linalg.solve(carrier[j + 1], uc @ carrier[j])
        rhs = g @ carrier[j] + uk @ d[j] - d[j + 1] @ wc
        answer.append(np.linalg.solve(kernel[j + 1], rhs))
    return d, answer


def render_adapter() -> str:
    # Reading the already-certified exact strings avoids replaying the expensive
    # symbolic geometry producer merely to generate a typed numerical consumer.
    r, omega = sp.symbols("r omega", real=True)
    cert = json.loads(RECON_CERT.read_text())
    A = sp.Matrix([[sp.sympify(x, locals={"r": r, "omega": omega,
                                         "I": sp.I})
                    for x in row] for row in cert["complete_reconstruction"]["flow6"]])
    carrier, kernel = A[:4, :4], A[4:, 4:]
    # First diagnostic version: certify separated diagonal flows and retain the
    # local full factors needed by the lower-lift recurrence.  The connection
    # consumer is appended once this width gate closes.
    lines = ["\n".join([
                 "// expect: 42", "// backends: c native",
                 "import prelude;", "import math/rational;", "import math/interval;",
                 "import math/qmat;", "import math/ivmat;", "import math/ivlinode;",
                 "import ds/vec;", "import text/strbuilder;", "import text/format;",
             ]),
             "", "// Phase-3 global connection v5 generated obstruction consumer.",
             "// Endpoint adapters are hash-pinned in certificate.json but are not",
             "// linked after the diagonal rank gate fails."]
    # A single required base cell is enough to prove the terminal wrapping
    # obstruction.  No untested cell is emitted as though the full cover closed.
    for i, cell in enumerate((DIAGNOSTIC_CELL,)):
        lines += render_matrix_callback(f"gc_full_{i}", A, r, omega, cell)
        lines += render_matrix_callback(f"gc_carrier_{i}", carrier, r, omega, cell)
        lines += render_matrix_callback(f"gc_kernel_{i}", kernel, r, omega, cell)
    # Exact rational moving-frame centers for the first-cell closure test.
    wc = sum(DIAGNOSTIC_CELL, Fraction(0)) / 2
    cc = midpoint_centers(carrier, r, omega, wc)
    kc = midpoint_centers(kernel, r, omega, wc)
    ac = midpoint_centers(A, r, omega, wc)
    dc, lc = structured_lower_data(ac, cc, kc)
    for k, matrix in enumerate(cc):
        lines += qmat_numeric(f"carrier_reset_{k}", matrix)
    for k, matrix in enumerate(kc):
        lines += qmat_numeric(f"kernel_reset_{k}", matrix)
    for k, matrix in enumerate(lc):
        lines += qmat_numeric(f"lower_center_{k}", matrix, bits=42)
    for k, matrix in enumerate(dc):
        lines += qmat_numeric(f"lower_frame_{k}", matrix, bits=42)
    lines += [
        "fn gc_width(a: borrow IvMat) -> f64 {",
        "  let w:f64=0.0; let i:i64=0; while(i<ivm_rows(a)){ let j:i64=0; while(j<ivm_cols(a)){ let x:f64=iv_wid(ivm_at(a,i,j)); if(x>w){w=x;} j=j+1;} i=i+1;} return w;",
        "}", "",
        "fn qcol(a: borrow QMat, j: i64) -> Vec<Rat> {",
        "  let v: Vec<Rat> = vec_new<Rat>(system_allocator(), usize(qm_rows(a)));",
        "  let i: i64 = 0;",
        "  while (i < qm_rows(a)) { vec_push<Rat>(v,qm_get(a,i,j)); i=i+1; }",
        "  return v;",
        "}", "",
        "fn ivcol(a: borrow IvMat, j: i64) -> IvVec {",
        "  let v: IvVec = ivv_zeros(ivm_rows(a));",
        "  let i: i64 = 0;",
        "  while (i < ivm_rows(a)) { ivv_set(v,i,ivm_at(a,i,j)); i=i+1; }",
        "  return v;",
        "}", "",
        "fn lower_block(a: borrow IvMat) -> IvMat {",
        "  let z:IvMat=ivm_zeros(4,8); let ki:i64=0; while(ki<4){let ii:i64=if(ki<2){4+ki}else{8+ki}; let cj:i64=0; while(cj<8){let jj:i64=if(cj<4){cj}else{2+cj}; ivm_set(z,ki,cj,ivm_at(a,ii,jj)); cj=cj+1;} ki=ki+1;} return z;",
        "}", "",
        "fn kernel_block(a: borrow IvMat) -> IvMat {",
        "  let z:IvMat=ivm_zeros(4,4);let i:i64=0;while(i<4){let ii:i64=if(i<2){4+i}else{8+i};let j:i64=0;while(j<4){let jj:i64=if(j<2){4+j}else{8+j};ivm_set(z,i,j,ivm_at(a,ii,jj));j=j+1;}i=i+1;}return z;",
        "}", "",
        "fn exact_unit(n:i64,j:i64)->Vec<Rat>{",
        "  let v:Vec<Rat>=vec_new<Rat>(system_allocator(),usize(n)); let i:i64=0;",
        "  while(i<n){if(i==j){vec_push<Rat>(v,rat(1,1));}else{vec_push<Rat>(v,rat(0,1));}i=i+1;} return v;",
        "}", "",
        "fn rank_box(center:borrow QMat,enclosure:borrow IvMat,n:i64)->bool{",
        "  let j:i64=0; while(j<n){let bq:Vec<Rat>=exact_unit(n,j);let bi:IvVec=ivv_from_rat_vec(bq);",
        "    match(ivm_solve_certified(center,bq,enclosure,bi)){some(c)=>{let unique:bool=c.unique;drop(c);drop(bi);drop(bq);if(!unique){return false;}},none=>{drop(bi);drop(bq);return false;}} j=j+1;} return true;",
        "}", "",
        "fn reset_step(local: borrow IvMat, oldc: borrow QMat, newc: borrow QMat, z: borrow IvMat) -> Option<IvMat> {",
        "  let rhs: IvMat = ivm_mul(local,ivm_from_qmat(oldc));",
        "  let amat: IvMat = ivm_from_qmat(newc);",
        "  let w: IvMat = ivm_zeros(qm_rows(newc),qm_cols(newc));",
        "  let j: i64 = 0;",
        "  while (j < qm_cols(newc)) {",
        "    let bc: Vec<Rat> = qcol(newc,j);",
        "    let bi: IvVec = ivcol(rhs,j);",
        "    match (ivm_solve_certified(newc,bc,amat,bi)) {",
        "      some(c) => {",
        "        let i: i64 = 0; while (i < qm_rows(newc)) { ivm_set(w,i,j,ivv_at(c.x,i)); i=i+1; }",
        "      },",
        "      none => { return Option.none; },",
        "    }",
        "    j=j+1;",
        "  }",
        "  return Option.some(ivm_mul(w,z));",
        "}", "",
    ]
    # Dispatch exact reset centers without an array-of-QMat ownership burden.
    last_reset = 28 * RESET_DEN
    cdisp = " else ".join([f"if (k=={i}) {{ carrier_reset_{i}() }}" for i in range(last_reset)] + [f"{{ carrier_reset_{last_reset}() }}"])
    kdisp = " else ".join([f"if (k=={i}) {{ kernel_reset_{i}() }}" for i in range(last_reset)] + [f"{{ kernel_reset_{last_reset}() }}"])
    ldisp = " else ".join([f"if (k=={i}) {{ lower_center_{i}() }}" for i in range(last_reset-1)] + [f"{{ lower_center_{last_reset-1}() }}"])
    ddisp = " else ".join([f"if (k=={i}) {{ lower_frame_{i}() }}" for i in range(last_reset)] + [f"{{ lower_frame_{last_reset}() }}"])
    lines += [f"fn carrier_reset(k:i64)->QMat {{ return {cdisp}; }}",
              f"fn kernel_reset(k:i64)->QMat {{ return {kdisp}; }}",
              f"fn lower_center(k:i64)->QMat {{ return {ldisp}; }}", "",
              f"fn lower_frame(k:i64)->QMat {{ return {ddisp}; }}", "",
              "fn local_lower(k:i64,fc:borrow IvLinAffineFlow)->Option<IvMat>{",
              f"  if(k<0 || k>={last_reset}){{return Option.none;}}",
              f"  let h:f64=28.0/{last_reset}.0; let ta:f64=f64(k)*h; let tb:f64=if(k+1=={last_reset}){{28.0}}else{{f64(k+1)*h}};",
              "  let lf:IvLinFlow=ivlin_fundamental(gc_full_0,12,ta,tb,2,12,true,true); if(!lf.ok){return Option.none;}",
              "  let g:IvMat=lower_block(lf.endpoint);let uk:IvMat=kernel_block(lf.endpoint);let wc:IvMat=match(ivlin_affine_correction(fc,k)){some(x)=>x,none=>{return Option.none;}};",
              "  let cc0:QMat=carrier_reset(k);let ck1:QMat=kernel_reset(k+1);let d0:QMat=lower_frame(k);let d1:QMat=lower_frame(k+1);",
              "  let rhs0:IvMat=ivm_add(ivm_mul(g,ivm_from_qmat(cc0)),ivm_mul(uk,ivm_from_qmat(d0)));let rhs:IvMat=ivm_sub(rhs0,ivm_mul(ivm_from_qmat(d1),wc));",
              "  let ac:IvMat=ivm_from_qmat(ck1); let lc:QMat=lower_center(k); let out:IvMat=ivm_zeros(4,8);",
              "  let j:i64=0; while(j<8){let xq:Vec<Rat>=qcol(lc,j); let bq:Vec<Rat>=qm_mul_vec(ck1,xq); let bi:IvVec=ivcol(rhs,j); match(ivm_solve_certified(ck1,bq,ac,bi)){some(c)=>{let i:i64=0;while(i<4){ivm_set(out,i,j,ivv_at(c.x,i));i=i+1;}},none=>{return Option.none;}} j=j+1;}",
              "  return Option.some(out);",
              "}", "",
              "fn lower_voc_obstruction(fc:borrow IvLinAffineFlow)->bool{let k:i64=0;let mk:i64=-1;let mw:f64=0.0;while(k<1792){match(local_lower(k,fc)){some(l)=>{let w:f64=gc_width(l);if(w>mw){mw=w;mk=k;}},none=>{println(strfmt(system_allocator(),\"lower refused reset={}\",k));return false;}}k=k+1;}println(strfmt(system_allocator(),\"structured-lower-solves=true max-width={} max-reset={}\",mw,mk));return mw>1000000.0 && mk==65;}", "",
              "fn affine_diagonal_first_cell() -> bool {",
              f"  let fc:IvLinAffineFlow=ivlin_affine_fundamental(gc_carrier_0,carrier_reset,8,0.0,28.0,{last_reset},2,12,true,true);",
              f"  let fk:IvLinAffineFlow=ivlin_affine_fundamental(gc_kernel_0,kernel_reset,4,0.0,28.0,{last_reset},2,12,true,true);",
              "  println(strfmt(system_allocator(), \"affine diagonal carrier-ok={} carrier-rank={} carrier-width={} kernel-ok={} kernel-rank={} kernel-width={}\",fc.ok,fc.rank_certified,fc.max_correction_width,fk.ok,fk.rank_certified,fk.max_correction_width));",
              "  if(!(fc.ok && fk.ok && fc.rank_certified && fk.rank_certified && fc.max_correction_width < 0.02 && fk.max_correction_width < 0.01)){return false;}",
              "  return lower_voc_obstruction(fc);",
              "}", ""]
    lines += ["fn diagnostic_growth() -> bool {",
              "  let a1: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,1.0,32,12,true,true);",
              "  let a2: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,2.0,64,12,true,true);",
              "  let a4: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,4.0,128,12,true,true);",
              "  let a8: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,8.0,256,12,true,true);",
              "  let a16: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,16.0,512,12,true,true);",
              "  let a28: IvLinFlow = ivlin_fundamental(gc_carrier_0,8,0.0,28.0,896,12,true,true);",
              "  if (!a1.ok || !a2.ok || !a4.ok || !a8.ok || !a16.ok || !a28.ok) { return false; }",
              "  println(strfmt(system_allocator(), \"carrier growth r31={} r30={} r28={} r24={} r16={} r4={}\", a1.max_endpoint_width,a2.max_endpoint_width,a4.max_endpoint_width,a8.max_endpoint_width,a16.max_endpoint_width,a28.max_endpoint_width));",
              "  return a1.max_endpoint_width < 0.1 && a2.max_endpoint_width < 0.2 && a4.max_endpoint_width < 1.0 && a8.max_endpoint_width > 10.0 && a16.max_endpoint_width > 100000.0 && a28.max_endpoint_width > 100000000000000.0;",
              "}", "",
              "pub fn axial_global_connection_parametric_frame_obstruction() -> bool {",
              "  if (!diagnostic_growth()) { return false; }",
              "  if (!affine_diagonal_first_cell()) { return false; }",
              "  return true;",
              "}", "",
              "pub fn main() -> i64 {",
              "  if (!axial_global_connection_parametric_frame_obstruction()) { return 3; }",
              "  return 42;", "}", ""]
    return "\n".join(lines)


def build_certificate() -> dict:
    return {
        "schema": "phase3-black-hole-axial-global-connection-matrix-v5-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5",
        "result_token": RESULT_TOKEN,
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["EXACT-ALGEBRAIC", "NUMERIC-ENCLOSURE"],
        "declaration": {
            "theory": "strict four-dimensional pure Weyl-squared gravity",
            "background": "Schwarzschild exterior with M=1",
            "sector": "axial ell=2, exp(+i omega v), repaired six-state chart",
            "target_frequency_cover": ["1/2", "3/4"],
            "target_cells": 64,
            "tested_required_cell": ["1/2", "129/256"],
            "matching_radius": 4,
            "infinity_handoff_radius": 32
        },
        "imports": {
            "practical_initializer": {"path": str(PRACTICAL.relative_to(PHYSICS)), "sha256": sha256(PRACTICAL)},
            "horizon_initializer": {"path": str(HORIZON.relative_to(PHYSICS)), "sha256": sha256(HORIZON)},
            "reconstruction_certificate": {"path": str(RECON_CERT.relative_to(PHYSICS)), "sha256": sha256(RECON_CERT)},
            "forge_ivlinode": {"path": str(FORGE / "lib/math/ivlinode.forge"), "sha256": sha256(FORGE / "lib/math/ivlinode.forge")},
        },
        "method": {
            "diagonal": "separate carrier 8-real and Einstein-kernel 4-real affine moving-frame Peano-Baker chains",
            "checkpoint_spacing": "1/64 in inward t=32-r",
            "local_steps_per_checkpoint": 2,
            "peano_baker_order": 12,
            "moving_centres": "DOP853 midpoint scouts quantized to exact rationals (2^30 diagonal frames; 2^42 lower frames/corrections); every use is independently enclosed by a Krawczyk solve",
            "checkpoints": 1792,
            "lower_lift": "local block variation of constants with exact block-triangular frames [[Cc,0],[D,Ck]]; every 4x8 transformed lower column is solved by interval Krawczyk without flattening the global flow",
            "solve": "certified Krawczyk solves only; never an explicit consumer inverse",
        },
        "flattened_width_growth": [
            {"radius": 31, "carrier_max_width": 0.013846707933141357},
            {"radius": 30, "carrier_max_width": 0.05664508765095389},
            {"radius": 28, "carrier_max_width": 0.6112034399810755},
            {"radius": 24, "carrier_max_width": 69.54826412879805},
            {"radius": 16, "carrier_max_width": 1615592.0908824624},
            {"radius": 4, "carrier_max_width": 2564827213010447.5},
        ],
        "affine_moving_frame_result": {
            "landed_substrate_commit": "1a4e53b88",
            "carrier_rank_certified": True,
            "kernel_rank_certified": True,
            "carrier_max_local_correction_width": 0.009978474438174208,
            "kernel_max_local_correction_width": 0.00332335609866979,
            "naive_full_frame": {
                "certified": False,
                "refusal_code": 10,
                "refusal_name": "IVLIN_AFFINE_FACTOR_RANK_UNCERTIFIED",
                "refusal_reset": 0,
                "meaning": "the unstructured 12-real interval factor loses the exact zero upper-right block; this is a representation refusal, not singularity"
            }
        },
        "structured_lower_lift_result": {
            "all_1792_local_krawczyk_solves_closed": True,
            "block_frame": "C_k=[[Cc_k,0],[D_k,Ck_k]] with exact rational Cc,Ck,D scouts",
            "correction_formula": "Ck_(k+1)^-1*(G_k*Cc_k+Uk_k*D_k-D_(k+1)*Wc_k)",
            "maximum_interval_width": 36880892.110833354,
            "maximum_width_reset": 65,
            "midpoint_correction_max_abs_at_reset_65": 2.9720385240453925e-11,
            "midpoint_lower_frame_max_abs_at_reset_65": 520.7048486768947,
            "diagnosis": "fixed rational frames discard the common omega dependence of A, D and the local flow before the cancellation; interval decorrelation overwhelms a nearly zero structured correction"
        },
        "stop_condition_disposition": "SHORTFALL",
        "missing_dependency": "Validated parameter-dependent affine frames (or equivalent Taylor-model/affine-arithmetic parameter generators) plus rectangular correlated multi-column factor-coordinate apply/solve. The frame must retain the shared omega generator through the block-triangular VoC cancellation instead of replacing D(omega) by a fixed rational box.",
        "missing_dependency_request": "planning/forge-requests/phase3-ivlinode-parametric-affine-rectangular.json",
        "claim_flags": {"required_first_cell_attempted": True,
                        "all_local_checkpoint_solves_certified": True,
                        "required_first_cell_diagonal_rank_certified": True,
                        "full_frequency_cover_certified": False,
                        "lower_lift_certified": False,
                        "global_connection_certified": False,
                        "radial_current_conservation_certified": False,
                        "endpoint_flux_or_scattering_claim": False},
        "does_not_establish": ["a global connection matrix", "an endpoint trace or flux",
                               "the nonexistence of a global connection matrix",
                               "a scientific obstruction in the Bach system",
                               "scattering, stability, CPT, positivity or unitarity"],
        "provenance": {
            "forge_head_observed": "3c4dfd5b43f0177e7ee450778a73d7c33f9749ac",
            "ivlinode_sha256": sha256(FORGE / "lib/math/ivlinode.forge")
        },
        "verification": {
            "producer": "python3 -m black_hole_programme.phase3.axial_global_connection_matrix_v5.produce --check",
            "independent": "python3 -m black_hole_programme.phase3.axial_global_connection_matrix_v5.verify",
            "tests": "python3 -m unittest black_hole_programme.phase3.axial_global_connection_matrix_v5.tests.test_global_connection -v",
            "mutations": "python3 -m black_hole_programme.phase3.axial_global_connection_matrix_v5.mutations"
        }
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    adapter = render_adapter()
    cert = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.check:
        require(ADAPTER.exists() and ADAPTER.read_text() == adapter, "adapter drift")
        require(OUTPUT.exists() and OUTPUT.read_text() == cert, "certificate drift")
        print("PASS global-connection producer replay")
    else:
        ADAPTER.write_text(adapter)
        OUTPUT.write_text(cert)
        print("wrote", ADAPTER)


if __name__ == "__main__":
    main()
