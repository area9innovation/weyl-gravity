#!/usr/bin/env python3
"""Run the second adaptive correlated Bplus4 successor panel."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1 import (
    produce as engine,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_bplus4_chunk01_v1/checkpoint.json"
)
CHECKPOINT = HERE / "checkpoint.json"
MANIFEST = HERE / "run_manifest.json"
CERTIFICATE = HERE / "certificate.json"

CANDIDATES = [
    {
        "choice": 0,
        "name": "LARGER_PRIMARY",
        "center": "1963/64",
        "step": "-5/32",
        "radius": "5/64",
        "denominator": "32/5",
        "order": 120,
        "final_radius": "979/32",
    },
    {
        "choice": 1,
        "name": "PROVEN_FALLBACK",
        "center": "491/16",
        "step": "-1/8",
        "radius": "1/16",
        "denominator": 8,
        "order": 96,
        "final_radius": "245/8",
    },
]

MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let choice:i64=0;let center:Rat=big("1963/64");
  let h:Rat=big("-5/32");let radius:Rat=big("5/64");
  let denominator:f64=6.4;let order:i64=120;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=MODEL_HULL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=SEED_HULL");
      return 3;}};
  let predicted:f64=sc_tail(sc_norm(mh)/denominator,order+1)*sc_norm(sh);
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    choice=1;center=big("491/16");h=big("-1/8");radius=big("1/16");
    denominator=8.0;order=96;
    models=sc_build_models(w,bc_radius(center,radius));
    mh=match(ivtm4_hull_checked(models.direct)){
      some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=FALLBACK_MODEL");
        return 3;}};
    predicted=sc_tail(sc_norm(mh)/denominator,order+1)*sc_norm(sh);
  }
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    println(strfmt(system_allocator(),
      "BPLUS4_CHUNK status=REFUSED choice={} order={} code=ADAPTIVE_TAIL tail={}",
      [choice,order,predicted]));return 3;
  }
  let dual:ScModels=sc_dual_series(models.base,models.tangent,h,order);
  let base_out:IvTaylor4Mat=sj_mul(dual.base,base);
  let tangent_out:IvTaylor4Mat=sc_add(
    sj_mul(dual.tangent,base),sj_mul(dual.base,tangent_n));
  let jet:IvTaylor4Mat=bc_stack(tangent_out,base_out);
  let direct:IvTaylor4Mat=sj_mul(sc_series(models.direct,h,order),seed);
  let jp:IvTaylor4Mat=sc_pad(jet,predicted);
  let dp:IvTaylor4Mat=sc_pad(direct,predicted);
  let coefficients:bool=sj_coefficients_equal(jp,dp);
  let containment:bool=sc_contains_zero(jp,dp);
  if(!coefficients||!containment){
    println(strfmt(system_allocator(),
      "BPLUS4_CHUNK status=REFUSED choice={} order={} code=DIRECT_GATE",
      [choice,order]));return 3;
  }
  let tangent_final:IvTaylor4Mat=sc_scale(bc_unstack_tangent(jp),big("512"));
  let base_final:IvTaylor4Mat=bc_unstack_base(jp);
  let width:f64=sj_width(match(ivtm4_hull_checked(jp)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=OUTPUT_HULL");
      return 3;}});
  if(!f64_is_finite(width)||width>=6.0){
    println(strfmt(system_allocator(),
      "BPLUS4_CHUNK status=REFUSED choice={} order={} code=WIDTH width={}",
      [choice,order,width]));return 3;
  }
  sr_emit("SUCCESSOR_BASE",base_final);
  sr_emit("SUCCESSOR_TANGENT",tangent_final);
  println(strfmt(system_allocator(),
    "BPLUS4_CHUNK status=PASS choice={} order={} tail={} width={} coefficients={} containment={}",
    [choice,order,predicted,width,coefficients,containment]));
  return 0;
}
'''


def configure_engine() -> None:
    engine.INPUT = INPUT
    engine.CHECKPOINT = CHECKPOINT
    engine.MANIFEST = MANIFEST
    engine.CERTIFICATE = CERTIFICATE
    engine.CANDIDATES = CANDIDATES
    engine.MAIN = MAIN


def build_certificate(
    checkpoint: dict, manifest: dict, input_document: dict
) -> dict:
    summary = manifest["run"]["summary"]
    selected = manifest["selected_candidate"]
    passed = (
        manifest["under_sixty_seconds"]
        and summary["coefficients"]
        and summary["containment"]
        and float(summary["tail"]) < 0.5
        and float(summary["width"]) < 6.0
        and checkpoint["payload"]["generator"] == 7315
    )
    return {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-chunk02-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_OUTGOING_BPLUS4_CHUNK02_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": (
            "BPLUS4_LARGER_STEP_SUCCESSOR_PASS"
            if passed
            else "BPLUS4_LARGER_STEP_SUCCESSOR_REFUSED"
        ),
        "imports": {
            "predecessor_checkpoint": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": engine.sha256(INPUT),
                "payload_sha256": input_document["payload_sha256"],
            }
        },
        "artifacts": {
            "checkpoint": {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "payload_sha256": checkpoint["payload_sha256"],
            },
            "run_manifest": {
                "path": str(MANIFEST.relative_to(ROOT)),
                "chunk_id": manifest["chunk_id"],
                "source_sha256": manifest["source_sha256"],
            },
        },
        "adaptive_chunk": {
            "candidates": CANDIDATES,
            "selection_rule": (
                "try the 5/32 order-120 panel first; fall back to the "
                "certified 1/8 order-96 panel unless the primary validated "
                "pre-tail is finite, nonnegative, and below 1/2"
            ),
            "selected": selected,
            "larger_primary_selected": selected["choice"] == 0,
            "summary": summary,
            "radial_progress": (
                "5/32" if selected["choice"] == 0 else "1/8"
            ),
            "total_elapsed_seconds": manifest["total_elapsed_seconds"],
            "under_sixty_seconds": manifest["under_sixty_seconds"],
            "raw_model_stdout_retained": False,
            "source_content_addressed": (
                manifest["chunk_id"]
                == engine.canonical_sha256(manifest["chunk_descriptor"])
            ),
        },
        "boundary_gate": {
            "direct_sixteen_state_expanded_once": True,
            "partial_jet_coefficients_equal_direct": summary["coefficients"],
            "interval_difference_contains_zero": summary["containment"],
            "shared_generator": 7315,
            "rank_three_preserved_by_common_invertible_flow": passed,
        },
        "claim_flags": {
            "content_addressed_chunk_certified": passed,
            "larger_step_probed_first": True,
            "adaptive_step_order_gate_certified": passed,
            "under_sixty_second_chunk_certified": passed,
            "boundary_direct_gate_certified": passed,
            "successor_checkpoint_serialized": passed,
            "shared_omega_generator_preserved": passed,
            "full_Bplus4_at_r4_certified": False,
            "T_plus_certified": False,
            "stokes_or_scattering_certified": False,
        },
        "does_not_establish": [
            "the complete outgoing Bplus4 frame at r=4",
            "the outgoing trace map T_plus",
            "a Stokes, scattering, reflection, or flux identity",
            "bounded continuation beyond the successor radius",
        ],
        "next_gate": (
            "resume only from this content-addressed checkpoint and probe "
            "the largest under-60-second candidate before the proven "
            "fallback; stop on the first tail, width, direct, or timeout gate"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    configure_engine()
    if args.reproduce:
        checkpoint, manifest, input_document = engine.reproduce()
        CHECKPOINT.write_text(engine.rendered(checkpoint))
        MANIFEST.write_text(engine.rendered(manifest))
    else:
        if not CHECKPOINT.exists() or not MANIFEST.exists():
            raise RuntimeError("successor artifacts absent; use --reproduce")
        checkpoint = json.loads(CHECKPOINT.read_text())
        manifest = json.loads(MANIFEST.read_text())
        input_document = json.loads(INPUT.read_text())
    certificate = build_certificate(checkpoint, manifest, input_document)
    text = engine.rendered(certificate)
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != text:
            raise SystemExit("certificate drift")
    else:
        CERTIFICATE.write_text(text)
    print(certificate["status"])
    return 0 if certificate["status"] == (
        "BPLUS4_LARGER_STEP_SUCCESSOR_PASS"
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
