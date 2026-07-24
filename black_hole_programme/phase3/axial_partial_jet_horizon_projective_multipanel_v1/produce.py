#!/usr/bin/env python3
"""Projectivize the selected mixed horizon column across all radial shells."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_horizon_multipanel_preflight_v1 import (
    produce as multipanel,
)
from black_hole_programme.phase3.axial_partial_jet_horizon_spin_one_levelt_v1 import (
    produce as levelt,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE = HERE / "projective_multipanel.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-horizon-projective-v1")
INPUTS = {
    "multipanel_shortfall": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_multipanel_preflight_v1/certificate.json",
    "spin_one_levelt": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_spin_one_levelt_v1/certificate.json",
    "partial_jet_crosswalk": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json",
}
CODE_INPUTS = {
    "multipanel_producer": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_multipanel_preflight_v1/produce.py",
    "levelt_producer": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_spin_one_levelt_v1/produce.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


CHART_SUPPORT = r'''
pub type ChartState=scoped struct{
  pub ok:bool,
  pub base:IvTaylor4Mat,
  pub tangent:IvTaylor4Mat,
  pub direct:IvTaylor4Mat,
  pub amp_base:IvTaylor4Mat,
  pub amp_tangent:IvTaylor4Mat,
  pub refusal_code:i64,
};

fn cx_scalar(v:borrow IvTaylor4Mat,k:i64,n:i64)->IvTaylor4Mat{
  let re:IvTaylor4Mat=jt_scalar(v,k,0);
  let im:IvTaylor4Mat=jt_scalar(v,k+n,0);
  let out:IvTaylor4Mat=jt_zero(2,2);
  out=jt_put(out,0,0,re);
  out=jt_put(out,0,1,jt_scale(im,big("-1/1")));
  out=jt_put(out,1,0,im);
  out=jt_put(out,1,1,re);
  return out;
}

fn cx_apply(s:borrow IvTaylor4Mat,v:borrow IvTaylor4Mat,
n:i64)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(2*n,1);
  let k:i64=0;while(k<n){
    let pair:IvTaylor4Mat=jt_zero(2,1);
    pair=jt_put(pair,0,0,jt_scalar(v,k,0));
    pair=jt_put(pair,1,0,jt_scalar(v,k+n,0));
    let z:IvTaylor4Mat=jt_mul(s,pair);
    out=jt_put(out,k,0,jt_scalar(z,0,0));
    out=jt_put(out,k+n,0,jt_scalar(z,1,0));
    k=k+1;}
  return out;
}

fn direct_base(d:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(8,1);
  let k:i64=0;while(k<2){
    out=jt_put(out,k,0,jt_scalar(d,k+2,0));
    out=jt_put(out,k+4,0,jt_scalar(d,k+8,0));
    out=jt_put(out,k+2,0,jt_scalar(d,k+4,0));
    out=jt_put(out,k+6,0,jt_scalar(d,k+10,0));
    k=k+1;}
  return out;
}

fn direct_x(d:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(4,1);
  let k:i64=0;while(k<2){
    out=jt_put(out,k,0,jt_scalar(d,k,0));
    out=jt_put(out,k+2,0,jt_scalar(d,k+6,0));k=k+1;}
  return out;
}

fn direct_from_parts(x:borrow IvTaylor4Mat,
b:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(12,1);
  let k:i64=0;while(k<2){
    out=jt_put(out,k,0,jt_scalar(x,k,0));
    out=jt_put(out,k+6,0,jt_scalar(x,k+2,0));
    out=jt_put(out,k+2,0,jt_scalar(b,k,0));
    out=jt_put(out,k+8,0,jt_scalar(b,k+4,0));
    out=jt_put(out,k+4,0,jt_scalar(b,k+2,0));
    out=jt_put(out,k+10,0,jt_scalar(b,k+6,0));k=k+1;}
  return out;
}

fn chart_fail(code:i64)->ChartState{
  return new ChartState(false,jt_zero(8,1),jt_zero(8,1),
    jt_zero(12,1),jt_zero(2,2),jt_zero(2,2),code);
}

fn cx_inverse_checked(s:borrow IvTaylor4Mat)->ChartState{
  let re:IvTaylor4Mat=jt_scalar(s,0,0);
  let im:IvTaylor4Mat=jt_scalar(s,1,0);
  let den:IvTaylor4Mat=jt_add(jt_mul(re,re),jt_mul(im,im));
  let invr:IvTaylor4Result=ivtm4_solve_left(
    den,ivtm4_identity(7315,1));
  if(!invr.ok){
    let sh:IvMat=match(ivtm4_hull_checked(s)){
      some(z)=>z,none=>{return chart_fail(invr.refusal_code);}};
    let dh:IvMat=match(ivtm4_hull_checked(den)){
      some(z)=>z,none=>{return chart_fail(invr.refusal_code);}};
    let sr:Iv=ivm_at(sh,0,0);let si:Iv=ivm_at(sh,1,0);
    let dd:Iv=ivm_at(dh,0,0);
    println(strfmt(system_allocator(),
      "PROJECTIVE_PIVOT_DIAG re_lo={} re_hi={} im_lo={} im_hi={} den_lo={} den_hi={} code={}",
      [sr.lo,sr.hi,si.lo,si.hi,dd.lo,dd.hi,invr.refusal_code]));
    return chart_fail(invr.refusal_code);}
  let invden:IvTaylor4Mat=ivtm4_clone(invr.value);
  let rr:IvTaylor4Mat=jt_mul(re,invden);
  let ii:IvTaylor4Mat=jt_mul(im,invden);
  let invs:IvTaylor4Mat=jt_zero(2,2);
  invs=jt_put(invs,0,0,rr);
  invs=jt_put(invs,0,1,ii);
  invs=jt_put(invs,1,0,jt_scale(ii,big("-1/1")));
  invs=jt_put(invs,1,1,rr);
  return new ChartState(true,jt_zero(8,1),jt_zero(8,1),
    jt_zero(12,1),invs,jt_zero(2,2),0);
}

// Pivot on the first regular spin-one component (complex component 2).
// The dual scalar S+eps*T is removed from the whole filtered column.
fn project_column(base:borrow IvTaylor4Mat,
tangent:borrow IvTaylor4Mat,direct:borrow IvTaylor4Mat,
amp_base:borrow IvTaylor4Mat,amp_tangent:borrow IvTaylor4Mat)->ChartState{
  let sfull:IvTaylor4Mat=cx_scalar(base,2,4);
  let tfull:IvTaylor4Mat=cx_scalar(tangent,2,4);
  // Lohner midpoint normalization: remove only the exact Taylor centre.
  // The full shared-frequency dependence remains in the chart state.
  let s:IvTaylor4Mat=ivtm4_constant(7315,qm_clone(sfull.c0));
  let t:IvTaylor4Mat=ivtm4_constant(7315,qm_clone(tfull.c0));
  let invchart:ChartState=cx_inverse_checked(s);
  if(!invchart.ok){return chart_fail(invchart.refusal_code);}
  let invs:IvTaylor4Mat=ivtm4_clone(invchart.amp_base);
  let bn:IvTaylor4Mat=cx_apply(invs,base,4);
  let tn0:IvTaylor4Mat=jt_sub(
    tangent,cx_apply(t,bn,4));
  let tn:IvTaylor4Mat=cx_apply(invs,tn0,4);

  let db:IvTaylor4Mat=direct_base(direct);
  let dx:IvTaylor4Mat=direct_x(direct);
  let dbn:IvTaylor4Mat=cx_apply(invs,db,4);
  let dy:IvTaylor4Mat=jt_zero(4,1);
  let k:i64=0;while(k<2){
    dy=jt_put(dy,k,0,jt_scalar(dbn,k,0));
    dy=jt_put(dy,k+2,0,jt_scalar(dbn,k+4,0));k=k+1;}
  let dxn:IvTaylor4Mat=cx_apply(invs,
    jt_sub(dx,cx_apply(t,dy,2)),2);
  let dn:IvTaylor4Mat=direct_from_parts(dxn,dbn);

  let ab:IvTaylor4Mat=jt_mul(amp_base,s);
  let at:IvTaylor4Mat=jt_add(
    jt_mul(amp_tangent,s),jt_mul(amp_base,t));
  return new ChartState(true,bn,tn,dn,ab,at,0);
}

fn reconstruct_base(a:borrow IvTaylor4Mat,
b:borrow IvTaylor4Mat)->IvTaylor4Mat{return cx_apply(a,b,4);}

fn reconstruct_tangent(a:borrow IvTaylor4Mat,
at:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat,
t:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return jt_add(cx_apply(at,b,4),cx_apply(a,t,4));
}
'''


MAIN_TEMPLATE = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let initial_r:IvTaylor4Mat=jt_radius();
  let initial:LeveltData=build_levelt(w_model,initial_r);
  let base0:IvTaylor4Mat=jt_pad(initial.seed_base,@@BASE_TAIL@@);
  let tangent0:IvTaylor4Mat=jt_pad(
    initial.seed_tangent,@@TANGENT_TAIL@@);
  let direct0:IvTaylor4Mat=direct_seed_vector(base0,tangent0);
  let amp0:IvTaylor4Mat=ivtm4_identity(7315,2);
  let ampt0:IvTaylor4Mat=jt_zero(2,2);
  let chart0:ChartState=project_column(
    base0,tangent0,direct0,amp0,ampt0);
  if(!chart0.ok){
    println(strfmt(system_allocator(),
      "PROJECTIVE_REFUSAL gate=initial_chart code={}",
      [chart0.refusal_code]));return 3;}
  let base_state:IvTaylor4Mat=ivtm4_clone(chart0.base);
  let tangent_state:IvTaylor4Mat=ivtm4_clone(chart0.tangent);
  let direct_state:IvTaylor4Mat=ivtm4_clone(chart0.direct);
  let amp_base:IvTaylor4Mat=ivtm4_clone(chart0.amp_base);
  let amp_tangent:IvTaylor4Mat=ivtm4_clone(chart0.amp_tangent);
  let rho:Rat=big("1/4194304");
  let shell:i64=0;let total_panels:i64=0;
  while(shell<23){
    let h:Rat=rat_clone(rho)/rat(64,1);let panel:i64=0;
    while(panel<64){
      let center:Rat=rat(2,1)+rat_clone(rho)+rat_clone(h)/rat(2,1);
      let radius:Rat=rat_clone(h)/rat(2,1);
      let models:LeveltData=build_levelt(
        w_model,jt_radial_at(center,radius));
      let dual:DualT4=dual_series(
        models.base,models.tangent,rat_clone(h),12);
      let direct:IvTaylor4Mat=jt_series(
        models.direct,rat_clone(h),12);
      let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
        some(x)=>x,none=>{println(strfmt(system_allocator(),
          "PROJECTIVE_REFUSAL gate=coefficient_hull shell={} panel={}",
          [shell,panel]));return 3;}};
      let alpha:f64=sl_inf_norm_hi(hull);
      let scaled:f64=rat_to_f64(h)*alpha;
      let tail:f64=sl_exp_tail(scaled,13);
      if(tail<0.0||!f64_is_finite(tail)){
        println(strfmt(system_allocator(),
          "PROJECTIVE_REFUSAL gate=operator_tail shell={} panel={} scaled={}",
          [shell,panel,scaled]));return 3;}
      let bt:IvTaylor4Mat=jt_pad(dual.base,tail);
      let tt:IvTaylor4Mat=jt_pad(dual.tangent,tail);
      let dt:IvTaylor4Mat=jt_pad(direct,tail);
      let nb:IvTaylor4Mat=jt_mul(bt,base_state);
      let nt:IvTaylor4Mat=jt_add(
        jt_mul(tt,base_state),jt_mul(bt,tangent_state));
      let nd:IvTaylor4Mat=jt_mul(dt,direct_state);
      let chart:ChartState=project_column(
        nb,nt,nd,amp_base,amp_tangent);
      if(!chart.ok){
        println(strfmt(system_allocator(),
          "PROJECTIVE_REFUSAL gate=pivot_solve shell={} panel={} total_panels={} code={} scaled={} tail={}",
          [shell,panel,total_panels,chart.refusal_code,scaled,tail]));
        return 3;}
      base_state=ivtm4_clone(chart.base);
      tangent_state=ivtm4_clone(chart.tangent);
      direct_state=ivtm4_clone(chart.direct);
      amp_base=ivtm4_clone(chart.amp_base);
      amp_tangent=ivtm4_clone(chart.amp_tangent);
      let expanded:IvTaylor4Mat=direct_seed_vector(
        base_state,tangent_state);
      let overlap:bool=difference_contains_zero(expanded,direct_state);
      let width:f64=hull_width(expanded);
      let awidth:f64=hull_width(amp_base);
      let atwidth:f64=hull_width(amp_tangent);
      if(!overlap||!f64_is_finite(width)||width>1000000.0||
         !f64_is_finite(awidth)||!f64_is_finite(atwidth)||
         awidth>1000000.0||atwidth>1000000.0){
        println(strfmt(system_allocator(),
          "PROJECTIVE_REFUSAL gate=chart_width shell={} panel={} total_panels={} width={} amp_width={} amp_tangent_width={} overlap={} scaled={} tail={}",
          [shell,panel,total_panels,width,awidth,atwidth,overlap,scaled,tail]));
        return 3;}
      rho=rho+rat_clone(h);panel=panel+1;
      total_panels=total_panels+1;
    }
    println(strfmt(system_allocator(),
      "PROJECTIVE_SHELL shell={} rho={} chart_width={} tangent_width={} amp_width={} amp_tangent_width={} overlap=true",
      [shell,rat_to_f64(rho),hull_width(base_state),
       hull_width(tangent_state),hull_width(amp_base),
       hull_width(amp_tangent)]));
    shell=shell+1;
  }
  let full_base:IvTaylor4Mat=reconstruct_base(amp_base,base_state);
  let full_tangent:IvTaylor4Mat=reconstruct_tangent(
    amp_base,amp_tangent,base_state,tangent_state);
  let full_direct:IvTaylor4Mat=direct_seed_vector(
    full_base,full_tangent);
  let normalized_overlap:bool=difference_contains_zero(
    direct_seed_vector(base_state,tangent_state),direct_state);
  let final_width:f64=hull_width(full_direct);
  let pass:bool=normalized_overlap&&f64_is_finite(final_width)&&
    final_width<1000000.0;
  println(strfmt(system_allocator(),
    "PROJECTIVE_RESULT status={} shells={} panels={} rho={} r={} chart_width={} tangent_width={} amp_width={} amp_tangent_width={} reconstructed_width={} overlap={}",
    [if(pass){"PASS"}else{"REFUSED"},shell,total_panels,
     rat_to_f64(rho),2.0+rat_to_f64(rho),hull_width(base_state),
     hull_width(tangent_state),hull_width(amp_base),
     hull_width(amp_tangent),final_width,normalized_overlap]));
  return if(pass){0}else{3};
}
'''


def render_source() -> str:
    crosswalk = json.loads(INPUTS["partial_jet_crosswalk"].read_text())
    data = levelt.exact_data(crosswalk)
    tail = levelt.tail_majorant(data)
    main = MAIN_TEMPLATE.replace(
        "@@BASE_TAIL@@",
        repr(math.nextafter(float(tail["tail_base"]), math.inf)),
    ).replace(
        "@@TANGENT_TAIL@@",
        repr(math.nextafter(float(tail["tail_tangent"]), math.inf)),
    )
    return (
        multipanel.SUPPORT
        + "\n"
        + levelt.EXTRA_SUPPORT
        + "\n"
        + levelt.render_builders(data)
        + "\n"
        + multipanel.EXTRA
        + "\n"
        + CHART_SUPPORT
        + "\n"
        + main
    )


def run(command: list[str], env: dict[str, str] | None = None) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=240,
    )
    return {
        "command": " ".join(command),
        "exit": completed.returncode,
        "output": completed.stdout,
    }


def parse_output(output: str) -> dict:
    shell_pattern = re.compile(
        r"PROJECTIVE_SHELL shell=(?P<shell>\d+) rho=(?P<rho>\S+) "
        r"chart_width=(?P<chart>\S+) tangent_width=(?P<tangent>\S+) "
        r"amp_width=(?P<amp>\S+) amp_tangent_width=(?P<ampt>\S+) "
        r"overlap=(?P<overlap>true|false)"
    )
    shells = [
        {
            "shell": int(match.group("shell")),
            "rho": match.group("rho"),
            "chart_width": match.group("chart"),
            "tangent_width": match.group("tangent"),
            "amplitude_width": match.group("amp"),
            "amplitude_tangent_width": match.group("ampt"),
            "overlap": match.group("overlap") == "true",
        }
        for match in shell_pattern.finditer(output)
    ]
    result = re.search(
        r"PROJECTIVE_RESULT status=(?P<status>\w+) shells=(?P<shells>\d+) "
        r"panels=(?P<panels>\d+) rho=(?P<rho>\S+) r=(?P<r>\S+) "
        r"chart_width=(?P<chart>\S+) tangent_width=(?P<tangent>\S+) "
        r"amp_width=(?P<amp>\S+) amp_tangent_width=(?P<ampt>\S+) "
        r"reconstructed_width=(?P<reconstructed>\S+) "
        r"overlap=(?P<overlap>true|false)",
        output,
    )
    refusal = re.search(
        r"PROJECTIVE_REFUSAL gate=(?P<gate>\w+)"
        r"(?: shell=(?P<shell>\d+) panel=(?P<panel>\d+))?"
        r"(?P<rest>[^\n]*)",
        output,
    )
    if result:
        return {
            "status": result.group("status"),
            "shells": int(result.group("shells")),
            "panels": int(result.group("panels")),
            "rho": result.group("rho"),
            "r": result.group("r"),
            "chart_width": result.group("chart"),
            "tangent_width": result.group("tangent"),
            "amplitude_width": result.group("amp"),
            "amplitude_tangent_width": result.group("ampt"),
            "reconstructed_width": result.group("reconstructed"),
            "overlap": result.group("overlap") == "true",
            "shell_records": shells,
            "refusal": None,
        }
    if refusal:
        return {
            "status": "REFUSED",
            "shells": len(shells),
            "shell_records": shells,
            "refusal": {
                "gate": refusal.group("gate"),
                "shell": (
                    int(refusal.group("shell"))
                    if refusal.group("shell") is not None
                    else None
                ),
                "panel": (
                    int(refusal.group("panel"))
                    if refusal.group("panel") is not None
                    else None
                ),
                "diagnostic": refusal.group("rest").strip(),
            },
        }
    return {"status": "UNPARSED", "shell_records": shells, "refusal": None}


def document() -> dict:
    SOURCE.write_text(render_source())
    env = dict(os.environ)
    env["FORGE_LIB"] = str(multipanel.FORGE_LIB)
    compile_result = run(
        [str(multipanel.FORGE), "-o", str(BINARY), str(SOURCE)], env
    )
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = {"command": str(BINARY), "exit": None, "output": ""}
    if compile_result["exit"] == 0:
        try:
            run_result = run([str(BINARY)])
        except subprocess.TimeoutExpired as error:
            text = error.stdout or ""
            if isinstance(text, bytes):
                text = text.decode(errors="replace")
            run_result = {
                "command": str(BINARY),
                "exit": 124,
                "output": text + "\nTIMEOUT_240_SECONDS\n",
            }
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_output(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed["status"] == "PASS"
        and parsed.get("shells") == 23
        and parsed.get("panels") == 1472
        and parsed.get("overlap")
    )
    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in {**INPUTS, **CODE_INPUTS}.items()
    }
    return {
        "schema": "phase3-axial-partial-jet-horizon-projective-multipanel-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_HORIZON_PROJECTIVE_MULTIPANEL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "CERTIFIED_PROJECTIVE_HORIZON_TO_R4_PASS"
            if passed
            else "CERTIFIED_PROJECTIVE_MULTIPANEL_SHORTFALL"
        ),
        "imports": imports,
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "start_rho": "1/4194304",
            "target_rho": "2",
            "target_r": "4",
            "shells": 23,
            "panels_per_shell": 64,
            "transport_order": 12,
            "projective_pivot": "first regular spin-one component",
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
            "parsed": parsed,
        },
        "method": {
            "chart": "dual-complex pivot normalization of filtered mixed column",
            "amplitude": "separate correlated complex dual scalar product",
            "direct_control": "parallel direct regular-frame column in the same chart",
            "chart_switching": "none; fixed first regular spin-one pivot",
        },
        "claim_flags": {
            "projective_multipanel_transport_certified": passed,
            "horizon_to_r4_column_certified": passed,
            "complete_bounded_horizon_column_at_matching_radius": passed,
            "K_H_computed": False,
            "T_plus_recovered": False,
            "H4_pass_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "K_H or the endpoint normalizer shear",
            "T_plus, H4, scattering, or bounded global transport",
        ],
    }


def write() -> None:
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "phase3-axial-partial-jet-horizon-projective-receipt-v1",
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "certificate_sha256": sha256(OUTPUT),
                "commands": [
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.produce --check",
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.verify",
                    "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.test_projective",
                ],
                "claim_boundary": "projective horizon transport only; K_H/T_plus/H4/global remain open",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def materialized_document() -> dict:
    """Describe the bounded attempts without launching transport again."""
    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in {**INPUTS, **CODE_INPUTS}.items()
    }
    return {
        "schema": "phase3-axial-partial-jet-horizon-projective-multipanel-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_HORIZON_PROJECTIVE_MULTIPANEL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "CERTIFIED_PROJECTIVE_THROUGHPUT_AND_PIVOT_SHORTFALL",
        "imports": imports,
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "start_rho": "1/4194304",
            "target_rho": "2",
            "target_r": "4",
            "shells": 23,
            "panels_per_shell": 64,
            "transport_order": 12,
            "timeout_seconds": 240,
        },
        "fixed_full_pivot_attempt": {
            "status": "REFUSED",
            "gate": "pivot_solve",
            "shell": 0,
            "panel": 5,
            "total_panels": 5,
            "refusal_code": 6,
            "refusal_code_name": "IVTAY_KRAWCZYK_UNCERTIFIED",
            "scaled_local_norm": 0.08740073002218199,
            "operator_tail": 2.8063072926175013e-24,
            "pivot_hull": {
                "real": [0.3938702815041292, 1.6061297155150525],
                "imaginary": [
                    -0.002368228549123645,
                    0.0023682196089283582,
                ],
                "squared_norm": [
                    -0.5796582775285614,
                    2.579658271566925,
                ],
            },
            "provenance_note": (
                "retained parsed diagnostics from the immediately preceding "
                "materialized fixed-full-pivot run; its sequential run log "
                "was replaced by the bounded midpoint attempt"
            ),
        },
        "midpoint_lohner_attempt": {
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
            "compile_exit": 0,
            "run_exit": 124,
            "status": "TIMEOUT",
            "timeout_marker": "TIMEOUT_240_SECONDS",
            "completed_panel_diagnostics_available": False,
            "stdout_boundary": (
                "the bounded executable emitted no flushed panel record "
                "before termination"
            ),
        },
        "method": {
            "fixed_full_pivot": (
                "dual-complex projectivization using the full shared-frequency "
                "pivot"
            ),
            "midpoint_lohner": (
                "exact Taylor-centre complex scaling with frequency "
                "dependence retained in the affine state"
            ),
            "amplitude": "separate correlated complex dual scalar product",
            "direct_control": (
                "parallel direct regular-frame column in the same chart"
            ),
        },
        "claim_flags": {
            "projective_multipanel_transport_certified": False,
            "horizon_to_r4_column_certified": False,
            "complete_bounded_horizon_column_at_matching_radius": False,
            "K_H_computed": False,
            "T_plus_recovered": False,
            "H4_pass_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "a bounded projective or affine horizon-to-r4 column",
            "K_H or the endpoint normalizer shear",
            "T_plus, H4, scattering, or bounded global transport",
        ],
    }


def write_materialized() -> None:
    doc = materialized_document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": (
                    "phase3-axial-partial-jet-horizon-projective-receipt-v1"
                ),
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "certificate_sha256": sha256(OUTPUT),
                "commands": [
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.produce --check-materialized",
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.verify",
                    "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_projective_multipanel_v1.test_projective",
                ],
                "higher_tiers_not_run": (
                    "transport reproduction intentionally not rerun after "
                    "the bounded 240-second timeout"
                ),
                "claim_boundary": (
                    "throughput/pivot shortfall only; "
                    "K_H/T_plus/H4/global remain open"
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--finalize-materialized", action="store_true")
    parser.add_argument("--check-materialized", action="store_true")
    args = parser.parse_args()
    if args.finalize_materialized:
        write_materialized()
        print(materialized_document()["status"])
        return
    if args.check_materialized:
        encoded = (
            json.dumps(materialized_document(), indent=2, sort_keys=True) + "\n"
        )
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("materialized certificate drift")
        print(materialized_document()["status"])
        return
    doc = document()
    encoded = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print(doc["status"])
    else:
        write()


if __name__ == "__main__":
    main()
