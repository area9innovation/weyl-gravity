#!/usr/bin/env python3
"""Build the exact BT canonical-radial pointwise obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_RADIAL_POINTWISE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-canonical-radial-pointwise-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-canonical-radial-pointwise-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_canonical_radial_pointwise_obstruction.py"
)
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_PHASE_SCORE_CONNECTION_V1.json"
)
SOURCE_COMMIT = "023cfc8abf180316fcf7e7f341335ac27677c5d5"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def enc_vector(values: list[Fraction]) -> list[dict[str, int]]:
    return [enc(value) for value in values]


def enc_matrix(values: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [enc_vector(row) for row in values]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def additive_fixture() -> dict:
    """C6 tensor lift; sine entries are stored as coefficients of sqrt(3)."""
    exponents = [2, -2, 2, 0, -1, 0]
    reciprocal_weights = [1, 16, 1, 4, 8, 4]
    denominator = sum(reciprocal_weights)
    marginal = [Fraction(value, denominator) for value in reciprocal_weights]
    cosine = [
        Fraction(1), Fraction(1, 2), Fraction(-1, 2),
        Fraction(-1), Fraction(-1, 2), Fraction(1, 2),
    ]
    sine_sqrt3 = [
        Fraction(), Fraction(1, 2), Fraction(1, 2),
        Fraction(), Fraction(-1, 2), Fraction(-1, 2),
    ]
    transverse = 6**3
    f_cosine = transverse * sum(
        (Fraction(n) * h for n, h in zip(exponents, cosine)), Fraction()
    )
    f_sine_sqrt3 = transverse * sum(
        (Fraction(n) * h for n, h in zip(exponents, sine_sqrt3)), Fraction()
    )
    z_cosine = sum(
        (p * h for p, h in zip(marginal, cosine)), Fraction()
    )
    z_sine_sqrt3 = sum(
        (p * h for p, h in zip(marginal, sine_sqrt3)), Fraction()
    )
    dot_coefficient = (
        f_cosine * z_cosine + 3 * f_sine_sqrt3 * z_sine_sqrt3
    )
    return {
        "length": 6,
        "transverse_multiplicity": transverse,
        "log2_exponents": exponents,
        "reciprocal_integer_weights": reciprocal_weights,
        "reciprocal_marginal": marginal,
        "phase_cosine": cosine,
        "phase_sine_sqrt3_coefficients": sine_sqrt3,
        "field_phase_over_log2": [f_cosine, f_sine_sqrt3],
        "constant_frame_phase_derivative": [z_cosine, z_sine_sqrt3],
        "field_dot_derivative_over_log2": dot_coefficient,
    }


def canonical_fixture() -> dict:
    """C4 tensor lift at lambda=2/5, using only exact rational arithmetic."""
    exponents = [-1, 0, -1, 1]
    omega_values = [Fraction(1, 2), Fraction(1), Fraction(1, 2), Fraction(2)]
    transverse = 4**3
    reciprocal_weights = [4, 2, 4, 1]
    marginal = [Fraction(value, 11) for value in reciprocal_weights]
    phase = [
        [Fraction(1), Fraction()],
        [Fraction(), Fraction(1)],
        [Fraction(-1), Fraction()],
        [Fraction(), Fraction(-1)],
    ]
    residual = []
    for site, value in enumerate(omega_values):
        laplacian = (
            omega_values[(site - 1) % 4]
            + omega_values[(site + 1) % 4]
            - 2 * value
        )
        residual.append(laplacian / value)
    gram = [
        [
            sum(
                (marginal[x] * phase[x][i] * phase[x][j] for x in range(4)),
                Fraction(),
            )
            for j in range(2)
        ]
        for i in range(2)
    ]
    gram_inverse = [
        [1 / gram[0][0], Fraction()],
        [Fraction(), 1 / gram[1][1]],
    ]
    lambda_squared = Fraction(4, 25)
    frequency = Fraction(2)
    ward_score = []
    for component in range(2):
        residual_part = sum(
            (
                marginal[x]
                * phase[x][component]
                * (residual[x] ** 2 + frequency * residual[x])
                for x in range(4)
            ),
            Fraction(),
        )
        entropy_part = sum(
            (
                marginal[x]
                * (1 - marginal[x] / transverse)
                * phase[x][component]
                for x in range(4)
            ),
            Fraction(),
        )
        ward_score.append(-residual_part / lambda_squared + entropy_part)
    connection = [Fraction(), Fraction()]
    for x in range(4):
        inverse_phase = [
            sum(
                (gram_inverse[i][j] * phase[x][j] for j in range(2)),
                Fraction(),
            )
            for i in range(2)
        ]
        leverage = sum(
            (phase[x][i] * inverse_phase[i] for i in range(2)), Fraction()
        )
        weight = marginal[x] ** 2 * (leverage - 1) / transverse
        for i in range(2):
            connection[i] += weight * inverse_phase[i]
    canonical_score = [
        sum(
            (gram_inverse[i][j] * ward_score[j] for j in range(2)),
            Fraction(),
        )
        - connection[i]
        for i in range(2)
    ]
    field_phase_over_log2 = [
        transverse
        * sum(
            (Fraction(exponents[x]) * phase[x][i] for x in range(4)),
            Fraction(),
        )
        for i in range(2)
    ]
    dot_coefficient = sum(
        (field_phase_over_log2[i] * canonical_score[i] for i in range(2)),
        Fraction(),
    )
    return {
        "length": 4,
        "transverse_multiplicity": transverse,
        "lambda": Fraction(2, 5),
        "log2_exponents": exponents,
        "omega_values": omega_values,
        "reciprocal_integer_weights": reciprocal_weights,
        "reciprocal_marginal": marginal,
        "residual": residual,
        "gram": gram,
        "gram_inverse": gram_inverse,
        "ward_score": ward_score,
        "connection": connection,
        "canonical_score": canonical_score,
        "field_phase_over_log2": field_phase_over_log2,
        "field_dot_score_over_log2": dot_coefficient,
    }


def build() -> dict:
    additive = additive_fixture()
    canonical = canonical_fixture()
    checks = {
        "additive_marginal_normalized": sum(additive["reciprocal_marginal"]) == 1,
        "additive_phase_is_mean_zero": (
            sum(additive["phase_cosine"]) == 0
            and sum(additive["phase_sine_sqrt3_coefficients"]) == 0
        ),
        "additive_field_phase": additive["field_phase_over_log2"] == [108, 108],
        "additive_derivative_phase": (
            additive["constant_frame_phase_derivative"]
            == [Fraction(5, 68), Fraction(5, 68)]
        ),
        "additive_outward_sign": (
            additive["field_dot_derivative_over_log2"] == Fraction(540, 17)
        ),
        "canonical_marginal_normalized": sum(canonical["reciprocal_marginal"]) == 1,
        "canonical_residual": canonical["residual"] == [4, -1, 4, Fraction(-3, 2)],
        "canonical_gram": canonical["gram"] == [
            [Fraction(8, 11), Fraction()],
            [Fraction(), Fraction(3, 11)],
        ],
        "canonical_ward_score": canonical["ward_score"] == [
            Fraction(), Fraction(6201, 7744)
        ],
        "canonical_connection": canonical["connection"] == [
            Fraction(), Fraction(1, 264)
        ],
        "canonical_score": canonical["canonical_score"] == [
            Fraction(), Fraction(563, 192)
        ],
        "canonical_field_phase": canonical["field_phase_over_log2"] == [0, -64],
        "canonical_inward_sign_fails": (
            canonical["field_dot_score_over_log2"] == Fraction(-563, 3)
        ),
        "input_hash_present": len(sha256(INPUT_REL)) == 64,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"internal exact checks failed: {failed}")
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "CANONICAL_RADIAL_POINTWISE_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "canonical-radial-pointwise-obstruction-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
        ],
        "lifecycle_state": "POINTWISE_RADIAL_SCORE_METHODS_OBSTRUCTED",
        "result_kind": "exact finite-volume method obstruction",
        "question": (
            "Can the normalized additive contraction or the field-level "
            "canonical phase score furnish a pointwise radial Lyapunov sign "
            "for the complete lowest Fourier phase?"
        ),
        "answer": (
            "No. Exact tensor-lifted BT configurations make the additive "
            "contraction increase the phase norm and make F dot S negative. "
            "Only an annealed conditional-score or full Witten-form estimate "
            "survives; no actual moment divergence is proved."
        ),
        "definitions": {
            "phase": "F_i=sum_x h_i(x)*psi_x",
            "constant_frame": "X_1=pi-N^-1*1",
            "canonical_score": "S=G^-1*Y-C",
            "marginal_score": "bar_S(F)=E[S|F]=-grad_F log rho_F",
            "exact_normalization": "E[F_k*bar_S_i(F)]=delta_ik",
            "radial_normalization": "E[F dot bar_S(F)]=2",
        },
        "additive_contraction_fixture": {
            "lattice": "periodic 6^4 torus, axial field repeated transversely",
            "transverse_multiplicity": additive["transverse_multiplicity"],
            "log2_exponents": additive["log2_exponents"],
            "reciprocal_integer_weights": additive["reciprocal_integer_weights"],
            "reciprocal_marginal": enc_vector(additive["reciprocal_marginal"]),
            "phase_cosine": enc_vector(additive["phase_cosine"]),
            "phase_sine_sqrt3_coefficients": enc_vector(
                additive["phase_sine_sqrt3_coefficients"]
            ),
            "field_phase_over_log2": enc_vector(additive["field_phase_over_log2"]),
            "constant_frame_phase_derivative": enc_vector(
                additive["constant_frame_phase_derivative"]
            ),
            "field_dot_derivative_over_log2": enc(
                additive["field_dot_derivative_over_log2"]
            ),
            "sign": "F dot (X_1 F)=(540/17)*log(2)>0",
            "disposition": "POINTWISE_PHASE_NORM_CONTRACTION_FALSE",
        },
        "canonical_score_fixture": {
            "lattice": "periodic 4^4 torus, axial field repeated transversely",
            "transverse_multiplicity": canonical["transverse_multiplicity"],
            "lambda": enc(canonical["lambda"]),
            "log2_exponents": canonical["log2_exponents"],
            "omega_values": enc_vector(canonical["omega_values"]),
            "reciprocal_integer_weights": canonical["reciprocal_integer_weights"],
            "reciprocal_marginal": enc_vector(canonical["reciprocal_marginal"]),
            "residual": enc_vector(canonical["residual"]),
            "gram": enc_matrix(canonical["gram"]),
            "gram_inverse": enc_matrix(canonical["gram_inverse"]),
            "ward_score": enc_vector(canonical["ward_score"]),
            "connection": enc_vector(canonical["connection"]),
            "canonical_score": enc_vector(canonical["canonical_score"]),
            "field_phase_over_log2": enc_vector(
                canonical["field_phase_over_log2"]
            ),
            "field_dot_score_over_log2": enc(
                canonical["field_dot_score_over_log2"]
            ),
            "sign": "F dot S=-(563/3)*log(2)<0",
            "disposition": "POINTWISE_FIELD_SCORE_RADIAL_MONOTONICITY_FALSE",
        },
        "annealed_boundary": {
            "surviving_object": "bar_S(F)=E[S|F]",
            "surviving_identity": "E[F dot bar_S(F)]=2",
            "why_fixture_is_not_marginal_no_go": (
                "A sign at one full-field configuration does not determine "
                "the conditional average over its phase fiber."
            ),
            "required_next_estimate": (
                "Prove a lower radial/form bound for bar_S or the full Witten "
                "operator, or construct an actual normalized low-Rayleigh sequence."
            ),
            "status": "ANNEALED_COERCIVITY_OPEN",
        },
        "method_disposition": {
            "normalized_additive_action_contraction": "PROVED_PREDECESSOR",
            "additive_pointwise_lowest_phase_contraction": "OBSTRUCTED",
            "canonical_score_integrability": "PROVED_PREDECESSOR",
            "field_level_pointwise_radial_score_sign": "OBSTRUCTED",
            "conditional_marginal_score_coercivity": "OPEN",
            "full_witten_form_coercivity": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a coercive estimate for the conditional marginal score E[S|F]",
            "a relative lower bound for the complete lowest-phase Witten form or an actual low-Rayleigh sequence",
            "a volume-uniform normalized lowest-mode second moment",
            "the dyadic interacting H^-1 bound or an actual diverging BT volume sequence",
        ],
        "next_gate": (
            "Work only after conditional averaging: estimate the marginal "
            "radial score or the full Witten quadratic form using the certified "
            "score moments. Do not reuse either failed pointwise sign."
        ),
        "does_not_establish": [
            "failure of canonical marginal-score or Witten coercivity",
            "a low-Rayleigh sequence for the full BT Witten operator",
            "boundedness or divergence of the normalized lowest-mode or interacting H^-1 moment",
            "tightness or a continuum Euclidean BT measure",
            "a change to the scoped ordinary Osterwalder-Schrader obstruction",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "arithmetic": (
                "Exact Fraction arithmetic in Q and Q(sqrt(3)); log(2) is "
                "retained symbolically and only its strict positivity is used."
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_canonical_radial_pointwise_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_canonical_radial_pointwise_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_canonical_radial_pointwise_obstruction",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, JSON/schema parse, scoped diff check, explicit-path inspection, and input hash audit.",
            "tier_1": "Deterministic producer, nonimporting verifier, and focused mutation suite.",
            "tier_2": "The sole mathematical input is unchanged and checked by exact SHA-256; no predecessor rebuild required.",
            "tier_3": "Not run: scoped method obstruction, not a freeze, lifecycle promotion, shared-core change, or release.",
            "memory_policy": "All Python rails run sequentially under ulimit -v 500000.",
            "elapsed_seconds_and_peak_kib": {
                "producer": "0.04 s, 20,660 KiB",
                "verifier": "0.10 s, 30,540 KiB",
                "tests": "0.13 s, 30,584 KiB; 10 tests including 6 mutations",
                "compile": "0.04 s, 16,364 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "Initial combined-shell invocation failed because the preceding Python "
                    "ulimit was inherited by Go; a fresh-shell retry under GOMEMLIMIT=300MiB "
                    "and GOGC=50 PASSed with 1,675 nodes, 0 invalid items, and 0 malformed events"
                ),
                "diff_check": "PASS on the explicit certificate package and seq-61 planning event",
                "science_forge_shadow": (
                    "Advisory wrapper exited 0; underlying bridge audit failed closed "
                    "because sympy was unavailable, and the census reported 1,810 "
                    "certificates versus the stale 976 baseline. These are findings, not passes."
                ),
                "higher_tiers": "Tier 3 not applicable by the stated criterion.",
            },
        },
        "checks": {
            "ok": True,
            "passed": len(checks),
            "total": len(checks),
            "failures": [],
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate read: {exc}")
            return 1
        if current != rendered:
            print("[FAIL] certificate differs from deterministic build")
            return 1
        print(f"[PASS] deterministic certificate ({len(certificate['checks']['details'])} checks)")
        return 0
    os.makedirs(os.path.dirname(CERT_PATH), exist_ok=True)
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    print(CERT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
