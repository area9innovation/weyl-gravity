"""Degree-two validated transport of the two finite infinity trace planes.

This module renders small Forge programs which consume the already-certified
local radial factors.  The programs carry each six-real-dimensional plane as
``Y = G_chart(Z) A``.  The Grassmann graph ``Z`` prevents basis growth from
polluting the geometric plane, while the separate amplitude ``A`` retains the
actual normalization needed by the endpoint current and connection problem.

The first stage imports the action-derived practical infinity initializer.
Later stages import the deterministic ``math/ivtaylor`` serialization emitted
by the preceding stage.  No joined 12-by-12 interval hull is used as
classification evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import (
    INFINITY_SOURCE,
    build_microfactor_render_context,
)
from .child_cell_factor import (
    cell_payload,
    frequency_cell,
    prefix_boundary_crosswalk,
)
from .child_tail_join import load_cover as load_tail_cover
from .compose_child_global import crosswalk_matrix, restrict_prefix_matrix
from .infinity_plane_contract import (
    IMINUS_SELECTOR,
    IPLUS_SELECTOR,
    contract_payload,
    verify_contract,
)
from .infinity_plane_factor_manifest import (
    STAGE_BOUNDARIES,
    build_manifest,
    verify_manifest,
)
from .prefix_join import load_prefix_cover
from .verify_handoff import _file_sha256, _require, canonical_sha256


SCHEMA = "phase3-axial-infinity-plane-taylor-stage-v1"
GENERATOR = 7315
IVTAYLOR_COMMIT = "972aa4337b73cc0f632d9599fb345098bc8ccce8"
IVTAYLOR_PATH = "lib/math/ivtaylor.forge"
IVTAYLOR_SHA256 = "fd51f0ab2a1ebce950660b58dcfc31728c032de872001f50f907f11cfa2be103"
REAL_SELECTORS = {
    "Iminus": tuple(IMINUS_SELECTOR) + tuple(index + 6 for index in IMINUS_SELECTOR),
    "Iplus": tuple(IPLUS_SELECTOR) + tuple(index + 6 for index in IPLUS_SELECTOR),
}


class TaylorTransportError(RuntimeError):
    """Fail-closed producer refusal."""


def _strip_endpoint_source(path: Path) -> str:
    text = path.read_text()
    lines = [line for line in text.splitlines() if not line.startswith("import ")]
    text = "\n".join(lines)
    marker = "pub fn main() -> i64 {"
    if marker not in text:
        raise TaylorTransportError("infinity endpoint adapter has no terminal main")
    return text.split(marker, 1)[0].rstrip() + "\n"


def _f64(bits: str | int) -> str:
    if isinstance(bits, str):
        raw = int(bits, 16)
        if raw >= 1 << 63:
            raw -= 1 << 64
    else:
        raw = bits
    return f"f64_from_bits({raw})"


def _matrix_builder(name: str, matrix: dict[str, Any]) -> list[str]:
    lines = [
        f"fn {name}()->IvTaylorMat{{",
        "  let c0:QMat=qm_new(12,12);let c1:QMat=qm_new(12,12);",
        "  let c2:QMat=qm_new(12,12);let rem:IvMat=ivm_zeros(12,12);",
    ]
    for row in range(12):
        for col in range(12):
            center = matrix["center"][row][col]
            linear = matrix["linear"][row][col]
            remainder = matrix["remainder"][row][col]
            if center != "0/1":
                lines.append(
                    f'  c0=qm_set(c0,{row},{col},big("{center}"));'
                )
            if linear != "0/1":
                lines.append(
                    f'  c1=qm_set(c1,{row},{col},big("{linear}"));'
                )
            if remainder != ["0000000000000000", "0000000000000000"]:
                lines.append(
                    f"  ivm_set(rem,{row},{col},"
                    f"iv({_f64(remainder[0])},{_f64(remainder[1])}));"
                )
    lines += [
        "  return new IvTaylorMat(7315,12,12,c0,c1,c2,rem);",
        "}",
        "",
    ]
    return lines


def _serialized_builder(name: str, model: dict[str, Any]) -> list[str]:
    _require(
        model.get("schema") == "ivtaylor-degree2-v1"
        and model.get("degree") == 2
        and model.get("generator") == GENERATOR,
        f"{name}: incompatible Taylor serialization",
    )
    rows, cols = int(model["rows"]), int(model["cols"])
    lines = [
        f"fn {name}()->IvTaylorMat{{",
        f"  let c0:QMat=qm_new({rows},{cols});",
        f"  let c1:QMat=qm_new({rows},{cols});",
        f"  let c2:QMat=qm_new({rows},{cols});",
        f"  let rem:IvMat=ivm_zeros({rows},{cols});",
    ]
    for degree, key in enumerate(model["coefficients"]):
        for row in range(rows):
            for col in range(cols):
                value = str(key[row][col])
                if value not in ("0", "0/1"):
                    lines.append(
                        f'  c{degree}=qm_set(c{degree},{row},{col},'
                        f'big("{value}"));'
                    )
    for row in range(rows):
        for col in range(cols):
            lo, hi = model["remainder_bits"][row][col]
            if lo != 0 or hi != 0:
                lines.append(
                    f"  ivm_set(rem,{row},{col},iv({_f64(lo)},{_f64(hi)}));"
                )
    lines += [
        f"  return new IvTaylorMat(7315,{rows},{cols},c0,c1,c2,rem);",
        "}",
        "",
    ]
    return lines


def _chart_dispatch() -> str:
    pairs = ((0, 4), (1, 5), (2, 6), (3, 7), (8, 10), (9, 11))
    import itertools

    charts = tuple(itertools.combinations(range(6), 3))

    def selector_rows(triple: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(pairs[index][0] for index in triple) + tuple(
            pairs[index][1] for index in triple
        )

    def dispatch(name: str, rows_by_chart: list[tuple[int, ...]]) -> str:
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
        return f"fn pt_i64_{name}(chart:i64,k:i64)->i64{{{body}}}\n"

    pivots = [selector_rows(chart) for chart in charts]
    graphs = [
        selector_rows(tuple(index for index in range(6) if index not in chart))
        for chart in charts
    ]
    return dispatch("i", pivots) + dispatch("j", graphs)


COMMON = r'''
pub type PtMajorant = value struct {
  pub ok: bool,
  pub mantissa: Iv,
  pub binary_exponent: i64,
};

pub type PtState = scoped struct {
  pub ok: bool,
  pub chart: i64,
  pub z: IvTaylorMat,
  pub amplitude: IvTaylorMat,
  pub forward_bound: PtMajorant,
  pub inverse_bound: PtMajorant,
};

pub type PtBasisBounds = value struct {
  pub ok: bool,
  pub forward: Iv,
  pub inverse: Iv,
};

fn pm_fail()->PtMajorant{
  return PtMajorant(false,iv_point(0.0),0);
}

fn pm_normalize(x:Iv,e0:i64)->PtMajorant{
  if(!iv_finite(x) || x.hi<=0.0){return pm_fail();}
  let y:Iv=x;let e:i64=e0;
  let high:f64=f64_from_bits(5183643171103440896); // 2^128
  let down:f64=f64_from_bits(3454260914193170432); // 2^-256
  let up:f64=f64_from_bits(5760103923406864384);   // 2^256
  while(y.hi>high){y=iv_mul(y,iv_point(down));e=e+256;
    if(!iv_finite(y)){return pm_fail();}}
  while(y.hi>0.0 && y.hi<f64_from_bits(4030721666496593920)){
    y=iv_mul(y,iv_point(up));e=e-256;
    if(!iv_finite(y)){return pm_fail();}}
  return PtMajorant(true,y,e);
}

fn pm_from_iv(x:Iv)->PtMajorant{return pm_normalize(x,0);}

fn pm_mul_iv(a:PtMajorant,b:Iv)->PtMajorant{
  if(!a.ok || !iv_finite(b) || b.hi<=0.0){return pm_fail();}
  let first:PtMajorant=pm_normalize(a.mantissa,a.binary_exponent);
  if(!first.ok){return pm_fail();}
  return pm_normalize(iv_mul(first.mantissa,b),first.binary_exponent);
}

fn pt_zero()->IvTaylorMat{
  return ivtm_constant(7315,qm_new(6,6));
}

fn pt_identity6()->IvTaylorMat{
  return ivtm_identity(7315,6);
}

fn pt_fail()->PtState{
  return new PtState(false,-1,pt_zero(),pt_zero(),
    pm_fail(),pm_fail());
}

fn pt_rows(a:borrow IvTaylorMat,chart:i64,pivot:bool)->IvTaylorMat{
  let c0:QMat=qm_new(6,a.cols);let c1:QMat=qm_new(6,a.cols);
  let c2:QMat=qm_new(6,a.cols);let rem:IvMat=ivm_zeros(6,a.cols);
  let i:i64=0;while(i<6){
    let si:i64=if(pivot){pt_i64_i(chart,i)}else{pt_i64_j(chart,i)};
    let j:i64=0;while(j<a.cols){
      c0=qm_set(c0,i,j,qm_get(a.c0,si,j));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,j));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,j));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,6,a.cols,c0,c1,c2,rem);
}

fn pt_block(a:borrow IvTaylorMat,chart:i64,row_i:bool,col_i:bool)
->IvTaylorMat{
  let c0:QMat=qm_new(6,6);let c1:QMat=qm_new(6,6);
  let c2:QMat=qm_new(6,6);let rem:IvMat=ivm_zeros(6,6);
  let i:i64=0;while(i<6){
    let si:i64=if(row_i){pt_i64_i(chart,i)}else{pt_i64_j(chart,i)};
    let j:i64=0;while(j<6){
      let sj:i64=if(col_i){pt_i64_i(chart,j)}else{pt_i64_j(chart,j)};
      c0=qm_set(c0,i,j,qm_get(a.c0,si,sj));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,sj));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,sj));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,6,6,c0,c1,c2,rem);
}

fn pt_graph_basis(z:borrow IvTaylorMat,chart:i64)->IvTaylorMat{
  let c0:QMat=qm_new(12,6);let c1:QMat=qm_new(12,6);
  let c2:QMat=qm_new(12,6);let rem:IvMat=ivm_zeros(12,6);
  let i:i64=0;while(i<6){
    c0=qm_set(c0,pt_i64_i(chart,i),i,rat(1,1));
    let j:i64=0;while(j<6){
      c0=qm_set(c0,pt_i64_j(chart,i),j,qm_get(z.c0,i,j));
      c1=qm_set(c1,pt_i64_j(chart,i),j,qm_get(z.c1,i,j));
      c2=qm_set(c2,pt_i64_j(chart,i),j,qm_get(z.c2,i,j));
      ivm_set(rem,pt_i64_j(chart,i),j,ivm_at(z.remainder,i,j));
      j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,12,6,c0,c1,c2,rem);
}

fn pt_norm(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=iv_abs(ivm_at(h,i,j));if(x.hi>best){best=x.hi;}
    j=j+1;}i=i+1;}return best;
}

fn pt_operator_inf_norm_hi(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let sum:Iv=iv_point(0.0);let j:i64=0;
    while(j<a.cols){sum=iv_add(sum,iv_abs(ivm_at(h,i,j)));j=j+1;}
    if(sum.hi>best){best=sum.hi;}i=i+1;}
  return best;
}

fn pt_basis_bounds(a:borrow IvTaylorMat)->PtBasisBounds{
  if(a.rows!=6 || a.cols!=6){
    return PtBasisBounds(false,iv_point(0.0),iv_point(0.0));}
  let inverse:IvTaylorResult=ivtm_solve_left(a,ivtm_identity(7315,6));
  if(!inverse.ok){
    return PtBasisBounds(false,iv_point(0.0),iv_point(0.0));}
  let f:f64=pt_operator_inf_norm_hi(a);
  let g:f64=pt_operator_inf_norm_hi(inverse.value);
  if(f!=f || g!=g){
    return PtBasisBounds(false,iv_point(0.0),iv_point(0.0));}
  return PtBasisBounds(true,iv(0.0,f),iv(0.0,g));
}

fn pt_from_basis(y:borrow IvTaylorMat,chart:i64)->PtState{
  let u:IvTaylorMat=pt_rows(y,chart,true);
  let v:IvTaylorMat=pt_rows(y,chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=6){return pt_fail();}
  let zr:IvTaylorResult=ivtm_solve_right(v,u);
  if(!zr.ok){return pt_fail();}
  let z:IvTaylorResult=ivtm_rebase_dyadic(zr.value,160);
  let bounds:PtBasisBounds=pt_basis_bounds(u);
  if(!z.ok || !bounds.ok){return pt_fail();}
  // Plane-classifier normalization: discard the endpoint-coordinate
  // amplitude and retain only the graph.  This preserves the subspace but
  // does not preserve the original scattering amplitude normalization.
  return new PtState(true,chart,ivtm_clone(z.value),pt_identity6(),
    pm_from_iv(bounds.forward),pm_from_iv(bounds.inverse));
}

fn pt_reconstruct(s:borrow PtState)->IvTaylorResult{
  // The plane-only rail keeps amplitude exactly I6, so reconstruction is
  // literally G_chart(Z).  Avoid multiplying by an interval identity, which
  // would add outward-rounding fuzz to structurally zero pivot remainders.
  return new IvTaylorResult(true,0,pt_graph_basis(s.z,s.chart));
}

fn pt_rechart(s:borrow PtState,new_chart:i64)->PtState{
  if(!s.ok){return pt_fail();}
  if(new_chart==s.chart){
    return new PtState(true,s.chart,ivtm_clone(s.z),
      ivtm_clone(s.amplitude),s.forward_bound,s.inverse_bound);}
  let g:IvTaylorMat=pt_graph_basis(s.z,s.chart);
  let u:IvTaylorMat=pt_rows(g,new_chart,true);
  let v:IvTaylorMat=pt_rows(g,new_chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,64);
  if(!rank.certified || rank.rank!=6){return pt_fail();}
  let zr0:IvTaylorResult=ivtm_solve_right(v,u);
  if(!zr0.ok){return pt_fail();}
  let zr:IvTaylorResult=ivtm_rebase_dyadic(zr0.value,160);
  let bounds:PtBasisBounds=pt_basis_bounds(u);
  if(!zr.ok || !bounds.ok){return pt_fail();}
  return new PtState(true,new_chart,ivtm_clone(zr.value),pt_identity6(),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));
}

fn pt_best_chart(s:borrow PtState)->PtState{
  let best:PtState=pt_fail();let c:i64=0;
  while(c<20){
    let cand:PtState=pt_rechart(s,c);
    if(cand.ok && (!best.ok || pt_norm(cand.z)<pt_norm(best.z))){
      best=new PtState(true,cand.chart,ivtm_clone(cand.z),
        ivtm_clone(cand.amplitude),cand.forward_bound,cand.inverse_bound);
    }
    drop(cand);c=c+1;
  }
  return best;
}

fn pt_best_basis(y:borrow IvTaylorMat)->PtState{
  let best:PtState=pt_fail();let c:i64=0;
  while(c<20){
    let cand:PtState=pt_from_basis(y,c);
    if(cand.ok && (!best.ok || pt_norm(cand.z)<pt_norm(best.z))){
      best=new PtState(true,cand.chart,ivtm_clone(cand.z),
        ivtm_clone(cand.amplitude),cand.forward_bound,cand.inverse_bound);
    }
    drop(cand);c=c+1;
  }
  return best;
}

fn pt_step(phi:borrow IvTaylorMat,s:borrow PtState)->PtState{
  let pii:IvTaylorMat=pt_block(phi,s.chart,true,true);
  let pij:IvTaylorMat=pt_block(phi,s.chart,true,false);
  let pji:IvTaylorMat=pt_block(phi,s.chart,false,true);
  let pjj:IvTaylorMat=pt_block(phi,s.chart,false,false);
  let az:IvTaylorResult=ivtm_mul_checked(pij,s.z);
  let bz:IvTaylorResult=ivtm_mul_checked(pjj,s.z);
  if(!az.ok || !bz.ok){return pt_fail();}
  let m0:IvTaylorResult=ivtm_add_checked(pii,az.value);
  let n0:IvTaylorResult=ivtm_add_checked(pji,bz.value);
  if(!m0.ok || !n0.ok){return pt_fail();}
  let m:IvTaylorResult=ivtm_rebase_dyadic(m0.value,160);
  let n:IvTaylorResult=ivtm_rebase_dyadic(n0.value,160);
  if(!m.ok || !n.ok){return pt_fail();}
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(m.value,64);
  if(!rank.certified || rank.rank!=6){return pt_fail();}
  let zr0:IvTaylorResult=ivtm_solve_right(n.value,m.value);
  if(!zr0.ok){return pt_fail();}
  let zr:IvTaylorResult=ivtm_rebase_dyadic(zr0.value,160);
  let bounds:PtBasisBounds=pt_basis_bounds(m.value);
  if(!zr.ok || !bounds.ok){return pt_fail();}
  return new PtState(true,s.chart,ivtm_clone(zr.value),pt_identity6(),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));
}

fn pt_step_any(phi:borrow IvTaylorMat,s:borrow PtState)->PtState{
  let direct:PtState=pt_step(phi,s);
  if(direct.ok){
    return new PtState(true,direct.chart,ivtm_clone(direct.z),
      ivtm_clone(direct.amplitude),direct.forward_bound,
      direct.inverse_bound);}
  let best:PtState=pt_fail();let c:i64=0;
  while(c<20){
    let charted:PtState=pt_rechart(s,c);
    if(charted.ok){
      let stepped:PtState=pt_step(phi,charted);
      if(stepped.ok && (!best.ok || pt_norm(stepped.z)<pt_norm(best.z))){
        best=new PtState(true,stepped.chart,ivtm_clone(stepped.z),
          ivtm_clone(stepped.amplitude),stepped.forward_bound,
          stepped.inverse_bound);
      }
      drop(stepped);
    }
    drop(charted);c=c+1;
  }
  return best;
}

fn pt_select_columns(a:borrow IvTaylorMat,plus:bool)->IvTaylorMat{
  let c0:QMat=qm_new(12,6);let c1:QMat=qm_new(12,6);
  let c2:QMat=qm_new(12,6);let rem:IvMat=ivm_zeros(12,6);
  let j:i64=0;while(j<6){
    let sj:i64=if(plus){
      if(j==0){2}else{if(j==1){3}else{if(j==2){5}else{
      if(j==3){8}else{if(j==4){9}else{11}}}}}}
    else{
      if(j==0){0}else{if(j==1){1}else{if(j==2){4}else{
      if(j==3){6}else{if(j==4){7}else{10}}}}}};
    let i:i64=0;while(i<12){
      c0=qm_set(c0,i,j,qm_get(a.c0,i,sj));
      c1=qm_set(c1,i,j,qm_get(a.c1,i,sj));
      c2=qm_set(c2,i,j,qm_get(a.c2,i,sj));
      ivm_set(rem,i,j,ivm_at(a.remainder,i,sj));i=i+1;}j=j+1;}
  return new IvTaylorMat(7315,12,6,c0,c1,c2,rem);
}

fn pt_standard_to_block(a:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(12,a.cols);let c1:QMat=qm_new(12,a.cols);
  let c2:QMat=qm_new(12,a.cols);let rem:IvMat=ivm_zeros(12,a.cols);
  let i:i64=0;while(i<12){
    let si:i64=if(i<8){if(i<4){i}else{i+2}}
      else{if(i<10){i-4}else{i}};
    let j:i64=0;while(j<a.cols){
      c0=qm_set(c0,i,j,qm_get(a.c0,si,j));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,j));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,j));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,12,a.cols,c0,c1,c2,rem);
}

fn pt_block_to_standard(a:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(12,a.cols);let c1:QMat=qm_new(12,a.cols);
  let c2:QMat=qm_new(12,a.cols);let rem:IvMat=ivm_zeros(12,a.cols);
  let i:i64=0;while(i<12){
    let si:i64=if(i<4){i}else{if(i<6){8+i-4}
      else{if(i<10){4+i-6}else{10+i-10}}};
    let j:i64=0;while(j<a.cols){
      c0=qm_set(c0,i,j,qm_get(a.c0,si,j));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,j));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,j));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,12,a.cols,c0,c1,c2,rem);
}

fn pt_hcat(a:borrow IvTaylorMat,b:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(12,a.cols+b.cols);
  let c1:QMat=qm_new(12,a.cols+b.cols);
  let c2:QMat=qm_new(12,a.cols+b.cols);
  let rem:IvMat=ivm_zeros(12,a.cols+b.cols);
  let i:i64=0;while(i<12){let j:i64=0;while(j<a.cols+b.cols){
    let from_a:bool=j<a.cols;let sj:i64=if(from_a){j}else{j-a.cols};
    c0=qm_set(c0,i,j,if(from_a){qm_get(a.c0,i,sj)}else{qm_get(b.c0,i,sj)});
    c1=qm_set(c1,i,j,if(from_a){qm_get(a.c1,i,sj)}else{qm_get(b.c1,i,sj)});
    c2=qm_set(c2,i,j,if(from_a){qm_get(a.c2,i,sj)}else{qm_get(b.c2,i,sj)});
    ivm_set(rem,i,j,if(from_a){ivm_at(a.remainder,i,sj)}
      else{ivm_at(b.remainder,i,sj)});j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,12,a.cols+b.cols,c0,c1,c2,rem);
}
'''


def _imports() -> str:
    return "\n".join([
        "// expect: 42",
        "// backends: c native",
        "// Degree-two shared-frequency infinity-plane transport.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivlinode;",
        "import math/ivendpoint;",
        "import math/ivaffine;",
        "import math/ivtaylor;",
        "import ds/vec;",
        "import ds/manualvec;",
        "import text/parse;",
        "import text/format;",
        "import text/strbuilder;",
        "",
    ])


def _initializer_source(child: int) -> str:
    lo, hi = frequency_cell(child)
    center, radius = (lo + hi) / 2, (hi - lo) / 2
    return _strip_endpoint_source(INFINITY_SOURCE) + f'''
fn pt_qsub(a:borrow QMat,b:borrow QMat)->QMat{{
  return qm_add(a,qm_scale(qm_clone(b),rat(-1,1)));
}}
fn pt_blockdiag_q(ca:borrow QMat,ka:borrow QMat)->QMat{{
  let z:QMat=qm_new(12,12);let i:i64=0;while(i<8){{let j:i64=0;
    while(j<8){{z=qm_set(z,i,j,qm_get(ca,i,j));j=j+1;}}i=i+1;}}
  i=0;while(i<4){{let j:i64=0;while(j<4){{
    z=qm_set(z,8+i,8+j,qm_get(ka,i,j));j=j+1;}}i=i+1;}}return z;
}}
fn pt_block_to_standard_q_both(a:borrow QMat)->QMat{{
  let z:QMat=qm_new(12,12);let i:i64=0;while(i<12){{
    let bi:i64=if(i<4){{i}}else{{if(i<6){{8+i-4}}else{{
      if(i<10){{4+i-6}}else{{i}}}}}};let j:i64=0;while(j<12){{
    let bj:i64=if(j<4){{j}}else{{if(j<6){{8+j-4}}else{{
      if(j<10){{4+j-6}}else{{j}}}}}};
    z=qm_set(z,i,j,qm_get(a,bi,bj));j=j+1;}}i=i+1;}}return z;
}}
fn pt_infinity_q(which:i64)->QMat{{
  let a:QMat=if(which==0){{carrier_center_0()}}else{{carrier_center_1()}};
  let k:QMat=if(which==0){{kernel_center_0()}}else{{kernel_center_1()}};
  return pt_block_to_standard_q_both(pt_blockdiag_q(a,k));
}}
fn pt_parent_affine()->IvAffineMat{{
  let parent:IvAffineCell=match(iva_cell(7315,big("257/512"),
    big("1/512"))){{some(z)=>z,none=>{{trap();}}}};
  let center:QMat=pt_infinity_q(0);
  let derivative:QMat=qm_scale(
    pt_qsub(pt_infinity_q(1),pt_infinity_q(0)),rat(256,1));
  let base:IvAffineResult=ivam_taylor1(parent,center,derivative,
    ivm_zeros(12,12));if(!base.ok){{trap();}}
  let ep:IvEndpointCert=axial_infinity_initializer(0);if(!ep.ok){{trap();}}
  let rem:IvMat=ivm_sub(ep.value,ivam_hull(base.value));
  let out:IvAffineResult=ivam_taylor1(parent,center,derivative,rem);
  if(!out.ok){{trap();}}return ivam_clone(out.value);
}}
fn pt_initial_full()->IvTaylorMat{{
  let parent:IvTaylorCell=match(ivt_cell(7315,big("257/512"),
    big("1/512"))){{some(z)=>z,none=>{{trap();}}}};
  let child:IvTaylorCell=match(ivt_cell(7315,big("{center}"),
    big("{radius}"))){{some(z)=>z,none=>{{trap();}}}};
  let lifted:IvTaylorMat=ivtm_from_affine(pt_parent_affine());
  let out:IvTaylorResult=ivtm_restrict(lifted,parent,child);
  if(!out.ok){{trap();}}return ivtm_clone(out.value);
}}
fn pt_input_minus()->IvTaylorMat{{
  return pt_standard_to_block(pt_select_columns(pt_initial_full(),false));
}}
fn pt_input_plus()->IvTaylorMat{{
  return pt_standard_to_block(pt_select_columns(pt_initial_full(),true));
}}
'''


def _continuation_source(previous: dict[str, Any]) -> str:
    minus_state = previous["chart_states"]["Iminus"]
    plus_state = previous["chart_states"]["Iplus"]
    minus_bounds = previous["basis_change_majorants"]["Iminus"]
    plus_bounds = previous["basis_change_majorants"]["Iplus"]

    def majorant_expr(record: dict[str, Any]) -> str:
        bits = record["mantissa_bits"]
        return (
            "PtMajorant(true,"
            f"iv({_f64(bits[0])},{_f64(bits[1])}),"
            f"{int(record['binary_exponent'])})"
        )

    return "\n".join(
        [
            "fn big(s:string)->Rat{return match(parse<Rat>(bytes(s),0)){",
            "  ok(r)=>r,err(e)=>trap()};}",
            "",
        ]
        + _serialized_builder("pt_previous_minus_z", minus_state["z"])
        + _serialized_builder("pt_previous_plus_z", plus_state["z"])
        + [
            "fn pt_seed_minus()->PtState{",
            f"  return new PtState(true,{minus_state['chart']},",
            "    pt_previous_minus_z(),pt_identity6(),",
            f"    {majorant_expr(minus_bounds['forward'])},",
            f"    {majorant_expr(minus_bounds['inverse'])});",
            "}",
            "fn pt_seed_plus()->PtState{",
            f"  return new PtState(true,{plus_state['chart']},",
            "    pt_previous_plus_z(),pt_identity6(),",
            f"    {majorant_expr(plus_bounds['forward'])},",
            f"    {majorant_expr(plus_bounds['inverse'])});",
            "}",
            "",
        ]
    )


def _load_matrices(
    child: int, artifact_dir: Path, repo_root: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = build_manifest(child, artifact_dir, repo_root)
    verify_manifest(manifest, child, artifact_dir, repo_root, rebuild=False)
    prefix_context = build_microfactor_render_context()
    child_context = build_microfactor_render_context(frequency_cell(child))
    _, prefix = load_prefix_cover(
        artifact_dir, repo_root, context=prefix_context
    )
    _, tail = load_tail_cover(
        artifact_dir / "child_tail", child, repo_root,
        context=child_context, prefix_context=prefix_context,
    )
    matrices = [restrict_prefix_matrix(item["matrix"], child) for item in prefix]
    matrices.append(crosswalk_matrix(prefix_boundary_crosswalk(child, prefix_context)))
    matrices += [item["matrix"] for item in tail]
    _require(len(matrices) == 279, "Taylor transport: incomplete factor cover")
    return manifest, matrices


def render_stage(
    *,
    child: int,
    stage: int,
    artifact_dir: Path,
    repo_root: Path,
    previous: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    if not 0 <= stage < len(STAGE_BOUNDARIES) - 1:
        raise TaylorTransportError("stage out of range")
    contract = contract_payload()
    verify_contract(contract)
    manifest, matrices = _load_matrices(child, artifact_dir, repo_root)
    ordinals = manifest["stages"][stage]["step_ordinals"]
    if stage == 0 and previous is not None:
        raise TaylorTransportError("stage zero cannot import a previous result")
    if stage > 0:
        _require(previous is not None, "Taylor transport: missing previous stage")
        _require(
            previous["child"] == child and previous["stage"] == stage - 1,
            "Taylor transport: previous stage mismatch",
        )

    lines = [_imports()]
    lines.append(_initializer_source(child) if stage == 0
                 else _continuation_source(previous))
    lines.append(_chart_dispatch())
    lines.append(COMMON)
    for local, ordinal in enumerate(ordinals):
        lines += _matrix_builder(f"pt_factor_{local:03d}", matrices[ordinal])

    initial_lines = (
        [
            "  let minus:PtState=pt_best_basis(pt_input_minus());",
            "  let plus:PtState=pt_best_basis(pt_input_plus());",
        ]
        if stage == 0
        else [
            "  let minus:PtState=pt_seed_minus();",
            "  let plus:PtState=pt_seed_plus();",
        ]
    )
    lines += [
        "pub fn main()->i64{",
        *initial_lines,
        '  if(!minus.ok || !plus.ok){println("REFUSE initial-chart");return 3;}',
    ]
    for local, ordinal in enumerate(ordinals):
        lines += [
            f"  let phi_{local}:IvTaylorMat=pt_factor_{local:03d}();",
            f"  let mn_{local}:PtState=pt_step_any(phi_{local},minus);",
            f"  let pn_{local}:PtState=pt_step_any(phi_{local},plus);",
            f'  if(!mn_{local}.ok || !pn_{local}.ok){{',
            f'    println("REFUSE step ordinal={ordinal}");return 3;}}',
            f"  minus=new PtState(true,mn_{local}.chart,ivtm_clone(mn_{local}.z),",
            f"    ivtm_clone(mn_{local}.amplitude),mn_{local}.forward_bound,",
            f"    mn_{local}.inverse_bound);",
            f"  plus=new PtState(true,pn_{local}.chart,ivtm_clone(pn_{local}.z),",
            f"    ivtm_clone(pn_{local}.amplitude),pn_{local}.forward_bound,",
            f"    pn_{local}.inverse_bound);",
        ]
        if (local + 1) % 4 == 0:
            lines += [
                f"  let mb_{local}:PtState=pt_best_chart(minus);",
                f"  let pb_{local}:PtState=pt_best_chart(plus);",
                f'  if(!mb_{local}.ok || !pb_{local}.ok){{',
                f'    println("REFUSE rechart ordinal={ordinal}");return 3;}}',
                f"  minus=new PtState(true,mb_{local}.chart,ivtm_clone(mb_{local}.z),",
                f"    ivtm_clone(mb_{local}.amplitude),mb_{local}.forward_bound,",
                f"    mb_{local}.inverse_bound);",
                f"  plus=new PtState(true,pb_{local}.chart,ivtm_clone(pb_{local}.z),",
                f"    ivtm_clone(pb_{local}.amplitude),pb_{local}.forward_bound,",
                f"    pb_{local}.inverse_bound);",
            ]
    lines += [
        "  let mr:IvTaylorResult=pt_reconstruct(minus);",
        "  let pr:IvTaylorResult=pt_reconstruct(plus);",
        '  if(!mr.ok || !pr.ok){println("REFUSE reconstruction");return 3;}',
        "  let mstd:IvTaylorMat=pt_block_to_standard(mr.value);",
        "  let pstd:IvTaylorMat=pt_block_to_standard(pr.value);",
        "  let combined:IvTaylorMat=pt_hcat(mstd,pstd);",
        "  let rm:IvTaylorRank=ivtm_full_column_rank_cells(mstd,64);",
        "  let rp:IvTaylorRank=ivtm_full_column_rank_cells(pstd,64);",
        "  let rc:IvTaylorRank=ivtm_full_column_rank_cells(combined,64);",
        '  println(strfmt(system_allocator(),"RANKS {} {} {}",',
        "    [rm.rank,rp.rank,rc.rank]));",
        '  println(strfmt(system_allocator(),"RANK_CERTS {} {} {} CODES {} {} {} CELLS {} {} {}",',
        "    [rm.certified,rp.certified,rc.certified,rm.refusal_code,",
        "     rp.refusal_code,rc.refusal_code,rm.cells_checked,",
        "     rp.cells_checked,rc.cells_checked]));",
        "  let combined_ok:bool=rc.certified && rc.rank==12;",
        "  let minus_ok:bool=(rm.certified && rm.rank==6) || combined_ok;",
        "  let plus_ok:bool=(rp.certified && rp.rank==6) || combined_ok;",
        '  println(strfmt(system_allocator(),"RANK_PROOF minus={} plus={} combined={} derived_from_combined={}",',
        "    [minus_ok,plus_ok,combined_ok,combined_ok]));",
        '  if(!minus_ok || !plus_ok || !combined_ok){',
        '    println("REFUSE terminal-rank");return 3;}',
        "  let ms:String=ivtm_serialize(mstd,0);",
        "  let ps:String=ivtm_serialize(pstd,0);",
        "  let mz:String=ivtm_serialize(minus.z,0);",
        "  let pz:String=ivtm_serialize(plus.z,0);",
        '  println(strfmt(system_allocator(),"CHARTS {} {}",',
        "    [minus.chart,plus.chart]));",
        '  println(strfmt(system_allocator(),"MINUS {}",[str_view(ms)]));',
        '  println(strfmt(system_allocator(),"PLUS {}",[str_view(ps)]));',
        '  println(strfmt(system_allocator(),"MINUS_Z {}",[str_view(mz)]));',
        '  println(strfmt(system_allocator(),"PLUS_Z {}",[str_view(pz)]));',
        '  if(!minus.forward_bound.ok || !minus.inverse_bound.ok ||',
        '     !plus.forward_bound.ok || !plus.inverse_bound.ok ||',
        '     !iv_finite(minus.forward_bound.mantissa) ||',
        '     !iv_finite(minus.inverse_bound.mantissa) ||',
        '     !iv_finite(plus.forward_bound.mantissa) ||',
        '     !iv_finite(plus.inverse_bound.mantissa)){',
        '    println("REFUSE nonfinite-basis-bound");return 3;}',
        '  println(strfmt(system_allocator(),"BOUNDS {} {} {} {} {} {} {} {} {} {} {} {}",',
        "    [f64_bits(minus.forward_bound.mantissa.lo),",
        "     f64_bits(minus.forward_bound.mantissa.hi),",
        "     minus.forward_bound.binary_exponent,",
        "     f64_bits(minus.inverse_bound.mantissa.lo),",
        "     f64_bits(minus.inverse_bound.mantissa.hi),",
        "     minus.inverse_bound.binary_exponent,",
        "     f64_bits(plus.forward_bound.mantissa.lo),",
        "     f64_bits(plus.forward_bound.mantissa.hi),",
        "     plus.forward_bound.binary_exponent,",
        "     f64_bits(plus.inverse_bound.mantissa.lo),",
        "     f64_bits(plus.inverse_bound.mantissa.hi),",
        "     plus.inverse_bound.binary_exponent]));",
        "  drop(ms);drop(ps);drop(mz);drop(pz);",
        (
            f'  println("PASS child={child} stage={stage}");return 42;'
        ),
        "}",
        "",
    ]
    source = "\n".join(lines)
    metadata = {
        "child": child,
        "stage": stage,
        "cell": cell_payload(child),
        "radial": manifest["stages"][stage]["radial"],
        "factor_ordinals": ordinals,
        "factor_count": len(ordinals),
        "factor_manifest_payload_sha256": manifest["payload_sha256"],
        "plane_contract_payload_sha256": contract["payload_sha256"],
        "ivtaylor": {
            "commit": IVTAYLOR_COMMIT,
            "path": IVTAYLOR_PATH,
            "sha256": IVTAYLOR_SHA256,
            "degree": 2,
        },
        "plane_representation": {
            "kind": "normalized-grassmann-graph-basis",
            "amplitude_at_each_chart": "identity-6",
            "preserves": [
                "propagated subspace",
                "separate and combined rank",
                "current-form inertia under congruence",
            ],
            "does_not_preserve": [
                "original infinity endpoint amplitude normalization",
                "connection or scattering amplitudes",
            ],
        },
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    }
    if previous is not None:
        metadata["previous_payload_sha256"] = previous["payload_sha256"]
    return source, metadata


def parse_stage_output(
    output: str,
) -> tuple[dict[str, Any], dict[str, int], dict[str, Any]]:
    minus = plus = None
    minus_z = plus_z = None
    charts = None
    bounds = None
    ranks = None
    direct = proof = None

    def parse_ivtm(text: str) -> dict[str, Any]:
        # The Forge kernel deliberately uses exact rational rendering inside
        # its deterministic JSON-shaped serialization.  Quote ``p/q`` tokens
        # before handing the envelope to the standard JSON parser; integer
        # zeros remain ordinary JSON numbers.
        quoted = re.sub(
            r"(?<![0-9A-Za-z_\"])(-?[0-9]+/[0-9]+)(?![0-9A-Za-z_\"])",
            r'"\1"',
            text,
        )
        return json.loads(quoted)

    for line in output.splitlines():
        if line.startswith("MINUS "):
            minus = parse_ivtm(line[6:])
        elif line.startswith("PLUS "):
            plus = parse_ivtm(line[5:])
        elif line.startswith("MINUS_Z "):
            minus_z = parse_ivtm(line[8:])
        elif line.startswith("PLUS_Z "):
            plus_z = parse_ivtm(line[7:])
        elif line.startswith("CHARTS "):
            values = [int(value) for value in line.split()[1:]]
            if len(values) == 2:
                charts = {"Iminus": values[0], "Iplus": values[1]}
        elif line.startswith("BOUNDS "):
            values = [int(value) for value in line.split()[1:]]
            if len(values) == 12:
                bounds = {
                    "Iminus": {
                        "forward": {
                            "mantissa_bits": values[0:2],
                            "binary_exponent": values[2],
                        },
                        "inverse": {
                            "mantissa_bits": values[3:5],
                            "binary_exponent": values[5],
                        },
                    },
                    "Iplus": {
                        "forward": {
                            "mantissa_bits": values[6:8],
                            "binary_exponent": values[8],
                        },
                        "inverse": {
                            "mantissa_bits": values[9:11],
                            "binary_exponent": values[11],
                        },
                    },
                }
        elif line.startswith("RANKS "):
            values = [int(value) for value in line.split()[1:]]
            if len(values) == 3:
                ranks = {
                    "Iminus": values[0],
                    "Iplus": values[1],
                    "combined": values[2],
                }
        elif line.startswith("RANK_CERTS "):
            values = line.split()[1:]
            if (
                len(values) == 11
                and values[3] == "CODES"
                and values[7] == "CELLS"
            ):
                direct = {
                    "certified": {
                        "Iminus": values[0] == "true",
                        "Iplus": values[1] == "true",
                        "combined": values[2] == "true",
                    },
                    "refusal_codes": {
                        "Iminus": int(values[4]),
                        "Iplus": int(values[5]),
                        "combined": int(values[6]),
                    },
                    "cells_checked": {
                        "Iminus": int(values[8]),
                        "Iplus": int(values[9]),
                        "combined": int(values[10]),
                    },
                }
        elif line.startswith("RANK_PROOF "):
            values = {
                key: value == "true"
                for key, value in (
                    field.split("=", 1) for field in line.split()[1:]
                )
            }
            proof = values
    if (
        minus is None or plus is None or minus_z is None or plus_z is None
        or charts is None or bounds is None or ranks is None
        or direct is None or proof is None
    ):
        raise TaylorTransportError("Taylor stage output is incomplete")
    return {
        "Iminus": minus, "Iplus": plus,
        "_chart_states": {
            "Iminus": {"chart": charts["Iminus"], "z": minus_z},
            "Iplus": {"chart": charts["Iplus"], "z": plus_z},
        },
        "_basis_change_majorants": bounds,
    }, ranks, {
        "direct": direct,
        "proof": proof,
        "logical_derivation": (
            "uniform rank 12 of [Iminus Iplus] implies uniform rank 6 "
            "of each six-column subfamily"
        ),
    }


def run_stage(
    *,
    child: int,
    stage: int,
    artifact_dir: Path,
    repo_root: Path,
    previous: dict[str, Any] | None,
    scratch: Path,
    output: Path,
    compile_timeout: float = 900,
    run_timeout: float = 900,
) -> dict[str, Any]:
    source_text, metadata = render_stage(
        child=child, stage=stage, artifact_dir=artifact_dir,
        repo_root=repo_root, previous=previous,
    )
    scratch.mkdir(parents=True, exist_ok=True)
    source = scratch / f"q{child:02d}-stage{stage}.forge"
    binary = scratch / f"q{child:02d}-stage{stage}"
    log = scratch / f"q{child:02d}-stage{stage}.log"
    source.write_text(source_text)
    compiled = subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        text=True, capture_output=True, timeout=compile_timeout, check=False,
    )
    if compiled.returncode:
        raise TaylorTransportError(
            f"Forge compile refused stage {stage}: {compiled.stderr[-4000:]}"
        )
    ran = subprocess.run(
        [str(binary)], text=True, capture_output=True,
        timeout=run_timeout, check=False,
    )
    log.write_text(ran.stdout + ran.stderr)
    if ran.returncode != 42:
        raise TaylorTransportError(
            f"Forge run refused stage {stage} with {ran.returncode}: "
            f"{ran.stdout[-4000:]}{ran.stderr[-4000:]}"
        )
    payload = stage_payload(
        metadata=metadata,
        stdout=ran.stdout,
        source=source,
        log=log,
        exit_code=ran.returncode,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def stage_payload(
    *,
    metadata: dict[str, Any],
    stdout: str,
    source: Path,
    log: Path,
    exit_code: int,
) -> dict[str, Any]:
    """Type a successful Forge trace without re-running the producer."""
    parsed, ranks, rank_evidence = parse_stage_output(stdout)
    chart_states = parsed.pop("_chart_states")
    basis_change_majorants = parsed.pop("_basis_change_majorants")
    planes = parsed
    _require(
        ranks == {"Iminus": 6, "Iplus": 6, "combined": 12},
        "Taylor stage: terminal rank gate failed",
    )
    payload = {
        "schema": SCHEMA,
        "status": "CERTIFIED_STAGE",
        **metadata,
        "planes": planes,
        "chart_states": chart_states,
        "basis_change_majorants": basis_change_majorants,
        "basis_change_proof": {
            "norm": "induced matrix infinity norm, binary-scaled",
            "construction": (
                "outward interval products of every normalized propagation "
                "and rechart basis map and its certified inverse"
            ),
            "establishes": (
                "uniform boundedness and invertibility of the endpoint-to-"
                "normalized graph basis change on this compact child"
            ),
            "does_not_establish": (
                "the original endpoint-coordinate scattering amplitudes"
            ),
        },
        "terminal_ranks": ranks,
        "rank_evidence": rank_evidence,
        "execution": {
            "backend": "c",
            "exit_code": exit_code,
            "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        },
        "does_not_establish": [
            "horizon-to-infinity matching",
            "endpoint current or flux conservation",
            "original infinity endpoint amplitude normalization",
            "a connection or scattering amplitude matrix",
            "a scattering channel",
            "stability, ghost, positivity, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload
