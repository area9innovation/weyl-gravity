#!/usr/bin/env python3
"""Serialize the r=63/2 mixed R+ state and resume to r=31."""
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
    produce as seed_producer,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_rplus_multipanel_v1 import (
    produce as panel_producer,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKPOINT = HERE / "checkpoint.json"
CHECKPOINT_SCHEMA = HERE / "checkpoint.schema.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
EXPORT_SOURCE = HERE / "export_reference.forge"
RESTART_SOURCE = HERE / "restart_chunk.forge"
ROUNDTRIP_SOURCE = HERE / "roundtrip_checkpoint.forge"
EXPORT_COMPILE_LOG = HERE / "export_compile.txt"
EXPORT_RUN_LOG = HERE / "export_run.txt"
ROUNDTRIP_COMPILE_LOG = HERE / "roundtrip_compile.txt"
ROUNDTRIP_RUN_LOG = HERE / "roundtrip_run.txt"
RESTART_COMPILE_LOG = HERE / "restart_compile.txt"
RESTART_RUN_LOG = HERE / "restart_run.txt"
EXPORT_BINARY = Path("/tmp/axial-rplus-checkpoint-export-v1")
ROUNDTRIP_BINARY = Path("/tmp/axial-rplus-checkpoint-roundtrip-v1")
RESTART_BINARY = Path("/tmp/axial-rplus-checkpoint-restart-v1")
PREDECESSOR_CERTIFICATE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_rplus_multipanel_v1/certificate.json"
)
CROSSWALK = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_transport_crosswalk_v1/certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def run(
    command: list[str], env: dict[str, str], timeout_seconds: float = 90.0
) -> dict:
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
            timeout=timeout_seconds,
        )
        exit_code = completed.returncode
        output = completed.stdout
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
    return {
        "command": " ".join(command),
        "exit": exit_code,
        "elapsed_seconds": time.perf_counter() - started,
        "output": output,
    }


SERIALIZE_SUPPORT = r'''
fn emit_mixed(tag:string,seed:borrow DualT4)->void{
  let b:String=ivtm4_serialize_json(seed.base,0);
  println(strfmt(system_allocator(),"{}_BASE {}",tag,str_view(b)));
  drop(b);
  let t:String=ivtm4_serialize_json(seed.tangent,0);
  println(strfmt(system_allocator(),"{}_TANGENT {}",tag,str_view(t)));
  drop(t);
}
'''


def loop_body(limit: int, checkpoint_at: int | None, final_tag: str) -> str:
    checkpoint = ""
    if checkpoint_at is not None:
        checkpoint = (
            f'    if(panel=={checkpoint_at}){{emit_mixed("CHECKPOINT",seed);}}\n'
        )
    return f'''
  let w_model:IvTaylor4Mat=jt_frequency();
  let seed:DualT4=INITIAL_SEED;
  let center:Rat=INITIAL_CENTER;
  let radial_step:Rat=big("1/32");
  let radius:Rat=big("1/64");
  let h:Rat=big("-1/32");
  let order:i64=12;
  let panel:i64=0;
  let max_width:f64=hull_width(stack_seed(seed));
  let max_tail:f64=0.0;
  while(panel<{limit}){{
    let r_model:IvTaylor4Mat=jt_radius_box(center,radius);
    let models:ModelTriple=build_models(w_model,r_model);
    let dual:DualT4=dual_series(models.base,models.tangent,h,order);
    let base_out:IvTaylor4Mat=jt_mul(dual.base,seed.base);
    let tangent_out:IvTaylor4Mat=jt_add(
      jt_mul(dual.tangent,seed.base),
      jt_mul(dual.base,seed.tangent));
    let jet_out:IvTaylor4Mat=stack_result(base_out,tangent_out);
    let direct_transport:IvTaylor4Mat=jt_series(models.direct,h,order);
    let direct_out:IvTaylor4Mat=jt_mul(direct_transport,stack_seed(seed));
    let hull:IvMat=match(ivtm4_hull_checked(models.direct)){{
      some(x)=>x,none=>{{
        println(strfmt(system_allocator(),
          "RPLUS_RESTART status=REFUSED panel={{}} code=COEFFICIENT_HULL",
          [panel]));return 3;}}}};
    let alpha:f64=sl_inf_norm_hi(hull);
    let scaled_norm:f64=rat_to_f64(radial_step)*alpha;
    let tail:f64=sl_exp_tail(scaled_norm,order+1);
    let seed_hull:IvMat=match(ivtm4_hull_checked(stack_seed(seed))){{
      some(x)=>x,none=>{{
        println(strfmt(system_allocator(),
          "RPLUS_RESTART status=REFUSED panel={{}} code=SEED_HULL",
          [panel]));return 3;}}}};
    let propagated_tail:f64=tail*sl_inf_norm_hi(seed_hull);
    if(!f64_is_finite(propagated_tail)||propagated_tail<0.0){{
      println(strfmt(system_allocator(),
        "RPLUS_RESTART status=REFUSED panel={{}} code=TAIL",
        [panel]));return 3;}}
    let jet_padded:IvTaylor4Mat=jt_pad(jet_out,propagated_tail);
    let direct_padded:IvTaylor4Mat=jt_pad(direct_out,propagated_tail);
    let exact:bool=coefficients_equal(jet_padded,direct_padded);
    let overlap:bool=difference_contains_zero(jet_padded,direct_padded);
    let width:f64=hull_width(jet_padded);
    if(!exact||!overlap||!f64_is_finite(width)||width>1.0e100){{
      println(strfmt(system_allocator(),
        "RPLUS_RESTART status=REFUSED panel={{}} code=CORRELATION_OR_WIDTH",
        [panel]));return 3;}}
    if(width>max_width){{max_width=width;}}
    if(propagated_tail>max_tail){{max_tail=propagated_tail;}}
    seed=unstack_result(jet_padded);
    center=rat_clone(center)-rat_clone(radial_step);
    panel=panel+1;
{checkpoint}  }}
  emit_mixed("{final_tag}",seed);
  println(strfmt(system_allocator(),
    "RPLUS_RESTART status=PASS panels={{}} max_width={{}} final_width={{}} max_tail={{}}",
    [panel,max_width,hull_width(stack_seed(seed)),max_tail]));
  return 0;
'''


def exporter_main() -> str:
    body = loop_body(32, 16, "REFERENCE")
    body = body.replace("INITIAL_SEED", "build_seed(w_model)")
    body = body.replace("INITIAL_CENTER", 'big("2047/64")')
    return "pub fn main()->i64{\n" + body + "}\n"


def signed_i64(hex_text: str) -> int:
    value = int(hex_text, 16)
    return value if value < 2**63 else value - 2**64


def render_model(name: str, model: dict) -> str:
    assert model["schema"] == "ivtaylor-degree4-v1"
    assert model["degree"] == 4
    rows = int(model["rows"])
    cols = int(model["cols"])
    lines = [
        f"fn {name}()->IvTaylor4Mat{{",
        f"  let c0:QMat=qm_new({rows},{cols});",
        f"  let c1:QMat=qm_new({rows},{cols});",
        f"  let c2:QMat=qm_new({rows},{cols});",
        f"  let c3:QMat=qm_new({rows},{cols});",
        f"  let c4:QMat=qm_new({rows},{cols});",
    ]
    for degree, matrix in enumerate(model["coefficients"]):
        for row, values in enumerate(matrix):
            for col, value in enumerate(values):
                lines.append(
                    f'  c{degree}=qm_set(c{degree},{row},{col},big("{value}"));'
                )
    lines.append(f"  let rem:IvMat=ivm_zeros({rows},{cols});")
    for row, values in enumerate(model["remainder_bits"]):
        for col, endpoints in enumerate(values):
            lo, hi = (signed_i64(item) for item in endpoints)
            lines.append(
                f"  ivm_set(rem,{row},{col},"
                f"iv(f64_from_bits({lo}),f64_from_bits({hi})));"
            )
    lines += [
        f"  return jt_expect(ivtm4_new({int(model['generator'])},"
        "c0,c1,c2,c3,c4,rem));",
        "}",
    ]
    return "\n".join(lines)


def restart_main() -> str:
    body = loop_body(16, None, "RESTART")
    body = body.replace(
        "INITIAL_SEED", "new DualT4(checkpoint_base(),checkpoint_tangent())"
    )
    body = body.replace("INITIAL_CENTER", 'big("2015/64")')
    return "pub fn main()->i64{\n" + body + "}\n"


def roundtrip_main() -> str:
    return r'''
pub fn main()->i64{
  let seed:DualT4=new DualT4(checkpoint_base(),checkpoint_tangent());
  emit_mixed("ROUNDTRIP",seed);
  println("RPLUS_CHECKPOINT_ROUNDTRIP status=PASS");
  return 0;
}
'''


def parse_models(output: str, prefix: str) -> tuple[dict, dict]:
    found: dict[str, dict] = {}
    for line in output.splitlines():
        for suffix in ("BASE", "TANGENT"):
            marker = f"{prefix}_{suffix} "
            if line.startswith(marker):
                found[suffix] = json.loads(line[len(marker) :])
    if set(found) != {"BASE", "TANGENT"}:
        raise ValueError(f"missing serialized {prefix} models")
    return found["BASE"], found["TANGENT"]


def parse_summary(output: str) -> dict:
    match = re.search(
        r"RPLUS_RESTART status=PASS panels=(?P<panels>\d+) "
        r"max_width=(?P<max_width>[-+0-9.eE]+) "
        r"final_width=(?P<final_width>[-+0-9.eE]+) "
        r"max_tail=(?P<max_tail>[-+0-9.eE]+)",
        output,
    )
    if match:
        result = match.groupdict()
        result["status"] = "PASS"
        return result
    refused = re.search(
        r"RPLUS_RESTART status=REFUSED panel=(?P<panel>\d+) "
        r"code=(?P<code>\w+)",
        output,
    )
    if refused:
        result = refused.groupdict()
        result["status"] = "REFUSED"
        return result
    return {"status": "UNPARSED"}


def source_prefix(data: dict, tail: dict, include_seed: bool) -> str:
    pieces = [
        seed_producer.SUPPORT,
        seed_producer.EXTRA_SUPPORT,
        panel_producer.MULTI_SUPPORT,
        SERIALIZE_SUPPORT,
    ]
    if include_seed:
        pieces.append(seed_producer.render_seed_builder(data, tail))
    pieces.append(seed_producer.render_matrix_builder(data))
    return "\n".join(pieces)


def produce() -> tuple[dict, float, list[dict]]:
    started = time.perf_counter()
    commands: list[dict] = []
    crosswalk = json.loads(CROSSWALK.read_text())
    data = seed_producer.phase_reduced_data(crosswalk)
    tail = seed_producer.jost_remainder_bound(data, crosswalk)
    env = os.environ.copy()
    env["FORGE_LIB"] = str(seed_producer.FORGE_LIB)

    EXPORT_SOURCE.write_text(
        source_prefix(data, tail, True) + "\n" + exporter_main()
    )
    export_compile = run(
        [str(seed_producer.FORGE), "-o", str(EXPORT_BINARY), str(EXPORT_SOURCE)],
        env,
    )
    commands.append(export_compile)
    EXPORT_COMPILE_LOG.write_text(export_compile["output"])
    export_run = (
        run([str(EXPORT_BINARY)], env)
        if export_compile["exit"] == 0
        else {"command": str(EXPORT_BINARY), "exit": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    commands.append(export_run)
    EXPORT_RUN_LOG.write_text(export_run["output"])

    checkpoint_written = False
    checkpoint_base: dict = {}
    checkpoint_tangent: dict = {}
    reference_base: dict = {}
    reference_tangent: dict = {}
    export_summary = parse_summary(export_run["output"])
    try:
        checkpoint_base, checkpoint_tangent = parse_models(
            export_run["output"], "CHECKPOINT"
        )
        reference_base, reference_tangent = parse_models(
            export_run["output"], "REFERENCE"
        )
        payload = {
            "arithmetic": "IvTaylor4_omega tensor dual_tau",
            "radial_state": {
                "radius": "63/2",
                "completed_panels": 16,
                "panel_width": "1/32",
                "next_panel_center": "2015/64",
                "transport_direction": "decreasing_r",
            },
            "omega_model": {
                "generator": 7315,
                "center": "8193/16384",
                "linear_coefficient": "1/16384",
                "parameter_domain": ["-1", "1"],
                "frequency_child": ["1/2", "4097/8192"],
            },
            "state_layout": {
                "base_rows": 4,
                "tangent_rows": 4,
                "stack_order": ["tangent[0:4]", "base[0:4]"],
                "shared_generator_required": True,
            },
            "base": checkpoint_base,
            "tangent": checkpoint_tangent,
        }
        checkpoint_document = {
            "schema": "phase3-axial-outgoing-rplus-mixed-checkpoint-v1",
            "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_RPLUS_CHECKPOINT_R63_OVER_2",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "lifecycle": "CLASSIFIED",
            "payload": payload,
            "payload_sha256": canonical_sha256(payload),
            "provenance": {
                "predecessor_certificate": {
                    "path": str(PREDECESSOR_CERTIFICATE.relative_to(ROOT)),
                    "sha256": sha256(PREDECESSOR_CERTIFICATE),
                },
                "export_source_sha256": sha256(EXPORT_SOURCE),
                "export_run_sha256": sha256(EXPORT_RUN_LOG),
            },
        }
        CHECKPOINT.write_text(json.dumps(checkpoint_document, indent=2) + "\n")
        checkpoint_written = True
    except (ValueError, json.JSONDecodeError, AssertionError):
        pass

    roundtrip_compile = {
        "command": "roundtrip source unavailable",
        "exit": 127,
        "elapsed_seconds": 0.0,
        "output": "",
    }
    roundtrip_run = dict(roundtrip_compile)
    roundtrip_base: dict = {}
    roundtrip_tangent: dict = {}
    restart_compile = {
        "command": "restart source unavailable",
        "exit": 127,
        "elapsed_seconds": 0.0,
        "output": "",
    }
    restart_run = dict(restart_compile)
    restart_summary = {"status": "UNAVAILABLE"}
    restart_base: dict = {}
    restart_tangent: dict = {}
    restart_source_is_replay_free = False
    if checkpoint_written:
        RESTART_SOURCE.write_text(
            "\n".join(
                (
                    source_prefix(data, tail, False),
                    render_model("checkpoint_base", checkpoint_base),
                    render_model("checkpoint_tangent", checkpoint_tangent),
                    restart_main(),
                )
            )
        )
        restart_source_is_replay_free = (
            "build_seed(" not in RESTART_SOURCE.read_text()
            and 'big("2015/64")' in RESTART_SOURCE.read_text()
        )
        ROUNDTRIP_SOURCE.write_text(
            "\n".join(
                (
                    seed_producer.SUPPORT,
                    SERIALIZE_SUPPORT,
                    render_model("checkpoint_base", checkpoint_base),
                    render_model("checkpoint_tangent", checkpoint_tangent),
                    roundtrip_main(),
                )
            )
        )
        remaining = max(1.0, 90.0 - (time.perf_counter() - started))
        roundtrip_compile = run(
            [
                str(seed_producer.FORGE),
                "-o",
                str(ROUNDTRIP_BINARY),
                str(ROUNDTRIP_SOURCE),
            ],
            env,
            remaining,
        )
        commands.append(roundtrip_compile)
        ROUNDTRIP_COMPILE_LOG.write_text(roundtrip_compile["output"])
        remaining = max(1.0, 90.0 - (time.perf_counter() - started))
        roundtrip_run = (
            run([str(ROUNDTRIP_BINARY)], env, remaining)
            if roundtrip_compile["exit"] == 0
            else {
                "command": str(ROUNDTRIP_BINARY),
                "exit": 127,
                "elapsed_seconds": 0.0,
                "output": "",
            }
        )
        commands.append(roundtrip_run)
        ROUNDTRIP_RUN_LOG.write_text(roundtrip_run["output"])
        try:
            roundtrip_base, roundtrip_tangent = parse_models(
                roundtrip_run["output"], "ROUNDTRIP"
            )
        except (ValueError, json.JSONDecodeError):
            pass
        remaining = max(1.0, 90.0 - (time.perf_counter() - started))
        restart_compile = run(
            [
                str(seed_producer.FORGE),
                "-o",
                str(RESTART_BINARY),
                str(RESTART_SOURCE),
            ],
            env,
            remaining,
        )
        commands.append(restart_compile)
        RESTART_COMPILE_LOG.write_text(restart_compile["output"])
        remaining = max(1.0, 90.0 - (time.perf_counter() - started))
        restart_run = (
            run([str(RESTART_BINARY)], env, remaining)
            if restart_compile["exit"] == 0
            else {
                "command": str(RESTART_BINARY),
                "exit": 127,
                "elapsed_seconds": 0.0,
                "output": "",
            }
        )
        commands.append(restart_run)
        RESTART_RUN_LOG.write_text(restart_run["output"])
        restart_summary = parse_summary(restart_run["output"])
        try:
            restart_base, restart_tangent = parse_models(
                restart_run["output"], "RESTART"
            )
        except (ValueError, json.JSONDecodeError):
            pass
    else:
        RESTART_SOURCE.write_text("")
        ROUNDTRIP_SOURCE.write_text("")
        ROUNDTRIP_COMPILE_LOG.write_text("")
        ROUNDTRIP_RUN_LOG.write_text("")
        RESTART_COMPILE_LOG.write_text("")
        RESTART_RUN_LOG.write_text("")

    exact_roundtrip = (
        bool(checkpoint_base)
        and checkpoint_base == roundtrip_base
        and checkpoint_tangent == roundtrip_tangent
    )
    exact_restart = (
        bool(reference_base)
        and reference_base == restart_base
        and reference_tangent == restart_tangent
    )
    passed = (
        export_compile["exit"] == 0
        and export_run["exit"] == 0
        and export_summary["status"] == "PASS"
        and checkpoint_written
        and restart_source_is_replay_free
        and roundtrip_compile["exit"] == 0
        and roundtrip_run["exit"] == 0
        and "RPLUS_CHECKPOINT_ROUNDTRIP status=PASS" in roundtrip_run["output"]
        and exact_roundtrip
        and restart_compile["exit"] == 0
        and restart_run["exit"] == 0
        and restart_summary["status"] == "PASS"
        and exact_restart
    )
    document = {
        "schema": "phase3-axial-partial-jet-outgoing-rplus-checkpoint-resume-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_OUTGOING_RPLUS_CHECKPOINT_RESUME",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "RPLUS_CHECKPOINT_RESTART_SECOND_CHUNK_PASS"
            if passed
            else "RPLUS_CHECKPOINT_RESUME_SHORTFALL"
        ),
        "imports": {
            "predecessor_certificate": {
                "path": str(PREDECESSOR_CERTIFICATE.relative_to(ROOT)),
                "sha256": sha256(PREDECESSOR_CERTIFICATE),
            },
            "crosswalk": {
                "path": str(CROSSWALK.relative_to(ROOT)),
                "sha256": sha256(CROSSWALK),
            },
        },
        "checkpoint": {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": sha256(CHECKPOINT) if checkpoint_written else None,
            "schema_path": str(CHECKPOINT_SCHEMA.relative_to(ROOT)),
            "schema_sha256": sha256(CHECKPOINT_SCHEMA),
            "payload_sha256": (
                json.loads(CHECKPOINT.read_text())["payload_sha256"]
                if checkpoint_written
                else None
            ),
            "radius": "63/2",
            "shared_omega_generator": 7315,
            "restart_source_is_replay_free": restart_source_is_replay_free,
        },
        "transport": {
            "reference": {
                "start_radius": "32",
                "end_radius": "31",
                "panels": 32,
                "summary": export_summary,
            },
            "restart": {
                "start_radius": "63/2",
                "end_radius": "31",
                "panels": 16,
                "summary": restart_summary,
            },
            "exact_serialized_checkpoint_roundtrip": exact_roundtrip,
            "exact_serialized_final_state_match": exact_restart,
            "export_source_path": str(EXPORT_SOURCE.relative_to(ROOT)),
            "export_source_sha256": sha256(EXPORT_SOURCE),
            "export_compile_log_path": str(EXPORT_COMPILE_LOG.relative_to(ROOT)),
            "export_compile_log_sha256": sha256(EXPORT_COMPILE_LOG),
            "export_run_log_path": str(EXPORT_RUN_LOG.relative_to(ROOT)),
            "export_run_log_sha256": sha256(EXPORT_RUN_LOG),
            "restart_source_path": str(RESTART_SOURCE.relative_to(ROOT)),
            "restart_source_sha256": sha256(RESTART_SOURCE),
            "roundtrip_source_path": str(ROUNDTRIP_SOURCE.relative_to(ROOT)),
            "roundtrip_source_sha256": sha256(ROUNDTRIP_SOURCE),
            "roundtrip_compile_log_path": str(
                ROUNDTRIP_COMPILE_LOG.relative_to(ROOT)
            ),
            "roundtrip_compile_log_sha256": sha256(ROUNDTRIP_COMPILE_LOG),
            "roundtrip_run_log_path": str(ROUNDTRIP_RUN_LOG.relative_to(ROOT)),
            "roundtrip_run_log_sha256": sha256(ROUNDTRIP_RUN_LOG),
            "restart_compile_log_path": str(RESTART_COMPILE_LOG.relative_to(ROOT)),
            "restart_compile_log_sha256": sha256(RESTART_COMPILE_LOG),
            "restart_run_log_path": str(RESTART_RUN_LOG.relative_to(ROOT)),
            "restart_run_log_sha256": sha256(RESTART_RUN_LOG),
        },
        "claim_flags": {
            "mixed_checkpoint_serialized": checkpoint_written,
            "checkpoint_payload_content_addressed": checkpoint_written,
            "restart_does_not_replay_from_r32": restart_source_is_replay_free,
            "checkpoint_roundtrip_is_bit_exact": exact_roundtrip,
            "restart_matches_independent_reference_exactly": exact_restart,
            "Rplus_reaches_r31": passed,
            "Rplus_reaches_r4": False,
            "complementary_outgoing_columns_constructed": False,
            "K_plus_computed": False,
            "T_plus_recovered": False,
            "scattering_claim": False,
        },
        "shortfall": (
            None
            if passed
            else {
                "code": "CHECKPOINT_OR_RESTART_GATE_FAILED",
                "export_summary": export_summary,
                "restart_summary": restart_summary,
                "checkpoint_written": checkpoint_written,
                "replay_free": restart_source_is_replay_free,
                "exact_roundtrip": exact_roundtrip,
                "exact_restart": exact_restart,
                "detail": (
                    "At least one content-addressed checkpoint, round-trip, "
                    "restart, or independent-reference gate failed."
                ),
                "next_gate": (
                    "inspect the first failing gate without promoting r=31"
                ),
            }
        ),
        "does_not_establish": [
            "transport of Rplus from r=31 to r=4",
            "any complementary outgoing column",
            "the endpoint K_plus shear",
            "T_plus, reflection, scattering, or flux",
        ],
        "producer_elapsed_seconds": 0.0,
    }
    return document, time.perf_counter() - started, commands


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()
    document, elapsed, commands = produce()
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    receipt = {
        "result_id": document["result_id"],
        "status": "PASS" if document["status"].endswith("_PASS") else "SHORTFALL",
        "certificate_path": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            {
                "command": item["command"],
                "elapsed_seconds": item["elapsed_seconds"],
                "status": "PASS" if item["exit"] == 0 else "FAIL",
            }
            for item in commands
        ],
        "producer_elapsed_seconds": elapsed,
        "higher_tiers_not_run": (
            "No T2/T3: selected Rplus checkpoint/restart only; Tplus stays false."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    if args.print:
        print(json.dumps(document, indent=2))


if __name__ == "__main__":
    main()
