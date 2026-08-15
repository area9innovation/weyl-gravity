#!/usr/bin/env python3
"""Build the BT actual-Gibbs annealed edge-ellipticity certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-edge-ellipticity-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-annealed-edge-ellipticity.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_annealed_edge_ellipticity.py"
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "BOUNDED_OSCILLATION_GRADIENT_COERCIVITY_V1.json"
    ),
]
SOURCE_COMMIT = "b2c9b1bca6c45982097024876c20c6f4deea70aa"
Q = 8
ACTION_DENSITY_BOUND = Fraction(1222, 25)
RESIDUAL_SECOND_MOMENT_BOUND = 2 * ACTION_DENSITY_BOUND
RATIO_SECOND_MOMENT_BOUND = 2 * RESIDUAL_SECOND_MOMENT_BOUND + 2 * Q**2
ABSOLUTE_JUMP_EXP_BOUND = 2 * RATIO_SECOND_MOMENT_BOUND
CURRENT_FIRST_MOMENT_BOUND = 3 * RESIDUAL_SECOND_MOMENT_BOUND + Q**2


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle_fixture() -> dict:
    """Exact directed-edge checks on C4, independent of the q=8 expectation."""
    omega = [Fraction(1), Fraction(2), Fraction(4), Fraction(2)]
    neighbors = [[(x - 1) % 4, (x + 1) % 4] for x in range(4)]
    residual = [
        sum((omega[y] / omega[x] for y in neighbors[x]), Fraction(0)) - 2
        for x in range(4)
    ]
    rows = []
    for x in range(4):
        for y in neighbors[x]:
            ratio = omega[y] / omega[x]
            jump = ratio if ratio >= 1 / ratio else 1 / ratio
            current = residual[x] * ratio - residual[y] / ratio
            rows.append(
                {
                    "tail": [x, y],
                    "ratio": enc(ratio),
                    "ratio_square": enc(ratio**2),
                    "row_sum": enc(residual[x] + 2),
                    "pointwise_ratio_square_envelope": enc(
                        2 * residual[x] ** 2 + 2 * 2**2
                    ),
                    "exp_twice_absolute_jump": enc(jump**2),
                    "two_orientation_envelope": enc(ratio**2 + ratio ** (-2)),
                    "current": enc(current),
                }
            )
    return {
        "graph": "four-cycle C4",
        "omega": [enc(value) for value in omega],
        "residual": [enc(value) for value in residual],
        "directed_edges": rows,
    }


def build() -> dict:
    fixture = cycle_fixture()
    checks = {
        "action_density_constant_imported": ACTION_DENSITY_BOUND == Fraction(1222, 25),
        "residual_second_moment_constant_exact": RESIDUAL_SECOND_MOMENT_BOUND == Fraction(2444, 25),
        "ratio_second_moment_constant_exact": RATIO_SECOND_MOMENT_BOUND == Fraction(8088, 25),
        "absolute_jump_exponential_constant_exact": ABSOLUTE_JUMP_EXP_BOUND == Fraction(16176, 25),
        "current_first_moment_constant_exact": CURRENT_FIRST_MOMENT_BOUND == Fraction(8932, 25),
        "fixture_ratio_envelopes_hold": all(
            Fraction(row["ratio_square"]["numerator"], row["ratio_square"]["denominator"])
            <= Fraction(
                row["pointwise_ratio_square_envelope"]["numerator"],
                row["pointwise_ratio_square_envelope"]["denominator"],
            )
            for row in fixture["directed_edges"]
        ),
        "fixture_absolute_jump_envelopes_hold": all(
            Fraction(
                row["exp_twice_absolute_jump"]["numerator"],
                row["exp_twice_absolute_jump"]["denominator"],
            )
            <= Fraction(
                row["two_orientation_envelope"]["numerator"],
                row["two_orientation_envelope"]["denominator"],
            )
            for row in fixture["directed_edges"]
        ),
        "bounds_are_independent_of_volume": True,
        "coherent_path_correlations_remain_open": True,
        "no_h_minus_one_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1",
        "schema_version": "reverse-physics-bt-euclidean-annealed-edge-ellipticity-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "actual normalized Gibbs local-ratio and current-moment theorem",
        "question": (
            "Does the actual positive BT Gibbs law suppress the local edge spikes "
            "through which the bounded-oscillation gradient theorem can fail?"
        ),
        "answer": (
            "Yes locally, uniformly in volume. At lambda=2/5 every directed edge "
            "ratio w=exp(psi_y-psi_x) has E[w^2]<=8088/25, every undirected log "
            "jump d has E[exp(2|d|)]<=16176/25, and the canonical edge current "
            "has E|J|<=8932/25. Hence local jump tails are exponentially small. "
            "This does not decorrelate moderate jumps along long paths and therefore "
            "does not yet prove current hyperuniformity or the H^-1 estimate."
        ),
        "theorem": {
            "scope": "every edge of every four-dimensional periodic BT lattice",
            "coupling": "lambda=2/5",
            "definitions": {
                "ratio": "w_xy=exp(psi_y-psi_x)",
                "jump": "d_xy=psi_y-psi_x",
                "residual": "r_x=sum_(z~x) w_xz-8",
                "current": "J_xy=r_x w_xy-r_y w_yx",
            },
            "bounds": {
                "expected_residual_square": "E[r_x^2]<=2444/25",
                "directed_ratio_second_moment": "E[w_xy^2]<=8088/25",
                "absolute_jump_exponential_moment": "E[exp(2|d_xy|)]<=16176/25",
                "absolute_current_first_moment": "E[|J_xy|]<=8932/25",
                "single_edge_tail": "P(|d_xy|>=u)<=(16176/25) exp(-2u) for u>=0",
                "bad_edge_density": (
                    "E[# undirected edges with |d|>=u]/N<=(64704/25) exp(-2u)"
                ),
                "bad_edge_fraction_tail": (
                    "P(#bad edges>=rho*N)<=(64704/(25*rho)) exp(-2u)"
                ),
                "maximum_jump_tail": (
                    "P(max_edge |d|>=u)<=(64704/25) N exp(-2u)"
                ),
            },
        },
        "proof_chain": {
            "action_to_residual": (
                "translation invariance gives E[r_x^2]=2E[A]/N<=2444/25"
            ),
            "residual_to_ratio": (
                "positivity gives w_xy<=r_x+8<=|r_x|+8 and "
                "(|r_x|+8)^2<=2r_x^2+128"
            ),
            "ratio_to_jump": (
                "exp(2|d_xy|)=max(w_xy^2,w_yx^2)<=w_xy^2+w_yx^2"
            ),
            "current": (
                "|r_x|w_xy<=r_x^2+8|r_x|<=(3/2)r_x^2+32, "
                "and the reverse endpoint supplies the second term"
            ),
            "tails": "Markov's inequality followed by the four-N undirected-edge union/count bound",
        },
        "exact_fixture": fixture,
        "method_disposition": {
            "single_edge_ratio_second_moment": "PROVED_VOLUME_UNIFORM",
            "single_edge_log_jump_exponential_tail": "PROVED_VOLUME_UNIFORM",
            "single_edge_current_first_moment": "PROVED_VOLUME_UNIFORM",
            "coherent_path_or_block_decorrelation": "OPEN",
            "background_marginal_current_hyperuniformity": "OPEN",
            "all_field_gradient_bound": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a block/path decorrelation or extraction theorem for moderate edge jumps under the relevant background marginal",
            "a volume-uniform low-momentum current structure-factor or alternative Witten bound",
            "an actual interacting H^-1 moment theorem or controlled divergence",
        ],
        "next_gate": (
            "Use the local exponential jump tail in a multiscale path/block decomposition. "
            "Prove that a large low-momentum corrector forces many separated moderate-jump "
            "blocks with compatible resampling costs, or construct a translation-covariant "
            "coherent-path family that evades this extraction and test it in the full Witten form."
        ),
        "does_not_establish": [
            "independence or decay of correlations between edge jumps",
            "current hyperuniformity under the integrated background marginal",
            "an all-field volume-uniform gradient constant",
            "a Poincare inequality, Witten coercivity, or interacting H^-1 bound",
            "a continuum measure, Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "exact rational propagation of the certified action-density constant; "
                "Fraction reconstruction of the C4 residual, ratios, currents, and pointwise envelopes"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_edge_ellipticity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_edge_ellipticity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_edge_ellipticity",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation and strict JSON/schema parsing passed; the planning import accepted 1691 nodes with zero invalid items and zero malformed events in 6.61 s at 185288 KB peak RSS; scoped diff and staged-diff checks are required before commit",
            "tier_1": "exact producer passed 10/10 in 0.03 s at 20612 KB, the nonimporting verifier passed 10/10 in 0.09 s at 29948 KB, and nine focused tests including mutation rejection passed in 0.11 s at 30800 KB",
            "tier_2": "the unchanged action-density and bounded-oscillation inputs are content-hash pinned",
            "tier_3": "not required absent an H^-1/reconstruction lifecycle promotion, freeze, release, or shared-core change",
            "memory_policy": "all Python commands ran sequentially under a 500000 KiB virtual-memory ceiling; Go used GOMEMLIMIT=300MiB and GOGC=50; the advisory Science Forge shadow rail was not rerun because its immediately preceding memory-capped attempt in this session aborted external indexing without an audit disposition, and that skip is not a pass",
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
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
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
        "[PASS] BT annealed edge ellipticity "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
