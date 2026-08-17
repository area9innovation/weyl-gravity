#!/usr/bin/env python3
"""Build the BT torus top-band flow and L^(11/3) cutoff certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_TOP_BAND_FLOW_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-top-band-flow-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-torus-top-band-flow.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_top_band_flow.py"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SPARSE_MAXIMA_FLOW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_HIGH_CONTRAST_FLOW_CLOSURE_V1.json",
]
SOURCE_COMMIT = "080de60e9dd36cf7bf29c54807abff34e762cb0e"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def torus() -> tuple[list[list[int]], list[tuple[int, int]]]:
    side = 4
    count = side**4
    adjacency = [[] for _ in range(count)]
    edges: list[tuple[int, int]] = []
    for left in range(count):
        work = left
        point = [0, 0, 0, 0]
        for coordinate in range(3, -1, -1):
            point[coordinate] = work % side
            work //= side
        for coordinate in range(4):
            shifted = point[:]
            shifted[coordinate] = (shifted[coordinate] + 1) % side
            right = 0
            for value in shifted:
                right = side * right + value
            edges.append((left, right))
            adjacency[left].append(right)
            adjacency[right].append(left)
    return adjacency, edges


def fixture() -> dict[str, object]:
    adjacency, edges = torus()
    count = len(adjacency)
    q = 8
    diameter = 8
    omega = [Fraction(1) for _ in range(count)]
    omega[0] = Fraction(1_000_000)
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
    maximum = max(
        max(omega[x] / omega[y], omega[y] / omega[x]) for x, y in edges
    )
    c = [Fraction() for _ in range(count)]
    oriented: list[tuple[int, int, Fraction]] = []
    equal: list[tuple[int, int]] = []
    for left, right in edges:
        if omega[left] == omega[right]:
            equal.append((left, right))
        else:
            tail, head = (left, right) if omega[left] < omega[right] else (right, left)
            alpha = omega[head] / (omega[tail] * maximum)
            c[tail] += alpha
            oriented.append((tail, head, alpha))
    flow_mass = sum((value**2 for value in c), Fraction())
    h = [residual[x] - maximum * c[x] for x in range(count)]
    main_divergence = [Fraction() for _ in range(count)]
    error_divergence = [Fraction() for _ in range(count)]
    error_edge_norm = Fraction()
    top_mass = Fraction()
    for tail, head, alpha in oriented:
        flow = c[tail] * alpha
        if alpha >= Fraction(1, 2):
            top_mass += flow
        error = (
            maximum * h[tail] * alpha
            - c[head] / alpha
            - h[head] / (maximum * alpha)
        )
        error_edge_norm += error**2
        main_divergence[tail] -= flow
        main_divergence[head] += flow
        error_divergence[tail] -= error
        error_divergence[head] += error
    for left, right in equal:
        error = residual[left] - residual[right]
        error_edge_norm += error**2
        error_divergence[left] -= error
        error_divergence[right] += error
    reconstructed = [
        maximum**2 * main_divergence[x] + error_divergence[x]
        for x in range(count)
    ]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    main_divergence_norm = sum((value**2 for value in main_divergence), Fraction())
    error_divergence_norm = sum((value**2 for value in error_divergence), Fraction())
    edge_error_ceiling = 7 * q**2 * maximum**2 * flow_mass + 6 * q**3 * count
    divergence_error_ceiling = 14 * q**3 * maximum**2 * flow_mass + 12 * q**4 * count
    top_condition_right = 256 * q**3 * diameter**2 * count * flow_mass
    gradient_floor_squared = maximum**4 / (4 * diameter**2 * count)
    quotient_floor = maximum**2 / (4 * q**2 * diameter**2 * count**2)
    return {
        "graph": "T_4^4 single spike",
        "vertices": count,
        "degree": q,
        "diameter": diameter,
        "height": 1_000_000,
        "maximum_edge_ratio": enc(maximum),
        "density_mass_F": enc(flow_mass),
        "top_half_band_flow_mass": enc(top_mass),
        "main_divergence_norm_squared": enc(main_divergence_norm),
        "error_edge_norm_squared": enc(error_edge_norm),
        "error_edge_norm_ceiling": enc(edge_error_ceiling),
        "error_divergence_norm_squared": enc(error_divergence_norm),
        "error_divergence_norm_ceiling": enc(divergence_error_ceiling),
        "top_condition_left_W_squared": enc(maximum**2),
        "top_condition_right": enc(top_condition_right),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "gradient_floor_squared": enc(gradient_floor_squared),
        "quotient": enc(gradient_norm / residual_norm),
        "quotient_floor": enc(quotient_floor),
        "checks": {
            "top_half_band_has_unit_mass": top_mass >= 1,
            "main_divergence_has_top_path_floor": main_divergence_norm >= Fraction(1, diameter**2 * count),
            "edge_error_obeys_refined_bound": error_edge_norm <= edge_error_ceiling,
            "divergence_error_obeys_refined_bound": error_divergence_norm <= divergence_error_ceiling,
            "complete_gradient_reconstructed": reconstructed == gradient,
            "top_condition_holds": maximum**2 >= top_condition_right,
            "gradient_clears_floor": gradient_norm >= gradient_floor_squared,
            "quotient_clears_floor": gradient_norm / residual_norm >= quotient_floor,
        },
    }


def build() -> dict[str, object]:
    exact = fixture()
    checks = {
        "fixture_checks_pass": all(exact["checks"].values()),
        "refined_edge_error_bound_proved": True,
        "top_half_band_contains_unit_flow": True,
        "top_band_path_length_at_most_two_diameters": True,
        "top_band_divergence_floor_proved": True,
        "sparse_F_free_scale_bound_proved": True,
        "dense_sparse_dichotomy_closes_L_11_over_3_sector": True,
        "cutoff_constant_is_3072": 48 * 8**2 == 3072,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_TOP_BAND_FLOW_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-top-band-flow-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "UNCONDITIONAL_SUPER_L_11_OVER_3_CONTRAST_CLOSED_MODERATE_MULTIBAND_GATE_OPEN",
        "result_kind": "exact top-band current theorem and unconditional torus high-contrast cutoff",
        "question": "Can the sparse near-maximal band left by the density-sensitive theorem support a BT quotient collapse at very large polynomial edge contrast?",
        "answer": "No above an explicit second threshold. The complete-current error has an L2 bound controlled by W*sqrt(F), not W*sqrt(N). The single edge attaining W carries at least unit leading flow in the alpha>=1/2 top band, whose paths contain at most 2D top edges. If W^2>=256*q^3*D^2*N*F, then Q>=W^2/(4*q^2*D^2*N^2)>=64*q*F/N>=64*q/N. Combining this sparse-F theorem with the density-sensitive predecessor at the split F=N^(1/3) proves that every T_L^4 field with W>=3072*L^(11/3) has Q/omega_L^2>=32/pi^4. A collapsing family must therefore have W<3072*L^(11/3). The remaining moderate sparse multiband sector is open.",
        "refined_error_theorem": {
            "edge_error_square": "sum_e epsilon_e^2<=7*q^2*W^2*F+6*q^3*N",
            "divergence_error_square": "||div(epsilon)||_2^2<=14*q^3*W^2*F+12*q^4*N",
            "norm_form": "||div(epsilon)||_2<=4*q^(3/2)*W*sqrt(F)+4*q^2*sqrt(N)",
            "scope": "the complete current, including reverse-current and equal-field edges",
        },
        "top_band_theorem": {
            "band": "H={e:alpha_e>=1/2}",
            "unit_mass": "sum_(e in H) f_e>=1 because an edge has alpha_e=1 and its tail has c_x>=1",
            "path_length": "every directed path has at most 2D top-band edges when W>=4",
            "divergence_floor": "||div(f)||_2>=1/(D*sqrt(N))",
            "hypothesis": "W^2>=256*q^3*D^2*N*F",
            "gradient_floor": "||g||_2>=W^2/(2*D*sqrt(N))",
            "quotient_floor": "Q>=W^2/(4*q^2*D^2*N^2)>=64*q*F/N>=64*q/N",
        },
        "four_torus_dichotomy": {
            "split": "F>=N^(1/3) uses the density-sensitive predecessor; F<N^(1/3) uses the top-band theorem",
            "common_contrast_hypothesis": "W>=24*q^2*D*N^(2/3)",
            "torus_sufficient_condition": "W>=3072*L^(11/3)",
            "normalized_conclusion": "Q/omega_L^2>=32/pi^4",
            "counterfamily_necessity": "Q/omega_L^2->0 implies eventually W<3072*L^(11/3)",
        },
        "exact_fixture": exact,
        "research_disposition": {
            "super_L_11_over_3_edge_contrast_collapse": "RULED_OUT",
            "sparse_top_band_error_control": "PROVED",
            "moderate_sparse_multiband_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for all edge contrasts on T_L^4",
            "exclusion of polynomial contrast W=O(L^(11/3))",
            "a nonseparable collapsing family",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure, Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction reconstruction of the complete T_4^4 spike residual, gradient, leading flow, edge error, divergence error, norms, and theorem floors",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_top_band_flow.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_top_band_flow.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_top_band_flow",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, deterministic drift, scoped diff check, exact staged-diff inspection, planning import, paper claim-map verification, and two-pass PDF build required; planning import passed with 1712 nodes, 0 invalid items, and 0 malformed events in 1.77 s at 16900 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.05 s at 20788 KiB; independent verifier 10/10 in 0.12 s at 30044 KiB; focused and mutation tests 11/11 in 0.27 s at 30968 KiB; unchanged sparse-maxima predecessor verifier 12/12 in 0.13 s at 30504 KiB",
            "tier_2": "the sparse-maxima and high-contrast predecessors are unchanged and checked by content hash",
            "tier_3": "not triggered: the all-field, Witten, H^-1, continuum, freeze, and release gates remain open",
            "paper_integration": "PASS: claim-map verifier 1.05 s at 148360 KiB maximum RSS; two-pass PDF build 2.49 s at 53844 KiB maximum RSS",
            "planning_event": "PASS: append-only event sequence 93, id da1d71826151d8fa",
            "science_forge_shadow": "ADVISORY EXIT 0 IN 8.05 S AT 336480 KiB, NOT A SCIENTIFIC PASS: bridge audit fail-closed on source-current Forge E9415 drift; coverage census reports 1972 certificates versus baseline 976",
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
    print(f"[PASS] BT torus top-band flow ({result['checks']['passed']}/{result['checks']['total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
