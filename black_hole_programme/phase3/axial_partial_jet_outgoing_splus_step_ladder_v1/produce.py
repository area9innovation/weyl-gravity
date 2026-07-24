#!/usr/bin/env python3
"""Test larger one-panel steps from the certified outgoing S+ checkpoint."""
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
SOURCE = HERE / "splus_step_ladder.forge"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-outgoing-splus-step-ladder-v1")
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_checkpoint_resume32_v1"
)
PREDECESSOR_CERT = PREDECESSOR / "certificate.json"
PREDECESSOR_CHECKPOINT = PREDECESSOR / "checkpoint.json"


class LadderError(RuntimeError):
    """Fail-closed ladder error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LadderError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


MAIN = r'''
fn ladder_case(
  w:borrow IvTaylor4Mat,
  base:borrow IvTaylor4Mat,
  tangent_n:borrow IvTaylor4Mat,
  center:borrow Rat,
  h:borrow Rat,
  denominator:f64,
  case_id:i64)->i64{
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
        "SPLUS_LADDER case={} status=REFUSED code=MODEL_HULL",[case_id]));
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(sc_stack(tangent_n,base))){
    some(x)=>x,none=>{
      println(strfmt(system_allocator(),
        "SPLUS_LADDER case={} status=REFUSED code=SEED_HULL",[case_id]));
      return 3;}};
  let alpha:f64=sc_norm(mh);let scaled:f64=alpha/denominator;
  let tail:f64=sc_tail(scaled,13)*sc_norm(sh);
  if(tail<0.0||!f64_is_finite(tail)){
    println(strfmt(system_allocator(),
      "SPLUS_LADDER case={} status=REFUSED code=TAIL",[case_id]));
    return 3;
  }
  let jp:IvTaylor4Mat=sc_pad(jet,tail);
  let dp:IvTaylor4Mat=sc_pad(direct,tail);
  if(!sj_coefficients_equal(jp,dp)||!sc_contains_zero(jp,dp)){
    println(strfmt(system_allocator(),
      "SPLUS_LADDER case={} status=REFUSED code=CORRELATION",[case_id]));
    return 3;
  }
  let tangent_next:IvTaylor4Mat=sc_unstack_tangent(jp);
  let base_next:IvTaylor4Mat=sc_unstack_base(jp);
  let nw:f64=sj_width(match(ivtm4_hull_checked(tangent_next)){
    some(x)=>x,none=>{trap();}});
  let bw:f64=sj_width(match(ivtm4_hull_checked(base_next)){
    some(x)=>x,none=>{trap();}});
  if(!f64_is_finite(nw)||!f64_is_finite(bw)){
    println(strfmt(system_allocator(),
      "SPLUS_LADDER case={} status=REFUSED code=WIDTH",[case_id]));
    return 3;
  }
  println(strfmt(system_allocator(),
    "SPLUS_LADDER case={} status=PASS tail={} base_width={} normalized_tangent_width={}",
    [case_id,tail,bw,nw]));
  return 0;
}

pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=successor_base();
  let tangent_n:IvTaylor4Mat=sc_scale(successor_tangent(),big("1/512"));
  let rc0:i64=ladder_case(w,base,tangent_n,big("4071/128"),big("-1/128"),128.0,128);
  let rc1:i64=ladder_case(w,base,tangent_n,big("8141/256"),big("-1/64"),64.0,64);
  let rc2:i64=ladder_case(w,base,tangent_n,big("8139/256"),big("-1/32"),32.0,32);
  if(rc0==0&&rc1==0&&rc2==0){return 0;}
  return 3;
}
'''


def source_text(payload: dict) -> str:
    return "\n".join(
        (
            predecessor.strip_predecessor(),
            render.render_model("successor_base", payload["base"]),
            render.render_model("successor_tangent", payload["tangent"]),
            MAIN,
        )
    )


def run(command: list[str], env: dict[str, str], timeout: float = 120.0) -> dict:
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


def parse(output: str) -> dict:
    results: dict[str, dict] = {}
    pattern = re.compile(
        r"SPLUS_LADDER case=(?P<case>\d+) status=(?P<status>PASS|REFUSED)"
        r"(?: tail=(?P<tail>[-+0-9.eE]+)"
        r" base_width=(?P<base>[-+0-9.eE]+)"
        r" normalized_tangent_width=(?P<tangent>[-+0-9.eE]+)"
        r"| code=(?P<code>\w+))"
    )
    for match in pattern.finditer(output):
        results[match.group("case")] = {
            key: value
            for key, value in match.groupdict().items()
            if key != "case" and value is not None
        }
    return results


def build() -> tuple[dict, float]:
    started = time.perf_counter()
    cert = json.loads(PREDECESSOR_CERT.read_text())
    checkpoint = json.loads(PREDECESSOR_CHECKPOINT.read_text())
    require(
        cert["claim_flags"]["S_32_panel_successor_certified"],
        "predecessor is not certified",
    )
    require(
        canonical_sha256(checkpoint["payload"])
        == checkpoint["payload_sha256"],
        "checkpoint payload drift",
    )
    payload = checkpoint["payload"]
    require(
        payload["generator"] == 7315 and payload["radius"] == "8143/256",
        "checkpoint type drift",
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
    cases = parse(run_result["output"])
    ran_all = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and set(cases) == {"128", "64", "32"}
        and all(case["status"] == "PASS" for case in cases.values())
    )
    admissibility_thresholds = {
        "tail_upper": 1.0e-3,
        "base_width_upper": 1.0e-2,
        "normalized_tangent_width_upper": 1.0,
    }
    for case in cases.values():
        case["operationally_admissible"] = (
            case.get("status") == "PASS"
            and float(case["tail"]) < admissibility_thresholds["tail_upper"]
            and float(case["base"]) < admissibility_thresholds["base_width_upper"]
            and float(case["tangent"])
            < admissibility_thresholds["normalized_tangent_width_upper"]
        )
    admissible = [
        denominator
        for denominator in (128, 64, 32)
        if cases.get(str(denominator), {}).get("operationally_admissible")
    ]
    passed = ran_all and admissible == [128]
    result = {
        "schema": "phase3-axial-outgoing-splus-step-ladder-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_SPLUS_STEP_LADDER_V1",
        "lifecycle": "NUMERIC-ENCLOSURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": (
            "FINITE_LADDER_1_OVER_128_ADMISSIBLE"
            if passed
            else "STEP_LADDER_REFUSED"
        ),
        "imports": {
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
            "generator": 7315,
            "start_radius": "8143/256",
            "internal_tangent_normalization": "tangent/512",
            "taylor_order": 12,
            "cases": cases,
            "admissibility_thresholds": admissibility_thresholds,
            "largest_finite_step": "1/32" if ran_all else None,
            "largest_operationally_admissible_step": "1/128" if passed else None,
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
            "step_1_over_128_certified": cases.get("128", {}).get("status") == "PASS",
            "step_1_over_64_certified": cases.get("64", {}).get("status") == "PASS",
            "step_1_over_32_certified": cases.get("32", {}).get("status") == "PASS",
            "step_1_over_128_operationally_admissible": cases.get("128", {}).get(
                "operationally_admissible", False
            ),
            "step_1_over_64_operationally_admissible": cases.get("64", {}).get(
                "operationally_admissible", False
            ),
            "step_1_over_32_operationally_admissible": cases.get("32", {}).get(
                "operationally_admissible", False
            ),
            "transport_to_r31_certified": False,
            "joint_E_R_S_frame_certified": False,
            "K_plus_certified": False,
            "T_plus_certified": False,
        },
        "does_not_establish": [
            "multipanel transport to r=31",
            "a joint outgoing E/R/S frame",
            "K_plus, T_plus, Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "resume the correlated checkpoint with 1/128 panels and an exact final fractional step to r=31"
            if passed
            else "use the largest individually passing step without downstream promotion"
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
        print("PASS outgoing S+ step-ladder producer check")
        return 0
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "phase3-axial-outgoing-splus-step-ladder-receipt-v1",
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "certificate_sha256": sha256(OUTPUT),
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_outgoing_splus_step_ladder_v1.produce"
                ),
                "elapsed_seconds": elapsed,
                "status": (
                    "PASS"
                    if result["status"] == "FINITE_LADDER_1_OVER_128_ADMISSIBLE"
                    else "REFUSED"
                ),
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
    return (
        0
        if result["status"] == "FINITE_LADDER_1_OVER_128_ADMISSIBLE"
        else 3
    )


if __name__ == "__main__":
    raise SystemExit(main())
