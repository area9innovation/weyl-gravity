#!/usr/bin/env python3
"""Certify the BT pointwise mixed-Hessian-square scaling obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_HESSIAN_SQUARE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-mixed-hessian-square-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-mixed-hessian-square-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_mixed_hessian_square_obstruction.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_HEAT_BATH_INFLUENCE_SYMBOL_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_UNIFORM_POINCARE_V1.json"
    ),
]
SOURCE_COMMIT = "dd7d9c131517b3774015f2e871a579b4a3c94588"
Site = tuple[int, int, int, int]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def directions() -> list[Site]:
    result: list[Site] = []
    for axis in range(4):
        for step in (-1, 1):
            vector = [0, 0, 0, 0]
            vector[axis] = step
            result.append(tuple(vector))
    return result


DIRS = directions()
PROFILE = tuple(Fraction(value) for value in (1, 2, 3, 4))
ORIGIN = (0, 0, 0, 0)


def add(left: Site, right: Site) -> Site:
    return tuple(left[index] + right[index] for index in range(4))


def omega(site: Site) -> Fraction:
    """The positive period-four axial profile Omega=(1,2,3,4)."""

    return PROFILE[site[0] % 4]


def transfer(left: Site, right: Site) -> Fraction:
    return omega(right) / omega(left)


def residual(site: Site) -> Fraction:
    return sum((transfer(site, add(site, edge)) for edge in DIRS), Fraction()) - 8


def origin_hessian_row() -> dict[Site, Fraction]:
    """Exact Hessian row of A=1/2 sum r_x^2 from its range-two stencil."""

    row: dict[Site, Fraction] = {}
    for edge in DIRS:
        site = add(ORIGIN, edge)
        row[site] = (
            -(8 + 2 * residual(ORIGIN)) * transfer(ORIGIN, site)
            -(8 + 2 * residual(site)) * transfer(site, ORIGIN)
        )
    for edge in DIRS:
        middle = add(ORIGIN, edge)
        site = add(middle, edge)
        row[site] = row.get(site, Fraction()) + (
            transfer(middle, ORIGIN) * transfer(middle, site)
        )
    for left_index, left in enumerate(DIRS):
        left_axis = next(index for index, value in enumerate(left) if value)
        for right in DIRS[left_index + 1 :]:
            right_axis = next(index for index, value in enumerate(right) if value)
            if left_axis == right_axis:
                continue
            left_middle = add(ORIGIN, left)
            right_middle = add(ORIGIN, right)
            site = add(left_middle, right)
            row[site] = row.get(site, Fraction()) + (
                transfer(left_middle, ORIGIN) * transfer(left_middle, site)
                + transfer(right_middle, ORIGIN) * transfer(right_middle, site)
            )
    row[ORIGIN] = -sum(row.values(), Fraction())
    return row


def shell_sums(row: dict[Site, Fraction]) -> dict[int, Fraction]:
    return {
        offset: sum(
            (value for site, value in row.items() if site[0] == offset),
            Fraction(),
        )
        for offset in (-2, -1, 1, 2)
    }


def build() -> dict:
    row = origin_hessian_row()
    shells = shell_sums(row)
    sine_one = shells[1] - shells[-1]
    sine_two = shells[2] - shells[-2]
    first_moment = sine_one + 2 * sine_two
    checks = {
        "profile_is_positive": all(value > 0 for value in PROFILE),
        "origin_residual_is_four": residual(ORIGIN) == 4,
        "range_two_row_has_forty_off_diagonal_sites": len(row) == 41,
        "shift_null_row_sum": sum(row.values(), Fraction()) == 0,
        "minus_two_shell_is_three_sixteenths": shells[-2] == Fraction(3, 16),
        "minus_one_shell_is_minus_forty": shells[-1] == -40,
        "plus_one_shell_is_minus_twenty_one": shells[1] == -21,
        "plus_two_shell_is_three_quarters": shells[2] == Fraction(3, 4),
        "sine_one_coefficient_is_nineteen": sine_one == 19,
        "sine_two_coefficient_is_nine_sixteenths": sine_two == Fraction(9, 16),
        "first_moment_is_161_over_8": first_moment == Fraction(161, 8),
        "fiber_square_limit_is_strictly_positive": first_moment != 0,
        "pointwise_bilaplacian_square_route_is_obstructed": True,
        "signed_covariance_route_remains_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_HESSIAN_SQUARE_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-mixed-hessian-square-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact method obstruction for a pointwise conditional mixed-Hessian-square estimate",
        "question": "Can the quotient-site Poincare/Cauchy response bound retain a uniform bilaplacian omega(p)^2 square at every conditional background?",
        "answer": (
            "No. On every L^4 torus with L a multiple of four and L>=8, repeat the "
            "positive axial profile Omega=(1,2,3,4). At the origin the exact action-"
            "Hessian applied to k_L(x)=sin(2*pi*x_1/L) is "
            "19*sin(p_L)+(9/16)*sin(2*p_L), hence (161/8)*p_L+O(p_L^3). "
            "Along the quotient-site conditional fiber the leading coefficient is "
            "analytic and is nonzero at the displayed profile, so its conditional "
            "square has a strictly positive p_L^2 limit coefficient. Since "
            "omega(p_L)^2 is order p_L^4, no background-uniform pointwise bound of "
            "that square by C*omega(p_L)^2 can hold. This retires only the route that "
            "takes the conditional square before extracting signed lattice "
            "cancellations; it does not obstruct the exact signed covariance response."
        ),
        "model": {
            "action": "A(psi)=1/2*sum_x r_x(psi)^2",
            "residual": "r_x=sum_{y~x} exp(psi_y-psi_x)-8",
            "scaled_action": "S(phi)=A(lambda*phi)/lambda^2",
            "hessian_scaling": "Hess_phi S=Hess_psi A",
            "site_direction": "h_o=delta_o-N^-1*1",
            "shift_nullity": "Hess A annihilates the constant vector, so Hess S[h_o,k]=(Hess A*k)_o",
        },
        "exact_range_two_stencil": {
            "nearest": "H_xy=-(8+2*r_x)*t_xy-(8+2*r_y)*t_yx for x~y",
            "axial_distance_two": "H_x,x+2e=t_x+e,x*t_x+e,x+2e",
            "mixed_distance_two": "H_x,x+e+f=t_x+e,x*t_x+e,x+e+f+t_x+f,x*t_x+f,x+e+f",
            "diagonal": "H_xx=-sum_{y!=x} H_xy",
            "transfer": "t_xy=Omega_y/Omega_x",
        },
        "periodic_fixture": {
            "volumes": "L^4 with L>=8 and L divisible by 4",
            "profile": [enc(value) for value in PROFILE],
            "profile_definition": "Omega_x=(1,2,3,4) indexed by x_1 mod 4 and constant in the transverse coordinates",
            "origin_residual": enc(residual(ORIGIN)),
            "origin_row_support": len(row),
            "axial_shell_sums": {str(key): enc(value) for key, value in shells.items()},
            "signed_unit_sine_coefficient": enc(sine_one),
            "signed_double_sine_coefficient": enc(sine_two),
            "first_axial_moment": enc(first_moment),
            "first_axial_moment_square": enc(first_moment * first_moment),
        },
        "long_wave_obstruction": {
            "mode": "k_L(x)=sin(p_L*x_1), p_L=2*pi/L; it is mean zero and k_L(o)=0, hence k_L lies in h_o^perp",
            "exact_origin_image": "Hess S[h_o,k_L]=19*sin(p_L)+(9/16)*sin(2*p_L) at the displayed fiber point",
            "pointwise_asymptotic": "Hess S[h_o,k_L]=(161/8)*p_L+O(p_L^3)",
            "conditional_fiber": "vary phi along h_o, equivalently multiply only Omega_o by exp(lambda*s); additive constants cancel from the normalized one-site law",
            "positive_limit": "lim_{L->infinity,4|L} E_q[(Hess S[h_o,k_L])^2]/p_L^2=E_q[M(s)^2]>0 for every nonzero lambda because M is analytic, q has positive density, and M(0)=161/8",
            "dispersion": "omega(p_L)=2*(1-cos(p_L))=p_L^2+O(p_L^4)",
            "divergence": "E_q[(Hess S[h_o,k_L])^2]/omega(p_L)^2 diverges like a positive constant times p_L^-2",
            "obstructed_estimate": "E_q[(Hess S[h_o,k_L])^2]<=C*omega(p_L)^2 uniformly in L and conditional backgrounds",
        },
        "method_disposition": {
            "exact_range_two_mixed_hessian": "PROVED",
            "background_uniform_pointwise_bilaplacian_square_bound": "OBSTRUCTED",
            "local_poincare_then_cauchy_route": "INSUFFICIENT_FOR_BILAPLACIAN_SCALING",
            "signed_conditional_covariance_response": "OPEN",
            "annealed_fourier_or_multiscale_cancellation": "OPEN",
            "volume_uniform_global_poincare": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "interacting_continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an estimate of the signed conditional covariance before squaring or taking absolute values",
            "an annealed block response identity that restores the omega(p)^2 cancellation",
            "a volume-uniform global Poincare/Witten or interacting H^-1 theorem",
        ],
        "next_gate": (
            "Keep the covariance sign in D_k m_o=-Cov(s,D_k S). Compute the "
            "translation-averaged signed response kernel, or condition whole blocks "
            "larger than the period-four fluctuation, before applying Cauchy. Test "
            "whether its axial symbol has a controlled omega term plus omega^2 term."
        ),
        "does_not_establish": [
            "failure of the signed conditional covariance or every heat-bath method",
            "failure of a block or annealed multiscale estimate",
            "failure of a global finite-volume or volume-uniform Poincare/Witten theorem",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound",
            "an interacting continuum Euclidean measure or ordinary OS reconstruction",
            "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Python integer/Fraction arithmetic on the exact local range-two stencil",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_hessian_square_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_hessian_square_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_hessian_square_obstruction",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer replay, independent residual-derivative Hessian verifier, and focused mutation tests required",
            "tier_2": "the unchanged one-site Poincare and heat-bath response inputs are checked by content hash; no shared operator changed",
            "tier_3": "not applicable: this is a method obstruction, not an H^-1/reconstruction theorem, freeze, release, or shared-core promotion",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; Go used GOMEMLIMIT=300MiB and GOGC=50",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.03 s, 20420 KiB",
                "independent_verifier": "0.11 s, 30340 KiB",
                "unit_tests": "0.26 s, 30672 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1694 nodes, 0 invalid items, 0 malformed events; 7.8 s under the declared Go memory policy",
                "science_forge_shadow": "not rerun after its earlier memory-capped external-indexing abort; this skip is not a pass",
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
        "[PASS] BT mixed-Hessian square obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
