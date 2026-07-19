#!/usr/bin/env python3
"""Certify the relative observable pullback and reduced cofiber detectors."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/relative-residual-observable-functor-v1.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-residual-observable-functor-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_relative_residual_observable_functor.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_relative_residual_observable_functor.py"

DEPENDENCIES = {
    "preflight": ROOT / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1.json",
    "linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "triangle_components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "generic_axial": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "generic_polar": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "exceptional_k0": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "current_cofiber_assembly": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    preflight = values["preflight"]
    triangle = values["linear_triangle"]
    components = values["triangle_components"]
    axial = values["generic_axial"]
    polar = values["generic_polar"]
    k0 = values["exceptional_k0"]
    knz = values["exceptional_nonzero_k"]
    homogeneous = values["homogeneous"]
    twist = values["twist"]
    assembly = values["current_cofiber_assembly"]

    if preflight["flags"]["EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED"] is not True:
        raise AssertionError("linear triangle preflight is not ready")
    for flag in ("OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS", "SUPPORT_LOCAL_MAPPING_COFIBER", "H_PRODUCT_EQUIVARIANT", "GLOBAL_ENDPOINTS_INCLUDED"):
        if triangle["acceptance_flags"][flag] is not True:
            raise AssertionError(f"triangle flag missing: {flag}")
    if components["equivariance"]["certified"] is not True or components["mapping_cofiber"]["square_zero"] is not True:
        raise AssertionError("equivariant cofiber import drifted")
    if axial["classification"]["Einstein_extra_symplectic_orthogonality"] is not True:
        raise AssertionError("generic axial detector orthogonality is absent")
    if axial["classification"]["generic_extra_module_direct_Lee_Wald_nonradical"] is not True:
        raise AssertionError("generic axial detector Gram is degenerate")
    if polar["classification"]["Einstein_extra_orthogonality"] is not True or polar["classification"]["extra_block_nonradical"] is not True:
        raise AssertionError("generic polar detector data are absent")
    if k0["classification"]["cofiber_action_pairing_nonradical"] is not True:
        raise AssertionError("exceptional k=0 detector data are absent")
    if knz["classification"]["standard_extra_action_orthogonality"] is not True or knz["classification"]["action_pairing_nonradical_positive_on_extra_cofiber"] is not True:
        raise AssertionError("exceptional nonzero-k detector data are absent")
    if homogeneous["classification"]["homogeneous_solution_cofiber_zero"] is not True:
        raise AssertionError("homogeneous cofiber disposition drifted")
    if twist["classification"]["twist_solution_cofiber_zero"] is not True:
        raise AssertionError("twist cofiber disposition drifted")
    if components["global_endpoints"]["cone_cohomology_dimension"] != 0:
        raise AssertionError("endpoint cofiber unexpectedly survives")
    if assembly["classification"]["full_relative_arity_two_morphism_constructed"] is not False:
        raise AssertionError("linear observable functor imported a false nonlinear morphism")

    return {
        "schema": "pure-weyl-relative-residual-observable-functor-v1",
        "result_id": RESULT_ID,
        "result_state": "LINEAR_OBSERVABLE_PULLBACK_AND_RELATIVE_COFIBER_DETECTORS_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "closed S1_L x S2, fixed Chern class N=2, before the final residual quotient",
            "charge_sector": "fixed magnetic bundle with electric tangent and flat S1 holonomy retained",
            "carrier": "complete minimal all-row linear triangle and its support-local mapping cofiber",
            "degree": "linear BRST observable DGA and solution-cohomology coefficient observables",
            "parity": "generic axial and polar plus certified exceptional sectors",
            "ell": "ell>=2 generic; ell=1 exceptional; homogeneous and twist zero-cofiber dispositions",
            "m": "all by SO3 equivariance", "k": "all certified compact momenta", "omega": "standard and extra certified shells",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "observable_pullback": {
            "source": "Obs_loc(C_WM)=Sym(Gamma_c(C_WM^!)) with the dual BRST derivation",
            "target": "Obs_loc(C_EM)=Sym(Gamma_c(C_EM^!)) with the dual BRST derivation",
            "linear_formula": "iota_star(O_f)=O_(iota_sharp f)",
            "polynomial_formula": "iota_star extends multiplicatively and by graded linearity",
            "chain_identity": "q_EM^dual iota_star = iota_star q_WM^dual, dual to q_WM iota=iota q_EM",
            "locality": "iota is finite-order differential, hence iota_sharp is finite-order differential and does not enlarge support",
            "cohomology_map": "H(Obs_loc(C_WM)) -> H(Obs_loc(C_EM))",
            "contravariant": True,
            "support_local": True,
        },
        "residual_equivariance": {
            "group": components["equivariance"]["group"],
            "field_identity": "L_X iota=iota L_X",
            "observable_identity": "iota_star L_X^dual=L_X^dual iota_star",
            "time_generator": "H_product contains H=partial_t and the identity is certified for it",
            "endpoint_map": "identity on H,P_x,J_1,J_2,J_3,u1_constant",
            "endpoint_cofiber_dimension": 0,
            "certified": True,
        },
        "relative_detectors": {
            "general_formula": "a_extra=G_extra^(-1) Omega_WM(conjugate(e_extra),Phi); orthogonality gives iota_star(a_extra)=0 and nondegeneracy separates the cofiber",
            "category": "REDUCED-MODE conserved stationary spectral coefficient; not a support-local spacetime or Peierls observable",
            "sectors": [
                {
                    "sector": "generic_axial_ell_ge_2",
                    "basis_rank": 2,
                    "basis": axial["full_solution_pairing"]["extra_representatives"],
                    "gram": "exact action Lee-Wald restriction imported from the generic axial completion",
                    "orthogonal_to_einstein_image": True,
                    "nonradical": True,
                    "pullback_zero": True,
                },
                {
                    "sector": "generic_polar_ell_ge_2",
                    "basis_rank": 2,
                    "basis": polar["shell_pairing"]["extra_basis_order_At_B_Ct_U"],
                    "gram": polar["shell_pairing"]["extra_Hermitian_current_Gram"],
                    "orthogonal_to_einstein_image": True,
                    "nonradical": True,
                    "pullback_zero": True,
                },
                {
                    "sector": "exceptional_ell1_k0",
                    "basis_rank": 2,
                    "basis": [k0["branch_representatives"]["axial"]["extra_fourth_order"], k0["branch_representatives"]["polar"]["fourth_order"]["representative"]],
                    "gram": k0["action_derived_pairing"]["extra_Gram"],
                    "orthogonal_to_einstein_image": True,
                    "nonradical": True,
                    "pullback_zero": True,
                },
                {
                    "sector": "exceptional_ell1_nonzero_k",
                    "basis_rank": 2,
                    "basis": [knz["theorem"]["polynomial_representatives"]["axial"]["extra"], knz["theorem"]["polynomial_representatives"]["polar"]["extra"]],
                    "gram": [knz["theorem"]["action_pairing"]["Gram"]["axial"]["extra"], knz["theorem"]["action_pairing"]["Gram"]["polar"]["extra"]],
                    "orthogonal_to_einstein_image": True,
                    "nonradical": True,
                    "pullback_zero": True,
                },
            ],
            "zero_cofiber_sectors": ["homogeneous_generalized_zero", "axial_twist_primary", "global_residual_endpoints"],
        },
        "classification": {
            "relative_observable_pullback_constructed": True,
            "observable_pullback_is_chain_map": True,
            "observable_pullback_support_local": True,
            "H_product_equivariance_exact": True,
            "time_translation_equivariance_exact": True,
            "cofiber_detectors_constructed": True,
            "detectors_annihilate_einstein_image": True,
            "detectors_separate_certified_extra_cofibers": True,
            "reduced_mode_pullback_kernel_nonzero": True,
            "endpoint_cofiber_zero": True,
            "full_SO42_equivariance_claimed": False,
            "standard_pairing_cyclic_relative_map": False,
            "full_relative_arity_two_morphism": False,
            "final_residual_quotient_computed": False,
            "causal_green_relative_functor": False,
            "Berger_cross_background_map": False,
            "quantum_lift": False,
        },
        "next_gate": "PARENT_TO_METRIC_CAUSAL_BRIDGE_CONTINUES; NONLINEAR_RELATIVE_REPAIR_REQUIRES_TYPED_CROSS_INCIDENCE_OR_DERIVED_SOURCE_PULLBACK",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.relative_residual_observable_functor --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_relative_residual_observable_functor",
                "python3 -m unittest d_quotient_classical.relative.tests.test_relative_residual_observable_functor",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-residual-observable-functor-v1.schema.json -d d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1.json",
            ],
        },
        "claim_boundary": (
            "This theorem constructs the contravariant support-local pullback on the linear local BRST observable DGA from the certified all-row finite-order inclusion and proves H_product equivariance, including time translation. On solution cohomology it also exports exact REDUCED-MODE coefficient detectors for every certified nonzero generic and exceptional extra cofiber; these annihilate the Einstein image by the imported action-current orthogonality and separate the cofiber by nondegenerate Gram matrices. The detectors are not support-local spacetime, Peierls or relational observables. The three action-derived forms remain distinct; no standard-pairing cyclic relative map, full f2, arity three, final residual quotient, causal Green functor, Berger cross-background map or quantum lift is claimed."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Relative residual and observable functor

The all-row finite-order chain map \(\iota:{\cal C}_{EM}\to{
\cal C}_{WM}\) induces the contravariant map on compactly supported local
polynomial BRST observables

\[
\iota^* O_f=O_{\iota^\sharp f}.
\]

Because \(q_{WM}\iota=\iota q_{EM}\), dualization and multiplicative
extension give \(q_{EM}^\vee\iota^*=\iota^*q_{WM}^\vee\).  Finite
differential order preserves support.  The imported product-equivariance also
dualizes, including for \(H=\partial_t\).  Explicitly, pairing the two sides
with a source test field reduces their difference to
\(\langle f,(q_{WM}\iota-\iota q_{EM})u\rangle=0\).  Hence the construction
is an actual support-local observable pullback on the linear BRST complexes.

The generic axial and polar extra blocks, exceptional \(\ell=1,k=0\) block,
and exceptional \(\ell=1,k\ne0\) block have action-derived nondegenerate Gram
matrices and vanish in mixed pairing with the Einstein image.  Pairing with an
extra basis and applying the inverse Gram matrix therefore gives coefficient
observables that vanish after \(\iota^*\) and separate the relative solution
cofiber.  These are stationary `REDUCED-MODE` observables, not local Peierls or
relational observables.  Homogeneous, twist and endpoint cofibers are zero in
their certified scopes.  The extra detectors give a nonzero kernel of the
reduced-mode pullback before the final residual quotient; no quasi-isomorphism
is asserted.  Equivariance is only under the certified product residual group,
not full \(SO(4,2)\).

Nothing here changes the noncyclic pairing disposition or repairs the direct
arity-two Taub obstruction.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("full_SO42_equivariance_claimed", "standard_pairing_cyclic_relative_map", "full_relative_arity_two_morphism", "final_residual_quotient_computed", "causal_green_relative_functor", "Berger_cross_background_map", "quantum_lift"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("relative observable functor outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
