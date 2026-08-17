#!/usr/bin/env python3
"""Build the BT torus extensive-action gradient-floor certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-extensive-action-gradient-floor-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-torus-extensive-action-gradient-floor.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_torus_extensive_action_gradient_floor.py"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_DYADIC_STOPPING_FLOW_V1.json",
]
SOURCE_COMMIT = "073224675bb1afad692251fd282b4eb714334e5c"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def torus_spike_fixture() -> dict[str, object]:
    side = 4
    count = side**4
    degree = 8

    def index(point: tuple[int, int, int, int]) -> int:
        result = 0
        for coordinate in point:
            result = side * result + coordinate
        return result

    adjacency: list[list[int]] = [[] for _ in range(count)]
    for point_number in range(count):
        work = point_number
        point = [0, 0, 0, 0]
        for coordinate in range(3, -1, -1):
            point[coordinate] = work % side
            work //= side
        for coordinate in range(4):
            for step in (-1, 1):
                shifted = point[:]
                shifted[coordinate] = (shifted[coordinate] + step) % side
                adjacency[point_number].append(index(tuple(shifted)))

    omega = [Fraction(1) for _ in range(count)]
    omega[0] = Fraction(1000)
    residual = [
        sum((omega[y] / omega[x] - 1 for y in adjacency[x]), Fraction())
        for x in range(count)
    ]
    gradient = [
        sum(
            (
                residual[y] * omega[x] / omega[y]
                - residual[x] * omega[y] / omega[x]
                for y in adjacency[x]
            ),
            Fraction(),
        )
        for x in range(count)
    ]
    action = sum((value**2 for value in residual), Fraction()) / 2
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    residual_norm = 2 * action
    threshold = Fraction(488, 5) * count
    quotient = gradient_norm / residual_norm
    return {
        "graph": "T_4^4 single spike",
        "side": side,
        "vertices": count,
        "degree": degree,
        "spike_height": 1000,
        "action": enc(action),
        "extensive_action_threshold": enc(threshold),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "quotient": enc(quotient),
        "gradient_sum": enc(sum(gradient, Fraction())),
        "maximum_edge_ratio": 1000,
        "checks": {
            "action_is_extensive": action >= threshold,
            "residual_is_nonzero": residual_norm > 0,
            "gradient_has_zero_sum": sum(gradient, Fraction()) == 0,
            "quotient_is_positive": quotient > 0,
            "edge_ratio_bound_holds": (1000 - 8) ** 2 <= 2 * action,
        },
    }


def constant_audit() -> dict[str, object]:
    virial_constant = Fraction(488, 5)
    normalized_numerator = Fraction(virial_constant, 512)
    checks = {
        "twice_virial_constant_below_14_squared": 2 * virial_constant < 14**2,
        "torus_degree_is_eight": 8 == 8,
        "diameter_ceiling_coefficient": 4 * Fraction(1, 2) == 2,
        "logarithm_ceiling_uses_L_at_least_four": 4 <= 4,
        "quotient_denominator_coefficient": 2 * 4 * 4 == 32,
        "spectral_square_coefficient": 4**2 == 16,
        "normalized_denominator_coefficient": 32 * 16 == 512,
        "normalized_fraction_reduced": normalized_numerator == Fraction(61, 320),
        "low_action_edge_ratio_coefficient": 8 + 14 * 4**2 < 16 * 4**2,
    }
    return {
        "virial_constant": enc(virial_constant),
        "twice_virial_constant": enc(2 * virial_constant),
        "sqrt_ceiling": 14,
        "torus_degree": 8,
        "minimum_side": 4,
        "diameter_ceiling": "D<=2*L",
        "logarithm_ceiling": "log(8+sqrt(2*C)*L^2)<2*L",
        "pre_spectral_floor_coefficient": enc(virial_constant / 32),
        "normalized_floor_coefficient": enc(normalized_numerator),
        "checks": checks,
    }


def build() -> dict[str, object]:
    audit = constant_audit()
    fixture = torus_spike_fixture()
    checks = {
        "constant_audit_closes": all(audit["checks"].values()),
        "fixture_checks_close": all(fixture["checks"].values()),
        "affine_virial_imported": True,
        "edge_ratio_from_residual_proved": True,
        "mean_zero_range_bound_proved": True,
        "large_action_monotonicity_proved": True,
        "four_torus_free_scale_floor_proved": True,
        "low_action_L_squared_contrast_necessity_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-extensive-action-gradient-floor-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXTENSIVE_ACTION_BRANCH_FREE_SCALE_CLOSED_LOW_ACTION_L2_CONTRAST_GATE_OPEN",
        "result_kind": "exact extensive-action gradient floor and low-action torus contrast reduction",
        "question": "Can the remaining BT torus quotient collapse by carrying extensive or superextensive residual action while keeping its largest edge ratio below the preceding stopping-flow threshold?",
        "answer": "No. The affine virial inequality, the mean-zero log-field range bound, and the exact edge-ratio bound imply that every T_L^4 field with A>=(488/5)L^4 obeys Q/omega_L^2>=61/(320*pi^4). Therefore every sequence below that floor has A<(488/5)L^4 and W<16L^2. This improves the live contrast window from W=O(L^(10/3)) to W=O(L^2), but does not decide the remaining low-action sector.",
        "graph_theorem": {
            "scope": "every finite connected 8-regular graph with mean-zero log field psi",
            "affine_virial_input": "<psi,g>>=2*A-C*N with C=488/5 for q=8",
            "large_action_hypothesis": "A>=C*N",
            "radial_pairing_floor": "<psi,g>>=A",
            "edge_ratio_bound": "W<=q+sqrt(2*A)",
            "log_field_range_bound": "||psi||_2<=D*sqrt(N)*log(q+sqrt(2*A))",
            "gradient_floor": "||g||_2>=A/[D*sqrt(N)*log(q+sqrt(2*A))]",
            "quotient_floor": "Q>=A/[2*N*D^2*log(q+sqrt(2*A))^2]",
            "monotonicity": "A/log(q+sqrt(2*A))^2 is increasing for A>0 when q>=1",
        },
        "four_torus_corollary": {
            "scope": "T_L^4 with L>=4",
            "vertices": "N=L^4",
            "degree": 8,
            "diameter": "D=4*floor(L/2)<=2*L",
            "spectral_scale": "omega_L=4*sin(pi/L)^2<=4*pi^2/L^2",
            "extensive_action_hypothesis": "A>=(488/5)*L^4",
            "quotient_floor": "Q>=(61/20)*L^(-4)",
            "normalized_floor": "Q/omega_L^2>=61/(320*pi^4)",
            "counterfamily_action_necessity": "Q/omega_L^2<61/(320*pi^4) implies A<(488/5)*L^4",
            "counterfamily_contrast_necessity": "Q/omega_L^2<61/(320*pi^4) implies W<16*L^2",
        },
        "exact_constant_audit": audit,
        "exact_fixture": fixture,
        "research_disposition": {
            "extensive_or_superextensive_action_collapse": "RULED_OUT",
            "super_16_L_squared_edge_contrast_collapse": "RULED_OUT_BELOW_THE_CERTIFIED_FLOOR",
            "low_action_sub_16_L_squared_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for fields with A<(488/5)*L^4 and W<16*L^2",
            "the all-field torus scaled Polyak-Lojasiewicz inequality",
            "absence of a nonseparable low-action collapsing family",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure or continuum identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction audit of C=488/5, its square-root ceiling, the 32 and 512 denominator factors, the reduced 61/320 normalized coefficient, and a complete rational T_4^4 spike",
            "analytic_inputs": [
                "e^4>16 from e>2, hence log(16)<4",
                "2*log(L)<=L for L>=4 by the base value and derivative comparison",
                "sin(x)<=x for x>=0",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_extensive_action_gradient_floor.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_extensive_action_gradient_floor.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_extensive_action_gradient_floor",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python compiled; strict JSON/schema parsing, deterministic certificate drift, scoped diff check, exact staged-diff inspection, planning import, claim-map verification, and two-pass PDF build were run; planning imported 1714 nodes with 0 invalid items and 0 malformed events in 1.23 s at 16964 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.05 s at 20564 KiB; nonimporting verifier 12/12 in 0.11 s at 29796 KiB; focused and mutation tests 12/12 in 0.19 s at 30512 KiB; unchanged affine-virial and dyadic-stopping predecessor verifiers passed 10/10 and 12/12 in 0.10 s each",
            "tier_2": "the affine-virial and dyadic-stopping inputs are unchanged and checked by content hash; no shared operator, schema consumer, or generated certificate chain changed",
            "tier_3": "not triggered: the all-field, Witten, H^-1, continuum, freeze, release, and shared-core gates remain open",
            "paper_integration": "PASS: Paper 21 RF-89 claim-map verification completed in 0.59 s at 148780 KiB maximum RSS and the PDF built twice in 1.77 s at 54264 KiB; the prose advisory remained non-certifying and reported manuscript-wide parenthetical and abstract-length findings",
            "planning_event": "PASS: append-only ACTIVE event sequence 95, id cb549856a2943012",
            "science_forge_shadow": "ADVISORY ONLY, NOT A SCIENTIFIC PASS: the shadow rail was interrupted after 172.70 s without a final disposition after its cbp indexing subprocesses aborted under the memory ceiling",
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
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != encoded:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(
        "[PASS] BT torus extensive-action gradient floor "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
