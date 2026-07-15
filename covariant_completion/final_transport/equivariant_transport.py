"""Conditional recognition of the full conformal causal transport.

The Cauchy splitting is not strictly invariant under the proper conformal
generators.  Strict invariance is also unnecessary.  If ``rho`` is any
local conformal chain symmetry and ``chi`` is a temporal cutoff, the
standard inverse to the causal map is represented by

    kappa = [Q, chi].

The Jacobi identity and ``[Q,rho]=0`` give the explicit chain homotopy

    [kappa,rho] = [Q,[chi,rho]].

For spacelike-compact sections on ``R x S3``, ``[chi,rho]`` has compact
support because it is supported in the cutoff time slab and ``S3`` is
compact.  Thus the cutoff inverse, and hence its causal cohomology inverse,
is SO(4,2)-equivariant.  This module composes that identity with the already
certified natural auxiliary/prolongation retracts, the global flat-BGG
theorem, and the all-level E/A/L curvature realization.

No Green operator is constructed here.  The theorem is deliberately
conditional on the actual causal quasi-isomorphism.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


SCHEMA = "pure-weyl-so42-causal-transport-recognition-v1"


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {name}")
    return value


def _normal_word(word: tuple[str, ...]) -> tuple[str, ...]:
    """Use [Q,rho]=0 to put Q before rho in a formal operator word."""

    result = list(word)
    changed = True
    while changed:
        changed = False
        for index in range(len(result) - 1):
            if result[index : index + 2] == ["rho", "Q"]:
                result[index : index + 2] = ["Q", "rho"]
                changed = True
    return tuple(result)


def _collect(terms: list[tuple[int, tuple[str, ...]]]) -> dict[tuple[str, ...], int]:
    result: dict[tuple[str, ...], int] = {}
    for coefficient, word in terms:
        key = _normal_word(word)
        result[key] = result.get(key, 0) + coefficient
    return {key: value for key, value in result.items() if value}


def cutoff_equivariance_defect() -> dict[tuple[str, ...], int]:
    """Return ``[[Q,chi],rho]-[Q,[chi,rho]]`` in exact normal form."""

    return _collect(
        [
            # [[Q,chi],rho]
            (+1, ("Q", "chi", "rho")),
            (-1, ("chi", "Q", "rho")),
            (-1, ("rho", "Q", "chi")),
            (+1, ("rho", "chi", "Q")),
            # -[Q,[chi,rho]]
            (-1, ("Q", "chi", "rho")),
            (+1, ("Q", "rho", "chi")),
            (+1, ("chi", "rho", "Q")),
            (-1, ("rho", "chi", "Q")),
        ]
    )


def recognition_certificate_passes(certificate: Mapping[str, object]) -> bool:
    if certificate.get("schema") != SCHEMA:
        return False
    try:
        theorem = _mapping(certificate.get("conditional_theorem"), "conditional_theorem")
        cutoff = _mapping(certificate.get("cutoff_homotopy"), "cutoff_homotopy")
        local = _mapping(certificate.get("local_naturality"), "local_naturality")
        module = _mapping(certificate.get("global_module_identification"), "global_module_identification")
        residual = _mapping(certificate.get("residual_action"), "residual_action")
        boundary = _mapping(certificate.get("promotion_boundary"), "promotion_boundary")
    except AssertionError:
        return False
    return bool(
        theorem.get("recognition_exact")
        and theorem.get("requires_causal_quasi_isomorphism")
        and cutoff.get("formal_defect") == 0
        and cutoff.get("identity") == "[kappa,rho]=[Q,[chi,rho]]"
        and cutoff.get("homotopy") == "[chi,rho]"
        and cutoff.get("homotopy_support_compact")
        and cutoff.get("all_fifteen_generators")
        and local.get("auxiliary_shift_natural")
        and local.get("auxiliary_retract_support_local")
        and local.get("curvature_map_natural")
        and local.get("curvature_mapping_cylinder_support_local")
        and local.get("first_order_state_action_inherited_from_covariant_rows")
        and local.get("contractible_rows_add_no_action")
        and module.get("smooth_global_BGG_equivariant")
        and module.get("curvature_quotient_is_W_plus_W_minus")
        and module.get("all_level_EAL_exhaustion")
        and module.get("both_chiralities")
        and residual.get("raw_generators_are_chain_maps")
        and residual.get("raw_SDR_homotopy_equivariant")
        and residual.get("strict_so42_action_on_cohomology")
        and residual.get("proper_conformal_brackets_exact")
        and boundary.get("does_not_construct_causal_green_homotopy")
        and boundary.get("does_not_claim_strict_Cauchy_split")
        and boundary.get("does_not_claim_pairing_transport")
        and boundary.get("SO42_equivariant_transport_conditional")
    )


@dataclass(frozen=True)
class SO42CausalTransportRecognition:
    causal_transport: Mapping[str, object]
    auxiliary_retract: Mapping[str, object]
    curvature_mapping_cylinder: Mapping[str, object]
    curvature_causal_pde: Mapping[str, object]
    raw_bv_transfer: Mapping[str, object]
    bgg_blocks: Mapping[str, object]
    metric_preimages: Mapping[str, object]
    eal_spectrum: Mapping[str, object]

    def verify(self) -> None:
        if cutoff_equivariance_defect():
            raise AssertionError("cutoff equivariance Jacobi defect is nonzero")

        if self.causal_transport.get("schema") != (
            "pure-weyl-causal-transport-recognition-v1"
        ):
            raise AssertionError("wrong causal transport recognition schema")
        causal_theorem = _mapping(
            self.causal_transport.get("conditional_theorem"), "causal theorem"
        )
        cylinder = _mapping(
            self.causal_transport.get("cylinder_specialization"), "cylinder"
        )
        if not (
            causal_theorem.get("recognition_exact")
            and causal_theorem.get("requires_actual_causal_green_homotopy")
            and cylinder.get("Gamma_sc_equals_Gamma_smooth")
            and cylinder.get("cauchy_surface_compact")
        ):
            raise AssertionError("causal/cylinder recognition is incomplete")

        if self.auxiliary_retract.get("schema") != (
            "pure-weyl-curved-auxiliary-canonical-split-v1"
        ):
            raise AssertionError("wrong auxiliary retract schema")
        shift = _mapping(self.auxiliary_retract.get("auxiliary_eom_shift"), "auxiliary shift")
        split = _mapping(
            self.auxiliary_retract.get("factorized_curved_Q_split"), "curved Q split"
        )
        support = _mapping(split.get("support"), "auxiliary support")
        if not (
            self.auxiliary_retract.get("curved_deformation_retract")
            and shift.get("nonlinear_shift")
            == "phi_hat=phi-A_g^{-1}G^b(g,b)"
            and shift.get("uses_green_operator") is False
            and shift.get("uses_nonlocal_projector") is False
            and support.get("compact")
            and support.get("spacelike_compact")
            and support.get("smooth_global")
        ):
            raise AssertionError("natural support-local auxiliary retract regressed")

        if self.curvature_mapping_cylinder.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("wrong curvature mapping-cylinder schema")
        kernel = _mapping(self.curvature_mapping_cylinder.get("kernel"), "mapping kernel")
        substitution = _mapping(
            self.curvature_mapping_cylinder.get("substitution"), "mapping substitution"
        )
        if not (
            self.curvature_mapping_cylinder.get("support_local")
            and self.curvature_mapping_cylinder.get("coefficientwise_complete_prolonged_Q")
            and substitution.get("state_gauge_relation") == "T_state K_aux=0"
            and substitution.get("state_gauge_relation_exact")
            and kernel.get("Q_squared") == "zero"
            and kernel.get("P_I") == "identity"
            and kernel.get("I_P_minus_identity") == "QH+HQ"
        ):
            raise AssertionError("natural curvature mapping cylinder regressed")

        if self.curvature_causal_pde.get("schema") != (
            "pure-weyl-cotton-causal-pde-v1"
        ):
            raise AssertionError("wrong curvature causal-PDE schema")
        covariant_system = _mapping(
            self.curvature_causal_pde.get("exact_covariant_curvature_system"),
            "exact covariant curvature system",
        )
        if not (
            covariant_system.get("adjusted_and_covariant_differential_ideals_equal")
            and covariant_system.get("smooth_solution_spaces_equal")
            and covariant_system.get(
                "therefore_constrained_solutions_satisfy_all_34_covariant_rows"
            )
        ):
            raise AssertionError(
                "the first-order curvature state has not been identified with the natural covariant equations"
            )

        if self.raw_bv_transfer.get("schema") != "pure-weyl-raw-polynomial-transfer-v1":
            raise AssertionError("wrong raw BV transfer schema")
        raw_scope = _mapping(self.raw_bv_transfer.get("scope"), "raw transfer scope")
        proved = raw_scope.get("proved")
        if not isinstance(proved, list):
            raise AssertionError("raw transfer proved ledger missing")
        required_raw = {
            "raw q intertwines all four translations and special conformal maps",
            "nonzero defects with explicit q-homotopies",
            "strict induced conformal bracket",
        }
        if not (
            required_raw.issubset(set(proved))
            and self.raw_bv_transfer.get("noncompact_result")
            == "homotopy-equivariant, not strict"
            and self.raw_bv_transfer.get("induced_result")
            == "strict so(4,2) action on cohomology"
        ):
            raise AssertionError("raw SO(4,2) chain transfer regressed")

        if self.bgg_blocks.get("schema") != "pure-weyl-cylinder-bgg-normal-form-v1":
            raise AssertionError("wrong cylinder BGG schema")
        bgg_scope = _mapping(self.bgg_blocks.get("scope"), "BGG scope")
        if not (
            self.bgg_blocks.get("external_theorem_dependency")
            == "smooth flat-BGG exactness on R x S3"
            and "all-slot exactness and quotient dimensions" in bgg_scope.get("proved", [])
            and "ker B/im K=W+ direct-sum W-" in self.bgg_blocks.get("identities", [])
        ):
            raise AssertionError("global BGG/module input regressed")

        if self.metric_preimages.get("schema") != "pure-weyl-cylinder-preimages-v1":
            raise AssertionError("wrong metric-preimage schema")
        if not (
            self.metric_preimages.get("right_inverse_identity")
            == "C1 R_n=id on E/A/L curvature image blocks"
            and len(self.metric_preimages.get("records", [])) == 3
            and self.metric_preimages.get("parity_completion", {}).get("orientation") == -1
        ):
            raise AssertionError("all-level chiral curvature intertwiner regressed")

        if self.eal_spectrum.get("schema") != (
            "pure-weyl-curvature-eal-spectrum-all-level-v1"
        ):
            raise AssertionError("wrong all-level E/A/L schema")
        character = _mapping(self.eal_spectrum.get("symbolic_character"), "E/A/L character")
        exhaustion = _mapping(self.eal_spectrum.get("global_exhaustion"), "E/A/L exhaustion")
        chirality = _mapping(self.eal_spectrum.get("chirality"), "chirality")
        if not (
            self.eal_spectrum.get("EAL_curvature_spectrum_match")
            and self.eal_spectrum.get("all_level_not_finite_cutoff")
            and character.get("identity_all_coefficients")
            and exhaustion.get("global_BGG_exhaustion")
            and chirality.get("both_chiralities")
        ):
            raise AssertionError("all-level E/A/L exhaustion regressed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        result = {
            "schema": SCHEMA,
            "conditional_theorem": {
                "recognition_exact": True,
                "requires_causal_quasi_isomorphism": True,
                "conclusion": (
                    "the causal/global-solution identification induces the strict "
                    "SO(4,2) action on W_plus direct-sum W_minus and the residual endpoints"
                ),
            },
            "cutoff_homotopy": {
                "causal_inverse": "kappa=[Q,chi]",
                "identity": "[kappa,rho]=[Q,[chi,rho]]",
                "homotopy": "[chi,rho]",
                "formal_defect": 0,
                "homotopy_support_compact": True,
                "support_reason": (
                    "d chi is supported in a compact time slab and S3 is compact; "
                    "rho is a local first-order conformal generator"
                ),
                "all_fifteen_generators": True,
            },
            "local_naturality": {
                "auxiliary_shift_natural": True,
                "auxiliary_retract_support_local": True,
                "curvature_map_natural": True,
                "curvature_mapping_cylinder_support_local": True,
                "first_order_state_action_inherited_from_covariant_rows": True,
                "contractible_rows_add_no_action": True,
            },
            "global_module_identification": {
                "smooth_global_BGG_equivariant": True,
                "curvature_quotient_is_W_plus_W_minus": True,
                "all_level_EAL_exhaustion": True,
                "both_chiralities": True,
                "external_theorem": "flat BGG fine resolution on the conformal cylinder",
            },
            "residual_action": {
                "raw_generators_are_chain_maps": True,
                "raw_SDR_homotopy_equivariant": True,
                "strict_so42_action_on_cohomology": True,
                "proper_conformal_brackets_exact": True,
            },
            "promotion_boundary": {
                "does_not_construct_causal_green_homotopy": True,
                "does_not_claim_strict_Cauchy_split": True,
                "does_not_claim_pairing_transport": True,
                "SO42_equivariant_transport_conditional": True,
            },
        }
        if not recognition_certificate_passes(result):
            raise AssertionError("emitted SO(4,2) recognition certificate is invalid")
        return result
