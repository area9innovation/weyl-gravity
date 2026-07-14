"""Fail-closed transport of the certified energy theorem to covariant BV.

This module performs no auxiliary-space cohomology calculation.  It reads the
validated final-claim DAG and records the chain of quasi-isomorphisms requested
by the covariant theorem.  The final status is exactly the conjunction declared
in :mod:`covariant_completion.dependencies.final_claims`.
"""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.dependencies import FinalClaimDependencyReport


@dataclass(frozen=True)
class FinalCovariantTransportStatus:
    """Transport diagram and its current theorem status."""

    report: FinalClaimDependencyReport

    @staticmethod
    def build() -> "FinalCovariantTransportStatus":
        return FinalCovariantTransportStatus.from_report(
            FinalClaimDependencyReport.build()
        )

    @staticmethod
    def from_report(
        report: FinalClaimDependencyReport,
    ) -> "FinalCovariantTransportStatus":
        """Build from one validated DAG snapshot.

        Keeping this constructor explicit makes the terminal behavior testable
        both before and after the upstream A--C lemmas close; no transport
        status is cached as an assumed constant.
        """

        result = FinalCovariantTransportStatus(report)
        result.verify()
        return result

    def verify(self) -> None:
        nodes = self.report.nodes
        final = nodes["final_covariant_H4"]
        expected = (
            "curved_operator_identity",
            "curved_deformation_retract",
            "curved_current_comparison",
            "scalar_wave_witness_no_go",
            "weyl_symbol_helicity_isomorphism",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curved_constraint_propagation",
            "EAL_curvature_spectrum_match",
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
            "causal_green_homotopy",
            "causal_quasi_isomorphism",
            "residual_endpoint_recovery",
            "SO42_equivariant_transport",
            "prolonged_current_comparison",
            "residual_H4_is_C2",
            "residual_gram_is_I2",
        )
        if final.requires != expected:
            raise AssertionError(
                "the terminal transport gate does not match the closure brief"
            )
        if final.status != all(nodes[name].status for name in expected):
            raise AssertionError("the terminal transport flag was set manually")

        # The energy theorem is an input, not an output of this transport.
        if not nodes["residual_H4_is_C2"].status:
            raise AssertionError("the independently certified residual H4 regressed")
        if not nodes["residual_gram_is_I2"].status:
            raise AssertionError("the independently certified residual Gram regressed")

    @property
    def complete(self) -> bool:
        return self.report.nodes["final_covariant_H4"].status

    def blocking_dependencies(self, claim: str) -> tuple[str, ...]:
        if claim not in self.report.nodes:
            raise KeyError(f"unknown transport claim: {claim}")
        payload = self.report.certificate()["claims"][claim]
        blockers = tuple(payload["blocking_dependencies"])
        if bool(blockers) == self.report.nodes[claim].status:
            raise AssertionError(
                f"{claim} blockers disagree with its dependency-DAG status"
            )
        return blockers

    def certificate(self) -> dict[str, object]:
        self.verify()
        nodes = self.report.nodes
        arrows = [
            {
                "name": "auxiliary_equivalence",
                "map": "Gamma_c(C_met)[1] <-> Gamma_c(C_aux)[1]",
                "status": nodes["curved_deformation_retract"].status,
                "requires": ["curved_deformation_retract"],
            },
            {
                "name": "auxiliary_prolongation",
                "map": "Gamma_c(C_aux)[1] -> Gamma_c(C_prol)[1]",
                "status": nodes["support_local_prolongation_retract"].status
                and nodes["prolonged_BV_operator_identity"].status,
                "requires": [
                    "support_local_prolongation_retract",
                    "prolonged_BV_operator_identity",
                ],
            },
            {
                "name": "causal",
                "map": "Gamma_c(C_prol)[1] -> Gamma_sc(C_prol)=Gamma(C_prol)",
                "status": all(
                    nodes[name].status
                    for name in (
                        "curved_EB_equations",
                        "curved_EB_first_order_closure",
                        "curved_EB_symmetric_hyperbolicity",
                        "curved_sourced_constraint_identity",
                        "curved_constraint_propagation",
                        "EAL_curvature_spectrum_match",
                        "support_local_prolongation_retract",
                        "prolonged_BV_operator_identity",
                        "prolonged_green_witness",
                        "curvature_causal_green_operators",
                        "causal_green_homotopy",
                        "causal_quasi_isomorphism",
                    )
                ),
                "requires": [
                    "curved_EB_equations",
                    "curved_EB_first_order_closure",
                    "curved_EB_symmetric_hyperbolicity",
                    "curved_sourced_constraint_identity",
                    "curved_constraint_propagation",
                    "EAL_curvature_spectrum_match",
                    "support_local_prolongation_retract",
                    "prolonged_BV_operator_identity",
                    "prolonged_green_witness",
                    "curvature_causal_green_operators",
                    "causal_green_homotopy",
                    "causal_quasi_isomorphism",
                ],
            },
            {
                "name": "Cauchy_and_polarization",
                "map": "Gamma(C_prol) -> C_Sigma -> K_energy",
                "status": nodes["EAL_curvature_spectrum_match"].status
                and nodes["EAL_pairing_regression"].status,
                "requires": [
                    "EAL_curvature_spectrum_match",
                    "certified reduced Cauchy-Sobolev and polarization theorems",
                ],
            },
            {
                "name": "residual",
                "map": "K_energy -> C_BFV,res",
                "status": nodes["residual_endpoint_recovery"].status
                and nodes["SO42_equivariant_transport"].status,
                "requires": [
                    "residual_endpoint_recovery",
                    "SO42_equivariant_transport",
                ],
            },
            {
                "name": "pairing",
                "map": "Omega_prol -> Omega_aux -> Omega_met -> Omega_energy -> G_res",
                "status": nodes["curved_current_comparison"].status
                and nodes["prolonged_current_comparison"].status
                and nodes["residual_gram_is_I2"].status,
                "requires": [
                    "curved_current_comparison",
                    "prolonged_current_comparison",
                    "residual_gram_is_I2",
                ],
            },
        ]
        return {
            "schema": "pure-weyl-final-covariant-transport-status-v1",
            "method": "transport through pairing-compatible quasi-isomorphisms; no auxiliary H4 recomputation",
            "arrows": arrows,
            "terminal_gate": {
                "requires": list(nodes["final_covariant_H4"].requires),
                "status": self.complete,
                "blocking_dependencies": list(
                    self.blocking_dependencies("final_covariant_H4")
                ),
                "derived_not_manually_set": True,
            },
            "transported_result_when_gate_passes": {
                "H4": ["W_+^2", "W_-^2"],
                "Gram": [[1, 0], [0, 1]],
            },
            "independent_inputs": {
                "residual_H4_is_C2": nodes["residual_H4_is_C2"].status,
                "residual_gram_is_I2": nodes["residual_gram_is_I2"].status,
                "energy_H4_is_C2": nodes["energy_H4_is_C2"].status,
                "energy_gram_is_I2": nodes["energy_gram_is_I2"].status,
            },
            "guard": (
                "the displayed result is not promoted until every terminal-gate "
                "dependency is true"
            ),
        }
