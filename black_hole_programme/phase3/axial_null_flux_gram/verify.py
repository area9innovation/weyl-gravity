"""Independent verifier for the axial null-endpoint flux-Gram theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
FORMAL = HERE / "formal-grams.json"
OMEGA = sp.Symbol("omega", positive=True, real=True)
I = sp.I

EXPECTED_COORDINATE = {
    "Iminus": [
        ["-576/(5*omega)", "-96*I/5", "-384*omega/5"],
        ["96*I/5", "144*omega/5", "192*I*omega**2/5"],
        ["-384*omega/5", "-192*I*omega**2/5", "0"],
    ],
    "Iplus": [
        [
            "(-196608*omega**6+245760*omega**4-106752*omega**2+14976)/(5*omega)",
            "12288*I*omega**4/5-3072*omega**3/5-9984*I*omega**2/5+192*omega+384*I",
            "-1536*I*omega**2/5+384*omega/5+768*I/5",
        ],
        [
            "-12288*I*omega**4/5-3072*omega**3/5+9984*I*omega**2/5+192*omega-384*I",
            "-768*omega**3/5+48*omega",
            "96*omega/5",
        ],
        [
            "1536*I*omega**2/5+384*omega/5-768*I/5",
            "96*omega/5",
            "0",
        ],
    ],
}

EXPECTED_NORM_DATA = {
    "Iminus": {
        "direct_maximum": sp.Rational(1429056, 25),
        "inverse_maximum": sp.Rational(7025, 65536),
        "direct_critical_count": 0,
        "inverse_critical_count": 0,
        "operator_ceiling": "240",
    },
    "Iplus": {
        "direct_maximum": sp.Rational(10389888, 25),
        "inverse_maximum": sp.Rational(19825, 65536),
        "direct_critical_count": 1,
        "inverse_critical_count": 1,
        "operator_ceiling": "645",
    },
}


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def parse(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"omega": OMEGA, "I": I})


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def equivalent(left: list[list[str]], right: list[list[str]]) -> bool:
    a, b = matrix(left), matrix(right)
    return all(sp.cancel(a[i, j] - b[i, j]) == 0
               for i in range(3) for j in range(3))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inertia_at_half(gram: sp.Matrix) -> tuple[int, int, int]:
    minors = [
        sp.factor(gram[:size, :size].det().subs(OMEGA, sp.Rational(1, 2)))
        for size in range(1, 4)
    ]
    if any(value == 0 for value in minors):
        fail("LDL sample lies on a pivot wall")
    pivots = [minors[0], minors[1] / minors[0], minors[2] / minors[1]]
    signs = [sp.sign(sp.factor(value)) for value in pivots]
    if any(sign not in (-1, 1) for sign in signs):
        fail("LDL sign is not exact")
    return signs.count(1), signs.count(-1), 0


def frobenius_squared(value: sp.Matrix) -> sp.Expr:
    return sp.factor(
        sum(sp.expand_complex(sp.conjugate(entry) * entry) for entry in value)
    )


def verify_uniform_control(endpoint: str, gram: sp.Matrix, printed: dict) -> None:
    expected = EXPECTED_NORM_DATA[endpoint]
    direct_function = frobenius_squared(gram)
    inverse = sp.simplify(gram.inv())
    inverse_function = frobenius_squared(inverse)
    direct = printed["direct_frobenius_squared"]
    inverse_data = printed["inverse_frobenius_squared"]
    if sp.cancel(parse(direct["function"]) - direct_function) != 0:
        fail(endpoint + " direct Frobenius function mismatch")
    if sp.cancel(parse(inverse_data["function"]) - inverse_function) != 0:
        fail(endpoint + " inverse Frobenius function mismatch")
    for payload, function, maximum, critical_count in [
        (
            direct,
            direct_function,
            expected["direct_maximum"],
            expected["direct_critical_count"],
        ),
        (
            inverse_data,
            inverse_function,
            expected["inverse_maximum"],
            expected["inverse_critical_count"],
        ),
    ]:
        derivative = sp.factor(sp.diff(function, OMEGA))
        numerator, denominator = sp.fraction(derivative)
        got_count = int(
            sp.count_roots(
                sp.Poly(numerator, OMEGA),
                sp.Rational(1, 2),
                sp.Rational(3, 4),
            )
        )
        pole_count = int(
            sp.count_roots(
                sp.Poly(denominator, OMEGA),
                sp.Rational(1, 2),
                sp.Rational(3, 4),
            )
        )
        if got_count != critical_count or pole_count:
            fail(endpoint + " exact norm critical-point audit mismatch")
        if payload["interior_critical_point_count"] != got_count:
            fail(endpoint + " printed critical-point count mismatch")
        if payload["interior_pole_count"] != pole_count:
            fail(endpoint + " printed pole count mismatch")
        signs = [
            int(sp.sign(derivative.subs(OMEGA, value)))
            for value in (sp.Rational(1, 2), sp.Rational(3, 4))
        ]
        if got_count == 0 and not (
            signs[0] == signs[1] and signs[0] in (-1, 1)
        ):
            fail(endpoint + " monotonic norm proof failed")
        if got_count == 1 and signs != [-1, 1]:
            fail(endpoint + " interior norm critical point is not a minimum")
        endpoint_values = [
            sp.factor(function.subs(OMEGA, value))
            for value in (sp.Rational(1, 2), sp.Rational(3, 4))
        ]
        if max(endpoint_values) != maximum:
            fail(endpoint + " exact norm maximum sentinel mismatch")
        if parse(payload["certified_maximum"]) != maximum:
            fail(endpoint + " printed norm maximum mismatch")
    if not equivalent(
        printed["inverse_matrix"],
        text_matrix := [
            [sp.sstr(sp.factor(inverse[i, j])) for j in range(3)]
            for i in range(3)
        ],
    ):
        fail(endpoint + " inverse matrix mismatch")
    if printed["spectral_operator_norm_upper_bound"] != expected["operator_ceiling"]:
        fail(endpoint + " operator ceiling mismatch")
    if printed["inverse_spectral_operator_norm_strict_upper_bound"] != "1":
        fail(endpoint + " inverse ceiling mismatch")
    if expected["direct_maximum"] > int(expected["operator_ceiling"]) ** 2:
        fail(endpoint + " operator ceiling does not dominate Frobenius maximum")
    if expected["inverse_maximum"] >= 1:
        fail(endpoint + " inverse Frobenius maximum does not imply lower bound")


def verify_document(document: dict, *, deep: bool = False) -> None:
    if document["schema"] != "phase3-black-hole-axial-null-flux-gram-v1":
        fail("schema drift")
    flags = document["claim_flags"]
    for key in (
        "action_current_pulled_back",
        "trace_limit_interchange_proved",
        "Iminus_flux_Gram_certified",
        "Iplus_flux_Gram_certified",
        "endpoint_rank_radical_inertia_certified",
        "uniform_auxiliary_L2_isomorphism_certified",
        "scoped_trace_local_improvement_invariance_certified",
    ):
        if not flags[key]:
            fail("proved claim hidden: " + key)
    for key in (
        "global_connection_constructed",
        "horizon_to_infinity_matching_constructed",
        "scattering_channels_classified",
        "stability_or_CPT_established",
        "unrestricted_improvement_invariance_certified",
    ):
        if flags[key]:
            fail("unsupported promotion: " + key)

    formal = json.loads(FORMAL.read_text())
    for endpoint in ("Iminus", "Iplus"):
        if not equivalent(
            formal[endpoint]["gram_over_pi_alpha"],
            EXPECTED_COORDINATE[endpoint],
        ):
            fail(endpoint + " frozen literal-current pullback changed")
        printed = document["endpoint_grams"][endpoint]
        if not equivalent(
            printed["coordinate_radial_gram_over_pi_alpha_W"],
            EXPECTED_COORDINATE[endpoint],
        ):
            fail(endpoint + " coordinate Gram differs from exact sentinel")
        coordinate = matrix(EXPECTED_COORDINATE[endpoint])
        stokes = -coordinate if endpoint == "Iminus" else coordinate
        if not equivalent(
            printed["stokes_gram_over_pi_alpha_W"],
            [[sp.sstr(stokes[i, j]) for j in range(3)] for i in range(3)],
        ):
            fail(endpoint + " Stokes orientation changed")
        if sp.simplify(stokes - stokes.conjugate().T) != sp.zeros(3):
            fail(endpoint + " Gram is not Hermitian")
        expected_det = {
            "Iminus": sp.Rational(14155776, 125) * OMEGA**3,
            "Iplus": sp.Rational(3538944, 125) * OMEGA,
        }[endpoint]
        if sp.cancel(stokes.det() - expected_det) != 0:
            fail(endpoint + " determinant mismatch")
        # The determinant is strictly positive for every omega in the closed
        # pilot interval, so the exact sample inertia extends by continuity.
        if inertia_at_half(stokes) != (1, 2, 0):
            fail(endpoint + " inertia mismatch")
        classification = printed["classification"]
        if classification["rank"] != 3 or classification["radical_dimension"] != 0:
            fail(endpoint + " false rank/radical")
        if classification["inertia_for_alpha_W_positive"] != {
            "positive": 1, "negative": 2, "zero": 0
        }:
            fail(endpoint + " false positive-coupling inertia")
        verify_uniform_control(
            endpoint, stokes, printed["uniform_auxiliary_L2_control"]
        )
        for row in formal[endpoint]["laurent_audit"]:
            for entry in row:
                if entry["first_power"] is not None and entry["first_power"] < 0:
                    fail(endpoint + " divergent formal-current term")

    if document["endpoint_grams"]["normalization"] != (
        "G_endpoint = Stokes-oriented i*F^r/(pi*alpha_W)"
    ):
        fail("endpoint-current normalization changed")
    if document["endpoint_grams"]["orientation"]["Iminus"] != (
        "minus the increasing-r coordinate Gram"
    ):
        fail("past-boundary orientation lost")
    if document["endpoint_grams"]["orientation"]["Iplus"] != (
        "the increasing-r coordinate Gram"
    ):
        fail("future-boundary orientation lost")
    if "T^dagger*J_out*T=J_in" not in document["endpoint_grams"][
        "orientation"
    ]["scattering_convention"]:
        fail("incoming/outgoing conservation convention lost")
    pullback = document["current_representative"]["chart_pullback"]
    if "h1_t=h1_EF+B^(-1)h0_v" not in pullback["metric"]:
        fail("differentiated EF-to-t reconstruction omitted")
    if document["current_representative"]["counterterm_or_radial_improvement_added"]:
        fail("unrecorded current counterterm")
    improvement = document["current_representative"]["improvement_audit"]
    if improvement["unrestricted_status"] != "OPEN":
        fail("unrestricted improvement ambiguity silently closed")
    if "finite-tangential-jet" not in improvement["scope"]:
        fail("scoped improvement theorem broadened")
    if not {
        "radial or subleading improvements",
        "nonlocal or soft improvements",
        "explicit-time or nondecaying improvements",
    }.issubset(set(improvement["not_covered"])):
        fail("unrestricted improvement exclusions lost")

    theorem = document["trace_limit_theorem"]
    if theorem["status"] != "PASS":
        fail("trace/limit theorem hidden")
    if theorem["formal_current_audit"]["first_omitted_metric_order"] != (
        "O(r^-4), uniformly on the pilot interval"
    ):
        fail("formal remainder order changed")
    # Independently strip the 106 bilinear field jets from the literal
    # action-current expression and audit its rational radial coefficients.
    from .formal_gram import _literal_current

    current, radius, metadata = _literal_current()
    degrees = []
    jet_ones = {atom: sp.Integer(1) for atom in metadata}
    for term in sp.Add.make_args(sp.expand(current)):
        coefficient = sp.cancel(term.xreplace(jet_ones))
        numerator, denominator = sp.fraction(coefficient)
        degrees.append(
            int(sp.degree(numerator, radius) - sp.degree(denominator, radius))
        )
    if [min(degrees), max(degrees)] != [-5, 0]:
        fail("literal current radial coefficient range changed")
    if theorem["formal_current_audit"]["coefficient_radial_degree_range"] != [
        -5, 0
    ]:
        fail("printed current coefficient range changed")
    if theorem["exact_remainder_input"]["minimum_cross_rate_decay_p"] != 5:
        fail("remainder decay weakened")
    if theorem["exact_remainder_input"]["omega_derivatives"] != [0, 1, 2, 3]:
        fail("frequency-derivative input changed")
    geometry = document["trace_space_geometry"]
    if geometry["common_uniform_constants"] != {
        "c": "1",
        "C": "645",
        "estimate": (
            "||a||_L2 <= ||G_endpoint*a||_L2 <= "
            "645||a||_L2 at either endpoint"
        ),
    }:
        fail("common L2 constants changed")
    if "not a CPT metric" not in geometry["krein_majorant"]:
        fail("Krein majorant overpromoted")
    verdict = document["common_verdict"]
    if (verdict["rank"], verdict["radical_dimension"],
            verdict["quotient_dimension"]) != (3, 0, 3):
        fail("common endpoint dimension verdict changed")
    if verdict["inertia_for_alpha_W_positive"] != [1, 2, 0]:
        fail("common inertia changed")
    if verdict["frequency_walls"]:
        fail("invented frequency wall")

    for name, imported in document["imports"].items():
        path = ROOT / imported["path"]
        if not path.exists() or sha256(path) != imported["sha256"]:
            fail("import drift: " + name)

    if deep:
        # This calls the independent literal-current evaluator for a single
        # sentinel rather than trusting the frozen matrix.  The complete 12
        # upper-triangle replay is exposed separately by formal_gram --check.
        from .formal_gram import endpoint_fields, gram_entry

        labels, fields = endpoint_fields("Iminus")
        value, visible = gram_entry(fields[labels[0]], fields[labels[0]])
        if sp.cancel(value + sp.Rational(576, 5) / OMEGA) != 0:
            fail("deep XI0 self-flux mismatch")
        if set(visible) != {0}:
            fail("deep XI0 Laurent audit changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deep", action="store_true")
    args = parser.parse_args()
    verify_document(json.loads(CERT.read_text()), deep=args.deep)
    print("PASS: exact axial null-endpoint flux Grams verified")


if __name__ == "__main__":
    main()
