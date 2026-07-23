#!/usr/bin/env python3
"""Regenerate fixed-frequency Ricci-carrier factors without reconstruction rows."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import (
    MICROFACTOR_COUNT,
    _canonical_sha256,
    _frame_payload,
    render_microfactor_adapter,
)
from ..affine_codegen import (
    FrameTaylor,
    numerical_frames_with_sensitivity,
)
from .run_point_microfactor_batch import (
    OMEGA0,
    build_point_context,
    point_trace_id,
    render_point_factor,
    verify_point_source,
)


SCHEMA = "phase3-axial-exact-point-carrier-factor-batch-v1"


def render_point_carrier_factor(
    micro: int,
    context: dict[str, Any],
    *,
    child: int | None = None,
    split: int = 8,
    local_frames: tuple[FrameTaylor, ...] | None = None,
    base_frame_table_sha256: str | None = None,
) -> tuple[str, str, int]:
    local_steps = 8 if child is None else 1
    if child is None:
        source, _ = render_point_factor(micro, context)
        trace = point_trace_id(micro)
        lo, hi = Fraction(micro, 8), Fraction(micro + 1, 8)
    else:
        if split not in (8, 32) or not 0 <= child < split:
            raise ValueError("carrier split child out of range")
        trace = (500_000 if split == 8 else 600_000) + split * micro + child
        panel = split * micro + child
        source, _ = render_microfactor_adapter(
            micro,
            context=context,
            panel_start=panel,
            panel_count=1,
            trace_id=trace,
            panel_denominator=8 * split,
            local_frames=local_frames,
            base_frame_table_sha256=base_frame_table_sha256,
        )
        verify_point_source(source)
        lo, hi = Fraction(panel, 8 * split), Fraction(panel + 1, 8 * split)
    marker = "fn gc_emit_affine(a:borrow IvAffineMat)->void{"
    if source.count(marker) != 1:
        raise RuntimeError("point factor emitter boundary drift")
    prefix = source.split(marker, 1)[0]
    suffix = f'''
fn pcf_emit(a:borrow IvAffineMat)->void{{
  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<8){{
    let j:i64=0;while(j<8){{
      let cv:f64=rat_to_f64(qm_get(a.center,i,j));
      let q:Iv=ivm_at(h,i,j);
      println(strfmt(system_allocator(),"C {{}} {{}} {{}} {{}} {{}}",
        [i,j,f64_bits(cv),f64_bits(q.lo),f64_bits(q.hi)]));
      j=j+1;}}i=i+1;}}
}}

fn axial_point_carrier_factor(j:i64)->bool{{
  if(j!={trace}){{return false;}}
  let at:Vec<IvAffineMat>=gc_micro_coeff_table(j);
  let ac:Vec<IvAffineMat>=gc_micro_subtable(at,0);
  let cell:IvAffineCell=gc_cell();
  let fc:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(
    ac,gc_micro_frames(j,0),cell,8,big("{lo}"),big("{hi}"),
    1,{local_steps},12,8,true,true,true);
  println(strfmt(system_allocator(),"CARRIER_FLOW {{}} {{}} {{}}",
    [fc.ok,fc.refusal_code,fc.refusal_reset]));
  if(!fc.ok){{return false;}}
  let eye:IvAffineMat=ivam_identity(gc_cell().generator,8);
  let raw:IvAffineResult=ivlin_param_affine_apply_rect(fc,eye);
  if(!raw.ok){{return false;}}
  let rb:IvAffineResult=ivam_rebase_dyadic(raw.value,128);
  if(!rb.ok){{return false;}}let phi:IvAffineMat=ivam_clone(rb.value);
  let rank:IvAffineRank=ivam_full_column_rank_cells(phi,32);
  println(strfmt(system_allocator(),"CARRIER_RESULT {{}} {{}} {{}}",
    [j,rank.rank,ivam_max_width(phi)]));
  if(!rank.certified || rank.rank!=8){{return false;}}
  pcf_emit(phi);println(strfmt(system_allocator(),"CARRIER_END {{}}",[j]));
  return true;
}}

pub fn main()->i64{{
  let j:i64=if(args_count()>1){{match(parse_i64(bytes(arg(1)),0)){{
    ok(p)=>p.v,err(e)=>-1}}}}else{{-1}};
  if(!axial_point_carrier_factor(j)){{return 3;}}return 42;
}}
'''
    rendered = prefix + suffix
    return rendered, hashlib.sha256(rendered.encode()).hexdigest(), trace


def _run_one(
    micro: int, child: int | None, trace: int,
    source: Path, binary: Path, log: Path, digest: str,
) -> dict[str, Any]:
    compiled = subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        text=True, capture_output=True, timeout=300,
    )
    if compiled.returncode:
        return {
            "micro": micro, "child": child, "trace_id": trace,
            "status": "REFUSED", "stage": "compile",
            "stderr": compiled.stderr[-3000:],
        }
    ran = subprocess.run(
        [str(binary), str(trace)],
        text=True, capture_output=True, timeout=900,
    )
    log.write_text(ran.stdout)
    return {
        "micro": micro,
        "child": child,
        "trace_id": trace,
        "status": "PASS" if ran.returncode == 42 else "REFUSED",
        "stage": "complete" if ran.returncode == 42 else "run",
        "returncode": ran.returncode,
        "source_sha256": digest,
        "log": str(log),
        "stderr": ran.stderr[-3000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=MICROFACTOR_COUNT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--split8",
        action="store_true",
        help="emit eight one-panel carrier factors per selected parent",
    )
    parser.add_argument(
        "--split32",
        action="store_true",
        help="emit thirty-two raw-panel carrier factors per selected parent",
    )
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.start < args.end <= MICROFACTOR_COUNT:
        raise SystemExit("bad carrier factor range")
    if not 1 <= args.workers <= 8:
        raise SystemExit("workers must lie in [1,8]")
    sources = args.scratch / "sources"
    binaries = args.scratch / "bin"
    logs = args.scratch / "logs"
    for path in (sources, binaries, logs):
        path.mkdir(parents=True, exist_ok=True)
    context = build_point_context()
    if args.split8 and args.split32:
        raise SystemExit("--split8 and --split32 are mutually exclusive")
    split = 32 if args.split32 else (8 if args.split8 else 1)
    local_tail_frames: tuple[FrameTaylor, ...] | None = None
    local_frame_hash: str | None = None
    if args.split32:
        data = context["data"]
        raw = numerical_frames_with_sensitivity(
            data["inward"], context["t"], data["omega"], OMEGA0,
            Fraction(args.start, 8), Fraction(args.end, 8),
            32 * (args.end - args.start), bits=34,
        )
        zero = tuple(
            tuple(Fraction(0) for _ in row) for row in raw[0].derivative
        )
        local_tail_frames = tuple(
            FrameTaylor(frame.center, zero) for frame in raw
        )
        local_frame_hash = _canonical_sha256(
            [_frame_payload(frame) for frame in local_tail_frames]
        )
    jobs, receipts = [], []
    for micro in range(args.start, args.end):
        children = range(split) if split > 1 else (None,)
        for child in children:
            suffix = f"{micro:03d}" if child is None else f"{micro:03d}_{child}"
            text, digest, trace = render_point_carrier_factor(
                micro,
                context,
                child=child,
                split=split,
                local_frames=(
                    None if local_tail_frames is None else
                    local_tail_frames[
                        32 * (micro - args.start) + int(child):
                        32 * (micro - args.start) + int(child) + 2
                    ]
                ),
                base_frame_table_sha256=local_frame_hash,
            )
            source = sources / f"carrier_{suffix}.forge"
            source.write_text(text)
            jobs.append((
                micro, child, trace, source,
                binaries / f"carrier_{suffix}",
                logs / f"carrier_{suffix}.log", digest,
            ))
            receipts.append({
                "micro": micro, "child": child, "trace_id": trace,
                "source_sha256": digest,
            })
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_run_one, *job): job for job in jobs}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                f"{result['status']} carrier={result['micro']} "
                f"child={result['child']} "
                f"stage={result['stage']}",
                flush=True,
            )
    results.sort(key=lambda value: (
        value["micro"],
        -1 if value.get("child") is None else value["child"],
    ))
    payload = {
        "schema": SCHEMA,
        "frequency": "4097/8192",
        "range": [args.start, args.end],
        "split8": args.split8,
        "split32": args.split32,
        "split": split,
        "sources": receipts,
        "results": results,
        "all_passed": (
            len(results) == (args.end - args.start) * split
            and all(item["status"] == "PASS" for item in results)
        ),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0 if payload["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
