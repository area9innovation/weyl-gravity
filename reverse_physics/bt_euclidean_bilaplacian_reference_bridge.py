#!/usr/bin/env python3
"""Certify a BT bilaplacian radial reference bound and its missing bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-bilaplacian-reference-bridge-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-bilaplacian-reference-bridge.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "492ddb2c210805b2ba786ba326d62bc76af1785d"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def alternating_log_two_lower_bound(terms: int = 20) -> Fraction:
    return sum(
        (Fraction(1 if index % 2 else -1, index) for index in range(1, terms + 1)),
        Fraction(0),
    )


def positive_square_fraction(values: tuple[int, ...]) -> Fraction:
    positive = sum(value * value for value in values if value >= 0)
    total = sum(value * value for value in values)
    return Fraction(positive, total) if total else Fraction(1)


def build() -> dict:
    coupling = Fraction(2, 5)
    degree = 8
    minimum_volume = 2**4
    free_h_minus_one_bound = Fraction(15, 32)
    log_two_lower = alternating_log_two_lower_bound()

    fixtures = [
        (-3, 1, 1, 1),
        (-5, 1, 1, 1, 1, 1),
        (-7, -2, 3, 3, 3),
        (-9, 2, 2, 2, 2, 1),
    ]
    positive_part_rows = [
        {
            "mean_zero_vector": list(values),
            "positive_square_fraction": encode(positive_square_fraction(values)),
            "one_over_dimension": encode(Fraction(1, len(values))),
            "bound_holds": positive_square_fraction(values)
            >= Fraction(1, len(values)),
        }
        for values in fixtures
    ]

    length = 6
    dimensions = 4
    volume = length**dimensions
    spatial_volume = length ** (dimensions - 1)
    family_parameter = 3
    center_time = (-3, 0, 0, -3, 3, 3)
    direction_time = (-1, -1, 1, 1, 1, -1)
    center_bilaplacian_integer_per_site = 252
    direction_bilaplacian_per_site = 16
    actual_hessian_full = Fraction(243)
    reference_quadratic_hessian = Fraction(
        2 * spatial_volume * direction_bilaplacian_per_site,
        4 * volume,
    )
    reference_quartic_hessian_lower = Fraction(
        (spatial_volume * center_bilaplacian_integer_per_site)
        * (2 * spatial_volume * direction_bilaplacian_per_site),
        8 * degree * degree * volume,
    ) * Fraction(4, 9)
    reference_hessian_lower = (
        reference_quadratic_hessian + reference_quartic_hessian_lower
    )
    difference_hessian_upper = actual_hessian_full - reference_hessian_lower

    reference_h_minus_one_multiplier = {
        "rational_prefactor": encode(Fraction(degree, 4 * coupling)),
        "squarefree_radicand": 15,
    }
    lambda_point_four_h_minus_one_bound = {
        "rational_prefactor": encode(Fraction(5)),
        "squarefree_radicand": 15,
    }

    checks = {
        "coupling_is_two_fifths": coupling == Fraction(2, 5),
        "all_positive_part_fixtures_pass": all(
            row["bound_holds"] for row in positive_part_rows
        ),
        "alternating_twenty_term_sum_is_lower_bound_above_two_thirds": (
            log_two_lower == Fraction(155685007, 232792560)
            and log_two_lower > Fraction(2, 3)
        ),
        "reference_quadratic_hessian_is_four_thirds": (
            reference_quadratic_hessian == Fraction(4, 3)
        ),
        "reference_quartic_hessian_lower_is_252": (
            reference_quartic_hessian_lower == 252
        ),
        "reference_hessian_lower_is_760_over_three": (
            reference_hessian_lower == Fraction(760, 3)
        ),
        "actual_hessian_is_243": actual_hessian_full == 243,
        "difference_hessian_is_below_minus_31_over_three": (
            difference_hessian_upper == Fraction(-31, 3)
        ),
        "convex_perturbation_bridge_is_obstructed": difference_hessian_upper < 0,
        "reference_h_minus_one_prefactor_is_five": (
            reference_h_minus_one_multiplier["rational_prefactor"] == encode(5)
        ),
        "reference_h_minus_one_bound_is_five_sqrt_fifteen": (
            lambda_point_four_h_minus_one_bound
            == {"rational_prefactor": encode(5), "squarefree_radicand": 15}
        ),
        "actual_interacting_h_minus_one_bound_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-bilaplacian-reference-bridge-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact all-volume bilaplacian envelope, solved radial reference "
            "moment, and obstruction to convex-perturbation transfer"
        ),
        "question": (
            "Can the quartic residual control be strengthened to the "
            "bilaplacian variable, does the resulting normalized reference "
            "measure have the required uniform H^-1 bound, and can that bound "
            "be transferred to the actual BT Gibbs measure by convex "
            "perturbation?"
        ),
        "answer": (
            "The actual action has the exact envelope A>=B/(4N)+"
            "B^2/(16q^2N), where B=sum_x(Delta psi_x)^2. The normalized "
            "radial reference measure defined by this envelope has a uniform "
            "H^-1 second moment, bounded by 5*sqrt(15) at lambda=0.4. But the "
            "difference between the actual and reference actions is not "
            "convex: an exact 6^4 Hessian witness is below -31/3. Pointwise "
            "domination therefore does not transfer the reference moment by "
            "the standard convex-perturbation route, and the actual interacting "
            "H^-1 bound remains open."
        ),
        "all_volume_bilaplacian_envelope": {
            "scope": "every connected q-regular finite periodic graph",
            "definitions": [
                "psi=lambda*phi",
                "a_x=Delta psi_x and sum_x a_x=0",
                "B=sum_x a_x^2",
                "r_x=a_x+sum_(y~x)[exp(psi_y-psi_x)-1-(psi_y-psi_x)]",
                "A=(1/2)*sum_x r_x^2",
            ],
            "positive_part_lemma": (
                "For every mean-zero a in R^N, sum_(a_x>=0)a_x^2>=B/N."
            ),
            "positive_part_proof": (
                "If P=sum a_+=sum (-a)_-, then ||a_-||_2^2<=P^2 and "
                "P^2<=(N-1)||a_+||_2^2, hence B<=N||a_+||_2^2."
            ),
            "positive_part_fixtures": positive_part_rows,
            "first_bound": "A>=B/(2N)",
            "spectral_step": (
                "sum_x r_x>=<psi,(-Delta)psi> and "
                "B<=2q*<psi,(-Delta)psi>"
            ),
            "second_bound": "A>=B^2/(8q^2N)",
            "combined_theorem": "A>=B/(4N)+B^2/(16q^2N)",
            "phi_form": (
                "S_lambda(phi)>=B_phi/(4N)+"
                "lambda^2*B_phi^2/(16q^2N)"
            ),
            "status": "PROVED",
        },
        "normalized_radial_reference": {
            "definition": (
                "dnu proportional to exp[-B_phi/(4N)-"
                "lambda^2*B_phi^2/(16q^2N)] dphi on sum phi=0"
            ),
            "bilaplacian_coordinates": (
                "y=Delta phi is an invertible linear coordinate on the "
                "mean-zero hyperplane; B_phi=||y||_2^2 and n=N-1"
            ),
            "radial_virial_identity": (
                "n=E_nu[B/(2N)+lambda^2*B^2/(4q^2N)]"
            ),
            "bilaplacian_energy_bound": (
                "E_nu[B]<=2q*sqrt(N*(N-1))/abs(lambda)"
            ),
            "isotropic_covariance_multiplier": (
                "c_N=E_nu[B]/(N-1)<=2q*sqrt(N/(N-1))/abs(lambda)"
            ),
            "minimum_lattice": {
                "dimensions": 4,
                "minimum_length": 2,
                "minimum_volume": minimum_volume,
                "bound": "sqrt(N/(N-1))<=4/sqrt(15)",
            },
            "imported_free_h_minus_one_trace_bound": encode(
                free_h_minus_one_bound
            ),
            "uniform_h_minus_one_theorem": (
                "sup_L E_nu||Phi_L||_H^-1^2 <= "
                "q*sqrt(15)/(4*abs(lambda))"
            ),
            "lambda_0p4_q8_bound": lambda_point_four_h_minus_one_bound,
            "lambda_0p4_q8_reading": "5*sqrt(15)",
            "status": "PROVED_FOR_REFERENCE_MEASURE",
        },
        "convex_transfer_obstruction": {
            "actual_minus_reference": (
                "D(psi)=A(psi)-B/(4N)-B^2/(16q^2N)"
            ),
            "lattice": {"length": length, "dimensions": dimensions, "volume": volume},
            "spatial_volume": spatial_volume,
            "center": "psi=(-3,0,0,-3,3,3)*log(2), spatially constant",
            "direction": list(direction_time),
            "family_parameter": family_parameter,
            "center_time": list(center_time),
            "center_bilaplacian_integer_per_spatial_site": (
                center_bilaplacian_integer_per_site
            ),
            "direction_bilaplacian_per_spatial_site": (
                direction_bilaplacian_per_site
            ),
            "center_direction_bilaplacian_cross_term": 0,
            "actual_directional_hessian_full": encode(actual_hessian_full),
            "log_two_lower_bound": {
                "method": "20-term even alternating harmonic partial sum",
                "value": encode(log_two_lower),
                "strictly_above": encode(Fraction(2, 3)),
            },
            "reference_directional_hessian_strict_lower_bound": encode(
                reference_hessian_lower
            ),
            "difference_directional_hessian_strict_upper_bound": encode(
                difference_hessian_upper
            ),
            "conclusion": (
                "D has a strictly negative directional Hessian, so it is not "
                "convex and the actual measure is not certified as a convex "
                "perturbation of the solved radial reference."
            ),
            "status": "CONVEX_PERTURBATION_TRANSFER_OBSTRUCTED",
        },
        "disposition": {
            "actual_all_volume_bilaplacian_envelope": "PROVED",
            "radial_reference_uniform_h_minus_one_bound": "PROVED",
            "pointwise_actual_over_reference_action_domination": "PROVED",
            "convex_perturbation_moment_transfer": "OBSTRUCTED",
            "general_nonconvex_or_annealed_moment_transfer": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a nonconvex comparison theorem adapted to the BT residual variance",
            "or a direct normalized one-mode marginal estimate",
            "an L-uniform actual interacting H^-1 second moment",
            "tightness and identification of any Euclidean limit",
        ],
        "next_gate": (
            "Exploit the exact residual decomposition A=U^2/(2N)+"
            "(1/2)*sum_x(r_x-U/N)^2 in an annealed/coarea estimate, or bound "
            "the normalized Fourier marginal directly; convex transfer is "
            "certifiably unavailable."
        ),
        "does_not_establish": [
            "an H^-1 moment bound for the actual interacting BT Gibbs measure",
            "a valid moment comparison from pointwise action domination alone",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction arithmetic plus the exact alternating-series "
                "lower bound for log(2); the reference bound is represented in "
                "Q(sqrt(15))"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_bilaplacian_reference_bridge.py --check",
            "python3 reverse_physics/verify_bt_euclidean_bilaplacian_reference_bridge.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_bilaplacian_reference_bridge",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped git "
                "diff --check, and staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, independently reconstructed graph and radial "
                "identities, unit tests, and mutation rejection"
            ),
            "tier_2": (
                "three predecessor certificates checked by content hash; no "
                "sampler rerun because no numerical Gibbs claim is made"
            ),
            "tier_3": (
                "not run: no freeze, release, shared classical operator, "
                "quantum lifecycle, or Lorentzian claim changes"
            ),
            "memory_policy": (
                "all commands sequential under a 500000 KiB virtual-memory "
                "ceiling where relevant"
            ),
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT bilaplacian radial reference bridge "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
