"""Integer grading signatures for dimension-four AFN0 local monomials."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .algebra import canonical_sha256


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class BasisExhaustivenessProof:
    """Hash-bound proof object required for complete witness promotion."""

    basis_manifest_hash: str
    declared_bounds_hash: str
    generator_algebra_hash: str
    grading_solution_hash: str
    orbit_enumeration_hash: str
    identity_quotient_hash: str
    proof_artifact_hash: str
    proof_hash: str
    verification_status: str = "VERIFIED"

    @classmethod
    def create(
        cls,
        *,
        basis_manifest_hash: str,
        declared_bounds_hash: str,
        generator_algebra_hash: str,
        grading_solution_hash: str,
        orbit_enumeration_hash: str,
        identity_quotient_hash: str,
        proof_artifact_hash: str,
    ) -> "BasisExhaustivenessProof":
        payload = {
            "basis_manifest_hash": basis_manifest_hash,
            "declared_bounds_hash": declared_bounds_hash,
            "generator_algebra_hash": generator_algebra_hash,
            "grading_solution_hash": grading_solution_hash,
            "orbit_enumeration_hash": orbit_enumeration_hash,
            "identity_quotient_hash": identity_quotient_hash,
            "proof_artifact_hash": proof_artifact_hash,
            "verification_status": "VERIFIED",
        }
        return cls(**payload, proof_hash=canonical_sha256(payload))

    def verify(self, *, expected_basis_manifest_hash: str) -> None:
        payload = self.canonical_payload(include_proof_hash=False)
        hashes = [value for key, value in payload.items() if key.endswith("_hash")]
        if self.verification_status != "VERIFIED":
            raise ValueError("basis exhaustiveness proof is not verified")
        if any(
            not isinstance(value, str) or _SHA256.fullmatch(value) is None
            for value in hashes
        ):
            raise ValueError("basis exhaustiveness proof contains a malformed hash")
        if self.basis_manifest_hash != expected_basis_manifest_hash:
            raise ValueError("basis exhaustiveness proof does not bind the supplied basis")
        if self.proof_hash != canonical_sha256(payload):
            raise ValueError("basis exhaustiveness proof hash does not reproduce")

    def canonical_payload(self, *, include_proof_hash: bool = True) -> dict[str, str]:
        payload = {
            "basis_manifest_hash": self.basis_manifest_hash,
            "declared_bounds_hash": self.declared_bounds_hash,
            "generator_algebra_hash": self.generator_algebra_hash,
            "grading_solution_hash": self.grading_solution_hash,
            "orbit_enumeration_hash": self.orbit_enumeration_hash,
            "identity_quotient_hash": self.identity_quotient_hash,
            "proof_artifact_hash": self.proof_artifact_hash,
            "verification_status": self.verification_status,
        }
        if include_proof_hash:
            payload["proof_hash"] = self.proof_hash
        return payload


def grading_signature_manifest(ghost_number: int, parity: str) -> dict[str, object]:
    """Enumerate nonnegative solutions of the declared engineering grading.

    This is an independent structural check on symbolic generation, not yet an
    exhaustiveness proof: tensor-index singlets, integration by parts, pure
    Diff ghosts, and generalized-connection expansion remain separate gates.
    """

    if ghost_number not in {0, 1}:
        raise ValueError("the AFN0 dimension-four manifest supports ghost number 0 or 1")
    if parity not in {"even", "odd"}:
        raise ValueError("spacetime parity must be even or odd")
    solutions: list[dict[str, object]] = []
    ghost_species = ("NONE",) if ghost_number == 0 else ("WEYL", "DIFF")
    for species in ghost_species:
        for curvature_count in range(3):
            for tensor_derivative_count in range(6):
                if species == "NONE":
                    ghost_derivative_orders = (0,)
                    ghost_engineering_offset = 0
                elif species == "WEYL":
                    ghost_derivative_orders = range(5)
                    ghost_engineering_offset = 0
                else:
                    ghost_derivative_orders = range(6)
                    ghost_engineering_offset = -1
                for ghost_derivative_order in ghost_derivative_orders:
                    engineering_dimension = (
                        2 * curvature_count
                        + tensor_derivative_count
                        + ghost_derivative_order
                        + ghost_engineering_offset
                    )
                    if engineering_dimension != 4:
                        continue
                    covariant_index_count = (
                        4 * curvature_count
                        + tensor_derivative_count
                        + ghost_derivative_order
                        - (1 if species == "DIFF" else 0)
                    )
                    if covariant_index_count < 0 or covariant_index_count % 2:
                        continue
                    if parity == "odd" and covariant_index_count < 4:
                        continue
                    solutions.append(
                        {
                            "curvature_count": curvature_count,
                            "tensor_derivative_count": tensor_derivative_count,
                            "ghost_factor_count": ghost_number,
                            "ghost_derivative_order": ghost_derivative_order,
                            "ghost_species": species,
                            "epsilon_count": 0 if parity == "even" else 1,
                            "covariant_index_count_after_diff_ghost": covariant_index_count,
                            "form_degree": 4,
                            "generalized_connection_degree": 0,
                        }
                    )
    solutions.sort(
        key=lambda row: tuple(row[key] for key in sorted(row))
    )
    generated = [
        row
        for row in solutions
        if row["ghost_species"] in {"NONE", "WEYL"}
        and row["ghost_derivative_order"] == 0
        and row["curvature_count"] in {1, 2}
    ]
    manifest = {
        "generator_algebra": {
            "curvature_or_weyl_tensor": {
                "engineering_dimension": 2,
                "ghost_number": 0,
            },
            "covariant_derivative": {
                "engineering_dimension": 1,
                "ghost_number": 0,
            },
            "weyl_ghost": {
                "engineering_dimension": 0,
                "ghost_number": 1,
                "derivative_cost": 1,
            },
            "diffeomorphism_ghost": {
                "engineering_dimension": -1,
                "ghost_number": 1,
                "contravariant_rank": 1,
                "derivative_cost": 1,
            },
            "metric_inverse_metric_levi_civita": {
                "engineering_dimension": 0,
                "ghost_number": 0,
            },
        },
        "grading_equations": [
            "2*n_curvature + n_tensor_derivative + n_ghost_derivative + ghost_engineering_offset = 4",
            f"n_total_ghost = {ghost_number}",
            "covariant index balance after contracting a Diff-ghost vector is even",
            "epsilon_count = 0 for even parity and 1 for odd parity",
            "ordinary top-form carrier has form_degree = 4 and generalized_connection_degree = 0",
            "all signature variables are nonnegative integers",
        ],
        "integer_solutions_for_monomial_types": solutions,
        "integer_solution_count": len(solutions),
        "currently_generated_signature_count": len(generated),
        "currently_generated_signatures": generated,
        "excluded_types_with_reason": [
            {
                "type": "pure_metric_derivatives",
                "reason": "metric compatibility gives no nonconstant tensor seed",
            },
            {
                "type": "pure_diffeomorphism_ghost_signatures",
                "reason": "signatures are enumerated; index-orbit generation and BRST quotient are pending",
            },
            {
                "type": "unexpanded_generalized_connection_signatures",
                "reason": "Euler generalized-connection bidegree expansion is in progress",
            },
        ],
        "generated_orbit_count": "PENDING_INDEX_ORBIT_ENUMERATION",
        "canonical_dimension": "PENDING_COMPLETE_IDENTITY_QUOTIENT",
        "multigrading_status": "ENGINEERING_FORM_GHOST_PARITY_INDEX_BALANCE_ENUMERATED",
        "exhaustiveness_status": "IN_PROGRESS",
    }
    return {**manifest, "grading_manifest_hash": canonical_sha256(manifest)}
