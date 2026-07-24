#!/usr/bin/env python3
"""Materialize the bounded chunk-03 runtime refusal without rerunning it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1 import (
    produce as engine,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_bplus4_chunk02_v1/checkpoint.json"
)
MANIFEST = HERE / "run_manifest.json"
CERTIFICATE = HERE / "certificate.json"

CANDIDATES = [
    {
        "choice": 0,
        "name": "LARGER_PRIMARY",
        "center": "1951/64",
        "step": "-7/32",
        "radius": "7/64",
        "denominator": "32/7",
        "order": 168,
        "final_radius": "243/8",
    },
    {
        "choice": 1,
        "name": "PROVEN_FALLBACK",
        "center": "1953/64",
        "step": "-5/32",
        "radius": "5/64",
        "denominator": "32/5",
        "order": 120,
        "final_radius": "487/16",
    },
]

MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let choice:i64=0;let center:Rat=big("1951/64");
  let h:Rat=big("-7/32");let radius:Rat=big("7/64");
  let denominator:f64=4.571428571428571;let order:i64=168;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=MODEL_HULL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=SEED_HULL");
      return 3;}};
  let predicted:f64=sc_tail(sc_norm(mh)/denominator,order+1)*sc_norm(sh);
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    choice=1;center=big("1953/64");h=big("-5/32");radius=big("5/64");
    denominator=6.4;order=120;
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
  if(!f64_is_finite(width)||width>=10.0){
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rendered(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def configure_engine() -> None:
    engine.INPUT = INPUT
    engine.CANDIDATES = CANDIDATES
    engine.MAIN = MAIN


def documents() -> tuple[dict, dict]:
    configure_engine()
    predecessor = json.loads(INPUT.read_text())
    source = engine.source_text(predecessor["payload"])
    source_sha256 = hashlib.sha256(source.encode()).hexdigest()
    descriptor = {
        "schema": "phase3-bplus4-content-addressed-chunk-v1",
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "source_sha256": source_sha256,
        "candidates": CANDIDATES,
        "compile_timeout_seconds": 15,
        "run_timeout_seconds": 42,
        "total_budget_seconds": 60,
        "direct_boundary_gate": (
            "partial jet Taylor coefficients must equal the independently "
            "expanded direct sixteen-state coefficients and their interval "
            "difference must contain zero"
        ),
    }
    chunk_id = engine.canonical_sha256(descriptor)
    manifest = {
        "schema": "phase3-axial-partial-jet-outgoing-bplus4-chunk03-run-v1",
        "chunk_descriptor": descriptor,
        "chunk_id": chunk_id,
        "source_sha256": source_sha256,
        "source_retained": False,
        "raw_output_retained": False,
        "predecessor_checkpoint": {
            "path": str(INPUT.relative_to(ROOT)),
            "sha256": sha256(INPUT),
            "payload_sha256": predecessor["payload_sha256"],
        },
        "attempt": {
            "status": "TIMEOUT",
            "compile_exit_code": 0,
            "run_exit_code": 124,
            "runtime_timeout_seconds": 42,
            "stdout_was_empty": True,
            "completed_boundary_diagnostic_available": False,
            "selected_candidate_not_inferred": True,
        },
        "successor_checkpoint_emitted": False,
    }
    certificate = {
        "schema": "phase3-axial-partial-jet-outgoing-bplus4-chunk03-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_BPLUS4_CHUNK03_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "BPLUS4_MAXIMAL_STEP_RUNTIME_REFUSED",
        "imports": {
            "predecessor_checkpoint": manifest["predecessor_checkpoint"]
        },
        "artifacts": {
            "run_manifest": {
                "path": str(MANIFEST.relative_to(ROOT)),
                "chunk_id": chunk_id,
                "source_sha256": source_sha256,
            }
        },
        "adaptive_chunk": {
            "candidates": CANDIDATES,
            "larger_step_probed_first": True,
            "selection_rule": (
                "try the 7/32 order-168 panel first; use the 5/32 "
                "order-120 fallback only when the primary pre-tail refuses"
            ),
            "terminal_gate": "RUNTIME_TIMEOUT",
            "runtime_timeout_seconds": 42,
            "compile_exit_code": 0,
            "run_exit_code": 124,
            "completed_boundary_diagnostic_available": False,
            "selected_candidate_not_inferred": True,
            "raw_model_stdout_retained": False,
            "source_content_addressed": (
                chunk_id == engine.canonical_sha256(descriptor)
            ),
        },
        "boundary_gate": {
            "direct_sixteen_state_expanded_once": False,
            "partial_jet_coefficients_equal_direct": False,
            "interval_difference_contains_zero": False,
            "shared_generator": 7315,
            "rank_three_preserved_by_common_invertible_flow": False,
        },
        "claim_flags": {
            "content_addressed_attempt_certified": True,
            "larger_step_probed_first": True,
            "runtime_refusal_certified": True,
            "under_sixty_second_chunk_certified": False,
            "boundary_direct_gate_certified": False,
            "successor_checkpoint_serialized": False,
            "shared_omega_generator_preserved_at_successor": False,
            "full_Bplus4_at_r4_certified": False,
            "T_plus_certified": False,
            "stokes_or_scattering_certified": False,
        },
        "does_not_establish": [
            "an admissible selected candidate or validated pre-tail",
            "a direct sixteen-state boundary comparison",
            "a successor checkpoint beyond r=979/32",
            "the complete outgoing Bplus4 frame at r=4",
            "the outgoing trace map T_plus",
            "a Stokes, scattering, reflection, or flux identity",
        ],
        "next_gate": (
            "resume from the unchanged chunk-02 checkpoint with a candidate "
            "whose compile and direct-boundary execution can finish inside "
            "the bounded runtime; do not infer a successor from this timeout"
        ),
    }
    return manifest, certificate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest, certificate = documents()
    if args.check:
        if (
            not MANIFEST.exists()
            or MANIFEST.read_text() != rendered(manifest)
            or not CERTIFICATE.exists()
            or CERTIFICATE.read_text() != rendered(certificate)
        ):
            raise SystemExit("materialized timeout artifact drift")
    else:
        MANIFEST.write_text(rendered(manifest))
        CERTIFICATE.write_text(rendered(certificate))
    print(certificate["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
