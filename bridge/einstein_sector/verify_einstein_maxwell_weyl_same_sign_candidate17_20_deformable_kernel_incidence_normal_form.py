"""Independent verifier for the deformable-kernel incidence normal form."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json"
)


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

    # Reconstruct the odd transvectant independently.
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")

    def A(v: tuple[sp.Symbol, ...]) -> sp.Matrix:
        return sp.Matrix(
            [
                [-v[3], 3 * v[2], -3 * v[1], v[0], 0],
                [-v[4], 2 * v[3], 0, -2 * v[1], v[0]],
                [0, -v[4], 3 * v[3], -3 * v[2], v[1]],
            ]
        )

    assert sp.simplify(A(f) * sp.Matrix(g) + A(g) * sp.Matrix(f)) == sp.zeros(3, 1)
    assert sp.simplify(A(f) * sp.Matrix(f)) == sp.zeros(3, 1)

    # Reconstruct both zero-node incidence points and the radial exit from I.
    a, b, delta, x, y, s = sp.symbols(
        "a b delta x y s", nonzero=True, real=True
    )
    c = delta + a * x - b * y
    assert sp.factor(c.subs({x: -delta / a, y: 0})) == 0
    assert sp.factor(c.subs({x: 0, y: delta / b})) == 0
    incidence_relation = {delta: -a * x + b * y}
    c_s = sp.factor(
        c.subs({x: s * x, y: s * y}).subs(incidence_relation)
    )
    assert c_s == sp.factor((1 - s) * (-a * x + b * y))

    # Independently check the Cartan radial section used in the path lift.
    u, r = sp.symbols("u r", real=True)
    inverse = (3 - sp.sqrt(9 - 8 * r**2)) / (2 * r)
    assert sp.simplify((r * u**2 - 3 * u + 2 * r).subs(u, inverse)) == 0
    assert (3 * u / (2 + u**2)).subs(u, 0) == 0
    assert (3 * u / (2 + u**2)).subs(u, 1) == 1

    flags = payload["classification"]
    assert flags["compactified_T3_kernel_moduli_defined"]
    assert flags["node_phase_and_lifted_rotation_quotient_defined"]
    assert flags["singular_stabilizers_and_boundary_occupations_retained"]
    assert flags["square_moment_path_lifting_certified"]
    assert flags["strict_opposite_sign_component_incidence_necessary"]
    assert flags["strict_opposite_sign_component_incidence_sufficient"]
    assert flags["candidate17_deformable_kernel_component_criterion_certified"]
    assert flags["candidate20_deformable_kernel_component_criterion_certified"]
    assert flags["both_strict_sign_boundary_incidence_sets_nonempty"]
    assert flags["fixed_direction_theorem_recovered_as_fibrewise_corollary"]
    assert not flags["every_admissible_component_meets_incidence"]
    assert not flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["global_zero_fibre_connected"]
    assert "if and only if" in payload["component_incidence_theorem"]["equivalence"]
    lift = payload["exact_algebra"]["cartan_square_path_lift"]
    assert "connected rotation orbit" in lift["connected_fibres"]
    assert "phase-real RP2" in lift["connected_fibres"]
    assert "oriented-frame bundle" in lift["path_lifting"]
    assert "compact-group slice theorem" in payload["compactified_moduli"]["component_path_property"]
    assert "nonemptiness alone does not prove" in payload["boundary_incidence"]["consequence"]
    assert "does not assert that every admissible component" in payload["claim_boundary"]
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_INCIDENCE_NORMAL_FORM verifier: PASS"
    )


if __name__ == "__main__":
    verify()
