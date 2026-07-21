"""Independent verifier for the fixed-Chern product Taub-sign preflight.

This rail intentionally does not import the producer.  It derives the chamber
quadratic by eliminating the flux and solves it independently.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FIXED_CHERN_PRODUCT_TAUB_SIGN_PREFLIGHT_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-fixed-chern-product-taub-sign-preflight-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-fixed-chern-product-taub-sign-preflight-v1.schema.json"

EXPECTED_INPUTS = {
    "bridge/certificates/einstein_maxwell_product_incidence.json": "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
    "bridge/certificates/einstein_maxwell_product_tangent_preflight.json": "cbae5417348975b9ceee8b04be7b6214c7ca8bf5f2c3778b4527de461569512b",
    "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json": "26fae23935261735385d6a7796d5f10db3404f863d2bdf85c7b5d0869afd0006",
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1.json": "983bfc000f32975f55f8d8a9b8e1fc14138b2cbeccb070f2f13d2dc239d4a59e",
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json": "935a3c264858c4f425025f2f1adf50886739bb84cdc86331120058c9ce7bd545",
    "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json": "047594a9019eb68a000ecce1799063789714db632c41e67e48d37bdf0fc3657a",
}


class IndependentPreflightVerificationError(RuntimeError):
    """Raised when the independent chamber audit fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentPreflightVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _independent_algebra() -> None:
    alpha, kappa, n, q, x = sp.symbols("a k N q x", positive=True, real=True)
    magnetic = n * x / (2 * q)
    first_curvature = x - kappa * magnetic**2
    # Substitute k1 into alpha*kappa*(k1+k2)=3 without using producer data.
    incidence = sp.factor(alpha * kappa * (first_curvature + x) - 3)
    polynomial = sp.factor(-incidence / (alpha * kappa))
    beta = sp.factor(kappa * n**2 / (4 * q**2))
    expected = sp.factor(beta * x**2 - 2 * x + 3 / (alpha * kappa))
    _require(sp.factor(polynomial - expected) == 0, "independent elimination changed")

    alpha_critical = sp.factor(3 * n**2 / (4 * q**2))
    discriminant = sp.factor(sp.discriminant(polynomial, x))
    _require(
        sp.factor(discriminant - 4 * (1 - alpha_critical / alpha)) == 0,
        "independent discriminant changed",
    )
    roots = [sp.factor(root) for root in sp.solve(polynomial, x)]
    _require(len(roots) == 2, "quadratic root count changed")

    fixture = {n: 2, q: 1, kappa: 1}
    fixture_poly = sp.factor(polynomial.subs(fixture))
    _require(sp.factor(fixture_poly.subs(alpha, 3) - (x - 1) ** 2) == 0, "wall is not a double root")
    alpha_four_roots = sorted(sp.solve(fixture_poly.subs(alpha, 4), x), key=lambda value: float(value))
    _require(alpha_four_roots == [sp.Rational(1, 2), sp.Rational(3, 2)], "alpha=4 roots changed")
    k1_values = [sp.factor(first_curvature.subs(fixture).subs(x, root)) for root in alpha_four_roots]
    _require(k1_values == [sp.Rational(1, 4), sp.Rational(-3, 4)], "alpha=4 branch signs changed")
    _require(sp.discriminant(fixture_poly.subs(alpha, 2), x) < 0, "subcritical mutation was not rejected")
    _require(sp.discriminant(fixture_poly.subs(alpha, 3), x) == 0, "critical mutation was not detected")
    _require(sp.discriminant(fixture_poly.subs(alpha, 4), x) > 0, "supercritical mutation was not detected")


def verify_certificate(
    certificate_path: Path = CERTIFICATE,
    atlas_path: Path = ATLAS,
) -> None:
    payload = _load(certificate_path)
    schema = _load(SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")

    imports = {entry["path"]: entry["sha256"] for entry in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED_INPUTS, "import ledger changed")
    for relative_path, expected_hash in EXPECTED_INPUTS.items():
        _require(_sha256(ROOT / relative_path) == expected_hash, f"input drift: {relative_path}")

    _independent_algebra()
    theorem = payload["fixed_chern_background_theorem"]
    _require(theorem["exact_fixture"]["alpha_critical"] == "3", "fixture wall changed")
    _require([row["background_count"] for row in theorem["chambers"]] == [0, 1, 2], "chamber counts changed")
    _require(theorem["chambers"][1]["classification"] == "FLAT_DOUBLE_ROOT_WALL", "wall label changed")

    classification = payload["classification"]
    _require(classification["flat_fixture_is_double_root_wall"] is True, "wall flag changed")
    for key in (
        "off_wall_full_linearized_operator_constructed",
        "off_wall_taub_moment_maps_defined",
        "off_wall_extra_energy_definiteness_certified",
        "off_wall_einstein_opposite_sign_certified",
        "sign_change_across_wall_certified",
        "variable_flux_theorem_certified",
        "bounded_second_order_sufficiency_certified_off_wall",
    ):
        _require(classification[key] is False, f"forbidden promotion: {key}")
    _require(payload["claim_flags"]["particle_or_quantum_norm_claim"] is False, "quantum promotion")

    atlas = _load(atlas_path)
    _require(atlas["schema"] == "pure-weyl-residual-atlas-fragment-v1", "atlas schema changed")
    _require(len(atlas["entries"]) == 1, "atlas entry count changed")
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(certificate_path), "atlas evidence hash drift")
    _require(
        entry["descriptions"]
        == {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "NO_CERTIFIED_MAP",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "atlas fail-closed statuses changed",
    )


def main() -> int:
    verify_certificate()
    print("independent fixed-Chern product Taub-sign preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
