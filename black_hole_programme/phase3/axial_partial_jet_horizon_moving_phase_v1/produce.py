#!/usr/bin/env python3
"""Certify the horizon exponent derivative and a finite reduced jet seed."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path

import sympy as sp

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
SOURCE = HERE / "moving_phase_seed.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-horizon-moving-phase-v1")

INPUTS = {
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "transport_preflight": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_preflight_v1/certificate.json"
    ),
    "endpoint_frames": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_endpoint_frames_v1/certificate.json"
    ),
    "projective_cocycle": ROOT / (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
}
CODE_INPUTS = {
    "endpoint_interval_evaluator": ROOT / (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/produce.py"
    ),
    "mixed_transport_preflight_producer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_preflight_v1/produce.py"
    ),
}

R = sp.Symbol("r", positive=True)
RHO = sp.Symbol("rho")
W = sp.Symbol("omega", real=True)
I = sp.I
ORDER = 5
RHO0 = sp.Rational(1, 2**22)
PANEL_WIDTH = sp.Rational(1, 2**30)
CAUCHY_RADIUS = sp.Rational(1, 2)
PIVOT_CONSTANT = sp.Rational(5, 4)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def enc(value: sp.Expr) -> str:
    return sp.sstr(clean(value))


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def coefficient(matrix_value: sp.Matrix, order: int) -> sp.Matrix:
    return matrix_value.applyfunc(
        lambda value: clean(
            sp.limit(
                sp.diff(value, RHO, order) / sp.factorial(order),
                RHO,
                0,
            )
        )
    )


def exact_data(crosswalk: dict) -> dict:
    blocks = crosswalk["exact_blocks"]
    a = matrix(blocks["A_RW"]).subs(R, 2 + RHO)
    e = matrix(blocks["E_RW_self_extension"]).subs(R, 2 + RHO)
    ax = matrix(blocks["A_x"]).subs(R, 2 + RHO)
    residue = (RHO * a).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    tangent_residue = (RHO * e).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    expected_residue = sp.Matrix(
        [[0, 0], [sp.Rational(3, 2), -1 - 4 * I * W]]
    )
    if (residue - expected_residue).applyfunc(clean) != sp.zeros(2):
        raise RuntimeError("RW horizon residue drift")
    if tangent_residue != sp.zeros(2):
        raise RuntimeError("tau source has acquired a horizon residue")
    ax_double_pole = (RHO**2 * ax).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    expected_ax_double_pole = sp.Matrix(
        [[0, 0], [-I * (4 * W - I), 0]]
    )
    if (
        ax_double_pole - expected_ax_double_pole
    ).applyfunc(clean) != sp.zeros(2):
        raise RuntimeError("spin-one companion double-pole drift")

    right = sp.Matrix([1, sp.Rational(3, 2) / (1 + 4 * I * W)])
    left = sp.Matrix([[1, 0]])
    if (residue * right).applyfunc(clean) != sp.zeros(2, 1):
        raise RuntimeError("selected regular right eigenvector drift")
    if (left * residue).applyfunc(clean) != sp.zeros(1, 2):
        raise RuntimeError("selected regular left eigenvector drift")
    pairing = clean((left * right)[0])
    exponent_derivative = clean((left * tangent_residue * right)[0] / pairing)
    if pairing != 1 or exponent_derivative != 0:
        raise RuntimeError("selected exponent derivative is not zero")

    regular_a = (a - residue / RHO).applyfunc(clean)
    a_coefficients = [coefficient(regular_a, n) for n in range(ORDER)]
    e_coefficients = [coefficient(e, n) for n in range(ORDER)]
    base = [right]
    tangent = [sp.zeros(2, 1)]
    pivots: list[sp.Expr] = []
    for n in range(1, ORDER + 1):
        pivot = n * sp.eye(2) - residue
        pivots.append(clean(pivot.det()))
        rhs = sum(
            (
                a_coefficients[k] * base[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(2, 1),
        )
        fn = (pivot.inv() * rhs).applyfunc(clean)
        tangent_rhs = sum(
            (
                a_coefficients[k] * tangent[n - 1 - k]
                + e_coefficients[k] * base[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(2, 1),
        )
        gn = (pivot.inv() * tangent_rhs).applyfunc(clean)
        if (pivot * fn - rhs).applyfunc(clean) != sp.zeros(2, 1):
            raise RuntimeError(f"base recurrence failed at order {n}")
        if (pivot * gn - tangent_rhs).applyfunc(clean) != sp.zeros(2, 1):
            raise RuntimeError(f"tangent recurrence failed at order {n}")
        base.append(fn)
        tangent.append(gn)
    expected_pivots = [
        clean(n * (n + 1 + 4 * I * W)) for n in range(1, ORDER + 1)
    ]
    if any(clean(x - y) != 0 for x, y in zip(pivots, expected_pivots)):
        raise RuntimeError("Frobenius pivot divisor drift")

    base_seed = sum(
        (base[n] * RHO0**n for n in range(ORDER + 1)),
        sp.zeros(2, 1),
    ).applyfunc(clean)
    tangent_seed = sum(
        (tangent[n] * RHO0**n for n in range(ORDER + 1)),
        sp.zeros(2, 1),
    ).applyfunc(clean)
    return {
        "A": a,
        "E": e,
        "Ax": ax,
        "residue": residue,
        "tangent_residue": tangent_residue,
        "ax_double_pole": ax_double_pole,
        "right": right,
        "left": left,
        "pairing": pairing,
        "exponent_derivative": exponent_derivative,
        "regular_a_limit": coefficient(regular_a, 0),
        "e_limit": coefficient(e, 0),
        "pivots": pivots,
        "base": base,
        "tangent": tangent,
        "base_seed": base_seed,
        "tangent_seed": tangent_seed,
    }


def coupled_tail_majorant(data: dict) -> dict:
    """Exact scalar majorant for the coupled base/tangent recurrence."""
    from fractions import Fraction

    environment = {
        W: CI(RI(Fraction(1, 2), Fraction(4097, 8192))),
        RHO: CI(
            RI(-Fraction(1, 2), Fraction(1, 2)),
            RI(-Fraction(1, 2), Fraction(1, 2)),
        ),
    }
    regular_a = (data["A"] - data["residue"] / RHO).applyfunc(clean)
    row_bounds_a = []
    row_bounds_e = []
    for value, target in ((regular_a, row_bounds_a), (data["E"], row_bounds_e)):
        for row in range(2):
            target.append(
                sum(
                    (
                        eval_rational_rect(value[row, col], environment)
                        .norm_one_hi()
                        for col in range(2)
                    ),
                    Fraction(0),
                )
            )
    majorant_a = sp.Rational(max(row_bounds_a))
    majorant_e = sp.Rational(max(row_bounds_e))
    p = clean(PIVOT_CONSTANT * majorant_a * CAUCHY_RADIUS)
    q = clean(PIVOT_CONSTANT * majorant_e * CAUCHY_RADIUS)
    x = clean(RHO0 / CAUCHY_RADIUS)

    coefficient = sp.Integer(1)
    harmonic = sp.Integer(0)
    first_base = None
    first_tangent = None
    first_omitted = ORDER + 1
    for n in range(1, first_omitted + 1):
        harmonic = clean(harmonic + 1 / (p + n - 1))
        coefficient = clean(coefficient * (p + n - 1) / n)
        if n == first_omitted:
            first_base = clean(coefficient * x**n)
            first_tangent = clean(q * coefficient * harmonic * x**n)
    assert first_base is not None and first_tangent is not None
    ratio_base = clean(x * (p + first_omitted) / (first_omitted + 1))
    # H_n >= 1/p gives the uniform bound
    # t_(n+1)/t_n <= x*(n+2p)/(n+1).
    ratio_tangent = clean(
        x * (first_omitted + 2 * p) / (first_omitted + 1)
    )
    if not (0 <= ratio_base < 1 and 0 <= ratio_tangent < 1):
        raise RuntimeError("coupled Frobenius tail ratio is not contractive")
    tail_base = clean(first_base / (1 - ratio_base))
    tail_tangent = clean(first_tangent / (1 - ratio_tangent))
    return {
        "row_bounds_a": [sp.Rational(x) for x in row_bounds_a],
        "row_bounds_e": [sp.Rational(x) for x in row_bounds_e],
        "majorant_a": majorant_a,
        "majorant_e": majorant_e,
        "pivot_constant": PIVOT_CONSTANT,
        "p": p,
        "q": q,
        "x": x,
        "first_base": first_base,
        "first_tangent": first_tangent,
        "ratio_base": ratio_base,
        "ratio_tangent": ratio_tangent,
        "tail_base": tail_base,
        "tail_tangent": tail_tangent,
    }


def render_seed_builder(data: dict) -> str:
    def realify_column(value: sp.Matrix) -> sp.Matrix:
        real = value.applyfunc(
            lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
        )
        imag = value.applyfunc(
            lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
        )
        return real.col_join(imag)

    base_seed = realify_column(data["base_seed"])
    tangent_seed = realify_column(data["tangent_seed"])
    values = list(base_seed) + list(tangent_seed)
    values = [value.subs({W: FORGE_W}) for value in values]
    replacements, reduced = sp.cse(values, symbols=sp.numbered_symbols("t"))
    renderer = ForgeExpression()
    lines = [
        "fn build_seed(w_model:borrow IvTaylor4Mat)->ModelTriple{",
        "  let r_model:IvTaylor4Mat=jt_const(big(\"2/1\"));",
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    lines.extend(
        [
            "  let base:IvTaylor4Mat=jt_zero(4,1);",
            "  let tangent:IvTaylor4Mat=jt_zero(4,1);",
            "  let direct:IvTaylor4Mat=jt_zero(1,1);",
        ]
    )
    for index in range(4):
        lines.append(
            f"  base=jt_put(base,{index},0,{renderer.render(reduced[index])});"
        )
        lines.append(
            "  tangent=jt_put(tangent,"
            f"{index},0,{renderer.render(reduced[4 + index])});"
        )
    lines.append("  return new ModelTriple(base,tangent,direct);")
    lines.append("}")
    return "\n".join(lines)


def realify_matrix(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.row_join(-imag).col_join(imag.row_join(real))


def render_panel_builder(data: dict) -> str:
    base = realify_matrix(data["A"].subs(RHO, R - 2))
    tangent = realify_matrix(data["E"].subs(RHO, R - 2))
    direct = sp.zeros(8)
    direct[:4, :4] = base
    direct[:4, 4:8] = tangent
    direct[4:8, 4:8] = base
    values: list[sp.Expr] = []
    locations: list[list[tuple[int, int, int]]] = []
    for matrix_value in (base, tangent, direct):
        current = []
        for row in range(matrix_value.rows):
            for col in range(matrix_value.cols):
                if matrix_value[row, col] != 0:
                    current.append((row, col, len(values)))
                    values.append(
                        matrix_value[row, col].subs(
                            {R: FORGE_R, W: FORGE_W}
                        )
                    )
        locations.append(current)
    replacements, reduced = sp.cse(values, symbols=sp.numbered_symbols("u"))
    renderer = ForgeExpression()
    lines = [
        "fn build_panel_models(w_model:borrow IvTaylor4Mat,"
        "r_model:borrow IvTaylor4Mat)->ModelTriple{"
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    for name, size in (("base", 4), ("tangent", 4), ("direct", 8)):
        lines.append(f"  let {name}:IvTaylor4Mat=jt_zero({size},{size});")
    for name, current in zip(("base", "tangent", "direct"), locations):
        for row, col, index in current:
            lines.append(
                f"  {name}=jt_put({name},{row},{col},"
                f"{renderer.render(reduced[index])});"
            )
    lines.append("  return new ModelTriple(base,tangent,direct);")
    lines.append("}")
    return "\n".join(lines)


PANEL_SUPPORT = r'''
fn dual_expand_spin2(a:borrow DualT4)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(8,8);
  let i:i64=0;while(i<4){let j:i64=0;while(j<4){
    out=jt_put(out,i,j,jt_scalar(a.base,i,j));
    out=jt_put(out,i,j+4,jt_scalar(a.tangent,i,j));
    out=jt_put(out,i+4,j+4,jt_scalar(a.base,i,j));
    j=j+1;}i=i+1;}
  return out;
}

fn dual_seed_vector(base:borrow IvTaylor4Mat,
tangent:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(8,1);
  let i:i64=0;while(i<4){
    out=jt_put(out,i,0,jt_scalar(tangent,i,0));
    out=jt_put(out,i+4,0,jt_scalar(base,i,0));
    i=i+1;}
  return out;
}
'''


MAIN_TEMPLATE = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let seed:ModelTriple=build_seed(w_model);
  let seed_base:IvTaylor4Mat=jt_pad(seed.base,@@BASE_TAIL@@);
  let seed_tangent:IvTaylor4Mat=jt_pad(seed.tangent,@@TANGENT_TAIL@@);
  let base_width:f64=hull_width(seed_base);
  let tangent_width:f64=hull_width(seed_tangent);
  if(!f64_is_finite(base_width)||!f64_is_finite(tangent_width)){
    println("MOVING_PHASE_SEED status=REFUSED");
    return 3;
  }
  let r_model:IvTaylor4Mat=jt_radius();
  let models:ModelTriple=build_panel_models(w_model,r_model);
  let h:Rat=big("1/1073741824");
  let order:i64=12;
  let dual:DualT4=dual_series(models.base,models.tangent,h,order);
  let expanded:IvTaylor4Mat=dual_expand_spin2(dual);
  let direct:IvTaylor4Mat=jt_series(models.direct,h,order);
  let hull:IvMat=match(ivtm4_hull_checked(models.direct)){
    some(x)=>x,none=>{println("PANEL_COEFFICIENT_REFUSAL");return 3;}};
  let alpha:f64=sl_inf_norm_hi(hull);
  let scaled_norm:f64=rat_to_f64(h)*alpha;
  let operator_tail:f64=sl_exp_tail(scaled_norm,order+1);
  if(!f64_is_finite(operator_tail)||operator_tail<0.0){
    println(strfmt(system_allocator(),
      "PANEL_TAIL_REFUSAL alpha={} scaled_norm={} tail={}",
      [alpha,scaled_norm,operator_tail]));return 3;}
  let expanded_padded:IvTaylor4Mat=jt_pad(expanded,operator_tail);
  let direct_padded:IvTaylor4Mat=jt_pad(direct,operator_tail);
  let exact_coefficients:bool=coefficients_equal(expanded,direct);
  let transport_overlap:bool=difference_contains_zero(
    expanded_padded,direct_padded);
  let initial_direct:IvTaylor4Mat=dual_seed_vector(
    seed_base,seed_tangent);
  let dual_out:IvTaylor4Mat=jt_mul(expanded_padded,initial_direct);
  let direct_out:IvTaylor4Mat=jt_mul(direct_padded,initial_direct);
  let seed_overlap:bool=difference_contains_zero(dual_out,direct_out);
  if(!(exact_coefficients&&transport_overlap&&seed_overlap)){
    println("PANEL_JET_COMPARISON status=REFUSED");
    return 3;
  }
  println(strfmt(system_allocator(),
    "MOVING_PHASE_SEED status=PASS base_width={} tangent_width={} alpha={} scaled_norm={} operator_tail={} transport_overlap={} seed_overlap={}",
    [base_width,tangent_width,alpha,scaled_norm,operator_tail,
     transport_overlap,seed_overlap]));
  return 0;
}
'''


def render_main(tail: dict) -> str:
    base_tail = math.nextafter(float(tail["tail_base"]), math.inf)
    tangent_tail = math.nextafter(
        float(tail["tail_tangent"]), math.inf
    )
    return (
        MAIN_TEMPLATE.replace("@@BASE_TAIL@@", repr(base_tail)).replace(
            "@@TANGENT_TAIL@@", repr(tangent_tail)
        )
    )


def run(command: list[str], env: dict[str, str] | None = None) -> dict:
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
        "output": completed.stdout,
    }


def parse_run(output: str) -> dict | None:
    match = re.search(
        r"MOVING_PHASE_SEED status=(?P<status>\w+) "
        r"base_width=(?P<base>[-+0-9.eE]+) "
        r"tangent_width=(?P<tangent>[-+0-9.eE]+) "
        r"alpha=(?P<alpha>[-+0-9.eE]+) "
        r"scaled_norm=(?P<scaled>[-+0-9.eE]+) "
        r"operator_tail=(?P<tail>[-+0-9.eE]+) "
        r"transport_overlap=(?P<transport>true|false) "
        r"seed_overlap=(?P<seed>true|false)",
        output,
    )
    if not match:
        return None
    return {
        "status": match.group("status"),
        "base_width": match.group("base"),
        "tangent_width": match.group("tangent"),
        "alpha": match.group("alpha"),
        "scaled_norm": match.group("scaled"),
        "operator_tail": match.group("tail"),
        "transport_overlap": match.group("transport") == "true",
        "seed_overlap": match.group("seed") == "true",
    }


def document() -> dict:
    imported = {
        name: json.loads(path.read_text()) for name, path in INPUTS.items()
    }
    data = exact_data(imported["partial_jet_crosswalk"])
    tail = coupled_tail_majorant(data)
    SOURCE.write_text(
        SUPPORT
        + "\n"
        + render_seed_builder(data)
        + "\n"
        + render_panel_builder(data)
        + "\n"
        + PANEL_SUPPORT
        + "\n"
        + render_main(tail)
    )
    env = dict(os.environ)
    env["FORGE_LIB"] = str(FORGE_LIB)
    compile_result = run([str(FORGE), "-o", str(BINARY), str(SOURCE)], env)
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = {"command": str(BINARY), "exit": None, "output": ""}
    if compile_result["exit"] == 0:
        run_result = run([str(BINARY)])
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_run(run_result["output"])
    finite_seed_pass = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed is not None
        and parsed["status"] == "PASS"
        and parsed["transport_overlap"]
        and parsed["seed_overlap"]
    )
    if not finite_seed_pass:
        raise RuntimeError("finite moving-phase seed rail refused")

    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in {**INPUTS, **CODE_INPUTS}.items()
    }
    return {
        "schema": "phase3-axial-partial-jet-horizon-moving-phase-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_HORIZON_MOVING_PHASE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "CERTIFIED_MOVING_PHASE_TAIL_AND_FIRST_PANEL_PARTIAL_JET_PASS",
        "imports": imports,
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "frequency_center": "8193/16384",
            "frequency_radius": "1/16384",
            "horizon_coordinate": "rho=r-2",
            "seed_radius": "1/4194304",
            "frobenius_order": ORDER,
            "selected_sector": "regular spin-two RW germ and intrinsic tau tangent",
            "arithmetic": "exact rational recurrence plus IvTaylor4_omega tensor dual_tau finite seed",
        },
        "moving_phase": {
            "imported_scalar_field_redefinition": imported[
                "projective_cocycle"
            ]["scalarization"]["field_redefinition"],
            "interpretation": (
                "the certified A_RW factor is already in the selected "
                "ingoing-phase-reduced P variable"
            ),
            "residue": [[enc(x) for x in row] for row in data["residue"].tolist()],
            "tangent_residue": [
                [enc(x) for x in row]
                for row in data["tangent_residue"].tolist()
            ],
            "spin_one_companion_rho2_Ax_limit": [
                [enc(x) for x in row]
                for row in data["ax_double_pole"].tolist()
            ],
            "selected_exponent": "0",
            "other_exponent": "-1-4*I*omega",
            "selected_right_vector": [enc(x) for x in data["right"]],
            "selected_left_vector": [enc(x) for x in data["left"]],
            "left_right_pairing": enc(data["pairing"]),
            "exponent_derivative_formula": "l_H**T*E_minus1*r_H/(l_H**T*r_H)",
            "dot_lambda_H": enc(data["exponent_derivative"]),
            "tau_log_rho_required": False,
        },
        "reduced_frobenius_recurrence": {
            "base_equation": (
                "(n*I-R_H)*f_n=sum_(k=0)^(n-1) A_k*f_(n-1-k)"
            ),
            "tangent_equation": (
                "(n*I-R_H)*g_n=sum_(k=0)^(n-1) "
                "(A_k*g_(n-1-k)+E_k*f_(n-1-k))"
            ),
            "normalization": "f_0=r_H; g_0=0",
            "pivot_determinants": [enc(x) for x in data["pivots"]],
            "base_coefficients": [
                [enc(x) for x in vector] for vector in data["base"]
            ],
            "tangent_coefficients": [
                [enc(x) for x in vector] for vector in data["tangent"]
            ],
            "regular_A_limit": [
                [enc(x) for x in row]
                for row in data["regular_a_limit"].tolist()
            ],
            "regular_E_limit": [
                [enc(x) for x in row] for row in data["e_limit"].tolist()
            ],
            "no_tau_log_through_computed_order": True,
        },
        "finite_seed_rail": {
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
            "parsed_result": parsed,
            "passed": finite_seed_pass,
            "tail_included": True,
            "tail_base_exact": enc(tail["tail_base"]),
            "tail_tangent_exact": enc(tail["tail_tangent"]),
        },
        "all_order_tail_majorant": {
            "cauchy_disk_radius": enc(CAUCHY_RADIUS),
            "pivot_inverse_bound": "||(n*I-R_H)^(-1)||_infinity<=5/(4*n)",
            "analytic_A_row_bounds": [
                enc(value) for value in tail["row_bounds_a"]
            ],
            "analytic_E_row_bounds": [
                enc(value) for value in tail["row_bounds_e"]
            ],
            "M_A": enc(tail["majorant_a"]),
            "M_E": enc(tail["majorant_e"]),
            "p=(5/4)*M_A*R": enc(tail["p"]),
            "q=(5/4)*M_E*R": enc(tail["q"]),
            "x=rho0/R": enc(tail["x"]),
            "base_majorant": "(1-x)**(-p)",
            "tangent_majorant": "q*(-log(1-x))*(1-x)**(-p)",
            "first_omitted_base_term": enc(tail["first_base"]),
            "first_omitted_tangent_term": enc(tail["first_tangent"]),
            "tail_ratio_base_upper": enc(tail["ratio_base"]),
            "tail_ratio_tangent_upper": enc(tail["ratio_tangent"]),
            "tail_base": enc(tail["tail_base"]),
            "tail_tangent": enc(tail["tail_tangent"]),
            "passed": True,
        },
        "first_panel_transport": {
            "radial_interval": [
                "2+1/4194304",
                "2+1/4194304+1/1073741824",
            ],
            "panel_width": "1/1073741824",
            "series_order": 12,
            "direct_route": "8x8 real repeated-spin-two block [[A,E],[0,A]]",
            "jet_route": "4x4 real A+epsilon*E dual transport",
            "transport_coefficients_equal": True,
            "transport_hulls_overlap": parsed["transport_overlap"],
            "tail_enclosed_seed_outputs_overlap": parsed["seed_overlap"],
            "passed": True,
        },
        "shortfall": {
            "exact": True,
            "code": "SPIN_ONE_LEVELT_AND_MULTIPANEL_TRANSPORT_OPEN",
            "reason": (
                "The certified initializer and first panel cover only the "
                "selected repeated spin-two base/tangent column. The A_x "
                "companion rho**(-2) block needs its own Levelt/phase "
                "initializer before the mixed spin-one input column can be "
                "transported."
            ),
            "next_bound": (
                "construct the phase-reduced spin-one horizon germ, combine "
                "it with the certified partial-jet seed, and extend the "
                "dual-number Peano-Baker rail panel by panel"
            ),
        },
        "diagnosis_of_prior_refusal": {
            "prior_code": imported["transport_preflight"]["attempt"][
                "parsed_result"
            ]["refusal"],
            "classification": (
                "endpoint representation failure: the old rail exponentiated "
                "the singular all-mode coefficient, including the A_x "
                "companion rho**(-2) entry, instead of initializing selected "
                "phase-reduced Frobenius/Levelt germs"
            ),
            "bulk_partial_jet_contradicted": False,
            "T_plus_contradicted": False,
        },
        "claim_flags": {
            "dot_lambda_H_exactly_zero": True,
            "tau_log_horizon_phase_absent": True,
            "selected_reduced_frobenius_recurrence_exact": True,
            "finite_mixed_seed_pass": finite_seed_pass,
            "uniform_frobenius_tail_enclosed": True,
            "first_panel_transport_certified": True,
            "endpoint_partial_jet_frame_constructed": False,
            "T_plus_recovered": False,
            "H4_pass_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "a complete tau-analytic horizon endpoint frame or its K_H shear",
            "transport beyond the first pure-spin-two radial panel",
            "the spin-one Levelt initializer and mixed spin-one input column",
            "the outgoing map T_plus, H4, scattering, or global transport",
        ],
    }


def write() -> None:
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-partial-jet-horizon-moving-phase-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.produce --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.verify",
            "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.test_moving_phase",
        ],
        "tiers": {
            "tier0": "required",
            "tier1": "required",
            "tier2": "not run: endpoint tail and global transport remain false",
            "tier3": "not run: not a freeze or theorem promotion",
        },
        "claim_boundary": (
            "exact zero exponent derivative, coupled Frobenius tail and one "
            "pure-spin-two panel only; endpoint K shear, spin-one initializer, "
            "T_plus and H4 remain open"
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = document()
    encoded = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS moving-phase tail and first pure-spin-two panel")
    else:
        write()


if __name__ == "__main__":
    main()
