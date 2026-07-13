#!/usr/bin/env python3
"""C2h: exact nontrivial HPL/Cartan transfer fixture.

The residual algebra is ``[D,K]=K``.  A local complex has one surviving
class ``h`` and a contractible pair ``a -> u``; crucially, ``K h=u`` is
exact.  The residual perturbation therefore changes the HPL inclusion
nontrivially.  The script verifies that a D-equivariant retract nevertheless
transfers the strict CE differential, elementary D-ghost contraction, and
Cartan identity exactly.

This proves only the finite algebraic transfer lemma.  It does not construct
the pure-Weyl local Diff x Weyl BV complex or its zero-mode split.
"""

from __future__ import annotations

import argparse

import sympy as sp


D_GHOST = 0
K_GHOST = 1
GHOST_BASIS = ((), (D_GHOST,), (K_GHOST,), (D_GHOST, K_GHOST))
LOCAL_A, LOCAL_H, LOCAL_U = range(3)
LOCAL_BASIS = (LOCAL_A, LOCAL_H, LOCAL_U)


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def wedge(first: tuple[int, ...], second: tuple[int, ...]):
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


def contract_d(monomial: tuple[int, ...]):
    if D_GHOST not in monomial:
        return None
    position = monomial.index(D_GHOST)
    return (-1) ** position, monomial[:position] + monomial[position + 1 :]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-pure-weyl-bv",
        action="store_true",
        help="fail closed: the fixture is not the pure-Weyl local BV complex",
    )
    args = parser.parse_args()
    if args.claim_pure_weyl_bv:
        raise SystemExit(
            "pure-Weyl local fields, antifields, gauge fixing, and zero modes are not encoded"
        )

    weight = sp.Integer(1)
    surviving_degree = sp.Integer(2)

    # deg(a)=-1 and deg(h)=deg(u)=0, with q a=u and s u=a.
    local_d = sp.zeros(3)
    local_d[LOCAL_U, LOCAL_A] = 1
    local_h = sp.zeros(3)
    local_h[LOCAL_A, LOCAL_U] = 1

    # D is diagonal. K has D-grade +1 and sends h to the exact state u.
    rho_d = sp.diag(
        surviving_degree + weight,
        surviving_degree,
        surviving_degree + weight,
    )
    rho_k = sp.zeros(3)
    rho_k[LOCAL_U, LOCAL_H] = 1
    check(
        "C2h-T1: the residual action obeys [D,K]=K exactly",
        rho_d * rho_k - rho_k * rho_d == weight * rho_k,
    )
    check(
        "C2h-T1: residual generators are chain maps of the local complex",
        local_d * rho_d == rho_d * local_d
        and local_d * rho_k == rho_k * local_d,
    )

    full_basis = tuple(
        (ghosts, local) for ghosts in GHOST_BASIS for local in LOCAL_BASIS
    )
    full_index = {basis: index for index, basis in enumerate(full_basis)}
    reduced_index = {ghosts: index for index, ghosts in enumerate(GHOST_BASIS)}
    full_dimension = len(full_basis)
    reduced_dimension = len(GHOST_BASIS)

    q_local = sp.zeros(full_dimension)
    homotopy = sp.zeros(full_dimension)
    perturbation = sp.zeros(full_dimension)
    contraction_d = sp.zeros(full_dimension)

    for column, (ghosts, local) in enumerate(full_basis):
        ghost_number = len(ghosts)
        for target in LOCAL_BASIS:
            if local_d[target, local] != 0:
                q_local[full_index[(ghosts, target)], column] += (
                    (-1) ** ghost_number * local_d[target, local]
                )
            if local_h[target, local] != 0:
                homotopy[full_index[(ghosts, target)], column] += (
                    (-1) ** ghost_number * local_h[target, local]
                )

        contracted = contract_d(ghosts)
        if contracted is not None:
            sign, result = contracted
            contraction_d[full_index[(result, local)], column] = sign

        # Ghost differential: d c^K=-c^D c^K for [D,K]=K.
        if ghosts == (K_GHOST,):
            perturbation[
                full_index[((D_GHOST, K_GHOST), local)], column
            ] -= weight

        # Module term c^a rho(G_a), inserting the ghost on the left.
        for ghost, action in ((D_GHOST, rho_d), (K_GHOST, rho_k)):
            product = wedge((ghost,), ghosts)
            if product is None:
                continue
            sign, result = product
            for target in LOCAL_BASIS:
                perturbation[full_index[(result, target)], column] += (
                    sign * action[target, local]
                )

    inclusion = sp.zeros(full_dimension, reduced_dimension)
    projection = sp.zeros(reduced_dimension, full_dimension)
    for ghosts in GHOST_BASIS:
        inclusion[full_index[(ghosts, LOCAL_H)], reduced_index[ghosts]] = 1
        projection[reduced_index[ghosts], full_index[(ghosts, LOCAL_H)]] = 1

    check(
        "C2h-T2: unperturbed data form an exact strong deformation retract",
        projection * inclusion == sp.eye(reduced_dimension)
        and inclusion * projection
        == sp.eye(full_dimension)
        - q_local * homotopy
        - homotopy * q_local,
    )
    total_q = q_local + perturbation
    check(
        "C2h-T2: the perturbed total differential is exactly nilpotent",
        total_q**2 == sp.zeros(full_dimension),
    )

    full_lie_d = total_q * contraction_d + contraction_d * total_q
    expected_full_lie_d = sp.zeros(full_dimension)
    for column, (ghosts, local) in enumerate(full_basis):
        ghost_weight = -weight * int(K_GHOST in ghosts)
        expected_full_lie_d[column, column] = rho_d[local, local] + ghost_weight
    check(
        "C2h-T2: the unreduced complex obeys the exact Cartan identity",
        full_lie_d == expected_full_lie_d,
    )
    check(
        "C2h-T2: homotopy and perturbation preserve the complete D grading",
        homotopy * full_lie_d == full_lie_d * homotopy
        and perturbation * full_lie_d == full_lie_d * perturbation,
    )

    # For jp=1-qh-hq the Basic Perturbation Lemma uses plus signs.
    corrected_inclusion = (
        sp.eye(full_dimension) + homotopy * perturbation
    ).inv() * inclusion
    corrected_projection = projection * (
        sp.eye(full_dimension) + perturbation * homotopy
    ).inv()
    reduced_q = sp.simplify(projection * perturbation * corrected_inclusion)
    check(
        "C2h-T3: residual transfer changes the inclusion nontrivially",
        corrected_inclusion != inclusion,
    )
    check(
        "C2h-T3: corrected maps are exact chain maps and a retraction",
        total_q * corrected_inclusion == corrected_inclusion * reduced_q
        and corrected_projection * total_q == reduced_q * corrected_projection
        and corrected_projection * corrected_inclusion == sp.eye(reduced_dimension),
    )
    check(
        "C2h-T3: the transferred differential is exactly nilpotent",
        reduced_q**2 == sp.zeros(reduced_dimension),
    )

    expected_reduced_q = sp.zeros(reduced_dimension)
    for ghosts in GHOST_BASIS:
        column = reduced_index[ghosts]
        if ghosts == (K_GHOST,):
            expected_reduced_q[reduced_index[(D_GHOST, K_GHOST)], column] -= weight
        product = wedge((D_GHOST,), ghosts)
        if product is not None:
            sign, result = product
            expected_reduced_q[reduced_index[result], column] += (
                sign * surviving_degree
            )
    check(
        "C2h-T3: transfer gives the strict residual CE differential",
        reduced_q == expected_reduced_q,
    )

    elementary_reduced_contraction = sp.zeros(reduced_dimension)
    for ghosts in GHOST_BASIS:
        contracted = contract_d(ghosts)
        if contracted is not None:
            sign, result = contracted
            elementary_reduced_contraction[
                reduced_index[result], reduced_index[ghosts]
            ] = sign
    expected_reduced_lie_d = sp.diag(
        *(
            surviving_degree - weight * int(K_GHOST in ghosts)
            for ghosts in GHOST_BASIS
        )
    )
    transferred_contraction = sp.simplify(
        corrected_projection * contraction_d * corrected_inclusion
    )
    transferred_lie_d = sp.simplify(
        corrected_projection * full_lie_d * corrected_inclusion
    )
    check(
        "C2h-T4: elementary D-ghost contraction transfers unchanged",
        transferred_contraction == elementary_reduced_contraction,
    )
    check(
        "C2h-T4: the compact-degree operator transfers as the expected grading",
        transferred_lie_d == expected_reduced_lie_d,
    )
    check(
        "C2h-T4: reduced Cartan identity survives the nontrivial transfer",
        reduced_q * elementary_reduced_contraction
        + elementary_reduced_contraction * reduced_q
        == expected_reduced_lie_d,
    )

    print("full/reduced dimensions:", full_dimension, reduced_dimension)
    print("corrected inclusion differs from the naive inclusion: True")
    print("transferred residual differential:", reduced_q)
    print("transferred D grading:", expected_reduced_lie_d)
    print("CONFORMAL C2h CARTAN TRANSFER FIXTURE: ALL PASS")


if __name__ == "__main__":
    main()
