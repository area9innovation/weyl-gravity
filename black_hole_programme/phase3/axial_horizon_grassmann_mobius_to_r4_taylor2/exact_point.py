#!/usr/bin/env python3
"""Regenerate the point plane at exact omega0 with zero frequency radius."""
from __future__ import annotations

import hashlib
from fractions import Fraction

from . import point

OUTPUT = point.plane.produce.HERE / "plane_point_exact_4097_8192.forge"
OMEGA0 = Fraction(4097, 8192)


def exact_builders() -> str:
    affine = point.plane.produce.affine
    rho, omega, flow, _, _ = affine.exact_inputs()
    initial = affine.child_initializer_model((OMEGA0, OMEGA0))
    lines = affine.base_producer.render_taylor_matrix(
        "hc_initial_model", initial
    )
    lines += affine.base_producer.render_runtime_taylor_builder(
        "hc_runtime", flow, rho, omega, OMEGA0, Fraction(0)
    )
    return "\n".join(lines) + "\n"


def render() -> str:
    source = point.render()
    start = "fn hc_initial_model_center()"
    end = "fn hr_i(chart:i64,k:i64)"
    if start not in source or end not in source:
        raise RuntimeError("quick-point builder boundaries missing")
    before, rest = source.split(start, 1)
    _, after = rest.split(end, 1)
    source = before + exact_builders() + end + after
    return source.replace(
        "quick-whole-cell-remainder", "exact-zero-frequency-radius"
    )


def main() -> None:
    source = render()
    OUTPUT.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())


if __name__ == "__main__":
    main()
