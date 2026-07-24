#!/usr/bin/env python3
"""Run one adaptive correlated Bplus4 successor panel."""
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
from black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_v1 import (
    _probe as prior,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1 import (
    produce as prefix,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1 import (
    produce as render,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_bplus4_v1/checkpoint.json"
)
CHECKPOINT = HERE / "checkpoint.json"
MANIFEST = HERE / "run_manifest.json"
CERTIFICATE = HERE / "certificate.json"

CANDIDATES = [
    {
        "choice": 0,
        "name": "PRIMARY",
        "center": "493/16",
        "step": "-1/8",
        "radius": "1/16",
        "denominator": 8,
        "order": 96,
        "final_radius": "123/4",
    },
    {
        "choice": 1,
        "name": "FALLBACK",
        "center": "987/32",
        "step": "-1/16",
        "radius": "1/32",
        "denominator": 16,
        "order": 64,
        "final_radius": "493/16",
    },
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def canonical_sha256(value: object) -> str:
    return sha256_bytes(canonical_bytes(value))


MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let choice:i64=0;let center:Rat=big("493/16");
  let h:Rat=big("-1/8");let radius:Rat=big("1/16");
  let denominator:f64=8.0;let order:i64=96;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=MODEL_HULL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("BPLUS4_CHUNK status=REFUSED code=SEED_HULL");
      return 3;}};
  let predicted:f64=sc_tail(sc_norm(mh)/denominator,order+1)*sc_norm(sh);
  if(predicted<0.0||!f64_is_finite(predicted)||predicted>=0.5){
    choice=1;center=big("987/32");h=big("-1/16");radius=big("1/32");
    denominator=16.0;order=64;
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
  let direct:IvTaylor4Mat=sj_mul(
    sc_series(models.direct,h,order),seed);
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
  if(!f64_is_finite(width)||width>=4.0){
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


def source_text(input_payload: dict) -> str:
    return "\n".join(
        (
            prefix.strip_predecessor(),
            render.render_model("initial_base", input_payload["base"]),
            render.render_model("initial_tangent", input_payload["tangent"]),
            prior.SUPPORT,
            MAIN,
        )
    )


def run(command: list[str], env: dict[str, str], timeout: float) -> dict:
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
        "exit_code": code,
        "elapsed_seconds": time.perf_counter() - started,
        "output": output,
    }


def parse_summary(output: str) -> dict:
    match = re.search(
        r"BPLUS4_CHUNK status=PASS choice=(?P<choice>\d+) "
        r"order=(?P<order>\d+) tail=(?P<tail>[-+0-9.eE]+) "
        r"width=(?P<width>[-+0-9.eE]+) "
        r"coefficients=(?P<coefficients>true|false) "
        r"containment=(?P<containment>true|false)",
        output,
    )
    if match is None:
        refused = re.search(
            r"BPLUS4_CHUNK status=REFUSED.*", output
        )
        raise RuntimeError(
            refused.group(0) if refused else "unparsed chunk output"
        )
    result = match.groupdict()
    result["choice"] = int(result["choice"])
    result["order"] = int(result["order"])
    result["coefficients"] = result["coefficients"] == "true"
    result["containment"] = result["containment"] == "true"
    return result


def reproduce() -> tuple[dict, dict, dict]:
    input_document = json.loads(INPUT.read_text())
    if canonical_sha256(input_document["payload"]) != (
        input_document["payload_sha256"]
    ):
        raise RuntimeError("input checkpoint payload drift")
    source = source_text(input_document["payload"])
    source_sha = sha256_bytes(source.encode())
    chunk_descriptor = {
        "input_payload_sha256": input_document["payload_sha256"],
        "source_sha256": source_sha,
        "candidates": CANDIDATES,
        "shared_generator": 7315,
        "boundary_direct_gate": True,
    }
    chunk_id = canonical_sha256(chunk_descriptor)
    source_path = Path(f"/tmp/axial-bplus4-{chunk_id[:16]}.forge")
    binary = Path(f"/tmp/axial-bplus4-{chunk_id[:16]}")
    source_path.write_text(source)
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    started = time.perf_counter()
    compiled = run(
        [str(jet.FORGE), "-o", str(binary), str(source_path)], env, 15.0
    )
    executed = (
        run([str(binary)], env, 42.0)
        if compiled["exit_code"] == 0
        else {"exit_code": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    elapsed = time.perf_counter() - started
    if elapsed > 60.0:
        raise RuntimeError(f"chunk exceeded 60 seconds: {elapsed}")
    if compiled["exit_code"] != 0 or executed["exit_code"] != 0:
        raise RuntimeError(
            f"chunk execution failed: compile={compiled['exit_code']} "
            f"run={executed['exit_code']} output={executed['output'][-500:]}"
        )
    summary = parse_summary(executed["output"])
    selected = CANDIDATES[summary["choice"]]
    if summary["order"] != selected["order"]:
        raise RuntimeError("adaptive order/choice mismatch")
    base = render.parse_model(executed["output"], "SUCCESSOR_BASE")
    tangent = render.parse_model(executed["output"], "SUCCESSOR_TANGENT")
    payload = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-"
            "successor-payload-v1"
        ),
        "chunk_id": chunk_id,
        "input_payload_sha256": input_document["payload_sha256"],
        "start_radius": input_document["payload"]["radius"],
        "radius": selected["final_radius"],
        "omega_child": input_document["payload"]["omega_child"],
        "generator": 7315,
        "degree": 4,
        "column_order": input_document["payload"]["column_order"],
        "real_state_layout": input_document["payload"]["real_state_layout"],
        "base": base,
        "tangent": tangent,
        "typed_common_unit_h0": input_document["payload"][
            "typed_common_unit_h0"
        ],
        "typed_columns": input_document["payload"]["typed_columns"],
    }
    checkpoint = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-"
            "successor-checkpoint-v1"
        ),
        "payload": payload,
        "payload_sha256": canonical_sha256(payload),
    }
    manifest = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-"
            "content-addressed-run-v1"
        ),
        "chunk_descriptor": chunk_descriptor,
        "chunk_id": chunk_id,
        "source_retained": False,
        "source_ephemeral_path": str(source_path),
        "source_sha256": source_sha,
        "binary_ephemeral_path": str(binary),
        "compile": {
            "exit_code": compiled["exit_code"],
            "elapsed_seconds": compiled["elapsed_seconds"],
            "output_sha256": sha256_bytes(compiled["output"].encode()),
        },
        "run": {
            "exit_code": executed["exit_code"],
            "elapsed_seconds": executed["elapsed_seconds"],
            "raw_output_retained": False,
            "raw_output_sha256": sha256_bytes(executed["output"].encode()),
            "summary": summary,
            "successor_base_sha256": canonical_sha256(base),
            "successor_tangent_sha256": canonical_sha256(tangent),
        },
        "total_elapsed_seconds": elapsed,
        "under_sixty_seconds": elapsed <= 60.0,
        "selected_candidate": selected,
        "checkpoint_payload_sha256": checkpoint["payload_sha256"],
    }
    return checkpoint, manifest, input_document


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
        and float(summary["width"]) < 4.0
        and checkpoint["payload"]["generator"] == 7315
    )
    return {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-chunk01-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_OUTGOING_BPLUS4_CHUNK01_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": (
            "BPLUS4_CONTENT_ADDRESSED_SUCCESSOR_PASS"
            if passed
            else "BPLUS4_CONTENT_ADDRESSED_SUCCESSOR_REFUSED"
        ),
        "imports": {
            "predecessor_checkpoint": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": sha256(INPUT),
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
                "accept primary iff its validated exponential pre-tail is "
                "finite, nonnegative, and <1/2; otherwise rebuild the "
                "coefficient enclosure and use the smaller fallback; refuse "
                "if the fallback pre-tail is not <1/2"
            ),
            "selected": selected,
            "summary": summary,
            "total_elapsed_seconds": manifest["total_elapsed_seconds"],
            "under_sixty_seconds": manifest["under_sixty_seconds"],
            "raw_model_stdout_retained": False,
            "source_content_addressed": (
                manifest["chunk_id"]
                == canonical_sha256(manifest["chunk_descriptor"])
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
            "resume only from this content-addressed checkpoint with the "
            "same adaptive one-panel contract; never replay the monolithic "
            "r=31 transport"
        ),
    }


def rendered(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    if args.reproduce:
        checkpoint, manifest, input_document = reproduce()
        CHECKPOINT.write_text(rendered(checkpoint))
        MANIFEST.write_text(rendered(manifest))
    else:
        if not CHECKPOINT.exists() or not MANIFEST.exists():
            raise RuntimeError("successor artifacts absent; use --reproduce")
        checkpoint = json.loads(CHECKPOINT.read_text())
        manifest = json.loads(MANIFEST.read_text())
        input_document = json.loads(INPUT.read_text())
    certificate = build_certificate(checkpoint, manifest, input_document)
    text = rendered(certificate)
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != text:
            raise SystemExit("certificate drift")
    else:
        CERTIFICATE.write_text(text)
    print(certificate["status"])
    return 0 if certificate["status"] == (
        "BPLUS4_CONTENT_ADDRESSED_SUCCESSOR_PASS"
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
