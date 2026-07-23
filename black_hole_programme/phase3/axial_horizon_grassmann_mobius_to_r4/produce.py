#!/usr/bin/env python3
"""Render exact-frequency Grassmann/Möbius transports toward r=4.

The action-derived coefficient builders and local Peano--Baker enclosure are
imported from a committed predecessor.  This producer replaces the
predecessor's basis composition by a complete 20-chart Grassmann transport
and a separate amplitude/pivot rail.  The frozen q=0 sentinel records the
first-order shared-affine enclosure shortfall before any wider run.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_horizon_to_r4_transport_preflight import (
    produce as base_producer,
)

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
BASE = (
    HERE.parent
    / "axial_horizon_to_r4_transport_preflight"
    / "validated_regular_subspace_first_shell.forge"
)
BASE_SHA256 = "5393dc56e465546f36a67d5c8e35510a238c95364f08e5b729cd737701330b15"
BASE_COMMIT = "d6b349535b88d21d86da0204f85305e453f71001"
ONE_SHELL_COMMIT = "26a81c6902cdceebf1dd1d65ecba1d92f8e782cd"
OUTPUTS = tuple(HERE / f"transport_c{q:02d}.forge" for q in range(16))
METADATA = HERE / "source_metadata.json"
GENERATOR = 7315
SHELLS = tuple(
    (i, Fraction(1, 1 << (22 - i)), Fraction(1, 1 << (21 - i)))
    for i in range(22)
) + ((22, Fraction(1), Fraction(2)),)
PARENT_CELLS = (
    (Fraction(1, 2), Fraction(513, 1024)),
    (Fraction(513, 1024), Fraction(257, 512)),
    (Fraction(257, 512), Fraction(515, 1024)),
    (Fraction(515, 1024), Fraction(129, 256)),
)
CELLS = tuple(
    (
        parent_lo + (parent_hi - parent_lo) * child / 4,
        parent_lo + (parent_hi - parent_lo) * (child + 1) / 4,
    )
    for parent_lo, parent_hi in PARENT_CELLS
    for child in range(4)
)
COMPLEX_REAL_ROWS = (
    (0, 4),   # P
    (1, 5),   # P'
    (2, 6),   # Q
    (3, 7),   # Q'
    (8, 10),  # H1
    (9, 11),  # rho F
)
CHARTS = tuple(itertools.combinations(range(6), 3))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rat(x: Fraction) -> str:
    return f'big("{x.numerator}/{x.denominator}")'


def base_prefix() -> str:
    if sha256(BASE) != BASE_SHA256:
        raise RuntimeError("pinned all-shell source drift")
    source = BASE.read_text()
    marker = "pub type HtGraph"
    if marker not in source:
        raise RuntimeError("predecessor Grassmann suffix missing")
    return source.split(marker, 1)[0].rstrip() + "\n"


_EXACT_DATA: tuple | None = None


def exact_inputs():
    global _EXACT_DATA
    if _EXACT_DATA is None:
        rho, omega, flow = base_producer.exact_horizon_flow()
        repair = base_producer.endpoint_producer.load_repair_module()
        data = base_producer.endpoint_producer.exact_horizon_data(repair)
        majorant = base_producer.endpoint_producer.cauchy_majorant(data)
        _EXACT_DATA = (rho, omega, flow, data, majorant)
    return _EXACT_DATA


def child_initializer_model(cell: tuple[Fraction, Fraction]):
    _, _, _, data, majorant = exact_inputs()
    epsilon = Fraction(1, 1 << 22)
    truncated = sp.zeros(6, 3)
    for n, head in enumerate(data["physical_heads"]):
        truncated += head[:, :3] * sp.Rational(
            epsilon.numerator ** n, epsilon.denominator ** n
        )
    truncated = truncated.applyfunc(sp.cancel)
    model = base_producer.parameter_taylor_model(
        truncated, data["omega"], cell
    )
    tau = majorant["tau"]
    x = epsilon / tau
    qh = majorant["s_b_tau"] / Fraction(data["order"] + 1 - 2)
    tail = (
        Fraction(8)
        / (1 - qh)
        * x ** (data["order"] + 1)
        / (1 - x)
    )
    remainder = tuple(tuple(
        base_producer.RI(value.lo - tail, value.hi + tail)
        for value in row
    ) for row in model.remainder)
    return base_producer.TaylorMatrix(
        model.center, model.derivative, remainder
    )


def child_exact_builders(q: int) -> str:
    rho, omega, flow, _, _ = exact_inputs()
    lo, hi = CELLS[q]
    center = (lo + hi) / 2
    radius = (hi - lo) / 2
    initial = child_initializer_model((lo, hi))
    lines = base_producer.render_taylor_matrix("hc_initial_model", initial)
    lines += base_producer.render_runtime_taylor_builder(
        "hc_runtime", flow, rho, omega, center, radius
    )
    return "\n".join(lines) + "\n"


def chart_dispatch() -> str:
    def selector_rows(triple):
        return tuple(COMPLEX_REAL_ROWS[i][0] for i in triple) + tuple(
            COMPLEX_REAL_ROWS[i][1] for i in triple
        )

    def dispatch(name: str, rows_by_chart) -> str:
        cases = []
        for chart, rows in enumerate(rows_by_chart):
            row_expr = "else{".join(
                [f"if(k=={k}){{{row}}}" for k, row in enumerate(rows[:-1])]
                + [f"{{{rows[-1]}}}"]
            ) + "}" * 5
            cases.append((chart, row_expr))
        body = "else{".join(
            [f"if(chart=={chart}){{return {expr};}}"
             for chart, expr in cases[:-1]]
            + [f"{{return {cases[-1][1]};}}"]
        ) + "}" * (len(cases) - 1)
        return f"fn {name}(chart:i64,k:i64)->i64{{{body}}}\n"

    pivots = [selector_rows(triple) for triple in CHARTS]
    graphs = [
        selector_rows(tuple(i for i in range(6) if i not in triple))
        for triple in CHARTS
    ]
    return dispatch("hr_i", pivots) + dispatch("hr_j", graphs)


COMMON = r'''
pub type HrSolve = scoped struct {
  pub ok: bool,
  pub value: IvAffineMat,
};

pub type HrState = scoped struct {
  pub ok: bool,
  pub chart: i64,
  pub z: IvAffineMat,
  pub amplitude: IvAffineMat,
};

fn hr_zero()->IvAffineMat{
  return ivam_constant(7315,qm_new(6,6));
}

fn hr_fail()->HrState{
  return new HrState(false,-1,hr_zero(),hr_zero());
}

fn hr_rows(a:borrow IvAffineMat,chart:i64,pivot:bool)->IvAffineMat{
  let c:QMat=qm_new(6,a.cols);let l:QMat=qm_new(6,a.cols);
  let r:IvMat=ivm_zeros(6,a.cols);let i:i64=0;while(i<6){
    let si:i64=if(pivot){hr_i(chart,i)}else{hr_j(chart,i)};
    let j:i64=0;while(j<a.cols){
      c=qm_set(c,i,j,qm_get(a.center,si,j));
      l=qm_set(l,i,j,qm_get(a.linear,si,j));
      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,6,a.cols,c,l,r);
}

fn hr_block(a:borrow IvAffineMat,chart:i64,row_i:bool,col_i:bool)
->IvAffineMat{
  let c:QMat=qm_new(6,6);let l:QMat=qm_new(6,6);
  let r:IvMat=ivm_zeros(6,6);let i:i64=0;while(i<6){
    let si:i64=if(row_i){hr_i(chart,i)}else{hr_j(chart,i)};
    let j:i64=0;while(j<6){
      let sj:i64=if(col_i){hr_i(chart,j)}else{hr_j(chart,j)};
      c=qm_set(c,i,j,qm_get(a.center,si,sj));
      l=qm_set(l,i,j,qm_get(a.linear,si,sj));
      ivm_set(r,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,6,6,c,l,r);
}

// Checked right solve X*A=B via A^T*X^T=B^T.
fn hr_right(b:borrow IvAffineMat,a:borrow IvAffineMat)->HrSolve{
  if(a.generator!=7315 || b.generator!=7315 ||
     a.rows!=6 || a.cols!=6 || b.rows!=6 || b.cols!=6){
    return new HrSolve(false,hr_zero());}
  let xt:IvAffineResult=ivam_solve_rect(ivam_transpose(a),ivam_transpose(b));
  if(!xt.ok){return new HrSolve(false,hr_zero());}
  let rb:IvAffineResult=ivam_rebase_dyadic(ivam_transpose(xt.value),128);
  if(!rb.ok){return new HrSolve(false,hr_zero());}
  let xa:IvAffineResult=ivam_mul_checked(rb.value,a);
  if(!xa.ok){return new HrSolve(false,hr_zero());}
  let defect:IvAffineResult=ivam_sub_checked(xa.value,b);
  if(!defect.ok || !hr_contains_zero(defect.value)){
    return new HrSolve(false,hr_zero());}
  return new HrSolve(true,ivam_clone(rb.value));
}

fn hr_contains_zero(a:borrow IvAffineMat)->bool{
  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<a.rows){
    let j:i64=0;while(j<a.cols){let x:Iv=ivm_at(h,i,j);
      if(x.lo>0.0 || x.hi<0.0){return false;}j=j+1;}i=i+1;}
  return true;
}

fn hr_intersects(a:borrow IvAffineMat,b:borrow IvAffineMat)->bool{
  if(a.rows!=b.rows || a.cols!=b.cols){return false;}
  let ah:IvMat=ivam_hull(a);let bh:IvMat=ivam_hull(b);
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=ivm_at(ah,i,j);let y:Iv=ivm_at(bh,i,j);
    if(x.hi<y.lo || y.hi<x.lo){return false;}j=j+1;}i=i+1;}
  return true;
}

fn hr_norm(z:borrow IvAffineMat)->f64{
  let h:IvMat=ivam_hull(z);let best:f64=0.0;let i:i64=0;
  while(i<z.rows){let j:i64=0;while(j<z.cols){
    let a:Iv=iv_abs(ivm_at(h,i,j));if(a.hi>best){best=a.hi;}
    j=j+1;}i=i+1;}return best;
}

// Diagnostic only.  Centre rank and a floating SVD computed from these exact
// entries do not certify the uniform interval family.
fn hr_emit_amplitude_center(a:borrow IvAffineMat)->void{
  println(strfmt(system_allocator(),"AMPLITUDE_CENTER_RANK {}",
    [qm_rank(a.center)]));
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    let s:String=rat_str(qm_get(a.center,i,j));
    println(strfmt(system_allocator(),"AC {} {} {}",[i,j,str_view(s)]));
    drop(s);j=j+1;}i=i+1;}
}

fn hr_graph_basis(z:borrow IvAffineMat,chart:i64)->IvAffineMat{
  let c:QMat=qm_new(12,6);let l:QMat=qm_new(12,6);
  let r:IvMat=ivm_zeros(12,6);let i:i64=0;while(i<6){
    c=qm_set(c,hr_i(chart,i),i,rat(1,1));
    let j:i64=0;while(j<6){
      c=qm_set(c,hr_j(chart,i),j,qm_get(z.center,i,j));
      l=qm_set(l,hr_j(chart,i),j,qm_get(z.linear,i,j));
      ivm_set(r,hr_j(chart,i),j,ivm_at(z.remainder,i,j));j=j+1;}i=i+1;}
  return new IvAffineMat(7315,12,6,c,l,r);
}

fn hr_from_basis(y:borrow IvAffineMat,chart:i64)->HrState{
  let u:IvAffineMat=hr_rows(y,chart,true);
  let v:IvAffineMat=hr_rows(y,chart,false);
  let rank:IvAffineRank=ivam_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=6){return hr_fail();}
  let z:HrSolve=hr_right(v,u);
  if(!z.ok){return hr_fail();}
  let amp:IvAffineResult=ivam_rebase_dyadic(u,128);
  if(!amp.ok){return hr_fail();}
  return new HrState(true,chart,ivam_clone(z.value),ivam_clone(amp.value));
}

fn hr_reconstruct(s:borrow HrState)->HrSolve{
  let y:IvAffineResult=ivam_mul_checked(hr_graph_basis(s.z,s.chart),s.amplitude);
  if(!y.ok){return new HrSolve(false,hr_zero());}
  let rb:IvAffineResult=ivam_rebase_dyadic(y.value,128);
  if(!rb.ok){return new HrSolve(false,hr_zero());}
  return new HrSolve(true,ivam_clone(rb.value));
}

fn hr_rechart(s:borrow HrState,new_chart:i64)->HrState{
  if(!s.ok){return hr_fail();}
  if(new_chart==s.chart){
    return new HrState(true,s.chart,ivam_clone(s.z),ivam_clone(s.amplitude));}
  let g:IvAffineMat=hr_graph_basis(s.z,s.chart);
  let u:IvAffineMat=hr_rows(g,new_chart,true);
  let v:IvAffineMat=hr_rows(g,new_chart,false);
  let rank:IvAffineRank=ivam_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=6){return hr_fail();}
  let z:HrSolve=hr_right(v,u);
  if(!z.ok || hr_norm(z.value)>=2.0){return hr_fail();}
  let amp0:IvAffineResult=ivam_mul_checked(u,s.amplitude);
  if(!amp0.ok){return hr_fail();}
  let amp:IvAffineResult=ivam_rebase_dyadic(amp0.value,128);
  if(!amp.ok){return hr_fail();}
  return new HrState(true,new_chart,ivam_clone(z.value),ivam_clone(amp.value));
}

fn hr_best_chart(s:borrow HrState)->HrState{
  let best:HrState=new HrState(true,s.chart,ivam_clone(s.z),
    ivam_clone(s.amplitude));
  let c:i64=0;while(c<20){
    let cand:HrState=hr_rechart(s,c);
    if(cand.ok && hr_norm(cand.z)<hr_norm(best.z)){
      best=new HrState(true,cand.chart,ivam_clone(cand.z),
        ivam_clone(cand.amplitude));
    }
    drop(cand);c=c+1;
  }
  return best;
}

fn hr_step(phi:borrow IvAffineMat,s:borrow HrState)->HrState{
  let pii:IvAffineMat=hr_block(phi,s.chart,true,true);
  let pij:IvAffineMat=hr_block(phi,s.chart,true,false);
  let pji:IvAffineMat=hr_block(phi,s.chart,false,true);
  let pjj:IvAffineMat=hr_block(phi,s.chart,false,false);
  let az:IvAffineResult=ivam_mul_checked(pij,s.z);
  let bz:IvAffineResult=ivam_mul_checked(pjj,s.z);
  if(!az.ok || !bz.ok){return hr_fail();}
  let m0:IvAffineResult=ivam_add_checked(pii,az.value);
  let n0:IvAffineResult=ivam_add_checked(pji,bz.value);
  if(!m0.ok || !n0.ok){return hr_fail();}
  let m:IvAffineResult=ivam_rebase_dyadic(m0.value,128);
  let n:IvAffineResult=ivam_rebase_dyadic(n0.value,128);
  if(!m.ok || !n.ok){return hr_fail();}
  let rank:IvAffineRank=ivam_full_column_rank_cells(m.value,64);
  if(!rank.certified || rank.rank!=6){return hr_fail();}
  let z:HrSolve=hr_right(n.value,m.value);
  if(!z.ok || hr_norm(z.value)>=2.0){return hr_fail();}
  let amp0:IvAffineResult=ivam_mul_checked(m.value,s.amplitude);
  if(!amp0.ok){return hr_fail();}
  let amp:IvAffineResult=ivam_rebase_dyadic(amp0.value,128);
  if(!amp.ok){return hr_fail();}
  return new HrState(true,s.chart,ivam_clone(z.value),ivam_clone(amp.value));
}

fn hr_step_any(phi:borrow IvAffineMat,s:borrow HrState)->HrState{
  let direct:HrState=hr_step(phi,s);
  if(direct.ok){
    return new HrState(true,direct.chart,ivam_clone(direct.z),
      ivam_clone(direct.amplitude));
  }
  let best:HrState=hr_fail();let c:i64=0;while(c<20){
    let charted:HrState=hr_rechart(s,c);
    if(charted.ok){
      let stepped:HrState=hr_step(phi,charted);
      if(stepped.ok && (!best.ok || hr_norm(stepped.z)<hr_norm(best.z))){
        best=new HrState(true,stepped.chart,ivam_clone(stepped.z),
          ivam_clone(stepped.amplitude));
      }
      drop(stepped);
    }
    drop(charted);c=c+1;
  }
  return best;
}

fn hr_gauge()->IvAffineMat{
  let s:QMat=qm_new(6,6);let i:i64=0;while(i<6){
    s=qm_set(s,i,i,rat(1,1));i=i+1;}
  s=qm_set(s,0,1,rat(1,2));s=qm_set(s,1,2,rat(1,3));
  s=qm_set(s,3,4,rat(1,2));s=qm_set(s,4,5,rat(1,3));
  return ivam_constant(7315,s);
}

fn hr_gauge_covariant(s:borrow HrState)->bool{
  let recon:HrSolve=hr_reconstruct(s);
  if(!recon.ok){return false;}
  let gamp0:IvAffineResult=ivam_mul_checked(s.amplitude,hr_gauge());
  if(!gamp0.ok){return false;}
  let gamp:IvAffineResult=ivam_rebase_dyadic(gamp0.value,128);
  if(!gamp.ok){return false;}
  let gs:HrState=new HrState(true,s.chart,ivam_clone(s.z),
    ivam_clone(gamp.value));
  let grecon:HrSolve=hr_reconstruct(gs);
  if(!grecon.ok){return false;}
  let expected:IvAffineResult=ivam_mul_checked(recon.value,hr_gauge());
  if(!expected.ok){return false;}
  let defect:IvAffineResult=ivam_sub_checked(grecon.value,expected.value);
  return defect.ok && hr_contains_zero(defect.value);
}

fn hr_restrict(a:borrow IvAffineMat,cell:borrow IvAffineCell)->IvAffineMat{
  let global:IvAffineCell=ht_cell();
  let shift:Rat=(rat_clone(cell.center)-rat_clone(global.center))/
    rat_clone(global.radius);
  let scale:Rat=rat_clone(cell.radius)/rat_clone(global.radius);
  let center:QMat=qm_add(a.center,qm_scale(qm_clone(a.linear),shift));
  let linear:QMat=qm_scale(qm_clone(a.linear),scale);
  let rem:IvMat=ivm_zeros(a.rows,a.cols);let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    ivm_set(rem,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvAffineMat(7315,a.rows,a.cols,center,linear,rem);
}
'''


def dispatch() -> str:
    coeff = " else ".join(
        [f"if(shell=={i}){{ht_coeff_{i}(panel,tbox)}}"
         for i, _, _ in SHELLS[:-1]]
        + [f"{{ht_coeff_{SHELLS[-1][0]}(panel,tbox)}}"]
    )
    lo = " else ".join(
        [f"if(shell=={i}){{{rat(a)}}}" for i, a, _ in SHELLS[:-1]]
        + [f"{{{rat(SHELLS[-1][1])}}}"]
    )
    width = " else ".join(
        [f"if(shell=={i}){{{rat((b-a)/256)}}}"
         for i, a, b in SHELLS[:-1]]
        + [f"{{{rat((SHELLS[-1][2]-SHELLS[-1][1])/256)}}}"]
    )
    return f'''
fn hr_coeff(shell:i64,panel:i64,tbox:Iv)->IvAffineMat{{
  return {coeff};
}}
fn hr_shell_lo(shell:i64)->Rat{{return {lo};}}
fn hr_panel_width(shell:i64)->Rat{{return {width};}}
'''


RUN = r'''
fn hr_run(q:i64)->bool{
  let cell:IvAffineCell=hr_cell();
  let initial:IvAffineMat=ht_standard_to_block_rows(hc_initial_model(cell));
  let state:HrState=hr_from_basis(initial,11);
  if(!state.ok || hr_norm(state.z)>=2.0){
    println("REFUSE initial");return false;}
  let gy:IvAffineResult=ivam_mul_checked(initial,hr_gauge());
  if(!gy.ok){println("REFUSE gauge-initial-apply");return false;}
  let gauge:HrState=hr_from_basis(gy.value,11);
  if(!gauge.ok || hr_norm(gauge.z)>=2.0 ||
     !hr_intersects(state.z,gauge.z)){
    println("REFUSE gauge-initial");return false;}
  drop(gauge);
  let direct:IvAffineMat=ivam_clone(initial);
  let direct_active:bool=true;let direct_cutoff:i64=-1;
  let switches:i64=0;let shell:i64=0;
  println(strfmt(system_allocator(),"BEGIN q={}",[q]));
  while(shell<23){
    let panel:i64=0;while(panel<256){
      let lo:Rat=hr_shell_lo(shell);
      let wdt:Rat=hr_panel_width(shell);
      let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(wdt));
      let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(wdt));
      let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(wdt));
      let a:IvAffineMat=hc_runtime(
        xc,iv(ta.lo,tb.hi),rat_clone(wdt)/rat(2,1),cell);
      let phi:IvAffineMat=match(sl_local_transition(a,wdt,12)){
        some(z)=>z,none=>{println(strfmt(system_allocator(),
          "REFUSE local q={} shell={} panel={}",[q,shell,panel]));return false;}};

      let sn:HrState=hr_step_any(phi,state);
      if(!sn.ok){println(strfmt(system_allocator(),
        "REFUSE all-charts-before-step q={} shell={} panel={}",
        [q,shell,panel]));return false;}
      if(sn.chart!=state.chart){
        println(strfmt(system_allocator(),
          "SWITCH q={} shell={} panel={} from={} to={}",
          [q,shell,panel,state.chart,sn.chart]));
        switches=switches+1;
      }
      state=new HrState(true,sn.chart,ivam_clone(sn.z),
        ivam_clone(sn.amplitude));
      drop(sn);
      if(!state.ok){println(strfmt(system_allocator(),
        "REFUSE step q={} shell={} panel={}",[q,shell,panel]));return false;}
      if(!hr_gauge_covariant(state)){println(strfmt(system_allocator(),
        "REFUSE amplitude-gauge q={} shell={} panel={}",
        [q,shell,panel]));return false;}
      if((panel+1)%64==0){println(strfmt(system_allocator(),
        "HEARTBEAT q={} shell={} panel={} chart={} norm={} zwidth={}",
        [q,shell,panel+1,state.chart,hr_norm(state.z),
         ivam_max_width(state.z)]));}

      if(direct_active){
        let dn:IvAffineResult=ivam_apply_rect(phi,direct);
        if(dn.ok){
          let dr:IvAffineResult=ivam_rebase_dyadic(dn.value,128);
          if(dr.ok){direct=ivam_clone(dr.value);}
          else{direct_active=false;direct_cutoff=shell;}
        }else{direct_active=false;direct_cutoff=shell;}
      }
      panel=panel+1;
    }

    // Certified dynamic chart choice at every exact shell boundary.
    let alt:HrState=if(hr_norm(state.z)>=1.5){hr_best_chart(state)}
      else{new HrState(true,state.chart,ivam_clone(state.z),
        ivam_clone(state.amplitude))};
    if(alt.ok && alt.chart!=state.chart){
      println(strfmt(system_allocator(),
        "SWITCH q={} shell={} panel={} from={} to={}",
        [q,shell,256,state.chart,alt.chart]));
      state=new HrState(true,alt.chart,ivam_clone(alt.z),
        ivam_clone(alt.amplitude));
      switches=switches+1;
    }
    drop(alt);
    if(!hr_gauge_covariant(state)){println(strfmt(system_allocator(),
      "REFUSE amplitude-gauge-after-chart q={} shell={}",
      [q,shell]));return false;}

    let overlap:bool=false;
    if(direct_active){
      let dg:HrState=hr_from_basis(direct,state.chart);
      if(dg.ok){
        overlap=hr_intersects(state.z,dg.z);
        if(!overlap){println(strfmt(system_allocator(),
          "REFUSE direct-overlap q={} shell={}",[q,shell]));return false;}
      }else{direct_active=false;direct_cutoff=shell;}
    }
    let ar:IvAffineRank=ivam_full_column_rank_cells(state.amplitude,64);
    if(!ar.certified || ar.rank!=6){println(strfmt(system_allocator(),
      "REFUSE amplitude-rank q={} shell={}",[q,shell]));
      hr_emit_amplitude_center(state.amplitude);return false;}
    println(strfmt(system_allocator(),
      "SHELL q={} shell={} chart={} rank={} norm={} zwidth={} awidth={} direct={} overlap={} switches={}",
      [q,shell,state.chart,ar.rank,hr_norm(state.z),ivam_max_width(state.z),
       ivam_max_width(state.amplitude),direct_active,overlap,switches]));
    shell=shell+1;
  }

  let final_block:HrSolve=hr_reconstruct(state);
  if(!final_block.ok){return false;}
  let final_standard:IvAffineMat=ht_block_to_standard_rows(final_block.value);
  let out:IvAffineMat=match(ht_standard_at_r4(final_standard)){
    some(z)=>z,none=>{println("REFUSE standard-r4");return false;}};
  let rank:IvAffineRank=ivam_full_column_rank_cells(out,64);
  if(!rank.certified || rank.rank!=6){println("REFUSE final-rank");return false;}
  println(strfmt(system_allocator(),
    "RESULT q={} generator={} shells={} rank={} chart={} switches={} norm={} width={} direct_cutoff={}",
    [q,7315,23,rank.rank,state.chart,switches,hr_norm(state.z),
     ivam_max_width(out),direct_cutoff]));
  ht_emit(out);
  println(strfmt(system_allocator(),"PASS q={}",[q]));
  return true;
}

pub fn main()->i64{
  if(!hr_run(HR_Q)){return 3;}return 42;
}
'''


def render(q: int) -> str:
    lo, hi = CELLS[q]
    center = (lo + hi) / 2
    radius = (hi - lo) / 2
    cell = f'''
fn hr_cell()->IvAffineCell{{
  return match(iva_cell(7315,{rat(center)},{rat(radius)})){{
    some(z)=>z,none=>{{trap();}}}};
}}
'''
    return (
        base_prefix()
        + child_exact_builders(q)
        + chart_dispatch()
        + COMMON
        + dispatch()
        + cell
        + RUN.replace("HR_Q", str(q))
    )


def produce(indices: tuple[int, ...] = tuple(range(16))) -> None:
    hashes = {}
    for q in indices:
        path = OUTPUTS[q]
        source = render(q)
        path.write_text(source)
        hashes[path.name] = hashlib.sha256(source.encode()).hexdigest()
    metadata = {
        "schema": "phase3-axial-horizon-grassmann-mobius-r4-source-v1",
        "base_source": str(BASE.relative_to(PHYSICS)),
        "base_source_sha256": BASE_SHA256,
        "base_source_commit": BASE_COMMIT,
        "one_shell_commit": ONE_SHELL_COMMIT,
        "generator": GENERATOR,
        "omega_parent": ["1/2", "129/256"],
        "omega_public_parent_cells": [
            [str(a), str(b)] for a, b in PARENT_CELLS
        ],
        "omega_internal_child_cells": [
            {"index": i, "parent_index": i // 4, "bounds": [str(a), str(b)]}
            for i, (a, b) in enumerate(CELLS)
        ],
        "rho_initial": "1/4194304",
        "rho_final": "2",
        "shells": [[i, str(a), str(b)] for i, a, b in SHELLS],
        "panels_per_shell": 256,
        "charts": [
            {
                "index": i,
                "pivot_complex_indices": list(chart),
                "graph_complex_indices": [
                    j for j in range(6) if j not in chart
                ],
            }
            for i, chart in enumerate(CHARTS)
        ],
        "attempted_indices": list(indices),
        "source_sha256": hashes,
        "terminal_disposition": (
            "FIRST_ORDER_SHARED_AFFINE_AMPLITUDE_RANK_SHORTFALL"
            if indices == (0,)
            else "NOT_EVALUATED_BY_PRODUCER"
        ),
        "does_not_establish": [
            "horizon-to-infinity connection",
            "scattering, flux sign, stability, ghost, positivity, CPT or unitarity",
            "frequencies outside the lower pilot interval",
            "ell other than 2 or polar parity",
        ],
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    import sys

    selected = (
        tuple(int(x) for x in sys.argv[1:])
        if len(sys.argv) > 1
        else tuple(range(16))
    )
    produce(selected)
