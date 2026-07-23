from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from black_hole_programme.phase3.axial_moving_lower_transition_preflight.verify import (
    VerificationError,
    verify_certificate,
)


HERE = Path(__file__).resolve().parents[1]


def load() -> tuple[dict, str, dict, bytes]:
    cert = json.loads((HERE / "certificate.json").read_text())
    source = (HERE / "moving_fixture.forge").read_text()
    metadata_bytes = (HERE / "source_metadata.json").read_bytes()
    metadata = json.loads(metadata_bytes)
    return cert, source, metadata, metadata_bytes


def rehash(cert: dict, source: str, metadata: dict) -> bytes:
    metadata["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    metadata_bytes = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()
    cert["provenance"]["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    cert["provenance"]["source_metadata_sha256"] = hashlib.sha256(
        metadata_bytes
    ).hexdigest()
    return metadata_bytes


def test_valid_certificate() -> None:
    cert, source, metadata, metadata_bytes = load()
    assert verify_certificate(cert, source, metadata, metadata_bytes)


def test_interleaved_extractor_mutation_refuses() -> None:
    cert, source, metadata, _ = load()
    source = source.replace(
        "let uc:IvAffineMat=ml_block_part(u,0);",
        "let uc:IvAffineMat=gc_affine_submatrix(u,0);",
        1,
    )
    metadata_bytes = rehash(cert, source, metadata)
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_drop_d1_wc_mutation_refuses() -> None:
    cert, source, metadata, _ = load()
    source = source.replace(
        "let d1wc:IvAffineResult=ivam_mul_checked(d1,wc0.value);",
        "let d1wc:IvAffineResult=ivam_mul_checked(d1,ivam_constant(7315,qm_new(8,8)));",
        1,
    )
    metadata_bytes = rehash(cert, source, metadata)
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_generator_mutation_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    cert = copy.deepcopy(cert)
    cert["method"]["generator"] = 7316
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_width_shortfall_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    cert = copy.deepcopy(cert)
    cert["result"]["piecewise_moving_lower_width"] = cert["result"][
        "baseline_unframed_lower_width"
    ]
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_source_hash_mutation_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    with pytest.raises(VerificationError):
        verify_certificate(cert, source + "\n", metadata, metadata_bytes)
