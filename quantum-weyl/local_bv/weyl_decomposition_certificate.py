"""Reproduce the exact Weyl--Schouten--Cotton foundation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .curvature import RIEMANN
from .hodge import Signature
from .specialization import WEYL, replace_riemann_by_weyl
from .tensors import TensorExpression, TensorFactor, TensorMonomial
from .weyl_decomposition import (
    COTTON,
    cotton_cyclic_relation,
    cotton_definition_relation,
    differentiated_ricci_decomposition_relation,
    expand_cotton_definitions,
    hodge_dualize_weyl_factor,
    ricci_decomposition_relation,
    tracefree_cotton_reduce,
    weyl_differential_bianchi_relation,
    weyl_hodge_square_contraction,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json"
)
RESULT_PATH = (
    QUANTUM_ROOT / "certificates" / "LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "weyl_decomposition_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "curvature.py",
        "hodge.py",
        "specialization.py",
        "tensors.py",
        "weyl_decomposition.py",
        "weyl_decomposition_certificate.py",
        "schema/weyl_decomposition_certificate.schema.json",
        "tests/test_specialization.py",
        "tests/test_weyl_decomposition.py",
        "tests/test_weyl_decomposition_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _differential_sign_audit() -> tuple[TensorExpression, TensorExpression]:
    cyclic_decomposition = -(
        differentiated_ricci_decomposition_relation((0, 1, 2, 3), 4)
        + differentiated_ricci_decomposition_relation((1, 4, 2, 3), 0)
        + differentiated_ricci_decomposition_relation((4, 0, 2, 3), 1)
    )
    schouten_form = TensorExpression(
        {
            monomial: coefficient
            for monomial, coefficient in cyclic_decomposition.terms.items()
            if all(factor.spec != RIEMANN for factor in monomial.factors)
        }
    )
    cotton_form = expand_cotton_definitions(
        weyl_differential_bianchi_relation()
    )
    return cotton_form, schouten_form


def build_certificate() -> dict[str, Any]:
    ricci = ricci_decomposition_relation()
    differentiated = differentiated_ricci_decomposition_relation()
    cotton_definition = cotton_definition_relation()
    cotton_cyclic = cotton_cyclic_relation()
    if len(ricci.terms) != 6 or len(differentiated.terms) != 6:
        raise AssertionError("Ricci decomposition term ledger drifted")
    if expand_cotton_definitions(cotton_cyclic):
        raise AssertionError(
            "Cotton cyclic identity does not follow from its definition"
        )

    cotton_form, schouten_form = _differential_sign_audit()
    if cotton_form != schouten_form:
        raise AssertionError("Cotton and Schouten differential identities disagree")

    trace_statuses = {}
    for name, slots in (
        ("first_second", (0, 0, 1)),
        ("first_third", (0, 1, 0)),
        ("second_third", (1, 0, 0)),
    ):
        traced = TensorExpression.monomial(
            TensorMonomial((TensorFactor(COTTON, slots),))
        )
        trace_statuses[name] = (
            "ZERO" if not tracefree_cotton_reduce(traced) else "NONZERO"
        )
    if set(trace_statuses.values()) != {"ZERO"}:
        raise AssertionError("Cotton trace reduction drifted")

    algebraic = TensorExpression.monomial(
        TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
    )
    differentiated_riemann = TensorExpression.monomial(
        TensorMonomial(
            (TensorFactor(RIEMANN, (0, 1, 2, 3), (4,)),)
        )
    )
    if not replace_riemann_by_weyl(algebraic):
        raise AssertionError("algebraic Riemann-to-Weyl restriction failed")
    try:
        replace_riemann_by_weyl(differentiated_riemann)
    except ValueError as error:
        derivative_guard = str(error)
    else:
        raise AssertionError("differentiated Riemann-to-Weyl shortcut did not fail")

    contraction_monomial = TensorMonomial(
        (
            TensorFactor(WEYL, (0, 1, 2, 3)),
            TensorFactor(WEYL, (0, 1, 2, 3)),
        )
    )
    contraction = TensorExpression.monomial(contraction_monomial)
    dual = hodge_dualize_weyl_factor(contraction_monomial, 0)
    if {monomial.spacetime_parity() for monomial in dual.terms} != {1}:
        raise AssertionError("Weyl Hodge dual did not enter the odd parity block")
    hodge_squares = {
        signature.value: weyl_hodge_square_contraction(signature)
        for signature in Signature
    }
    if hodge_squares[Signature.EUCLIDEAN.value] != contraction:
        raise AssertionError("Euclidean Weyl Hodge square drifted")
    if hodge_squares[Signature.LORENTZIAN.value] != -contraction:
        raise AssertionError("Lorentzian Weyl Hodge square drifted")

    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE",
        "result_state": "WEYL_DECOMPOSITION_INFRASTRUCTURE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Exact metric/Schouten/Cotton tensor conventions, algebraic and "
            "differentiated Ricci decomposition, cyclic Weyl--Cotton identity, "
            "fail-closed derivative specialization, and full-Weyl Hodge witnesses."
        ),
        "conventions": {
            "schouten": "P_ab=(R_ab-R*g_ab/(2*(n-1)))/(n-2)",
            "cotton": "A_abc=nabla_b(P_ca)-nabla_c(P_ba)",
            "ricci_decomposition": (
                "R_abcd=C_abcd+g_ac*P_bd-g_ad*P_bc-"
                "g_bc*P_ad+g_bd*P_ac"
            ),
            "hodge": "(*C)_abcd=epsilon_abef*C_efcd/2",
        },
        "checks": {
            "ricci_decomposition": "VERIFIED",
            "differentiated_ricci_decomposition": "VERIFIED",
            "cotton_antisymmetry": "VERIFIED",
            "cotton_cyclic_identity": "VERIFIED",
            "cotton_trace_reduction": "VERIFIED",
            "weyl_differential_bianchi_sign_audit": "VERIFIED",
            "derivative_shortcut_guard": "VERIFIED",
            "full_weyl_hodge_parity": "VERIFIED",
            "euclidean_hodge_square": "VERIFIED",
            "lorentzian_hodge_square": "VERIFIED",
            "tracefree_weyl_quotient": "NOT_COMPUTED",
            "parity_odd_invariant_enumeration": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "relations": {
            "ricci_term_count": len(ricci.terms),
            "ricci_sha256": ricci.canonical_hash(),
            "differentiated_ricci_term_count": len(differentiated.terms),
            "differentiated_ricci_sha256": differentiated.canonical_hash(),
            "cotton_definition_term_count": len(cotton_definition.terms),
            "cotton_definition_sha256": cotton_definition.canonical_hash(),
            "cotton_cyclic_term_count": len(cotton_cyclic.terms),
            "cotton_cyclic_sha256": cotton_cyclic.canonical_hash(),
            "expanded_cotton_cyclic_status": "ZERO",
            "weyl_differential_term_count": len(
                weyl_differential_bianchi_relation().terms
            ),
            "weyl_differential_sha256": (
                weyl_differential_bianchi_relation().canonical_hash()
            ),
            "expanded_differential_term_count": len(cotton_form.terms),
            "expanded_cotton_sha256": cotton_form.canonical_hash(),
            "expanded_schouten_sha256": schouten_form.canonical_hash(),
            "cotton_trace_statuses": trace_statuses,
        },
        "shortcut_guard": {
            "algebraic_restriction": "ALLOWED",
            "differentiated_restriction": "REJECTED",
            "error": derivative_guard,
        },
        "hodge": {
            "dual_parity": "odd",
            "dual_sha256": dual.canonical_hash(),
            "star_square": {"EUCLIDEAN": 1, "LORENTZIAN": -1},
            "euclidean_witness_sha256": hodge_squares[
                Signature.EUCLIDEAN.value
            ].canonical_hash(),
            "lorentzian_witness_sha256": hodge_squares[
                Signature.LORENTZIAN.value
            ].canonical_hash(),
        },
        "provenance": [
            {
                "source": "Boulanger, A Weyl-covariant tensor calculus",
                "url": "https://arxiv.org/abs/hep-th/0412314",
                "role": "Schouten and Weyl convention; Cotton/Weyl differential identity cross-check",
            },
            {
                "source": "Garcia, Hehl, Heinicke, Macias, The Cotton tensor in Riemannian spacetimes",
                "url": "https://arxiv.org/abs/gr-qc/0309008",
                "role": "independent Cotton convention and Bianchi provenance",
            },
        ],
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(source_manifest),
            "certificate_inputs_sha256": canonical_sha256(
                {
                    "relations": [
                        ricci.canonical_hash(),
                        differentiated.canonical_hash(),
                        cotton_definition.canonical_hash(),
                        cotton_cyclic.canonical_hash(),
                        weyl_differential_bianchi_relation().canonical_hash(),
                    ],
                    "hodge": {
                        key: value.canonical_hash()
                        for key, value in hodge_squares.items()
                    },
                }
            ),
        },
        "not_computed": [
            "the tracefree-Weyl image and kernel of the eight-dimensional "
            "four-dimensional Riemann quotient",
            "the parity-odd single-epsilon invariant basis",
            "Weyl-BRST closure, antifield descent, and H^{g,4}(s|d)",
            "anomaly or counterterm coefficients and the quantum master equation",
        ],
        "assumptions": [
            "All displayed abstract indices are lowered; repeated labels denote inverse-metric contraction.",
            "The Riemann sign convention is the one already frozen by the local curvature package.",
            "Cotton trace reduction is the irreducible consequence of the "
            "contracted Bianchi identity and the declared Schouten normalization.",
            "The Hodge witness tests a complete Weyl contraction; it does not enumerate the parity-odd invariant quotient.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": "exact Weyl--Schouten--Cotton decomposition infrastructure",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json"
        ),
        "assumptions": [
            "The classical import is unfrozen and no tracefree-Weyl quotient is claimed."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC infrastructure only. Differential specialization "
            "now fails closed unless Schouten/Cotton terms are explicit; full-Weyl "
            "Hodge signs are exact, while invariant and BRST quotients remain NOT_COMPUTED."
        ),
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    detailed = _render(build_certificate())
    result = _render(build_result_envelope())
    if args.emit:
        DETAILED_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        DETAILED_PATH.write_text(detailed, encoding="utf-8")
        RESULT_PATH.write_text(result, encoding="utf-8")
    if args.check:
        if DETAILED_PATH.read_text(encoding="utf-8") != detailed:
            raise SystemExit("detailed Weyl decomposition certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common Weyl decomposition result envelope is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL WEYL DECOMPOSITION FOUNDATIONS: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
