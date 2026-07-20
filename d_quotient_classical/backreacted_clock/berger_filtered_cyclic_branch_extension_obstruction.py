#!/usr/bin/env python3
"""Certify the first filtered cyclic obstruction to a Berger branch split."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-filtered-cyclic-branch-extension-obstruction.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-filtered-cyclic-branch-extension-obstruction-v1.schema.json"
)
VERIFIER = HERE / "verify_berger_filtered_cyclic_branch_extension_obstruction.py"
TESTS = (
    HERE
    / "tests/test_berger_filtered_cyclic_branch_extension_obstruction.py"
)

PHYSICAL = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json"
)
SUBPRINCIPAL = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json"
)
GRAPH46 = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
)
PAIRING36 = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
)
K_CARTAN = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json"
)
ELL3 = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: Mapping[str, object]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _validate_dependencies() -> dict[str, dict]:
    physical = _load(PHYSICAL)
    subprincipal = _load(SUBPRINCIPAL)
    graph46 = _load(GRAPH46)
    pairing36 = _load(PAIRING36)
    k_cartan = _load(K_CARTAN)
    ell3 = _load(ELL3)

    if (
        physical.get("result_state")
        != "PHYSICAL_HELICITY_PROJECTIVE_MODULE_CERTIFIED_V2_FILTERED_DESCENT_OPEN"
        or physical.get("filtered_principal_module", {}).get(
            "generalized_wave_rank_over_Q_sqrt10"
        )
        != 4
        or physical.get("null_cone_chart", {}).get("projective_rank") != 2
    ):
        raise ValueError("principal branch-sequence authority drifted")
    if (
        subprincipal.get("result_state")
        != "SUBPRINCIPAL_PHYSICAL_MODULE_LIFT_OBSTRUCTED_AT_STANDARD_NULL_FIBRE"
        or subprincipal.get("normalized_obstruction", {}).get(
            "normalized_evaluation_on_physical_columns"
        )
        != [["1", "0"]]
        or not all(subprincipal.get("exact_checks", {}).values())
    ):
        raise ValueError("subprincipal obstruction authority drifted")
    if (
        graph46.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True
        or graph46.get("flags", {}).get("CANONICAL_BRANCH_PROJECTOR_CERTIFIED")
        is not False
        or graph46.get("graph_construction", {}).get("Schur_complement") != "A10"
    ):
        raise ValueError("rank-46 cyclic graph authority drifted")
    if (
        pairing36.get("claim_status")
        != "CERTIFIED_EXPLICIT_TYPED_64_36_CYCLIC_CARRIER"
        or pairing36.get("retained_complex", {}).get("total_rows") != 36
        or pairing36.get("flags", {}).get("BERGER_EXPLICIT_TYPED_PAIRING_36")
        is not True
        or pairing36.get("exact_checks", {}).get("q36_typed_pairing_cyclic")
        is not True
    ):
        raise ValueError("retained cyclic pairing authority drifted")
    if (
        k_cartan.get("claim_status")
        != "CERTIFIED_COUPLED_CAUSAL_CYCLIC_K_CARTAN_THROUGH_ARITY_THREE"
        or k_cartan.get("flags", {}).get(
            "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"
        )
        is not True
        or k_cartan.get("exact_checks", {}).get(
            "typed_retained36_C3_C4_cyclicity_audited"
        )
        is not True
    ):
        raise ValueError("retained residual-action authority drifted")
    if (
        ell3.get("result_state")
        != "FILTERED_CYCLIC_FULL_BV_REMOVAL_OBSTRUCTED_AT_FIRST_ASSOCIATED_GRADED_PAGE"
        or ell3.get("claim_flags", {}).get(
            "FILTERED_CYCLIC_REDEFINITION_OBSTRUCTED_AT_FIRST_PAGE"
        )
        is not True
        or ell3.get("claim_flags", {}).get("BRANCH_PROJECTION_DECIDED")
        is not False
    ):
        raise ValueError("retained ell3 obstruction authority drifted")
    return {
        "physical": physical,
        "subprincipal": subprincipal,
        "graph46": graph46,
        "pairing36": pairing36,
        "k_cartan": k_cartan,
        "ell3": ell3,
    }


def _canonical_incidence_fixture() -> dict[str, object]:
    """Put the certified rank ledger into its exact active normal form."""

    # Four admitted boundary directions in a five-dimensional active target.
    boundary = sp.Matrix(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0],
        ]
    )
    # The plus column is transverse; the cross column is the fourth boundary.
    target = sp.Matrix(
        [
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 1],
            [1, 0],
        ]
    )
    witness = sp.Matrix([[0, 0, 0, 0, 1]])
    canonical_repair = sp.Matrix([0, 0, 0, 0, 1])
    extended = boundary.row_join(canonical_repair)

    ledger = {
        "allowed_boundary": int(boundary.rank()),
        "plus_augmented": int(boundary.row_join(target[:, 0]).rank()),
        "cross_augmented": int(boundary.row_join(target[:, 1]).rank()),
        "both_augmented": int(boundary.row_join(target).rank()),
    }
    if ledger != {
        "allowed_boundary": 4,
        "plus_augmented": 5,
        "cross_augmented": 4,
        "both_augmented": 5,
    }:
        raise AssertionError("canonical incidence rank ledger failed")
    if witness * boundary != sp.zeros(1, 4):
        raise AssertionError("canonical witness does not annihilate boundaries")
    if witness * target != sp.Matrix([[1, 0]]):
        raise AssertionError("canonical witness normalization failed")
    if extended.rank() != 5 or extended.row_join(target).rank() != 5:
        raise AssertionError("one-generator canonical repair did not close the page")

    obstruction_rank = int(boundary.row_join(target).rank() - boundary.rank())
    if obstruction_rank != 1:
        raise AssertionError("obstruction-image rank drifted")
    return {
        "normal_form_field": "Q(sqrt(10))",
        "active_boundary_shape": [5, 4],
        "physical_target_shape": [5, 2],
        "rank_ledger": ledger,
        "normalized_cokernel_evaluation": ["1", "0"],
        "obstruction_image_rank": obstruction_rank,
        "zero_new_boundary_directions_sufficient": False,
        "one_new_boundary_direction_sufficient_at_page": True,
        "canonical_new_boundary_column": ["0", "0", "0", "0", "1"],
        "extended_boundary_rank": int(extended.rank()),
        "extended_augmented_rank": int(extended.row_join(target).rank()),
        "minimum_new_field_directions": obstruction_rank,
        "minimum_cyclic_BV_rows": 2 * obstruction_rank,
    }


def build() -> dict:
    dependencies = _validate_dependencies()
    subprincipal = dependencies["subprincipal"]
    fixture = _canonical_incidence_fixture()
    if subprincipal["filtered_lift_problem"]["rank_ledger"] != fixture["rank_ledger"]:
        raise AssertionError("certified obstruction is not in the declared normal form")

    source_manifest = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    dependency_refs = {
        "principal_physical_branch_sequence": _dependency(
            PHYSICAL, dependencies["physical"]
        ),
        "subprincipal_lift_obstruction": _dependency(
            SUBPRINCIPAL, dependencies["subprincipal"]
        ),
        "rank_46_contractible_cyclic_graph": _dependency(
            GRAPH46, dependencies["graph46"]
        ),
        "retained_36_cyclic_pairing": _dependency(
            PAIRING36, dependencies["pairing36"]
        ),
        "retained_K_Berger_action": _dependency(
            K_CARTAN, dependencies["k_cartan"]
        ),
        "retained_mixed_ell3_obstruction": _dependency(
            ELL3, dependencies["ell3"]
        ),
    }

    return {
        "schema": "pure-weyl-berger-filtered-cyclic-branch-extension-obstruction-v1",
        "result_id": "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1",
        "result_state": "ARITY_ONE_FILTERED_CYCLIC_BRANCH_SPLITTING_OBSTRUCTED_MINIMAL_PAGE_REPAIR_CLASSIFIED",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "mode_scope": {
            "theory": "Weyl gravity coupled to the positive Berger clock and Maxwell field",
            "background": "compact positive Berger clock at the certified rational fixture",
            "boundaries": "closed compact slice; support-local PBW operator category",
            "charge_sector": "fixed coupling; retained gravity-clock-Maxwell bundle",
            "carrier": "typed retained 36-row cyclic BV complex, with the certified rank-46 STF2 contractible graph test",
            "degree": "full retained BV grading; physical branch anchor in degrees zero and one",
            "parity": "complete declared retained carrier",
            "ell": "NOT_APPLICABLE_LOCAL_PBW_CARRIER",
            "m": "NOT_APPLICABLE_LOCAL_PBW_CARRIER",
            "k": "standard null-symbol fibre zeta=(1,1,0,0), not a compact harmonic momentum",
            "omega": "principal null characteristic; no mode-frequency crosswalk",
        },
        "principal_exact_sequence": {
            "coefficient_field": "k=Q(sqrt(10))",
            "dual_number_algebra": "A=k[epsilon]/(epsilon^2)",
            "polarization_module": "H_hel, projective rank two on the normalized null cone",
            "sequence": "0 -> E_E -> E_W -> E_X -> 0",
            "Einstein_module": "E_E=H_hel tensor epsilon*A",
            "Weyl_module": "E_W=H_hel tensor A",
            "extra_module": "E_X=H_hel tensor A/(epsilon*A)",
            "inclusion": "i_E(h tensor epsilon)=h tensor epsilon",
            "quotient": "p_X(h tensor (a+b*epsilon))=h tensor a",
            "exactness": "ker(p_X)=im(i_E)=H_hel tensor epsilon*A",
            "interpretation": "an associated-principal repeated-wave extension; not an already lifted branch decomposition of the retained differential complex",
        },
        "admissible_category": {
            "objects": "finite filtered local BV complexes over Q(sqrt(10)) with q1, nondegenerate typed cyclic pairing, retained K_Berger action, and declared q2/q3/ell3 operations",
            "unary_maps": [
                "finite-order support-local PBW operators of nonnegative filtration",
                "degree preserving q1 chain maps",
                "typed-cyclic adjoint compatible",
                "K_Berger equivariant on the retained carrier",
                "no inverse Laplacian, Green operator, TT/helicity mode projector, or row-name branch assignment",
            ],
            "branch_split": "filtered chain inclusion s:E_E->E_W and projection r:E_W->E_E with r*s=id, equivalently a cyclic self-adjoint q1-intertwining idempotent P_E=s*r with the declared principal anchor",
            "nonlinear_split": "a cyclic filtered L_infinity isomorphism whose unary term realizes the branch split and whose higher F2/F3 terms respect the same filtration and residual action",
            "equivalence": "conjugation by invertible filtered cyclic K_Berger-equivariant chain maps, together with admissible higher F2/F3 redefinitions; higher terms do not alter existence of the unary idempotent",
            "residual_action": "K_Berger=D-omega*R on the retained 36-row carrier through arity three",
            "pairing": "the certified typed odd BV pairing induced by the cyclic 64-to-36 SDR",
        },
        "first_obstruction_class": {
            "name": "beta_1",
            "lifting_map": "M=[sigma_4(H_retained), J_phys, sigma_2(V2)*sigma_1(K_spatial)]",
            "target": "T=sigma_2(V2)*I_phys",
            "class": "beta_1=pi_coker(M)*T in Hom(H_hel,coker(M))",
            "necessary_and_sufficient_page_test": "the declared physical principal module lifts through the first nonzero filtered page iff beta_1=0, equivalently rank([M,T])=rank(M)",
            "allowed_freedoms_quotiented": [
                "every principal Hessian boundary",
                "every physical-equation representative",
                "every principal spatial-gauge change of the field representatives",
            ],
            "certified_rank_ledger": subprincipal["filtered_lift_problem"][
                "rank_ledger"
            ],
            "normalized_witness": subprincipal["normalized_obstruction"][
                "normalized_left_null_covector"
            ],
            "normalized_evaluation": subprincipal["normalized_obstruction"][
                "normalized_evaluation_on_physical_columns"
            ],
            "obstructed_polarization": "h_hat_22-h_hat_33",
            "lifted_polarization": "h_hat_23",
            "lifted_cross_coefficient": subprincipal["normalized_obstruction"][
                "cross_physical_equation_coefficient"
            ],
            "invariance": "an admissible unary change induces isomorphisms of coker(M) and H_hel, so beta_1 is conjugated; its zero/nonzero verdict and image rank are invariant",
        },
        "splitting_theorem": {
            "statement": "No admissible filtered cyclic Einstein-image/additional-Weyl splitting with the certified physical principal anchor exists on the retained 36-row complex or on its certified rank-46 contractible STF2 graph prolongation.",
            "proof_chain": [
                "a cyclic L_infinity branch split has a unary filtered cyclic chain split",
                "a unary split restricts at the standard null fibre to a lift of both physical principal columns",
                "the first-page lift exists iff beta_1 vanishes",
                "the normalized exact witness evaluates beta_1 as (1,0)",
                "therefore the unary split, and hence the full cyclic L_infinity split, does not exist in the declared category",
                "the rank-46 STF2 enlargement is a cyclic contractible graph SDR with Schur complement A10, so it induces the same obstruction quotient and cannot kill beta_1",
            ],
            "nonlinear_higher_map_consequence": "F2 and F3 cannot repair failure of the arity-one idempotent; no q2/q3/ell3 branch-mixing table is authorized",
        },
        "minimal_page_enlargement_classification": {
            "category": "finite-dimensional cyclic extensions of the first filtered lifting page, modulo filtered cyclic isomorphism and addition of contractible hyperbolic pairs",
            "general_obstruction_map": "o:H->Q=coker(M)",
            "repair_datum": "an added field correction space Z with page-boundary map j:Z->Q; cyclicity adds the dual equation space Z^vee",
            "necessity_and_sufficiency": "the page lifts after enlargement iff im(o) is contained in im(j)",
            "minimum": "dim(Z)=rank(o); every minimal repair identifies Z isomorphically with im(o), and its cyclic completion is the hyperbolic pair Z direct-sum Z^vee",
            "contractible_case": "a filtered cyclic SDR enlargement induces an isomorphism on Q and has zero new image in the obstruction quotient, so it cannot change a nonzero o",
            "equivariant_case": "with a certified residual action, replace im(o) by its smallest invariant submodule W; the minimum is dim(W) field directions and dim(W) cyclic-dual equation directions",
            "standard_fibre": fixture,
            "classification_table": [
                {
                    "new_boundary_directions": 0,
                    "cyclic_BV_rows": 0,
                    "verdict": "OBSTRUCTED",
                    "reason": "rank(o)=1",
                },
                {
                    "new_boundary_directions": 1,
                    "cyclic_BV_rows": 2,
                    "verdict": "PAGE_SUFFICIENT_ONLY_IF_NONCONTRACTIBLE",
                    "reason": "one column spanning im(o) is necessary and sufficient at the standard fibre",
                },
                {
                    "new_boundary_directions": "s>=1",
                    "cyclic_BV_rows": "2s",
                    "verdict": "PAGE_SUFFICIENT_IFF_IM_O_SUBSET_IM_J",
                    "reason": "complete rank criterion; extra contractible pairs do not contribute to coker(M)",
                },
            ],
            "global_realization_boundary": "the rank of the K_Berger-equivariant global bundle closure W and the higher-page nilpotent/cyclic realization are not certified; the existing rank-46 STF2 graph is contractible and fails",
        },
        "relation_to_retained_ell3": {
            "unary_extension_class": "beta_1 is the first filtered obstruction to lifting/splitting the physical branch sequence",
            "ternary_deformation_class": "the separate 22-row witness proves the retained mixed ell3 is nonremovable in the declared filtered cyclic F2/F3 class on the unsplit carrier",
            "logical_relation": "the two classes are independent: beta_1 blocks branch projection before ell3 can be assigned to branches, while the ell3 witness concerns removal of the unsplit ternary operation",
            "branch_label_status": "NO_CERTIFIED_MAP",
            "mode_pair_source_table_status": "NO_CERTIFIED_MAP",
        },
        "dependency_refs": dependency_refs,
        "source_manifest": source_manifest,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_filtered_cyclic_branch_extension_obstruction.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_filtered_cyclic_branch_extension_obstruction.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_filtered_cyclic_branch_extension_obstruction -v",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-filtered-cyclic-branch-extension-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json",
        ],
        "claim_flags": {
            "PRINCIPAL_BRANCH_EXACT_SEQUENCE_DEFINED": True,
            "ADMISSIBLE_FILTERED_CYCLIC_CATEGORY_DEFINED": True,
            "FIRST_EXTENSION_OBSTRUCTION_CLASS_CERTIFIED": True,
            "ARITY_ONE_BRANCH_SPLIT_EXISTS": False,
            "CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS": False,
            "RANK46_CONTRACTIBLE_GRAPH_REPAIRS_OBSTRUCTION": False,
            "STANDARD_FIBRE_MINIMAL_PAGE_REPAIR_CLASSIFIED": True,
            "GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED": False,
            "ELL3_BRANCH_PROJECTION_AUTHORIZED": False,
            "MODE_PAIR_SOURCE_TABLE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_NONCONTRACTIBLE_OR_MIXED_BUNDLE_REALIZATION_OF_THE_MINIMAL_OBSTRUCTION_MODULE",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC theorem defines the principal Einstein-image/"
            "additional-Weyl extension, the admissible filtered cyclic category, and the "
            "first invariant lifting class beta_1. The exact standard-fibre witness "
            "beta_1=(1,0) rules out an arity-one branch projector and therefore every "
            "cyclic L_infinity branch split with the certified principal anchor on the "
            "retained 36-row carrier and its rank-46 contractible STF2 graph prolongation. "
            "It completely classifies finite page-level repairs: a repair must add a "
            "noncontractible boundary image covering im(beta_1), with one field direction "
            "and its cyclic dual minimally sufficient at the standard fibre. It does not "
            "construct the global K_Berger-equivariant bundle closure, solve higher filtered "
            "pages, identify retained rows with Einstein or extra-Weyl modes, project ell3, "
            "compute a mode-pair source table, establish causal propagation of an enlarged "
            "carrier, or make observational, quantum, ghost, scattering, or all-orders claims."
        ),
    }


def validate(value: Mapping[str, object], *, verify_sources: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if (
        flags["FIRST_EXTENSION_OBSTRUCTION_CLASS_CERTIFIED"] is not True
        or flags["STANDARD_FIBRE_MINIMAL_PAGE_REPAIR_CLASSIFIED"] is not True
        or any(
            flags[name] is not False
            for name in (
                "ARITY_ONE_BRANCH_SPLIT_EXISTS",
                "CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS",
                "RANK46_CONTRACTIBLE_GRAPH_REPAIRS_OBSTRUCTION",
                "GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED",
                "ELL3_BRANCH_PROJECTION_AUTHORIZED",
                "MODE_PAIR_SOURCE_TABLE_AUTHORIZED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("branch-extension claim boundary drifted")
    fixture = value["minimal_page_enlargement_classification"]["standard_fibre"]
    if (
        fixture["obstruction_image_rank"] != 1
        or fixture["minimum_new_field_directions"] != 1
        or fixture["minimum_cyclic_BV_rows"] != 2
        or fixture["extended_boundary_rank"] != fixture["extended_augmented_rank"]
    ):
        raise ValueError("minimal page-enlargement classification drifted")
    if value["first_obstruction_class"]["normalized_evaluation"] != [["1", "0"]]:
        raise ValueError("normalized extension obstruction drifted")
    if verify_sources:
        for record in value["dependency_refs"].values():
            if _sha256(ROOT / record["path"]) != record["sha256"]:
                raise ValueError(f"dependency digest drifted: {record['artifact_id']}")
        for relative, digest in value["source_manifest"].items():
            if _sha256(ROOT / relative) != digest:
                raise ValueError(f"source digest drifted: {relative}")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Filtered cyclic Einstein--Weyl branch-extension obstruction

## The extension category

On the certified physical principal module, let

\[
A=\mathbb Q(\sqrt{10})[\epsilon]/(\epsilon^2),\qquad
0\longrightarrow H_{\rm hel}\otimes\epsilon A
\longrightarrow H_{\rm hel}\otimes A
\longrightarrow H_{\rm hel}\otimes A/\epsilon A
\longrightarrow0.
\]

The three terms are the principal Einstein layer, repeated-wave Weyl layer,
and additional-Weyl quotient.  An admissible split must lift this sequence to
finite-order support-local filtered chain maps on the retained cyclic BV
complex, preserve the typed pairing and the retained `K_Berger` action, and
use no Green, inverse-Laplacian, helicity-mode, or row-name projector.

## First invariant obstruction

At the first nonzero filtered page the lifting equation is

\[
M X=T,\qquad
M=[\sigma_4(H),J_{\rm phys},\sigma_2(V_2)\sigma_1(K)],\qquad
T=\sigma_2(V_2)I_{\rm phys}.
\]

It already quotients every principal Hessian boundary, physical-equation
representative, and spatial-gauge change of the field representatives.  The
invariant class is

\[
\beta_1=\pi_{\operatorname{coker}M}T.
\]

The certified ranks are `rank(M)=4`, `rank(M,T_plus)=5`, and
`rank(M,T_cross)=4`.  The normalized exact covector annihilates `M` and
evaluates on the two physical columns as `(1,0)`.  Thus the cross
polarization lifts, with coefficient `71/40`, but the complete rank-two
physical module does not.

Any cyclic `L_infinity` branch split has a unary filtered cyclic chain split.
Its restriction to this fibre would force `beta_1=0`.  Therefore no such
split exists on the retained 36-row carrier.  The rank-46 STF2 graph
prolongation cannot change the verdict: it is a cyclic contractible SDR with
Schur complement `A10`, so it induces the same obstruction quotient.

## Complete minimal page repair

For any finite first-page problem let `o:H->Q=coker(M)`.  An enlargement by a
field correction space `Z` contributes a map `j:Z->Q`; cyclicity adds the dual
equation space `Z^vee`.  The enlarged page lifts if and only if

\[
\operatorname{im}o\subseteq\operatorname{im}j.
\]

Consequently the minimum is `dim Z=rank(o)`, and every minimal repair is,
up to filtered cyclic isomorphism and contractible hyperbolic summands, the
hyperbolic completion of `im(o)`.  Contractible SDR enlargements have no new
image in `Q` and cannot repair a nonzero class.

Here `rank(o)=1` at the standard fibre.  Exactly one noncontractible field
direction and its cyclic dual -- two BV rows -- are necessary and sufficient
at this page.  A global support-local repair must instead close the
obstruction image under the residual action and solve the later filtered
pages.  That bundle and its rank are not certified.

## Relation to the retained mixed ell3

This unary extension class and the landed ternary deformation class are
different.  `beta_1` prevents an admissible branch projection from existing;
the separate 22-row witness prevents removal of the mixed retained `ell3`
within the declared filtered cyclic `F2/F3` class on the unsplit carrier.
Neither result authorizes assigning `ell3` coefficients to Einstein-like or
additional-Weyl modes.

CLOSE-OUT: OBSTRUCTED — the first invariant unary extension class is nonzero, and the minimal page-level noncontractible repair is classified
EVIDENCE: d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json
"""


def _guards(value: dict) -> None:
    mutations = [
        ("accept unary split", "ARITY_ONE_BRANCH_SPLIT_EXISTS", True),
        ("accept nonlinear split", "CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS", True),
        (
            "promote contractible repair",
            "RANK46_CONTRACTIBLE_GRAPH_REPAIRS_OBSTRUCTION",
            True,
        ),
        ("authorize ell3 projection", "ELL3_BRANCH_PROJECTION_AUTHORIZED", True),
        ("promote global construction", "GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED", True),
    ]
    for name, flag, replacement in mutations:
        mutant = deepcopy(value)
        mutant["claim_flags"][flag] = replacement
        try:
            validate(mutant, verify_sources=False)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")
    mutant = deepcopy(value)
    mutant["minimal_page_enlargement_classification"]["standard_fibre"][
        "minimum_cyclic_BV_rows"
    ] = 0
    try:
        validate(mutant, verify_sources=False)
    except Exception:
        return
    raise AssertionError("mutation guard accepted: zero-row repair")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    validate(value)
    if args.check:
        if OUTPUT.read_text() != _render(value):
            raise AssertionError("branch-extension certificate drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("branch-extension report drifted")
    if args.guards:
        _guards(value)
    print("BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
