#!/usr/bin/env python3
"""Independent replay of the Candidate-B three-form obstruction.

This verifier does not import the producer.  It reconstructs the background
Euler residual, HT Hessian kernel, compact/ordinary de Rham ledger,
flux-multiplier current and Berger raw-D cohomology test directly from the
serialized certificate and frozen dependencies.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-candidate-b-unimodular-threeform-obstruction-v1.schema.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dense(record: dict[str, Any], symbols: dict[str, Any] | None = None) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(
            entry["coefficient"], locals=symbols or {}
        )
    return value


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    if (
        payload["result_id"]
        != "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1"
        or payload["result_state"] != "OBSTRUCTED"
        or payload["dependency_tags"]
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("Candidate-B identity or lifecycle drifted")

    for row in payload["dependencies"].values():
        path = ROOT / row["path"]
        dependency = json.loads(path.read_text())
        if (
            _sha(path) != row["sha256"]
            or dependency.get("result_id", dependency.get("schema"))
            != row["result_id"]
        ):
            raise AssertionError(f"Candidate-B dependency drift: {row['path']}")

    # Reconstruct the f(R)+lambda metric equation in the frozen orthonormal
    # cylinder frame.  Its trace-free part cannot depend on V0 or lambda.
    metric = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(0, 2, 2, 2)
    m2 = sp.Rational(1, 6)
    v0, multiplier = sp.symbols("V0 lambda_HT")
    f = m2 * 6 / 2 - v0 + multiplier
    euler = m2 * ricci / 2 - f * metric / 2
    trace = sum(metric[i, i] * euler[i, i] for i in range(4))
    tracefree = sp.simplify(euler - trace * metric / 4)
    expected = sp.diag(
        sp.Rational(1, 8),
        sp.Rational(1, 24),
        sp.Rational(1, 24),
        sp.Rational(1, 24),
    )
    if tracefree != expected:
        raise AssertionError("independent trace-free cylinder residual failed")
    serialized_tf = _dense(
        payload["unit_cylinder_background_obstruction"][
            "tracefree_Euler_matrix"
        ]
    )
    if serialized_tf != expected:
        raise AssertionError("serialized trace-free cylinder residual drifted")
    if payload["unit_cylinder_background_obstruction"][
        "simultaneous_equations_have_solution"
    ]:
        raise AssertionError("unit cylinder incorrectly put on shell")

    # Reconstruct the formally self-adjoint HT block over Q(D).
    d = sp.Symbol("D", commutative=True)
    expected_hessian = sp.Matrix([[0, 0, 2], [0, 0, d], [2, -d, 0]])
    hessian = _dense(
        payload["linearized_topological_block"]["Hessian"], {"D": d}
    )
    if hessian != expected_hessian:
        raise AssertionError("HT Hessian drifted")
    if hessian.T.xreplace({d: -d}) != hessian:
        raise AssertionError("HT formal self-adjointness failed")
    kernel = sp.Matrix([d / 2, 1, 0])
    if hessian.rank() != 2 or hessian * kernel != sp.zeros(3, 1):
        raise AssertionError("HT arbitrary-flux polynomial kernel failed")
    h0 = hessian.subs(d, 0)
    if h0.rank() != 2 or h0 * sp.Matrix([0, 1, 0]) != sp.zeros(3, 1):
        raise AssertionError("HT harmonic flux kernel failed")

    # Independent Kunneth ledger.  H*(R)=H0 and H*(S3)=H0+H3;
    # compact support on R shifts the S3 degrees by one.
    topology = payload["global_topology"]
    if topology["ordinary_de_Rham_betti_H0_to_H4"] != [1, 0, 0, 1, 0]:
        raise AssertionError("ordinary de Rham ledger failed")
    if topology["compact_support_betti_Hc0_to_Hc4"] != [0, 1, 0, 0, 1]:
        raise AssertionError("compact-support de Rham ledger failed")
    if not topology["no_local_Poincare_promotion"]:
        raise AssertionError("local Poincare lemma was overpromoted")

    # The global Lee-Wald pair is exact.  Raw D translates a by one
    # normalized spatial volume and therefore contracts Omega to d lambda.
    pairing = _dense(
        payload["linearized_topological_block"][
            "flux_multiplier_pairing"
        ]["Lee_Wald_matrix"]
    )
    if pairing != sp.Matrix([[0, 1], [-1, 0]]) or pairing.det() != 1:
        raise AssertionError("flux/multiplier current drifted")
    if sp.Matrix([[1, 0]]) * pairing != sp.Matrix([[0, 1]]):
        raise AssertionError("raw-D Hamiltonian contraction failed")

    # At the rational Berger fixture the spatial volume coefficient is
    # a^2 c=3 sqrt(10)/20 and the volume form generates H3(S3), so it is
    # not d of a global two-form.
    berger = payload["Berger_gate"]
    coefficient = sp.sympify(berger["normalized_spatial_volume_coefficient"])
    if coefficient != 3 * sp.sqrt(10) / 20 or coefficient <= 0:
        raise AssertionError("Berger volume coefficient drifted")
    if berger["small_gauge_compensator_exists"]:
        raise AssertionError("Berger H3 generator incorrectly made exact")
    if (
        berger["compatibility_status"]
        != "FAIL_WITHOUT_NEW_GLOBAL_SUPERSELECTION_OR_GAUGE"
    ):
        raise AssertionError("Berger gate overpromoted")

    gates = {row["gate"]: row for row in payload["seven_gate_disposition"]}
    if len(gates) != 7 or gates[2]["status"] != "FAIL" or gates[3]["status"] != "FAIL":
        raise AssertionError("Candidate-B terminal gates drifted")
    flags = payload["claim_flags"]
    forbidden_true = (
        "CANDIDATE_B_FULL_CAUSAL_PARENT",
        "DRESSED_TRACE_CONTRACTED",
        "GLOBAL_FLUX_CONTROLLED_WITHOUT_EXTRA_DATA",
        "UNIT_CYLINDER_BACKGROUND_ON_SHELL",
        "BERGER_RAW_D_PRESERVED",
        "HADAMARD_STATE",
        "ANOMALY_OR_QME",
        "PARTICLE_SCATTERING_UNITARITY",
    )
    if any(flags[name] for name in forbidden_true):
        raise AssertionError("Candidate-B forbidden promotion")


if __name__ == "__main__":
    verify()
    print(
        "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1 "
        "INDEPENDENT REPLAY: PASS"
    )
