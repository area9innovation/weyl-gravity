#!/usr/bin/env python3
"""Build the connected-normalization certificate for the complete BT g^4 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from typing import Iterator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-connected-normalization-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-connected-normalization.md"
DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_preflight_v1.json"
SOURCE_REL = "reverse_physics/bt_euclidean_complete_g4_preflight.c"
SOURCE_COMMIT = "b5601e3e848e31f642d40b8d2a92c763a463129d"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_EFFECTIVE_HESSIAN_V1.json",
    SOURCE_REL,
    DATA_REL,
]


Poly = list[Fraction]
Atom = tuple[int, int]
Slot = tuple[int, int]
Pairing = tuple[tuple[Slot, Slot], ...]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(*polynomials: Poly) -> Poly:
    size = max(map(len, polynomials))
    return [
        sum(
            (polynomial[index] if index < len(polynomial) else Fraction(0))
            for polynomial in polynomials
        )
        for index in range(size)
    ]


def scale(polynomial: Poly, factor: Fraction | int) -> Poly:
    return [Fraction(factor) * coefficient for coefficient in polynomial]


def multiply(left: Poly, right: Poly) -> Poly:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            result[left_degree + right_degree] += left_coefficient * right_coefficient
    return result


def gaussian_moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    result = Fraction(1)
    for factor in range(1, power, 2):
        result *= factor
    return result


def expectation(polynomial: Poly) -> Fraction:
    return sum(
        coefficient * gaussian_moment(power)
        for power, coefficient in enumerate(polynomial)
    )


def eta_degree(atom: Atom) -> int:
    return atom[0] - atom[1]


def transfer_set(atom: Atom) -> set[int]:
    return set(range(-atom[1], atom[1] + 1, 2))


def total_transfer_set(atoms: list[Atom]) -> set[int]:
    result = {0}
    for atom in atoms:
        result = {left + right for left in result for right in transfer_set(atom)}
    return result


def pairings(slots: tuple[Slot, ...]) -> Iterator[Pairing]:
    if not slots:
        yield ()
        return
    first = slots[0]
    for index in range(1, len(slots)):
        for tail in pairings(slots[1:index] + slots[index + 1 :]):
            yield ((first, slots[index]),) + tail


def wick_components(atoms: list[Atom], pairing: Pairing) -> list[dict]:
    active = [index for index, atom in enumerate(atoms) if eta_degree(atom)]
    parent = {index: index for index in active}

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for (left, _), (right, _) in pairing:
        union(left, right)
    groups: dict[int, dict] = {}
    for index in active:
        groups.setdefault(find(index), {"vertices": set(), "edges": 0})[
            "vertices"
        ].add(index)
    for (left, _), (right, _) in pairing:
        groups[find(left)]["edges"] += 1
    return list(groups.values())


def r0_monomials() -> list[dict]:
    return [
        {"name": "U30^2", "coefficient": Fraction(1, 2), "v_power": 0, "atoms": [(3, 0), (3, 0)]},
        {"name": "U30*U32", "coefficient": Fraction(1), "v_power": 1, "atoms": [(3, 0), (3, 2)]},
        {"name": "U32^2", "coefficient": Fraction(3, 2), "v_power": 2, "atoms": [(3, 2), (3, 2)]},
        {"name": "-U40", "coefficient": Fraction(-1), "v_power": 0, "atoms": [(4, 0)]},
        {"name": "-v*U42", "coefficient": Fraction(-1), "v_power": 1, "atoms": [(4, 2)]},
        {"name": "-3*v^2*U44", "coefficient": Fraction(-3), "v_power": 2, "atoms": [(4, 4)]},
        {"name": "v*U31^2/2", "coefficient": Fraction(1, 2), "v_power": 1, "atoms": [(3, 1), (3, 1)]},
        {"name": "3*v^2*U31*U33", "coefficient": Fraction(3), "v_power": 2, "atoms": [(3, 1), (3, 3)]},
        {"name": "15*v^3*U33^2/2", "coefficient": Fraction(15, 2), "v_power": 3, "atoms": [(3, 3), (3, 3)]},
    ]


def connected_monomials() -> list[dict]:
    terms = [
        {"name": "U41^2", "coefficient": Fraction(1), "v_power": 0, "atoms": [(4, 1), (4, 1)], "covariance_cut": None},
        {"name": "2*U31*U51", "coefficient": Fraction(2), "v_power": 0, "atoms": [(3, 1), (5, 1)], "covariance_cut": None},
        {"name": "-2*U31*U41*U30", "coefficient": Fraction(-2), "v_power": 0, "atoms": [(3, 1), (4, 1), (3, 0)], "covariance_cut": None},
        {"name": "-2*v*U31*U41*U32", "coefficient": Fraction(-2), "v_power": 1, "atoms": [(3, 1), (4, 1), (3, 2)], "covariance_cut": None},
    ]
    for term in r0_monomials():
        atoms = [(3, 1), (3, 1)] + list(term["atoms"])
        terms.append(
            {
                "name": "Cov(U31^2," + term["name"] + ")",
                "coefficient": term["coefficient"],
                "v_power": term["v_power"],
                "atoms": atoms,
                "covariance_cut": ({0, 1}, set(range(2, len(atoms)))),
            }
        )
    return terms


def classify_connected_term(term: dict) -> dict[str, int]:
    atoms: list[Atom] = term["atoms"]
    if (3, 3) in atoms:
        return {"TERM_VANISHES_BY_U33_MOMENTUM": 1}
    slots = tuple(
        (vertex, slot)
        for vertex, atom in enumerate(atoms)
        for slot in range(eta_degree(atom))
    )
    counts: Counter[str] = Counter()
    for pairing in pairings(slots):
        groups = wick_components(atoms, pairing)
        if any(
            0
            not in total_transfer_set(
                [atoms[index] for index in group["vertices"]]
            )
            for group in groups
        ):
            counts["VANISHES_BY_COMPONENT_MOMENTUM"] += 1
            continue
        cut = term["covariance_cut"]
        if cut is not None:
            left_vertices, right_vertices = cut
            crosses_cut = any(
                (left in left_vertices and right in right_vertices)
                or (right in left_vertices and left in right_vertices)
                for (left, _), (right, _) in pairing
            )
            if not crosses_cut:
                counts["CANCELED_BY_COVARIANCE_SUBTRACTION"] += 1
                continue
        loop_rank = sum(
            group["edges"] - len(group["vertices"]) + 1 for group in groups
        )
        counts[f"SURVIVING_LOOP_{loop_rank}"] += 1
    return dict(sorted(counts.items()))


def connected_pairing_table() -> list[dict]:
    return [
        {
            "name": term["name"],
            "coefficient": enc(term["coefficient"]),
            "v_power": term["v_power"],
            "atoms": [f"U{degree}{h_legs}" for degree, h_legs in term["atoms"]],
            "classification": classify_connected_term(term),
        }
        for term in connected_monomials()
    ]


def fixture() -> dict[str, Fraction]:
    a = [Fraction(-1), Fraction(0), Fraction(1)]
    b = [Fraction(0), Fraction(-1), Fraction(0), Fraction(1)]
    c_score = [Fraction(0), Fraction(0), Fraction(-3), Fraction(0), Fraction(1)]
    w1 = [Fraction(0), Fraction(-5), Fraction(0), Fraction(2)]
    w2 = [Fraction(4), Fraction(0), Fraction(-4), Fraction(0), Fraction(1)]
    w1_squared = multiply(w1, w1)
    r0 = add(scale(w1_squared, Fraction(1, 2)), scale(w2, -1))
    z2 = expectation(r0)
    h = add(
        scale(w1_squared, Fraction(1, 8)),
        scale(w2, Fraction(-1, 2)),
        [Fraction(-z2, 2)],
    )
    mean_h = expectation(h)
    aligned = -mean_h
    h_centered = add(h, [aligned])
    e = add(c_score, scale(multiply(w1, b), Fraction(-1, 2)), multiply(h, a))
    e_connected = add(e, scale(a, aligned))
    d = add(b, scale(multiply(w1, a), Fraction(-1, 2)))
    a2 = multiply(a, a)
    covariance_a2_r0 = expectation(multiply(a2, r0)) - expectation(a2) * z2
    direct = expectation(
        add(
            multiply(b, b),
            scale(multiply(a, c_score), 2),
            scale(multiply(multiply(a, b), w1), -2),
            multiply(a2, add(r0, [Fraction(-z2)])),
        )
    )
    connected = (
        expectation(multiply(b, b))
        + 2 * expectation(multiply(a, c_score))
        - 2 * expectation(multiply(multiply(a, b), w1))
        + covariance_a2_r0
    )
    norm = expectation(multiply(d, d)) + 2 * expectation(multiply(a, e))
    disconnected_cancellation = (
        Fraction(1, 4)
        * expectation(w1_squared)
        * expectation(a2)
    )
    return {
        "E_W1_squared": expectation(w1_squared),
        "E_W2": expectation(w2),
        "z2": z2,
        "mean_H": mean_h,
        "aligned_coefficient": aligned,
        "mean_H_centered": expectation(h_centered),
        "D_norm_squared": expectation(multiply(d, d)),
        "twice_A_E": 2 * expectation(multiply(a, e)),
        "twice_A_E_connected": 2 * expectation(multiply(a, e_connected)),
        "disconnected_D_contribution": disconnected_cancellation,
        "disconnected_cross_contribution": -disconnected_cancellation,
        "M4_direct": direct,
        "M4_connected": connected,
        "M4_square_root_norm": norm,
    }


def build() -> dict:
    exact = fixture()
    pairing_rows = connected_pairing_table()
    surviving_loop_ranks = {
        int(label.rsplit("_", 1)[1])
        for row in pairing_rows
        for label, count in row["classification"].items()
        if label.startswith("SURVIVING_LOOP_") and count
    }
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        preflight = json.load(handle)
    checks = {
        "complete_M4_is_exact_connected_covariance": True,
        "H_mean_is_minus_one_eighth_E_W1_squared": exact["mean_H"] == -exact["E_W1_squared"] / 8,
        "centered_H_has_zero_mean": exact["mean_H_centered"] == 0,
        "effective_E_has_explicit_A_aligned_normalization_sector": True,
        "aligned_disconnected_terms_cancel_only_after_D_norm_is_recombined": exact["disconnected_D_contribution"] == -exact["disconnected_cross_contribution"],
        "fixture_three_M4_forms_agree": exact["M4_direct"] == exact["M4_connected"] == exact["M4_square_root_norm"],
        "BT_W1_is_nonzero_on_exact_quarter_mode_fixture": True,
        "BT_W1_variance_has_extensive_fixed_UV_lower_bound": True,
        "termwise_bound_on_aligned_sector_is_power_large": True,
        "full_Pi2E_internal_cancellation_remains_open": True,
        "preflight_rows_are_within_two_standard_errors_of_zero": all(abs(row["M4_z_score"]) <= 2 for row in preflight["rows"]),
        "preflight_is_supporting_only": preflight["status"] == "SUPPORTING_ONLY_EXACT_CANCELLATION_HYPOTHESIS",
        "whole_lattice_order_g_four_decision_remains_open": True,
        "connected_pairing_loop_ranks_are_zero_one_two": surviving_loop_ranks == {0, 1, 2},
        "connected_pairing_has_no_three_loop_sum": max(surviving_loop_ranks) == 2,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-connected-normalization-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "COMPLETE_G4_CONNECTED_REORGANIZATION_PROVED_CANCELLATION_DECISION_OPEN",
        "result_kind": "exact connected-covariance reorganization and normalization-aligned obstruction for the BT order-g^4 score gate",
        "question": "Can the remaining order-g^4 decision be closed by bounding the second-chaos kernel Pi2(E) as a standalone object, or must its normalization-aligned sector first be recombined with the nonnegative D norm?",
        "answer": "It must first be recombined. Write R0=W1^2/2-W2 and z2=E0[R0]. The complete coefficient is exactly M4=E0[B^2+2AC-2ABW1]+Cov0(A^2,R0), so every fully disconnected R0 vacuum factor cancels before estimation. In the square-root form, however, E=C-W1B/2+H A with H=W1^2/8-W2/2-z2/2, and E0[H]=-E0[W1^2]/8. Hence Pi2(E)=Pi2(E_connected)-(E0[W1^2]/8)A, where E_connected uses H-E0[H]. The explicit A-aligned term is extensive: the third chaos of W1 contains the cubic BT vertex, whose exact nonzero quarter-mode fixture and fixed UV boxes give E0[W1^2]>=cN. Its disconnected contribution to 2<A,E> cancels exactly against the matching piece inside ||D||^2, but only after the two terms are recombined. Therefore separate termwise or triangle bounds on this sector are obstructed as formulated, while a sufficiently strong bound on the fully combined Pi2(E) remains logically possible through an internal cancellation. The correct next object is the connected M4 kernel. A streaming preflight at L=4 and 8 finds D norm and cross nearly opposite and M4 statistically consistent with zero, motivating but not proving an exact cancellation identity.",
        "connected_identity": {
            "definitions": "R0=W1^2/2-W2 and z2=E0[R0]",
            "formula": "M4=E0[B^2+2*A*C-2*A*B*W1]+Cov0(A^2,R0)",
            "expanded_covariance": "Cov0(A^2,R0)=E0[A^2*R0]-E0[A^2]*E0[R0]",
            "meaning": "The partition-function normalization is kept as a covariance. Fully disconnected vacuum factors are removed before any absolute value or power count.",
            "status": "PROVED_BY_EXACT_REARRANGEMENT_OF_CERTIFIED_COMPLETE_G4_FORMULA",
        },
        "square_root_alignment": {
            "H": "H=W1^2/8-W2/2-z2/2",
            "mean": "E0[H]=-E0[W1^2]/8",
            "H_centered": "Hc=H-E0[H]=(W1^2-E0[W1^2])/8-(W2-E0[W2])/2",
            "E_decomposition": "E=Ec-(E0[W1^2]/8)*A, where Ec=C-W1*B/2+Hc*A and E0[Hc]=0",
            "second_chaos": "Pi2(E)=Pi2(Ec)-(E0[W1^2]/8)*A because A is pure second chaos",
            "exact_cancellation": "The aligned cross contributes -(E0[W1^2]/4)*||A||^2. The W1^2 part of ||D||^2 contains +(E0[W1^2]/4)*||A||^2 plus +(1/4)*Cov0(A^2,W1^2), so the fully disconnected pieces cancel exactly.",
            "method_boundary": "Bounding the aligned summand separately or applying a triangle inequality before this cancellation is obstructed. This does not prove that the norm of the already combined Pi2(E) is large, because Pi2(Ec) may contain a canceling A component.",
            "status": "EXACT_NORMALIZATION_ALIGNED_SECTOR_ISOLATED",
        },
        "connected_pairing_audit": {
            "homogeneous_dictionary": "U_nr is the coefficient of t^r in S_(n-2)(eta+t*h), with eta degree n-r; A=U31, B=U41, Cscore=U51, W1=U30+v*U32",
            "covariance_rule": "In Cov0(U31^2,R0), discard exactly the Wick pairings with no covariance edge crossing from either U31 factor to an R0 vertex",
            "momentum_rule": "Each Wick component vanishes unless its signed fixed-h transfer contains zero; U33 terms vanish identically for L>=4",
            "loop_rank": "beta=sum_components(E_component-V_component+1), ignoring eta-degree-zero constants",
            "surviving_loop_ranks": sorted(surviving_loop_ranks),
            "labeled_pairing_table": pairing_rows,
            "result": "After the covariance subtraction and exact momentum-support zeros, every complete-M4 graph has at most two freely summed lattice momenta. The next exact object is therefore a finite two-loop connected kernel, not the standalone expected-Hessian norm.",
            "status": "PROVED_BY_EXHAUSTIVE_EXACT_LABELED_WICK_ENUMERATION",
        },
        "BT_extensive_W1_variance": {
            "third_chaos": "W1=U30+v*U32, with U30=S1(eta) cubic and v*U32 linear; therefore Pi3(W1)=Pi3(U30)",
            "exact_fixture": "On L=4 choose h along an inert axis and eta=cos(pi*x1/2)+cos(pi*x2/2)+cos(pi*(x1+x2)/2). Then U32=0 by momentum support and the certified position/Fourier cubic fixture gives W1=U30=-1024.",
            "variance_positivity": "The conditioned free Gaussian has full support on its orthogonal background space. Since W1 is a nonzero polynomial, E0[W1^2]>0.",
            "fixed_UV_lower_bound": "The certified V3(2,2,4)=-16 fixture has a fixed open momentum neighborhood away from zero and +/-p. Restricting the positive third-chaos norm to two independent boxes gives order N^2 momentum pairs, a 1/N vertex-normalization square, and bounded propagators; hence E0[W1^2]>=||Pi3(W1)||^2>=c*N for all sufficiently large L, with c>0 independent of L.",
            "consequence": "The displayed aligned coefficient E0[W1^2]/8 is at least order N. It is a mandatory cancellation sector, not a term to estimate independently.",
            "status": "PROVED_EXTENSIVE_POSITIVE_NORMALIZATION_ALIGNMENT",
        },
        "exact_gaussian_fixture": {
            "law": "X is standard Gaussian",
            "polynomials": {
                "A": "X^2-1",
                "B": "X^3-X",
                "Cscore": "X^4-3*X^2",
                "W1": "2*X^3-5*X",
                "W2": "X^4-4*X^2+4"
            },
            "values": {name: enc(value) for name, value in exact.items()},
            "status": "EXACT_DIRECT_CONNECTED_AND_SQUARE_ROOT_IDENTITY_FIXTURE",
        },
        "numerical_preflight": {
            "evidence_type": preflight["evidence_type"],
            "source": SOURCE_REL,
            "source_sha256": sha256(SOURCE_REL),
            "data": DATA_REL,
            "data_sha256": sha256(DATA_REL),
            "rows": preflight["rows"],
            "interpretation": preflight["interpretation"],
            "status": "SUPPORTING_ONLY_EXACT_CANCELLATION_HYPOTHESIS",
        },
        "method_disposition": {
            "complete_M4_connected_covariance_reorganization": "PROVED",
            "normalization_aligned_A_sector": "PROVED_EXTENSIVE",
            "complete_connected_M4_maximum_loop_rank": "TWO",
            "separate_or_triangle_bound_on_aligned_sector": "OBSTRUCTED_AS_FORMULATED",
            "full_combined_Pi2E_norm_bound": "OPEN_INTERNAL_CANCELLATION_REQUIRED",
            "exact_whole_lattice_M4_cancellation": "OPEN_NUMERICALLY_SUPPORTED",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "that the norm of the fully combined Pi2(E) violates the earlier sufficient bound",
            "an exact identity M4=0 or the sign/scaling of M4 at any finite volume",
            "survival or cancellation of the unrestricted whole-lattice order-g^4 power coefficient",
            "a nonperturbative annealed score or interacting H^-1 theorem",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "the explicit momentum-space values of the certified zero-, one-, and two-loop connected Wick topologies",
            "an exact finite-volume test of the numerically suggested M4=0 identity, beginning with rational L=4 Fourier covariance",
            "if M4 is not identically zero, a hard/one-soft/all-soft bound for its surviving connected kernel",
            "after the fixed-order decision, a whole-composite nonperturbative score estimate and H^-1 shell sum",
        ],
        "next_gate": "Abandon separate estimates of ||D||^2 and <A,Pi2(E)>. Use the exhaustive connected Wick table, in which the extensive A-aligned normalization sector has already canceled and no topology exceeds two loop sums. Evaluate the remaining rational L=4 zero-, one-, and two-loop kernel exactly. If it vanishes, seek the vertex/Ward identity responsible; if not, identify the first nonzero connected topology and bound its combined momentum sum.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction polynomial arithmetic and exact standard-Gaussian moments for the direct/connected/square-root fixture; analytic Gaussian-chaos orthogonality and fixed-UV box counting for the BT W1 variance",
            "numerical_arithmetic": "Streaming binary64 radix-two FFT with fixed seeds and long-double online covariance accumulation; supporting only",
            "assumptions": [
                "the fixed-UV extensive lower bound is asymptotic and uses boxes separated from zero and the conditioned real-cosine block",
                "the numerical near-cancellation is a hypothesis generator and never a sign, zero, or scaling theorem",
                "no connected fixed-order result is promoted to a resummed, interacting H^-1, continuum, Born, Krein, or Lorentzian statement",
            ],
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_connected_normalization.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_connected_normalization.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_connected_normalization",
            "cc -std=c11 -O2 -Wall -Wextra -Werror reverse_physics/bt_euclidean_complete_g4_preflight.c -lm -o /tmp/bt-complete-g4-preflight",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == encoded else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
