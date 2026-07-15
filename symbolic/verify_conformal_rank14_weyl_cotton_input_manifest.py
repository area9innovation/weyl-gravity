#!/usr/bin/env python3
"""Verify the content-addressed rank-14 Weyl--Cotton input manifest."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_weyl_cotton_input_manifest import (  # noqa: E402
    Rank14WeylCottonInputManifest,
    _matrix_hash,
    _matrix_tuple_hash,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (  # noqa: E402
    ConstraintAdjustedWeylCottonEvolution,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_weyl_cotton_input_manifest.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rejects(documents: dict[str, dict[str, object]]) -> bool:
    try:
        Rank14WeylCottonInputManifest(documents=documents).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-rank14-complete", action="store_true")
    args = parser.parse_args()
    if args.claim_rank14_complete:
        raise SystemExit(
            "REFUSED: this is a content-addressed input manifest; it does not "
            "construct L14, V14, source lifts or Green operators"
        )

    audit = Rank14WeylCottonInputManifest.build()
    certificate = audit.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    registry = certificate["authoritative_registry"]
    bases = certificate["ordered_bases"]
    quotient = certificate["quotient_and_filtration_maps"]
    coefficients = certificate["coefficient_table_index"]
    tables = certificate["large_table_references"]
    matrix_hashes = certificate["exact_matrix_table_hashes"]
    pde = certificate["evolution_constraint_source_package"]
    rows = certificate["prolonged_BV_rows"]
    conventions = certificate["adjoint_and_current_conventions"]
    availability = certificate["availability"]
    exact = ConstraintAdjustedWeylCottonEvolution.build()
    checks = {
        "registry_complete": len(registry) == 12,
        "all_paths_exist": all(
            (ROOT / entry[key]).is_file()
            for entry in registry.values()
            for key in ("source", "verifier", "certificate")
        ),
        "all_file_hashes_current": all(
            _sha256(ROOT / entry[path_key]) == entry[hash_key]
            for entry in registry.values()
            for path_key, hash_key in (
                ("source", "source_sha256"),
                ("verifier", "verifier_sha256"),
                ("certificate", "certificate_sha256"),
            )
        ),
        "rank34_basis": bases["rank34_bundle"] == ["h[10]", "f[10]", "Csharp[14]"],
        "state26_basis": len(bases["state_26"]) == 6
        and bases["state_26"][-2:] == ["x[3]", "y[3]"],
        "constraint14_basis": bases["constraint_14"]
        == ["q[3]", "r[3]", "a[3]", "c[3]", "s[1]", "t[1]"],
        "component_basis_exact": bases["component_basis_conventions"]["STF_5"]
        == [
            "diag(1,-1,0)",
            "diag(1,1,-2)",
            "e_12+e_21",
            "e_13+e_31",
            "e_23+e_32",
        ]
        and bases["component_basis_conventions"]["vector_3"]
        == ["e_1", "e_2", "e_3"],
        "raw_row_order_exact": bases["raw_first_order_rows_34"]["constraint_rows"]
        == [5, 6, 7, 13, 14, 15, 16, 25]
        and len(bases["raw_first_order_rows_34"]["independent_temporal_rows"])
        == 26,
        "mapping_BV16_basis": len(bases["prolonged_BV_16"]) == 16,
        "rank12_map_hashed": quotient["rank12_embedding"]["coefficient_sha256"]
        and quotient["rank12_embedding"]["intertwining_identity"]
        == "L_34 J=J L_12",
        "rank14_boundary_visible": quotient["rank14_field_cokernel"]["rank"] == 14
        and quotient["rank14_field_cokernel"]["C1_descends"]
        and not quotient["rank14_field_cokernel"][
            "induced_biwave_intertwiner_constructed"
        ],
        "TAB_coefficient_tables": set(coefficients)
        == {"T_state", "A_equation", "B_identity"}
        and all(entry["sha256"] for entry in coefficients.values()),
        "large_tables_by_reference_only": set(tables)
        == {
            "cotton_first_order_4x16x10",
            "bach_derivative_4x9x16",
            "bach_zeroth_9x10",
            "compatibility_derivative_4x9x16",
            "compatibility_zeroth_9x10",
            "evolution_symmetrizer_26",
        }
        and all("canonical_sha256" in entry for entry in tables.values()),
        "exact_evolution_matrix_hash": matrix_hashes[
            "evolution_spatial_3x26x26"
        ]["sha256"]
        == _matrix_tuple_hash(exact.evolution_spatial_coefficients)
        and matrix_hashes["evolution_zeroth_26x26"]["sha256"]
        == _matrix_hash(exact.evolution_zeroth_coefficient),
        "exact_constraint_matrix_hash": matrix_hashes[
            "constraint_spatial_3x14x26"
        ]["sha256"]
        == _matrix_tuple_hash(exact.source_compatibility_spatial_coefficients)
        and matrix_hashes["constraint_zeroth_14x26"]["sha256"]
        == _matrix_hash(exact.source_compatibility_zeroth_coefficient),
        "exact_subsidiary_matrix_hash": matrix_hashes[
            "subsidiary_spatial_3x14x14"
        ]["sha256"]
        == _matrix_tuple_hash(exact.constraint_spatial_coefficients)
        and matrix_hashes["subsidiary_zeroth_14x14"]["sha256"]
        == _matrix_hash(exact.constraint_zeroth_coefficient),
        "exact_symmetrizer_hashes": matrix_hashes[
            "evolution_symmetrizer_26x26"
        ]["sha256"]
        == _matrix_hash(exact.evolution_symmetrizer)
        and matrix_hashes["subsidiary_symmetrizer_14x14"]["sha256"]
        == _matrix_hash(exact.constraint_symmetrizer)
        and not matrix_hashes["matrices_embedded"],
        "evolution26": pde["evolution_26"]["state_rank"] == 26,
        "constraints14": pde["constraints_14"]["rank"] == 14,
        "source_compatibility": pde["source_compatibility"]["identity"]
        == "L_K K_WC=K_src L_WC",
        "subsidiary_hyperbolic": pde["subsidiary"]["symmetric_hyperbolic"],
        "symmetrizers_positive": pde["symmetrizers"]["evolution_positive"]
        and pde["symmetrizers"]["subsidiary_positive"],
        "all_BV_rows": len(rows["degree_ledger"]) == 16
        and rows["coefficientwise_complete"]
        and len(rows["primal_attachments"]) == 3
        and len(rows["cotangent_attachments"]) == 3,
        "formal_adjoint_tables": set(conventions["adjoint_table_index"])
        == {"T_state_sharp", "A_equation_sharp", "B_identity_sharp"},
        "pairings_separated": not conventions["current_pairing_separation"][
            "identified_with_each_other"
        ],
        "compact_manifest": len(json.dumps(certificate, sort_keys=True)) < 40000,
        "no_matrix_duplication": not any(
            key.endswith("_tables") for key in certificate["large_table_references"]
        ),
        "inputs_available": availability["all_authoritative_files_present"]
        and availability["all_schemas_match"]
        and availability["all_cross_hashes_recomputed"],
        "rank14_still_open": not availability["rank14_operator_constructed"]
        and not availability["rank14_backward_witness_constructed"]
        and not availability["rank14_source_lift_constructed"]
        and not availability["rank14_green_operators_constructed"],
        "no_global_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"]
        and certificate["status_flags_promoted"] == [],
    }

    if args.guards:
        documents = {
            key: deepcopy(dict(value)) for key, value in audit.documents.items()
        }
        bad_rank = deepcopy(documents)
        bad_rank["rank34_filtration"]["quotient_presentation"][
            "field_cokernel_rank"
        ] = 13
        bad_map = deepcopy(documents)
        bad_map["curvature_state_gauge_map"]["T_state_K_aux_exact"] = False
        bad_hyper = deepcopy(documents)
        bad_hyper["weyl_cotton_hyperbolic"][
            "exact_sourced_subsidiary_operator_identity"
        ] = False
        bad_source = deepcopy(documents)
        bad_source["weyl_cotton_causal_pde"]["source_compatibility"][
            "exact_operator_identity"
        ] = "broken"
        bad_rows = deepcopy(documents)
        bad_rows["mapping_cylinder_substitution"]["kernel"][
            "complete_16_block_degree_ledger"
        ] = []
        bad_current = deepcopy(documents)
        bad_current["prolonged_current"]["pairing_separation"][
            "identified_with_each_other"
        ] = True
        checks.update(
            {
                "broken_rank14_rejected": _rejects(bad_rank),
                "broken_state_map_rejected": _rejects(bad_map),
                "broken_subsidiary_rejected": _rejects(bad_hyper),
                "broken_source_identity_rejected": _rejects(bad_source),
                "broken_BV_rows_rejected": _rejects(bad_rows),
                "conflated_pairings_rejected": _rejects(bad_current),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RANK14 INPUT MANIFEST: {sum(checks.values())}/{len(checks)} PASS")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
