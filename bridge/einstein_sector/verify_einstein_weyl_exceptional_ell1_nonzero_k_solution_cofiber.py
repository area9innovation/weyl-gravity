#!/usr/bin/env python3
"""Independent replay of the nonzero-k exceptional solution cofiber."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-exceptional-ell1-nonzero-k-solution-cofiber-v1.schema.json"
MANIFEST_PATHS = {
    "generator": ROOT / "bridge/einstein_sector/einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber.py",
    "schema": SCHEMA,
    "verifier": Path(__file__),
    "test": ROOT / "bridge/einstein_sector/tests/test_einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber.py",
    "report": ROOT / "bridge/einstein_sector/reports/einstein-weyl-exceptional-ell1-nonzero-k-solution-cofiber.md",
    "input_offshell_maps": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "input_direct_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
    "input_source_exceptional": ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
    "input_k0_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "input_exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "input_physical_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "engine_axial_current": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_axial_lee_wald_completion.py",
    "engine_polar_current": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_lee_wald_gate.py",
}


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"stale dependency {name}: {path}")
    for name, path in MANIFEST_PATHS.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if value["source_manifest"].get(name) != digest:
            raise AssertionError(f"stale source-manifest entry {name}: {path}")

    k, omega, spectral = sp.symbols("k omega s", real=True)
    parse = lambda expression: sp.sympify(expression, locals={"k": k, "omega": omega, "s": spectral})
    theorem = value["theorem"]
    shells = {name: parse(expression) for name, expression in theorem["shells"].items()}
    for projector_name, expression in theorem["projectors"].items():
        projector = parse(expression)
        for shell_name, shell in shells.items():
            if sp.factor(projector.subs(spectral, shell) - int(projector_name == shell_name)) != 0:
                raise AssertionError(f"projector {projector_name} failed on {shell_name}")

    expected_gram = {
        "axial": {"standard": "4*(k**2 + 4)", "extra": "4*(3*k**2 + 4)"},
        "polar": {"standard": "4", "extra": "4*(3*k**2 + 4)"},
    }
    if theorem["action_pairing"]["Gram"] != expected_gram:
        raise AssertionError("all-k exceptional Gram changed")
    if theorem["action_pairing"]["standard_extra_mixed"] != {"axial": "0", "polar": "0"}:
        raise AssertionError("standard-extra orthogonality changed")
    if theorem["inclusion_relations"]["polar_relation_remainder"] != ["0", "0", "0", "0"]:
        raise AssertionError("polar source-to-target quotient relation changed")
    flags = value["classification"]
    if not flags["nonzero_k_exceptional_solution_cofiber_certified"]:
        raise AssertionError("cofiber was not promoted")
    if flags["single_covariant_support_local_map_reconstructed"] or flags["finite_residual_endpoint_descent_certified"]:
        raise AssertionError("nonzero-k certificate over-promoted its scope")
    print("EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
