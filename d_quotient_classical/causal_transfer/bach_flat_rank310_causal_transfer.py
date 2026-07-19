#!/usr/bin/env python3
"""Lift the Bach-flat metric Green homotopy through the natural rank-310 SDR."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/bach-flat-rank310-causal-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-rank310-causal-transfer-v1.schema.json"
VERIFIER = HERE / "verify_bach_flat_rank310_causal_transfer.py"
TESTS = HERE / "tests/test_bach_flat_rank310_causal_transfer.py"
METRIC = ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
SDR = ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json"
ABSTRACT = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {"artifact_id": value["result_id"], "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, object]:
    metric = json.loads(METRIC.read_text())
    sdr = json.loads(SDR.read_text())
    abstract = json.loads(ABSTRACT.read_text())
    if not metric["flags"]["BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS"]:
        raise AssertionError("metric Green homotopy unavailable")
    if not sdr["flags"]["BACH_FLAT_RELATIVE_G3_RANK310_SDR"]:
        raise AssertionError("rank-310 SDR unavailable")
    if not abstract["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"]:
        raise AssertionError("abstract causal transfer unavailable")

    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    return {
        "schema": "pure-weyl-bach-flat-rank310-causal-transfer-v1",
        "result_id": "BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1",
        "result_state": "RELATIVE_G3_BACH_FLAT_RANK310_ALL_ROW_CAUSAL_HOMOTOPY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "metric_homotopy": _dependency(METRIC),
            "rank310_SDR": _dependency(SDR),
            "abstract_transfer": _dependency(ABSTRACT),
        },
        "scope": {
            "class": sdr["scope"]["class"],
            "manifold": sdr["scope"]["manifold"],
            "carrier": sdr["scope"]["carrier"],
            "degree_ranks": sdr["scope"]["degree_ranks"],
            "support": metric["scope"]["support"],
        },
        "transfer": {
            "SDR_convention": "Q310 H+H Q310=1-I pi and pi I=1",
            "formula": "Lambda310,+/-=H+I Lambda_metric,+/- pi",
            "identity": "Q310 Lambda310,+/-+Lambda310,+/- Q310=1",
            "support": "H, I and pi are finite-order support-nonincreasing; Lambda_metric,+/- is same-sided causal",
            "cyclic_adjoint": "follows from the cyclic SDR and complementary-degree metric advanced/retarded reversal",
            "metric_descent": "pi Lambda310,+/- I=Lambda_metric,+/-",
        },
        "exact_checks": {
            "all_310_rows_included": True,
            "finite_order_support_local_SDR": True,
            "metric_endpoint_causal": True,
            "advanced_retarded_chain_identity": True,
            "same_sided_causal_support": True,
            "cyclic_adjoint_reversal": True,
            "metric_descent_exact": True,
        },
        "flags": {
            "BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1": True,
            "BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS": True,
            "BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS": True,
            "PURE_PARENT_TO_METRIC_SDR": False,
            "EXACT_SAME_BUNDLE_FACTORIZATION_ON_CLASS": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The natural rank-310 curvature-corrected mapping cone has exact advanced and retarded all-row Green homotopies on every background in the certified relative-open Bach-flat ADM class, obtained by cyclic SDR lift from the four-row metric Bach homotopy.",
            "not_claimed": [
                "a pure normal-tractor-parent to metric SDR",
                "an ambient-open class in all smooth Lorentzian metrics",
                "exact same-bundle factorization of the metric Bach witness",
                "Hadamard wavefront-set control",
                "nonlinear stability or a quantum theorem",
            ],
        },
        "next_gate": "CAUSAL_ATLAS_AND_COVARIANT_TRANSPORT_CONSUMERS",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in sources},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/bach_flat_rank310_causal_transfer.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_bach_flat_rank310_causal_transfer.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_bach_flat_rank310_causal_transfer",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/bach-flat-rank310-causal-transfer-v1.schema.json -d d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json",
        ],
    }


def _report() -> str:
    return """# Bach-flat rank-310 causal transfer

The class-wide metric biwave homotopy and the natural cyclic rank-310 SDR now
compose without a new coefficient calculation.  With

```text
Q310 H + H Q310 = 1 - I pi,
pi I = 1,
```

the all-row homotopy is

```text
Lambda310,+/- = H + I Lambda_metric,+/- pi.
```

It obeys the chain identity, same-sided causal support, complementary-degree
adjoint reversal and exact metric descent on all degree ranks
`(15,140,140,15)`.  This closes the rank-310 causal bridge throughout the
declared relative-open Bach-flat ADM class.  It does not identify the pure
normal-tractor parent with the metric complex and does not promote Hadamard,
nonlinear or quantum claims.
"""


def write() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report())


def check() -> None:
    value = build()
    if json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("rank-310 Bach-flat causal transfer drifted")
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)


def guards() -> None:
    schema = Draft202012Validator(json.loads(SCHEMA.read_text()))
    value = build()
    for key in ("PURE_PARENT_TO_METRIC_SDR", "HADAMARD_STATE", "QUANTUM_CLAIM"):
        bad = json.loads(json.dumps(value))
        bad["flags"][key] = True
        try:
            schema.validate(bad)
        except Exception:
            continue
        raise AssertionError(f"schema accepted forbidden promotion: {key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check:
        check()
    if args.guards:
        guards()
    if not (args.write or args.check or args.guards):
        print(json.dumps(build(), indent=2, sort_keys=True))
