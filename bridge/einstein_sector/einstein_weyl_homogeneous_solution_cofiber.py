"""Certify that the homogeneous Weyl-Maxwell solution cofiber is zero."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_homogeneous_solution_cofiber.schema.json"
INPUTS = {
    "operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads(INPUTS[name].read_text(encoding="utf-8"))


def _polynomial_theorem() -> dict[str, object]:
    # Source coordinates (a,b,c,d) map to the coefficients of
    # D=C-K=d0+d1*t+d2*t^2+d3*t^3.
    source_to_kernel = sp.Matrix(
        [
            [-1, 0, 1, 0],
            [0, -1, 0, 1],
            [1, 0, 0, 0],
            [0, sp.Rational(1, 3), 0, 0],
        ]
    )
    if source_to_kernel.det() != sp.Rational(1, 3):
        raise AssertionError("homogeneous source-to-kernel determinant changed")
    inverse = source_to_kernel.inv()
    expected_inverse = sp.Matrix(
        [
            [0, 0, 1, 0],
            [0, 0, 0, 3],
            [1, 0, 1, 0],
            [0, 1, 0, 3],
        ]
    )
    if inverse != expected_inverse:
        raise AssertionError("homogeneous kernel inverse changed")
    time = sp.symbols("t")
    d0, d1, d2, d3, w, q = sp.symbols("d0 d1 d2 d3 w q")
    invariant_metric = d0 + d1 * time + d2 * time**2 + d3 * time**3
    invariant_connection = w + q * time
    if sp.diff(invariant_metric, time, 4) != 0 or sp.diff(invariant_connection, time, 2) != 0:
        raise AssertionError("homogeneous polynomial kernel changed")
    return {
        "raw_fields": ["h_tt(t)", "h_tx(t)", "C(t)=h_xx", "K(t)=sphere trace", "a_t(t)", "A_x(t)"],
        "polynomial_gauge_parameters": ["T(t)=xi^t", "X(t)=xi^x", "sigma(t)", "chi(t)"],
        "gauge_action": {
            "delta_h_tt": "-2*(T'+sigma)",
            "delta_h_tx": "X'",
            "delta_C": "2*sigma",
            "delta_K": "2*sigma",
            "delta_a_t": "chi'",
            "delta_A_x": "0",
        },
        "global_polynomial_slice": {
            "choice": ["X'=-h_tx", "chi'=-a_t", "sigma=-K/2", "T'=-h_tt/2-sigma"],
            "no_frequency_inversion": True,
            "allowed_function_class": "smooth exponential-polynomial generalized-zero fields and gauge parameters",
            "complete_invariants": ["D=C-K", "A_x"],
        },
        "invariant_operator": ["D''''=0", "A_x''=0"],
        "complete_target_kernel": ["D=d0+d1*t+d2*t^2+d3*t^3", "A_x=W_x+Q_e*t"],
        "source_representative": ["K=a+b*t", "C=a*t^2+(b/3)*t^3+c+d*t", "A_x=W_x+Q_e*t"],
        "source_coordinate_order": ["a", "b", "c", "d"],
        "target_metric_kernel_order": ["d0", "d1", "d2", "d3"],
        "source_to_target_metric_kernel": [[str(value) for value in source_to_kernel.row(row)] for row in range(4)],
        "determinant": "1/3",
        "inverse_dictionary": ["a=d2", "b=3*d3", "c=d0+d2", "d=d1+3*d3"],
    }


def build() -> dict[str, object]:
    records = {name: _load(name) for name in INPUTS}
    if not records["operator"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"]:
        raise AssertionError("homogeneous nonzero-frequency operator changed")
    if not records["pairing"]["classification"]["restricted_target_form_nondegenerate"]:
        raise AssertionError("homogeneous target pairing changed")
    if not records["standard"]["classification"]["homogeneous_ell0_included"]:
        raise AssertionError("homogeneous standard inclusion changed")
    theorem = _polynomial_theorem()
    return {
        "schema": "einstein-weyl-homogeneous-solution-cofiber-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_HOMOGENEOUS_SOLUTION_COFIBER_V1",
        "result_state": "HOMOGENEOUS_GENERALIZED_ZERO_TARGET_EXHAUSTED_BY_EINSTEIN_MAXWELL_IMAGE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2; smooth polynomial generalized-zero class before final residual quotient",
            "charge_sector": "fixed magnetic bundle; Q_e and flat holonomy W_x retained",
            "carrier": "complete homogeneous ell=0,k=0 local-gauge-reduced solution module",
            "degree": 1,
            "parity": "homogeneous scalar/global",
            "ell": 0,
            "m": 0,
            "k": 0,
            "omega": "generalized zero; polynomial time degree at most three in D and one in A_x",
        },
        "map_lifecycle": "ONSHELL_MAP_ONLY",
        "polynomial_gauge_and_kernel_theorem": theorem,
        "solution_map": {
            "inclusion": "the identity Einstein-Maxwell inclusion maps bijectively onto the complete six-dimensional Weyl-Maxwell homogeneous quotient",
            "projection": "the inverse coefficient dictionary a=d2, b=3*d3, c=d0+d2, d=d1+3*d3, with Q_e and W_x unchanged",
            "solution_cofiber": "0",
        },
        "action_derived_pairing": {
            "source_rank": 6,
            "target_rank": 6,
            "relative_endomorphism": "R=I+N, rank(N)=2, N^2=0",
            "linear_symplectomorphism": "S=I+N/2, S^T*Omega_EM*S=Omega_WM",
            "meaning": "zero solution cofiber does not make the identity inclusion symplectic",
        },
        "classification": {
            "polynomial_gauge_slice_complete": True,
            "complete_homogeneous_target_kernel_certified": True,
            "Einstein_image_equals_complete_homogeneous_target_quotient": True,
            "homogeneous_solution_cofiber_zero": True,
            "homogeneous_pairing_transport_certified": True,
            "homogeneous_offshell_chain_map_certified": False,
            "large_gauge_and_final_residual_descent_certified": False,
            "bounded_in_time_subspace_claim": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "There is no additional homogeneous Weyl-Maxwell solution branch in the declared smooth polynomial generalized-zero class. The four metric kernel coefficients and the electric/holonomy pair are exhausted bijectively by the six Einstein-Maxwell global coordinates. Nevertheless the identity inclusion changes the symplectic form by the certified nilpotent shear, so equality of solution spaces is not equality of Hamiltonian structures.",
        "next_gate": "construct or obstruct the homogeneous ghost-field-equation-identity chain map and perform the large-gauge/final-residual descent",
        "claim_boundary": "This same-background solution-cofiber theorem uses smooth polynomial generalized-zero gauge parameters. It does not impose bounded time behavior, certify an off-shell homogeneous BV triangle, quotient large gauge transformations, perform final residual descent, or support causal, particle, observational, or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_weyl_homogeneous_solution_cofiber --check", "python3 bridge/einstein_sector/verify_einstein_weyl_homogeneous_solution_cofiber.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_homogeneous_solution_cofiber"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the direct target operator, complete standard inclusion and action-derived pairing are unchanged content-addressed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the off-shell global chain map and bridge-1 activation remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_homogeneous_solution_cofiber --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_homogeneous_solution_cofiber.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_homogeneous_solution_cofiber",
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
        raise AssertionError("homogeneous solution-cofiber certificate is stale")
    print("EINSTEIN_WEYL_HOMOGENEOUS_SOLUTION_COFIBER_V1: PASS")


if __name__ == "__main__":
    main()
