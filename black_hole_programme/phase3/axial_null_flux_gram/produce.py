"""Produce the exact axial null-endpoint wave-packet flux certificate.

The expensive literal-current pullback is frozen in ``formal-grams.json`` and
can be reproduced with ``python -m ...formal_gram --check``.  This producer
performs the inexpensive exact classification and records the trace/limit
argument that promotes the formal matrices to the already certified exact
wave-packet traces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
OMEGA = sp.Symbol("omega", positive=True, real=True)
I = sp.I

INPUTS = {
    "formal_grams": "black_hole_programme/phase3/axial_null_flux_gram/formal-grams.json",
    "literal_axial_current": "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json",
    "wavepacket_traces": "black_hole_programme/phase3/axial_wavepacket_null_trace/certificate.json",
    "differentiated_envelope": "black_hole_programme/phase3/axial_wavepacket_null_trace/differentiated-envelope.json",
    "boundary_flux_contract": "black_hole_programme/phase3/boundary_flux_contract/certificate.json",
    "complete_reconstruction": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
    "depth_five_heads": "black_hole_programme/phase3/axial_wavepacket_null_trace/depth5-heads.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"omega": OMEGA, "I": I})


def matrix_from(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def text_matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
            for i in range(matrix.rows)]


def frobenius_squared(matrix: sp.Matrix) -> sp.Expr:
    """Return the exact squared Frobenius norm."""
    return sp.factor(
        sum(sp.expand_complex(sp.conjugate(entry) * entry) for entry in matrix)
    )


def interval_maximum_by_derivative(expression: sp.Expr) -> dict:
    """Certify a rational-function maximum on the closed pilot interval."""
    left, right = sp.Rational(1, 2), sp.Rational(3, 4)
    derivative = sp.factor(sp.diff(expression, OMEGA))
    numerator, denominator = sp.fraction(derivative)
    critical_count = int(
        sp.count_roots(sp.Poly(numerator, OMEGA), left, right)
    )
    pole_count = int(
        sp.count_roots(sp.Poly(denominator, OMEGA), left, right)
    )
    if pole_count:
        raise RuntimeError("norm function has a pole in the pilot interval")
    endpoint_signs = [
        int(sp.sign(derivative.subs(OMEGA, value)))
        for value in (left, right)
    ]
    if critical_count == 0:
        if endpoint_signs[0] != endpoint_signs[1] or endpoint_signs[0] not in (-1, 1):
            raise RuntimeError("uncertified monotonic norm function")
        disposition = (
            "strictly increasing" if endpoint_signs[0] > 0
            else "strictly decreasing"
        )
    elif critical_count == 1:
        if endpoint_signs != [-1, 1]:
            raise RuntimeError("interior critical point is not a certified minimum")
        disposition = "one strict interior minimum"
    else:
        raise RuntimeError("unexpected number of norm critical points")
    endpoint_values = [
        sp.factor(expression.subs(OMEGA, value))
        for value in (left, right)
    ]
    maximum = max(endpoint_values)
    return {
        "function": sp.sstr(sp.factor(expression)),
        "derivative_numerator": sp.sstr(sp.factor(numerator)),
        "derivative_denominator": sp.sstr(sp.factor(denominator)),
        "interior_critical_point_count": critical_count,
        "interior_pole_count": pole_count,
        "derivative_endpoint_signs": [
            "+" if sign > 0 else "-" for sign in endpoint_signs
        ],
        "critical_point_disposition": disposition,
        "endpoint_values": [sp.sstr(value) for value in endpoint_values],
        "certified_maximum": sp.sstr(maximum),
        "proof": (
            "Exact Sturm counts and exact derivative signs show that every "
            "interior critical point is a minimum, so the maximum is the "
            "larger exact endpoint value."
        ),
    }


def uniform_control(matrix: sp.Matrix, operator_ceiling: int) -> dict:
    """Certify uniform Euclidean operator and inverse bounds."""
    direct = interval_maximum_by_derivative(frobenius_squared(matrix))
    inverse_matrix = sp.simplify(matrix.inv())
    inverse = interval_maximum_by_derivative(frobenius_squared(inverse_matrix))
    direct_max = parse(direct["certified_maximum"])
    inverse_max = parse(inverse["certified_maximum"])
    if direct_max > operator_ceiling**2:
        raise RuntimeError("declared direct operator ceiling is too small")
    if inverse_max >= 1:
        raise RuntimeError("inverse norm is not certified below one")
    return {
        "inverse_matrix": text_matrix(inverse_matrix),
        "direct_frobenius_squared": direct,
        "inverse_frobenius_squared": inverse,
        "spectral_operator_norm_upper_bound": str(operator_ceiling),
        "inverse_spectral_operator_norm_strict_upper_bound": "1",
        "uniform_singular_value_lower_bound": "1",
        "pointwise_estimate": (
            f"||a||_2 <= ||G(omega)a||_2 <= {operator_ceiling}||a||_2"
        ),
        "method": (
            "||A||_2<=||A||_F and ||A^(-1)||_2<=||A^(-1)||_F; "
            "the exact Frobenius-square maxima are independently certified "
            "by Sturm counts and derivative signs."
        ),
    }


def classify(matrix: sp.Matrix, sample: sp.Rational) -> dict:
    """Classify a continuous Hermitian 3x3 family on the pilot interval.

    Nonvanishing of the determinant prevents any eigenvalue crossing zero.
    Exact LDL pivots at one endpoint therefore determine the inertia on the
    whole connected interval, even when a chosen leading principal minor
    vanishes inside it.
    """
    if sp.simplify(matrix - matrix.conjugate().T) != sp.zeros(3):
        raise RuntimeError("endpoint Gram is not Hermitian")
    minors = [
        sp.factor(matrix[:size, :size].det())
        for size in range(1, 4)
    ]
    determinant = minors[-1]
    numerator, denominator = sp.fraction(determinant)
    if sp.count_roots(sp.Poly(numerator, OMEGA),
                      sp.Rational(1, 2), sp.Rational(3, 4)) != 0:
        raise RuntimeError("determinant wall in pilot interval")
    if denominator != 1:
        den_poly = sp.Poly(denominator, OMEGA)
        if sp.count_roots(den_poly, sp.Rational(1, 2),
                          sp.Rational(3, 4)) != 0:
            raise RuntimeError("Gram pole in pilot interval")
    values = [sp.factor(value.subs(OMEGA, sample)) for value in minors]
    if any(value == 0 for value in values):
        raise RuntimeError("sample is not an LDL pivot cell")
    pivots = [
        values[0],
        sp.factor(values[1] / values[0]),
        sp.factor(values[2] / values[1]),
    ]
    signs = [sp.sign(value) for value in pivots]
    if any(sign not in (-1, 1) for sign in signs):
        raise RuntimeError("indeterminate exact LDL sign")
    return {
        "rank": 3,
        "radical_dimension": 0,
        "determinant": sp.sstr(determinant),
        "leading_principal_minors": [sp.sstr(value) for value in minors],
        "sample_frequency": sp.sstr(sample),
        "sample_LDL_pivots": [sp.sstr(value) for value in pivots],
        "sample_pivot_signs": ["+" if sign == 1 else "-" for sign in signs],
        "inertia_for_alpha_W_positive": {
            "positive": signs.count(1),
            "negative": signs.count(-1),
            "zero": 0,
        },
        "inertia_for_alpha_W_negative": {
            "positive": signs.count(-1),
            "negative": signs.count(1),
            "zero": 0,
        },
        "whole_interval_argument": (
            "The Hermitian entries are continuous on [1/2,3/4] and the exact "
            "determinant has no zero there. Eigenvalues cannot cross zero, so "
            "the exact sample inertia is constant on the connected interval."
        ),
    }


def build_document() -> dict:
    imported = {
        name: json.loads((ROOT / path).read_text())
        for name, path in INPUTS.items()
    }
    formal = imported["formal_grams"]
    traces = imported["wavepacket_traces"]
    boundary = imported["boundary_flux_contract"]

    if traces["matching_direction_wavepacket_trace"]["Iminus"]["basis"] != [
        "XI0", "XI1", "EI0"
    ]:
        raise RuntimeError("Iminus trace basis drift")
    if traces["matching_direction_wavepacket_trace"]["Iplus"]["basis"] != [
        "XI2", "XI3", "EI2"
    ]:
        raise RuntimeError("Iplus trace basis drift")
    if boundary["action_derived_current"]["orientation"]["boundary_identity"] != (
        "J_Hplus + J_Iplus - J_Hminus - J_Iminus = 0"
    ):
        raise RuntimeError("boundary orientation drift")

    coordinate = {
        endpoint: matrix_from(formal[endpoint]["gram_over_pi_alpha"])
        for endpoint in ("Iminus", "Iplus")
    }
    # Coordinate F^r points toward increasing r.  It agrees with the future
    # I+ Stokes orientation and is opposite to the past I- orientation.
    stokes = {"Iminus": -coordinate["Iminus"], "Iplus": coordinate["Iplus"]}
    classifications = {
        endpoint: classify(stokes[endpoint], sp.Rational(1, 2))
        for endpoint in stokes
    }
    expected_determinants = {
        "Iminus": sp.Rational(14155776, 125) * OMEGA**3,
        "Iplus": sp.Rational(3538944, 125) * OMEGA,
    }
    for endpoint, expected in expected_determinants.items():
        if sp.cancel(stokes[endpoint].det() - expected) != 0:
            raise RuntimeError(f"{endpoint} determinant sentinel changed")
        if classifications[endpoint]["inertia_for_alpha_W_positive"] != {
            "positive": 1, "negative": 2, "zero": 0
        }:
            raise RuntimeError(f"{endpoint} inertia changed")
        for row in formal[endpoint]["laurent_audit"]:
            for entry in row:
                first = entry["first_power"]
                if first is not None and first < 0:
                    raise RuntimeError(f"{endpoint} current has a divergent term")

    endpoint_grams = {
        "normalization": "G_endpoint = Stokes-oriented i*F^r/(pi*alpha_W)",
        "orientation": {
            "boundary_identity": (
                "J_Hplus + J_Iplus - J_Hminus - J_Iminus = 0"
            ),
            "Iminus": "minus the increasing-r coordinate Gram",
            "Iplus": "the increasing-r coordinate Gram",
            "scattering_convention": (
                "Incoming Grams include the past-boundary sign, so a globally "
                "constructed a_out=T*a_in must satisfy "
                "T^dagger*J_out*T=J_in. If no horizon channels are present, "
                "this reduces to T^dagger*Gplus*T=Gminus."
            ),
            "warning": (
                "The negative indices are not orientation artifacts after this "
                "incoming/outgoing convention is fixed, but they remain endpoint "
                "indices until a global connection populates the trace spaces."
            ),
        },
    }
    ceilings = {"Iminus": 240, "Iplus": 645}
    for endpoint in ("Iminus", "Iplus"):
        endpoint_grams[endpoint] = {
            "basis": formal[endpoint]["basis"],
            "coordinate_radial_gram_over_pi_alpha_W": text_matrix(
                coordinate[endpoint]
            ),
            "stokes_gram_over_pi_alpha_W": text_matrix(stokes[endpoint]),
            "classification": classifications[endpoint],
            "uniform_auxiliary_L2_control": uniform_control(
                stokes[endpoint], ceilings[endpoint]
            ),
            "formal_laurent_audit": formal[endpoint]["laurent_audit"],
        }

    return {
        "schema": "phase3-black-hole-axial-null-flux-gram-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1",
        "result_token": "EXACT_AXIAL_WAVEPACKET_ENDPOINT_GRAMS_FULL_RANK_INDEFINITE",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior with M=1",
            "sector": "axial ell=2",
            "frequency_interval": ["1/2", "3/4"],
            "positive_frequency_core": "C_c^infinity((1/2,3/4);C^3)",
            "completion": "L2([1/2,3/4];C^3)",
            "negative_frequencies": (
                "fixed by a_{ell,-m}(-omega)=(-1)^m conjugate(a_{ell,m}(omega))"
            ),
            "coupling_convention": (
                "Matrices are divided by pi*alpha_W. Inertia (1,2) assumes "
                "alpha_W>0; reversing the action sign reverses the inertia."
            ),
        },
        "current_representative": {
            "theta": boundary["action_derived_current"]["theta"],
            "presymplectic_current": boundary[
                "action_derived_current"
            ]["presymplectic_current"],
            "representative": boundary[
                "action_derived_current"
            ]["representative"],
            "counterterm_or_radial_improvement_added": False,
            "improvement_audit": {
                "scoped_invariance": (
                    "delta Y vanishes by delta^2=0; angular exact terms integrate "
                    "to zero; and a stationary globally defined local "
                    "finite-tangential-jet dZ with finite trace-only pullback has "
                    "zero cut terms on the C_c^infinity frequency core because "
                    "the inverse Fourier traces are Schwartz. Its continuous L2 "
                    "extension therefore leaves the endpoint Grams unchanged."
                ),
                "scope": (
                    "stationary globally defined local finite-tangential-jet "
                    "improvements with finite trace-only pullback"
                ),
                "unrestricted_status": "OPEN",
                "unrestricted_missing_audit": [
                    "a typed local-improvement basis {Z_A} modulo d and delta",
                    "radial and subleading pullbacks on all six endpoint jets",
                    "uniform corner-continuity bounds on the L2 completion",
                    "the exact additive matrices Delta G_A and their inertia strata",
                ],
                "not_covered": [
                    "radial or subleading improvements",
                    "nonlocal or soft improvements",
                    "explicit-time or nondecaying improvements",
                    "improvements without a finite trace-only pullback",
                ],
            },
            "chart_pullback": {
                "metric": "h0_t=h0_v; h1_t=h1_EF+B^(-1)h0_v, B=1-2/r",
                "fixed_t_radial_derivative": (
                    "partial_r|t=partial_r|v+i*omega/B on the positive-frequency "
                    "slot and partial_r|v-i*omega/B on the conjugate slot"
                ),
                "reason": (
                    "The literal frozen current is written in the Schwarzschild "
                    "t chart; omitting this differentiated reconstruction changes "
                    "the endpoint form."
                ),
            },
        },
        "trace_limit_theorem": {
            "finite_radius_pairing": (
                "For the unitary Fourier convention, time integration and "
                "Plancherel give integral a(omega)^dagger H_R(omega)b(omega)domega."
            ),
            "formal_current_audit": {
                "current_radial_coefficient_growth": "at most r^0",
                "coefficient_radial_degree_range": [-5, 0],
                "maximum_metric_head_growth": "r^2",
                "fixed_t_radial_order": 3,
                "first_omitted_metric_order": "O(r^-4), uniformly on the pilot interval",
                "bilinear_error": (
                    "Every formal/exact cross term is O(r^-2) and every "
                    "remainder/remainder term is O(r^-8), up to harmless logarithms."
                ),
                "formal_Laurent_result": (
                    "Every one of the nine entries at each endpoint has no "
                    "negative z=1/r power; its z^0 coefficient is the printed Gram."
                ),
            },
            "exact_remainder_input": {
                "omega_derivatives": [0, 1, 2, 3],
                "minimum_cross_rate_decay_p": 5,
                "decay_rule": "d_omega^k correction = O(r^(-(p-k))) up to logarithms",
            },
            "interchange": (
                "Uniform Volterra remainder bounds and the displayed bilinear "
                "error give dominated convergence on the compact frequency "
                "interval. Cross-rate oscillatory products have L1 spectral "
                "amplitudes and vanish by the Riemann-Lebesgue lemma."
            ),
            "completion": (
                "Exact Sturm-certified Frobenius bounds for G and G^(-1) show "
                "that the pairing on the smooth compactly supported core extends "
                "uniquely and continuously to a uniformly nondegenerate form on "
                "the auxiliary positive L2 trace space."
            ),
            "status": "PASS",
        },
        "trace_space_geometry": {
            "auxiliary_positive_topology": (
                "The Hilbert completion uses the coefficient norm "
                "||a||_L2^2=integral a(omega)^dagger*a(omega)domega."
            ),
            "indefinite_flux_form": (
                "The normalized endpoint form is integral "
                "a(omega)^dagger*G_endpoint(omega)*b(omega)domega; the physical "
                "current restores the overall factor pi*alpha_W."
            ),
            "common_uniform_constants": {
                "c": "1",
                "C": "645",
                "estimate": (
                    "||a||_L2 <= ||G_endpoint*a||_L2 <= "
                    "645||a||_L2 at either endpoint"
                ),
            },
            "krein_majorant": (
                "Because G is continuous, Hermitian and uniformly invertible, "
                "J=sign(G) is a continuous fundamental symmetry and |G| defines "
                "a positive Krein majorant uniformly equivalent to the auxiliary "
                "L2 norm. This canonical majorant is not a CPT metric, positive "
                "energy, or particle norm."
            ),
        },
        "endpoint_grams": endpoint_grams,
        "common_verdict": {
            "rank": 3,
            "radical_dimension": 0,
            "quotient_dimension": 3,
            "inertia_for_alpha_W_positive": [1, 2, 0],
            "frequency_walls": [],
            "statement": (
                "Both exact axial null-endpoint trace spaces carry a full-rank "
                "indefinite Lee-Wald flux Gram throughout the pilot interval."
            ),
        },
        "claim_flags": {
            "action_current_pulled_back": True,
            "trace_limit_interchange_proved": True,
            "Iminus_flux_Gram_certified": True,
            "Iplus_flux_Gram_certified": True,
            "endpoint_rank_radical_inertia_certified": True,
            "uniform_auxiliary_L2_isomorphism_certified": True,
            "scoped_trace_local_improvement_invariance_certified": True,
            "unrestricted_improvement_invariance_certified": False,
            "global_connection_constructed": False,
            "horizon_to_infinity_matching_constructed": False,
            "scattering_channels_classified": False,
            "stability_or_CPT_established": False,
        },
        "does_not_establish": [
            "a horizon-to-infinity connection or scattering matrix",
            "that any endpoint direction is populated by horizon-regular data",
            "a positive energy, CPT metric, particle norm or unitarity theorem",
            "pole exclusion, quasinormal stability or time-domain decay",
            "polar parity, ell other than two or frequencies outside [1/2,3/4]",
            "invariance under unrestricted radial/corner improvements of the current",
        ],
        "imports": {
            name: {"path": path, "sha256": sha256(ROOT / path)}
            for name, path in INPUTS.items()
        },
        "verification": {
            "producer": (
                "python3 -m black_hole_programme.phase3.axial_null_flux_gram.produce --check"
            ),
            "verifier": (
                "python3 -m black_hole_programme.phase3.axial_null_flux_gram.verify"
            ),
            "deep_literal_current_replay": (
                "python3 -m black_hole_programme.phase3.axial_null_flux_gram.formal_gram --check --jobs 4"
            ),
            "mutations": (
                "python3 -m black_hole_programme.phase3.axial_null_flux_gram.mutations"
            ),
            "tests": (
                "python3 -m unittest "
                "black_hole_programme.phase3.axial_null_flux_gram.tests.test_null_flux_gram"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build_document()
    if args.check:
        if document != json.loads(OUTPUT.read_text()):
            raise SystemExit("certificate drift")
        print("PASS: axial null-endpoint flux certificate reproduces")
    else:
        OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
