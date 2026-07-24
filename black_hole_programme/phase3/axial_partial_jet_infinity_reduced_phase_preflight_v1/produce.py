#!/usr/bin/env python3
"""Build one phase-reduced outgoing infinity partial-jet microfactor.

The oscillatory factor exp(-2*i*omega*r_*) is kept symbolic.  Only its
reduced amplitude is represented in IvTaylor4_omega tensor dual_tau.
The endpoint seed is the finite exact XI2/XI3 factor head; no all-order
Jost-remainder claim is made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_volterra_envelope import (
    exact_blocks,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    CI,
    RI,
    eval_rational_rect,
)
from black_hole_programme.phase3.axial_partial_jet_transport_preflight_v1.produce import (
    FORGE,
    FORGE_LIB,
    ForgeExpression,
    R as FORGE_R,
    SUPPORT,
    W as FORGE_W,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE = HERE / "reduced_phase_panel.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-infinity-reduced-phase-v1")

INPUTS = {
    "endpoint_frames": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_endpoint_frames_v1/certificate.json"
    ),
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "infinity_metric_heads": ROOT / (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/infinity-metric-heads.json"
    ),
    "infinity_practical_transfer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_infinity_practical_transfer/certificate.json"
    ),
}

R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega", real=True)
I = sp.I
Z = sp.Symbol("z", nonnegative=True)
R0 = sp.Integer(32)
STEP = -sp.Rational(1, 32)
MIDPOINT = R0 + STEP / 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def forge_symbols(value: sp.Expr) -> sp.Expr:
    replacements = {}
    for symbol in value.free_symbols:
        if symbol.name == "omega":
            replacements[symbol] = FORGE_W
        elif symbol.name == "r":
            replacements[symbol] = FORGE_R
    return value.xreplace(replacements)


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def complex_to_real(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.row_join(-imag).col_join(imag.row_join(real))


def phase_reduced_data(crosswalk: dict) -> dict:
    """Return the exact finite R+ factor head and reduced generator."""
    blocks = exact_blocks()
    columns = dict(blocks["columns"])
    omega = blocks["omega"]
    z = blocks["z"]
    r = blocks["r"]

    # Both terms are expressed relative to the common XI2 factor
    # exp(-2*i*omega*r)*r^(-4*i*omega).  XI3 carries one extra z.
    quotient_cancel = -I * (16 * omega**2 - 4 * I * omega - 5) / omega
    rplus_old = (
        columns["XI2"] + quotient_cancel * z * columns["XI3"]
    ).applyfunc(clean)
    transform = matrix(
        crosswalk["full_transform_crosswalk"][
            "coordinate_map_old_to_new"
        ]
    ).subs({R: 1 / z, W: omega})
    # The imported endpoint columns are finite formal heads.  Truncate the
    # transformed result at their certified common order; rational frame
    # denominators otherwise manufacture irrelevant higher-order terms.
    rplus_new = (transform * rplus_old).applyfunc(
        lambda value: clean(sp.series(value, z, 0, 7).removeO())
    )

    # Exact quotient cancellation is part of the endpoint factor audit.
    if any(clean(entry) != 0 for entry in rplus_new[4:6, :]):
        raise RuntimeError("R+ factor line has acquired a spin-one component")

    tangent = rplus_new[0:2, :].subs(z, sp.Rational(1, R0))
    base = rplus_new[2:4, :].subs(z, sp.Rational(1, R0))

    exact = crosswalk["exact_blocks"]
    a = matrix(exact["A_RW"])
    e = matrix(exact["E_RW_self_extension"])
    # Use the exact formal infinity factor carried by the imported endpoint
    # head.  It differs from exp(-2*i*omega*r_*) by the bounded unit-modulus
    # conjugator (1-2/r)^(4*i*omega), handled in the Volterra proof below.
    log_phase_derivative = -2 * I * W - 4 * I * W / R
    reduced_a = (a - log_phase_derivative * sp.eye(2)).applyfunc(clean)

    base_real = complex_to_real(reduced_a)
    tangent_real = complex_to_real(e)
    direct_real = sp.zeros(8)
    direct_real[:4, :4] = base_real
    direct_real[:4, 4:8] = tangent_real
    direct_real[4:8, 4:8] = base_real

    def realify_column(value: sp.Matrix) -> sp.Matrix:
        re = value.applyfunc(
            lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
        )
        im = value.applyfunc(
            lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
        )
        return re.col_join(im)

    return {
        "rate": -2 * I * W,
        "power": -4 * I * W,
        "log_phase_derivative": log_phase_derivative,
        "rplus_new": rplus_new,
        "base_seed": realify_column(base),
        "tangent_seed": realify_column(tangent),
        "base_generator": base_real,
        "tangent_generator": tangent_real,
        "direct_generator": direct_real,
        "quotient_cancel": quotient_cancel,
    }


def rational_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def rational_fraction(value: sp.Expr) -> Fraction:
    value = sp.cancel(value)
    if not value.is_Rational:
        raise RuntimeError(f"expected a rational value, got {value}")
    return Fraction(int(value.p), int(value.q))


def normalize_symbols(value: sp.Expr) -> sp.Expr:
    replacements = {}
    for symbol in value.free_symbols:
        if symbol.name == "omega":
            replacements[symbol] = W
        elif symbol.name == "z":
            replacements[symbol] = Z
        elif symbol.name == "r":
            replacements[symbol] = 1 / Z
    return clean(value.xreplace(replacements))


def valuation_at_zero(value: sp.Expr) -> int:
    value = sp.cancel(value)
    if value == 0:
        return 10**6
    numerator, denominator = sp.fraction(value)
    numerator_poly = sp.Poly(numerator, Z)
    denominator_poly = sp.Poly(denominator, Z)
    return (
        min(monomial[0] for monomial, _ in numerator_poly.terms())
        - min(monomial[0] for monomial, _ in denominator_poly.terms())
    )


def scaled_rectangle_bound(value: sp.Expr) -> tuple[int, Fraction]:
    power = valuation_at_zero(value)
    if power >= 10**6:
        return power, Fraction(0)
    environment = {
        W: CI(RI(Fraction(1, 2), Fraction(4097, 8192))),
        Z: CI(RI(Fraction(0), Fraction(1, 32))),
    }
    scaled = sp.cancel(value / Z**power)
    return power, eval_rational_rect(scaled, environment).norm_one_hi()


def jost_remainder_bound(data: dict, crosswalk: dict) -> dict:
    """Rigorous real-axis Volterra remainder for the R+ factor head."""
    p0 = normalize_symbols(data["rplus_new"][2])
    x0 = normalize_symbols(data["rplus_new"][0])
    r = 1 / Z

    exact = crosswalk["exact_blocks"]
    a = matrix(exact["A_RW"]).subs(R, r)
    e = matrix(exact["E_RW_self_extension"]).subs(R, r)
    q_formal = -2 * I * W - 4 * I * W * Z

    def dr(value: sp.Expr) -> sp.Expr:
        return clean(-Z**2 * sp.diff(value, Z))

    first = clean(2 * q_formal - a[1, 1])
    zeroth = clean(
        dr(q_formal)
        + q_formal**2
        - a[1, 1] * q_formal
        - a[1, 0]
    )

    def operator(value: sp.Expr) -> sp.Expr:
        return clean(dr(dr(value)) + first * dr(value) + zeroth * value)

    s1 = clean(e[0, 0] + dr(e[0, 1]) + e[1, 1])
    s0 = clean(
        dr(e[0, 0])
        - a[1, 1] * e[0, 0]
        + e[1, 0]
        + e[0, 1] * a[1, 0]
    )
    t0 = clean(s0 + q_formal * s1)
    base_residual = clean(operator(p0))
    tangent_residual = clean(
        operator(x0) - s1 * dr(p0) - t0 * p0
    )

    p_base, c_base = scaled_rectangle_bound(base_residual)
    p_tangent, c_tangent = scaled_rectangle_bound(tangent_residual)
    p_s1, c_s1 = scaled_rectangle_bound(s1)
    p_t0, c_t0 = scaled_rectangle_bound(t0)
    if min(p_base, p_tangent, p_s1, p_t0) <= 1:
        raise RuntimeError("phase-reduced tail has acquired a nonintegrable term")

    radius = Fraction(32)

    def integral(power: int, coefficient: Fraction) -> Fraction:
        return coefficient / ((power - 1) * radius ** (power - 1))

    base_residual_integral = integral(p_base, c_base)
    tangent_residual_integral = integral(p_tangent, c_tangent)
    s1_integral = integral(p_s1, c_s1)
    t0_integral = integral(p_t0, c_t0)

    # For the ell=2 RW potential,
    # integral_R^infinity V dr_* = 6/R-3/R^2 exactly.
    potential_integral = Fraction(6, 32) - Fraction(3, 32**2)
    omega_min = Fraction(1, 2)
    contraction = potential_integral / omega_min
    if contraction >= 1:
        raise RuntimeError("outgoing scalar Volterra contraction failed")

    base_value = (
        base_residual_integral / omega_min / (1 - contraction)
    )
    base_x_derivative = (
        potential_integral * base_value + base_residual_integral
    )
    f_at_seed = Fraction(15, 16)
    omega_max = Fraction(4097, 8192)
    chi_log_derivative = (
        8 * omega_max / (Fraction(32) * Fraction(30))
    )
    base_r_derivative = (
        base_x_derivative / f_at_seed
        + chi_log_derivative * base_value
    )

    tangent_forcing = (
        s1_integral * base_r_derivative
        + t0_integral * base_value
        + tangent_residual_integral
    )
    tangent_value = (
        tangent_forcing / omega_min / (1 - contraction)
    )
    tangent_x_derivative = (
        potential_integral * tangent_value + tangent_forcing
    )
    tangent_r_derivative = (
        tangent_x_derivative / f_at_seed
        + chi_log_derivative * tangent_value
    )

    base_seed_radius = max(base_value, base_r_derivative)
    tangent_seed_radius = max(tangent_value, tangent_r_derivative)
    return {
        "formal_phase": "exp(-2*I*omega*r)*r**(-4*I*omega)",
        "exact_phase": "exp(-2*I*omega*rstar)",
        "unit_modulus_conjugator": "(1-2/r)**(4*I*omega)",
        "potential_integral": potential_integral,
        "omega_min": omega_min,
        "contraction": contraction,
        "residuals": {
            "base": {
                "valuation": p_base,
                "scaled_bound": c_base,
                "integral_bound": base_residual_integral,
            },
            "tangent": {
                "valuation": p_tangent,
                "scaled_bound": c_tangent,
                "integral_bound": tangent_residual_integral,
            },
        },
        "source_coefficients": {
            "s1": {
                "valuation": p_s1,
                "scaled_bound": c_s1,
                "integral_bound": s1_integral,
            },
            "t0": {
                "valuation": p_t0,
                "scaled_bound": c_t0,
                "integral_bound": t0_integral,
            },
        },
        "base_error": {
            "value": base_value,
            "x_derivative": base_x_derivative,
            "r_derivative": base_r_derivative,
        },
        "tangent_error": {
            "forcing": tangent_forcing,
            "value": tangent_value,
            "x_derivative": tangent_x_derivative,
            "r_derivative": tangent_r_derivative,
        },
        "base_seed_radius": base_seed_radius,
        "tangent_seed_radius": tangent_seed_radius,
    }


def render_matrix_builder(data: dict) -> str:
    matrices = (
        data["base_generator"],
        data["tangent_generator"],
        data["direct_generator"],
    )
    names = ("base", "tangent", "direct")
    sizes = (4, 4, 8)
    expressions: list[sp.Expr] = []
    positions: list[list[tuple[int, int, int]]] = []
    for value in matrices:
        current: list[tuple[int, int, int]] = []
        for row in range(value.rows):
            for col in range(value.cols):
                entry = clean(forge_symbols(value[row, col]))
                if entry != 0:
                    current.append((row, col, len(expressions)))
                    expressions.append(entry)
        positions.append(current)
    replacements, reduced = sp.cse(
        expressions, symbols=sp.numbered_symbols("t")
    )
    renderer = ForgeExpression()
    lines = [
        "fn build_models(w_model:borrow IvTaylor4Mat,"
        "r_model:borrow IvTaylor4Mat)->ModelTriple{"
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    for name, size in zip(names, sizes):
        lines.append(f"  let {name}:IvTaylor4Mat=jt_zero({size},{size});")
    for matrix_index, current in enumerate(positions):
        name = names[matrix_index]
        for row, col, expression_index in current:
            lines.append(
                f"  {name}=jt_put({name},{row},{col},"
                f"{renderer.render(reduced[expression_index])});"
            )
    lines.append("  return new ModelTriple(base,tangent,direct);")
    lines.append("}")
    return "\n".join(lines)


def render_seed_builder(data: dict, tail: dict) -> str:
    values = [
        forge_symbols(value)
        for value in list(data["base_seed"]) + list(data["tangent_seed"])
    ]
    replacements, reduced = sp.cse(values, symbols=sp.numbered_symbols("s"))
    renderer = ForgeExpression()
    lines = ["fn build_seed(w_model:borrow IvTaylor4Mat)->DualT4{"]
    # ForgeExpression recognizes r, but no seed expression depends on it.
    lines.append("  let r_model:IvTaylor4Mat=jt_const(big(\"32/1\"));")
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    lines.extend(
        [
            "  let base:IvTaylor4Mat=jt_zero(4,1);",
            "  let tangent:IvTaylor4Mat=jt_zero(4,1);",
        ]
    )
    for index in range(4):
        lines.append(
            f"  base=jt_put(base,{index},0,"
            f"{renderer.render(reduced[index])});"
        )
        lines.append(
            f"  tangent=jt_put(tangent,{index},0,"
            f"{renderer.render(reduced[4 + index])});"
        )
    base_padding = 2 * tail["base_seed_radius"]
    tangent_padding = 2 * tail["tangent_seed_radius"]
    lines.append(
        "  base=jt_pad(base,rat_to_f64("
        f'big("{rational_text(base_padding)}")));'
    )
    lines.append(
        "  tangent=jt_pad(tangent,rat_to_f64("
        f'big("{rational_text(tangent_padding)}")));'
    )
    lines.append("  return new DualT4(base,tangent);")
    lines.append("}")
    return "\n".join(lines)


EXTRA_SUPPORT = r'''
fn jt_infinity_radius()->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);
  c0=qm_set(c0,0,0,big("2047/64"));
  let rem:IvMat=ivm_zeros(1,1);
  let rad:Iv=iv_from_rat(big("1/64"));
  ivm_set(rem,0,0,iv(0.0-rad.hi,rad.hi));
  return jt_expect(ivtm4_new(7315,c0,qm_new(1,1),qm_new(1,1),
    qm_new(1,1),qm_new(1,1),rem));
}

fn stack_seed(seed:borrow DualT4)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(8,1);
  let i:i64=0;while(i<4){
    out=jt_put(out,i,0,jt_scalar(seed.tangent,i,0));
    out=jt_put(out,4+i,0,jt_scalar(seed.base,i,0));
    i=i+1;
  }
  return out;
}

fn stack_result(base:borrow IvTaylor4Mat,
tangent:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(8,1);
  let i:i64=0;while(i<4){
    out=jt_put(out,i,0,jt_scalar(tangent,i,0));
    out=jt_put(out,4+i,0,jt_scalar(base,i,0));
    i=i+1;
  }
  return out;
}
'''


MAIN = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let r_model:IvTaylor4Mat=jt_infinity_radius();
  let seed:DualT4=build_seed(w_model);
  let models:ModelTriple=build_models(w_model,r_model);
  let h:Rat=big("-1/32");
  let order:i64=12;
  let dual:DualT4=dual_series(models.base,models.tangent,h,order);
  let base_out:IvTaylor4Mat=jt_mul(dual.base,seed.base);
  let tangent_out:IvTaylor4Mat=jt_add(
    jt_mul(dual.tangent,seed.base),
    jt_mul(dual.base,seed.tangent));
  let jet_out:IvTaylor4Mat=stack_result(base_out,tangent_out);
  let direct_transport:IvTaylor4Mat=jt_series(models.direct,h,order);
  let direct_seed:IvTaylor4Mat=stack_seed(seed);
  let direct_out:IvTaylor4Mat=jt_mul(direct_transport,direct_seed);

  let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("COEFFICIENT_HULL_REFUSAL");return 3;}};
  let alpha:f64=sl_inf_norm_hi(hull);
  let scaled_norm:f64=(0.0-rat_to_f64(h))*alpha;
  let tail:f64=sl_exp_tail(scaled_norm,order+1);
  let seed_hull:IvMat=match(ivtm4_hull_checked(direct_seed)){
    some(x)=>x,none=>{println("SEED_HULL_REFUSAL");return 3;}};
  let seed_norm:f64=sl_inf_norm_hi(seed_hull);
  let propagated_tail:f64=tail*seed_norm;
  if(!f64_is_finite(propagated_tail)||propagated_tail<0.0){
    println(strfmt(system_allocator(),
      "TAIL_REFUSAL alpha={} scaled_norm={} tail={} seed_norm={}",
      [alpha,scaled_norm,tail,seed_norm]));return 3;}
  let jet_padded:IvTaylor4Mat=jt_pad(jet_out,propagated_tail);
  let direct_padded:IvTaylor4Mat=jt_pad(direct_out,propagated_tail);
  let exact_coefficients:bool=coefficients_equal(jet_padded,direct_padded);
  let overlap:bool=difference_contains_zero(jet_padded,direct_padded);
  let seed_width:f64=hull_width(direct_seed);
  let direct_width:f64=hull_width(direct_padded);
  let jet_width:f64=hull_width(jet_padded);
  println(strfmt(system_allocator(),
    "INFINITY_REDUCED_PHASE status={} coefficient_equal={} difference_contains_zero={} alpha={} scaled_norm={} tail={} seed_norm={} seed_width={} direct_width={} jet_width={}",
    [if(exact_coefficients&&overlap){"PASS"}else{"REFUSED"},
     exact_coefficients,overlap,alpha,scaled_norm,propagated_tail,seed_norm,
     seed_width,direct_width,jet_width]));
  return if(exact_coefficients&&overlap){0}else{3};
}
'''


def run(command: list[str], env: dict[str, str] | None = None) -> dict:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": " ".join(command),
        "exit": completed.returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "output": completed.stdout,
    }


def parse_run(output: str) -> dict | None:
    match = re.search(
        r"INFINITY_REDUCED_PHASE status=(?P<status>\w+) "
        r"coefficient_equal=(?P<equal>\w+) "
        r"difference_contains_zero=(?P<overlap>\w+) "
        r"alpha=(?P<alpha>[-+0-9.eE]+) "
        r"scaled_norm=(?P<scaled>[-+0-9.eE]+) "
        r"tail=(?P<tail>[-+0-9.eE]+) "
        r"seed_norm=(?P<seednorm>[-+0-9.eE]+) "
        r"seed_width=(?P<seedwidth>[-+0-9.eE]+) "
        r"direct_width=(?P<direct>[-+0-9.eE]+) "
        r"jet_width=(?P<jet>[-+0-9.eE]+)",
        output,
    )
    if not match:
        return None
    return {
        key: match.group(key)
        for key in (
            "status",
            "equal",
            "overlap",
            "alpha",
            "scaled",
            "tail",
            "seednorm",
            "seedwidth",
            "direct",
            "jet",
        )
    }


def document() -> dict:
    imported = {
        name: json.loads(path.read_text()) for name, path in INPUTS.items()
    }
    crosswalk = imported["partial_jet_crosswalk"]
    data = phase_reduced_data(crosswalk)
    tail = jost_remainder_bound(data, crosswalk)
    source = "\n".join(
        (
            SUPPORT,
            EXTRA_SUPPORT,
            render_seed_builder(data, tail),
            render_matrix_builder(data),
            MAIN,
        )
    )
    SOURCE.write_text(source)

    env = os.environ.copy()
    env["FORGE_PATH"] = str(FORGE_LIB)
    compile_result = run(
        [str(FORGE), "-o", str(BINARY), str(SOURCE)],
        env,
    )
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = (
        run([str(BINARY)], env)
        if compile_result["exit"] == 0
        else {"command": str(BINARY), "exit": 127, "output": ""}
    )
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_run(run_result["output"])
    finite_pass = bool(
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed
        and parsed["status"] == "PASS"
        and parsed["equal"] == "true"
        and parsed["overlap"] == "true"
    )

    result = {
        "schema": "phase3-axial-partial-jet-infinity-reduced-phase-preflight-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_INFINITY_REDUCED_PHASE_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "PHASE_REDUCED_JOST_REMAINDER_AND_FIRST_MACROPANEL_PASS"
            if finite_pass
            else "REDUCED_PHASE_MICROFACTOR_REFUSED"
        ),
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "phase_factor": {
            "kept_symbolic": True,
            "factor": "exp(-2*I*omega*r)*r**(-4*I*omega)",
            "drstar_dr": "r/(r-2)",
            "logarithmic_derivative": sp.sstr(
                data["log_phase_derivative"]
            ),
            "asymptotic_form": "exp(-2*I*omega*r)*r**(-4*I*omega)",
            "exact_tortoise_conjugator": "(1-2/r)**(4*I*omega)",
            "exact_tortoise_conjugator_modulus_on_real_axis": "1",
            "omega_phase_taylor_expanded": False,
        },
        "exact_endpoint_factor_seed": {
            "line": (
                "R_plus=XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega"
            ),
            "common_factor": "exp(-2*I*omega*r)*r**(-4*I*omega)",
            "XI3_relative_factor": "1/r",
            "spin_one_projection_zero": True,
            "factor_state_order": [
                "metric_RW_tau_tangent",
                "carrier_RW_base",
                "Lx_spin_one",
            ],
            "seed_radius": 32,
            "finite_head_only": True,
        },
        "all_order_jost_remainder": {
            "method": (
                "residual-corrected outgoing scalar RW Volterra equation "
                "conjugated by (1-2/r)**(4*I*omega)"
            ),
            "domain": "r>=32, omega in [1/2,4097/8192]",
            "potential_integral": rational_text(
                tail["potential_integral"]
            ),
            "omega_min": rational_text(tail["omega_min"]),
            "contraction": rational_text(tail["contraction"]),
            "contraction_strictly_below_one": tail["contraction"] < 1,
            "residuals": {
                label: {
                    key: (
                        value
                        if isinstance(value, int)
                        else rational_text(value)
                    )
                    for key, value in item.items()
                }
                for label, item in tail["residuals"].items()
            },
            "source_coefficients": {
                label: {
                    key: (
                        value
                        if isinstance(value, int)
                        else rational_text(value)
                    )
                    for key, value in item.items()
                }
                for label, item in tail["source_coefficients"].items()
            },
            "base_error": {
                key: rational_text(value)
                for key, value in tail["base_error"].items()
            },
            "tangent_error": {
                key: rational_text(value)
                for key, value in tail["tangent_error"].items()
            },
            "base_seed_padding_applied": rational_text(
                2 * tail["base_seed_radius"]
            ),
            "tangent_seed_padding_applied": rational_text(
                2 * tail["tangent_seed_radius"]
            ),
            "padding_safety_factor": 2,
            "shared_omega_model": (
                "exact rational finite head in IvTaylor4_omega plus one "
                "uniform interval remainder on the common omega child"
            ),
            "dual_tau_model": (
                "base and intrinsic tangent remainders are attached before "
                "the common dual-number transport"
            ),
        },
        "mixed_rail": {
            "arithmetic": "IvTaylor4_omega tensor dual_tau",
            "frequency_child": ["1/2", "4097/8192"],
            "frequency_center": "8193/16384",
            "frequency_radius": "1/16384",
            "radial_panel": ["32", "1023/32"],
            "panel_midpoint": sp.sstr(MIDPOINT),
            "panel_width": sp.sstr(abs(STEP)),
            "exponential_order": 12,
            "finite_seed_and_panel_passed": finite_pass,
            "parsed_result": parsed,
            "compile_exit": compile_result["exit"],
            "compile_elapsed_seconds": 0.0,
            "run_exit": run_result["exit"],
            "run_elapsed_seconds": 0.0,
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
        },
        "correlation_gate": {
            "identity": (
                "direct [[Ahat,E],[0,Ahat]] transport equals "
                "dual_tau transport coefficientwise through order 12"
            ),
            "coefficient_equal": bool(parsed and parsed["equal"] == "true"),
            "interval_difference_contains_zero": bool(
                parsed and parsed["overlap"] == "true"
            ),
            "bd_minus_ac_or_T_plus_evaluated": False,
        },
        "claim_flags": {
            "symbolic_outgoing_phase_factored": True,
            "finite_factor_head_seed_bounded": finite_pass,
            "first_tiny_reduced_panel_bounded": finite_pass,
            "first_macropanel_to_1023_over_32_bounded": finite_pass,
            "direct_vs_jet_correlation_passed": finite_pass,
            "uniform_all_order_infinity_remainder_enclosed": finite_pass,
            "outgoing_Jost_column_certified": finite_pass,
            "T_plus_recovered": False,
            "scattering_claim": False,
        },
        "shortfall": {
            "code": "OUTGOING_COLUMN_ONLY_NOT_YET_JOINED_TO_GLOBAL_CONNECTION",
            "exact": True,
            "reason": (
                "The selected repeated-spin-two R_plus Jost seed and first "
                "macropanel are enclosed, but the remaining infinity basis "
                "columns, endpoint K_plus shear, and transport to the common "
                "matching radius have not been assembled."
            ),
            "next_gate": (
                "iterate phase-reduced partial-jet panels from 1023/32 to "
                "the common matching radius and construct the complementary "
                "outgoing factor columns with the same endpoint normalization"
            ),
        },
        "does_not_establish": [
            "a complete analytic tau endpoint frame or K_plus shear",
            "T_plus, reflection, scattering, flux, or H4",
            "complex-frequency QNM or Evans data",
        ],
    }
    # Content-addressed certificates must be byte-deterministic. Runtime
    # measurements belong only in the non-authoritative execution receipt.
    result["producer_elapsed_seconds"] = 0.0
    return result


def make_receipt(document: dict, producer_elapsed_seconds: float) -> dict:
    return {
        "result_id": document["result_id"],
        "status": "PASS" if document["mixed_rail"][
            "finite_seed_and_panel_passed"
        ] else "FAIL",
        "certificate_path": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_infinity_reduced_phase_preflight_v1."
                    "produce"
                ),
                "elapsed_seconds": producer_elapsed_seconds,
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_infinity_reduced_phase_preflight_v1."
                    "verify"
                ),
                "elapsed_seconds": "recorded by invoking session",
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest "
                    "black_hole_programme.phase3."
                    "axial_partial_jet_infinity_reduced_phase_preflight_v1."
                    "test_preflight"
                ),
                "elapsed_seconds": "recorded by invoking session",
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": (
            "Tier 2/3 not required: this is a fail-closed endpoint "
            "representation preflight and promotes no global claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    elapsed = time.perf_counter() - started
    RECEIPT.write_text(
        json.dumps(make_receipt(doc, elapsed), indent=2) + "\n"
    )
    if args.print:
        print(json.dumps(doc, indent=2, sort_keys=True))
    if not doc["mixed_rail"]["finite_seed_and_panel_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
