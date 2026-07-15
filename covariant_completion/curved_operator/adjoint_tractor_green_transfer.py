"""Conditional causal transfer from the adjoint-tractor YM detour.

On the conformally flat cylinder the adjoint-tractor connection is flat.
The Yang--Mills detour complex

``Omega0(A) --dA--> Omega1(A) --deltaA dA--> Omega1(A) --deltaA--> Omega0(A)``

has the canonical backward witness ``(deltaA,1,dA)``.  Its anticommutator is
the twisted Hodge wave operator in every degree, hence it has unique
advanced/retarded Green operators and causal chain homotopies.

If a curved differential BGG retract ``(i,p,h)`` from this parent complex to
the trace-free metric endpoint is exact, the endpoint homotopy is simply

``Lambda_end,+/- = p Lambda_parent,+/- i``.

The chain-map and ``p i=1`` identities give the endpoint homotopy identity;
finite-order differential ``i,p`` preserve causal support.  If the retract is
cyclic, ``i^sharp=p``, the advanced/retarded adjoint relation transfers too.

This module proves that transfer theorem and records its prerequisites.  It
is fail closed against the current BGG screen: the latter has only flat
associated-graded chain maps and a nonzero curved PBW defect, so no endpoint
causal flag is promoted yet.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _reduce_transfer(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce the abstract endpoint transfer identity exactly."""

    pending = list(entry.terms)
    values: dict[tuple[str, ...], object] = {}
    while pending:
        word, coefficient = pending.pop()
        replaced = False
        rewrites = {
            ("q", "p"): ("p", "Q"),
            ("i", "q"): ("Q", "i"),
            ("p", "i"): (),
        }
        for index in range(max(0, len(word) - 1)):
            pair = word[index : index + 2]
            if pair in rewrites:
                pending.append(
                    (
                        word[:index] + rewrites[pair] + word[index + 2 :],
                        coefficient,
                    )
                )
                replaced = True
                break
        if replaced:
            continue
        values[word] = values.get(word, 0) + coefficient

    # The only nontrivial sum is p(QL+LQ)i=p i.
    left = values.pop(("p", "Q", "L", "i"), 0)
    right = values.pop(("p", "L", "Q", "i"), 0)
    if left != right:
        values[("p", "Q", "L", "i")] = left
        values[("p", "L", "Q", "i")] = right
    elif left:
        values[()] = values.get((), 0) + left
    return OperatorPolynomial._from_dict(values)


@dataclass(frozen=True)
class AdjointTractorGreenTransfer:
    """Algebraic and analytic inputs for the conditional causal transfer."""

    parent_bundle_ranks: tuple[int, int, int, int]
    endpoint_bundle_ranks: tuple[int, int, int, int]
    parent_connection_flat: bool
    parent_hodge_wave_normally_hyperbolic: bool
    endpoint_transfer_identity_exact: bool
    endpoint_adjoint_transfer_exact: bool

    @staticmethod
    def build() -> "AdjointTractorGreenTransfer":
        q = OperatorPolynomial.atom("q")
        p = OperatorPolynomial.atom("p")
        lam = OperatorPolynomial.atom("L")
        inclusion = OperatorPolynomial.atom("i")
        transferred = p * lam * inclusion
        identity = _reduce_transfer(q * transferred + transferred * q)
        result = AdjointTractorGreenTransfer(
            parent_bundle_ranks=(15, 60, 60, 15),
            endpoint_bundle_ranks=(4, 9, 9, 4),
            parent_connection_flat=True,
            parent_hodge_wave_normally_hyperbolic=True,
            endpoint_transfer_identity_exact=(
                identity == OperatorPolynomial.identity()
            ),
            endpoint_adjoint_transfer_exact=True,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.parent_bundle_ranks != (15, 60, 60, 15):
            raise AssertionError("parent adjoint-tractor detour ranks drifted")
        if self.endpoint_bundle_ranks != (4, 9, 9, 4):
            raise AssertionError("compressed metric endpoint ranks drifted")
        if not self.parent_connection_flat:
            raise AssertionError("the parent Hodge wave needs a flat tractor connection")
        if not self.parent_hodge_wave_normally_hyperbolic:
            raise AssertionError("the parent causal Green theorem is unavailable")
        if not self.endpoint_transfer_identity_exact:
            raise AssertionError("p Lambda i does not satisfy the endpoint identity")
        if not self.endpoint_adjoint_transfer_exact:
            raise AssertionError("cyclic adjoint transfer formula drifted")

    def certificate(
        self,
        *,
        kostant_certificate: Mapping[str, object],
        differential_screen_certificate: Mapping[str, object],
        endpoint_certificate: Mapping[str, object],
        endpoint_filtration_certificate: Mapping[str, object],
        curved_bgg_certificate: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        self.verify()
        if kostant_certificate.get("schema_version") != 1 or (
            kostant_certificate.get("result") != "PASS"
        ):
            raise AssertionError("the pointwise Kostant compression is unavailable")
        if differential_screen_certificate.get("schema_version") != 1:
            raise AssertionError("wrong BGG differential screen input")
        if endpoint_certificate.get("schema") != (
            "pure-weyl-prolonged-metric-endpoint-complex-v1"
        ):
            raise AssertionError("wrong exact endpoint input")
        if endpoint_filtration_certificate.get("schema") != (
            "pure-weyl-endpoint-green-filtration-boundary-v1"
        ):
            raise AssertionError("wrong endpoint filtration input")

        boundary = differential_screen_certificate.get("theorem_boundary")
        if not isinstance(boundary, Mapping):
            raise AssertionError("BGG screen theorem boundary is missing")
        screen_open = not all(
            boundary.get(key) is True
            for key in (
                "curved_cylinder_BGG_chain_maps_exact",
                "curved_differential_homotopy_exact",
                "full_Bach_coefficient_match",
            )
        )

        required_curved_keys = (
            "curved_BGG_chain_maps_exact",
            "curved_differential_homotopy_exact",
            "endpoint_Bach_operator_match",
            "support_local",
            "cyclic_i_sharp_equals_p",
        )
        curved_boundary = (
            curved_bgg_certificate.get("theorem_boundary")
            if curved_bgg_certificate is not None
            else None
        )
        curved_schema_valid = bool(
            curved_bgg_certificate is not None
            and curved_bgg_certificate.get("schema_version") == 1
            and curved_bgg_certificate.get("dependency_tag")
            == "LORENTZIAN-CAUSAL"
            and curved_bgg_certificate.get("fail_closed") is True
            and isinstance(curved_boundary, Mapping)
            and curved_boundary.get("parent_green_homotopy_transferred")
            is False
        )
        curved_ready = bool(
            curved_schema_valid
            and isinstance(curved_boundary, Mapping)
            and all(curved_boundary.get(key) is True for key in required_curved_keys)
        )
        endpoint_ready = curved_ready

        dependencies = {
            "kostant": _certificate_digest(kostant_certificate),
            "differential_screen": _certificate_digest(
                differential_screen_certificate
            ),
            "endpoint": _certificate_digest(endpoint_certificate),
            "endpoint_filtration": _certificate_digest(
                endpoint_filtration_certificate
            ),
        }
        if curved_bgg_certificate is not None:
            dependencies["curved_bgg"] = _certificate_digest(
                curved_bgg_certificate
            )

        return {
            "schema": "pure-weyl-adjoint-tractor-green-transfer-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "dependency_sha256": dependencies,
            "parent_YM_detour": {
                "bundle_ranks": list(self.parent_bundle_ranks),
                "differential": "d_A, delta_A d_A, delta_A",
                "backward_witness": "delta_A, identity, d_A",
                "wave_anticommutator": [
                    "delta_A d_A",
                    "d_A delta_A+delta_A d_A",
                    "d_A delta_A+delta_A d_A",
                    "delta_A d_A",
                ],
                "flat_adjoint_tractor_connection": self.parent_connection_flat,
                "degreewise_normally_hyperbolic": (
                    self.parent_hodge_wave_normally_hyperbolic
                ),
                "advanced_retarded_Green_operators": True,
                "Q_parent_G_equals_G_Q_parent": (
                    "by two-sided uniqueness and Q_parent P=P Q_parent"
                ),
                "causal_homotopy": (
                    "Lambda_parent,+/-=W_parent G_parent,+/-"
                ),
                "homotopy_identity": (
                    "Q_parent Lambda_parent,+/-+Lambda_parent,+/- Q_parent=1"
                ),
                "adjoint_relation": "Lambda_parent,+^sharp=Lambda_parent,-",
            },
            "transfer_theorem": {
                "endpoint_bundle_ranks": list(self.endpoint_bundle_ranks),
                "formula": "Lambda_end,+/-=p Lambda_parent,+/- i",
                "algebraic_identity_exact": self.endpoint_transfer_identity_exact,
                "derivation": (
                    "q p=p Q, Q i=i q, p i=1 imply "
                    "q(p Lambda i)+(p Lambda i)q=p(Q Lambda+Lambda Q)i=1"
                ),
                "support_derivation": (
                    "finite-order differential pre/postcomposition does not "
                    "enlarge support, so supp Lambda_end,+/- f is contained "
                    "in J^+/- supp f"
                ),
                "adjoint_derivation": (
                    "i^sharp=p and p^sharp=i imply "
                    "Lambda_end,+^sharp=p Lambda_parent,- i"
                ),
                "cyclic_adjoint_exact_conditionally": (
                    self.endpoint_adjoint_transfer_exact
                ),
            },
            "curved_BGG_gate": {
                "current_screen_boundary_open": screen_open,
                "future_certificate_supplied": curved_bgg_certificate is not None,
                "authoritative_future_filename": (
                    "adjoint_tractor_bgg_curved_pbw.json"
                ),
                "required_future_schema_version": 1,
                "future_certificate_schema_valid": curved_schema_valid,
                "upstream_transfer_flag_remains_false": (
                    isinstance(curved_boundary, Mapping)
                    and curved_boundary.get("parent_green_homotopy_transferred")
                    is False
                ),
                "future_certificate_sha256": (
                    dependencies.get("curved_bgg")
                ),
                "required_true_keys": list(required_curved_keys),
                "all_required_keys_true": curved_ready,
                "current_commuting_derivative_defect_entries": (
                    differential_screen_certificate.get(
                        "cylinder_metric_split_screen", {}
                    ).get("commuting_derivative_chain_defect_entries")
                ),
            },
            "endpoint_assembly": {
                "tracefree_parent_transfer_ready": endpoint_ready,
                "trace_Weyl_triangular_channels_already_green": True,
                "complete_30_row_endpoint_causal_homotopy": False,
                "formula_when_ready": (
                    "a downstream certificate must directly assemble the "
                    "transferred 4-9-9-4 homotopy with the certified four "
                    "trace/Weyl rows"
                ),
            },
            "warranted_atomic_flags": [
                "adjoint_tractor_parent_YM_green_homotopy_exact",
                "cyclic_BGG_green_transfer_theorem_exact",
            ],
            "status_flags_promoted": [],
            "support_local_prolongation_retract": False,
            "curvature_causal_green_operators": False,
            "tracefree_causal_green_homotopy": endpoint_ready,
            "causal_green_homotopy": False,
            "prolonged_green_witness": False,
            "proof_boundary": (
                "the parent causal theorem and abstract cyclic transfer are "
                "exact; a future coefficientwise curved BGG SDR certificate "
                "activates only the trace-free 4-9-9-4 homotopy. A separate "
                "trace/Weyl triangular assembly is required for the full "
                "30-row endpoint and all-row causal flag"
            ),
            "fail_closed": True,
        }
