#!/usr/bin/env python3
"""Render the bounded shell-2 structural rescue preflight."""
from __future__ import annotations

import hashlib
from pathlib import Path

from . import produce

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "rescue_shell2.forge"

RESCUE = r'''
fn hs_scan(stage:i64,s:borrow HrState)->void{
  let g:IvTaylorMat=hr_graph_basis(s.z,s.chart);
  let c:i64=0;while(c<20){
    let u:IvTaylorMat=hr_rows(g,c,true);
    let ur:IvTaylorRank=ivtm_full_column_rank_cells(u,64);
    let cand:HrState=hr_rechart(s,c);
    let ac:bool=false;let arank:i64=0;
    if(cand.ok){
      let ar:IvTaylorRank=ivtm_full_column_rank_cells(cand.amplitude,64);
      ac=ar.certified;arank=ar.rank;
    }
    println(strfmt(system_allocator(),
      "CHART_SCAN stage={} chart={} minor_cert={} minor_rank={} candidate={} norm={} amplitude_cert={} amplitude_rank={}",
      [stage,c,ur.certified,ur.rank,cand.ok,
       if(cand.ok){hr_norm(cand.z)}else{-1.0},ac,arank]));
    c=c+1;
  }
}

fn hs_rebase(stage:i64,s:borrow HrState)->void{
  let bits:i64=128;while(bits<=512){
    let rb:IvTaylorResult=ivtm_rebase_dyadic(s.amplitude,bits);
    let cert:bool=false;let rank:i64=0;
    if(rb.ok){
      let ar:IvTaylorRank=ivtm_full_column_rank_cells(rb.value,64);
      cert=ar.certified;rank=ar.rank;
    }
    println(strfmt(system_allocator(),
      "REBASE_SCAN stage={} bits={} ok={} amplitude_cert={} amplitude_rank={}",
      [stage,bits,rb.ok,cert,rank]));
    bits=bits*2;
  }
}

fn hs_step(shell:i64,panel:i64,panels:i64,cell:borrow IvAffineCell,
s:borrow HrState)->HrState{
  let lo:Rat=hr_shell_lo(shell);
  let wdt:Rat=(hr_panel_width(shell)*rat(256,1))/rat(panels,1);
  let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(wdt));
  let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(wdt));
  let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(wdt));
  let a:IvAffineMat=hc_runtime(
    xc,iv(ta.lo,tb.hi),rat_clone(wdt)/rat(2,1),cell);
  let phi0:IvAffineMat=match(sl_local_transition(a,wdt,12)){
    some(z)=>z,none=>{return hr_fail();}};
  let phi:IvTaylorMat=ivtm_from_affine(phi0);
  return hr_step_any(phi,s);
}

pub fn main()->i64{
  let cell:IvAffineCell=hr_cell();
  let initial:IvTaylorMat=hr_reorder_rows(
    ivtm_from_affine(hc_initial_model(cell)),true);
  let state:HrState=hr_from_basis(initial,11);
  if(!state.ok){println("RESCUE_REFUSE initial");return 3;}
  let shell:i64=0;while(shell<2){
    let panel:i64=0;while(panel<256){
      let sn:HrState=hs_step(shell,panel,256,cell,state);
      if(!sn.ok || !hr_gauge_covariant(sn)){
        println(strfmt(system_allocator(),
          "RESCUE_REFUSE prefix shell={} panel={}",[shell,panel]));return 3;}
      state=new HrState(true,sn.chart,ivtm_clone(sn.z),
        ivtm_clone(sn.amplitude));
      panel=panel+1;
    }
    let ar:IvTaylorRank=ivtm_full_column_rank_cells(state.amplitude,64);
    if(!ar.certified || ar.rank!=6){
      println(strfmt(system_allocator(),
        "RESCUE_REFUSE prefix-rank shell={}",[shell]));return 3;}
    shell=shell+1;
  }

  println("RESCUE_STAGE shell2-entry");
  hs_scan(0,state);hs_rebase(0,state);
  let entry:HrState=new HrState(true,state.chart,ivtm_clone(state.z),
    ivtm_clone(state.amplitude));

  let panel:i64=0;while(panel<128){
    let sn:HrState=hs_step(2,panel,256,cell,state);
    if(!sn.ok || !hr_gauge_covariant(sn)){
      println(strfmt(system_allocator(),
        "RESCUE_REFUSE coarse-center panel={}",[panel]));return 3;}
    state=new HrState(true,sn.chart,ivtm_clone(sn.z),
      ivtm_clone(sn.amplitude));
    panel=panel+1;
  }
  println("RESCUE_STAGE shell2-center");
  hs_scan(1,state);hs_rebase(1,state);

  let fine:HrState=new HrState(true,entry.chart,ivtm_clone(entry.z),
    ivtm_clone(entry.amplitude));
  panel=0;while(panel<512){
    let sn:HrState=hs_step(2,panel,512,cell,fine);
    if(!sn.ok || !hr_gauge_covariant(sn)){
      println(strfmt(system_allocator(),
        "RESCUE_REFUSE fine-step panel={}",[panel]));return 3;}
    fine=new HrState(true,sn.chart,ivtm_clone(sn.z),
      ivtm_clone(sn.amplitude));
    panel=panel+1;
  }
  let far:IvTaylorRank=ivtm_full_column_rank_cells(fine.amplitude,64);
  println(strfmt(system_allocator(),
    "FINE_RESULT panels=512 chart={} norm={} zwidth={} awidth={} amplitude_cert={} amplitude_rank={}",
    [fine.chart,hr_norm(fine.z),hr_max_width(fine.z),
     hr_max_width(fine.amplitude),far.certified,far.rank]));
  hs_scan(2,fine);hs_rebase(2,fine);
  return if(far.certified && far.rank==6){42}else{3};
}
'''


def render() -> str:
    base = produce.render()
    marker = "fn hr_run(q:i64)->bool"
    if marker not in base:
        raise RuntimeError("Taylor2 run suffix missing")
    return base.split(marker, 1)[0] + RESCUE


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())


if __name__ == "__main__":
    main()
