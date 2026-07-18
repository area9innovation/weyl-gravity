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
    "minimal_kt": ROOT / "quantum-weyl/local_bv/certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
    "elliptic": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "multiplicity": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "integration_slice": ROOT / "quantum-weyl/spectral/euclidean/certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
    "factor_coefficients": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
    "breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "matter": ROOT / "quantum-weyl/anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "wz_preflight": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "extended": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "gamma1": ROOT / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_tt_log": ROOT / "quantum-weyl/transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "curvature_squared_log": ROOT / "quantum-weyl/transfer/certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "fv_conformized_log": ROOT / "quantum-weyl/transfer/certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
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
    minimal_kt = values["minimal_kt"]
    elliptic = values["elliptic"]
    multiplicity = values["multiplicity"]
    integration_slice = values["integration_slice"]
    factor_coefficients = values["factor_coefficients"]
    breaking = values["breaking"]
    matter = values["matter"]
    lift = values["lift"]
    wz_preflight = values["wz_preflight"]
    extended = values["extended"]
    gamma1 = values["gamma1"]
    flat_tt_log = values["flat_tt_log"]
    curvature_squared_log = values["curvature_squared_log"]
    fv_conformized_log = values["fv_conformized_log"]
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
        or minimal_kt.get("spectral_sequence", {}).get("collapse_page") != "E2"
        or len(minimal_kt.get("contraction", {}).get("contractible_pairs", [])) != 6
        or elliptic.get("result_state")
        != "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC"
        or any(not row.get("exact_at_middle") for row in elliptic.get("principal_symbol_exactness", []))
        or len(multiplicity.get("repository_factors", [])) != 4
        or len(integration_slice.get("factor_exponent_ledger", [])) != 4
        or factor_coefficients.get("coefficient_result", {}).get("coefficients", {}).get("C2")
        != {"numerator": 199, "denominator": 30}
        or factor_coefficients.get("coefficient_result", {}).get("coefficients", {}).get("E4")
        != {"numerator": -87, "denominator": 20}
        or len(factor_coefficients.get("coefficient_result", {}).get("factor_contributions", []))
        != 4
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or matter.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or lift.get("exact_checks", {}).get("Q_squared_zero_on_all_atoms") is not True
        or lift.get("contractible_quartet", {}).get("anticommutator")
        != [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        or wz_preflight.get("local_primitives", {}).get("variation_convention")
        != "Q_W B_C=ANOM_OMEGA_C2; Q_W B_E=ANOM_OMEGA_E4 modulo d_h"
        or extended.get("H04", {}).get("even_quotient_dimension") != 3
        or extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or extended.get("H14", {}).get("boundary_rank") != 4
        or extended.get("H14", {}).get("even_quotient_dimension") != 0
        or extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or gamma1.get("result_state")
        != "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN"
        or gamma1.get("exact_coefficient_solve", {}).get("rank") != 3
        or flat_tt_log.get("result_state")
        != "FLAT_TT_UNIVERSAL_LOGARITHMIC_GAMMA1_FORM_FACTOR_CERTIFIED_FINITE_CONSTANT_AND_CURVED_COMPLETION_OPEN"
        or flat_tt_log.get("exact_logarithmic_form_factor", {}).get("logarithmic_coefficient")
        != {"numerator": -199, "denominator": 60}
        or curvature_squared_log.get("covariant_curvature_squared_form_factor", {}).get(
            "curvature_order"
        )
        != 2
        or curvature_squared_log.get("operator_choice_independence", {}).get(
            "first_difference_order"
        )
        != 3
        or fv_conformized_log.get("decision", {}).get(
            "selected_C2_log_local_Weyl_completion"
        )
        != "CERTIFIED"
        or fv_conformized_log.get("carrier_crosswalk", {}).get("identity_status")
        != "DISTINCT_CARRIERS_NO_IDENTIFICATION"
    ):
        raise ValueError("Paper 12 generated-table dependency drifted")
    return values


def _local_prescription(operator: str) -> str:
    if operator == "Delta_0(-4)":
        return "cut; negative-mode phase locally constant"
    return "factorwise spectral cut"


def _factor_label(factor_id: str) -> str:
    return {
        "repository_physical_upper": "metric TT, upper",
        "repository_scalar_ghost": "Diff--Weyl scalar ghost",
        "repository_physical_lower": "metric TT, lower",
        "repository_vector_ghost": "transverse Diff ghost",
    }[factor_id]


def build() -> str:
    values = _load()
    even = values["even"]
    odd = values["odd"]
    gauge = values["gauge_fixed"]
    minimal_kt = values["minimal_kt"]
    elliptic = values["elliptic"]
    multiplicity = values["multiplicity"]
    integration_slice = values["integration_slice"]
    factor_coefficients = values["factor_coefficients"]
    breaking = values["breaking"]
    matter = values["matter"]
    lift = values["lift"]
    wz_preflight = values["wz_preflight"]
    extended = values["extended"]
    gamma1 = values["gamma1"]
    flat_tt_log = values["flat_tt_log"]
    curvature_squared_log = values["curvature_squared_log"]
    fv_conformized_log = values["fv_conformized_log"]
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
    flat_log = flat_tt_log["exact_logarithmic_form_factor"]
    curved_log = curvature_squared_log["covariant_curvature_squared_form_factor"]
    operator_comparison = curvature_squared_log["operator_choice_independence"]
    fv_carrier = fv_conformized_log["conformized_C2_log"]
    fv_cubic = fv_conformized_log["cubic_carrier"]
    zero_modes = {
        row["operator"]: row["zero_mode_dimension"]
        for row in integration_slice["factor_exponent_ledger"]
    }
    determinant_rows = "\n".join(
        rf"{_factor_label(factor['factor_id'])} & "
        rf"\texttt{{{factor['operator'].replace('_', r'\_')}}} & {factor['component_rank']} & "
        rf"{factor['statistics'].lower()} & ${_q(factor['determinant_exponent'])}$ & "
        rf"{zero_modes[factor['operator']]} & {_local_prescription(factor['operator'])} \\"
        for factor in multiplicity["repository_factors"]
    )
    contribution_rows = "\n".join(
        rf"{_factor_label(row['factor_id'])} & ${_q(row['coordinates']['C2'])}$ & "
        rf"${_q(row['coordinates']['E4'])}$ & ${_q(row['coordinates']['CdualC'])}$ & "
        rf"${_q(row['coordinates']['BoxR'])}$ \\"
        for row in factor_coefficients["coefficient_result"]["factor_contributions"]
    )
    matter_labels = {
        "real_conformal_scalar": "real conformal scalar",
        "Weyl_fermion": "Weyl fermion",
        "Dirac_fermion": "Dirac fermion",
        "gauge_vector": "gauge vector (with BRST ghosts)",
    }
    matter_rows = "\n".join(
        rf"{matter_labels[name]} & ${_q(data['vector'][0])}$ & ${_q(data['vector'][1])}$ \\"
        for name in ("real_conformal_scalar", "Weyl_fermion", "Dirac_fermion", "gauge_vector")
        for data in (matter["matter_generators"][name],)
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
$\tau$-adic extended BV & {extended['H04']['even_quotient_dimension']} & {extended['H04']['odd_quotient_dimension']} & {extended['H14']['even_quotient_dimension']} & {extended['H14']['odd_quotient_dimension']} \\
\bottomrule
\end{{tabular}}
\caption{{Exact dimension-four local BV quotient dimensions.}}
\label{{tab:generated-quotient-dimensions}}
\end{{table}}

\begin{{table}}[ht]
\centering\small
\begin{{tabularx}}{{\textwidth}}{{@{{}}Y Y r Y@{{}}}}
\toprule
Spectral-sequence step & Exact input & Rank/count & Outcome \\
\midrule
Koszul--Tate $E_0$ & adapted regular-Bach pairs & {len(minimal_kt['contraction']['contractible_pairs'])} pairs & positive AFN columns vanish \\
$E_1\Rightarrow E_2$ & AFN0 modulo Euler--Noether ideal & {minimal_kt['contraction']['regression_monomial_count']} monomials & collapse at $E_2$ \\
nonminimal extension & pointwise Diff$\times$Weyl doublets & {gauge['direct_sum_contraction']['pair_count']} pairs & chain contraction \\
gauge-fixing transport & local BV-canonical similarity & {gauge['direct_sum_contraction']['regression_monomial_count']} monomials & quotient preserved \\
\bottomrule
\end{{tabularx}}
\caption{{Strict-quotient spectral-sequence and contraction ledger on the regular Bach locus.}}
\label{{tab:generated-spectral-sequence}}
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
\centering\small
\begin{{tabularx}}{{\textwidth}}{{@{{}}YlrlrrY@{{}}}}
\toprule
Sector & operator & rank & statistics & exponent in $Z$ & zero modes removed & local prescription \\
\midrule
{determinant_rows}
\bottomrule
\end{{tabularx}}
\caption{{Human-readable determinant ledger for the accepted repository Euclidean integration slice.  Exponents are determinant powers in $Z$; the corresponding $\Gamma_1$ powers have the opposite sign.}}
\label{{tab:generated-determinant-ledger}}
\end{{table}}

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lrrrr@{{}}}}
\toprule
Sector & $C^2$ & $E_4$ & $C\widetilde C$ & $\Box R$ \\
\midrule
{contribution_rows}
\midrule
exact sum & $\frac{{199}}{{30}}$ & $-\frac{{87}}{{20}}$ & $0$ & $0$ \\
\bottomrule
\end{{tabular}}
\caption{{Factorwise local heat-kernel coordinates after the accepted determinant exponents, measure and quartet cancellations.  Their exact sum is the bosonic-Weyl-parameter Ward carrier before ghost replacement and BV quotient reduction.}}
\label{{tab:generated-factorwise-coefficients}}
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
\begin{{tabular}}{{@{{}}lrr@{{}}}}
\toprule
Standard-sign field & $C^2$ coordinate & $E_4$ coordinate \\
\midrule
pure Weyl graviton & $\frac{{199}}{{30}}$ & $-\frac{{87}}{{20}}$ \\
{matter_rows}
\bottomrule
\end{{tabular}}
\caption{{Exact anomaly vectors in the convention $(c,-a)$.  The functional $(1,0)$ is strictly positive on the gravity vector and every allowed matter ray, already excluding cancellation in the nonnegative cone.}}
\label{{tab:generated-matter-vectors}}
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

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lr@{{}}}}
\toprule
Flat-TT form-factor datum & exact value \\
\midrule
$c$ & ${_q(flat_log['anomaly_C2_coefficient_c'])}$ \\
$\beta_2$ & ${_q(flat_log['heat_kernel_beta2'])}$ \\
$A_{{\log}}$ & ${_q(flat_log['logarithmic_coefficient'])}$ \\
$\mu\partial_\mu F_C$ & ${_q(flat_log['RG_scale_response'])}$ \\
finite local $C^2$ constant & open \\
\bottomrule
\end{{tabular}}
\caption{{Universal nonzero-momentum flat Euclidean TT logarithmic form factor.  The additive finite normalization and curved completion are not fixed.}}
\label{{tab:generated-flat-tt-logarithm}}
\end{{table}}

\begin{{table}}[ht]
\centering
\begin{{tabular}}{{@{{}}lr@{{}}}}
\toprule
Covariant-log datum & exact value \\
\midrule
curvature order of $\langle C,\log(\Delta_C/\mu^2)C\rangle$ & {curved_log['curvature_order']} \\
first admissible operator-choice difference & {operator_comparison['first_difference_order']} \\
logarithmic coefficient & ${_q(curved_log['logarithmic_coefficient'])}$ \\
selected FV Weyl-orbit completion & certified \\
first forced FV correction order & {fv_cubic['first_completion_order']} \\
independent cubic Weyl-invariant form factors & open \\
finite $C^2/R^2$ normalization & open \\
\bottomrule
\end{{tabular}}
\caption{{Covariant curvature-squared logarithm, its exact FV completion as a selected carrier, and the independent-data boundary.  The coefficient remains ${_q(fv_carrier['logarithmic_coefficient'])}$.}}
\label{{tab:generated-curvature-squared-logarithm}}
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

The Euler primitive used by the boundary matrix is
\begin{{equation}}
B_E=\int\!\sqrt g\,\left[
 \tau E_4+4G^{{\mu\nu}}\nabla_\mu\tau\nabla_\nu\tau
 -4(\Box\tau)(\nabla\tau)^2+2(\nabla\tau)^4\right],
\qquad Q_WB_E=\int\!\sqrt g\,\omega E_4\pmod{{\dd_h}},
\label{{eq:generated-euler-wz}}
\end{{equation}}
with the sign convention $Q_WB_C=\int\sqrt g\,\omega C^2$ and
$Q_WB_E=\int\sqrt g\,\omega E_4$ modulo $\dd_h$.

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
