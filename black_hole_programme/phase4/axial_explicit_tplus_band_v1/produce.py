#!/usr/bin/env python3
"""Resume the correlated outgoing partial jet after the Phase-3 timeout."""

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
CHECKPOINT = HERE / "checkpoint.json"
MANIFEST = HERE / "run_manifest.json"
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

CANDIDATES = [
    {
        "choice": 0,
        "name": "BOUNDED_REPAIR",
        "center": "1953/64",
        "step": "-5/32",
        "radius": "5/64",
        "denominator": "32/5",
        "order": 120,
        "final_radius": "487/16",
    }
]

MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let center:Rat=big("1953/64");let h:Rat=big("-5/32");
  let radius:Rat=big("5/64");let denominator:f64=6.4;
  let order:i64=120;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=MODEL_HULL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=SEED_HULL");
      return 3;}};
  let predicted:f64=sc_tail(sc_norm(mh)/denominator,order+1)*sc_norm(sh);
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    println(strfmt(system_allocator(),
      "BPLUS4_CHUNK status=REFUSED choice=0 order={} code=TAIL tail={}",
      [order,predicted]));return 3;
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
    println("BPLUS4_CHUNK status=REFUSED choice=0 order=120 code=DIRECT_GATE");
    return 3;
  }
  let tangent_final:IvTaylor4Mat=sc_scale(bc_unstack_tangent(jp),big("512"));
  let base_final:IvTaylor4Mat=bc_unstack_base(jp);
  let width:f64=sj_width(match(ivtm4_hull_checked(jp)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=OUTPUT_HULL");
      return 3;}});
  if(!f64_is_finite(width)||width>=10.0){
    println(strfmt(system_allocator(),
      "BPLUS4_CHUNK status=REFUSED choice=0 order=120 code=WIDTH width={}",
      [width]));return 3;
  }
  sr_emit("SUCCESSOR_BASE",base_final);
  sr_emit("SUCCESSOR_TANGENT",tangent_final);
  println(strfmt(system_allocator(),
    "BPLUS4_CHUNK status=PASS choice=0 order=120 tail={} width={} coefficients={} containment={}",
    [predicted,width,coefficients,containment]));
  return 0;
}
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rendered(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def configure() -> None:
    engine.INPUT = INPUT
    engine.CHECKPOINT = CHECKPOINT
    engine.MANIFEST = MANIFEST
    engine.CERTIFICATE = CERTIFICATE
    engine.CANDIDATES = CANDIDATES
    engine.MAIN = MAIN


def certificate(checkpoint: dict, manifest: dict) -> dict:
    summary = manifest["run"]["summary"]
    passed = (
        manifest["under_sixty_seconds"]
        and summary["coefficients"]
        and summary["containment"]
        and float(summary["tail"]) < 0.5
        and float(summary["width"]) < 10.0
        and checkpoint["payload"]["generator"] == 7315
        and manifest["selected_candidate"]["final_radius"] == "487/16"
    )
    return {
        "schema": "phase4-axial-explicit-tplus-band-v1",
        "result_id": "PURE_WEYL_PHASE4_AXIAL_EXPLICIT_TPLUS_BAND_V1_CHECKPOINT",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": (
            "CORRELATED_OUTGOING_SUCCESSOR_PASS_R4_OPEN"
            if passed
            else "CORRELATED_OUTGOING_SUCCESSOR_REFUSED"
        ),
        "imports": {
            "checkpoint": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": sha256(INPUT),
            }
        },
        "successor": {
            "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
            "checkpoint_sha256": sha256(CHECKPOINT),
            "payload_sha256": checkpoint["payload_sha256"],
            "run_manifest": str(MANIFEST.relative_to(ROOT)),
            "run_manifest_sha256": sha256(MANIFEST),
            "radial_start": "979/32",
            "radial_end": "487/16",
            "frequency_generator": checkpoint["payload"]["generator"],
            "summary": summary,
        },
        "claim_flags": {
            "correlated_base_tangent_transport_certified": passed,
            "direct_sixteen_state_boundary_gate_certified": passed,
            "common_frequency_generator_preserved": passed,
            "complete_outgoing_frame_at_r4": False,
            "explicit_Tplus_certified": False,
            "reflection_or_stokes_certified": False,
        },
        "does_not_establish": [
            "the complete outgoing frame at r=4",
            "the outgoing trace map T_plus",
            "reflection amplitudes or a Stokes identity",
            "a full radial continuation or a positive-real frequency band theorem",
        ],
        "next_gate": (
            "resume only from the content-addressed r=487/16 checkpoint; "
            "retain the correlated partial-jet and direct boundary gates"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    configure()
    if args.reproduce:
        checkpoint, manifest, _ = engine.reproduce()
        CHECKPOINT.write_text(rendered(checkpoint))
        MANIFEST.write_text(rendered(manifest))
    else:
        if not CHECKPOINT.exists() or not MANIFEST.exists():
            raise SystemExit("missing successor artifacts; use --reproduce")
        checkpoint = json.loads(CHECKPOINT.read_text())
        manifest = json.loads(MANIFEST.read_text())
    result = certificate(checkpoint, manifest)
    wanted = rendered(result)
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != wanted:
            raise SystemExit("certificate drift")
    else:
        CERTIFICATE.write_text(wanted)
        receipt = {
            "schema": "phase4-axial-explicit-tplus-band-receipt-v1",
            "status": result["status"],
            "certificate_sha256": sha256(CERTIFICATE),
            "checkpoint_payload_sha256": checkpoint["payload_sha256"],
            "producer_sha256": sha256(Path(__file__)),
        }
        RECEIPT.write_text(rendered(receipt))
    print(result["status"])
    return 0 if "PASS" in result["status"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
