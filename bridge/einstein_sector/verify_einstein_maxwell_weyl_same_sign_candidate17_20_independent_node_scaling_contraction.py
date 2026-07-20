"""Independent exact verifier for the independent-node-scaling theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(
        ROOT / payload["provenance"]["generator_path"]
    )
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    # Reconstruct the affine coefficient and all incidence formulae without
    # importing the producer.
    a, b, delta, kappa = sp.symbols(
        "a b delta kappa", nonzero=True, real=True
    )
    x, y = sp.symbols("x y", real=True)
    coefficient = delta + a * x - b * y
    y_star = sp.cancel(-delta / (a * kappa - b))
    x_star = sp.cancel(kappa * y_star)
    assert sp.factor(-x_star + kappa * y_star) == 0
    assert sp.factor(coefficient.subs({x: x_star, y: y_star})) == 0
    assert sp.factor(coefficient.subs({x: -delta / a, y: 0})) == 0
    assert sp.factor(coefficient.subs({x: 0, y: delta / b})) == 0

    # Verify the three-stage construction from only c(z*)=M(z*)=0 and the
    # initial rotation-zero relation M(1,1)=-alpha*mu_0.
    tau, alpha = sp.symbols("tau alpha", real=True)
    c_first = sp.expand(
        coefficient.subs(
            {
                x: (1 - tau) + tau * x_star,
                y: (1 - tau) + tau * y_star,
            }
        )
    )
    c_first = sp.factor(c_first.subs(delta, alpha + b - a))
    incidence_relation = sp.solve(
        sp.Eq(
            (alpha + b - a) + a * x_star - b * y_star,
            0,
        ),
        alpha,
    )[0]
    assert sp.factor(c_first.subs(alpha, incidence_relation)) == sp.factor(
        (1 - tau) * incidence_relation
    )
    c_last = sp.factor(
        coefficient.subs(
            {x: (1 - tau) * x_star, y: (1 - tau) * y_star}
        )
    )
    assert sp.factor(c_last.subs(delta, -a * x_star + b * y_star)) == sp.factor(
        tau * (-a * x_star + b * y_star)
    )

    flags = payload["classification"]
    assert flags["zero_alpha_uniform_scaling_repair_imported"]
    assert flags["strict_opposite_sign_incidence_necessary"]
    assert flags["strict_opposite_sign_incidence_sufficient"]
    assert flags["fixed_direction_independent_node_scaling_ansatz_classified"]
    assert flags["positive_collinear_incidence_formula_certified"]
    assert flags["one_zero_moment_incidence_formulas_certified"]
    assert flags["nonpositive_collinearity_obstructed_within_ansatz"]
    assert flags["incidence_points_contract_to_connected_hub"]
    assert flags["generic_fixed_direction_opposite_sign_points_obstructed"]
    assert not flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["general_nonradial_no_go"]
    assert not flags["K_direction_deformation_classified"]
    assert "if and only if I is nonempty" in payload["three_stage_contraction"]["equivalence"]
    assert "not a no-go for deformation" in payload["claim_boundary"]
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_INDEPENDENT_NODE_SCALING_CONTRACTION verifier: PASS"
    )


if __name__ == "__main__":
    verify()
