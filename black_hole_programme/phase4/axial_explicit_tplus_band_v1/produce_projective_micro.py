#!/usr/bin/env python3
"""Certify one outgoing microfactor in interaction/projective variables.

The nonlinear chart operations are applied to the near-identity local
microfactor, not to the already-wide transported endpoint columns.  The
certified microfactor is then applied to the sealed outgoing checkpoint and
audited against the direct sixteen-state boundary transport.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import time
from fractions import Fraction
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1 import (
    produce as engine,
)
from black_hole_programme.phase4.axial_explicit_tplus_band_v1 import (
    produce as predecessor,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = HERE / "interaction_successor_checkpoint.json"
CHECKPOINT = HERE / "projective_micro_checkpoint.json"
MANIFEST = HERE / "projective_micro_manifest.json"
CERTIFICATE = HERE / "projective_micro_certificate.json"
RECEIPT = HERE / "projective_micro_receipt.json"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

CANDIDATE = {
    "choice": 0,
    "name": "PROJECTIVE_INTERACTION_MICRO",
    "center": "7789/256",
    "step": "-1/128",
    "radius": "1/256",
    "denominator": 128,
    "order": 32,
    "final_radius": "1947/64",
}

SUPPORT = r'''
fn pi_block(a:borrow IvTaylor4Mat,ro:i64,co:i64)->IvTaylor4Mat{
  let z:IvTaylor4Mat=sj_zero(4,4);let i:i64=0;while(i<4){
    let si:i64=if(i<2){ro+i}else{ro+i-2+4};
    let j:i64=0;while(j<4){
      let sj:i64=if(j<2){co+j}else{co+j-2+4};
      z=sj_put(z,i,j,sj_scalar(a,si,sj));j=j+1;}i=i+1;}return z;
}
fn pi_put_block(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat,
ro:i64,co:i64)->IvTaylor4Mat{
  let z:IvTaylor4Mat=ivtm4_clone(a);let i:i64=0;while(i<4){
    let ti:i64=if(i<2){ro+i}else{ro+i-2+4};
    let j:i64=0;while(j<4){
      let tj:i64=if(j<2){co+j}else{co+j-2+4};
      z=sj_put(z,ti,tj,sj_scalar(b,i,j));j=j+1;}i=i+1;}return z;
}
fn pi_cx_entry(a:borrow IvTaylor4Mat,i:i64,j:i64)->IvTaylor4Mat{
  let z:IvTaylor4Mat=sj_zero(2,2);
  z=sj_put(z,0,0,sj_scalar(a,i,j));
  z=sj_put(z,0,1,sj_scalar(a,i,j+2));
  z=sj_put(z,1,0,sj_scalar(a,i+2,j));
  z=sj_put(z,1,1,sj_scalar(a,i+2,j+2));
  return z;
}
fn pi_put_cx(a:borrow IvTaylor4Mat,z:borrow IvTaylor4Mat,
i:i64,j:i64)->IvTaylor4Mat{
  let out:IvTaylor4Mat=ivtm4_clone(a);
  out=sj_put(out,i,j,sj_scalar(z,0,0));
  out=sj_put(out,i,j+2,sj_scalar(z,0,1));
  out=sj_put(out,i+2,j,sj_scalar(z,1,0));
  out=sj_put(out,i+2,j+2,sj_scalar(z,1,1));
  return out;
}
fn pi_inv(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  return sj_expect(ivtm4_solve_left(a,ivtm4_identity(7315,a.rows)));
}
fn pi_det(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let a00:IvTaylor4Mat=pi_cx_entry(a,0,0);
  let a01:IvTaylor4Mat=pi_cx_entry(a,0,1);
  let a10:IvTaylor4Mat=pi_cx_entry(a,1,0);
  let a11:IvTaylor4Mat=pi_cx_entry(a,1,1);
  return sc_add(sj_mul(a00,a11),
    sc_scale(sj_mul(a01,a10),big("-1/1")));
}
fn pi_norm2_lo(a:borrow IvTaylor4Mat)->f64{
  let re:IvTaylor4Mat=sj_scalar(a,0,0);
  let im:IvTaylor4Mat=sj_scalar(a,1,0);
  let n:IvTaylor4Mat=sc_add(sj_mul(re,re),sj_mul(im,im));
  let h:IvMat=match(ivtm4_hull_checked(n)){some(x)=>x,none=>{return -1.0;}};
  return ivm_at(h,0,0).lo;
}
fn pi_max_width(a:borrow IvTaylor4Mat,b:borrow IvTaylor4Mat)->f64{
  let x:f64=sj_width(match(ivtm4_hull_checked(a)){some(z)=>z,none=>{return -1.0;}});
  let y:f64=sj_width(match(ivtm4_hull_checked(b)){some(z)=>z,none=>{return -1.0;}});
  return if(x>y){x}else{y};
}
fn pi_trace_block(a:borrow IvTaylor4Mat,offset:i64)->IvTaylor4Mat{
  let x:IvTaylor4Mat=pi_block(a,offset,offset);
  return sc_add(pi_cx_entry(x,0,0),pi_cx_entry(x,1,1));
}
fn pi_chart(a:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let a00:IvTaylor4Mat=pi_cx_entry(a,0,0);
  let a10:IvTaylor4Mat=pi_cx_entry(a,1,0);
  let a01:IvTaylor4Mat=pi_cx_entry(a,0,1);
  let a11:IvTaylor4Mat=pi_cx_entry(a,1,1);
  let q:IvTaylor4Mat=sj_mul(a10,pi_inv(a00));
  let p:IvTaylor4Mat=sj_mul(a01,pi_inv(a11));
  let z:IvTaylor4Mat=sj_zero(4,4);
  z=pi_put_cx(z,a00,0,0);z=pi_put_cx(z,sj_mul(q,a00),1,0);
  z=pi_put_cx(z,sj_mul(p,a11),0,1);z=pi_put_cx(z,a11,1,1);
  return z;
}
fn pi_chart_tangent(a:borrow IvTaylor4Mat,
at:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let a00:IvTaylor4Mat=pi_cx_entry(a,0,0);
  let a10:IvTaylor4Mat=pi_cx_entry(a,1,0);
  let a01:IvTaylor4Mat=pi_cx_entry(a,0,1);
  let a11:IvTaylor4Mat=pi_cx_entry(a,1,1);
  let t00:IvTaylor4Mat=pi_cx_entry(at,0,0);
  let t10:IvTaylor4Mat=pi_cx_entry(at,1,0);
  let t01:IvTaylor4Mat=pi_cx_entry(at,0,1);
  let t11:IvTaylor4Mat=pi_cx_entry(at,1,1);
  let i00:IvTaylor4Mat=pi_inv(a00);let i11:IvTaylor4Mat=pi_inv(a11);
  let q:IvTaylor4Mat=sj_mul(a10,i00);
  let p:IvTaylor4Mat=sj_mul(a01,i11);
  let qt:IvTaylor4Mat=sj_mul(
    sc_add(t10,sc_scale(sj_mul(q,t00),big("-1/1"))),i00);
  let pt:IvTaylor4Mat=sj_mul(
    sc_add(t01,sc_scale(sj_mul(p,t11),big("-1/1"))),i11);
  let z:IvTaylor4Mat=sj_zero(4,4);
  z=pi_put_cx(z,t00,0,0);
  z=pi_put_cx(z,sc_add(sj_mul(qt,a00),sj_mul(q,t00)),1,0);
  z=pi_put_cx(z,sc_add(sj_mul(pt,a11),sj_mul(p,t11)),0,1);
  z=pi_put_cx(z,t11,1,1);
  return z;
}
fn pi_chart_width(a:borrow IvTaylor4Mat,
at:borrow IvTaylor4Mat)->f64{
  let a00:IvTaylor4Mat=pi_cx_entry(a,0,0);
  let a10:IvTaylor4Mat=pi_cx_entry(a,1,0);
  let a01:IvTaylor4Mat=pi_cx_entry(a,0,1);
  let a11:IvTaylor4Mat=pi_cx_entry(a,1,1);
  let t00:IvTaylor4Mat=pi_cx_entry(at,0,0);
  let t10:IvTaylor4Mat=pi_cx_entry(at,1,0);
  let t01:IvTaylor4Mat=pi_cx_entry(at,0,1);
  let t11:IvTaylor4Mat=pi_cx_entry(at,1,1);
  let i00:IvTaylor4Mat=pi_inv(a00);let i11:IvTaylor4Mat=pi_inv(a11);
  let q:IvTaylor4Mat=sj_mul(a10,i00);
  let p:IvTaylor4Mat=sj_mul(a01,i11);
  let qt:IvTaylor4Mat=sj_mul(
    sc_add(t10,sc_scale(sj_mul(q,t00),big("-1/1"))),i00);
  let pt:IvTaylor4Mat=sj_mul(
    sc_add(t01,sc_scale(sj_mul(p,t11),big("-1/1"))),i11);
  let l0:IvTaylor4Mat=sj_mul(i00,t00);
  let l1:IvTaylor4Mat=sj_mul(i11,t11);
  let w:f64=pi_max_width(q,p);
  let v:f64=pi_max_width(qt,pt);if(v>w){w=v;}
  let u:f64=pi_max_width(l0,l1);if(u>w){w=u;}return w;
}
'''

MAIN = r'''
pub fn main()->i64{
  let w:IvTaylor4Mat=sj_frequency();
  let base:IvTaylor4Mat=initial_base();
  let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big("1/512"));
  let seed:IvTaylor4Mat=bc_stack(tangent_n,base);
  let center:Rat=big("7789/256");let h:Rat=big("-1/128");
  let radius:Rat=big("1/256");let order:i64=32;
  let models:ScModels=sc_build_models(w,bc_radius(center,radius));
  let mh:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("PROJECTIVE_MICRO status=REFUSED code=MODEL");
      return 3;}};
  let sh:IvMat=match(ivtm4_hull_checked(seed)){
    some(x)=>x,none=>{println("PROJECTIVE_MICRO status=REFUSED code=SEED");
      return 3;}};
  let op_tail:f64=sc_tail(sc_norm(mh)/128.0,order+1);
  let state_tail:f64=op_tail*sc_norm(sh);
  if(op_tail<0.0||state_tail<0.0||!f64_is_finite(op_tail)||
     !f64_is_finite(state_tail)||state_tail>=0.5){
    println(strfmt(system_allocator(),
      "PROJECTIVE_MICRO status=REFUSED code=TAIL op={} state={}",
      [op_tail,state_tail]));return 3;}

  let dual0:ScModels=sc_dual_series(models.base,models.tangent,h,order);
  let F:IvTaylor4Mat=sc_pad(dual0.base,op_tail);
  let Ft:IvTaylor4Mat=sc_pad(dual0.tangent,op_tail);
  let P:IvTaylor4Mat=pi_block(F,0,0);
  let Q:IvTaylor4Mat=pi_block(F,0,2);
  let R:IvTaylor4Mat=pi_block(F,2,2);
  let Pt:IvTaylor4Mat=pi_block(Ft,0,0);
  let Qt:IvTaylor4Mat=pi_block(Ft,0,2);
  let Pinv:IvTaylor4Mat=pi_inv(P);
  let J:IvTaylor4Mat=sj_mul(Pinv,Pt);
  let K:IvTaylor4Mat=sj_mul(Pinv,Q);
  let drive:IvTaylor4Mat=sj_mul(Pinv,Q);
  let dotK:IvTaylor4Mat=sc_add(
    sj_mul(Pinv,Qt),sc_scale(sj_mul(J,drive),big("-1/1")));

  let Frec:IvTaylor4Mat=sj_zero(8,8);
  Frec=pi_put_block(Frec,P,0,0);
  Frec=pi_put_block(Frec,sj_mul(P,K),0,2);
  Frec=pi_put_block(Frec,R,2,2);
  let Ftrec:IvTaylor4Mat=sj_zero(8,8);
  Ftrec=pi_put_block(Ftrec,sj_mul(P,J),0,0);
  Ftrec=pi_put_block(Ftrec,
    sj_mul(P,sc_add(sj_mul(J,K),dotK)),0,2);
  let interaction_overlap:bool=
    sc_contains_zero(F,Frec)&&sc_contains_zero(Ft,Ftrec);

  let Pchart:IvTaylor4Mat=pi_chart(P);
  let Ptchart:IvTaylor4Mat=pi_chart_tangent(P,Pt);
  let Rchart:IvTaylor4Mat=pi_chart(R);
  let projective_overlap:bool=
    sc_contains_zero(P,Pchart)&&sc_contains_zero(Pt,Ptchart)&&
    sc_contains_zero(R,Rchart);

  let detP:IvTaylor4Mat=pi_det(P);let detR:IvTaylor4Mat=pi_det(R);
  let trP:IvTaylor4Mat=pi_trace_block(models.base,0);
  let trR:IvTaylor4Mat=pi_trace_block(models.base,2);
  let trPh:IvMat=match(ivtm4_hull_checked(trP)){some(x)=>x,none=>{trap();}};
  let trRh:IvMat=match(ivtm4_hull_checked(trR)){some(x)=>x,none=>{trap();}};
  let tw2:f64=sc_tail(sc_norm(trPh)/128.0,order+1);
  let tw1:f64=sc_tail(sc_norm(trRh)/128.0,order+1);
  let w2:IvTaylor4Mat=sc_pad(sc_series(trP,h,order),tw2);
  let w1:IvTaylor4Mat=sc_pad(sc_series(trR,h,order),tw1);
  let wronskian2:bool=sc_contains_zero(detP,w2);
  let wronskian1:bool=sc_contains_zero(detR,w1);

  let p00:f64=pi_norm2_lo(pi_cx_entry(P,0,0));
  let p11:f64=pi_norm2_lo(pi_cx_entry(P,1,1));
  let r00:f64=pi_norm2_lo(pi_cx_entry(R,0,0));
  let r11:f64=pi_norm2_lo(pi_cx_entry(R,1,1));
  let det_margin:f64=pi_norm2_lo(detP);
  let interaction_width:f64=pi_max_width(J,K);
  let dotk_width:f64=sj_width(match(ivtm4_hull_checked(dotK)){
    some(x)=>x,none=>{return 3;}});
  if(dotk_width>interaction_width){interaction_width=dotk_width;}
  let chart_width:f64=pi_chart_width(P,Pt);
  let rchart_width:f64=pi_max_width(
    sj_mul(pi_cx_entry(R,1,0),pi_inv(pi_cx_entry(R,0,0))),
    sj_mul(pi_cx_entry(R,0,1),pi_inv(pi_cx_entry(R,1,1))));
  if(rchart_width>chart_width){chart_width=rchart_width;}
  let wronskian_width:f64=pi_max_width(detP,detR);
  if(!interaction_overlap||!projective_overlap||!wronskian2||!wronskian1||
     p00<=0.0||p11<=0.0||r00<=0.0||r11<=0.0||det_margin<=0.0||
     !f64_is_finite(interaction_width)||!f64_is_finite(chart_width)){
    println(strfmt(system_allocator(),
      "PROJECTIVE_MICRO status=REFUSED code=GATE interaction={} projective={} w2={} w1={} p00={} p11={} r00={} r11={} det={}",
      [interaction_overlap,projective_overlap,wronskian2,wronskian1,
       p00,p11,r00,r11,det_margin]));return 3;}

  let base_out:IvTaylor4Mat=sj_mul(F,base);
  let tangent_out:IvTaylor4Mat=sc_add(
    sj_mul(Ft,base),sj_mul(F,tangent_n));
  let jet:IvTaylor4Mat=bc_stack(tangent_out,base_out);
  let direct:IvTaylor4Mat=sj_mul(sc_series(models.direct,h,order),seed);
  let jp:IvTaylor4Mat=sc_pad(jet,state_tail);
  let dp:IvTaylor4Mat=sc_pad(direct,state_tail);
  let coefficients:bool=sj_coefficients_equal(jp,dp);
  let containment:bool=sc_contains_zero(jp,dp);
  if(!coefficients||!containment){
    println("PROJECTIVE_MICRO status=REFUSED code=DIRECT");return 3;}
  let tangent_final:IvTaylor4Mat=sc_scale(
    bc_unstack_tangent(jp),big("512"));
  let base_final:IvTaylor4Mat=bc_unstack_base(jp);
  let width:f64=sj_width(match(ivtm4_hull_checked(jp)){
    some(x)=>x,none=>{println("PROJECTIVE_MICRO status=REFUSED code=OUTPUT");
      return 3;}});
  if(!f64_is_finite(width)||width>=10.0){
    println(strfmt(system_allocator(),
      "PROJECTIVE_MICRO status=REFUSED code=WIDTH width={}",[width]));
    return 3;}
  sr_emit("SUCCESSOR_BASE",base_final);
  sr_emit("SUCCESSOR_TANGENT",tangent_final);
  println(strfmt(system_allocator(),
    "PROJECTIVE_GATES status=PASS interaction={} projective={} wronskian2={} wronskian1={} pinv_margin={} p00={} p11={} r00={} r11={} interaction_width={} chart_width={} wronskian_width={} op_tail={}",
    [interaction_overlap,projective_overlap,wronskian2,wronskian1,
     det_margin,p00,p11,r00,r11,interaction_width,chart_width,
     wronskian_width,op_tail]));
  println(strfmt(system_allocator(),
    "BPLUS4_CHUNK status=PASS choice=0 order=32 tail={} width={} coefficients={} containment={}",
    [state_tail,width,coefficients,containment]));
  return 0;
}
'''


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


def rendered(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def exact_hull(model: dict, row: int, col: int) -> tuple[Fraction, Fraction]:
    coefficients = [
        Fraction(model["coefficients"][degree][row][col])
        for degree in range(5)
    ]
    radius = sum(abs(value) for value in coefficients[1:])
    lo_bits, hi_bits = model["remainder_bits"][row][col]
    lo = Fraction.from_float(struct.unpack(">d", bytes.fromhex(lo_bits))[0])
    hi = Fraction.from_float(struct.unpack(">d", bytes.fromhex(hi_bits))[0])
    return coefficients[0] - radius + lo, coefficients[0] + radius + hi


def accumulated_pivot_diagnostic(checkpoint: dict) -> dict:
    model = checkpoint["payload"]["base"]

    def pivot(name: str, real_row: int, imag_row: int, col: int) -> dict:
        re_lo, re_hi = exact_hull(model, real_row, col)
        im_lo, im_hi = exact_hull(model, imag_row, col)
        excludes = re_lo > 0 or re_hi < 0 or im_lo > 0 or im_hi < 0
        return {
            "name": name,
            "real_hull": [float(re_lo), float(re_hi)],
            "imaginary_hull": [float(im_lo), float(im_hi)],
            "rectangular_enclosure_excludes_zero": excludes,
        }

    return {
        "spin_two_R_column": pivot("Y0", 0, 4, 0),
        "spin_one_S_column": pivot("Z0", 2, 6, 1),
        "interpretation": (
            "failure to exclude zero is an enclosure obstruction only; it "
            "does not assert that the physical endpoint line is singular"
        ),
    }


def parse_gates(output: str) -> dict:
    pattern = re.compile(
        r"PROJECTIVE_GATES status=PASS "
        r"interaction=(?P<interaction>true|false) "
        r"projective=(?P<projective>true|false) "
        r"wronskian2=(?P<wronskian2>true|false) "
        r"wronskian1=(?P<wronskian1>true|false) "
        r"pinv_margin=(?P<pinv_margin>[-+0-9.eE]+) "
        r"p00=(?P<p00>[-+0-9.eE]+) "
        r"p11=(?P<p11>[-+0-9.eE]+) "
        r"r00=(?P<r00>[-+0-9.eE]+) "
        r"r11=(?P<r11>[-+0-9.eE]+) "
        r"interaction_width=(?P<interaction_width>[-+0-9.eE]+) "
        r"chart_width=(?P<chart_width>[-+0-9.eE]+) "
        r"wronskian_width=(?P<wronskian_width>[-+0-9.eE]+) "
        r"op_tail=(?P<op_tail>[-+0-9.eE]+)"
    )
    match = pattern.search(output)
    if match is None:
        refused = re.search(r"PROJECTIVE_MICRO status=REFUSED.*", output)
        raise RuntimeError(refused.group(0) if refused else "unparsed projective output")
    result: dict[str, object] = match.groupdict()
    for key in ("interaction", "projective", "wronskian2", "wronskian1"):
        result[key] = result[key] == "true"
    return result


def reproduce() -> tuple[dict, dict]:
    predecessor.configure()
    input_document = json.loads(INPUT.read_text())
    if canonical_sha256(input_document["payload"]) != input_document["payload_sha256"]:
        raise RuntimeError("input checkpoint payload drift")
    engine.MAIN = SUPPORT + "\n" + MAIN
    engine.CANDIDATES = [CANDIDATE]
    source = engine.source_text(input_document["payload"])
    source_sha = sha256_bytes(source.encode())
    chunk_descriptor = {
        "input_payload_sha256": input_document["payload_sha256"],
        "source_sha256": source_sha,
        "candidate": CANDIDATE,
        "shared_generator": 7315,
        "interaction_picture": True,
        "projective_multiplicative_charts": True,
        "wronskian_gate": True,
        "boundary_direct_gate": True,
    }
    chunk_id = canonical_sha256(chunk_descriptor)
    source_path = Path(f"/tmp/axial-tplus-projective-{chunk_id[:16]}.forge")
    binary = Path(f"/tmp/axial-tplus-projective-{chunk_id[:16]}")
    source_path.write_text(source)
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    started = time.perf_counter()
    compiled = engine.run(
        [str(jet.FORGE), "-o", str(binary), str(source_path)], env, 20.0
    )
    executed = (
        engine.run([str(binary)], env, 42.0)
        if compiled["exit_code"] == 0
        else {"exit_code": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    elapsed = time.perf_counter() - started
    if compiled["exit_code"] != 0 or executed["exit_code"] != 0:
        raise RuntimeError(
            f"projective micro failed: compile={compiled['exit_code']} "
            f"run={executed['exit_code']} output={executed['output'][-1200:]}"
        )
    if elapsed > 60.0:
        raise RuntimeError(f"projective micro exceeded 60 seconds: {elapsed}")
    summary = engine.parse_summary(executed["output"])
    gates = parse_gates(executed["output"])
    base = engine.render.parse_model(executed["output"], "SUCCESSOR_BASE")
    tangent = engine.render.parse_model(executed["output"], "SUCCESSOR_TANGENT")
    payload = {
        **input_document["payload"],
        "schema": "phase4-axial-tplus-projective-micro-payload-v1",
        "chunk_id": chunk_id,
        "input_payload_sha256": input_document["payload_sha256"],
        "start_radius": input_document["payload"]["radius"],
        "radius": CANDIDATE["final_radius"],
        "base": base,
        "tangent": tangent,
    }
    checkpoint = {
        "schema": "phase4-axial-tplus-projective-micro-checkpoint-v1",
        "payload": payload,
        "payload_sha256": canonical_sha256(payload),
    }
    manifest = {
        "schema": "phase4-axial-tplus-projective-micro-run-v1",
        "chunk_descriptor": chunk_descriptor,
        "chunk_id": chunk_id,
        "source_sha256": source_sha,
        "source_ephemeral_path": str(source_path),
        "binary_ephemeral_path": str(binary),
        "compile": {
            "exit_code": compiled["exit_code"],
            "elapsed_seconds": compiled["elapsed_seconds"],
            "output_sha256": sha256_bytes(compiled["output"].encode()),
        },
        "run": {
            "exit_code": executed["exit_code"],
            "elapsed_seconds": executed["elapsed_seconds"],
            "raw_output_sha256": sha256_bytes(executed["output"].encode()),
            "summary": summary,
            "projective_gates": gates,
            "successor_base_sha256": canonical_sha256(base),
            "successor_tangent_sha256": canonical_sha256(tangent),
        },
        "total_elapsed_seconds": elapsed,
        "under_sixty_seconds": elapsed <= 60.0,
        "checkpoint_payload_sha256": checkpoint["payload_sha256"],
    }
    CHECKPOINT.write_text(rendered(checkpoint))
    MANIFEST.write_text(rendered(manifest))
    return checkpoint, manifest


def build_certificate(checkpoint: dict, manifest: dict) -> dict:
    summary = manifest["run"]["summary"]
    gates = manifest["run"]["projective_gates"]
    passed = (
        manifest["under_sixty_seconds"]
        and all(gates[key] for key in ("interaction", "projective", "wronskian2", "wronskian1"))
        and all(float(gates[key]) > 0.0 for key in ("pinv_margin", "p00", "p11", "r00", "r11"))
        and summary["coefficients"]
        and summary["containment"]
        and float(summary["tail"]) < 0.5
        and float(summary["width"]) < 10.0
        and checkpoint["payload"]["generator"] == 7315
        and checkpoint["payload"]["radius"] == "1947/64"
    )
    return {
        "schema": "phase4-axial-tplus-projective-micro-certificate-v1",
        "result_id": "PURE_WEYL_PHASE4_AXIAL_TPLUS_PROJECTIVE_MICRO_V1",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "conventions": {
            "intrinsic_tangent_normalization": (
                "the pinned outgoing rail transports the column tangent divided "
                "by 512; its coefficient-source block is therefore multiplied "
                "by 512 when compared with the unscaled point ODE"
            ),
            "amplitude_chart": (
                "multiplicative amplitude plus logarithmic tau derivative; "
                "no interval branch of the complex logarithm is asserted"
            ),
        },
        "status": (
            "PROJECTIVE_INTERACTION_MICRO_PASS_R4_OPEN"
            if passed
            else "PROJECTIVE_INTERACTION_MICRO_REFUSED"
        ),
        "imports": {
            "predecessor_checkpoint": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": sha256(INPUT),
                "payload_sha256": json.loads(INPUT.read_text())["payload_sha256"],
            }
        },
        "successor": {
            "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
            "checkpoint_sha256": sha256(CHECKPOINT),
            "payload_sha256": checkpoint["payload_sha256"],
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_sha256": sha256(MANIFEST),
            "radial_start": checkpoint["payload"]["start_radius"],
            "radial_end": checkpoint["payload"]["radius"],
            "frequency_cell": checkpoint["payload"]["omega_child"],
            "frequency_generator": checkpoint["payload"]["generator"],
        },
        "validated_gates": {
            "interaction_reconstruction": gates["interaction"],
            "projective_multiplicative_reconstruction": gates["projective"],
            "spin_two_wronskian": gates["wronskian2"],
            "spin_one_wronskian": gates["wronskian1"],
            "inverse_and_chart_margins": {
                key: gates[key]
                for key in ("pinv_margin", "p00", "p11", "r00", "r11")
            },
            "interaction_width": gates["interaction_width"],
            "chart_width": gates["chart_width"],
            "wronskian_width": gates["wronskian_width"],
            "operator_tail": gates["op_tail"],
            "direct_boundary_summary": summary,
        },
        "accumulated_frame_chart_diagnostic": accumulated_pivot_diagnostic(
            checkpoint
        ),
        "claim_flags": {
            "local_interaction_variables_interval_enclosed": passed,
            "local_projective_multiplicative_charts_interval_enclosed": passed,
            "reciprocal_chart_denominators_exclude_zero": passed,
            "local_wronskian_laws_interval_certified": passed,
            "correlated_successor_applied_to_outgoing_frame": passed,
            "complete_outgoing_frame_at_r4": False,
            "explicit_Tplus_certified": False,
            "reflection_or_stokes_certified": False,
        },
        "does_not_establish": [
            "validated projective/multiplicative-amplitude propagation over the remaining interval to r=4",
            "the complete outgoing frame at r=4",
            "the typed outgoing map T_plus or reflection matrix",
            "the scattering Stokes audit",
        ],
        "next_gate": (
            "iterate the certified near-identity projective/interaction microfactor "
            "with adaptive panel sizing, reprojecting only local factors before "
            "their action on the accumulated outgoing frame"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.reproduce:
        checkpoint, manifest = reproduce()
    else:
        if not CHECKPOINT.exists() or not MANIFEST.exists():
            raise SystemExit("missing artifacts; run --reproduce")
        checkpoint = json.loads(CHECKPOINT.read_text())
        manifest = json.loads(MANIFEST.read_text())
    result = build_certificate(checkpoint, manifest)
    wanted = rendered(result)
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != wanted:
            raise SystemExit("projective micro certificate drift")
    else:
        CERTIFICATE.write_text(wanted)
        receipt = {
            "schema": "phase4-axial-tplus-projective-micro-receipt-v1",
            "status": result["status"],
            "certificate_sha256": sha256(CERTIFICATE),
            "checkpoint_payload_sha256": checkpoint["payload_sha256"],
            "producer_sha256": sha256(Path(__file__)),
            "verifier_sha256": sha256(HERE / "verify_projective_micro.py"),
        }
        RECEIPT.write_text(rendered(receipt))
    print(result["status"])
    return 0 if "PASS" in result["status"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
