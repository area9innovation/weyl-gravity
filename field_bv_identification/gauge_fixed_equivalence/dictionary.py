"""Exhaustive coordinate ledger for the gauge-fixed extension."""

from __future__ import annotations

from field_bv_identification.gauge_fixed_equivalence.auxiliary_elimination import (
    elimination_ledger,
)
from field_bv_identification.gauge_fixed_equivalence.contraction import (
    GaugeFixedContraction,
)
from field_bv_identification.variable_dictionary import basis_records


def gauge_fixed_records(
    contraction: GaugeFixedContraction,
) -> tuple[dict[str, object], ...]:
    block = contraction.block
    q_nnz = [0] * block.dimension
    shift_nnz = [0] * block.dimension
    for _, column in block.q_gauge_fixed.todok():
        q_nnz[column] += 1
    for _, column in block.shear.todok():
        shift_nnz[column] += 1

    records: list[dict[str, object]] = []
    for raw in basis_records(block.energy, block.raw):
        index = int(raw["raw_index"])
        records.append(
            {
                "energy": block.energy,
                "full_index": index,
                "sector": "minimal",
                "variable": raw["bv_variable"],
                "basis_element": raw["raw_basis_element"],
                "component_index": index,
                "conventional_bv_ghost_number": raw[
                    "conventional_bv_ghost_number"
                ],
                "antifield_number": raw["antifield_number"],
                "local_tangent_degree": raw["local_tangent_degree"],
                "compact_degree": block.energy,
                "tensor_type": raw["so4_content"],
                "primary_weight": raw["primary_weight"],
                "polynomial_level": raw["polynomial_level"],
                "classification": "proven minimal raw chain",
                "coordinate_brst_rule": "minimal master-action rule",
                "tangent_differential": raw["differential_image"],
                "q_gf_image_nnz": q_nnz[index],
                "canonical_shift_nnz": shift_nnz[index],
                "elimination": "retained by p_gf",
                "equality_certificate": "exact",
            }
        )

    coordinate_rules = {
        row["source"]: row["image"]
        for row in block.nonminimal.coordinate_brst_rules()
    }
    tangent_rules = {
        "vector_multiplier": "vector_antighost",
        "scalar_multiplier": "scalar_antighost",
        "vector_antighost_antifield": "vector_multiplier_antifield",
        "scalar_antighost_antifield": "scalar_multiplier_antifield",
    }
    eliminations = {
        row["variable"]: row for row in elimination_ledger(block.nonminimal)
    }
    offset = block.raw.dimension
    for field in block.nonminimal.slices:
        level = block.energy - field.primary_weight
        for local_index in range(field.dimension):
            index = offset + field.start + local_index
            records.append(
                {
                    "energy": block.energy,
                    "full_index": index,
                    "sector": "nonminimal",
                    "variable": field.name,
                    "basis_element": f"{field.name}[{local_index}]",
                    "component_index": local_index,
                    "conventional_bv_ghost_number": field.conventional_ghost_number,
                    "antifield_number": field.antifield_number,
                    "local_tangent_degree": field.tangent_degree,
                    "compact_degree": block.energy,
                    "tensor_type": field.tensor_type,
                    "primary_weight": field.primary_weight,
                    "polynomial_level": level,
                    "classification": eliminations[field.name]["classification"],
                    "coordinate_brst_rule": coordinate_rules.get(field.name, "0"),
                    "tangent_differential": tangent_rules.get(field.name, "0"),
                    "q_gf_image_nnz": q_nnz[index],
                    "canonical_shift_nnz": shift_nnz[index],
                    "elimination": eliminations[field.name]["elimination"],
                    "equality_certificate": "exact",
                }
            )
    if len(records) != block.dimension:
        raise AssertionError("gauge-fixed dictionary does not exhaust the block")
    return tuple(records)

