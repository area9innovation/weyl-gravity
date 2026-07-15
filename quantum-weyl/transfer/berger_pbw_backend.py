"""Registered operator-level backend for the imported retained Berger q1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .berger_retained_q1_import_certificate import build_certificate
    from .operator_backend_registry import (
        OperatorBackendDescriptor,
        OperatorBackendRegistry,
    )
except ImportError:
    from berger_retained_q1_import_certificate import build_certificate
    from operator_backend_registry import OperatorBackendDescriptor, OperatorBackendRegistry


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
BACKEND_ID = "berger-invariant-pbw-linear-v1"
EXPRESSION_SCHEMA_VERSION = "quantum-weyl-berger-retained-minimal-q1-import-v1"
COEFFICIENT_DOMAIN = "Q[alpha_B,u,v] tensor U(e_Berger) in ordered PBW normal form"
CAPABILITIES = (
    "exact_polynomial_coefficient_parse",
    "formal_adjoint",
    "matrix_composition",
    "noncommutative_pbw_reduction",
    "support_local_order_audit",
)


@dataclass(frozen=True)
class VerifiedBergerPBWQ1:
    result_id: str
    retained_rows: int
    block_hashes: tuple[tuple[str, str], ...]
    pbw_term_count: int
    maximum_differential_order: int


def validate_retained_q1_receipt(payload: dict[str, Any]) -> VerifiedBergerPBWQ1:
    expected = build_certificate()
    if payload != expected:
        raise ValueError("retained Berger q1 receipt does not reproduce")
    if (
        payload["nd2_gate"]["physical_execution_authorized"] is not False
        or payload["coverage"]["complete_classical_contraction"] is not False
    ):
        raise ValueError("retained Berger q1 receipt crossed its fail-closed boundary")
    blocks = payload["operator_summary"]["blocks"]
    return VerifiedBergerPBWQ1(
        result_id=payload["result_id"],
        retained_rows=payload["coverage"]["retained_minimal_rows"],
        block_hashes=tuple(
            (name, blocks[name]["sha256"])
            for name in sorted(blocks)
        ),
        pbw_term_count=sum(block["pbw_term_count"] for block in blocks.values()),
        maximum_differential_order=max(
            block["maximum_differential_order"] for block in blocks.values()
        ),
    )


def build_operator_backend_registry(
    *,
    repository_root: Path | None = None,
) -> OperatorBackendRegistry:
    root = (repository_root or ROOT).resolve()
    descriptor = OperatorBackendDescriptor.from_paths(
        backend_id=BACKEND_ID,
        expression_schema_version=EXPRESSION_SCHEMA_VERSION,
        coefficient_domain=COEFFICIENT_DOMAIN,
        supported_arities=(1,),
        capabilities=CAPABILITIES,
        repository_root=root,
        implementation_paths=(
            TRANSFER_ROOT / "operator_backend_registry.py",
            Path(__file__).resolve(),
            TRANSFER_ROOT / "berger_retained_q1_import.py",
            TRANSFER_ROOT / "berger_retained_q1_import_certificate.py",
        ),
        assembly_mode="OPERATOR_VALIDATION_ONLY",
        nd2_physical_assembly_authorized=False,
    )
    registry = OperatorBackendRegistry(root)
    registry.register(descriptor, validate_retained_q1_receipt)
    return registry
