#!/usr/bin/env python3
"""Render the isolated moving-frame structured-lower Forge preflight.

The authoritative coefficient and shared-frame tables are copied verbatim
from the already certified structured-lower first-microfactor source.  This
producer changes only the representation in which each local transition is
composed:

    W = B_1^{-1} U B_0,

where every B is block lower.  In particular,

    W_l = C_{k,1}^{-1}
          (L C_{c,0} + U_k D_0 - D_1 W_c).

The active global-connection implementation is deliberately not imported or
modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent
    / "axial_structured_lower_transition_preflight"
    / "actual_fixture.forge"
)
OUTPUT = HERE / "moving_fixture.forge"
METADATA = HERE / "source_metadata.json"


INSERT = r'''
// Layout boundary: gc_affine_submatrix is ONLY for the original interleaved
// standard-real state.  ivam_block_lower returns a contiguous 8+4 layout.
fn ml_block_part(a:borrow IvAffineMat,kind:i64)->IvAffineMat{
  if(a.rows!=12 || a.cols!=12 || kind<0 || kind>2){trap();}
  let nr:i64=if(kind==0){8}else{if(kind==1){4}else{4}};
  let nc:i64=if(kind==2){8}else{nr};
  let r0:i64=if(kind==0){0}else{8};
  let c0:i64=if(kind==1){8}else{0};
  let c:QMat=qm_new(nr,nc);
  let l:QMat=qm_new(nr,nc);
  let r:IvMat=ivm_zeros(nr,nc);
  let i:i64=0;while(i<nr){let j:i64=0;while(j<nc){
    c=qm_set(c,i,j,qm_get(a.center,r0+i,c0+j));
    l=qm_set(l,i,j,qm_get(a.linear,r0+i,c0+j));
    ivm_set(r,i,j,ivm_at(a.remainder,r0+i,c0+j));
    j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,nr,nc,c,l,r);
}

fn ml_lower_width(a:borrow IvAffineMat)->f64{
  return ivam_max_width(ml_block_part(a,2));
}

fn ml_upper_right_exact_zero(a:borrow IvAffineMat)->bool{
  if(a.rows!=12 || a.cols!=12){return false;}
  let i:i64=0;while(i<8){let j:i64=8;while(j<12){
    let rr:Iv=ivm_at(a.remainder,i,j);
    if(rat_sign(qm_get(a.center,i,j))!=0 ||
       rat_sign(qm_get(a.linear,i,j))!=0 ||
       rr.lo!=0.0 || rr.hi!=0.0){return false;}
    j=j+1;}i=i+1;}
  return true;
}

fn ml_compose(left:borrow IvAffineMat,right:borrow IvAffineMat)
->Option<IvAffineMat>{
  let lc:IvAffineMat=ml_block_part(left,0);
  let lk:IvAffineMat=ml_block_part(left,1);
  let ld:IvAffineMat=ml_block_part(left,2);
  let rc:IvAffineMat=ml_block_part(right,0);
  let rk:IvAffineMat=ml_block_part(right,1);
  let rd:IvAffineMat=ml_block_part(right,2);
  let cc0:IvAffineResult=ivam_mul_checked(lc,rc);
  let kk0:IvAffineResult=ivam_mul_checked(lk,rk);
  let a:IvAffineResult=ivam_mul_checked(ld,rc);
  let b:IvAffineResult=ivam_mul_checked(lk,rd);
  if(!cc0.ok || !kk0.ok || !a.ok || !b.ok){return Option.none;}
  let low0:IvAffineResult=ivam_add_checked(a.value,b.value);
  if(!low0.ok){return Option.none;}
  let cc:IvAffineResult=ivam_rebase_dyadic(cc0.value,128);
  let kk:IvAffineResult=ivam_rebase_dyadic(kk0.value,128);
  let low:IvAffineResult=ivam_rebase_dyadic(low0.value,128);
  if(!cc.ok || !kk.ok || !low.ok){return Option.none;}
  let out:IvAffineResult=ivam_block_lower(cc.value,low.value,kk.value);
  if(!out.ok){return Option.none;}
  return Option.some(ivam_clone(out.value));
}

// Restrict a model X=C+L*e+R from the global omega cell to a dyadic
// subcell without changing the shared generator.  If
// e=shift+scale*e_sub, then C_sub=C+shift*L and L_sub=scale*L.
// The outward interval remainder is retained verbatim.
fn ml_restrict_global(a:borrow IvAffineMat,cell:borrow IvAffineCell)
->IvAffineMat{
  let global:IvAffineCell=gc_cell();
  let shift:Rat=(rat_clone(cell.center)-rat_clone(global.center))/
    rat_clone(global.radius);
  let scale:Rat=rat_clone(cell.radius)/rat_clone(global.radius);
  let shifted:QMat=qm_scale(qm_clone(a.linear),shift);
  let center:QMat=qm_add(a.center,shifted);
  let linear:QMat=qm_scale(qm_clone(a.linear),scale);
  let rem:IvMat=ivm_zeros(a.rows,a.cols);
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    ivm_set(rem,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,a.rows,a.cols,center,linear,rem);
}

fn ml_subcell(q:i64,count:i64)->IvAffineCell{
  if(q<0 || q>=count || count<1){trap();}
  // [1/2,129/256] has width 1/256.  The q-th of count equal cells
  // has centre 1/2+(2q+1)/(512*count) and radius 1/(512*count).
  let center:Rat=rat(1,2)+rat(2*q+1,512*count);
  let radius:Rat=rat(1,512*count);
  return match(iva_cell(7315,center,radius)){
    some(z)=>z,none=>{trap();}};
}

fn ml_frame_part(p:i64,kind:i64,cell:borrow IvAffineCell)
->IvAffineMat{
  return gc_affine_submatrix(
    ml_restrict_global(gc_micro_frame_full(p),cell),kind);
}

// For U=[[Uc,0],[L,Uk]] and endpoint frames
// B_i=[[Cc_i,0],[D_i,Ck_i]], compute W=B_1^{-1} U B_0 while
// preserving the exact zero upper-right block:
//   Wc = Cc1^{-1} Uc Cc0,
//   Wk = Ck1^{-1} Uk Ck0,
//   Wl = Ck1^{-1}(L Cc0 + Uk D0 - D1 Wc).
fn ml_moving_between(u:borrow IvAffineMat,p0:i64,p1:i64,
cell:borrow IvAffineCell)
->Option<IvAffineMat>{
  if(u.rows!=12 || u.cols!=12 || u.generator!=7315 ||
     p0<0 || p1<=p0 || p1>8 || !ml_upper_right_exact_zero(u)){
    return Option.none;
  }
  let uc:IvAffineMat=ml_block_part(u,0);
  let uk:IvAffineMat=ml_block_part(u,1);
  let lower:IvAffineMat=ml_block_part(u,2);
  let cc0:IvAffineMat=ml_frame_part(p0,0,cell);
  let cc1:IvAffineMat=ml_frame_part(p1,0,cell);
  let ck0:IvAffineMat=ml_frame_part(p0,1,cell);
  let ck1:IvAffineMat=ml_frame_part(p1,1,cell);
  let d0:IvAffineMat=ml_frame_part(p0,2,cell);
  let d1:IvAffineMat=ml_frame_part(p1,2,cell);

  let uccc0:IvAffineResult=ivam_mul_checked(uc,cc0);
  let ukck0:IvAffineResult=ivam_mul_checked(uk,ck0);
  if(!uccc0.ok || !ukck0.ok){println("ML_REFUSE pre-diagonal");return Option.none;}
  let wc0:IvAffineResult=ivam_solve_rect(cc1,uccc0.value);
  let wk0:IvAffineResult=ivam_solve_rect(ck1,ukck0.value);
  if(!wc0.ok || !wk0.ok){println("ML_REFUSE diagonal-solve");return Option.none;}

  let lcc0:IvAffineResult=ivam_mul_checked(lower,cc0);
  let ukd0:IvAffineResult=ivam_mul_checked(uk,d0);
  if(!lcc0.ok || !ukd0.ok){println("ML_REFUSE lower-products");return Option.none;}
  let plus:IvAffineResult=ivam_add_checked(lcc0.value,ukd0.value);
  let d1wc:IvAffineResult=ivam_mul_checked(d1,wc0.value);
  if(!plus.ok || !d1wc.ok){println("ML_REFUSE lower-sum");return Option.none;}
  let rhs:IvAffineResult=ivam_sub_checked(plus.value,d1wc.value);
  if(!rhs.ok){println("ML_REFUSE lower-rhs");return Option.none;}
  let wl0:IvAffineResult=ivam_solve_rect(ck1,rhs.value);
  if(!wl0.ok){println("ML_REFUSE lower-solve");return Option.none;}

  let wc:IvAffineResult=ivam_rebase_dyadic(wc0.value,128);
  let wk:IvAffineResult=ivam_rebase_dyadic(wk0.value,128);
  let wl:IvAffineResult=ivam_rebase_dyadic(wl0.value,128);
  if(!wc.ok || !wk.ok || !wl.ok){println("ML_REFUSE rebase");return Option.none;}
  let rc:IvAffineRank=ivam_full_column_rank_cells(wc.value,16);
  let rk:IvAffineRank=ivam_full_column_rank_cells(wk.value,16);
  if(!rc.certified || rc.rank!=8 || !rk.certified || rk.rank!=4){
    println(strfmt(system_allocator(),
      "ML_REFUSE rank {} {} {} {} lower_width={} carrier_width={} kernel_width={}",
      [rc.rank,rc.certified,rk.rank,rk.certified,ivam_max_width(wl.value),
       ivam_max_width(wc.value),ivam_max_width(wk.value)]));
    return Option.none;
  }
  let out:IvAffineResult=ivam_block_lower(wc.value,wl.value,wk.value);
  if(!out.ok){return Option.none;}
  return Option.some(ivam_clone(out.value));
}

fn ml_moving_step(u:borrow IvAffineMat,p:i64,cell:borrow IvAffineCell)
->Option<IvAffineMat>{
  return ml_moving_between(u,p,p+1,cell);
}

fn ml_first_microfactor()->bool{
  let table:Vec<IvAffineMat>=gc_micro_coeff_table(0);
  let h:Rat=rat(1,64);
  let count:i64=4;
  let max_width:f64=0.0;
  let max_local:f64=0.0;
  let q:i64=0;while(q<count){
    let cell:IvAffineCell=ml_subcell(q,count);
    let ui:IvAffineResult=ivam_block_lower(
      ivam_identity(cell.generator,8),
      ivam_constant(cell.generator,qm_new(4,8)),
      ivam_identity(cell.generator,4));
    if(!ui.ok){return false;}
    let moving:IvAffineMat=ivam_clone(ui.value);
    let p:i64=0;while(p<8){
      let restricted:IvAffineMat=ml_restrict_global(
        vec_get_ref<IvAffineMat>(table,usize(p)),cell);
      let raw:IvAffineMat=match(sl_local_transition(restricted,h,12)){
        some(z)=>z,none=>{println("REFUSED local");return false;}};
      let step:IvAffineMat=match(ml_moving_step(raw,p,cell)){
        some(z)=>z,none=>{println(strfmt(system_allocator(),
          "REFUSED moving-step {} {}",[q,p]));return false;}};
      let lw:f64=ml_lower_width(step);
      if(lw>max_local){max_local=lw;}
      moving=match(ml_compose(step,moving)){
        some(z)=>z,none=>{println("REFUSED moving-compose");return false;}};
      p=p+1;
    }
    let mc:IvAffineMat=ml_block_part(moving,0);
    let mk:IvAffineMat=ml_block_part(moving,1);
    let rc:IvAffineRank=ivam_full_column_rank_cells(mc,16);
    let rk:IvAffineRank=ivam_full_column_rank_cells(mk,16);
    let width:f64=ml_lower_width(moving);
    println(strfmt(system_allocator(),
      "SUBCELL q={} lower_width={} full_width={} ranks={} {}",
      [q,width,ivam_max_width(moving),rc.rank,rk.rank]));
    if(!rc.certified || rc.rank!=8 || !rk.certified || rk.rank!=4 ||
       !ml_upper_right_exact_zero(moving) || moving.generator!=7315){
      return false;
    }
    if(width>max_width){max_width=width;}
    q=q+1;
  }
  println(strfmt(system_allocator(),
    "MOVING piecewise_lower_width={} max_local_lower_width={} subcells={} generator={}",
    [max_width,max_local,count,7315]));
  if(!(max_width<621.8840812306481)){
    println("WIDTH_SHORTFALL MOVING_BLOCK_NOT_NARROWER");
    return false;
  }
  println("PASS MOVING_LOWER_FIRST_MICROFACTOR");
  return true;
}

pub fn main()->i64{if(!ml_first_microfactor()){return 3;}return 42;}
'''


def render() -> str:
    source = SOURCE.read_text()
    # The predecessor's composition/extraction tail is deliberately excluded:
    # it mixed standard-interleaved and contiguous block layouts.  We retain
    # only the coefficient/frame tables and the independently valid local
    # block-power recurrence, then append the layout-tagged implementation.
    anchor = "fn sl_compose(left:borrow IvAffineMat,right:borrow IvAffineMat)"
    if source.count(anchor) != 1:
        raise RuntimeError("predecessor composition anchor is missing or ambiguous")
    return source[: source.index(anchor)] + INSERT


def produce(output: Path = OUTPUT, metadata_path: Path = METADATA) -> None:
    rendered = render()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered)
    metadata = {
        "schema": "phase3-axial-moving-lower-source-v1",
        "generator": 7315,
        "omega_cell": ["1/2", "129/256"],
        "domain": ["0", "1/8"],
        "frame_count": 9,
        "frame_source": str(SOURCE.relative_to(HERE.parents[2])),
        "frame_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        "formula": "Ck1^-1*(L*Cc0+Uk*D0-D1*Wc)",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--metadata", type=Path, default=METADATA)
    args = parser.parse_args()
    produce(args.output, args.metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
