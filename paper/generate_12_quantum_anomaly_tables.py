#!/usr/bin/env python3
"""Generate exact certificate tables for the Paper 12 supplement."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/generated/12-quantum-anomaly-certificate-tables.tex"
INPUTS = {
    "even": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "odd": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "gauge_fixed": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "matter": ROOT / "quantum-weyl/anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "extended": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "gamma1": ROOT / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> str:
    numerator = value["numerator"]
    denominator = value["denominator"]
    if denominator == 1:
        return str(numerator)
    if numerator < 0:
        return rf"-\frac{{{-numerator}}}{{{denominator}}}"
    return rf"\frac{{{numerator}}}{{{denominator}}}"


def _load() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    even = values["even"]
    odd = values["odd"]
    gauge = values["gauge_fixed"]
    breaking = values["breaking"]
    matter = values["matter"]
    lift = values["lift"]
    extended = values["extended"]
    gamma1 = values["gamma1"]
    if (
        even.get("result_state") != "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT"
        or even.get("smallest_relative_sector", {}).get("closure_rank") != 6
        or even.get("smallest_relative_sector", {}).get("boundary_rank") != 4
        or odd.get("result_state") != "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT"
        or odd.get("smallest_relative_sector", {}).get("quotient_dimension") != 1
        or gauge.get("result_state")
        != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_even_dimension") != 2
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_odd_dimension") != 1
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or matter.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or lift.get("exact_checks", {}).get("Q_squared_zero_on_all_atoms") is not True
        or lift.get("contractible_quartet", {}).get("anticommutator")
        != [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        or extended.get("H04", {}).get("even_quotient_dimension") != 3
        or extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or extended.get("H14", {}).get("boundary_rank") != 4
        or extended.get("H14", {}).get("even_quotient_dimension") != 0
        or extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or gamma1.get("result_state")
        != "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN"
        or gamma1.get("exact_coefficient_solve", {}).get("rank") != 3
    ):
        raise ValueError("Paper 12 generated-table dependency drifted")
    return values


def build() -> str:
    values = _load()
    even = values["even"]
    odd = values["odd"]
    gauge = values["gauge_fixed"]
    breaking = values["breaking"]
    lift = values["lift"]
    extended = values["extended"]
    gamma1 = values["gamma1"]
    even_orbits = json.loads(
        next(
            item["payload_json"]
            for item in even["basis_exhaustiveness_proof"]["bound_artifacts"]
            if item["role"] == "orbit_enumeration"
        )
    )
    odd_orbits = json.loads(
        next(
            item["payload_json"]
            for item in odd["basis_exhaustiveness_proof"]["bound_artifacts"]
            if item["role"] == "orbit_enumeration"
        )
    )
    coefficients = breaking["coefficients"]
    quartet = lift["contractible_quartet"]
    rows = [
        ("$C^2$", coefficients["ANOM_OMEGA_C2"]),
        ("$E_4$", coefficients["ANOM_OMEGA_E4"]),
        ("$C\\widetilde C$", coefficients["ANOM_OMEGA_C_DUAL_C"]),
        ("$\\Box R$", coefficients["ANOM_OMEGA_BOX_R"]),
    ]
    coefficient_rows = "\n".join(
        rf"{name} & ${_q(value)}$ \\" for name, value in rows
    )
    gamma_solution = gamma1["exact_coefficient_solve"]["solution_vector"]
    gamma_rows = "\n".join(
        rf"{name} & ${_q(value)}$ \\"
        for name, value in zip(
            (r"$\langle\mathcal E_4,G_4C^2\rangle$", r"$\langle\mathcal E_4,G_4\mathcal E_4\rangle$", r"$\int\sqrt g R^2$"),
            gamma_solution,
        )
    )
    hashes = "\n".join(
        rf"\nolinkurl{{{path.relative_to(ROOT)}}} & \texttt{{{_sha256(path)[:16]}}} \\"
        for path in INPUTS.values()
    )
    return rf"""% Generated by paper/generate_12_quantum_anomaly_tables.py.
% Do not edit by hand.
\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lrrrr@{{}}}}
\toprule
Stage & $\dim H^{{0,4}}_{{\rm even}}$ & $\dim H^{{0,4}}_{{\rm odd}}$ & $\dim H^{{1,4}}_{{\rm even}}$ & $\dim H^{{1,4}}_{{\rm odd}}$ \\
\midrule
strict gauge-fixed BV & {gauge['gauge_fixed_cohomology']['H04_even_dimension']} & {gauge['gauge_fixed_cohomology']['H04_odd_dimension']} & {gauge['gauge_fixed_cohomology']['H14_even_dimension']} & {gauge['gauge_fixed_cohomology']['H14_odd_dimension']} \\
tau-adic extended BV & {extended['H04']['even_quotient_dimension']} & {extended['H04']['odd_quotient_dimension']} & {extended['H14']['even_quotient_dimension']} & {extended['H14']['odd_quotient_dimension']} \\
\bottomrule
\end{{tabular}}
\caption{{Exact dimension-four local BV quotient dimensions.}}
\label{{tab:generated-quotient-dimensions}}
\end{{table}}

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lrrr@{{}}}}
\toprule
Sector & raw graphs/pairings materialized & closure rank & boundary rank \\
\midrule
even AFN0 relative carrier & {even_orbits['raw_graphs_materialized']} & {even['smallest_relative_sector']['closure_rank']} & {even['smallest_relative_sector']['boundary_rank']} \\
odd AFN0 mixed carrier & {odd_orbits['mixed_raw_graphs_materialized']} & {odd['smallest_relative_sector']['closure_rank']} & {odd['smallest_relative_sector']['boundary_rank']} \\
\bottomrule
\end{{tabular}}
\caption{{Orbit-first strict AFN0 quotient audit.  The ambient $2.86\times10^9$ raw-graph expansion is never materialized.}}
\label{{tab:generated-orbit-audit}}
\end{{table}}

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lr@{{}}}}
\toprule
Density coordinate & repository one-loop coefficient \\
\midrule
{coefficient_rows}
\bottomrule
\end{{tabular}}
\caption{{Coefficient vector in the convention $(4\pi)^{{-2}}[cC^2-aE_4+pC\widetilde C+b\Box R]$.}}
\label{{tab:generated-coefficients}}
\end{{table}}

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lr@{{}}}}
\toprule
Anomaly-induced functional carrier & exact coefficient \\
\midrule
{gamma_rows}
\bottomrule
\end{{tabular}}
\caption{{Exact Paneitz/Riegert solve.  The Weyl-response matrix is $\operatorname{{diag}}(4,8,-12)$; re-expansion returns $(199/30,-87/20,0)$ in $(C^2,E_4,\Box R)$.}}
\label{{tab:generated-anomaly-induced-gamma1}}
\end{{table}}

\begin{{equation}}
Q_W=
\begin{{pmatrix}}
0&0&0&0\\
1&0&0&0\\
0&0&0&0\\
0&0&1&0
\end{{pmatrix}},\qquad
h=
\begin{{pmatrix}}
0&1&0&0\\
0&0&0&0\\
0&0&0&1\\
0&0&0&0
\end{{pmatrix}},\qquad
Q_Wh+hQ_W=I_4,
\label{{eq:generated-quartet-matrices}}
\end{{equation}}
in the ordered basis
$(\tau,\omega,\omega^*,\widehat\tau^*)$.
The certificate checks {lift['exact_checks']['checked_atom_count']} atoms and
{lift['extension_scope']['generator_count']} generators over
${lift['extension_scope']['coefficient_field']}$; all component gradings,
$\delta^2$, $\delta\gamma+\gamma\delta$, and $Q^2$ pass exactly.

\begin{{equation}}
B_{{\rm ext}}=
\begin{{pmatrix}}
1&0&0&0\\
0&1&0&0\\
0&0&1&0\\
0&0&0&1
\end{{pmatrix}},\qquad
\operatorname{{rank}}B_{{\rm ext}}={extended['H14']['boundary_rank']},
\label{{eq:generated-extended-boundary}}
\end{{equation}}
from the ordered primitive basis
$(B_C,B_E,B_P,B_{{\Box}})$ to
$(\omega C^2,\omega E_4,\omega C\widetilde C,\omega\Box R)$.
The strict breaking and its extended boundary image are both
\[
\left(\frac{{199}}{{30}},-\frac{{87}}{{20}},0,0\right).
\]

\begin{{table}}[ht]
\centering\small
\begin{{tabularx}}{{\textwidth}}{{@{{}}Yl@{{}}}}
\toprule
Certificate & SHA-256 prefix \\
\midrule
{hashes}
\bottomrule
\end{{tabularx}}
\caption{{Content-addressed inputs to the generated supplement tables.  Full hashes are stored in the Paper 12 claim map.}}
\label{{tab:generated-input-hashes}}
\end{{table}}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = build()
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("Paper 12 generated tables are stale; rerun with --emit")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()
