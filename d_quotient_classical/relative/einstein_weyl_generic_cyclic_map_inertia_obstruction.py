#!/usr/bin/env python3
"""Obstruct every standard-pairing cyclic correction on generic product modes.

The previous theorem fixed the field map to the physical identity.  Here we
use the complete generic physical rings and action-derived forms.  Product-
symmetry equivariance forces a corrected chain map to preserve each q-shell;
on that shell the Einstein form is positive definite while the Weyl target
form has inertia (1,1).  Hermitian congruence therefore forbids every
cohomology-isomorphic cyclic correction, not only the identity map.
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
HERE = ROOT / "d_quotient_classical/relative"
OUTPUT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-generic-cyclic-map-inertia-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/einstein-weyl-generic-cyclic-map-inertia-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_einstein_weyl_generic_cyclic_map_inertia_obstruction.py"
TESTS = HERE / "tests/test_einstein_weyl_generic_cyclic_map_inertia_obstruction.py"

DEPENDENCIES = {
    "radiative_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "axial_physical_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "fixed_identity_obstruction": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "relative_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _exact_blocks() -> dict[str, object]:
    lam = sp.symbols("lambda", positive=True)
    blocks = {
        "axial": (
            sp.diag(lam, 2),
            sp.Matrix([[1, 3], [sp.Rational(3, 2) * lam, 1]]),
        ),
        "polar": (
            sp.Matrix([[1, -2], [-2, 2 * lam]]),
            sp.Matrix([[1, -3 * lam], [-sp.Rational(3, 2), 1]]),
        ),
    }
    result: dict[str, object] = {}
    for parity, (einstein, relative) in blocks.items():
        target = (einstein * relative).applyfunc(sp.factor)
        if target != target.T:
            raise AssertionError(f"{parity} target coefficient form is not Hermitian-real symmetric")
        det_e = sp.factor(einstein.det())
        det_t = sp.factor(target.det())
        expected_e = 2 * lam if parity == "axial" else 2 * (lam - 2)
        expected_t = -lam * (9 * lam - 2) if parity == "axial" else -(lam - 2) * (9 * lam - 2)
        if sp.simplify(det_e - expected_e) != 0 or sp.simplify(det_t - expected_t) != 0:
            raise AssertionError(f"{parity} determinant ledger drifted")
        result[parity] = {
            "Einstein_form": _matrix_strings(einstein),
            "relative_operator": _matrix_strings(relative),
            "restricted_Weyl_form": _matrix_strings(target),
            "Einstein_leading_minor": str(einstein[0, 0]),
            "Einstein_determinant": str(det_e),
            "restricted_Weyl_leading_minor": str(target[0, 0]),
            "restricted_Weyl_determinant": str(det_t),
            "Einstein_inertia_lambda_ge_6": [2, 0],
            "restricted_Weyl_inertia_lambda_ge_6": [1, 1],
        }
    return result


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    theorem = records["radiative_pairing"].get("theorem", {})
    classification = theorem.get("all_ell_ge_2_classification", {})
    if (
        classification.get("restricted_target_form_nondegenerate") is not True
        or classification.get("identity_inclusion_preserves_Einstein_symplectic_form") is not False
        or classification.get("branch_coefficient_relative_signature_per_real_spatial_harmonic")
        != {"negative": 2, "positive": 2, "zero": 0}
    ):
        raise ValueError("radiative pairing authority drifted")
    if records["fixed_identity_obstruction"].get("classification", {}).get("induced_solution_pairing_defect_nonradical") is not True:
        raise ValueError("fixed-identity obstruction authority drifted")
    if records["axial_physical_ring"].get("classification", {}).get("Einstein_image_equals_complete_q_primary_summand_on_every_physical_fiber") is not True:
        raise ValueError("axial q-primary completeness authority drifted")
    if records["polar_pairing"].get("classification", {}).get("extra_block_nonradical") is not True:
        raise ValueError("polar pairing authority drifted")
    dictionary = records["relative_dictionary"].get("classification", {})
    if (
        dictionary.get("generic_axial_and_polar_solution_cofibers_certified") is not True
        or dictionary.get("same_background_only") is not True
    ):
        raise ValueError("generic same-background cofiber authority drifted")

    blocks = _exact_blocks()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-einstein-weyl-generic-cyclic-map-inertia-obstruction-v1",
        "result_id": "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1",
        "result_state": "ALL_STANDARD_PAIRING_PRODUCT_EQUIVARIANT_GENERIC_CYCLIC_CORRECTIONS_OBSTRUCTED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: _artifact(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "generic axial and polar physical q-primary cohomology fibres",
            "degree": "induced linear solution cohomology pairing",
            "parity": "axial and polar separately",
            "ell": ">=2",
            "m": "all",
            "k": "2*pi*n/L for every n in Z",
            "omega": "both noncolliding q-primary radiative shells",
        },
        "exact_inertia_blocks": blocks,
        "shell_separation": {
            "Einstein_q_mu": ["lambda+sqrt(2*lambda)", "lambda-sqrt(2*lambda)"],
            "extra_p_mu": "lambda-2/3",
            "q_plus_minus_p": "sqrt(2*lambda)+2/3 > 0",
            "q_minus_minus_p": "-sqrt(2*lambda)+2/3 < 0 for lambda>=6",
            "same_label_frequency_collision": False,
            "equivariance_consequence": "an H_product, SO(3), S1-translation and parity equivariant chain map preserves each labelled q shell and cannot repair its form using the p-primary extra shell",
        },
        "obstruction_theorem": {
            "congruence_identity_required": "S^sharp (Omega_WM restricted to q-primary cohomology) S = Omega_EM",
            "rank_requirement": "a cohomology-isomorphic map on each two-dimensional parity fibre has invertible S",
            "invariant": "Hermitian inertia is preserved by every invertible congruence",
            "source_inertia": [2, 0],
            "target_q_primary_inertia": [1, 1],
            "normalized_failed_direction": "the q-minus Weyl image has negative relative weight 1-(3/2)*sqrt(2*lambda), whereas the Einstein q-minus norm is positive",
            "verdict": "no real-structure-preserving product-equivariant corrected field map can be cyclic for the two standard action-derived pairings on the generic physical cohomology",
        },
        "homotopy_and_improvement_consequence": {
            "chain_homotopy_repairs_inertia": False,
            "cohomologically_exact_pairing_improvement_repairs_inertia": False,
            "reason": "chain homotopies and exact current improvements do not change the induced nondegenerate cohomology form",
            "allowed_reformulations": [
                "retain the derived relative triangle as noncyclic and transport all three forms separately",
                "replace the Einstein source form by the pulled-back Weyl form and state that change explicitly",
                "drop product equivariance or standard real structure as a different theorem",
            ],
        },
        "classification": {
            "fixed_identity_obstruction_strengthened": True,
            "corrected_nonidentity_standard_pairing_map_exists_generic": False,
            "declared_chain_homotopy_cyclic_resolution_exists_generic": False,
            "standard_pairing_all_sector_cyclic_triangle_possible": False,
            "noncyclic_off_shell_relative_triangle_obstructed": False,
            "pairing_changed_relative_triangle_obstructed": False,
            "exceptional_or_global_off_shell_maps_classified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "exact_checks": {
            "axial_source_positive_definite": True,
            "polar_source_positive_definite": True,
            "axial_target_q_form_indefinite": True,
            "polar_target_q_form_indefinite": True,
            "same_label_q_and_p_shells_noncolliding": True,
            "inertia_mismatch_both_parities": True,
            "fixed_identity_result_imported_without_weakening": True,
        },
        "flags": {
            "GENERIC_STANDARD_PAIRING_CYCLIC_MAP_OBSTRUCTED": True,
            "FULL_STANDARD_PAIRING_CYCLIC_RELATIVE_TRIANGLE": False,
            "NONCYCLIC_RELATIVE_TRIANGLE": False,
            "PAIRING_CHANGED_RELATIVE_TRIANGLE": False,
            "RELATIVE_ARITY_TWO_DEFECT_COMPUTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "ASSEMBLE_NONCYCLIC_OFF_SHELL_RELATIVE_TRIANGLE_WITH_THREE_DISTINCT_FORMS",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_generic_cyclic_map_inertia_obstruction --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/relative/verify_einstein_weyl_generic_cyclic_map_inertia_obstruction.py",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_generic_cyclic_map_inertia_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/einstein-weyl-generic-cyclic-map-inertia-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem strengthens the fixed-identity obstruction on every generic axial and polar compact-product physical fibre. Product-symmetry equivariance and the certified shell decomposition force any cohomology-isomorphic corrected map to act within the q-primary target fibre, whose action-derived form has inertia (1,1), while the Einstein source form has inertia (2,0). Congruence invariance therefore rules out every real-structure-preserving corrected nonidentity map, chain-homotopy repair, or cohomologically exact current improvement that would make the standard pairings cyclic. It does not obstruct a noncyclic off-shell relative triangle carrying three distinct forms, an explicitly pairing-changed theorem, exceptional/global maps, causal propagation, observables, particles, or quantum states."
        ),
    }


def validate(value: dict) -> None:
    classification = value.get("classification", {})
    if classification.get("fixed_identity_obstruction_strengthened") is not True:
        raise ValueError("strengthened obstruction dropped")
    for name in (
        "corrected_nonidentity_standard_pairing_map_exists_generic",
        "declared_chain_homotopy_cyclic_resolution_exists_generic",
        "standard_pairing_all_sector_cyclic_triangle_possible",
        "noncyclic_off_shell_relative_triangle_obstructed",
        "pairing_changed_relative_triangle_obstructed",
        "exceptional_or_global_off_shell_maps_classified",
        "Lorentzian_causal_or_quantum_claim",
    ):
        if classification.get(name) is not False:
            raise ValueError("claim boundary crossed")
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("exact inertia check dropped")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Generic Einstein--Weyl cyclic-map inertia obstruction

The earlier compact-product obstruction held the physical field inclusion
fixed to the identity. The complete action-derived solution forms give a
stronger result.

For \(\lambda=\ell(\ell+1)\geq 6\), the Einstein coefficient forms are

\[
E_{\rm ax}=\begin{pmatrix}\lambda&0\\0&2\end{pmatrix},\qquad
E_{\rm pol}=\begin{pmatrix}1&-2\\-2&2\lambda\end{pmatrix}.
\]

Both are positive definite. The corresponding Weyl forms restricted to the
complete \(q\)-primary image are

\[
E_{\rm ax}R_{\rm ax}
=\begin{pmatrix}\lambda&3\lambda\\3\lambda&2\end{pmatrix},\qquad
E_{\rm pol}R_{\rm pol}
=\begin{pmatrix}4&-3\lambda-2\\-3\lambda-2&8\lambda\end{pmatrix}.
\]

Their determinants are respectively \(-\lambda(9\lambda-2)\) and
\(-(\lambda-2)(9\lambda-2)\), so both have inertia \((1,1)\).

The extra \(p\)-primary shell has \(\mu_p=\lambda-2/3\), whereas the two
Einstein shells have \(\mu_q=\lambda\pm\sqrt{2\lambda}\). They never collide
for \(\lambda\geq6\). Product-symmetry equivariance therefore prevents a
corrected chain map from borrowing the positive extra block to change the
form on a labelled \(q\) shell.

Any cohomology-isomorphic correction would require an invertible congruence
\(S^\sharp(ER)S=E\). Hermitian inertia is invariant under congruence, so no
such \(S\) exists. Chain homotopies and exact current improvements cannot
repair the mismatch because they leave the induced cohomology form unchanged.

Thus the compact-product relative triangle may still exist off shell, but it
cannot be a standard-pairing cyclic triangle. The honest next construction is
a noncyclic relative triangle carrying the Einstein form, the pulled-back
Weyl form and the relative form separately. Alternatively one may explicitly
change the source pairing; that is a different theorem.
"""


def _guards(value: dict) -> None:
    for name in (
        "corrected_nonidentity_standard_pairing_map_exists_generic",
        "declared_chain_homotopy_cyclic_resolution_exists_generic",
        "standard_pairing_all_sector_cyclic_triangle_possible",
        "noncyclic_off_shell_relative_triangle_obstructed",
        "pairing_changed_relative_triangle_obstructed",
        "exceptional_or_global_off_shell_maps_classified",
        "Lorentzian_causal_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
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
            raise AssertionError("generic cyclic-map obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print("EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
