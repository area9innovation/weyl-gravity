"""Formal-integrability bridge for the exact and hyperbolic curvature rows.

The covariant Weyl--Cotton system has 34 rows on 26 variables.  Its direct
temporal reduction is not hyperbolic.  The constraint-adjusted system uses
26 symmetric-hyperbolic evolution rows and the fourteen constraint
quantities ``q,r,a,c,s,t``.

The two row sets are not pointwise row-equivalent: the exact vector Bach
rows ``U_x,U_y`` and adjusted propagation rows ``R_x,R_y`` satisfy

``R_x=U_x-2a`` and ``R_y=U_y-2c``.

They are nevertheless equivalent as *formally integrable differential
ideals*.  The exact primary rows ``q=r=0`` and vector Bach rows imply the
secondary constraints ``a=c=0`` after one time derivative.  Conversely,
the adjusted rows together with ``a=c=0`` recover the vector Bach rows.
This module certifies that implication and the compatible-source version;
it does not alter the repository status ledger.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution
from .weyl_cotton_row_audit import WeylCottonRowReductionAudit


@dataclass(frozen=True)
class WeylCottonFormalIntegrability:
    """Exact differential-ideal equivalence and source compatibility."""

    adjusted: ConstraintAdjustedWeylCottonEvolution
    row_audit: WeylCottonRowReductionAudit
    exact_raw_subsidiary_characteristic: sp.Expr

    @staticmethod
    def build() -> "WeylCottonFormalIntegrability":
        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        # Principal exact-raw subsidiary state order q,r,a,c,s,t.  This
        # unadjusted system is recorded to expose (not hide) its imaginary
        # longitudinal pair; the formally equivalent adjusted subsidiary is
        # the symmetric-hyperbolic one used for propagation.
        vector_curl = adjusted.vector_curl_coefficients[0]
        derivative = sp.eye(3)[:, 0]
        divergence = derivative.T
        slices = (
            slice(0, 3),
            slice(3, 6),
            slice(6, 9),
            slice(9, 12),
            slice(12, 13),
            slice(13, 14),
        )
        raw = sp.zeros(14)
        raw[slices[0], slices[1]] = sp.Rational(1, 2) * vector_curl
        raw[slices[1], slices[0]] = -sp.Rational(1, 2) * vector_curl
        raw[slices[2], slices[3]] = vector_curl
        raw[slices[3], slices[2]] = -vector_curl
        raw[slices[2], slices[4]] = -sp.Rational(1, 3) * derivative
        raw[slices[3], slices[5]] = -sp.Rational(1, 3) * derivative
        raw[slices[4], slices[2]] = divergence
        raw[slices[5], slices[3]] = divergence
        spectral_parameter = sp.Symbol("lambda")
        result = WeylCottonFormalIntegrability(
            adjusted=adjusted,
            row_audit=WeylCottonRowReductionAudit.build(),
            exact_raw_subsidiary_characteristic=sp.factor(
                raw.charpoly(spectral_parameter).as_expr()
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.adjusted.verify()
        self.row_audit.verify()
        if self.row_audit.exact_first_twenty_defects:
            raise AssertionError("first twenty hyperbolic rows are not covariant")
        if self.row_audit.vector_difference_defect:
            raise AssertionError("R_x=U_x-2a derivative identity failed")
        if self.row_audit.zeroth_order_difference_defect:
            raise AssertionError("R_x=U_x-2a lower-order identity failed")
        if self.row_audit.original_constraint_defects:
            raise AssertionError("primary q,r,s,t rows are not covariant")
        if self.row_audit.additional_ac_rank != 6:
            raise AssertionError("secondary a,c constraints lost rank")
        certificate = self.adjusted.certificate()
        if not certificate["exact_sourced_subsidiary_operator_identity"]:
            raise AssertionError("sourced subsidiary operator identity regressed")
        if not certificate["subsidiary_symmetrizer_positive"]:
            raise AssertionError("subsidiary symmetric hyperbolicity regressed")
        if not certificate["homogeneous_constraints_propagate"]:
            raise AssertionError("homogeneous constraints do not propagate")
        lam = sp.Symbol("lambda")
        expected_raw = sp.factor(
            lam**2
            * (lam**2 - 1) ** 2
            * (4 * lam**2 - 1) ** 2
            * (3 * lam**2 + 1) ** 2
            / 144
        )
        if self.exact_raw_subsidiary_characteristic != expected_raw:
            raise AssertionError("exact raw subsidiary characteristic drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        adjusted_certificate = self.adjusted.certificate()
        return {
            "schema": "pure-weyl-cotton-formal-integrability-v1",
            "exact_covariant_system": "34 Weyl-definition/Bach/dual rows",
            "hyperbolic_system": "26 adjusted evolution rows plus 14 constraints",
            "primary_covariant_constraints": [
                "q=x-div E",
                "r=y-div B",
                "s=div x",
                "t=div y",
            ],
            "secondary_constraints": [
                "a=div A+(1/2)curl y",
                "c=div C-(1/2)curl x",
            ],
            "secondary_constraint_rank": self.row_audit.additional_ac_rank,
            "exact_vector_row_relation": [
                "R_x=U_x-2a",
                "R_y=U_y-2c",
            ],
            "exact_to_hyperbolic_implication": [
                "q_t+(1/2)curl r=R_x on the exact first-twenty rows",
                "r_t-(1/2)curl q=R_y on the exact first-twenty rows",
                "q=r=U_x=U_y=0 and R_x=U_x-2a, R_y=U_y-2c imply a=c=0",
                "then R_x=R_y=0",
            ],
            "hyperbolic_to_exact_implication": [
                "the first twenty hyperbolic rows are exact covariant row combinations",
                "q=r=s=t=0 recover the eight primary covariant constraints",
                "R_x=R_y=a=c=0 imply U_x=U_y=0",
            ],
            "formally_integrable_differential_ideals_equivalent": True,
            "pointwise_row_modules_equal": False,
            "pointwise_row_rank_defect": self.row_audit.exact_plus_adjusted_rank
            - self.row_audit.exact_row_rank,
            "exact_raw_homogeneous_subsidiary_equations": [
                "q_t+(1/2)curl r+2a=0",
                "r_t-(1/2)curl q+2c=0",
                "a_t+curl c-q-(1/3)grad s=0",
                "c_t-curl a-r-(1/3)grad t=0",
                "s_t+div a=0",
                "t_t+div c=0",
            ],
            "exact_raw_sourced_subsidiary_equations": [
                "q_t+(1/2)curl r+2a=g_x-div f_E",
                "r_t-(1/2)curl q+2c=g_y-div f_B",
                "a_t+curl c-q-(1/3)grad s=div f_A+(1/2)curl g_y",
                "c_t-curl a-r-(1/3)grad t=div f_C-(1/2)curl g_x",
                "s_t+div a=div g_x",
                "t_t+div c=div g_y",
            ],
            "exact_raw_subsidiary_characteristic": str(
                self.exact_raw_subsidiary_characteristic
            ),
            "exact_raw_subsidiary_hyperbolic": False,
            "exact_raw_longitudinal_speeds": ["-i/sqrt(3)", "+i/sqrt(3)"],
            "adjusted_homogeneous_subsidiary_equations": [
                "q_t+(1/2)curl r=0",
                "r_t-(1/2)curl q=0",
                "a_t-q-(1/3)grad s=0",
                "c_t-r-(1/3)grad t=0",
                "s_t-div a=0",
                "t_t-div c=0",
            ],
            "adjusted_sourced_subsidiary_equations": adjusted_certificate[
                "sourced_subsidiary_equations"
            ],
            "compatible_exact_sources": [
                "g_x-div f_E=0",
                "g_y-div f_B=0",
                "div f_A+(1/2)curl g_y=0",
                "div f_C-(1/2)curl g_x=0",
                "div g_x=0",
                "div g_y=0",
            ],
            "source_notation": (
                "f_E,f_B,f_A,f_C source the first twenty tensor rows; "
                "g_x,g_y source the exact vector Bach rows"
            ),
            "compatible_sources_preserve_all_fourteen_constraints": True,
            "exact_sourced_subsidiary_operator_identity": True,
            "constraint_adjustment_removes_raw_imaginary_longitudinal_pair": True,
            "subsidiary_symmetrizer_positive": True,
            "subsidiary_characteristic": adjusted_certificate[
                "subsidiary_characteristic"
            ],
            "subsidiary_characteristic_speeds": {
                "-1/sqrt(3)": 2,
                "-1/2": 2,
                "0": 6,
                "+1/2": 2,
                "+1/sqrt(3)": 2,
            },
            "subsidiary_characteristics_causal": True,
            "constraint_additions_are_support_local": True,
            "warranted_atomic_flags": [
                "curved_EB_symmetric_hyperbolicity",
                "curved_sourced_constraint_identity",
                "curved_constraint_propagation",
            ],
            "flags_promoted_here": [],
            "proof_boundary": (
                "exact curvature PDE and formally integrable sourced constraint "
                "closure only; no E/A/L, BV, Green, causal-homotopy, endpoint, "
                "equivariance, or current theorem"
            ),
            "fail_closed": True,
        }
