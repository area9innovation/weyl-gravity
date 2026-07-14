"""Quantitative fail-closed ledger for the one-point globalization proof."""

from __future__ import annotations

from dataclasses import dataclass
import math


def jet_monomials_through(order: int, dimension: int = 4) -> int:
    """Number of symmetric derivative multiindices of degree at most order."""

    return math.comb(dimension + order, order)


def homogeneous_jet_monomials(order: int, dimension: int = 4) -> int:
    return math.comb(dimension + order - 1, order)


@dataclass(frozen=True)
class OperatorJetObligation:
    name: str
    input_rank: int
    output_rank: int
    order: int
    principal_vectors_tested: int
    complete_vectors_tested: int = 0

    @property
    def required_vectors(self) -> int:
        return self.input_rank * jet_monomials_through(self.order)

    @property
    def principal_vectors_required(self) -> int:
        return self.input_rank * homogeneous_jet_monomials(self.order)

    @property
    def complete(self) -> bool:
        return self.complete_vectors_tested == self.required_vectors

    def certificate(self) -> dict[str, object]:
        return {
            "input_rank": self.input_rank,
            "output_rank": self.output_rank,
            "operator_order": self.order,
            "required_jet_vectors_through_order": self.required_vectors,
            "principal_jet_vectors_required": self.principal_vectors_required,
            "principal_jet_vectors_tested": self.principal_vectors_tested,
            "complete_jet_vectors_tested": self.complete_vectors_tested,
            "complete": self.complete,
        }


@dataclass(frozen=True)
class CurvedOperatorGlobalization:
    obligations: tuple[OperatorJetObligation, ...]
    homogeneous_background: bool
    parallel_curvature: bool
    normal_form_available: bool
    expanded_coefficient_tables_available: bool

    @staticmethod
    def build() -> "CurvedOperatorGlobalization":
        # Principal-symbol vectors are already exhausted by the exact
        # polynomial matrices.  No full curved lower-jet evaluation is
        # recorded until the expanded operators exist.
        obligations = (
            OperatorJetObligation(
                "Q_squared_G_to_E",
                9,
                24,
                3,
                9 * homogeneous_jet_monomials(3),
            ),
            OperatorJetObligation(
                "Q_squared_M_to_I",
                24,
                9,
                3,
                24 * homogeneous_jet_monomials(3),
            ),
            OperatorJetObligation(
                "QW_plus_WQ_minus_P_on_G",
                9,
                9,
                2,
                9 * homogeneous_jet_monomials(2),
            ),
            OperatorJetObligation(
                "QW_plus_WQ_minus_P_on_M",
                24,
                24,
                2,
                24 * homogeneous_jet_monomials(2),
            ),
            OperatorJetObligation(
                "QW_plus_WQ_minus_P_on_E",
                24,
                24,
                2,
                24 * homogeneous_jet_monomials(2),
            ),
            OperatorJetObligation(
                "QW_plus_WQ_minus_P_on_I",
                9,
                9,
                2,
                9 * homogeneous_jet_monomials(2),
            ),
            OperatorJetObligation(
                "W_sharp_minus_W",
                66,
                66,
                1,
                66 * homogeneous_jet_monomials(1),
            ),
        )
        result = CurvedOperatorGlobalization(
            obligations=obligations,
            homogeneous_background=True,
            parallel_curvature=True,
            normal_form_available=True,
            expanded_coefficient_tables_available=False,
        )
        result.verify()
        return result

    def verify(self) -> None:
        for obligation in self.obligations:
            if obligation.principal_vectors_tested != obligation.principal_vectors_required:
                raise AssertionError(
                    f"principal coverage drifted for {obligation.name}"
                )
            if obligation.complete_vectors_tested > obligation.required_vectors:
                raise AssertionError("invalid jet coverage count")

    @property
    def complete(self) -> bool:
        return (
            self.homogeneous_background
            and self.parallel_curvature
            and self.normal_form_available
            and self.expanded_coefficient_tables_available
            and all(obligation.complete for obligation in self.obligations)
        )

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-operator-globalization-ledger-v1",
            "background_group": "R x SO(4)",
            "transitive_on_cylinder": True,
            "homogeneous_coefficients": self.homogeneous_background,
            "parallel_curvature": self.parallel_curvature,
            "isotropy_covariance_required": True,
            "derivative_normal_form_available": self.normal_form_available,
            "expanded_coefficient_tables_available": self.expanded_coefficient_tables_available,
            "obligations": {
                obligation.name: obligation.certificate()
                for obligation in self.obligations
            },
            "complete": self.complete,
            "globalization_rule": (
                "an equivariant finite-order operator vanishing on the exhaustive "
                "normal-frame jet fibre at one point vanishes globally"
            ),
            "guard": (
                "transitivity and a normal-form engine do not prove vanishing until "
                "every required lower-order jet vector has actually been evaluated"
            ),
        }
