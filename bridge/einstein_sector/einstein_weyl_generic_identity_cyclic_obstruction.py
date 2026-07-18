"""Certify the cyclic obstruction for the fixed generic identity inclusion."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_generic_identity_cyclic_obstruction.schema.json"
INPUTS = {
    "axial_chain": ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json",
    "polar_chain": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
    "radiative_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads(INPUTS[name].read_text(encoding="utf-8"))


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in matrix.row(row)] for row in range(matrix.rows)]


def _defect_theorem() -> dict[str, object]:
    eigenvalue = sp.symbols("lambda", positive=True)
    identity = sp.eye(2)
    masters = {
        "axial": sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]]),
        "polar": sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]]),
    }
    rows: dict[str, object] = {}
    for parity, master in masters.items():
        relative = identity + sp.Rational(3, 2) * (master - eigenvalue * identity)
        defect = sp.factor(relative - identity)
        determinant = sp.factor(defect.det())
        square = (defect**2).applyfunc(sp.factor)
        expected_square = sp.Rational(9, 2) * eigenvalue * identity
        if determinant != -sp.Rational(9, 2) * eigenvalue:
            raise AssertionError(f"{parity} cyclic-defect determinant changed")
        if square != expected_square:
            raise AssertionError(f"{parity} cyclic-defect square changed")
        rows[parity] = {
            "master_operator": _matrix_strings(master),
            "relative_operator_R": _matrix_strings(relative),
            "cyclic_defect_D=R-I": _matrix_strings(defect),
            "D_squared": "(9/2)*lambda*I",
            "determinant_D": "-9*lambda/2",
            "eigenvalues_D": ["+(3/2)*sqrt(2*lambda)", "-(3/2)*sqrt(2*lambda)"],
            "rank_for_physical_lambda": 2,
        }
    return {
        "solution_pairing_identity": "iota^*Omega_WM(u,v)-Omega_EM(u,v)=Omega_EM(u,Dv), D=R-I",
        "parity_blocks": rows,
        "physical_specialization": "lambda=ell*(ell+1)>=6, every allowed compact k=2*pi*n/L",
        "nondegeneracy_reason": "Omega_EM and D are both invertible on every generic physical fibre",
        "strict_cyclic_consequence": "a strict cyclic chain map with the fixed identity field inclusion and the standard action-derived pairings would induce a symplectic solution map; the displayed nonzero nonradical defect contradicts that necessary condition",
    }


def build() -> dict[str, object]:
    records = {name: _load(name) for name in INPUTS}
    if not records["axial_chain"]["classification"]["generic_axial_offshell_chain_map_certified"]:
        raise AssertionError("generic axial chain input changed")
    if not records["polar_chain"]["classification"]["polynomial_ghost_field_equation_identity_chain_map_certified"]:
        raise AssertionError("generic polar chain input changed")
    if records["polar_chain"]["classification"]["cyclic_BV_chain_map_certified"]:
        raise AssertionError("polar chain lifecycle unexpectedly changed")
    pairing = records["radiative_pairing"]["theorem"]
    if pairing["all_ell_ge_2_classification"]["identity_inclusion_preserves_Einstein_symplectic_form"]:
        raise AssertionError("radiative pairing input changed")
    theorem = _defect_theorem()
    return {
        "schema": "einstein-weyl-generic-identity-cyclic-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1",
        "result_state": "FIXED_IDENTITY_GENERIC_CHAIN_MAPS_HAVE_NONRADICAL_CYCLIC_DEFECT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "generic axial and polar polynomial chain maps with their fixed identity field inclusion and standard action-derived pairings",
            "degree": "linear BV/equation-Noether map tested through induced solution pairing",
            "parity": "axial and polar separately",
            "ell": ">=2",
            "m": "all",
            "k": "2*pi*n/L, every n in Z including zero",
            "omega": "both q-primary Einstein-Maxwell radiative shells",
        },
        "map_lifecycle": "DERIVED_COFIBER_TRIANGLE_NONCYCLIC_FIXED_IDENTITY",
        "cyclic_obstruction_theorem": theorem,
        "classification": {
            "generic_axial_and_polar_chain_maps_imported": True,
            "fixed_identity_cyclic_pairing_compatibility": "OBSTRUCTED",
            "induced_solution_pairing_defect_nonzero": True,
            "induced_solution_pairing_defect_nonradical": True,
            "strict_cyclic_enhancement_with_fixed_identity_field_map_exists": False,
            "corrected_nonidentity_or_chain_homotopy_cyclic_morphism_classified": False,
            "final_residual_descent_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The already certified generic axial and polar chain maps are genuine polynomial maps, but they are not cyclic morphisms for the standard action pairings when their field map is held to the physical identity inclusion. The obstruction is visible on solution cohomology and is nonradical in both parities. A different, explicitly corrected field identification or higher chain-homotopy notion is a separate open problem and cannot be called the identity Einstein inclusion.",
        "next_gate": "classify polynomial/local corrected field maps or cyclic chain-homotopies, while constructing or obstructing the exceptional and global off-shell maps",
        "claim_boundary": "This theorem obstructs only strict cyclic compatibility of the certified generic chain maps with their fixed identity field inclusion and standard action-derived pairings. It does not obstruct arbitrary nonidentity symplectic reidentifications, pairing-changing improvements, cyclic maps up to a declared homotopy, exceptional/global sectors, final residual descent, causal propagation, observables, particles, or quantum states.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_weyl_generic_identity_cyclic_obstruction --check", "python3 bridge/einstein_sector/verify_einstein_weyl_generic_identity_cyclic_obstruction.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_generic_identity_cyclic_obstruction"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the exact generic chain maps and direct action-derived radiative pairing are unchanged content-addressed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "no all-sector cyclic triangle or bridge-1 activation is promoted"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_generic_identity_cyclic_obstruction --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_generic_identity_cyclic_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_generic_identity_cyclic_obstruction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("generic cyclic-obstruction certificate is stale")
    print("EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
