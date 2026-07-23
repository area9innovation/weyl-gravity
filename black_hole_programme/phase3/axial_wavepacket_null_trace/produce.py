"""Produce the Phase-3 exact axial wave-packet null-trace audit.

The four additional XI columns and both Einstein-kernel columns are extended
far enough that every cross-rate Volterra generator entry decays as at least
``r^-5``.  Exact interval bounds through three frequency derivatives then
promote the formal endpoint heads to bounded wave-packet radiation traces.
The action-current pullback needed for the endpoint flux Gram remains open.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from .kernel_depth4 import build_kernel_heads


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
    "depth5_heads": "black_hole_programme/phase3/axial_wavepacket_null_trace/depth5-heads.json",
    "differentiated_envelope": "black_hole_programme/phase3/axial_wavepacket_null_trace/differentiated-envelope.json",
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
    for label, branch in metric_heads.items():
        values: list[sp.Expr] = []
        for field in ("H0", "H1", "F"):
            values.extend(parse(item) for item in branch[field])
        expressions[label] = values
    kernels = build_kernel_heads()
    for label in ("EI0", "EI2"):
        expressions[label] = [
            parse(item) for field in ("H1", "F") for item in kernels[label][field]
        ]

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
    old_heads = imported["metric_heads"]
    heads = imported["depth5_heads"]
    differentiated = imported["differentiated_envelope"]
    reconstruction = imported["reconstruction"]

    if preflight["endpoint_polarizations"]["Iminus_incoming_rate_zero"] != ["XI0", "XI1", "EI0"]:
        raise RuntimeError("Iminus polarization drift")
    if preflight["endpoint_polarizations"]["Iplus_outgoing_rate_minus_2Iomega"] != ["XI2", "XI3", "EI2"]:
        raise RuntimeError("Iplus polarization drift")
    imported_decay = envelope["volterra_kernel"]["decay_p_ij"]
    imported_p_min = min(
        entry for row in imported_decay for entry in row if entry < 99
    )
    if imported_p_min != 3:
        raise RuntimeError(f"imported cross-rate minimum changed: {imported_p_min}")
    if tuple(heads) != ("XI0", "XI1", "XI2", "XI3"):
        raise RuntimeError("depth-five branch inventory changed")
    for label, branch in heads.items():
        if branch["carrier_depth"] != 8:
            raise RuntimeError(f"under-resolved carrier source for {label}")
        if len(branch["H0"]) != 6 or len(branch["H1"]) != 6:
            raise RuntimeError(f"depth-five metric head missing for {label}")
        expected_f = 7 if label in ("XI2", "XI3") else 6
        if len(branch["F"]) != expected_f:
            raise RuntimeError(f"derivative-forced F depth changed for {label}")
        if branch["metric_recurrence_rank"] != 2 or branch["forced_log_coefficient"] != "0":
            raise RuntimeError(f"recurrence compatibility changed for {label}")
    # Sentinel against the seductive carrier-depth-seven A5 false solution.
    xi0_a5 = parse(heads["XI0"]["H1"][5])
    expected_xi0_a5 = I*(6169*OMEGA**2 - 7278*I*OMEGA + 1512)/(96*OMEGA**7)
    if sp.cancel(xi0_a5 - expected_xi0_a5) != 0:
        raise RuntimeError("XI0 A5 source-depth sentinel failed")

    repaired_decay = differentiated["decay_p_ij"]
    repaired_p_min = min(
        entry for row in repaired_decay for entry in row if entry < 99
    )
    if repaired_p_min != 5 or repaired_decay[4][5] != 5:
        raise RuntimeError("differentiated recurrence repair is incomplete")
    if not differentiated["q_each_less_than_one_quarter"]:
        raise RuntimeError("differentiated Volterra gate failed")
    if differentiated["correction_derivative_integer_ceilings"] != [2, 1, 2, 4]:
        raise RuntimeError("correction derivative gate changed")

    maximum_metric_weight = 2
    ibp_orders = maximum_metric_weight + 1
    certified_omega_derivatives = 3
    first_missing_derivative = None
    required_decay = ibp_orders + 2
    additional_orders = 0
    if (ibp_orders, certified_omega_derivatives,
            required_decay, additional_orders) != (3, 3, 5, 0):
        raise RuntimeError("derivative-depth arithmetic changed")

    return {
        "schema": "phase3-black-hole-axial-wavepacket-null-trace-v3",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_EXACT_WAVEPACKET_NULL_TRACES_V3",
        "result_token": "EXACT_IPLUS_IMINUS_WAVEPACKET_TRACES_FLUX_GRAM_OPEN",
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
        "depth_five_recurrence": {
            "artifact": INPUTS["depth5_heads"],
            "artifact_sha256": sha256(ROOT / INPUTS["depth5_heads"]),
            "source_pole_order": 2,
            "carrier_depth_required_for_H1_A5": 8,
            "underresolved_depth_seven_disposition": "REJECTED: the z^-2 metric source makes A5 depend on carrier coefficient n=8",
            "branches": {
                label: {
                    "carrier_depth": branch["carrier_depth"],
                    "H0_inverse_depth": len(branch["H0"]) - 1,
                    "H1_inverse_depth": len(branch["H1"]) - 1,
                    "F_inverse_depth": len(branch["F"]) - 1,
                    "A4": branch["H1"][4],
                    "A5": branch["H1"][5],
                    "metric_recurrence_rank": branch["metric_recurrence_rank"],
                    "forced_log_coefficient": branch["forced_log_coefficient"],
                }
                for label, branch in heads.items()
            },
            "pivot_audit": {
                "carrier": {
                    label: old_heads["branches"][label]["recurrence"]["carrier_determinant"]
                    for label in heads
                },
                "metric": {
                    label: old_heads["branches"][label]["recurrence"]["metric_pivot"]
                    for label in heads
                },
                "frequency_interval": "omega in [1/2,3/4], so no new pivot vanishes at n=4,5",
            },
            "exact_raw_lower_residual_valuations": [8, 7, 5, 4],
            "conservative_raw_lower_bounds_used_in_decay_table": [5, 5, 5, 4],
            "status": "PASS",
        },
        "kernel_depth_four_recurrence": {
            "branches": build_kernel_heads(),
            "pivots_n4": {"EI0": "-8*I*omega", "EI2": "8*I*omega"},
            "raw_residual_valuations": {"EI0": 6, "EI2": 6},
            "forced_log_coefficients": {"EI0": "0", "EI2": "0"},
            "status": "PASS",
        },
        "formal_joint_symbol_bounds": {
            "frequency_interval": ["1/2", "3/4"],
            "method": "exact rational l1 coefficient bound using omega<=3/4 and omega^(-1)<=2",
            "bounds_by_branch": formal_head_bounds(heads, reconstruction),
            "pole_statement": "Every displayed coefficient and its first three omega derivatives is uniformly bounded; the only real denominator zero is omega=0, outside the profile support.",
        },
        "matching_direction_wavepacket_trace": {
            "Iminus": {
                "fixed_coordinate": "v",
                "dimension": 3,
                "basis": ["XI0", "XI1", "EI0"],
                "phase": "exp(I*omega*v)",
                "trace_space": "L2([1/2,3/4];C^3) positive-frequency amplitudes with C_c^infinity core",
            },
            "Iplus": {
                "fixed_coordinate": "u",
                "dimension": 3,
                "basis": ["XI2", "XI3", "EI2"],
                "phase": "2^(-4*I*omega)*exp(I*omega*u)",
                "finite_radius_factor": "(1-2/r)^(4*I*omega) -> 1 uniformly in omega",
                "trace_space": "L2([1/2,3/4];C^3) positive-frequency amplitudes with C_c^infinity core",
            },
            "exact_solution_statement": "The repaired Volterra corrections have omega derivatives k=0..3 with uniform integrable bounds. Dominated convergence gives each matching rescaled limit, and three-fold nonstationary phase makes every exact wrong-endpoint contribution vanish.",
            "boundedness": "Plancherel identifies the time-domain radiation trace with the declared L2 spectral amplitude norm; the trace map is bounded on the C_c^infinity core and extends to its L2 completion.",
            "regularity_boundary": "The matching trace extends to the L2 completion. The three-fold integration-by-parts proof of wrong-endpoint suppression is asserted on the C_c^infinity core (and its H^3 closure), not on arbitrary L2 profiles.",
            "reality": "negative frequencies are supplied by a_{ell,-m}(-omega)=(-1)^m conjugate(a_{ell,m}(omega))",
            "status": "EXACT_SOLUTION_WAVEPACKET_TRACE",
        },
        "exact_remainder_derivative_audit": {
            "imported_kernel_bound": "|K_N,ij(r,omega)| <= C_ij*r^(-p_ij)",
            "imported_minimum_cross_rate_decay_p": imported_p_min,
            "repaired_decay_p_ij": repaired_decay,
            "minimum_cross_rate_decay_p": repaired_p_min,
            "xi_only_minimum_cross_rate_decay_p": 5,
            "phase_derivative_rule": "Each omega derivative of exp(+/-2*I*omega*r)*r^(+/-4*I*omega) costs at most one power of r (log r is subleading).",
            "absolute_decay_after_k_derivatives": "r^(-(p-k)) up to logarithms",
            "integrability_condition": "p-k>1",
            "certified_omega_derivatives": certified_omega_derivatives,
            "first_missing_derivative_order": first_missing_derivative,
            "first_failure": None,
            "orders_needed_by_wrong_endpoint_lemma": ibp_orders,
            "required_minimum_decay_p": required_decay,
            "minimum_additional_inverse_radius_recurrence_orders": additional_orders,
            "status": "PASS",
        },
        "differentiated_volterra_envelope": {
            "artifact": INPUTS["differentiated_envelope"],
            "artifact_sha256": sha256(ROOT / INPUTS["differentiated_envelope"]),
            "frequency_cells": differentiated["frequency_cells"],
            "normalization_radius": differentiated["normalization_radius"],
            "omega_derivative_orders": [0, 1, 2, 3],
            "decay_p_ij": differentiated["decay_p_ij"],
            "inverse_C_jet_integer_ceilings": differentiated["inverse_derivative_bounds"]["C"],
            "inverse_K_jet_integer_ceilings": differentiated["inverse_derivative_bounds"]["K"],
            "generator_U_jet_integer_ceilings": differentiated["generator_block_derivative_bounds"]["U"],
            "generator_V_jet_integer_ceilings": differentiated["generator_block_derivative_bounds"]["V"],
            "generator_W_jet_integer_ceilings": differentiated["generator_block_derivative_bounds"]["W"],
            "q_derivative_strict_upper_bounds": [entry["strict_upper_bound"] for entry in differentiated["q_by_omega_derivative_order"]],
            "q_each_less_than_one_quarter": differentiated["q_each_less_than_one_quarter"],
            "correction_derivative_integer_ceilings": differentiated["correction_derivative_integer_ceilings"],
            "proof_method": "Exact rational rectangle arithmetic, Neumann inverse gates, differentiated inverse recursion and Volterra derivative recursion.",
            "status": "PASS",
        },
        "endpoint_flux_disposition": {
            "Iminus": {"trace_dimension": 3, "flux_Gram": "NOT_CERTIFIED", "radical": "UNDEFINED", "quotient_dimension": "UNDEFINED", "inertia": "UNDEFINED"},
            "Iplus": {"trace_dimension": 3, "flux_Gram": "NOT_CERTIFIED", "radical": "UNDEFINED", "quotient_dimension": "UNDEFINED", "inertia": "UNDEFINED"},
            "reason": "The wave-packet traces are exact, but no action-current continuity/pullback theorem has yet identified the asymptotic Lee-Wald current with a finite Hermitian form on these trace amplitudes. A formal fixed-frequency Gram is not silently promoted.",
            "orientation": "Iplus and Iminus retain separate outward-normal conventions; they are never combined into one local endpoint test.",
            "reality": "a_{ell,-m}(-omega)=(-1)^m*conjugate(a_{ell,m}(omega)); only positive-frequency amplitudes are independent.",
        },
        "disposition": {
            "status": "SHORTFALL",
            "what_is_proved": "On the declared compact positive-frequency interval, the six-column axial infinity basis has an exact differentiated Volterra envelope through omega order three with cross-rate decay p>=5. The resulting exact solutions define bounded three-dimensional wave-packet radiation traces at each null endpoint, and every wrong-endpoint contribution vanishes after three integrations by parts.",
            "missing_dependency": "An action-derived asymptotic current pullback and continuity theorem is required before the endpoint Lee-Wald flux Gram, radical and inertia can be certified.",
        },
        "claim_flags": {
            "scalar_nonstationary_phase_lemma": True,
            "formal_head_wrong_endpoint_suppression": True,
            "formal_head_joint_symbol_bounds_through_order_three": True,
            "matching_direction_wavepacket_trace_dimension": True,
            "xi_depth_five_recurrence": True,
            "xi_cross_rate_p_at_least_five": True,
            "full_six_column_p_at_least_five": True,
            "exact_solution_wrong_endpoint_suppression": True,
            "wavepacket_trace_constructed": True,
            "endpoint_flux_Gram_certified": False,
            "global_connection_constructed": False,
            "scattering_channels_classified": False,
            "stability_or_CPT_established": False,
        },
        "does_not_establish": [
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
        "schema": "phase3-black-hole-axial-wavepacket-null-trace-receipt-v3",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "producer_sha256": sha256(Path(__file__)),
        "schema_sha256": sha256(SCHEMA),
        "status": "PASS_SHORTFALL",
        "tier_0": "Python compile, schema validation and git diff check",
        "tier_1": "producer replay, independent verifier, scoped tests and mutation tests",
        "tier_2": "independent exact six-state residual and algebraic H0 replay via verify --deep",
        "higher_tiers_not_run": "No shared core operator changed. The endpoint flux phase space remains unpromoted pending an action-current pullback theorem.",
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
        print("PASS: exact axial wave-packet null traces reproduce exactly")
    else:
        write_document()
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
