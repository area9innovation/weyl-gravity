#!/usr/bin/env python3
"""Render a less restrictive exact-point horizon carrier-plane probe.

The producer owned by ``axial_horizon_grassmann_mobius_to_r4_taylor2``
originally rejected every chart whose graph coordinate had max norm at
least two.  That is a conditioning preference, not a Grassmann-chart
validity condition.  This probe removes only that artificial cutoff and
adds progressively finer panel fallbacks.  It does not alter or claim the
upstream horizon initializer.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from ...axial_horizon_grassmann_mobius_to_r4_taylor2 import carrier_point


class HorizonCarrierProbeError(RuntimeError):
    """Raised when the frozen upstream source no longer matches this adapter."""


OLD_FALLBACK = r'''    let used:i64=64;let a:CpAttempt=cp_attempt(shell,64,cell,state);
    if(!a.ok){used=128;println(strfmt(system_allocator(),
      "CARRIER_FALLBACK shell={} panels=128",[shell]));
      a=cp_attempt(shell,128,cell,state);}
    if(!a.ok){println(strfmt(system_allocator(),
      "CARRIER_REFUSE shell={} after-fallback=128",[shell]));return 3;}'''

NEW_FALLBACK = r'''    let used:i64=256;let a:CpAttempt=cp_attempt(shell,256,cell,state);
    if(!a.ok){used=512;println(strfmt(system_allocator(),
      "CARRIER_FALLBACK shell={} panels=512",[shell]));
      a=cp_attempt(shell,512,cell,state);}
    if(!a.ok){used=1024;println(strfmt(system_allocator(),
      "CARRIER_FALLBACK shell={} panels=1024",[shell]));
      a=cp_attempt(shell,1024,cell,state);}
    if(!a.ok){println(strfmt(system_allocator(),
      "CARRIER_REFUSE shell={} after-fallback=1024",[shell]));return 3;}'''


def render() -> str:
    """Return the exact-point probe source after two checked adaptations."""
    source = carrier_point.render()
    cutoff = "if(!z.ok || cp_norm(z.value)>=2.0){return cp_fail();}"
    if source.count(cutoff) != 2:
        raise HorizonCarrierProbeError(
            "expected exactly two artificial chart-norm cutoffs"
        )
    source = source.replace(
        cutoff, "if(!z.ok){return cp_fail();}"
    )
    if source.count(OLD_FALLBACK) != 1:
        raise HorizonCarrierProbeError(
            "upstream horizon carrier fallback block drifted"
        )
    return source.replace(OLD_FALLBACK, NEW_FALLBACK)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)
    print(hashlib.sha256(source.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
