#!/usr/bin/env python3
"""Reissue the all-order outgoing XI3/S column in the common jet algebra.

The practical infinity adapter already encloses the all-order old-coordinate
XI3 column uniformly on its first omega cell.  This producer applies the exact
old-to-factor coordinate map and the exact S=i*XI3/(2*omega) normalization in
IvTaylor4 generator 7315.  The exact finite factor head supplies c0,...,c4;
the difference between the validated all-order hull and that head is attached
as one common remainder before the partial dual-tau state is extracted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    exact_blocks,
)
from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "splus_common_remainder.forge"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-outgoing-splus-common-remainder-v1")
ADAPTER = ROOT / (
    "black_hole_programme/phase3/axial_infinity_practical_transfer/"
    "validated_infinity_transfer.forge"
)
CROSSWALK = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_transport_crosswalk_v1/certificate.json"
)
PRACTICAL_CERT = ADAPTER.with_name("certificate.json")
FRAME_PREFLIGHT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_frame_completion_v1/certificate.json"
)

R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega", real=True)
I = sp.I
Z = sp.Symbol("z", positive=True)
R0 = sp.Integer(32)


class SPlusError(RuntimeError):
    """Fail-closed construction error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SPlusError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def realify_matrix(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.row_join(-imag).col_join(imag.row_join(real))


def realify_column(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.col_join(imag)


def forge_symbols(value: sp.Expr) -> sp.Expr:
    replacements = {}
    for symbol in value.free_symbols:
        if symbol.name == "omega":
            replacements[symbol] = jet.FORGE_W
        elif symbol.name == "r":
            replacements[symbol] = jet.FORGE_R
    return value.xreplace(replacements)


def exact_s_data(crosswalk: dict) -> dict:
    blocks = exact_blocks()
    columns = dict(blocks["columns"])
    omega = blocks["omega"]
    z = blocks["z"]
    transform = matrix(
        crosswalk["full_transform_crosswalk"]["coordinate_map_old_to_new"]
    ).subs({R: 1 / z, W: omega})
    normalized_transform = (I / (2 * omega) * transform).applyfunc(clean)
    formal = (normalized_transform * columns["XI3"]).applyfunc(clean)
    formal_r32 = formal.subs(z, sp.Rational(1, 32)).applyfunc(clean)

    # The exact partial-jet coordinate order is (X,Y,Z), each two complex
    # components.  The S normalization has unit quotient by the independent
    # endpoint-frame audit.
    require(formal_r32.rows == 6 and formal_r32.cols == 1, "S head shape drift")
    return {
        "transform_real": realify_matrix(
            normalized_transform.subs(z, sp.Rational(1, 32))
        ),
        "formal_real": realify_column(formal_r32),
        "formal_complex": [sp.sstr(value) for value in formal_r32],
        "rate": sp.sstr(blocks["rates"][3]),
        "power": sp.sstr(blocks["powers"][3]),
    }


def strip_adapter(path: Path) -> str:
    text = path.read_text()
    lines = [line for line in text.splitlines() if not line.startswith("import ")]
    text = "\n".join(lines)
    marker = "pub fn main() -> i64 {"
    require(marker in text, "practical infinity adapter has no terminal main")
    return text.split(marker, 1)[0].rstrip() + "\n"


def render_tm_builder(name: str, value: sp.Matrix) -> str:
    expressions: list[sp.Expr] = []
    positions: list[tuple[int, int, int]] = []
    for row in range(value.rows):
        for col in range(value.cols):
            entry = clean(forge_symbols(value[row, col]))
            if entry != 0:
                positions.append((row, col, len(expressions)))
                expressions.append(entry)
    replacements, reduced = sp.cse(
        expressions, symbols=sp.numbered_symbols(f"{name}_t")
    )
    renderer = jet.ForgeExpression()
    lines = [
        f"fn {name}(w_model:borrow IvTaylor4Mat)->IvTaylor4Mat{{",
        "  let r_model:IvTaylor4Mat=sj_const(big(\"32/1\"));",
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    lines.append(f"  let out:IvTaylor4Mat=sj_zero({value.rows},{value.cols});")
    for row, col, index in positions:
        lines.append(
            f"  out=sj_put(out,{row},{col},"
            f"{renderer.render(reduced[index])});"
        )
    lines.append("  return out;")
    lines.append("}")
    return "\n".join(lines)


SUPPORT = r'''
fn sj_expect(z:IvTaylor4Result)->IvTaylor4Mat{
  if(!z.ok){
    println(strfmt(system_allocator(),"SPLUS status=REFUSED code=ARITHMETIC_{}",
      [z.refusal_code]));trap();
  }
  return ivtm4_clone(z.value);
}
fn sj_zero(rows:i64,cols:i64)->IvTaylor4Mat{
  return ivtm4_constant(7315,qm_new(rows,cols));
}
fn sj_const(q:Rat)->IvTaylor4Mat{
  let m:QMat=qm_new(1,1);m=qm_set(m,0,0,q);
  return ivtm4_constant(7315,m);
}
fn sj_frequency()->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);let c1:QMat=qm_new(1,1);
  c0=qm_set(c0,0,0,big("8193/16384"));
  c1=qm_set(c1,0,0,big("1/16384"));
  return sj_expect(ivtm4_new(7315,c0,c1,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),ivm_zeros(1,1)));
}
fn sj_rem_clone(a:borrow IvMat)->IvMat{
  let z:IvMat=ivm_zeros(ivm_rows(a),ivm_cols(a));
  let i:i64=0;while(i<ivm_rows(a)){let j:i64=0;while(j<ivm_cols(a)){
    ivm_set(z,i,j,ivm_at(a,i,j));j=j+1;}i=i+1;}return z;
}
fn sj_put(a:borrow IvTaylor4Mat,row:i64,col:i64,
x:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let c0:QMat=qm_clone(a.c0);let c1:QMat=qm_clone(a.c1);
  let c2:QMat=qm_clone(a.c2);let c3:QMat=qm_clone(a.c3);
  let c4:QMat=qm_clone(a.c4);let rem:IvMat=sj_rem_clone(a.remainder);
  c0=qm_set(c0,row,col,qm_get(x.c0,0,0));
  c1=qm_set(c1,row,col,qm_get(x.c1,0,0));
  c2=qm_set(c2,row,col,qm_get(x.c2,0,0));
  c3=qm_set(c3,row,col,qm_get(x.c3,0,0));
  c4=qm_set(c4,row,col,qm_get(x.c4,0,0));
  ivm_set(rem,row,col,ivm_at(x.remainder,0,0));
  return sj_expect(ivtm4_new(7315,c0,c1,c2,c3,c4,rem));
}
fn sj_scalar(a:borrow IvTaylor4Mat,row:i64,col:i64)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);let c1:QMat=qm_new(1,1);
  let c2:QMat=qm_new(1,1);let c3:QMat=qm_new(1,1);
  let c4:QMat=qm_new(1,1);let rem:IvMat=ivm_zeros(1,1);
  c0=qm_set(c0,0,0,qm_get(a.c0,row,col));
  c1=qm_set(c1,0,0,qm_get(a.c1,row,col));
  c2=qm_set(c2,0,0,qm_get(a.c2,row,col));
  c3=qm_set(c3,0,0,qm_get(a.c3,row,col));
  c4=qm_set(c4,0,0,qm_get(a.c4,row,col));
  ivm_set(rem,0,0,ivm_at(a.remainder,row,col));
  return sj_expect(ivtm4_new(7315,c0,c1,c2,c3,c4,rem));
}
fn sj_mul(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_expect(ivtm4_mul_checked(a,b));
}
// ForgeExpression uses the established partial-jet helper names.
fn jt_const(q:Rat)->IvTaylor4Mat{return sj_const(q);}
fn jt_add(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_expect(ivtm4_add_checked(a,b));
}
fn jt_mul(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_mul(a,b);
}
fn jt_inv(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_expect(ivtm4_solve_left(a,ivtm4_identity(7315,1)));
}
fn jt_pow(a:borrow IvTaylor4Mat,n:i64)->IvTaylor4Mat{
  let z:IvTaylor4Mat=ivtm4_identity(7315,1);let k:i64=0;
  while(k<n){z=jt_mul(z,a);k=k+1;}return z;
}
fn sj_old_xi3()->IvTaylor4Mat{
  let ep:IvEndpointCert=axial_infinity_initializer(0);
  if(!ep.ok || !ep.rank_certified || !ep.parameter_uniform){
    println("SPLUS status=REFUSED code=ENDPOINT_INPUT");trap();
  }
  let rem:IvMat=ivm_zeros(12,1);let i:i64=0;
  while(i<12){ivm_set(rem,i,0,ivm_at(ep.value,i,3));i=i+1;}
  return sj_expect(ivtm4_new(7315,qm_new(12,1),qm_new(12,1),
    qm_new(12,1),qm_new(12,1),qm_new(12,1),rem));
}
fn sj_width(a:borrow IvMat)->f64{
  let best:f64=0.0;let i:i64=0;while(i<ivm_rows(a)){
    let j:i64=0;while(j<ivm_cols(a)){let x:Iv=ivm_at(a,i,j);
      let w:f64=x.hi-x.lo;if(!f64_is_finite(w)){return -1.0;}
      if(w>best){best=w;}j=j+1;}i=i+1;}return best;
}
fn sj_subset(a:borrow IvMat,b:borrow IvMat)->bool{
  let i:i64=0;while(i<ivm_rows(a)){let j:i64=0;
    while(j<ivm_cols(a)){let x:Iv=ivm_at(a,i,j);let y:Iv=ivm_at(b,i,j);
      if(x.lo<y.lo || x.hi>y.hi){return false;}j=j+1;}i=i+1;}
  return true;
}
fn sj_qequal(a:borrow QMat,b:borrow QMat)->bool{
  let i:i64=0;while(i<qm_rows(a)){let j:i64=0;while(j<qm_cols(a)){
    if(!(qm_get(a,i,j)==qm_get(b,i,j))){return false;}j=j+1;}i=i+1;}
  return true;
}
fn sj_coefficients_equal(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->bool{
  return sj_qequal(a.c0,b.c0)&&sj_qequal(a.c1,b.c1)&&
    sj_qequal(a.c2,b.c2)&&sj_qequal(a.c3,b.c3)&&
    sj_qequal(a.c4,b.c4);
}
fn sj_correlated(actual:borrow IvTaylor4Mat,
formal:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let ah:IvMat=match(ivtm4_hull_checked(actual)){some(x)=>x,none=>{trap();}};
  let fh:IvMat=match(ivtm4_hull_checked(formal)){some(x)=>x,none=>{trap();}};
  let rem:IvMat=ivm_sub(ah,fh);
  return sj_expect(ivtm4_new(7315,formal.c0,formal.c1,formal.c2,
    formal.c3,formal.c4,rem));
}
fn sj_extract_base(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,1);let i:i64=0;
  while(i<4){
    out=sj_put(out,i,0,sj_scalar(a,2+i,0));
    out=sj_put(out,4+i,0,sj_scalar(a,8+i,0));i=i+1;}
  return out;
}
fn sj_extract_tangent(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,1);
  out=sj_put(out,0,0,sj_scalar(a,0,0));
  out=sj_put(out,1,0,sj_scalar(a,1,0));
  out=sj_put(out,4,0,sj_scalar(a,6,0));
  out=sj_put(out,5,0,sj_scalar(a,7,0));
  return out;
}
'''


MAIN = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=sj_frequency();
  let old:IvTaylor4Mat=sj_old_xi3();
  let transform:IvTaylor4Mat=sj_normalized_transform(w_model);
  let actual:IvTaylor4Mat=sj_mul(transform,old);
  let formal:IvTaylor4Mat=sj_formal_head(w_model);
  let common:IvTaylor4Mat=sj_correlated(actual,formal);
  let ah:IvMat=match(ivtm4_hull_checked(actual)){some(x)=>x,none=>{trap();}};
  let ch:IvMat=match(ivtm4_hull_checked(common)){some(x)=>x,none=>{trap();}};
  let fh:IvMat=match(ivtm4_hull_checked(formal)){some(x)=>x,none=>{trap();}};
  let base:IvTaylor4Mat=sj_extract_base(common);
  let tangent:IvTaylor4Mat=sj_extract_tangent(common);
  let bh:IvMat=match(ivtm4_hull_checked(base)){some(x)=>x,none=>{trap();}};
  let th:IvMat=match(ivtm4_hull_checked(tangent)){some(x)=>x,none=>{trap();}};
  let contained:bool=sj_subset(ah,ch);
  let coefficients:bool=sj_coefficients_equal(common,formal);
  let finite:bool=sj_width(ch)>=0.0&&sj_width(bh)>=0.0&&sj_width(th)>=0.0;
  let pass:bool=contained&&coefficients&&finite;
  println(strfmt(system_allocator(),
    "SPLUS status={} generator=7315 contained={} coefficients={} actual_width={} formal_width={} common_width={} base_width={} tangent_width={}",
    [if(pass){"PASS"}else{"REFUSED"},contained,coefficients,sj_width(ah),
     sj_width(fh),sj_width(ch),sj_width(bh),sj_width(th)]));
  return if(pass){0}else{3};
}
'''


def source_text(data: dict) -> str:
    imports = "\n".join(
        (
            "// expect: 0",
            "// backends: c native",
            "import prelude;",
            "import math/rational;",
            "import math/interval;",
            "import math/qmat;",
            "import math/ivmat;",
            "import math/ivlinode;",
            "import math/ivendpoint;",
            "import math/ivtaylor;",
            "import math/ivlinparam;",
            "import ds/vec;",
            "import text/parse;",
            "import text/format;",
            "import text/strbuilder;",
        )
    )
    return "\n".join(
        (
            imports,
            strip_adapter(ADAPTER),
            SUPPORT,
            render_tm_builder("sj_normalized_transform", data["transform_real"]),
            render_tm_builder("sj_formal_head", data["formal_real"]),
            MAIN,
        )
    )


def run(command: list[str], env: dict[str, str]) -> dict:
    started = time.perf_counter()
    result = subprocess.run(
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
        "exit": result.returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "output": result.stdout,
    }


def parse_run(output: str) -> dict:
    match = re.search(
        r"SPLUS status=(?P<status>\w+) generator=(?P<generator>\d+) "
        r"contained=(?P<contained>\w+) coefficients=(?P<coefficients>\w+) "
        r"actual_width=(?P<actual>[-+0-9.eE]+) "
        r"formal_width=(?P<formal>[-+0-9.eE]+) "
        r"common_width=(?P<common>[-+0-9.eE]+) "
        r"base_width=(?P<base>[-+0-9.eE]+) "
        r"tangent_width=(?P<tangent>[-+0-9.eE]+)",
        output,
    )
    if not match:
        return {"status": "UNPARSED", "output": output.strip()}
    return match.groupdict()


def build() -> tuple[dict, dict]:
    crosswalk = json.loads(CROSSWALK.read_text())
    practical = json.loads(PRACTICAL_CERT.read_text())
    preflight = json.loads(FRAME_PREFLIGHT.read_text())
    require(
        practical["claim_flags"]["full_rank_R32_initializer_certified"],
        "practical infinity initializer is not certified",
    )
    require(
        preflight["claim_flags"]["formal_E_R_S_columns_constructed"],
        "formal outgoing frame drifted",
    )
    data = exact_s_data(crosswalk)
    SOURCE.write_text(source_text(data))
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    compile_result = run([str(jet.FORGE), "-o", str(BINARY), str(SOURCE)], env)
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = (
        run([str(BINARY)], env)
        if compile_result["exit"] == 0
        else {"exit": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_run(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed.get("status") == "PASS"
        and parsed.get("generator") == "7315"
        and parsed.get("contained") == "true"
        and parsed.get("coefficients") == "true"
    )
    result = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-common-remainder-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_SPLUS_COMMON_REMAINDER",
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": (
            "SPLUS_COMMON_GENERATOR_REMAINDER_PASS"
            if passed
            else "SPLUS_COMMON_GENERATOR_REMAINDER_REFUSED"
        ),
        "imports": {
            "practical_infinity_adapter": {
                "path": str(ADAPTER.relative_to(ROOT)),
                "sha256": sha256(ADAPTER),
            },
            "practical_infinity_certificate": {
                "path": str(PRACTICAL_CERT.relative_to(ROOT)),
                "sha256": sha256(PRACTICAL_CERT),
            },
            "partial_jet_crosswalk": {
                "path": str(CROSSWALK.relative_to(ROOT)),
                "sha256": sha256(CROSSWALK),
            },
            "outgoing_frame_preflight": {
                "path": str(FRAME_PREFLIGHT.relative_to(ROOT)),
                "sha256": sha256(FRAME_PREFLIGHT),
            },
        },
        "domain": {
            "radius": "32",
            "practical_parent_omega_cell": ["1/2", "129/256"],
            "exported_first_pilot_child": ["1/2", "4097/8192"],
            "phase": "exp(-2*I*omega*(r-32))*(r/32)**(-4*I*omega-1)",
            "phase_omega_taylor_expanded": False,
        },
        "factor_column": {
            "old_line": "XI3",
            "normalized_line": "S=I*XI3/(2*omega)",
            "factor_state_order": ["X_tau", "Y_base", "Z_spin_one"],
            "dual_base_order": ["Y_re", "Z_re", "Y_im", "Z_im"],
            "dual_tangent_order": [
                "X_re",
                "zero_Z_re",
                "X_im",
                "zero_Z_im",
            ],
            "spin_one_tangent_is_exactly_zero": True,
            "formal_rate": data["rate"],
            "formal_power": data["power"],
            "formal_complex_head_at_r32": data["formal_complex"],
        },
        "common_remainder": {
            "arithmetic": "IvTaylor4_omega tensor partial dual_tau",
            "generator_id": 7315,
            "construction": (
                "validated all-order old XI3 hull -> exact rational factor "
                "transform and unit quotient normalization -> exact degree-4 "
                "factor-head coefficients plus one common interval remainder"
            ),
            "all_order_input": True,
            "exact_head_coefficients_preserved": passed,
            "all_order_actual_hull_contained": passed,
            "runtime": parsed,
        },
        "artifacts": {
            "source": {
                "path": str(SOURCE.relative_to(ROOT)),
                "sha256": sha256(SOURCE),
            },
            "compile_log": {
                "path": str(COMPILE_LOG.relative_to(ROOT)),
                "sha256": sha256(COMPILE_LOG),
            },
            "run_log": {
                "path": str(RUN_LOG.relative_to(ROOT)),
                "sha256": sha256(RUN_LOG),
            },
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
        },
        "claim_flags": {
            "S_phase_factored_all_order_input_certified": True,
            "S_common_omega_generator_certified": passed,
            "S_partial_dual_tau_remainder_certified": passed,
            "all_three_correlated_outgoing_columns_certified": False,
            "validated_analytic_K_plus_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "does_not_establish": [
            "transport of S from r=32 to the interior matching section",
            "a jointly propagated three-column outgoing endpoint frame",
            "a validated analytic K_plus normalizer",
            "T_plus, reflection, Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "transport this correlated S dual column with the same checkpointed "
            "partial-jet rail as R+, then certify the joint E/R/S endpoint frame"
        ),
    }
    return result, {
        "compile_elapsed_seconds": compile_result["elapsed_seconds"],
        "run_elapsed_seconds": run_result["elapsed_seconds"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    result, timing = build()
    total_elapsed = time.perf_counter() - started
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS Splus common remainder producer check")
        return 0
    OUTPUT.write_text(encoded)
    receipt = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-common-remainder-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "dependency_tags": result["dependency_tags"],
        "commands": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_outgoing_splus_common_remainder_v1.produce"
                ),
                "elapsed_seconds": total_elapsed,
                "compile_elapsed_seconds": timing["compile_elapsed_seconds"],
                "run_elapsed_seconds": timing["run_elapsed_seconds"],
                "status": "PASS"
                if result["status"].endswith("_PASS")
                else "REFUSED",
            }
        ],
        "tiers": {
            "tier0": "Python/Forge compile, deterministic producer, JSON schema",
            "tier1": "independent verifier and mutation tests",
            "tier2": "not run; no shared operator changed",
            "tier3": "not run; no scattering theorem promoted",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    return 0 if result["status"].endswith("_PASS") else 3


if __name__ == "__main__":
    raise SystemExit(main())
