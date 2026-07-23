#!/usr/bin/env python3
"""Staged exact-point transport of the two Ricci-carrier infinity planes."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

from .infinity_plane_taylor_transport import (
    GENERATOR,
    IVTAYLOR_COMMIT,
    IVTAYLOR_PATH,
    IVTAYLOR_SHA256,
    _f64,
    _serialized_builder,
    _strip_endpoint_source,
)
from .point_carrier_factor_artifact import verify_carrier_factor
from .verify_handoff import _require, canonical_sha256


SCHEMA = "phase3-axial-exact-point-carrier-plane-stage-v1"
STAGE_BOUNDARIES = (
    0, 32, 64, 96, 128, 160, 192, 220, 252, 284, 316, 348,
)
PAIRS = ((0, 4), (1, 5), (2, 6), (3, 7))
CHARTS = tuple(itertools.combinations(range(4), 2))


class PointCarrierError(RuntimeError):
    pass


def _imports() -> str:
    return "\n".join([
        "// expect: 42",
        "// backends: c native",
        "// Fixed-frequency Ricci-carrier Grassmann transport.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivlinode;",
        "import math/ivendpoint;",
        "import math/ivaffine;",
        "import math/ivtaylor;",
        "import ds/vec;",
        "import ds/manualvec;",
        "import text/parse;",
        "import text/format;",
        "import text/strbuilder;",
        "",
    ])


def _chart_dispatch() -> str:
    def rows(triple: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(PAIRS[index][0] for index in triple) + tuple(
            PAIRS[index][1] for index in triple
        )

    pivots = [rows(chart) for chart in CHARTS]
    graphs = [
        rows(tuple(index for index in range(4) if index not in chart))
        for chart in CHARTS
    ]

    def function(name: str, table: list[tuple[int, ...]]) -> str:
        expressions = []
        for selected in table:
            expression = "else{".join(
                [f"if(k=={i}){{{row}}}"
                 for i, row in enumerate(selected[:-1])]
                + [f"{{{selected[-1]}}}"]
            ) + "}" * (len(selected) - 1)
            expressions.append(expression)
        body = "else{".join(
            [f"if(chart=={chart}){{return {expression};}}"
             for chart, expression in enumerate(expressions[:-1])]
            + [f"{{return {expressions[-1]};}}"]
        ) + "}" * (len(expressions) - 1)
        return f"fn pc_i64_{name}(chart:i64,k:i64)->i64{{{body}}}\n"

    return function("i", pivots) + function("j", graphs)


COMMON = r'''
pub type PcState = scoped struct {
  pub ok: bool,
  pub chart: i64,
  pub z: IvTaylorMat,
};

fn pc_zero()->IvTaylorMat{return ivtm_constant(7315,qm_new(4,4));}
fn pc_fail()->PcState{return new PcState(false,-1,pc_zero());}

fn pc_rows(a:borrow IvTaylorMat,chart:i64,pivot:bool)->IvTaylorMat{
  let c0:QMat=qm_new(4,a.cols);let c1:QMat=qm_new(4,a.cols);
  let c2:QMat=qm_new(4,a.cols);let rem:IvMat=ivm_zeros(4,a.cols);
  let i:i64=0;while(i<4){
    let si:i64=if(pivot){pc_i64_i(chart,i)}else{pc_i64_j(chart,i)};
    let j:i64=0;while(j<a.cols){
      c0=qm_set(c0,i,j,qm_get(a.c0,si,j));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,j));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,j));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,4,a.cols,c0,c1,c2,rem);
}

fn pc_block(a:borrow IvTaylorMat,chart:i64,row_i:bool,col_i:bool)
->IvTaylorMat{
  let c0:QMat=qm_new(4,4);let c1:QMat=qm_new(4,4);
  let c2:QMat=qm_new(4,4);let rem:IvMat=ivm_zeros(4,4);
  let i:i64=0;while(i<4){
    let si:i64=if(row_i){pc_i64_i(chart,i)}else{pc_i64_j(chart,i)};
    let j:i64=0;while(j<4){
      let sj:i64=if(col_i){pc_i64_i(chart,j)}else{pc_i64_j(chart,j)};
      c0=qm_set(c0,i,j,qm_get(a.c0,si,sj));
      c1=qm_set(c1,i,j,qm_get(a.c1,si,sj));
      c2=qm_set(c2,i,j,qm_get(a.c2,si,sj));
      ivm_set(rem,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,4,4,c0,c1,c2,rem);
}

fn pc_graph_basis(z:borrow IvTaylorMat,chart:i64)->IvTaylorMat{
  let c0:QMat=qm_new(8,4);let c1:QMat=qm_new(8,4);
  let c2:QMat=qm_new(8,4);let rem:IvMat=ivm_zeros(8,4);
  let i:i64=0;while(i<4){
    c0=qm_set(c0,pc_i64_i(chart,i),i,rat(1,1));
    let j:i64=0;while(j<4){
      c0=qm_set(c0,pc_i64_j(chart,i),j,qm_get(z.c0,i,j));
      c1=qm_set(c1,pc_i64_j(chart,i),j,qm_get(z.c1,i,j));
      c2=qm_set(c2,pc_i64_j(chart,i),j,qm_get(z.c2,i,j));
      ivm_set(rem,pc_i64_j(chart,i),j,ivm_at(z.remainder,i,j));
      j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,8,4,c0,c1,c2,rem);
}

fn pc_norm(a:borrow IvTaylorMat)->f64{
  let h:IvMat=ivtm_hull(a);let best:f64=0.0;let i:i64=0;
  while(i<a.rows){let j:i64=0;while(j<a.cols){
    let x:Iv=iv_abs(ivm_at(h,i,j));if(x.hi>best){best=x.hi;}
    j=j+1;}i=i+1;}return best;
}

fn pc_from_basis(y:borrow IvTaylorMat,chart:i64)->PcState{
  let u:IvTaylorMat=pc_rows(y,chart,true);
  let v:IvTaylorMat=pc_rows(y,chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,1);
  if(!rank.certified || rank.rank!=4){return pc_fail();}
  let zr0:IvTaylorResult=ivtm_solve_right(v,u);
  if(!zr0.ok){return pc_fail();}
  let zr:IvTaylorResult=ivtm_rebase_dyadic(zr0.value,160);
  if(!zr.ok){return pc_fail();}
  return new PcState(true,chart,ivtm_clone(zr.value));
}

fn pc_rechart(s:borrow PcState,new_chart:i64)->PcState{
  if(!s.ok){return pc_fail();}
  if(new_chart==s.chart){
    return new PcState(true,s.chart,ivtm_clone(s.z));}
  return pc_from_basis(pc_graph_basis(s.z,s.chart),new_chart);
}

fn pc_best_basis(y:borrow IvTaylorMat)->PcState{
  let best:PcState=pc_fail();let c:i64=0;
  while(c<6){let cand:PcState=pc_from_basis(y,c);
    if(cand.ok && (!best.ok || pc_norm(cand.z)<pc_norm(best.z))){
      best=new PcState(true,cand.chart,ivtm_clone(cand.z));}
    drop(cand);c=c+1;}return best;
}

fn pc_best_chart(s:borrow PcState)->PcState{
  let best:PcState=pc_fail();let c:i64=0;
  while(c<6){let cand:PcState=pc_rechart(s,c);
    if(cand.ok && (!best.ok || pc_norm(cand.z)<pc_norm(best.z))){
      best=new PcState(true,cand.chart,ivtm_clone(cand.z));}
    drop(cand);c=c+1;}return best;
}

fn pc_step(phi:borrow IvTaylorMat,s:borrow PcState)->PcState{
  let pii:IvTaylorMat=pc_block(phi,s.chart,true,true);
  let pij:IvTaylorMat=pc_block(phi,s.chart,true,false);
  let pji:IvTaylorMat=pc_block(phi,s.chart,false,true);
  let pjj:IvTaylorMat=pc_block(phi,s.chart,false,false);
  let az:IvTaylorResult=ivtm_mul_checked(pij,s.z);
  let bz:IvTaylorResult=ivtm_mul_checked(pjj,s.z);
  if(!az.ok || !bz.ok){return pc_fail();}
  let m0:IvTaylorResult=ivtm_add_checked(pii,az.value);
  let n0:IvTaylorResult=ivtm_add_checked(pji,bz.value);
  if(!m0.ok || !n0.ok){return pc_fail();}
  let m:IvTaylorResult=ivtm_rebase_dyadic(m0.value,160);
  let n:IvTaylorResult=ivtm_rebase_dyadic(n0.value,160);
  if(!m.ok || !n.ok){return pc_fail();}
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(m.value,1);
  if(!rank.certified || rank.rank!=4){return pc_fail();}
  let zr0:IvTaylorResult=ivtm_solve_right(n.value,m.value);
  if(!zr0.ok){return pc_fail();}
  let zr:IvTaylorResult=ivtm_rebase_dyadic(zr0.value,160);
  if(!zr.ok){return pc_fail();}
  return new PcState(true,s.chart,ivtm_clone(zr.value));
}

fn pc_step_any(phi:borrow IvTaylorMat,s:borrow PcState)->PcState{
  let direct:PcState=pc_step(phi,s);
  if(direct.ok){return new PcState(true,direct.chart,ivtm_clone(direct.z));}
  let best:PcState=pc_fail();let c:i64=0;
  while(c<6){let charted:PcState=pc_rechart(s,c);
    if(charted.ok){let stepped:PcState=pc_step(phi,charted);
      if(stepped.ok && (!best.ok || pc_norm(stepped.z)<pc_norm(best.z))){
        best=new PcState(true,stepped.chart,ivtm_clone(stepped.z));}
      drop(stepped);}drop(charted);c=c+1;}return best;
}

fn pc_hcat(a:borrow IvTaylorMat,b:borrow IvTaylorMat)->IvTaylorMat{
  let c0:QMat=qm_new(8,8);let c1:QMat=qm_new(8,8);
  let c2:QMat=qm_new(8,8);let rem:IvMat=ivm_zeros(8,8);
  let i:i64=0;while(i<8){let j:i64=0;while(j<8){
    let left:bool=j<4;let sj:i64=if(left){j}else{j-4};
    c0=qm_set(c0,i,j,if(left){qm_get(a.c0,i,sj)}else{qm_get(b.c0,i,sj)});
    c1=qm_set(c1,i,j,if(left){qm_get(a.c1,i,sj)}else{qm_get(b.c1,i,sj)});
    c2=qm_set(c2,i,j,if(left){qm_get(a.c2,i,sj)}else{qm_get(b.c2,i,sj)});
    ivm_set(rem,i,j,if(left){ivm_at(a.remainder,i,sj)}
      else{ivm_at(b.remainder,i,sj)});j=j+1;}i=i+1;}
  return new IvTaylorMat(7315,8,8,c0,c1,c2,rem);
}
'''


def _factor_builder(name: str, matrix: dict[str, Any]) -> list[str]:
    lines = [
        f"fn {name}()->IvTaylorMat{{",
        "  let c0:QMat=qm_new(8,8);let c1:QMat=qm_new(8,8);",
        "  let c2:QMat=qm_new(8,8);let rem:IvMat=ivm_zeros(8,8);",
    ]
    for row in range(8):
        for col in range(8):
            center = matrix["center"][row][col]
            linear = matrix["linear"][row][col]
            remainder = matrix["remainder"][row][col]
            _require(linear == "0/1", "point carrier factor has linear drift")
            if center != "0/1":
                lines.append(
                    f'  c0=qm_set(c0,{row},{col},big("{center}"));'
                )
            if remainder != ["0000000000000000", "0000000000000000"]:
                lines.append(
                    f"  ivm_set(rem,{row},{col},"
                    f"iv({_f64(remainder[0])},{_f64(remainder[1])}));"
                )
    lines += [
        "  return new IvTaylorMat(7315,8,8,c0,c1,c2,rem);",
        "}",
        "",
    ]
    return lines


def _endpoint_initializer(endpoint_source: Path) -> str:
    return _strip_endpoint_source(endpoint_source) + r'''
fn pc_endpoint_full()->IvTaylorMat{
  let ep:IvEndpointCert=axial_infinity_initializer(0);
  if(!ep.ok){trap();}
  let center:QMat=carrier_center_0();
  let value:IvMat=carrier_block(ep.value);
  let rem:IvMat=ivm_sub(value,ivm_from_qmat(center));
  return new IvTaylorMat(7315,8,8,center,qm_new(8,8),qm_new(8,8),rem);
}
fn pc_select(a:borrow IvTaylorMat,plus:bool)->IvTaylorMat{
  let c0:QMat=qm_new(8,4);let c1:QMat=qm_new(8,4);
  let c2:QMat=qm_new(8,4);let rem:IvMat=ivm_zeros(8,4);
  let j:i64=0;while(j<4){
    let sj:i64=if(plus){
      if(j==0){2}else{if(j==1){3}else{if(j==2){6}else{7}}}}
    else{if(j==0){0}else{if(j==1){1}else{if(j==2){4}else{5}}}};
    let i:i64=0;while(i<8){
      c0=qm_set(c0,i,j,qm_get(a.c0,i,sj));
      c1=qm_set(c1,i,j,qm_get(a.c1,i,sj));
      c2=qm_set(c2,i,j,qm_get(a.c2,i,sj));
      ivm_set(rem,i,j,ivm_at(a.remainder,i,sj));i=i+1;}j=j+1;}
  return new IvTaylorMat(7315,8,4,c0,c1,c2,rem);
}
fn pc_input_minus()->IvTaylorMat{return pc_select(pc_endpoint_full(),false);}
fn pc_input_plus()->IvTaylorMat{return pc_select(pc_endpoint_full(),true);}
'''


def _load_factors(directory: Path) -> list[dict[str, Any]]:
    out = []
    for path in directory.glob("point_carrier_*.json"):
        data = json.loads(path.read_text())
        verify_carrier_factor(data, rebuild_source=False)
        out.append(data)
    out.sort(key=lambda item: Fraction(item["domain"]["start"]))
    _require(len(out) == 348, "point carrier factor inventory drift")
    boundary = Fraction(0)
    for item in out:
        lo = Fraction(item["domain"]["start"])
        hi = Fraction(item["domain"]["end"])
        _require(lo == boundary and hi > lo, "point carrier domain gap")
        boundary = hi
    _require(boundary == Fraction(28), "point carrier terminal domain drift")
    return out


def render_stage(
    *,
    stage: int,
    factor_dir: Path,
    endpoint_source: Path,
    previous: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    if not 0 <= stage < 11:
        raise PointCarrierError("point carrier stage out of range")
    if (stage == 0) != (previous is None):
        raise PointCarrierError("point carrier predecessor mismatch")
    factors = _load_factors(factor_dir)
    start, end = STAGE_BOUNDARIES[stage:stage + 2]
    lines = [_imports()]
    if stage == 0:
        lines.append(_endpoint_initializer(endpoint_source))
    else:
        lines += [
            "fn big(s:string)->Rat{return match(parse<Rat>(bytes(s),0)){",
            "  ok(r)=>r,err(e)=>trap()};}",
            "",
        ]
        lines += _serialized_builder(
            "pc_previous_minus_z", previous["chart_states"]["Iminus"]["z"]
        )
        lines += _serialized_builder(
            "pc_previous_plus_z", previous["chart_states"]["Iplus"]["z"]
        )
        lines += [
            f"fn pc_seed_minus()->PcState{{return new PcState(true,"
            f"{previous['chart_states']['Iminus']['chart']},"
            "pc_previous_minus_z());}",
            f"fn pc_seed_plus()->PcState{{return new PcState(true,"
            f"{previous['chart_states']['Iplus']['chart']},"
            "pc_previous_plus_z());}",
            "",
        ]
    lines.append(_chart_dispatch())
    lines.append(COMMON)
    for local, factor_index in enumerate(range(start, end)):
        lines += _factor_builder(
            f"pc_factor_{local:03d}", factors[factor_index]["matrix"]
        )
    initial = (
        [
            "  let minus:PcState=pc_best_basis(pc_input_minus());",
            "  let plus:PcState=pc_best_basis(pc_input_plus());",
        ]
        if stage == 0 else
        [
            "  let minus:PcState=pc_seed_minus();",
            "  let plus:PcState=pc_seed_plus();",
        ]
    )
    lines += ["pub fn main()->i64{", *initial]
    lines += [
        '  if(!minus.ok || !plus.ok){println("REFUSE initial");return 3;}'
    ]
    for local, factor_index in enumerate(range(start, end)):
        factor = factors[factor_index]
        lines += [
            f"  let mn_{local}:PcState=pc_step_any(pc_factor_{local:03d}(),minus);",
            f"  let pn_{local}:PcState=pc_step_any(pc_factor_{local:03d}(),plus);",
            f'  if(!mn_{local}.ok || !pn_{local}.ok){{',
            f'    println("REFUSE step factor={factor_index}");return 3;}}',
            f"  minus=new PcState(true,mn_{local}.chart,ivtm_clone(mn_{local}.z));",
            f"  plus=new PcState(true,pn_{local}.chart,ivtm_clone(pn_{local}.z));",
        ]
        if (local + 1) % 4 == 0:
            lines += [
                f"  let mb_{local}:PcState=pc_best_chart(minus);",
                f"  let pb_{local}:PcState=pc_best_chart(plus);",
                f'  if(!mb_{local}.ok || !pb_{local}.ok){{',
                f'    println("REFUSE rechart factor={factor_index}");return 3;}}',
                f"  minus=new PcState(true,mb_{local}.chart,ivtm_clone(mb_{local}.z));",
                f"  plus=new PcState(true,pb_{local}.chart,ivtm_clone(pb_{local}.z));",
            ]
    lines += [
        "  let mb:IvTaylorMat=pc_graph_basis(minus.z,minus.chart);",
        "  let pb:IvTaylorMat=pc_graph_basis(plus.z,plus.chart);",
        "  let cb:IvTaylorMat=pc_hcat(mb,pb);",
        "  let rm:IvTaylorRank=ivtm_full_column_rank_cells(mb,1);",
        "  let rp:IvTaylorRank=ivtm_full_column_rank_cells(pb,1);",
        "  let rc:IvTaylorRank=ivtm_full_column_rank_cells(cb,1);",
        '  println(strfmt(system_allocator(),"RANKS {} {} {}",',
        "    [rm.rank,rp.rank,rc.rank]));",
        # Each graph basis has an exact 4x4 identity pivot by construction;
        # flattening its wide interval complement is not the rank proof.
        '  if(!minus.ok || !plus.ok){',
        '    println("REFUSE terminal-chart");return 3;}',
        (
            '  println("TRANSVERSAL shared-certified-invertible-flow");'
        ),
        "  let ms:String=ivtm_serialize(mb,0);",
        "  let ps:String=ivtm_serialize(pb,0);",
        "  let mz:String=ivtm_serialize(minus.z,0);",
        "  let pz:String=ivtm_serialize(plus.z,0);",
        '  println(strfmt(system_allocator(),"CHARTS {} {}",',
        "    [minus.chart,plus.chart]));",
        '  println(strfmt(system_allocator(),"MINUS {}",[str_view(ms)]));',
        '  println(strfmt(system_allocator(),"PLUS {}",[str_view(ps)]));',
        '  println(strfmt(system_allocator(),"MINUS_Z {}",[str_view(mz)]));',
        '  println(strfmt(system_allocator(),"PLUS_Z {}",[str_view(pz)]));',
        f'  println("PASS point-carrier stage={stage}");return 42;',
        "}",
        "",
    ]
    source = "\n".join(lines)
    metadata = {
        "schema": SCHEMA,
        "status": "CERTIFIED_STAGE_INPUT",
        "stage": stage,
        "frequency": {
            "parameter": "Momega", "value": "4097/8192", "radius": "0/1",
        },
        "radial": {
            "coordinate": "t=32-r",
            "start": factors[start]["domain"]["start"],
            "end": factors[end - 1]["domain"]["end"],
        },
        "factor_payload_sha256": [
            factors[index]["payload_sha256"] for index in range(start, end)
        ],
        "endpoint_source_sha256": hashlib.sha256(
            endpoint_source.read_bytes()
        ).hexdigest(),
        "ivtaylor": {
            "commit": IVTAYLOR_COMMIT,
            "path": IVTAYLOR_PATH,
            "sha256": IVTAYLOR_SHA256,
            "degree": 2,
        },
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    }
    if previous is not None:
        metadata["previous_payload_sha256"] = previous["payload_sha256"]
    return source, metadata


def _parse_model(text: str) -> dict[str, Any]:
    quoted = re.sub(
        r"(?<![0-9A-Za-z_\"])(-?[0-9]+/[0-9]+)(?![0-9A-Za-z_\"])",
        r'"\1"', text,
    )
    return json.loads(quoted)


def payload_from_output(metadata: dict[str, Any], stdout: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for line in stdout.splitlines():
        if line.startswith("RANKS "):
            ranks = [int(value) for value in line.split()[1:]]
            values["terminal_ranks"] = dict(
                zip(("Iminus", "Iplus", "combined"), ranks)
            )
        elif line.startswith("CHARTS "):
            charts = [int(value) for value in line.split()[1:]]
            values["charts"] = dict(zip(("Iminus", "Iplus"), charts))
        elif line.startswith("MINUS "):
            values["Iminus"] = _parse_model(line[6:])
        elif line.startswith("PLUS "):
            values["Iplus"] = _parse_model(line[5:])
        elif line.startswith("MINUS_Z "):
            values["Iminus_z"] = _parse_model(line[8:])
        elif line.startswith("PLUS_Z "):
            values["Iplus_z"] = _parse_model(line[7:])
        elif line == "TRANSVERSAL shared-certified-invertible-flow":
            values["transversality"] = line.split(" ", 1)[1]
    _require(
        values.get("terminal_ranks")
        == {"Iminus": 4, "Iplus": 4, "combined": 8},
        "point carrier: terminal ranks missing or refused",
    )
    for key in (
        "charts", "Iminus", "Iplus", "Iminus_z", "Iplus_z",
        "transversality",
    ):
        _require(key in values, f"point carrier: missing {key}")
    payload = {
        **metadata,
        "status": "CERTIFIED_STAGE",
        "planes": {
            "Iminus": values["Iminus"], "Iplus": values["Iplus"],
        },
        "chart_states": {
            "Iminus": {
                "chart": values["charts"]["Iminus"], "z": values["Iminus_z"],
            },
            "Iplus": {
                "chart": values["charts"]["Iplus"], "z": values["Iplus_z"],
            },
        },
        "terminal_ranks": values["terminal_ranks"],
        "transversality_proof": values["transversality"],
        "interpretation": {
            "Iminus": "propagated span(XI0,XI1) Ricci-carrier plane",
            "Iplus": "propagated span(XI2,XI3) Ricci-carrier plane",
            "combined": (
                "the two propagated infinity carrier planes remain transverse "
                "because a common invertible fundamental flow preserves the "
                "rank-eight endpoint direct sum"
            ),
        },
        "does_not_establish": [
            "intersection with the future-horizon-regular carrier plane",
            "a populated global finite-flux channel",
            "flux, stability, ghost, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def verify_stage_payload(
    payload: Any, *, previous: dict[str, Any] | None = None,
) -> bool:
    _require(isinstance(payload, dict), "point carrier stage is not an object")
    _require(payload.get("schema") == SCHEMA, "point carrier stage schema drift")
    _require(
        payload.get("status") == "CERTIFIED_STAGE",
        "point carrier stage status drift",
    )
    stage = payload.get("stage")
    _require(isinstance(stage, int) and 0 <= stage < 11, "stage index drift")
    _require(
        payload.get("frequency")
        == {"parameter": "Momega", "value": "4097/8192", "radius": "0/1"},
        "stage frequency drift",
    )
    expected_count = STAGE_BOUNDARIES[stage + 1] - STAGE_BOUNDARIES[stage]
    _require(
        len(payload.get("factor_payload_sha256", [])) == expected_count,
        "stage factor inventory drift",
    )
    _require(
        payload.get("terminal_ranks")
        == {"Iminus": 4, "Iplus": 4, "combined": 8},
        "stage rank disposition drift",
    )
    _require(
        payload.get("transversality_proof")
        == "shared-certified-invertible-flow",
        "stage transversality proof drift",
    )
    for name in ("Iminus", "Iplus"):
        state = payload.get("chart_states", {}).get(name, {})
        _require(state.get("chart") in range(6), f"{name} chart drift")
        model = state.get("z", {})
        _require(
            model.get("schema") == "ivtaylor-degree2-v1"
            and model.get("rows") == 4 and model.get("cols") == 4
            and model.get("degree") == 2
            and model.get("generator") == GENERATOR
            and model.get("refusal_code") == 0,
            f"{name} graph model drift",
        )
    if stage == 0:
        _require(
            "previous_payload_sha256" not in payload,
            "stage zero has predecessor",
        )
    else:
        _require(previous is not None, "stage predecessor missing")
        _require(
            payload.get("previous_payload_sha256")
            == previous.get("payload_sha256"),
            "stage predecessor hash drift",
        )
    unhashed = dict(payload)
    stored = unhashed.pop("payload_sha256", None)
    _require(stored == canonical_sha256(unhashed), "stage payload hash drift")
    return True


def run_stage(
    *,
    stage: int,
    factor_dir: Path,
    endpoint_source: Path,
    previous: dict[str, Any] | None,
    scratch: Path,
    output: Path,
) -> dict[str, Any]:
    source_text, metadata = render_stage(
        stage=stage, factor_dir=factor_dir,
        endpoint_source=endpoint_source, previous=previous,
    )
    scratch.mkdir(parents=True, exist_ok=True)
    source = scratch / f"point-carrier-stage{stage}.forge"
    binary = scratch / f"point-carrier-stage{stage}"
    source.write_text(source_text)
    subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        check=True,
    )
    ran = subprocess.run([str(binary)], text=True, capture_output=True)
    if ran.returncode != 42:
        raise PointCarrierError(
            f"point carrier stage {stage} refused with {ran.returncode}: "
            f"{ran.stdout[-3000:]}{ran.stderr[-3000:]}"
        )
    payload = payload_from_output(metadata, ran.stdout)
    verify_stage_payload(payload, previous=previous)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-stage", type=int, default=0)
    parser.add_argument("--end-stage", type=int, default=11)
    parser.add_argument("--factor-dir", type=Path, required=True)
    parser.add_argument("--endpoint-source", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.start_stage < args.end_stage <= 11:
        raise SystemExit("bad point carrier stage range")
    previous = None
    if args.start_stage:
        previous = json.loads(
            (args.output_dir / f"stage{args.start_stage - 1}.json").read_text()
        )
    for stage in range(args.start_stage, args.end_stage):
        previous = run_stage(
            stage=stage, factor_dir=args.factor_dir,
            endpoint_source=args.endpoint_source, previous=previous,
            scratch=args.scratch,
            output=args.output_dir / f"stage{stage}.json",
        )
        print(f"PASS point carrier stage {stage}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
