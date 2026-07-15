#!/usr/bin/env python3
"""Exact principal witness after reattaching the Berger clock doublets.

The retained 26-row complex has only the three spatial diffeomorphism
columns, and its metric witness consequently has fourth-order rank eight.
The already-certified support-local clock SDR may be reversed without any
nonlocal operation.  On the resulting five-generator presentation this file
constructs a full diffeomorphism/Weyl companion and proves

    J H_4 + K_1 T = (zeta^2)^2 I_10,
    T K_1           = (zeta^2)^2 I_5.

This is a principal-symbol theorem.  It deliberately does not infer the
curved lower-order witness or causal Green homotopy from the symbol alone.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
        _matrix_from_record,
        _symbol,
    )
    from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
        ALPHA_B,
        ETA,
        PAIRS,
        ROOT,
        _spatial_gauge_operator,
        _split_operator_vector,
    )
except ModuleNotFoundError:  # Direct script execution.
    from berger_causal_witness_preflight import _matrix_from_record, _symbol
    from berger_linearized_bach_pbw import (
        ALPHA_B,
        ETA,
        PAIRS,
        ROOT,
        _spatial_gauge_operator,
        _split_operator_vector,
    )


Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_SDR_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-clock-reattached-principal-witness.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-clock-reattached-principal-witness-v1.schema.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _principal_data() -> dict[str, object]:
    q1 = json.loads(Q1_CERTIFICATE.read_text())
    if q1["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained Berger q1 dependency is not certified")
    clock = json.loads(CLOCK_SDR_CERTIFICATE.read_text())
    if clock["flags"]["support_local_clock_SDR_exact"] is not True:
        raise AssertionError("clock reattachment is not certified support local")

    hessian4 = _symbol(_matrix_from_record(q1["q1_blocks"]["H_retained"]), 4)
    momenta = sp.symbols("p0:4")
    wave = -momenta[0] ** 2 + sum(momenta[index] ** 2 for index in range(1, 4))

    spatial_gauge = _symbol(_split_operator_vector(_spatial_gauge_operator(), 3), 1)
    temporal_gauge = sp.Matrix(
        [
            (momenta[first] if second == 0 else 0)
            + (momenta[second] if first == 0 else 0)
            for first, second in PAIRS
        ]
    )
    metric_trace_vector = sp.Matrix([ETA[first, second] for first, second in PAIRS])
    full_gauge = spatial_gauge.row_join(temporal_gauge).row_join(2 * metric_trace_vector)

    trace = sp.Matrix([[ETA[first, second] for first, second in PAIRS]])
    divergence = sp.zeros(4, 10)
    for mu in range(4):
        for column, (first, second) in enumerate(PAIRS):
            divergence[mu, column] = sum(
                ETA[axis, axis] * momenta[axis]
                for axis in range(4)
                if tuple(sorted((axis, mu))) == (first, second)
            )
    double_divergence = sp.zeros(1, 10)
    for mu in range(4):
        double_divergence += ETA[mu, mu] * momenta[mu] * divergence[mu, :]

    # The density-dual independent-component basis has a factor two on each
    # off-diagonal component.  R is the inverse raised-index fibre pairing.
    raised_pairing_inverse = sp.diag(
        *[
            sp.Rational(
                1,
                (1 if first == second else 2) * ETA[first, first] * ETA[second, second],
            )
            for first, second in PAIRS
        ]
    )
    fibre_identification = sp.Rational(4, 1) / ALPHA_B * raised_pairing_inverse

    diffeomorphism_companion = sp.zeros(4, 10)
    for mu in range(4):
        diffeomorphism_companion[mu, :] = (
            wave * divergence[mu, :]
            - sp.Rational(1, 6) * wave * momenta[mu] * trace
            - sp.Rational(1, 3) * momenta[mu] * double_divergence
        )
    weyl_companion = (
        sp.Rational(1, 6) * wave**2 * trace
        - sp.Rational(1, 6) * wave * double_divergence
    )
    companion = sp.zeros(5, 10)
    companion[:3, :] = diffeomorphism_companion[1:4, :]
    companion[3, :] = diffeomorphism_companion[0, :]
    companion[4, :] = weyl_companion

    metric_principal = sp.simplify(fibre_identification * hessian4 + full_gauge * companion)
    ghost_principal = sp.simplify(companion * full_gauge)
    target_metric = wave**2 * sp.eye(10)
    target_ghost = wave**2 * sp.eye(5)
    if sp.simplify(metric_principal - target_metric) != sp.zeros(10):
        raise AssertionError("clock-reattached metric principal witness failed")
    if sp.simplify(ghost_principal - target_ghost) != sp.zeros(5):
        raise AssertionError("clock-reattached ghost principal witness failed")
    if sp.factor(raised_pairing_inverse.det()) == 0:
        raise AssertionError("metric fibre identification became degenerate")

    # These cross checks explain why the five ghost directions decouple at
    # principal order rather than merely sharing a determinant.
    diffeomorphism_weyl_cross = sp.simplify(diffeomorphism_companion * (2 * metric_trace_vector))
    weyl_diffeomorphism_cross = sp.simplify(weyl_companion * full_gauge[:, :4])
    if diffeomorphism_weyl_cross != sp.zeros(4, 1):
        raise AssertionError("diffeomorphism companion does not annihilate Weyl gauge")
    if weyl_diffeomorphism_cross != sp.zeros(1, 4):
        raise AssertionError("Weyl companion does not annihilate diffeomorphism gauge")

    return {
        "q1": q1,
        "clock": clock,
        "wave": wave,
        "full_gauge": full_gauge,
        "divergence": divergence,
        "double_divergence": double_divergence,
        "raised_pairing_inverse": raised_pairing_inverse,
        "fibre_identification": fibre_identification,
        "companion": companion,
        "metric_principal": metric_principal,
        "ghost_principal": ghost_principal,
    }


@dataclass(frozen=True)
class BergerClockReattachedPrincipalWitness:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerClockReattachedPrincipalWitness":
        data = _principal_data()
        q1 = data["q1"]
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-clock-reattached-principal-witness-v1",
            "result_id": "BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS",
            "setting_id": q1["setting_id"],
            "claim_status": "CERTIFIED_PRINCIPAL_COMPLETION_CURVED_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "dependency_refs": {
                "retained_q1": {
                    "result_id": q1["result_id"],
                    "sha256": _sha256(Q1_CERTIFICATE),
                },
                "clock_sdr": {
                    "result_id": data["clock"]["result_id"],
                    "sha256": _sha256(CLOCK_SDR_CERTIFICATE),
                },
            },
            "reattached_layout": {
                "degree_ranks": [5, 12, 12, 5],
                "total_minimal_rows": 34,
                "metric_rank": 10,
                "gauge_rank": 5,
                "gauge_order": ["xi_1", "xi_2", "xi_3", "tau", "sigma"],
                "support_local": True,
                "clock_rows_remain_contractible": True,
            },
            "normalized_witness": {
                "wave_symbol": "zeta^2=-p0^2+p1^2+p2^2+p3^2",
                "fibre_identification": "J=(4/alpha_B) R_raise",
                "R_raise_diagonal": [str(value) for value in data["raised_pairing_inverse"].diagonal()],
                "diffeomorphism_companion": "T_mu=zeta^2 D_mu-(1/6)zeta^2 p_mu tr-(1/3)p_mu DD",
                "weyl_companion": "T_sigma=(1/6)(zeta^2)^2 tr-(1/6)zeta^2 DD",
                "D_mu": "p^nu h_{nu mu}",
                "DD": "p^mu p^nu h_{nu mu}",
                "companion_matrix": _matrix_strings(data["companion"]),
            },
            "principal_identities": {
                "metric": "J H_4 + K_1 T = (zeta^2)^2 I_10",
                "ghost": "T K_1 = (zeta^2)^2 I_5",
                "metric_matrix": _matrix_strings(data["metric_principal"]),
                "ghost_matrix": _matrix_strings(data["ghost_principal"]),
                "metric_rank_off_characteristic": 10,
                "ghost_rank_off_characteristic": 5,
                "diffeomorphism_weyl_cross_terms": "zero",
            },
            "exact_checks": {
                "retained_q1_imported": True,
                "clock_sdr_imported": True,
                "full_five_direction_gauge_symbol": True,
                "fibre_identification_nondegenerate": True,
                "metric_scalar_biwave_principal": True,
                "ghost_scalar_biwave_principal": True,
                "principal_cross_terms_zero": True,
            },
            "flags": {
                "BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS": True,
                "BERGER_FULL_METRIC_BIWAVE_PRINCIPAL": True,
                "BERGER_FULL_GHOST_BIWAVE_PRINCIPAL": True,
                "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_ARITY_TWO_D_CARTAN": False,
            },
            "next_gate": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "claim_boundary": "This certificate proves an exact scalar-biwave principal completion after support-locally reattaching the already contractible temporal-diffeomorphism/Weyl clock rows. It does not prove the lower-order curved QW+WQ identity, construct advanced or retarded Green operators, complete nonminimal rows, or establish arity-two D-Cartan stability.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        checks = self.payload["exact_checks"]
        if any(value is not True for value in checks.values()):
            raise AssertionError("principal witness exact check dropped")
        flags = self.payload["flags"]
        for key in (
            "BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS",
            "BERGER_FULL_METRIC_BIWAVE_PRINCIPAL",
            "BERGER_FULL_GHOST_BIWAVE_PRINCIPAL",
        ):
            if flags[key] is not True:
                raise AssertionError(f"principal theorem dropped: {key}")
        for key in (
            "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_ARITY_TWO_D_CARTAN",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream theorem promoted: {key}")
        if self.payload["next_gate"] != "BERGER_CURVED_CLOCK_REATTACHED_WITNESS":
            raise AssertionError("clock-reattached witness next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Clock-reattached Berger principal witness

The rank-eight principal block of the retained 26-row presentation is not a
principal obstruction. Reversing the already-certified support-local clock
SDR restores the temporal-diffeomorphism and Weyl columns. With

\[
J=\frac4{\alpha_B}R_{\rm raise},
\]

and the normalized full companion

\[
T_\mu=\zeta^2D_\mu-\frac16\zeta^2p_\mu\operatorname{tr}
-\frac13p_\mu DD,
\qquad
T_\sigma=\frac16(\zeta^2)^2\operatorname{tr}
-\frac16\zeta^2DD,
\]

the exact principal identities are

\[
JH_4+K_1T=(\zeta^2)^2I_{10},
\qquad
TK_1=(\zeta^2)^2I_5.
\]

Thus all ten metric directions and all five gauge directions have scalar
biwave principal symbol on the reattached 34-row minimal presentation. The
two directions missing downstairs are precisely supplied by the local clock
doublets; no helicity or elliptic projector is used.

This is deliberately not yet a Green theorem. The next gate is to PBW-lift
the displayed companion through every lower curved order, assemble the exact
34-row cyclic identity \(P=QW+WQ\), and then construct and transport its
retarded/advanced homotopies back through the clock SDR.
"""


def _write(result: BergerClockReattachedPrincipalWitness) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerClockReattachedPrincipalWitness) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("clock-reattached principal certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("clock-reattached principal report drifted")


def _guards(result: BergerClockReattachedPrincipalWitness) -> None:
    mutations = [
        ("drop metric principal", ("flags", "BERGER_FULL_METRIC_BIWAVE_PRINCIPAL"), False),
        ("drop ghost principal", ("flags", "BERGER_FULL_GHOST_BIWAVE_PRINCIPAL"), False),
        ("promote curved witness", ("flags", "BERGER_CURVED_CLOCK_REATTACHED_WITNESS"), True),
        ("promote causal homotopy", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("skip curved gate", ("next_gate",), "BERGER_ARITY_TWO_D_CARTAN"),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        try:
            BergerClockReattachedPrincipalWitness(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerClockReattachedPrincipalWitness.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print("BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
