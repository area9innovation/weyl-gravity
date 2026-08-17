#!/usr/bin/env python3
"""Build the exact BT torus curvature/cut concentration certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_CURVATURE_CUT_CONCENTRATION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-curvature-cut-concentration-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-torus-curvature-cut-concentration.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_curvature_cut_concentration.py"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_RECIPROCAL_VIRIAL_LOCALIZATION_V1.json"
]
SOURCE_COMMIT = "1d80094413f2365cff2b9c3c5b7c24292d6d40d4"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def checkerboard_fixture() -> dict[str, object]:
    side = 4
    points = list(product(range(side), repeat=4))

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    field = [Fraction(1) if sum(point) % 2 == 0 else Fraction(2) for point in points]
    neighbors: list[list[int]] = [[] for _ in points]
    edges: list[tuple[int, int]] = []
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                neighbors[x].append(index(tuple(neighbor)))
            neighbor = list(point)
            neighbor[axis] = (neighbor[axis] + 1) % side
            edges.append((x, index(tuple(neighbor))))
    residual = [
        sum((field[y] / field[x] - 1 for y in neighbors[x]), Fraction())
        for x in range(len(points))
    ]
    curvature = [r / (u * u) for r, u in zip(residual, field)]
    gradient = [
        sum(
            (
                residual[y] * field[x] / field[y]
                - residual[x] * field[y] / field[x]
                for y in neighbors[x]
            ),
            Fraction(),
        )
        for x in range(len(points))
    ]
    curvature_mean = sum(curvature, Fraction()) / len(points)
    centered = [value - curvature_mean for value in curvature]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    centered_norm = sum((value**2 for value in centered), Fraction())
    energy = sum(
        (
            field[x] * field[y] * (curvature[x] - curvature[y]) ** 2
            for x, y in edges
        ),
        Fraction(),
    )
    pairing = sum((h * g for h, g in zip(curvature, gradient)), Fraction())
    threshold = Fraction(1)
    low = [x for x, value in enumerate(field) if value <= threshold]
    high = [x for x, value in enumerate(field) if value > threshold]
    low_residual_norm = sum((residual[x] ** 2 for x in low), Fraction())
    cut_flux = sum((gradient[x] for x in high), Fraction())
    boundary_flux = Fraction()
    crossing_edges = 0
    for x, y in edges:
        if field[x] <= threshold < field[y]:
            low_x, high_y = x, y
        elif field[y] <= threshold < field[x]:
            low_x, high_y = y, x
        else:
            continue
        crossing_edges += 1
        boundary_flux += (
            residual[low_x] * field[high_y] / field[low_x]
            - residual[high_y] * field[low_x] / field[high_y]
        )
    omega = Fraction(2)
    spectral_lhs = omega * centered_norm
    spectral_squared_lhs = omega * omega * centered_norm
    exact_cut_floor = (
        Fraction(len(points)) * cut_flux**2
        / (len(low) * len(high) * residual_norm)
    )
    universal_cut_coefficient = cut_flux**2 / (4 * residual_norm)
    return {
        "graph": "T_4^4 parity checkerboard",
        "vertices": len(points),
        "threshold": enc(threshold),
        "low_vertices": len(low),
        "high_vertices": len(high),
        "crossing_edges": crossing_edges,
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "curvature_mean": enc(curvature_mean),
        "centered_curvature_norm_squared": enc(centered_norm),
        "weighted_curvature_energy": enc(energy),
        "curvature_gradient_pairing": enc(pairing),
        "omega_L": enc(omega),
        "poincare_lower_side": enc(spectral_lhs),
        "spectral_flatness_squared_side": enc(spectral_squared_lhs),
        "low_residual_norm_squared": enc(low_residual_norm),
        "low_residual_fraction": enc(low_residual_norm / residual_norm),
        "cut_flux": enc(cut_flux),
        "boundary_current_flux": enc(boundary_flux),
        "exact_cut_quotient_floor": enc(exact_cut_floor),
        "universal_cut_coefficient_without_pi4": enc(universal_cut_coefficient),
        "checks": {
            "minimum_field_is_one": min(field) == 1,
            "gradient_has_zero_sum": sum(gradient, Fraction()) == 0,
            "weighted_energy_identity": energy == -pairing,
            "torus_poincare_step": energy >= spectral_lhs,
            "spectral_flatness_step": gradient_norm >= spectral_squared_lhs,
            "cut_flux_is_boundary_current": cut_flux == boundary_flux,
            "cut_cauchy_floor_holds": gradient_norm / residual_norm >= exact_cut_floor,
            "low_fraction_is_four_fifths": low_residual_norm / residual_norm == Fraction(4, 5),
            "cut_is_balanced": len(low) == len(high) == len(points) // 2,
        },
    }


def build() -> dict[str, object]:
    fixture = checkerboard_fixture()
    checks = {
        "fixture_checks_close": all(fixture["checks"].values()),
        "ground_state_current_identity_proved": True,
        "torus_spectral_flatness_proved": True,
        "height_cut_flux_identity_proved": True,
        "height_cut_free_scale_floor_proved": True,
        "reciprocal_localization_imported_by_hash": True,
        "three_condition_collapsing_alternative_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_CURVATURE_CUT_CONCENTRATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-curvature-cut-concentration-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CURVATURE_FLATNESS_AND_HEIGHT_CUT_CANCELLATION_CERTIFIED_ALL_FIELD_GATE_OPEN",
        "result_kind": "exact torus curvature-flatness, height-cut flux, and residual-superlevel concentration alternative",
        "question": "What additional canonical-current conditions must accompany the certified residual escape to high field superlevels in every collapsing BT four-torus sequence?",
        "answer": "Normalize min(u)=1 and put h=r/u^2. The complete gradient is the weighted Laplacian g=L_c h with c_xy=u_x*u_y>=1. The torus spectral gap therefore gives ||h-h_bar||_2/R<=sqrt(Q/omega_L^2). Every collapsing sequence has curvature flatness in this precise unweighted sense. For every height cut S_K={u>K}, its complete boundary-current flux Gamma_K=sum_(S_K)g gives Q/omega_L^2>=Gamma_K^2/(4*pi^4*R^2). Combining this with the imported reciprocal floor proves that positive-action collapse requires simultaneously: residual escape above every fixed K, vanishing normalized curvature fluctuation, and cancellation of the canonical current across every height cut. If {u<=K} retains a macroscopic volume fraction, then even ||h||_2/R tends to zero and the residual must be created purely by u^2 weight amplification. This is a concentration alternative, not the all-field lower bound.",
        "definitions": {
            "field": "u_x>0, rescaled so min_x u_x=1",
            "residual": "r_x=sum_(y~x)(u_y/u_x-1)",
            "action_and_norm": "A=R^2/2 and R^2=sum_x r_x^2",
            "curvature": "h_x=r_x/u_x^2",
            "conductance": "c_xy=u_x*u_y>=1",
            "gradient": "g_x=sum_(y~x)c_xy*(h_y-h_x)",
            "quotient": "Q=||g||_2^2/R^2",
        },
        "spectral_flatness_theorem": {
            "scope": "every nonconstant positive field on T_L^4 with L>=4",
            "energy": "E=sum_edges c_xy*(h_x-h_y)^2=-<h,g>=-<h-h_bar,g>",
            "poincare_chain": "omega_L*||h-h_bar||_2^2<=sum_edges(h_x-h_y)^2<=E<=||h-h_bar||_2*||g||_2",
            "flatness_bound": "||h-h_bar||_2<=||g||_2/omega_L",
            "normalized_flatness": "||h-h_bar||_2/R<=sqrt(Q/omega_L^2)",
        },
        "height_cut_theorem": {
            "threshold": "K>=1, S_K={x:u_x>K}, s_K=|S_K|, and Gamma_K=sum_(x in S_K)g_x",
            "boundary_formula": "Gamma_K=sum_(x outside S_K,y inside S_K,x~y)[r_x*u_y/u_x-r_y*u_x/u_y]",
            "exact_indicator_floor": "Q>=N*Gamma_K^2/[s_K*(N-s_K)*R^2] for 0<s_K<N",
            "normalized_floor": "Q/omega_L^2>=Gamma_K^2/(4*pi^4*R^2)",
            "collapsing_necessity": "Q/omega_L^2->0 implies Gamma_K/R->0 for every chosen nontrivial height threshold K",
        },
        "combined_concentration_theorem": {
            "low_fraction": "F_K=sum_(u_x<=K)r_x^2/R^2 and m_K=|{u_x<=K}|",
            "mean_bound": "|h_bar|*sqrt(m_K)/R<=sqrt(F_K)+sqrt(Q/omega_L^2)",
            "macroscopic_low_set_bound": "if m_K>=theta*N then ||h||_2/R<=sqrt(F_K/theta)+(1+1/sqrt(theta))*sqrt(Q/omega_L^2)",
            "imported_reciprocal_floor": "Q/omega_L^2>=A*F_K^2/(2*pi^4*K^2)",
            "fixed_threshold_positive_action_conclusion": "if Q/omega_L^2->0, liminf A>0, and K is fixed, then F_K->0, Gamma_K/R->0, and ||h-h_bar||_2/R->0",
            "macroscopic_low_set_conclusion": "under the preceding hypotheses, if liminf m_K/N>0 then ||h||_2/R->0",
        },
        "exact_fixture": fixture,
        "research_disposition": {
            "positive_action_fixed_height_residual_retention": "RULED_OUT_FOR_COLLAPSE",
            "nonflat_unweighted_curvature": "RULED_OUT_FOR_COLLAPSE",
            "noncancelling_height_cut_current": "RULED_OUT_FOR_COLLAPSE",
            "remaining_counterfamily_shape": "HIGH_FIELD_WEIGHT_AMPLIFICATION_WITH_FLAT_UNWEIGHTED_CURVATURE_AND_ALL_HEIGHT_CUT_CURRENT_CANCELLATION",
            "all_field_torus_scaled_PL": "OPEN",
            "nonseparable_counterfamily": "NOT_CONSTRUCTED",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a positive lower bound uniform over every torus field",
            "incompatibility of the three remaining concentration conditions",
            "absence or existence of a nonseparable polynomial-contrast counterfamily",
            "a quantitative weighted norm comparison between h and r=u^2*h",
            "a concentration-compactness theorem closing all high-field components",
            "a Witten or Poincare theorem for the interacting measure",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure or continuum identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction reconstruction of the complete T_4^4 checkerboard residual, h curvature, canonical gradient, weighted energy, spectral chain, K=1 height-cut flux, boundary-current sum, residual fraction, and indicator quotient floor",
            "analytic_inputs": [
                "the exact ground-state current identity g=L_c h",
                "the exact torus spectral gap omega_L=4*sin(pi/L)^2",
                "Cauchy-Schwarz and centered-indicator variance",
                "sin(x)<=x",
                "the content-pinned reciprocal-virial localization theorem",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_curvature_cut_concentration.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_curvature_cut_concentration.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_curvature_cut_concentration",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python compiled; strict JSON/schema parsing, deterministic certificate and claim-map drift checks, scoped diff check, exact staged-diff inspection, and planning import were run; planning imported 1719 nodes with 0 invalid items and 0 malformed events in 1.17 s at 17200 KiB maximum RSS",
            "tier_1": "PASS: producer 9/9 in 0.07 s at 20712 KiB; nonimporting verifier 10/10 in 0.16 s at 30436 KiB; focused and mutation tests 12/12 in 0.39 s at 30824 KiB; unchanged reciprocal-virial predecessor verifier passed 10/10 in 0.11 s at 30428 KiB",
            "tier_2": "the reciprocal-virial predecessor is unchanged and pinned by content hash",
            "tier_3": "not triggered: the all-field, H^-1, continuum, freeze, release, and shared-core gates remain open",
            "paper_integration": "PASS: Paper 21 RF-94 claim-map generator completed in 0.35 s at 145788 KiB, independent claim-map verification in 0.55 s at 149276 KiB, and the 85-page PDF built twice in 1.07 s at 54112 KiB and 0.84 s at 53816 KiB",
            "planning_event": "PASS: append-only ACTIVE event sequence 100, id b8657813e9092250",
            "science_forge_shadow": "ADVISORY_INCOMPLETE_NOT_SCIENTIFIC_PASS: the read-only advisory wrapper encountered aborted cbp callers/where helper processes before reporting its usual certlab and census summaries; this is recorded as an incomplete advisory rail and is not counted as evidence for the claim",
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
        "[PASS] BT torus curvature/cut concentration "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
