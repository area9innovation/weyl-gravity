#!/usr/bin/env python3
"""Render the frozen q0 horizon consumer over the pinned Taylor2 kernel."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4 import (
    produce as affine,
)

HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
FROZEN = HERE.parent / "axial_horizon_grassmann_mobius_to_r4" / "transport_c00.forge"
FROZEN_SHA256 = "6978e7532e7f30944b746db91fb58d2254bd3267607947b2c3e7ea5e9ed527c3"
FROZEN_COMMIT = "630880a6cb8d83efa286c585ffe68c52898e7f04"
TANGO_COMMIT = "972aa4337b73cc0f632d9599fb345098bc8ccce8"
IVTAYLOR_SHA256 = "fd51f0ab2a1ebce950660b58dcfc31728c032de872001f50f907f11cfa2be103"
OUTPUT = HERE / "transport_c00_taylor2.forge"
METADATA = HERE / "source_metadata.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_between(source: str, start: str, end: str, replacement: str) -> str:
    before, rest = source.split(start, 1)
    _, after = rest.split(end, 1)
    return before + replacement + end + after


def taylor_common() -> str:
    source = affine.COMMON.split("\nfn hr_restrict", 1)[0] + "\n"
    source = (
        source.replace("IvAffineMat", "IvTaylorMat")
        .replace("IvAffineResult", "IvTaylorResult")
        .replace("IvAffineRank", "IvTaylorRank")
        .replace("ivam_", "ivtm_")
        .replace(".center", ".c0")
        .replace(".linear", ".c1")
    )
    source = source.replace(
        "let c:QMat=qm_new(6,a.cols);let l:QMat=qm_new(6,a.cols);",
        "let c:QMat=qm_new(6,a.cols);let l:QMat=qm_new(6,a.cols);"
        "let q:QMat=qm_new(6,a.cols);",
    ).replace(
        "l=qm_set(l,i,j,qm_get(a.c1,si,j));",
        "l=qm_set(l,i,j,qm_get(a.c1,si,j));"
        "q=qm_set(q,i,j,qm_get(a.c2,si,j));",
        1,
    ).replace(
        "new IvTaylorMat(a.generator,6,a.cols,c,l,r)",
        "new IvTaylorMat(a.generator,6,a.cols,c,l,q,r)",
    )
    source = source.replace(
        "let c:QMat=qm_new(6,6);let l:QMat=qm_new(6,6);",
        "let c:QMat=qm_new(6,6);let l:QMat=qm_new(6,6);"
        "let q:QMat=qm_new(6,6);",
    ).replace(
        "l=qm_set(l,i,j,qm_get(a.c1,si,sj));",
        "l=qm_set(l,i,j,qm_get(a.c1,si,sj));"
        "q=qm_set(q,i,j,qm_get(a.c2,si,sj));",
    ).replace(
        "new IvTaylorMat(a.generator,6,6,c,l,r)",
        "new IvTaylorMat(a.generator,6,6,c,l,q,r)",
    )
    source = source.replace(
        "let c:QMat=qm_new(12,6);let l:QMat=qm_new(12,6);",
        "let c:QMat=qm_new(12,6);let l:QMat=qm_new(12,6);"
        "let q:QMat=qm_new(12,6);",
    ).replace(
        "l=qm_set(l,hr_j(chart,i),j,qm_get(z.c1,i,j));",
        "l=qm_set(l,hr_j(chart,i),j,qm_get(z.c1,i,j));"
        "q=qm_set(q,hr_j(chart,i),j,qm_get(z.c2,i,j));",
    ).replace(
        "new IvTaylorMat(7315,12,6,c,l,r)",
        "new IvTaylorMat(7315,12,6,c,l,q,r)",
    )
    right = """// Checked degree-two right solve X*A=B.
fn hr_right(b:borrow IvTaylorMat,a:borrow IvTaylorMat)->HrSolve{
  if(a.generator!=7315 || b.generator!=7315 ||
     a.rows!=6 || a.cols!=6 || b.rows!=6 || b.cols!=6){
    return new HrSolve(false,hr_zero());}
  let x:IvTaylorResult=ivtm_solve_right(b,a);
  if(!x.ok){return new HrSolve(false,hr_zero());}
  let rb:IvTaylorResult=ivtm_rebase_dyadic(x.value,128);
  if(!rb.ok){return new HrSolve(false,hr_zero());}
  let xa:IvTaylorResult=ivtm_mul_checked(rb.value,a);
  if(!xa.ok){return new HrSolve(false,hr_zero());}
  let defect:IvTaylorResult=ivtm_sub_checked(xa.value,b);
  if(!defect.ok || !hr_contains_zero(defect.value)){
    return new HrSolve(false,hr_zero());}
  return new HrSolve(true,ivtm_clone(rb.value));
}

"""
    source = replace_between(
        source, "// Checked right solve", "fn hr_contains_zero", right
    )
    width = """
fn hr_max_width(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=ivm_at(h,i,j);let w:f64=x.hi-x.lo;
    if(w>best){best=w;}j=j+1;}i=i+1;}return best;
}

fn hr_reorder_rows(a:borrow IvTaylorMat,to_block:bool)->IvTaylorMat{
  let c:QMat=qm_new(12,a.cols);let l:QMat=qm_new(12,a.cols);
  let q:QMat=qm_new(12,a.cols);let r:IvMat=ivm_zeros(12,a.cols);
  let i:i64=0;while(i<12){
    let si:i64=if(to_block){
      if(i<8){if(i<4){i}else{i+2}}else{if(i<10){i-4}else{i}}
    }else{
      if(i<4){i}else{if(i<6){8+i-4}else{if(i<10){4+i-6}else{i}}}
    };
    let j:i64=0;while(j<a.cols){
      c=qm_set(c,i,j,qm_get(a.c0,si,j));
      l=qm_set(l,i,j,qm_get(a.c1,si,j));
      q=qm_set(q,i,j,qm_get(a.c2,si,j));
      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(a.generator,12,a.cols,c,l,q,r);
}

fn hr_at_r4(a:borrow IvTaylorMat)->HrSolve{
  let s:QMat=qm_new(12,12);let i:i64=0;while(i<12){
    s=qm_set(s,i,i,if(i==5 || i==11){rat(1,2)}else{rat(1,1)});
    i=i+1;}
  let z:IvTaylorResult=ivtm_mul_checked(ivtm_constant(7315,s),a);
  if(!z.ok){return new HrSolve(false,hr_zero());}
  let rb:IvTaylorResult=ivtm_rebase_dyadic(z.value,128);
  if(!rb.ok){return new HrSolve(false,hr_zero());}
  return new HrSolve(true,ivtm_clone(rb.value));
}

fn hr_emit(a:borrow IvTaylorMat)->void{
  let h:IvMat=ivtm_hull(a);let i:i64=0;while(i<12){
    let j:i64=0;while(j<6){
      let c0:String=rat_str(qm_get(a.c0,i,j));
      let c1:String=rat_str(qm_get(a.c1,i,j));
      let c2:String=rat_str(qm_get(a.c2,i,j));
      let r:Iv=ivm_at(a.remainder,i,j);let q:Iv=ivm_at(h,i,j);
      println(strfmt(system_allocator(),
        "T2 {} {} {} {} {} {} {} {} {}",
        [i,j,str_view(c0),str_view(c1),str_view(c2),
         f64_bits(r.lo),f64_bits(r.hi),f64_bits(q.lo),f64_bits(q.hi)]));
      drop(c0);drop(c1);drop(c2);j=j+1;}i=i+1;}
}
"""
    return source + width


def taylor_run() -> str:
    source = (
        affine.RUN.replace("IvAffineMat", "IvTaylorMat")
        .replace("IvAffineResult", "IvTaylorResult")
        .replace("IvAffineRank", "IvTaylorRank")
        .replace("ivam_", "ivtm_")
    )
    source = source.replace(
        "let initial:IvTaylorMat=ht_standard_to_block_rows(hc_initial_model(cell));",
        "let initial:IvTaylorMat=hr_reorder_rows("
        "ivtm_from_affine(hc_initial_model(cell)),true);",
    )
    source = source.replace(
        "let a:IvTaylorMat=hc_runtime(", "let a:IvAffineMat=hc_runtime("
    )
    source = source.replace(
        "let phi:IvTaylorMat=match(sl_local_transition(a,wdt,12)){\n"
        "        some(z)=>z,none=>{println(strfmt(system_allocator(),\n"
        '          "REFUSE local q={} shell={} panel={}",[q,shell,panel]));return false;}};',
        "let phi0:IvAffineMat=match(sl_local_transition(a,wdt,12)){\n"
        "        some(z)=>z,none=>{println(strfmt(system_allocator(),\n"
        '          "REFUSE local q={} shell={} panel={}",[q,shell,panel]));return false;}};\n'
        "      let phi:IvTaylorMat=ivtm_from_affine(phi0);",
    )
    source = source.replace("ivtm_apply_rect(phi,direct)", "ivtm_mul_checked(phi,direct)")
    source = source.replace("ivtm_max_width(", "hr_max_width(")
    source = source.replace(
        "let final_standard:IvTaylorMat=ht_block_to_standard_rows(final_block.value);\n"
        "  let out:IvTaylorMat=match(ht_standard_at_r4(final_standard)){\n"
        '    some(z)=>z,none=>{println("REFUSE standard-r4");return false;}};',
        "let final_standard:IvTaylorMat=hr_reorder_rows(final_block.value,false);\n"
        "  let out0:HrSolve=hr_at_r4(final_standard);\n"
        '  if(!out0.ok){println("REFUSE standard-r4");return false;}\n'
        "  let out:IvTaylorMat=ivtm_clone(out0.value);",
    )
    return source.replace("ht_emit(out);", "hr_emit(out);")


def render() -> str:
    if digest(FROZEN) != FROZEN_SHA256:
        raise RuntimeError("frozen affine q0 source drift")
    frozen_source = FROZEN.read_text()
    marker = "pub type HrSolve"
    if marker not in frozen_source:
        raise RuntimeError("frozen affine Grassmann suffix missing")
    prefix = frozen_source.split(marker, 1)[0].replace(
        "import math/ivaffine;", "import math/ivaffine;\nimport math/ivtaylor;"
    )
    lo, hi = affine.CELLS[0]
    cell = f"""
fn hr_cell()->IvAffineCell{{
  return match(iva_cell(7315,{affine.rat((lo + hi) / 2)},
    {affine.rat((hi - lo) / 2)})){{
    some(z)=>z,none=>{{trap();}}}};
}}
"""
    return (
        prefix
        + taylor_common()
        + affine.dispatch()
        + cell
        + taylor_run().replace("HR_Q", "0")
    )


def produce() -> None:
    source = render()
    OUTPUT.write_text(source)
    metadata = {
        "schema": "phase3-axial-horizon-grassmann-mobius-r4-taylor2-source-v1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "frequency_child": 0,
        "frequency_bounds": ["1/2", "2049/4096"],
        "generator": 7315,
        "charts": 20,
        "shells": 23,
        "panels_per_shell": 256,
        "rank_cover_cells": 64,
        "frozen_affine_source": str(FROZEN.relative_to(PHYSICS)),
        "frozen_affine_source_sha256": FROZEN_SHA256,
        "frozen_affine_source_commit": FROZEN_COMMIT,
        "tango_commit": TANGO_COMMIT,
        "tango_ivtaylor_sha256": IVTAYLOR_SHA256,
        "taylor_degree": 2,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "does_not_establish": [
            "any frequency child other than q0",
            "horizon-to-infinity connection or scattering",
            "flux sign, stability, ghost, positivity, CPT or unitarity",
            "LORENTZIAN-CAUSAL quantum claims",
        ],
        "superseded_provenance": [
            "A corrective lifecycle checkpoint briefly named nonexistent commit "
            "630880a6cb7968b18d6d789438e658f2f6a34fe3; it is not an input."
        ],
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    produce()
