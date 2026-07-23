"""Exact pullback of the literal axial Lee--Wald radial current at infinity.

This module evaluates the action-derived current on the phase-normalized
metric heads that underlie the exact wave-packet traces.  The calculation is
performed in the Schwarzschild ``t`` chart used by the frozen current:

* ``h0_t = h0_v`` and ``h1_t = h1_r + B^{-1} h0_v``;
* a radial derivative at fixed ``t`` is the ingoing-EF radial derivative
  plus ``i*omega/B`` on the positive-frequency slot;
* the conjugate slot carries the opposite frequency and conjugate endpoint
  exponent.

The common nonintegral infinity power is kept in the derivative operator and
cancelled between the two Hermitian slots.  All explicit Laurent series
therefore have integral powers of ``z=1/r``.
"""
from __future__ import annotations

import json
import argparse
import multiprocessing
from functools import lru_cache
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
)
from black_hole_programme.phase3.axial_wavepacket_null_trace.kernel_depth4 import (
    build_kernel_heads,
)


ROOT = Path(__file__).resolve().parents[3]
TRACE = ROOT / "black_hole_programme/phase3/axial_wavepacket_null_trace"
LITERAL = ROOT / "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json"
OUTPUT = Path(__file__).resolve().parent / "formal-grams.json"
I = sp.I
W = sp.Symbol("omega", positive=True, real=True)
Z = sp.Symbol("z", positive=True, real=True)
JET_TRUNCATION = 7


def _parse(text: str, omega: sp.Symbol = W) -> sp.Expr:
    return sp.sympify(text, locals={"omega": omega, "I": I})


def _conjugate(expr: sp.Expr) -> sp.Expr:
    return sp.conjugate(expr).subs(sp.conjugate(W), W)


def _laurent(coefficients: list[str], real_power: int) -> sp.Expr:
    return sp.expand(
        Z ** (-real_power)
        * sum(_parse(value) * Z**n for n, value in enumerate(coefficients))
    )


def _truncate(value: sp.Expr, order: int = JET_TRUNCATION) -> sp.Expr:
    """Canonical Laurent truncation deep enough for the current's constant."""
    return sp.series(value, Z, 0, order).removeO().expand()


def _kernel_h0(label: str, kernel: dict) -> sp.Expr:
    """Reconstruct the reduced Laurent H0 series for a carrier-zero head."""
    system = build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    local = lambda value: _parse(value, omega)
    h1_power = local(kernel["H1_power"])
    shared_imaginary = 0 if label == "EI0" else -4 * I * omega
    real_h1_power = sp.simplify(h1_power - shared_imaginary)
    real_f_power = sp.simplify(local(kernel["F_power"]) - shared_imaginary)
    if not (real_h1_power.is_Integer and real_f_power.is_Integer):
        raise RuntimeError(f"nonintegral reduced kernel power for {label}")
    h1 = Z ** (-int(real_h1_power)) * sum(
        local(value) * Z**n for n, value in enumerate(kernel["H1"])
    )
    f = Z ** (-int(real_f_power)) * sum(
        local(value) * Z**n for n, value in enumerate(kernel["F"])
    )
    substitutions = {
        r: 1 / Z,
        system["states"]["carrier"][0]: 0,
        system["states"]["carrier"][1]: 0,
        system["states"]["carrier"][2]: 0,
        system["states"]["carrier"][3]: 0,
        system["states"]["reduced"][4]: h1,
        system["states"]["reduced"][5]: f,
    }
    return _truncate(sp.cancel(system["h0"].subs(substitutions)).subs(omega, W))


def endpoint_fields(endpoint: str) -> tuple[list[str], dict[str, dict[str, sp.Expr]]]:
    heads = json.loads((TRACE / "depth5-heads.json").read_text())
    kernels = build_kernel_heads()
    if endpoint == "Iminus":
        labels = ["XI0", "XI1", "EI0"]
        shared_rate = sp.Integer(0)
        shared_imaginary_power = sp.Integer(0)
    elif endpoint == "Iplus":
        labels = ["XI2", "XI3", "EI2"]
        shared_rate = -2 * I * W
        shared_imaginary_power = -4 * I * W
    else:
        raise ValueError(endpoint)

    answer: dict[str, dict[str, sp.Expr]] = {}
    for label in labels:
        if label.startswith("XI"):
            branch = heads[label]
            h0_power = sp.simplify(_parse(branch["H0_power"]) - shared_imaginary_power)
            h1_power = sp.simplify(_parse(branch["H1_power"]) - shared_imaginary_power)
            if not (h0_power.is_Integer and h1_power.is_Integer):
                raise RuntimeError(f"nonintegral reduced XI power for {label}")
            h0 = _laurent(branch["H0"], int(h0_power))
            h1_ef = _laurent(branch["H1"], int(h1_power))
        else:
            kernel = kernels[label]
            h1_power = sp.simplify(
                _parse(kernel["H1_power"]) - shared_imaginary_power
            )
            if not h1_power.is_Integer:
                raise RuntimeError(f"nonintegral reduced EI power for {label}")
            h1_ef = _laurent(kernel["H1"], int(h1_power))
            h0 = _kernel_h0(label, kernel)
        B = 1 - 2 * Z
        answer[label] = {
            "h0": _truncate(h0),
            "h1": _truncate(h1_ef + h0 / B),
            "rate": shared_rate,
            "imaginary_power": shared_imaginary_power,
        }
    return labels, answer


def _radial_derivative(
    value: sp.Expr,
    *,
    rate: sp.Expr,
    imaginary_power: sp.Expr,
    frequency_sign: int,
) -> sp.Expr:
    B = 1 - 2 * Z
    return _truncate(
        rate * value
        + imaginary_power * Z * value
        - Z**2 * sp.diff(value, Z)
        + frequency_sign * I * W * value / B
    )


def _jets(field: dict[str, sp.Expr], conjugate_slot: bool) -> dict[tuple[str, int], sp.Expr]:
    if conjugate_slot:
        rate = _conjugate(field["rate"])
        imaginary_power = _conjugate(field["imaginary_power"])
        frequency_sign = -1
        values = {name: _conjugate(field[name]) for name in ("h0", "h1")}
    else:
        rate = field["rate"]
        imaginary_power = field["imaginary_power"]
        frequency_sign = 1
        values = {name: field[name] for name in ("h0", "h1")}
    answer: dict[tuple[str, int], sp.Expr] = {}
    for name, value in values.items():
        answer[(name, 0)] = value
        for order in range(1, 4):
            value = _radial_derivative(
                value,
                rate=rate,
                imaginary_power=imaginary_power,
                frequency_sign=frequency_sign,
            )
            answer[(name, order)] = value
    return answer


@lru_cache(maxsize=1)
def _literal_current() -> tuple[
    sp.Expr, sp.Symbol, dict[sp.Expr, tuple[str, str, int, int]]
]:
    payload = json.loads(LITERAL.read_text())
    t, r, mass, alpha = sp.symbols("t r m alpha")
    functions = {
        name: sp.Function(name) for name in ("h0a", "h1a", "h0b", "h1b")
    }
    expression = sp.sympify(payload["bilinear"]["F_r"], locals={
        "t": t,
        "r": r,
        "m": mass,
        "alpha": alpha,
        "pi": sp.pi,
        "Derivative": sp.Derivative,
        **functions,
    }) / (sp.pi * alpha)
    expression = expression.subs(mass, 1)
    metadata: dict[sp.Expr, tuple[str, str, int, int]] = {}
    atoms = list(expression.atoms(sp.Derivative))
    atoms.extend(functions[name](t, r) for name in functions)
    for atom in atoms:
        if isinstance(atom, sp.Derivative):
            function = atom.expr
            radial_order = sum(
                int(pair[1]) for pair in atom.args[1:] if pair[0] == r
            )
            time_order = sum(
                int(pair[1]) for pair in atom.args[1:] if pair[0] == t
            )
        else:
            function = atom
            radial_order = time_order = 0
        name = str(function.func)
        metadata[atom] = (name[-1], name[:2], radial_order, time_order)
    return expression, r, metadata


def gram_entry(
    left: dict[str, sp.Expr],
    right: dict[str, sp.Expr],
    *,
    series_order: int = 1,
) -> tuple[sp.Expr, dict[int, sp.Expr]]:
    """Return ``i F^r/(pi alpha_W)`` and its visible Laurent coefficients."""
    expression, r, metadata = _literal_current()
    a_jets = _jets(right, conjugate_slot=False)
    b_jets = _jets(left, conjugate_slot=True)
    replacements = {}
    for atom, (side, field, radial_order, time_order) in metadata.items():
        if side == "a":
            value = a_jets[(field, radial_order)] * (I * W) ** time_order
        else:
            value = b_jets[(field, radial_order)] * (-I * W) ** time_order
        replacements[atom] = value
    value = sp.cancel(I * expression.xreplace(replacements).subs(r, 1 / Z))
    expanded = sp.series(
        value, Z, 0, series_order
    ).removeO().expand()
    visible = {
        power: sp.cancel(expanded.coeff(Z, power))
        for power in range(-8, series_order)
        if sp.cancel(expanded.coeff(Z, power)) != 0
    }
    return sp.cancel(visible.get(0, 0)), visible


def _pair_worker(task: tuple[str, int, int]) -> tuple[int, int, sp.Expr, dict[int, sp.Expr]]:
    endpoint, i, j = task
    labels, fields = endpoint_fields(endpoint)
    constant, visible = gram_entry(fields[labels[i]], fields[labels[j]])
    return i, j, constant, visible


def build_formal_gram(endpoint: str, *, jobs: int = 1) -> dict:
    labels, fields = endpoint_fields(endpoint)
    gram: list[list[str | None]] = [[None] * len(labels) for _ in labels]
    valuations: list[list[dict | None]] = [[None] * len(labels) for _ in labels]
    tasks = [
        (endpoint, i, j)
        for i in range(len(labels))
        for j in range(i, len(labels))
    ]
    if jobs > 1:
        with multiprocessing.get_context("spawn").Pool(jobs) as pool:
            results = pool.map(_pair_worker, tasks)
    else:
        results = [_pair_worker(task) for task in tasks]
    for i, j, constant, visible in results:
        gram[i][j] = sp.sstr(constant)
        valuations[i][j] = {
            "first_power": min(visible) if visible else None,
            "nonzero_coefficients": {
                str(power): sp.sstr(value) for power, value in visible.items()
            },
        }
        if i != j:
            gram[j][i] = sp.sstr(_conjugate(constant))
            valuations[j][i] = {
                "first_power": min(visible) if visible else None,
                "nonzero_coefficients": {
                    str(power): sp.sstr(_conjugate(value))
                    for power, value in visible.items()
                },
            }
    return {"basis": labels, "gram_over_pi_alpha": gram, "laurent_audit": valuations}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    document = {
        "normalization": "i*F^r/(pi*alpha_W), before Stokes endpoint orientation",
        "Iminus": build_formal_gram("Iminus", jobs=args.jobs),
        "Iplus": build_formal_gram("Iplus", jobs=args.jobs),
    }
    if args.check:
        if document != json.loads(OUTPUT.read_text()):
            raise SystemExit("formal endpoint Gram drift")
        print("PASS: exact formal endpoint Grams reproduce")
    else:
        OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
