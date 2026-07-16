"""Exact D/adjoint preflight and fail-closed retained-Volterra contract."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

from transfer import berger_54_row_local_d_import as D_IMPORT
from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _is_zero,
    _load_record,
    _matrix_add,
    _multiply,
    _subtract,
)

from . import metric_lower_by_two_biwave_import as LOWER


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPANION_CERTIFICATE = (
    HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
)
D_IMPORT_CERTIFICATE = (
    ROOT / "quantum-weyl/transfer/certificates/BERGER_54_ROW_LOCAL_D_IMPORT.json"
)
CLASSICAL_RESULT_ID = "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT"
CLASSICAL_SCHEMA = "pure-weyl-berger-retained-biwave-volterra-resolvent-v1"
CLASSICAL_SCHEMA_PATH = (
    "d_quotient_classical/schema/"
    "berger-retained-biwave-volterra-resolvent-v1.schema.json"
)
CLASSICAL_COMMIT = "512545b781d4b0aff474bc5dc224890b246b070c"
CLASSICAL_CERTIFICATE = (
    "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT.json"
)
CLASSICAL_PRODUCER = (
    "d_quotient_classical/backreacted_clock/berger_retained_biwave_volterra_resolvent.py"
)
CLASSICAL_TEST = (
    "d_quotient_classical/backreacted_clock/tests/"
    "test_berger_retained_biwave_volterra_resolvent.py"
)
CLASSICAL_REPORT = (
    "d_quotient_classical/reports/berger-retained-biwave-volterra-resolvent.md"
)
CLASSICAL_NORMAL_FORM = (
    "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
)
CLASSICAL_CONTRACTION = (
    "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
)
CLASSICAL_RAW_TRANSPORT = (
    "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned retained Volterra artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned retained Volterra JSON is not an object: {relative}")
    return value


def _classical_artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _zero(rows: int, columns: int):
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _identity(rank: int):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = {(): sp.S.One}
    return result


def _negative(matrix):
    return [
        [
            {word: -coefficient for word, coefficient in entry.items()}
            for entry in row
        ]
        for row in matrix
    ]


def _embed(target, block, row_offset: int, column_offset: int) -> None:
    for row, values in enumerate(block):
        for column, operator in enumerate(values):
            target[row + row_offset][column + column_offset] = operator


def _block(matrix, rows: range, columns: range):
    return [[matrix[row][column] for column in columns] for row in rows]


def _commutes(left, right) -> bool:
    return _is_zero(_subtract(_multiply(left, right), _multiply(right, left)))


def _load_boundaries() -> tuple[dict[str, Any], dict[str, Any]]:
    companion = json.loads(COMPANION_CERTIFICATE.read_text())
    d_import = json.loads(D_IMPORT_CERTIFICATE.read_text())
    if (
        companion.get("result_id")
        != "BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT"
        or companion.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR"
        )
        is not True
        or companion.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"
        )
        is not False
        or companion.get("next_gate")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT"
    ):
        raise ValueError("retained companion boundary drifted")
    if (
        d_import.get("result_id") != "BERGER_54_ROW_LOCAL_D_ACTION_IMPORT"
        or d_import.get("result_state")
        != "COMPLETE_54_ROW_LOCAL_D_ACTION_IMPORTED_SUPPORT_LOCAL_Q2_BLOCKED"
        or d_import.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or d_import.get("independent_checks", {}).get("D_formally_skew_adjoint")
        is not True
    ):
        raise ValueError("Berger D-import boundary drifted")
    return companion, d_import


def _classical_path_exists(relative: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def _audit_volterra_source(source: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        "claim_boundary",
        "claim_status",
        "companion_graph_sdr",
        "construction_dags",
        "dependency_refs",
        "dependency_tags",
        "exact_checks",
        "flags",
        "next_gate",
        "result_id",
        "retained_identification",
        "schema",
        "setting_id",
        "volterra_theorem",
        "zero_mode_policy",
    }
    if set(source) != expected_fields:
        raise ValueError("retained Volterra source fields drifted")
    if (
        source.get("schema") != CLASSICAL_SCHEMA
        or source.get("result_id") != CLASSICAL_RESULT_ID
        or source.get("setting_id") != LOWER.SETTING_ID
        or source.get("claim_status")
        != "CERTIFIED_RETAINED_METRIC_CAUSAL_GREEN_OPERATORS_26_ROW_ASSEMBLY_OPEN"
        or source.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"
    ):
        raise ValueError("retained Volterra source identity drifted")

    expected_checks = {
        "advanced_resolvent_converges",
        "both_same_sided_inverse_identities",
        "companion_graph_SDR_exact",
        "formal_adjoint_reversal",
        "metric_causal_support",
        "metric_graph_pullback_both_inverses",
        "no_spatial_projector",
        "retained_metric_projection_exact",
        "retarded_resolvent_converges",
        "triangular_base_green_formula_exact",
        "volterra_factorial_bound_closes_in_graded_energy",
    }
    if set(source.get("exact_checks", {})) != expected_checks or not all(
        value is True for value in source["exact_checks"].values()
    ):
        raise ValueError("retained Volterra exact-check ledger drifted")
    if source.get("flags") != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_CAUSAL_D_CARTAN": False,
        "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": True,
        "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
        "BERGER_RETAINED_METRIC_GREEN_OPERATORS": True,
    }:
        raise ValueError("retained Volterra lifecycle boundary drifted")
    expected_dependencies = {}
    for name, relative in (
        ("metric_normal_form", CLASSICAL_NORMAL_FORM),
        ("minimal_clock_contraction", CLASSICAL_CONTRACTION),
        ("raw_witness_transport", CLASSICAL_RAW_TRANSPORT),
    ):
        dependency = _git_json(relative)
        expected_dependencies[name] = {
            "result_id": dependency["result_id"],
            "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
        }
    if source.get("dependency_refs") != expected_dependencies:
        raise ValueError("retained Volterra dependency hashes drifted")

    graph = source.get("companion_graph_sdr", {})
    if (
        set(graph.get("exact_checks", {}))
        != {"C_i_sol", "p_sol_i_sol", "p_src_C", "p_src_i_src", "solution_retract", "source_retract"}
        or not all(graph["exact_checks"].values())
        or graph.get("operator") != "C20=[[Box_2,-I10],[V_2,Box_2]]"
        or graph.get("solution_inclusion") != "i_sol(h)=(h,Box_2 h)"
        or graph.get("source_inclusion") != "i_src(f)=(0,f)"
    ):
        raise ValueError("retained Volterra graph-SDR boundary drifted")

    theorem = source.get("volterra_theorem", {})
    expected_theorem_fields = {
        "adjoint_identity",
        "base_green",
        "both_inverse_identities",
        "convergence",
        "finite_slab_bound",
        "globalization",
        "graded_energy_spaces",
        "metric_inverse_identities",
        "metric_pullback",
        "order_zero_perturbation",
        "support",
        "triangular_base",
    }
    if (
        set(theorem) != expected_theorem_fields
        or theorem.get("finite_slab_bound")
        != "norm((G_C0,pm N)^n)<=C_T^n/n! on every compact causal slab"
        or theorem.get("both_inverse_identities")
        != ["C20 G_C20,pm=I", "G_C20,pm C20=I"]
        or theorem.get("metric_inverse_identities")
        != ["A10 G_A10,pm=I", "G_A10,pm A10=I"]
    ):
        raise ValueError("retained Volterra analytic theorem ledger drifted")
    if source.get("zero_mode_policy") != {
        "inverse_spatial_laplacian": False,
        "massless_zero_modes": "included in the causal Cauchy evolution of Box_2",
        "spatial_mode_projector": False,
    }:
        raise ValueError("retained Volterra zero-mode policy drifted")

    dags = source.get("construction_dags", {})
    conflated_resolvents = True
    for name, sign in (("advanced", "+"), ("retarded", "-")):
        dag = dags.get(name, {})
        nodes = dag.get("nodes", [])
        if dag.get("sign") != sign or [node.get("id") for node in nodes] != [
            f"G_Box2_{sign}",
            f"G_C0_{sign}",
            "N",
            f"R_{sign}",
            f"G_C20_{sign}",
            f"G_A10_{sign}",
        ]:
            raise ValueError(f"retained Volterra {name} construction DAG drifted")
        resolvent = nodes[3]
        conflated_resolvents &= (
            resolvent.get("formula") == f"sum_(n>=0)(-G_C0_{sign} N)^n"
            and resolvent.get("equivalent_formula")
            == f"sum_(n>=0)(-N G_C0_{sign})^n"
        )

    allowed_tags = {
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL",
    }
    defects = [
        {
            "defect_id": "UNDECLARED_DEPENDENCY_TAG",
            "observed": source.get("dependency_tags"),
            "required": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "repair": "remove FUNCTIONAL-ANALYTIC and encode analytic hypotheses under LORENTZIAN-CAUSAL",
        },
        {
            "defect_id": "MISSING_STRICT_SOURCE_SCHEMA",
            "observed": "ABSENT_AT_PINNED_COMMIT",
            "required": CLASSICAL_SCHEMA_PATH,
            "repair": "add a strict Draft 2020-12 schema with additionalProperties=false",
        },
        {
            "defect_id": "CONFLATED_SOURCE_AND_SOLUTION_RESOLVENTS",
            "observed": "one R_pm node equates sum(-G0 N)^n with sum(-N G0)^n",
            "required": "R_sol=(I+G0 N)^-1 and R_src=(I+N G0)^-1 as distinct endomorphisms",
            "repair": "state G=R_sol G0=G0 R_src and prove convergence for both sides",
        },
        {
            "defect_id": "MALFORMED_FORMAL_ADJOINT_IDENTITY",
            "observed": theorem.get("adjoint_identity"),
            "required": "(G_A,+)^sharp=G_(A^sharp),-; simplify only after proving A=A^sharp in the declared pairing",
            "repair": "bind the metric/antifield pairing and record the correctly typed adjoint reversal",
        },
        {
            "defect_id": "UNREFERENCED_ANALYTIC_BOOLEAN_ASSERTIONS",
            "observed": sorted(source.get("exact_checks", {})),
            "required": "proof-artifact references for convergence, support, inverse, and adjoint claims",
            "repair": "replace bare true values by theorem/proof artifacts and independently checkable hypotheses",
        },
        {
            "defect_id": "MISSING_SOURCE_PROVENANCE_AND_VERIFICATION_RECEIPT",
            "observed": "no source manifest, immutable producer hashes, commands, or elapsed-time receipt",
            "required": "content-addressed source manifest and scoped verification receipt",
            "repair": "record certificate, schema, producer, verifier, tests, report, commands, and timings",
        },
        {
            "defect_id": "SOURCE_SIDE_FACTORIAL_BOUND_NOT_STATED",
            "observed": theorem.get("finite_slab_bound"),
            "required": "bounds for both (G0 N)^n and (N G0)^n on their respective spaces",
            "repair": "state domain/codomain-correct two-sided Volterra estimates",
        },
        {
            "defect_id": "GRADED_ENERGY_MAPPING_UNDERSPECIFIED",
            "observed": theorem.get("graded_energy_spaces"),
            "required": "precise slab spaces, time regularity, source/solution norms, coefficient bounds, and derivative mapping orders",
            "repair": "supply the energy proposition and hypotheses rather than a one-line description",
        },
    ]
    if set(source.get("dependency_tags", [])) <= allowed_tags:
        raise ValueError("expected invalid dependency-tag defect unexpectedly closed")
    if _classical_path_exists(CLASSICAL_SCHEMA_PATH):
        raise ValueError("expected missing source-schema defect unexpectedly closed")
    if not conflated_resolvents:
        raise ValueError("expected source/solution resolvent defect unexpectedly closed")
    if theorem.get("adjoint_identity") != "G_A10,+^sharp=G_A10^sharp,-":
        raise ValueError("expected malformed adjoint defect unexpectedly closed")
    return {
        "strict_top_level_fields": True,
        "identity_and_lifecycle": True,
        "dependency_hashes": True,
        "exact_check_ledger": True,
        "graph_SDR_boundary": True,
        "advanced_and_retarded_DAGs": True,
        "zero_mode_policy": True,
        "acceptance_status": "REJECTED_FAIL_CLOSED",
        "defects": defects,
    }


@lru_cache(maxsize=1)
def evaluate_readiness() -> dict[str, Any]:
    companion_boundary, d_boundary = _load_boundaries()
    volterra_source = _git_json(CLASSICAL_CERTIFICATE)
    source_audit = _audit_volterra_source(volterra_source)

    lower_source = LOWER._git_json(LOWER.CERTIFICATE)
    artifacts = lower_source["normal_form"]["artifacts"]
    wave = LOWER._load_artifact(
        artifacts["rough_tensor_wave"], "rough_tensor_wave"
    )
    remainder = LOWER._load_artifact(
        artifacts["lower_by_two_remainder"], "lower_by_two_remainder"
    )
    metric = _matrix_add(_multiply(wave, wave), remainder)

    d_source = D_IMPORT._git_json(D_IMPORT.CERTIFICATE_RELATIVE)
    d26 = _load_record(
        "retained_D_action", d_source["retained_D_action"]["matrix"], (26, 26)
    )
    d10 = _block(d26, range(3, 13), range(3, 13))
    expected_d10 = _zero(10, 10)
    for index in range(10):
        expected_d10[index][index] = {(0,): sp.S.One}
    d10_is_exact_e0 = d10 == expected_d10

    identity10 = _identity(10)
    companion = _zero(20, 20)
    _embed(companion, wave, 0, 0)
    _embed(companion, _negative(identity10), 0, 10)
    _embed(companion, remainder, 10, 0)
    _embed(companion, wave, 10, 10)
    d20 = _zero(20, 20)
    _embed(d20, d10, 0, 0)
    _embed(d20, d10, 10, 10)

    solution_inclusion = _zero(20, 10)
    _embed(solution_inclusion, identity10, 0, 0)
    _embed(solution_inclusion, wave, 10, 0)
    solution_projection = _zero(10, 20)
    _embed(solution_projection, identity10, 0, 0)
    source_inclusion = _zero(20, 10)
    _embed(source_inclusion, identity10, 10, 0)
    source_projection = _zero(10, 20)
    _embed(source_projection, wave, 0, 0)
    _embed(source_projection, identity10, 0, 10)
    graph_homotopy = _zero(20, 20)
    _embed(graph_homotopy, _negative(identity10), 10, 0)

    wave_sharp = _adjoint_transpose(wave)
    remainder_sharp = _adjoint_transpose(remainder)
    metric_sharp = _adjoint_transpose(metric)
    expected_metric_sharp = _matrix_add(
        _multiply(wave_sharp, wave_sharp), remainder_sharp
    )
    expected_companion_sharp = _zero(20, 20)
    _embed(expected_companion_sharp, wave_sharp, 0, 0)
    _embed(expected_companion_sharp, remainder_sharp, 0, 10)
    _embed(expected_companion_sharp, _negative(identity10), 10, 0)
    _embed(expected_companion_sharp, wave_sharp, 10, 10)

    checks = {
        "retained_metric_D10_is_diagonal_e0": d10_is_exact_e0,
        "D10_is_formally_skew_adjoint": _is_zero(
            _matrix_add(_adjoint_transpose(d10), d10)
        ),
        "D10_commutes_with_Box2": _commutes(d10, wave),
        "D10_commutes_with_V2": _commutes(d10, remainder),
        "D10_commutes_with_A10": _commutes(d10, metric),
        "D20_commutes_with_C20": _commutes(d20, companion),
        "D_equivariant_solution_inclusion": _is_zero(
            _subtract(
                _multiply(d20, solution_inclusion),
                _multiply(solution_inclusion, d10),
            )
        ),
        "D_equivariant_solution_projection": _is_zero(
            _subtract(
                _multiply(d10, solution_projection),
                _multiply(solution_projection, d20),
            )
        ),
        "D_equivariant_source_inclusion": _is_zero(
            _subtract(
                _multiply(d20, source_inclusion),
                _multiply(source_inclusion, d10),
            )
        ),
        "D_equivariant_source_projection": _is_zero(
            _subtract(
                _multiply(d10, source_projection),
                _multiply(source_projection, d20),
            )
        ),
        "D_equivariant_graph_homotopy": _commutes(d20, graph_homotopy),
        "A10_sharp_equals_Box2_sharp_squared_plus_V2_sharp": _is_zero(
            _subtract(metric_sharp, expected_metric_sharp)
        ),
        "C20_sharp_block_formula_exact": _is_zero(
            _subtract(_adjoint_transpose(companion), expected_companion_sharp)
        ),
        "D10_commutes_with_A10_sharp": _commutes(d10, metric_sharp),
        "D20_commutes_with_C20_sharp": _commutes(
            d20, expected_companion_sharp
        ),
    }
    if not all(checks.values()):
        raise ValueError("retained Volterra D/adjoint readiness check failed")

    result = {
        "schema": "quantum-weyl-berger-retained-biwave-volterra-import-readiness-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS",
        "result_state": "SOURCE_LANDED_REJECTED_ANALYTIC_CONTRACT_D_ADJOINT_GRAPH_READY",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_IMPORT_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": LOWER.SETTING_ID,
        "exact_compatibility": {
            "D10": "diag(e_0)_10",
            "D20": "diag(D10,D10)",
            "metric_operator": "A10=Box_2^2+V_2",
            "companion_operator": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "formal_adjoint_metric": "A10^sharp=(Box_2^sharp)^2+V_2^sharp",
            "formal_adjoint_companion": "C20^sharp=[[Box_2^sharp,V_2^sharp],[-I10,Box_2^sharp]]",
            "checks": checks,
        },
        "source_audit": {
            "status": "REJECTED_FAIL_CLOSED",
            "source_result_id": CLASSICAL_RESULT_ID,
            "source_schema_version": CLASSICAL_SCHEMA,
            "source_commit": CLASSICAL_COMMIT,
            "source_dependency_tags": volterra_source["dependency_tags"],
            "structural_checks": {
                key: value
                for key, value in source_audit.items()
                if key not in {"acceptance_status", "defects"}
            },
            "defects": source_audit["defects"],
            "blocked_claims": [
                "finite-slab factorial Volterra estimate in declared graded energy spaces",
                "advanced and retarded convergence in every declared Sobolev grade",
                "globalization by causal uniqueness",
                "closed causal-support passage to the limit",
                "both same-sided inverse identities for C20",
                "both inverse identities for the graph pullback G_A10,+/-",
                "formal-adjoint sign reversal for A10 and A10^sharp",
                "no inverse spatial Laplacian or spatial-mode projector",
            ],
        },
        "realization_policy": {
            "accepted_when_repaired": "RETAINED_BIWAVE_COMPANION_VOLTERRA_GRAPH_PULLBACK",
            "rejected_routes": {
                "RAW_CLOCK_RANK_ONE_WAVE_EXTENSION": "raw L13 carries an additional real characteristic and is not a metric-cone Green realization",
                "FULL_G13_ARBITRARY_SOURCE_METRIC_CONE": "incompatible with the certified raw principal-symbol obstruction",
                "PROJECT_RAW_L13_SOLUTIONS_TO_RETAINED_ROWS": "the raw extra polarization mixes metric and clock components; apply the BV SDR and construct the retained witness",
            },
        },
        "claim_flags": {
            "BERGER_RETAINED_BIWAVE_D_EQUIVARIANT": True,
            "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY": True,
            "BERGER_RETAINED_BIWAVE_COMPANION_CYCLIC_PAIRING": False,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_CAUSAL_D_CARTAN": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPAIR_CLASSICAL_BERGER_RETAINED_BIWAVE_VOLTERRA_CERTIFICATE",
        "provenance": {
            "dependencies": {
                "companion_preflight": {
                    "path": str(COMPANION_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(COMPANION_CERTIFICATE),
                    "result_id": companion_boundary["result_id"],
                },
                "D_import": {
                    "path": str(D_IMPORT_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(D_IMPORT_CERTIFICATE),
                    "result_id": d_boundary["result_id"],
                },
                "lower_by_two_classical": LOWER._artifact(LOWER.CERTIFICATE),
                "D_action_classical": D_IMPORT._artifact(
                    D_IMPORT.CERTIFICATE_RELATIVE
                ),
                "volterra_certificate_classical": _classical_artifact(
                    CLASSICAL_CERTIFICATE
                ),
                "volterra_producer_classical": _classical_artifact(
                    CLASSICAL_PRODUCER
                ),
                "volterra_test_classical": _classical_artifact(CLASSICAL_TEST),
                "volterra_report_classical": _classical_artifact(
                    CLASSICAL_REPORT
                ),
            }
        },
        "claim_boundary": (
            "Exact PBW arithmetic proves that the retained metric biwave, its "
            "twenty-row companion, both graph source/solution maps and their "
            "formal-adjoint operators are equivariant for D=e_0. This exact "
            "algebraic replay accompanies a pinned audit of the landed classical retained "
            "Volterra package. The analytic source is rejected fail-closed because its "
            "resolvents are type-conflated, its adjoint identity is malformed, its "
            "dependency vocabulary is invalid, and its analytic booleans lack strict "
            "schema/proof/provenance receipts. It does not import advanced or retarded "
            "metric Green operators, assemble the 26- or 54-row causal BV homotopy, "
            "prove causal D-Cartan, establish Hadamard data or make a quantum claim."
        ),
    }
    validate_readiness(result)
    return result


def validate_readiness(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS"
        or result.get("result_state")
        != "SOURCE_LANDED_REJECTED_ANALYTIC_CONTRACT_D_ADJOINT_GRAPH_READY"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "REPAIR_CLASSICAL_BERGER_RETAINED_BIWAVE_VOLTERRA_CERTIFICATE"
    ):
        raise ValueError("retained Volterra readiness identity drifted")
    if not all(
        result.get("exact_compatibility", {}).get("checks", {}).values()
    ):
        raise ValueError("retained Volterra readiness exact check dropped")
    receipt = result.get("source_audit", {})
    if (
        receipt.get("status") != "REJECTED_FAIL_CLOSED"
        or receipt.get("source_commit") != CLASSICAL_COMMIT
        or len(receipt.get("defects", [])) != 8
        or not all(receipt.get("structural_checks", {}).values())
    ):
        raise ValueError("classical Volterra source audit drifted")
    flags = result.get("claim_flags", {})
    expected_true = {
        "BERGER_RETAINED_BIWAVE_D_EQUIVARIANT",
        "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY",
    }
    if set(name for name, value in flags.items() if value is True) != expected_true:
        raise ValueError("retained Volterra lifecycle boundary drifted")
    rejected = result.get("realization_policy", {}).get("rejected_routes", {})
    if set(rejected) != {
        "RAW_CLOCK_RANK_ONE_WAVE_EXTENSION",
        "FULL_G13_ARBITRARY_SOURCE_METRIC_CONE",
        "PROJECT_RAW_L13_SOLUTIONS_TO_RETAINED_ROWS",
    }:
        raise ValueError("stale raw realization route was accepted")
