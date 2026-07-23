#!/usr/bin/env python3
"""Render the rigorous exact-point horizon plane in moving dyadic frames."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from ...axial_horizon_grassmann_mobius_to_r4_taylor2 import carrier_point
from .point_horizon_dyadic_frames import (
    FRAMES_PER_SHELL,
    SCHEMA as FRAME_SCHEMA,
)
from .verify_handoff import canonical_sha256


SCHEMA = "phase3-axial-exact-point-horizon-dyadic-transport-v1"


class HorizonDyadicTransportError(RuntimeError):
    """Raised when a frame schedule or generated trace is inconsistent."""


def _complex_matrix(data: list) -> list[list[complex | tuple[Fraction, Fraction]]]:
    return [
        [(Fraction(value[0]), Fraction(value[1])) for value in row]
        for row in data
    ]


def _realify(data: list) -> list[list[Fraction]]:
    matrix = _complex_matrix(data)
    size = len(matrix)
    out = [[Fraction(0) for _ in range(2 * size)] for _ in range(2 * size)]
    for row in range(size):
        for col in range(size):
            real, imag = matrix[row][col]
            out[row][col] = real
            out[row][col + size] = -imag
            out[row + size][col] = imag
            out[row + size][col + size] = real
    return out


def _qmat_builder(name: str, matrix: list[list[Fraction]]) -> str:
    lines = [
        f"fn {name}()->IvTaylorMat{{",
        "  let q:QMat=qm_new(8,8);",
    ]
    for row in range(8):
        for col in range(8):
            value = matrix[row][col]
            if value:
                lines.append(
                    f'  q=qm_set(q,{row},{col},big("'
                    f'{value.numerator}/{value.denominator}"));'
                )
    lines += [
        "  return ivtm_constant(7315,q);",
        "}",
        "",
    ]
    return "\n".join(lines)


def _load_schedule(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if (
        payload.get("schema") != FRAME_SCHEMA
        or payload.get("status") != "NONCERTIFYING_FRAME_CHOICE"
        or payload.get("frequency") != "4097/8192"
        or payload.get("frame_count") != 23 * FRAMES_PER_SHELL + 1
        or len(payload.get("frames", [])) != 23 * FRAMES_PER_SHELL + 1
    ):
        raise HorizonDyadicTransportError("dyadic frame schedule drift")
    without_hash = dict(payload)
    stored = without_hash.pop("payload_sha256")
    if stored != canonical_sha256(without_hash):
        raise HorizonDyadicTransportError("dyadic frame payload hash drift")
    for frame in payload["frames"]:
        s = _realify(frame["S"])
        sinv = _realify(frame["Sinv"])
        for row in range(8):
            for col in range(8):
                value = sum(s[row][k] * sinv[k][col] for k in range(8))
                if value != Fraction(row == col):
                    raise HorizonDyadicTransportError(
                        f"frame {frame['index']} inverse identity failed"
                    )
    return payload


ATTEMPT = r'''
fn phd_mul(a:borrow IvTaylorMat,b:borrow IvTaylorMat)->IvTaylorMat{
  let x:IvTaylorResult=ivtm_mul_checked(a,b);
  if(!x.ok){trap();}return ivtm_clone(x.value);
}

fn phd_frame_factor(phi:borrow IvTaylorMat,s:borrow IvTaylorMat,
sinv:borrow IvTaylorMat)->IvTaylorMat{
  return phd_mul(phd_mul(s,phi),sinv);
}

fn phd_attempt(shell:i64,panel_start:i64,panel_count:i64,panels:i64,
cell:borrow IvAffineCell,
start:borrow CpState,s:borrow IvTaylorMat,sinv:borrow IvTaylorMat)->CpAttempt{
  let state:CpState=new CpState(true,start.chart,ivtm_clone(start.z),
    iv_point(1.0),iv_point(1.0));
  let fw:Iv=iv_point(1.0);let iw:Iv=iv_point(1.0);
  let mc:f64=1.0;let panel:i64=panel_start;
  while(panel<panel_start+panel_count){
    let lo:Rat=hr_shell_lo(shell);
    let w:Rat=(hr_panel_width(shell)*rat(256,1))/rat(panels,1);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(w));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(w));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(w));
    let a:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(w)/rat(2,1),cell);
    let p0:IvAffineMat=match(sl_local_transition(a,w,12)){
      some(z)=>z,none=>{println(strfmt(system_allocator(),
        "DYADIC_ATTEMPT_REFUSE kind=local shell={} panel={} panels={}",
        [shell,panel,panels]));
        return new CpAttempt(false,cp_fail(),fw,iw,mc);}};
    let p:IvTaylorMat=phd_frame_factor(
      cp_carrier(cp_pointify(p0)),s,sinv);
    let sn:CpState=cp_step_any(p,state);
    if(!sn.ok){println(strfmt(system_allocator(),
      "DYADIC_ATTEMPT_REFUSE kind=mobius shell={} panel={} panels={}",
      [shell,panel,panels]));
      return new CpAttempt(false,cp_fail(),fw,iw,mc);}
    fw=iv_mul(fw,sn.forward_bound);iw=iv_mul(sn.inverse_bound,iw);
    let cond:Iv=iv_mul(sn.forward_bound,sn.inverse_bound);
    if(cond.hi>mc){mc=cond.hi;}
    state=new CpState(true,sn.chart,ivtm_clone(sn.z),
      iv_point(1.0),iv_point(1.0));panel=panel+1;
  }
  return new CpAttempt(true,new CpState(true,state.chart,ivtm_clone(state.z),
    iv_point(1.0),iv_point(1.0)),fw,iw,mc);
}
'''


def render(schedule_path: Path) -> tuple[str, dict[str, Any]]:
    schedule = _load_schedule(schedule_path)
    source = carrier_point.render()
    cutoff = "if(!z.ok || cp_norm(z.value)>=2.0){return cp_fail();}"
    if source.count(cutoff) != 2:
        raise HorizonDyadicTransportError("upstream graph cutoff drift")
    source = source.replace(cutoff, "if(!z.ok){return cp_fail();}")
    marker = "pub fn main()->i64{"
    if source.count(marker) != 1:
        raise HorizonDyadicTransportError("upstream carrier main drift")
    prefix = source.split(marker, 1)[0]
    builders = []
    for frame in schedule["frames"]:
        index = int(frame["index"])
        builders.append(_qmat_builder(f"phd_s_{index}", _realify(frame["S"])))
        builders.append(
            _qmat_builder(f"phd_sinv_{index}", _realify(frame["Sinv"]))
        )
    main = [
        "pub fn main()->i64{",
        "  let cell:IvAffineCell=hr_cell();",
        "  let full:IvTaylorMat=hr_reorder_rows(",
        "    cp_pointify(hc_initial_model(cell)),true);",
        "  let y0:IvTaylorMat=phd_mul(phd_s_0(),cp_initial(full));",
        "  let state:CpState=cp_from_basis(y0,0);",
        '  if(!state.ok){println("DYADIC_REFUSE initial");return 3;}',
        "  let fw:Iv=state.forward_bound;let iw:Iv=state.inverse_bound;",
        "  let mc:f64=iv_mul(fw,iw).hi;",
        '  println("DYADIC_BEGIN omega=4097/8192 basis=XH0a,XH0b");',
    ]
    for shell in range(23):
        for segment in range(FRAMES_PER_SHELL):
            index = shell * FRAMES_PER_SHELL + segment
            main += [
                f"  let used_{index}:i64=64;",
                f"  let a_{index}:CpAttempt=phd_attempt("
                f"{shell},{segment * 8},8,64,cell,state,"
                f"phd_s_{index}(),phd_sinv_{index}());",
                f"  if(!a_{index}.ok){{used_{index}=128;",
                f'    println("DYADIC_FALLBACK shell={shell} '
                f'segment={segment} panels=128");',
                f"    a_{index}=phd_attempt("
                f"{shell},{segment * 16},16,128,cell,state,"
                f"phd_s_{index}(),phd_sinv_{index}());}}",
                f"  if(!a_{index}.ok){{used_{index}=256;",
                f'    println("DYADIC_FALLBACK shell={shell} '
                f'segment={segment} panels=256");',
                f"    a_{index}=phd_attempt("
                f"{shell},{segment * 32},32,256,cell,state,"
                f"phd_s_{index}(),phd_sinv_{index}());}}",
                f"  if(!a_{index}.ok){{println("
                f'"DYADIC_REFUSE shell={shell} segment={segment}");'
                f"return 3;}}",
                f"  fw=iv_mul(fw,a_{index}.forward_bound);",
                f"  iw=iv_mul(a_{index}.inverse_bound,iw);",
                f"  if(a_{index}.max_condition>mc)"
                f"{{mc=a_{index}.max_condition;}}",
                f"  state=new CpState(true,a_{index}.state.chart,"
                f"ivtm_clone(a_{index}.state.z),"
                f"iv_point(1.0),iv_point(1.0));",
                f"  let change_{index}:IvTaylorMat=phd_mul("
                f"phd_s_{index + 1}(),phd_sinv_{index}());",
                f"  let moved_{index}:CpState="
                f"cp_step_any(change_{index},state);",
                f"  if(!moved_{index}.ok){{println("
                f'"DYADIC_REFUSE frame-change={index}");return 3;}}',
                f"  state=cp_from_basis(cp_graph(moved_{index}.z,"
                f"moved_{index}.chart),0);",
                f"  if(!state.ok){{println("
                f'"DYADIC_REFUSE frame-best={index}");return 3;}}',
            ]
        main += [
            f'  println(strfmt(system_allocator(),'
            f'"DYADIC_SHELL shell={shell} chart={{}} norm={{}} '
            f'zwidth={{}}",'
            f"[state.chart,cp_norm(state.z),cp_width(state.z)]));",
        ]
    main += [
        "  let framed:IvTaylorMat=cp_graph(state.z,state.chart);",
        f"  let out:IvTaylorMat=phd_mul("
        f"phd_sinv_{23 * FRAMES_PER_SHELL}(),framed);",
        "  let rank:IvTaylorRank=ivtm_full_column_rank_cells(out,64);",
        '  if(!rank.certified || rank.rank!=4){',
        '    println("DYADIC_REFUSE final-rank");return 3;}',
        '  println(strfmt(system_allocator(),'
        '"DYADIC_RESULT omega=4097/8192 radius=4 complex_rank=2 '
        'real_rank=4 chart={} norm={} width={} forward_bound={} '
        'inverse_bound={} max_local_condition={}",',
        "[state.chart,cp_norm(state.z),cp_width(out),fw.hi,iw.hi,mc]));",
        "  cp_emit(out);",
        '  println("DYADIC_PASS omega=4097/8192 radius=4");return 42;',
        "}",
        "",
    ]
    rendered = prefix + "\n".join(builders) + ATTEMPT + "\n".join(main)
    metadata = {
        "schema": SCHEMA,
        "status": "RENDERED",
        "frequency": "4097/8192",
        "rho_start": "1/4194304",
        "rho_end": "2/1",
        "state_order": (
            "Re(P),Re(Pprime),Re(Q),Re(Qprime),"
            "Im(P),Im(Pprime),Im(Q),Im(Qprime)"
        ),
        "plane": "span(XH0a,XH0b)",
        "frame_payload_sha256": schedule["payload_sha256"],
        "source_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        "does_not_establish": [
            "the infinity splitting or its intersection with this plane",
            "a finite-flux scattering channel",
            "flux, stability, CPT, or unitarity",
        ],
    }
    return rendered, metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    source, receipt = render(args.frames)
    args.source.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.source.write_text(source)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(receipt["source_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
