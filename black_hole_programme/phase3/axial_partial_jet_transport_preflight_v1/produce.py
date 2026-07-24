#!/usr/bin/env python3
"""Render, compile, and run one bounded omega-Taylor/dual-tau microfactor."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "partial_jet_microfactor.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
CERTIFICATE = HERE / "certificate.json"
FORGE_ROOT = Path("/home/alstrup/area9/tango/forge")
FORGE = FORGE_ROOT / "forge"
FORGE_LIB = FORGE_ROOT / "lib"
IVTAYLOR = FORGE_LIB / "math/ivtaylor.forge"
BINARY = Path("/tmp/axial-partial-jet-transport-preflight-v1")

INPUTS = {
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "q00_split_certificate": ROOT / (
        "black_hole_programme/phase3/"
        "axial_horizon_h4_plucker_q00_split_v1/certificate.json"
    ),
    "q00_child_source_metadata": ROOT / (
        "black_hole_programme/phase3/axial_horizon_h4_resume_v1/"
        "children/h4_child_q00_source_metadata.json"
    ),
}

R = sp.Symbol("r", real=True)
W = sp.Symbol("omega", real=True)
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def complex_to_real(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: sp.cancel(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: sp.cancel(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.row_join(-imag).col_join(imag.row_join(real))


class ForgeExpression:
    """Render scalar rational expressions into checked IvTaylor4 operations."""

    def render(self, value: sp.Expr) -> str:
        value = sp.factor(value)
        if value == 0:
            return "jt_const(big(\"0/1\"))"
        if value == 1:
            return "jt_const(big(\"1/1\"))"
        if value == R:
            return "ivtm4_clone(r_model)"
        if value == W:
            return "ivtm4_clone(w_model)"
        if value.is_Rational:
            q = sp.Rational(value)
            return f'jt_const(big("{q.p}/{q.q}"))'
        if value.is_Symbol:
            return str(value)
        if value.is_Add:
            args = list(value.as_ordered_terms())
            out = self.render(args[0])
            for arg in args[1:]:
                out = f"jt_add({out},{self.render(arg)})"
            return out
        if value.is_Mul:
            args = list(value.as_ordered_factors())
            out = self.render(args[0])
            for arg in args[1:]:
                out = f"jt_mul({out},{self.render(arg)})"
            return out
        if value.is_Pow and value.exp.is_Integer:
            exponent = int(value.exp)
            base = self.render(value.base)
            if exponent < 0:
                return f"jt_inv(jt_pow({base},{-exponent}))"
            return f"jt_pow({base},{exponent})"
        raise ValueError(f"unsupported Forge expression: {value!r}")


def block_matrices(crosswalk: dict) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    blocks = crosswalk["exact_blocks"]
    a = matrix(blocks["A_RW"])
    ax = matrix(blocks["A_x"])
    d = matrix(blocks["D_Lx_to_carrier_RW"])
    e = matrix(blocks["E_RW_self_extension"])
    c = matrix(blocks["C_Lx_to_metric_RW"])

    base = sp.zeros(4)
    base[:2, :2] = a
    base[:2, 2:4] = d
    base[2:4, 2:4] = ax
    tangent = sp.zeros(4)
    tangent[:2, :2] = e
    tangent[:2, 2:4] = c
    direct = sp.zeros(6)
    direct[:2, :2] = a
    direct[:2, 2:4] = e
    direct[:2, 4:6] = c
    direct[2:4, 2:4] = a
    direct[2:4, 4:6] = d
    direct[4:6, 4:6] = ax
    return tuple(complex_to_real(value) for value in (base, tangent, direct))


def render_matrix_builders(matrices: tuple[sp.Matrix, ...]) -> str:
    names = ("base", "tangent", "direct")
    sizes = (8, 8, 12)
    expressions: list[sp.Expr] = []
    positions: list[list[tuple[int, int, int]]] = []
    for value in matrices:
        current: list[tuple[int, int, int]] = []
        for row in range(value.rows):
            for col in range(value.cols):
                entry = sp.factor(value[row, col])
                if entry != 0:
                    current.append((row, col, len(expressions)))
                    expressions.append(entry)
        positions.append(current)

    replacements, reduced = sp.cse(
        expressions, symbols=sp.numbered_symbols("t")
    )
    renderer = ForgeExpression()
    lines: list[str] = []
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    for name, size in zip(names, sizes):
        lines.append(f"  let {name}:IvTaylor4Mat=jt_zero({size},{size});")
    for matrix_index, current in enumerate(positions):
        name = names[matrix_index]
        for row, col, expression_index in current:
            lines.append(
                f"  {name}=jt_put({name},{row},{col},"
                f"{renderer.render(reduced[expression_index])});"
            )
    lines.append("  return new ModelTriple(base,tangent,direct);")
    return "\n".join(lines)


SUPPORT = r'''
// expect: 0
// backends: c native
// One q00-child shell-0/panel-0 partial-jet microfactor only.
import prelude;
import math/rational;
import math/interval;
import math/qmat;
import math/ivmat;
import math/ivtaylor;
import math/ivlinparam;
import text/parse;
import text/format;
import text/strbuilder;

fn big(s:string)->Rat{return match(parse<Rat>(bytes(s),0)){
  ok(r)=>r,err(e)=>trap()};}

fn rem_clone(a:borrow IvMat)->IvMat{
  let z:IvMat=ivm_zeros(ivm_rows(a),ivm_cols(a));
  let i:i64=0;while(i<ivm_rows(a)){let j:i64=0;while(j<ivm_cols(a)){
    ivm_set(z,i,j,ivm_at(a,i,j));j=j+1;}i=i+1;}return z;
}

fn jt_expect(z:IvTaylor4Result)->IvTaylor4Mat{
  if(!z.ok){
    println(strfmt(system_allocator(),"ARITHMETIC_REFUSAL code={}",
      [z.refusal_code]));
    trap();
  }
  return ivtm4_clone(z.value);
}

fn jt_zero(rows:i64,cols:i64)->IvTaylor4Mat{
  return ivtm4_constant(7315,qm_new(rows,cols));
}

fn jt_const(q:Rat)->IvTaylor4Mat{
  let m:QMat=qm_new(1,1);m=qm_set(m,0,0,q);
  return ivtm4_constant(7315,m);
}

fn jt_frequency()->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);let c1:QMat=qm_new(1,1);
  c0=qm_set(c0,0,0,big("8193/16384"));
  c1=qm_set(c1,0,0,big("1/16384"));
  return jt_expect(ivtm4_new(7315,c0,c1,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),ivm_zeros(1,1)));
}

fn jt_radius()->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);
  c0=qm_set(c0,0,0,big("4294967809/2147483648"));
  let rem:IvMat=ivm_zeros(1,1);
  let rad:Iv=iv_from_rat(big("1/2147483648"));
  ivm_set(rem,0,0,iv(0.0-rad.hi,rad.hi));
  return jt_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}

fn jt_add(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return jt_expect(ivtm4_add_checked(a,b));
}
fn jt_sub(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return jt_expect(ivtm4_sub_checked(a,b));
}
fn jt_mul(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return jt_expect(ivtm4_mul_checked(a,b));
}
fn jt_scale(a:borrow IvTaylor4Mat,q:borrow Rat)->IvTaylor4Mat{
  return jt_expect(ivtm4_scale_rat_checked(a,q));
}
fn jt_inv(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return jt_expect(ivtm4_solve_left(a,ivtm4_identity(7315,1)));
}
fn jt_pow(a:borrow IvTaylor4Mat,n:i64)->IvTaylor4Mat{
  let z:IvTaylor4Mat=ivtm4_identity(7315,1);let k:i64=0;
  while(k<n){z=jt_mul(z,a);k=k+1;}return z;
}

fn jt_put(a:borrow IvTaylor4Mat,row:i64,col:i64,
x:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let c0:QMat=qm_clone(a.c0);let c1:QMat=qm_clone(a.c1);
  let c2:QMat=qm_clone(a.c2);let c3:QMat=qm_clone(a.c3);
  let c4:QMat=qm_clone(a.c4);let rem:IvMat=rem_clone(a.remainder);
  c0=qm_set(c0,row,col,qm_get(x.c0,0,0));
  c1=qm_set(c1,row,col,qm_get(x.c1,0,0));
  c2=qm_set(c2,row,col,qm_get(x.c2,0,0));
  c3=qm_set(c3,row,col,qm_get(x.c3,0,0));
  c4=qm_set(c4,row,col,qm_get(x.c4,0,0));
  ivm_set(rem,row,col,ivm_at(x.remainder,0,0));
  return jt_expect(ivtm4_new(7315,c0,c1,c2,c3,c4,rem));
}

fn jt_scalar(a:borrow IvTaylor4Mat,row:i64,col:i64)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);let c1:QMat=qm_new(1,1);
  let c2:QMat=qm_new(1,1);let c3:QMat=qm_new(1,1);
  let c4:QMat=qm_new(1,1);let rem:IvMat=ivm_zeros(1,1);
  c0=qm_set(c0,0,0,qm_get(a.c0,row,col));
  c1=qm_set(c1,0,0,qm_get(a.c1,row,col));
  c2=qm_set(c2,0,0,qm_get(a.c2,row,col));
  c3=qm_set(c3,0,0,qm_get(a.c3,row,col));
  c4=qm_set(c4,0,0,qm_get(a.c4,row,col));
  ivm_set(rem,0,0,ivm_at(a.remainder,row,col));
  return jt_expect(ivtm4_new(7315,c0,c1,c2,c3,c4,rem));
}

fn jt_series(a:borrow IvTaylor4Mat,h:borrow Rat,order:i64)->IvTaylor4Mat{
  let sum:IvTaylor4Mat=ivtm4_identity(7315,a.rows);
  let power:IvTaylor4Mat=ivtm4_identity(7315,a.rows);
  let coeff:Rat=rat(1,1);let n:i64=1;
  while(n<=order){
    power=jt_mul(a,power);
    coeff=(rat_clone(coeff)*rat_clone(h))/rat(n,1);
    sum=jt_add(sum,jt_scale(power,coeff));
    n=n+1;
  }
  return sum;
}

fn jt_pad(a:borrow IvTaylor4Mat,radius:f64)->IvTaylor4Mat{
  if(radius<0.0 || !f64_is_finite(radius)){trap();}
  let rem:IvMat=rem_clone(a.remainder);
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    let old:Iv=ivm_at(rem,i,j);
    let z:Iv=match(iv_add_checked(old,iv(0.0-radius,radius))){
      some(x)=>x,none=>{trap();}};
    ivm_set(rem,i,j,z);j=j+1;}i=i+1;}
  return jt_expect(ivtm4_new(7315,a.c0,a.c1,a.c2,a.c3,a.c4,rem));
}

pub type DualT4=scoped struct{
  pub base:IvTaylor4Mat,
  pub tangent:IvTaylor4Mat,
};

fn dual_mul(a:borrow DualT4,b:borrow DualT4)->DualT4{
  let base:IvTaylor4Mat=jt_mul(a.base,b.base);
  let left:IvTaylor4Mat=jt_mul(a.tangent,b.base);
  let right:IvTaylor4Mat=jt_mul(a.base,b.tangent);
  return new DualT4(base,jt_add(left,right));
}

fn dual_series(base:borrow IvTaylor4Mat,tangent:borrow IvTaylor4Mat,
h:borrow Rat,order:i64)->DualT4{
  let sum:DualT4=new DualT4(ivtm4_identity(7315,base.rows),
    jt_zero(base.rows,base.cols));
  let power:DualT4=new DualT4(ivtm4_identity(7315,base.rows),
    jt_zero(base.rows,base.cols));
  let coefficient:DualT4=new DualT4(ivtm4_clone(base),
    ivtm4_clone(tangent));
  let coeff:Rat=rat(1,1);let n:i64=1;
  while(n<=order){
    power=dual_mul(coefficient,power);
    coeff=(rat_clone(coeff)*rat_clone(h))/rat(n,1);
    sum=new DualT4(jt_add(sum.base,jt_scale(power.base,coeff)),
      jt_add(sum.tangent,jt_scale(power.tangent,coeff)));
    n=n+1;
  }
  return sum;
}

fn dual_expand(a:borrow DualT4)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(12,12);
  let i:i64=0;while(i<6){let j:i64=0;while(j<6){
    let kind:i64=if(i<2 && j<2){1}else{
      if(i<2 && j>=2){2}else{
      if(i>=2 && i<4 && j>=2){1}else{
      if(i>=4 && j>=4){1}else{0}}}};
    if(kind!=0){
      let si:i64=if(i<2){i}else{i-2};
      let sj:i64=if(j<2){j}else{j-2};
      let pr:i64=0;while(pr<2){let pc:i64=0;while(pc<2){
        let source:IvTaylor4Mat=if(kind==1){
          jt_scalar(a.base,pr*4+si,pc*4+sj)
        }else{
          jt_scalar(a.tangent,pr*4+si,pc*4+sj)
        };
        out=jt_put(out,pr*6+i,pc*6+j,source);
        pc=pc+1;}pr=pr+1;}
    }
    j=j+1;}i=i+1;}
  return out;
}

fn qcoeff_equal(a:borrow QMat,b:borrow QMat)->bool{
  let i:i64=0;while(i<qm_rows(a)){let j:i64=0;while(j<qm_cols(a)){
    if(!(qm_get(a,i,j)==qm_get(b,i,j))){return false;}j=j+1;}i=i+1;}
  return true;
}

fn coefficients_equal(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->bool{
  return qcoeff_equal(a.c0,b.c0)&&qcoeff_equal(a.c1,b.c1)&&
    qcoeff_equal(a.c2,b.c2)&&qcoeff_equal(a.c3,b.c3)&&
    qcoeff_equal(a.c4,b.c4);
}

fn difference_contains_zero(a:borrow IvTaylor4Mat,
b:borrow IvTaylor4Mat)->bool{
  let d:IvTaylor4Mat=jt_sub(a,b);
  let h:IvMat=match(ivtm4_hull_checked(d)){some(x)=>x,none=>{return false;}};
  let i:i64=0;while(i<ivm_rows(h)){let j:i64=0;while(j<ivm_cols(h)){
    let x:Iv=ivm_at(h,i,j);
    if(x.lo>0.0 || x.hi<0.0){return false;}j=j+1;}i=i+1;}
  return true;
}

fn hull_width(a:borrow IvTaylor4Mat)->f64{
  let h:IvMat=match(ivtm4_hull_checked(a)){some(x)=>x,none=>{trap();}};
  let width:f64=0.0;let i:i64=0;
  while(i<ivm_rows(h)){let j:i64=0;while(j<ivm_cols(h)){
    let x:Iv=ivm_at(h,i,j);let w:f64=x.hi-x.lo;
    if(w>width){width=w;}j=j+1;}i=i+1;}return width;
}

fn sl_inf_norm_hi(a:borrow IvMat)->f64{
  let best:f64=0.0;let i:i64=0;
  while(i<ivm_rows(a)){let s:Iv=iv_point(0.0);let j:i64=0;
    while(j<ivm_cols(a)){s=iv_add(s,iv_abs(ivm_at(a,i,j)));j=j+1;}
    if(!iv_finite(s)){return -1.0;}if(s.hi>best){best=s.hi;}i=i+1;}
  return best;
}

fn sl_exp_tail(x:f64,first_power:i64)->f64{
  if(x<0.0 || !f64_is_finite(x) || first_power<1){return -1.0;}
  let fact:f64=1.0;let j:i64=1;
  while(j<=first_power){fact=fact*f64(j);j=j+1;}
  let xp:f64=1.0;j=0;while(j<first_power){xp=xp*x;j=j+1;}
  let q:f64=x/f64(first_power+1);
  if(!f64_is_finite(fact) || !f64_is_finite(xp) || q>=1.0){return -1.0;}
  return (xp/fact)/(1.0-q);
}

pub type ModelTriple=scoped struct{
  pub base:IvTaylor4Mat,
  pub tangent:IvTaylor4Mat,
  pub direct:IvTaylor4Mat,
};
'''


MAIN = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let r_model:IvTaylor4Mat=jt_radius();
  let models:ModelTriple=build_models(w_model,r_model);
  let h:Rat=big("1/1073741824");
  let order:i64=12;
  let dual:DualT4=dual_series(models.base,models.tangent,h,order);
  let expanded:IvTaylor4Mat=dual_expand(dual);
  let direct:IvTaylor4Mat=jt_series(models.direct,h,order);
  let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("COEFFICIENT_HULL_REFUSAL");return 3;}};
  let alpha:f64=sl_inf_norm_hi(hull);
  let scaled_norm:f64=rat_to_f64(h)*alpha;
  let tail:f64=sl_exp_tail(scaled_norm,order+1);
  if(!f64_is_finite(tail)||tail<0.0){
    println(strfmt(system_allocator(),
      "TAIL_REFUSAL alpha={} scaled_norm={} tail={}",
      [alpha,scaled_norm,tail]));return 3;}
  let expanded_padded:IvTaylor4Mat=jt_pad(expanded,tail);
  let direct_padded:IvTaylor4Mat=jt_pad(direct,tail);
  let exact_coefficients:bool=coefficients_equal(expanded_padded,direct_padded);
  let overlap:bool=difference_contains_zero(expanded_padded,direct_padded);
  let direct_width:f64=hull_width(direct_padded);
  let jet_width:f64=hull_width(expanded_padded);
  println(strfmt(system_allocator(),
    "PARTIAL_JET_MICROFACTOR status={} coefficient_equal={} difference_contains_zero={} alpha={} tail={} direct_width={} jet_width={}",
    [if(exact_coefficients&&overlap){"PASS"}else{"REFUSED"},
     exact_coefficients,overlap,alpha,tail,direct_width,jet_width]));
  return if(exact_coefficients&&overlap){0}else{3};
}
'''


def render_source(crosswalk: dict) -> str:
    builders = render_matrix_builders(block_matrices(crosswalk))
    build_function = (
        "\nfn build_models(w_model:borrow IvTaylor4Mat,"
        "r_model:borrow IvTaylor4Mat)->ModelTriple{\n"
        + builders
        + "\n}\n"
    )
    return SUPPORT + build_function + "\n" + MAIN


def run_command(command: list[str], env: dict[str, str] | None = None) -> dict:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": " ".join(command),
        "exit": completed.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output": completed.stdout,
    }


def parse_result(output: str) -> dict | None:
    pattern = re.compile(
        r"PARTIAL_JET_MICROFACTOR status=(?P<status>\\w+) "
        r"coefficient_equal=(?P<coefficient>true|false) "
        r"difference_contains_zero=(?P<overlap>true|false) "
        r"alpha=(?P<alpha>[-+0-9.eE]+) "
        r"tail=(?P<tail>[-+0-9.eE]+) "
        r"direct_width=(?P<direct_width>[-+0-9.eE]+) "
        r"jet_width=(?P<jet_width>[-+0-9.eE]+)"
    )
    match = pattern.search(output)
    if match:
        values = match.groupdict()
        return {
            "status": values["status"],
            "refusal": None,
            "coefficient_equal": values["coefficient"] == "true",
            "difference_contains_zero": values["overlap"] == "true",
            "alpha": values["alpha"],
            "scaled_norm": None,
            "tail": values["tail"],
            "direct_width": values["direct_width"],
            "jet_width": values["jet_width"],
        }
    tail = re.search(
        r"TAIL_REFUSAL alpha=(?P<alpha>[-+0-9.eE]+) "
        r"scaled_norm=(?P<scaled>[-+0-9.eE]+) "
        r"tail=(?P<tail>[-+0-9.eE]+)",
        output,
    )
    if tail:
        values = tail.groupdict()
        return {
            "status": "REFUSED",
            "refusal": "ANALYTIC_TAIL_NONCONTRACTIVE",
            "coefficient_equal": None,
            "difference_contains_zero": None,
            "alpha": values["alpha"],
            "scaled_norm": values["scaled"],
            "tail": values["tail"],
            "direct_width": None,
            "jet_width": None,
        }
    return None


def produce() -> dict:
    imported = {
        name: json.loads(path.read_text())
        for name, path in INPUTS.items()
    }
    crosswalk = imported["partial_jet_crosswalk"]
    if crosswalk["status"] != (
        "EXACT_LOCAL_PARTIAL_JET_CROSSWALK_ENDPOINT_OPEN"
    ):
        raise RuntimeError("partial-jet crosswalk status drift")
    source = render_source(crosswalk)
    SOURCE.write_text(source)

    env = dict(os.environ)
    env["FORGE_LIB"] = str(FORGE_LIB)
    compile_result = run_command(
        [str(FORGE), "-o", str(BINARY), str(SOURCE)], env=env
    )
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = {
        "command": str(BINARY),
        "exit": None,
        "elapsed_seconds": 0.0,
        "output": "",
    }
    if compile_result["exit"] == 0:
        run_result = run_command([str(BINARY)])
    RUN_LOG.write_text(run_result["output"])
    result = parse_result(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and result is not None
        and result["status"] == "PASS"
        and result["coefficient_equal"]
        and result["difference_contains_zero"]
    )
    status = (
        "CERTIFIED_ONE_MICROFACTOR_PARTIAL_JET_PASS"
        if passed
        else "CERTIFIED_BOUNDED_PREFLIGHT_SHORTFALL"
    )
    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
        for name, path in INPUTS.items()
    }
    document = {
        "schema": "phase3-axial-partial-jet-transport-preflight-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_TRANSPORT_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": status,
        "imports": imports,
        "forge_substrate": {
            "executable": str(FORGE),
            "ivtaylor_path": str(IVTAYLOR),
            "ivtaylor_sha256": sha256(IVTAYLOR),
        },
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "frequency_center": "8193/16384",
            "frequency_radius": "1/16384",
            "shared_generator": 7315,
            "radial_shell": 0,
            "radial_panel": 0,
            "radial_interval": [
                "2+1/4194304",
                "2+1/4194304+1/1073741824",
            ],
            "radial_center": "4294967809/2147483648",
            "radial_radius": "1/2147483648",
            "panel_width": "1/1073741824",
            "series_order": 12,
            "arithmetic": (
                "IvTaylor4_omega tensor dual_tau; radial uncertainty is "
                "an outward interval remainder"
            ),
        },
        "attempt": {
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
            # Wall-clock timings belong in the receipt, not in the
            # content-addressed mathematical certificate.
            "compile_elapsed_seconds": 0.0,
            "run_elapsed_seconds": 0.0,
            "parsed_result": result,
        },
        "comparison": {
            "jet_route": (
                "transport the 8x8 real base/tangent pair in dual_tau, "
                "then expand to the 12x12 real six-state order"
            ),
            "reference_route": (
                "transport the direct 12x12 real form of the exact six-state "
                "connection imported from the crosswalk"
            ),
            "same_analytic_tail_padding": True,
            "success_requires": [
                "exact equality of IvTaylor4 omega coefficients C0..C4",
                "zero contained in every entry of the difference hull",
                "zero arithmetic refusal and process exit",
            ],
            "passed": passed,
        },
        "claim_flags": {
            "one_microfactor_bounded_partial_jet_pass": passed,
            "shared_omega_dual_tau_arithmetic_exercised": (
                compile_result["exit"] == 0 and result is not None
            ),
            "expanded_six_state_reference_compared": (
                result is not None
                and result["coefficient_equal"] is not None
            ),
            "whole_q00_child_transport_certified": False,
            "H4_pass_certified": False,
            "endpoint_partial_jet_frames_constructed": False,
            "T_plus_recovered": False,
            "scattering_identity_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "transport of the complete q00 child",
            "transport beyond one shell-0 radial panel",
            "an H4 exterior-norm pass",
            "compatible endpoint partial-jet frames",
            "the outgoing map T_plus",
            "a scattering identity or global bounded population map",
        ],
    }
    CERTIFICATE.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


if __name__ == "__main__":
    certificate = produce()
    print("status=" + certificate["status"])
