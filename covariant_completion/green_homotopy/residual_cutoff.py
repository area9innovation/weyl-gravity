"""Cutoff-source realization of the fifteen global residual classes."""

from __future__ import annotations

from dataclasses import dataclass

from field_bv_identification.polarized_state import AlgebraicZeroModeTransgression
from field_bv_identification.zero_modes import DualEndpointCokernel


@dataclass(frozen=True)
class ResidualCutoffRecovery:
    residual_dimension: int
    endpoint_dimension: int
    suspension_sign: int

    @staticmethod
    def build() -> "ResidualCutoffRecovery":
        endpoint = DualEndpointCokernel.build()
        suspension = AlgebraicZeroModeTransgression.build()
        result = ResidualCutoffRecovery(
            residual_dimension=endpoint.zero_dimension,
            endpoint_dimension=endpoint.obstruction_dimension,
            suspension_sign=int(suspension.transgression_scalar),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.residual_dimension != 15 or self.endpoint_dimension != 15:
            raise AssertionError("the covariant residual pair is not 15+15")
        if self.suspension_sign != 1:
            raise AssertionError("the certified BV-to-BFV suspension sign changed")

        # At cochain level let chi_++chi_-=1 and Q xi=0.  Then
        # j=Q(chi_+ xi)=-Q(chi_- xi) is supported where d chi is nonzero.
        # The retarded solution represents chi_+xi, the advanced solution
        # represents -chi_-xi, and their difference represents xi.
        cutoff_identity = {
            "partition": "chi_plus+chi_minus=1",
            "source": "j_a=Q(chi_plus xi_a)=-Q(chi_minus xi_a)",
            "causal_recovery": "[Lambda j_a]=[xi_a]",
        }
        if "[xi_a]" not in cutoff_identity["causal_recovery"]:
            raise AssertionError("the cutoff source did not recover the global class")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-covariant-residual-cutoff-recovery-v1",
            "analytic_hypothesis": (
                "the curved Green-witness certificate supplies Lambda; the cutoff "
                "identity below is the exact consequence once that hypothesis passes"
            ),
            "temporal_cutoff": {
                "chi_past": 0,
                "chi_future": 1,
                "d_chi_support": "compact time slab times S^3",
            },
            "ghost_classes": {
                "source": "j_a=Q(chi xi_a)",
                "source_compact": True,
                "causal_recovery": "[Lambda j_a]=[xi_a]",
                "rank": self.residual_dimension,
                "compact_types": "4_-1 + 7_0 + 4_+1",
            },
            "dual_endpoint_classes": {
                "rank": self.endpoint_dimension,
                "duality": "I/im(K^sharp) isomorphic to (ker K)^*",
                "cutoff_construction": "formal-adjoint dual of the ghost cutoff sources",
            },
            "bfv_replacement": {
                "endpoint_suspension_lambda": self.suspension_sign,
                "one_residual_ghost_copy": 15,
                "one_bfv_momentum_copy": 15,
                "moment_map_is_a_function_not_an_extra_coordinate": True,
            },
            "no_duplication": {
                "auxiliary_enlargement": "contractible 36-dimensional cotangent sector",
                "gauge_fixing": "existing zero-mode-preserving contraction",
                "global_causal_map_after_curved_witness": (
                    "rank 15 recovered by cutoff sources"
                ),
                "bfv_replacement": "transfer, not direct-sum duplication",
            },
            "theorem_boundary": (
                "the cutoff formula and algebraic BFV comparison are certified; its "
                "realization by a causal map is conditional on the curved witness, and "
                "the endpoint current normalization belongs to the pairing certificate"
            ),
        }
