#!/usr/bin/env python3
"""One-chunk throughput/width probe for the correlated Bplus transport."""
from __future__ import annotations

import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1 import (
    produce as prefix,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1 import (
    produce as render,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "probe.forge"
RUN = HERE / "probe_run.txt"
BINARY = Path("/tmp/axial-bplus4-probe")
INPUT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_moving_frame_r31_v1/checkpoint.json"
)


def zero_model(rows: int, cols: int) -> dict:
    return {
        "schema": "ivtaylor-degree4-v1",
        "generator": 7315,
        "degree": 4,
        "rows": rows,
        "cols": cols,
        "refusal_code": 0,
        "coefficients": [
            [["0" for _ in range(cols)] for _ in range(rows)]
            for _ in range(5)
        ],
        "remainder_bits": [
            [["0000000000000000", "0000000000000000"]
             for _ in range(cols)]
            for _ in range(rows)
        ],
    }


def merge(models: dict) -> tuple[dict, dict]:
    base = zero_model(8, 2)
    tangent = zero_model(8, 2)
    r_base = models["R_base"]
    r_tangent = models["R_tangent_moving"]
    s_base = models["S_base_core"]
    s_tangent = models["S_tangent_moving_core"]
    r_rows = (0, 1, 4, 5)
    for degree in range(5):
        for source, target in enumerate(r_rows):
            base["coefficients"][degree][target][0] = (
                r_base["coefficients"][degree][source][0]
            )
            tangent["coefficients"][degree][target][0] = (
                r_tangent["coefficients"][degree][source][0]
            )
        for row in range(8):
            base["coefficients"][degree][row][1] = (
                s_base["coefficients"][degree][row][0]
            )
            tangent["coefficients"][degree][row][1] = (
                s_tangent["coefficients"][degree][row][0]
            )
    for source, target in enumerate(r_rows):
        base["remainder_bits"][target][0] = deepcopy(
            r_base["remainder_bits"][source][0]
        )
        tangent["remainder_bits"][target][0] = deepcopy(
            r_tangent["remainder_bits"][source][0]
        )
    for row in range(8):
        base["remainder_bits"][row][1] = deepcopy(
            s_base["remainder_bits"][row][0]
        )
        if row not in (2, 3, 6, 7):
            tangent["remainder_bits"][row][1] = deepcopy(
                s_tangent["remainder_bits"][row][0]
            )
    return base, tangent


SUPPORT = r'''
fn bc_stack(tangent:borrow IvTaylor4Mat,
base:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(16,2);let i:i64=0;while(i<8){
    let j:i64=0;while(j<2){
      out=sj_put(out,i,j,sj_scalar(tangent,i,j));
      out=sj_put(out,8+i,j,sj_scalar(base,i,j));j=j+1;}i=i+1;}return out;
}
fn bc_unstack_tangent(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,2);let i:i64=0;while(i<8){
    let j:i64=0;while(j<2){out=sj_put(out,i,j,sj_scalar(a,i,j));
      j=j+1;}i=i+1;}return out;
}
fn bc_unstack_base(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=sj_zero(8,2);let i:i64=0;while(i<8){
    let j:i64=0;while(j<2){out=sj_put(out,i,j,sj_scalar(a,8+i,j));
      j=j+1;}i=i+1;}return out;
}
fn bc_radius(center:borrow Rat,radius:borrow Rat)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);c0=qm_set(c0,0,0,rat_clone(center));
  let rem:IvMat=ivm_zeros(1,1);let rad:Iv=iv_from_rat(radius);
  ivm_set(rem,0,0,iv(0.0-rad.hi,rad.hi));
  return sj_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}
'''


MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let center:Rat=big("495/16");let h:Rat=big("-1/8");
  let panel:i64=0;let max_tail:f64=0.0;let max_width:f64=0.0;
  while(panel<1){
    let models:ScModels=sc_build_models(w,bc_radius(center,big("1/16")));
    let dual:ScModels=sc_dual_series(models.base,models.tangent,h,96);
    let base_out:IvTaylor4Mat=sj_mul(dual.base,base);
    let tangent_out:IvTaylor4Mat=sc_add(
      sj_mul(dual.tangent,base),sj_mul(dual.base,tangent_n));
    let jet:IvTaylor4Mat=bc_stack(tangent_out,base_out);
    let direct:IvTaylor4Mat=sj_mul(
      sc_series(models.direct,h,96),bc_stack(tangent_n,base));
    let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
      some(x)=>x,none=>{println("PROBE status=REFUSED code=MODEL");return 3;}};
    let sh:IvMat=match(ivtm4_hull_checked(bc_stack(tangent_n,base))){
      some(x)=>x,none=>{println("PROBE status=REFUSED code=SEED");return 3;}};
    let tail:f64=sc_tail(sc_norm(mh)/8.0,97)*sc_norm(sh);
    if(tail<0.0||!f64_is_finite(tail)){
      println(strfmt(system_allocator(),"PROBE status=REFUSED panel={} code=TAIL",
        [panel]));return 3;}
    let jp:IvTaylor4Mat=sc_pad(jet,tail);
    let dp:IvTaylor4Mat=sc_pad(direct,tail);
    if(!sj_coefficients_equal(jp,dp)||!sc_contains_zero(jp,dp)){
      println(strfmt(system_allocator(),
        "PROBE status=REFUSED panel={} code=CORRELATION",[panel]));return 3;}
    tangent_n=bc_unstack_tangent(jp);base=bc_unstack_base(jp);
    let width:f64=sj_width(match(ivtm4_hull_checked(jp)){
      some(x)=>x,none=>{trap();}});
    println(strfmt(system_allocator(),
      "PROBE_PANEL panel={} tail={} width={}",[panel,tail,width]));
    if(!f64_is_finite(width)||width>1.0e100){
      println(strfmt(system_allocator(),"PROBE status=REFUSED panel={} code=WIDTH",
        [panel]));return 3;}
    if(width>max_width){max_width=width;}if(tail>max_tail){max_tail=tail;}
    center=rat_clone(center)-big("1/8");panel=panel+1;
  }
  let tangent:IvTaylor4Mat=sc_scale(tangent_n,big("512"));
  sr_emit("FINAL_BASE",base);sr_emit("FINAL_TANGENT",tangent);
  println(strfmt(system_allocator(),
    "PROBE status=PASS panels={} final_r=247/8 max_tail={} max_width={}",
    [panel,max_tail,max_width]));
  return 0;
}
'''


def main() -> None:
    payload = json.loads(INPUT.read_text())["payload"]
    base, tangent = merge(payload["models"])
    SOURCE.write_text(
        "\n".join(
            (
                prefix.strip_predecessor(),
                render.render_model("initial_base", base),
                render.render_model("initial_tangent", tangent),
                SUPPORT,
                MAIN,
            )
        )
    )
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    subprocess.run(
        [str(jet.FORGE), "-o", str(BINARY), str(SOURCE)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    completed = subprocess.run(
        [str(BINARY)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=180,
    )
    RUN.write_text(completed.stdout)
    print(completed.stdout.splitlines()[-1])
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
