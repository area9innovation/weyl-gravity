#!/usr/bin/env python3
"""Independent verifier for the validated-connection substrate obstruction."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

import jsonschema
import numpy as np
from scipy.integrate import solve_ivp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FORGE_ROOT = Path("/home/alstrup/area9/tango/forge")
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
REQUEST = ROOT / "planning/forge-requests/phase3-validated-connection-substrate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpx(v: dict[str, str]) -> complex:
    return complex(float(v["re"]), float(v["im"]))


def matrix(v: list[list[dict[str, str]]]) -> np.ndarray:
    return np.array([[cpx(x) for x in row] for row in v], dtype=np.complex128)


def public_functions(text: str) -> set[str]:
    return set(re.findall(r"\bpub\s+fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text))


def independent_flow() -> np.ndarray:
    omega = 3.0 / 5.0

    def f(r: float, flat: np.ndarray) -> np.ndarray:
        phi = flat.view(np.complex128).reshape(2, 2)
        c2 = r * r - 2 * r
        c1 = 2j * omega * r * r + 2 * r + 2
        c0 = 6j * omega * r - 6
        a = np.array([[0, 1], [-c0 / c2, -c1 / c2]], dtype=np.complex128)
        return (a @ phi).reshape(-1).view(np.float64)

    y0 = np.eye(2, dtype=np.complex128).reshape(-1).view(np.float64)
    sol = solve_ivp(f, (3.0, 4.0), y0, method="DOP853", rtol=2e-13, atol=2e-15)
    if not sol.success:
        raise AssertionError(sol.message)
    return sol.y[:, -1].copy().view(np.complex128).reshape(2, 2)


def verify(payload: dict) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    assert payload["result_token"] == "BLOCKED_MISSING_VALIDATED_COUPLED_FUNDAMENTAL_FLOW"

    # Re-open every pinned upstream source independently.
    for rel, rec in payload["provenance"]["forge_sources"].items():
        path = FORGE_ROOT / rel
        assert path.is_file(), rel
        assert sha256(path) == rec["sha256"], f"upstream drift: {rel}"

    ivode_text = (FORGE_ROOT / "lib/math/ivode.forge").read_text()
    ivmat_text = (FORGE_ROOT / "lib/math/ivmat.forge").read_text()
    completeness = (FORGE_ROOT / "lib/math/COMPLETENESS.md").read_text()
    ivode_fns = public_functions(ivode_text)
    ivmat_fns = public_functions(ivmat_text)
    assert {"ode_step", "ode_integrate"} <= ivode_fns
    assert {"ivm_mul", "ivm_solve_certified"} <= ivmat_fns
    assert "fn(Iv, Iv) -> Iv" in ivode_text
    forbidden_present = {
        "ode_integrate_vec", "ode_fundamental_matrix", "ode_integrate_matrix",
        "ivode_vector", "ivode_bvp", "ode_multiple_shooting",
    } & ivode_fns
    assert not forbidden_present, forbidden_present
    normalized_completeness = " ".join(completeness.split())
    assert "validated boundary-value ODE integration" in normalized_completeness
    assert "certified series-truncation error bounds" in normalized_completeness

    caps = payload["landed_capabilities"]
    assert caps["scalar_validated_ivp"]["available"] is True
    assert caps["interval_matrix_algebra"]["available"] is True
    assert caps["coupled_vector_validated_ivp"]["available"] is False
    assert caps["validated_fundamental_matrix"]["available"] is False

    # Independent DOP853 calculation checks that the producer actually exercised
    # the declared axial ODE.  This is corroboration only; both are explicitly
    # uncontrolled numerical rails and neither is promoted to an enclosure.
    reported = matrix(payload["uncontrolled_pilot"]["fundamental_matrix_n1024"])
    independent = independent_flow()
    assert np.max(np.abs(reported - independent)) < 2e-10
    defects = [float(payload["uncontrolled_pilot"]["current_defect_max"][str(n)])
               for n in (256, 512, 1024)]
    assert defects[0] > defects[1] > defects[2] > 0
    assert defects[0] / defects[1] > 12 and defects[1] / defects[2] > 12
    assert payload["rounded_output_counterexample"]["same_printed_matrix"] is True
    assert float(payload["rounded_output_counterexample"]["normalized_current_defect_max"]) < 1e-60
    assert float(payload["rounded_output_counterexample"]["mutated_current_defect_max"]) > 1e-17

    request = json.loads(REQUEST.read_text())
    assert request["id"] == "sf:forge-request/phase3-validated-connection-substrate"
    assert request["body"]["state"] == "REQUESTED"
    stop = request["body"]["stop_condition"]
    assert "fundamental-matrix" in stop and "wrapping" in stop
    assert "finite nonsingular" in stop

    flags = payload["claim_flags"]
    assert flags["validated_fundamental_matrix_enclosed"] is False
    assert flags["current_conservation_defect_enclosed"] is False
    assert flags["scattering_claim"] is False


def mutation_test(payload: dict) -> None:
    cases = []
    m1 = copy.deepcopy(payload)
    m1["claim_flags"]["validated_fundamental_matrix_enclosed"] = True
    cases.append(m1)
    m2 = copy.deepcopy(payload)
    m2["result_token"] = "VALIDATED_CONNECTION_CERTIFIED"
    cases.append(m2)
    m3 = copy.deepcopy(payload)
    m3["rounded_output_counterexample"]["same_printed_matrix"] = False
    cases.append(m3)
    rejected = 0
    for case in cases:
        try:
            verify(case)
        except Exception:
            rejected += 1
    assert rejected == len(cases), f"mutation survivors: {len(cases)-rejected}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test-mutation", action="store_true")
    args = ap.parse_args()
    payload = json.loads(CERT.read_text())
    verify(payload)
    if args.self_test_mutation:
        mutation_test(payload)
        print("PASS 3/3 decisive mutations rejected")
    else:
        print("PASS independent substrate/API, axial-flow and claim-boundary verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
