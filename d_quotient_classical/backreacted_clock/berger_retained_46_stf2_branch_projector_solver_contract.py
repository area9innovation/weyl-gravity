#!/usr/bin/env python3
"""Freeze the exact rank-46 STF2 branch-projector solver contract."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
OBSTRUCTION = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-46-stf2-branch-projector-solver-contract.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-branch-projector-solver-contract-v1.schema.json"
VERIFIER = HERE / "verify_berger_retained_46_stf2_branch_projector_solver_contract.py"
TESTS = HERE / "tests/test_berger_retained_46_stf2_branch_projector_solver_contract.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _validate_inputs(carrier: dict, obstruction: dict) -> dict[str, bool]:
    if (
        carrier.get("result_state")
        != "CERTIFIED_CYCLIC_GRAPH_CARRIER_PROJECTOR_OPEN"
        or carrier.get("carrier", {}).get("total_rows") != 46
        or carrier.get("carrier", {}).get("degree_ranks")
        != {"-1": 4, "0": 19, "1": 19, "2": 4}
        or not all(carrier.get("exact_checks", {}).values())
        or carrier.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True
        or carrier.get("flags", {}).get("CANONICAL_BRANCH_PROJECTOR_CERTIFIED")
        is not False
    ):
        raise ValueError("rank-46 carrier boundary drifted")
    artifacts = carrier.get("artifacts", {})
    for name in ("q1_46", "omega_46", "graph_shear_U_46", "graph_shear_U_46_inverse"):
        record = artifacts.get(name, {})
        path = ROOT / record.get("path", "")
        if record.get("shape") != [46, 46] or not path.is_file():
            raise ValueError(f"rank-46 solver artifact missing: {name}")
        if _sha256(path) != record.get("sha256"):
            raise ValueError(f"rank-46 solver artifact drifted: {name}")
    if (
        obstruction.get("result_state")
        != "NORMALIZED_LOCAL_PROJECTOR_OBSTRUCTION_CANONICAL_SAME_BUNDLE_SCOPE"
        or obstruction.get("smallest_carrier_enlargement_required", {})
        .get("smallest_natural_support_local_candidate", {})
        .get("candidate_retained_rank")
        != 46
    ):
        raise ValueError("rank-36 obstruction authority drifted")
    return {
        "rank_36_obstruction_imported": True,
        "rank_46_carrier_imported": True,
        "rank_46_q1_nilpotent": True,
        "rank_46_pairing_cyclic": True,
        "rank_46_graph_SDR_exact": True,
        "graph_shear_exported": True,
        "graph_shear_inverse_exact": True,
        "graph_shear_cyclic": True,
        "branch_projector_still_open": True,
    }


def build() -> dict:
    carrier = _load(CARRIER)
    obstruction = _load(OBSTRUCTION)
    checks = _validate_inputs(carrier, obstruction)
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-retained-46-stf2-branch-projector-solver-contract-v1",
        "result_id": "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1",
        "result_state": "SOLVER_CONTRACT_FROZEN_PROJECTOR_VERDICT_NOT_RUN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "rank_36_projector_obstruction": _dependency(OBSTRUCTION, obstruction),
            "rank_46_STF2_graph_carrier": _dependency(CARRIER, carrier),
        },
        "exact_import_checks": checks,
        "row_partition": {
            "gravity_ghost_rows": [0, 1, 2],
            "gravity_configuration_rows": list(range(3, 18)),
            "gravity_equation_rows": list(range(18, 33)),
            "gravity_ghost_dual_rows": [33, 34, 35],
            "fixed_Maxwell_spectator_rows": list(range(36, 46)),
        },
        "declared_graph_ansatz": {
            "independent_unknown": "constant 15x15 Einstein projector block P_E_graph on (h_hat,Y_STF)",
            "independent_coefficient_count_over_Q_sqrt10": 225,
            "PBW_order_in_graph_coordinates": 0,
            "export_formula": "P_E_export=U_46 P_E_graph U_46_inverse with graded chain/cyclic completion",
            "maximum_exported_PBW_order": 2,
            "derived_blocks": [
                "degree-one block from the typed cyclic adjoint equation",
                "ghost and ghost-dual blocks from q1 intertwining and cyclicity",
                "extra-Weyl projector P_X=P_gravity-P_E",
            ],
            "forbidden_shortcuts": [
                "unrestricted 46x46 polydifferential coefficient search",
                "inverse Laplacian or inverse curl",
                "TT or helicity projector",
                "Green operator",
                "mode truncation or numerical pseudoinverse",
                "synthetic branch basis substituted for a failed exact solve",
            ],
            "scope": "binary verdict for the declared order-zero graph-coordinate projector ansatz; broader filtered or mapping-cylinder carriers remain separate follow-ups",
        },
        "principal_symbol_anchor": {
            "Einstein_image": "rough tensor-wave layer with Y_STF=0 at principal symbol",
            "extra_Weyl_image": "complementary generalized-wave layer carried by Y_STF",
            "real_physical_helicity_rank_each": 2,
            "topological_odd_direction": "excluded deformation/vertex class, not a dynamical branch",
        },
        "exact_acceptance_equations": [
            "P_E^2=P_E",
            "P_X^2=P_X",
            "P_E P_X=P_X P_E=0",
            "P_E+P_X=P_gravity",
            "P_M^2=P_M with P_M fixed on rows 36..45",
            "[q1_46,P_E]=[q1_46,P_X]=0",
            "P_E^dagger omega_46=omega_46 P_E",
            "P_X^dagger omega_46=omega_46 P_X",
            "rho P_E=P_E rho and rho P_X=P_X rho",
            "[K_Berger_46,P_E]=[K_Berger_46,P_X]=0",
            "all entries are finite-order support-local PBW operators over Q(sqrt(10))",
        ],
        "ordered_solver_stages": [
            {
                "stage": 0,
                "name": "INPUT_AND_GRAPH_COORDINATE_GATE",
                "failure_output": "INPUT_BLOCKED with the first missing content-addressed carrier object",
            },
            {
                "stage": 1,
                "name": "PRINCIPAL_SYMBOL_AND_IDEMPOTENCE",
                "failure_output": "normalized principal-symbol dual witness",
            },
            {
                "stage": 2,
                "name": "LOWER_ORDER_CHAIN_AND_CYCLIC_COMPLETION",
                "failure_output": "normalized exact PBW dual witness naming derivative order and field rows",
            },
            {
                "stage": 3,
                "name": "REAL_AND_K_BERGER_EQUIVARIANCE",
                "failure_output": "normalized reality or K-weight obstruction; no provisional projector promotion",
            },
            {
                "stage": 4,
                "name": "BINARY_VERDICT",
                "failure_output": "exact projector package or normalized scoped obstruction",
            },
        ],
        "required_success_payload": [
            "exact P_E and P_X matrices plus fixed P_M",
            "complete branch row, degree, parity, reality and K_Berger-weight ledgers",
            "all acceptance-equation replays and complementary rank ledger",
            "exact rank-46 K_Berger action and real structure used by the replay",
            "mutation rejections for idempotence, cyclicity, chain intertwining, graph shear and K weight",
            "explicit statement that q2/q3 lift and ell3 mixing remain false until separately materialized",
        ],
        "required_obstruction_payload": [
            "first failed solver stage and exact equation",
            "normalized dual functional evaluating the defect to one",
            "proof that the functional annihilates the complete declared ansatz image",
            "PBW derivative order, field rows, D/K weight and real content",
            "whether Einstein-like and extra-Weyl layers are coupled by the defect",
            "whether any negative kinetic direction is introduced (normally not inferred by this unary projector test)",
            "smallest missing carrier or ansatz enlargement",
            "precise REDUCED-MODE limitation",
        ],
        "mutation_contract": [
            "flip one graph-shear coefficient",
            "accept a non-idempotent projector",
            "break one typed cyclic-adjoint sign",
            "break one q1-intertwining coefficient",
            "assign one incompatible K_Berger weight",
        ],
        "claim_flags": {
            "SOLVER_CONTRACT_FROZEN": True,
            "RANK_46_CARRIER_IMPORTED": True,
            "GRAPH_SHEAR_EXPORTED": True,
            "PROJECTOR_SOLVE_RUN": False,
            "BRANCH_PROJECTOR_ACCEPTED": False,
            "NORMALIZED_PROJECTOR_OBSTRUCTION_FOUND": False,
            "Q2_Q3_LIFT_MATERIALIZED": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        "provenance": {
            "source_manifest": sources,
            "carrier_certificate_sha256": _sha256(CARRIER),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC object freezes the exact binary solver contract for the "
            "landed rank-46 STF2 cyclic graph carrier. It reduces the independent search to a "
            "constant 15x15 graph-coordinate block, with all exported order-two, dual, ghost and "
            "antifield entries derived and checked rather than independently fitted. It neither "
            "runs the solve nor asserts an Einstein-like/extra-Weyl projector, obstruction, "
            "nonlinear lift, branch mixing table, particle interpretation, QME result or quantum claim."
            " A negative verdict will be scoped to the order-zero graph-coordinate ansatz and will "
            "not rule out a broader filtered carrier, a Berger specialization of the curvature "
            "mapping cylinder, or a separately tagged REDUCED-MODE splitting. A positive algebraic "
            "candidate cannot be promoted until its real structure and K_Berger equivariance pass "
            "exactly, and it cannot be used for interaction mixing until q2 and q3 are materialized "
            "on the accepted branch carrier."
        ),
    }


def validate(value: dict) -> None:
    if value.get("result_state") != "SOLVER_CONTRACT_FROZEN_PROJECTOR_VERDICT_NOT_RUN":
        raise ValueError("solver-contract state drifted")
    if value.get("declared_graph_ansatz", {}).get(
        "independent_coefficient_count_over_Q_sqrt10"
    ) != 225:
        raise ValueError("solver-contract ansatz drifted")
    flags = value.get("claim_flags", {})
    if (
        flags.get("SOLVER_CONTRACT_FROZEN") is not True
        or flags.get("RANK_46_CARRIER_IMPORTED") is not True
        or flags.get("GRAPH_SHEAR_EXPORTED") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "PROJECTOR_SOLVE_RUN",
                "BRANCH_PROJECTOR_ACCEPTED",
                "NORMALIZED_PROJECTOR_OBSTRUCTION_FOUND",
                "Q2_Q3_LIFT_MATERIALIZED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("solver-contract claim boundary drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict) -> str:
    return """# Berger rank-46 STF2 branch-projector solver contract

The landed cyclic graph carrier is now a complete input to a scoped binary
projector calculation.  The independent ansatz is a constant `15 x 15`
Einstein block in graph coordinates: 225 coefficients over `Q(sqrt(10))`.
The exported projector is obtained with the exact cyclic graph shear and has
PBW order at most two.  Degree-one, ghost and ghost-dual entries are forced by
the typed cyclic-adjoint and `q1`-intertwining equations rather than fitted as
independent `46 x 46` operator blocks.

The solve is ordered: principal symbol/idempotence, lower-order chain and
cyclic completion, then real and `K_Berger` equivariance.  The result must be
either exact complementary Einstein-like/extra-Weyl projectors or a normalized
dual obstruction at the first failed stage.  A success still does not
authorize an `ell3` mixing table until the nonlinear lift is materialized.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check:
        if OUTPUT.read_text() != _render(value):
            raise ValueError("solver-contract certificate drifted")
        if REPORT.read_text() != _report(value):
            raise ValueError("solver-contract report drifted")
    if args.guards:
        for name in (
            "BRANCH_PROJECTOR_ACCEPTED",
            "NORMALIZED_PROJECTOR_OBSTRUCTION_FOUND",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][name] = True
            try:
                validate(mutant)
            except ValueError:
                continue
            raise ValueError(f"solver-contract overclaim mutation accepted: {name}")
    print("BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
