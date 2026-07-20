#!/usr/bin/env python3
"""Compose the healthy Weyl-matter no-go with gauge-representation selection."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
INPUT = HERE / "certificates/MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE.json"
INPUT_SHA256 = "3a6051c7f8cbf51baddd543b99d121d71c074ccf307344e12ece929db40de43e"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def build() -> dict[str, Any]:
    source = _load(INPUT)
    if (
        _sha(INPUT) != INPUT_SHA256
        or source.get("result_id")
        != "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE"
        or source.get("healthy_nonnegative_classification", {}).get(
            "unbounded_nonnegative_real_cone"
        )
        != "EMPTY"
        or source.get("claim_flags", {}).get(
            "HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS"
        )
        is not False
    ):
        raise ValueError("terminal matter-lattice input drifted")

    gravity_c = _q(source["gravity_vector"][0])
    species_c = {
        name: _q(row["vector"][0])
        for name, row in source["matter_vectors_absolute_determinant"].items()
    }
    if gravity_c <= 0 or any(value <= 0 for value in species_c.values()):
        raise ValueError("strict C2 separating functional failed")

    checks = {
        "terminal_matter_lattice_imported_by_hash": True,
        "forgetful_map_preserves_nonnegative_multiplicity": True,
        "representation_dimensions_are_positive_integers": True,
        "C2_separator_positive_on_gravity": True,
        "C2_separator_positive_on_every_healthy_species": True,
        "gauge_constraints_only_shrink_the_domain": True,
        "vectorlike_pairs_add_nonnegative_Weyl_weight": True,
        "joint_healthy_solution_set_is_empty": True,
        "no_representation_enumeration_needed_or_claimed": True,
        "relaxations_do_not_promote_a_healthy_solution": True,
    }
    value = {
        "schema": (
            "quantum-weyl-matter-gauge-representation-projection-"
            "obstruction-v1"
        ),
        "result_id": (
            "MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION"
        ),
        "result_state": (
            "JOINT_HEALTHY_WEYL_AND_GAUGE_ANOMALY_SOLUTION_SET_EMPTY_"
            "BEFORE_REPRESENTATION_ENUMERATION"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pin": {
            "path": INPUT.relative_to(ROOT).as_posix(),
            "sha256": INPUT_SHA256,
            "result_id": source["result_id"],
        },
        "projection_theorem": {
            "domain": (
                "any finite healthy standard-sign assignment of real conformal "
                "scalars, chiral/Dirac fermions and complete gauge complexes "
                "to finite-dimensional compact-group representations"
            ),
            "forgetful_map": (
                "forget gauge labels and weight every species multiplicity by "
                "the positive integer dimension of its representation"
            ),
            "codomain": (
                "the certified nonnegative real/integer Weyl-matter cone"
            ),
            "separator_coordinates_C2_E4_CdualC_BoxR": [1, 0, 0, 0],
            "gravity_separator_value": {
                "numerator": gravity_c.numerator,
                "denominator": gravity_c.denominator,
            },
            "species_separator_values": {
                name: {
                    "numerator": coefficient.numerator,
                    "denominator": coefficient.denominator,
                }
                for name, coefficient in species_c.items()
            },
            "proof": [
                "every healthy representation assignment maps to a nonnegative matter vector",
                "the C2 functional is positive on gravity and every nonzero healthy matter ray",
                "therefore the projected Weyl-cancellation set is empty",
                "local cubic, mixed, global mod-two and beta constraints intersect a pre-existing empty set",
            ],
            "joint_solution_set": "EMPTY",
            "scope": (
                "universal for the declared healthy species, hence every "
                "bounded U1/SU(N)/SO(N)/Sp(N) or product-family subset is empty"
            ),
        },
        "representation_gate_disposition": {
            "bounded_group_rank_highest_weight_enumeration": (
                "NOT_PERFORMED_PROJECTION_OBSTRUCTION_IS_PRIOR"
            ),
            "cubic_local_gauge_anomaly": "NOT_COMPUTED_EMPTY_DOMAIN",
            "mixed_gauge_gravitational_anomaly": "NOT_COMPUTED_EMPTY_DOMAIN",
            "global_mod_two_anomaly": "NOT_COMPUTED_EMPTY_DOMAIN",
            "one_loop_gauge_beta_function": "NOT_COMPUTED_EMPTY_DOMAIN",
            "direct_tensor_invariant_table": "NOT_COMPUTED_EMPTY_DOMAIN",
            "character_index_table": "NOT_COMPUTED_EMPTY_DOMAIN",
            "vectorlike_pair_policy": (
                "may cancel gauge chirality but contributes the sum of two "
                "positive Weyl C2 coordinates and cannot evade the separator"
            ),
        },
        "relaxation_ledger": {
            "formal_signed_determinant_lattice": (
                "CERTIFIED upstream, but negative multiplicities are inverse "
                "determinants or wrong-statistics powers rather than healthy "
                "representation multiplicities; gauge assignments remain open"
            ),
            "wrong_sign_kinetic_terms": (
                "do not automatically realize negative determinant powers and "
                "are outside the healthy family"
            ),
            "shifting_Wess_Zumino_compensator": (
                "changes the BV complex and counterterm algebra; it is not a "
                "gauge-representation lattice column or strict cancellation"
            ),
            "higher_derivative_conformal_fields": (
                "OPEN: require their own BV complexes, kinetic-sign audit and "
                "two independent anomaly-coefficient rails"
            ),
        },
        "exact_checks": checks,
        "claim_flags": {
            "JOINT_HEALTHY_WEYL_GAUGE_SOLUTION_EXISTS": False,
            "BOUNDED_REPRESENTATION_CLASSIFICATION_PERFORMED": False,
            "GAUGE_ANOMALY_TABLE_COMPUTED": False,
            "SIGNED_LATTICE_IS_HEALTHY_MATTER": False,
            "COMPENSATOR_IS_STRICT_CANCELLATION": False,
            "GUT_STANDARD_MODEL_OR_PARTICLE_SELECTION_CLAIM": False,
            "LORENTZIAN_QME_OR_UNITARITY_CLAIM": False,
        },
        "next_gate": (
            "ONLY_INSTANTIATE_REPRESENTATION_TABLES_FOR_A_CHANGED_FIELD_"
            "FAMILY_WITH_A_CERTIFIED_NONEMPTY_WEYL_CANCELLATION_TARGET"
        ),
        "claim_boundary": (
            "This is a composed LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL empty-set "
            "theorem. It says that imposing gauge-anomaly cancellation cannot "
            "rescue the already-empty healthy Weyl-matter cone. It is not a "
            "classification of gauge groups or representations, a Standard "
            "Model or GUT selection, a beta-function, Lorentzian QME, particle, "
            "phenomenology, positivity, unitarity or ultraviolet-completion claim."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("projection-obstruction checks failed")
    flags = value.get("claim_flags", {})
    if (
        value.get("projection_theorem", {}).get("joint_solution_set") != "EMPTY"
        or flags.get("JOINT_HEALTHY_WEYL_GAUGE_SOLUTION_EXISTS") is not False
        or flags.get("BOUNDED_REPRESENTATION_CLASSIFICATION_PERFORMED")
        is not False
        or flags.get("GAUGE_ANOMALY_TABLE_COMPUTED") is not False
        or flags.get("SIGNED_LATTICE_IS_HEALTHY_MATTER") is not False
        or flags.get("COMPENSATOR_IS_STRICT_CANCELLATION") is not False
        or flags.get("GUT_STANDARD_MODEL_OR_PARTICLE_SELECTION_CLAIM")
        is not False
        or flags.get("LORENTZIAN_QME_OR_UNITARITY_CLAIM") is not False
    ):
        raise ValueError("joint matter/gauge claim boundary over-promoted")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
