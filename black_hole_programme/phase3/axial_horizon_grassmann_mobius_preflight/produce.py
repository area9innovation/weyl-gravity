#!/usr/bin/env python3
"""Render the isolated exact-affine one-shell Grassmann/Mobius preflight.

The renderer imports only a pinned, committed predecessor *producer* for the
action-derived axial flow, exact Frobenius initializer, and certified local
transition kernel.  It resets that renderer to the requested
rho=[2^-22,2^-21] shell and replaces its terminal full-column transport by a
named-row Grassmann graph update.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_to_r4_transport_preflight import (
    produce as base,
)


HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
OUTPUT = HERE / "mobius_first_shell.forge"
METADATA = HERE / "source_metadata.json"

BASE_PRODUCER = Path(base.__file__).resolve()
BASE_PRODUCER_SHA256 = (
    "60d72529c89597860d14d9cf6d58f806e74e519fb5a7c93b4823203c8b13ede4"
)
INPUT_COMMIT = "d6b349535"
BASE_SOURCE = HERE / "base_first_shell.forge"
BASE_SOURCE_SHA256 = (
    "09ac6e687fd58d138df383ce7e3312929e8c70c23129220b96c544597d8b3780"
)
BASE_RENDER_IMPORTS = {
    "/home/alstrup/area9/tango/forge/lib/math/ivaffine.forge":
        "c9f7fe51ae598f38cde37b79cedefa6d9b2bcd4eef35c272c513b34b81f6a1bc",
    "/home/alstrup/area9/tango/forge/lib/math/ivlinparam.forge":
        "d8d3775306d12b00b4ba35306a043a5cb41edfcb23e3c0d61e63e9dda85b2f55",
    "symplectic-reconstruction/black_hole_programme/phase3/"
    "axial_complete_reconstruction_repair/certificate.json":
        "13a4077ee8c77cc5b99e379d35aa15afa09ebeea78c0df9a4771b4845c00c990",
    "symplectic-reconstruction/black_hole_programme/phase3/"
    "axial_endpoint_remainder_enclosures/certificate.json":
        "9886a02e9d49dbfca813e9520d9e488afce22fc82470b2ba6601b3092f9c64b9",
    "symplectic-reconstruction/black_hole_programme/phase3/"
    "axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge":
        "558cc357a1a6d205c1d0ae156b7f16d4399fb39e1426d0f95ead2d914257c97a",
    "symplectic-reconstruction/black_hole_programme/phase3/"
    "axial_global_connection_matrix_v5/affine_codegen.py":
        "def0d650cdcd1e9ec61752db5194daeca0e91afade096cc15b841a3cb1da7b1c",
    "symplectic-reconstruction/black_hole_programme/phase3/"
    "axial_structured_lower_transition_preflight/actual_fixture.forge":
        "11713c14ebcf2d5f49f7f9527b31a1ee1e4533ded7d491a9d6838c5d80680a27",
}
EPSILON = Fraction(1, 1 << 22)
RHO_FINAL = Fraction(1, 1 << 21)
GENERATOR = 7315
REBASE_BITS = 128
PIVOT_COMPLEX = ("P_prime", "Q", "H1")
GRAPH_COMPLEX = ("P", "Q_prime", "rho_F")
PIVOT_REAL_BLOCK = (1, 2, 8, 5, 6, 10)
GRAPH_REAL_BLOCK = (0, 3, 9, 4, 7, 11)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


INSERT = r'''
pub type HmResult = scoped struct {
  pub ok: bool,
  pub value: IvAffineMat,
};

pub type HmGraph = scoped struct {
  pub ok: bool,
  pub z: IvAffineMat,
  pub pivot: IvAffineMat,
};

fn hm_fail(rows:i64,cols:i64)->HmResult{
  return new HmResult(false,ivam_constant(7315,qm_new(rows,cols)));
}

fn hm_graph_fail()->HmGraph{
  return new HmGraph(false,ivam_constant(7315,qm_new(6,6)),
    ivam_constant(7315,qm_new(6,6)));
}

// Named complex-row selectors resolved in the active contiguous block-real
// layout:
// (Re P,Re P',Re Q,Re Q',Im P,Im P',Im Q,Im Q',
//  Re H1,Re rhoF,Im H1,Im rhoF).
fn hm_i(k:i64)->i64{
  return if(k==0){1}else{if(k==1){2}else{if(k==2){8}else{
    if(k==3){5}else{if(k==4){6}else{10}}}}};
}

fn hm_j(k:i64)->i64{
  return if(k==0){0}else{if(k==1){3}else{if(k==2){9}else{
    if(k==3){4}else{if(k==4){7}else{11}}}}};
}

fn hm_select_rows(a:borrow IvAffineMat,use_i:bool)->IvAffineMat{
  let c:QMat=qm_new(6,a.cols);let l:QMat=qm_new(6,a.cols);
  let r:IvMat=ivm_zeros(6,a.cols);let i:i64=0;while(i<6){
    let si:i64=if(use_i){hm_i(i)}else{hm_j(i)};
    let j:i64=0;while(j<a.cols){
      c=qm_set(c,i,j,qm_get(a.center,si,j));
      l=qm_set(l,i,j,qm_get(a.linear,si,j));
      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,6,a.cols,c,l,r);
}

fn hm_select_block(a:borrow IvAffineMat,row_i:bool,col_i:bool)
->IvAffineMat{
  let c:QMat=qm_new(6,6);let l:QMat=qm_new(6,6);
  let r:IvMat=ivm_zeros(6,6);let i:i64=0;while(i<6){
    let si:i64=if(row_i){hm_i(i)}else{hm_j(i)};
    let j:i64=0;while(j<6){
      let sj:i64=if(col_i){hm_i(j)}else{hm_j(j)};
      c=qm_set(c,i,j,qm_get(a.center,si,sj));
      l=qm_set(l,i,j,qm_get(a.linear,si,sj));
      ivm_set(r,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,6,6,c,l,r);
}

// Checked right solve X*A=B, implemented as A^T*X^T=B^T.
fn hm_right_solve(b:borrow IvAffineMat,a:borrow IvAffineMat)->HmResult{
  if(a.generator!=7315 || b.generator!=7315 ||
     a.rows!=6 || a.cols!=6 || b.rows!=6 || b.cols!=6){
    return hm_fail(6,6);}
  let at:IvAffineMat=ivam_transpose(a);
  let bt:IvAffineMat=ivam_transpose(b);
  let xt:IvAffineResult=ivam_solve_rect(at,bt);
  if(!xt.ok){return hm_fail(6,6);}
  let x0:IvAffineMat=ivam_transpose(xt.value);
  let x:IvAffineResult=ivam_rebase_dyadic(x0,128);
  if(!x.ok){return hm_fail(6,6);}
  // Residual is an independent fail-closed consistency enclosure.
  let xa:IvAffineResult=ivam_mul_checked(x.value,a);
  if(!xa.ok){return hm_fail(6,6);}
  let defect:IvAffineResult=ivam_sub_checked(xa.value,b);
  if(!defect.ok){return hm_fail(6,6);}
  let dh:IvMat=ivam_hull(defect.value);let i:i64=0;while(i<6){
    let j:i64=0;while(j<6){let q:Iv=ivm_at(dh,i,j);
      if(q.lo>0.0 || q.hi<0.0){return hm_fail(6,6);}j=j+1;}i=i+1;}
  return new HmResult(true,ivam_clone(x.value));
}

fn hm_from_basis(y:borrow IvAffineMat)->HmGraph{
  if(y.generator!=7315 || y.rows!=12 || y.cols!=6){
    return hm_graph_fail();}
  let u:IvAffineMat=hm_select_rows(y,true);
  let v:IvAffineMat=hm_select_rows(y,false);
  let ru:IvAffineRank=ivam_full_column_rank_cells(u,64);
  if(!ru.certified || ru.rank!=6){return hm_graph_fail();}
  let solved:HmResult=hm_right_solve(v,u);
  if(!solved.ok){return hm_graph_fail();}
  return new HmGraph(true,ivam_clone(solved.value),ivam_clone(u));
}

fn hm_graph_basis(z:borrow IvAffineMat)->IvAffineMat{
  let c:QMat=qm_new(12,6);let l:QMat=qm_new(12,6);
  let r:IvMat=ivm_zeros(12,6);let i:i64=0;while(i<6){
    c=qm_set(c,hm_i(i),i,rat(1,1));
    let j:i64=0;while(j<6){
      c=qm_set(c,hm_j(i),j,qm_get(z.center,i,j));
      l=qm_set(l,hm_j(i),j,qm_get(z.linear,i,j));
      ivm_set(r,hm_j(i),j,ivm_at(z.remainder,i,j));j=j+1;}i=i+1;}
  return new IvAffineMat(z.generator,12,6,c,l,r);
}

fn hm_norm_hi(z:borrow IvAffineMat)->f64{
  let h:IvMat=ivam_hull(z);let best:f64=0.0;
  let i:i64=0;while(i<z.rows){let j:i64=0;while(j<z.cols){
    let a:Iv=iv_abs(ivm_at(h,i,j));if(a.hi>best){best=a.hi;}
    j=j+1;}i=i+1;}return best;
}

fn hm_intersects(a:borrow IvAffineMat,b:borrow IvAffineMat)->bool{
  if(a.rows!=b.rows || a.cols!=b.cols){return false;}
  let ah:IvMat=ivam_hull(a);let bh:IvMat=ivam_hull(b);
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=ivm_at(ah,i,j);let y:Iv=ivm_at(bh,i,j);
    if(x.hi<y.lo || y.hi<x.lo){return false;}j=j+1;}i=i+1;}
  return true;
}

// Restrict X=C+L*e+R from the global frequency cell to one of four exact
// subcells without changing generator 7315.  If e=shift+scale*e_sub, then
// C_sub=C+shift*L and L_sub=scale*L; R is retained outward verbatim.
fn hm_restrict_global(a:borrow IvAffineMat,cell:borrow IvAffineCell)
->IvAffineMat{
  let global:IvAffineCell=ht_cell();
  let shift:Rat=(rat_clone(cell.center)-rat_clone(global.center))/
    rat_clone(global.radius);
  let scale:Rat=rat_clone(cell.radius)/rat_clone(global.radius);
  let center:QMat=qm_add(a.center,qm_scale(qm_clone(a.linear),shift));
  let linear:QMat=qm_scale(qm_clone(a.linear),scale);
  let rem:IvMat=ivm_zeros(a.rows,a.cols);
  let i:i64=0;while(i<a.rows){let j:i64=0;while(j<a.cols){
    ivm_set(rem,i,j,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}
  return new IvAffineMat(a.generator,a.rows,a.cols,center,linear,rem);
}

fn hm_subcell(q:i64)->IvAffineCell{
  if(q<0 || q>=4){trap();}
  return match(iva_cell(7315,rat(1,2)+rat(2*q+1,2048),rat(1,2048))){
    some(z)=>z,none=>{trap();}};
}

fn hm_step(phi:borrow IvAffineMat,z:borrow IvAffineMat)->HmGraph{
  if(phi.generator!=7315 || z.generator!=7315 ||
     phi.rows!=12 || phi.cols!=12 || z.rows!=6 || z.cols!=6){
    return hm_graph_fail();}
  let pii:IvAffineMat=hm_select_block(phi,true,true);
  let pij:IvAffineMat=hm_select_block(phi,true,false);
  let pji:IvAffineMat=hm_select_block(phi,false,true);
  let pjj:IvAffineMat=hm_select_block(phi,false,false);
  let a:IvAffineResult=ivam_mul_checked(pij,z);
  let b:IvAffineResult=ivam_mul_checked(pjj,z);
  if(!a.ok || !b.ok){return hm_graph_fail();}
  let m0:IvAffineResult=ivam_add_checked(pii,a.value);
  let n0:IvAffineResult=ivam_add_checked(pji,b.value);
  if(!m0.ok || !n0.ok){return hm_graph_fail();}
  let m:IvAffineResult=ivam_rebase_dyadic(m0.value,128);
  let n:IvAffineResult=ivam_rebase_dyadic(n0.value,128);
  if(!m.ok || !n.ok){return hm_graph_fail();}
  let rm:IvAffineRank=ivam_full_column_rank_cells(m.value,64);
  if(!rm.certified || rm.rank!=6){return hm_graph_fail();}
  let solved:HmResult=hm_right_solve(n.value,m.value);
  if(!solved.ok || hm_norm_hi(solved.value)>=2.0){
    return hm_graph_fail();}
  return new HmGraph(true,ivam_clone(solved.value),ivam_clone(m.value));
}

fn hm_gauge()->IvAffineMat{
  // Nontrivial S in GL(3,Q), applied identically to Re and Im columns.
  // This is a strict subset of GL(3,Q(i)) and has determinant one.
  let s:QMat=qm_new(6,6);let i:i64=0;while(i<6){
    s=qm_set(s,i,i,rat(1,1));i=i+1;}
  s=qm_set(s,0,1,rat(1,2));s=qm_set(s,1,2,rat(1,3));
  s=qm_set(s,3,4,rat(1,2));s=qm_set(s,4,5,rat(1,3));
  return ivam_constant(7315,s);
}

fn hm_run_subcell(q:i64)->bool{
  let cell:IvAffineCell=hm_subcell(q);
  let initial:IvAffineMat=hm_restrict_global(
    ht_standard_to_block_rows(ht_initial()),cell);
  let g0:HmGraph=hm_from_basis(initial);
  if(!g0.ok || hm_norm_hi(g0.z)>=2.0){println("REFUSE initial-chart");return false;}
  let initial_rank:IvAffineRank=ivam_full_column_rank_cells(g0.pivot,64);
  if(!initial_rank.certified || initial_rank.rank!=6){
    println("REFUSE initial-pivot-rank");return false;}

  let gy0:IvAffineResult=ivam_mul_checked(initial,hm_gauge());
  if(!gy0.ok){println("REFUSE gauge-apply");return false;}
  let gg0:HmGraph=hm_from_basis(gy0.value);
  if(!gg0.ok || !hm_intersects(g0.z,gg0.z)){
    println("REFUSE gauge-initial");return false;}

  let z:IvAffineMat=ivam_clone(g0.z);
  let zg:IvAffineMat=ivam_clone(gg0.z);
  let direct:IvAffineMat=ivam_clone(initial);
  let max_norm:f64=hm_norm_hi(z);
  let p:i64=0;while(p<16){
    let ta:Iv=iv_from_rat(rat(1,4194304)+rat(p,67108864));
    let tb:Iv=iv_from_rat(rat(1,4194304)+rat(p+1,67108864));
    let ag:IvAffineMat=ht_coeff_0(p,iv(ta.lo,tb.hi));
    let a:IvAffineMat=hm_restrict_global(ag,cell);
    let w:IvAffineMat=match(sl_local_transition(a,rat(1,67108864),12)){
      some(q)=>q,none=>{println("REFUSE local-factor");return false;}};
    if(w.generator!=7315){println("REFUSE generator");return false;}

    let next:HmGraph=hm_step(w,z);
    let nextg:HmGraph=hm_step(w,zg);
    if(!next.ok || !nextg.ok){println(strfmt(system_allocator(),
      "REFUSE mobius-panel {}",[p]));return false;}
    z=ivam_clone(next.z);zg=ivam_clone(nextg.z);
    let zn:f64=hm_norm_hi(z);if(zn>max_norm){max_norm=zn;}
    if(!hm_intersects(z,zg)){println("REFUSE gauge-panel");return false;}

    let dn:IvAffineResult=ivam_apply_rect(w,direct);
    if(!dn.ok){println("REFUSE direct-apply");return false;}
    let dr:IvAffineResult=ivam_rebase_dyadic(dn.value,128);
    if(!dr.ok){println("REFUSE direct-rebase");return false;}
    direct=ivam_clone(dr.value);
    let bz:IvAffineMat=hm_graph_basis(z);
    // Rank is certified on the named chart pivot, which is the exact
    // identity by construction.  Do not ask a generic full-box pivot search
    // to rediscover a deliberately fixed Grassmann chart.
    let rz:IvAffineRank=ivam_full_column_rank_cells(
      hm_select_rows(bz,true),64);
    if(!rz.certified || rz.rank!=6){println("REFUSE graph-rank");return false;}
    println(strfmt(system_allocator(),
      "PANEL q={} p={} rank={} norm={} width={}",
      [q,p,rz.rank,zn,ivam_max_width(z)]));
    p=p+1;
  }

  let direct_graph:HmGraph=hm_from_basis(direct);
  if(!direct_graph.ok || !hm_intersects(z,direct_graph.z)){
    println("REFUSE direct-intersection");return false;}
  if(!hm_intersects(z,zg)){println("REFUSE gauge-endpoint");return false;}
  let graph_width:f64=ivam_max_width(z);
  let direct_width:f64=ivam_max_width(direct_graph.z);
  let improvement:f64=direct_width/graph_width;
  println(strfmt(system_allocator(),
    "RESULT q={} generator={} panels={} initial_rank={} endpoint_rank={} max_norm={} graph_width={} direct_rechart_width={} improvement={} direct_intersection={} gauge_invariant={}",
    [q,7315,16,initial_rank.rank,6,max_norm,graph_width,direct_width,
     improvement,hm_intersects(z,direct_graph.z),hm_intersects(z,zg)]));
  if(!(improvement>=2.0)){println("WIDTH_SHORTFALL");return false;}
  println("PASS HORIZON_GRASSMANN_MOBIUS_ONE_SHELL");
  return true;
}

pub fn axial_horizon_grassmann_mobius_one_shell()->bool{
  let q:i64=0;while(q<4){
    if(!hm_run_subcell(q)){return false;}q=q+1;}
  println("PASS HORIZON_GRASSMANN_MOBIUS_ALL_SUBCELLS");
  return true;
}

pub fn main()->i64{
  if(!axial_horizon_grassmann_mobius_one_shell()){return 3;}return 42;
}
'''


def render() -> tuple[str, dict]:
    require(sha256(BASE_PRODUCER) == BASE_PRODUCER_SHA256, "base producer drift")
    require(sha256(BASE_SOURCE) == BASE_SOURCE_SHA256, "base source drift")
    source = BASE_SOURCE.read_text()
    require("pub fn axial_horizon_to_r4()->bool{" in source, "base flow missing")
    require("pub fn main()" not in source, "base source contains a terminal main")
    rendered = source + INSERT
    metadata = {
        "schema": "phase3-axial-horizon-grassmann-mobius-source-v1",
        "input_commit": INPUT_COMMIT,
        "generator": GENERATOR,
        "omega_cell": ["1/2", "129/256"],
        "rho_cell": ["1/4194304", "1/2097152"],
        "complex_state_order": ["P", "P_prime", "Q", "Q_prime", "H1", "rho_F"],
        "block_real_state_order": [
            "Re(P)", "Re(P_prime)", "Re(Q)", "Re(Q_prime)",
            "Im(P)", "Im(P_prime)", "Im(Q)", "Im(Q_prime)",
            "Re(H1)", "Re(rho_F)", "Im(H1)", "Im(rho_F)",
        ],
        "pivot_complex_rows": list(PIVOT_COMPLEX),
        "graph_complex_rows": list(GRAPH_COMPLEX),
        "pivot_real_block_rows": list(PIVOT_REAL_BLOCK),
        "graph_real_block_rows": list(GRAPH_REAL_BLOCK),
        "omega_subcells": 4,
        "panels_per_subcell": 16,
        "local_order": 12,
        "dyadic_rebase_bits": REBASE_BITS,
        "chart_norm_limit": 2,
        "width_improvement_minimum": 2,
        "mobius_formula": "(Phi_JI+Phi_JJ*Z)*(Phi_II+Phi_IJ*Z)^-1",
        "right_solve_formula": "X*A=B via A^T*X^T=B^T",
        "base_producer_path": str(BASE_PRODUCER.relative_to(PHYSICS)),
        "base_producer_sha256": BASE_PRODUCER_SHA256,
        "base_source_path": str(BASE_SOURCE.relative_to(PHYSICS)),
        "base_source_sha256": BASE_SOURCE_SHA256,
        "base_render_imports": BASE_RENDER_IMPORTS,
        "does_not_establish": [
            "transport beyond the first dyadic horizon shell",
            "horizon-labelled amplitude transport",
            "a horizon-to-r4 map or horizon-to-infinity connection",
            "scattering, flux-sign, stability, ghost, positivity, CPT or unitarity",
            "other frequency cells, ell values or polar parity",
        ],
    }
    return rendered, metadata


def produce(output: Path = OUTPUT, metadata_path: Path = METADATA) -> None:
    rendered, metadata = render()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered)
    metadata["source_sha256"] = hashlib.sha256(rendered.encode()).hexdigest()
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def main() -> int:
    produce()
    print(OUTPUT)
    print(METADATA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
