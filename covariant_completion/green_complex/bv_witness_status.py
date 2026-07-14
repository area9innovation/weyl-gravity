"""Machine-readable boundary between direct and auxiliary BV witnesses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BVGreenWitnessStatus:
    """Inventory the proved auxiliary structure and remaining curved route."""

    def certificate(self) -> dict[str, object]:
        return {
            "schema": "pure-weyl-bv-green-witness-status-v3",
            "auxiliary_symbol_witness_proved": True,
            "exact_66_to_30_symbol_retract_with_support_local_formulas_proved": True,
            "curved_auxiliary_green_hyperbolic_realization_proved": False,
            "direct_same_bundle_metric_factorization_proved": False,
            "proved_inputs": [
                "reduced TT Bach block P_minus P_plus",
                "reduced transverse-vector block P_A",
                "T K=Box(Box+2) on the complete local ghost bundle",
                "action-normalized B_lin and H=B_lin+K T/2 on S^2_0",
                "graded formal witness matrix with metric block 2H",
                "ordinary-derivative tensor--tensor--vector realization",
                "scalar wave principal symbols for auxiliary ghost and field operators",
                "exact 66-to-30 all-row Fourier-complex SDR with support-local formulas",
                "formal retarded/advanced Green-homotopy recognition identities",
                "pointwise causal trace and nonminimal doublets",
            ],
            "remaining_direct_route": [
                "a same-bundle product of H on every trace-free metric component",
                "or another direct Green proof for 2H without auxiliary fields",
            ],
            "remaining_covariant_completion": [
                "the complete curved first/zeroth-order auxiliary coefficient table",
                "the curved lower-order chain identities for the 66-to-30 retract",
                "covariant formal-adjoint verification including every lower term",
                "the auxiliary differential Green current and its metric pullback",
                "the programme-specific covariant/Cauchy pairing normalization",
                "distributional/Hadamard extensions beyond compact and spacelike-compact smooth sections",
            ],
            "forbidden_inference": (
                "the exact auxiliary symbol witness and local SDR do not by themselves "
                "prove the curved Green theorem or a direct same-bundle factorization of B+K T/2"
            ),
        }
