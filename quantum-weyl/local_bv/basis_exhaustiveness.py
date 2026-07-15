"""Integer grading signatures for dimension-four AFN0 local monomials."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .algebra import canonical_json, canonical_sha256


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class BoundProofArtifact:
    """Canonical payload carried by, and cryptographically bound to, a proof."""

    role: str
    payload_json: str
    sha256: str

    @classmethod
    def create(cls, role: str, payload: object) -> "BoundProofArtifact":
        return cls(
            role=role,
            payload_json=canonical_json(payload),
            sha256=canonical_sha256(payload),
        )

    def verify(self) -> None:
        try:
            payload = json.loads(self.payload_json)
        except json.JSONDecodeError as error:
            raise ValueError(f"proof artifact {self.role} is not canonical JSON") from error
        if canonical_json(payload) != self.payload_json:
            raise ValueError(f"proof artifact {self.role} is not canonically serialized")
        if _SHA256.fullmatch(self.sha256) is None:
            raise ValueError(f"proof artifact {self.role} contains a malformed hash")
        if canonical_sha256(payload) != self.sha256:
            raise ValueError(f"proof artifact {self.role} hash does not reproduce")

    def canonical_payload(self) -> dict[str, str]:
        return {
            "role": self.role,
            "payload_json": self.payload_json,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class BasisExhaustivenessProof:
    """Artifact-bound proof object required for complete witness promotion."""

    basis_manifest_hash: str
    declared_bounds_hash: str
    generator_algebra_hash: str
    grading_solution_hash: str
    orbit_enumeration_hash: str
    identity_quotient_hash: str
    proof_artifact_hash: str
    bound_artifacts: tuple[BoundProofArtifact, ...]
    proof_hash: str
    verification_status: str = "VERIFIED_ARTIFACT_BOUND"

    @classmethod
    def create(
        cls,
        *,
        basis_manifest: object,
        declared_bounds: object,
        generator_algebra: object,
        grading_solution: object,
        orbit_enumeration: object,
        identity_quotient: object,
        proof_artifact: object,
    ) -> "BasisExhaustivenessProof":
        artifacts = tuple(
            BoundProofArtifact.create(role, artifact)
            for role, artifact in (
                ("basis_manifest", basis_manifest),
                ("declared_bounds", declared_bounds),
                ("generator_algebra", generator_algebra),
                ("grading_solution", grading_solution),
                ("orbit_enumeration", orbit_enumeration),
                ("identity_quotient", identity_quotient),
                ("proof_artifact", proof_artifact),
            )
        )
        hashes = {artifact.role: artifact.sha256 for artifact in artifacts}
        payload = {
            "basis_manifest_hash": hashes["basis_manifest"],
            "declared_bounds_hash": hashes["declared_bounds"],
            "generator_algebra_hash": hashes["generator_algebra"],
            "grading_solution_hash": hashes["grading_solution"],
            "orbit_enumeration_hash": hashes["orbit_enumeration"],
            "identity_quotient_hash": hashes["identity_quotient"],
            "proof_artifact_hash": hashes["proof_artifact"],
            "bound_artifacts": artifacts,
            "verification_status": "VERIFIED_ARTIFACT_BOUND",
        }
        proof_payload = {
            **{key: value for key, value in payload.items() if key != "bound_artifacts"},
            "bound_artifacts": [artifact.canonical_payload() for artifact in artifacts],
        }
        return cls(**payload, proof_hash=canonical_sha256(proof_payload))

    def verify(self, *, expected_basis_manifest_hash: str) -> None:
        payload = self.canonical_payload(include_proof_hash=False)
        hashes = [value for key, value in payload.items() if key.endswith("_hash")]
        if self.verification_status != "VERIFIED_ARTIFACT_BOUND":
            raise ValueError("basis exhaustiveness proof is not artifact-bound and verified")
        if any(
            not isinstance(value, str) or _SHA256.fullmatch(value) is None
            for value in hashes
        ):
            raise ValueError("basis exhaustiveness proof contains a malformed hash")
        if self.basis_manifest_hash != expected_basis_manifest_hash:
            raise ValueError("basis exhaustiveness proof does not bind the supplied basis")
        required_roles = {
            "basis_manifest",
            "declared_bounds",
            "generator_algebra",
            "grading_solution",
            "orbit_enumeration",
            "identity_quotient",
            "proof_artifact",
        }
        artifacts = {artifact.role: artifact for artifact in self.bound_artifacts}
        if set(artifacts) != required_roles or len(artifacts) != len(self.bound_artifacts):
            raise ValueError("basis exhaustiveness proof artifact roles are incomplete or duplicated")
        for artifact in artifacts.values():
            artifact.verify()
        for role in required_roles:
            field_hash = getattr(self, f"{role}_hash")
            if field_hash != artifacts[role].sha256:
                raise ValueError(f"basis exhaustiveness proof {role} artifact is not bound")
        if self.proof_hash != canonical_sha256(payload):
            raise ValueError("basis exhaustiveness proof hash does not reproduce")

    def canonical_payload(self, *, include_proof_hash: bool = True) -> dict[str, object]:
        payload = {
            "basis_manifest_hash": self.basis_manifest_hash,
            "declared_bounds_hash": self.declared_bounds_hash,
            "generator_algebra_hash": self.generator_algebra_hash,
            "grading_solution_hash": self.grading_solution_hash,
            "orbit_enumeration_hash": self.orbit_enumeration_hash,
            "identity_quotient_hash": self.identity_quotient_hash,
            "proof_artifact_hash": self.proof_artifact_hash,
            "bound_artifacts": [
                artifact.canonical_payload() for artifact in self.bound_artifacts
            ],
            "verification_status": self.verification_status,
        }
        if include_proof_hash:
            payload["proof_hash"] = self.proof_hash
        return payload


def _signature(
    *,
    curvature_count: int,
    tensor_derivative_count: int,
    ghost_derivative_order: int,
    ghost_species: str,
    parity: str,
) -> dict[str, object]:
    ghost_factor_count = 0 if ghost_species == "NONE" else 1
    tensor_index_slots = 4 * curvature_count + tensor_derivative_count
    ghost_index_slots = ghost_derivative_order + int(ghost_species == "DIFF")
    return {
        "curvature_count": curvature_count,
        "tensor_derivative_count": tensor_derivative_count,
        "ghost_factor_count": ghost_factor_count,
        "ghost_derivative_order": ghost_derivative_order,
        "ghost_species": ghost_species,
        "epsilon_count": 0 if parity == "even" else 1,
        "tensor_index_slots": tensor_index_slots,
        "ghost_index_slots": ghost_index_slots,
        "total_index_slots": tensor_index_slots + ghost_index_slots,
        "form_degree": 4,
        "generalized_connection_degree": 0,
    }


def coarse_top_form_signatures(
    ghost_number: int, parity: str, *, ghost_species: str | None = None
) -> tuple[dict[str, object], ...]:
    """Solve engineering grading before tensor-realizability constraints."""

    if ghost_number not in {0, 1}:
        raise ValueError("the AFN0 dimension-four manifest supports ghost number 0 or 1")
    if parity not in {"even", "odd"}:
        raise ValueError("spacetime parity must be even or odd")
    if ghost_species is None:
        ghost_species = "NONE" if ghost_number == 0 else "WEYL"
    permitted = {0: {"NONE"}, 1: {"WEYL", "DIFF"}}
    if ghost_species not in permitted[ghost_number]:
        raise ValueError("ghost species does not match ghost number")
    ghost_offset = -1 if ghost_species == "DIFF" else 0
    solutions = []
    for curvature_count in range(3):
        for tensor_derivative_count in range(6):
            if ghost_species == "DIFF":
                derivative_orders = range(6)
            elif ghost_species == "WEYL":
                derivative_orders = range(5)
            else:
                derivative_orders = (0,)
            for ghost_derivative_order in derivative_orders:
                if (
                    2 * curvature_count
                    + tensor_derivative_count
                    + ghost_derivative_order
                    + ghost_offset
                    != 4
                ):
                    continue
                solutions.append(
                    _signature(
                        curvature_count=curvature_count,
                        tensor_derivative_count=tensor_derivative_count,
                        ghost_derivative_order=ghost_derivative_order,
                        ghost_species=ghost_species,
                        parity=parity,
                    )
                )
    return tuple(
        sorted(solutions, key=lambda row: tuple(row[key] for key in sorted(row)))
    )


def refine_top_form_signature(
    signature: dict[str, object],
) -> tuple[bool, str]:
    """Apply structural constraints that precede index-graph generation."""

    if (
        signature["curvature_count"] == 0
        and signature["tensor_derivative_count"]
    ):
        return (
            False,
            "covariant tensor derivatives have no tensor seed because nabla g = 0",
        )
    total_slots = int(signature["total_index_slots"])
    if total_slots % 2:
        return False, "a Lorentz scalar cannot contract an odd total index count"
    if signature["epsilon_count"] and total_slots < 4:
        return False, "a four-dimensional epsilon tensor requires four index slots"
    return True, "passes tensor-seed, scalar-index, and epsilon-availability constraints"


def grading_signature_manifest(ghost_number: int, parity: str) -> dict[str, object]:
    """Audit coarse, refined-Weyl, and separate Diff top-form signatures."""

    coarse = coarse_top_form_signatures(ghost_number, parity)
    diff_coarse = (
        coarse_top_form_signatures(1, parity, ghost_species="DIFF")
        if ghost_number == 1
        else ()
    )
    refined = [row for row in coarse if refine_top_form_signature(row)[0]]
    diff_refined = [row for row in diff_coarse if refine_top_form_signature(row)[0]]
    rejected = [
        {"signature": row, "reason": refine_top_form_signature(row)[1]}
        for row in (*coarse, *diff_coarse)
        if not refine_top_form_signature(row)[0]
    ]
    template_covered = [
        row
        for row in refined
        if row["ghost_derivative_order"] == 0
        and row["curvature_count"] in {1, 2}
    ]
    combined_coarse = sorted(
        (*coarse, *diff_coarse),
        key=lambda row: tuple(row[key] for key in sorted(row)),
    )
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
            "n_total_index_slots is even for a Lorentz scalar",
            "epsilon_count = 0 for even parity and 1 for odd parity",
            "ordinary top-form carrier has form_degree = 4 and generalized_connection_degree = 0",
            "all signature variables are nonnegative integers",
        ],
        "coarse_grading_signatures": list(coarse),
        "coarse_grading_signature_count": len(coarse),
        "refined_grading_signatures": refined,
        "refined_grading_signature_count": len(refined),
        "diff_top_form_coarse_signatures": list(diff_coarse),
        "diff_top_form_coarse_signature_count": len(diff_coarse),
        "diff_top_form_refined_signatures": diff_refined,
        "diff_top_form_refined_signature_count": len(diff_refined),
        "combined_coarse_signatures": combined_coarse,
        "combined_coarse_signature_count": len(combined_coarse),
        "refinement_rejections": rejected,
        "template_covered_signature_count": len(template_covered),
        "template_covered_signatures": template_covered,
        "excluded_types_with_reason": [
            {
                "type": "pure_metric_derivatives",
                "reason": "metric compatibility gives no nonconstant tensor seed",
            },
            {
                "type": "pure_diffeomorphism_ghost_signatures",
                "reason": "top-form Diff signatures are separated from the Weyl-anomaly count; their index quotient and descent role are pending",
            },
            {
                "type": "unexpanded_generalized_connection_signatures",
                "reason": "Euler generalized-connection bidegree expansion is in progress",
            },
        ],
        "generated_orbit_count": "PENDING_INDEX_ORBIT_ENUMERATION",
        "canonical_dimension": "PENDING_COMPLETE_IDENTITY_QUOTIENT",
        "tensor_realizable_signature_count": "PENDING_CONTRACTION_GRAPH_ENUMERATION",
        "canonical_nonzero_signature_count": "PENDING_CANONICAL_QUOTIENT",
        "multigrading_status": "COARSE_AND_REFINED_TOP_FORM_COUNTS_SEPARATED",
        "exhaustiveness_status": "IN_PROGRESS",
    }
    return {**manifest, "grading_manifest_hash": canonical_sha256(manifest)}
