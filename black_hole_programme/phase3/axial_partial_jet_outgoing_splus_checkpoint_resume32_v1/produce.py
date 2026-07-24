#!/usr/bin/env python3
"""Resume the normalized outgoing S checkpoint for up to 32 panels."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1 import (
    produce as prior,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "splus_checkpoint_resume32.forge"
OUTPUT = HERE / "certificate.json"
CHECKPOINT = HERE / "checkpoint.json"
RECEIPT = HERE / "receipt.json"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-outgoing-splus-checkpoint-resume32-v1")
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_checkpoint_resume_v1"
)
PREDECESSOR_SOURCE = PREDECESSOR / "splus_checkpoint_resume.forge"
PREDECESSOR_CERT = PREDECESSOR / "certificate.json"
PREDECESSOR_CHECKPOINT = PREDECESSOR / "checkpoint.json"


class Resume32Error(RuntimeError):
    """Fail-closed continuation error."""


canonical_sha256 = prior.canonical_sha256


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Resume32Error(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_predecessor() -> str:
    text = PREDECESSOR_SOURCE.read_text()
    marker = "pub fn main()->i64{"
    require(marker in text, "predecessor source has no terminal main")
    return text.split(marker, 1)[0].rstrip() + "\n"


MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=successor_base();
  let tangent_n:IvTaylor4Mat=sc_scale(successor_tangent(),big("1/512"));
  let center:Rat=big("16349/512");
  let h:Rat=big("-1/256");let order:i64=12;let panel:i64=0;
  let max_tail:f64=0.0;
  let max_base_width:f64=sj_width(match(ivtm4_hull_checked(base)){
    some(x)=>x,none=>{trap();}});
  let max_normalized_width:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
    some(x)=>x,none=>{trap();}});
  while(panel<32){
    let models:ScModels=sc_build_models(w,sr_radius(center));
    let dual:ScModels=sc_dual_series(models.base,models.tangent,h,order);
    let base_out:IvTaylor4Mat=sj_mul(dual.base,base);
    let tangent_out:IvTaylor4Mat=sc_add(
      sj_mul(dual.tangent,base),sj_mul(dual.base,tangent_n));
    let jet:IvTaylor4Mat=sc_stack(tangent_out,base_out);
    let direct:IvTaylor4Mat=sj_mul(
      sc_series(models.direct,h,order),sc_stack(tangent_n,base));
    let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "SPLUS_RESUME32 status=REFUSED panel={} code=MODEL_HULL",[panel]));
        return 3;}};
    let sh:IvMat=match(ivtm4_hull_checked(sc_stack(tangent_n,base))){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "SPLUS_RESUME32 status=REFUSED panel={} code=SEED_HULL",[panel]));
        return 3;}};
    let alpha:f64=sc_norm(mh);let scaled:f64=alpha/256.0;
    let tail:f64=sc_tail(scaled,13)*sc_norm(sh);
    if(tail<0.0||!f64_is_finite(tail)){
      println(strfmt(system_allocator(),
        "SPLUS_RESUME32 status=REFUSED panel={} code=TAIL",[panel]));
      return 3;
    }
    let jp:IvTaylor4Mat=sc_pad(jet,tail);
    let dp:IvTaylor4Mat=sc_pad(direct,tail);
    if(!sj_coefficients_equal(jp,dp)||!sc_contains_zero(jp,dp)){
      println(strfmt(system_allocator(),
        "SPLUS_RESUME32 status=REFUSED panel={} code=CORRELATION",[panel]));
      return 3;
    }
    tangent_n=sc_unstack_tangent(jp);base=sc_unstack_base(jp);
    let nw:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
      some(x)=>x,none=>{trap();}});
    let bw:f64=sj_width(match(ivtm4_hull_checked(base)){
      some(x)=>x,none=>{trap();}});
    if(!f64_is_finite(nw)||!f64_is_finite(bw)){
      println(strfmt(system_allocator(),
        "SPLUS_RESUME32 status=REFUSED panel={} code=WIDTH",[panel]));
      return 3;
    }
    if(nw>max_normalized_width){max_normalized_width=nw;}
    if(bw>max_base_width){max_base_width=bw;}
    if(tail>max_tail){max_tail=tail;}
    center=rat_clone(center)-big("1/256");panel=panel+1;
  }
  let tangent:IvTaylor4Mat=sc_scale(tangent_n,big("512"));
  let final_nw:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
    some(x)=>x,none=>{trap();}});
  let final_tw:f64=sj_width(match(ivtm4_hull_checked(tangent)){
    some(x)=>x,none=>{trap();}});
  let final_bw:f64=sj_width(match(ivtm4_hull_checked(base)){
    some(x)=>x,none=>{trap();}});
  sr_emit("CHECKPOINT_BASE",base);sr_emit("CHECKPOINT_TANGENT",tangent);
  println(strfmt(system_allocator(),
    "SPLUS_RESUME32 status=PASS generator=7315 panels={} final_r=31.80859375 max_tail={} max_base_width={} max_normalized_width={} final_base_width={} final_normalized_width={} final_tangent_width={}",
    [panel,max_tail,max_base_width,max_normalized_width,final_bw,final_nw,
     final_tw]));
  return 0;
}
'''


def source_text(payload: dict) -> str:
    return "\n".join(
        (
            strip_predecessor(),
            prior.render_model("successor_base", payload["base"]),
            prior.render_model("successor_tangent", payload["tangent"]),
            MAIN,
        )
    )


def run(command: list[str], env: dict[str, str], timeout: float = 90.0) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
        code, output = completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as exc:
        code, output = 124, exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
    return {
        "exit": code,
        "elapsed_seconds": time.perf_counter() - started,
        "output": output,
    }


def parse_summary(output: str) -> dict:
    match = re.search(
        r"SPLUS_RESUME32 status=(?P<status>\w+) "
        r"generator=(?P<generator>\d+) panels=(?P<panels>\d+) "
        r"final_r=(?P<final_r>[-+0-9.eE]+) "
        r"max_tail=(?P<max_tail>[-+0-9.eE]+) "
        r"max_base_width=(?P<max_base>[-+0-9.eE]+) "
        r"max_normalized_width=(?P<max_normalized>[-+0-9.eE]+) "
        r"final_base_width=(?P<final_base>[-+0-9.eE]+) "
        r"final_normalized_width=(?P<final_normalized>[-+0-9.eE]+) "
        r"final_tangent_width=(?P<final_tangent>[-+0-9.eE]+)",
        output,
    )
    if match:
        return match.groupdict()
    refused = re.search(
        r"SPLUS_RESUME32 status=REFUSED panel=(?P<panel>\d+) "
        r"code=(?P<code>\w+)",
        output,
    )
    return (
        {"status": "REFUSED", **refused.groupdict()}
        if refused
        else {"status": "UNPARSED"}
    )


def build() -> tuple[dict, float]:
    started = time.perf_counter()
    predecessor_cert = json.loads(PREDECESSOR_CERT.read_text())
    checkpoint = json.loads(PREDECESSOR_CHECKPOINT.read_text())
    require(
        predecessor_cert["claim_flags"]["S_16_panel_resume_certified"],
        "predecessor continuation is not certified",
    )
    require(
        prior.canonical_sha256(checkpoint["payload"])
        == checkpoint["payload_sha256"],
        "predecessor checkpoint payload drift",
    )
    payload = checkpoint["payload"]
    require(
        payload["generator"] == 7315 and payload["radius"] == "8175/256",
        "predecessor checkpoint type drift",
    )
    SOURCE.write_text(source_text(payload))
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    compile_result = run([str(jet.FORGE), "-o", str(BINARY), str(SOURCE)], env)
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = (
        run([str(BINARY)], env)
        if compile_result["exit"] == 0
        else {"exit": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    RUN_LOG.write_text(run_result["output"])
    summary = parse_summary(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and summary.get("status") == "PASS"
        and summary.get("generator") == "7315"
        and summary.get("panels") == "32"
    )
    checkpoint_written = False
    if passed:
        final_payload = {
            "generator": 7315,
            "radius": "8143/256",
            "omega_child": payload["omega_child"],
            "phase": payload["phase"],
            "base": prior.parse_model(run_result["output"], "CHECKPOINT_BASE"),
            "tangent": prior.parse_model(
                run_result["output"], "CHECKPOINT_TANGENT"
            ),
        }
        CHECKPOINT.write_text(
            json.dumps(
                {
                    "schema": "phase3-axial-outgoing-splus-checkpoint-v1",
                    "payload": final_payload,
                    "payload_sha256": prior.canonical_sha256(final_payload),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        checkpoint_written = True
    completed = (
        int(summary["panels"])
        if summary.get("status") == "PASS"
        else int(summary.get("panel", 0))
    )
    result = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-checkpoint-resume32-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_SPLUS_CHECKPOINT_RESUME32",
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": (
            "SPLUS_CORRELATED_32_PANEL_SUCCESSOR_PASS"
            if passed
            else "SPLUS_CORRELATED_32_PANEL_SUCCESSOR_REFUSED"
        ),
        "imports": {
            "predecessor_source": {
                "path": str(PREDECESSOR_SOURCE.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_SOURCE),
            },
            "predecessor_certificate": {
                "path": str(PREDECESSOR_CERT.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CERT),
            },
            "predecessor_checkpoint": {
                "path": str(PREDECESSOR_CHECKPOINT.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CHECKPOINT),
                "payload_sha256": checkpoint["payload_sha256"],
            },
        },
        "transport": {
            "arithmetic": "IvTaylor4_omega tensor partial dual_tau",
            "generator": 7315,
            "start_radius": "8175/256",
            "target_radius": "8143/256",
            "panel_width": "1/256",
            "planned_panels": 32,
            "completed_panels": completed,
            "internal_tangent_normalization": "tangent/512 throughout",
            "physical_tangent_restored_only_at_serialization": True,
            "summary": summary,
        },
        "checkpoint": {
            "written": checkpoint_written,
            "path": str(CHECKPOINT.relative_to(ROOT))
            if checkpoint_written
            else None,
            "sha256": sha256(CHECKPOINT) if checkpoint_written else None,
            "payload_sha256": (
                json.loads(CHECKPOINT.read_text())["payload_sha256"]
                if checkpoint_written
                else None
            ),
        },
        "artifacts": {
            "source": {
                "path": str(SOURCE.relative_to(ROOT)),
                "sha256": sha256(SOURCE),
            },
            "compile_log": {
                "path": str(COMPILE_LOG.relative_to(ROOT)),
                "sha256": sha256(COMPILE_LOG),
            },
            "run_log": {
                "path": str(RUN_LOG.relative_to(ROOT)),
                "sha256": sha256(RUN_LOG),
            },
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
        },
        "claim_flags": {
            "common_generator_preserved": passed,
            "dual_direct_gate_checked_each_completed_panel": True,
            "S_32_panel_successor_certified": passed,
            "S_checkpoint_serialized": checkpoint_written,
            "S_reaches_r31": False,
            "joint_E_R_S_frame_certified": False,
            "K_plus_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "does_not_establish": [
            "transport of S to r=31",
            "a joint E/R/S outgoing frame",
            "K_plus or T_plus",
            "Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "resume from the r=8143/256 checkpoint in another bounded "
            "successor, stopping on the first honest transport refusal"
            if passed
            else "inspect the first recorded refusal without promoting downstream claims"
        ),
    }
    return result, time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, elapsed = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS Splus resume32 producer check")
        return 0
    OUTPUT.write_text(encoded)
    receipt = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-resume32-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "command": (
            "python3 -m black_hole_programme.phase3."
            "axial_partial_jet_outgoing_splus_checkpoint_resume32_v1.produce"
        ),
        "elapsed_seconds": elapsed,
        "status": "PASS" if result["status"].endswith("_PASS") else "REFUSED",
        "tiers": {
            "tier0": "Python/Forge compile, deterministic producer, JSON schema",
            "tier1": "independent verifier and mutation tests",
            "tier2": "not run; no shared operator changed",
            "tier3": "not run; no Tplus or scattering theorem promoted",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    return 0 if result["status"].endswith("_PASS") else 3


if __name__ == "__main__":
    raise SystemExit(main())
