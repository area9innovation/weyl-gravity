#!/usr/bin/env python3
"""Produce the exact interaction-picture and micro-successor certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1 import (
    produce as engine,
)
from black_hole_programme.phase4.axial_explicit_tplus_band_v1 import (
    produce as predecessor,
)
from black_hole_programme.phase4.axial_explicit_tplus_band_v1.interaction_picture import (
    PREDECESSOR,
    exact_fixture,
    physical_point_fixture,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUCCESSOR = HERE / "interaction_successor_checkpoint.json"
MANIFEST = HERE / "interaction_run_manifest.json"
CERTIFICATE = HERE / "interaction_certificate.json"
RECEIPT = HERE / "interaction_receipt.json"

CANDIDATE = {
    "choice": 0,
    "name": "INTERACTION_COARSE_AUDIT_MICRO",
    "center": "7791/256",
    "step": "-1/128",
    "radius": "1/256",
    "denominator": 128,
    "order": 32,
    "final_radius": "3895/128",
}

MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let center:Rat=big("7791/256");let h:Rat=big("-1/128");
  let radius:Rat=big("1/256");let order:i64=32;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("INTERACTION_MICRO status=REFUSED code=MODEL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("INTERACTION_MICRO status=REFUSED code=SEED");
      return 3;}};
  let predicted:f64=sc_tail(sc_norm(mh)/128.0,order+1)*sc_norm(sh);
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    println(strfmt(system_allocator(),
      "INTERACTION_MICRO status=REFUSED code=TAIL tail={}",[predicted]));
    return 3;
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
    println("INTERACTION_MICRO status=REFUSED code=DIRECT");return 3;
  }
  let tangent_final:IvTaylor4Mat=sc_scale(
    bc_unstack_tangent(jp),big("512"));
  let base_final:IvTaylor4Mat=bc_unstack_base(jp);
  let width:f64=sj_width(match(ivtm4_hull_checked(jp)){
    some(x)=>x,none=>{println("INTERACTION_MICRO status=REFUSED code=OUTPUT");
      return 3;}});
  if(!f64_is_finite(width)||width>=10.0){
    println(strfmt(system_allocator(),
      "INTERACTION_MICRO status=REFUSED code=WIDTH width={}",[width]));
    return 3;
  }
  sr_emit("SUCCESSOR_BASE",base_final);
  sr_emit("SUCCESSOR_TANGENT",tangent_final);
  println(strfmt(system_allocator(),
    "BPLUS4_CHUNK status=PASS choice=0 order=32 tail={} width={} coefficients={} containment={}",
    [predicted,width,coefficients,containment]));
  return 0;
}
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rendered(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def reproduce_interval() -> tuple[dict, dict]:
    predecessor.configure()
    engine.INPUT = PREDECESSOR
    engine.CHECKPOINT = SUCCESSOR
    engine.MANIFEST = MANIFEST
    engine.CERTIFICATE = CERTIFICATE
    engine.CANDIDATES = [CANDIDATE]
    engine.MAIN = MAIN
    checkpoint, manifest, _ = engine.reproduce()
    SUCCESSOR.write_text(rendered(checkpoint))
    MANIFEST.write_text(rendered(manifest))
    return checkpoint, manifest


def build_certificate(checkpoint: dict, manifest: dict) -> dict:
    exact = exact_fixture()
    point = physical_point_fixture()
    summary = manifest["run"]["summary"]
    interval_pass = (
        manifest["under_sixty_seconds"]
        and manifest["selected_candidate"]["final_radius"] == "3895/128"
        and summary["coefficients"]
        and summary["containment"]
        and float(summary["tail"]) < 0.5
        and float(summary["width"]) < 10.0
        and checkpoint["payload"]["generator"] == 7315
    )
    passed = exact["all_zero"] and point["status"] == "POINT_FIXTURE_PASS" and interval_pass
    return {
        "schema": "phase4-axial-explicit-tplus-interaction-picture-v1",
        "result_id": "PURE_WEYL_PHASE4_AXIAL_TPLUS_INTERACTION_PICTURE_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "lifecycle": {
            "exact": "EXACT-ALGEBRAIC",
            "point_fixture": "NUMERIC-CONSISTENCY",
            "micro_successor": "NUMERIC-ENCLOSURE",
        },
        "status": (
            "INTERACTION_PICTURE_EXACT_AND_MICRO_SUCCESSOR_PASS_R4_OPEN"
            if passed
            else "INTERACTION_PICTURE_OR_MICRO_SUCCESSOR_REFUSED"
        ),
        "assumptions": [
            "the partial jet differentiates only the spin-two row",
            "the spin-one transport R is tau-independent",
            "projective charts are changed only when the reciprocal denominator excludes zero",
            "logarithmic amplitudes are compared after exponentiation, so branch shifts are harmless",
        ],
        "imports": {
            "predecessor": {
                "path": str(PREDECESSOR.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR),
                "payload_sha256": json.loads(PREDECESSOR.read_text())["payload_sha256"],
            },
            "forge_model_source": {
                "path": (
                    "black_hole_programme/phase3/"
                    "axial_partial_jet_outgoing_splus_checkpoint_resume_v1/"
                    "splus_checkpoint_resume.forge"
                ),
                "sha256": sha256(
                    ROOT
                    / "black_hole_programme/phase3/"
                    "axial_partial_jet_outgoing_splus_checkpoint_resume_v1/"
                    "splus_checkpoint_resume.forge"
                ),
            },
        },
        "exact_interaction_picture": exact,
        "physical_center_fixture": point,
        "validated_micro_successor": {
            "radial_start": "487/16",
            "radial_end": "3895/128",
            "checkpoint": str(SUCCESSOR.relative_to(ROOT)),
            "checkpoint_sha256": sha256(SUCCESSOR),
            "payload_sha256": checkpoint["payload_sha256"],
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_sha256": sha256(MANIFEST),
            "frequency_cell": checkpoint["payload"]["omega_child"],
            "frequency_generator": checkpoint["payload"]["generator"],
            "summary": summary,
        },
        "equations": {
            "projective_q": "q'=c+(d-a)q-bq^2",
            "log_amplitude_q": "lambda'=a+bq",
            "projective_q_tau": (
                "q_tau'=c_tau+(d_tau-a_tau)q-b_tau q^2"
                "+((d-a)-2bq)q_tau"
            ),
            "log_amplitude_q_tau": (
                "lambda_tau'=a_tau+b_tau q+b q_tau"
            ),
            "reciprocal_transition": (
                "p=1/q; mu=lambda+log(q); "
                "p_tau=-q_tau/q^2; mu_tau=lambda_tau+q_tau/q"
            ),
            "interaction_J": "J'=P^{-1}EP",
            "interaction_K": "K'=P^{-1}DR",
            "interaction_dotK": (
                "dotK'=P^{-1}CR-J P^{-1}DR"
            ),
            "wronskian": "W'=(tr A)W",
            "six_state": (
                "diag(P,P,R)[[I,J,JK+dotK],[0,I,K],[0,0,I]]"
                "=[[P,dotP,dotQ],[0,P,Q],[0,0,R]]"
            ),
        },
        "claim_flags": {
            "interaction_picture_identity_exact": exact["all_zero"],
            "reciprocal_chart_transition_exact": exact["all_zero"],
            "wronskian_fixture_pass": (
                point["residuals"]["wronskian_spin2"] < point["threshold"]
                and point["residuals"]["wronskian_spin1"] < point["threshold"]
            ),
            "physical_point_interaction_direct_agreement": point["status"] == "POINT_FIXTURE_PASS",
            "validated_correlated_successor_beyond_487_over_16": interval_pass,
            "validated_projective_interval_transport_to_r4": False,
            "complete_outgoing_frame_at_r4": False,
            "explicit_Tplus_certified": False,
            "reflection_or_stokes_certified": False,
        },
        "does_not_establish": [
            "a validated projective/log-amplitude enclosure on the full radial interval",
            "the complete outgoing frame at r=4",
            "the outgoing trace map T_plus or reflection matrix",
            "a Stokes identity or channel-factorized C test",
            "a positive-real frequency-band theorem beyond the inherited narrow cell",
        ],
        "next_gate": (
            "replace the coarse direct audit after r=3895/128 by correlated "
            "interval enclosures for projective/log lines and J,K,dotK; "
            "retain reciprocal-chart and Wronskian gates"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.reproduce:
        checkpoint, manifest = reproduce_interval()
    else:
        if not SUCCESSOR.exists() or not MANIFEST.exists():
            raise SystemExit("missing successor artifacts; run --reproduce")
        checkpoint = json.loads(SUCCESSOR.read_text())
        manifest = json.loads(MANIFEST.read_text())

    result = build_certificate(checkpoint, manifest)
    wanted = rendered(result)
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != wanted:
            raise SystemExit("interaction certificate drift")
    else:
        CERTIFICATE.write_text(wanted)
        verifier = HERE / "verify_interaction.py"
        receipt = {
            "schema": "phase4-axial-explicit-tplus-interaction-receipt-v1",
            "status": result["status"],
            "certificate_sha256": sha256(CERTIFICATE),
            "successor_payload_sha256": checkpoint["payload_sha256"],
            "producer_sha256": sha256(Path(__file__)),
            "verifier_sha256": sha256(verifier) if verifier.exists() else None,
        }
        RECEIPT.write_text(rendered(receipt))
    print(result["status"])
    return 0 if "PASS" in result["status"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
