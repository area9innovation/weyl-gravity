"""Render the parameter-correlated first-cell global-connection rail."""
from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

from .affine_codegen import (
    FrameTaylor,
    block_extract,
    coefficient_taylor_model,
    numerical_frames_with_sensitivity,
    parameter_taylor_model,
    prepare_taylor_matrix,
    rat_literal,
    realify_symbolic,
    render_frame,
    render_qmat,
    render_runtime_taylor_builder,
    render_taylor_matrix,
    require,
)


HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
RECON = HERE.parent / "axial_complete_reconstruction_repair/certificate.json"
HORIZON_SOURCE = (
    HERE.parent
    / "axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge"
)
INFINITY_SOURCE = (
    HERE.parent
    / "axial_infinity_practical_transfer/validated_infinity_transfer.forge"
)
CURRENT_CERT = HERE.parent / "axial_null_infinity_trace_preflight/certificate.json"
OMEGA_CELL = (Fraction(1, 2), Fraction(129, 256))
OMEGA_CENTER = sum(OMEGA_CELL, Fraction(0)) / 2
OMEGA_RADIUS = (OMEGA_CELL[1] - OMEGA_CELL[0]) / 2
GENERATOR = 7315
INWARD_RESETS = 28
INWARD_LOCAL_STEPS = 64
INWARD_PANELS = INWARD_RESETS * INWARD_LOCAL_STEPS
HORIZON_RESETS_PER_SHELL = 8
HORIZON_LOCAL_STEPS = 2
HORIZON_EPSILON = Fraction(1, 1 << 22)
RAW_HORIZON_ORDER = (
    "XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus"
)
PUBLIC_HORIZON_ORDER = (
    "XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout"
)
RAW_FUTURE_REGULAR = (0, 1, 2)
PUBLIC_FUTURE_REGULAR = (0, 1, 4)
INFINITY_ORDER = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_inputs() -> dict:
    r, omega = sp.symbols("r omega", real=True)
    cert = json.loads(RECON.read_text())
    a = sp.Matrix([
        [sp.sympify(x, locals={"r": r, "omega": omega, "I": sp.I})
         for x in row]
        for row in cert["complete_reconstruction"]["flow6"]
    ])
    rho = sp.Symbol("rho", positive=True, real=True)
    shear = sp.diag(1, 1, 1, 1, 1, rho)
    shear_inv = sp.diag(1, 1, 1, 1, 1, 1 / rho)
    shear_flow = (
        shear.diff(rho) * shear_inv
        + shear * a.subs(r, 2 + rho) * shear_inv
    ).applyfunc(sp.cancel)

    current_cert = json.loads(CURRENT_CERT.read_text())
    j = sp.Matrix([
        [sp.sympify(x, locals={"omega": omega, "I": sp.I}) for x in row]
        for row in current_cert["exact_radial_current"]["matrix_without_pi_alpha"]
    ])
    current_h = realify_symbolic((-sp.I * j).applyfunc(sp.cancel))
    return {
        "r": r,
        "rho": rho,
        "omega": omega,
        "A": a,
        "inward": (-a.subs(r, 32 - sp.Symbol("t", real=True))).applyfunc(sp.cancel),
        "horizon_flow": shear_flow,
        "current_h": current_h,
    }


def _strip_endpoint_source(path: Path) -> str:
    """Reuse the already-certified endpoint adapters without their mains."""
    text = path.read_text()
    lines = [line for line in text.splitlines() if not line.startswith("import ")]
    text = "\n".join(lines)
    marker = "pub fn main() -> i64 {"
    require(marker in text, f"endpoint adapter has no terminal main: {path}")
    return text.split(marker, 1)[0].rstrip() + "\n"


def _render_cell() -> list[str]:
    return [
        "fn gc_cell() -> IvAffineCell {",
        f"  return match(iva_cell({GENERATOR},{rat_literal(OMEGA_CENTER)},",
        f"    {rat_literal(OMEGA_RADIUS)})){{some(z)=>z,none=>{{trap();}}}};",
        "}",
        "",
    ]


def _render_models(
    prefix: str,
    matrix: sp.Matrix,
    coordinate: sp.Symbol,
    x0: Fraction,
    x1: Fraction,
    panels: int,
) -> tuple[list[str], tuple[str, ...]]:
    lines: list[str] = []
    names = []
    h = (x1 - x0) / panels
    omega = next(s for s in matrix.free_symbols if s.name == "omega")
    prepared = prepare_taylor_matrix(matrix, coordinate, omega)
    for panel in range(panels):
        xa, xb = x0 + panel * h, x0 + (panel + 1) * h
        name = f"{prefix}_panel_{panel}"
        model = coefficient_taylor_model(
            matrix, coordinate, omega, (xa, xb), OMEGA_CELL,
            prepared=prepared,
        )
        lines += render_taylor_matrix(name, model)
        names.append(name)
    return lines, tuple(names)


def _render_frame_family(
    prefix: str,
    frames: tuple[FrameTaylor, ...],
) -> tuple[list[str], tuple[str, ...]]:
    lines: list[str] = []
    names = []
    for k, frame in enumerate(frames):
        name = f"{prefix}_{k}"
        lines += render_frame(name, frame)
        names.append(name)
    return lines, tuple(names)


def _if_dispatch(index: str, names: tuple[str, ...], suffix: str) -> str:
    require(bool(names), "empty generated dispatch")
    return " else ".join(
        [f"if({index}=={i}){{{name}{suffix}}}"
         for i, name in enumerate(names[:-1])]
        + [f"{{{names[-1]}{suffix}}}"]
    )


def _common_affine_helpers() -> list[str]:
    return [
        "fn gc_affine_transpose(a:borrow IvAffineMat)->IvAffineMat{",
        "  let r:IvMat=ivm_zeros(a.cols,a.rows);let i:i64=0;",
        "  while(i<a.rows){let j:i64=0;while(j<a.cols){",
        "    ivm_set(r,j,i,ivm_at(a.remainder,i,j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,a.cols,a.rows,",
        "    qm_transpose(a.center),qm_transpose(a.linear),r);",
        "}",
        "",
        "fn gc_affine_submatrix(a:borrow IvAffineMat,kind:i64)->IvAffineMat{",
        "  let nr:i64=if(kind==0){8}else{if(kind==1){4}else{4}};",
        "  let nc:i64=if(kind==2){8}else{nr};",
        "  let c:QMat=qm_new(nr,nc);let l:QMat=qm_new(nr,nc);",
        "  let r:IvMat=ivm_zeros(nr,nc);let i:i64=0;",
        "  while(i<nr){let si:i64=if(kind==0){if(i<4){i}else{i+2}}",
        "    else{if(i<2){i+4}else{i+8}};let j:i64=0;",
        "    while(j<nc){let sj:i64=if(kind==1){if(j<2){j+4}else{j+8}}",
        "      else{if(j<4){j}else{j+2}};",
        "      c=qm_set(c,i,j,qm_get(a.center,si,sj));",
        "      l=qm_set(l,i,j,qm_get(a.linear,si,sj));",
        "      ivm_set(r,i,j,ivm_at(a.remainder,si,sj));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,nr,nc,c,l,r);",
        "}",
        "",
        "fn gc_block_to_standard_rows(a:borrow IvAffineMat)->IvAffineMat{",
        "  let c:QMat=qm_new(12,a.cols);let l:QMat=qm_new(12,a.cols);",
        "  let r:IvMat=ivm_zeros(12,a.cols);let i:i64=0;",
        "  while(i<12){let si:i64=if(i<4){i}else{if(i<6){8+i-4}",
        "    else{if(i<10){4+i-6}else{10+i-10}}};let j:i64=0;",
        "    while(j<a.cols){c=qm_set(c,i,j,qm_get(a.center,si,j));",
        "      l=qm_set(l,i,j,qm_get(a.linear,si,j));",
        "      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,12,a.cols,c,l,r);",
        "}",
        "",
        "fn gc_standard_to_block_rows(a:borrow IvAffineMat)->IvAffineMat{",
        "  let c:QMat=qm_new(12,a.cols);let l:QMat=qm_new(12,a.cols);",
        "  let r:IvMat=ivm_zeros(12,a.cols);let i:i64=0;",
        "  while(i<12){let si:i64=if(i<8){if(i<4){i}else{i+2}}",
        "    else{if(i<10){i-4}else{i}};let j:i64=0;",
        "    while(j<a.cols){c=qm_set(c,i,j,qm_get(a.center,si,j));",
        "      l=qm_set(l,i,j,qm_get(a.linear,si,j));",
        "      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,12,a.cols,c,l,r);",
        "}",
        "",
        "fn gc_selected_horizon_rows(a:borrow IvMat)->IvMat{",
        "  let z:IvMat=ivm_zeros(12,6);",
        "  let i:i64=0;while(i<12){let j:i64=0;while(j<6){",
        "    let sj:i64=if(j<3){j}else{j+3};",
        "    ivm_set(z,i,j,ivm_at(a,i,sj));j=j+1;}i=i+1;}",
        "  return z;",
        "}",
        "",
        "fn gc_remainder_from_box(enclosure:borrow IvMat,model:borrow IvAffineMat)->IvMat{",
        "  return ivm_sub(enclosure,ivam_hull(model));",
        "}",
        "",
        "fn gc_contains_zero(a:borrow IvAffineMat)->bool{",
        "  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<ivm_rows(h)){",
        "    let j:i64=0;while(j<ivm_cols(h)){let x:Iv=ivm_at(h,i,j);",
        "      if(x.lo>0.0 || x.hi<0.0){return false;}j=j+1;}i=i+1;}",
        "  return true;",
        "}",
        "",
    ]


def render_affine_adapter() -> tuple[str, dict]:
    data = exact_inputs()
    omega, rho = data["omega"], data["rho"]
    t = next(s for s in data["inward"].free_symbols if s.name == "t")
    lines = [
        "// expect: 42",
        "// backends: c native",
        "// Generated parameter-correlated first-cell v5 rail.",
        "// horizon crosswalk: raw=0,1,2; public=0,1,4.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivode;",
        "import math/ivlinode;",
        "import math/ivendpoint;",
        "import math/ivaffine;",
        "import math/ivlinparam;",
        "import ds/vec;",
        "import ds/manualvec;",
        "import text/parse;",
        "import text/format;",
        "import text/strbuilder;",
        "",
        _strip_endpoint_source(HORIZON_SOURCE),
        _strip_endpoint_source(INFINITY_SOURCE),
    ]
    lines += _render_cell()
    lines += _common_affine_helpers()

    # Exact endpoint Taylor centres.  The remainder is formed at runtime by
    # subtracting the correlated affine hull from the already-certified
    # endpoint enclosure.
    jmodel = parameter_taylor_model(data["current_h"], omega, OMEGA_CELL)
    lines += render_taylor_matrix("gc_current_model", jmodel)
    lines += [
        "fn gc_qsub(a:borrow QMat,b:borrow QMat)->QMat{",
        "  return qm_add(a,qm_scale(qm_clone(b),rat(-1,1)));",
        "}",
        "",
        "fn gc_select_horizon_q(a:borrow QMat)->QMat{",
        "  let z:QMat=qm_new(12,6);let i:i64=0;while(i<12){",
        "    let j:i64=0;while(j<6){let sj:i64=if(j<3){j}else{j+3};",
        "      z=qm_set(z,i,j,qm_get(a,i,sj));j=j+1;}i=i+1;}return z;",
        "}",
        "",
        "fn gc_horizon_derivative()->QMat{",
        "  let a:QMat=gc_select_horizon_q(center_0());",
        "  let b:QMat=gc_select_horizon_q(center_1());",
        "  return qm_scale(gc_qsub(b,a),rat(16,1));",
        "}",
        "",
        "fn gc_horizon_center()->QMat{",
        "  let a:QMat=gc_select_horizon_q(center_0());",
        "  return qm_add(a,qm_scale(gc_horizon_derivative(),rat(-15,512)));",
        "}",
        "",
        "fn gc_blockdiag_q(ca:borrow QMat,ka:borrow QMat)->QMat{",
        "  let z:QMat=qm_new(12,12);let i:i64=0;while(i<8){let j:i64=0;",
        "    while(j<8){z=qm_set(z,i,j,qm_get(ca,i,j));j=j+1;}i=i+1;}",
        "  i=0;while(i<4){let j:i64=0;while(j<4){",
        "    z=qm_set(z,8+i,8+j,qm_get(ka,i,j));j=j+1;}i=i+1;}return z;",
        "}",
        "",
        "fn gc_block_to_standard_q_both(a:borrow QMat)->QMat{",
        "  let z:QMat=qm_new(12,12);let i:i64=0;while(i<12){",
        "    let bi:i64=if(i<4){i}else{if(i<6){8+i-4}else{",
        "      if(i<10){4+i-6}else{i}}};let j:i64=0;while(j<12){",
        "    let bj:i64=if(j<4){j}else{if(j<6){8+j-4}else{",
        "      if(j<10){4+j-6}else{j}}};",
        "    z=qm_set(z,i,j,qm_get(a,bi,bj));j=j+1;}i=i+1;}return z;",
        "}",
        "",
        "fn gc_infinity_q(which:i64)->QMat{",
        "  let a:QMat=if(which==0){carrier_center_0()}else{carrier_center_1()};",
        "  let k:QMat=if(which==0){kernel_center_0()}else{kernel_center_1()};",
        "  return gc_block_to_standard_q_both(gc_blockdiag_q(a,k));",
        "}",
        "",
        "fn gc_infinity_center()->QMat{return gc_infinity_q(0);}",
        "fn gc_infinity_derivative()->QMat{",
        "  return qm_scale(gc_qsub(gc_infinity_q(1),gc_infinity_q(0)),rat(256,1));",
        "}",
        "",
        "fn gc_horizon_initial()->IvAffineMat{",
        "  let c:IvAffineCell=gc_cell();",
        "  let base:IvAffineResult=ivam_taylor1(c,gc_horizon_center(),",
        "    gc_horizon_derivative(),ivm_zeros(12,6));if(!base.ok){trap();}",
        "  let ep:IvEndpointCert=axial_horizon_initializer(0);",
        "  if(!ep.ok){trap();}let enclosure:IvMat=gc_selected_horizon_rows(ep.value);",
        "  let rem:IvMat=gc_remainder_from_box(enclosure,base.value);",
        "  let out:IvAffineResult=ivam_taylor1(c,gc_horizon_center(),",
        "    gc_horizon_derivative(),rem);if(!out.ok){trap();}",
        "  return ivam_clone(out.value);",
        "}",
        "",
        "fn gc_infinity_initial()->IvAffineMat{",
        "  let c:IvAffineCell=gc_cell();",
        "  let base:IvAffineResult=ivam_taylor1(c,gc_infinity_center(),",
        "    gc_infinity_derivative(),ivm_zeros(12,12));if(!base.ok){trap();}",
        "  let ep:IvEndpointCert=axial_infinity_initializer(0);",
        "  if(!ep.ok){trap();}let rem:IvMat=gc_remainder_from_box(ep.value,base.value);",
        "  let out:IvAffineResult=ivam_taylor1(c,gc_infinity_center(),",
        "    gc_infinity_derivative(),rem);if(!out.ok){trap();}",
        "  return ivam_clone(out.value);",
        "}",
        "",
    ]

    # Infinity-side parameter-correlated coefficient and exact affine frames.
    # The coefficient is evaluated from one action-specific exact rational
    # Taylor builder at runtime.  This preserves the single omega generator
    # without materialising 1792 near-identical functions in the compiler.
    lines += [
        "fn gc_sym(x:Iv)->Iv{let a:Iv=iv_abs(x);return iv(0.0-a.hi,a.hi);}",
        "",
    ]
    lines += render_runtime_taylor_builder(
        "gc_inward_runtime", data["inward"], t, omega,
        OMEGA_CENTER, OMEGA_RADIUS,
    )
    full_frames = numerical_frames_with_sensitivity(
        data["inward"], t, omega, OMEGA_CENTER,
        Fraction(0), Fraction(28), INWARD_RESETS, bits=34,
    )
    frame_lines, frame_names = _render_frame_family("gc_inward_frame", full_frames)
    lines += frame_lines
    frame_dispatch = _if_dispatch("k", frame_names, "(c)")
    lines += [
        "fn gc_inward_coeff(panel:i64,tbox:Iv)->IvAffineMat{",
        "  let c:IvAffineCell=gc_cell();",
        "  let xc:Rat=rat(2*panel+1,128);",
        "  return gc_inward_runtime(xc,tbox,rat(1,128),c);",
        "}",
        "",
        "fn gc_inward_carrier_coeff(panel:i64,tv:Iv)->IvAffineMat{",
        "  let a:IvAffineMat=gc_inward_coeff(panel,tv);",
        "  return gc_affine_submatrix(a,0);",
        "}",
        "",
        "fn gc_inward_kernel_coeff(panel:i64,tv:Iv)->IvAffineMat{",
        "  let a:IvAffineMat=gc_inward_coeff(panel,tv);",
        "  return gc_affine_submatrix(a,1);",
        "}",
        "",
        "fn gc_inward_frame_full(k:i64)->IvAffineMat{",
        "  let c:IvAffineCell=gc_cell();",
        f"  return {frame_dispatch};",
        "}",
        "",
        "fn gc_inward_frame_carrier(k:i64)->IvAffineMat{",
        "  let a:IvAffineMat=gc_inward_frame_full(k);",
        "  return gc_affine_submatrix(a,0);",
        "}",
        "",
        "fn gc_inward_frame_kernel(k:i64)->IvAffineMat{",
        "  let a:IvAffineMat=gc_inward_frame_full(k);",
        "  return gc_affine_submatrix(a,1);",
        "}",
        "",
        "fn gc_identity_frame(k:i64)->IvAffineMat{",
        "  return ivam_identity(gc_cell().generator,12);",
        "}",
        "",
        "fn gc_inward_coeff_table_range(p0:i64,p1:i64)->Vec<IvAffineMat>{",
        "  let d:ManualVec<IvAffineMat>=manual_vec_new<IvAffineMat>(system_allocator(),usize(p1-p0));",
        "  let p:i64=p0;while(p<p1){",
        "    let ta:Iv=iv_from_rat(rat(p,64));",
        "    let tb:Iv=iv_from_rat(rat(p+1,64));",
        "    let tv:Iv=iv(ta.lo,tb.hi);",
        "    d=manual_vec_push<IvAffineMat>(d,gc_inward_coeff(p,tv));p=p+1;}",
        "  return vec_seal(d);",
        "}",
        "",
        "fn gc_affine_subtable(a:borrow Vec<IvAffineMat>,kind:i64)->Vec<IvAffineMat>{",
        "  let n:usize=len(a);let d:ManualVec<IvAffineMat>=",
        "    manual_vec_new<IvAffineMat>(system_allocator(),n);",
        "  let k:usize=0;while(k<n){d=manual_vec_push<IvAffineMat>(d,",
        "    gc_affine_submatrix(vec_get_ref<IvAffineMat>(a,k),kind));k=k+1;}",
        "  return vec_seal(d);",
        "}",
        "",
        "fn gc_inward_frame_table_range(kind:i64,k0:i64,k1:i64)->Vec<IvAffineMat>{",
        "  let d:ManualVec<IvAffineMat>=manual_vec_new<IvAffineMat>(system_allocator(),usize(k1-k0));",
        "  let k:i64=k0;while(k<k1){",
        "    let z:IvAffineMat=if(kind==3){gc_identity_frame(k)}else{",
        "      if(kind==0){gc_inward_frame_full(k)}else{",
        "      if(kind==1){gc_inward_frame_carrier(k)}else{gc_inward_frame_kernel(k)}}};",
        "    d=manual_vec_push<IvAffineMat>(d,z);k=k+1;}return vec_seal(d);",
        "}",
        "",
    ]

    # Horizon shells: rho doubles from 2^-22 to 2.  They share one compact
    # action-specific Taylor builder; shell wrappers provide the exact panel
    # midpoint and half-width.
    lines += render_runtime_taylor_builder(
        "gc_horizon_runtime", data["horizon_flow"], rho, omega,
        OMEGA_CENTER, OMEGA_RADIUS,
    )
    shell_specs = []
    shell_lo = HORIZON_EPSILON
    shell_index = 0
    while shell_lo < 2:
        shell_hi = min(Fraction(2), 2 * shell_lo)
        panels = HORIZON_RESETS_PER_SHELL * HORIZON_LOCAL_STEPS
        frames = numerical_frames_with_sensitivity(
            data["horizon_flow"], rho, omega, OMEGA_CENTER,
            shell_lo, shell_hi, HORIZON_RESETS_PER_SHELL, bits=34,
        )
        flines, fnames = _render_frame_family(
            f"gc_hshell_frame_{shell_index}", frames
        )
        lines += flines
        fdispatch = _if_dispatch("k", fnames, "(c)")
        xhalf = (shell_hi - shell_lo) / (2 * panels)
        lines += [
            f"fn gc_hshell_coeff_{shell_index}(panel:i64,tbox:Iv)->IvAffineMat{{",
            "  let c:IvAffineCell=gc_cell();",
            f"  let xc:Rat={rat_literal(shell_lo)}+",
            f"    rat(2*panel+1,1)*{rat_literal(xhalf)};",
            f"  return gc_horizon_runtime(xc,tbox,{rat_literal(xhalf)},c);",
            "}",
            "",
            f"fn gc_hshell_frame_dispatch_{shell_index}(k:i64)->IvAffineMat{{",
            "  let c:IvAffineCell=gc_cell();",
            f"  return {fdispatch};",
            "}",
            "",
        ]
        shell_specs.append((shell_index, shell_lo, shell_hi))
        shell_lo = shell_hi
        shell_index += 1

    # The remaining algorithmic body is intentionally compact; all large
    # tables above are generated evidence inputs.
    lines += _render_algorithm(shell_specs)
    metadata = {
        "omega_cell": [str(x) for x in OMEGA_CELL],
        "generator": GENERATOR,
        "inward_factors": INWARD_RESETS,
        "inward_local_steps": INWARD_LOCAL_STEPS,
        "inward_panels": INWARD_PANELS,
        "horizon_shells": len(shell_specs),
        "horizon_factors": len(shell_specs) * HORIZON_RESETS_PER_SHELL,
        "raw_horizon_order": list(RAW_HORIZON_ORDER),
        "public_horizon_order": list(PUBLIC_HORIZON_ORDER),
        "raw_future_regular_selector": list(RAW_FUTURE_REGULAR),
        "public_future_regular_selector": list(PUBLIC_FUTURE_REGULAR),
    }
    return "\n".join(lines), metadata


def _render_algorithm(
    shells: list[tuple[int, Fraction, Fraction]],
) -> list[str]:
    lines = [
        "fn gc_build_full_factor(fc:borrow IvLinParamAffineFlow,",
        "fk:borrow IvLinParamAffineFlow,raw:borrow IvLinParamAffineFlow,",
        "k:i64,offset:i64)->Option<IvAffineMat>{",
        "  let wc:IvAffineMat=match(ivlin_param_affine_correction(fc,k)){",
        "    some(z)=>z,none=>{return Option.none;}};",
        "  let wk:IvAffineMat=match(ivlin_param_affine_correction(fk,k)){",
        "    some(z)=>z,none=>{return Option.none;}};",
        "  let u:IvAffineMat=match(ivlin_param_affine_correction(raw,k)){",
        "    some(z)=>z,none=>{return Option.none;}};",
        "  let g:IvAffineMat=gc_affine_submatrix(u,2);",
        "  let uk:IvAffineMat=gc_affine_submatrix(u,1);",
        "  let gk:i64=k+offset;",
        "  let cc:IvAffineMat=gc_inward_frame_carrier(gk);",
        "  let ck1:IvAffineMat=gc_inward_frame_kernel(gk+1);",
        "  let d:IvAffineMat=gc_affine_submatrix(gc_inward_frame_full(gk),2);",
        "  let d1:IvAffineMat=gc_affine_submatrix(gc_inward_frame_full(gk+1),2);",
        "  let a:IvAffineResult=ivam_mul_checked(g,cc);if(!a.ok){return Option.none;}",
        "  let b:IvAffineResult=ivam_mul_checked(uk,d);if(!b.ok){return Option.none;}",
        "  let c:IvAffineResult=ivam_add_checked(a.value,b.value);if(!c.ok){return Option.none;}",
        "  let d1wc:IvAffineResult=ivam_mul_checked(d1,wc);if(!d1wc.ok){return Option.none;}",
        "  let rhs:IvAffineResult=ivam_sub_checked(c.value,d1wc.value);if(!rhs.ok){return Option.none;}",
        "  let lr:IvAffineResult=ivam_solve_rect(ck1,rhs.value);if(!lr.ok){return Option.none;}",
        "  let w:IvAffineResult=ivam_block_lower(wc,lr.value,wk);",
        "  if(!w.ok){return Option.none;}return Option.some(ivam_clone(w.value));",
        "}",
        "",
        "fn gc_propagate_infinity(x:borrow IvAffineMat,",
        "fc:borrow IvLinParamAffineFlow,fk:borrow IvLinParamAffineFlow,",
        "raw:borrow IvLinParamAffineFlow)->Option<IvAffineMat>{",
        "  let y:IvAffineMat=gc_standard_to_block_rows(x);let k:i64=0;",
        f"  while(k<{INWARD_RESETS}){{",
        "    let w:IvAffineMat=match(gc_build_full_factor(fc,fk,raw,k,0)){",
        "      some(z)=>z,none=>{return Option.none;}};",
        "    let z:IvAffineResult=ivam_apply_rect(w,y);if(!z.ok){return Option.none;}",
        "    y=ivam_clone(z.value);k=k+1;}",
        "  let cf:IvAffineMat=gc_inward_frame_carrier(" + str(INWARD_RESETS) + ");",
        "  let kf:IvAffineMat=gc_inward_frame_kernel(" + str(INWARD_RESETS) + ");",
        "  let df:IvAffineMat=gc_affine_submatrix(gc_inward_frame_full("
        + str(INWARD_RESETS) + "),2);",
        "  let bf:IvAffineResult=ivam_block_lower(cf,df,kf);if(!bf.ok){return Option.none;}",
        "  let z:IvAffineResult=ivam_apply_rect(bf.value,y);if(!z.ok){return Option.none;}",
        "  return Option.some(gc_block_to_standard_rows(z.value));",
        "}",
        "",
        "fn gc_full_frame_at(k:i64)->Option<IvAffineMat>{",
        "  let cf:IvAffineMat=gc_inward_frame_carrier(k);",
        "  let kf:IvAffineMat=gc_inward_frame_kernel(k);",
        "  let df:IvAffineMat=gc_affine_submatrix(gc_inward_frame_full(k),2);",
        "  let b:IvAffineResult=ivam_block_lower(cf,df,kf);",
        "  if(!b.ok){return Option.none;}return Option.some(ivam_clone(b.value));",
        "}",
        "",
        "fn gc_chunk_transfer(fc:borrow IvLinParamAffineFlow,",
        "fk:borrow IvLinParamAffineFlow,raw:borrow IvLinParamAffineFlow,",
        "start:i64,count:i64)->Option<IvAffineMat>{",
        "  let x:IvAffineMat=ivam_identity(gc_cell().generator,12);",
        "  let xb:IvAffineMat=gc_standard_to_block_rows(x);",
        "  let b0:IvAffineMat=match(gc_full_frame_at(start)){",
        "    some(z)=>z,none=>{return Option.none;}};",
        "  let y0:IvAffineResult=ivam_solve_rect(b0,xb);",
        "  if(!y0.ok){return Option.none;}let y:IvAffineMat=ivam_clone(y0.value);",
        "  let k:i64=0;while(k<count){",
        "    let w:IvAffineMat=match(gc_build_full_factor(fc,fk,raw,k,start)){",
        "      some(z)=>z,none=>{return Option.none;}};",
        "    let z:IvAffineResult=ivam_apply_rect(w,y);if(!z.ok){return Option.none;}",
        "    y=ivam_clone(z.value);k=k+1;}",
        "  let b1:IvAffineMat=match(gc_full_frame_at(start+count)){",
        "    some(z)=>z,none=>{return Option.none;}};",
        "  let z:IvAffineResult=ivam_apply_rect(b1,y);if(!z.ok){return Option.none;}",
        "  return Option.some(gc_block_to_standard_rows(z.value));",
        "}",
        "",
        "pub fn axial_global_connection_chunk(start:i64,count:i64)->bool{",
        "  if(start<0 || count<1 || start+count>28){return false;}",
        "  let p0:i64=start*64;let p1:i64=(start+count)*64;",
        "  let at:Vec<IvAffineMat>=gc_inward_coeff_table_range(p0,p1);",
        "  let ac:Vec<IvAffineMat>=gc_affine_subtable(at,0);",
        "  let ak:Vec<IvAffineMat>=gc_affine_subtable(at,1);",
        "  let cff:Vec<IvAffineMat>=gc_inward_frame_table_range(1,start,start+count+1);",
        "  let kff:Vec<IvAffineMat>=gc_inward_frame_table_range(2,start,start+count+1);",
        "  let iff:Vec<IvAffineMat>=gc_inward_frame_table_range(3,start,start+count+1);",
        "  let cell:IvAffineCell=gc_cell();",
        "  println(strfmt(system_allocator(),\"chunk={} carrier begin\",[start]));",
        "  let fc:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    ac,cff,cell,8,rat(start,1),rat(start+count,1),count,64,12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"chunk={} carrier end refusal={}\",[start,fc.refusal_code]));",
        "  println(strfmt(system_allocator(),\"chunk={} kernel begin\",[start]));",
        "  let fk:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    ak,kff,cell,4,rat(start,1),rat(start+count,1),count,64,12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"chunk={} kernel end refusal={}\",[start,fk.refusal_code]));",
        "  println(strfmt(system_allocator(),\"chunk={} raw begin\",[start]));",
        "  let raw:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    at,iff,cell,12,rat(start,1),rat(start+count,1),count,64,12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"chunk={} raw end refusal={}\",[start,raw.refusal_code]));",
        "  if(!fc.ok || !fk.ok || !raw.ok){println(strfmt(system_allocator(),",
        "    \"chunk={} refusal fc={} fk={} raw={}\",[start,fc.refusal_code,",
        "    fk.refusal_code,raw.refusal_code]));return false;}",
        "  let phi:IvAffineMat=match(gc_chunk_transfer(fc,fk,raw,start,count)){",
        "    some(z)=>z,none=>{return false;}};",
        "  let rk:IvAffineRank=ivam_full_column_rank_cells(phi,16);",
        "  println(strfmt(system_allocator(),\"chunk={} rank={} width={}\",",
        "    [start,rk.rank,ivam_max_width(phi)]));return rk.certified;",
        "}",
        "",
        "fn gc_propagate_horizon()->Option<IvAffineMat>{",
        "  let y:IvAffineMat=gc_horizon_initial();",
    ]
    for index, lo, hi in shells:
        lines += [
            f"  let hf_{index}:IvLinParamAffineFlow=",
            f"    ivlin_param_affine_fundamental_indexed(gc_hshell_coeff_{index},",
            f"    gc_hshell_frame_dispatch_{index},gc_cell(),12,",
            f"    {rat_literal(lo)},{rat_literal(hi)},",
            f"    {HORIZON_RESETS_PER_SHELL},{HORIZON_LOCAL_STEPS},12,8,",
            "    true,true,true);",
            f"  if(!hf_{index}.ok){{return Option.none;}}",
            f"  let hz_{index}:IvAffineResult=ivlin_param_affine_apply_rect(hf_{index},y);",
            f"  if(!hz_{index}.ok){{return Option.none;}}y=ivam_clone(hz_{index}.value);",
        ]
    # At rho=2 the sheared variable rho*F is divided by 2 to recover F.
    lines += [
        "  let s:QMat=qm_new(12,12);let i:i64=0;while(i<12){",
        "    s=qm_set(s,i,i,if(i==5 || i==11){rat(1,2)}else{rat(1,1)});i=i+1;}",
        "  let conv:IvAffineMat=ivam_constant(gc_cell().generator,s);",
        "  let out:IvAffineResult=ivam_apply_rect(conv,y);if(!out.ok){return Option.none;}",
        "  return Option.some(ivam_clone(out.value));",
        "}",
        "",
        "fn gc_projection(t:borrow IvAffineMat,plus:bool)->IvAffineMat{",
        "  let c:QMat=qm_new(6,t.cols);let l:QMat=qm_new(6,t.cols);",
        "  let r:IvMat=ivm_zeros(6,t.cols);let i:i64=0;while(i<6){",
        "    let si:i64=if(plus){if(i==0){2}else{if(i==1){3}else{",
        "      if(i==2){5}else{if(i==3){8}else{if(i==4){9}else{11}}}}}}",
        "      else{if(i==0){0}else{if(i==1){1}else{if(i==2){4}else{",
        "      if(i==3){6}else{if(i==4){7}else{10}}}}}};",
        "    let j:i64=0;while(j<t.cols){",
        "      c=qm_set(c,i,j,qm_get(t.center,si,j));",
        "      l=qm_set(l,i,j,qm_get(t.linear,si,j));",
        "      ivm_set(r,i,j,ivm_at(t.remainder,si,j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(t.generator,6,t.cols,c,l,r);",
        "}",
        "",
        "pub fn axial_global_connection_first_cell()->bool{",
        "  let cell:IvAffineCell=gc_cell();",
        "  println(\"stage=infinity-tables begin\");",
        "  let at:Vec<IvAffineMat>=gc_inward_coeff_table_range(0,1792);",
        "  let ac:Vec<IvAffineMat>=gc_affine_subtable(at,0);",
        "  let ak:Vec<IvAffineMat>=gc_affine_subtable(at,1);",
        "  let ff:Vec<IvAffineMat>=gc_inward_frame_table_range(0,0,29);",
        "  let fcframes:Vec<IvAffineMat>=gc_inward_frame_table_range(1,0,29);",
        "  let fkframes:Vec<IvAffineMat>=gc_inward_frame_table_range(2,0,29);",
        "  let idframes:Vec<IvAffineMat>=gc_inward_frame_table_range(3,0,29);",
        "  println(\"stage=infinity-tables end\");",
        "  println(\"stage=infinity-carrier begin\");",
        "  let fc:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    ac,fcframes,cell,8,",
        f"    rat(0,1),rat(28,1),{INWARD_RESETS},{INWARD_LOCAL_STEPS},12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"stage=infinity-carrier end ok={} refusal={}\",[fc.ok,fc.refusal_code]));",
        "  println(\"stage=infinity-kernel begin\");",
        "  let fk:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    ak,fkframes,cell,4,",
        f"    rat(0,1),rat(28,1),{INWARD_RESETS},{INWARD_LOCAL_STEPS},12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"stage=infinity-kernel end ok={} refusal={}\",[fk.ok,fk.refusal_code]));",
        "  println(\"stage=infinity-raw begin\");",
        "  let raw:IvLinParamAffineFlow=ivlin_param_affine_fundamental_tables(",
        "    at,idframes,cell,12,",
        f"    rat(0,1),rat(28,1),{INWARD_RESETS},{INWARD_LOCAL_STEPS},12,8,true,true,true);",
        "  println(strfmt(system_allocator(),\"stage=infinity-raw end ok={} refusal={}\",[raw.ok,raw.refusal_code]));",
        "  if(!fc.ok || !fk.ok || !raw.ok){",
        "    println(strfmt(system_allocator(),\"flow refusal fc={} fk={} raw={}\",",
        "      [fc.refusal_code,fk.refusal_code,raw.refusal_code]));return false;}",
        "  let i4:IvAffineMat=match(gc_propagate_infinity(gc_infinity_initial(),fc,fk,raw)){",
        "    some(z)=>z,none=>{return false;}};",
        "  let h4:IvAffineMat=match(gc_propagate_horizon()){some(z)=>z,none=>{return false;}};",
        "  let tr:IvAffineResult=ivam_solve_rect(i4,h4);if(!tr.ok){return false;}",
        "  let rt:IvAffineRank=ivam_full_column_rank_cells(tr.value,16);",
        "  let rm:IvAffineRank=ivam_full_column_rank_cells(gc_projection(tr.value,false),16);",
        "  let rp:IvAffineRank=ivam_full_column_rank_cells(gc_projection(tr.value,true),16);",
        "  if(!rt.certified || !rm.certified || !rp.certified){return false;}",
        "  let g:IvAffineMat=gc_current_model(cell);",
        "  let it:IvAffineMat=gc_affine_transpose(i4);",
        "  let ht:IvAffineMat=gc_affine_transpose(h4);",
        "  let gi:IvAffineResult=ivam_mul_checked(g,i4);if(!gi.ok){return false;}",
        "  let ih:IvAffineResult=ivam_mul_checked(it,gi.value);if(!ih.ok){return false;}",
        "  let gh:IvAffineResult=ivam_mul_checked(g,h4);if(!gh.ok){return false;}",
        "  let hh:IvAffineResult=ivam_mul_checked(ht,gh.value);if(!hh.ok){return false;}",
        "  let tt:IvAffineMat=gc_affine_transpose(tr.value);",
        "  let iht:IvAffineResult=ivam_mul_checked(ih.value,tr.value);if(!iht.ok){return false;}",
        "  let pull:IvAffineResult=ivam_mul_checked(tt,iht.value);if(!pull.ok){return false;}",
        "  let defect:IvAffineResult=ivam_sub_checked(pull.value,hh.value);",
        "  if(!defect.ok || !gc_contains_zero(defect.value)){return false;}",
        "  println(strfmt(system_allocator(),",
        "    \"global first cell ranks T={} I-={} I+={} defect-width={}\",",
        "    [rt.rank,rm.rank,rp.rank,ivam_max_width(defect.value)]));",
        "  return true;",
        "}",
        "",
        "pub fn main()->i64{if(!axial_global_connection_first_cell()){return 3;}return 42;}",
        "",
    ]
    return lines
