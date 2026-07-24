#!/usr/bin/env python3
"""Produce the spin-one Levelt/mixed partial-jet horizon certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from fractions import Fraction
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
    complex_to_real,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE = HERE / "spin_one_levelt_panel.forge"
COMPILE_LOG = HERE / "compile.txt"
RUN_LOG = HERE / "run.txt"
BINARY = Path("/tmp/axial-partial-jet-horizon-spin-one-levelt-v1")
INPUTS = {
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "moving_phase_spin_two": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_moving_phase_v1/certificate.json"
    ),
    "endpoint_frames": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_endpoint_frames_v1/certificate.json"
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
CAUCHY_RADIUS = sp.Rational(1, 2)
PIVOT_CONSTANT = sp.Integer(3)


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
    c = matrix(blocks["C_Lx_to_metric_RW"]).subs(R, 2 + RHO)
    d = matrix(blocks["D_Lx_to_carrier_RW"]).subs(R, 2 + RHO)
    ax = matrix(blocks["A_x"]).subs(R, 2 + RHO)

    spin_two = (a + sp.eye(2) / RHO).applyfunc(clean)
    levelt = sp.diag(RHO, RHO**2)
    spin_one = (
        levelt.diff(RHO) * levelt.inv()
        + levelt * ax * levelt.inv()
    ).applyfunc(clean)
    inverse_levelt_source = sp.diag(1, 1 / RHO)
    d_regular = (d * inverse_levelt_source).applyfunc(clean)
    c_regular = (c * inverse_levelt_source).applyfunc(clean)
    if any(
        value.has(sp.zoo)
        for value in list(coefficient(d_regular, 0))
        + list(coefficient(c_regular, 0))
    ):
        raise RuntimeError("mixed Levelt sources are not regular")

    base = sp.zeros(4)
    base[:2, :2] = spin_two
    base[:2, 2:4] = d_regular
    base[2:4, 2:4] = spin_one
    tangent = sp.zeros(4)
    tangent[:2, :2] = e
    tangent[:2, 2:4] = c_regular
    direct = sp.zeros(6)
    direct[:2, :2] = spin_two
    direct[:2, 2:4] = e
    direct[:2, 4:6] = c_regular
    direct[2:4, 2:4] = spin_two
    direct[2:4, 4:6] = d_regular
    direct[4:6, 4:6] = spin_one

    residue = (RHO * base).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    tangent_residue = (RHO * tangent).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    expected = sp.zeros(4)
    expected[:2, :2] = sp.Matrix(
        [[1, 0], [sp.Rational(3, 2), -4 * I * W]]
    )
    expected[2:4, 2:4] = sp.Matrix(
        [[1, 1], [-1 - 4 * I * W, -1 - 4 * I * W]]
    )
    if (residue - expected).applyfunc(clean) != sp.zeros(4):
        raise RuntimeError("Levelt residue drift")
    if tangent_residue != sp.zeros(4):
        raise RuntimeError("Levelt tangent has acquired a residue")
    selected = sp.Matrix([0, 0, 1, -1])
    if (residue * selected).applyfunc(clean) != sp.zeros(4, 1):
        raise RuntimeError("regular spin-one Levelt line drift")
    characteristic = sp.factor(residue.charpoly().as_expr())
    expected_characteristic = sp.factor(
        sp.Symbol("lambda")
        * (sp.Symbol("lambda") - 1)
        * (sp.Symbol("lambda") + 4 * I * W) ** 2
    )
    if sp.expand(characteristic - expected_characteristic) != 0:
        raise RuntimeError("Levelt characteristic drift")

    regular_base = (base - residue / RHO).applyfunc(clean)
    base_coefficients = [
        coefficient(regular_base, n) for n in range(ORDER)
    ]
    tangent_coefficients = [
        coefficient(tangent, n) for n in range(ORDER)
    ]
    f = [selected]
    g = [sp.zeros(4, 1)]
    resonance = []
    for n in range(1, ORDER + 1):
        pivot = n * sp.eye(4) - residue
        rhs = sum(
            (
                base_coefficients[k] * f[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(4, 1),
        )
        fn, parameters = pivot.gauss_jordan_solve(rhs)
        fn = fn.subs({parameter: 0 for parameter in parameters}).applyfunc(
            clean
        )
        tangent_rhs = sum(
            (
                base_coefficients[k] * g[n - 1 - k]
                + tangent_coefficients[k] * f[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(4, 1),
        )
        gn, tangent_parameters = pivot.gauss_jordan_solve(tangent_rhs)
        gn = gn.subs(
            {parameter: 0 for parameter in tangent_parameters}
        ).applyfunc(clean)
        if (pivot * fn - rhs).applyfunc(clean) != sp.zeros(4, 1):
            raise RuntimeError(f"base Levelt recurrence failed at {n}")
        if (
            pivot * gn - tangent_rhs
        ).applyfunc(clean) != sp.zeros(4, 1):
            raise RuntimeError(f"tangent Levelt recurrence failed at {n}")
        if parameters or tangent_parameters:
            resonance.append(
                {
                    "order": n,
                    "base_free_parameters_set_to_zero": len(parameters),
                    "tangent_free_parameters_set_to_zero": len(
                        tangent_parameters
                    ),
                    "base_compatibility_residual": "0",
                    "tangent_compatibility_residual": "0",
                }
            )
        f.append(fn)
        g.append(gn)
    if resonance != [
        {
            "order": 1,
            "base_free_parameters_set_to_zero": 1,
            "tangent_free_parameters_set_to_zero": 1,
            "base_compatibility_residual": "0",
            "tangent_compatibility_residual": "0",
        }
    ]:
        raise RuntimeError("unexpected Levelt resonance structure")
    if g[1] != sp.zeros(4, 1):
        raise RuntimeError("order-one tangent normalization drift")

    base_seed = sum(
        (f[n] * RHO0**n for n in range(ORDER + 1)),
        sp.zeros(4, 1),
    ).applyfunc(clean)
    tangent_seed = sum(
        (g[n] * RHO0**n for n in range(ORDER + 1)),
        sp.zeros(4, 1),
    ).applyfunc(clean)
    return {
        "spin_two": spin_two,
        "spin_one": spin_one,
        "d_regular": d_regular,
        "c_regular": c_regular,
        "base": base,
        "tangent": tangent,
        "direct": direct,
        "residue": residue,
        "tangent_residue": tangent_residue,
        "characteristic": characteristic,
        "selected": selected,
        "regular_base": regular_base,
        "f": f,
        "g": g,
        "resonance": resonance,
        "base_seed": base_seed,
        "tangent_seed": tangent_seed,
    }


def row_norm_bound(
    value: sp.Matrix, environment: dict[sp.Symbol, CI]
) -> tuple[list[sp.Rational], sp.Rational]:
    rows = []
    for row in range(value.rows):
        rows.append(
            sp.Rational(
                sum(
                    (
                        eval_rational_rect(value[row, col], environment)
                        .norm_one_hi()
                        for col in range(value.cols)
                    ),
                    Fraction(0),
                )
            )
        )
    return rows, max(rows)


def tail_majorant(data: dict) -> dict:
    frequency = CI(RI(Fraction(1, 2), Fraction(4097, 8192)))
    disk_environment = {
        W: frequency,
        RHO: CI(
            RI(-Fraction(1, 2), Fraction(1, 2)),
            RI(-Fraction(1, 2), Fraction(1, 2)),
        ),
    }
    base_rows, majorant_base = row_norm_bound(
        data["regular_base"], disk_environment
    )
    tangent_rows, majorant_tangent = row_norm_bound(
        data["tangent"], disk_environment
    )

    finite_inverse_bounds = []
    for n in range(2, 13):
        inverse = (n * sp.eye(4) - data["residue"]).inv().applyfunc(clean)
        rows, bound = row_norm_bound(inverse, {W: frequency})
        scaled = clean(n * bound)
        if scaled > PIVOT_CONSTANT:
            raise RuntimeError(f"finite pivot bound failed at {n}")
        finite_inverse_bounds.append(
            {"n": n, "row_bounds": [enc(x) for x in rows], "n_norm": enc(scaled)}
        )
    residue_bound = sp.Rational(6145, 1024)
    if clean(13 / (13 - residue_bound)) >= PIVOT_CONSTANT:
        raise RuntimeError("large-n Neumann pivot bound failed")

    initial_environment = {W: frequency}
    f1_rows = [
        sp.Rational(
            eval_rational_rect(value, initial_environment).norm_one_hi()
        )
        for value in data["f"][1]
    ]
    f1_bound = max(f1_rows)
    if f1_bound > PIVOT_CONSTANT * majorant_base:
        raise RuntimeError("resonant f1 is not dominated by the majorant")
    if data["g"][1] != sp.zeros(4, 1):
        raise RuntimeError("nonzero resonant tangent coefficient")

    p = clean(PIVOT_CONSTANT * majorant_base * CAUCHY_RADIUS)
    q = clean(PIVOT_CONSTANT * majorant_tangent * CAUCHY_RADIUS)
    x = clean(RHO0 / CAUCHY_RADIUS)
    coefficient_value = sp.Integer(1)
    harmonic = sp.Integer(0)
    for n in range(1, ORDER + 2):
        harmonic = clean(harmonic + 1 / (p + n - 1))
        coefficient_value = clean(
            coefficient_value * (p + n - 1) / n
        )
    first_base = clean(coefficient_value * x ** (ORDER + 1))
    first_tangent = clean(
        q * coefficient_value * harmonic * x ** (ORDER + 1)
    )
    ratio_base = clean(x * (p + ORDER + 1) / (ORDER + 2))
    ratio_tangent = clean(x * (ORDER + 1 + 2 * p) / (ORDER + 2))
    if not (0 <= ratio_base < 1 and 0 <= ratio_tangent < 1):
        raise RuntimeError("Levelt tail ratio is not contractive")
    return {
        "base_rows": base_rows,
        "tangent_rows": tangent_rows,
        "majorant_base": majorant_base,
        "majorant_tangent": majorant_tangent,
        "finite_inverse_bounds": finite_inverse_bounds,
        "residue_bound": residue_bound,
        "f1_bound": f1_bound,
        "p": p,
        "q": q,
        "x": x,
        "first_base": first_base,
        "first_tangent": first_tangent,
        "ratio_base": ratio_base,
        "ratio_tangent": ratio_tangent,
        "tail_base": clean(first_base / (1 - ratio_base)),
        "tail_tangent": clean(first_tangent / (1 - ratio_tangent)),
    }


def realify_column(value: sp.Matrix) -> sp.Matrix:
    real = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[0])
    )
    imag = value.applyfunc(
        lambda entry: clean(sp.expand_complex(entry).as_real_imag()[1])
    )
    return real.col_join(imag)


def render_builders(data: dict) -> str:
    renderer = ForgeExpression()
    base_seed = realify_column(data["base_seed"])
    tangent_seed = realify_column(data["tangent_seed"])
    matrices = [
        complex_to_real(
            data[key].subs(RHO, R - 2)
        ).subs({R: FORGE_R, W: FORGE_W})
        for key in ("base", "tangent", "direct")
    ]
    seed_values = [
        value.subs({W: FORGE_W})
        for value in list(base_seed) + list(tangent_seed)
    ]
    matrix_values: list[sp.Expr] = []
    matrix_locations: list[list[tuple[int, int, int]]] = []
    for value in matrices:
        current = []
        for row in range(value.rows):
            for col in range(value.cols):
                if value[row, col] != 0:
                    current.append((row, col, len(matrix_values)))
                    matrix_values.append(value[row, col])
        matrix_locations.append(current)
    replacements, reduced = sp.cse(
        seed_values + matrix_values, symbols=sp.numbered_symbols("v")
    )
    lines = [
        "fn build_levelt(w_model:borrow IvTaylor4Mat,"
        "r_model:borrow IvTaylor4Mat)->LeveltData{"
    ]
    for symbol, expression in replacements:
        lines.append(
            f"  let {symbol}:IvTaylor4Mat={renderer.render(expression)};"
        )
    lines.extend(
        [
            "  let seed_base:IvTaylor4Mat=jt_zero(8,1);",
            "  let seed_tangent:IvTaylor4Mat=jt_zero(8,1);",
            "  let base:IvTaylor4Mat=jt_zero(8,8);",
            "  let tangent:IvTaylor4Mat=jt_zero(8,8);",
            "  let direct:IvTaylor4Mat=jt_zero(12,12);",
        ]
    )
    for index in range(8):
        lines.append(
            "  seed_base=jt_put(seed_base,"
            f"{index},0,{renderer.render(reduced[index])});"
        )
        lines.append(
            "  seed_tangent=jt_put(seed_tangent,"
            f"{index},0,{renderer.render(reduced[8 + index])});"
        )
    offset = len(seed_values)
    for name, current in zip(("base", "tangent", "direct"), matrix_locations):
        for row, col, index in current:
            lines.append(
                f"  {name}=jt_put({name},{row},{col},"
                f"{renderer.render(reduced[offset + index])});"
            )
    lines.append(
        "  return new LeveltData(seed_base,seed_tangent,base,tangent,direct);"
    )
    lines.append("}")
    return "\n".join(lines)


EXTRA_SUPPORT = r'''
pub type LeveltData=scoped struct{
  pub seed_base:IvTaylor4Mat,
  pub seed_tangent:IvTaylor4Mat,
  pub base:IvTaylor4Mat,
  pub tangent:IvTaylor4Mat,
  pub direct:IvTaylor4Mat,
};

fn direct_seed_vector(base:borrow IvTaylor4Mat,
tangent:borrow IvTaylor4Mat)->IvTaylor4Mat{
  let out:IvTaylor4Mat=jt_zero(12,1);
  let i:i64=0;while(i<2){
    out=jt_put(out,i,0,jt_scalar(tangent,i,0));
    out=jt_put(out,i+2,0,jt_scalar(base,i,0));
    out=jt_put(out,i+4,0,jt_scalar(base,i+2,0));
    out=jt_put(out,i+6,0,jt_scalar(tangent,i+4,0));
    out=jt_put(out,i+8,0,jt_scalar(base,i+4,0));
    out=jt_put(out,i+10,0,jt_scalar(base,i+6,0));
    i=i+1;}
  return out;
}
'''


MAIN_TEMPLATE = r'''
pub fn main()->i64{
  let w_model:IvTaylor4Mat=jt_frequency();
  let r_model:IvTaylor4Mat=jt_radius();
  let data:LeveltData=build_levelt(w_model,r_model);
  let seed_base:IvTaylor4Mat=jt_pad(data.seed_base,@@BASE_TAIL@@);
  let seed_tangent:IvTaylor4Mat=jt_pad(
    data.seed_tangent,@@TANGENT_TAIL@@);
  let h:Rat=big("1/1073741824");
  let order:i64=12;
  let dual:DualT4=dual_series(data.base,data.tangent,h,order);
  let expanded:IvTaylor4Mat=dual_expand(dual);
  let direct:IvTaylor4Mat=jt_series(data.direct,h,order);
  let hull:IvMat=match(ivtm4_hull_checked(data.direct)){
    some(x)=>x,none=>{println("LEVELT_PANEL_HULL_REFUSAL");return 3;}};
  let alpha:f64=sl_inf_norm_hi(hull);
  let scaled_norm:f64=rat_to_f64(h)*alpha;
  let operator_tail:f64=sl_exp_tail(scaled_norm,order+1);
  if(!f64_is_finite(operator_tail)||operator_tail<0.0){
    println(strfmt(system_allocator(),
      "LEVELT_PANEL_TAIL_REFUSAL alpha={} scaled_norm={} tail={}",
      [alpha,scaled_norm,operator_tail]));return 3;}
  let expanded_padded:IvTaylor4Mat=jt_pad(expanded,operator_tail);
  let direct_padded:IvTaylor4Mat=jt_pad(direct,operator_tail);
  let coefficient_equal:bool=coefficients_equal(expanded,direct);
  let transport_overlap:bool=difference_contains_zero(
    expanded_padded,direct_padded);
  let initial:IvTaylor4Mat=direct_seed_vector(
    seed_base,seed_tangent);
  let jet_out:IvTaylor4Mat=jt_mul(expanded_padded,initial);
  let direct_out:IvTaylor4Mat=jt_mul(direct_padded,initial);
  let seed_overlap:bool=difference_contains_zero(jet_out,direct_out);
  println(strfmt(system_allocator(),
    "SPIN_ONE_LEVELT_PANEL status={} coefficient_equal={} transport_overlap={} seed_overlap={} alpha={} scaled_norm={} operator_tail={} base_width={} tangent_width={}",
    [if(coefficient_equal&&transport_overlap&&seed_overlap){"PASS"}else{"REFUSED"},
     coefficient_equal,transport_overlap,seed_overlap,alpha,scaled_norm,
     operator_tail,hull_width(seed_base),hull_width(seed_tangent)]));
  return if(coefficient_equal&&transport_overlap&&seed_overlap){0}else{3};
}
'''


def render_source(data: dict, tail: dict) -> str:
    base_tail = math.nextafter(float(tail["tail_base"]), math.inf)
    tangent_tail = math.nextafter(
        float(tail["tail_tangent"]), math.inf
    )
    main = MAIN_TEMPLATE.replace("@@BASE_TAIL@@", repr(base_tail)).replace(
        "@@TANGENT_TAIL@@", repr(tangent_tail)
    )
    return SUPPORT + "\n" + EXTRA_SUPPORT + "\n" + render_builders(data) + "\n" + main


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
        r"SPIN_ONE_LEVELT_PANEL status=(?P<status>\w+) "
        r"coefficient_equal=(?P<coefficient>true|false) "
        r"transport_overlap=(?P<transport>true|false) "
        r"seed_overlap=(?P<seed>true|false) "
        r"alpha=(?P<alpha>[-+0-9.eE]+) "
        r"scaled_norm=(?P<scaled>[-+0-9.eE]+) "
        r"operator_tail=(?P<tail>[-+0-9.eE]+) "
        r"base_width=(?P<base>[-+0-9.eE]+) "
        r"tangent_width=(?P<tangent>[-+0-9.eE]+)",
        output,
    )
    if not match:
        return None
    values = match.groupdict()
    return {
        "status": values["status"],
        "coefficient_equal": values["coefficient"] == "true",
        "transport_overlap": values["transport"] == "true",
        "seed_overlap": values["seed"] == "true",
        "alpha": values["alpha"],
        "scaled_norm": values["scaled"],
        "operator_tail": values["tail"],
        "base_width": values["base"],
        "tangent_width": values["tangent"],
    }


def document() -> dict:
    imported = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    data = exact_data(imported["partial_jet_crosswalk"])
    tail = tail_majorant(data)
    SOURCE.write_text(render_source(data, tail))
    env = dict(os.environ)
    env["FORGE_LIB"] = str(FORGE_LIB)
    compile_result = run([str(FORGE), "-o", str(BINARY), str(SOURCE)], env)
    COMPILE_LOG.write_text(compile_result["output"])
    run_result = {"command": str(BINARY), "exit": None, "output": ""}
    if compile_result["exit"] == 0:
        run_result = run([str(BINARY)])
    RUN_LOG.write_text(run_result["output"])
    parsed = parse_run(run_result["output"])
    passed = (
        compile_result["exit"] == 0
        and run_result["exit"] == 0
        and parsed is not None
        and parsed["status"] == "PASS"
        and parsed["coefficient_equal"]
        and parsed["transport_overlap"]
        and parsed["seed_overlap"]
    )
    if not passed:
        raise RuntimeError("spin-one Levelt first-panel rail refused")
    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in {**INPUTS, **CODE_INPUTS}.items()
    }
    return {
        "schema": "phase3-axial-partial-jet-horizon-spin-one-levelt-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_HORIZON_SPIN_ONE_LEVELT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "CERTIFIED_SPIN_ONE_LEVELT_TAIL_AND_MIXED_FIRST_PANEL_PASS",
        "imports": imports,
        "scope": {
            "frequency_child": ["1/2", "4097/8192"],
            "horizon_coordinate": "rho=r-2",
            "seed_radius": "1/4194304",
            "panel_width": "1/1073741824",
            "frobenius_order": ORDER,
            "transport_order": 12,
            "arithmetic": "exact Levelt recurrence plus IvTaylor4_omega tensor dual_tau",
        },
        "levelt_frame": {
            "original_spin_one_state": "Z",
            "regular_spin_one_state": "Zhat=diag(rho,rho**2)*Z",
            "common_selected_column_scaling": "Xhat=rho*X; Yhat=rho*Y",
            "spin_two_block": "A+I/rho",
            "spin_one_block": "T_prime*T_inverse+T*A_x*T_inverse",
            "regular_D": [[enc(x) for x in row] for row in data["d_regular"].tolist()],
            "regular_C": [[enc(x) for x in row] for row in data["c_regular"].tolist()],
            "residue": [[enc(x) for x in row] for row in data["residue"].tolist()],
            "tangent_residue": [
                [enc(x) for x in row]
                for row in data["tangent_residue"].tolist()
            ],
            "characteristic": enc(data["characteristic"]),
            "selected_exponent": "0",
            "selected_vector_Y_then_Z": [enc(x) for x in data["selected"]],
            "tau_moves_exponent": False,
        },
        "resonant_recurrence": {
            "base_equation": "(n*I-R_4)*f_n=sum B_k*f_(n-1-k)",
            "tangent_equation": "(n*I-R_4)*g_n=sum(B_k*g+E_k*f)",
            "normalization": "f_0=(0,0,1,-1); g_0=0",
            "resonance_witnesses": data["resonance"],
            "interpretation": (
                "the order-one free parameter is the regular spin-two shear; "
                "compatibility residual zero excludes a forced logarithm"
            ),
            "base_coefficients": [
                [enc(x) for x in vector] for vector in data["f"]
            ],
            "tangent_coefficients": [
                [enc(x) for x in vector] for vector in data["g"]
            ],
        },
        "all_order_tail_majorant": {
            "cauchy_radius": enc(CAUCHY_RADIUS),
            "pivot_bound_n_ge_2": "||(n*I-R_4)^(-1)||_infinity<=3/n",
            "finite_pivot_checks_n_2_to_12": tail["finite_inverse_bounds"],
            "large_n_residue_norm_bound": enc(tail["residue_bound"]),
            "large_n_neumann_start": 13,
            "analytic_base_row_bounds": [enc(x) for x in tail["base_rows"]],
            "analytic_tangent_row_bounds": [
                enc(x) for x in tail["tangent_rows"]
            ],
            "M_base": enc(tail["majorant_base"]),
            "M_tangent": enc(tail["majorant_tangent"]),
            "resonant_f1_bound": enc(tail["f1_bound"]),
            "p": enc(tail["p"]),
            "q": enc(tail["q"]),
            "x": enc(tail["x"]),
            "tail_base": enc(tail["tail_base"]),
            "tail_tangent": enc(tail["tail_tangent"]),
            "tail_ratio_base_upper": enc(tail["ratio_base"]),
            "tail_ratio_tangent_upper": enc(tail["ratio_tangent"]),
            "passed": True,
        },
        "first_panel_transport": {
            "source_path": str(SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE),
            "compile_log_path": str(COMPILE_LOG.relative_to(ROOT)),
            "compile_log_sha256": sha256(COMPILE_LOG),
            "run_log_path": str(RUN_LOG.relative_to(ROOT)),
            "run_log_sha256": sha256(RUN_LOG),
            "compile_exit": compile_result["exit"],
            "run_exit": run_result["exit"],
            "parsed_result": parsed,
            "direct_route": "12x12 real regular-frame six-state transport",
            "jet_route": "8x8 real four-state base/tangent dual transport",
            "passed": True,
        },
        "remaining_shortfall": {
            "code": "MULTIPANEL_AND_ENDPOINT_NORMALIZER_SHEARS_OPEN",
            "next": (
                "continue the regular-frame shared-omega dual rail across "
                "successive panels and construct the tau-analytic endpoint "
                "normalizer shear K_H"
            ),
        },
        "claim_flags": {
            "spin_one_levelt_frame_exact": True,
            "order_one_resonance_compatible_no_forced_log": True,
            "spin_one_mixed_tail_enclosed": True,
            "mixed_first_panel_transport_certified": True,
            "multipanel_transport_certified": False,
            "K_H_computed": False,
            "endpoint_partial_jet_frame_constructed": False,
            "T_plus_recovered": False,
            "H4_pass_certified": False,
            "bounded_global_transport_certified": False,
        },
        "does_not_establish": [
            "transport beyond the first horizon panel",
            "the endpoint normalizer shear K_H or a complete endpoint jet frame",
            "T_plus, H4, scattering, or bounded global transport",
        ],
    }


def write() -> None:
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-partial-jet-horizon-spin-one-levelt-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_spin_one_levelt_v1.produce --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_spin_one_levelt_v1.verify",
            "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_spin_one_levelt_v1.test_spin_one_levelt",
        ],
        "tiers": {
            "tier0": "required",
            "tier1": "required",
            "tier2": "not run: only one local panel changed",
            "tier3": "not run: no freeze or theorem promotion",
        },
        "claim_boundary": (
            "spin-one Levelt germ, coupled tail and first mixed panel only; "
            "multipanel/K_H/T_plus/H4/global remain open"
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
        print("PASS spin-one Levelt tail and mixed first panel")
    else:
        write()


if __name__ == "__main__":
    main()
