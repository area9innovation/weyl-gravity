#!/usr/bin/env python3
"""Render the exact-point 2D plane in the 4D Ricci carrier."""
from __future__ import annotations

import hashlib
import itertools

from . import exact_point

OUTPUT = exact_point.point.plane.produce.HERE / "carrier_plane_point_exact_4097_8192.forge"
SOURCE = exact_point.OUTPUT
CHARTS = tuple(itertools.combinations(range(4), 2))


def dispatch() -> str:
    def one(name: str, complements: bool) -> str:
        cases = []
        for ci, pair in enumerate(CHARTS):
            chosen = tuple(i for i in range(4) if i not in pair) if complements else pair
            rows = (chosen[0], chosen[1], chosen[0] + 4, chosen[1] + 4)
            expr = (
                f"if(k==0){{{rows[0]}}}else{{if(k==1){{{rows[1]}}}"
                f"else{{if(k==2){{{rows[2]}}}else{{{rows[3]}}}}}}}"
            )
            cases.append((ci, expr))
        body = cases[-1][1]
        for ci, expr in reversed(cases[:-1]):
            body = f"if(chart=={ci}){{{expr}}}else{{{body}}}"
        return f"fn {name}(chart:i64,k:i64)->i64{{return {body};}}\n"
    return one("cp_i", False) + one("cp_j", True)


CODE = r'''
pub type CpSolve = scoped struct {
  pub ok: bool,
  pub value: IvTaylorMat,
};
pub type CpState = scoped struct {
  pub ok: bool,
  pub chart: i64,
  pub z: IvTaylorMat,
  pub forward_bound: Iv,
  pub inverse_bound: Iv,
};
pub type CpAttempt = scoped struct {
  pub ok: bool,
  pub state: CpState,
  pub forward_bound: Iv,
  pub inverse_bound: Iv,
  pub max_condition: f64,
};
pub type CpBounds = value struct {
  pub ok: bool,
  pub forward: Iv,
  pub inverse: Iv,
};

fn cp_zero()->IvTaylorMat{return ivtm_constant(7315,qm_new(4,4));}
fn cp_fail()->CpState{
  return new CpState(false,-1,cp_zero(),iv_point(0.0),iv_point(0.0));}

fn cp_pointify(a:borrow IvAffineMat)->IvTaylorMat{
  let r:IvMat=ivm_zeros(a.rows,a.cols);let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    ivm_set(r,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(a.generator,a.rows,a.cols,qm_clone(a.center),
    qm_new(a.rows,a.cols),qm_new(a.rows,a.cols),r);
}

// Select the carrier rows and XH0a/XH0b realified columns.
fn cp_initial(a:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(8,4);let c1:QMat=qm_new(8,4);
  let c2:QMat=qm_new(8,4);let r:IvMat=ivm_zeros(8,4);
  let i:i64=0;while(i<8){let j:i64=0;while(j<4){
    let sj:i64=if(j<2){j}else{j+1};
    c0=qm_set(c0,i,j,qm_get(a.c0,i,sj));
    c1=qm_set(c1,i,j,qm_get(a.c1,i,sj));
    c2=qm_set(c2,i,j,qm_get(a.c2,i,sj));
    ivm_set(r,i,j,ivm_at(a.remainder,i,sj));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,8,4,c0,c1,c2,r);
}

fn cp_carrier(a:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(8,8);let c1:QMat=qm_new(8,8);
  let c2:QMat=qm_new(8,8);let r:IvMat=ivm_zeros(8,8);
  let i:i64=0;while(i<8){let j:i64=0;while(j<8){
    c0=qm_set(c0,i,j,qm_get(a.c0,i,j));
    c1=qm_set(c1,i,j,qm_get(a.c1,i,j));
    c2=qm_set(c2,i,j,qm_get(a.c2,i,j));
    ivm_set(r,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,8,8,c0,c1,c2,r);
}

fn cp_rows(a:borrow IvTaylorMat,chart:i64,pivot:bool)->IvTaylorMat{
  let c0:QMat=qm_new(4,a.cols);let c1:QMat=qm_new(4,a.cols);
  let c2:QMat=qm_new(4,a.cols);let r:IvMat=ivm_zeros(4,a.cols);
  let i:i64=0;while(i<4){
    let si:i64=if(pivot){cp_i(chart,i)}else{cp_j(chart,i)};
    let j:i64=0;while(j<a.cols){
      c0=qm_set(c0,i,j,qm_get(a.c0,si,j));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,j));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,j));
      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,4,a.cols,c0,c1,c2,r);
}

fn cp_block(a:borrow IvTaylorMat,chart:i64,row_i:bool,col_i:bool)
->IvTaylorMat{
  let c0:QMat=qm_new(4,4);let c1:QMat=qm_new(4,4);
  let c2:QMat=qm_new(4,4);let r:IvMat=ivm_zeros(4,4);
  let i:i64=0;while(i<4){
    let si:i64=if(row_i){cp_i(chart,i)}else{cp_j(chart,i)};
    let j:i64=0;while(j<4){
      let sj:i64=if(col_i){cp_i(chart,j)}else{cp_j(chart,j)};
      c0=qm_set(c0,i,j,qm_get(a.c0,si,sj));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,sj));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,sj));
      ivm_set(r,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,4,4,c0,c1,c2,r);
}

fn cp_hull_zero(a:borrow IvTaylorMat)->bool{
  let h:IvMat=ivtm_hull(a);let i:i64=0;while(i<a.rows){
    let j:i64=0;while(j<a.cols){let x:Iv=ivm_at(h,i,j);
      if(x.lo>0.0 || x.hi<0.0){return false;}j=j+1;}i=i+1;}
  return true;
}

fn cp_right(b:borrow IvTaylorMat,a:borrow IvTaylorMat)->CpSolve{
  let x:IvTaylorResult=ivtm_solve_right(b,a);
  if(!x.ok){return new CpSolve(false,cp_zero());}
  let rb:IvTaylorResult=ivtm_rebase_dyadic(x.value,128);
  if(!rb.ok){return new CpSolve(false,cp_zero());}
  let xa:IvTaylorResult=ivtm_mul_checked(rb.value,a);
  if(!xa.ok){return new CpSolve(false,cp_zero());}
  let d:IvTaylorResult=ivtm_sub_checked(xa.value,b);
  if(!d.ok || !cp_hull_zero(d.value)){return new CpSolve(false,cp_zero());}
  return new CpSolve(true,ivtm_clone(rb.value));
}

fn cp_inf(a:borrow IvTaylorMat)->Iv{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let s:Iv=iv_point(0.0);let j:i64=0;
    while(j<a.cols){s=iv_add(s,iv_abs(ivm_at(h,i,j)));j=j+1;}
    if(s.hi>best){best=s.hi;}i=i+1;}
  return iv(0.0,best);
}
fn cp_bounds(a:borrow IvTaylorMat)->CpBounds{
  let inv:IvTaylorResult=ivtm_solve_left(a,ivtm_identity(7315,4));
  if(!inv.ok){return CpBounds(false,iv_point(0.0),iv_point(0.0));}
  return CpBounds(true,cp_inf(a),cp_inf(inv.value));
}
fn cp_norm(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=iv_abs(ivm_at(h,i,j));if(x.hi>best){best=x.hi;}
    j=j+1;}i=i+1;}return best;
}
fn cp_width(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=ivm_at(h,i,j);if(x.hi-x.lo>best){best=x.hi-x.lo;}
    j=j+1;}i=i+1;}return best;
}

fn cp_graph(z:borrow IvTaylorMat,chart:i64)->IvTaylorMat{
  let c0:QMat=qm_new(8,4);let c1:QMat=qm_new(8,4);
  let c2:QMat=qm_new(8,4);let r:IvMat=ivm_zeros(8,4);
  let i:i64=0;while(i<4){
    c0=qm_set(c0,cp_i(chart,i),i,rat(1,1));
    let j:i64=0;while(j<4){
      c0=qm_set(c0,cp_j(chart,i),j,qm_get(z.c0,i,j));
      c1=qm_set(c1,cp_j(chart,i),j,qm_get(z.c1,i,j));
      c2=qm_set(c2,cp_j(chart,i),j,qm_get(z.c2,i,j));
      ivm_set(r,cp_j(chart,i),j,ivm_at(z.remainder,i,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,8,4,c0,c1,c2,r);
}

fn cp_from_basis(y:borrow IvTaylorMat,chart:i64)->CpState{
  let u:IvTaylorMat=cp_rows(y,chart,true);
  let v:IvTaylorMat=cp_rows(y,chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=4){return cp_fail();}
  let bd:CpBounds=cp_bounds(u);if(!bd.ok){return cp_fail();}
  let z:CpSolve=cp_right(v,u);
  if(!z.ok || cp_norm(z.value)>=2.0){return cp_fail();}
  return new CpState(true,chart,ivtm_clone(z.value),bd.forward,bd.inverse);
}
fn cp_rechart(s:borrow CpState,c:i64)->CpState{
  if(c==s.chart){return new CpState(true,c,ivtm_clone(s.z),
    iv_point(1.0),iv_point(1.0));}
  return cp_from_basis(cp_graph(s.z,s.chart),c);
}
fn cp_best(s:borrow CpState)->CpState{
  let best:CpState=new CpState(true,s.chart,ivtm_clone(s.z),
    iv_point(1.0),iv_point(1.0));let c:i64=0;while(c<6){
    let x:CpState=cp_rechart(s,c);
    if(x.ok && cp_norm(x.z)<cp_norm(best.z)){
      best=new CpState(true,x.chart,ivtm_clone(x.z),
        x.forward_bound,x.inverse_bound);}c=c+1;}return best;
}

fn cp_step(phi:borrow IvTaylorMat,s:borrow CpState)->CpState{
  let pii:IvTaylorMat=cp_block(phi,s.chart,true,true);
  let pij:IvTaylorMat=cp_block(phi,s.chart,true,false);
  let pji:IvTaylorMat=cp_block(phi,s.chart,false,true);
  let pjj:IvTaylorMat=cp_block(phi,s.chart,false,false);
  let az:IvTaylorResult=ivtm_mul_checked(pij,s.z);
  let bz:IvTaylorResult=ivtm_mul_checked(pjj,s.z);
  if(!az.ok || !bz.ok){return cp_fail();}
  let m0:IvTaylorResult=ivtm_add_checked(pii,az.value);
  let n0:IvTaylorResult=ivtm_add_checked(pji,bz.value);
  if(!m0.ok || !n0.ok){return cp_fail();}
  let m:IvTaylorResult=ivtm_rebase_dyadic(m0.value,128);
  let n:IvTaylorResult=ivtm_rebase_dyadic(n0.value,128);
  if(!m.ok || !n.ok){return cp_fail();}
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(m.value,64);
  if(!rank.certified || rank.rank!=4){return cp_fail();}
  let bd:CpBounds=cp_bounds(m.value);if(!bd.ok){return cp_fail();}
  let z:CpSolve=cp_right(n.value,m.value);
  if(!z.ok || cp_norm(z.value)>=2.0){return cp_fail();}
  return new CpState(true,s.chart,ivtm_clone(z.value),bd.forward,bd.inverse);
}
fn cp_step_any(phi:borrow IvTaylorMat,s:borrow CpState)->CpState{
  let d:CpState=cp_step(phi,s);
  if(d.ok){return new CpState(true,d.chart,ivtm_clone(d.z),
    d.forward_bound,d.inverse_bound);}
  let best:CpState=cp_fail();let c:i64=0;while(c<6){
    let ch:CpState=cp_rechart(s,c);
    if(ch.ok){let st:CpState=cp_step(phi,ch);
      if(st.ok && (!best.ok || cp_norm(st.z)<cp_norm(best.z))){
        best=new CpState(true,st.chart,ivtm_clone(st.z),
          iv_mul(st.forward_bound,ch.forward_bound),
          iv_mul(ch.inverse_bound,st.inverse_bound));}}
    c=c+1;}return best;
}
fn cp_initial_best(y:borrow IvTaylorMat)->CpState{
  let best:CpState=cp_fail();let c:i64=0;while(c<6){
    let x:CpState=cp_from_basis(y,c);
    if(x.ok && (!best.ok || cp_norm(x.z)<cp_norm(best.z))){
      best=new CpState(true,x.chart,ivtm_clone(x.z),
        x.forward_bound,x.inverse_bound);}c=c+1;}return best;
}

fn cp_attempt(shell:i64,panels:i64,cell:borrow IvAffineCell,
start:borrow CpState)->CpAttempt{
  let state:CpState=new CpState(true,start.chart,ivtm_clone(start.z),
    iv_point(1.0),iv_point(1.0));
  let fw:Iv=iv_point(1.0);let iw:Iv=iv_point(1.0);
  let mc:f64=1.0;let panel:i64=0;
  while(panel<panels){
    let lo:Rat=hr_shell_lo(shell);
    let w:Rat=(hr_panel_width(shell)*rat(256,1))/rat(panels,1);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(w));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(w));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(w));
    let a:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(w)/rat(2,1),cell);
    let p0:IvAffineMat=match(sl_local_transition(a,w,12)){
      some(z)=>z,none=>{println(strfmt(system_allocator(),
        "CARRIER_ATTEMPT_REFUSE kind=local shell={} panel={} panels={}",
        [shell,panel,panels]));
        return new CpAttempt(false,cp_fail(),fw,iw,mc);}};
    let p:IvTaylorMat=cp_carrier(cp_pointify(p0));
    let sn:CpState=cp_step_any(p,state);
    if(!sn.ok){println(strfmt(system_allocator(),
      "CARRIER_ATTEMPT_REFUSE kind=mobius-all-charts shell={} panel={} panels={}",
      [shell,panel,panels]));
      return new CpAttempt(false,cp_fail(),fw,iw,mc);}
    fw=iv_mul(fw,sn.forward_bound);iw=iv_mul(sn.inverse_bound,iw);
    let cond:Iv=iv_mul(sn.forward_bound,sn.inverse_bound);
    if(cond.hi>mc){mc=cond.hi;}
    state=new CpState(true,sn.chart,ivtm_clone(sn.z),
      iv_point(1.0),iv_point(1.0));panel=panel+1;
  }
  let alt:CpState=if(cp_norm(state.z)>=1.5){cp_best(state)}
    else{new CpState(true,state.chart,ivtm_clone(state.z),
      iv_point(1.0),iv_point(1.0))};
  if(alt.ok && alt.chart!=state.chart){
    println(strfmt(system_allocator(),
      "CARRIER_SWITCH shell={} panels={} from={} to={}",
      [shell,panels,state.chart,alt.chart]));
    fw=iv_mul(fw,alt.forward_bound);iw=iv_mul(alt.inverse_bound,iw);
    let cond:Iv=iv_mul(alt.forward_bound,alt.inverse_bound);
    if(cond.hi>mc){mc=cond.hi;}
    state=new CpState(true,alt.chart,ivtm_clone(alt.z),
      iv_point(1.0),iv_point(1.0));
  }
  let named:IvTaylorMat=cp_rows(cp_graph(state.z,state.chart),state.chart,true);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(named,64);
  if(!rank.certified || rank.rank!=4){
    return new CpAttempt(false,cp_fail(),fw,iw,mc);}
  return new CpAttempt(true,new CpState(true,state.chart,ivtm_clone(state.z),
    iv_point(1.0),iv_point(1.0)),fw,iw,mc);
}

fn cp_emit(a:borrow IvTaylorMat)->void{
  let h:IvMat=ivtm_hull(a);let i:i64=0;while(i<8){
    let j:i64=0;while(j<4){let q:Iv=ivm_at(h,i,j);
      println(strfmt(system_allocator(),"CP {} {} {} {}",
        [i,j,f64_bits(q.lo),f64_bits(q.hi)]));j=j+1;}i=i+1;}
}

pub fn main()->i64{
  let cell:IvAffineCell=hr_cell();
  let full:IvTaylorMat=hr_reorder_rows(
    cp_pointify(hc_initial_model(cell)),true);
  let state:CpState=cp_initial_best(cp_initial(full));
  if(!state.ok){println("CARRIER_REFUSE initial");return 3;}
  let fw:Iv=state.forward_bound;let iw:Iv=state.inverse_bound;
  let mc:f64=iv_mul(fw,iw).hi;let shell:i64=0;
  println("CARRIER_BEGIN omega=4097/8192 frequency_radius=0 basis=XH0a,XH0b state_order=Re(P),Re(Pprime),Re(Q),Re(Qprime),Im(P),Im(Pprime),Im(Q),Im(Qprime)");
  while(shell<23){
    let used:i64=64;let a:CpAttempt=cp_attempt(shell,64,cell,state);
    if(!a.ok){used=128;println(strfmt(system_allocator(),
      "CARRIER_FALLBACK shell={} panels=128",[shell]));
      a=cp_attempt(shell,128,cell,state);}
    if(!a.ok){println(strfmt(system_allocator(),
      "CARRIER_REFUSE shell={} after-fallback=128",[shell]));return 3;}
    fw=iv_mul(fw,a.forward_bound);iw=iv_mul(a.inverse_bound,iw);
    if(a.max_condition>mc){mc=a.max_condition;}
    state=new CpState(true,a.state.chart,ivtm_clone(a.state.z),
      iv_point(1.0),iv_point(1.0));
    println(strfmt(system_allocator(),
      "CARRIER_SHELL shell={} panels={} chart={} rank=4 norm={} zwidth={} forward_bound={} inverse_bound={} max_local_condition={}",
      [shell,used,state.chart,cp_norm(state.z),cp_width(state.z),
       fw.hi,iw.hi,mc]));shell=shell+1;
  }
  let out:IvTaylorMat=cp_graph(state.z,state.chart);
  let named:IvTaylorMat=cp_rows(out,state.chart,true);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(named,64);
  if(!rank.certified || rank.rank!=4){println("CARRIER_REFUSE final-rank");return 3;}
  println(strfmt(system_allocator(),
    "CARRIER_RESULT omega=4097/8192 radius=4 complex_rank=2 real_rank=4 chart={} norm={} width={} normalization=chart-identity original_horizon_amplitude=false forward_bound={} inverse_bound={} max_local_condition={}",
    [state.chart,cp_norm(state.z),cp_width(out),fw.hi,iw.hi,mc]));
  cp_emit(out);println("CARRIER_PASS omega=4097/8192 radius=4");return 42;
}
'''


def render() -> str:
    source = SOURCE.read_text()
    marker = "pub type HpState"
    if marker not in source:
        raise RuntimeError("exact-point Taylor common prefix missing")
    return source.split(marker, 1)[0] + dispatch() + CODE


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())


if __name__ == "__main__":
    main()
