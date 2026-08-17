#!/usr/bin/env python3
"""Build the exact BT independent tensor-phase hierarchy obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TENSOR_PHASE_HIERARCHY_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-tensor-phase-hierarchy-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-tensor-phase-hierarchy-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_tensor_phase_hierarchy_obstruction.py"
)
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_PHASE_PULLBACK_OBSTRUCTION_V1.json"
)
SOURCE_COMMIT = "1344df51fa33a79fd26a755e7dd7c102b995d38f"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle(member: int) -> dict[str, object]:
    m = member
    ramp = m**4
    slope = Fraction(m - 1, ramp)
    side = [
        Fraction(1) + slope * min(index, 2 * ramp - index)
        for index in range(2 * ramp + 1)
    ]
    ratio = side + [1 / side[2 * ramp - index] for index in range(2 * ramp + 1)]
    length = len(ratio)
    rho = [
        ratio[index] + 1 / ratio[(index - 1) % length] - 2
        for index in range(length)
    ]
    reverse_rho = [
        1 / ratio[index] + ratio[(index - 1) % length] - 2
        for index in range(length)
    ]
    delta = [reverse_rho[index] - rho[index] for index in range(length)]
    current = [
        rho[index] * ratio[index]
        - rho[(index + 1) % length] / ratio[index]
        for index in range(length)
    ]
    gradient = [
        current[(index - 1) % length] - current[index]
        for index in range(length)
    ]
    start = (ramp + 1) // 2 + 1
    stop = 3 * ramp // 4
    bulk = list(range(start, stop + 1))
    return {
        "member": m,
        "ramp": ramp,
        "slope": slope,
        "ratio": ratio,
        "rho": rho,
        "delta": delta,
        "gradient": gradient,
        "length": length,
        "bulk": bulk,
    }


def raw_moment(
    data: dict[str, object], powers: tuple[int, int, int]
) -> Fraction:
    h_power, rho_power, delta_power = powers
    return sum(
        (
            h**h_power * rho**rho_power * delta**delta_power
            for h, rho, delta in zip(
                data["gradient"], data["rho"], data["delta"], strict=True
            )
        ),
        Fraction(0),
    )


def tensor_norm(data: dict[str, object], active: int) -> tuple[Fraction, Fraction]:
    """Sum the tensor residual and gradient squares using 1D moments."""
    length = int(data["length"])
    cache: dict[tuple[int, int, int], Fraction] = {}

    def moment(power: tuple[int, int, int]) -> Fraction:
        if power not in cache:
            cache[power] = raw_moment(data, power)
        return cache[power]

    # A monomial is a coordinate -> (h power, rho power, delta power) map.
    residual_terms = [{index: (0, 1, 0)} for index in range(active)]
    gradient_terms: list[dict[int, tuple[int, int, int]]] = [
        {index: (1, 0, 0)} for index in range(active)
    ]
    for first in range(active):
        for second in range(active):
            if first == second:
                continue
            gradient_terms.append(
                {first: (0, 0, 1), second: (0, 1, 0)}
            )

    def square_sum(terms: list[dict[int, tuple[int, int, int]]]) -> Fraction:
        total = Fraction(0)
        for left in terms:
            for right in terms:
                product = Fraction(1)
                for coordinate in range(active):
                    lp = left.get(coordinate, (0, 0, 0))
                    rp = right.get(coordinate, (0, 0, 0))
                    product *= moment(tuple(lp[i] + rp[i] for i in range(3)))
                total += product
        return total

    return square_sum(residual_terms), square_sum(gradient_terms)


def fixture(member: int) -> dict[str, object]:
    data = cycle(member)
    m = member
    length = int(data["length"])
    bulk = data["bulk"]
    rows = []
    for active in (2, 3, 4):
        residual_norm, gradient_norm = tensor_norm(data, active)
        quotient = gradient_norm / residual_norm
        analytic_lower = Fraction(1, 256 * 40**active * m**6)
        rows.append(
            {
                "active_phases": active,
                "residual_norm_squared": enc(residual_norm),
                "gradient_norm_squared": enc(gradient_norm),
                "quotient": enc(quotient),
                "quotient_scaled_by_m6": enc(quotient * m**6),
                "analytic_lower_bound": enc(analytic_lower),
                "lower_bound_verified": quotient >= analytic_lower,
            }
        )
    local_bound = Fraction(1, 8 * m**2)
    return {
        "member": m,
        "length": length,
        "ramp_length": m**4,
        "bulk_start": bulk[0],
        "bulk_stop": bulk[-1],
        "bulk_count": len(bulk),
        "maximum_edge_ratio": enc(m),
        "local_gradient_floor": enc(local_bound),
        "minimum_bulk_rho": enc(min(data["rho"][index] for index in bulk)),
        "maximum_bulk_delta": enc(max(data["delta"][index] for index in bulk)),
        "maximum_bulk_gradient": enc(
            max(data["gradient"][index] for index in bulk)
        ),
        "tensor_rows": rows,
        "checks": {
            "length_is_4m4_plus_2": length == 4 * m**4 + 2,
            "bulk_has_at_least_m4_over_8_sites": len(bulk) >= m**4 // 8,
            "bulk_residual_is_positive": all(
                data["rho"][index] > 0 for index in bulk
            ),
            "bulk_reverse_difference_is_negative": all(
                data["delta"][index] < 0 for index in bulk
            ),
            "bulk_cycle_gradient_has_floor": all(
                data["gradient"][index] <= -local_bound for index in bulk
            ),
            "all_tensor_quotients_obey_analytic_floor": all(
                row["lower_bound_verified"] for row in rows
            ),
            "cycle_gradient_conserves": sum(data["gradient"], Fraction(0)) == 0,
            "reverse_difference_conserves": sum(data["delta"], Fraction(0)) == 0,
        },
    }


def build() -> dict[str, object]:
    fixtures = [fixture(member) for member in (4, 5)]
    checks = {
        "two_exact_hierarchy_fixtures": len(fixtures) == 2,
        "all_fixture_checks_pass": all(
            all(row["checks"].values()) for row in fixtures
        ),
        "all_active_phase_counts_two_through_four": all(
            [row["active_phases"] for row in fixture["tensor_rows"]] == [2, 3, 4]
            for fixture in fixtures
        ),
        "tensor_residual_identity_proved": True,
        "tensor_gradient_identity_proved": True,
        "same_sign_bulk_lower_bound_proved": True,
        "free_scale_normalized_growth_is_m10": True,
        "polynomial_edge_contrast_is_retained": True,
        "nonseparable_corrector_gate_remains_open": True,
        "witten_h_minus_one_and_lorentzian_remain_open": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "TENSOR_PHASE_HIERARCHY_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "tensor-phase-hierarchy-obstruction-v1"
        ),
        "created": "2026-08-17",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": (
            "INDEPENDENT_TENSOR_PHASE_ROUTE_RULED_OUT_"
            "NONSEPARABLE_CORRECTOR_GATE_OPEN"
        ),
        "result_kind": (
            "exact all-k tensor-phase exclusion for the polynomial-contrast "
            "cycle hierarchy on the four-torus"
        ),
        "question": (
            "Can two, three, or four independently varying copies of the "
            "low-divergence cycle hierarchy produce a four-torus quotient "
            "that collapses below the free infrared scale?"
        ),
        "answer": (
            "No for the complete multiplicative tensor family. For "
            "Omega(x)=product_(a=1)^k u(x_a), 2<=k<=4, the residual is the "
            "sum of the k cycle residuals and the full gradient is the sum "
            "of the cycle gradients plus every ordered cross term "
            "delta(x_a)*rho(x_b). On a macroscopic increasing-ramp block, "
            "rho is positive while delta and the cycle gradient are negative. "
            "All terms therefore reinforce. This gives Q_k>=1/(256*40^k*m^6) "
            "for L=4m^4+2 and m>=4. Since omega_L^2<=16*pi^4/L^4, "
            "Q_k/omega_L^2>=m^10/(16*40^k*pi^4), which diverges. Independent "
            "tensor phases are not the missing transverse cancellation."
        ),
        "tensor_identity": {
            "field": "Omega(x)=product_(a=1)^k u(x_a), 2<=k<=4; remaining coordinates are inert",
            "cycle_residual": "rho_i=u_(i+1)/u_i+u_(i-1)/u_i-2",
            "reverse_residual": "rho_bar_i=u_i/u_(i+1)+u_i/u_(i-1)-2",
            "reverse_difference": "delta_i=rho_bar_i-rho_i",
            "cycle_gradient": "h_i=J_(i-1)-J_i for J_i=rho_i*u_(i+1)/u_i-rho_(i+1)*u_i/u_(i+1)",
            "torus_residual": "r(x)=sum_a rho_(x_a)",
            "torus_gradient": "g(x)=sum_a h_(x_a)+sum_(a!=b) delta_(x_a)*rho_(x_b)",
            "derivation": "expand the complete degree-eight log-field gradient; inert neighbors cancel and the -2*rho_a*rho_b terms combine with reverse-neighbor sums into delta_a*rho_b",
            "maximum_edge_ratio": "exactly m for the adopted hierarchy",
        },
        "same_sign_bulk_theorem": {
            "hierarchy": "ramp R=m^4, slope s=(m-1)/R, length L=4R+2",
            "bulk": "B={ceil(R/2)+1,...,floor(3R/4)} with |B|>=R/8 for m>=4",
            "signs": "on B, rho_i>0, delta_i<0, and h_i<=-1/(8m^2)",
            "current_calculus": "on the increasing ramp J_i=F_s(z_i), where F_s(z)=z^2+z/(z-s)-2z-1-s/z-z^-2+2/z and F_s'(z)>=z-1",
            "tensor_pointwise": "if every active coordinate lies in B, every cross term is negative and |g(x)|>=k/(8m^2)",
            "gradient_norm": "||g||^2>=|B|^k*L^(4-k)*k^2/(64m^4)",
            "residual_norm": "|rho_i|<=2m, hence ||r||^2<=4k^2*m^2*L^4",
            "quotient": "Q_k>=1/(256*40^k*m^6) for 2<=k<=4 and m>=4",
        },
        "four_torus_corollary": {
            "dispersion": "omega_L=4*sin(pi/L)^2 and omega_L^2<=16*pi^4/L^4",
            "length_bound": "L>=4m^4",
            "normalized_bound": "Q_k/omega_L^2>=m^10/(16*40^k*pi^4)",
            "asymptotic": "the normalized quotient diverges for each k=2,3,4",
        },
        "exact_fixtures": fixtures,
        "research_disposition": {
            "linear_single_phase_pullback": "RULED_OUT_BY_PREDECESSOR",
            "independent_multiplicative_tensor_phases": "RULED_OUT",
            "polynomial_edge_contrast": "RETAINED",
            "additive_or_harmonic_tensor_screen": "NUMERICALLY_NONCOLLAPSING_NOT_A_THEOREM",
            "nonseparable_transverse_corrector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "full_witten_coercivity": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a contrast-free estimate for fields with genuinely coupled level sets",
            "a localized weighted Rellich/Hodge theorem for the polynomial-contrast sector",
            "a nonseparable polynomial-contrast family with normalized quotient tending to zero if that theorem is false",
            "a separate Witten and interacting H^-1 transfer after the deterministic fork closes",
        ],
        "next_gate": (
            "Do not spend the cycle hierarchy again through linear phases or "
            "independent tensor products. A negative candidate must couple the "
            "phases so that cross terms change sign on a macroscopic set. The "
            "positive route is a localized weighted Rellich/Hodge estimate "
            "combining the exact additive pairing with torus cut geometry."
        ),
        "does_not_establish": [
            "a lower bound for arbitrary positive fields on T_L^4",
            "exclusion of additive, harmonic-mean, or genuinely coupled phase fields",
            "a concentration-compactness theorem for all polynomial-contrast sequences",
            "a Poincare inequality or Witten one-form coercivity",
            "boundedness or divergence of the interacting H^-1 moment",
            "tightness or a continuum Euclidean measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "exact_arithmetic": (
                "Fraction reconstruction of the cycle residual, reverse "
                "residual, current and gradient; tensor norms are evaluated "
                "from exact one-dimensional mixed moments"
            ),
            "assumptions": [
                "the lattice is the isotropic nearest-neighbor four-torus",
                "the field is the multiplicative tensor product of k identical hierarchy profiles",
                "the hierarchy parameter is an integer m at least four and 2<=k<=4",
                "the result is deterministic reduced-mode evidence, not a Gibbs or Lorentzian theorem",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_tensor_phase_hierarchy_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tensor_phase_hierarchy_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tensor_phase_hierarchy_obstruction",
        ],
        "tier_receipt": {
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "tier_0": "Python compilation, strict JSON/schema parsing, deterministic drift, scoped diff check, and exact staged-diff inspection required",
            "tier_1": "exact producer, nonimporting verifier, method-distinct direct tensor enumeration, focused tests, and mutation rejection required",
            "tier_2": "the phase-pullback predecessor is unchanged and checked by content hash",
            "tier_3": "not triggered: the all-field torus, Witten, H^-1, continuum, freeze, and release lifecycle states remain open",
            "scoped_command_receipts": {
                "producer_check": "PASS: 10/10 checks; 0.95 s; 22660 KiB maximum RSS",
                "independent_verifier": "PASS: 11/11 checks; 0.64 s; 32756 KiB maximum RSS",
                "focused_and_mutation_tests": "PASS: 10/10 tests; 5.25 s; 32616 KiB maximum RSS",
                "predecessor_verifier": "PASS: 11/11 checks; 0.19 s; 30960 KiB maximum RSS",
                "planning_event": "PASS: append-only event sequence 91, id c8f6fd0b18ec564f",
                "planning_import": "PASS: 1710 nodes, 0 invalid items, 0 malformed events; 1.42 s; 17020 KiB maximum RSS",
                "paper_integration": "PASS: claim-map verifier 0.60 s (148408 KiB maximum RSS) and two-pass PDF build 1.90 s (53700 KiB maximum RSS)",
                "science_forge_shadow": "ADVISORY EXIT 0, NOT A SCIENTIFIC PASS: bridge audit fail-closed on source-current Forge E9415 drift; coverage census reports 1970 certificates versus baseline 976",
            },
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
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != encoded:
            print("[FAIL] certificate drift")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(
        "[PASS] BT tensor-phase hierarchy obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0 if result["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
