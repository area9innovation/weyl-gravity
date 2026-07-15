"""Exact Einstein-incidence test for the positive Berger clock background.

The classical Berger certificate solves the Weyl--matter equations

    alpha_B B_ab = T_ab

on a non-conformally-flat static Berger cylinder.  This module asks the
logically separate question whether the same metric and clock stress also
solve an Einstein--matter equation for any constants kappa and Lambda.

The answer is no on the certified open q interval.  The result is a
background obstruction, so it deliberately stops before constructing a
linearized Einstein complex at a base point which is not an Einstein--matter
solution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/berger_einstein_incidence.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/berger_einstein_incidence.schema.json"
BACKGROUND = ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json"
RETAINED_OPERATOR = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_SDR = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"


class BergerEinsteinIncidenceError(RuntimeError):
    """Raised when an imported gate or exact incidence identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BergerEinsteinIncidenceError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _exact_data() -> dict[str, Any]:
    q, a, alpha_b = sp.symbols("q a alpha_B", positive=True, real=True)
    kappa, cosmological = sp.symbols("kappa Lambda", real=True)
    eta = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(
        0,
        (2 - q) / (2 * a**2),
        (2 - q) / (2 * a**2),
        q / (2 * a**2),
    )
    scalar = sp.factor((4 - q) / (2 * a**2))
    bach = sp.diag(
        (1 - q) ** 2 / (6 * a**4),
        (1 - q) * (1 - 3 * q) / (6 * a**4),
        (1 - q) * (1 - 3 * q) / (6 * a**4),
        (1 - q) * (5 * q - 1) / (6 * a**4),
    )
    stress = sp.simplify(alpha_b * bach)

    _require(sp.simplify(sp.trace(eta * bach)) == 0, "Berger Bach trace changed")
    _require(bach[0, 0] != 0, "symbolic Bach obstruction unexpectedly vanished")

    # Ric=Lambda g would force Lambda=0 from the 00 component, after which
    # the positive spatial Ricci components cannot vanish on 0<q<1/4.
    einstein_lambda_from_00 = sp.S.Zero
    einstein_spatial_residual = sp.factor(ricci[1, 1])

    # A four-dimensional conformally Einstein metric is Bach-flat.  The 00
    # component is strictly positive throughout the certified interval.
    conformal_einstein_bach_obstruction = sp.factor(bach[0, 0])

    # For G+Lambda g=kappa T with trace-free T, the trace fixes Lambda=R/4.
    # The remaining equation is S_ab=(kappa alpha_B)B_ab.  A single exact
    # 2x2 minor of the (S,B) component columns rules out proportionality.
    trace_fixed_lambda = sp.factor(scalar / 4)
    tracefree_ricci = sp.simplify(ricci - trace_fixed_lambda * eta)
    proportionality_minor_0011 = sp.factor(
        tracefree_ricci[0, 0] * bach[1, 1]
        - tracefree_ricci[1, 1] * bach[0, 0]
    )
    expected_minor = -q * (1 - q) / (8 * a**6)
    _require(
        sp.simplify(proportionality_minor_0011 - expected_minor) == 0,
        "Einstein--clock proportionality obstruction changed",
    )

    einstein_clock_residual = sp.simplify(
        ricci - scalar * eta / 2 + cosmological * eta - kappa * stress
    )
    trace_residual = sp.factor(sp.trace(eta * einstein_clock_residual))
    _require(
        sp.simplify(trace_residual - (-scalar + 4 * cosmological)) == 0,
        "Einstein--clock trace equation changed",
    )

    fixture = {q: sp.Rational(9, 40), a: 1, alpha_b: 5}
    return {
        "symbols": {
            "q": q,
            "a": a,
            "alpha_B": alpha_b,
            "kappa": kappa,
            "Lambda": cosmological,
        },
        "eta": eta,
        "ricci": ricci,
        "scalar": scalar,
        "bach": bach,
        "stress": stress,
        "einstein_lambda_from_00": einstein_lambda_from_00,
        "einstein_spatial_residual": einstein_spatial_residual,
        "conformal_einstein_bach_obstruction": conformal_einstein_bach_obstruction,
        "trace_fixed_lambda": trace_fixed_lambda,
        "tracefree_ricci": tracefree_ricci,
        "proportionality_minor_0011": proportionality_minor_0011,
        "fixture": {
            "ricci": ricci.subs(fixture),
            "scalar": scalar.subs(fixture),
            "bach": bach.subs(fixture),
            "stress": stress.subs(fixture),
            "trace_fixed_lambda": trace_fixed_lambda.subs(fixture),
            "proportionality_minor_0011": proportionality_minor_0011.subs(fixture),
        },
    }


def build_certificate() -> dict[str, Any]:
    background = _load(BACKGROUND)
    retained = _load(RETAINED_OPERATOR)
    clock_sdr = _load(CLOCK_SDR)
    _require(
        background.get("result_id") == "POSITIVE_BERGER_CLOCK_BACKGROUND"
        and background.get("claim_status") == "CERTIFIED_EXACT_BACKGROUND"
        and background.get("flags", {}).get("exact_backreacted_background_exists") is True
        and background.get("berger_geometry", {}).get("nonconformally_flat_on_solution_interval") is True,
        "positive Berger background import gate changed",
    )
    _require(
        retained.get("result_id") == "BERGER_RETAINED_MINIMAL_OPERATOR"
        and retained.get("claim_status") == "CERTIFIED_COMPLETE_MINIMAL_Q1"
        and retained.get("flags", {}).get("BERGER_RETAINED_MINIMAL_OPERATOR") is True
        and retained.get("flags", {}).get("BERGER_NONMINIMAL_COMPLETION") is False,
        "retained Berger operator import gate changed",
    )
    _require(
        clock_sdr.get("result_id") == "BERGER_MINIMAL_BV_CLOCK_SDR"
        and clock_sdr.get("flags", {}).get("support_local_clock_SDR_exact") is True,
        "Berger clock SDR import gate changed",
    )

    data = _exact_data()
    fixture = data["fixture"]
    return {
        "schema": "berger-einstein-incidence-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "BERGER_EINSTEIN_INCIDENCE",
        "result_state": "EXACT_BACKGROUND_NONINCIDENCE_CERTIFIED_TANGENT_EMBEDDING_NOT_APPLICABLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                "positive_berger_clock_background": {
                    "path": str(BACKGROUND.relative_to(ROOT)),
                    "sha256": _sha256(BACKGROUND),
                },
                "berger_retained_minimal_operator": {
                    "path": str(RETAINED_OPERATOR.relative_to(ROOT)),
                    "sha256": _sha256(RETAINED_OPERATOR),
                },
                "berger_minimal_bv_clock_sdr": {
                    "path": str(CLOCK_SDR.relative_to(ROOT)),
                    "sha256": _sha256(CLOCK_SDR),
                },
            },
        },
        "domain": {
            "metric": "g=-dt^2+a^2(sigma_1^2+sigma_2^2)+q a^2 sigma_3^2",
            "signature": "(-,+,+,+)",
            "parameter_interval": background["exact_solution_family"]["parameter_interval"],
            "assumptions": ["a>0", "alpha_B>0", "(5-sqrt(21))/2<q<1/4"],
            "weyl_matter_equation": "alpha_B B_ab=T_ab",
            "einstein_matter_test_equation": "G_ab+Lambda g_ab=kappa T_ab",
        },
        "exact_tensors": {
            "ricci_orthonormal": _matrix_strings(data["ricci"]),
            "scalar_curvature": str(data["scalar"]),
            "bach_orthonormal": _matrix_strings(data["bach"]),
            "clock_stress_orthonormal": _matrix_strings(data["stress"]),
            "tracefree_ricci_orthonormal": _matrix_strings(data["tracefree_ricci"]),
        },
        "incidence_tests": {
            "einstein": {
                "status": "REFUTED_ON_CERTIFIED_INTERVAL",
                "lambda_from_00": str(data["einstein_lambda_from_00"]),
                "spatial_residual_after_00": str(data["einstein_spatial_residual"]),
                "reason": "Ric_00=0 forces Lambda=0, while Ric_11=(2-q)/(2a^2)>0",
            },
            "conformally_einstein": {
                "status": "REFUTED_ON_CERTIFIED_INTERVAL",
                "necessary_condition": "four-dimensional conformally Einstein metrics are Bach-flat",
                "obstruction": f"B_00={data['conformal_einstein_bach_obstruction']}>0",
            },
            "einstein_with_same_clock_stress": {
                "status": "REFUTED_FOR_ALL_CONSTANT_KAPPA_AND_LAMBDA_ON_CERTIFIED_INTERVAL",
                "trace_fixed_lambda": str(data["trace_fixed_lambda"]),
                "reduced_equation": "Ric_ab-(R/4)g_ab=(kappa alpha_B)B_ab",
                "proportionality_minor_00_11": str(data["proportionality_minor_0011"]),
                "interval_reason": "-q(1-q)/(8a^6) is strictly negative for 0<q<1/4",
            },
        },
        "rational_fixture": {
            "parameters": {"q": "9/40", "a": "1", "alpha_B": "5"},
            "ricci_orthonormal": _matrix_strings(fixture["ricci"]),
            "scalar_curvature": str(fixture["scalar"]),
            "bach_orthonormal": _matrix_strings(fixture["bach"]),
            "clock_stress_orthonormal": _matrix_strings(fixture["stress"]),
            "trace_fixed_lambda": str(fixture["trace_fixed_lambda"]),
            "proportionality_minor_00_11": str(fixture["proportionality_minor_0011"]),
        },
        "classification": {
            "berger_background_in_pure_einstein_locus": False,
            "berger_background_in_conformally_einstein_locus": False,
            "berger_background_in_einstein_same_clock_locus": False,
            "berger_background_is_genuine_non_einstein_weyl_matter_branch": True,
            "same_base_point_linearized_einstein_clock_complex_exists": False,
            "retained_berger_q1_is_complete_weyl_matter_minimal_complex": True,
            "retained_berger_q1_is_einstein_tangent_subcomplex": False,
        },
        "tangent_gate": {
            "status": "NOT_APPLICABLE_AT_THIS_BASE_POINT",
            "reason": "a tangent inclusion of solution complexes requires a common background solution; the certified Berger background fails every tested Einstein incidence condition",
            "allowed_followups": [
                "classify a different common Einstein--matter/Weyl--matter background before comparing tangent complexes",
                "export delta B and delta T separately to study the affine Einstein defect around this non-Einstein branch without calling it a tangent inclusion",
                "continue the Berger nonminimal and causal programme as a Weyl--matter theorem",
            ],
        },
        "claim_flags": {
            "exact_berger_background_imported": True,
            "complete_retained_minimal_q1_imported": True,
            "support_local_clock_sdr_imported": True,
            "berger_einstein_incidence_refuted": True,
            "berger_conformally_einstein_incidence_refuted": True,
            "berger_same_clock_einstein_incidence_refuted": True,
            "berger_tangent_einstein_embedding_constructed": False,
            "berger_matter_bv_to_flat_source_ward_lift_constructed": False,
            "nonminimal_completion_claimed": False,
            "lorentzian_causal_claim": False,
            "nonlinear_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This exact theorem classifies one certified homogeneous Berger Weyl--matter background. It proves no universal obstruction to Einstein--matter backgrounds, no tangent theorem about a different common base point, and no nonminimal, causal, nonlinear, scattering, or quantum result.",
        "verification_command": "python3 -m bridge.einstein_sector.berger_einstein_incidence --verify bridge/certificates/berger_einstein_incidence.json",
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"Berger Einstein-incidence certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
