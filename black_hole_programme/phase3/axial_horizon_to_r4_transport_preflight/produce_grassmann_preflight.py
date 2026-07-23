#!/usr/bin/env python3
"""Render a one-shell validated Grassmann/reset preflight.

This is the smallest falsification experiment for the horizon transport
repair.  It propagates the six-real-dimensional future-regular subspace over
rho in [2^-22,2^-21], normalizing its first six standard-state rows after
every local transition.  The corresponding 6x6 amplitude matrix is retained,
so the original recurrence normalization is not discarded.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import produce


HERE = Path(__file__).resolve().parent
BASE = HERE / "validated_horizon_to_r4.forge"
OUTPUT = HERE / "validated_regular_subspace_first_shell.forge"
METADATA = HERE / "grassmann-preflight-metadata.json"


INSERT = r'''
pub type HtGraph = scoped struct {
  pub ok: bool,
  pub basis: IvAffineMat,
  pub pivot: IvAffineMat,
};

fn ht_pivot_row(i:i64)->i64{
  return if(i==0){0}else{if(i==1){6}else{if(i==2){4}else{
    if(i==3){10}else{if(i==4){8}else{2}}}}};
}

fn ht_graph_row(i:i64)->i64{
  return if(i==0){1}else{if(i==1){3}else{if(i==2){5}else{
    if(i==3){7}else{if(i==4){9}else{11}}}}};
}

fn ht_rows(a:borrow IvAffineMat,top:bool)->IvAffineMat{
  let c:QMat=qm_new(6,a.cols);let l:QMat=qm_new(6,a.cols);
  let r:IvMat=ivm_zeros(6,a.cols);let i:i64=0;while(i<6){
    // Frozen midpoint-QR chart.  Every inverse is nevertheless validated.
    let si:i64=if(top){ht_pivot_row(i)}else{ht_graph_row(i)};
    let j:i64=0;while(j<a.cols){
      c=qm_set(c,i,j,qm_get(a.center,si,j));
      l=qm_set(l,i,j,qm_get(a.linear,si,j));
      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,6,a.cols,c,l,r);
}

fn ht_graph_refused(generator:i64)->HtGraph{
  return new HtGraph(false,ivam_constant(generator,qm_new(12,6)),
    ivam_constant(generator,qm_new(6,6)));
}

// For B=[U;V], compute Y=B U^-1 by the transpose solve
// U^T Y^T=B^T.  The returned pivot U is the exact amplitude update:
// if old physical columns equal Y_old X_old, then after a flow step
// X_new=U X_old and Y_new=B U^-1.
fn ht_graph_normalize(b:borrow IvAffineMat)->HtGraph{
  if(b.rows!=12 || b.cols!=6 || b.generator!=7315){
    return ht_graph_refused(b.generator);}
  let u:IvAffineMat=ht_rows(b,true);
  let ut:IvAffineMat=ivam_transpose(u);
  let bt:IvAffineMat=ivam_transpose(b);
  let solved:IvAffineResult=ivam_solve_rect(ut,bt);
  if(!solved.ok){return ht_graph_refused(b.generator);}
  let y0:IvAffineMat=ivam_transpose(solved.value);
  let rb:IvAffineResult=ivam_rebase_dyadic(y0,128);
  let ur:IvAffineResult=ivam_rebase_dyadic(u,128);
  if(!rb.ok || !ur.ok){return ht_graph_refused(b.generator);}
  let rr:IvAffineRank=ivam_full_column_rank_cells(ur.value,64);
  if(!rr.certified || rr.rank!=6){return ht_graph_refused(b.generator);}
  return new HtGraph(true,ivam_clone(rb.value),ivam_clone(ur.value));
}

fn ht_contains_zero(a:borrow IvAffineMat)->bool{
  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<a.rows){
    let j:i64=0;while(j<a.cols){let x:Iv=ivm_at(h,i,j);
      if(x.lo>0.0 || x.hi<0.0){return false;}j=j+1;}i=i+1;}
  return true;
}

fn ht_top_contains_identity(a:borrow IvAffineMat)->bool{
  let h:IvMat=ivam_hull(ht_rows(a,true));let i:i64=0;while(i<6){
    let j:i64=0;while(j<6){let x:Iv=ivm_at(h,i,j);
      let q:f64=if(i==j){1.0}else{0.0};
      if(x.lo>q || x.hi<q){return false;}j=j+1;}i=i+1;}
  return true;
}

pub fn axial_regular_subspace_first_shell()->bool{
  let initial:IvAffineMat=ht_initial();
  let g0:HtGraph=ht_graph_normalize(initial);
  if(!g0.ok){println("GRAPH_REFUSE initial");return false;}
  let y:IvAffineMat=ivam_clone(g0.basis);
  let x:IvAffineMat=ivam_clone(g0.pivot);
  let direct:IvAffineMat=ivam_clone(initial);
  let p:i64=0;while(p<16){
    let ta:Iv=iv_from_rat(rat(1,4194304)+rat(p,67108864));
    let tb:Iv=iv_from_rat(rat(1,4194304)+rat(p+1,67108864));
    let a:IvAffineMat=ht_coeff_0(p,iv(ta.lo,tb.hi));
    let w:IvAffineMat=match(sl_local_transition(a,rat(1,67108864),12)){
      some(z)=>z,none=>{println("GRAPH_REFUSE local");return false;}};

    let yb:IvAffineMat=ht_standard_to_block_rows(y);
    let stepped_b:IvAffineResult=ivam_apply_rect(w,yb);
    if(!stepped_b.ok){println("GRAPH_REFUSE step");return false;}
    let stepped:IvAffineMat=ht_block_to_standard_rows(stepped_b.value);
    if((p+1)%4==0){
      let gn:HtGraph=ht_graph_normalize(stepped);
      if(!gn.ok){println(strfmt(system_allocator(),
        "GRAPH_REFUSE normalize {}",[p]));return false;}
      let xn:IvAffineResult=ivam_apply_rect(gn.pivot,x);
      if(!xn.ok){println("GRAPH_REFUSE amplitude");return false;}
      let xr:IvAffineResult=ivam_rebase_dyadic(xn.value,128);
      if(!xr.ok){return false;}
      y=ivam_clone(gn.basis);x=ivam_clone(xr.value);
    }else{
      let yr:IvAffineResult=ivam_rebase_dyadic(stepped,128);
      if(!yr.ok){return false;}y=ivam_clone(yr.value);
    }

    let db:IvAffineMat=ht_standard_to_block_rows(direct);
    let dn:IvAffineResult=ivam_apply_rect(w,db);
    if(!dn.ok){return false;}
    let ds:IvAffineMat=ht_block_to_standard_rows(dn.value);
    let dr:IvAffineResult=ivam_rebase_dyadic(ds,128);
    if(!dr.ok){return false;}direct=ivam_clone(dr.value);
    p=p+1;
  }
  let recon0:IvAffineResult=ivam_apply_rect(y,x);
  if(!recon0.ok){return false;}
  let recon:IvAffineResult=ivam_rebase_dyadic(recon0.value,128);
  if(!recon.ok){return false;}
  let defect:IvAffineResult=ivam_sub_checked(recon.value,direct);
  if(!defect.ok || !ht_contains_zero(defect.value)){return false;}
  let ry:IvAffineRank=ivam_full_column_rank_cells(y,64);
  let rx:IvAffineRank=ivam_full_column_rank_cells(x,64);
  println(strfmt(system_allocator(),
    "GRASSMANN first-shell basis_width={} amplitude_width={} recon_width={} direct_width={} defect_width={} ranks={} {} top_identity={}",
    [ivam_max_width(y),ivam_max_width(x),ivam_max_width(recon.value),
     ivam_max_width(direct),ivam_max_width(defect.value),
     ry.rank,rx.rank,ht_top_contains_identity(y)]));
  return ry.certified && rx.certified && ry.rank==6 && rx.rank==6 &&
    ht_top_contains_identity(y);
}

pub fn main()->i64{
  if(!axial_regular_subspace_first_shell()){return 3;}return 42;
}
'''


def render() -> str:
    if not BASE.exists():
        produce.main()
    source = BASE.read_text()
    anchor = "pub fn main()->i64{if(!axial_horizon_to_r4()){return 3;}return 42;}"
    if source.count(anchor) != 1:
        raise RuntimeError("base main anchor missing or ambiguous")
    return source.replace(anchor, INSERT)


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    metadata = {
        "schema": "phase3-axial-horizon-grassmann-preflight-source-v1",
        "generator": produce.GENERATOR,
        "omega_cell": [str(x) for x in produce.OMEGA_CELL],
        "rho_cell": [str(produce.EPSILON), str(2 * produce.EPSILON)],
        "pivot_rows": [0, 6, 4, 10, 8, 2],
        "graph_rows": [1, 3, 5, 7, 9, 11],
        "pivot_schedule_source": "midpoint column-pivoted QR; every interval inverse is certified",
        "local_panels": 16,
        "chart_reset_cadence": 4,
        "local_order": 12,
        "dyadic_rebase_bits": produce.REBASE_BITS,
        "base_source_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "claim_boundary": (
            "one-shell regular-subspace/reset falsification preflight only"
        ),
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
