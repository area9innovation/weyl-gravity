"""Independent verifier for the polar cyclic-BV/residual obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-polar-ungauged-bv-residual-descent-obstruction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict[str, Any], *, verify_files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if verify_files:
        assert payload["schema_sha256"] == _sha256(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
        for record in payload["provenance"]["inputs"].values():
            path = ROOT / record["path"]
            imported = json.loads(path.read_text())
            assert record["sha256"] == _sha256(path)
            assert record["result_id"] == imported["result_id"]

    l = sp.symbols("lambda", positive=True)
    defect = sp.Matrix([[0, -3*l], [-sp.Rational(3, 2), 0]])
    assert defect**2 == sp.Rational(9, 2)*l*sp.eye(2)
    assert sp.factor(defect.det()) == -sp.Rational(9, 2)*l
    assert payload["first_exact_obstruction"]["cyclic_defect_D_equals_R_minus_I"] == [["0", "-3*lambda"], ["-3/2", "0"]]
    assert payload["first_exact_obstruction"]["rank_for_every_physical_lambda_ell_at_least_2"] == 2

    ledger = {row["scope"]: row for row in payload["endpoint_ledger"]}
    assert ledger["generic polar"]["cyclic_identity_map"] == "OBSTRUCTED"
    assert ledger["exceptional polar"]["ell"] == 1
    assert ledger["polar nonzero Fourier"]["relative_operator"] == "empty physical solution quotient"
    assert ledger["homogeneous global"]["relative_operator"] == "I+N, N^2=0, rank(N)=2"
    assert ledger["axial twist endpoint"]["relative_operator"] == "-2*I on each position/velocity pair"
    assert "does not kill" in ledger["finite U(1) winding"]["residual_verdict"]
    assert ledger["asymptotic or exterior boundary"]["ungauged_chain"] == "NO_CERTIFIED_MAP"

    authority = payload["global_residual_authority"]
    assert authority["absolute_stabilizer_gauge_quotient"] == "NOT_AUTHORIZED"
    assert authority["universal_presymplectic_nullity"] is False
    assert authority["final_residual_cohomology_dimensions"] == "NO_CERTIFIED_MAP"
    assert payload["charge_and_large_gauge"]["electric_tangent_Q_e"].startswith("retained")
    assert "does not gauge-delete" in payload["charge_and_large_gauge"]["Wilson_line_W_x"]
    assert payload["classification"]["strict_identity_cyclic_BV_lift_exists"] is False
    assert payload["classification"]["final_residual_descent_certified"] is False
    assert payload["classification"]["causal_particle_or_quantum_claim"] is False


def verify_certificate() -> None:
    verify_payload(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    verify_certificate()
