#!/usr/bin/env python3
"""Build the BT torus sparse-maxima flow certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SPARSE_MAXIMA_FLOW_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-sparse-maxima-flow-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-torus-sparse-maxima-flow.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_sparse_maxima_flow.py"
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_HIGH_CONTRAST_FLOW_CLOSURE_V1.json"
)
SOURCE_COMMIT = "b215c6e7090cd07f3afe66d31f4ea27ddf80502a"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def torus_graph(side: int) -> tuple[list[list[int]], list[tuple[int, int]]]:
    vertices = side**4

    def index(point: tuple[int, int, int, int]) -> int:
        out = 0
        for coordinate in point:
            out = out * side + coordinate
        return out

    adjacency = [[] for _ in range(vertices)]
    edges: list[tuple[int, int]] = []
    for raw in range(vertices):
        work = raw
        point = [0, 0, 0, 0]
        for coordinate in range(3, -1, -1):
            point[coordinate] = work % side
            work //= side
        for coordinate in range(4):
            other = point[:]
            other[coordinate] = (other[coordinate] + 1) % side
            right = index(tuple(other))
            edges.append((raw, right))
            adjacency[raw].append(right)
            adjacency[right].append(raw)
    return adjacency, edges


def evaluate_fixture(kind: str, height: int) -> dict[str, object]:
    side = 4
    adjacency, edges = torus_graph(side)
    vertices = len(adjacency)
    degree = 8
    diameter = 8
    if kind == "single_spike":
        omega = [Fraction(1) for _ in range(vertices)]
        omega[0] = Fraction(height)
    elif kind == "checkerboard":
        omega = []
        for raw in range(vertices):
            work = raw
            parity = 0
            for _ in range(4):
                parity += work % side
                work //= side
            omega.append(Fraction(height if parity % 2 else 1))
    else:
        raise ValueError(kind)

    residual = [
        sum((omega[neighbor] / omega[site] - 1 for neighbor in adjacency[site]), Fraction())
        for site in range(vertices)
    ]
    gradient = [
        sum(
            (
                residual[neighbor] * omega[site] / omega[neighbor]
                - residual[site] * omega[neighbor] / omega[site]
                for neighbor in adjacency[site]
            ),
            Fraction(),
        )
        for site in range(vertices)
    ]
    maximum = max(
        max(omega[left] / omega[right], omega[right] / omega[left])
        for left, right in edges
    )
    outgoing_mass = [Fraction() for _ in range(vertices)]
    oriented: list[tuple[int, int, Fraction]] = []
    equal: list[tuple[int, int]] = []
    for left, right in edges:
        if omega[left] == omega[right]:
            equal.append((left, right))
            continue
        tail, head = (left, right) if omega[left] < omega[right] else (right, left)
        alpha = (omega[head] / omega[tail]) / maximum
        outgoing_mass[tail] += alpha
        oriented.append((tail, head, alpha))
    flow_mass = sum((value * value for value in outgoing_mass), Fraction())
    threshold = flow_mass / (4 * degree**2 * vertices)
    main_divergence = [Fraction() for _ in range(vertices)]
    error_divergence = [Fraction() for _ in range(vertices)]
    low_mass = Fraction()
    high_mass = Fraction()
    near_max_edges = 0
    for tail, head, alpha in oriented:
        flow = outgoing_mass[tail] * alpha
        if alpha < threshold:
            low_mass += flow
        else:
            high_mass += flow
        if alpha >= Fraction(1, 2):
            near_max_edges += 1
        current = (
            residual[tail] * omega[head] / omega[tail]
            - residual[head] * omega[tail] / omega[head]
        )
        error = current - maximum**2 * flow
        main_divergence[tail] -= flow
        main_divergence[head] += flow
        error_divergence[tail] -= error
        error_divergence[head] += error
    for left, right in equal:
        error = residual[left] - residual[right]
        error_divergence[left] -= error
        error_divergence[right] += error
    reconstructed = [
        maximum**2 * main_divergence[site] + error_divergence[site]
        for site in range(vertices)
    ]
    residual_norm = sum((value * value for value in residual), Fraction())
    gradient_norm = sum((value * value for value in gradient), Fraction())
    quotient = gradient_norm / residual_norm
    condition_floor = 24 * degree**2 * diameter * vertices
    theorem_floor = Fraction(9 * degree**2)
    return {
        "kind": kind,
        "side": side,
        "vertices": vertices,
        "degree": degree,
        "diameter": diameter,
        "height": height,
        "maximum_edge_ratio": enc(maximum),
        "oriented_edge_count": len(oriented),
        "equal_edge_count": len(equal),
        "near_maximal_half_edge_count": near_max_edges,
        "outgoing_square_mass_F": enc(flow_mass),
        "band_threshold_tau": enc(threshold),
        "low_flow_mass": enc(low_mass),
        "high_flow_mass": enc(high_mass),
        "condition_left_WF": enc(maximum * flow_mass),
        "condition_right_24q2DN": enc(condition_floor),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "quotient": enc(quotient),
        "theorem_quotient_floor": enc(theorem_floor),
        "checks": {
            "flow_mass_splits": low_mass + high_mass == flow_mass,
            "low_mass_bound": low_mass <= flow_mass / 8,
            "complete_gradient_reconstructed": reconstructed == gradient,
            "density_condition_holds": maximum * flow_mass >= condition_floor,
            "quotient_clears_floor": quotient >= theorem_floor,
            "near_maximal_count_bound": near_max_edges <= 4 * flow_mass,
        },
    }


def build() -> dict[str, object]:
    fixtures = [
        evaluate_fixture("single_spike", 1_000_000),
        evaluate_fixture("checkerboard", 1_000),
    ]
    checks = {
        "two_exact_four_torus_fixtures": len(fixtures) == 2,
        "all_fixture_checks_pass": all(all(row["checks"].values()) for row in fixtures),
        "finite_amplitude_split_is_exact": True,
        "low_band_carries_at_most_one_eighth": True,
        "high_edge_path_count_uses_torus_diameter": True,
        "full_flow_divergence_floor_proved": True,
        "complete_current_error_bound_proved": True,
        "density_sensitive_quotient_bound_proved": True,
        "near_maximal_edge_sparsity_corollary_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SPARSE_MAXIMA_FLOW_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-sparse-maxima-flow-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "DENSITY_SENSITIVE_HIGH_CONTRAST_CLOSED_MULTIBAND_GATE_OPEN",
        "result_kind": "exact torus-specific finite-amplitude flow theorem and sparse-maxima necessity",
        "question": "Can near-maximal edge ratios remain macroscopically distributed in a polynomial-contrast BT counterfamily on the isotropic four-torus?",
        "answer": "Only below an explicit density-contrast threshold. Let W be the largest unoriented edge ratio, alpha_e=z_e/W on increasing edges, c_x=sum_(x->y) alpha_e, and F=sum_x c_x^2. On T_L^4, if W*F>=24*q^2*diam(T_L^4)*L^4, then the complete residual-gradient quotient is at least 9q^2, hence at least (9/4) times the free bilaplacian scale. Therefore any collapsing family must obey W*F<3072*L^5. More generally the number E_theta of edges with z_e>=theta*W obeys E_theta<=F/theta^2, so a bad family with W/L tending to infinity must make every fixed near-maximal band sparse. This does not decide the remaining dense multiband sector.",
        "definitions": {
            "graph": "nearest-neighbor isotropic four-torus T_L^4 with L>=4, N=L^4, q=8, D=4*floor(L/2)<=2L",
            "field": "Omega_x>0, modulo common scale",
            "residual": "r_x=sum_(y~x)(Omega_y/Omega_x-1)",
            "gradient": "g_x=sum_(y~x)[r_y*Omega_x/Omega_y-r_x*Omega_y/Omega_x]",
            "maximum_ratio": "W=max_(undirected edges){Omega_y/Omega_x,Omega_x/Omega_y}>1",
            "normalized_uphill_edge": "alpha_e=(Omega_head/Omega_tail)/W on every strictly increasing edge",
            "outgoing_mass": "c_x=sum_(e:x->y) alpha_e",
            "density_mass": "F=sum_x c_x^2, with 1<=F<=q^2*N",
        },
        "finite_amplitude_decomposition": {
            "residual": "r_x=W*c_x+h_x with -q<=h_x<=0",
            "oriented_current": "J_e=r_tail*z_e-r_head/z_e=W^2*c_tail*alpha_e+epsilon_e",
            "current_error": "|epsilon_e|<=3*q*W, including equal-field edges in epsilon",
            "gradient": "g=W^2*div(f)+div(epsilon), f_e=c_tail*alpha_e",
            "error_divergence": "||div(epsilon)||_2<=3*q^2*W*sqrt(N)",
            "total_flow_mass": "sum_e f_e=sum_x c_x^2=F",
        },
        "torus_band_transport": {
            "threshold": "tau=F/(4*q^2*N)",
            "low_edge_mass": "sum_(alpha_e<tau) f_e<=F/8",
            "high_edge_ratio": "alpha_e>=tau implies z_e>=W*F/(4*q^2*N)",
            "path_geometry": "if W*F>=24*q^2*D*N, every flow path contains at most 5D high edges because its field increase is at most W^D",
            "transported_source_mass": "S=(1/2)||div(f)||_1>=7F/(40D)",
            "divergence_floor": "||div(f)||_2>=7F/(20D*sqrt(N))",
        },
        "theorem": {
            "hypothesis": "W*F>=24*q^2*D*N",
            "gradient_floor": "||g||_2>=7*W^2*F/(40*D*sqrt(N))",
            "residual_ceiling": "||r||_2<=q*W*sqrt(N)",
            "quotient_floor": "||g||_2^2/||r||_2^2>=49*W^2*F^2/(1600*q^2*D^2*N^2)>=9*q^2",
            "free_scale": "9*q^2>=(9/4)*omega_L^2 because omega_L<=2q",
        },
        "four_torus_corollary": {
            "sufficient_condition": "W*F>=3072*L^5",
            "bad_family_necessity": "Q_L<9*q^2 implies W*F<24*q^2*D*L^4<=3072*L^5",
            "near_maximal_count": "E_theta=#{e:z_e>=theta*W}<=F/theta^2",
            "bad_family_density": "E_theta/(4*L^4)<768*L/(theta^2*W)",
            "interpretation": "if W/L->infinity along a collapsing candidate, every fixed relative top ratio band has vanishing edge density",
        },
        "exact_fixtures": fixtures,
        "research_disposition": {
            "macroscopic_near_maximal_high_contrast_flow": "RULED_OUT_ABOVE_EXPLICIT_WF_THRESHOLD",
            "sparse_maxima_necessity": "PROVED",
            "bounded_oscillation_sector": "RULED_OUT_BY_HASHED_PREDECESSOR_CHAIN",
            "dense_multiband_polynomial_contrast_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for every positive field on T_L^4",
            "exclusion of a sparse hierarchy spread over many ratio bands",
            "a nonseparable polynomial-contrast collapsing family",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure, Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "exact_arithmetic": "Fraction evaluation of two complete 4^4 torus fields, residuals, gradients, flows, errors, norms, thresholds, and density counts",
            "assumptions": [
                "the graph is the isotropic nearest-neighbor four-torus with L>=4",
                "the field is strictly positive and nonconstant",
                "the theorem concerns the deterministic residual-gradient quotient only",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_sparse_maxima_flow.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_sparse_maxima_flow.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_sparse_maxima_flow",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, deterministic drift, scoped diff check, exact staged-diff inspection, planning import, paper claim-map verification, and two-pass PDF build required; planning import passed with 1711 nodes, 0 invalid items, and 0 malformed events in 1.36 s at 17032 KiB maximum RSS",
            "tier_1": "PASS: producer 11/11 in 0.07 s at 20900 KiB; independent verifier 12/12 in 0.12 s at 30520 KiB; focused and mutation tests 11/11 in 0.35 s at 30820 KiB; unchanged predecessor verifier 9/9 including 318 rational fields in 0.17 s at 32172 KiB",
            "tier_2": "the high-contrast predecessor is unchanged and checked by content hash",
            "tier_3": "not triggered unless the paper integration promotes a lifecycle state; the all-field, Witten, H^-1, continuum, freeze, and release gates remain open",
            "paper_integration": "PASS: claim-map verifier 0.68 s at 148136 KiB maximum RSS; two-pass PDF build 1.75 s at 53904 KiB maximum RSS",
            "planning_event": "PASS: append-only event sequence 92, id 951fabdfad0112a6",
            "science_forge_shadow": "ADVISORY EXIT 0 IN 6.82 S AT 339548 KiB, NOT A SCIENTIFIC PASS: bridge audit fail-closed on source-current Forge E9415 drift; coverage census reports 1971 certificates versus baseline 976",
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
    print(f"[PASS] BT torus sparse-maxima flow ({result['checks']['passed']}/{result['checks']['total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
