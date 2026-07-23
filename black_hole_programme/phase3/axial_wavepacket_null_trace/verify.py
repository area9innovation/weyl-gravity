"""Independent verifier for the exact axial wave-packet trace theorem."""
from __future__ import annotations

import hashlib
import json
import argparse
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
)
from black_hole_programme.phase3.axial_wavepacket_null_trace.kernel_depth4 import (
    build_kernel_heads,
)


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
HEADS = HERE / "depth5-heads.json"
ENV = ROOT / "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-volterra-envelope.json"
RECON = ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json"
DIFF = HERE / "differentiated-envelope.json"
OMEGA = sp.Symbol("omega", positive=True)
I = sp.I

EXPECTED_A4_A5 = {
    "XI0": (
        "(-205*omega+494*I)/(16*omega**5)",
        "I*(6169*omega**2-7278*I*omega+1512)/(96*omega**7)",
    ),
    "XI1": (
        "-I*(205*omega**2+402*I*omega+840)/(32*omega**5)",
        "-(10369*omega**2-10782*I*omega+13608)/(192*omega**6)",
    ),
    "XI2": (
        "-(49152*omega**9-86016*I*omega**8-138240*omega**7+125184*I*omega**6+104064*omega**5-56736*I*omega**4-27460*omega**3+8989*I*omega**2+2114*omega-360*I)/(12*omega**3)",
        "-I*(262144*omega**11-720896*I*omega**10-1277952*omega**9+1474560*I*omega**8+1366016*omega**7-937984*I*omega**6-520448*omega**5+225040*I*omega**4+70660*omega**3-17510*I*omega**2-2075*omega+180*I)/(30*omega**4)",
    ),
    "XI3": (
        "I*(12288*omega**8-18432*I*omega**7-23808*omega**6+16128*I*omega**5+10080*omega**4-3600*I*omega**3-733*omega**2+168*I*omega-36)/(48*omega**3)",
        "-(32768*omega**9-81920*I*omega**8-122880*omega**7+112640*I*omega**6+81152*omega**5-40640*I*omega**4-13680*omega**3+3670*I*omega**2+95*omega+30*I)/(60*omega**3)",
    ),
}


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def _parse(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"omega": OMEGA, "I": I})


def _rectangle_bound(expr: sp.Expr) -> Fraction:
    """Independent Bernstein-free rectangle bound for a Laurent polynomial."""
    expr = sp.cancel(expr)
    num, den = sp.fraction(expr)
    dterms = sp.Poly(den, OMEGA).terms()
    if len(dterms) != 1:
        fail(f"nonmonomial denominator {den}")
    (q,), scale = dterms[0]
    scale = sp.Rational(scale)
    total = Fraction(0)
    for (power,), coeff in sp.Poly(sp.expand(num), OMEGA).terms():
        re, im = sp.expand_complex(coeff).as_real_imag()
        for part in (sp.Rational(re), sp.Rational(im)):
            total += Fraction(abs(int(part.p)), int(part.q)) * Fraction(3, 4) ** power
    return total * 2**q / Fraction(abs(int(scale.p)), int(scale.q))


def _derivative(value: sp.Expr, rate: sp.Expr, power: sp.Expr,
                z: sp.Symbol) -> sp.Expr:
    return sp.expand(rate*value + power*z*value - z**2*sp.diff(value, z))


def _valuation(value: sp.Expr, z: sp.Symbol, order: int = 11) -> int:
    expansion = sp.series(value, z, 0, order).removeO().expand()
    for power in range(-4, order):
        if sp.cancel(expansion.coeff(z, power)) != 0:
            return power
    return 10**6


def verify_depth_five_heads(heads: dict) -> None:
    """Independent exact recurrence and reconstruction rail.

    Closed A4/A5 formulae are compared symbolically.  The full six-state
    residual and algebraic H0 reconstruction are then evaluated with exact
    rational arithmetic at an interior frequency.  This is independent of
    the slow linear solver that produced the frozen head artifact.
    """
    if tuple(heads) != ("XI0", "XI1", "XI2", "XI3"):
        fail("depth-five branch inventory changed")
    system = build_exact_system()
    omega = system["symbols"]["omega"]
    r = system["symbols"]["r"]
    z = sp.Symbol("z")
    flow = system["flow6"].subs(r, 1/z)
    test_frequency = sp.Rational(5, 8)
    expected_valuations = (8, 7, 5, 4)
    local_parse = lambda text: _parse(text).xreplace({OMEGA: omega})

    for index, (label, branch) in enumerate(heads.items()):
        if branch["carrier_depth"] != 8:
            fail(f"carrier depth is not eight for {label}")
        if (len(branch["H0"]), len(branch["H1"])) != (6, 6):
            fail(f"metric depth changed for {label}")
        if len(branch["F"]) != (7 if label in ("XI2", "XI3") else 6):
            fail(f"F depth changed for {label}")
        for offset, expected in enumerate(EXPECTED_A4_A5[label], start=4):
            if sp.cancel(local_parse(branch["H1"][offset]) - local_parse(expected)) != 0:
                fail(f"independent A{offset} mismatch for {label}")

        rate = local_parse(branch["rate"])
        carrier_power = local_parse(branch["carrier_power"])
        h1_power = local_parse(branch["H1_power"])
        h0_power = local_parse(branch["H0_power"])
        f_power = local_parse(branch["F_power"])
        p_series = sum(local_parse(value)*z**n for n, value in enumerate(branch["carrier_P"]))
        q_series = sum(local_parse(value)*z**n for n, value in enumerate(branch["carrier_Q"]))
        h1_series = sum(local_parse(value)*z**n for n, value in enumerate(branch["H1"]))
        f_series = sum(local_parse(value)*z**n for n, value in enumerate(branch["F"]))

        differentiated = sp.expand(
            z**(f_power - h1_power)*_derivative(
                h1_series, rate, h1_power, z
            )
        )
        for n, printed in enumerate(branch["F"]):
            if sp.cancel(differentiated.coeff(z, n) - local_parse(printed)) != 0:
                fail(f"derivative-forced F mismatch for {label}, n={n}")

        substitutions = {omega: test_frequency}
        rate_n = rate.subs(substitutions)
        cp_n = carrier_power.subs(substitutions)
        hp_n = h1_power.subs(substitutions)
        fp_n = f_power.subs(substitutions)
        p_n = p_series.subs(substitutions)
        q_n = q_series.subs(substitutions)
        h1_n = h1_series.subs(substitutions)
        f_n = f_series.subs(substitutions)
        column = sp.Matrix([
            p_n,
            _derivative(p_n, rate_n, cp_n, z),
            q_n,
            _derivative(q_n, rate_n, cp_n, z),
            z**(cp_n - hp_n)*h1_n,
            z**(cp_n - fp_n)*f_n,
        ])
        residual = column.applyfunc(
            lambda value: _derivative(value, rate_n, cp_n, z)
        ) - flow.subs(substitutions)*column
        actual_valuation = _valuation(residual[5], z)
        if actual_valuation != expected_valuations[index]:
            fail(
                f"raw lower residual valuation for {label}: "
                f"{actual_valuation} != {expected_valuations[index]}"
            )

        relative = z**(hp_n - cp_n)
        h0_exact = system["h0"].subs({
            r: 1/z,
            omega: test_frequency,
            system["states"]["carrier"][0]: relative*p_n,
            system["states"]["carrier"][1]: relative*_derivative(
                p_n, rate_n, cp_n, z
            ),
            system["states"]["carrier"][2]: relative*q_n,
            system["states"]["carrier"][3]: relative*_derivative(
                q_n, rate_n, cp_n, z
            ),
            system["states"]["reduced"][4]: h1_n,
            system["states"]["reduced"][5]: z**(hp_n - fp_n)*f_n,
        })
        printed_h0 = sum(
            local_parse(value).subs(substitutions)*z**n
            for n, value in enumerate(branch["H0"])
        )
        difference = sp.series(
            z**(h0_power.subs(substitutions) - hp_n)*h0_exact - printed_h0,
            z, 0, 6,
        ).removeO().expand()
        if any(sp.cancel(difference.coeff(z, n)) != 0 for n in range(6)):
            fail(f"algebraic H0 reconstruction mismatch for {label}")


def verify_document(document: dict, *, deep: bool = False) -> None:
    flags = document["claim_flags"]
    for key in ("endpoint_flux_Gram_certified", "global_connection_constructed",
                "scattering_channels_classified", "stability_or_CPT_established"):
        if flags[key]:
            fail(f"unsupported promotion {key}")
    for key in ("full_six_column_p_at_least_five",
                "exact_solution_wrong_endpoint_suppression",
                "wavepacket_trace_constructed"):
        if not flags[key]:
            fail(f"proved result hidden: {key}")
    if document["disposition"]["status"] != "SHORTFALL":
        fail("shortfall hidden")

    audit = document["exact_remainder_derivative_audit"]
    if (audit["minimum_cross_rate_decay_p"], audit["certified_omega_derivatives"],
            audit["first_missing_derivative_order"], audit["orders_needed_by_wrong_endpoint_lemma"],
            audit["required_minimum_decay_p"], audit["minimum_additional_inverse_radius_recurrence_orders"]) != (5, 3, None, 3, 5, 0):
        fail("derivative-depth theorem changed")
    if not (5 - 3 > 1):
        fail("integrability inequalities are inconsistent")

    envelope = json.loads(ENV.read_text())
    pmin = min(x for row in envelope["volterra_kernel"]["decay_p_ij"] for x in row if x < 99)
    if pmin != 3:
        fail("imported p-min is not three")

    repaired = audit["repaired_decay_p_ij"]
    if repaired != [
        [10, 11, 10, 11, 99, 99],
        [9, 10, 9, 10, 99, 99],
        [10, 11, 10, 11, 99, 99],
        [9, 10, 9, 10, 99, 99],
        [5, 6, 5, 5, 6, 5],
        [6, 7, 6, 6, 7, 6],
    ]:
        fail("repaired decay table mismatch")
    if audit["status"] != "PASS" or audit["first_failure"] is not None:
        fail("closed differentiated-envelope gate reported open")

    heads = json.loads(HEADS.read_text())
    if deep:
        verify_depth_five_heads(heads)
    printed = document["formal_joint_symbol_bounds"]["bounds_by_branch"]
    for label, branch in heads.items():
        expressions = []
        for field in ("H0", "H1", "F"):
            expressions.extend(_parse(x) for x in branch[field])
        if printed[label]["coefficient_count"] != len(expressions):
            fail(f"coefficient count changed for {label}")
        for order, bound_text in enumerate(printed[label]["exact_l1_upper_bounds"]):
            bound = Fraction(bound_text)
            actual = max(_rectangle_bound(sp.diff(value, OMEGA, order)) for value in expressions)
            if actual != bound:
                fail(f"coefficient bound mismatch for {label}, d={order}")
    kernels = build_kernel_heads()
    expected_kernel_a4 = {
        "EI0": -45*(OMEGA - 2*I)/(8*OMEGA**3),
        "EI2": (4096*OMEGA**7 - 10240*I*OMEGA**6 - 14080*OMEGA**5
                + 10496*I*OMEGA**4 + 5920*OMEGA**3 - 2016*I*OMEGA**2
                - 531*OMEGA + 90*I)/(24*OMEGA**3),
    }
    for label in ("EI0", "EI2"):
        if sp.cancel(_parse(kernels[label]["H1"][4]) - expected_kernel_a4[label]) != 0:
            fail(f"kernel A4 recurrence repair changed for {label}")
        expressions = [
            _parse(x) for field in ("H1", "F") for x in kernels[label][field]
        ]
        if printed[label]["coefficient_count"] != len(expressions):
            fail(f"coefficient count changed for {label}")
        for order, bound_text in enumerate(printed[label]["exact_l1_upper_bounds"]):
            actual = max(_rectangle_bound(sp.diff(value, OMEGA, order)) for value in expressions)
            if actual != Fraction(bound_text):
                fail(f"coefficient bound mismatch for {label}, d={order}")
    # The formerly leading EI2 obstruction cannot disappear accidentally on
    # the pilot interval: its imaginary numerator has no root there.
    old_ei2_imaginary = (
        -10240*OMEGA**6 + 10496*OMEGA**4 - 2016*OMEGA**2 + 90
    )
    if sp.count_roots(old_ei2_imaginary, sp.Rational(1, 2), sp.Rational(3, 4)) != 0:
        fail("old EI2 leading coefficient acquired a pilot-interval zero")
    if old_ei2_imaginary.subs(OMEGA, sp.Rational(1, 2)) != 82:
        fail("EI2 Sturm sign sentinel changed")

    if document["matching_direction_wavepacket_trace"]["Iminus"]["basis"] != ["XI0", "XI1", "EI0"]:
        fail("Iminus endpoint swap")
    if document["matching_direction_wavepacket_trace"]["Iplus"]["basis"] != ["XI2", "XI3", "EI2"]:
        fail("Iplus endpoint swap")
    for endpoint in ("Iminus", "Iplus"):
        disposition = document["endpoint_flux_disposition"][endpoint]
        if disposition["trace_dimension"] != 3 or disposition["flux_Gram"] != "NOT_CERTIFIED":
            fail(f"physical Gram smuggled into {endpoint}")

    depth = document["depth_five_recurrence"]
    if depth["carrier_depth_required_for_H1_A5"] != 8:
        fail("source-pole carrier-depth gate missing")
    if depth["exact_raw_lower_residual_valuations"] != [8, 7, 5, 4]:
        fail("exact XI residual valuations changed")

    diff = json.loads(DIFF.read_text())
    printed_diff = document["differentiated_volterra_envelope"]
    if diff["decay_p_ij"] != repaired:
        fail("differentiated-envelope decay table drift")
    if diff["exact_raw_residual_valuations"] != {
            "Rc": [10, 10, 10, 10], "Rk": [6, 6], "Rm": [8, 7, 5, 4]}:
        fail("differentiated-envelope residual valuation drift")
    if printed_diff["q_derivative_strict_upper_bounds"] != [
            "2^-16356", "2^-12252", "2^-8148", "2^-4042"]:
        fail("Volterra contraction bounds changed")
    if printed_diff["correction_derivative_integer_ceilings"] != [2, 1, 2, 4]:
        fail("correction derivative bounds changed")

    for name, imported in document["imports"].items():
        path = ROOT / imported["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != imported["sha256"]:
            fail(f"import hash drift: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deep", action="store_true",
        help="also replay the expensive exact six-state residual/H0 rail",
    )
    args = parser.parse_args()
    verify_document(json.loads(CERT.read_text()), deep=args.deep)
    suffix = " with deep recurrence replay" if args.deep else ""
    print("PASS: independent exact wave-packet trace verifier" + suffix)


if __name__ == "__main__":
    main()
