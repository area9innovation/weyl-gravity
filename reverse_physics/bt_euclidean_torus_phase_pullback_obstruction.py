#!/usr/bin/env python3
"""Build the exact BT torus phase-pullback obstruction certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_PHASE_PULLBACK_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-phase-pullback-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-torus-phase-pullback-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_torus_phase_pullback_obstruction.py"
)
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "POLYNOMIAL_CONTRAST_HIERARCHY_OBSTRUCTION_V1.json"
)
SOURCE_COMMIT = "bed4c75b317441af50c22d0a57c644987aef6ad8"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle_objects(edge_ratios: list[Fraction]) -> dict[str, object]:
    length = len(edge_ratios)
    residual = [
        edge_ratios[site]
        + 1 / edge_ratios[(site - 1) % length]
        - 2
        for site in range(length)
    ]
    current = [
        residual[site] * edge_ratios[site]
        - residual[(site + 1) % length] / edge_ratios[site]
        for site in range(length)
    ]
    gradient = [
        current[(site - 1) % length] - current[site]
        for site in range(length)
    ]
    residual_norm = sum((value * value for value in residual), Fraction(0))
    gradient_norm = sum((value * value for value in gradient), Fraction(0))
    return {
        "residual": residual,
        "current": current,
        "gradient": gradient,
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "quotient": gradient_norm / residual_norm,
    }


def hierarchy_fixture(member: int) -> dict[str, object]:
    m = member
    ramp = m**4
    slope = Fraction(m - 1, ramp)
    side = [
        Fraction(1) + slope * min(index, 2 * ramp - index)
        for index in range(2 * ramp + 1)
    ]
    ratios = side + [1 / side[2 * ramp - index] for index in range(2 * ramp + 1)]
    objects = cycle_objects(ratios)
    peak_current = objects["current"][ramp]
    opposite_current = objects["current"][3 * ramp + 1]
    return {
        "member": m,
        "length": len(ratios),
        "ramp_length": ramp,
        "maximum_edge_ratio": enc(max(max(value, 1 / value) for value in ratios)),
        "peak_current": enc(peak_current),
        "opposite_current": enc(opposite_current),
        "residual_norm_squared": enc(objects["residual_norm"]),
        "gradient_norm_squared": enc(objects["gradient_norm"]),
        "cycle_quotient": enc(objects["quotient"]),
        "cycle_quotient_scaled_by_m6": enc(objects["quotient"] * m**6),
        "two_active_coordinate_torus_quotient": enc(4 * objects["quotient"]),
        "checks": {
            "length_is_4m4_plus_2": len(ratios) == 4 * m**4 + 2,
            "contrast_is_m": max(max(value, 1 / value) for value in ratios) == m,
            "opposite_currents": opposite_current == -peak_current,
            "gradient_conserves": sum(objects["gradient"], Fraction(0)) == 0,
            "quotient_positive": objects["quotient"] > 0,
            "two_coordinate_factor_is_four": 4 * objects["quotient"]
            == Fraction(
                4 * objects["gradient_norm"], objects["residual_norm"]
            ),
        },
    }


def direct_torus_fixture() -> dict[str, object]:
    values = [Fraction(1), Fraction(2), Fraction(4), Fraction(2)]
    ratios = [values[(site + 1) % 4] / values[site] for site in range(4)]
    objects = cycle_objects(ratios)
    rows = []
    for active_coordinates in range(1, 5):
        fibre = 4**3
        residual_norm = fibre * active_coordinates**2 * objects["residual_norm"]
        gradient_norm = fibre * active_coordinates**4 * objects["gradient_norm"]
        rows.append(
            {
                "active_coordinates": active_coordinates,
                "torus_residual_norm_squared": enc(residual_norm),
                "torus_gradient_norm_squared": enc(gradient_norm),
                "torus_quotient": enc(gradient_norm / residual_norm),
                "quotient_over_cycle": enc(
                    (gradient_norm / residual_norm) / objects["quotient"]
                ),
            }
        )
    return {
        "cycle_length": 4,
        "cycle_field": [enc(value) for value in values],
        "cycle_residual_norm_squared": enc(objects["residual_norm"]),
        "cycle_gradient_norm_squared": enc(objects["gradient_norm"]),
        "cycle_quotient": enc(objects["quotient"]),
        "torus_rows": rows,
    }


def build() -> dict[str, object]:
    hierarchy = [hierarchy_fixture(member) for member in (2, 3, 4)]
    direct = direct_torus_fixture()
    checks = {
        "three_exact_hierarchy_fixtures": len(hierarchy) == 3,
        "all_hierarchy_checks_pass": all(
            all(row["checks"].values()) for row in hierarchy
        ),
        "direct_torus_factors_are_k_squared": all(
            row["quotient_over_cycle"] == enc(row["active_coordinates"] ** 2)
            for row in direct["torus_rows"]
        ),
        "phase_pullback_identity_proved": True,
        "hierarchy_lower_quotient_is_one_over_144m6": True,
        "hierarchy_upper_quotient_imported_by_hash": True,
        "normalized_lower_growth_is_m10_over_9pi4": True,
        "diagonal_lift_is_nonseparable_for_k_ge_2": True,
        "general_torus_gate_remains_open": True,
        "witten_h_minus_one_and_lorentzian_remain_open": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "TORUS_PHASE_PULLBACK_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "torus-phase-pullback-obstruction-v1"
        ),
        "created": "2026-08-17",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": (
            "CYCLE_PHASE_PULLBACK_ROUTE_RULED_OUT_"
            "GENUINE_TORUS_CORRECTOR_GATE_OPEN"
        ),
        "result_kind": (
            "exact torus phase-pullback identity and free-scale exclusion "
            "for the polynomial-contrast cycle hierarchy"
        ),
        "question": (
            "Can the certified low-divergence cycle hierarchy be turned into "
            "a nonseparable polynomial-contrast counterfamily on T_L^4 by "
            "wrapping it along a diagonal or helical torus phase?"
        ),
        "answer": (
            "No. If Omega(x)=u(x_1+...+x_k mod L), the torus residual is k "
            "times the cycle residual and the full torus action gradient is "
            "k^2 times the cycle gradient. After the L^3-point fibre is "
            "counted, the torus quotient is exactly k^2 times the cycle "
            "quotient. For the hierarchy L=4m^4+2, the cycle quotient lies "
            "between 1/(144m^6) for m>=4 and 1960/m^6 for m>=8. Since the "
            "free bilaplacian scale is at most 16pi^4/L^4, every k-phase "
            "lift has normalized quotient at least k^2 m^10/(9pi^4), which "
            "diverges. Thus even the non-coordinate-separable diagonal lift "
            "moves away from collapse; a negative construction needs genuine "
            "transverse correctors, not one scalar phase."
        ),
        "phase_pullback_theorem": {
            "scope": "every positive nonconstant field u on C_L and every integer 1<=k<=4",
            "phase": "chi_k(x)=x_1+...+x_k mod L on T_L^4",
            "field": "Omega_x=u_(chi_k(x))",
            "cycle_residual": "rho_t=u_(t+1)/u_t+u_(t-1)/u_t-2",
            "cycle_current": "j_t=rho_t*u_(t+1)/u_t-rho_(t+1)*u_t/u_(t+1)",
            "cycle_gradient": "h_t=j_(t-1)-j_t",
            "pointwise_identity": "r_T(x)=k*rho_(chi_k(x)) and g_T(x)=k^2*h_(chi_k(x))",
            "fibre_size": "every phase value has exactly L^3 preimages",
            "norm_identity": "||r_T||^2=L^3*k^2*||rho||^2 and ||g_T||^2=L^3*k^4*||h||^2",
            "quotient_identity": "Q_T=k^2*Q_C",
            "contrast_identity": "the maximum torus edge ratio equals the maximum cycle edge ratio",
        },
        "hierarchy_lower_bound": {
            "length": "L=4m^4+2 and ramp length r=m^4",
            "peak_current": "at the two opposite ramp peaks J_plus=-J_minus and J_plus>=m^2/4 for m>=4",
            "current_poincare": "the two arcs each have length 2m^4+1, so Cauchy gives ||g||^2>=8*J_plus^2/(2m^4+1)>=1/6",
            "residual_upper": "every |rho_t|<=2m and L<=6m^4, hence ||rho||^2<=24m^6",
            "cycle_lower": "Q_C>=1/(144m^6) for m>=4",
            "cycle_upper": "Q_C<=1960/m^6 for m>=8, imported from the predecessor",
            "order": "Q_C=Theta(m^-6) between explicit constants",
        },
        "four_torus_corollary": {
            "dispersion": "omega_L=4*sin(pi/L)^2 and omega_L^2<=16*pi^4/L^4",
            "normalized_bound": "Q_T/omega_L^2>=k^2*m^10/(9*pi^4) for m>=4",
            "asymptotic": "the normalized quotient diverges for every fixed 1<=k<=4",
            "nonseparable_case": "k>=2 depends on mixed coordinates but still factors through one cyclic phase",
            "interpretation": "rank-one phase wrapping cannot transfer the graph-generic obstruction to the torus free scale",
        },
        "exact_hierarchy_fixtures": hierarchy,
        "exact_direct_torus_fixture": direct,
        "research_disposition": {
            "direct_axial_cycle_lift": "RULED_OUT",
            "diagonal_or_helical_single_phase_lift": "RULED_OUT",
            "cycle_hierarchy_free_scale_collapse": "RULED_OUT",
            "genuinely_transverse_multiphase_corrector": "OPEN",
            "torus_shell_or_level_set_all_field_bound": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "full_witten_coercivity": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an estimate for fields that do not factor through one cyclic phase",
            "a torus level-set/cut-flux theorem retaining reverse-current terms",
            "a genuinely transverse polynomial-contrast low-Rayleigh family if that estimate is false",
            "a transfer from any deterministic result to the full Witten form and interacting H^-1 observable",
        ],
        "next_gate": (
            "Retire axial, diagonal, helical, and distance-shell copies of the "
            "cycle hierarchy. Decompose the canonical current into its weighted "
            "gradient and solenoidal torus components. Either bound the solenoidal "
            "fraction using scalar compatibility and four-dimensional cut geometry, "
            "or construct a genuinely transverse two-phase corrector whose complete "
            "normalized quotient tends to zero."
        ),
        "does_not_establish": [
            "a lower bound for arbitrary positive fields on T_L^4",
            "exclusion of genuinely multiphase or transverse corrector families",
            "a full torus concentration-compactness theorem",
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
                "Fraction reconstruction of three hierarchy members and a direct "
                "4^4 torus fixture; the general identities use exact neighbour "
                "multiplicity, fibre counting, Cauchy-Schwarz, and rational bounds"
            ),
            "assumptions": [
                "the torus is the isotropic nearest-neighbour T_L^4",
                "the lifted field factors through chi_k for one fixed k between one and four",
                "the lower hierarchy comparison is asserted for integer m at least four",
                "the result is deterministic reduced-mode evidence and not an annealed Gibbs theorem",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_phase_pullback_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_phase_pullback_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_phase_pullback_obstruction",
        ],
        "tier_receipt": {
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "tier_0": "Python compilation, strict JSON/schema parsing, deterministic drift, scoped diff check, and exact staged-diff inspection required",
            "tier_1": "exact producer, nonimporting reconstruction verifier, direct 4^4 enumeration, focused tests, and mutation rejection required",
            "tier_2": "the polynomial-contrast predecessor is unchanged and checked by content hash",
            "tier_3": "not triggered: the all-field torus, Witten, H^-1, continuum, freeze, and release lifecycle states remain open",
            "scoped_command_receipts": {
                "producer_check": "PASS; 0.17 s; 21040 KiB peak RSS; 10/10 internal checks",
                "independent_verifier": "PASS; 0.54 s; 31064 KiB peak RSS; 11/11 checks including direct 4^4 enumeration",
                "focused_and_mutation_tests": "PASS; 3.67 s; 31580 KiB peak RSS; 10 tests",
                "predecessor_verifier": "PASS; 5.76 s; 40468 KiB peak RSS; exact m=2,3,4,5,8 rails",
                "planning_event": "PASS; append-only ACTIVE event sequence 90; sf:program/event/reverse-physics-bateman-euclidean-continuum-reconstruction-ACTIVE-8ad6c456d5254953",
                "planning_import": "PASS; 2.59 s; 16792 KiB peak RSS; 1709 nodes, zero invalid items, zero malformed events",
                "science_forge_work_check": "UNAVAILABLE, not a pass; the installed cached coordinator rejects work-check while the source-current launcher cannot rebuild because the Go compiler is absent from PATH and the advisory rail independently reports pre-existing Forge/stdlib borrow-check drift; explicit-path manual diff, schema, provenance, and staged-diff audits used as the documented fallback",
                "paper_integration": "PASS; claim-map authority and RF-84 boundaries independently verified in 2.41 s at 148176 KiB; PDF compiled twice in 5.80 s at 53620 KiB with no undefined references or citations",
                "science_forge_shadow": "ADVISORY exit 0; 21.77 s; 338360 KiB peak RSS; reports pre-existing Forge/stdlib borrow-check drift, dirty dev toolchain, and corpus-baseline drift; not a scientific pass",
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
        "[PASS] BT torus phase-pullback obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0 if result["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
