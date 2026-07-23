#!/usr/bin/env python3
"""Render one-boundary correlated projective replays for both q00 children."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_h4_plucker_q00_split_v1 import (
    produce as split,
)

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
CHILDREN_DIR = HERE / "children"
MANIFEST = HERE / "correlated_manifest.json"
SPLIT_CERTIFICATE = split.HERE / "certificate.json"
SPLIT_MANIFEST = split.MANIFEST
EXPECTED_SPLIT_CERTIFICATE_SHA256 = (
    "af08dcca5bd805a2fbcbd1817bf8342c685c9c2c82103609c782a8e4c4cf988a"
)
EXPECTED_SPLIT_MANIFEST_SHA256 = (
    "e8a253ad95687bbb5ed18701969a50bebe6a018ab154389a9d02182016ddc5f3"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def checked_split() -> dict:
    if sha256(SPLIT_CERTIFICATE) != EXPECTED_SPLIT_CERTIFICATE_SHA256:
        raise RuntimeError("split certificate hash drift")
    if sha256(SPLIT_MANIFEST) != EXPECTED_SPLIT_MANIFEST_SHA256:
        raise RuntimeError("split manifest hash drift")
    certificate = json.loads(SPLIT_CERTIFICATE.read_text())
    manifest = json.loads(SPLIT_MANIFEST.read_text())
    if certificate.get("status") != "CERTIFIED_SPLIT_COVER_NEGATIVE":
        raise RuntimeError("split negative result is not certified")
    if manifest.get("status") != "COVER_REFUSED":
        raise RuntimeError("split refusal manifest drift")
    return manifest


def paths(index: int) -> dict[str, Path]:
    stem = f"q00_child_{index}_correlated"
    return {
        "source": CHILDREN_DIR / f"{stem}.forge",
        "metadata": CHILDREN_DIR / f"{stem}_metadata.json",
        "compile_log": CHILDREN_DIR / f"{stem}_compile.txt",
        "run_log": CHILDREN_DIR / f"{stem}_run.txt",
    }


CORRELATED_SUPPORT = r'''
fn pl_correlated_pivot(a:borrow IvTaylor4Mat)->PlPivot{
  if(a.rows!=40 || a.cols!=1){
    return PlPivot(false,-1,0.0,0.0,34);}
  let witness:IvTaylor4Mat=pl_zero(1,1);
  let i:i64=0;while(i<20){
    let xr:IvTaylor4Mat=pl_scalar(a,i,0);
    let xi:IvTaylor4Mat=pl_scalar(a,i+20,0);
    let ar:Rat=rat_clone(qm_get(a.c0,i,0));
    let ai:Rat=rat_clone(qm_get(a.c0,i+20,0));
    let tx:IvTaylor4Result=ivtm4_scale_rat_checked(xr,ar);
    if(!tx.ok){return PlPivot(false,-1,0.0,0.0,tx.refusal_code);}
    let ty:IvTaylor4Result=ivtm4_scale_rat_checked(xi,ai);
    if(!ty.ok){return PlPivot(false,-1,0.0,0.0,ty.refusal_code);}
    let addx:IvTaylor4Result=ivtm4_add_checked(witness,tx.value);
    if(!addx.ok){
      return PlPivot(false,-1,0.0,0.0,addx.refusal_code);}
    witness=ivtm4_clone(addx.value);
    let addy:IvTaylor4Result=ivtm4_add_checked(witness,ty.value);
    if(!addy.ok){
      return PlPivot(false,-1,0.0,0.0,addy.refusal_code);}
    witness=ivtm4_clone(addy.value);
    i=i+1;
  }
  let wh:IvMat=match(ivtm4_hull_checked(witness)){
    some(z)=>z,none=>{
      return PlPivot(false,-1,0.0,0.0,IVTAY_INTERVAL_OVERFLOW);}};
  let value:Iv=ivm_at(wh,0,0);
  let margin:f64=if(value.lo>0.0){value.lo}else{
    if(value.hi<0.0){0.0-value.hi}else{0.0}};
  let ah:IvMat=match(ivtm4_hull_checked(a)){
    some(z)=>z,none=>{
      return PlPivot(false,-1,0.0,0.0,IVTAY_INTERVAL_OVERFLOW);}};
  let norm:f64=0.0;let row:i64=0;while(row<40){
    let av:Iv=iv_abs(ivm_at(ah,row,0));
    if(av.hi>norm){norm=av.hi;}row=row+1;
  }
  if(margin<=0.0){
    println(strfmt(system_allocator(),
      "CORRELATED_FUNCTIONAL_DEFECT lo={} hi={} norm={}",
      [value.lo,value.hi,norm]));
    return PlPivot(false,-1,0.0,norm,35);
  }
  return PlPivot(true,20,margin,norm,IVTAY_OK);
}

fn pl_correlated_projective_normalize(
a:borrow IvTaylor4Mat)->PlState{
  let before:PlPivot=pl_correlated_pivot(a);
  if(!before.ok){return pl_fail(before.refusal_code);}
  if(before.norm<=0.0 || !f64_is_finite(before.norm)){
    return pl_fail(IVTAY_INTERVAL_OVERFLOW);}
  let scale:Rat=rat(1,1);let exponent:i64=0;let n:f64=before.norm;
  while(n>1.0 && exponent<1024){
    scale=rat_clone(scale)/rat(2,1);n=n/2.0;exponent=exponent+1;}
  while(n<0.5 && exponent>-1024){
    scale=rat_clone(scale)*rat(2,1);n=n*2.0;exponent=exponent-1;}
  if(exponent==1024 || exponent==-1024){return pl_fail(32);}
  let scaled:IvTaylor4Result=ivtm4_scale_rat_checked(a,scale);
  if(!scaled.ok){return pl_fail(scaled.refusal_code);}
  let rebased:IvTaylor4Result=ivtm4_rebase_dyadic(scaled.value,160);
  if(!rebased.ok){return pl_fail(IVTAY_INTERVAL_OVERFLOW);}
  let after:PlPivot=pl_correlated_pivot(rebased.value);
  if(!after.ok){return pl_fail(after.refusal_code);}
  return new PlState(true,ivtm4_clone(rebased.value),20,
    after.margin,after.norm,exponent,IVTAY_OK);
}

fn pl_correlated_attempt(shell:i64,segment:i64,
cell:borrow IvAffineCell,start:borrow PlState)->PlState{
  if(!start.ok){return pl_fail(start.refusal_code);}
  let state:PlState=new PlState(true,ivtm4_clone(start.value),
    start.pivot,start.margin,start.norm,start.scale_exponent,IVTAY_OK);
  let count:i64=32;let panel:i64=segment*count;
  while(panel<(segment+1)*count){
    let lo:Rat=hr_shell_lo(shell);
    let width:Rat=hr_panel_width(shell);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(width));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(width));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(width));
    let coeff:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(width)/rat(2,1),cell);
    let stepped:H4Result=pl_step(coeff,width,state.value,12);
    if(!stepped.ok){return pl_fail(stepped.refusal_code);}
    let normalized:PlState=
      pl_correlated_projective_normalize(stepped.value);
    if(!normalized.ok){return normalized;}
    state=new PlState(true,ivtm4_clone(normalized.value),
      normalized.pivot,normalized.margin,normalized.norm,
      normalized.scale_exponent,IVTAY_OK);
    panel=panel+1;
  }
  return state;
}
'''


def render_child(index: int) -> str:
    manifest = checked_split()
    if not 0 <= index < 2:
        raise ValueError("child index out of range")
    entry = manifest["children"][index]
    source_path = split.HERE / entry["source_path"]
    source = source_path.read_text()
    if sha256(source_path) != entry["source_sha256"]:
        raise RuntimeError("split child source hash drift")
    marker = "pub fn main()->i64{"
    if source.count(marker) != 1:
        raise RuntimeError("split child main marker drift")
    source = source.replace(
        marker, CORRELATED_SUPPORT + "\n" + marker, 1
    )
    raw = "pl_attempt(4,3,cell,state)"
    correlated = "pl_correlated_attempt(4,3,cell,state)"
    if source.count(raw) != 1:
        raise RuntimeError("refused-boundary call marker drift")
    source = source.replace(raw, correlated, 1)
    source = source.replace(
        "PLUCKER_PASS reached_shell=4 reached_segment=3 "
        "rank_witness=true parameter_correlation=true",
        "PLUCKER_PASS reached_shell=4 reached_segment=3 "
        "rank_witness=midpoint-hermitian "
        "parameter_correlation=true",
        1,
    )
    return source


def write_child(index: int) -> dict:
    CHILDREN_DIR.mkdir(parents=True, exist_ok=True)
    child_paths = paths(index)
    source = render_child(index)
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    split_manifest = checked_split()
    split_entry = split_manifest["children"][index]
    metadata = {
        "schema": (
            "phase3-axial-h4-plucker-correlated-child-source-v1"
        ),
        "status": "RENDERED_NOT_YET_VERIFIED",
        "child_index": index,
        "frequency_cell": split_entry["frequency_cell"],
        "target": {"shell": 4, "segment": 3},
        "replay_only": {"shell": 4, "segment": 3},
        "witness": {
            "kind": "midpoint-Hermitian real functional",
            "formula": "Re sum_j conjugate(p_j(0)) q_j",
            "runtime_coefficients": "exact Taylor c0 rationals",
            "success_condition": "interval real part excludes zero",
            "refusal_code": 35,
        },
        "split_source_sha256": split_entry["source_sha256"],
        "split_run_log_sha256": split_entry["run_log_sha256"],
        "split_certificate_sha256": (
            EXPECTED_SPLIT_CERTIFICATE_SHA256
        ),
        "split_manifest_sha256": EXPECTED_SPLIT_MANIFEST_SHA256,
        "source_sha256": source_sha,
        "does_not_establish": [
            "transport beyond shell 4 segment 3",
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity scattering theorem",
        ],
    }
    child_paths["source"].write_text(source)
    child_paths["metadata"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    return metadata


def write_sources() -> list[dict]:
    return [write_child(index) for index in range(2)]


def main() -> int:
    metadata = write_sources()
    print("\n".join(value["source_sha256"] for value in metadata))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
