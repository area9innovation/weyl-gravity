#!/usr/bin/env python3
"""Render the q0 plane-only Taylor2 Grassmann successor."""
from __future__ import annotations

import hashlib

from . import produce

OUTPUT = produce.HERE / "plane_c00_taylor2.forge"

PLANE = r'''
pub type HpState = scoped struct {
  pub ok: bool,
  pub chart: i64,
  pub z: IvTaylorMat,
  pub forward_bound: Iv,
  pub inverse_bound: Iv,
};

pub type HpBounds = value struct {
  pub ok: bool,
  pub forward: Iv,
  pub inverse: Iv,
};

fn hp_fail()->HpState{
  return new HpState(false,-1,hr_zero(),iv_point(0.0),iv_point(0.0));}

fn hp_inf_bound(a:borrow IvTaylorMat)->Iv{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let s:Iv=iv_point(0.0);let j:i64=0;
    while(j<a.cols){s=iv_add(s,iv_abs(ivm_at(h,i,j)));j=j+1;}
    if(s.hi>best){best=s.hi;}i=i+1;}
  return iv(0.0,best);
}

fn hp_bounds(a:borrow IvTaylorMat)->HpBounds{
  if(a.rows!=6 || a.cols!=6){return HpBounds(false,iv_point(0.0),iv_point(0.0));}
  let inv:IvTaylorResult=ivtm_solve_left(
    a,ivtm_identity(a.generator,6));
  if(!inv.ok){return HpBounds(false,iv_point(0.0),iv_point(0.0));}
  return HpBounds(true,hp_inf_bound(a),hp_inf_bound(inv.value));
}

fn hp_from_basis(y:borrow IvTaylorMat,chart:i64)->HpState{
  let u:IvTaylorMat=hr_rows(y,chart,true);
  let v:IvTaylorMat=hr_rows(y,chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=6){return hp_fail();}
  let bounds:HpBounds=hp_bounds(u);
  if(!bounds.ok){return hp_fail();}
  let z:HrSolve=hr_right(v,u);
  if(!z.ok || hr_norm(z.value)>=2.0){return hp_fail();}
  return new HpState(true,chart,ivtm_clone(z.value),
    bounds.forward,bounds.inverse);
}

fn hp_rechart(s:borrow HpState,new_chart:i64)->HpState{
  if(!s.ok){return hp_fail();}
  if(new_chart==s.chart){
    return new HpState(true,s.chart,ivtm_clone(s.z),
      iv_point(1.0),iv_point(1.0));}
  let g:IvTaylorMat=hr_graph_basis(s.z,s.chart);
  return hp_from_basis(g,new_chart);
}

fn hp_best_chart(s:borrow HpState)->HpState{
  let best:HpState=new HpState(true,s.chart,ivtm_clone(s.z),
    iv_point(1.0),iv_point(1.0));
  let c:i64=0;while(c<20){
    let cand:HpState=hp_rechart(s,c);
    if(cand.ok && hr_norm(cand.z)<hr_norm(best.z)){
      best=new HpState(true,cand.chart,ivtm_clone(cand.z),
        cand.forward_bound,cand.inverse_bound);
    }
    c=c+1;
  }
  return best;
}

fn hp_step(phi:borrow IvTaylorMat,s:borrow HpState)->HpState{
  let pii:IvTaylorMat=hr_block(phi,s.chart,true,true);
  let pij:IvTaylorMat=hr_block(phi,s.chart,true,false);
  let pji:IvTaylorMat=hr_block(phi,s.chart,false,true);
  let pjj:IvTaylorMat=hr_block(phi,s.chart,false,false);
  let az:IvTaylorResult=ivtm_mul_checked(pij,s.z);
  let bz:IvTaylorResult=ivtm_mul_checked(pjj,s.z);
  if(!az.ok || !bz.ok){return hp_fail();}
  let m0:IvTaylorResult=ivtm_add_checked(pii,az.value);
  let n0:IvTaylorResult=ivtm_add_checked(pji,bz.value);
  if(!m0.ok || !n0.ok){return hp_fail();}
  let m:IvTaylorResult=ivtm_rebase_dyadic(m0.value,128);
  let n:IvTaylorResult=ivtm_rebase_dyadic(n0.value,128);
  if(!m.ok || !n.ok){return hp_fail();}
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(m.value,64);
  if(!rank.certified || rank.rank!=6){return hp_fail();}
  let bounds:HpBounds=hp_bounds(m.value);
  if(!bounds.ok){return hp_fail();}
  let z:HrSolve=hr_right(n.value,m.value);
  if(!z.ok || hr_norm(z.value)>=2.0){return hp_fail();}
  return new HpState(true,s.chart,ivtm_clone(z.value),
    bounds.forward,bounds.inverse);
}

fn hp_step_any(phi:borrow IvTaylorMat,s:borrow HpState)->HpState{
  let direct:HpState=hp_step(phi,s);
  if(direct.ok){
    return new HpState(true,direct.chart,ivtm_clone(direct.z),
      direct.forward_bound,direct.inverse_bound);}
  let best:HpState=hp_fail();let c:i64=0;while(c<20){
    let charted:HpState=hp_rechart(s,c);
    if(charted.ok){
      let stepped:HpState=hp_step(phi,charted);
      if(stepped.ok && (!best.ok || hr_norm(stepped.z)<hr_norm(best.z))){
        best=new HpState(true,stepped.chart,ivtm_clone(stepped.z),
          iv_mul(stepped.forward_bound,charted.forward_bound),
          iv_mul(charted.inverse_bound,stepped.inverse_bound));
      }
    }
    c=c+1;
  }
  return best;
}

pub fn main()->i64{
  let cell:IvAffineCell=hr_cell();
  let initial:IvTaylorMat=hr_reorder_rows(
    ivtm_from_affine(hc_initial_model(cell)),true);
  let state:HpState=hp_from_basis(initial,11);
  if(!state.ok){println("PLANE_REFUSE initial");return 3;}
  let forward_product:Iv=state.forward_bound;
  let inverse_product:Iv=state.inverse_bound;
  let max_condition:f64=
    iv_mul(state.forward_bound,state.inverse_bound).hi;
  let switches:i64=0;let shell:i64=0;
  println("PLANE_BEGIN q=0 normalization=chart-identity");
  while(shell<23){
    let panel:i64=0;while(panel<256){
      let lo:Rat=hr_shell_lo(shell);
      let wdt:Rat=hr_panel_width(shell);
      let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(wdt));
      let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(wdt));
      let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(wdt));
      let a:IvAffineMat=hc_runtime(
        xc,iv(ta.lo,tb.hi),rat_clone(wdt)/rat(2,1),cell);
      let phi0:IvAffineMat=match(sl_local_transition(a,wdt,12)){
        some(z)=>z,none=>{println(strfmt(system_allocator(),
          "PLANE_REFUSE local shell={} panel={}",[shell,panel]));return 3;}};
      let sn:HpState=hp_step_any(ivtm_from_affine(phi0),state);
      if(!sn.ok){println(strfmt(system_allocator(),
        "PLANE_REFUSE all-charts shell={} panel={}",[shell,panel]));return 3;}
      if(sn.chart!=state.chart){
        println(strfmt(system_allocator(),
          "PLANE_SWITCH shell={} panel={} from={} to={}",
          [shell,panel,state.chart,sn.chart]));switches=switches+1;}
      forward_product=iv_mul(forward_product,sn.forward_bound);
      inverse_product=iv_mul(sn.inverse_bound,inverse_product);
      let cond:Iv=iv_mul(sn.forward_bound,sn.inverse_bound);
      if(cond.hi>max_condition){max_condition=cond.hi;}
      state=new HpState(true,sn.chart,ivtm_clone(sn.z),
        iv_point(1.0),iv_point(1.0));
      if((panel+1)%64==0){println(strfmt(system_allocator(),
        "PLANE_HEARTBEAT shell={} panel={} chart={} norm={} zwidth={}",
        [shell,panel+1,state.chart,hr_norm(state.z),
         hr_max_width(state.z)]));}
      panel=panel+1;
    }
    let alt:HpState=if(hr_norm(state.z)>=1.5){hp_best_chart(state)}
      else{new HpState(true,state.chart,ivtm_clone(state.z),
        iv_point(1.0),iv_point(1.0))};
    if(alt.ok && alt.chart!=state.chart){
      println(strfmt(system_allocator(),
        "PLANE_SWITCH shell={} panel=256 from={} to={}",
        [shell,state.chart,alt.chart]));
      forward_product=iv_mul(forward_product,alt.forward_bound);
      inverse_product=iv_mul(alt.inverse_bound,inverse_product);
      let cond:Iv=iv_mul(alt.forward_bound,alt.inverse_bound);
      if(cond.hi>max_condition){max_condition=cond.hi;}
      state=new HpState(true,alt.chart,ivtm_clone(alt.z),
        iv_point(1.0),iv_point(1.0));
      switches=switches+1;
    }
    let graph:IvTaylorMat=hr_graph_basis(state.z,state.chart);
    let named_minor:IvTaylorMat=hr_rows(graph,state.chart,true);
    let rank:IvTaylorRank=ivtm_full_column_rank_cells(named_minor,64);
    if(!rank.certified || rank.rank!=6){
      println(strfmt(system_allocator(),
        "PLANE_REFUSE normalized-rank shell={}",[shell]));return 3;}
    println(strfmt(system_allocator(),
      "PLANE_SHELL shell={} chart={} rank={} norm={} zwidth={} switches={} forward_bound={} inverse_bound={} max_local_condition={}",
      [shell,state.chart,rank.rank,hr_norm(state.z),
       hr_max_width(state.z),switches,forward_product.hi,
       inverse_product.hi,max_condition]));
    shell=shell+1;
  }
  let block:IvTaylorMat=hr_graph_basis(state.z,state.chart);
  let standard:IvTaylorMat=hr_reorder_rows(block,false);
  let out0:HrSolve=hr_at_r4(standard);
  if(!out0.ok){println("PLANE_REFUSE standard-r4");return 3;}
  let named_minor:IvTaylorMat=hr_rows(block,state.chart,true);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(named_minor,64);
  if(!rank.certified || rank.rank!=6){
    println("PLANE_REFUSE final-rank");return 3;}
  println(strfmt(system_allocator(),
    "PLANE_RESULT q=0 generator=7315 shells=23 rank={} chart={} switches={} norm={} width={} normalization=chart-identity forward_bound={} inverse_bound={} max_local_condition={}",
    [rank.rank,state.chart,switches,hr_norm(state.z),
     hr_max_width(out0.value),forward_product.hi,
     inverse_product.hi,max_condition]));
  hr_emit(out0.value);
  println("PLANE_PASS q=0 original_horizon_amplitude=false");
  return 42;
}
'''


def render() -> str:
    base = produce.render()
    marker = "fn hr_run(q:i64)->bool"
    if marker not in base:
        raise RuntimeError("Taylor2 run suffix missing")
    return base.split(marker, 1)[0] + PLANE


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())


if __name__ == "__main__":
    main()
