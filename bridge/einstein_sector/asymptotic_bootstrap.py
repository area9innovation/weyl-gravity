"""Fail-closed bootstrap for the asymptotically flat Einstein sector.

The exact result proved here is deliberately smaller than the commissioned
null-infinity theorem: for each nonzero spatial Fourier mode in linearized
TT pure-Weyl gravity on Minkowski space, the Einstein two-jet constraint is
an invariant subspace of the fourth-order Bach evolution.  Boundary
function spaces, surface charges, nonlinear closure, and scattering remain
open and are recorded as such.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "bridge" / "certificates" / "asymptotically_flat_einstein_bootstrap.json"
)
SCHEMA_PATH = (
    ROOT / "bridge" / "einstein_sector" / "schema" / "asymptotic_bootstrap.schema.json"
)

INPUTS = {
    "flat_einstein_symplectic_restriction": ROOT
    / "bridge"
    / "certificates"
    / "flat_einstein_symplectic_restriction.json",
    "einstein_defect_asymptotics": ROOT
    / "bridge"
    / "certificates"
    / "einstein_defect_asymptotics.json",
    "bondi_bach_indicial": ROOT
    / "bridge"
    / "certificates"
    / "bondi_bach_indicial.json",
    "flat_tt_bach": ROOT
    / "bridge"
    / "certificates"
    / "flat_tt_bach_operator.json",
    "einstein_sector": ROOT
    / "bridge"
    / "certificates"
    / "einstein_sector_theorem.json",
    "closed_universe_bfv": ROOT
    / "bridge"
    / "certificates"
    / "closed_universe_bfv.json",
    "cylinder_causal_transport": ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_causal_transport_recognition.json",
    "cylinder_tt_factorization": ROOT
    / "covariant_completion"
    / "certificates"
    / "tt_local_factorization.json",
}


class AsymptoticBootstrapError(RuntimeError):
    """Raised when the bootstrap or an imported scope guard fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AsymptoticBootstrapError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "pure-weyl-asymptotically-flat-einstein-bootstrap-v2",
        "wrong asymptotic bootstrap schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"bootstrap certificate is missing required field {key}")
    _require(
        payload.get("schema") == schema.get("$id"),
        "bootstrap payload/schema identifier mismatch",
    )
    _require(
        payload.get("schema_path")
        == "bridge/einstein_sector/schema/asymptotic_bootstrap.schema.json",
        "bootstrap schema path mismatch",
    )
    _require(
        payload.get("schema_sha256") == _sha256(SCHEMA_PATH),
        "bootstrap schema hash mismatch",
    )
    provenance = payload.get("provenance", {})
    _require(
        provenance.get("generator_path")
        == "bridge/einstein_sector/asymptotic_bootstrap.py",
        "bootstrap generator path mismatch",
    )
    _require(
        provenance.get("generator_sha256") == _sha256(Path(__file__)),
        "bootstrap generator hash mismatch",
    )
    allowed_tags = {"LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"}
    _require(
        set(payload.get("dependency_tags", [])) <= allowed_tags,
        "bootstrap contains an unknown dependency tag",
    )
    obligations = payload.get("obligation_status", [])
    _require(
        [row.get("id") for row in obligations] == [f"AF-E{index}" for index in range(1, 9)],
        "bootstrap obligation inventory is incomplete or reordered",
    )
    _require(
        all(
            row.get("status") in {"OPEN", "PARTIAL"}
            and row.get("required_closure_tag") == "LORENTZIAN-CAUSAL"
            and row.get("partial_receipt_tag") in allowed_tags | {None}
            and (
                (row.get("status") == "PARTIAL" and row.get("partial_receipt_tag") is not None)
                or (row.get("status") == "OPEN" and row.get("partial_receipt_tag") is None)
            )
            for row in obligations
        ),
        "bootstrap obligation status or closure tag is invalid",
    )
    flags = payload.get("claim_flags", {})
    _require(flags.get("flat_tt_bach_operator_derived") is True, "flat TT premise is not closed")
    _require(
        flags.get("linearized_minkowski_einstein_data_invariant") is True,
        "linearized Einstein invariant-subspace theorem is absent",
    )
    _require(
        flags.get("bondi_bach_radiative_indicial_roots_classified") is True,
        "Bondi/Bach radiative indicial roots are absent",
    )
    _require(
        flags.get("p0_boundary_metric_branch_identified") is True,
        "leading p=0 boundary-metric branch is absent",
    )
    _require(
        flags.get("p1_same_falloff_bach_obstruction_identified") is True,
        "same-falloff p=1 Bach obstruction is absent",
    )
    _require(
        flags.get("fixed_boundary_metric_excludes_leading_p0_kinematically") is True,
        "kinematic p=0 boundary-selection result is absent",
    )
    _require(
        flags.get("einstein_defect_factorization_derived") is True,
        "Einstein-defect factorization is absent",
    )
    _require(
        flags.get("kappa_zero_insufficient_for_einstein") is True,
        "kappa insufficiency result is absent",
    )
    _require(
        flags.get("flat_reduced_einstein_pairing_zero") is True,
        "flat Einstein pairing restriction is absent",
    )
    _require(
        flags.get("nonzero_eh_symplectic_embedding_refuted_on_schwartz_core")
        is True,
        "flat reduced symplectic no-go is absent",
    )
    full_claims = {
        "full_asymptotically_flat_function_space_admissible",
        "null_infinity_green_complex_constructed",
        "pure_weyl_surface_charges_computed",
        "non_einstein_branch_causally_excluded",
        "nonlinear_einstein_constraint_preserved",
        "radiative_symplectic_form_matched",
        "helicity_two_scattering_space_recovered",
        "extra_weyl_channels_classified",
    }
    _require(
        all(flags.get(name) is False for name in full_claims),
        "a full asymptotic claim was promoted without its Lorentzian certificate",
    )


def _matrix_rows(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(entry)) for entry in matrix.row(row)] for row in range(matrix.rows)]


def _verify_scope_inputs(records: dict[str, dict[str, Any]]) -> None:
    restriction = records["flat_einstein_symplectic_restriction"]
    _require(
        restriction.get("schema")
        == "pure-weyl-flat-einstein-symplectic-restriction-v1",
        "flat symplectic-restriction schema changed",
    )
    _require(
        restriction.get("verdict")
        == "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        "flat symplectic-restriction verdict is absent",
    )
    _require(
        restriction.get("claim_flags", {}).get(
            "nonzero_symplectic_proportionality_refuted"
        )
        is True,
        "flat symplectic rank mismatch is absent",
    )
    _require(
        restriction.get("claim_flags", {}).get("full_einstein_scattering_no_go_proved")
        is False,
        "reduced symplectic no-go was promoted to a full scattering no-go",
    )

    defect = records["einstein_defect_asymptotics"]
    _require(
        defect.get("schema") == "pure-weyl-einstein-defect-asymptotics-v1",
        "Einstein-defect asymptotics schema changed",
    )
    _require(
        defect.get("geometric_definition", {}).get("einstein_equation") == "chi=0",
        "Einstein-defect zero condition changed",
    )
    _require(
        defect.get("defect_wave_recurrence", {})
        .get("factorization_check", {})
        .get("status")
        == "PASS",
        "Einstein-defect factorization is not certified",
    )
    _require(
        defect.get("claim_flags", {}).get("kappa_zero_sufficient_for_einstein")
        is False,
        "upstream defect theorem overpromotes kappa=0",
    )
    _require(
        defect.get("claim_flags", {}).get("causal_zero_defect_theorem_proved")
        is False,
        "upstream defect theorem claims unproved causal uniqueness",
    )

    indicial = records["bondi_bach_indicial"]
    _require(
        indicial.get("schema") == "pure-weyl-bondi-bach-indicial-v2",
        "Bondi/Bach indicial schema changed",
    )
    _require(
        indicial.get("radiative_indicial_roots") == ["0", "1"],
        "Bondi/Bach radiative indicial roots changed",
    )
    _require(
        indicial.get("p0_extra_bach_falloff", {}).get("boundary_metric_changed")
        is True,
        "p=0 branch no longer changes the unphysical boundary metric",
    )
    _require(
        indicial.get("kinematic_boundary_selection", {}).get("status")
        == "KINEMATIC_LEADING_BRANCH_ONLY",
        "p=0 boundary selection was promoted beyond its certificate",
    )
    _require(
        indicial.get("p1_einstein_compatible_falloff", {}).get(
            "einstein_subconstraint"
        )
        == "kappa=0",
        "p=1 Einstein subconstraint changed",
    )
    _require(
        indicial.get("claim_flags", {}).get("p1_non_einstein_obstruction_identified")
        is True,
        "p=1 same-falloff Bach obstruction is not certified",
    )
    _require(
        indicial.get("claim_flags", {}).get(
            "fixed_boundary_metric_isolates_full_einstein_sector"
        )
        is False,
        "upstream certificate incorrectly isolates the full Einstein sector",
    )
    _require(
        indicial.get("claim_flags", {}).get(
            "boundary_condition_preserved_by_causal_green_operators"
        )
        is False,
        "upstream indicial certificate claims unproved causal preservation",
    )

    flat = records["flat_tt_bach"]
    _require(
        flat.get("operator_identity") == "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "flat TT Bach operator has not been derived with the expected normalization",
    )
    _require(
        flat.get("helicity_commutator_zero") is True,
        "flat TT Bach operator does not preserve both helicities",
    )

    theorem = records["einstein_sector"]
    commission = theorem.get("next_theorem_commission", {})
    _require(
        commission.get("status") == "OPEN_FAIL_CLOSED",
        "Einstein scattering commission is not open and fail-closed",
    )
    _require(
        theorem.get("claim_flags", {}).get(
            "einstein_sector_causally_closed_at_null_infinity"
        )
        is False,
        "upstream theorem already claims null-infinity closure",
    )

    closed = records["closed_universe_bfv"]
    _require(closed.get("boundary_components") == [], "closed-cylinder boundary changed")
    _require(
        closed.get("surface_charge_rank") == 0,
        "closed-cylinder input unexpectedly has surface charges",
    )
    _require(
        closed.get("alternative", {}).get("compact_time_is_charge") is True,
        "closed-cylinder input no longer recognizes a charged-time alternative",
    )

    causal = records["cylinder_causal_transport"]
    cylinder = causal.get("cylinder_specialization", {})
    _require(
        cylinder.get("cauchy_surface_compact") is True
        and cylinder.get("Gamma_sc_equals_Gamma_smooth") is True,
        "cylinder causal specialization changed",
    )

    tt = records["cylinder_tt_factorization"]
    _require(
        tt.get("constraint_subspace") == "TT, preserved by C_2 and both factors",
        "upstream TT factorization no longer preserves its constraint space",
    )
    _require(
        tt.get("scope_guard")
        == "this is the reduced physical TT operator, not a Green's witness for the complete BV complex",
        "upstream TT scope guard changed",
    )


def _linearized_tt_identity() -> dict[str, Any]:
    q = sp.symbols("q", real=True)

    # State x=(h, h_dot, h_ddot, h_dddot) for
    # (d_t^2+q)^2 h=0, one TT polarization at fixed |k|^2=q.
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [-q**2, 0, -2 * q, 0],
        ]
    )
    einstein_constraint = sp.Matrix([[q, 0, 1, 0], [0, q, 0, 1]])
    constraint_evolution = sp.Matrix([[0, 1], [-q, 0]])
    defect = sp.simplify(
        einstein_constraint * evolution
        - constraint_evolution * einstein_constraint
    )
    _require(defect == sp.zeros(2, 4), "Einstein constraint is not evolution-invariant")
    _require(einstein_constraint.rank() == 2, "Einstein constraint rank changed")

    kernel_basis = sp.Matrix(
        [
            [1, 0],
            [0, 1],
            [-q, 0],
            [0, -q],
        ]
    )
    _require(
        einstein_constraint * kernel_basis == sp.zeros(2, 2),
        "displayed Einstein data do not lie in the constraint kernel",
    )
    induced = sp.Matrix([[0, 1], [-q, 0]])
    _require(
        evolution * kernel_basis == kernel_basis * induced,
        "Bach evolution does not restrict to Einstein wave evolution",
    )
    _require(
        defect.subs(q, 0) == sp.zeros(2, 4),
        "polynomial intertwining identity fails at the homogeneous q=0 value",
    )

    return {
        "background": "four-dimensional Minkowski space",
        "sector": "one transverse-traceless polarization at fixed spatial q=|k|^2>0",
        "bach_equation": "(d_t^2+q)^2 h=0",
        "bach_operator_provenance": "flat_tt_bach_operator.json",
        "einstein_equation": "(d_t^2+q) h=0",
        "state_order": ["h", "d_t h", "d_t^2 h", "d_t^3 h"],
        "bach_evolution_matrix": _matrix_rows(evolution),
        "einstein_constraint_order": ["(d_t^2+q)h", "d_t(d_t^2+q)h"],
        "einstein_constraint_matrix": _matrix_rows(einstein_constraint),
        "constraint_evolution_matrix": _matrix_rows(constraint_evolution),
        "intertwining_identity": "C_E A_B = A_E C_E",
        "intertwining_defect": _matrix_rows(defect),
        "einstein_kernel_basis": _matrix_rows(kernel_basis),
        "restricted_evolution_identity": "A_B i_E = i_E A_E",
        "bach_data_dimension_per_helicity": 4,
        "einstein_data_dimension_per_helicity": 2,
        "result": (
            "the linearized Einstein initial-data kernel is exactly invariant under "
            "fixed-mode Bach evolution"
        ),
        "algebraic_q_zero_extension": (
            "the polynomial intertwining identity also holds at q=0, but a spatially "
            "homogeneous TT plane wave is not an admissible asymptotically flat mode"
        ),
        "scope_guards": [
            "the homogeneous q=0 Fourier value is not identified with soft or Coulombic data",
            "soft limits, memory zero modes, and Coulombic sectors are not classified",
            "no statement about radial falloff or null-infinity flux",
            "no nonlinear constraint-preservation theorem",
            "modewise evolution invariance is not a support theorem for Green operators",
        ],
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _verify_scope_inputs(records)
    linearized = _linearized_tt_identity()

    obligations = [
        ("AF-E1", "PARTIAL", "linearized TT, p=0,1, and Einstein-defect radial recursions fixed; full tensor weighted spaces open", "REDUCED-MODE"),
        ("AF-E2", "OPEN", "no retarded/advanced null-infinity complex", None),
        ("AF-E3", "PARTIAL", "charge criterion fixed; pure-Weyl charges not computed", "LOCAL-ALGEBRAIC"),
        ("AF-E4", "PARTIAL", "Einstein is chi=0; fixed boundary metric and kappa=0 are each insufficient, and causal zero-defect preservation is open", "REDUCED-MODE"),
        ("AF-E5", "PARTIAL", "linearized fixed-mode closure proved; nonlinear closure open", "REDUCED-MODE"),
        ("AF-E6", "PARTIAL", "flat Schwartz TT restriction of the pure-Weyl current is zero while the Einstein-Hilbert pairing is nonzero; null-infinity current/flux comparison remains open", "LORENTZIAN-CAUSAL"),
        ("AF-E7", "PARTIAL", "conventional nondegenerate Einstein symplectic embedding is refuted on the flat Schwartz TT core; full asymptotic scattering cohomology remains open", "LORENTZIAN-CAUSAL"),
        ("AF-E8", "PARTIAL", "p=0 defect plus p=1 kappa and rho tower identified; tensor, soft, Coulombic, and corner data open", "REDUCED-MODE"),
    ]

    certificate = {
        "schema": "pure-weyl-asymptotically-flat-einstein-bootstrap-v2",
        "schema_path": "bridge/einstein_sector/schema/asymptotic_bootstrap.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "ASYMPTOTICALLY_FLAT_EINSTEIN_SECTOR_BOOTSTRAP",
        "result_state": "PARTIAL_WITH_REDUCED_FLAT_SYMPLECTIC_NO_GO",
        "provenance": {
            "input_base_commit": "ed5ada08f4dbe0dca929fc49957770b4a8a99fd0",
            "generator_path": "bridge/einstein_sector/asymptotic_bootstrap.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "required_promotion_tag": "LORENTZIAN-CAUSAL",
        "linearized_minkowski_theorem": linearized,
        "flat_symplectic_restriction": {
            "verdict": records["flat_einstein_symplectic_restriction"]["verdict"],
            "action_current_derivation": records["flat_einstein_symplectic_restriction"]
            ["action_current_derivation"],
            "cauchy_matrix_test": records["flat_einstein_symplectic_restriction"]
            ["cauchy_matrix_test"],
            "boundary_improvement_test": records[
                "flat_einstein_symplectic_restriction"
            ]["boundary_improvement_test"],
            "time_translation_test": records["flat_einstein_symplectic_restriction"]
            ["time_translation_test"],
            "scope_guards": records["flat_einstein_symplectic_restriction"]
            ["scope_guards"],
        },
        "einstein_defect_theorem": {
            "definition": records["einstein_defect_asymptotics"][
                "geometric_definition"
            ],
            "radial_map": records["einstein_defect_asymptotics"][
                "radial_defect_map"
            ],
            "p0_defect": records["einstein_defect_asymptotics"]["p0_defect"],
            "p1_defect_tower": records["einstein_defect_asymptotics"][
                "p1_defect_tower"
            ],
            "boundary_consequence": records["einstein_defect_asymptotics"][
                "boundary_selection_consequence"
            ],
            "scope_guards": records["einstein_defect_asymptotics"][
                "scope_guards"
            ],
        },
        "bondi_bach_indicial_theorem": {
            "sector": "scalar amplitude of each flat Cartesian TT polarization",
            "retarded_series": "phi=sum_(n>=0) r^(-p-n) f_n(u) Y_L(x)",
            "radiative_indicial_polynomial": records["bondi_bach_indicial"][
                "radiative_indicial_polynomial"
            ],
            "radiative_indicial_roots": records["bondi_bach_indicial"][
                "radiative_indicial_roots"
            ],
            "einstein_compatible_falloff": records["bondi_bach_indicial"][
                "p1_einstein_compatible_falloff"
            ],
            "extra_bach_branch": records["bondi_bach_indicial"][
                "p0_extra_bach_falloff"
            ],
            "boundary_selection": records["bondi_bach_indicial"][
                "kinematic_boundary_selection"
            ],
            "scope_guards": records["bondi_bach_indicial"]["scope_guards"],
        },
        "asymptotic_data_seed": {
            "status": "SPECIFIED_NOT_ADMISSIBILITY_PROVED",
            "conformal_completion": {
                "objects": ["M_tilde", "g_tilde", "Omega"],
                "relations": [
                    "g_tilde=Omega^2 g on the physical interior",
                    "Omega=0 and dOmega nonzero at I_plus and I_minus",
                    "I_plus and I_minus each have topology R x S^2",
                ],
                "regularity_choice": "smooth conformal completion at null infinity",
            },
            "bondi_seed_fields": [
                "unit-sphere metric q_AB",
                "trace-free shear C_AB(u,x)",
                "news N_AB=d_u C_AB",
                "Bondi mass aspect m(u,x)",
                "angular-momentum aspect N_A(u,x)",
            ],
            "radiative_class_rails": {
                "finite_flux_completion": {
                    "news": "N_AB in L^2_u H^s(S^2), s>3 declared but not sharp",
                    "endpoint_shear_required": False,
                    "status": "CANDIDATE",
                },
                "strong_scattering_core": {
                    "news": "N_AB in L^1_u H^s(S^2) intersect L^2_u H^s(S^2)",
                    "shear": "C_AB has finite H^s endpoint limits",
                    "memory": "Delta C_AB=C_AB(+infinity)-C_AB(-infinity) is allowed",
                    "status": "CANDIDATE_DENSE_CORE_NOT_PROVED",
                },
                "soft_memory_extension": {
                    "purpose": "complete the finite-flux/core spaces by soft and memory data",
                    "topology": "OPEN",
                    "distributional_endpoints": "NOT_CLASSIFIED",
                    "status": "OPEN",
                },
            },
            "sector_distinctions": {
                "homogeneous_fourier_zero": (
                    "q=0 in the fixed-mode oscillator identity; algebraically invariant "
                    "but normally excluded by asymptotically flat spatial falloff"
                ),
                "soft_sector": (
                    "zero-frequency limit of radiative data, including memory/large-gauge "
                    "structure; not a single homogeneous Fourier mode"
                ),
                "coulombic_sector": (
                    "non-radiative mass and angular-momentum aspects constrained along "
                    "null infinity; not part of the TT oscillator q=0 substitution"
                ),
            },
            "missing_bach_data": [
                "falloffs and regularity for the second fourth-order radiative pair",
                "soft/memory and Coulombic boundary sectors",
                "corner matching through spatial infinity",
                "closure of the Bach operator on weighted/polyhomogeneous spaces",
                "constraint-compatible gauge and ghost falloffs",
            ],
        },
        "gauge_charge_rule": {
            "status": "CRITERION_FIXED_ASSIGNMENTS_OPEN",
            "proper_gauge_core": "Diff x Weyl parameters vanishing near null infinity",
            "boundary_preserving_parameter": (
                "proper gauge only when its renormalized surface-charge variation "
                "vanishes on every tangent direction and its reference charge is zero"
            ),
            "charged_parameter": "asymptotic symmetry, not quotiented as gauge",
            "consequence": "time translations and BMS-type generators cannot be gauged by name alone",
            "missing": [
                "pure-Weyl presymplectic potential and boundary counterterm choice",
                "finite integrable surface-charge formula",
                "flux/balance law and charge algebra",
                "generator-by-generator proper/charged classification",
            ],
        },
        "conformal_freedom_split": {
            "physical_weyl_gauge": {
                "action": "g -> exp(2 sigma) g on the physical metric",
                "boundary_question": "which sigma preserve the phase space and have zero renormalized charge",
            },
            "compactification_frame": {
                "action": "(g_tilde,Omega) -> (omega^2 g_tilde, omega Omega)",
                "role": "redundancy of the unphysical conformal completion",
            },
            "non_identification_rule": (
                "physical Weyl gauge and compactification-frame rescaling are distinct "
                "until an explicit boundary map identifies a common zero-charge action"
            ),
            "status": "DISTINCTION_FIXED_BOUNDARY_INTERSECTION_OPEN",
        },
        "cylinder_non_reuse": {
            "established": True,
            "reasons": [
                "the cylinder proof uses compact S^3 to identify all smooth sections with spacelike-compact sections",
                "the selected closed-universe BFV problem has no boundary and surface-charge rank zero",
                "null infinity has boundary flux and may retain time/BMS transformations as charged symmetries",
            ],
        },
        "obligation_status": [
            {
                "id": identifier,
                "status": status,
                "receipt": receipt,
                "partial_receipt_tag": partial_tag,
                "required_closure_tag": "LORENTZIAN-CAUSAL",
            }
            for identifier, status, receipt, partial_tag in obligations
        ],
        "claim_flags": {
            "flat_tt_bach_operator_derived": True,
            "linearized_minkowski_einstein_data_invariant": True,
            "bondi_bach_radiative_indicial_roots_classified": True,
            "p0_boundary_metric_branch_identified": True,
            "p1_same_falloff_bach_obstruction_identified": True,
            "fixed_boundary_metric_excludes_leading_p0_kinematically": True,
            "einstein_defect_factorization_derived": True,
            "kappa_zero_insufficient_for_einstein": True,
            "flat_reduced_einstein_pairing_zero": True,
            "nonzero_eh_symplectic_embedding_refuted_on_schwartz_core": True,
            "full_asymptotically_flat_function_space_admissible": False,
            "null_infinity_green_complex_constructed": False,
            "pure_weyl_surface_charges_computed": False,
            "non_einstein_branch_causally_excluded": False,
            "nonlinear_einstein_constraint_preserved": False,
            "radiative_symplectic_form_matched": False,
            "helicity_two_scattering_space_recovered": False,
            "extra_weyl_channels_classified": False,
        },
        "claim_dependency_tags": {
            "flat_tt_bach_operator_derived": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "linearized_minkowski_einstein_data_invariant": ["REDUCED-MODE"],
            "bondi_bach_radiative_indicial_roots_classified": ["REDUCED-MODE"],
            "p0_boundary_metric_branch_identified": ["REDUCED-MODE"],
            "p1_same_falloff_bach_obstruction_identified": ["REDUCED-MODE"],
            "fixed_boundary_metric_excludes_leading_p0_kinematically": ["REDUCED-MODE"],
            "einstein_defect_factorization_derived": ["REDUCED-MODE"],
            "kappa_zero_insufficient_for_einstein": ["REDUCED-MODE"],
            "flat_reduced_einstein_pairing_zero": [
                "REDUCED-MODE",
                "LORENTZIAN-CAUSAL",
            ],
            "nonzero_eh_symplectic_embedding_refuted_on_schwartz_core": [
                "REDUCED-MODE",
                "LORENTZIAN-CAUSAL",
            ],
            "all_false_asymptotic_claims_require": ["LORENTZIAN-CAUSAL"],
        },
        "sources": [
            {
                "role": "null-infinity radiative phase-space control",
                "citation": "Ashtekar and Streubel, Proc. Roy. Soc. A 376 (1981) 585",
                "url": "https://doi.org/10.1098/rspa.1981.0109",
            },
            {
                "role": "charge-versus-gauge criterion with radiative flux",
                "citation": "Wald and Zoupas, Phys. Rev. D 61 (2000) 084027",
                "url": "https://arxiv.org/abs/gr-qc/9911095",
            },
            {
                "role": "four-dimensional conformal-gravity canonical charge control",
                "citation": "Lovrekovic, arXiv:1505.05820",
                "url": "https://arxiv.org/abs/1505.05820",
                "scope_guard": "generalized Fefferman-Graham boundaries, not an asymptotically flat theorem",
            },
            {
                "role": "linearized Minkowski boundary-condition control",
                "citation": "Hell, Lust, and Zoupanos, arXiv:2306.13714",
                "url": "https://arxiv.org/abs/2306.13714",
                "scope_guard": (
                    "temporal perturbative boundary analysis, not a null-infinity "
                    "Bondi or Lorentzian-causal theorem"
                ),
            },
        ],
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "verification_command": (
            "python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify "
            "bridge/certificates/asymptotically_flat_einstein_bootstrap.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    actual = _load(path)
    expected = build_certificate()
    _require(actual == expected, f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
