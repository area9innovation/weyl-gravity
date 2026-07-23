"""Independent verifier for the axial wave-packet null-trace shortfall."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
HEADS = ROOT / "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-metric-heads.json"
ENV = ROOT / "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-volterra-envelope.json"
RECON = ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json"
OMEGA = sp.Symbol("omega", positive=True)
I = sp.I


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


def verify_document(document: dict) -> None:
    flags = document["claim_flags"]
    for key in ("wavepacket_trace_constructed", "endpoint_flux_Gram_certified",
                "global_connection_constructed", "scattering_channels_classified",
                "stability_or_CPT_established", "exact_solution_wrong_endpoint_suppression"):
        if flags[key]:
            fail(f"unsupported promotion {key}")
    if document["disposition"]["status"] != "SHORTFALL":
        fail("shortfall hidden")

    audit = document["exact_remainder_derivative_audit"]
    if (audit["minimum_cross_rate_decay_p"], audit["certified_omega_derivatives"],
            audit["first_missing_derivative_order"], audit["orders_needed_by_wrong_endpoint_lemma"],
            audit["required_minimum_decay_p"], audit["minimum_additional_inverse_radius_recurrence_orders"]) != (3, 1, 2, 3, 5, 2):
        fail("derivative-depth theorem changed")
    if not (3 - 1 > 1 and 3 - 2 <= 1 and 5 - 3 > 1):
        fail("integrability inequalities are inconsistent")

    envelope = json.loads(ENV.read_text())
    pmin = min(x for row in envelope["volterra_kernel"]["decay_p_ij"] for x in row if x < 99)
    if pmin != 3:
        fail("imported p-min is not three")

    heads = json.loads(HEADS.read_text())
    printed = document["formal_joint_symbol_bounds"]["bounds_by_branch"]
    for label, branch in heads["branches"].items():
        expressions = []
        for field in ("H0_from_C_equals_zero", "H1", "F_equals_dH1_dr"):
            expressions.extend(_parse(x) for x in branch[field]["coefficients_through_inverse_order_3"])
        if printed[label]["coefficient_count"] != len(expressions):
            fail(f"coefficient count changed for {label}")
        for order, bound_text in enumerate(printed[label]["exact_l1_upper_bounds"]):
            bound = Fraction(bound_text)
            actual = max(_rectangle_bound(sp.diff(value, OMEGA, order)) for value in expressions)
            if actual != bound:
                fail(f"coefficient bound mismatch for {label}, d={order}")
    kernels = json.loads(RECON.read_text())["endpoint_bases"]["infinity"]["Einstein_kernel"]
    for label in ("EI0", "EI2"):
        expressions = [_parse(x) for x in kernels[label]["H1_head"]]
        if printed[label]["coefficient_count"] != len(expressions):
            fail(f"coefficient count changed for {label}")
        for order, bound_text in enumerate(printed[label]["exact_l1_upper_bounds"]):
            actual = max(_rectangle_bound(sp.diff(value, OMEGA, order)) for value in expressions)
            if actual != Fraction(bound_text):
                fail(f"coefficient bound mismatch for {label}, d={order}")

    if document["matching_direction_formal_trace"]["Iminus"]["basis"] != ["XI0", "XI1", "EI0"]:
        fail("Iminus endpoint swap")
    if document["matching_direction_formal_trace"]["Iplus"]["basis"] != ["XI2", "XI3", "EI2"]:
        fail("Iplus endpoint swap")
    for endpoint in ("Iminus", "Iplus"):
        disposition = document["endpoint_flux_disposition"][endpoint]
        if disposition["trace_dimension"] != 3 or disposition["flux_Gram"] != "NOT_CERTIFIED":
            fail(f"physical Gram smuggled into {endpoint}")

    for name, imported in document["imports"].items():
        path = ROOT / imported["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != imported["sha256"]:
            fail(f"import hash drift: {name}")


def main() -> None:
    verify_document(json.loads(CERT.read_text()))
    print("PASS: independent wave-packet shortfall verifier")


if __name__ == "__main__":
    main()
