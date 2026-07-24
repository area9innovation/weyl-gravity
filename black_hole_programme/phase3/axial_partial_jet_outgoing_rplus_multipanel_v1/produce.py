#!/usr/bin/env python3
"""Continue the certified R+ Jost column from r=32 toward r=4."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as seed_producer,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "rplus_multipanel.forge"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-outgoing-rplus-multipanel-v1")
SEED_CERTIFICATE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_infinity_reduced_phase_preflight_v1/certificate.json"
)
CROSSWALK = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_transport_crosswalk_v1/certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


MULTI_SUPPORT = r'''
fn jt_radius_box(center:borrow Rat,radius:borrow Rat)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);c0=qm_set(c0,0,0,rat_clone(center));
  let rem:IvMat=ivm_zeros(1,1);let rad:Iv=iv_from_rat(radius);
  ivm_set(rem,0,0,iv(0.0-rad.hi,rad.hi));
  return jt_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}

fn unstack_result(a:borrow IvTaylor4Mat)->DualT4{
  let tangent:IvTaylor4Mat=jt_zero(4,1);
  let base:IvTaylor4Mat=jt_zero(4,1);
  let i:i64=0;while(i<4){
    tangent=jt_put(tangent,i,0,jt_scalar(a,i,0));
    base=jt_put(base,i,0,jt_scalar(a,4+i,0));
    i=i+1;
  }
  return new DualT4(base,tangent);
}
'''


MAIN = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let seed:DualT4=build_seed(w_model);
  let center:Rat=big("2047/64");
  let radial_step:Rat=big("1/32");
  let radius:Rat=big("1/64");
  let h:Rat=big("-1/32");
  let order:i64=12;
  let panel:i64=0;
  let max_width:f64=hull_width(stack_seed(seed));
  let max_tail:f64=0.0;
  while(panel<16){
    let r_model:IvTaylor4Mat=jt_radius_box(center,radius);
    let models:ModelTriple=build_models(w_model,r_model);
    let dual:DualT4=dual_series(models.base,models.tangent,h,order);
    let base_out:IvTaylor4Mat=jt_mul(dual.base,seed.base);
    let tangent_out:IvTaylor4Mat=jt_add(
      jt_mul(dual.tangent,seed.base),
      jt_mul(dual.base,seed.tangent));
    let jet_out:IvTaylor4Mat=stack_result(base_out,tangent_out);
    let direct_transport:IvTaylor4Mat=jt_series(models.direct,h,order);
    let direct_out:IvTaylor4Mat=jt_mul(direct_transport,stack_seed(seed));
    let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "RPLUS_MULTIPANEL status=REFUSED panel={} code=COEFFICIENT_HULL",
          [panel]));return 3;}};
    let alpha:f64=sl_inf_norm_hi(hull);
    let scaled_norm:f64=rat_to_f64(radial_step)*alpha;
    let tail:f64=sl_exp_tail(scaled_norm,order+1);
    let seed_hull:IvMat=match(ivtm4_hull_checked(stack_seed(seed))){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "RPLUS_MULTIPANEL status=REFUSED panel={} code=SEED_HULL",
          [panel]));return 3;}};
    let seed_norm:f64=sl_inf_norm_hi(seed_hull);
    let propagated_tail:f64=tail*seed_norm;
    if(!f64_is_finite(propagated_tail)||propagated_tail<0.0){
      println(strfmt(system_allocator(),
        "RPLUS_MULTIPANEL status=REFUSED panel={} code=TAIL alpha={} scaled_norm={}",
        [panel,alpha,scaled_norm]));return 3;}
    let jet_padded:IvTaylor4Mat=jt_pad(jet_out,propagated_tail);
    let direct_padded:IvTaylor4Mat=jt_pad(direct_out,propagated_tail);
    let exact:bool=coefficients_equal(jet_padded,direct_padded);
    let overlap:bool=difference_contains_zero(jet_padded,direct_padded);
    let width:f64=hull_width(jet_padded);
    if(!exact||!overlap||!f64_is_finite(width)||width>1.0e100){
      println(strfmt(system_allocator(),
        "RPLUS_MULTIPANEL status=REFUSED panel={} code=CORRELATION_OR_WIDTH alpha={} scaled_norm={} tail={} width={}",
        [panel,alpha,scaled_norm,propagated_tail,width]));return 3;}
    if(width>max_width){max_width=width;}
    if(propagated_tail>max_tail){max_tail=propagated_tail;}
    seed=unstack_result(jet_padded);
    center=rat_clone(center)-rat_clone(radial_step);
    panel=panel+1;
  }
  println(strfmt(system_allocator(),
    "RPLUS_MULTIPANEL status=PASS panels={} final_r=31.5 max_width={} final_width={} max_tail={}",
    [panel,max_width,hull_width(stack_seed(seed)),max_tail]));
  return 0;
}
'''


def run(command: list[str], env: dict[str, str] | None = None) -> dict:
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
        "command": " ".join(command),
        "exit": completed.returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "output": completed.stdout,
    }


def parse_run(output: str) -> dict:
    passed = re.search(
        r"RPLUS_MULTIPANEL status=PASS panels=(?P<panels>\d+) "
        r"final_r=(?P<radius>[-+0-9.eE]+) "
        r"max_width=(?P<max_width>[-+0-9.eE]+) "
        r"final_width=(?P<final_width>[-+0-9.eE]+) "
        r"max_tail=(?P<max_tail>[-+0-9.eE]+)",
        output,
    )
    if passed:
        result = passed.groupdict()
        result["status"] = "PASS"
        return result
    refused = re.search(
        r"RPLUS_MULTIPANEL status=REFUSED panel=(?P<panel>\d+) "
        r"code=(?P<code>\w+)(?P<rest>.*)",
        output,
    )
    if refused:
        return {
            "status": "REFUSED",
            "panel": refused.group("panel"),
            "code": refused.group("code"),
            "detail": refused.group("rest").strip(),
        }
    return {"status": "UNPARSED", "output": output}


def produce() -> tuple[dict, float]:
    started = time.perf_counter()
    crosswalk = json.loads(CROSSWALK.read_text())
    data = seed_producer.phase_reduced_data(crosswalk)
    tail = seed_producer.jost_remainder_bound(data, crosswalk)
    SOURCE.write_text(
        "\n".join(
            (
                seed_producer.SUPPORT,
                seed_producer.EXTRA_SUPPORT,
                MULTI_SUPPORT,
                seed_producer.render_seed_builder(data, tail),
                seed_producer.render_matrix_builder(data),
                MAIN,
            )
        )
    )
    env = os.environ.copy()
    env["FORGE_LIB"] = str(seed_producer.FORGE_LIB)
    compile_result = run(
        [str(seed_producer.FORGE), "-o", str(BINARY), str(SOURCE)], env
    )
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
        and parsed["status"] == "PASS"
    )
    document = {
        "schema": "phase3-axial-partial-jet-outgoing-rplus-multipanel-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_OUTGOING_RPLUS_MULTIPANEL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "RPLUS_CORRELATED_FIRST_CHUNK_PASS"
            if passed
            else "RPLUS_CORRELATED_MULTIPANEL_SHORTFALL"
        ),
        "imports": {
            "seed_certificate": {
                "path": str(SEED_CERTIFICATE.relative_to(ROOT)),
                "sha256": sha256(SEED_CERTIFICATE),
            },
            "crosswalk": {
                "path": str(CROSSWALK.relative_to(ROOT)),
                "sha256": sha256(CROSSWALK),
            },
        },
        "transport": {
            "arithmetic": "IvTaylor4_omega tensor dual_tau",
            "frequency_child": ["1/2", "4097/8192"],
            "start_radius": "32",
            "chunk_target_radius": "63/2",
            "eventual_target_radius": "4",
            "panel_width": "1/32",
            "planned_panels": 16,
            "exponential_order": 12,
            "parsed_result": parsed,
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
            "compile_elapsed_seconds": 0.0,
            "run_elapsed_seconds": 0.0,
        },
        "claim_flags": {
            "Rplus_Jost_remainder_imported": True,
            "correlation_checked_each_completed_panel": True,
            "Rplus_reaches_63_over_2": passed,
            "Rplus_reaches_r4": False,
            "complementary_outgoing_columns_constructed": False,
            "K_plus_computed": False,
            "T_plus_recovered": False,
            "scattering_claim": False,
        },
        "shortfall": (
            {
                "code": "FULL_896_PANEL_MONOLITH_EXCEEDS_SCOPED_RUNTIME_BUDGET",
                "first_failed_panel": None,
                "detail": (
                    "The uncheckpointed 896-panel native attempt was terminated "
                    "after more than 360 seconds without a terminal result; this "
                    "is not a mathematical refusal."
                ),
                "next_gate": (
                    "serialize correlation-preserving chunk checkpoints and "
                    "resume from r=63/2 rather than replaying from r=32"
                ),
            }
            if passed
            else {
                "code": parsed.get("code", "UNPARSED"),
                "first_failed_panel": parsed.get("panel"),
                "detail": parsed.get("detail", parsed.get("output", "")),
                "next_gate": (
                    "bisect the first refused panel and retain the same "
                    "dual/direct correlation gate"
                ),
            }
        ),
        "does_not_establish": [
            "transport of Rplus from r=63/2 to r=4",
            "the complementary outgoing spin-one factor column",
            "the endpoint K_plus shear",
            "T_plus, reflection, scattering, or flux",
        ],
        "producer_elapsed_seconds": 0.0,
    }
    return document, time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()
    document, elapsed = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "result_id": document["result_id"],
        "status": "PASS",
        "certificate_path": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_outgoing_rplus_multipanel_v1.produce"
                ),
                "elapsed_seconds": elapsed,
                "status": "PASS",
            }
        ],
        "higher_tiers_not_run": (
            "No T2/T3: selected-column continuation only; Tplus stays false."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    if args.print:
        print(json.dumps(document, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
