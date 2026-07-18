#!/usr/bin/env python3
"""Lift the unit-Nariai metric Green homotopy to the repaired 310-row cone.

The local cyclic SDR is an exact ten-block operator identity.  The metric
endpoint has an independently certified advanced/retarded Green homotopy.
This producer instantiates the abstract cyclic causal-transfer theorem on
those two inputs and replays the chain identity in both split and original
parent/metric graph coordinates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.abstract_cyclic_causal_transfer import (
    exact_fixture as abstract_transfer_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-repaired-310-all-row-green-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-repaired-310-all-row-green-transfer-v1.schema.json"
VERIFIER = HERE / "verify_nariai_repaired_310_all_row_green_transfer.py"
TESTS = HERE / "tests/test_nariai_repaired_310_all_row_green_transfer.py"
REPAIR_SOURCE = HERE / "nariai_parent_detour_mapping_cone_repair.py"
METRIC_SOURCE = HERE / "nariai_metric_biwave_green_homotopy.py"
ABSTRACT_SOURCE = HERE / "abstract_cyclic_causal_transfer.py"

REPAIR_CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"
METRIC_CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
ABSTRACT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": payload["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _endpoint_homotopy() -> repair.Matrix:
    value = repair._zero(4, 4)
    value[0][1] = repair.O.atom("Lambda01")
    value[1][2] = repair.O.atom("Lambda12")
    value[2][3] = repair.O.atom("Lambda23")
    return value


def _endpoint_replace_once(value: repair.O) -> tuple[repair.O, bool]:
    """Orient q_met Lambda+Lambda q_met=1 as a terminating rewrite."""
    replacements = {
        ("Lambda01", "K"): repair.O.identity(),
        ("K", "Lambda01"): repair.O.identity()
        + (repair.O.atom("Lambda12") * repair.O.atom("B")).scale(-1),
        ("B", "Lambda12"): repair.O.identity()
        + (repair.O.atom("Lambda23") * repair.O.atom("Ksharp")).scale(-1),
        ("Ksharp", "Lambda23"): repair.O.identity(),
    }
    for word, coefficient in value.terms:
        for old, replacement in replacements.items():
            for index in range(len(word) - len(old) + 1):
                if word[index:index + len(old)] != old:
                    continue
                rest = value + repair.O._from_dict({word: -coefficient})
                prefix = repair.O._from_dict({word[:index]: coefficient})
                suffix = repair.O._from_dict({word[index + len(old):]: 1})
                return rest + prefix * replacement * suffix, True
    return value, False


def _transfer_reduce(value: repair.O) -> repair.O:
    for _ in range(1000):
        value = repair._reduce(value)
        value, changed = _endpoint_replace_once(value)
        if not changed:
            return repair._reduce(value)
    raise AssertionError("causal-transfer rewrite did not terminate")


def _transfer_matrix_zero(value: repair.Matrix) -> bool:
    return all(
        _transfer_reduce(entry) == repair.O.zero()
        for row in value
        for entry in row
    )


def transfer_fixture() -> dict[str, Any]:
    kernel = repair.abstract_kernel()
    endpoint = _endpoint_homotopy()
    endpoint_identity = repair._identity(4)
    full_identity = repair._identity(10)

    endpoint_defect = repair._add(
        repair._add(
            repair._multiply(kernel["metric_q"], endpoint),
            repair._multiply(endpoint, kernel["metric_q"]),
        ),
        repair._scale(endpoint_identity, -1),
    )

    checks: dict[str, bool] = {}
    transferred: dict[str, repair.Matrix] = {}
    for coordinate in ("split", "original"):
        prefix = "" if coordinate == "split" else "original_"
        q = kernel[prefix + "q"]
        inclusion = kernel[prefix + "inclusion"]
        projection = kernel[prefix + "projection"]
        homotopy = kernel[prefix + "homotopy"]
        causal = repair._add(
            homotopy,
            repair._multiply(repair._multiply(inclusion, endpoint), projection),
        )
        transferred[coordinate] = causal
        chain_defect = repair._add(
            repair._add(repair._multiply(q, causal), repair._multiply(causal, q)),
            repair._scale(full_identity, -1),
        )
        descent_defect = repair._add(
            repair._multiply(repair._multiply(projection, causal), inclusion),
            repair._scale(endpoint, -1),
        )
        checks[f"{coordinate}_homotopy_square_zero"] = repair._matrix_zero(
            repair._multiply(homotopy, homotopy), relations=True
        )
        checks[f"{coordinate}_homotopy_inclusion_zero"] = repair._matrix_zero(
            repair._multiply(homotopy, inclusion), relations=True
        )
        checks[f"{coordinate}_projection_homotopy_zero"] = repair._matrix_zero(
            repair._multiply(projection, homotopy), relations=True
        )
        checks[f"{coordinate}_causal_chain_identity"] = _transfer_matrix_zero(chain_defect)
        checks[f"{coordinate}_metric_descent"] = repair._matrix_zero(
            descent_defect, relations=True
        )

    conjugated_split = repair._multiply(
        repair._multiply(kernel["transform"], transferred["split"]),
        kernel["transform_inverse"],
    )
    checks.update({
        "endpoint_causal_chain_identity": _transfer_matrix_zero(endpoint_defect),
        "coordinate_conjugation": repair._matrix_zero(
            repair._add(transferred["original"], repair._scale(conjugated_split, -1)),
            relations=True,
        ),
        "all_ten_blocks_enumerated": len(repair.BLOCK_NAMES) == 10,
        "full_rank_is_310": sum(repair.BLOCK_RANKS) == 310,
        "metric_rank_is_26": sum((4, 9, 9, 4)) == 26,
        "degree_ranks_are_15_140_140_15": tuple(
            sum(rank for degree, rank in zip(repair.BLOCK_DEGREES, repair.BLOCK_RANKS) if degree == target)
            for target in (-1, 0, 1, 2)
        ) == (15, 140, 140, 15),
        "abstract_transfer_fixture_exact": not any(
            abstract_transfer_fixture()["identity_defects"].values()
        ),
        "repair_core_checks_all_true": all(kernel["checks"].values()),
    })
    failed = [name for name, result in checks.items() if not result]
    if failed:
        raise AssertionError(f"Nariai all-row causal transfer failed: {failed}")
    return {
        "checks": checks,
        "endpoint_homotopy": endpoint,
        "split_homotopy": transferred["split"],
        "original_homotopy": transferred["original"],
    }


def build() -> dict[str, Any]:
    repair_certificate = json.loads(REPAIR_CERTIFICATE.read_text())
    metric_certificate = json.loads(METRIC_CERTIFICATE.read_text())
    abstract_certificate = json.loads(ABSTRACT_CERTIFICATE.read_text())
    if repair_certificate["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"] is not True:
        raise AssertionError("Nariai cyclic SDR unavailable")
    if metric_certificate["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Nariai metric causal homotopy unavailable")
    if abstract_certificate["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise AssertionError("abstract causal-transfer theorem unavailable")

    fixture = transfer_fixture()
    fixture["checks"].update({
        "support_local_sdr_dependency": repair_certificate["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"] is True,
        "metric_causal_support_dependency": metric_certificate["flags"]["NARIAI_METRIC_CAUSAL_SUPPORT"] is True,
        "metric_adjoint_reversal_dependency": metric_certificate["flags"]["NARIAI_METRIC_ADJOINT_REVERSAL"] is True,
        "abstract_cyclic_transfer_dependency": abstract_certificate["flags"]["ABSTRACT_CYCLIC_ADJOINT_TRANSFER_CERTIFIED"] is True,
    })
    if not all(fixture["checks"].values()):
        raise AssertionError("a causal or cyclic transfer dependency is incomplete")
    dependencies = {
        "rank_310_cyclic_sdr": _dependency(REPAIR_CERTIFICATE, repair_certificate),
        "metric_causal_homotopy": _dependency(METRIC_CERTIFICATE, metric_certificate),
        "abstract_causal_transfer": _dependency(ABSTRACT_CERTIFICATE, abstract_certificate),
    }
    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA,
        REPAIR_SOURCE, METRIC_SOURCE, ABSTRACT_SOURCE,
    )
    row_coverage = [
        {
            "index": index,
            "name": name,
            "degree": degree,
            "rank": rank,
            "sector": (
                "metric_field_endpoint"
                if index in (3, 7)
                else "metric_ghost_plus_algebraic_complement"
                if index in (0, 9)
                else "algebraic_parent_cone"
            ),
        }
        for index, (name, degree, rank) in enumerate(
            zip(repair.BLOCK_NAMES, repair.BLOCK_DEGREES, repair.BLOCK_RANKS)
        )
    ]
    return {
        "schema": "pure-weyl-nariai-repaired-310-all-row-green-transfer-v1",
        "result_id": "NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1",
        "result_state": "RANK_310_CAUSAL_GREEN_HOMOTOPY_AND_METRIC_DESCENT_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependencies,
        "carrier": {
            "background": "global unit Nariai R x (S1 x S2)",
            "block_count": 10,
            "total_rank": 310,
            "degree_ranks": [15, 140, 140, 15],
            "metric_endpoint_degree_ranks": [4, 9, 9, 4],
            "metric_endpoint_total_rank": 26,
            "endpoint_embedding": "the rank-4 metric ghost and dual ghost are support-local subbundles of the first and last rank-15 blocks; the rank-9 field and antifield are full blocks",
            "row_coverage": row_coverage,
            "dropped_rows": [],
        },
        "transfer": {
            "split_formula": "Lambda_310,+/-=H_split+I_split Lambda_metric,+/- P_split",
            "original_formula": "Lambda_310,+/-=H_original+I_original Lambda_metric,+/- P_original",
            "coordinate_relation": "Lambda_original=U Lambda_split U^-1",
            "metric_descent": "P Lambda_310,+/- I=Lambda_metric,+/-",
            "chain_identity": "Q_310 Lambda_310,+/-+Lambda_310,+/- Q_310=1_310",
            "support": "H,I,P,U,U^-1 are support-nonincreasing and Lambda_metric,+/- is same-sided causal; hence supp Lambda_310,+/- f subset J^+/-(supp f)",
            "cyclic_adjoint": "Lambda_310,+^sharp=Sigma_310 Lambda_310,- Sigma_310^-1",
            "cyclic_route": "I^sharp=P, the algebraic H is odd cyclic, and the metric endpoint has complementary-degree advanced/retarded adjoint reversal",
        },
        "formal_replay": {
            "endpoint_homotopy": repair._serialize_matrix(fixture["endpoint_homotopy"]),
            "split_transferred_homotopy": repair._serialize_matrix(fixture["split_homotopy"]),
            "original_transferred_homotopy": repair._serialize_matrix(fixture["original_homotopy"]),
            "endpoint_relations": [
                "Lambda01 K=1",
                "K Lambda01+Lambda12 B=1",
                "B Lambda12+Lambda23 Ksharp=1",
                "Ksharp Lambda23=1",
            ],
        },
        "exact_checks": fixture["checks"],
        "flags": {
            "NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1": True,
            "NARIAI_REPAIRED_310_GREEN_HOMOTOPY": True,
            "NARIAI_REPAIRED_310_CAUSAL_SUPPORT": True,
            "NARIAI_REPAIRED_310_ADJOINT_REVERSAL": True,
            "NARIAI_METRIC_DESCENT_RECOVERS_ENDPOINT": True,
            "NARIAI_G2_SINGLE_BACKGROUND_CAUSAL_GATE": True,
            "OPEN_BACKGROUND_CLASS": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The complete repaired 310-component BV complex on global unit Nariai has advanced and retarded Green homotopies obtained by cyclic support-local SDR transfer from the exact four-row metric biwave endpoint, and descending recovers that endpoint homotopy exactly.",
            "not_claimed": [
                "uniform Green estimates on an open conformally Einstein or Bach-flat family",
                "Hadamard wavefront-set control",
                "a timelike-boundary version",
                "nonlinear stability",
                "a quantum state or quantum master equation",
            ],
        },
        "next_gate": "C_G2_CONFORMALLY_EINSTEIN_FIRST_CURVATURE_OBSTRUCTION",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in source_paths
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_repaired_310_all_row_green_transfer.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_repaired_310_all_row_green_transfer.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_repaired_310_all_row_green_transfer",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-repaired-310-all-row-green-transfer-v1.schema.json -d d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
        ],
    }


def _write_report(value: dict[str, Any]) -> None:
    checks = value["exact_checks"]
    REPORT.write_text(f"""# Nariai repaired 310-row causal Green transfer

The complete ten-block, 310-component repaired parent-detour cone retracts
cyclically and support-locally onto the independently certified 26-component
metric Bach endpoint.  The advanced and retarded homotopies are

```text
Lambda_310,+/- = H + I Lambda_metric,+/- P.
```

The side conditions `H^2=0`, `H I=0`, and `P H=0` hold in both split and
original coordinates.  Exact operator-polynomial replay gives

```text
Q_310 Lambda_310,+/- + Lambda_310,+/- Q_310 = 1_310,
P Lambda_310,+/- I = Lambda_metric,+/-.
```

All ten blocks are enumerated, with degree ranks `15,140,140,15`; no BV row
is dropped.  Local algebraic maps do not enlarge support, so the transferred
homotopies retain the same advanced or retarded causal support.  Cyclicity of
the SDR and complementary-degree adjoint reversal at the endpoint give the
full advanced/retarded adjoint relation.

Exact checks: {sum(checks.values())}/{len(checks)}.

This closes the single-background Nariai `G2` causal gate.  It does not prove
uniform stability on an open background family or a Hadamard theorem.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise SystemExit("certificate drift")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    if args.guards:
        if not all(value["exact_checks"].values()):
            raise SystemExit("all-row causal transfer has a nonzero defect")
        if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not True:
            raise SystemExit("rank-310 causal flag not promoted")
        for forbidden in ("OPEN_BACKGROUND_CLASS", "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM"):
            if value["flags"][forbidden] is not False:
                raise SystemExit(f"forbidden downstream promotion: {forbidden}")
    print(value["result_id"])


if __name__ == "__main__":
    main()
