#!/usr/bin/env python3
"""Checkpointed continuation of the normalized outgoing S+ state to r=31."""
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
    produce as render,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1 import (
    produce as predecessor,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
CHECKPOINT = HERE / "checkpoint.json"
RECEIPT = HERE / "receipt.json"
PROGRESS = HERE / "progress.json"
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_checkpoint_resume32_v1"
)
PREDECESSOR_CERT = PREDECESSOR / "certificate.json"
PREDECESSOR_CHECKPOINT = PREDECESSOR / "checkpoint.json"

CHUNKS = (
    {
        "id": 0,
        "start": "8143/256",
        "center": "4071/128",
        "regular_panels": 32,
        "total_panels": 32,
        "final": "8079/256",
    },
    {
        "id": 1,
        "start": "8079/256",
        "center": "4039/128",
        "regular_panels": 16,
        "total_panels": 16,
        "final": "8047/256",
    },
    {
        "id": 2,
        "start": "8047/256",
        "center": "4023/128",
        "regular_panels": 16,
        "total_panels": 16,
        "final": "8015/256",
    },
    {
        "id": 3,
        "start": "8015/256",
        "center": "4007/128",
        "regular_panels": 16,
        "total_panels": 16,
        "final": "7983/256",
    },
    {
        "id": 4,
        "start": "7983/256",
        "center": "3991/128",
        "regular_panels": 16,
        "total_panels": 16,
        "final": "7951/256",
    },
    {
        "id": 5,
        "start": "7951/256",
        "center": "3975/128",
        "regular_panels": 7,
        "total_panels": 8,
        "final_step_center": "15873/512",
        "final": "31",
    },
)


class R31Error(RuntimeError):
    """Fail-closed r=31 continuation error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise R31Error(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


MAIN_TEMPLATE = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=successor_base();
  let tangent_n:IvTaylor4Mat=sc_scale(successor_tangent(),big("1/512"));
  let center:Rat=big("@@CENTER@@");
  let h:Rat=big("-1/128");
  let denominator:f64=128.0;
  let panel:i64=0;
  let max_tail:f64=0.0;
  let max_base_width:f64=sj_width(match(ivtm4_hull_checked(base)){
    some(x)=>x,none=>{trap();}});
  let max_normalized_width:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
    some(x)=>x,none=>{trap();}});
  while(panel<@@TOTAL@@){
    if(panel==@@REGULAR@@){
      center=big("@@FINAL_CENTER@@");
      h=big("-1/256");
      denominator=256.0;
    }
    let models:ScModels=sc_build_models(w,sr_radius(center));
    let dual:ScModels=sc_dual_series(models.base,models.tangent,h,12);
    let base_out:IvTaylor4Mat=sj_mul(dual.base,base);
    let tangent_out:IvTaylor4Mat=sc_add(
      sj_mul(dual.tangent,base),sj_mul(dual.base,tangent_n));
    let jet:IvTaylor4Mat=sc_stack(tangent_out,base_out);
    let direct:IvTaylor4Mat=sj_mul(
      sc_series(models.direct,h,12),sc_stack(tangent_n,base));
    let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "SPLUS_R31 chunk=@@ID@@ status=REFUSED panel={} code=MODEL_HULL",[panel]));
        return 3;}};
    let sh:IvMat=match(ivtm4_hull_checked(sc_stack(tangent_n,base))){
      some(x)=>x,none=>{
        println(strfmt(system_allocator(),
          "SPLUS_R31 chunk=@@ID@@ status=REFUSED panel={} code=SEED_HULL",[panel]));
        return 3;}};
    let alpha:f64=sc_norm(mh);let scaled:f64=alpha/denominator;
    let tail:f64=sc_tail(scaled,13)*sc_norm(sh);
    if(tail<0.0||!f64_is_finite(tail)){
      println(strfmt(system_allocator(),
        "SPLUS_R31 chunk=@@ID@@ status=REFUSED panel={} code=TAIL",[panel]));
      return 3;
    }
    let jp:IvTaylor4Mat=sc_pad(jet,tail);
    let dp:IvTaylor4Mat=sc_pad(direct,tail);
    if(!sj_coefficients_equal(jp,dp)||!sc_contains_zero(jp,dp)){
      println(strfmt(system_allocator(),
        "SPLUS_R31 chunk=@@ID@@ status=REFUSED panel={} code=CORRELATION",[panel]));
      return 3;
    }
    tangent_n=sc_unstack_tangent(jp);base=sc_unstack_base(jp);
    let nw:f64=sj_width(match(ivtm4_hull_checked(tangent_n)){
      some(x)=>x,none=>{trap();}});
    let bw:f64=sj_width(match(ivtm4_hull_checked(base)){
      some(x)=>x,none=>{trap();}});
    if(!f64_is_finite(nw)||!f64_is_finite(bw)){
      println(strfmt(system_allocator(),
        "SPLUS_R31 chunk=@@ID@@ status=REFUSED panel={} code=WIDTH",[panel]));
      return 3;
    }
    if(nw>max_normalized_width){max_normalized_width=nw;}
    if(bw>max_base_width){max_base_width=bw;}
    if(tail>max_tail){max_tail=tail;}
    if(panel<@@REGULAR@@){center=rat_clone(center)-big("1/128");}
    panel=panel+1;
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
    "SPLUS_R31 chunk=@@ID@@ status=PASS generator=7315 panels={} final_r=@@FINAL@@ max_tail={} max_base_width={} max_normalized_width={} final_base_width={} final_normalized_width={} final_tangent_width={}",
    [panel,max_tail,max_base_width,max_normalized_width,final_bw,final_nw,
     final_tw]));
  return 0;
}
'''


def main_text(spec: dict) -> str:
    final_center = spec.get("final_step_center", spec["center"])
    replacements = {
        "@@ID@@": str(spec["id"]),
        "@@CENTER@@": spec["center"],
        "@@REGULAR@@": str(spec["regular_panels"]),
        "@@TOTAL@@": str(spec["total_panels"]),
        "@@FINAL_CENTER@@": final_center,
        "@@FINAL@@": spec["final"],
    }
    text = MAIN_TEMPLATE
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def source_text(payload: dict, spec: dict) -> str:
    return "\n".join(
        (
            predecessor.strip_predecessor(),
            render.render_model("successor_base", payload["base"]),
            render.render_model("successor_tangent", payload["tangent"]),
            main_text(spec),
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


def parse_summary(output: str, chunk_id: int) -> dict:
    match = re.search(
        rf"SPLUS_R31 chunk={chunk_id} status=(?P<status>PASS) "
        r"generator=(?P<generator>\d+) panels=(?P<panels>\d+) "
        r"final_r=(?P<final_r>[-+/0-9.eE]+) "
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
        rf"SPLUS_R31 chunk={chunk_id} status=REFUSED "
        r"panel=(?P<panel>\d+) code=(?P<code>\w+)",
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
    predecessor_checkpoint = json.loads(PREDECESSOR_CHECKPOINT.read_text())
    require(
        predecessor_cert["claim_flags"]["S_32_panel_successor_certified"],
        "predecessor continuation is not certified",
    )
    require(
        canonical_sha256(predecessor_checkpoint["payload"])
        == predecessor_checkpoint["payload_sha256"],
        "predecessor checkpoint payload drift",
    )
    payload = predecessor_checkpoint["payload"]
    require(
        payload["generator"] == 7315 and payload["radius"] == "8143/256",
        "predecessor checkpoint type drift",
    )
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    previous = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    previous_chunks = {
        item["specification"]["id"]: item
        for item in previous.get("transport", {}).get("chunks", [])
        if item.get("passed")
    }
    progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    if (
        progress.get("predecessor_payload_sha256")
        == predecessor_checkpoint["payload_sha256"]
    ):
        chunk_results = progress.get("chunks", [])
        if chunk_results:
            payload = progress["payload"]
            require(
                canonical_sha256(payload) == progress["payload_sha256"],
                "progress payload drift",
            )
    else:
        chunk_results = []
    all_passed = True
    total_completed = sum(item["completed_panels"] for item in chunk_results)
    for spec in CHUNKS[len(chunk_results) :]:
        require(payload["radius"] == spec["start"], "chunk radius discontinuity")
        source = HERE / f"chunk_{spec['id']:02d}.forge"
        compile_log = HERE / f"chunk_{spec['id']:02d}_compile.txt"
        run_log = HERE / f"chunk_{spec['id']:02d}_run.txt"
        binary = Path(f"/tmp/axial-splus-r31-v1-chunk-{spec['id']:02d}")
        expected_source = source_text(payload, spec)
        source.write_text(expected_source)
        cached = previous_chunks.get(spec["id"])
        cached_valid = (
            cached is not None
            and cached["specification"] == spec
            and cached["source"]["sha256"] == sha256(source)
            and (ROOT / cached["run_log"]["path"]).exists()
            and sha256(ROOT / cached["run_log"]["path"])
            == cached["run_log"]["sha256"]
        )
        if cached_valid:
            compile_result = {
                "exit": cached["compile_exit"],
                "elapsed_seconds": cached["compile_seconds"],
                "output": compile_log.read_text() if compile_log.exists() else "",
            }
            run_result = {
                "exit": cached["run_exit"],
                "elapsed_seconds": cached["run_seconds"],
                "output": run_log.read_text(),
            }
        else:
            compile_result = run(
                [str(jet.FORGE), "-o", str(binary), str(source)], env
            )
            compile_log.write_text(compile_result["output"])
            run_result = (
                run([str(binary)], env)
                if compile_result["exit"] == 0
                else {"exit": 127, "elapsed_seconds": 0.0, "output": ""}
            )
            run_log.write_text(run_result["output"])
        summary = parse_summary(run_result["output"], spec["id"])
        passed = (
            compile_result["exit"] == 0
            and run_result["exit"] == 0
            and summary.get("status") == "PASS"
            and summary.get("generator") == "7315"
            and summary.get("panels") == str(spec["total_panels"])
            and summary.get("final_r") == spec["final"]
        )
        completed = (
            int(summary["panels"])
            if summary.get("status") == "PASS"
            else int(summary.get("panel", 0))
        )
        total_completed += completed
        chunk_results.append(
            {
                "specification": spec,
                "passed": passed,
                "completed_panels": completed,
                "summary": summary,
                "source": {
                    "path": str(source.relative_to(ROOT)),
                    "sha256": sha256(source),
                },
                "compile_log": {
                    "path": str(compile_log.relative_to(ROOT)),
                    "sha256": sha256(compile_log),
                },
                "run_log": {
                    "path": str(run_log.relative_to(ROOT)),
                    "sha256": sha256(run_log),
                },
                "compile_exit": compile_result["exit"],
                "run_exit": run_result["exit"],
                "compile_seconds": compile_result["elapsed_seconds"],
                "run_seconds": run_result["elapsed_seconds"],
            }
        )
        if not passed:
            all_passed = False
            break
        payload = {
            "generator": 7315,
            "radius": spec["final"],
            "omega_child": payload["omega_child"],
            "phase": payload["phase"],
            "base": render.parse_model(run_result["output"], "CHECKPOINT_BASE"),
            "tangent": render.parse_model(
                run_result["output"], "CHECKPOINT_TANGENT"
            ),
        }
        PROGRESS.write_text(
            json.dumps(
                {
                    "schema": "phase3-axial-outgoing-splus-r31-progress-v1",
                    "predecessor_payload_sha256": predecessor_checkpoint[
                        "payload_sha256"
                    ],
                    "chunks": chunk_results,
                    "payload": payload,
                    "payload_sha256": canonical_sha256(payload),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    checkpoint_written = all_passed and len(chunk_results) == len(CHUNKS)
    if checkpoint_written:
        CHECKPOINT.write_text(
            json.dumps(
                {
                    "schema": "phase3-axial-outgoing-splus-checkpoint-v1",
                    "payload": payload,
                    "payload_sha256": canonical_sha256(payload),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    result = {
        "schema": "phase3-axial-partial-jet-outgoing-splus-r31-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_SPLUS_R31_V1",
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": "SPLUS_REACHES_R31" if checkpoint_written else "SPLUS_R31_REFUSED",
        "imports": {
            "predecessor_certificate": {
                "path": str(PREDECESSOR_CERT.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CERT),
            },
            "predecessor_checkpoint": {
                "path": str(PREDECESSOR_CHECKPOINT.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CHECKPOINT),
                "payload_sha256": predecessor_checkpoint["payload_sha256"],
            },
        },
        "transport": {
            "arithmetic": "IvTaylor4_omega tensor partial dual_tau",
            "generator": 7315,
            "start_radius": "8143/256",
            "target_radius": "31",
            "planned_panels": 104,
            "completed_panels": total_completed,
            "chunk_count": 6,
            "chunks": chunk_results,
            "internal_tangent_normalization": "tangent/512 throughout",
            "supersedes_monolithic_timeout": {
                "elapsed_seconds": 183.72787416400388,
                "run_exit": 124,
                "scientific_disposition": "throughput failure; no transport refusal",
            },
        },
        "progress": {
            "path": str(PROGRESS.relative_to(ROOT)) if PROGRESS.exists() else None,
            "sha256": sha256(PROGRESS) if PROGRESS.exists() else None,
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
        "claim_flags": {
            "common_generator_preserved": checkpoint_written,
            "dual_direct_gate_checked_each_completed_panel": True,
            "S_reaches_r31": checkpoint_written,
            "S_checkpoint_serialized": checkpoint_written,
            "joint_E_R_S_frame_certified": False,
            "K_plus_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "does_not_establish": [
            "a joint E/R/S outgoing frame at r=31",
            "K_plus or T_plus",
            "Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "assemble the co-located E/R/S frame at r=31 and certify its determinant"
            if checkpoint_written
            else "resume from the last completed content-addressed chunk"
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
        print("PASS outgoing S+ r31 producer check")
        return 0
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "phase3-axial-outgoing-splus-r31-receipt-v1",
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "certificate_sha256": sha256(OUTPUT),
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_outgoing_splus_r31_v1.produce"
                ),
                "elapsed_seconds": elapsed,
                "status": "PASS" if result["status"] == "SPLUS_REACHES_R31" else "REFUSED",
                "tiers": {
                    "tier0": "Python/Forge compile, deterministic producer, JSON schema",
                    "tier1": "independent verifier and mutation tests",
                    "tier2": "not run; no shared operator changed",
                    "tier3": "not run; no Tplus or scattering theorem promoted",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(result["status"])
    return 0 if result["status"] == "SPLUS_REACHES_R31" else 3


if __name__ == "__main__":
    raise SystemExit(main())
