"""Signed orbit-first generation for complete tensor contractions."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Iterable

from .tensors import TensorSpec


Pair = tuple[int, int]
Pairing = tuple[Pair, ...]


@dataclass(frozen=True)
class SignedPositionPermutation:
    """A slot action stored as ``new_position -> old_position``."""

    positions: tuple[int, ...]
    sign: int

    def __post_init__(self) -> None:
        if sorted(self.positions) != list(range(len(self.positions))):
            raise ValueError("positions must be a permutation")
        if self.sign not in (-1, 1):
            raise ValueError("signed position permutation requires sign +/-1")


@dataclass(frozen=True)
class PairingOrbit:
    canonical_pairing: Pairing
    members: tuple[Pairing, ...]
    signs_to_canonical: tuple[int, ...]
    vanishes: bool

    def __post_init__(self) -> None:
        if len(self.members) != len(self.signs_to_canonical):
            raise ValueError("each orbit member requires one canonical sign")
        if self.canonical_pairing != min(self.members):
            raise ValueError("orbit representative must be lexicographically canonical")
        if any(sign not in (-1, 0, 1) for sign in self.signs_to_canonical):
            raise ValueError("orbit signs must be -1, 0, or 1")
        if self.vanishes != all(sign == 0 for sign in self.signs_to_canonical):
            raise ValueError("vanishing orbit signs must all be zero")

    @property
    def size(self) -> int:
        return len(self.members)

    def sign_for(self, pairing: Pairing) -> int:
        try:
            return self.signs_to_canonical[self.members.index(pairing)]
        except ValueError as error:
            raise KeyError("pairing is outside this orbit") from error


def normalize_pairing(pairing: Iterable[Pair], slot_count: int) -> Pairing:
    """Validate and canonicalize a perfect matching of numbered slots."""

    normalized = tuple(sorted(tuple(sorted(pair)) for pair in pairing))
    if any(len(pair) != 2 or pair[0] == pair[1] for pair in normalized):
        raise ValueError("pairing entries must contain two distinct slots")
    if sorted(position for pair in normalized for position in pair) != list(
        range(slot_count)
    ):
        raise ValueError("pairing must cover every slot exactly once")
    return normalized


def identical_factor_group(
    spec: TensorSpec, factor_count: int
) -> tuple[SignedPositionPermutation, ...]:
    """Return the full signed slot/factor action for identical tensor factors."""

    if factor_count < 1:
        raise ValueError("factor count must be positive")
    actions: dict[tuple[int, ...], int] = {}
    intrinsic_choices = tuple(spec.intrinsic_symmetries)
    for choices in product(intrinsic_choices, repeat=factor_count):
        intrinsic_sign = 1
        for _, sign in choices:
            intrinsic_sign *= sign
        for order in permutations(range(factor_count)):
            inversions = sum(
                1
                for left in range(factor_count)
                for right in range(left + 1, factor_count)
                if order[left] > order[right]
            )
            koszul_sign = (
                -1 if spec.grassmann_parity and inversions % 2 else 1
            )
            positions: list[int] = []
            for old_factor in order:
                slot_permutation, _ = choices[old_factor]
                positions.extend(
                    old_factor * spec.rank + slot
                    for slot in slot_permutation
                )
            action = tuple(positions)
            sign = intrinsic_sign * koszul_sign
            previous = actions.get(action)
            if previous is not None and previous != sign:
                raise ValueError("factor action carries inconsistent signs")
            actions[action] = sign
    return tuple(
        SignedPositionPermutation(positions, sign)
        for positions, sign in sorted(actions.items())
    )


def transform_pairing(
    pairing: Pairing, action: SignedPositionPermutation
) -> Pairing:
    """Apply a ``new -> old`` slot action to a normalized pairing."""

    slot_count = len(action.positions)
    normalized = normalize_pairing(pairing, slot_count)
    old_to_new = [0] * slot_count
    for new, old in enumerate(action.positions):
        old_to_new[old] = new
    return normalize_pairing(
        ((old_to_new[left], old_to_new[right]) for left, right in normalized),
        slot_count,
    )


def signed_pairing_orbits(
    pairings: Iterable[Pairing],
    actions: Iterable[SignedPositionPermutation],
) -> tuple[PairingOrbit, ...]:
    """Partition perfect matchings into exact signed symmetry orbits."""

    action_tuple = tuple(actions)
    if not action_tuple:
        raise ValueError("at least one signed action is required")
    slot_count = len(action_tuple[0].positions)
    if any(len(action.positions) != slot_count for action in action_tuple):
        raise ValueError("all actions must use the same slot count")
    remaining = {
        normalize_pairing(pairing, slot_count) for pairing in pairings
    }
    orbits: list[PairingOrbit] = []
    while remaining:
        seed = min(remaining)
        signs_from_seed: dict[Pairing, set[int]] = {}
        for action in action_tuple:
            transformed = transform_pairing(seed, action)
            signs_from_seed.setdefault(transformed, set()).add(action.sign)
        members = tuple(sorted(signs_from_seed))
        if not set(members) <= remaining:
            overlap = set(members) - remaining
            raise AssertionError(
                f"signed actions do not form disjoint complete orbits: {len(overlap)} overlap"
            )
        vanishes = any(len(signs) > 1 for signs in signs_from_seed.values())
        if vanishes:
            signs_to_canonical = tuple(0 for _ in members)
        else:
            canonical_sign = next(iter(signs_from_seed[members[0]]))
            signs_to_canonical = tuple(
                canonical_sign * next(iter(signs_from_seed[member]))
                for member in members
            )
        orbits.append(
            PairingOrbit(
                members[0], members, signs_to_canonical, vanishes
            )
        )
        remaining.difference_update(members)
    return tuple(orbits)
