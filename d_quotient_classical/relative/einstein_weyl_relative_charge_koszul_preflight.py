#!/usr/bin/env python3
"""Select the derived charge receiver after the relative f2 obstruction.

The direct full-domain Einstein--Weyl morphism is obstructed at arity two.
This producer records the smallest honest replacement on the certified
standard radiative solution carrier: keep the support-local unary mapping
cofiber, retain the five stabilizer moment maps as a quadratic charge fibre,
and present their derived zero locus by its Koszul algebra.  The construction
is deliberately REDUCED-MODE.  It does not manufacture the still-missing
off-shell local q2 lift.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-charge-koszul-receiver-preflight.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-charge-koszul-receiver-preflight-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_charge_koszul_preflight.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_charge_koszul_preflight.py"

DEPENDENCIES = {
    "linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "linear_triangle_components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "radiative_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "relative_solution_form": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "moment_map_taub_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _s(value: sp.Expr) -> str:
    return str(sp.factor(sp.radsimp(sp.simplify(value))))


def _koszul_square(generator_count: int) -> bool:
    """Check d^2=0 on every exterior monomial with symbolic moments."""

    moments = sp.symbols(f"mu0:{generator_count}", commutative=True)

    def differential(term: tuple[int, ...]) -> dict[tuple[int, ...], sp.Expr]:
        out: dict[tuple[int, ...], sp.Expr] = {}
        for position, generator in enumerate(term):
            rest = term[:position] + term[position + 1 :]
            out[rest] = sp.expand(out.get(rest, 0) + (-1) ** position * moments[generator])
        return out

    for mask in range(1 << generator_count):
        term = tuple(i for i in range(generator_count) if mask & (1 << i))
        twice: dict[tuple[int, ...], sp.Expr] = {}
        for first_term, first_coefficient in differential(term).items():
            for second_term, second_coefficient in differential(first_term).items():
                twice[second_term] = sp.expand(
                    twice.get(second_term, 0) + first_coefficient * second_coefficient
                )
        if any(sp.simplify(value) != 0 for value in twice.values()):
            return False
    return True


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    triangle = records["linear_triangle"]
    components = records["linear_triangle_components"]
    radiative = records["radiative_restriction"]
    relative_form = records["relative_solution_form"]
    moment = records["moment_map_taub_bridge"]
    obstruction = records["f2_obstruction"]

    if triangle["acceptance_flags"]["SUPPORT_LOCAL_MAPPING_COFIBER"] is not True:
        raise AssertionError("support-local unary mapping cofiber is not certified")
    if triangle["acceptance_flags"]["H_PRODUCT_EQUIVARIANT"] is not True:
        raise AssertionError("product-stabilizer equivariance is not certified")
    endpoints = components["global_endpoints"]
    endpoint_basis = endpoints["source_basis"]
    expected_endpoints = ["partial_t", "partial_x", "J_1", "J_2", "J_3", "u1_constant"]
    if endpoint_basis != expected_endpoints or endpoints["target_basis"] != expected_endpoints:
        raise AssertionError("global endpoint basis drifted")
    identity = [[int(i == j) for j in range(6)] for i in range(6)]
    if endpoints["map_matrix"] != identity or endpoints["dual_map_matrix"] != identity:
        raise AssertionError("global endpoint maps are not the identity")
    if endpoints["cone_cohomology_dimension"] != 0:
        raise AssertionError("unary endpoint cone unexpectedly carries cohomology")
    if moment["classification"]["generic_covariant_moment_map_Taub_equality_certified"] is not True:
        raise AssertionError("moment-map--Taub bridge is not certified")
    if relative_form["cyclic_obstruction_theorem"]["solution_pairing_identity"] != (
        "iota^*Omega_WM(u,v)-Omega_EM(u,v)=Omega_EM(u,Dv), D=R-I"
    ):
        raise AssertionError("relative solution form drifted")
    if obstruction["classification"]["frozen_unary_full_domain_f2_exists"] is not False:
        raise AssertionError("direct f2 obstruction was not retained")

    lam = sp.symbols("lambda", positive=True)
    imported = radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    weights = [sp.sympify(text.replace("lambda", "lam"), locals={"lam": lam}) for text in imported]
    relative_weights = [sp.simplify(weight - 1) for weight in weights]
    expected = [sp.Rational(3, 2) * sp.sqrt(2 * lam), -sp.Rational(3, 2) * sp.sqrt(2 * lam)]
    if any(sp.simplify(got - want) != 0 for got, want in zip(relative_weights, expected)):
        raise AssertionError("relative charge weights drifted")

    witness = obstruction["taub_pairing"]
    mu_rel_h = sp.sympify(witness["relative_half_delta2_pairing"])
    if sp.simplify(mu_rel_h + sp.Rational(54, 5) * (1 + sp.sqrt(3))) != 0:
        raise AssertionError("relative H witness drifted")
    if not _koszul_square(5):
        raise AssertionError("five-generator Koszul differential failed to square to zero")

    charge_basis = ["H=partial_t", "P_x=partial_x", "J_1", "J_2", "J_3"]
    return {
        "schema": "pure-weyl-relative-charge-koszul-receiver-preflight-v1",
        "result_id": RESULT_ID,
        "result_state": "DERIVED_RELATIVE_CHARGE_RECEIVER_SELECTED_OFFSHELL_LIFT_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1_L x S2",
            "boundaries": "closed Cauchy slice S1_L x S2 before final residual quotient",
            "charge_sector": "fixed compact U(1) bundle P_N with N=2",
            "carrier": "standard radiative ell>=2 solution carrier together with the certified support-local unary mapping cofiber",
            "degree": "quadratic relative moment map and its Koszul generators",
            "parity": "axial and polar",
            "ell": "ell>=2",
            "m": "all real SO(3) multiplicities",
            "k": "2*pi*n/L for every n in Z",
            "omega": "Einstein plus and minus branches",
        },
        "dependencies": {
            name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()
        },
        "unary_carrier": {
            "construction": "retain the certified support-local noncyclic mapping cofiber Cone(f1)",
            "degree_dimensions": components["mapping_cofiber"]["degree_dimensions"],
            "square_zero": components["mapping_cofiber"]["square_zero"],
            "support_local": components["mapping_cofiber"]["support_local"],
            "endpoint_basis": endpoint_basis,
            "endpoint_map": "identity_6",
            "endpoint_cone_cohomology_dimension": endpoints["cone_cohomology_dimension"],
        },
        "charge_fibre": {
            "basis": charge_basis,
            "dimension": 5,
            "origin": "dual of the connected product-isometry stabilizer",
            "constant_u1_endpoint": {
                "basis_element": "u1_constant",
                "disposition": "REDUCIBILITY_NOT_A_SIXTH_TAUB_CHARGE",
                "reason": "the constant U1 parameter has d lambda=0 and hence zero fundamental vector field on the fixed-bundle perturbation carrier",
            },
            "relative_moment_map": "mu_rel,X(u)=1/2*(iota^*Omega_WM-Omega_EM)(u,L_X u)",
            "polarization": "mu_rel,X(u,v)=1/2 of the symmetric polarization of the displayed quadratic form",
            "branch_rule": "mu_rel,X=(w_branch-1)*mu_EM,X on an Einstein branch eigenmode; the spectral relative operator commutes with H_product by certified equivariance",
            "weyl_pullback_weights": [_s(value) for value in weights],
            "relative_weights": [_s(value) for value in relative_weights],
            "h_witness": {
                "mode": "axial ell=2,m=0,k=0 plus branch",
                "mu_rel_H": _s(mu_rel_h),
                "nonzero": True,
            },
        },
        "derived_zero_locus": {
            "presentation": "O(Sol_std) tensor Exterior(kappa_H,kappa_Px,kappa_J1,kappa_J2,kappa_J3)",
            "differential": "d_K f=0 on reduced solution functions and d_K kappa_X=mu_rel,X",
            "generator_count": 5,
            "exterior_basis_dimension": 32,
            "square_zero_checked_on_all_exterior_monomials": True,
            "quadratic_origin": "mu_rel(0)=0 and d mu_rel|_0=0",
            "unary_tangent_consequence": "the full standard radiative tangent survives at first order; the Taub-zero condition enters at quadratic order",
            "plain_linear_subcomplex_restriction_valid": False,
        },
        "architecture_decision": {
            "selected": "CERTIFIED_UNARY_MAPPING_COFIBER_PLUS_REDUCED_MODE_RELATIVE_CHARGE_KOSZUL_RECEIVER",
            "rejected": "delete every nonzero-charge mode by calling the quadratic Taub-zero locus a linear subcomplex",
            "reason": "the relative moment map is homogeneous quadratic, so its derived zero locus is encoded by Koszul generators rather than by a linear q1 restriction",
        },
        "classification": {
            "unary_mapping_cofiber_retained": True,
            "five_dimensional_relative_charge_fibre_identified": True,
            "constant_u1_is_sixth_taub_charge": False,
            "reduced_mode_koszul_square_zero": True,
            "relative_h_witness_nonzero": True,
            "plain_linear_taub_zero_subcomplex_valid": False,
            "full_offshell_charge_map_certified": False,
            "support_local_koszul_bv_extension_certified": False,
            "relative_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CONSTRUCT_OFFSHELL_FIVE_CHARGE_POLARIZATION_OR_RETURN_TYPED_OBSTRUCTION",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_charge_koszul_preflight --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_charge_koszul_preflight",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_charge_koszul_preflight",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-charge-koszul-receiver-preflight-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
            ],
        },
        "claim_boundary": (
            "This REDUCED-MODE preflight selects the correct post-obstruction architecture on the certified standard radiative carrier: retain the support-local unary mapping cofiber and adjoin the five relative stabilizer moment maps through a Koszul derived-zero-locus receiver. The constant U1 reducibility is not a sixth Taub charge. The exact relative H witness remains nonzero. No complete off-shell five-charge polarization, support-local BV/Koszul extension, repaired f2, arity-three morphism, causal Green functor, observable, particle or quantum theorem is claimed; exceptional and global sectors remain outside the charge formula certified here."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["classification"]["relative_f2_repaired"] is not False:
        raise AssertionError("preflight silently repaired f2")
    if value["classification"]["reduced_mode_koszul_square_zero"] is not True:
        raise AssertionError("Koszul square-zero theorem dropped")


def _report() -> str:
    return r"""# Relative charge/Koszul receiver preflight

The direct full-domain Einstein--Weyl morphism is obstructed at arity two,
but the obstruction does not justify deleting the offending linear mode.  The
relative Taub map is quadratic, so its zero locus is a derived quadratic locus,
not a linear subcomplex.

The certified unary carrier remains the support-local noncyclic mapping
cofiber.  Its six residual endpoints map identically and have zero endpoint
cone cohomology.  Five endpoints are connected product isometries,

\[
H,\quad P_x,\quad J_1,\quad J_2,\quad J_3,
\]

and define the relative moment maps

\[
\mu_{\mathrm{rel},X}(u)
=\frac12(\iota^*\Omega_{\mathrm{WM}}-\Omega_{\mathrm{EM}})
(u,\mathcal L_Xu).
\]

The sixth endpoint is constant (U(1)) reducibility.  Since
(d\lambda=0), its fundamental vector field vanishes; it is not a sixth Taub
charge.

On the standard radiative branches,

\[
w_\pm=1\pm\frac32\sqrt{2\ell(\ell+1)},\qquad
\mu_{\mathrm{rel},X}=(w_\pm-1)\mu_{\mathrm{EM},X}.
\]

The derived zero locus is represented, at this reduced-mode stage, by

\[
\mathcal O(\mathrm{Sol}_{\mathrm{std}})\otimes
\Lambda(\kappa_H,\kappa_{P_x},\kappa_{J_1},\kappa_{J_2},\kappa_{J_3}),
\qquad d_K\kappa_X=\mu_{\mathrm{rel},X}.
\]

The exact exterior-algebra check gives (d_K^2=0) on all 32 monomials.
Because each moment map is homogeneous quadratic,
(\mu_{\mathrm{rel}}(0)=d\mu_{\mathrm{rel}}|_0=0): the full radiative
tangent survives at unary order and the Taub condition first appears at
quadratic order.

This selects the architecture but does not yet build its off-shell local BV
lift.  The next gate is the complete five-charge polarization of the exact
PBW defect, including exceptional and global rows as required, or a typed
obstruction to such a lift.  The original (f_2) remains obstructed and arity
three remains closed.
"""


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _guards(value: dict) -> None:
    mutations = (
        ("classification", "constant_u1_is_sixth_taub_charge", True),
        ("classification", "plain_linear_taub_zero_subcomplex_valid", True),
        ("classification", "full_offshell_charge_map_certified", True),
        ("classification", "relative_f2_repaired", True),
        ("classification", "arity_three_authorized", True),
        ("classification", "causal_observable_particle_or_quantum_claim", True),
    )
    for section, key, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][key] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted {section}.{key}")


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
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("relative charge/Koszul preflight outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
