#!/usr/bin/env python3
"""Independent verifier for the outgoing frame completion preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(data: dict) -> None:
    if data["schema"] != "phase3-axial-partial-jet-outgoing-frame-completion-v1":
        raise AssertionError("schema drift")
    for item in data["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise AssertionError(f"import drift: {path}")
    omega = sp.Symbol("omega", nonzero=True)
    I = sp.I
    pi2 = 2 * (16 * omega**2 - 4 * I * omega - 5)
    pi3 = -2 * I * omega
    r = pi2 - I * (16 * omega**2 - 4 * I * omega - 5) * pi3 / omega
    s = I * pi3 / (2 * omega)
    if sp.factor(r) != 0 or sp.factor(s) != 1:
        raise AssertionError("factor quotient normalization failed")
    columns = data["normalized_columns"]
    if list(columns) != ["E", "R", "S"]:
        raise AssertionError("typed outgoing order drift")
    if (
        columns["E"]["line"] != "2*EI2"
        or columns["R"]["line"]
        != "XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega"
        or columns["S"]["line"] != "I*XI3/(2*omega)"
    ):
        raise AssertionError("typed outgoing lines drift")
    flags = data["claim_flags"]
    if not (
        flags["formal_E_R_S_columns_constructed"]
        and flags["E_all_order_remainder_certified"]
        and flags["R_all_order_remainder_certified"]
        and flags["S_six_state_all_order_existence_certified"]
        and flags["formal_K_plus_zero_in_canonical_gauge"]
    ):
        raise AssertionError("proved endpoint flags were demoted")
    for forbidden in (
        "S_correlated_dual_remainder_certified",
        "validated_analytic_K_plus_certified",
        "all_three_correlated_outgoing_columns_certified",
        "T_plus_certified",
        "scattering_or_flux_certified",
    ):
        if flags[forbidden]:
            raise AssertionError(f"fail-closed flag promoted: {forbidden}")
    if data["formal_endpoint_jet"]["K_plus_canonical_formal"] != [
        ["0", "0"], ["0", "0"]
    ]:
        raise AssertionError("formal K_plus drift")


def main() -> None:
    verify(json.loads(CERTIFICATE.read_text()))
    print("PASS independent outgoing frame completion preflight")


if __name__ == "__main__":
    main()
