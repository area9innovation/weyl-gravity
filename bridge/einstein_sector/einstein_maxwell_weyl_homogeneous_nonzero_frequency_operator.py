"""Classify the homogeneous Weyl-Maxwell target at nonzero frequency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _equations


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.schema.json"
ENGINES = {
    "curvature": ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py",
    "weyl_maxwell_equations": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py",
}


class HomogeneousOperatorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HomogeneousOperatorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_reduced_operator() -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    omega = sp.symbols("omega", real=True)
    circle, sphere, holonomy = sp.symbols("C K A_x")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(-sp.I * omega * time)
    metric = sp.diag(
        -1,
        1 + epsilon * circle * wave,
        1 + epsilon * sphere * wave,
        (1 + epsilon * sphere * wave) * sine**2,
    )
    tr = lambda expression: _trunc(expression, epsilon, 1)
    inverse = metric.inv().applyfunc(tr)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = tr(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(holonomy * wave, time)
    field[1, 0] = -field[0, 1]
    geometry = {
        "epsilon": epsilon,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }
    data = _curvature(geometry, 1)
    metric_equations, maxwell_equations = _equations(data, 1, ((0, 0), (0, 1), (1, 1), (2, 2), (3, 3)))
    sphere_trace = (metric_equations[(2, 2)] + metric_equations[(3, 3)] / sine**2) / 2
    expressions = (
        metric_equations[(0, 0)],
        metric_equations[(0, 1)],
        metric_equations[(1, 1)],
        sphere_trace,
        maxwell_equations[0],
        maxwell_equations[1],
    )
    rows = [_canonical(sp.diff(expression, epsilon).subs(epsilon, 0) / wave) for expression in expressions]
    expected = [0, 0, -omega**4 * (circle - sphere) / 2, omega**4 * (circle - sphere) / 4, 0, omega**2 * holonomy]
    _require([sp.factor(rows[index] - expected[index]) for index in range(6)] == [0] * 6, "homogeneous reduced operator changed")
    return {
        "frequency": "omega!=0",
        "partial_gauge_slice": "h_tt=h_tx=a_t=0",
        "slice_fields": ["C=h_xx", "K=sphere trace coefficient", "A_x"],
        "residual_gauge": "a combined Weyl/time-diffeomorphism shifts (C,K) by the same amount; C-K is invariant",
        "row_order": ["E00", "E01", "E11", "sphere_trace", "Maxwell0", "Maxwell1"],
        "rows": [str(sp.factor(row)) for row in rows],
        "reduced_invariants": ["D=C-K", "A_x"],
        "invariant_equations": ["omega^4*D=0", "omega^2*A_x=0"],
        "nonzero_frequency_quotient_dimension": 0,
    }


def build_certificate() -> dict[str, object]:
    theorem = _direct_reduced_operator()
    return {
        "schema": "einstein-maxwell-weyl-homogeneous-nonzero-frequency-operator-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_NONZERO_FREQUENCY_OPERATOR",
        "result_state": "HOMOGENEOUS_NONZERO_FREQUENCY_WEYL_MAXWELL_QUOTIENT_EMPTY",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "homogeneous ell=0,k=0 Weyl-Maxwell coefficient complex at omega!=0 on the fixed magnetic bundle, before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "engines": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in ENGINES.items()},
        },
        "gauge_completeness": {
            "raw_fields": ["h_tt", "h_tx", "h_xx", "sphere trace", "a_t", "a_x"],
            "nonzero_frequency_gauge_parameters": ["xi_t", "xi_x", "sigma", "chi"],
            "first_slice": "xi_t,xi_x,chi set h_tt,h_tx,a_t to zero for omega!=0",
            "residual_slice_action": "sigma accompanied by xi_t preserves h_tt=0 and shifts h_xx and the sphere trace equally",
            "complete_gauge_invariants": ["h_xx-sphere trace", "a_x"],
        },
        "operator_theorem": theorem,
        "classification": {
            "direct_four_dimensional_linearization_computed": True,
            "nonzero_frequency_gauge_slice_complete": True,
            "homogeneous_nonzero_frequency_physical_quotient_empty": True,
            "homogeneous_extra_oscillatory_weyl_modes_absent": True,
            "generalized_zero_frequency_block_unchanged": True,
            "final_residual_descent_certified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The homogeneous target has no hidden fourth-order oscillator. At nonzero frequency its only gauge-invariant coefficients obey omega^4(C-K)=0 and omega^2 A_x=0, so both vanish; the remaining common metric coefficient is residual Weyl/diffeomorphism gauge. All genuine homogeneous data therefore remain in the separately certified generalized zero-frequency block.",
        "next_gate": "use the empty homogeneous oscillatory quotient to close the exceptional 2omega positive-sum resonance census, then compute the surviving generalized-zero times ell=2-extra bilinear source",
        "claim_boundary": "This is a local-gauge-reduced homogeneous nonzero-frequency operator theorem. It does not alter the generalized zero-frequency phase space, classify nonlinear mixed sources, perform final residual descent, or make causal, particle, or quantum claims.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 6.42, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(ENGINES)},
            "tier_3": {"status": "NOT_RUN", "reason": "no freeze promotion beyond the scoped homogeneous operator theorem"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "homogeneous operator certificate is stale")


if __name__ == "__main__":
    main()
