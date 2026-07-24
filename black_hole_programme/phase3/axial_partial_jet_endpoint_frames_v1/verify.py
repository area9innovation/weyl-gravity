#!/usr/bin/env python3
"""Method-distinct verifier for the endpoint partial-jet frame audit."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import sympy as sp

from .produce import HERE, INPUTS, OUTPUT, ROOT, clean, parse, w


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "phase3-axial-partial-jet-endpoint-frames-v1":
        errors.append("schema drift")
    if doc.get("status") != "EXACT_ENDPOINT_FACTOR_COMPATIBILITY_K_SHEARS_OPEN":
        errors.append("status promotion or drift")
    if doc.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency tag drift")
    for name, expected in INPUTS.items():
        item = doc.get("imports", {}).get(name, {})
        path = ROOT / item.get("path", "")
        if path.resolve() != expected.resolve() or not path.is_file():
            errors.append(f"import path drift: {name}")
        elif item.get("sha256") != sha256(path):
            errors.append(f"import hash drift: {name}")

    frames = doc.get("endpoint_frames", {})
    expected = {
        "H": [
            sp.I*w*(4*w-sp.I)/(2*(w-sp.I)),
            4*(w-sp.I)*(2*w-sp.I),
            -sp.I*w*(4*w-sp.I)/(4*(w-sp.I)),
        ],
        "Iminus": [1, -2*sp.I*w, -sp.I*w],
        "Iplus": [1, -2*sp.I*w, sp.Rational(1, 2)],
    }
    for endpoint, values in expected.items():
        got = frames.get(endpoint, {}).get("scalar_amplitudes_R_S_E", [])
        if len(got) != 3 or any(clean(parse(x)-y) != 0 for x, y in zip(got, values)):
            errors.append(f"{endpoint} scalar amplitude drift")
    plusq = frames.get("Iplus", {}).get("spin_one_quotient_amplitudes_XI2_XI3", [])
    if len(plusq) != 2 or clean(parse(plusq[0])-2*(16*w**2-4*sp.I*w-5)) != 0 or clean(parse(plusq[1])+2*sp.I*w) != 0:
        errors.append("Iplus quotient drift")

    order = doc.get("common_order", {})
    perm = sp.Matrix([[parse(x) for x in row] for row in order.get("right_column_permutation", [])])
    if perm.shape != (3, 3) or perm.det() != 1 or list(perm*sp.Matrix(sp.symbols("R S E"))) != [sp.Symbol("S"), sp.Symbol("E"), sp.Symbol("R")]:
        # Its action is less informative than its columns; verify columns below.
        if perm.shape != (3, 3) or perm != sp.Matrix([[0,1,0],[0,0,1],[1,0,0]]):
            errors.append("permutation drift")

    dual = doc.get("dual_number_solution", {})
    a, b, c, d, f = sp.symbols("a b c d f")
    inv1 = sp.Matrix([[parse(x) for x in row] for row in dual.get("inverse_tangent", [])])
    expected_inv1 = sp.Matrix([[-b/a**2, (b*d-a*c)/(a**2*f)], [0,0]])
    if inv1.shape != (2,2) or any(clean(x) != 0 for x in inv1-expected_inv1):
        errors.append("dual inverse tangent drift")
    if not dual.get("spin_one_normalization_frozen"):
        errors.append("spin-one normalization unfrozen")

    law = doc.get("endpoint_frame_derivative_law", {})
    if law.get("K_allowed_shape") != [["k_2", "h"], ["0", "0"]]:
        errors.append("K shape drift")
    for key in ("K_H_computed", "K_Iminus_computed", "K_Iplus_computed", "moving_exponent_derivatives_computed"):
        if law.get(key) is not False:
            errors.append(f"unsupported K promotion: {key}")
    if law.get("repeated_entry_law") != "b_tilde=b+a*(k_2_H-k_2_I)":
        errors.append("repeated-entry law drift")

    flags = doc.get("claim_flags", {})
    for key in ("analytic_tau_endpoint_family_constructed", "moving_exponent_derivatives_computed", "K_shears_computed", "endpoint_partial_jet_frames_constructed", "T_plus_recovered", "scattering_claim"):
        if flags.get(key) is not False:
            errors.append(f"open claim promoted: {key}")
    for key in ("exact_H_factor_lines", "exact_Iminus_factor_lines", "exact_Iplus_factor_lines", "exact_rescalings_and_permutation", "all_imported_endpoint_recurrences_audited", "dual_number_inverse_and_functoriality", "spin_one_normalization_frozen", "epsilon_copy_identified"):
        if flags.get(key) is not True:
            errors.append(f"proved gate demoted: {key}")
    if not doc.get("shortfall", {}).get("exact"):
        errors.append("exact shortfall removed")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(OUTPUT.read_text()))


if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("verified=true endpoint_factor_compatibility=true K_shears_open=true T_plus=false")
