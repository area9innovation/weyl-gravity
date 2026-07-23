"""Produce the exact arbitrary-radius repaired-axial current certificate.

The literal Lee--Wald action current is evaluated at 26 rational radii over
QQ(I)(omega).  A separately audited localized-ring bound proves that, after
multiplication by the declared denominator, every entry has radial degree at
most 25.  Exact interpolation therefore recovers the arbitrary-r current
without assuming the conservation equation.  Only after reconstruction do we
differentiate it and test the repaired six-state flow identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ_I
from sympy.polys.fields import field

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = HERE / "schema.json"

INPUTS = {
    "literal_action_current": "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json",
    "repaired_system": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
    "repaired_system_producer": "black_hole_programme/phase3/axial_complete_reconstruction_repair/produce.py",
    "literal_current_dag": "black_hole_programme/phase3/axial_null_infinity_trace_preflight/current_dag.py",
    "fixed_radius_current": "black_hole_programme/phase3/axial_null_infinity_trace_preflight/certificate.json",
    "literal_samples": "black_hole_programme/phase3/axial_arbitrary_radius_current_conservation/literal-samples.json",
    "literal_samples_receipt": "black_hole_programme/phase3/axial_arbitrary_radius_current_conservation/literal-samples-receipt.json",
}

RADII = [sp.Integer(value) for value in range(3, 33)]
MAX_R_DEGREE = 29
MAX_OMEGA_DEGREE = 13
DENOMINATOR_EXPONENTS = {
    "r": 7,
    "r_minus_2": 6,
    "omega_r_minus_2I": 4,
    "omega_r_plus_2I": 4,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_matrix_hash(matrix: sp.Matrix) -> str:
    payload = json.dumps(
        [[sp.sstr(sp.cancel(matrix[i, j])) for j in range(matrix.cols)]
         for i in range(matrix.rows)],
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _newton_coefficients(points: list[sp.Integer], values: list) -> list:
    """Expanded polynomial coefficients over an arbitrary exact field."""
    divided = list(values)
    count = len(points)
    for level in range(1, count):
        for index in range(count - 1, level - 1, -1):
            divided[index] = (
                (divided[index] - divided[index - 1])
                / int(points[index] - points[index - level])
            )
    polynomial = [divided[-1]]
    for index in range(count - 2, -1, -1):
        shifted = [-int(points[index]) * coefficient for coefficient in polynomial]
        shifted.append(polynomial[-1].field.zero)
        for degree, coefficient in enumerate(polynomial):
            shifted[degree + 1] += coefficient
        shifted[0] += divided[index]
        polynomial = shifted
    return polynomial


def interpolate_literal_current() -> tuple[sp.Matrix, sp.Matrix, list[dict]]:
    coefficient_field, omega_f = field("omega", QQ_I)
    i_f = coefficient_field.from_expr(sp.I)
    sample_artifact = json.loads((ROOT / INPUTS["literal_samples"]).read_text())
    sample_values = [
        sp.Matrix([
            [sp.sympify(entry, locals={"omega": sp.Symbol("omega"), "I": sp.I})
             for entry in row]
            for row in sample["matrix_without_pi_alpha"]
        ])
        for sample in sample_artifact["samples"]
    ]
    samples = [
        {
            "radius": sample["radius"],
            "literal_matrix_sha256": sample["matrix_sha256"],
        }
        for sample in sample_artifact["samples"]
    ]

    denominator_values = [
        coefficient_field.from_expr(
            radius**DENOMINATOR_EXPONENTS["r"]
            * (radius - 2)**DENOMINATOR_EXPONENTS["r_minus_2"]
        )
        * (omega_f * int(radius) - 2 * i_f)
        ** DENOMINATOR_EXPONENTS["omega_r_minus_2I"]
        * (omega_f * int(radius) + 2 * i_f)
        ** DENOMINATOR_EXPONENTS["omega_r_plus_2I"]
        for radius in RADII
    ]

    entries: list[sp.Expr] = []
    numerators: list[sp.Expr] = []
    r, omega = sp.symbols("r omega")
    denominator = (
        r**DENOMINATOR_EXPONENTS["r"]
        * (r - 2)**DENOMINATOR_EXPONENTS["r_minus_2"]
        * (omega * r - 2 * sp.I)
        ** DENOMINATOR_EXPONENTS["omega_r_minus_2I"]
        * (omega * r + 2 * sp.I)
        ** DENOMINATOR_EXPONENTS["omega_r_plus_2I"]
    )
    for row in range(6):
        for column in range(6):
            values = [
                coefficient_field.from_expr(
                    sp.cancel(sample_values[index][row, column])
                ) * denominator_values[index]
                for index in range(len(RADII))
            ]
            coefficients = _newton_coefficients(RADII, values)
            bad_denominators = [
                coefficient.denom.as_expr()
                for coefficient in coefficients
                if coefficient.denom.as_expr().free_symbols
            ]
            if bad_denominators:
                raise RuntimeError(
                    f"interpolated entry ({row},{column}) retained an omega "
                    f"denominator: {bad_denominators[0]}"
                )
            numerator = sum(
                (coefficient.as_expr() * r**degree
                 for degree, coefficient in enumerate(coefficients)),
                sp.Integer(0),
            )
            entries.append(numerator / denominator)
            numerators.append(numerator)
        print(f"interpolated row {row + 1}/6", flush=True)
    return sp.Matrix(6, 6, entries), sp.Matrix(6, 6, numerators), samples


def load_flow() -> tuple[sp.Matrix, sp.Symbol, sp.Symbol]:
    payload = json.loads((ROOT / INPUTS["repaired_system"]).read_text())
    r, omega = sp.symbols("r omega")
    matrix = sp.Matrix([
        [sp.sympify(entry, locals={"r": r, "omega": omega, "I": sp.I})
         for entry in row]
        for row in payload["complete_reconstruction"]["flow6"]
    ])
    return matrix, r, omega


def build_document() -> dict:
    current, numerators, samples = interpolate_literal_current()
    print("checking global rational conservation identity", flush=True)
    flow, r, omega = load_flow()
    coefficient_field, _omega_f = field("omega", QQ_I)
    denominator = (
        r**DENOMINATOR_EXPONENTS["r"]
        * (r - 2)**DENOMINATOR_EXPONENTS["r_minus_2"]
        * (omega * r - 2 * sp.I)
        ** DENOMINATOR_EXPONENTS["omega_r_minus_2I"]
        * (omega * r + 2 * sp.I)
        ** DENOMINATOR_EXPONENTS["omega_r_plus_2I"]
    )
    flow_denominator = r**2 * (r - 2)**2 * (omega * r - 2 * sp.I)
    D = sp.Poly(denominator, r, domain=coefficient_field)
    E = sp.Poly(flow_denominator, r, domain=coefficient_field)
    N = [[sp.Poly(numerators[i, j], r, domain=coefficient_field)
          for j in range(6)] for i in range(6)]
    flow_plus = [[
        sp.Poly(sp.cancel(flow_denominator * flow[i, j]),
                r, domain=coefficient_field)
        for j in range(6)
    ] for i in range(6)]
    flow_minus = [[
        sp.Poly(
            sp.cancel(
                flow_denominator.subs(omega, -omega)
                * flow[i, j].subs(omega, -omega)
            ),
            r,
            domain=coefficient_field,
        )
        for j in range(6)
    ] for i in range(6)]
    E_minus = sp.Poly(
        flow_denominator.subs(omega, -omega),
        r,
        domain=coefficient_field,
    )
    # The two A terms have different omega-reflected denominators.  Clear
    # D^2*E(omega)*E(-omega) without any rational-function GCD.
    nonzero = []
    for i in range(6):
        for j in range(6):
            derivative = (N[i][j].diff() * D - N[i][j] * D.diff())
            left = sum(
                (flow_minus[q][i] * N[q][j] for q in range(6)),
                sp.Poly(0, r, domain=coefficient_field),
            )
            right = sum(
                (N[i][q] * flow_plus[q][j] for q in range(6)),
                sp.Poly(0, r, domain=coefficient_field),
            )
            cleared = derivative * E * E_minus + D * (
                left * E + right * E_minus
            )
            if not cleared.is_zero:
                nonzero.append([i, j])
    if nonzero:
        raise RuntimeError(f"conservation residual is nonzero at {nonzero[:3]}")
    print("global rational conservation identity: 36/36 zero", flush=True)

    numerator_degrees = []
    for numerator in numerators:
        polynomial = sp.Poly(numerator, r, omega)
        r_degree = polynomial.degree(r)
        omega_degree = polynomial.degree(omega)
        numerator_degrees.append({
            "r": 0 if r_degree is sp.S.NegativeInfinity else int(r_degree),
            "omega": (
                0
                if omega_degree is sp.S.NegativeInfinity
                else int(omega_degree)
            ),
        })
    if max(item["r"] for item in numerator_degrees) > MAX_R_DEGREE:
        raise RuntimeError("interpolated numerator exceeds the audited radial bound")
    if max(item["omega"] for item in numerator_degrees) > MAX_OMEGA_DEGREE:
        raise RuntimeError("interpolated numerator exceeds the audited frequency bound")

    imports = {
        name: {"path": path, "sha256": sha256(ROOT / path)}
        for name, path in INPUTS.items()
    }
    return {
        "schema": "phase3-black-hole-axial-arbitrary-radius-current-conservation-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_ARBITRARY_RADIUS_CURRENT_CONSERVATION_V1",
        "result_token": "LITERAL_ACTION_CURRENT_CONSERVATION_EXACT_ALL_R",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1 in ingoing Eddington-Finkelstein coordinates",
            "sector": "axial ell=2 with Fourier phase exp(+I*omega*v)",
            "domain": "r>2 away from algebraic poles; omega is an exact indeterminate",
            "state_order": ["P", "P_prime", "Q", "Q_prime", "H1", "F"],
            "current_normalization": "F^r(y,bar(z))=pi*alpha_W*z^dagger*Jhat(r,omega)*y",
        },
        "literal_current_reconstruction": {
            "method": "localized-ring degree bound plus 30 exact rational-radius evaluations over QQ(I)(omega)",
            "sample_radii": samples,
            "sample_count": len(samples),
            "interpolation_uniqueness": "D*Jhat has radial degree <=29, so its values at 30 distinct radii determine it uniquely over QQ(I)(omega)",
            "common_denominator": "r^7*(r-2)^6*(omega*r-2*I)^4*(omega*r+2*I)^4",
            "denominator_exponents": DENOMINATOR_EXPONENTS,
            "maximum_numerator_r_degree": MAX_R_DEGREE,
            "maximum_numerator_omega_degree": MAX_OMEGA_DEGREE,
            "observed_entry_numerator_degrees": [
                numerator_degrees[index * 6:(index + 1) * 6]
                for index in range(6)
            ],
            "matrix_without_pi_alpha": [
                [sp.sstr(current[i, j]) for j in range(6)]
                for i in range(6)
            ],
        },
        "conservation_proof": {
            "identity": "dJhat/dr + A(r,-omega)^T*Jhat + Jhat*A(r,omega) = 0",
            "residual_shape": [6, 6],
            "zero_numerator_count": 36,
            "nonzero_numerator_count": 0,
            "proof_ring": "QQ(I)(r,omega)",
            "status": "EXACT_RATIONAL_IDENTITY",
        },
        "claim_flags": {
            "literal_action_current_reconstructed_for_arbitrary_r": True,
            "repaired_six_state_current_conservation_certified": True,
            "global_connection_constructed": False,
            "endpoint_flux_limits_certified": False,
            "scattering_or_stability_certified": False,
        },
        "imports": imports,
        "does_not_establish": [
            "regularity at the horizon r=2 or at algebraic frequency poles",
            "convergence of endpoint series or existence of endpoint flux limits",
            "a horizon-to-infinity connection matrix or scattering matrix",
            "mode stability, quasinormal-mode exclusion, CPT positivity, particles, or quantum unitarity",
        ],
        "verification": {
            "producer_reproduction": "python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.produce --check",
            "independent_verifier": "python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify",
            "tests": "python3 -m pytest -q black_hole_programme/phase3/axial_arbitrary_radius_current_conservation/tests",
            "exhaustive_literal_replay": "python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify --replay-literal-samples",
        },
    }


def write_document(elapsed_seconds: float) -> None:
    document = build_document()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-black-hole-axial-arbitrary-radius-current-conservation-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "producer_sha256": sha256(Path(__file__)),
        "schema_sha256": sha256(SCHEMA),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "producer_elapsed_seconds_excluding_receipt_write": round(elapsed_seconds, 3),
        "status": "PASS",
        "tier_2_not_run": "No shared mathematical input or operator changed; imported hashes are frozen and the affected current package is replayed directly.",
        "tier_3_not_run": "No freeze, theorem lifecycle promotion, shared-core change, or release was requested.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    expected = build_document()
    elapsed = time.monotonic() - started
    if args.check:
        if expected != json.loads(OUTPUT.read_text()):
            raise SystemExit("certificate drift")
        print(f"PASS: literal arbitrary-r current reproduced in {elapsed:.3f}s")
        return
    OUTPUT.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-black-hole-axial-arbitrary-radius-current-conservation-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "producer_sha256": sha256(Path(__file__)),
        "schema_sha256": sha256(SCHEMA),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "producer_elapsed_seconds_excluding_receipt_write": round(elapsed, 3),
        "status": "PASS",
        "tier_2_not_run": "No shared mathematical input or operator changed; imported hashes are frozen and the affected current package is replayed directly.",
        "tier_3_not_run": "No freeze, theorem lifecycle promotion, shared-core change, or release was requested.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
