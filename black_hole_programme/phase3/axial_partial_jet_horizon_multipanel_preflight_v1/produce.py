#!/usr/bin/env python3
"""Attempt adaptive Levelt/partial-jet transport from the horizon to r=4."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_horizon_spin_one_levelt_v1 import (
    produce as levelt,
)
from black_hole_programme.phase3.axial_partial_jet_transport_preflight_v1.produce import (
    FORGE,
    FORGE_LIB,
    SUPPORT,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE = HERE / "multipanel_levelt.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-horizon-multipanel-v1")
INPUTS = {
    "spin_one_levelt": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_spin_one_levelt_v1/certificate.json"
    ),
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
}
CODE_INPUTS = {
    "spin_one_levelt_producer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_spin_one_levelt_v1/produce.py"
    ),
    "mixed_transport_preflight_producer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_preflight_v1/produce.py"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


EXTRA = r'''
fn jt_radial_at(center:borrow Rat,radius:borrow Rat)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);
  c0=qm_set(c0,0,0,rat_clone(center));
  let rem:IvMat=ivm_zeros(1,1);
  let rad:f64=rat_to_f64(radius);
  ivm_set(rem,0,0,iv(0.0-rad,rad));
  return jt_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}
'''


MAIN_TEMPLATE = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let initial_r:IvTaylor4Mat=jt_radius();
  let initial:LeveltData=build_levelt(w_model,initial_r);
  let base_state:IvTaylor4Mat=jt_pad(initial.seed_base,@@BASE_TAIL@@);
  let tangent_state:IvTaylor4Mat=jt_pad(
    initial.seed_tangent,@@TANGENT_TAIL@@);
  let direct_state:IvTaylor4Mat=direct_seed_vector(
    base_state,tangent_state);
  let rho:Rat=big("1/4194304");
  let shell:i64=0;
  let total_panels:i64=0;
  while(shell<23){
    let h:Rat=rat_clone(rho)/rat(4,1);
    let panel:i64=0;
    while(panel<4){
      let center:Rat=rat(2,1)+rat_clone(rho)+rat_clone(h)/rat(2,1);
      let radius:Rat=rat_clone(h)/rat(2,1);
      let r_model:IvTaylor4Mat=jt_radial_at(center,radius);
      let models:LeveltData=build_levelt(w_model,r_model);
      let dual:DualT4=dual_series(
        models.base,models.tangent,rat_clone(h),24);
      let direct:IvTaylor4Mat=jt_series(
        models.direct,rat_clone(h),24);
      let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
        some(x)=>x,none=>{
          println(strfmt(system_allocator(),
            "MULTIPANEL_REFUSAL gate=coefficient_hull shell={} panel={}",
            [shell,panel]));return 3;}};
      let alpha:f64=sl_inf_norm_hi(hull);
      let scaled:f64=rat_to_f64(h)*alpha;
      let tail:f64=sl_exp_tail(scaled,25);
      if(tail<0.0||!f64_is_finite(tail)){
        println(strfmt(system_allocator(),
          "MULTIPANEL_REFUSAL gate=operator_tail shell={} panel={} alpha={} scaled={}",
          [shell,panel,alpha,scaled]));return 3;
      }
      let base_transport:IvTaylor4Mat=jt_pad(dual.base,tail);
      let tangent_transport:IvTaylor4Mat=jt_pad(dual.tangent,tail);
      let direct_transport:IvTaylor4Mat=jt_pad(direct,tail);
      let next_base:IvTaylor4Mat=jt_mul(base_transport,base_state);
      let next_tangent:IvTaylor4Mat=jt_add(
        jt_mul(tangent_transport,base_state),
        jt_mul(base_transport,tangent_state));
      let next_direct:IvTaylor4Mat=jt_mul(
        direct_transport,direct_state);
      base_state=next_base;
      tangent_state=next_tangent;
      direct_state=next_direct;
      let expanded:IvTaylor4Mat=direct_seed_vector(
        base_state,tangent_state);
      let overlap:bool=difference_contains_zero(expanded,direct_state);
      let width:f64=hull_width(expanded);
      if(!overlap||!f64_is_finite(width)||width>1000000.0){
        println(strfmt(system_allocator(),
          "MULTIPANEL_REFUSAL gate=state_width shell={} panel={} total_panels={} width={} overlap={} scaled={} tail={}",
          [shell,panel,total_panels,width,overlap,scaled,tail]));
        return 3;
      }
      rho=rho+rat_clone(h);
      panel=panel+1;
      total_panels=total_panels+1;
    }
    println(strfmt(system_allocator(),
      "MULTIPANEL_SHELL shell={} rho={} width={} direct_width={}",
      [shell,rat_to_f64(rho),hull_width(direct_seed_vector(
       base_state,tangent_state)),hull_width(direct_state)]));
    shell=shell+1;
  }
  let final_overlap:bool=difference_contains_zero(
    direct_seed_vector(base_state,tangent_state),direct_state);
  println(strfmt(system_allocator(),
    "MULTIPANEL_RESULT status={} shells={} panels={} rho={} r={} width={} tangent_width={} overlap={}",
    [if(final_overlap){"PASS"}else{"REFUSED"},shell,total_panels,
     rat_to_f64(rho),2.0+rat_to_f64(rho),hull_width(base_state),
     hull_width(tangent_state),final_overlap]));
  return if(final_overlap){0}else{3};
}
'''


def render_source() -> str:
    crosswalk = json.loads(INPUTS["partial_jet_crosswalk"].read_text())
    data = levelt.exact_data(crosswalk)
    tail = levelt.tail_majorant(data)
    base_tail = math.nextafter(float(tail["tail_base"]), math.inf)
    tangent_tail = math.nextafter(
        float(tail["tail_tangent"]), math.inf
    )
    main = MAIN_TEMPLATE.replace("@@BASE_TAIL@@", repr(base_tail)).replace(
        "@@TANGENT_TAIL@@", repr(tangent_tail)
    )
    return (
        SUPPORT
        + "\n"
        + levelt.EXTRA_SUPPORT
        + "\n"
        + levelt.render_builders(data)
        + "\n"
        + EXTRA
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
        timeout=120,
    )
    return {
        "command": " ".join(command),
        "exit": completed.returncode,
        "output": completed.stdout,
    }


def parse_output(output: str) -> dict:
    result = re.search(
        r"MULTIPANEL_RESULT status=(?P<status>\w+) shells=(?P<shells>\d+) "
        r"panels=(?P<panels>\d+) rho=(?P<rho>[-+0-9.eE]+) "
        r"r=(?P<r>[-+0-9.eE]+) width=(?P<width>[-+0-9.eE]+) "
        r"tangent_width=(?P<tangent>[-+0-9.eE]+) "
        r"overlap=(?P<overlap>true|false)",
        output,
    )
    refusal = re.search(
        r"MULTIPANEL_REFUSAL gate=(?P<gate>\w+) shell=(?P<shell>\d+) "
        r"panel=(?P<panel>\d+)(?P<rest>[^\n]*)",
        output,
    )
    shells = [
        {
            "shell": int(match.group("shell")),
            "rho": match.group("rho"),
            "width": match.group("width"),
            "direct_width": match.group("direct"),
        }
        for match in re.finditer(
            r"MULTIPANEL_SHELL shell=(?P<shell>\d+) "
            r"rho=(?P<rho>[-+0-9.eE]+) width=(?P<width>[-+0-9.eE]+) "
            r"direct_width=(?P<direct>[-+0-9.eE]+)",
            output,
        )
    ]
    if result:
        return {
            "status": result.group("status"),
            "shells": int(result.group("shells")),
            "panels": int(result.group("panels")),
            "rho": result.group("rho"),
            "r": result.group("r"),
            "width": result.group("width"),
            "tangent_width": result.group("tangent"),
            "overlap": result.group("overlap") == "true",
            "shell_records": shells,
            "refusal": None,
        }
    if refusal:
        diagnostic = refusal.group("rest").strip()
        details: dict[str, int | float | bool | str] = {}
        for key, value in re.findall(r"(\w+)=([^\s]+)", diagnostic):
            if value in {"true", "false"}:
                details[key] = value == "true"
            elif re.fullmatch(r"\d+", value):
                details[key] = int(value)
            else:
                try:
                    details[key] = float(value)
                except ValueError:
                    details[key] = value
        return {
            "status": "REFUSED",
            "shells": len(shells),
            "panels": None,
            "shell_records": shells,
            "refusal": {
                "gate": refusal.group("gate"),
                "shell": int(refusal.group("shell")),
                "panel": int(refusal.group("panel")),
                "diagnostic": diagnostic,
                "details": details,
            },
        }
    return {"status": "UNPARSED", "shell_records": shells, "refusal": None}


def document() -> dict:
    SOURCE.write_text(render_source())
    env = dict(os.environ)
    env["FORGE_LIB"] = str(FORGE_LIB)
    compile_result = run([str(FORGE), "-o", str(BINARY), str(SOURCE)], env)
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = {"command": str(BINARY), "exit": None, "output": ""}
    if compile_result["exit"] == 0:
        try:
            run_result = run([str(BINARY)])
        except subprocess.TimeoutExpired as error:
            run_result = {
                "command": str(BINARY),
                "exit": 124,
                "output": (error.stdout or "") + "\nTIMEOUT_120_SECONDS\n",
            }
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_output(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed["status"] == "PASS"
        and parsed.get("shells") == 23
        and parsed.get("overlap")
    )
    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in {**INPUTS, **CODE_INPUTS}.items()
    }
    status = (
        "CERTIFIED_HORIZON_TO_R4_REGULAR_PARTIAL_JET_PASS"
        if passed
        else "CERTIFIED_MULTIPANEL_REGULAR_PARTIAL_JET_SHORTFALL"
    )
    return {
        "schema": "phase3-axial-partial-jet-horizon-multipanel-preflight-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_HORIZON_MULTIPANEL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": status,
        "imports": imports,
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "start_rho": "1/4194304",
            "target_rho": "2",
            "target_r": "4",
            "geometric_shells": 23,
            "panels_per_shell": 4,
            "transport_order": 24,
            "width_refusal_threshold": 1000000,
            "arithmetic": "regular Levelt IvTaylor4_omega tensor dual_tau",
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
            "adaptive_panels": "four equal panels per rho-doubling shell",
            "phase_frame": "spin-two moving phase plus spin-one Levelt frame",
            "partial_jet_correlation": "base/tangent propagated in dual arithmetic",
            "direct_control": "parallel regular-frame 12x12 six-state column",
            "reconditioning": "phase/Levelt state scaling only; no nonlinear projective QR reset",
        },
        "claim_flags": {
            "horizon_to_r4_column_certified": passed,
            "multipanel_transport_certified": passed,
            "K_H_computed": False,
            "complete_bounded_horizon_column_at_matching_radius": passed,
            "T_plus_recovered": False,
            "H4_pass_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "K_H or a tau-analytic endpoint normalizer identification",
            "T_plus, H4, scattering, or bounded global transport",
        ],
    }


def write() -> None:
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "phase3-axial-partial-jet-horizon-multipanel-receipt-v1",
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "certificate_sha256": sha256(OUTPUT),
                "commands": [
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_multipanel_preflight_v1.produce --check",
                    "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_multipanel_preflight_v1.verify",
                    "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_multipanel_preflight_v1.test_multipanel",
                ],
                "claim_boundary": "multipanel preflight only; K_H/T_plus/H4/global remain open",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
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
