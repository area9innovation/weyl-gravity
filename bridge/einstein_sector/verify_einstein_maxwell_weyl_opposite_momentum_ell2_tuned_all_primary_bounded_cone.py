"""Independent verifier for the tuned all-primary bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for entry in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / entry["path"]) == entry["sha256"]

    root = sp.sqrt(3)
    k_squared = 2 * root - sp.Rational(7, 6)
    input_squares = {
        "minus": sp.Rational(29, 6),
        "extra": 2 * root + sp.Rational(25, 6),
        "plus": sp.Rational(29, 6) + 4 * root,
    }
    frequencies = {name: sp.sqrt(value) for name, value in input_squares.items()}
    outputs = {"zero": sp.Integer(0)}
    order = ["minus", "extra", "plus"]
    for index, left in enumerate(order):
        for right in order[index:]:
            if left == right:
                outputs[f"two_{left}"] = 4 * input_squares[left]
            else:
                outputs[f"{left}_plus_{right}"] = sp.expand((frequencies[left] + frequencies[right]) ** 2)
                outputs[f"{right}_minus_{left}"] = sp.expand((frequencies[right] - frequencies[left]) ** 2)
    momenta = {"K_zero": sp.Integer(0), "K_two_k": 4 * k_squared}
    collisions = []
    rows = payload["collision_census"]["checks"]
    assert len(rows) == 140
    for row in rows:
        frequency = outputs[row["frequency"]]
        momentum = momenta[row["momentum"]]
        ell = row["ell"]
        if ell == 1:
            residual = (frequency - momentum - 4) * (frequency - momentum - sp.Rational(4, 3))
        else:
            eigenvalue = ell * (ell + 1)
            residual = (
                frequency - momentum - eigenvalue + sp.Rational(2, 3)
                if row["target"] == "p"
                else (frequency - momentum - eigenvalue) ** 2 - 2 * eigenvalue
            )
        collision = residual.equals(0) is True
        assert row["collision"] is collision
        if collision:
            collisions.append((row["frequency"], row["momentum"], ell, row["target"]))
        else:
            assert sp.simplify(sp.sympify(row["nonzero_witness"]["residual"]) - residual) == 0
            assert sp.sympify(row["nonzero_witness"]["minimal_polynomial_constant"]) != 0
    assert collisions == [("two_minus", "K_zero", 4, "p")]

    minus_squared = input_squares["minus"]
    r_extra = sp.sqrt(minus_squared / input_squares["extra"])
    r_plus = sp.sqrt(minus_squared / input_squares["plus"])
    assert 0 < float(r_plus.evalf()) < float(r_extra.evalf()) < 1
    interval = payload["nonzero_bounded_components"]["complete_imbalance_interval"]
    assert sp.simplify(sp.sympify(interval["lower"]) - (1 - r_extra) / (1 + r_extra)) == 0
    assert sp.simplify(sp.sympify(interval["upper"]) - (1 + r_extra) / (1 - r_extra)) == 0

    n_plus, n_minus = sp.symbols("N_plus N_minus", nonnegative=True)
    e_total = r_extra**2 * (n_plus + n_minus)
    e_difference = r_extra * (n_plus - n_minus)
    e_plus = (e_total + e_difference) / 2
    e_minus = (e_total - e_difference) / 2
    omega_minus = sp.sqrt(minus_squared)
    omega_extra = sp.sqrt(input_squares["extra"])
    assert sp.simplify(omega_extra**2 * (e_plus + e_minus) - omega_minus**2 * (n_plus + n_minus)) == 0
    assert sp.simplify(omega_extra * (e_plus - e_minus) - omega_minus * (n_plus - n_minus)) == 0

    flags = payload["classification"]
    assert flags["extra_primary_inputs_create_no_new_shell_collision"] is True
    assert flags["complete_tuned_axisymmetric_all_primary_bounded_cone_classified"] is True
    assert flags["positive_branch_moment_polytope_complete"] is True
    assert flags["causal_or_quantum_claim"] is False
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert payload["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_ALL_PRIMARY_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
