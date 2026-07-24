#!/usr/bin/env python3
"""Audit whether a resumable correlated horizon checkpoint still exists.

The existing checkpoint rail is a fixed-frequency complex-ball rail.  Its
radial Taylor coefficients are local temporaries and each accepted step is
collapsed back to a Cartesian list of ``acb`` balls.  This audit records that
representation boundary and emits the exact restart/export contract needed by
an affine/Taylor-model successor.  It does not reinterpret Cartesian balls as
correlated sets.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import textwrap
from pathlib import Path

from . import checkpoint_transport as transport
from . import pivot_switch as repair
from . import shared_remainder_multipanel_successor as successor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_RUN = HERE / "shared-remainder-multipanel-successor-run.json"
ADAPTIVE_RUN = HERE / "adaptive-chart-separation-run.json"
RUN = HERE / "correlated-affine-export-audit-run.json"

LEVELT = (
    HERE.parent / "axial_partial_jet_horizon_spin_one_levelt_v1" / "produce.py"
)
MOVING = (
    HERE.parent / "axial_partial_jet_horizon_moving_phase_v1" / "produce.py"
)

REQUIRED_CORRELATED_KEYS = {
    "omega_model",
    "dual_tau_state",
    "affine_generators",
    "shared_noise_domain",
    "residual_norm_ball",
    "radial_taylor_coefficients",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_ast(function) -> ast.AST:
    return ast.parse(textwrap.dedent(inspect.getsource(function)))


def called_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def string_constants(tree: ast.AST) -> set[str]:
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def checkpoint_has_correlated_export(payload: dict) -> bool:
    """Require the actual correlated payload, not a representation label."""
    correlated = payload.get("correlated_state")
    return isinstance(correlated, dict) and REQUIRED_CORRELATED_KEYS <= set(
        correlated
    )


def _list_return_annotation(function) -> str:
    return inspect.signature(function).return_annotation.__str__()


def compute() -> dict:
    source = json.loads(SOURCE_RUN.read_text())
    adaptive = json.loads(ADAPTIVE_RUN.read_text())
    last_checkpoint = source["checkpoint_chain"][-1]
    terminal_payload = adaptive["terminal_raw_enclosure"]["payload"]

    rational_init_tree = source_ast(transport.RationalFunction.__init__)
    seed_tree = source_ast(transport.seed_vector)
    step_tree = source_ast(transport.taylor_step)
    payload_tree = source_ast(repair.line_payload)
    address_tree = source_ast(successor.addressed_checkpoint)

    rational_source = inspect.getsource(transport.RationalFunction.__init__)
    step_source = inspect.getsource(transport.taylor_step)
    seed_source = inspect.getsource(transport.seed_vector)

    facts = {
        "frequency_substituted_before_numeric_transport": (
            "moving.W, sp.Rational(OMEGA)" in rational_source
        ),
        "seed_uses_componentwise_inflate": (
            "inflate" in called_names(seed_tree)
            and "for value in values" in seed_source
        ),
        "step_state_type_is_cartesian_acb_list": (
            "list[acb]" in _list_return_annotation(transport.taylor_step)
        ),
        "radial_coefficients_are_local_temporaries": (
            "coefficients" in {
                node.id
                for node in ast.walk(step_tree)
                if isinstance(node, ast.Name)
            }
        ),
        "step_returns_only_result_and_metadata": (
            "return result" in step_source
            and "coefficients" not in string_constants(step_tree)
        ),
        "step_inflates_each_output_component": (
            "result = [inflate(value, tail) for value in result]" in step_source
        ),
        "dual_line_has_no_affine_generator_field": (
            set(transport.DualLine.__dataclass_fields__)
            == {
                "tangent",
                "base",
                "amplitude",
                "amplitude_tangent",
                "pivot",
            }
        ),
        "line_payload_serializes_only_ball_coordinates": (
            called_names(payload_tree) == {"serialize_vector"}
            and "correlated_state" not in string_constants(payload_tree)
        ),
        "addressed_checkpoint_has_no_correlated_payload": (
            "correlated_state" not in string_constants(address_tree)
        ),
        "last_checkpoint_has_no_correlated_export": (
            not checkpoint_has_correlated_export(last_checkpoint)
        ),
        "terminal_payload_has_no_correlated_export": (
            not checkpoint_has_correlated_export(terminal_payload)
        ),
    }
    if not all(facts.values()):
        raise RuntimeError(f"correlation-loss audit drift: {facts}")

    restart_rho = str(transport.RHO0)
    contract = {
        "schema": "phase3-horizon-correlated-affine-checkpoint-contract-v1",
        "restart_disposition": "REGENERATE_FROM_SYMBOLIC_MIXED_LEVELT_SEED",
        "earliest_required_restart": {
            "rho": restart_rho,
            "r": str(transport.RHO0 + 2),
            "stage": (
                "levelt.exact_data(crosswalk), while omega remains symbolic, "
                "before seed_vector, initial projective normalization, or "
                "RationalFunction substitution of OMEGA"
            ),
            "reason": (
                "the seed tail is first converted into independent acb "
                "component balls and every later step repeats that collapse"
            ),
        },
        "required_frequency_model": {
            "coordinate": "zeta=omega-omega_center",
            "omega_center": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
            "omega_radius": "REQUIRED_EXPLICIT_INPUT",
            "omega_order": "REQUIRED_EXPLICIT_INPUT",
            "phase_rule": (
                "keep the complete moving Frobenius/Jost phase symbolic; "
                "Taylor-expand only the reduced amplitude"
            ),
        },
        "required_state_export": {
            "keys": sorted(REQUIRED_CORRELATED_KEYS),
            "dual_tau_state": (
                "base and intrinsic tau tangent share the same omega "
                "polynomial variables and affine noise symbols"
            ),
            "affine_generators": (
                "serialize one generator matrix acting on shared bounded "
                "noise symbols; do not issue a new independent symbol per "
                "coordinate or per dual rail"
            ),
            "residual_norm_ball": (
                "serialize a coupled vector remainder in a declared norm, "
                "separate from the affine generators"
            ),
            "radial_taylor_coefficients": (
                "serialize accepted-step polynomial coefficients or a hash "
                "bound to a deterministic replay that reconstructs them "
                "without consuming Cartesian checkpoints"
            ),
        },
        "required_transport_invariants": [
            "omega polynomial, tau tangent, and affine noise symbols survive every panel",
            "base and tangent remainders are not independently re-inflated",
            "chart transformations act on polynomial, generators, and residual together",
            "projective reciprocal is evaluated as a correlated Taylor-model operation",
            "each checkpoint hashes parent, generator, chart, polynomial, affine generators, noise domain, and residual",
        ],
        "acceptance_gates": {
            "state_excludes_zero": (
                "certified separation of the correlated set from the zero vector"
            ),
            "or_chart_denominator_excludes_zero": (
                "certified positive lower modulus of one fixed row over the "
                "entire correlated set"
            ),
            "successor_attempt": (
                "after a separating gate passes, apply the transformed chart "
                "and certify one radial successor substep without Cartesian collapse"
            ),
        },
        "forbidden_substitutes": [
            "a representation label without correlated_state data",
            "independent complex balls with equal printed radii",
            "midpoint-only chart selection",
            "replay from panel 30 or panel 31 Cartesian checkpoints",
            "claiming local radial Taylor temporaries are a serialized omega Taylor model",
        ],
    }

    return {
        "schema": "phase3-axial-horizon-correlated-affine-export-audit-run-v1",
        "frequency": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
        "sources": {
            "multipanel_run": {
                "path": str(SOURCE_RUN.relative_to(ROOT)),
                "sha256": sha256(SOURCE_RUN),
            },
            "adaptive_run": {
                "path": str(ADAPTIVE_RUN.relative_to(ROOT)),
                "sha256": sha256(ADAPTIVE_RUN),
            },
            "checkpoint_transport": {
                "path": str(Path(transport.__file__).relative_to(ROOT)),
                "sha256": sha256(Path(transport.__file__)),
            },
            "levelt_symbolic_seed": {
                "path": str(LEVELT.relative_to(ROOT)),
                "sha256": sha256(LEVELT),
            },
            "moving_phase": {
                "path": str(MOVING.relative_to(ROOT)),
                "sha256": sha256(MOVING),
            },
        },
        "representation_audit": facts,
        "last_accepted_cartesian_checkpoint": {
            "rho": last_checkpoint["rho"],
            "content_sha256": last_checkpoint["content_sha256"],
            "resumable_as_correlated_affine_state": False,
        },
        "terminal_cartesian_enclosure": {
            "rho": adaptive["terminal_raw_enclosure"]["rho"],
            "content_sha256": adaptive["terminal_raw_enclosure"]["content_sha256"],
            "resumable_as_correlated_affine_state": False,
        },
        "rerun_export_contract": contract,
        "terminal": {
            "gate": "CORRELATED_STATE_NOT_SERIALIZED",
            "earliest_restart_rho": restart_rho,
            "successor_substep_attempted": False,
            "reason": (
                "a rigorous affine/Taylor successor cannot be reconstructed "
                "from Cartesian checkpoint balls without inventing correlations"
            ),
        },
        "claim_flags": {
            "shared_omega_taylor_model_present": False,
            "shared_dual_tau_affine_remainder_present": False,
            "last_checkpoint_affine_resumable": False,
            "terminal_enclosure_affine_resumable": False,
            "earliest_restart_identified": True,
            "rerun_export_contract_emitted": True,
            "correlated_pivot_certified": False,
            "successor_substep_certified": False,
            "next_base_panel_completed": False,
            "r4_reached": False,
            "H4_certified": False,
            "T_plus_certified": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
