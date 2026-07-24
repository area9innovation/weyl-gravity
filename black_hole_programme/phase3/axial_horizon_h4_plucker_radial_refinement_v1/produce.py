#!/usr/bin/env python3
"""Render exact 2x/4x radial refinements of shell 4, segment 3 only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_h4_plucker_correlated_functional_v1 import (
    produce as correlated,
)

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
ATTEMPTS = HERE / "attempts"
MANIFEST = HERE / "refinement_manifest.json"
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"

UPSTREAM_CERTIFICATE = correlated.HERE / "certificate.json"
UPSTREAM_MANIFEST = correlated.MANIFEST
EXPECTED_UPSTREAM_CERTIFICATE_SHA256 = (
    "14fb85004516b03e6ecfffa566ac2a2ee8080168ddd125b3754cedb6391f4003"
)
EXPECTED_UPSTREAM_MANIFEST_SHA256 = (
    "7fbd0ef15ea0d1442ff03b93b06b24c05f2ac5c60e3dfb1784b0c6a28b7881e3"
)
FACTORS = (2, 4)
RADIAL_WIDTHS = {2: "1/134217728", 4: "1/268435456"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def checked_upstream() -> dict:
    if sha256(UPSTREAM_CERTIFICATE) != EXPECTED_UPSTREAM_CERTIFICATE_SHA256:
        raise RuntimeError("correlated certificate hash drift")
    if sha256(UPSTREAM_MANIFEST) != EXPECTED_UPSTREAM_MANIFEST_SHA256:
        raise RuntimeError("correlated manifest hash drift")
    certificate = json.loads(UPSTREAM_CERTIFICATE.read_text())
    manifest = json.loads(UPSTREAM_MANIFEST.read_text())
    if certificate.get("status") != "CERTIFIED_CORRELATED_FUNCTIONAL_OBSTRUCTION":
        raise RuntimeError("correlated obstruction is not certified")
    if manifest.get("status") != "CORRELATED_REFUSED":
        raise RuntimeError("correlated refusal manifest drift")
    return manifest


def paths(factor: int, child: int) -> dict[str, Path]:
    stem = f"q00_child_{child}_radial_{factor}x"
    return {
        "source": ATTEMPTS / f"{stem}.forge",
        "metadata": ATTEMPTS / f"{stem}_metadata.json",
        "compile_log": ATTEMPTS / f"{stem}_compile.txt",
        "run_log": ATTEMPTS / f"{stem}_run.txt",
    }


REFINEMENT_SUPPORT = r'''
fn pl_hybrid_refined_attempt(shell:i64,segment:i64,
cell:borrow IvAffineCell,start:borrow PlState,factor:i64)->PlState{
  if(!start.ok){return pl_fail(start.refusal_code);}
  if(factor!=2 && factor!=4){return pl_fail(37);}
  let state:PlState=new PlState(true,ivtm4_clone(start.value),
    start.pivot,start.margin,start.norm,start.scale_exponent,IVTAY_OK);
  let count:i64=32*factor;let panel:i64=segment*count;
  let width:Rat=rat_clone(hr_panel_width(shell))/rat(factor,1);
  while(panel<(segment+1)*count){
    let lo:Rat=hr_shell_lo(shell);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(width));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(width));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(width));
    let coeff:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(width)/rat(2,1),cell);
    let stepped:H4Result=pl_step(coeff,width,state.value,12);
    if(!stepped.ok){return pl_fail(stepped.refusal_code);}
    let raw:PlState=pl_projective_normalize(stepped.value);
    if(raw.ok){
      state=new PlState(true,ivtm4_clone(raw.value),raw.pivot,
        raw.margin,raw.norm,raw.scale_exponent,IVTAY_OK);
    }else{
      if(raw.refusal_code!=32){return raw;}
      let correlated:PlState=
        pl_correlated_projective_normalize(stepped.value);
      if(!correlated.ok){
        println(strfmt(system_allocator(),
          "RADIAL_REFINEMENT_REFUSE factor={} panel={} raw_code={} correlated_code={}",
          [factor,panel,raw.refusal_code,correlated.refusal_code]));
        return correlated;
      }
      state=new PlState(true,ivtm4_clone(correlated.value),
        correlated.pivot,correlated.margin,correlated.norm,
        correlated.scale_exponent,IVTAY_OK);
    }
    panel=panel+1;
  }
  println(strfmt(system_allocator(),
    "RADIAL_REFINEMENT_PASS factor={} panels={} final_pivot={} margin={} norm={}",
    [factor,count,state.pivot,state.margin,state.norm]));
  return state;
}
'''


def render_attempt(factor: int, child: int) -> str:
    checked_upstream()
    if factor not in FACTORS or child not in (0, 1):
        raise ValueError("attempt coordinate out of range")
    source = correlated.render_child(child)
    marker = "pub fn main()->i64{"
    if source.count(marker) != 1:
        raise RuntimeError("main marker drift")
    source = source.replace(marker, REFINEMENT_SUPPORT + "\n" + marker, 1)
    old = "pl_correlated_attempt(4,3,cell,state)"
    new = f"pl_hybrid_refined_attempt(4,3,cell,state,{factor})"
    if source.count(old) != 1:
        raise RuntimeError("target replay marker drift")
    source = source.replace(old, new, 1)
    source = source.replace(
        "rank_witness=midpoint-hermitian parameter_correlation=true",
        f"rank_witness=raw-or-midpoint-hermitian radial_refinement={factor}x "
        "parameter_correlation=true",
        1,
    )
    return source


def write_attempt(factor: int, child: int) -> dict:
    ATTEMPTS.mkdir(parents=True, exist_ok=True)
    upstream = checked_upstream()
    entry = upstream["children"][child]
    attempt_paths = paths(factor, child)
    source = render_attempt(factor, child)
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    metadata = {
        "schema": "phase3-axial-h4-plucker-radial-refinement-source-v1",
        "status": "RENDERED_NOT_YET_VERIFIED",
        "factor": factor,
        "child_index": child,
        "frequency_cell": entry["frequency_cell"],
        "scope": {
            "shell": 4,
            "segment": 3,
            "base_panels": 32,
            "refined_panels": 32 * factor,
            "radial_panel_width": RADIAL_WIDTHS[factor],
            "prior_segments_unchanged": 19,
        },
        "normalization": (
            "raw Pluecker coordinate first; existing midpoint-Hermitian "
            "functional only when raw code 32"
        ),
        "upstream_source_sha256": entry["source_sha256"],
        "upstream_run_log_sha256": entry["run_log_sha256"],
        "upstream_certificate_sha256": EXPECTED_UPSTREAM_CERTIFICATE_SHA256,
        "upstream_manifest_sha256": EXPECTED_UPSTREAM_MANIFEST_SHA256,
        "source_sha256": source_sha,
        "does_not_establish": [
            "rank loss when a refined interval still contains zero",
            "transport beyond shell 4 segment 3",
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity scattering theorem",
        ],
    }
    attempt_paths["source"].write_text(source)
    attempt_paths["metadata"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    return metadata


def write_factor(factor: int) -> list[dict]:
    return [write_attempt(factor, child) for child in (0, 1)]


def main() -> int:
    for factor in FACTORS:
        write_factor(factor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
