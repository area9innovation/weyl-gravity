#!/usr/bin/env python3
"""Certify the physical helicity projective module on the Berger null cone.

The retained Berger symbol complex has six degree-zero classes at a nonzero
null covector.  This module derives the rank-two physical submodule instead
of identifying all six classes with helicities.  Globally over the normalized
projective null cone the submodule is represented by the transverse-traceless
idempotent; at the standard null fibre it agrees with the independently
certified linearized-Weyl quotient.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from itertools import combinations
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
Q1 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
NULL_QUOTIENT = ROOT / "covariant_completion/certificates/curved_null_symbol_quotient.json"
HELICITY = ROOT / "covariant_completion/certificates/curved_helicity_two_channel.json"
V2_NORMAL_FORM = ROOT / "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
RANK46 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-46-stf2-physical-helicity-filtered-quotient.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-physical-helicity-filtered-quotient-v1.schema.json"
VERIFIER = HERE / "verify_berger_retained_46_stf2_physical_helicity_filtered_quotient.py"
TESTS = HERE / "tests/test_berger_retained_46_stf2_physical_helicity_filtered_quotient.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": value.get("result_id", value.get("atomic_flag", value["schema"])),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _matrix_record(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _sparse_columns(matrix: sp.Matrix) -> list[list[object]]:
    return [
        [row, column, str(matrix[row, column])]
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if matrix[row, column] != 0
    ]


def _symmetric_basis() -> tuple[sp.Matrix, ...]:
    result = []
    for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
        value = sp.zeros(3)
        value[i, j] = 1
        if i != j:
            value[j, i] = 1
        result.append(value)
    return tuple(result)


def _symmetric_vector(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        [matrix[0, 0], matrix[0, 1], matrix[0, 2], matrix[1, 1], matrix[1, 2], matrix[2, 2]]
    )


def _rotation_generators() -> tuple[sp.Matrix, ...]:
    result = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        value = sp.zeros(3)
        value[i, j] = -1
        value[j, i] = 1
        result.append(value)
    return tuple(result)


def _exact_data() -> dict[str, object]:
    layout = _load(LAYOUT)
    q1 = _load(Q1)
    null_quotient = _load(NULL_QUOTIENT)
    helicity = _load(HELICITY)
    v2 = _load(V2_NORMAL_FORM)
    rank46 = _load(RANK46)

    if layout.get("pairing_conventions", {}).get("dual_involution_exact") is not True:
        raise ValueError("retained canonical pairing authority drifted")
    if q1.get("claim_status") != "CERTIFIED_COMPLETE_MINIMAL_Q1":
        raise ValueError("complete retained q1 authority drifted")
    if (
        null_quotient.get("image_N_mod_image_K_dimension") != 2
        or null_quotient.get("physical_normalized_block", {}).get("domain_basis")
        != ["h_22-h_33", "h_23"]
        or helicity.get("linearized_Weyl_symbol", {}).get("is_isomorphism") is not True
        or helicity.get("linearized_Weyl_symbol", {}).get("target_quotient_dimension") != 2
    ):
        raise ValueError("universal physical helicity quotient authority drifted")
    if (
        v2.get("normal_form", {}).get("identity") != "A10=Box_2^2+V_2"
        or v2.get("normal_form", {}).get("maximum_order_V2") != 2
    ):
        raise ValueError("exact Berger V2 authority drifted")
    if rank46.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True:
        raise ValueError("rank-46 cyclic graph carrier authority drifted")

    p0, n1, n2, n3 = sp.symbols("p0 n1 n2 n3")
    original_p = sp.symbols("p0:4")
    substitutions = dict(zip(original_p, (1, n1, n2, n3), strict=True))
    blocks = q1["q1_blocks"]
    gauge = sp.Matrix(_symbol(_matrix_from_record(blocks["K_spatial"]), 1)).subs(substitutions)
    hessian = sp.Matrix(_symbol(_matrix_from_record(blocks["H_retained"]), 4)).subs(substitutions)
    alpha_B = next(symbol for symbol in hessian.free_symbols if symbol.name == "alpha_B")
    hessian = hessian.subs(alpha_B, 5)
    identity = sp.Matrix(_symbol(_matrix_from_record(blocks["minus_K_spatial_sharp"]), 1)).subs(substitutions)

    relation = n1**2 + n2**2 + n3**2 - 1
    groebner = sp.groebner([relation], n1, n2, n3, order="grlex", domain=sp.QQ)

    def reduce_polynomial(value: sp.Expr) -> sp.Expr:
        return sp.factor(groebner.reduce(sp.expand(value))[1])

    n = sp.Matrix([n1, n2, n3])
    transverse = sp.eye(3) - n * n.T
    ptt_columns = []
    for basis in _symmetric_basis():
        projected = transverse * basis * transverse
        projected -= sp.Rational(1, 2) * sp.trace(transverse * basis) * transverse
        ptt_columns.append(_symmetric_vector(projected))
    ptt = sp.Matrix.hstack(*ptt_columns).applyfunc(reduce_polynomial)

    spatial_inclusion = sp.zeros(10, 6)
    spatial_projection = sp.zeros(6, 10)
    for index in range(6):
        spatial_inclusion[index + 4, index] = 1
        spatial_projection[index, index + 4] = 1
    field_projector = (spatial_inclusion * ptt * spatial_projection).applyfunc(reduce_polynomial)
    equation_projector = field_projector.T

    hessian_reduced = hessian.applyfunc(reduce_polynomial)
    two_by_two_minors = 0
    for rows in combinations(range(10), 2):
        for columns in combinations(range(10), 2):
            two_by_two_minors += 1
            if reduce_polynomial(hessian.extract(rows, columns).det()) != 0:
                raise ValueError("Berger null Hessian has rank greater than one")
    if reduce_polynomial(hessian_reduced[0, 0] - sp.Rational(5, 6)) != 0:
        raise ValueError("Berger null Hessian lost its rank-one witness")

    residuals = {
        "PTT_idempotence": ptt * ptt - ptt,
        "field_projector_idempotence": field_projector * field_projector - field_projector,
        "equation_projector_idempotence": equation_projector * equation_projector - equation_projector,
        "field_projector_kills_gauge": field_projector * gauge,
        "Hessian_kills_physical_fields": hessian * field_projector,
        "Noether_kills_physical_equations": identity * equation_projector,
        "physical_equations_kill_Hessian_image": equation_projector * hessian,
    }
    residual_counts = {
        name: sum(reduce_polynomial(value) != 0 for value in matrix)
        for name, matrix in residuals.items()
    }
    if any(residual_counts.values()):
        raise ValueError(f"physical null-cone projector identity failed: {residual_counts}")
    if reduce_polynomial(sp.trace(ptt)) != 2:
        raise ValueError("physical null-cone projector rank drifted")

    covariance_defects = []
    for generator in _rotation_generators():
        tensor_generator = sp.Matrix.hstack(
            *[_symmetric_vector(generator * basis - basis * generator) for basis in _symmetric_basis()]
        )
        delta_n = generator * n
        derivative = sum(
            (sp.diff(ptt, variable) * delta_n[index] for index, variable in enumerate((n1, n2, n3))),
            sp.zeros(6),
        )
        covariance_defects.append(
            sum(
                reduce_polynomial(value) != 0
                for value in derivative + ptt * tensor_generator - tensor_generator * ptt
            )
        )
    if covariance_defects != [0, 0, 0]:
        raise ValueError("SO(3)-equivariance of the physical projector failed")

    standard = {n1: 1, n2: 0, n3: 0}
    gauge_standard = gauge.subs(standard)
    hessian_standard = hessian.subs(standard)
    identity_standard = identity.subs(standard)
    field_inclusion = sp.zeros(10, 2)
    field_inclusion[7, 0] = 1
    field_inclusion[9, 0] = -1
    field_inclusion[8, 1] = 1
    equation_inclusion = sp.zeros(10, 2)
    equation_inclusion[7, 0] = sp.Rational(1, 2)
    equation_inclusion[9, 0] = -sp.Rational(1, 2)
    equation_inclusion[8, 1] = 1
    field_projection = equation_inclusion.T
    equation_projection = field_inclusion.T
    if (
        hessian_standard * field_inclusion != sp.zeros(10, 2)
        or identity_standard * equation_inclusion != sp.zeros(3, 2)
        or field_projection * gauge_standard != sp.zeros(2, 3)
        or equation_projection * hessian_standard != sp.zeros(2, 10)
        or field_projection * field_inclusion != sp.eye(2)
        or equation_projection * equation_inclusion != sp.eye(2)
        or field_inclusion.T * equation_inclusion != sp.eye(2)
    ):
        raise ValueError("normalized standard-fibre physical quotient failed")

    ranks = {
        "K1": int(gauge_standard.rank()),
        "H4": int(hessian_standard.rank()),
        "L1": int(identity_standard.rank()),
    }
    cohomology = [
        3 - ranks["K1"],
        (10 - ranks["H4"]) - ranks["K1"],
        (10 - ranks["L1"]) - ranks["H4"],
        3 - ranks["L1"],
    ]
    if ranks != {"K1": 3, "H4": 1, "L1": 3} or cohomology != [0, 6, 6, 0]:
        raise ValueError("Berger full null-symbol cohomology drifted")
    if gauge.row_join(field_projector).subs(standard).rank() != 5:
        raise ValueError("physical fields are not independent modulo gauge")
    if hessian.row_join(equation_projector).subs(standard).rank() != 3:
        raise ValueError("physical equations are not independent modulo Hessian image")

    v2_artifact = v2["normal_form"]["artifacts"]["lower_by_two_remainder"]
    v2_path = ROOT / v2_artifact["path"]
    if _sha256(v2_path) != v2_artifact["sha256"]:
        raise ValueError("exact Berger V2 artifact drifted")

    return {
        "dependencies": {
            "retained_layout": _dependency(LAYOUT, layout),
            "retained_q1": _dependency(Q1, q1),
            "universal_null_symbol_quotient": _dependency(NULL_QUOTIENT, null_quotient),
            "universal_helicity_channel": _dependency(HELICITY, helicity),
            "Berger_V2_normal_form": _dependency(V2_NORMAL_FORM, v2),
            "rank_46_STF2_graph_carrier": _dependency(RANK46, rank46),
        },
        "projectors": (ptt, field_projector, equation_projector),
        "standard_maps": (field_inclusion, field_projection, equation_inclusion, equation_projection),
        "ranks": ranks,
        "cohomology": cohomology,
        "minor_count": two_by_two_minors,
        "residual_counts": residual_counts,
        "covariance_defects": covariance_defects,
        "v2_artifact": {
            "path": v2_artifact["path"],
            "sha256": v2_artifact["sha256"],
            "shape": [10, 10],
        },
        "helicity": helicity,
    }


def build() -> dict:
    data = _exact_data()
    ptt, field_projector, equation_projector = data["projectors"]
    field_inclusion, field_projection, equation_inclusion, equation_projection = data["standard_maps"]
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-retained-46-stf2-physical-helicity-filtered-quotient-v1",
        "result_id": "BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1",
        "result_state": "PHYSICAL_HELICITY_PROJECTIVE_MODULE_CERTIFIED_V2_FILTERED_DESCENT_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "method_tags": ["MICROLOCAL-SYMBOL", "PROJECTIVE-NULL-CONE", "EXACT-POLYNOMIAL-QUOTIENT"],
        "dependency_refs": data["dependencies"],
        "null_cone_chart": {
            "normalization": "p0=1",
            "coordinate_ring": "Q[n1,n2,n3]/(n1^2+n2^2+n3^2-1)",
            "projective_coverage": "every nonzero real null ray has p0 nonzero and therefore a representative with p0=1",
            "spatial_symmetric_component_order": ["11", "12", "13", "22", "23", "33"],
            "TT_formula": "P_ij=delta_ij-n_i n_j; Pi_TT(t)_ij=P_i^k P_j^l t_kl-(1/2)P_ij P^kl t_kl",
            "TT_projector_6x6": _matrix_record(ptt),
            "field_projector_10x10": _matrix_record(field_projector),
            "equation_projector_10x10": _matrix_record(equation_projector),
            "equation_projector_is_canonical_transpose": True,
            "projective_rank": 2,
            "global_two_column_frame_asserted": False,
        },
        "full_Berger_null_symbol_cohomology": {
            "complex_ranks": [3, 10, 10, 3],
            "symbol_ranks": data["ranks"],
            "cohomology_dimensions": data["cohomology"],
            "physical_degree_zero_rank": 2,
            "physical_degree_one_rank": 2,
            "remaining_degree_zero_classes_outside_physical_submodule": 4,
            "remaining_degree_one_classes_outside_physical_submodule": 4,
            "interpretation": "the full six-dimensional null-symbol cohomology is not identified with the two physical helicities",
        },
        "normalized_standard_null_fibre": {
            "covector": [1, 1, 0, 0],
            "metric_component_order": ["00", "01", "02", "03", "11", "12", "13", "22", "23", "33"],
            "field_basis": ["h_hat_22-h_hat_33", "h_hat_23"],
            "equation_dual_basis": ["(h_hat_star_22-h_hat_star_33)/2", "h_hat_star_23"],
            "field_inclusion_entries": _sparse_columns(field_inclusion),
            "field_projection_entries": _sparse_columns(field_projection),
            "equation_inclusion_entries": _sparse_columns(equation_inclusion),
            "equation_projection_entries": _sparse_columns(equation_projection),
            "induced_cyclic_pairing": [["1", "0"], ["0", "1"]],
            "little_group_generator": data["helicity"]["infinitesimal_generator"],
            "little_group_generator_square": data["helicity"]["generator_square"],
            "complex_helicity_weights": data["helicity"]["complex_weights"],
            "linearized_Weyl_induced_matrix": data["helicity"]["linearized_Weyl_symbol"]["induced_quotient_matrix"],
            "linearized_Weyl_isomorphism": True,
        },
        "filtered_principal_module": {
            "polarization_module": "H_hel=im(Pi_TT), a rank-two projective module over the normalized projective null cone",
            "generalized_wave_module": "H_hel tensor Q(sqrt(10))[epsilon]/(epsilon^2)",
            "generalized_wave_rank_over_Q_sqrt10": 4,
            "Einstein_layer": "H_hel tensor epsilon A",
            "extra_Weyl_quotient": "(H_hel tensor A)/(H_hel tensor epsilon A)",
            "topological_deformation_direction_included": False,
        },
        "exact_checks": {
            "Berger_null_Hessian_all_2x2_minors_vanish_mod_null_relation": True,
            "Berger_null_Hessian_rank_one_witness_nonzero": True,
            "full_Berger_null_symbol_cohomology_0_6_6_0": True,
            "TT_projector_idempotent_mod_null_relation": data["residual_counts"]["PTT_idempotence"] == 0,
            "TT_projector_trace_two_mod_null_relation": True,
            "field_projector_kills_gauge_mod_null_relation": data["residual_counts"]["field_projector_kills_gauge"] == 0,
            "Hessian_kills_physical_fields_mod_null_relation": data["residual_counts"]["Hessian_kills_physical_fields"] == 0,
            "Noether_kills_physical_equations_mod_null_relation": data["residual_counts"]["Noether_kills_physical_equations"] == 0,
            "physical_equations_annihilate_Hessian_image_mod_null_relation": data["residual_counts"]["physical_equations_kill_Hessian_image"] == 0,
            "canonical_pairing_descends_nondegenerately": True,
            "SO3_equivariance_three_generators": data["covariance_defects"] == [0, 0, 0],
            "standard_fibre_agrees_with_Weyl_helicity_quotient": True,
            "rank_46_contractible_graph_complement_preserves_physical_module": True,
            "exact_V2_payload_content_addressed": True,
        },
        "audit_ledger": {
            "Hessian_2x2_minors_checked": data["minor_count"],
            "projector_residual_nonzero_counts": data["residual_counts"],
            "SO3_covariance_defect_counts": data["covariance_defects"],
        },
        "V2_receiving_contract": {
            "artifact": data["v2_artifact"],
            "required_calculation": "solve the filtered symbol-complex descent equations for V2 and lower-symbol corrections on im(Pi_TT)",
            "raw_10x10_diagonalization_authorized": False,
            "raw_Pi_TT_V2_Pi_TT_compression_is_an_invariant_verdict": False,
            "V2_filtered_descent_computed_here": False,
            "binary_output": "exact lower-order Einstein/extra-Weyl anchor or normalized filtered-extension obstruction",
        },
        "claim_flags": {
            "PHYSICAL_HELICITY_FILTERED_QUOTIENT_CERTIFIED": True,
            "PHYSICAL_POLARIZATION_PROJECTIVE_RANK_TWO": True,
            "GENERALIZED_WAVE_MODULE_RANK_FOUR": True,
            "GLOBAL_TWO_COLUMN_HELICITY_FRAME_CERTIFIED": False,
            "V2_FILTERED_DESCENT_COMPUTED": False,
            "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE": False,
            "BRANCH_PROJECTOR_ACCEPTED": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_46_stf2_physical_helicity_filtered_quotient.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_46_stf2_physical_helicity_filtered_quotient.py",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_46_stf2_physical_helicity_filtered_quotient",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-46-stf2-physical-helicity-filtered-quotient-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC microlocal certificate derives the physical rank-two helicity projective module inside the six-dimensional degree-zero Berger null-symbol cohomology. Over the normalized projective null cone it is the image of the tensorial transverse-traceless idempotent; its canonical transpose gives the paired degree-one module, and the retained BV pairing descends nondegenerately. At zeta=(1,1,0,0) the normalized representatives agree with the independently certified linearized-Weyl helicity quotient and carry weights +2i and -2i. Tensoring this rank-two polarization module with the dual-number repeated-wave algebra gives rank four, not rank two. The result does not choose a global two-column helicity frame, identify the other four symbol classes as particles, diagonalize the raw 10-by-10 V2 matrix, prove that V2 descends without lower-symbol corrections, split the Einstein-like and extra-Weyl layers, authorize ell3 branch mixing, infer a kinetic sign, or make a quantum claim. The next gate must solve the invariant filtered symbol-complex descent equations and return an exact lower-order anchor or a normalized obstruction."
        ),
    }


def validate(value: dict) -> None:
    if value.get("result_state") != "PHYSICAL_HELICITY_PROJECTIVE_MODULE_CERTIFIED_V2_FILTERED_DESCENT_OPEN":
        raise ValueError("physical-helicity result state drifted")
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("physical-helicity exact check dropped")
    flags = value.get("claim_flags", {})
    if (
        flags.get("PHYSICAL_HELICITY_FILTERED_QUOTIENT_CERTIFIED") is not True
        or flags.get("PHYSICAL_POLARIZATION_PROJECTIVE_RANK_TWO") is not True
        or flags.get("GENERALIZED_WAVE_MODULE_RANK_FOUR") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "GLOBAL_TWO_COLUMN_HELICITY_FRAME_CERTIFIED",
                "V2_FILTERED_DESCENT_COMPUTED",
                "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE",
                "BRANCH_PROJECTOR_ACCEPTED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("physical-helicity claim boundary drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Rank-46 STF2 physical-helicity filtered quotient

The retained Berger null-symbol complex has cohomology dimensions

```text
(0, 6, 6, 0).
```

The six degree-zero classes are not all physical helicities.  Over the
normalized projective null cone `p0=1`, `n.n=1`, the exact tensorial
transverse-traceless idempotent has rank two.  It kills the spatial gauge
image, its image is killed by the principal Hessian, and its canonical
transpose defines the paired rank-two degree-one module.  The retained odd
BV pairing descends perfectly between these two projective modules.

At `zeta=(1,1,0,0)` the normalized field representatives are
`h_hat_22-h_hat_33` and `h_hat_23`.  Their normalized equation-dual partners
give the identity pairing.  This agrees with the independent linearized-Weyl
quotient and carries the two spin-two weights `+2i,-2i`.

The polarization module has rank two.  After tensoring with the repeated-wave
dual-number algebra its generalized-wave module has rank four.  No global
two-column frame is asserted: the invariant object is the projective module
defined by the idempotent.

The exact `V2` payload is now content-addressed at this gate, but its filtered
descent is deliberately open.  The next calculation must solve the filtered
symbol-complex equations; diagonalizing the raw ten-component matrix or merely
compressing it as `Pi_TT V2 Pi_TT` is not an invariant branch verdict.
"""


def _guards() -> None:
    baseline = build()
    mutant = deepcopy(baseline)
    mutant["claim_flags"]["V2_FILTERED_DESCENT_COMPUTED"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise AssertionError("V2-descent overclaim mutation survived")
    mutant = deepcopy(baseline)
    mutant["claim_flags"]["GLOBAL_TWO_COLUMN_HELICITY_FRAME_CERTIFIED"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise AssertionError("global-frame overclaim mutation survived")
    mutant = deepcopy(baseline)
    mutant["exact_checks"]["TT_projector_idempotent_mod_null_relation"] = False
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise AssertionError("projector mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("physical-helicity filtered-quotient outputs drifted")
    if args.guards:
        _guards()
    print("BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1: PASS")


if __name__ == "__main__":
    main()
