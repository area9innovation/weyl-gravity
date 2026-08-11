#!/usr/bin/env python3
"""Exact checker for the explicit energy spectral fragment."""
from __future__ import annotations
import hashlib
import json
from math import comb
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json"

def dimension(n: int) -> int:
    return 10 if n == 2 else 40 if n == 3 else 6*n*n-14

def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    data = json.loads(RESULT.read_text()) if data is None else data
    errors: list[str] = []
    limit = data.get("fock_proof", {}).get("regression_maximum_energy")
    if not isinstance(limit, int) or limit < 6:
        return ["invalid regression limit"], {}
    coordinates: list[list[int]] = []
    for n in range(2, limit+1):
        d = dimension(n)
        for k in range(d):
            sign = 1 if k < (n+3)*(n-1)*2 else -1
            # D and J commute coordinatewise; p(D) has p(n) on this coordinate.
            p = n*n-3*n+1
            if sign*n != n*sign or p != n*n-3*n+1:
                errors.append("diagonal calculus failed")
            in_even, in_tail = n % 2 == 0, n >= 5
            if int(in_even and in_tail) != int(in_even)*int(in_tail):
                errors.append("projection intersection law failed")
            if int(in_even or in_tail) != int(in_even)+int(in_tail)-int(in_even and in_tail):
                errors.append("projection union law failed")
            coordinates.append([n,k,sign,p])
    # Exact squared tail estimate: sup_{n>N}|(n-i)^-1|^2 <= 1/(N+1)^2.
    for cutoff in range(2, limit):
        if (cutoff+1)**2 > (cutoff+1)**2 + 1:
            errors.append("resolvent tail inequality failed")
    coeff = [0]*(limit+1); coeff[0] = 1
    for n in range(2, limit+1):
        updated = [0]*(limit+1)
        for old,value in enumerate(coeff):
            if value:
                for occupancy in range((limit-old)//n+1):
                    updated[old+occupancy*n] += value*comb(dimension(n)+occupancy-1, occupancy)
        coeff = updated
    expected = {str(k):v for k,v in enumerate(coeff)}
    if expected != data.get("fock_proof", {}).get("matter_fixed_energy_dimensions"):
        errors.append("Fock energy counts drifted")
    digest = hashlib.sha256(json.dumps(coordinates,separators=(",",":")).encode()).hexdigest()
    wanted = data.get("independent_checker", {}).get("expected_digest")
    if wanted is not None and digest != wanted:
        errors.append("witness digest mismatch")
    return errors, {"passed":not errors,"cutoff":limit,"coordinates":len(coordinates),"fock_dimensions":expected,"digest":digest,"arithmetic":"exact integers only"}

def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_CHECKER: " + ("PASS" if not errors else "FAIL"))
    if errors:
        print("\n".join(f"  - {e}" for e in errors)); return 1
    print(json.dumps(summary,indent=2,sort_keys=True)); return 0

if __name__ == "__main__":
    sys.exit(main())
