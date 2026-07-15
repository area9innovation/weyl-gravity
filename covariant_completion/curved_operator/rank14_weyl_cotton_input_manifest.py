"""Content-addressed input manifest for the rank-14 Weyl--Cotton bridge.

The remaining field-cokernel problem touches several independently certified
calculations.  This module packages their locations, ordered bases and exact
cross-hashes without copying any coefficient matrix.  Large tables stay in
their authoritative certificates; the manifest stores a JSON pointer, shape
and canonical subtree hash.

The manifest is an input package, not the missing construction.  In
particular it does not claim that the rank-fourteen quotient operator,
backward BV witness, compatible-source lift or Green operators exist.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


ROOT = Path(__file__).resolve().parents[2]


REGISTRY = (
    (
        "rank34_filtration",
        "covariant_completion/curved_operator/expanded_relative_witness_rank34_module.py",
        "symbolic/verify_conformal_expanded_relative_witness_rank34_module.py",
        "covariant_completion/certificates/curved_expanded_relative_witness_rank34_module.json",
        "pure-weyl-expanded-relative-rank34-module-v1",
    ),
    (
        "curvature_state_gauge_map",
        "covariant_completion/curved_retract/curvature_state_gauge_chain_map.py",
        "symbolic/verify_conformal_curvature_state_gauge_chain_map.py",
        "covariant_completion/certificates/curved_curvature_state_gauge_chain_map.json",
        "pure-weyl-curvature-state-gauge-chain-map-v1",
    ),
    (
        "curvature_identity_map",
        "covariant_completion/curved_retract/curvature_identity_chain_map.py",
        "symbolic/verify_conformal_curvature_identity_chain_map.py",
        "covariant_completion/certificates/curved_curvature_identity_chain_map.json",
        "pure-weyl-curvature-auxiliary-identity-chain-map-v1",
    ),
    (
        "weyl_cotton_3plus1",
        "covariant_completion/curved_operator/weyl_3plus1.py",
        "symbolic/verify_conformal_weyl_cotton_3plus1.py",
        "covariant_completion/certificates/curved_weyl_cotton_3plus1.json",
        "pure-weyl-cotton-3plus1-algebra-v1",
    ),
    (
        "weyl_cotton_bach_first_order",
        "covariant_completion/curved_operator/weyl_3plus1.py",
        "symbolic/verify_conformal_weyl_cotton_3plus1.py",
        "covariant_completion/certificates/curved_weyl_cotton_bach_first_order.json",
        "pure-weyl-cotton-bach-first-order-v1",
    ),
    (
        "promoted_constraints",
        "covariant_completion/curved_operator/weyl_cotton_promoted_constraints.py",
        "symbolic/verify_conformal_weyl_cotton_promoted_constraints.py",
        "covariant_completion/certificates/curved_weyl_cotton_promoted_constraints.json",
        "pure-weyl-cotton-promoted-constraint-candidate-v1",
    ),
    (
        "weyl_cotton_hyperbolic",
        "covariant_completion/curved_operator/weyl_cotton_hyperbolic.py",
        "symbolic/verify_conformal_weyl_cotton_hyperbolic.py",
        "covariant_completion/certificates/curved_weyl_cotton_hyperbolic.json",
        "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1",
    ),
    (
        "weyl_cotton_causal_pde",
        "covariant_completion/curved_operator/weyl_cotton_causal_pde.py",
        "symbolic/verify_conformal_weyl_cotton_causal_pde.py",
        "covariant_completion/certificates/curved_weyl_cotton_causal_pde.json",
        "pure-weyl-cotton-causal-pde-v1",
    ),
    (
        "weyl_cotton_block_witness",
        "covariant_completion/curved_operator/weyl_cotton_block_green_witness.py",
        "symbolic/verify_conformal_weyl_cotton_block_green_witness.py",
        "covariant_completion/certificates/curved_weyl_cotton_block_green_witness.json",
        "pure-weyl-cotton-block-green-witness-v1",
    ),
    (
        "mapping_cylinder_substitution",
        "covariant_completion/curved_retract/curvature_mapping_cylinder_substitution.py",
        "symbolic/verify_conformal_curvature_mapping_cylinder_substitution.py",
        "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json",
        "pure-weyl-curvature-mapping-cylinder-substitution-v1",
    ),
    (
        "prolonged_current",
        "covariant_completion/curved_current/prolonged_current_comparison.py",
        "symbolic/verify_conformal_prolonged_current_comparison.py",
        "covariant_completion/certificates/curved_prolonged_current_comparison.json",
        "pure-weyl-prolonged-current-comparison-v1",
    ),
    (
        "curved_current",
        "covariant_completion/curved_current/bv_current_closure.py",
        "symbolic/verify_conformal_curved_current.py",
        "covariant_completion/certificates/curved_current_comparison.json",
        "pure-weyl-curved-current-comparison-status-v1",
    ),
)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _matrix_hash(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _matrix_tuple_hash(matrices: tuple[sp.Matrix, ...]) -> str:
    payload = "\n".join(_matrix_hash(matrix) for matrix in matrices).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {relative}")
    return value


def _pointer(value: Mapping[str, object], path: str) -> object:
    current: object = value
    for token in path.strip("/").split("/"):
        if not isinstance(current, Mapping) or token not in current:
            raise AssertionError(f"missing JSON pointer /{path.strip('/')}")
        current = current[token]
    return current


def _reference(
    certificate_path: str,
    certificate: Mapping[str, object],
    pointer: str,
    *,
    shape: object | None = None,
) -> dict[str, object]:
    value = _pointer(certificate, pointer)
    result: dict[str, object] = {
        "certificate": certificate_path,
        "json_pointer": "/" + pointer.strip("/"),
        "canonical_sha256": _canonical_hash(value),
    }
    if shape is not None:
        result["shape"] = shape
    return result


@dataclass(frozen=True)
class Rank14WeylCottonInputManifest:
    """Availability and semantic cross-hash audit for the missing bridge."""

    documents: Mapping[str, Mapping[str, object]]

    @staticmethod
    def build() -> "Rank14WeylCottonInputManifest":
        documents: dict[str, Mapping[str, object]] = {}
        for label, source, verifier, certificate, schema in REGISTRY:
            for relative in (source, verifier, certificate):
                if not (ROOT / relative).is_file():
                    raise AssertionError(f"missing authoritative input: {relative}")
            value = _load(certificate)
            if value.get("schema") != schema:
                raise AssertionError(
                    f"schema drift for {label}: {value.get('schema')!r} != {schema!r}"
                )
            documents[label] = value
        result = Rank14WeylCottonInputManifest(documents=documents)
        result.verify()
        return result

    def verify(self) -> None:
        rank34 = self.documents["rank34_filtration"]
        component = _pointer(rank34, "rank34_component")
        quotient = _pointer(rank34, "quotient_presentation")
        submodule = _pointer(rank34, "local_differential_submodule")
        if not isinstance(component, Mapping) or component.get("rank") != 34:
            raise AssertionError("rank-34 component drifted")
        if not isinstance(submodule, Mapping) or not (
            submodule.get("presentation_rank") == 12
            and submodule.get("intertwining_defect") == 0
        ):
            raise AssertionError("rank-12 filtration map drifted")
        if not isinstance(quotient, Mapping) or not (
            quotient.get("constraint_quotient_rank") == 8
            and quotient.get("field_cokernel_rank") == 14
            and quotient.get("C1_descends_to_field_cokernel")
            and not quotient.get("C1_induced_biwave_intertwiner_constructed")
        ):
            raise AssertionError("rank-14 quotient boundary drifted")

        state_map = self.documents["curvature_state_gauge_map"]
        if not (
            state_map.get("T_state") == "(C1,div C1)"
            and state_map.get("T_state_K_aux_exact")
        ):
            raise AssertionError("curvature state quotient map drifted")

        identity = self.documents["curvature_identity_map"]
        if not (
            identity.get("second_chain_relation_exact")
            and isinstance(identity.get("cotangent_lift"), Mapping)
            and identity["cotangent_lift"].get("generated_from_same_BV_pairings")
        ):
            raise AssertionError("identity/cotangent chain map drifted")

        first_order = self.documents["weyl_cotton_bach_first_order"]
        state_bundle = _pointer(first_order, "state_bundle")
        if not isinstance(state_bundle, Mapping) or state_bundle.get("total") != 26:
            raise AssertionError("Weyl--Cotton state rank drifted")

        hyperbolic = self.documents["weyl_cotton_hyperbolic"]
        if not (
            hyperbolic.get("state_rank") == 26
            and hyperbolic.get("constraint_rank") == 14
            and hyperbolic.get("evolution_symmetrizer_positive")
            and hyperbolic.get("subsidiary_symmetrizer_positive")
            and hyperbolic.get("exact_sourced_subsidiary_operator_identity")
        ):
            raise AssertionError("26+14 hyperbolic package drifted")

        causal = self.documents["weyl_cotton_causal_pde"]
        source = _pointer(causal, "source_compatibility")
        if not isinstance(source, Mapping) or not (
            source.get("exact_operator_identity") == "L_K K_WC=K_src L_WC"
            and source.get("K_src_is_finite_order_differential")
        ):
            raise AssertionError("sourced compatibility package drifted")

        block = self.documents["weyl_cotton_block_witness"]
        identities = _pointer(block, "exact_block_identities")
        if not isinstance(identities, Mapping) or not (
            identities.get("P_equals_QW_plus_WQ")
            and identities.get("Q_P_equals_P_Q")
        ):
            raise AssertionError("curvature block witness drifted")

        substitution = self.documents["mapping_cylinder_substitution"]
        if not substitution.get("coefficientwise_complete_prolonged_Q"):
            raise AssertionError("prolonged coefficient substitution drifted")
        kernel = _pointer(substitution, "kernel")
        if not isinstance(kernel, Mapping) or len(
            kernel.get("complete_16_block_degree_ledger", [])
        ) != 16:
            raise AssertionError("16-row BV ledger drifted")

        current = self.documents["prolonged_current"]
        if not (
            current.get("prolonged_current_comparison")
            and _pointer(current, "pairing_separation/identified_with_each_other")
            is False
        ):
            raise AssertionError("current/pairing convention drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        registry: dict[str, object] = {}
        for label, source, verifier, certificate, schema in REGISTRY:
            registry[label] = {
                "source": source,
                "source_sha256": _file_hash(ROOT / source),
                "verifier": verifier,
                "verifier_sha256": _file_hash(ROOT / verifier),
                "certificate": certificate,
                "certificate_sha256": _file_hash(ROOT / certificate),
                "schema": schema,
            }

        rank34_path = REGISTRY[0][3]
        state_map_path = REGISTRY[1][3]
        identity_path = REGISTRY[2][3]
        three_path = REGISTRY[3][3]
        first_path = REGISTRY[4][3]
        promoted_path = REGISTRY[5][3]
        hyper_path = REGISTRY[6][3]
        causal_path = REGISTRY[7][3]
        block_path = REGISTRY[8][3]
        substitution_path = REGISTRY[9][3]
        current_path = REGISTRY[10][3]

        rank34 = self.documents["rank34_filtration"]
        state_map = self.documents["curvature_state_gauge_map"]
        identity = self.documents["curvature_identity_map"]
        three = self.documents["weyl_cotton_3plus1"]
        first = self.documents["weyl_cotton_bach_first_order"]
        promoted = self.documents["promoted_constraints"]
        hyper = self.documents["weyl_cotton_hyperbolic"]
        causal = self.documents["weyl_cotton_causal_pde"]
        block = self.documents["weyl_cotton_block_witness"]
        substitution = self.documents["mapping_cylinder_substitution"]
        current = self.documents["prolonged_current"]
        exact_hyperbolic = ConstraintAdjustedWeylCottonEvolution.build()

        coefficient_tables = _pointer(substitution, "coefficient_tables")
        assert isinstance(coefficient_tables, Mapping)
        adjoints = _pointer(substitution, "formal_adjoint_provenance")
        assert isinstance(adjoints, Mapping)
        kernel = _pointer(substitution, "kernel")
        assert isinstance(kernel, Mapping)

        return {
            "schema": "pure-weyl-rank14-weyl-cotton-input-manifest-v1",
            "purpose": (
                "content-addressed authoritative inputs for constructing the "
                "projector-free rank-14 field-cokernel Weyl--Cotton bridge"
            ),
            "authoritative_registry": registry,
            "ordered_bases": {
                "rank34_bundle": list(
                    _pointer(rank34, "rank34_component/bundle_order")
                ),
                "rank12_coordinates": list(
                    _pointer(rank34, "local_differential_submodule/coordinates")
                ),
                "weyl_10": _pointer(three, "weyl_coordinates"),
                "cotton_16": _pointer(three, "cotton_coordinates"),
                "state_26": list(_pointer(hyper, "state_order")),
                "constraint_14": list(_pointer(hyper, "constraint_order")),
                "promoted_state_32": list(_pointer(promoted, "state_order")),
                "curvature_block_BV": list(_pointer(block, "block_order")),
                "prolonged_BV_16": [
                    entry["block"]
                    for entry in kernel["complete_16_block_degree_ledger"]
                ],
                "auxiliary_ghost_9": list(
                    _pointer(state_map, "auxiliary_ghost_order")
                ),
                "auxiliary_identity_9": _pointer(
                    identity, "basis_conventions/auxiliary_identities"
                ),
                "component_basis_conventions": {
                    "STF_5": [
                        "diag(1,-1,0)",
                        "diag(1,1,-2)",
                        "e_12+e_21",
                        "e_13+e_31",
                        "e_23+e_32",
                    ],
                    "vector_3": ["e_1", "e_2", "e_3"],
                    "Cotton_16": (
                        "X_STF[5],X_antisymmetric(e_1,e_2,e_3),"
                        "Y_STF[5],Y_antisymmetric(e_1,e_2,e_3)"
                    ),
                    "authoritative_definition": (
                        "covariant_completion/curved_operator/weyl_3plus1.py::"
                        "stf_basis,tracefree_matrix_basis"
                    ),
                },
                "raw_first_order_rows_34": {
                    "order": [
                        "Cotton_definition[0:16]",
                        "Bach_STF[16:25]",
                        "dual_compatibility_STF[25:34]",
                    ],
                    "independent_temporal_rows": list(
                        _pointer(first, "independent_temporal_rows")
                    ),
                    "constraint_rows": list(_pointer(first, "constraint_rows")),
                },
            },
            "quotient_and_filtration_maps": {
                "rank34_component": _reference(
                    rank34_path, rank34, "rank34_component"
                ),
                "rank12_embedding": {
                    **_reference(
                        rank34_path,
                        rank34,
                        "local_differential_submodule",
                    ),
                    "formula": _pointer(
                        rank34, "local_differential_submodule/embedding"
                    ),
                    "coefficient_sha256": _pointer(
                        rank34, "local_differential_submodule/embedding_sha256"
                    ),
                    "intertwining_identity": _pointer(
                        rank34,
                        "local_differential_submodule/intertwining_identity",
                    ),
                },
                "rank22_quotient": _reference(
                    rank34_path, rank34, "quotient_presentation"
                ),
                "rank14_field_cokernel": {
                    "rank": 14,
                    "C1_descends": True,
                    "induced_biwave_intertwiner_constructed": False,
                    "reference": _reference(
                        rank34_path, rank34, "quotient_presentation"
                    ),
                },
                "metric_to_state": {
                    "formula": "T_state=(C1,div C1)",
                    "gauge_annihilation": "T_state K_aux=0",
                    "reference": _reference(
                        state_map_path, state_map, "T_state_K_aux"
                    ),
                },
                "equation_and_identity_maps": {
                    "A_equation": "E_curv T_state=A_equation Ebar_aux",
                    "B_identity": "N_curv A_equation=B_identity C_aux",
                    "reference": _reference(
                        identity_path, identity, "full_auxiliary_chain_relation"
                    ),
                },
            },
            "coefficient_table_index": {
                name: {
                    **dict(value),
                    "authoritative_certificate": substitution_path,
                    "json_pointer": f"/coefficient_tables/{name}",
                }
                for name, value in coefficient_tables.items()
                if isinstance(value, Mapping)
            },
            "large_table_references": {
                "cotton_first_order_4x16x10": _reference(
                    three_path,
                    three,
                    "cotton_first_order_tables",
                    shape=[4, 16, 10],
                ),
                "bach_derivative_4x9x16": _reference(
                    first_path,
                    first,
                    "bach_derivative_tables",
                    shape=[4, 9, 16],
                ),
                "bach_zeroth_9x10": _reference(
                    first_path,
                    first,
                    "bach_zeroth_table",
                    shape=[9, 10],
                ),
                "compatibility_derivative_4x9x16": _reference(
                    first_path,
                    first,
                    "compatibility_derivative_tables",
                    shape=[4, 9, 16],
                ),
                "compatibility_zeroth_9x10": _reference(
                    first_path,
                    first,
                    "compatibility_zeroth_table",
                    shape=[9, 10],
                ),
                "evolution_symmetrizer_26": _reference(
                    hyper_path,
                    hyper,
                    "evolution_symmetrizer_diagonal",
                    shape=[26],
                ),
            },
            "exact_matrix_table_hashes": {
                "authoritative_source": (
                    "covariant_completion/curved_operator/"
                    "weyl_cotton_hyperbolic.py::"
                    "ConstraintAdjustedWeylCottonEvolution.build"
                ),
                "evolution_spatial_3x26x26": {
                    "shape": [3, 26, 26],
                    "sha256": _matrix_tuple_hash(
                        exact_hyperbolic.evolution_spatial_coefficients
                    ),
                },
                "evolution_zeroth_26x26": {
                    "shape": [26, 26],
                    "sha256": _matrix_hash(
                        exact_hyperbolic.evolution_zeroth_coefficient
                    ),
                },
                "constraint_spatial_3x14x26": {
                    "shape": [3, 14, 26],
                    "sha256": _matrix_tuple_hash(
                        exact_hyperbolic.source_compatibility_spatial_coefficients
                    ),
                },
                "constraint_zeroth_14x26": {
                    "shape": [14, 26],
                    "sha256": _matrix_hash(
                        exact_hyperbolic.source_compatibility_zeroth_coefficient
                    ),
                },
                "subsidiary_spatial_3x14x14": {
                    "shape": [3, 14, 14],
                    "sha256": _matrix_tuple_hash(
                        exact_hyperbolic.constraint_spatial_coefficients
                    ),
                },
                "subsidiary_zeroth_14x14": {
                    "shape": [14, 14],
                    "sha256": _matrix_hash(
                        exact_hyperbolic.constraint_zeroth_coefficient
                    ),
                },
                "evolution_symmetrizer_26x26": {
                    "shape": [26, 26],
                    "sha256": _matrix_hash(exact_hyperbolic.evolution_symmetrizer),
                },
                "subsidiary_symmetrizer_14x14": {
                    "shape": [14, 14],
                    "sha256": _matrix_hash(exact_hyperbolic.constraint_symmetrizer),
                },
                "matrices_embedded": False,
            },
            "evolution_constraint_source_package": {
                "evolution_26": {
                    "operator": "L_WC",
                    "state_rank": 26,
                    "reference": _reference(causal_path, causal, "operator"),
                },
                "constraints_14": {
                    "operator": "K_WC",
                    "rank": 14,
                    "reference": _reference(
                        causal_path, causal, "constraint_operator"
                    ),
                },
                "source_compatibility": {
                    "identity": "L_K K_WC=K_src L_WC",
                    "reference": _reference(
                        causal_path, causal, "source_compatibility"
                    ),
                },
                "subsidiary": {
                    "operator": "L_K",
                    "symmetric_hyperbolic": True,
                    "reference": _reference(
                        hyper_path, hyper, "sourced_subsidiary_equations"
                    ),
                },
                "symmetrizers": {
                    "evolution_positive": True,
                    "subsidiary_positive": True,
                    "reference": _reference(
                        hyper_path, hyper, "evolution_symmetrizer_diagonal"
                    ),
                },
                "promoted_constraint_reference": _reference(
                    promoted_path, promoted, "retained_constraints"
                ),
            },
            "prolonged_BV_rows": {
                "degree_ledger": [
                    {"index": entry["index"], "block": entry["block"], "degree": entry["degree"]}
                    for entry in kernel["complete_16_block_degree_ledger"]
                ],
                "reference": _reference(
                    substitution_path,
                    substitution,
                    "kernel/complete_16_block_degree_ledger",
                ),
                "coefficientwise_complete": True,
                "primal_attachments": list(
                    _pointer(substitution, "substitution/primal_blocks")
                ),
                "cotangent_attachments": list(
                    _pointer(substitution, "substitution/cotangent_blocks")
                ),
            },
            "adjoint_and_current_conventions": {
                "formal_adjoint_rule": adjoints["rule"],
                "adjoint_table_index": {
                    name: dict(value)
                    for name, value in adjoints.items()
                    if isinstance(value, Mapping)
                },
                "odd_pairing_reference": _reference(
                    substitution_path, substitution, "kernel/odd_BV_cyclicity_defect"
                ),
                "current_pairing_separation": dict(
                    _pointer(current, "pairing_separation")
                ),
                "current_concomitant_convention": (
                    "d J_R(u,v)=<u,Rv>-<R^sharp u,v>"
                ),
                "current_reference": _reference(
                    current_path, current, "variational_transgression"
                ),
            },
            "availability": {
                "all_authoritative_files_present": True,
                "all_schemas_match": True,
                "all_cross_hashes_recomputed": True,
                "large_matrices_duplicated_in_manifest": False,
                "rank14_operator_constructed": False,
                "rank14_backward_witness_constructed": False,
                "rank14_source_lift_constructed": False,
                "rank14_green_operators_constructed": False,
            },
            "missing_output_contract": {
                "consume": [
                    "ordered_bases",
                    "quotient_and_filtration_maps",
                    "coefficient_table_index",
                    "evolution_constraint_source_package",
                    "prolonged_BV_rows",
                    "adjoint_and_current_conventions",
                ],
                "produce": [
                    "projector-free local rank-14 presentation pi14",
                    "complete curved L14 and degree-minus-one V14",
                    "P14=Q14 V14+V14 Q14 on primal and cotangent rows",
                    "compatible-source G14_plus/minus with causal support",
                    "residual source lifts through rank8 and rank12",
                ],
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": [],
            "fail_closed": True,
        }
