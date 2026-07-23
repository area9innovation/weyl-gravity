#!/usr/bin/env python3
"""Render the isolated validated future-horizon-to-r=4 transport pilot.

The generated Forge rail keeps one shared affine frequency generator over the
first Phase-3 frequency cell.  It starts from the independently certified
regular-singular horizon initializer in the sheared chart

    (P,P',Q,Q',H1,rho F), rho=r-2,

propagates only the three future-regular complex columns through logarithmic
rho shells, rebases after every shell, and converts to the standard
six-complex-component metric state at r=4.

This producer deliberately does not import the concurrently edited global
connection producer.  The state order and raw/public crosswalk are repeated
explicitly and their sources are hashed into the output metadata.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_global_connection_matrix_v5.affine_codegen import (
    TaylorMatrix,
    parameter_taylor_model,
    rat_literal,
    realify_symbolic,
    render_taylor_matrix,
    render_runtime_taylor_builder,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures import (
    produce as endpoint_producer,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    RI,
)


HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parents[3]
RECON = HERE.parent / "axial_complete_reconstruction_repair/certificate.json"
INITIALIZER = (
    HERE.parent
    / "axial_endpoint_remainder_enclosures/validated_horizon_initializer.forge"
)
INITIALIZER_CERT = (
    HERE.parent / "axial_endpoint_remainder_enclosures/certificate.json"
)
AFFINE_CODEGEN = (
    HERE.parent / "axial_global_connection_matrix_v5/affine_codegen.py"
)
STRUCTURED_SOURCE = (
    HERE.parent / "axial_structured_lower_transition_preflight/actual_fixture.forge"
)
FORGE_IVAFFINE = Path("/home/alstrup/area9/tango/forge/lib/math/ivaffine.forge")
FORGE_IVLINPARAM = Path(
    "/home/alstrup/area9/tango/forge/lib/math/ivlinparam.forge"
)

OUTPUT = HERE / "validated_horizon_to_r4.forge"
METADATA = HERE / "render-metadata.json"

OMEGA_CELL = (Fraction(1, 2), Fraction(129, 256))
OMEGA_CENTER = sum(OMEGA_CELL, Fraction(0)) / 2
OMEGA_RADIUS = (OMEGA_CELL[1] - OMEGA_CELL[0]) / 2
GENERATOR = 7315
# The public handoff still certifies the requested rho=2^-22 section.  The
# analytic recurrence is initialized deeper, at 2^-40, so its regular-tail
# enclosure remains transverse to the singular complement after transport.
REQUESTED_INITIAL_SECTION = Fraction(1, 1 << 22)
EPSILON = Fraction(1, 1 << 40)
RHO_TARGET = Fraction(2)
RESETS_PER_SHELL = 8
LOCAL_STEPS = 2
REBASE_BITS = 128

STATE_ORDER = (
    "Re(P)", "Re(P_prime)", "Re(Q)", "Re(Q_prime)", "Re(H1)", "Re(F)",
    "Im(P)", "Im(P_prime)", "Im(Q)", "Im(Q_prime)", "Im(H1)", "Im(F)",
)
SHEARED_STATE_ORDER = tuple(
    "Re(rho*F)" if x == "Re(F)" else
    "Im(rho*F)" if x == "Im(F)" else x
    for x in STATE_ORDER
)
RAW_HORIZON_ORDER = (
    "XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus",
)
PUBLIC_HORIZON_ORDER = (
    "XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout",
)
RAW_FUTURE_REGULAR = (0, 1, 2)
PUBLIC_FUTURE_REGULAR = (0, 1, 4)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_endpoint_source(path: Path) -> str:
    text = path.read_text()
    lines = [line for line in text.splitlines() if not line.startswith("import ")]
    text = "\n".join(lines)
    marker = "pub fn main() -> i64 {"
    require(marker in text, f"endpoint adapter has no terminal main: {path}")
    return text.split(marker, 1)[0].rstrip() + "\n"


def structured_local_kernel(path: Path) -> str:
    """Import the independently valid one-panel block recurrence only.

    The predecessor package later withdrew its *multi-panel composition*
    because it mixed two row layouts.  The local recurrence precedes that
    operation and is independently tested.  This package never imports the
    withdrawn composer: it applies each correctly tagged contiguous
    block-lower factor directly to its state and rebases immediately.
    """
    text = path.read_text()
    start = text.index("fn sl_inf_norm_hi")
    end = text.index("fn sl_compose")
    return text[start:end].rstrip() + "\n"


def exact_horizon_flow() -> tuple[sp.Symbol, sp.Symbol, sp.Matrix]:
    r, omega = sp.symbols("r omega", real=True)
    cert = json.loads(RECON.read_text())
    a = sp.Matrix([
        [
            sp.sympify(x, locals={"r": r, "omega": omega, "I": sp.I})
            for x in row
        ]
        for row in cert["complete_reconstruction"]["flow6"]
    ])
    require(a.shape == (6, 6), "complete axial reconstruction flow changed")
    rho = sp.Symbol("rho", positive=True, real=True)
    shear = sp.diag(1, 1, 1, 1, 1, rho)
    shear_inv = sp.diag(1, 1, 1, 1, 1, 1 / rho)
    flow = (
        shear.diff(rho) * shear_inv
        + shear * a.subs(r, 2 + rho) * shear_inv
    ).applyfunc(sp.cancel)
    # The realified flow uses the declared Re(6),Im(6) row order.
    require(realify_symbolic(flow).shape == (12, 12), "realified flow changed")
    return rho, omega, flow


def exact_regular_initializer_model() -> tuple[TaylorMatrix, dict]:
    """Tight affine initializer for the three zero-indicial columns.

    The already-certified broad endpoint artifact covers the first 1/16-wide
    frequency cell.  Reboxing it onto our 1/256-wide cell discards the shared
    omega correlation and injects artificial singular-column contamination.
    Here we rerun the same exact recurrence and Cauchy majorant, select only
    its three zero-indicial columns, and construct the Taylor enclosure
    directly on the smaller declared cell.
    """
    repair = endpoint_producer.load_repair_module()
    data = endpoint_producer.exact_horizon_data(repair)
    majorant = endpoint_producer.cauchy_majorant(data)
    require(EPSILON < majorant["tau"],
            "auxiliary horizon start lies outside the certified Cauchy disk")
    require(data["order"] == 3, "certified horizon recurrence order changed")
    require(all(rate == 0 for rate in data["rates"][:3]),
            "future-regular zero-indicial selector changed")

    truncated = sp.zeros(6, 3)
    for n, head in enumerate(data["physical_heads"]):
        truncated += head[:, :3] * sp.Rational(
            EPSILON.numerator ** n, EPSILON.denominator ** n
        )
    truncated = truncated.applyfunc(sp.cancel)
    model = parameter_taylor_model(truncated, data["omega"], OMEGA_CELL)

    # This is exactly the ivend_regular value-tail formula for N=3 and the
    # zero phase columns.  All quantities are exact rationals.
    tau = majorant["tau"]
    x = EPSILON / tau
    qh = majorant["s_b_tau"] / Fraction(data["order"] + 1 - 2)
    coefficient_majorant = Fraction(8)
    tail = (
        coefficient_majorant
        / (1 - qh)
        * x ** (data["order"] + 1)
        / (1 - x)
    )
    require(0 < qh < 1 and tail > 0, "invalid analytic-tail majorant")
    remainder = tuple(tuple(
        RI(value.lo - tail, value.hi + tail)
        for value in row
    ) for row in model.remainder)
    tight = TaylorMatrix(model.center, model.derivative, remainder)
    return tight, {
        "recurrence_order": data["order"],
        "zero_indicial_columns": [0, 1, 2],
        "tau": str(tau),
        "epsilon_over_tau": str(x),
        "qh": str(qh),
        "coefficient_majorant": str(coefficient_majorant),
        "uniform_value_tail": str(tail),
        "resonance_witnesses": data["resonance_witnesses"],
    }


def shell_specs() -> tuple[tuple[int, Fraction, Fraction], ...]:
    out = []
    lo = EPSILON
    index = 0
    while lo < RHO_TARGET:
        hi = min(RHO_TARGET, 2 * lo)
        out.append((index, lo, hi))
        lo = hi
        index += 1
    require(len(out) == 41 and out[-1][2] == RHO_TARGET,
            "dyadic horizon shell partition changed")
    return tuple(out)


def if_dispatch(index: str, names: tuple[str, ...], suffix: str) -> str:
    require(bool(names), "empty generated dispatch")
    return " else ".join(
        [f"if({index}=={i}){{{name}{suffix}}}"
         for i, name in enumerate(names[:-1])]
        + [f"{{{names[-1]}{suffix}}}"]
    )


def render() -> tuple[str, dict]:
    rho, omega, flow = exact_horizon_flow()
    initial_model, initial_proof = exact_regular_initializer_model()
    shells = shell_specs()
    lines = [
        "// expect: 42",
        "// backends: c native",
        "// Isolated validated future-horizon regular transport to r=4.",
        "// This is a radial transport preflight, not a scattering theorem.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivendpoint;",
        "import math/ivaffine;",
        "import math/ivlinparam;",
        "import ds/vec;",
        "import ds/manualvec;",
        "import text/parse;",
        "import text/format;",
        "import text/strbuilder;",
        "",
        "fn big(s:string)->Rat{return match(parse<Rat>(bytes(s),0)){",
        "  ok(r)=>r,err(e)=>trap()};}",
        "",
        "fn ht_cell()->IvAffineCell{",
        f"  return match(iva_cell({GENERATOR},{rat_literal(OMEGA_CENTER)},",
        f"    {rat_literal(OMEGA_RADIUS)})){{some(z)=>z,none=>{{trap();}}}};",
        "}",
        "",
        "fn ht_sym(x:Iv)->Iv{let a:Iv=iv_abs(x);return iv(0.0-a.hi,a.hi);}",
        "",
        "fn gc_sym(x:Iv)->Iv{return ht_sym(x);}",
        "",
    ]
    lines += render_taylor_matrix("ht_initial_model", initial_model)
    lines += [
        "fn ht_initial()->IvAffineMat{return ht_initial_model(ht_cell());}",
        "",
    ]
    lines += render_runtime_taylor_builder(
        "ht_runtime", flow, rho, omega, OMEGA_CENTER, OMEGA_RADIUS,
    )

    for index, lo, hi in shells:
        panels = RESETS_PER_SHELL * LOCAL_STEPS
        half = (hi - lo) / (2 * panels)
        lines += [
            f"fn ht_coeff_{index}(panel:i64,tbox:Iv)->IvAffineMat{{",
            "  let c:IvAffineCell=ht_cell();",
            f"  let xc:Rat={rat_literal(lo)}+rat(2*panel+1,1)*",
            f"    {rat_literal(half)};",
            f"  return ht_runtime(xc,tbox,{rat_literal(half)},c);",
            "}",
            "",
        ]

    lines += [
        "fn gc_cell()->IvAffineCell{return ht_cell();}",
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
        "fn ht_standard_to_block_rows(a:borrow IvAffineMat)->IvAffineMat{",
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
        "fn ht_block_to_standard_rows(a:borrow IvAffineMat)->IvAffineMat{",
        "  let c:QMat=qm_new(12,a.cols);let l:QMat=qm_new(12,a.cols);",
        "  let r:IvMat=ivm_zeros(12,a.cols);let i:i64=0;",
        "  while(i<12){let si:i64=if(i<4){i}else{if(i<6){8+i-4}",
        "    else{if(i<10){4+i-6}else{i}}};let j:i64=0;",
        "    while(j<a.cols){c=qm_set(c,i,j,qm_get(a.center,si,j));",
        "      l=qm_set(l,i,j,qm_get(a.linear,si,j));",
        "      ivm_set(r,i,j,ivm_at(a.remainder,si,j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,12,a.cols,c,l,r);",
        "}",
        "",
        structured_local_kernel(STRUCTURED_SOURCE),
        "fn ht_emit(a:borrow IvAffineMat)->void{",
        "  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<12){",
        "    let j:i64=0;while(j<6){",
        "      let cs:String=rat_str(qm_get(a.center,i,j));",
        "      let ls:String=rat_str(qm_get(a.linear,i,j));",
        "      let r:Iv=ivm_at(a.remainder,i,j);let q:Iv=ivm_at(h,i,j);",
        "      println(strfmt(system_allocator(),",
        "        \"A {} {} {} {} {} {} {} {}\",",
        "        [i,j,str_view(cs),str_view(ls),f64_bits(r.lo),f64_bits(r.hi),",
        "         f64_bits(q.lo),f64_bits(q.hi)]));",
        "      drop(cs);drop(ls);j=j+1;}i=i+1;}",
        "}",
        "",
        "fn ht_standard_at_r4(a:borrow IvAffineMat)->Option<IvAffineMat>{",
        "  let s:QMat=qm_new(12,12);let i:i64=0;while(i<12){",
        "    s=qm_set(s,i,i,if(i==5 || i==11){rat(1,2)}else{rat(1,1)});",
        "    i=i+1;}",
        "  let c:IvAffineMat=ivam_constant(ht_cell().generator,s);",
        "  let z:IvAffineResult=ivam_apply_rect(c,a);",
        "  if(!z.ok){return Option.none;}",
        f"  let rb:IvAffineResult=ivam_rebase_dyadic(z.value,{REBASE_BITS});",
        "  if(!rb.ok){return Option.none;}return Option.some(ivam_clone(rb.value));",
        "}",
        "",
        "pub fn axial_horizon_to_r4()->bool{",
        "  let y:IvAffineMat=ht_standard_to_block_rows(ht_initial());",
        "  println(\"BEGIN HORIZON_TO_R4\");",
    ]
    for index, lo, hi in shells:
        panels = RESETS_PER_SHELL * LOCAL_STEPS
        width = (hi - lo) / panels
        lines += [
            f"  let p_{index}:i64=0;while(p_{index}<{panels}){{",
            f"    let ta_{index}:Iv=iv_from_rat({rat_literal(lo)}+",
            f"      rat(p_{index},1)*{rat_literal(width)});",
            f"    let tb_{index}:Iv=iv_from_rat({rat_literal(lo)}+",
            f"      rat(p_{index}+1,1)*{rat_literal(width)});",
            f"    let a_{index}:IvAffineMat=ht_coeff_{index}(p_{index},",
            f"      iv(ta_{index}.lo,tb_{index}.hi));",
            f"    let w_{index}:IvAffineMat=match(sl_local_transition(",
            f"      a_{index},{rat_literal(width)},12)){{",
            f"      some(z)=>z,none=>{{println(\"LOCAL_REFUSAL {index}\");return false;}}}};",
            f"    let z_{index}:IvAffineResult=ivam_apply_rect(w_{index},y);",
            f"    if(!z_{index}.ok){{return false;}}",
            f"    let rb_{index}:IvAffineResult=",
            f"      ivam_rebase_dyadic(z_{index}.value,{REBASE_BITS});",
            f"    if(!rb_{index}.ok){{return false;}}y=ivam_clone(rb_{index}.value);",
            f"    p_{index}=p_{index}+1;}}",
            f"  let rk_{index}:IvAffineRank=ivam_full_column_rank_cells(y,32);",
            f"  println(strfmt(system_allocator(),\"SHELL {index} {{}} {{}}\",",
            f"    [rk_{index}.certified,ivam_max_width(y)]));",
        ]
    lines += [
        "  let standard:IvAffineMat=ht_block_to_standard_rows(y);",
        "  let out:IvAffineMat=match(ht_standard_at_r4(standard)){",
        "    some(z)=>z,none=>{return false;}};",
        "  let rk:IvAffineRank=ivam_full_column_rank_cells(out,64);",
        "  println(strfmt(system_allocator(),\"RESULT {} {} {}\",",
        "    [rk.certified,rk.rank,ivam_max_width(out)]));",
        "  if(!rk.certified || rk.rank!=6){return false;}",
        "  let k:usize=0;while(k<len(rk.pivot_rows)){",
        "    println(strfmt(system_allocator(),\"PIVOT {} {}\",",
        "      [k,vec_get<i64>(rk.pivot_rows,k)]));k=k+1;}",
        "  ht_emit(out);println(\"END HORIZON_TO_R4\");return true;",
        "}",
        "",
        "pub fn main()->i64{if(!axial_horizon_to_r4()){return 3;}return 42;}",
        "",
    ]

    metadata = {
        "schema": "phase3-axial-horizon-to-r4-render-v1",
        "generator": GENERATOR,
        "omega_cell": [str(x) for x in OMEGA_CELL],
        "omega_center": str(OMEGA_CENTER),
        "omega_radius": str(OMEGA_RADIUS),
        "rho_initial": str(EPSILON),
        "requested_initializer_section": str(REQUESTED_INITIAL_SECTION),
        "requested_initializer_shell_index": 18,
        "rho_final": str(RHO_TARGET),
        "shells": [[i, str(lo), str(hi)] for i, lo, hi in shells],
        "resets_per_shell": RESETS_PER_SHELL,
        "local_steps": LOCAL_STEPS,
        "rebase_bits": REBASE_BITS,
        "generator_preserved": True,
        "state_order": list(STATE_ORDER),
        "sheared_state_order": list(SHEARED_STATE_ORDER),
        "raw_horizon_order": list(RAW_HORIZON_ORDER),
        "public_horizon_order": list(PUBLIC_HORIZON_ORDER),
        "raw_future_regular_selector": list(RAW_FUTURE_REGULAR),
        "public_future_regular_selector": list(PUBLIC_FUTURE_REGULAR),
        "initializer_proof": initial_proof,
        "structured_transport": {
            "layout": "contiguous-block-lower-8-plus-4",
            "panel_method": "order-12 Peano-Baker block recurrence",
            "composition": "direct rectangular apply to tagged block-row state",
            "withdrawn_predecessor_composer_imported": False,
        },
        "imports": {
            str(RECON.relative_to(PHYSICS)): sha256(RECON),
            str(INITIALIZER.relative_to(PHYSICS)): sha256(INITIALIZER),
            str(INITIALIZER_CERT.relative_to(PHYSICS)): sha256(INITIALIZER_CERT),
            str(AFFINE_CODEGEN.relative_to(PHYSICS)): sha256(AFFINE_CODEGEN),
            str(STRUCTURED_SOURCE.relative_to(PHYSICS)): sha256(STRUCTURED_SOURCE),
            str(FORGE_IVAFFINE): sha256(FORGE_IVAFFINE),
            str(FORGE_IVLINPARAM): sha256(FORGE_IVLINPARAM),
        },
        "does_not_establish": [
            "an infinity basis or horizon-to-infinity connection matrix",
            "finite endpoint flux, a populated scattering channel or a ghost",
            "scattering, poles, stability or CPT positivity",
            "frequencies outside [1/2,129/256], other ell or polar parity",
        ],
    }
    return "\n".join(lines), metadata


def main() -> None:
    source, metadata = render()
    OUTPUT.write_text(source)
    metadata["output_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)
    print(METADATA)


if __name__ == "__main__":
    main()
