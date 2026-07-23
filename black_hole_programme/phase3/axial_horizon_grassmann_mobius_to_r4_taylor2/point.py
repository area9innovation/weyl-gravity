#!/usr/bin/env python3
"""Render the sound quick point pass retaining q0 whole-cell remainders."""
from __future__ import annotations

import hashlib

from . import plane

OUTPUT = plane.produce.HERE / "plane_point_quick_4097_8192.forge"

POINT = r'''
pub type HppAttempt = scoped struct {
  pub ok: bool,
  pub state: HpState,
  pub forward_bound: Iv,
  pub inverse_bound: Iv,
  pub max_condition: f64,
};

// Sound quick evaluation at epsilon=0.  The q0 whole-cell affine remainder is
// deliberately retained, so a refusal triggers exact omega0 regeneration.
fn hpp_pointify(a:borrow IvAffineMat)->IvTaylorMat{
  let r:IvMat=ivm_zeros(a.rows,a.cols);let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    ivm_set(r,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(a.generator,a.rows,a.cols,qm_clone(a.center),
    qm_new(a.rows,a.cols),qm_new(a.rows,a.cols),r);
}

fn hpp_attempt(shell:i64,panels:i64,cell:borrow IvAffineCell,
start:borrow HpState)->HppAttempt{
  let state:HpState=new HpState(true,start.chart,ivtm_clone(start.z),
    iv_point(1.0),iv_point(1.0));
  let forward:Iv=iv_point(1.0);let inverse:Iv=iv_point(1.0);
  let max_condition:f64=1.0;let panel:i64=0;
  while(panel<panels){
    let lo:Rat=hr_shell_lo(shell);
    let wdt:Rat=(hr_panel_width(shell)*rat(256,1))/rat(panels,1);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(wdt));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(wdt));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(wdt));
    let a0:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(wdt)/rat(2,1),cell);
    let phi0:IvAffineMat=match(sl_local_transition(a0,wdt,12)){
      some(z)=>z,none=>{println(strfmt(system_allocator(),
        "POINT_ATTEMPT_REFUSE kind=local shell={} panel={} panels={}",
        [shell,panel,panels]));
        return new HppAttempt(false,hp_fail(),forward,inverse,max_condition);}};
    let sn:HpState=hp_step_any(hpp_pointify(phi0),state);
    if(!sn.ok){println(strfmt(system_allocator(),
      "POINT_ATTEMPT_REFUSE kind=mobius-all-charts shell={} panel={} panels={}",
      [shell,panel,panels]));
      return new HppAttempt(false,hp_fail(),forward,inverse,max_condition);}
    forward=iv_mul(forward,sn.forward_bound);
    inverse=iv_mul(sn.inverse_bound,inverse);
    let cond:Iv=iv_mul(sn.forward_bound,sn.inverse_bound);
    if(cond.hi>max_condition){max_condition=cond.hi;}
    state=new HpState(true,sn.chart,ivtm_clone(sn.z),
      iv_point(1.0),iv_point(1.0));
    panel=panel+1;
  }
  let alt:HpState=if(hr_norm(state.z)>=1.5){hp_best_chart(state)}
    else{new HpState(true,state.chart,ivtm_clone(state.z),
      iv_point(1.0),iv_point(1.0))};
  if(alt.ok && alt.chart!=state.chart){
    println(strfmt(system_allocator(),
      "POINT_SWITCH shell={} panel={} panels={} from={} to={}",
      [shell,panels,panels,state.chart,alt.chart]));
    forward=iv_mul(forward,alt.forward_bound);
    inverse=iv_mul(alt.inverse_bound,inverse);
    let cond:Iv=iv_mul(alt.forward_bound,alt.inverse_bound);
    if(cond.hi>max_condition){max_condition=cond.hi;}
    state=new HpState(true,alt.chart,ivtm_clone(alt.z),
      iv_point(1.0),iv_point(1.0));
  }
  let graph:IvTaylorMat=hr_graph_basis(state.z,state.chart);
  let named:IvTaylorMat=hr_rows(graph,state.chart,true);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(named,64);
  if(!rank.certified || rank.rank!=6){
    println(strfmt(system_allocator(),
      "POINT_ATTEMPT_REFUSE kind=named-rank shell={} panels={}",
      [shell,panels]));
    return new HppAttempt(false,hp_fail(),forward,inverse,max_condition);}
  return new HppAttempt(true,new HpState(true,state.chart,
    ivtm_clone(state.z),iv_point(1.0),iv_point(1.0)),
    forward,inverse,max_condition);
}

pub fn main()->i64{
  let cell:IvAffineCell=hr_cell();
  let initial:IvTaylorMat=hr_reorder_rows(
    hpp_pointify(hc_initial_model(cell)),true);
  let state:HpState=hp_from_basis(initial,11);
  if(!state.ok){println("POINT_REFUSE initial quick-whole-cell-remainder");return 3;}
  let forward_product:Iv=state.forward_bound;
  let inverse_product:Iv=state.inverse_bound;
  let max_condition:f64=iv_mul(state.forward_bound,state.inverse_bound).hi;
  let shell:i64=0;
  println("POINT_BEGIN omega=4097/8192 mode=quick-whole-cell-remainder panels=64 fallback=128 state_order=Re(P),Re(Pprime),Re(Q),Re(Qprime),Re(H1),Re(F),Im(P),Im(Pprime),Im(Q),Im(Qprime),Im(H1),Im(F)");
  while(shell<23){
    let used:i64=64;
    let attempt:HppAttempt=hpp_attempt(shell,64,cell,state);
    if(!attempt.ok){
      println(strfmt(system_allocator(),
        "POINT_FALLBACK shell={} panels=128",[shell]));
      used=128;
      attempt=hpp_attempt(shell,128,cell,state);
    }
    if(!attempt.ok){println(strfmt(system_allocator(),
      "POINT_REFUSE shell={} after-fallback=128 mode=quick-whole-cell-remainder",
      [shell]));return 3;}
    forward_product=iv_mul(forward_product,attempt.forward_bound);
    inverse_product=iv_mul(attempt.inverse_bound,inverse_product);
    if(attempt.max_condition>max_condition){
      max_condition=attempt.max_condition;}
    state=new HpState(true,attempt.state.chart,ivtm_clone(attempt.state.z),
      iv_point(1.0),iv_point(1.0));
    println(strfmt(system_allocator(),
      "POINT_SHELL shell={} panels={} chart={} rank=6 norm={} zwidth={} forward_bound={} inverse_bound={} max_local_condition={}",
      [shell,used,state.chart,hr_norm(state.z),
       hr_max_width(state.z),forward_product.hi,inverse_product.hi,
       max_condition]));
    shell=shell+1;
  }
  let block:IvTaylorMat=hr_graph_basis(state.z,state.chart);
  let named:IvTaylorMat=hr_rows(block,state.chart,true);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(named,64);
  if(!rank.certified || rank.rank!=6){println("POINT_REFUSE final-named-rank");return 3;}
  let standard:IvTaylorMat=hr_reorder_rows(block,false);
  let out0:HrSolve=hr_at_r4(standard);
  if(!out0.ok){println("POINT_REFUSE standard-r4");return 3;}
  println(strfmt(system_allocator(),
    "POINT_RESULT omega=4097/8192 generator=7315 shells=23 rank=6 chart={} norm={} width={} normalization=chart-identity original_horizon_amplitude=false forward_bound={} inverse_bound={} max_local_condition={} state_order=standard-12-real",
    [state.chart,hr_norm(state.z),hr_max_width(out0.value),
     forward_product.hi,inverse_product.hi,max_condition]));
  hr_emit(out0.value);
  println("POINT_PASS omega=4097/8192 mode=quick-whole-cell-remainder");
  return 42;
}
'''


def render() -> str:
    base = plane.render()
    marker = "pub fn main()->i64"
    if marker not in base:
        raise RuntimeError("plane main missing")
    return base.split(marker, 1)[0] + POINT


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())


if __name__ == "__main__":
    main()
