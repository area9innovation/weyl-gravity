from __future__ import annotations

import struct
import unittest

from ..emit_join import JoinTraceError, parse_join_trace


ZERO = "0"
ONE = str(struct.unpack(">Q", struct.pack(">d", 1.0))[0])


def trace() -> str:
    lines = [
        "BEGIN JOIN",
        "LAYOUT contiguous-block-lower-v1",
        "WIDTH 0.1 0.2 0.3",
        "RESULT 12 0.3",
    ]
    for i in range(12):
        for j in range(12):
            center = "1/1" if i == j else "0/1"
            hull = ONE if i == j else ZERO
            lines.append(
                f"A {i} {j} {center} 0/1 {ZERO} {ZERO} {hull} {hull}"
            )
    lines.append("END JOIN")
    return "\n".join(lines)


class JoinTraceTests(unittest.TestCase):
    def test_valid_trace(self) -> None:
        matrix, widths = parse_join_trace(trace())
        self.assertEqual(matrix["center"][0][0], "1/1")
        self.assertEqual(widths, {
            "carrier": "0.1", "lower": "0.2", "kernel": "0.3",
        })

    def test_truncated_trace_refuses(self) -> None:
        with self.assertRaises(JoinTraceError):
            parse_join_trace(trace().removesuffix("END JOIN"))

    def test_nonfinite_width_refuses(self) -> None:
        with self.assertRaises(JoinTraceError):
            parse_join_trace(trace().replace("WIDTH 0.1", "WIDTH nan"))

    def test_nonzero_upper_right_refuses(self) -> None:
        bad = trace().replace(
            f"A 0 8 0/1 0/1 {ZERO} {ZERO} {ZERO} {ZERO}",
            f"A 0 8 1/1 0/1 {ZERO} {ZERO} {ONE} {ONE}",
        )
        with self.assertRaises(JoinTraceError):
            parse_join_trace(bad)


if __name__ == "__main__":
    unittest.main()
