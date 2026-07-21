"""Exact fixed-Chern background chambers for the product Taub-sign programme.

This preflight combines the certified locally symmetric product incidence with
Dirac flux quantization.  It classifies the resulting background branches and
locates the compact Plebanski--Hacyan fixture on the double-root wall.  It does
not extrapolate the fixture's reduced-mode Taub signs away from that wall: the
curvature/flux lower-order Hessians and action-derived Lee--Wald current have
not yet been constructed on either open chamber.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FIXED_CHERN_PRODUCT_TAUB_SIGN_PREFLIGHT_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/einstein-fixed-chern-product-taub-sign-preflight-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-fixed-chern-product-taub-sign-preflight-v1.schema.json"
PRODUCER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight.py"

INPUTS = {
    "product_incidence": (
        ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
        "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
        "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
    ),
    "product_tangent_preflight": (
        ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
        "cbae5417348975b9ceee8b04be7b6214c7ca8bf5f2c3778b4527de461569512b",
        "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
    ),
    "harmonic_taub_sign": (
        ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
        "26fae23935261735385d6a7796d5f10db3404f863d2bdf85c7b5d0869afd0006",
        "EINSTEIN_MAXWELL_WEYL_HARMONIC_TAUB_SIGN_CLASSIFICATION",
    ),
    "exceptional_all_m": (
        ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1.json",
        "983bfc000f32975f55f8d8a9b8e1fc14138b2cbeccb070f2f13d2dc239d4a59e",
        "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1",
    ),
    "finite_harmonic_structural": (
        ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
        "935a3c264858c4f425025f2f1adf50886739bb84cdc86331120058c9ce7bd545",
        "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1",
    ),
    "moment_map_taub": (
        ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
        "047594a9019eb68a000ecce1799063789714db632c41e67e48d37bdf0fc3657a",
        "EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE",
    ),
}


class FixedChernTaubPreflightError(RuntimeError):
    """Raised when an exact chamber or import invariant fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixedChernTaubPreflightError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _import_gate() -> list[dict[str, str]]:
    imported: list[dict[str, str]] = []
    payloads: dict[str, dict[str, Any]] = {}
    for name, (path, expected_hash, result_id) in INPUTS.items():
        _require(path.exists(), f"missing input: {path}")
        actual_hash = _sha256(path)
        _require(actual_hash == expected_hash, f"input hash drift: {name}")
        payload = _load(path)
        _require(payload.get("result_id") == result_id, f"result id drift: {name}")
        payloads[name] = payload
        imported.append(
            {
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "result_id": result_id,
                "sha256": actual_hash,
            }
        )

    incidence = payloads["product_incidence"]
    tangent = payloads["product_tangent_preflight"]
    signs = payloads["harmonic_taub_sign"]
    moment = payloads["moment_map_taub"]
    structural = payloads["finite_harmonic_structural"]
    _require(
        incidence["claim_flags"]["exact_nonlinear_background_incidence_certified"]
        and incidence["claim_flags"]["u1_flux_quantization_relation_certified"],
        "background incidence gate changed",
    )
    _require(
        tangent["classification"]["principal_bv_chain_map_constructed"]
        and not tangent["classification"]["full_curved_tangent_chain_map_constructed"]
        and not tangent["classification"]["covariant_presymplectic_map_constructed"],
        "generic tangent preflight boundary changed",
    )
    _require(
        signs["classification"]["generic_extra_all_ell_all_k_both_parities_negative"]
        and signs["classification"]["Einstein_q_minus_opposite_sign_all_ell_both_parities"]
        and not signs["classification"]["variable_magnetic_flux_extension_classified"],
        "fixed-fixture sign boundary changed",
    )
    _require(
        moment["classification"]["generic_covariant_moment_map_Taub_equality_certified"]
        and structural["classification"]["finite_exponential_polynomial_cone_theorem_ready"],
        "moment/cone structural import gate changed",
    )
    return imported


def _exact_chambers() -> dict[str, Any]:
    alpha, kappa, n, q, k_1, k_2 = sp.symbols(
        "alpha_B kappa N q_min k_1 k_2", positive=True, real=True
    )
    beta = sp.factor(kappa * n**2 / (4 * q**2))
    alpha_critical = sp.factor(3 * n**2 / (4 * q**2))
    magnetic = sp.factor(n * k_2 / (2 * q))
    k_1_from_flux = sp.factor(k_2 - kappa * magnetic**2)
    polynomial = sp.factor(
        beta * k_2**2 - 2 * k_2 + sp.Rational(3, 1) / (alpha * kappa)
    )
    discriminant = sp.factor(sp.discriminant(polynomial, k_2))
    expected_discriminant = sp.factor(4 * (1 - alpha_critical / alpha))
    _require(sp.simplify(discriminant - expected_discriminant) == 0, "discriminant changed")

    s = sp.symbols("s", positive=True, real=True)
    root_low = sp.factor((1 - s) / beta)
    root_high = sp.factor((1 + s) / beta)
    alpha_from_s = sp.factor(alpha_critical / (1 - s**2))
    for root in (root_low, root_high):
        remainder = sp.factor(polynomial.subs({k_2: root, alpha: alpha_from_s}))
        _require(remainder == 0, "open-chamber root failed")
    k1_low = sp.factor(k_1_from_flux.subs(k_2, root_low))
    k1_high = sp.factor(k_1_from_flux.subs(k_2, root_high))
    _require(k1_low == sp.factor(s * root_low), "low-branch k1 sign changed")
    _require(k1_high == sp.factor(-s * root_high), "high-branch k1 sign changed")

    critical_root = sp.factor(1 / beta)
    _require(
        sp.factor(polynomial.subs({alpha: alpha_critical, k_2: critical_root})) == 0,
        "critical root failed",
    )
    _require(sp.factor(k_1_from_flux.subs(k_2, critical_root)) == 0, "wall is not flat")

    fixture = {n: 2, q: 1, kappa: 1}
    _require(sp.factor(alpha_critical.subs(fixture)) == 3, "fixture alpha wall changed")
    alpha_four_s = sp.Rational(1, 2)
    low_four = sp.factor(root_low.subs(fixture).subs(s, alpha_four_s))
    high_four = sp.factor(root_high.subs(fixture).subs(s, alpha_four_s))
    _require((low_four, high_four) == (sp.Rational(1, 2), sp.Rational(3, 2)), "alpha=4 roots changed")
    _require(
        (
            sp.factor(k1_low.subs(fixture).subs(s, alpha_four_s)),
            sp.factor(k1_high.subs(fixture).subs(s, alpha_four_s)),
        )
        == (sp.Rational(1, 4), sp.Rational(-3, 4)),
        "alpha=4 k1 values changed",
    )

    return {
        "flux_quantization": {
            "assumptions": ["N is a nonzero integer", "q_min>0", "kappa>0", "k_2>0", "E=0"],
            "chern_relation": "(q_min/(2*pi))*integral_Sigma F=N",
            "sphere_area": "4*pi/k_2",
            "magnetic_amplitude": "P=N*k_2/(2*q_min)",
            "fixed_scope": "fixed magnetic bundle component P_N; N is not varied",
        },
        "reduction": {
            "beta": str(beta),
            "alpha_critical": str(alpha_critical),
            "einstein_flux_relation": f"k_1={k_1_from_flux}",
            "background_quadratic": "beta*k_2**2-2*k_2+3/(alpha_B*kappa)=0",
            "expanded_left_hand_side": str(polynomial),
            "discriminant": str(discriminant),
        },
        "chambers": [
            {
                "condition": "alpha_B<alpha_critical",
                "background_count": 0,
                "classification": "NO_REAL_FIXED_CHERN_PURE_MAGNETIC_COMMON_PRODUCT",
            },
            {
                "condition": "alpha_B=alpha_critical",
                "background_count": 1,
                "multiplicity": 2,
                "k_2": str(critical_root),
                "k_1": "0",
                "classification": "FLAT_DOUBLE_ROOT_WALL",
                "compact_cauchy_status": "CERTIFIED_BY_THE_IMPORTED_PLEBANSKI_HACYAN_FIXTURE",
            },
            {
                "condition": "alpha_B>alpha_critical; s=sqrt(1-alpha_critical/alpha_B) in (0,1)",
                "background_count": 2,
                "branches": [
                    {
                        "id": "LOW_CURVATURE_DS2_BRANCH",
                        "k_2": str(root_low),
                        "k_1": str(k1_low),
                        "sign_k_1": "POSITIVE",
                        "compact_cauchy_status": "GEOMETRICALLY_AVAILABLE_ON_GLOBAL_DS2_X_S2; TANGENT_CARRIER_NOT_CERTIFIED",
                    },
                    {
                        "id": "HIGH_CURVATURE_ADS2_BRANCH",
                        "k_2": str(root_high),
                        "k_1": str(k1_high),
                        "sign_k_1": "NEGATIVE",
                        "compact_cauchy_status": "NO_CERTIFIED_GLOBAL_COMPACT_CAUCHY_QUOTIENT",
                    },
                ],
            },
        ],
        "exact_fixture": {
            "N": 2,
            "q_min": 1,
            "kappa": 1,
            "alpha_critical": "3",
            "wall": {"alpha_B": "3", "k_2": "1", "k_1": "0"},
            "open_chamber_example": {
                "alpha_B": "4",
                "s": "1/2",
                "branches": [
                    {"k_2": "1/2", "k_1": "1/4"},
                    {"k_2": "3/2", "k_1": "-3/4"},
                ],
            },
        },
    }


def build_certificate() -> dict[str, Any]:
    imported = _import_gate()
    chambers = _exact_chambers()
    return {
        "schema": "einstein-maxwell-weyl-fixed-chern-product-taub-sign-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FIXED_CHERN_PRODUCT_TAUB_SIGN_PREFLIGHT_V1",
        "result_state": "BACKGROUND_CHAMBERS_CERTIFIED_TAUB_SIGN_GENERALIZATION_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_commit": "414853ed8",
            "producer": str(PRODUCER_PATH.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER_PATH),
            "imported_artifacts": imported,
        },
        "scope": {
            "theory": "common Einstein-Maxwell/pure-Weyl-Maxwell product solution locus",
            "background": "M_2(k_1) x S^2(k_2), aligned pure magnetic Maxwell field",
            "boundaries": "fixed-Chern compact-S2 products; compact Cauchy status branch-specific",
            "charge_sector": "fixed magnetic U(1) bundle P_N, N nonzero; electric amplitude E=0",
            "carrier": "nonlinear background incidence plus imported fixed-wall reduced harmonic carriers only",
            "degree": "background degree 0; Taub comparison degree 2 only where imported",
            "parity": "axial and polar only on the flat wall; off-wall NO_CERTIFIED_MAP",
            "ell": "all certified wall harmonics; off-wall unclassified",
            "m": "all certified wall magnetic labels; off-wall unclassified",
            "k": "all certified compact wall momenta; off-wall spatial spectrum unclassified",
            "omega": "certified wall q/p shells only; off-wall dispersion unclassified",
        },
        "fixed_chern_background_theorem": chambers,
        "carrier_audit": {
            "nonlinear_product_incidence": "CERTIFIED_ON_THE_FULL_PARAMETERIZED_FAMILY",
            "principal_symbol_chain_map": "CERTIFIED_AND_PARAMETER_INDEPENDENT_AT_PRINCIPAL_ORDER",
            "curvature_flux_lower_order_hessians": "NO_CERTIFIED_MAP",
            "off_wall_axial_polar_branch_dictionary": "NO_CERTIFIED_MAP",
            "off_wall_action_derived_lee_wald_current": "NO_CERTIFIED_MAP",
            "flat_wall_taub_signs": "CERTIFIED_ON_THE_PLEBANSKI_HACYAN_DOUBLE_ROOT_FIXTURE",
            "logical_consequence": "The wall signs cannot be continued to either open chamber from principal-symbol data alone.",
        },
        "classification": {
            "fixed_chern_background_chambers_classified": True,
            "flat_fixture_is_double_root_wall": True,
            "two_open_background_branches_above_critical_coupling": True,
            "no_real_background_below_critical_coupling": True,
            "off_wall_full_linearized_operator_constructed": False,
            "off_wall_taub_moment_maps_defined": False,
            "off_wall_extra_energy_definiteness_certified": False,
            "off_wall_einstein_opposite_sign_certified": False,
            "sign_change_across_wall_certified": False,
            "variable_flux_theorem_certified": False,
            "bounded_second_order_sufficiency_certified_off_wall": False,
        },
        "next_gate": {
            "priority_branch": "LOW_CURVATURE_DS2_BRANCH",
            "required_objects": [
                "full curvature/flux lower-order axial and polar Weyl-Maxwell Hessians",
                "same-background Einstein image and q/p branch dictionary",
                "action-derived Lee-Wald current and stabilizer lifts",
                "factorization of every shell, current pivot, and exceptional harmonic wall",
            ],
            "then": "Repeat separately on the high-curvature AdS2 branch with an explicit boundary/global-hyperbolicity policy.",
        },
        "claim_flags": {
            "exact_background_chamber_theorem": True,
            "structural_taub_sign_theorem_beyond_flat_fixture": False,
            "moment_map_zero_equals_bounded_continuation": False,
            "lorentzian_causal_claim": False,
            "observable_claim": False,
            "scattering_claim": False,
            "particle_or_quantum_norm_claim": False,
        },
        "claim_boundary": (
            "This exact preflight classifies the pure-magnetic fixed-Chern common-product background chambers and proves that the certified compact Plebanski-Hacyan Taub signs live on their flat double-root wall. It does not define or infer the off-wall q/p modes, Lee-Wald form, stabilizer moment maps, sign pivots, bounded tangent cone, causal evolution, observables, particles, scattering, or quantum norms."
        ),
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight --check",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-fixed-chern-product-taub-sign-preflight-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER_PATH.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER_PATH),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.product.fixed_chern.background_chambers.taub_sign_preflight",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "NO_CERTIFIED_MAP",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "NO_CERTIFIED_MAP", "statement": "No off-wall harmonic shells are certified."},
                    "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "The off-wall action-derived current is missing."},
                    "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "Wall moment maps cannot be transported without the lower-order carrier."},
                    "resonance": {"status": "NO_CERTIFIED_MAP", "statement": "No off-wall source operator or resonant functional is defined."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Background chambers are exact; the off-wall tangent cone is undefined."},
                        "smooth_secular": {"status": "OPEN", "statement": "No off-wall exponential-polynomial operator is certified."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."},
                    },
                },
                "evidence": [
                    {
                        "path": str(certificate_path.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": _sha256(certificate_path),
                    }
                ],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atlas", type=Path, default=ATLAS_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(args.output.exists(), "committed certificate missing")
        _require(_load(args.output) == certificate, "committed certificate drift")
        expected_atlas = build_atlas(certificate, args.output)
        _require(args.atlas.exists(), "committed atlas missing")
        _require(_load(args.atlas) == expected_atlas, "committed atlas drift")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate, args.output)
    args.atlas.parent.mkdir(parents=True, exist_ok=True)
    args.atlas.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
