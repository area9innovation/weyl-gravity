#!/usr/bin/env python3
"""Transport the correlated outgoing S column through one inward panel."""
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

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_common_remainder_v1 import (
    produce as splus,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "splus_checkpoint.forge"
OUTPUT = HERE / "certificate.json"
CHECKPOINT = HERE / "checkpoint.json"
RECEIPT = HERE / "receipt.json"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-outgoing-splus-checkpoint-v1")
PREDECESSOR_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_common_remainder_v1/"
    "splus_common_remainder.forge"
)
PREDECESSOR_CERT = PREDECESSOR_SOURCE.with_name("certificate.json")
CROSSWALK = splus.CROSSWALK

R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega", real=True)
I = sp.I
TANGENT_SCALE = sp.Integer(512)


class CheckpointError(RuntimeError):
    """Fail-closed checkpoint error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def realify(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.row_join(-imag).col_join(imag.row_join(real))


def exact_generators(crosswalk: dict) -> dict:
    exact = crosswalk["exact_blocks"]
    a = matrix(exact["A_RW"])
    ax = matrix(exact["A_x"])
    d = matrix(exact["D_Lx_to_carrier_RW"])
    e = matrix(exact["E_RW_self_extension"])
    c = matrix(exact["C_Lx_to_metric_RW"])
    q = -2 * I * W - (4 * I * W + 1) / R

    base = sp.zeros(4)
    base[:2, :2] = a
    base[:2, 2:4] = d
    base[2:4, 2:4] = ax
    base -= q * sp.eye(4)

    tangent = sp.zeros(4)
    tangent[:2, :2] = e / TANGENT_SCALE
    tangent[:2, 2:4] = c / TANGENT_SCALE

    base_real = realify(base)
    tangent_real = realify(tangent)
    direct = sp.zeros(16)
    direct[:8, :8] = base_real
    direct[:8, 8:16] = tangent_real
    direct[8:16, 8:16] = base_real
    return {"base": base_real, "tangent": tangent_real, "direct": direct}


def forge_symbols(value: sp.Expr) -> sp.Expr:
    replacements = {}
    for symbol in value.free_symbols:
        if symbol.name == "omega":
            replacements[symbol] = jet.FORGE_W
        elif symbol.name == "r":
            replacements[symbol] = jet.FORGE_R
    return value.xreplace(replacements)


def render_models(data: dict) -> str:
    names = ("base", "tangent", "direct")
    matrices = tuple(data[name] for name in names)
    expressions: list[sp.Expr] = []
    positions: list[list[tuple[int, int, int]]] = []
    for value in matrices:
        current = []
        for row in range(value.rows):
            for col in range(value.cols):
                entry = clean(forge_symbols(value[row, col]))
                if entry != 0:
                    current.append((row, col, len(expressions)))
                    expressions.append(entry)
        positions.append(current)
    replacements, reduced = sp.cse(
        expressions, symbols=sp.numbered_symbols("sc_t")
    )
    renderer = jet.ForgeExpression()
    lines = [
        "fn sc_build_models(w_model:borrow IvTaylor4Mat,"
        "r_model:borrow IvTaylor4Mat)->ScModels{"
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    for name, value in zip(names, matrices):
        lines.append(
            f"  let {name}:IvTaylor4Mat=sj_zero({value.rows},{value.cols});"
        )
    for name, current in zip(names, positions):
        for row, col, index in current:
            lines.append(
                f"  {name}=sj_put({name},{row},{col},"
                f"{renderer.render(reduced[index])});"
            )
    lines.append("  return new ScModels(base,tangent,direct);")
    lines.append("}")
    return "\n".join(lines)


def strip_predecessor() -> str:
    text = PREDECESSOR_SOURCE.read_text()
    marker = "pub fn main()->i64{"
    require(marker in text, "S predecessor has no terminal main")
    return text.split(marker, 1)[0].rstrip() + "\n"


SUPPORT = r'''
pub type ScModels=scoped struct{
  pub base:IvTaylor4Mat,
  pub tangent:IvTaylor4Mat,
  pub direct:IvTaylor4Mat,
};
fn sc_scale(a:borrow IvTaylor4Mat,q:borrow Rat)->IvTaylor4Mat{
  return sj_expect(ivtm4_scale_rat_checked(a,q));
}
fn sc_add(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_expect(ivtm4_add_checked(a,b));
}
fn sc_series(a:borrow IvTaylor4Mat,h:borrow Rat,order:i64)->IvTaylor4Mat{
  let sum:IvTaylor4Mat=ivtm4_identity(7315,a.rows);
  let power:IvTaylor4Mat=ivtm4_identity(7315,a.rows);
  let coeff:Rat=rat(1,1);let n:i64=1;
  while(n<=order){
    power=sj_mul(a,power);
    coeff=(rat_clone(coeff)*rat_clone(h))/rat(n,1);
    sum=sc_add(sum,sc_scale(power,coeff));n=n+1;
  }
  return sum;
}
fn sc_dual_series(base:borrow IvTaylor4Mat,tangent:borrow IvTaylor4Mat,
h:borrow Rat,order:i64)->ScModels{
  let sb:IvTaylor4Mat=ivtm4_identity(7315,base.rows);
  let st:IvTaylor4Mat=sj_zero(base.rows,base.cols);
  let pb:IvTaylor4Mat=ivtm4_identity(7315,base.rows);
  let pt:IvTaylor4Mat=sj_zero(base.rows,base.cols);
  let coeff:Rat=rat(1,1);let n:i64=1;
  while(n<=order){
    let next_t:IvTaylor4Mat=sc_add(sj_mul(tangent,pb),sj_mul(base,pt));
    let next_b:IvTaylor4Mat=sj_mul(base,pb);
    pb=next_b;pt=next_t;
    coeff=(rat_clone(coeff)*rat_clone(h))/rat(n,1);
    sb=sc_add(sb,sc_scale(pb,coeff));
    st=sc_add(st,sc_scale(pt,coeff));n=n+1;
  }
  return new ScModels(sb,st,sj_zero(1,1));
}
fn sc_radius()->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);c0=qm_set(c0,0,0,big("16383/512"));
  let rem:IvMat=ivm_zeros(1,1);let rad:Iv=iv_from_rat(big("1/512"));
  ivm_set(rem,0,0,iv(0.0-rad.hi,rad.hi));
  return sj_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}
fn sc_stack(tangent:borrow IvTaylor4Mat,
base:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(16,1);let i:i64=0;while(i<8){
    out=sj_put(out,i,0,sj_scalar(tangent,i,0));
    out=sj_put(out,8+i,0,sj_scalar(base,i,0));i=i+1;}return out;
}
fn sc_unstack_tangent(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,1);let i:i64=0;while(i<8){
    out=sj_put(out,i,0,sj_scalar(a,i,0));i=i+1;}return out;
}
fn sc_unstack_base(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,1);let i:i64=0;while(i<8){
    out=sj_put(out,i,0,sj_scalar(a,8+i,0));i=i+1;}return out;
}
fn sc_pad(a:borrow IvTaylor4Mat,radius:f64)->IvTaylor4Mat{
  let rem:IvMat=sj_rem_clone(a.remainder);let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let old:Iv=ivm_at(rem,i,j);
    let z:Iv=match(iv_add_checked(old,iv(0.0-radius,radius))){
      some(x)=>x,none=>{trap();}};
    ivm_set(rem,i,j,z);j=j+1;}i=i+1;}
  return sj_expect(ivtm4_new(7315,a.c0,a.c1,a.c2,a.c3,a.c4,rem));
}
fn sc_norm(a:borrow IvMat)->f64{
  let best:f64=0.0;let i:i64=0;while(i<ivm_rows(a)){
    let sum:Iv=iv_point(0.0);let j:i64=0;while(j<ivm_cols(a)){
      sum=iv_add(sum,iv_abs(ivm_at(a,i,j)));j=j+1;}
    if(!iv_finite(sum)){return -1.0;}if(sum.hi>best){best=sum.hi;}i=i+1;}
  return best;
}
fn sc_tail(x:f64,n:i64)->f64{
  let fact:f64=1.0;let k:i64=1;while(k<=n){fact=fact*f64(k);k=k+1;}
  let xp:f64=1.0;k=0;while(k<n){xp=xp*x;k=k+1;}
  let q:f64=x/f64(n+1);
  if(q>=1.0||!f64_is_finite(q)){return -1.0;}
  return (xp/fact)/(1.0-q);
}
fn sc_contains_zero(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->bool{
  let d:IvTaylor4Mat=sj_expect(ivtm4_sub_checked(a,b));
  let h:IvMat=match(ivtm4_hull_checked(d)){some(x)=>x,none=>{return false;}};
  let i:i64=0;while(i<ivm_rows(h)){let j:i64=0;while(j<ivm_cols(h)){
    let x:Iv=ivm_at(h,i,j);if(x.lo>0.0||x.hi<0.0){return false;}
    j=j+1;}i=i+1;}return true;
}
fn sc_emit(tag:string,a:borrow IvTaylor4Mat)->void{
  let text:String=ivtm4_serialize_json(a,0);
  println(strfmt(system_allocator(),"{}_MODEL {}",tag,str_view(text)));drop(text);
}
'''


MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let old:IvTaylor4Mat=sj_old_xi3();
  let actual:IvTaylor4Mat=sj_mul(sj_normalized_transform(w),old);
  let formal:IvTaylor4Mat=sj_formal_head(w);
  let common:IvTaylor4Mat=sj_correlated(actual,formal);
  let base:IvTaylor4Mat=sj_extract_base(common);
  let tangent:IvTaylor4Mat=sj_extract_tangent(common);
  let tangent_n:IvTaylor4Mat=sc_scale(tangent,big("1/512"));
  let initial_tangent_width:f64=sj_width(match(ivtm4_hull_checked(tangent)){
    some(x)=>x,none=>{trap();}});
  let initial_normalized_width:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
    some(x)=>x,none=>{trap();}});
  let models:ScModels=sc_build_models(w,sc_radius());
  let h:Rat=big("-1/256");let order:i64=12;
  let dual:ScModels=sc_dual_series(models.base,models.tangent,h,order);
  let base_out:IvTaylor4Mat=sj_mul(dual.base,base);
  let tangent_n_out:IvTaylor4Mat=sc_add(
    sj_mul(dual.tangent,base),sj_mul(dual.base,tangent_n));
  let jet:IvTaylor4Mat=sc_stack(tangent_n_out,base_out);
  let direct_phi:IvTaylor4Mat=sc_series(models.direct,h,order);
  let direct:IvTaylor4Mat=sj_mul(direct_phi,sc_stack(tangent_n,base));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{trap();}};
  let sh:IvMat=match(ivtm4_hull_checked(sc_stack(tangent_n,base))){
    some(x)=>x,none=>{trap();}};
  let alpha:f64=sc_norm(mh);let scaled:f64=alpha/256.0;
  let tail:f64=sc_tail(scaled,13)*sc_norm(sh);
  if(tail<0.0||!f64_is_finite(tail)){
    println("SPLUS_CHECKPOINT status=REFUSED code=TAIL");return 3;}
  let jp:IvTaylor4Mat=sc_pad(jet,tail);
  let dp:IvTaylor4Mat=sc_pad(direct,tail);
  let coefficients:bool=sj_coefficients_equal(jp,dp);
  let overlap:bool=sc_contains_zero(jp,dp);
  let tangent_n_final:IvTaylor4Mat=sc_unstack_tangent(jp);
  let base_final:IvTaylor4Mat=sc_unstack_base(jp);
  let tangent_final:IvTaylor4Mat=sc_scale(tangent_n_final,big("512"));
  let nw:f64=sj_width(match(ivtm4_hull_checked(tangent_n_final)){
    some(x)=>x,none=>{trap();}});
  let tw:f64=sj_width(match(ivtm4_hull_checked(tangent_final)){
    some(x)=>x,none=>{trap();}});
  let bw:f64=sj_width(match(ivtm4_hull_checked(base_final)){
    some(x)=>x,none=>{trap();}});
  let pass:bool=coefficients&&overlap&&f64_is_finite(nw)&&
    f64_is_finite(tw)&&f64_is_finite(bw);
  sc_emit("CHECKPOINT_BASE",base_final);
  sc_emit("CHECKPOINT_TANGENT",tangent_final);
  println(strfmt(system_allocator(),
    "SPLUS_CHECKPOINT status={} generator=7315 panels=1 final_r=31.99609375 coefficients={} overlap={} alpha={} scaled_norm={} tail={} initial_tangent_width={} initial_normalized_width={} final_normalized_width={} final_tangent_width={} final_base_width={}",
    [if(pass){"PASS"}else{"REFUSED"},coefficients,overlap,alpha,scaled,tail,
     initial_tangent_width,initial_normalized_width,nw,tw,bw]));
  return if(pass){0}else{3};
}
'''


def source_text(generators: dict) -> str:
    return "\n".join(
        (
            strip_predecessor(),
            SUPPORT,
            render_models(generators),
            MAIN,
        )
    )


def run(command: list[str], env: dict[str, str]) -> dict:
    started = time.perf_counter()
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
        "exit": completed.returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "output": completed.stdout,
    }


def parse_model(output: str, tag: str) -> dict:
    prefix = f"{tag}_MODEL "
    for line in output.splitlines():
        if line.startswith(prefix):
            return json.loads(line[len(prefix) :])
    raise CheckpointError(f"missing serialized {tag}")


def parse_summary(output: str) -> dict:
    match = re.search(
        r"SPLUS_CHECKPOINT status=(?P<status>\w+) generator=(?P<generator>\d+) "
        r"panels=(?P<panels>\d+) final_r=(?P<final_r>[-+0-9.eE]+) "
        r"coefficients=(?P<coefficients>\w+) overlap=(?P<overlap>\w+) "
        r"alpha=(?P<alpha>[-+0-9.eE]+) "
        r"scaled_norm=(?P<scaled>[-+0-9.eE]+) "
        r"tail=(?P<tail>[-+0-9.eE]+) "
        r"initial_tangent_width=(?P<initial_tangent>[-+0-9.eE]+) "
        r"initial_normalized_width=(?P<initial_normalized>[-+0-9.eE]+) "
        r"final_normalized_width=(?P<final_normalized>[-+0-9.eE]+) "
        r"final_tangent_width=(?P<final_tangent>[-+0-9.eE]+) "
        r"final_base_width=(?P<final_base>[-+0-9.eE]+)",
        output,
    )
    return match.groupdict() if match else {"status": "UNPARSED"}


def build() -> tuple[dict, float]:
    started = time.perf_counter()
    predecessor = json.loads(PREDECESSOR_CERT.read_text())
    require(
        predecessor["claim_flags"]["S_partial_dual_tau_remainder_certified"],
        "S endpoint predecessor is not certified",
    )
    crosswalk = json.loads(CROSSWALK.read_text())
    SOURCE.write_text(source_text(exact_generators(crosswalk)))
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
    summary = parse_summary(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and summary.get("status") == "PASS"
        and summary.get("generator") == "7315"
        and summary.get("coefficients") == "true"
        and summary.get("overlap") == "true"
    )
    checkpoint_written = False
    if passed:
        base = parse_model(run_result["output"], "CHECKPOINT_BASE")
        tangent = parse_model(run_result["output"], "CHECKPOINT_TANGENT")
        payload = {
            "generator": 7315,
            "radius": "8191/256",
            "omega_child": ["1/2", "4097/8192"],
            "phase": "exp(-2*I*omega*(r-32))*(r/32)**(-4*I*omega-1)",
            "base": base,
            "tangent": tangent,
        }
        CHECKPOINT.write_text(
            json.dumps(
                {
                    "schema": "phase3-axial-outgoing-splus-checkpoint-v1",
                    "payload": payload,
                    "payload_sha256": canonical_sha256(payload),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        checkpoint_written = True
    result = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-checkpoint-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_SPLUS_CHECKPOINT",
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": (
            "SPLUS_CORRELATED_ONE_PANEL_CHECKPOINT_PASS"
            if passed
            else "SPLUS_CORRELATED_ONE_PANEL_CHECKPOINT_REFUSED"
        ),
        "imports": {
            "predecessor_source": {
                "path": str(PREDECESSOR_SOURCE.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_SOURCE),
            },
            "predecessor_certificate": {
                "path": str(PREDECESSOR_CERT.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CERT),
            },
            "crosswalk": {
                "path": str(CROSSWALK.relative_to(ROOT)),
                "sha256": sha256(CROSSWALK),
            },
        },
        "transport": {
            "arithmetic": "IvTaylor4_omega tensor partial dual_tau",
            "generator": 7315,
            "start_radius": "32",
            "final_radius": "8191/256",
            "panels": 1,
            "panel_width": "1/256",
            "exponential_order": 12,
            "internal_tangent_normalization": "tangent/512",
            "normalization_is_exactly_undone_at_checkpoint": True,
            "summary": summary,
        },
        "checkpoint": {
            "written": checkpoint_written,
            "path": str(CHECKPOINT.relative_to(ROOT))
            if checkpoint_written
            else None,
            "sha256": sha256(CHECKPOINT) if checkpoint_written else None,
            "payload_sha256": (
                json.loads(CHECKPOINT.read_text())["payload_sha256"]
                if checkpoint_written
                else None
            ),
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
            "S_common_endpoint_remainder_imported": True,
            "S_one_panel_partial_jet_correlation_certified": passed,
            "S_checkpoint_serialized": checkpoint_written,
            "S_reaches_interior_match": False,
            "joint_E_R_S_frame_certified": False,
            "K_plus_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "interpretation": {
            "normalization_outcome": (
                "The exact factor 512 reduces the internal tangent diameter "
                "but cannot reduce the physical checkpoint diameter after "
                "undoing the scale. A sharper physical enclosure requires a "
                "correlated upstream XI3 Volterra correction, not a coordinate "
                "recenter of the rectangular practical endpoint box."
            ),
            "short_chunk_purpose": (
                "prove that the common generator and partial dual correlation "
                "survive a genuine inward radial panel"
            ),
        },
        "does_not_establish": [
            "transport of S beyond r=8191/256",
            "a joint E/R/S outgoing frame at an interior match",
            "K_plus or T_plus",
            "Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "either continue the serialized checkpoint in bounded chunks or "
            "replace the coarse tangent endpoint box by a direct correlated "
            "XI3 Volterra remainder before long transport"
        ),
    }
    return result, time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, elapsed = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS Splus checkpoint producer check")
        return 0
    OUTPUT.write_text(encoded)
    receipt = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-checkpoint-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "command": (
            "python3 -m black_hole_programme.phase3."
            "axial_partial_jet_outgoing_splus_checkpoint_v1.produce"
        ),
        "elapsed_seconds": elapsed,
        "status": "PASS" if result["status"].endswith("_PASS") else "REFUSED",
        "tiers": {
            "tier0": "Python/Forge compile, deterministic producer, JSON schema",
            "tier1": "independent verifier and mutation tests",
            "tier2": "not run; no shared operator changed",
            "tier3": "not run; no Tplus or scattering theorem promoted",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    return 0 if result["status"].endswith("_PASS") else 3


if __name__ == "__main__":
    raise SystemExit(main())
