"""First exact obstruction to the polar ungauged cyclic BV residual descent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-polar-ungauged-bv-residual-descent-obstruction-v1.schema.json"
INPUTS = {
    "direct_polar_current": (ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json", "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1", "f411d2e62c4ffa7436966d11f7d77e4c91b85d4ffbaf220f04f816bd80ec0b71"),
    "polar_polynomial_square": (ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json", "EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION", "01ddd0a84f348d9c52a0e05812f6ceb27cb19d7fd2a6bc094eac2edfd7cedeaf"),
    "polar_ungauged_lift": (ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json", "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT", "3e49bc59330f35a5f382887d4e1d89c9750bec3283d1b80cfdfbc65af4a34733"),
    "generic_cyclic_obstruction": (ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json", "EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1", "49c0623114c5eee478463d58fcdc9a6e89b36e57a27aa66354b5a925a77bcc77"),
    "covariant_chain_map": (ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json", "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1", "50958aaae3339a1aa5a78d7be3d17d71a3754c06633783e9957e2df0a02eeec0"),
    "relative_branch_dictionary": (ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json", "EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1", "0489e3a15956b9e397387476cd76974f6083692a85bc840b34d81d7893bae5aa"),
    "background_stabilizer": (ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json", "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT", "7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8"),
    "exceptional_global_chain_maps": (ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json", "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1", "3d4b271bac82751c6b50e6da088dfcdf97ebe946a78c96f2dfe052103a060a0e"),
}


class PolarBVResidualDescentError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarBVResidualDescentError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generic_obstruction() -> dict[str, Any]:
    l = sp.symbols("lambda", positive=True)
    defect = sp.Matrix([[0, -3*l], [-sp.Rational(3, 2), 0]])
    square = (defect*defect).applyfunc(sp.factor)
    determinant = sp.factor(defect.det())
    _require(square == sp.Rational(9, 2)*l*sp.eye(2), "polar cyclic-defect square changed")
    _require(determinant == -sp.Rational(9, 2)*l, "polar cyclic-defect determinant changed")
    return {
        "relative_operator_R": [["1", "-3*lambda"], ["-3/2", "1"]],
        "cyclic_defect_D_equals_R_minus_I": [["0", "-3*lambda"], ["-3/2", "0"]],
        "D_squared": "9*lambda*I/2",
        "determinant_D": "-9*lambda/2",
        "rank_for_every_physical_lambda_ell_at_least_2": 2,
        "cohomology_pairing_identity": "iota^*Omega_WM-Omega_EM=Omega_EM(.,D .)",
        "necessary_condition": "a strict cyclic BV chain map with the fixed identity field inclusion and standard action pairings must induce a symplectic map on solution cohomology",
        "conclusion": "the nonzero nonradical D contradicts that necessary condition on every generic physical polar fibre",
    }


def _endpoint_ledger() -> list[dict[str, Any]]:
    return [
        {"scope": "generic polar", "ell": ">=2", "k": "all allowed including zero", "ungauged_chain": "CERTIFIED", "cyclic_identity_map": "OBSTRUCTED", "relative_operator": "R=[[1,-3*lambda],[-3/2,1]]", "residual_verdict": "stops before strict cyclic BV cofiber"},
        {"scope": "exceptional polar", "ell": 1, "k": "zero and nonzero separately", "ungauged_chain": "CERTIFIED", "cyclic_identity_map": "OBSTRUCTED", "relative_operator": "4*I on the physical standard quotient", "residual_verdict": "extra omega^2-k^2=4/3 cofiber remains pre-residual; no generic inference used"},
        {"scope": "polar nonzero Fourier", "ell": 0, "k": "nonzero", "ungauged_chain": "CERTIFIED", "cyclic_identity_map": "NOT_APPLICABLE_ON_SOLUTION_COHOMOLOGY", "relative_operator": "empty physical solution quotient", "residual_verdict": "no propagating class to descend"},
        {"scope": "homogeneous global", "ell": 0, "k": 0, "ungauged_chain": "CERTIFIED", "cyclic_identity_map": "OBSTRUCTED", "relative_operator": "I+N, N^2=0, rank(N)=2", "residual_verdict": "Q_e and W_x retained; solution cofiber zero but identity form is noncyclic"},
        {"scope": "axial twist endpoint", "ell": 1, "k": 0, "ungauged_chain": "CERTIFIED", "cyclic_identity_map": "OBSTRUCTED", "relative_operator": "-2*I on each position/velocity pair", "residual_verdict": "three physical holonomy pairs retained; not deleted as gauge"},
        {"scope": "finite U(1) winding", "ell": 0, "k": 0, "ungauged_chain": "NOT_APPLICABLE_TO_DISCRETE_ENDPOINT", "cyclic_identity_map": "NOT_APPLICABLE", "relative_operator": "W_x is a local real tangent with a periodic finite quotient", "residual_verdict": "large gauge identifies finite Wilson-line points discretely; it does not kill the tangent pair"},
        {"scope": "asymptotic or exterior boundary", "ell": "not applicable", "k": "not applicable", "ungauged_chain": "NO_CERTIFIED_MAP", "cyclic_identity_map": "NO_CERTIFIED_MAP", "relative_operator": "NO_CERTIFIED_MAP", "residual_verdict": "common boundary domain, fluxes, charges and causal Green carrier absent"},
    ]


def build_certificate() -> dict[str, Any]:
    records = {}
    for name, (path, result_id, digest) in INPUTS.items():
        record = json.loads(path.read_text(encoding="utf-8"))
        _require(record["result_id"] == result_id, f"{name} result ID changed")
        _require(_sha256(path) == digest, f"{name} hash changed")
        records[name] = record
    lift = records["polar_ungauged_lift"]
    _require(lift["classification"]["polynomial_ghost_field_equation_identity_chain_map_certified"], "ungauged chain map missing")
    _require(not lift["classification"]["cyclic_BV_chain_map_certified"], "unexpected cyclic promotion")
    stabilizer = records["background_stabilizer"]
    _require(stabilizer["residual_dispositions"]["stabilizers_gauged_in_an_absolute_CE_complex"] == "NOT_AUTHORIZED", "stabilizer quotient silently authorized")
    return {
        "schema": "einstein-maxwell-weyl-polar-ungauged-bv-residual-descent-obstruction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1",
        "result_state": "STRICT_IDENTITY_CYCLIC_BV_LIFT_OBSTRUCTED_BEFORE_FINAL_RESIDUAL_DESCENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": digest} for name, (path, result_id, digest) in INPUTS.items()},
        },
        "domain": "same compactified Plebanski-Hacyan Einstein-Maxwell/Weyl-Maxwell system, fixed magnetic bundle, all compact harmonic strata, local gauge quotient and global endpoints kept distinct",
        "certified_precursor": {
            "natural_support_local_all_row_chain_map": True,
            "polar_ghost_field_equation_identity_squares": "0",
            "source_and_target_nilpotency": True,
            "polynomial_zero_momentum_and_zero_frequency_retained": True,
            "direct_polar_current_immutable": True,
            "strict_standard_pairing_cyclic_map": False,
        },
        "first_exact_obstruction": _generic_obstruction(),
        "endpoint_ledger": _endpoint_ledger(),
        "global_residual_authority": {
            "connected_stabilizer": "R_t x U(1)_x x SO(3), five generators H,P_x,J_i",
            "Lee_Wald_invariance": "CERTIFIED",
            "universal_presymplectic_nullity": False,
            "nonzero_charge_witnesses": ["H on every nonzero p-shell vector", "P_x for k!=0", "J_0 for m!=0"],
            "absolute_stabilizer_gauge_quotient": "NOT_AUTHORIZED",
            "required_missing_carrier": "a declared common moment-map/Taub-zero derived sector with its induced quotient complex and pairing",
            "final_residual_cohomology_dimensions": "NO_CERTIFIED_MAP",
            "descended_pairing_and_radical": "NO_CERTIFIED_MAP",
        },
        "charge_and_large_gauge": {
            "magnetic_Chern_class": "fixed",
            "electric_tangent_Q_e": "retained unless a separately declared fixed-electric-charge fibre is imposed",
            "Wilson_line_W_x": "physical tangent coordinate; finite large U(1) winding makes the global coordinate periodic but does not gauge-delete its tangent",
            "twist_holonomies": "three position/velocity pairs retained before a separately declared finite moduli quotient",
        },
        "obstruction_scope": {
            "strict_fixed_identity_cyclic_BV_morphism": "OBSTRUCTED",
            "corrected_nonidentity_field_map": "OPEN",
            "cyclic_chain_homotopy": "OPEN",
            "pairing_changed_triangle": "CERTIFIED_NONCYCLIC_THREE_FORM_ONLY",
            "final_absolute_residual_descent": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "promote_strict_cyclic_map": "REJECTED",
            "gauge_all_five_stabilizers": "REJECTED by explicit nonzero moment-map witnesses",
            "delete_W_x_or_Q_e_as_local_gauge": "REJECTED by fixed-bundle/large-gauge endpoint ledger",
            "infer_ell_1_from_generic_lambda": "REJECTED; exceptional chain maps are imported independently",
        },
        "classification": {
            "ungauged_equation_Noether_chain_map_certified": True,
            "strict_identity_cyclic_BV_lift_exists": False,
            "first_exact_obstruction_nonradical": True,
            "exceptional_and_global_strata_separate": True,
            "large_gauge_and_charge_directions_preserved": True,
            "final_residual_descent_certified": False,
            "causal_particle_or_quantum_claim": False,
        },
        "claim_boundary": "This obstruction rules out a strict cyclic BV enhancement of the fixed identity Einstein inclusion with the standard action-derived pairings, and records why no absolute quotient by the charged background stabilizer is authorized. It does not obstruct corrected nonidentity maps or cyclic chain homotopies, compute a declared moment-map-zero derived quotient, or establish causal, observable, particle, positivity, unitarity or quantum claims.",
        "next_gate": "classify local polynomial corrected field maps or cyclic chain homotopies; independently construct the complete common moment-map-zero derived carrier before attempting final residual cohomology",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_bv_residual_descent --verify bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_ungauged_bv_residual_descent.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ungauged_bv_residual_descent",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True)+"\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
