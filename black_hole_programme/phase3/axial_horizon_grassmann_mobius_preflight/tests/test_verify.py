from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from black_hole_programme.phase3.axial_horizon_grassmann_mobius_preflight.verify import (
    VerificationError,
    verify_certificate,
)


HERE = Path(__file__).resolve().parents[1]


def load() -> tuple[dict, str, dict, bytes]:
    cert = json.loads((HERE / "certificate.json").read_text())
    source = (HERE / "mobius_first_shell.forge").read_text()
    metadata_bytes = (HERE / "source_metadata.json").read_bytes()
    return cert, source, json.loads(metadata_bytes), metadata_bytes


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


def test_wrong_left_solve_mutation_refuses() -> None:
    cert, source, metadata, _ = load()
    source = source.replace(
        "let solved:HmResult=hm_right_solve(n.value,m.value);",
        "let solved:HmResult=hm_right_solve(m.value,n.value);",
        1,
    )
    metadata_bytes = rehash(cert, source, metadata)
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_drop_phi_ij_z_mutation_refuses() -> None:
    cert, source, metadata, _ = load()
    source = source.replace(
        "let m0:IvAffineResult=ivam_add_checked(pii,a.value);",
        "let m0:IvAffineResult=ivam_add_checked(pii,z);",
        1,
    )
    metadata_bytes = rehash(cert, source, metadata)
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_wrong_row_crosswalk_mutation_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    cert = copy.deepcopy(cert)
    cert["method"]["complex_chart"]["pivot_real_block_rows"] = [1, 2, 4, 7, 8, 10]
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_generator_mutation_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    cert = copy.deepcopy(cert)
    cert["method"]["generator"] = 7316
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_gauge_invariance_mutation_refuses_on_pass() -> None:
    cert, source, metadata, metadata_bytes = load()
    if cert["status"] != "PREFLIGHT_PASS":
        pytest.skip("shortfall certificate has no promoted gauge gate")
    cert = copy.deepcopy(cert)
    cert["gates"]["column_gauge_invariance"] = False
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_omit_rebase_mutation_refuses() -> None:
    cert, source, metadata, _ = load()
    source = source.replace(
        "let m:IvAffineResult=ivam_rebase_dyadic(m0.value,128);",
        "let m:IvAffineResult=m0;",
        1,
    )
    metadata_bytes = rehash(cert, source, metadata)
    with pytest.raises(VerificationError):
        verify_certificate(cert, source, metadata, metadata_bytes)


def test_source_hash_mutation_refuses() -> None:
    cert, source, metadata, metadata_bytes = load()
    with pytest.raises(VerificationError):
        verify_certificate(cert, source + "\n", metadata, metadata_bytes)
