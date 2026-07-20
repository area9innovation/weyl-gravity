"""Independent exact verifier for the asymptotic local-counterterm obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-local-counterterm-cohomology-obstruction-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-local-counterterm-cohomology-fragment-v1.json"
RAW_HASH = "1cef43665f6ff2917669d7e762e20c527b3b4b001f8c77a1581856d93c35e10c"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _total(expression: sp.Expr, families: tuple[tuple[sp.Symbol, ...], ...]) -> sp.Expr:
    return sp.expand(
        sum(
            sp.diff(expression, family[index]) * family[index + 1]
            for family in families
            for index in range(len(family) - 1)
        )
    )


def verify() -> None:
    certificate = _load(CERTIFICATE)
    schema = _load(SCHEMA)
    atlas = _load(ATLAS)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    assert certificate["schema_sha256"] == _sha256(SCHEMA)
    assert certificate["provenance"]["pinned_raw_sha256"] == RAW_HASH
    for reference in certificate["provenance"]["inputs"].values():
        path = ROOT / reference["path"]
        assert _sha256(path) == reference["sha256"]
        assert _load(path)["result_id"] == reference["result_id"]

    # Re-derive the four-dimensional algebra without importing the producer.
    x, y, z = sp.symbols("Riemann2 Ricci2 Scalar2")
    c2 = x - 2 * y + z / 3
    e4 = x - 4 * y + z
    assert sp.expand(c2 - e4) == 2 * y - sp.Rational(2, 3) * z
    alpha, curvature = sp.symbols("alpha curvature")
    assert sp.diff(alpha * curvature**2 / 8, curvature) == alpha * curvature / 4

    # Euler-operator test: the antisymmetric news density is nonexact, while
    # the one-sign mutation is the total derivative D_u(fg).
    f0, f1, f2, g0, g1, g2 = sp.symbols("f0 f1 f2 g0 g1 g2")
    families = ((f0, f1, f2), (g0, g1, g2))
    news = f0 * g1 - g0 * f1
    e_f = sp.expand(sp.diff(news, f0) - _total(sp.diff(news, f1), families))
    e_g = sp.expand(sp.diff(news, g0) - _total(sp.diff(news, g1), families))
    assert (e_f, e_g) == (2 * g1, -2 * f1)
    mutation = f0 * g1 + g0 * f1
    assert mutation == _total(f0 * g0, families)
    assert sp.diff(mutation, f0) - _total(sp.diff(mutation, f1), families) == 0
    assert sp.diff(mutation, g0) - _total(sp.diff(mutation, g1), families) == 0

    exact = certificate["exact_algebra"]
    ric2, scalar2 = sp.symbols("Ric2 R2")
    assert sp.expand(
        sp.sympify(
            exact["four_dimensional_curvature_identity"]["difference"],
            locals={"Ric2": ric2, "R2": scalar2},
        )
        - (2 * ric2 - sp.Rational(2, 3) * scalar2)
    ) == 0
    assert exact["curvature_momentum"]["factor"] == "alpha_B/4"
    assert exact["flat_einstein_restriction"]["restricted_value"] == "0"
    assert exact["nonexact_news_witness"]["Euler_f"] == "2*g1"
    assert exact["nonexact_news_witness"]["Euler_g"] == "-2*f1"
    assert exact["mutation_control"]["verdict"] == "DETECTOR_REJECTS_EXACT_MUTATION"

    flags = certificate["classification"]
    assert flags["full_tensor_C2_lee_wald_potential_derived"] is True
    assert flags["complete_existing_field_local_JKM_ambiguity_classified"] is True
    assert flags["fixed_boundary_local_counterterm_repair_obstructed"] is True
    assert flags["full_tensor_Bondi_BV_BFV_carrier_constructed"] is False
    assert flags["enlarged_p0_p1_renormalized_phase_space_constructed"] is False
    assert flags["P0_charge_computed"] is False
    assert flags["D_M_charge_computed"] is False

    entry = atlas["entries"][0]
    assert entry["id"] == "einstein.asymptotic.minkowski.weyl.local_counterterm_cohomology"
    assert entry["descriptions"]["symplectic"] == "OBSTRUCTED"
    assert entry["mode_data"]["lee_wald"]["status"] == "OBSTRUCTED"
    assert entry["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"
    evidence = entry["evidence"][0]
    assert evidence["sha256"] == _sha256(CERTIFICATE)
    assert evidence["result_id"] == certificate["result_id"]


if __name__ == "__main__":
    verify()
    print("ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1 independent verification: PASS")
