#!/usr/bin/env python3
"""Independent unseen-fixture replay of the vector n=1+n=2 CPT projection."""

from __future__ import annotations

import hashlib
import itertools
import json

import sympy as sp

from .generic_background_ghost_n1_n2_vector_cpt_projection import (
    DEPENDENCIES,
    OUTPUT,
    build,
)


UNSEEN_FIXTURES = (
    ((2, 1, -1, 0), (1, -2, 0, 1)),
    ((1, -2, 1, 1), (2, 0, -1, 1)),
)


def _transverse_traceless(momentum: sp.Matrix) -> list[sp.Matrix]:
    transverse = sp.Matrix([list(momentum)]).nullspace()
    frame: list[sp.Matrix] = []
    for vector in transverse:
        for old in frame:
            vector -= old * old.dot(vector) / old.dot(old)
        frame.append(vector)
    projectors = [vector * vector.T / vector.dot(vector) for vector in frame]
    return [
        projectors[0] - projectors[1],
        projectors[0] - projectors[2],
        frame[0] * frame[1].T + frame[1] * frame[0].T,
        frame[0] * frame[2].T + frame[2] * frame[0].T,
        frame[1] * frame[2].T + frame[2] * frame[1].T,
    ]


def _linear_riemann(k: sp.Matrix, ricci: sp.Matrix) -> list[list[sp.Matrix]]:
    h = 2 * ricci / k.dot(k)
    return [
        [
            sp.Matrix(
                4,
                4,
                lambda a, b: sp.Rational(1, 2)
                * (
                    -k[mu] * k[b] * h[a, nu]
                    - k[nu] * k[a] * h[b, mu]
                    + k[nu] * k[b] * h[a, mu]
                    + k[mu] * k[a] * h[b, nu]
                ),
            )
            for nu in range(4)
        ]
        for mu in range(4)
    ]


def _source(structure: int, momenta: list[sp.Matrix], tensors: list[sp.Matrix]) -> sp.Expr:
    r1 = _linear_riemann(momenta[0], tensors[0])
    r2 = _linear_riemann(momenta[1], tensors[1])
    if structure == 3:
        return sum(
            (
                sp.trace(r1[mu][nu] * r2[mu][nu] * tensors[2])
                for mu, nu in itertools.product(range(4), repeat=2)
            ),
            sp.S.Zero,
        )
    divergence1 = [
        sum((momenta[0][mu] * r1[mu][nu] for mu in range(4)), sp.zeros(4))
        for nu in range(4)
    ]
    divergence2 = [
        sum((momenta[1][mu] * r2[mu][nu] for mu in range(4)), sp.zeros(4))
        for nu in range(4)
    ]
    return -sum(
        (sp.trace(divergence1[nu] * divergence2[nu] * tensors[2]) for nu in range(4)),
        sp.S.Zero,
    )


def _carrier(
    carrier: str,
    labels: list[int],
    momenta: list[sp.Matrix],
    tensors: list[sp.Matrix],
) -> sp.Expr:
    indices = [label - 1 for label in labels]
    k1, k2, k3 = [momenta[index] for index in indices]
    first, second, third = [tensors[index] for index in indices]
    if carrier == "I10":
        return sp.trace(first * second * third)
    if carrier == "I24":
        return -(k2.T * first * k3)[0] * sp.trace(second * third)
    if carrier == "I25":
        return -((second * k3).T * first * (third * k2))[0]
    if carrier == "I28":
        return (k1.T * third * k2)[0] * (k3.T * first * second * k3)[0]
    if carrier == "I29":
        return -(k2.T * first * k2)[0] * (k3.T * second * k3)[0] * (k1.T * third * k1)[0]
    raise ValueError(carrier)


def unseen_residual_count(
    value: dict, mutate: bool = False, stop_on_first: bool = False
) -> int:
    projection = value["ordered_structure_projection"]
    symbols = {name: sp.Symbol(name, nonzero=True) for name in ("x1", "x2", "x3")}
    coordinate_rows = {
        3: [sp.sympify(item, locals=symbols) for item in projection["structure_3_coordinates"]],
        14: [sp.sympify(item, locals=symbols) for item in projection["structure_14_coordinates"]],
    }
    if mutate:
        coordinate_rows[3][0] += 1
    residuals = 0
    for first, second in UNSEEN_FIXTURES:
        momenta = [sp.Matrix(first), sp.Matrix(second)]
        momenta.append(-momenta[0] - momenta[1])
        boxes = {symbols[f"x{index + 1}"]: momentum.dot(momentum) for index, momentum in enumerate(momenta)}
        bases = [_transverse_traceless(momentum) for momentum in momenta]
        for choice in itertools.product(range(5), repeat=3):
            tensors = [bases[index][choice[index]] for index in range(3)]
            channels = [
                _carrier(row["carrier_id"], row["labels"], momenta, tensors)
                for row in projection["channels"]
            ]
            for structure in (3, 14):
                coordinates = [item.subs(boxes) for item in coordinate_rows[structure]]
                residual = _source(structure, momenta, tensors) - sum(
                    (coordinate * channel for coordinate, channel in zip(coordinates, channels)),
                    sp.S.Zero,
                )
                residuals += int(sp.factor(residual) != 0)
                if residuals and stop_on_first:
                    return residuals
    return residuals


def verify() -> dict:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("vector n=1+n=2 CPT projection certificate is stale")
    for name, path in DEPENDENCIES.items():
        reference = stored["dependencies"][name]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
    channels = stored["vector_n1_plus_n2_channel_integrands"]
    digest = hashlib.sha256(
        json.dumps(channels, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("channel formula digest drifted")
    if unseen_residual_count(stored) != 0:
        raise ValueError("unseen CPT carrier projection replay failed")
    if unseen_residual_count(stored, mutate=True, stop_on_first=True) == 0:
        raise ValueError("unseen replay failed to detect a coordinate mutation")
    if stored["minimal_missing_carrier_theorem"]["principal_symbol"] != "sigma_2(D_W)(p)=W^{mu nu} p_mu p_nu":
        raise ValueError("minimal missing-carrier theorem drifted")
    forbidden = (
        "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED",
        "COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED",
        "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    )
    if any(stored["claim_flags"][flag] for flag in forbidden):
        raise ValueError("vector CPT projection crossed its claim boundary")
    return stored


def main() -> int:
    verify()
    print("independent generic ghost vector n=1+n=2 CPT projection: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
