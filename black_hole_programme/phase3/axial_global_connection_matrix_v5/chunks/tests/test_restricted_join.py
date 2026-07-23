from __future__ import annotations

import struct
import unittest
from fractions import Fraction

from ..restrict_join import SCALE, SUBCELLS, _restrict_matrix


ZERO = "0000000000000000"


def _bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def parent_matrix() -> dict:
    center = [["0/1" for _ in range(12)] for _ in range(12)]
    linear = [["0/1" for _ in range(12)] for _ in range(12)]
    remainder = [[[ZERO, ZERO] for _ in range(12)] for _ in range(12)]
    hull = [[[_bits(0.0), _bits(0.0)] for _ in range(12)] for _ in range(12)]
    center[0][0], linear[0][0] = "2/1", "1/1"
    hull[0][0] = [_bits(1.0), _bits(3.0)]
    return {
        "center": center, "linear": linear,
        "remainder": remainder, "hull": hull,
    }


class RestrictedJoinTests(unittest.TestCase):
    def test_frozen_cover_and_normalized_restriction(self) -> None:
        self.assertEqual(SCALE, Fraction(1, 4))
        self.assertEqual(SUBCELLS[0][5], Fraction(-3, 4))
        self.assertEqual(SUBCELLS[-1][5], Fraction(3, 4))
        restricted = _restrict_matrix(parent_matrix(), Fraction(-3, 4))
        self.assertEqual(restricted["center"][0][0], "5/4")
        self.assertEqual(restricted["linear"][0][0], "1/4")
        lo, hi = (
            struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]
            for bits in restricted["hull"][0][0]
        )
        self.assertLessEqual(lo, 1.0)
        self.assertGreaterEqual(hi, 1.5)

    def test_remainder_is_retained(self) -> None:
        parent = parent_matrix()
        parent["remainder"][3][4] = [_bits(-0.25), _bits(0.5)]
        restricted = _restrict_matrix(parent, Fraction(1, 4))
        self.assertEqual(
            restricted["remainder"][3][4], parent["remainder"][3][4]
        )


if __name__ == "__main__":
    unittest.main()
