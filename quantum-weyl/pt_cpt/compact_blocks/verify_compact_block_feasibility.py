#!/usr/bin/env python3
"""Independent exact verifier for compact-block structured metrics."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1.json"
SCHEMA = HERE / "schema/compact-block-structured-cpt-feasibility-v1.schema.json"
RECEIPT = HERE / "receipts/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1_TIER_RECEIPT.json"
REPORT = ROOT / "reports/phase2-cpt-compact-block-feasibility-2026-07-22.md"
ATLAS = ROOT / "residual_atlas/phase2-cpt-compact-block-feasibility-fragment-v1.json"

EXPECTED_INPUTS = {
    "branch_dictionary": ("bridge/certificates/einstein_weyl_relative_branch_dictionary.json", "0489e3a15956b9e397387476cd76974f6083692a85bc840b34d81d7893bae5aa"),
    "axial_lee_wald": ("bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json", "e3d59018c9ae4a1d65b2ca531f24534d553dc7da1e6386c1d4afb577effd05f8"),
    "axial_extra_gram": ("bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json", "024d580eb7f6c6be88fd561d52a53c716b53ee6ac487b95f8326db7484a36c7d"),
    "polar_lee_wald": ("bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json", "327cfacb304218b894b622f08a8ad0a2d8cb370a1cb041c69f58e343ac33ac76"),
    "radiative_restriction": ("bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json", "560f9e96be8ee095972e745544a709fdb6a8ac7a939658a21163bc173884c2bd"),
    "ell1_standard": ("bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json", "0413c43de06931565f18effe21bdc18d272d45d5d52d5007273935c6ea71a0ec"),
    "ell1_exceptional": ("bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json", "04399fac0172e73a74026401cdd3972028add3f54ca8f141bd00ef7a04adaaed"),
    "ell1_nonzero_k": ("bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json", "4d3839689270af952808b14adef4f00fcbabeb69ef17efcf7e6d18b7747340a3"),
    "residual_descent": ("bridge/certificates/EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1.json", "84bc53857ea4ca2620d0be42a3fae98432775868c1780411d0586de705cf08c9"),
    "cyclic_inertia": ("d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json", "affb12a8655671a06748a8fc6e2d38e8732478e4ef293b3cfea482597735bd9c"),
    "p2a_contract": ("quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json", "377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a"),
}
OUTPUTS = {
    "producer": HERE / "compact_block_feasibility.py", "verifier": Path(__file__), "schema": SCHEMA,
    "certificate": CERTIFICATE, "tests": HERE / "tests/test_compact_block_feasibility.py",
    "report": REPORT, "atlas": ATLAS,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mat(rows: list[list[str]], lam: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(v.replace("lambda", "lam"), locals={"lam": lam}) for v in row] for row in rows])


def _verify_exact(c: dict[str, Any]) -> None:
    lam, k, omega = sp.symbols("lambda k omega", positive=True, real=True)
    root = sp.sqrt(2 * lam)
    h2 = sp.diag(k**2 + lam - root, k**2 + lam + root, k**2 + lam - sp.Rational(2, 3), k**2 + lam - sp.Rational(2, 3))
    xs = sp.symbols("x0:16")
    x = sp.Matrix(4, 4, xs)
    if len(sp.linsolve(list(x*h2-h2*x), xs).free_symbols) != 6:
        raise AssertionError("independent commutant solve failed")
    comm = c["generic_blocks"]["computed_commutant"]
    h2full = sp.diag(h2[0,0], h2[0,0], h2[1,1], h2[1,1], h2[2,2], h2[2,2], h2[2,2], h2[2,2])
    ys = sp.symbols("y0:64"); y = sp.Matrix(8,8,ys)
    full_dim = len(sp.linsolve(list(y*h2full-h2full*y),ys).free_symbols)
    if comm["full_orientation_preserving_H_product_algebra"] != "M_2(C) direct-sum M_2(C) direct-sum M_4(C)" or comm["full_complex_dimension"] != full_dim or full_dim != 24:
        raise AssertionError("commutant classification mutation")
    if comm["uncertified_parity_label_used_to_shrink_full_commutant"] is not False:
        raise AssertionError("uncertified parity shrank full commutant")
    convention = c["generic_blocks"]["Hamiltonian_convention"]
    if convention["H_confused_with_H_squared"] is not False:
        raise AssertionError("H was confused with H squared")
    if "positive spectral square root" not in convention["H"] or "Comm(H)=Comm(H^2)" not in convention["commutant_identity"]:
        raise AssertionError("positive-frequency Hamiltonian convention missing")
    if sp.simplify((lam-root).subs(lam, 6)) <= 0 or sp.simplify((lam-sp.Rational(2,3)).subs(lam,6)) <= 0:
        raise AssertionError("physical squared-frequency positivity failed")
    if any(sp.simplify(value) == 0 for value in (2*root, sp.Rational(2,3)-root, root+sp.Rational(2,3))):
        raise AssertionError("physical shell separation failed")

    for parity in ("axial", "polar"):
        row = c["generic_blocks"]["exact_blocks"][parity]
        ge, r, gw, cq, eta = (_mat(row[name], lam) for name in (
            "Einstein_source_form", "relative_spectral_operator", "restricted_Weyl_q_form",
            "q_fundamental_symmetry_C0", "q_eta0_equals_Gq_C0"))
        if sp.simplify(ge*r-gw) != sp.zeros(2) or sp.simplify(cq*cq-sp.eye(2)) != sp.zeros(2):
            raise AssertionError("q construction failed")
        if sp.simplify(cq.T*gw-gw*cq) != sp.zeros(2) or sp.simplify(gw*cq-eta) != sp.zeros(2):
            raise AssertionError("q G-selfadjoint/eta relation failed")
        if parity == "axial":
            expected_det = lam*(9*lam-2)
        else:
            expected_det = (lam-2)*(9*lam-2)
        stored_det = sp.sympify(row["q_eta0_determinant"].replace("lambda", "lam"), locals={"lam": lam})
        if sp.simplify(eta.det()-expected_det) != 0 or sp.simplify(stored_det-expected_det) != 0:
            raise AssertionError("q eta positivity determinant failed")

    ga = _mat(c["generic_blocks"]["exact_blocks"]["axial"]["extra_action_Gram"], lam)
    ga = ga.xreplace({sp.Symbol("k"): k, sp.Symbol("omega"): omega})
    if sp.simplify(ga.det().subs(omega**2, k**2+lam-sp.Rational(2,3))-lam**4*(lam-2)*(9*lam-2)/3) != 0:
        raise AssertionError("axial extra determinant failed")
    gp = _mat(c["generic_blocks"]["exact_blocks"]["polar"]["extra_action_Gram"], lam).xreplace({sp.Symbol("k"): k})
    expected_gp = 9*lam**2*(lam-2)*(9*lam-2)*(3*k**2+3*lam-2)*(6*k**2+3*lam-2)**2
    if sp.simplify(gp.det()-expected_gp) != 0:
        raise AssertionError("polar extra determinant failed")


def verify_certificate(c: dict[str, Any], *, pins: bool = True) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(c)
    if pins:
        for role, (relative, expected) in EXPECTED_INPUTS.items():
            if _sha(ROOT/relative) != expected or c["source_refs"][role] != {"path": relative, "sha256": expected}:
                raise AssertionError(f"input pin drift: {role}")
    _verify_exact(c)
    eta = c["generic_blocks"]["all_structured_eta"]
    if "A_minus>0" not in eta["strict_positivity"] or "imaginary parts are odd" not in eta["real_involution"]:
        raise AssertionError("eta cone/reality weakened")
    if c["basis_invariance"]["unconstrained_eigenbasis_metric_accepted"] is not False:
        raise AssertionError("unconstrained eigenbasis metric accepted")
    gate = c["Mannheim_C_gate"]
    if gate["eta_is_not_C"] is not True or gate["genuine_Mannheim_C_certified"] is not False:
        raise AssertionError("eta promoted to genuine C")
    ledger = c["exceptional_and_residual_ledger"]
    if set(ledger) != {"ell1_standard", "ell1_extra_k_zero", "ell1_extra_nonzero_k", "global_generalized_zero_blocks", "residual_scope"}:
        raise AssertionError("exceptional/residual omission")
    if c["decision"]["particles_scattering_or_unitarity"] != "NOT_ESTABLISHED":
        raise AssertionError("quantum promotion")


def verify_receipt(r: dict[str, Any], c: dict[str, Any]) -> None:
    if r["subject_result_id"] != c["result_id"] or set(r["output_hashes"]) != set(OUTPUTS):
        raise AssertionError("receipt manifest mismatch")
    for role, path in OUTPUTS.items():
        if r["output_hashes"][role] != _sha(path):
            raise AssertionError(f"output hash mismatch: {role}")


def main() -> None:
    c = json.loads(CERTIFICATE.read_text())
    verify_certificate(c)
    mutations = [
        lambda x: x["generic_blocks"]["computed_commutant"].update(full_orientation_preserving_H_product_algebra="PARITY_GRADED_DIMENSION_12"),
        lambda x: x["generic_blocks"]["computed_commutant"].update(uncertified_parity_label_used_to_shrink_full_commutant=True),
        lambda x: x["generic_blocks"]["Hamiltonian_convention"].update(H_confused_with_H_squared=True),
        lambda x: x["basis_invariance"].update(unconstrained_eigenbasis_metric_accepted=True),
        lambda x: x["Mannheim_C_gate"].update(genuine_Mannheim_C_certified=True),
        lambda x: x["generic_blocks"]["exact_blocks"]["axial"].update(q_eta0_determinant="0"),
        lambda x: x["exceptional_and_residual_ledger"].pop("ell1_extra_k_zero"),
        lambda x: x["decision"].update(particles_scattering_or_unitarity="ESTABLISHED"),
    ]
    for mutate in mutations:
        mutant = copy.deepcopy(c); mutate(mutant)
        try: verify_certificate(mutant, pins=False)
        except (AssertionError, KeyError, TypeError, ValidationError): continue
        raise AssertionError("decisive mutation accepted")
    verify_receipt(json.loads(RECEIPT.read_text()), c)
    print(f"COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1 independent verification: PASS ({len(mutations)} mutations rejected)")


if __name__ == "__main__":
    main()
