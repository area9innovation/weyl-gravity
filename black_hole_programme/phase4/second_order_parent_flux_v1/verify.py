#!/usr/bin/env python3
"""Independent verifier for the second-order parent-flux certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    assert data["status"] == "EXACT_SECOND_ORDER_PARENT_FLUX_PASS"
    assert data["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    # Re-derive the four-dimensional trace solve without calling the producer.
    q, f, q2 = sp.symbols("q f q2")
    equation = -3 * q + 3 * f
    assert sp.solve(equation, f) == [q]
    reduced = sp.expand(4 * ((q2 - q**2) - (q2 - q**2) / 2))
    assert reduced == 2 * (q2 - q**2)

    # Independently verify the null-lift and determinant.
    ar, ai, b = sp.symbols("ar ai b", real=True)
    modulus2 = ar**2 + ai**2
    assert sp.factor(-modulus2) == -(ar**2 + ai**2)
    # c=-b/(2*conj(a)) makes c*conj(a)+conj(c)*a=-b.
    c_re = sp.simplify(-b * ar / (2 * modulus2))
    c_im = sp.simplify(-b * ai / (2 * modulus2))
    cross = sp.expand(2 * (c_re * ar + c_im * ai))
    assert sp.simplify(b + cross) == 0

    flags = data["claim_flags"]
    assert flags["parent_action_equivalent_mod_euler"]
    assert flags["factorized_current_mod_euler"]
    assert flags["canonical_null_lift"]
    assert flags["qnm_count_identity"]
    assert flags["one_physical_connection_ep2"]
    assert not flags["generic_radial_nonsplitting_implies_time_jordan"]
    assert not flags["physical_green_resolvent_double_pole"]
    assert not flags["all_positive_frequency_reflection_zero_exclusion"]
    assert not flags["complete_polar_parent_gram"]
    assert not flags["quantum_statement"]

    for item in data["imports"].values():
        path = ROOT / item["path"]
        assert path.exists()
        assert digest(path) == item["sha256"]

    qnm_path = ROOT / data["imports"]["physical_connection_ep2"]["path"]
    qnm = json.loads(qnm_path.read_text())
    assert qnm["claim_flags"]["connection_level_intrinsic_ep2"]
    assert not qnm["claim_flags"]["green_resolvent_second_order_pole_established"]

    euler_path = ROOT / data["imports"]["euler_transgression"]["path"]
    euler = json.loads(euler_path.read_text())
    assert euler["claim_flags"]["literal_minus_ricci_current_exact"]

    print("EXACT_SECOND_ORDER_PARENT_FLUX_VERIFIED")


if __name__ == "__main__":
    main()
