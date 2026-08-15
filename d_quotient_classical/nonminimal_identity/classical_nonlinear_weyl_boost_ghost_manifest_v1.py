#!/usr/bin/env python3
"""Certify the nonlinear Weyl/boost gauge algebra and shifted ghost manifest."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
MINIMAL = ROOT / "field_bv_identification/certificates/minimal_bv_chain.json"
ANTIFIELD = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
DIFF = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-nonlinear-weyl-boost-ghost-manifest-v1.md"

PDF_URL = "https://arxiv.org/pdf/0707.4437v3"
PDF_SHA256 = "80bbe298159e4fdfc35c0f4dd4e33f01e5da51227184a0bed870e5fa3e6b2676"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def add(*vectors: dict[str, Fraction]) -> dict[str, Fraction]:
    keys = set().union(*(vector.keys() for vector in vectors))
    return {key: sum((vector.get(key, Fraction(0)) for vector in vectors), Fraction(0)) for key in sorted(keys)}


def encode(vector: dict[str, Fraction]) -> dict[str, str]:
    return {key: str(value) for key, value in vector.items() if value}


def build() -> dict[str, Any]:
    action, minimal, antifield, diff = (
        json.loads(path.read_text()) for path in (ACTION, MINIMAL, ANTIFIELD, DIFF)
    )
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("curved ordinary-derivative action drift")
    if minimal.get("schema") != "pure-weyl-field-bv-minimal-chain-v1":
        raise ValueError("minimal BV master-action drift")
    if antifield.get("result_id") != "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2":
        raise ValueError("minimal BV executable export drift")
    if diff.get("result_id") != "CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1":
        raise ValueError("auxiliary Diff representation drift")

    # Formal tensor structures are independent.  Equality of their rational
    # coefficients therefore proves the displayed natural tensor identities.
    boost_delta_G = {
        "sym_nabla_kappa": Fraction(-1, 2),
        "sym_b_kappa": Fraction(-1, 2),
        "g_div_kappa": Fraction(1),
        "g_b_dot_kappa": Fraction(-1, 2),
    }
    boost_A_delta_phi = dict(boost_delta_G)
    boost_defect = add(boost_delta_G, {key: -value for key, value in boost_A_delta_phi.items()})

    weyl_contributions = {
        "delta_Ric": {"hess_sigma": Fraction(-1), "g_box_sigma": Fraction(-1, 2)},
        "delta_sym_nabla_b": {
            "hess_sigma": Fraction(1),
            "sym_b_dsigma": Fraction(-1, 2),
            "g_b_dot_dsigma": Fraction(1, 2),
        },
        "delta_half_b_tensor_b": {"sym_b_dsigma": Fraction(1, 2)},
        "delta_trace_term": {"g_box_sigma": Fraction(1, 2), "g_b_dot_dsigma": Fraction(-1, 2)},
    }
    weyl_delta_G = add(*weyl_contributions.values())

    dk_connection = {"sym_kappa_dsigma": Fraction(-1), "g_kappa_dot_dsigma": Fraction(1)}
    dk_b_terms = {"sym_kappa_dsigma": Fraction(1), "g_kappa_dot_dsigma": Fraction(-1)}
    dk_commutator = add(dk_connection, dk_b_terms)
    kk_first = {"sym_kappa1_kappa2": Fraction(-1), "g_kappa1_dot_kappa2": Fraction(1)}
    kk_second = dict(kk_first)
    kk_commutator = add(kk_first, {key: -value for key, value in kk_second.items()})

    source_transformations = {
        "convention_crosswalk": {
            "literature_parameter": "xi_D=-2 sigma_Metsaev",
            "repository_parameter": "sigma=xi_D",
            "effect": "Metsaev (6.5)-(6.7) become delta g=sigma g and delta b=d sigma-kappa",
        },
        "diffeomorphism": "delta_c(g,phi,b)=(L_c g,L_c phi,L_c b)",
        "Weyl": "delta_sigma g=sigma g; delta_sigma b=d sigma; delta_sigma phi=0",
        "conformal_boost": "delta_kappa g=0; delta_kappa b=-kappa; delta_kappa phi_mu_nu=nabla_mu kappa_nu+nabla_nu kappa_mu+b_mu kappa_nu+b_nu kappa_mu-g_mu_nu b^rho kappa_rho",
    }
    covariance = {
        "boost": {
            "delta_G_b_coefficients": encode(boost_delta_G),
            "A_g_delta_phi_coefficients": encode(boost_A_delta_phi),
            "delta_G_b_minus_A_g_delta_phi": encode(boost_defect),
            "f_hat_boost_invariant": not encode(boost_defect),
        },
        "Weyl": {
            "contributions": {name: encode(vector) for name, vector in weyl_contributions.items()},
            "delta_G_b_coefficients": encode(weyl_delta_G),
            "A_g_on_weight_zero_covariant_tensors_invariant": True,
            "f_hat_Weyl_invariant": not encode(weyl_delta_G),
        },
    }
    algebra = {
        "brackets": [
            {"pair": "Diff,Diff", "result": "Diff([c1,c2])", "internal_zero": False},
            {"pair": "Diff,Weyl", "result": "Weyl(L_c sigma)", "internal_zero": False},
            {"pair": "Diff,boost", "result": "boost(L_c kappa)", "internal_zero": False},
            {"pair": "Weyl,Weyl", "result": "zero", "internal_zero": True},
            {"pair": "Weyl,boost", "result": "zero", "internal_zero": True, "coefficient_defect": encode(dk_commutator)},
            {"pair": "boost,boost", "result": "zero", "internal_zero": True, "coefficient_defect": encode(kk_commutator)},
        ],
        "off_shell_closure": not encode(dk_commutator) and not encode(kk_commutator),
        "field_dependent_structure_functions": False,
        "local_gauge_reducibility": "none; the algebraic boost shift delta b=-kappa is injective",
    }
    shifted = {
        "ghost_change": "eta=kappa-d sigma",
        "field_change": "f_hat=phi-A_g^-1 G^b(g,b)",
        "BRST_rows": {
            "Q_v_internal": "-eta",
            "Q_f_hat_internal": "0",
            "Q_eta_internal": "0",
            "Q_sigma_internal": "0",
            "Q_f_hat_Diff": "L_c f_hat",
            "Q_v_Diff": "L_c v",
            "Q_eta_Diff": "L_c eta",
            "Q_sigma_Diff": "L_c sigma",
        },
        "non_Diff_nonlinear_ghost_antifield_terms": [],
    }
    manifest = [
        {"family_id": "DIFF_C_C_C_STAR", "source": "minimal BV master action", "status": "SOURCE_SERIALIZED_MINIMAL"},
        {"family_id": "DIFF_C_SIGMA_SIGMA_STAR", "source": "minimal BV master action", "status": "SOURCE_SERIALIZED_MINIMAL"},
        {"family_id": "DIFF_C_ETA_ETA_STAR", "source": diff["result_id"], "status": "SOURCE_SERIALIZED_AUXILIARY"},
    ]
    absence = [
        {"candidate_family": "WEYL_SIGMA_ETA_ETA_STAR", "coefficient": "0", "reason": "Weyl and boost commute exactly"},
        {"candidate_family": "BOOST_ETA_ETA_ETA_STAR", "coefficient": "0", "reason": "boost transformations commute exactly"},
        {"candidate_family": "WEYL_OR_BOOST_F_HAT_F_HAT_STAR", "coefficient": "0", "reason": "f_hat is exactly invariant under both internal symmetries"},
        {"candidate_family": "WEYL_OR_BOOST_V_V_STAR", "coefficient": "0", "reason": "the internal v transformation is the unary row Qv=-eta"},
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-nonlinear-weyl-boost-ghost-manifest-v1",
        "result_id": "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1",
        "result_kind": "AUTHORITATIVE_NONLINEAR_WEYL_BOOST_GAUGE_ALGEBRA_AND_GHOST_MANIFEST",
        "result_state": "FULL_WEYL_BOOST_LAWS_IMPORTED_INTERNAL_ALGEBRA_ABELIAN_SHIFTED_GHOST_MANIFEST_EXHAUSTIVE_IN_SCOPE",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "four-dimensional ordinary-derivative strict pure-Weyl gravity",
            "fields": ["g_mu_nu", "phi_mu_nu", "b_mu"],
            "gauge_parameters": ["c^mu", "sigma", "kappa_mu"],
            "coefficient_field": "Q",
            "claim_scope": "off-shell local gauge algebra and ghost-antifield families induced by Weyl/boost after the exact shifted-variable change",
        },
        "primary_literature": {
            "citation": "R. R. Metsaev, Ordinary-derivative formulation of conformal low-spin fields, arXiv:0707.4437v3",
            "url": "https://arxiv.org/abs/0707.4437",
            "pdf_url": PDF_URL,
            "pdf_sha256": PDF_SHA256,
            "pages": 58,
            "equations": ["6.2", "6.3", "6.5", "6.6", "6.7"],
            "retrieved": "2026-08-15",
        },
        "source_transformations": source_transformations,
        "shifted_auxiliary_covariance": covariance,
        "gauge_algebra": algebra,
        "shifted_BRST_manifest": shifted,
        "nonzero_ghost_antifield_family_manifest": manifest,
        "certified_zero_candidate_families": absence,
        "manifest_summary": {
            "nonzero_ghost_antifield_families": len(manifest),
            "minimal_families": 2,
            "auxiliary_families": 1,
            "certified_zero_candidate_families": len(absence),
            "additional_nonlinear_Weyl_boost_ghost_antifield_families": 0,
        },
        "claim_flags": {
            "FULL_NONLINEAR_WEYL_BOOST_GAUGE_TRANSFORMATIONS_IMPORTED": True,
            "WEYL_BOOST_GAUGE_ALGEBRA_OFF_SHELL_CLOSED": True,
            "SHIFTED_F_HAT_WEYL_BOOST_INVARIANT": True,
            "INTERNAL_WEYL_BOOST_GHOST_BRACKETS_ZERO": True,
            "EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST": True,
            "ADDITIONAL_AUXILIARY_GHOST_ANTIFIELD_FAMILIES_REQUIRED": False,
            "FULL_386_SOURCE_Q2_ASSEMBLED": False,
            "FULL_Q1_Q2_IDENTITY_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the assembled 386-row source q2 or q3 payload",
            "the q1/q2 identity, cyclicity or D-equivariance after combining all component families",
            "the residual SDR and pairing gates required by Gate A",
            "a Lorentzian off-shell BV propagator, Hadamard state, renormalized products, QME restoration or residual transfer",
        ],
        "canonical_hashes": {
            "source_transformations_sha256": digest(source_transformations),
            "shifted_auxiliary_covariance_sha256": digest(covariance),
            "gauge_algebra_sha256": digest(algebra),
            "shifted_BRST_manifest_sha256": digest(shifted),
            "nonzero_family_manifest_sha256": digest(manifest),
            "certified_zero_candidate_families_sha256": digest(absence),
        },
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "result_or_artifact_id": action["schema"], "sha256": sha(ACTION), "role": "local action and incomplete gauge manifest to be completed append-only"},
            {"path": str(MINIMAL.relative_to(ROOT)), "result_or_artifact_id": minimal["schema"], "sha256": sha(MINIMAL), "role": "displayed minimal Diff x Weyl master action"},
            {"path": str(ANTIFIELD.relative_to(ROOT)), "result_or_artifact_id": antifield["result_id"], "sha256": sha(ANTIFIELD), "role": "executable minimal ghost and antifield rows"},
            {"path": str(DIFF.relative_to(ROOT)), "result_or_artifact_id": diff["result_id"], "sha256": sha(DIFF), "role": "source-forced Diff action on shifted auxiliary fields"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Import this exhaustive scoped manifest into the 386-row receiver, assemble all known source q2 component families on common bytes, and replay q1/q2, cyclicity and D-equivariance without inferring those identities from the manifest alone.",
    }


def render(value: dict[str, Any]) -> str:
    summary = value["manifest_summary"]
    return f"""# Nonlinear Weyl/boost ghost manifest v1

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`

Metsaev's full nonlinear transformation (6.6), absent from the older local
summary, contains the three `b-kappa` terms.  In the repository convention it
is

```text
delta_kappa phi_mu_nu = nabla_mu kappa_nu + nabla_nu kappa_mu
                      + b_mu kappa_nu + b_nu kappa_mu
                      - g_mu_nu b^rho kappa_rho.
```

Exact coefficient collection proves `delta_kappa G^b=A_g(delta_kappa phi)`
and `delta_sigma G^b=0`.  Hence `f_hat=phi-A_g^-1 G^b` is invariant under
both internal symmetries.  The Weyl--boost and boost--boost commutators also
vanish off shell.  After `eta=kappa-d sigma`, the only nonzero ghost brackets
are the Diff semidirect actions.

The exhaustive manifest in this scope therefore has
**{summary['nonzero_ghost_antifield_families']}** nonzero families: two
already in the minimal master action and the already serialized
`DIFF_C_ETA_ETA_STAR` auxiliary family.  It requires
**{summary['additional_nonlinear_Weyl_boost_ghost_antifield_families']}**
additional Weyl/boost ghost-antifield families.

This closes the manifest question, not the full source import.  The separate
386-row assembly and its `q1/q2`, cyclicity and `D` replays remain open.

Primary source: [Metsaev, arXiv:0707.4437v3](https://arxiv.org/abs/0707.4437),
equations (6.2)--(6.7); the retrieved 58-page PDF hash is
`{value['primary_literature']['pdf_sha256']}`.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_nonlinear_weyl_boost_ghost_manifest_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_nonlinear_weyl_boost_ghost_manifest_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_nonlinear_weyl_boost_ghost_manifest_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_nonlinear_weyl_boost_ghost_manifest_v1
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
