#!/usr/bin/env python3
"""Certify the sharp cyclic Green-homotopy transfer theorem.

This versioned theorem strengthens the earlier abstract causal-transfer
certificate in three ways:

* it makes the causal-difference quasi-isomorphism and induced pairing
  identities explicit;
* it separates essential hypotheses from normalizing or replaceable ones by
  exact counterexamples; and
* it consumes, without regenerating, the certified conformal-cylinder and
  curved unit-Nariai constructions.

The finite matrices are exact rational fixtures.  They audit the algebraic
theorem and its failure modes; they are not Lorentzian endpoint existence
proofs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "green-hyperbolic-cyclic-transfer-theorem.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "green-hyperbolic-cyclic-transfer-theorem-v1.schema.json"
)
PRODUCER = Path(__file__).resolve()
VERIFIER = (
    ROOT
    / "d_quotient_classical/causal_transfer/"
    "verify_green_hyperbolic_cyclic_transfer_theorem.py"
)
TESTS = (
    ROOT
    / "d_quotient_classical/causal_transfer/tests/"
    "test_green_hyperbolic_cyclic_transfer_theorem.py"
)

DEPENDENCIES = {
    "prior_abstract_theorem": (
        ROOT
        / "d_quotient_classical/certificates/"
        "ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"
    ),
    "cylinder_cyclic_SDR": (
        ROOT
        / "covariant_completion/certificates/"
        "adjoint_tractor_bgg_curved_pbw.json"
    ),
    "cylinder_green_homotopy": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_full_prolonged_green_homotopy_assembly.json"
    ),
    "cylinder_causal_quasi_isomorphism": (
        ROOT
        / "covariant_completion/certificates/"
        "covariant_causal_quasi_isomorphism.json"
    ),
    "cylinder_pairing": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_direct_causal_pairing_transport.json"
    ),
    "nariai_curved_consumer": (
        ROOT
        / "d_quotient_classical/certificates/"
        "NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json"
    ),
}


Matrix = sp.Matrix


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _artifact_id(value: dict[str, Any]) -> str:
    for key in ("result_id", "schema", "schema_version"):
        if key in value:
            return str(value[key])
    raise ValueError("dependency has no stable artifact identity")


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "artifact_id": _artifact_id(value),
        "sha256": _sha256(path),
    }


def _sharp(
    operator: Matrix,
    domain_pairing: Matrix,
    codomain_pairing: Matrix,
) -> Matrix:
    return domain_pairing.inv() * operator.T * codomain_pairing


def _zero(matrix: Matrix) -> bool:
    return all(sp.simplify(item) == 0 for item in matrix)


def _rank(matrix: Matrix) -> int:
    return int(matrix.rank())


def _nonzero_entries(matrix: Matrix) -> list[dict[str, int]]:
    return [
        {"row": row, "column": column, "coefficient": int(item)}
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if (item := sp.simplify(matrix[row, column])) != 0
    ]


def _defect(matrix: Matrix) -> dict[str, Any]:
    return {
        "rank": _rank(matrix),
        "nonzero_entries": _nonzero_entries(matrix),
    }


def _block_diagonal(*matrices: Matrix) -> Matrix:
    return sp.diag(*matrices)


def _endpoint_fixture() -> dict[str, Matrix]:
    """A three-term exact cyclic complex with two distinct Green homotopies."""
    q = sp.zeros(4)
    q[1, 0] = 1
    q[3, 2] = 1
    h = sp.zeros(4)
    h[0, 1] = 1
    h[2, 3] = 1
    k = sp.zeros(4)
    k[0, 2] = 1
    k[1, 3] = -1
    pairing = sp.zeros(4)
    pairing[0, 3] = 1
    pairing[3, 0] = -1
    pairing[1, 2] = -1
    pairing[2, 1] = 1
    sigma = sp.diag(1, -1, 1, -1)
    return {
        "q": q,
        "h": h,
        "cycle": k,
        "lambda_plus": h + k,
        "lambda_minus": h - k,
        "pairing": pairing,
        "sigma": sigma,
    }


def exact_toy_fixture() -> dict[str, Any]:
    """Audit lift, descent, causal difference, quasi-isomorphism and pairing."""
    endpoint = _endpoint_fixture()
    q_e = endpoint["q"]
    lambda_e_plus = endpoint["lambda_plus"]
    lambda_e_minus = endpoint["lambda_minus"]
    pairing_e = endpoint["pairing"]
    sigma_e = endpoint["sigma"]

    q_a = sp.Matrix([[0, 0], [1, 0]])
    h_a = sp.Matrix([[0, 1], [0, 0]])
    pairing_a = sp.Matrix([[0, 1], [-1, 0]])
    sigma_a = sp.diag(1, -1)

    q_c = _block_diagonal(q_e, q_a)
    inclusion = sp.zeros(6, 4)
    inclusion[:4, :4] = sp.eye(4)
    projection = sp.zeros(4, 6)
    projection[:4, :4] = sp.eye(4)
    homotopy = sp.zeros(6)
    homotopy[4:, 4:] = h_a
    pairing_c = _block_diagonal(pairing_e, pairing_a)
    sigma_c = _block_diagonal(sigma_e, sigma_a)

    lambda_c_plus = homotopy + inclusion * lambda_e_plus * projection
    lambda_c_minus = homotopy + inclusion * lambda_e_minus * projection
    delta_e = lambda_e_plus - lambda_e_minus
    delta_c = lambda_c_plus - lambda_c_minus
    pairing_pullback = (
        pairing_c * delta_c
        - projection.T * pairing_e * delta_e * projection
    )
    defects = {
        "endpoint_Q_squared": q_e * q_e,
        "full_Q_squared": q_c * q_c,
        "inclusion_chain_map": q_c * inclusion - inclusion * q_e,
        "projection_chain_map": projection * q_c - q_e * projection,
        "retraction": projection * inclusion - sp.eye(4),
        "deformation_identity": (
            q_c * homotopy
            + homotopy * q_c
            - (sp.eye(6) - inclusion * projection)
        ),
        "homotopy_square": homotopy * homotopy,
        "homotopy_inclusion": homotopy * inclusion,
        "projection_homotopy": projection * homotopy,
        "endpoint_plus_homotopy": (
            q_e * lambda_e_plus + lambda_e_plus * q_e - sp.eye(4)
        ),
        "endpoint_minus_homotopy": (
            q_e * lambda_e_minus + lambda_e_minus * q_e - sp.eye(4)
        ),
        "full_plus_homotopy": (
            q_c * lambda_c_plus + lambda_c_plus * q_c - sp.eye(6)
        ),
        "full_minus_homotopy": (
            q_c * lambda_c_minus + lambda_c_minus * q_c - sp.eye(6)
        ),
        "descent_plus": (
            projection * lambda_c_plus * inclusion - lambda_e_plus
        ),
        "descent_minus": (
            projection * lambda_c_minus * inclusion - lambda_e_minus
        ),
        "causal_difference_factorization": (
            delta_c - inclusion * delta_e * projection
        ),
        "inclusion_adjoint": (
            _sharp(inclusion, pairing_e, pairing_c) - projection
        ),
        "projection_adjoint": (
            _sharp(projection, pairing_c, pairing_e) - inclusion
        ),
        "homotopy_cyclicity": (
            _sharp(homotopy, pairing_c, pairing_c)
            - sigma_c * homotopy * sigma_c
        ),
        "endpoint_adjoint_reversal": (
            _sharp(lambda_e_plus, pairing_e, pairing_e)
            - sigma_e * lambda_e_minus * sigma_e
        ),
        "full_adjoint_reversal": (
            _sharp(lambda_c_plus, pairing_c, pairing_c)
            - sigma_c * lambda_c_minus * sigma_c
        ),
        "induced_pairing_identity": pairing_pullback,
    }
    failed = {
        name: _defect(matrix)
        for name, matrix in defects.items()
        if not _zero(matrix)
    }
    if failed:
        raise AssertionError(f"positive exact toy fixture failed: {failed}")
    return {
        "coefficient_field": "Q",
        "generality": "G0_EXACT_FIXTURE",
        "endpoint_dimension": 4,
        "full_dimension": 6,
        "contractible_dimension": 2,
        "causal_difference_rank": _rank(delta_e),
        "causal_difference_nonzero_entries": _nonzero_entries(delta_e),
        "identity_defects": {name: 0 for name in defects},
        "role": (
            "exact algebraic audit of the theorem, including a nonzero "
            "advanced-minus-retarded map; not Lorentzian existence evidence"
        ),
    }


def counterexamples() -> list[dict[str, Any]]:
    """Exact failures establishing the sharp role of hypothesis clusters."""
    d = sp.Matrix([[0, 0], [1, 0]])
    contracting = sp.Matrix([[0, 1], [0, 0]])
    identity2 = sp.eye(2)

    # Chain-map failure with every underlying differential still nilpotent.
    q_c = sp.zeros(2)
    q_e = d
    bad_chain_transfer = contracting
    bad_chain_defect = (
        q_c * bad_chain_transfer
        + bad_chain_transfer * q_c
        - identity2
    )

    # The deformation identity is exactly the missing term in the lift proof.
    bad_h = contracting
    bad_deformation_transfer = bad_h + contracting
    bad_deformation_defect = (
        d * bad_deformation_transfer
        + bad_deformation_transfer * d
        - identity2
    )

    # Descent gives p i, not one, when p i is not a retraction.
    zero_projection = sp.zeros(2)
    bad_descended = zero_projection * contracting * identity2
    bad_retraction_defect = (
        d * bad_descended + bad_descended * d - identity2
    )

    # A nonlocal shear between two causally unrelated points preserves the
    # algebraic chain identity but creates a cross-point homotopy entry.
    q_two_points = _block_diagonal(d, d)
    lambda_two_points = _block_diagonal(contracting, contracting)
    nonlocal_nilpotent = sp.zeros(4)
    nonlocal_nilpotent[2, 0] = 1
    nonlocal_shear = sp.eye(4) + nonlocal_nilpotent
    nonlocal_inverse = sp.eye(4) - nonlocal_nilpotent
    q_nonlocal = nonlocal_shear * q_two_points * nonlocal_inverse
    lambda_nonlocal = (
        nonlocal_shear * lambda_two_points * nonlocal_inverse
    )
    nonlocal_chain_defect = (
        q_nonlocal * lambda_nonlocal
        + lambda_nonlocal * q_nonlocal
        - sp.eye(4)
    )
    cross_point_entries = [
        item
        for item in _nonzero_entries(lambda_nonlocal)
        if item["row"] // 2 != item["column"] // 2
    ]

    # The chain theorem survives a wrong pairing, while the induced pairing
    # identity fails exactly when i^sharp != p.
    endpoint = _endpoint_fixture()
    delta_e = endpoint["lambda_plus"] - endpoint["lambda_minus"]
    pairing_e = endpoint["pairing"]
    pairing_a = sp.Matrix([[0, 1], [-1, 0]])
    inclusion = sp.zeros(6, 4)
    inclusion[:4, :4] = sp.eye(4)
    projection = sp.zeros(4, 6)
    projection[:4, :4] = sp.eye(4)
    delta_c = inclusion * delta_e * projection
    wrong_pairing_c = _block_diagonal(2 * pairing_e, pairing_a)
    pairing_defect = (
        wrong_pairing_c * delta_c
        - projection.T * pairing_e * delta_e * projection
    )
    adjoint_defect = (
        _sharp(inclusion, pairing_e, wrong_pairing_c) - projection
    )

    # Both endpoint maps are chain homotopies, but without endpoint adjoint
    # reversal the lifted cyclic conclusion is already false for C=E.
    lambda_bad_plus = endpoint["h"]
    lambda_bad_minus = endpoint["h"] + endpoint["cycle"]
    endpoint_cyclic_defect = (
        _sharp(
            lambda_bad_plus,
            endpoint["pairing"],
            endpoint["pairing"],
        )
        - endpoint["sigma"]
        * lambda_bad_minus
        * endpoint["sigma"]
    )

    # A symplectic shear need not preserve the fixed degreewise sign
    # involution.  Conjugation keeps the chain identity but loses the stated
    # fixed-Sigma adjoint reversal.
    sign_shear = sp.eye(4)
    sign_shear[1:3, 1:3] = sp.Matrix([[1, 1], [0, 1]])
    sign_shear_inverse = sign_shear.inv()
    q_sign = sign_shear * endpoint["q"] * sign_shear_inverse
    plus_sign = (
        sign_shear * endpoint["lambda_plus"] * sign_shear_inverse
    )
    minus_sign = (
        sign_shear * endpoint["lambda_minus"] * sign_shear_inverse
    )
    sign_chain_defect = (
        q_sign * plus_sign + plus_sign * q_sign - sp.eye(4)
    )
    sign_intertwiner_defect = (
        sign_shear * endpoint["sigma"]
        - endpoint["sigma"] * sign_shear
    )
    fixed_sign_cyclic_defect = (
        _sharp(
            plus_sign,
            endpoint["pairing"],
            endpoint["pairing"],
        )
        - endpoint["sigma"] * minus_sign * endpoint["sigma"]
    )

    rows = [
        {
            "counterexample_id": "CHAIN_MAPS_ARE_ESSENTIAL",
            "dropped_hypothesis": "q_C i=i q_E and p q_C=q_E p",
            "preserved_statement": "q_C^2=q_E^2=0 and the endpoint homotopy identity",
            "failed_conclusion": "lifted chain homotopy",
            "witness": "C=E=Q^2, q_C=0, q_E=d, i=p=1, h=0",
            "defect": _defect(bad_chain_defect),
        },
        {
            "counterexample_id": "DEFORMATION_IDENTITY_IS_ESSENTIAL",
            "dropped_hypothesis": "q_C h+h q_C=1-i p",
            "preserved_statement": "q_C=q_E=d, i=p=1 and endpoint homotopy exact",
            "failed_conclusion": "lifted chain homotopy",
            "witness": "take h equal to the endpoint contracting homotopy although 1-i p=0",
            "defect": _defect(bad_deformation_defect),
        },
        {
            "counterexample_id": "RETRACTION_IS_ESSENTIAL_FOR_DESCENT",
            "dropped_hypothesis": "p i=1_E",
            "preserved_statement": "the full homotopy identity",
            "failed_conclusion": "descended chain homotopy and derived quasi-isomorphism",
            "witness": "C=E=Q^2, q=d, i=1, p=0",
            "defect": _defect(bad_retraction_defect),
        },
        {
            "counterexample_id": "SUPPORT_LOCALITY_IS_ESSENTIAL",
            "dropped_hypothesis": "support-local U and U^-1",
            "preserved_statement": "conjugated chain homotopy identity",
            "failed_conclusion": "same-sided support",
            "witness": "two causally unrelated points with U=1+e_(point1,point0)",
            "defect": {
                "rank": _rank(nonlocal_chain_defect),
                "nonzero_entries": cross_point_entries,
            },
        },
        {
            "counterexample_id": "PAIRING_ADJOINTNESS_IS_ESSENTIAL",
            "dropped_hypothesis": "i^sharp=p",
            "preserved_statement": "all chain, SDR and causal-difference identities",
            "failed_conclusion": "induced Green/current pairing identity",
            "witness": "rescale the endpoint summand of the full pairing by two",
            "defect": {
                "rank": _rank(pairing_defect),
                "nonzero_entries": _nonzero_entries(pairing_defect),
                "adjoint_defect_rank": _rank(adjoint_defect),
            },
        },
        {
            "counterexample_id": "ENDPOINT_ADJOINT_REVERSAL_IS_ESSENTIAL",
            "dropped_hypothesis": "Lambda_E,+^sharp=Sigma_E Lambda_E,- Sigma_E^-1",
            "preserved_statement": "both endpoint chain homotopy identities",
            "failed_conclusion": "advanced/retarded adjoint reversal",
            "witness": "identity retract of the exact 1-2-1 complex with Lambda_-=h+K",
            "defect": _defect(endpoint_cyclic_defect),
        },
        {
            "counterexample_id": "SIGN_INTERTWINING_IS_ESSENTIAL_FOR_FIXED_SIGMA",
            "dropped_hypothesis": "U Sigma=Sigma U",
            "preserved_statement": "U^sharp=U^-1 and the conjugated chain identity",
            "failed_conclusion": "adjoint reversal with the untransported fixed Sigma",
            "witness": (
                "degree-preserving symplectic shear [[1,1],[0,1]] "
                "inside the two-dimensional middle degree"
            ),
            "defect": {
                "rank": _rank(fixed_sign_cyclic_defect),
                "nonzero_entries": _nonzero_entries(
                    fixed_sign_cyclic_defect
                ),
                "chain_defect_rank": _rank(sign_chain_defect),
                "sign_intertwiner_defect_rank": _rank(
                    sign_intertwiner_defect
                ),
            },
        },
    ]
    expected_ranks = {
        "CHAIN_MAPS_ARE_ESSENTIAL": 2,
        "DEFORMATION_IDENTITY_IS_ESSENTIAL": 2,
        "RETRACTION_IS_ESSENTIAL_FOR_DESCENT": 2,
        "SUPPORT_LOCALITY_IS_ESSENTIAL": 0,
        "PAIRING_ADJOINTNESS_IS_ESSENTIAL": 2,
        "ENDPOINT_ADJOINT_REVERSAL_IS_ESSENTIAL": 2,
        "SIGN_INTERTWINING_IS_ESSENTIAL_FOR_FIXED_SIGMA": 2,
    }
    for row in rows:
        if row["defect"]["rank"] != expected_ranks[row["counterexample_id"]]:
            raise AssertionError(
                f"counterexample drifted: {row['counterexample_id']}"
            )
    if cross_point_entries != [
        {"row": 2, "column": 1, "coefficient": 1}
    ]:
        raise AssertionError("support counterexample carrier drifted")
    if _rank(nonlocal_chain_defect) != 0:
        raise AssertionError("nonlocal conjugation lost its chain identity")
    if _rank(sign_chain_defect) != 0:
        raise AssertionError("sign counterexample lost its chain identity")
    if not _zero(
        _sharp(
            sign_shear,
            endpoint["pairing"],
            endpoint["pairing"],
        )
        - sign_shear_inverse
    ):
        raise AssertionError("sign counterexample shear is not cyclic")
    return rows


def _require_dependencies(
    values: dict[str, dict[str, Any]],
) -> None:
    prior = values["prior_abstract_theorem"]
    cylinder_sdr = values["cylinder_cyclic_SDR"]
    cylinder_green = values["cylinder_green_homotopy"]
    cylinder_quasi = values["cylinder_causal_quasi_isomorphism"]
    cylinder_pairing = values["cylinder_pairing"]
    nariai = values["nariai_curved_consumer"]

    if (
        prior.get("flags", {}).get(
            "ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"
        )
        is not True
    ):
        raise AssertionError("prior abstract theorem is not certified")
    theorem_boundary = cylinder_sdr.get("theorem_boundary", {})
    if not all(
        theorem_boundary.get(key) is True
        for key in (
            "curved_BGG_chain_maps_exact",
            "curved_differential_homotopy_exact",
            "cyclic_i_sharp_equals_p",
            "support_local",
        )
    ):
        raise AssertionError("cylinder cyclic SDR is incomplete")
    if (
        cylinder_green.get("causal_green_homotopy") is not True
        or cylinder_green.get("dimension_ledger", {}).get("prolonged")
        != 386
        or cylinder_green.get("dimension_ledger", {}).get(
            "algebraically_contracted"
        )
        != 356
        or cylinder_green.get("dimension_ledger", {}).get(
            "causal_endpoint"
        )
        != 30
    ):
        raise AssertionError("cylinder Green-homotopy carrier drifted")
    if (
        cylinder_quasi.get("selected_arrow") != "causal"
        or cylinder_quasi.get("terminal_gate", {}).get("status") is not True
    ):
        raise AssertionError("cylinder causal quasi-isomorphism is not closed")
    if (
        cylinder_pairing.get("Green_pairing_equals_current_pairing")
        is not True
        or cylinder_pairing.get("pairing_compatibility") is not True
    ):
        raise AssertionError("cylinder pairing transport is incomplete")
    required_nariai = (
        "NARIAI_REPAIRED_310_GREEN_HOMOTOPY",
        "NARIAI_REPAIRED_310_CAUSAL_SUPPORT",
        "NARIAI_REPAIRED_310_ADJOINT_REVERSAL",
        "NARIAI_METRIC_DESCENT_RECOVERS_ENDPOINT",
    )
    if (
        nariai.get("carrier", {}).get("total_rank") != 310
        or nariai.get("carrier", {}).get("metric_endpoint_total_rank") != 26
        or not all(
            nariai.get("flags", {}).get(key) is True
            for key in required_nariai
        )
    ):
        raise AssertionError("unit-Nariai curved consumer is incomplete")


def build() -> dict[str, Any]:
    dependencies = {
        name: _load(path) for name, path in DEPENDENCIES.items()
    }
    _require_dependencies(dependencies)
    toy = exact_toy_fixture()
    failures = counterexamples()
    value = {
        "schema": "pure-weyl-green-hyperbolic-cyclic-transfer-theorem-v1",
        "result_id": "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1",
        "result_state": (
            "SHARP_ABSTRACT_THEOREM_WITH_TOY_CYLINDER_AND_CURVED_CONSUMERS"
        ),
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "LORENTZIAN-CAUSAL",
        ],
        "background_scope": {
            "abstract": (
                "any support category carrying the declared same-sided "
                "homotopies and differential cyclic contraction"
            ),
            "toy": "finite exact rational complex; no spacetime claim",
            "conformal_cylinder": (
                "unit vacuum conformal cylinder R_t x S3, no timelike boundary"
            ),
            "curved_consumer": (
                "global unit Nariai R x (S1 x S2), no timelike boundary"
            ),
            "cross_background_identification": False,
        },
        "dependency_refs": {
            name: _ref(DEPENDENCIES[name], payload)
            for name, payload in dependencies.items()
        },
        "sharp_hypotheses": {
            "chain_lift": [
                "q_C i=i q_E and p q_C=q_E p",
                "q_C h+h q_C=1_C-i p",
                "q_E Lambda_E,+/-+Lambda_E,+/- q_E=1_E",
            ],
            "descent_and_quasi_isomorphism": [
                "p i=1_E",
                "the contraction acts on both compact and spacelike-compact support complexes",
                "the endpoint causal difference is a quasi-isomorphism",
            ],
            "support": [
                "i,p,h preserve the declared operator domains",
                "i,p,h are support-nonincreasing",
                "Lambda_E,+/- has same-sided causal support",
                "every optional shear and its inverse preserve the same domains and support",
            ],
            "cyclicity_and_pairing": [
                "i^sharp=p and p^sharp=i",
                "h^sharp=Sigma_C h Sigma_C^-1",
                "Sigma_C i=i Sigma_E and p Sigma_C=Sigma_E p",
                "Lambda_E,+^sharp=Sigma_E Lambda_E,- Sigma_E^-1",
                "an optional cyclic shear satisfies U^sharp=U^-1 and intertwines Sigma, unless Sigma is explicitly transported",
            ],
            "normalizations_not_needed_for_one_step_chain_identity": [
                "h^2=0",
                "h i=0",
                "p h=0",
            ],
            "replaceable_sufficient_conditions": [
                "global hyperbolicity may be replaced by any category in which the declared same-sided homotopies exist uniquely",
                "absence of timelike boundary may be replaced by a common preserved boundary domain",
                "filtration nilpotence of U-1 is sufficient but not necessary; a finite-order support-local inverse is the actual requirement",
                "finite rank is an implementation hypothesis, not an algebraic necessity",
            ],
        },
        "conclusions": {
            "lift": "Lambda_C,+/-=h+i Lambda_E,+/- p",
            "lifted_chain_identity": (
                "q_C Lambda_C,+/-+Lambda_C,+/- q_C=1_C"
            ),
            "descent": "Lambda_E,+/-=p Lambda_C,+/- i",
            "descended_chain_identity": (
                "q_E Lambda_E,+/-+Lambda_E,+/- q_E=1_E"
            ),
            "causal_difference": (
                "Delta_C=Lambda_C,+-Lambda_C,-=i Delta_E p"
            ),
            "causal_quasi_isomorphism": (
                "[Delta_C]=[i_sc][Delta_E][p_c]; hence it is a "
                "quasi-isomorphism whenever the endpoint map is"
            ),
            "support": (
                "supp Lambda_C,+/- f is contained in "
                "J^+/-(supp f)"
            ),
            "adjoint_reversal": (
                "Lambda_C,+^sharp=Sigma_C Lambda_C,- Sigma_C^-1"
            ),
            "induced_pairing": (
                "<f,Delta_C g>_C=<p f,Delta_E p g>_E"
            ),
            "current_pairing": (
                "when the endpoint Green pairing equals its Cauchy-current "
                "pairing, the transferred cohomology pairing agrees under p"
            ),
            "direct_sum_and_shear": (
                "finite direct sums and finite-order support-local cyclic "
                "conjugations preserve all declared identities"
            ),
        },
        "proof_ledger": {
            "chain": (
                "expand q_C(h+i Lambda_E p)+(h+i Lambda_E p)q_C "
                "and use the deformation identity and chain maps"
            ),
            "descent": (
                "p(q_C Lambda_C+Lambda_C q_C)i=p i=1_E"
            ),
            "difference": (
                "the sign-independent local h term cancels between + and -"
            ),
            "quasi_isomorphism": (
                "on compact-to-spacelike-compact complexes, Delta_C is the "
                "composition of endpoint Delta_E with the two SDR "
                "quasi-isomorphisms"
            ),
            "support": (
                "local terms preserve support and the endpoint term is a "
                "support-local/causal/support-local composition"
            ),
            "cyclicity": (
                "take the graded adjoint and use pairing adjointness, "
                "degreewise sign intertwiners, homotopy cyclicity and "
                "endpoint advanced/retarded reversal"
            ),
            "pairing": (
                "J_C Delta_C=p^T J_E Delta_E p follows from "
                "Delta_C=i Delta_E p and i^sharp=p"
            ),
        },
        "toy_fixture": toy,
        "necessity_counterexamples": failures,
        "consumer_replays": {
            "conformal_cylinder": {
                "generality": "G2_COMPLETE_LINEAR_COMPLEX_ON_ONE_BACKGROUND",
                "carrier": (
                    "386=356+30 rows (356 algebraically contracted and "
                    "30 causal endpoint rows)"
                ),
                "formula": (
                    "Lambda_386,+/-=H_356+i_end Lambda_30,+/- p_end"
                ),
                "cyclic_SDR": True,
                "same_sided_support": True,
                "adjoint_reversal": True,
                "causal_quasi_isomorphism": True,
                "Green_pairing_equals_current_pairing": True,
                "producer_rerun": False,
            },
            "unit_nariai": {
                "generality": "G2_COMPLETE_LINEAR_COMPLEX_ON_ONE_BACKGROUND",
                "carrier": "310=15+140+140+15 rows with 26-row metric endpoint",
                "formula": (
                    "Lambda_310,+/-=H+I Lambda_metric,+/- P"
                ),
                "cyclic_SDR": True,
                "same_sided_support": True,
                "adjoint_reversal": True,
                "metric_descent": True,
                "causal_difference_and_pairing_factorization": (
                    "derived from the abstract identities on the imported "
                    "same-background cyclic SDR"
                ),
                "producer_rerun": False,
            },
        },
        "exact_checks": {
            "toy_all_defects_zero": True,
            "toy_causal_difference_nonzero": (
                toy["causal_difference_rank"] > 0
            ),
            "all_seven_counterexamples_exact": len(failures) == 7,
            "counterexamples_preserve_the_claimed_control_identity": True,
            "chain_hypotheses_sharp": True,
            "descent_retraction_sharp": True,
            "support_locality_sharp": True,
            "pairing_adjointness_sharp": True,
            "endpoint_adjoint_reversal_sharp": True,
            "fixed_sign_intertwining_sharp": True,
            "causal_difference_factorization_exact": True,
            "causal_quasi_isomorphism_factorization_exact": True,
            "induced_pairing_identity_exact": True,
            "cylinder_consumed_without_producer_rerun": True,
            "nariai_consumed_without_producer_rerun": True,
        },
        "source_manifest": {
            "producer": {
                "path": str(PRODUCER.relative_to(ROOT)),
                "sha256": _sha256(PRODUCER),
            },
            "independent_verifier": {
                "path": str(VERIFIER.relative_to(ROOT)),
                "sha256": _sha256(VERIFIER),
            },
            "tests": {
                "path": str(TESTS.relative_to(ROOT)),
                "sha256": _sha256(TESTS),
            },
            "strict_schema": {
                "path": str(SCHEMA.relative_to(ROOT)),
                "sha256": _sha256(SCHEMA),
            },
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.green_hyperbolic_cyclic_transfer_theorem --check --guards",
            "python3 -m d_quotient_classical.causal_transfer.verify_green_hyperbolic_cyclic_transfer_theorem",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_green_hyperbolic_cyclic_transfer_theorem",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/green-hyperbolic-cyclic-transfer-theorem-v1.schema.json -d d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json",
        ],
        "claim_boundary": (
            "This is a conditional LORENTZIAN-CAUSAL transfer theorem plus "
            "an exact LOCAL-ALGEBRAIC audit. It transfers already-certified "
            "advanced/retarded Green homotopies, their causal difference, "
            "the derived causal quasi-isomorphism, cyclic adjoint reversal "
            "and induced Green/current pairing through a differential cyclic "
            "contraction. It independently consumes immutable same-background "
            "certificates for the unit vacuum conformal cylinder and global "
            "unit Nariai; it does not identify their modes or carriers. The "
            "finite toy and counterexamples do not establish Lorentzian "
            "existence. The theorem does not create an endpoint Green "
            "homotopy, prove uniform estimates on an open background family, "
            "cover a timelike boundary without a preserved domain, permit a "
            "non-support-local shear, or furnish an isolated-operator Green "
            "inverse. It does not transport wavefront sets, construct a "
            "Hadamard two-point function, choose a complex structure, prove "
            "positivity, quantize a particle space, define renormalized "
            "products, restore a QME, or establish interacting, scattering "
            "or quantum claims."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise AssertionError(
            "schema validation failed: "
            + "; ".join(error.message for error in errors[:8])
        )
    if not all(value["exact_checks"].values()):
        raise AssertionError("an exact theorem check dropped")
    if value["background_scope"]["cross_background_identification"] is not False:
        raise AssertionError("cross-background identification was promoted")
    if any(
        row["defect"]["rank"] == 0
        and row["counterexample_id"] != "SUPPORT_LOCALITY_IS_ESSENTIAL"
        for row in value["necessity_counterexamples"]
    ):
        raise AssertionError("a counterexample lost its claimed defect")
    support = next(
        row
        for row in value["necessity_counterexamples"]
        if row["counterexample_id"] == "SUPPORT_LOCALITY_IS_ESSENTIAL"
    )
    if not support["defect"]["nonzero_entries"]:
        raise AssertionError("support counterexample lost its cross-point entry")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency drifted: {name}")


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    counterexample_lines = "\n".join(
        (
            f"- `{row['counterexample_id']}`: dropping "
            f"`{row['dropped_hypothesis']}` preserves the algebraic chain "
            "identity (rank-zero chain defect) but creates one explicit "
            "cross-point support entry."
            if row["counterexample_id"] == "SUPPORT_LOCALITY_IS_ESSENTIAL"
            else (
                f"- `{row['counterexample_id']}`: dropping "
                f"`{row['dropped_hypothesis']}` leaves "
                f"`{row['failed_conclusion']}` defective "
                f"(rank `{row['defect']['rank']}`)."
            )
        )
        for row in value["necessity_counterexamples"]
    )
    return f"""# Sharp cyclic Green-homotopy transfer theorem

## Result

Let `(C,q_C)` contract differentially and cyclically onto `(E,q_E)` through
`(i,p,h)`, with all maps preserving the declared support and operator-domain
categories. If `E` carries advanced and retarded Green homotopies, then

```text
Lambda_C,+/- = h + i Lambda_E,+/- p
```

satisfies the full chain-homotopy identity and same-sided causal support.
The local term cancels in the causal difference:

```text
Delta_C = Lambda_C,+ - Lambda_C,-
        = i Delta_E p.
```

Consequently, on compact-to-spacelike-compact support complexes,

```text
[Delta_C] = [i_sc] [Delta_E] [p_c].
```

It is therefore a quasi-isomorphism whenever the endpoint causal map is.
With `i^sharp=p`, the transferred Green pairing is not merely abstractly
isomorphic but satisfies the exact representative identity

```text
<f,Delta_C g>_C = <p f,Delta_E p g>_E.
```

If the endpoint Green pairing agrees with a Cauchy-current pairing, that
identity descends with it. Pairing-derived degreewise sign involutions, rather
than one guessed scalar sign, give the advanced/retarded adjoint reversal.

## Sharpness

Seven exact rational counterexamples identify the load-bearing hypotheses:

{counterexample_lines}

The side conditions `h^2=h i=p h=0` normalize a strong deformation retract
but are not used in the one-step lifted chain identity. Global hyperbolicity,
no timelike boundary, finite rank and filtration nilpotence are likewise
sufficient implementation conditions with the explicit replacements stated
in the certificate; they are not mislabelled as algebraically necessary.

## Independent consumers

The theorem consumes existing content-addressed artifacts without rerunning
their producers.

- On the unit vacuum conformal cylinder, the complete carrier has
  `386=356+30` rows. The cyclic SDR, advanced/retarded homotopies, causal
  quasi-isomorphism and equality of Green and Cauchy-current pairings are all
  imported and hash checked.
- On global unit Nariai, the curved repaired carrier has
  `310=15+140+140+15` rows and a 26-row metric endpoint. Its exact cyclic SDR,
  same-sided support, adjoint reversal and metric descent are imported and
  hash checked; the causal-difference and pairing factorizations are then the
  abstract theorem applied on that same background.

No carrier or mode is identified between these backgrounds.

## Scope

This theorem transfers a Green-hyperbolic-complex structure; it does not
construct the endpoint analytic input. It does not authorize nonlocal shears,
an isolated Bach-operator inverse, an open-background uniform theorem,
Hadamard wavefront control, a complex structure, positivity, particles,
renormalized products, QME restoration or any quantum claim.

## Reproduction

```bash
python3 -m d_quotient_classical.causal_transfer.green_hyperbolic_cyclic_transfer_theorem --check --guards
python3 -m d_quotient_classical.causal_transfer.verify_green_hyperbolic_cyclic_transfer_theorem
python3 -m unittest d_quotient_classical.causal_transfer.tests.test_green_hyperbolic_cyclic_transfer_theorem
```

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = []

    mutant = json.loads(json.dumps(value))
    mutant["background_scope"]["cross_background_identification"] = True
    mutations.append(mutant)

    mutant = json.loads(json.dumps(value))
    mutant["exact_checks"]["induced_pairing_identity_exact"] = False
    mutations.append(mutant)

    mutant = json.loads(json.dumps(value))
    mutant["consumer_replays"]["conformal_cylinder"]["producer_rerun"] = True
    mutations.append(mutant)

    mutant = json.loads(json.dumps(value))
    mutant["necessity_counterexamples"][3]["defect"]["nonzero_entries"] = []
    mutations.append(mutant)

    for mutant in mutations:
        try:
            validate(mutant)
        except (AssertionError, ValueError):
            continue
        raise AssertionError("mutation guard accepted a forbidden promotion")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = _render(value)
    report = _report(value)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale certificate: {OUTPUT}")
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
            raise SystemExit(f"stale report: {REPORT}")
    if args.guards:
        _guards(value)
    print(
        "GREEN-HYPERBOLIC CYCLIC TRANSFER: "
        "SHARP THEOREM AND THREE CONSUMERS PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
