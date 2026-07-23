"""Produce the exact Phase-3 axial wave-packet null-trace audit.

The package proves the scalar nonstationary-phase estimate and applies it to
the *finite formal heads*.  It then audits the already-certified Volterra
remainder.  The audit is deliberately fail-closed: the present cross-rate
remainder has only ``p=3`` decay, hence has one absolutely integrable
frequency derivative but not the three required to suppress the largest
``r^2`` metric head.  The output is therefore a precise SHORTFALL and a
minimum recurrence-depth theorem, not a wave-packet phase-space claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = HERE / "schema.json"

INPUTS = {
    "null_trace_preflight": "black_hole_programme/phase3/axial_null_infinity_trace_preflight/certificate.json",
    "metric_heads": "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-metric-heads.json",
    "volterra_envelope": "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-volterra-envelope.json",
    "endpoint_bases": "black_hole_programme/phase3/axial_endpoint_bases/certificate.json",
    "reconstruction": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
}

OMEGA = sp.Symbol("omega", positive=True)
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"omega": OMEGA, "I": I})


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def rational_l1_bound(value: sp.Expr) -> Fraction:
    """Exact l1 bound on |value| for 1/2 <= omega <= 3/4.

    All imported formal-head coefficients and their first three derivatives
    have a monomial denominator c*omega**q.  Expanding the numerator and
    using |omega|<=3/4, |omega|^-1<=2 and |a+ib|<=|a|+|b| gives a rational
    upper bound.  Refusing a non-monomial denominator makes the pole audit
    explicit rather than numerical.
    """
    value = sp.cancel(value)
    numerator, denominator = sp.fraction(value)
    poly_den = sp.Poly(denominator, OMEGA)
    terms_den = poly_den.terms()
    if len(terms_den) != 1:
        raise RuntimeError(f"nonmonomial denominator: {denominator}")
    (q,), c = terms_den[0]
    c = sp.Rational(c)
    if c == 0:
        raise RuntimeError("zero denominator coefficient")
    total = Fraction(0)
    for (k,), coeff in sp.Poly(sp.expand(numerator), OMEGA).terms():
        re, im = sp.expand_complex(coeff).as_real_imag()
        re_q, im_q = sp.Rational(re), sp.Rational(im)
        size = Fraction(abs(int(re_q.p)), int(re_q.q)) + Fraction(abs(int(im_q.p)), int(im_q.q))
        total += size * Fraction(3, 4) ** k
    return total * Fraction(2) ** q / Fraction(abs(int(c.p)), int(c.q))


def formal_head_bounds(metric_heads: dict, reconstruction: dict) -> dict:
    expressions: dict[str, list[sp.Expr]] = {}
    for label, branch in metric_heads["branches"].items():
        values: list[sp.Expr] = []
        for field in ("H0_from_C_equals_zero", "H1", "F_equals_dH1_dr"):
            values.extend(parse(item) for item in branch[field]["coefficients_through_inverse_order_3"])
        expressions[label] = values
    kernels = reconstruction["endpoint_bases"]["infinity"]["Einstein_kernel"]
    for label in ("EI0", "EI2"):
        expressions[label] = [parse(item) for item in kernels[label]["H1_head"]]

    answer = {}
    for label, values in expressions.items():
        derivative_bounds = []
        for order in range(4):
            derivative_bounds.append(fraction_text(max(
                rational_l1_bound(sp.diff(value, OMEGA, order))
                for value in values
            )))
        answer[label] = {
            "coefficient_count": len(values),
            "derivative_orders": [0, 1, 2, 3],
            "exact_l1_upper_bounds": derivative_bounds,
            "only_real_pole": "omega=0 (outside the compact pilot support)",
        }
    return answer


def build_document() -> dict:
    imported = {name: json.loads((ROOT / path).read_text()) for name, path in INPUTS.items()}
    preflight = imported["null_trace_preflight"]
    envelope = imported["volterra_envelope"]
    heads = imported["metric_heads"]
    reconstruction = imported["reconstruction"]

    if preflight["endpoint_polarizations"]["Iminus_incoming_rate_zero"] != ["XI0", "XI1", "EI0"]:
        raise RuntimeError("Iminus polarization drift")
    if preflight["endpoint_polarizations"]["Iplus_outgoing_rate_minus_2Iomega"] != ["XI2", "XI3", "EI2"]:
        raise RuntimeError("Iplus polarization drift")
    decay = envelope["volterra_kernel"]["decay_p_ij"]
    finite_decay = [entry for row in decay for entry in row if entry < 99]
    p_min = min(finite_decay)
    if p_min != 3:
        raise RuntimeError(f"cross-rate minimum decay changed: {p_min}")

    maximum_metric_weight = 2
    ibp_orders = maximum_metric_weight + 1
    certified_omega_derivatives = p_min - 2
    first_missing_derivative = certified_omega_derivatives + 1
    required_decay = ibp_orders + 2
    additional_orders = required_decay - p_min
    if (ibp_orders, certified_omega_derivatives, first_missing_derivative,
            required_decay, additional_orders) != (3, 1, 2, 5, 2):
        raise RuntimeError("derivative-depth arithmetic changed")

    return {
        "schema": "phase3-black-hole-axial-wavepacket-null-trace-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_WAVEPACKET_NULL_TRACE_SHORTFALL_V1",
        "result_token": "FORMAL_HEAD_NONSTATIONARY_SUPPRESSION_EXACT_REMAINDER_C2_MISSING",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior, M=1, ingoing Eddington-Finkelstein convention exp(+I*omega*v)",
            "sector": "axial ell=2",
            "frequency_profiles": "C_c^infinity((1/2,3/4)); negative frequencies fixed by the real-field involution",
            "endpoint_split": {
                "Iminus_matching": ["XI0", "XI1", "EI0"],
                "Iplus_matching": ["XI2", "XI3", "EI2"],
            },
        },
        "scalar_nonstationary_phase_lemma": {
            "statement": "If b is C_c^N((1/2,3/4)) and Phi has constant nonzero omega derivative L, then |integral exp(I*omega*L)b(omega)domega| <= |L|^(-N)*||d_omega^N b||_L1.",
            "proof": "Integrate by parts N times. Every boundary term vanishes because b has compact support in the open interval.",
            "wrong_endpoint_phases": {
                "rate_zero_at_fixed_u": "exp(I*omega*(u+2*r_star)); L=u+2*r_star",
                "rate_minus_2Iomega_at_fixed_v": "exp(I*omega*(v-2*r-4*log(r))); L=v-2*r-4*log(r)",
                "nonstationarity": "For fixed u or v, |L| is bounded below by r for all sufficiently large r.",
            },
            "maximum_formal_metric_weight": maximum_metric_weight,
            "minimum_IBP_orders_for_vanishing": ibp_orders,
            "formal_head_consequence": "Every displayed wrong-endpoint finite head vanishes after three integrations by parts, including the r^2 metric heads.",
        },
        "formal_joint_symbol_bounds": {
            "frequency_interval": ["1/2", "3/4"],
            "method": "exact rational l1 coefficient bound using omega<=3/4 and omega^(-1)<=2",
            "bounds_by_branch": formal_head_bounds(heads, reconstruction),
            "pole_statement": "Every displayed coefficient and its first three omega derivatives is uniformly bounded; the only real denominator zero is omega=0, outside the profile support.",
        },
        "matching_direction_formal_trace": {
            "Iminus": {
                "fixed_coordinate": "v",
                "dimension": 3,
                "basis": ["XI0", "XI1", "EI0"],
                "phase": "exp(I*omega*v)",
            },
            "Iplus": {
                "fixed_coordinate": "u",
                "dimension": 3,
                "basis": ["XI2", "XI3", "EI2"],
                "phase": "2^(-4*I*omega)*exp(I*omega*u)",
                "finite_radius_factor": "(1-2/r)^(4*I*omega) -> 1 uniformly in omega",
            },
            "limit_integral_interchange_for_heads": "The finite formal heads obey uniform coefficient bounds on compact frequency support, so dominated convergence applies after the declared columnwise radiation rescaling.",
            "status": "FORMAL_HEAD_TRACE_ONLY",
        },
        "exact_remainder_derivative_audit": {
            "imported_kernel_bound": "|K_N,ij(r,omega)| <= C_ij*r^(-p_ij)",
            "minimum_cross_rate_decay_p": p_min,
            "phase_derivative_rule": "Each omega derivative of exp(+/-2*I*omega*r)*r^(+/-4*I*omega) costs at most one power of r (log r is subleading).",
            "absolute_decay_after_k_derivatives": "r^(-(p-k)) up to logarithms",
            "integrability_condition": "p-k>1",
            "certified_omega_derivatives": certified_omega_derivatives,
            "first_missing_derivative_order": first_missing_derivative,
            "first_failure": "At k=2 and p=3 the absolute Volterra majorant is r^(-1) times logarithms and is not integrable.",
            "orders_needed_by_wrong_endpoint_lemma": ibp_orders,
            "required_minimum_decay_p": required_decay,
            "minimum_additional_inverse_radius_recurrence_orders": additional_orders,
            "required_extension": "Extend H0 and H1 from inverse order 3 through inverse order 5, retain the derivative-forced F coefficient through inverse order 6, and reprove a cross-rate p>=5 Volterra envelope with omega derivatives k=0,1,2,3.",
        },
        "endpoint_flux_disposition": {
            "Iminus": {"trace_dimension": 3, "flux_Gram": "NOT_CERTIFIED", "radical": "UNDEFINED", "quotient_dimension": "UNDEFINED", "inertia": "UNDEFINED"},
            "Iplus": {"trace_dimension": 3, "flux_Gram": "NOT_CERTIFIED", "radical": "UNDEFINED", "quotient_dimension": "UNDEFINED", "inertia": "UNDEFINED"},
            "reason": "The exact three-derivative remainder estimate needed to pass from formal heads to a bounded wave-packet trace is absent; a formal fixed-frequency Gram is not promoted as a physical null-flux Gram.",
            "orientation": "Iplus and Iminus retain separate outward-normal conventions; they are never combined into one local endpoint test.",
            "reality": "a_{ell,-m}(-omega)=(-1)^m*conjugate(a_{ell,m}(omega)); only positive-frequency amplitudes are independent.",
        },
        "disposition": {
            "status": "SHORTFALL",
            "what_is_proved": "Exact all-order scalar IBP lemma, its six-head formal application, uniform exact coefficient bounds through three omega derivatives, and the first missing remainder derivative with minimum recurrence depth.",
            "missing_dependency": "Two additional exact infinity recurrence orders and a p>=5 omega-differentiated Volterra envelope.",
        },
        "claim_flags": {
            "scalar_nonstationary_phase_lemma": True,
            "formal_head_wrong_endpoint_suppression": True,
            "formal_head_joint_symbol_bounds_through_order_three": True,
            "matching_direction_formal_trace_dimension": True,
            "exact_solution_wrong_endpoint_suppression": False,
            "wavepacket_trace_constructed": False,
            "endpoint_flux_Gram_certified": False,
            "global_connection_constructed": False,
            "scattering_channels_classified": False,
            "stability_or_CPT_established": False,
        },
        "does_not_establish": [
            "a bounded exact-solution trace at Iplus or Iminus",
            "a finite Lee-Wald wave-packet flux Gram, radical, quotient or inertia",
            "horizon-to-infinity matching or scattering channels",
            "pole exclusion, stability, CPT positivity, particles or unitarity",
        ],
        "imports": {name: {"path": path, "sha256": sha256(ROOT / path)} for name, path in INPUTS.items()},
        "verification": {
            "producer": "python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.produce --check",
            "verifier": "python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.verify",
            "tests": "python3 -m pytest -q black_hole_programme/phase3/axial_wavepacket_null_trace/tests",
        },
    }


def write_document() -> None:
    document = build_document()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    RECEIPT.write_text(json.dumps({
        "schema": "phase3-black-hole-axial-wavepacket-null-trace-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "producer_sha256": sha256(Path(__file__)),
        "schema_sha256": sha256(SCHEMA),
        "status": "PASS_SHORTFALL",
        "tier_0": "Python compile, schema validation and git diff check",
        "tier_1": "producer replay, independent verifier, scoped tests and mutation tests",
        "higher_tiers_not_run": "No shared operator or promoted endpoint phase space changed; the result is a fail-closed missing-depth theorem.",
    }, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = build_document()
        actual = json.loads(OUTPUT.read_text())
        if expected != actual:
            raise SystemExit("certificate drift")
        print("PASS: axial wave-packet null-trace shortfall reproduces exactly")
    else:
        write_document()
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
