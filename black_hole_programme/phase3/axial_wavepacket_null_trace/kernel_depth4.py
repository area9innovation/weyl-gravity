"""Exact one-order repair of the two Einstein-kernel infinity heads."""
from __future__ import annotations

import sympy as sp


def build_kernel_heads() -> dict:
    w = sp.Symbol("omega", positive=True)
    I = sp.I
    ei0_a4 = -45*(w - 2*I)/(8*w**3)
    ei2_a4 = (
        4096*w**7 - 10240*I*w**6 - 14080*w**5 + 10496*I*w**4
        + 5920*w**3 - 2016*I*w**2 - 531*w + 90*I
    )/(24*w**3)
    raw = {
        "EI0": {
            "rate": 0,
            "H1_power": 0,
            "H1": [1, 0, (3*I*w + 6)/(2*w**2), 0, ei0_a4],
        },
        "EI2": {
            "rate": -2*I*w,
            "H1_power": 1 - 4*I*w,
            "H1": [
                1,
                (16*I*w**2 + 4*w - 5*I)/(2*w),
                (-64*w**4 + 48*I*w**3 + 48*w**2 - 9*I*w - 6)/(2*w**2),
                (-1024*I*w**6 - 1536*w**5 + 1664*I*w**4
                 + 768*w**3 - 396*I*w**2 - 63*w + 18*I)/(12*w**3),
                ei2_a4,
            ],
        },
    }
    answer = {}
    for label, item in raw.items():
        rate = item["rate"]
        power = item["H1_power"]
        h1 = item["H1"]
        if rate == 0:
            # F is normalized with one lower radial power than H1.
            derivative = [(power - n)*value for n, value in enumerate(h1)]
        else:
            derivative = [rate*h1[0]]
            derivative.extend(
                rate*h1[n] + (power - n + 1)*h1[n - 1]
                for n in range(1, len(h1))
            )
            derivative.append((power - 4)*h1[4])
        answer[label] = {
            "rate": sp.sstr(rate),
            "H1_power": sp.sstr(power),
            "H1": [sp.sstr(sp.cancel(value)) for value in h1],
            "F": [sp.sstr(sp.cancel(value)) for value in derivative],
            "F_power": sp.sstr(power if rate != 0 else power - 1),
            "raw_residual_valuation": 6,
            "forced_log_coefficient": "0",
        }
    return answer
